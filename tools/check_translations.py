#!/usr/bin/env python3

"""Which translations have drifted away from their source.

    python3 tools/check_translations.py            what is out of date
    python3 tools/check_translations.py --update    write the hashes forward

This is the condition under which the project is allowed to keep a text twice at all. Point 68 had
rejected bilingual documentation for one reason: *"the second copy goes stale and nobody notices."*
That is still true. Point 71 does not deny it -- it answers it with this script.

**The file names decide what is checked, not a list.** ``operations.de.md`` beside
``operations.md`` is a pair, so the German half has to name the hash of the English one. A
``*.de.md`` with no English neighbour is a German original, and originals are not checked:
``history.de.md`` is frozen and takes no further entries. It cannot forget a marker it never
needed.

The marker is an HTML comment in the first lines:

    <!-- translated-from: docs/operations.md -->
    <!-- source-sha: 4f2a1c9… -->

An HTML comment and not YAML front matter, although front matter is the more usual carrier: GitHub
renders front matter as a table at the top of the page, and these files are read in the repository
as well as on the documentation site. A comment shows up in neither.

**What it reports is drift, not wrongness.** A typo fixed in the English source turns the check red
although the German needs no change. That is the intended cost: somebody has to look, decide, and
then run ``--update``. A check that guessed would be a check nobody believes.

**Deliberately not a test**, like its neighbours: it reads documentation, not behaviour.
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE_MARKER = re.compile(r"^<!--\s*translated-from:\s*(\S+)\s*-->\s*$", re.M)
SHA_MARKER = re.compile(r"^<!--\s*source-sha:\s*([0-9a-f]{64})\s*-->\s*$", re.M)

#: How far into the file the markers may stand. They belong at the top; a limit keeps a quoted
#: example further down from being read as the real thing.
MARKER_LINES = 10

#: Any marker line, well formed or not -- ``--update`` strips these before writing a fresh pair.
MARKER_LINE = re.compile(r"^<!--\s*(?:translated-from|source-sha):.*-->\s*$")


def translations() -> list[str]:
    """Every ``*.de.md`` under version control."""
    listed = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT
    ).stdout.split("\n")
    return sorted(name for name in listed if name.endswith(".de.md"))


def source_of(name: str) -> str:
    """The English neighbour of a translation -- ``a/b.de.md`` becomes ``a/b.md``."""
    return name[: -len(".de.md")] + ".md"


def sha_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head(path: Path) -> str:
    """The first lines, where the markers belong."""
    return "\n".join(path.read_text(encoding="utf-8").splitlines()[:MARKER_LINES])


def marked(path: Path) -> tuple[str | None, str | None]:
    """(the source it names, the hash it carries) -- either may be missing."""
    text = head(path)
    named = SOURCE_MARKER.search(text)
    carried = SHA_MARKER.search(text)
    return (named.group(1) if named else None, carried.group(1) if carried else None)


def problems() -> list[str]:
    found = []
    for name in translations():
        path = ROOT / name
        source = source_of(name)
        named, carried = marked(path)

        if not (ROOT / source).is_file():
            if named is not None:
                found.append(f"{name} names {named}, and that file does not exist")
            # No English neighbour and no marker: a German original. Nothing to check.
            continue

        if named is None or carried is None:
            found.append(f"{name} has an English source ({source}) but carries no marker")
            continue
        if named != source:
            found.append(f"{name} names {named}, but its source by name is {source}")
            continue

        current = sha_of(ROOT / source)
        if carried != current:
            found.append(f"{name} was made from an older {source}")
    return found


def update() -> int:
    """Write the current hash of every source into its translation."""
    written = 0
    for name in translations():
        path = ROOT / name
        source = source_of(name)
        if not (ROOT / source).is_file():
            continue

        current = sha_of(ROOT / source)
        text = path.read_text(encoding="utf-8")
        named, carried = marked(path)

        if carried == current and named == source:
            continue
        # Strip whatever marker lines the head carries and write one correct pair above them.
        # Repairing rather than prepending: a half-written marker -- a source line with a
        # malformed hash under it -- used to get a fresh pair put on top and left the old line
        # orphaned below. A stale second copy, in the file whose purpose is to catch those.
        kept = [
            line
            for i, line in enumerate(text.splitlines())
            if not (i < MARKER_LINES and MARKER_LINE.match(line))
        ]
        while kept and not kept[0].strip():
            kept.pop(0)
        marker = f"<!-- translated-from: {source} -->\n<!-- source-sha: {current} -->\n\n"
        path.write_text(marker + "\n".join(kept) + "\n", encoding="utf-8")

        print(f"  {name}  <- {source}")
        written += 1

    print(f"{written} markers written." if written else "Every marker was already current.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update", action="store_true", help="write the hash of each source forward"
    )
    args = parser.parse_args()

    if args.update:
        return update()

    pairs = [name for name in translations() if (ROOT / source_of(name)).is_file()]
    found = problems()
    if not found:
        print(f"{len(pairs)} translations, none adrift.")
        return 0

    print(f"\n{len(found)} of {len(translations())} translations need looking at:")
    for problem in found:
        print(f"  {problem}")
    print("\n  Pull the translation along, then: python3 tools/check_translations.py --update")
    return 1


if __name__ == "__main__":
    sys.exit(main())
