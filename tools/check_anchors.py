#!/usr/bin/env python3
"""Check that every in-page link in the docs points at a heading that exists.

    python3 tools/check_anchors.py

The backlog links its points to one another by anchor. Those links break silently: a renamed
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

#: Files whose in-page links are checked. Anchors only ever point inside their own file here.
DOCUMENTS = ("docs/backlog.md", "docs/decisions.md", "docs/history.md", "docs/index.md")


def slug(heading: str) -> str:
    """GitHub's rule: lower case, drop anything but letters, digits, spaces and hyphens.

    Umlauts survive -- they are letters. The middle dot in "7 · Titel" does not, which is why the
    anchor of such a heading carries two hyphens in a row.
    """
    lowered = heading.strip().lower()
    kept = "".join(c for c in lowered if c.isalnum() or c in " -_" or unicodedata.combining(c))
    return kept.replace(" ", "-")


def check(path: Path) -> list[str]:
    """The dead anchors of one file, empty when all of them resolve."""
    text = path.read_text(encoding="utf-8")
    headings = {slug(match.group(1)) for match in re.finditer(r"^#{2,6} (.+)$", text, re.M)}
    links = re.findall(r"\]\(#([^)]+)\)", text)
    return [link for link in links if link not in headings]


def main() -> int:
    broken = 0
    for name in DOCUMENTS:
        path = ROOT / name
        if not path.is_file():
            continue
        dead = check(path)
        broken += len(dead)
        print(f"  {name:20} {len(dead):2} tot {dead if dead else ''}")

    print("Kein toter Anker." if not broken else f"{broken} tote Anker.")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
