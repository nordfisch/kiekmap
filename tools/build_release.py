#!/usr/bin/env python3

"""Build the folder that goes on the update stick.

    python3 tools/build_release.py                    into release/kiekmap-update
    python3 tools/build_release.py --to /Volumes/STICK/kiekmap-update
    python3 tools/build_release.py --with-map         take the map and the place index along

``deploy/pi/update.sh`` expects exactly this folder: ``images.tar`` with both images, a
``version`` file whose content is the image tag, and optionally ``tiles/`` and ``places.json``.
Until now that was four commands typed by hand out of ``docs/operations.md``, and the one that
gets forgotten is the ``version`` file -- the images load, the ``.env`` keeps the old number, and
``docker compose up`` on the Pi pulls the previous image back up. The device then runs the old
software and says so nowhere.

    python3 tools/build_release.py --notes             the release text, both languages

**What it refuses to do**, because a stick that does not match a commit is worse than no stick:
build from a dirty working tree, or from a tree whose version does not match the tag it claims to
release. There is no ``--force``; the fix is to commit and to tag.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from set_version import found  # noqa: E402  -- needs ROOT on the path first

#: The two images, and the build context each is built from.
IMAGES = (("kiekmap-backend", ROOT / "backend"), ("kiekmap-frontend", ROOT / "frontend"))


def run(*command: str) -> str:
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"Failed: {' '.join(command)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def version() -> str:
    """The one version, and an abort when the places disagree."""
    values = {value for _, value in found()}
    if len(values) != 1:
        raise SystemExit("The version numbers disagree. Run `make check` first.")
    return values.pop()


def check_tree(tag: str) -> None:
    """A stick has to correspond to a commit, and to the tag that names it."""
    if run("git", "status", "--porcelain"):
        raise SystemExit(
            "The working tree is not clean.\n"
            "  A stick that belongs to no commit cannot be traced back later."
        )
    tags = run("git", "tag", "--list", tag)
    if not tags:
        raise SystemExit(
            f"There is no tag {tag}.\n"
            f"  Tag it first:  git tag -s {tag} -m {tag}\n"
            "  The tag is what nails the stick down to one state."
        )
    if run("git", "rev-parse", "HEAD") != run("git", "rev-parse", f"{tag}^{{commit}}"):
        raise SystemExit(f"HEAD is not on {tag}. Check out what is being shipped first.")


#: Where the two changelogs sit. Root rather than ``docs/``, so that the name rule of
#: ``check_translations.py`` holds: a translation is ``X.de.md`` beside ``X.md``.
CHANGELOG = ROOT / "CHANGELOG.md"
CHANGELOG_DE = ROOT / "CHANGELOG.de.md"


def section(path: Path, version: str) -> str:
    """The entries of one version out of a changelog, without its heading.

    Matched on ``## [1.2.3]`` and read to the next ``## ``. Empty when the version is not in there
    -- which is a statement in itself, and the caller says so.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    wanted, collected, inside = f"## [{version}]", [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line.startswith(wanted)
            continue
        if inside:
            collected.append(line)
    return "\n".join(collected).strip()


def notes(version: str) -> str:
    """The body of a GitHub release: English first, German below it.

    One field, no language variants -- so both go into it, and the English half comes first
    because the repository speaks English. A missing half is named rather than passed over: a
    release whose German notes are silently absent is worse than one that says they are.
    """
    parts = []
    for path, heading in ((CHANGELOG, None), (CHANGELOG_DE, "## Auf Deutsch")):
        found = section(path, version)
        if heading:
            parts.append("---\n\n" + heading + "\n")
        parts.append(found or f"*({path.name} names no {version}.)*")
    return "\n\n".join(parts).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", type=Path, default=ROOT / "release" / "kiekmap-update")
    parser.add_argument(
        "--with-map",
        action="store_true",
        help="take the map file and the place index along (only needed when the region changed)",
    )
    parser.add_argument(
        "--notes", action="store_true", help="print the release text and build nothing"
    )
    args = parser.parse_args()

    number = version()
    tag = f"v{number}"

    if args.notes:
        print(notes(number), end="")
        return 0

    check_tree(tag)

    target = args.to
    target.mkdir(parents=True, exist_ok=True)
    print(f"== {tag} to {target}")

    for name, context in IMAGES:
        print(f"== building {name}:{tag}")
        subprocess.run(["docker", "build", "-t", f"{name}:{tag}", str(context)], check=True)

    print("== saving the images")
    archive = target / "images.tar"
    subprocess.run(
        ["docker", "save", *(f"{name}:{tag}" for name, _ in IMAGES), "-o", str(archive)],
        check=True,
    )

    # The line most easily forgotten by hand -- and without it the Pi pulls the previous image
    # back up, because KIEKMAP_VERSION stays as it was in its .env.
    (target / "version").write_text(f"{tag}\n", encoding="utf-8")

    if args.with_map:
        print("== taking the map and the place index along")
        for source, name in (
            (ROOT / "frontend/public/tiles", "tiles"),
            (ROOT / "data/places.json", "places.json"),
        ):
            if not source.exists():
                missing = source.relative_to(ROOT)
                raise SystemExit(f"{missing} is missing -- run `make tiles` first.")
            if source.is_dir():
                shutil.rmtree(target / name, ignore_errors=True)
                shutil.copytree(source, target / name)
            else:
                shutil.copy2(source, target / name)

    size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
    print(f"\nDone. {size / 1e6:.0f} MB")
    for f in sorted(target.iterdir()):
        print(f"  {f.name}")
    print(f"\nOn the Pi:  sudo sh /opt/kiekmap/deploy/pi/update.sh <stick>/{target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
