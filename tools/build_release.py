#!/usr/bin/env python3

"""Build the folder that goes on the update stick.

    python3 tools/build_release.py                    into release/kiekmap-update
    python3 tools/build_release.py --nach /Volumes/STICK/kiekmap-update
    python3 tools/build_release.py --mit-karte        take the map and the place index along

``deploy/pi/update.sh`` expects exactly this folder: ``abbilder.tar`` with both images, a
``version`` file whose content is the image tag, and optionally ``tiles/`` and ``places.json``.
Until now that was four commands typed by hand out of ``docs/operations.md``, and the one that
gets forgotten is the ``version`` file -- the images load, the ``.env`` keeps the old number, and
``docker compose up`` on the Pi pulls the previous image back up. The device then runs the old
software and says so nowhere.

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
        raise SystemExit(f"Fehlgeschlagen: {' '.join(command)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def version() -> str:
    """The one version, and an abort when the places disagree."""
    values = {value for _, value in found()}
    if len(values) != 1:
        raise SystemExit("Die Versionsangaben laufen auseinander. Erst `make check`.")
    return values.pop()


def check_tree(tag: str) -> None:
    """A stick has to correspond to a commit, and to the tag that names it."""
    if run("git", "status", "--porcelain"):
        raise SystemExit(
            "Der Arbeitsbaum ist nicht sauber.\n"
            "  Ein Stick, der zu keinem Commit gehoert, ist spaeter nicht mehr zuzuordnen."
        )
    tags = run("git", "tag", "--list", tag)
    if not tags:
        raise SystemExit(
            f"Den Tag {tag} gibt es nicht.\n"
            f"  Erst taggen:  git tag -s {tag} -m {tag}\n"
            "  Der Tag ist das, was den Stick auf einen Stand festnagelt."
        )
    if run("git", "rev-parse", "HEAD") != run("git", "rev-parse", f"{tag}^{{commit}}"):
        raise SystemExit(f"HEAD steht nicht auf {tag}. Erst auschecken, was ausgeliefert wird.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nach", type=Path, default=ROOT / "release" / "kiekmap-update")
    parser.add_argument(
        "--mit-karte",
        action="store_true",
        help="Kartendatei und Ortsindex mitnehmen (nur noetig, wenn die Region sich geaendert hat)",
    )
    args = parser.parse_args()

    number = version()
    tag = f"v{number}"
    check_tree(tag)

    ziel = args.nach
    ziel.mkdir(parents=True, exist_ok=True)
    print(f"== {tag} nach {ziel}")

    for name, context in IMAGES:
        print(f"== {name}:{tag} bauen")
        subprocess.run(["docker", "build", "-t", f"{name}:{tag}", str(context)], check=True)

    print("== Abbilder sichern")
    archive = ziel / "abbilder.tar"
    subprocess.run(
        ["docker", "save", *(f"{name}:{tag}" for name, _ in IMAGES), "-o", str(archive)],
        check=True,
    )

    # The line most easily forgotten by hand -- and without it the Pi pulls the previous image
    # back up, because KIEKMAP_VERSION stays as it was in its .env.
    (ziel / "version").write_text(f"{tag}\n", encoding="utf-8")

    if args.mit_karte:
        print("== Karte und Ortsindex mitnehmen")
        for quelle, name in (
            (ROOT / "frontend/public/tiles", "tiles"),
            (ROOT / "data/places.json", "places.json"),
        ):
            if not quelle.exists():
                raise SystemExit(f"{quelle.relative_to(ROOT)} fehlt -- erst `make tiles`.")
            if quelle.is_dir():
                shutil.rmtree(ziel / name, ignore_errors=True)
                shutil.copytree(quelle, ziel / name)
            else:
                shutil.copy2(quelle, ziel / name)

    print(f"\nFertig. {sum(f.stat().st_size for f in ziel.rglob('*') if f.is_file()) / 1e6:.0f} MB")
    for f in sorted(ziel.iterdir()):
        print(f"  {f.name}")
    print(f"\nAuf dem Pi:  sudo sh /opt/kiekmap/deploy/pi/update.sh <Stick>/{ziel.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
