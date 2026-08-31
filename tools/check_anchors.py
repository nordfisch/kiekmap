#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Check that every in-page link in the docs points at a heading that exists.

    python3 tools/check_anchors.py

The documents link to one another by anchor. Those links break silently: a renamed
heading, a dissolved point, a heading removed along with its neighbour -- the file still renders,
and only a reader following the link notices. That happened while the backlog was being reworked,
which is why this exists.

Deliberately **not** a test: it checks documentation, not behaviour, and a red test suite over a
renamed heading would train people to ignore the suite.
"""

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Files whose links are checked -- and whose headings other files may point at.
#:
#: The two manuals joined the list on 15 August 2026, after a rewritten section left a link in
#: ``operations.md`` pointing nowhere and nothing noticed. They are the files the museum team and
#: whoever keeps the device running actually read; a link that goes nowhere there costs more than
#: one in the backlog.
#:
#: ``architecture.md`` was missing until 21 August 2026 -- an oversight, not a decision. Nothing
#: had noticed, because until then nobody had linked into it or out of it by anchor.
DOCUMENTS = (
    "docs/decisions.md",
    "docs/history.md",
    "docs/index.md",
    "docs/architecture.md",
    "docs/adaption.md",
    "docs/development.md",
    "docs/licensing.md",
    "docs/operations.md",
    "docs/usermanual.md",
    "README.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
)


def slug(heading: str) -> str:
    """GitHub's rule: lower case, drop anything but letters, digits, spaces and hyphens.

    Umlauts survive -- they are letters. The middle dot in "7 · Titel" does not, which is why the
    anchor of such a heading carries two hyphens in a row.
    """
    lowered = heading.strip().lower()
    kept = "".join(c for c in lowered if c.isalnum() or c in " -_" or unicodedata.combining(c))
    return kept.replace(" ", "-")


def headings_of(path: Path) -> set[str]:
    """The anchors a file offers.

    ``#`` counts. It used to start at ``##``, on the assumption that a level-one heading is a
    document title and nothing links to it -- until the register in ``history.md`` linked to its
    six parts and all six were reported dead. Only ever adds anchors, so nothing that passed
    before can fail now.
    """
    text = path.read_text(encoding="utf-8")
    return {slug(match.group(1)) for match in re.finditer(r"^#{1,6} (.+)$", text, re.M)}


def check(path: Path, headings: dict[str, set[str]]) -> list[str]:
    """The dead anchors of one file, empty when all of them resolve.

    **Both kinds count.** ``](#anchor)`` points inside the file; ``](other.md#anchor)`` points
    into a neighbour, and that is the kind that breaks unnoticed -- whoever rewrites a section
    reads their own file, not the three that link into it. A link to a file outside the list is
    left alone: we do not know its headings, and guessing would be noise.
    """
    text = path.read_text(encoding="utf-8")
    dead = [link for link in re.findall(r"\]\(#([^)]+)\)", text) if link not in headings[path.name]]

    for target, anchor in re.findall(r"\]\(([\w./-]+\.md)#([^)]+)\)", text):
        name = Path(target).name
        if name in headings and anchor not in headings[name]:
            dead.append(f"{name}#{anchor}")
    return dead


def main() -> int:
    paths = [ROOT / name for name in DOCUMENTS if (ROOT / name).is_file()]
    headings = {path.name: headings_of(path) for path in paths}

    broken = 0
    for path in paths:
        name = str(path.relative_to(ROOT))
        dead = check(path, headings)
        broken += len(dead)
        print(f"  {name:20} {len(dead):2} tot {dead if dead else ''}")

    print("Kein toter Anker." if not broken else f"{broken} tote Anker.")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
