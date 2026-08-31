#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Check the numbering of the decisions -- ascending, and no number twice.

    python3 tools/check_numbers.py

A number is handed out once and never again, so that a citation in an old note points at the same
thing a year later. ``decisions.md`` is the only file that still hands out numbers; the backlog's
numbering ended at 66 when the open points moved into GitHub issues, and what is left of it lives
in the history under its date.

Gaps are allowed and are a statement: point 8 was withdrawn and its number stays vacant.

**Deliberately not a test**, like its neighbours: it checks documentation, not behaviour.

What it does *not* do is count the numbers that stand in prose, although that was the first idea.
Measured, the pattern "N Punkte" matches a handful of places in the docs and **not one of them
should be updated**: several quote the wrong old figure on purpose, several are about points on a
map, and one is a sentence in the history that was true on its date. A count in prose is either a
quotation or a record; see docs/decisions.md, point 59.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DECISIONS = ROOT / "docs/decisions.md"


def check_decisions(problems: list[str]) -> None:
    """The same rule one file over -- but with gaps allowed.

    ``decisions.md`` keeps it like the backlog: point 8 was withdrawn and its number stays vacant,
    with a reason given in the text. So only two things are checked here -- that no number occurs
    twice and that they ascend. A gap in that file is a statement, not a mistake.
    """
    text = DECISIONS.read_text(encoding="utf-8")
    numbers = [int(n) for n in re.findall(r"^## (\d+)\. ", text, re.M)]

    doubled = sorted(n for n in set(numbers) if numbers.count(n) > 1)
    if doubled:
        problems.append(f"decisions.md: Nummer doppelt vergeben: {doubled}")
    if numbers != sorted(numbers):
        problems.append("decisions.md: die Punkte stehen nicht in aufsteigender Reihenfolge")


def main() -> int:
    problems: list[str] = []
    check_decisions(problems)

    for problem in problems:
        print(f"  {problem}")

    print("Die Buchfuehrung stimmt." if not problems else f"{len(problems)} Unstimmigkeiten.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
