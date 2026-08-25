#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""The one version number, and the two files that have to agree on it.

    python3 tools/set_version.py            print it
    python3 tools/set_version.py --check    fail if the two files disagree
    python3 tools/set_version.py 0.8.0      write it into both

Front end and back end are versioned together: this is a single-device system, and separate
numbers would be ballast -- see docs/development.md. That leaves one number in **four** files, and
a number kept by hand in four places is wrong within a month. Hence the check, in the same spirit
as ``build_notices.py`` and ``build_register.py``.

Four, not the two the plan expected. ``app/__init__.py`` is the one that matters most and was the
one nobody would have noticed: ``__version__`` is what ``/api/health`` answers and what OpenAPI
prints. Left behind, the device on the wall would have kept announcing 0.1.0 while its image tag
counted on -- and the one question the API exists to answer, *which version is running here*,
would have had a wrong answer.

**The tag is not the source, the files are.** A check against ``git describe`` would go red in the
window between bumping the version and creating the tag -- and that window is exactly where the
commit hook runs. What the tag has to do instead is match: ``make release`` refuses to build a
stick from a working tree whose version does not equal the tag it is releasing.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_JSON = ROOT / "frontend" / "package.json"
PACKAGE_LOCK = ROOT / "frontend" / "package-lock.json"
PYPROJECT = ROOT / "backend" / "pyproject.toml"
INIT_PY = ROOT / "backend" / "app" / "__init__.py"

#: Major.minor.patch, nothing else. No pre-release suffixes: the Pi reads this number out of a
#: file written by ``make release``, and ``0.8.0-rc.1`` in a Docker image tag is a trap nobody
#: needs on a device that is updated twice a year.
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


#: Where the number lives, and the pattern that finds it. ``count`` guards the two lines in
#: ``package-lock.json`` that belong to the root package -- further down the file every dependency
#: carries a ``"version"`` of its own, and those must stay untouched.
PLACES = (
    (PACKAGE_JSON, re.compile(r'^(  "version": ")([^"]*)(")', re.M), 1),
    (PACKAGE_LOCK, re.compile(r'^(  "version": ")([^"]*)(")', re.M), 1),
    (PACKAGE_LOCK, re.compile(r'^(      "version": ")([^"]*)(")', re.M), 1),
    (PYPROJECT, re.compile(r'^(version = ")([^"]*)(")', re.M), 1),
    (INIT_PY, re.compile(r'^(__version__ = ")([^"]*)(")', re.M), 1),
)


def found() -> list[tuple[Path, str]]:
    """What each place says today."""
    values = []
    for path, pattern, _ in PLACES:
        match = pattern.search(path.read_text(encoding="utf-8"))
        if not match:
            raise SystemExit(f"{path.relative_to(ROOT)}: keine Zeile mit einer Version gefunden.")
        values.append((path, match.group(2)))
    return values


def write(version: str) -> None:
    """Every place, line by line -- the JSON files are **not** re-serialised.

    ``json.dump`` would reformat the whole file and bury the change in noise. npm writes these
    same files, and a diff nobody can read is a diff nobody checks.
    """
    for path, pattern, count in PLACES:
        text = path.read_text(encoding="utf-8")
        replaced, n = pattern.subn(rf"\g<1>{version}\g<3>", text, count=count)
        if n != count:
            raise SystemExit(f"{path.relative_to(ROOT)}: {n} statt {count} Stellen.")
        path.write_text(replaced, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", help="die neue Version, etwa 0.8.0")
    parser.add_argument("--check", action="store_true", help="nur pruefen, nichts schreiben")
    args = parser.parse_args()

    if args.version:
        if not SEMVER.match(args.version):
            print(f'„{args.version}" ist keine Version der Form 1.2.3.')
            return 1
        write(args.version)
        print(f"Version {args.version} an {len(PLACES)} Stellen geschrieben.")
        print("Nicht vergessen: committen, dann taggen.")
        return 0

    values = found()
    differing = {value for _, value in values}
    if len(differing) > 1:
        print("Die Stellen nennen verschiedene Versionen:")
        for path, value in values:
            print(f"  {str(path.relative_to(ROOT)):32} {value}")
        print("\n  Zusammenfuehren mit: make version v=<nummer>")
        return 1

    version = differing.pop()
    print(version if not args.check else f"Version einheitlich an {len(values)} Stellen: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
