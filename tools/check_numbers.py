#!/usr/bin/env python3
"""Check the backlog's own bookkeeping -- the numbers it keeps about itself.

    python3 tools/check_numbers.py

The backlog hands out a number once and never again: an open point, a retired one, and the next
free number together have to account for every number ever given. That is easy to state and easy
to get wrong by hand -- a point that moves to the history has to leave the overview table, join
the retired list, raise the count word in front of it, and possibly move the next free number.
Four edits in three places for one move.

**Deliberately not a test**, like its two neighbours: it checks documentation, not behaviour.

What it does *not* do is count the numbers that stand in prose, although that was the first idea.
Measured on 19 August 2026, the pattern "N Punkte" matches four places in the docs and **not one
of them should be updated**: two quote the wrong old figures on purpose, two are about points on a
map, and one is a sentence in the history that was true on its date and has to stay that way. A
count in prose is either a quotation or a record. The two places that were meant to be current
lost their numbers instead; see docs/decisions.md, point 59.
"""

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BACKLOG = ROOT / "docs/backlog.md"
DECISIONS = ROOT / "docs/decisions.md"

_EINER = (
    "",
    "ein",
    "zwei",
    "drei",
    "vier",
    "fünf",
    "sechs",
    "sieben",
    "acht",
    "neun",
)
_ZEHNER = (
    "",
    "zehn",
    "zwanzig",
    "dreißig",
    "vierzig",
    "fünfzig",
    "sechzig",
    "siebzig",
    "achtzig",
    "neunzig",
)
_TEENS = {
    11: "elf",
    12: "zwölf",
    13: "dreizehn",
    14: "vierzehn",
    15: "fünfzehn",
    16: "sechzehn",  # not "sechszehn"
    17: "siebzehn",  # not "siebenzehn"
    18: "achtzehn",
    19: "neunzehn",
}


def number_word(value: int) -> str:
    """The German word for 1..99, as it stands at the start of the sentence.

    Only that range, because the backlog will not outgrow it -- and a converter that also handles
    thousands would be more code than the sentence it guards.
    """
    if value in _TEENS:
        return _TEENS[value].capitalize()
    if value < 10:
        word = "eins" if value == 1 else _EINER[value]
    elif value % 10 == 0:
        word = _ZEHNER[value // 10]
    else:
        word = f"{_EINER[value % 10]}und{_ZEHNER[value // 10]}"
    return word.capitalize()


def slug(heading: str) -> str:
    """GitHub's anchor rule -- the same one ``check_anchors.py`` applies."""
    lowered = heading.strip().lower()
    kept = "".join(c for c in lowered if c.isalnum() or c in " -_" or unicodedata.combining(c))
    return kept.replace(" ", "-")


def check_backlog(problems: list[str]) -> None:
    text = BACKLOG.read_text(encoding="utf-8")

    sections = {int(n): title for n, title in re.findall(r"^### (\d+) · (.+)$", text, re.M)}
    rows = {
        int(n): anchor
        for n, anchor in re.findall(r"^\| (\d+) \| \[[^\]]+\]\(#([^)]+)\)", text, re.M)
    }

    # 1. Every point stands in both -- the overview table and the running text.
    for number in sorted(set(sections) - set(rows)):
        problems.append(f"Punkt {number} hat einen Abschnitt, steht aber nicht in der Uebersicht")
    for number in sorted(set(rows) - set(sections)):
        problems.append(f"Punkt {number} steht in der Uebersicht, hat aber keinen Abschnitt")

    # 2. And a row points at its *own* point, not at a neighbour. check_anchors only asks
    #    whether an anchor exists, never whether it is the right one.
    for number in sorted(set(rows) & set(sections)):
        expected = slug(f"{number} · {sections[number]}")
        if rows[number] != expected:
            problems.append(f"Punkt {number}: die Zeile verweist auf '{rows[number]}'")

    retired_sentence = re.search(
        r"\*\*(\w+) Nummern sind vergriffen\*\* — (.+?)\. Sie sind", text, re.S
    )
    next_free = re.search(r"bekommt die \*\*(\d+)\*\*", text)
    if retired_sentence is None or next_free is None:
        problems.append("Der Satz ueber die vergriffenen Nummern fehlt oder ist umformuliert")
        return

    retired = [int(value) for value in re.findall(r"\d+", retired_sentence.group(2))]
    following = int(next_free.group(1))

    # 3. A number is open or retired, never both.
    for number in sorted(set(retired) & set(sections)):
        problems.append(f"Punkt {number} steht offen *und* in der Liste der vergriffenen")

    doubled = sorted(n for n in set(retired) if retired.count(n) > 1)
    if doubled:
        problems.append(f"Doppelt in der Liste der vergriffenen: {doubled}")

    # 4. The number word in front of the list.
    word = retired_sentence.group(1)
    expected_word = number_word(len(retired))
    if word != expected_word:
        problems.append(
            f"'{word} Nummern sind vergriffen', gezaehlt sind es {len(retired)} ({expected_word})"
        )

    # 5. Every number ever handed out is either open or retired -- no gap, no overhang. That
    #    is exactly what "numbers are never given out twice" means.
    given = set(retired) | set(sections)
    missing = sorted(set(range(1, following)) - given)
    if missing:
        problems.append(f"Weder offen noch vergriffen, also spurlos verschwunden: {missing}")
    beyond = sorted(number for number in given if number >= following)
    if beyond:
        problems.append(f"Vergeben, obwohl die naechste freie Nummer {following} ist: {beyond}")


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
    check_backlog(problems)
    check_decisions(problems)

    for problem in problems:
        print(f"  {problem}")

    print("Die Buchfuehrung stimmt." if not problems else f"{len(problems)} Unstimmigkeiten.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
