#!/usr/bin/env python3

"""Build the register at the top of ``docs/archive/history.de.md`` -- one dated row per section.

    python3 tools/build_register.py            # write it
    python3 tools/build_register.py --check     # fail if it is out of date

The history is a work diary: appended to, never reordered, and by now the largest file in the
repository. It is not read from the front, and it should not be split -- the chronology is the one
thing it offers that the changelog and the decisions do not. What it lacked was a way in.

**The date is the way in.** People look for a day ("what happened around the 9th?"), rarely for a
title; the titles here are mnemonics, not search terms. The dates were in the file all along, but
buried in prose where nothing could reach them.

Generated rather than kept by hand, for the reason ``build_seed.py`` and ``build_notices.py`` are:
a list of ninety rows maintained by hand is wrong within a month, and a register that quietly
omits a section is worse than none. Hence the abort below when a section names no date.

**One rule about dates, without exceptions: a section inherits the date of its part, and a part
that names none passes none on.** Parts I to V are closed blocks -- nobody wrote down which day
stage 4 was built, only that the block ran from the 28th to the 30th of July, so the block says it
once and its sections inherit it. Part VI is a diary and names no date of its own; its sections
must therefore each state theirs, and the abort catches the one that forgets.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# One rule at one place: the anchor checker owns the slug rule, this builds links against it. Both
# run as ``python3 tools/<name>.py``, so ``tools`` is on the path.
from check_anchors import slug

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "docs" / "archive" / "history.de.md"

BEGIN = "<!-- register:anfang -- erzeugt von tools/build_register.py, nicht von Hand ändern -->"
END = "<!-- register:ende -->"

MONTHS = {
    m: i
    for i, m in enumerate(
        "Januar Februar März April Mai Juni Juli August September Oktober November "
        "Dezember".split(),
        start=1,
    )
}

#: A section states its date in the first few lines, as ```hash` · 3. August 2026.`` or as the
#: opening words of its first paragraph. Both forms grew naturally and both are kept; only the
#: date is read, the commit hashes beside it are for the reader.
#:
#: The optional prefix is what makes a range one date rather than two. It has to allow a month of
#: its own -- ``31. Juli – 2. August 2026`` crosses one, and without that the pattern quietly
#: matched the tail alone and part V lost the day it began.
_MONTH = "(?:" + "|".join(MONTHS) + ")"
DATE = re.compile(
    rf"(?:\d{{1,2}}\.(?:\s*{_MONTH})?\s*(?:und|bis|–|-)\s*)?"
    rf"(\d{{1,2}})\.\s*({_MONTH})\s+(20\d{{2}})"
)

#: How far below a heading the date may stand. Four lines covers the blank line, the commit line
#: and a paragraph that opens with the date; more would start catching the next section's dates.
LOOKAHEAD = 4


def date_below(lines: list[str], index: int) -> str | None:
    """The date a section states, as it is written -- ``"4.–5. August 2026"``.

    Returned verbatim rather than normalised: a section that took two days says so, and flattening
    that to one date would be a small lie in a file whose whole point is what actually happened.
    """
    for line in lines[index + 1 : index + 1 + LOOKAHEAD]:
        match = DATE.search(line)
        if match:
            return match.group(0)
    return None


def sortable(date: str) -> tuple[int, int, int]:
    """Year, month, day -- the end of a range, which is close enough to order two-day entries."""
    match = DATE.search(date)
    assert match is not None
    return int(match.group(3)), MONTHS[match.group(2)], int(match.group(1))


@dataclass
class Entry:
    """One row of the register: a part heading, or a section beneath one."""

    date: str | None
    heading: str
    is_part: bool = False
    #: For a part: the dates of its sections, which give it its span.
    covers: list[str] = field(default_factory=list)


def span(dates: list[str]) -> str:
    """``"2. August – 21. August 2026"`` -- the range a part covers, from its sections."""
    if not dates:
        return "--"
    first, last = min(dates, key=sortable), max(dates, key=sortable)
    if first == last:
        return first
    # The year is written once, at the end, when both ends share it.
    year = sortable(first)[0]
    if year == sortable(last)[0]:
        first = first.removesuffix(f" {year}")
    return f"{first} – {last}"


def register(text: str) -> str:
    """The table, from the headings and the dates beneath them."""
    lines = text.splitlines()
    entries: list[Entry] = []
    undated, order = [], []
    part: Entry | None = None

    # The chronicle starts after the generated block. Everything before it carries no dates: the
    # title, the table of neighbouring files, the note that the file is closed, the number register
    # -- and the block's own heading, which would otherwise count as a section. A list of headings
    # to exclude by name would have to grow with every one of them.
    chronicle = lines.index(END)

    for index, line in enumerate(lines):
        if index < chronicle:
            continue
        match = re.match(r"^(#{1,2}) (.+)$", line)
        if not match:
            continue
        level, heading = match.group(1), match.group(2)
        date = date_below(lines, index)

        if level == "#":
            # A new part: whatever it states is what its sections inherit -- nothing, if it
            # states nothing. Its own date is filled in below, from the span of its sections.
            part = Entry(date, heading, is_part=True)
            entries.append(part)
            continue

        date = date or (part.date if part else None)
        if date is None:
            undated.append(heading)
            continue
        entries.append(Entry(date, heading))
        order.append((sortable(date), heading))
        if part is not None:
            part.covers.append(date)

    if undated:
        raise SystemExit(
            "No date, and therefore no place in the register:\n  "
            + "\n  ".join(undated)
            + "\n\nEvery section names its date in the first lines below it, for example\n"
            "  `38ead98` · 19. August 2026."
        )

    for (earlier, first), (later, second) in zip(order, order[1:], strict=False):
        if later < earlier:
            print(f"  Note: {second!r} stands before {first!r} but is older.", file=sys.stderr)

    rows = []
    for entry in entries:
        link = f"[{entry.heading}](#{slug(entry.heading)})"
        date = entry.date
        if entry.is_part:
            # A part without a date of its own is dated by its sections -- that way the span of
            # part VI stays right without anyone maintaining it. The table of blocks this register
            # replaced named a commit range instead, and it had been wrong for fifty sections.
            date = date or span(entry.covers)
            link = f"**{link}**"
        rows.append(f"| {date} | {link} |")

    return "\n".join(
        [
            BEGIN,
            "",
            "## Änderungsregister",
            "",
            f"{len(rows)} Einträge. **Gesucht wird hier meist ein Datum**, nicht ein Titel —",
            "die Titel sind Merkhilfen. Für ein Stichwort ist `grep` das bessere Werkzeug; die",
            "Datei ist ausführlich genug dafür.",
            "",
            "| Datum | Abschnitt |",
            "|---|---|",
            *rows,
            "",
            END,
        ]
    )


def replaced(text: str, table: str) -> str:
    """The file with its register brought up to date."""
    if BEGIN not in text:
        raise SystemExit(f"{HISTORY.name} carries no marker {BEGIN!r} -- set it once by hand.")
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head + table + tail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only check, write nothing")
    args = parser.parse_args()

    text = HISTORY.read_text(encoding="utf-8")
    wanted = replaced(text, register(text))

    if args.check:
        if wanted != text:
            print("The register in docs/archive/history.de.md is out of date: make register")
            return 1
        print("The register is up to date.")
        return 0

    HISTORY.write_text(wanted, encoding="utf-8")
    print(f"Register written: {register(text).count(chr(10) + chr(124)) - 2} entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
