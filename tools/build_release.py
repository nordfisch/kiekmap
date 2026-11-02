#!/usr/bin/env python3

"""Build what a device or a server installs.

    python3 tools/build_release.py --pi               the bundle for a Pi, into release/kiekmap
    python3 tools/build_release.py --pi --to /Volumes/STICK/kiekmap
    python3 tools/build_release.py                    the images for the online server
    python3 tools/build_release.py --notes            the release text, both languages

**The bundle for a Pi** is everything the device needs, in one folder: both images, the map, the
place index, the compose file, the scripts under ``deploy/pi/`` and the Pi's ``.env``.
``make deploy`` copies it over with rsync; ``deploy/pi/setup-pi.sh`` installs from it once and
``deploy/pi/update.sh`` updates from it. The Pi needs no clone of the repository and no git.

**The images for the server** are ``images.tar`` and a ``version`` file, built on the release tag;
see docs/museum/operations.md, "Updating the server".

**The coat of arms comes from ``local/logo.png``** and reaches the frontend image as a named build
context (see ``frontend/Dockerfile``). The tree keeps the placeholder, so the clean-tree rule below
needs no exception.

**What it refuses to do**, because a bundle that does not match a commit is worse than none: build
from a dirty working tree. The server images and the release text also need HEAD on the release
tag. A Pi bundle does not: off the tag it carries the commit in its version, see ``described``.
There is no ``--force``; the fix is to commit.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from set_version import found  # noqa: E402  -- needs ROOT on the path first

#: The two images, and the build context each is built from.
IMAGES = (("kiekmap-backend", ROOT / "backend"), ("kiekmap-frontend", ROOT / "frontend"))

#: What belongs to this museum and never into the repository. Git-ignored.
LOCAL = ROOT / "local"
CREST = LOCAL / "logo.png"
PI_ENV = LOCAL / "pi.env"

#: Every Pi that runs this is a 4 or a 5 (WebGL 2), and both are arm64. Named explicitly so that a
#: bundle built on an Intel machine does not carry images the Pi cannot start.
PI_PLATFORM = "linux/arm64"


def run(*command: str) -> str:
    # S603: every caller passes a literal git command; nothing here comes from outside.
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)  # noqa: S603
    if result.returncode != 0:
        raise SystemExit(f"Failed: {' '.join(command)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def version() -> str:
    """The one version, and an abort when the places disagree."""
    values = {value for _, value in found()}
    if len(values) != 1:
        raise SystemExit("The version numbers disagree. Run `make check` first.")
    return values.pop()


def check_clean() -> None:
    """A bundle has to correspond to a commit."""
    stray = run("git", "status", "--porcelain")
    if stray:
        raise SystemExit(
            "The working tree is not clean.\n"
            "  A bundle that belongs to no commit cannot be traced back later.\n"
            "  Commit first. The coat of arms belongs in local/logo.png, not in the tree.\n\n"
            + stray
        )


def check_tag(tag: str) -> None:
    """HEAD has to be the commit the tag names.

    For the server images, and for the release text as well: the version comes from the files, so
    a run on a tree whose number was never raised prints the notes of the *previous* release, and
    nothing about them looks wrong.
    """
    tags = run("git", "tag", "--list", tag)
    if not tags:
        raise SystemExit(
            f"There is no tag {tag}.\n"
            f"  Tag it first:  git tag -s {tag} -m {tag}\n"
            "  The tag is what nails the images down to one state."
        )
    if run("git", "rev-parse", "HEAD") != run("git", "rev-parse", f"{tag}^{{commit}}"):
        raise SystemExit(f"HEAD is not on {tag}. Check out what is being shipped first.")


def described(tag: str) -> str:
    """``v0.9.6`` on the release tag, ``v0.9.6-g0942491`` on any other commit.

    Either is a valid image tag and names exactly one commit. Not ``git describe``: the release
    tags sit on merge commits in ``main``, which ``develop`` never contains, so on a branch it
    names a release several versions old.
    """
    head = run("git", "rev-parse", "HEAD")
    if run("git", "tag", "--list", tag) and head == run("git", "rev-parse", f"{tag}^{{commit}}"):
        return tag
    return f"{tag}-g{head[:7]}"


def check_pi_env() -> None:
    """The Pi's .env exists and carries a PIN hash Compose will read whole.

    On the first run the file is created from the template, and the run stops: what goes into it
    is a decision about this museum, not something to default.
    """
    if not PI_ENV.exists():
        LOCAL.mkdir(exist_ok=True)
        shutil.copy2(ROOT / "deploy" / ".env.example", PI_ENV)
        raise SystemExit(
            f"{PI_ENV.relative_to(ROOT)} did not exist and has been created from the template.\n"
            "  Fill it in: the PIN (make pin) and the settings of the collection.\n"
            '  See docs/museum/operations.md, "What the development machine needs".'
        )
    for line in PI_ENV.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        if key.strip() != "KIEKMAP_ADMIN_PIN_HASH":
            continue
        value = value.strip()
        if not value:
            break
        # Compose reads `$600000` in an unquoted value as a variable and keeps only the algorithm.
        # The PIN then never matches, and nothing says why.
        if "$" in value and not (value.startswith("'") and value.endswith("'")):
            raise SystemExit(
                f"KIEKMAP_ADMIN_PIN_HASH in {PI_ENV.relative_to(ROOT)} has to be in single "
                "quotes.\n  Compose would cut it at the first `$`. `make pin` prints it that way."
            )
        return
    raise SystemExit(
        f"{PI_ENV.relative_to(ROOT)} has no KIEKMAP_ADMIN_PIN_HASH.\n"
        "  Without it nobody can open the admin area, and so nobody can restore a backup.\n"
        "  `make pin` prints the line."
    )


def build_images(tag: str, platform: str | None, *, crest_required: bool) -> None:
    """Both images, the frontend one with the coat of arms from local/logo.png if there is one."""
    if crest_required and not CREST.exists():
        raise SystemExit(
            f"{CREST.relative_to(ROOT)} is missing.\n"
            "  Copy the museum's coat of arms there. A museum without one copies the placeholder\n"
            "  frontend/public/logo.png there, so that the choice is a deliberate one."
        )
    with tempfile.TemporaryDirectory() as crest_dir:
        crest = []
        if CREST.exists():
            shutil.copy2(CREST, Path(crest_dir) / "logo.png")
            crest = ["--build-context", f"crest={crest_dir}"]
            print(f"== coat of arms from {CREST.relative_to(ROOT)}")
        else:
            print("== no local/logo.png: the image carries the placeholder")
        for name, context in IMAGES:
            print(f"== building {name}:{tag}")
            extra = crest if name == "kiekmap-frontend" else []
            if platform:
                extra = ["--platform", platform, *extra]
            # S603, S607: a literal list without a shell, and docker comes from PATH -- Docker
            # Desktop and a package manager put it in different places.
            subprocess.run(  # noqa: S603
                ["docker", "build", *extra, "-t", f"{name}:{tag}", str(context)],  # noqa: S607
                check=True,
            )


def save_images(tag: str, target: Path) -> None:
    print("== saving the images")
    saved = [f"{name}:{tag}" for name, _ in IMAGES]
    subprocess.run(  # noqa: S603
        ["docker", "save", *saved, "-o", str(target / "images.tar")],  # noqa: S607
        check=True,
    )
    # Without it the device starts the previous image again, because KIEKMAP_VERSION in its .env
    # stays as it was.
    (target / "version").write_text(f"{tag}\n", encoding="utf-8")


def prepare(target: Path) -> None:
    """An empty target folder -- but never by deleting something that is not a bundle.

    ``--to /Volumes/STICK`` instead of ``--to /Volumes/STICK/kiekmap`` would otherwise empty the
    stick. A folder is taken as an earlier bundle when it holds a ``version`` file.
    """
    if target.exists() and any(target.iterdir()):
        if not (target / "version").is_file():
            raise SystemExit(
                f"{target} is not empty and holds no earlier bundle.\n"
                "  Name a folder of its own, for example /Volumes/STICK/kiekmap."
            )
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


def build_pi(target: Path, tag: str) -> str:
    """The folder setup-pi.sh and update.sh read. Returns the version it carries."""
    check_clean()
    check_pi_env()
    sources = {
        "tiles": ROOT / "frontend" / "public" / "tiles",
        "places.json": ROOT / "data" / "places.json",
    }
    for name, source in sources.items():
        if not source.exists():
            command = "make tiles" if name == "tiles" else "make places"
            raise SystemExit(f"{source.relative_to(ROOT)} is missing -- run `{command}` first.")

    tag = described(tag)
    prepare(target)
    print(f"== {tag} to {target}")
    build_images(tag, PI_PLATFORM, crest_required=True)
    save_images(tag, target)

    print("== the map, the place index, the scripts and the .env")
    shutil.copytree(sources["tiles"], target / "tiles")
    shutil.copy2(sources["places.json"], target / "places.json")
    (target / "deploy").mkdir()
    shutil.copy2(ROOT / "deploy" / "docker-compose.yml", target / "deploy" / "docker-compose.yml")
    shutil.copytree(ROOT / "deploy" / "pi", target / "deploy" / "pi")
    shutil.copy2(PI_ENV, target / "env")
    remove_apple_double(target)
    return tag


def remove_apple_double(target: Path) -> None:
    """The ``._<name>`` files macOS writes beside every file on a stick without extended attributes.

    On exFAT or FAT, macOS keeps a file's extended attributes in a file of its own. A bundle
    written onto a stick from a Mac had twenty of them, and ``update.sh`` copied them onto the
    device. Removing them drops the attributes, which nothing on the Pi reads.
    """
    for path in sorted(target.rglob("._*"), reverse=True):
        if path.is_file():
            path.unlink()


def build_server(target: Path, tag: str) -> None:
    check_clean()
    check_tag(tag)
    target.mkdir(parents=True, exist_ok=True)
    print(f"== {tag} to {target}")
    build_images(tag, None, crest_required=False)
    save_images(tag, target)


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
    because the repository speaks English.

    **A changelog without a block for this version aborts the run.** It used to print a placeholder
    and exit 0, and the release of 0.9.5 went out with that placeholder as its whole text: the
    version heading had not been written yet. A body that says nothing is a failed step, and the
    step has to say so while it can still be repeated.
    """
    parts = []
    for path, heading in ((CHANGELOG, None), (CHANGELOG_DE, "## Auf Deutsch")):
        found = section(path, version)
        if not found:
            raise SystemExit(
                f"{path.name} has no block ## [{version}].\n"
                f"  Rename its ## [Unreleased] block to ## [{version}] -- <date> first; see\n"
                '  docs/developer/development.md, "Making a release".'
            )
        if heading:
            parts.append("---\n\n" + heading + "\n")
        parts.append(found)
    return "\n\n".join(parts).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", type=Path, help="the folder to build into")
    parser.add_argument("--pi", action="store_true", help="the bundle for a Pi")
    parser.add_argument(
        "--notes", action="store_true", help="print the release text and build nothing"
    )
    args = parser.parse_args()

    number = version()
    tag = f"v{number}"

    if args.notes:
        check_tag(tag)
        print(notes(number), end="")
        return 0

    if args.pi:
        target = args.to or ROOT / "release" / "kiekmap"
        tag = build_pi(target, tag)
    else:
        target = args.to or ROOT / "release" / "kiekmap-update"
        build_server(target, tag)

    size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
    print(f"\nDone: {tag}, {size / 1e6:.0f} MB in {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
