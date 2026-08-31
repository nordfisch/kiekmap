"""Fuzzy dating.

For historical photos, "the 1920s" or "around 1930" is the normal case, not the exception. Each
photo therefore stores an interval rather than a point in time, and the time filter queries for
overlap.

The pitfall this avoids: with the obvious query ("date between from and to") exactly the loosely
dated photos drop out of the view -- the interesting ones. It happens silently, which is why there
are dedicated tests for it.
"""

import calendar
from datetime import UTC, date, datetime

from app.models import DatePrecision

#: German month names -- these end up in user-facing labels.
MONTH_NAMES = (
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)

#: Widths a bar of the histogram may have, in years. Readable steps, no odd ones.
BAR_WIDTHS = (1, 5, 10, 25, 50)

#: More bars than this and the strip becomes a hedge rather than a picture.
MAX_BARS = 30


def bar_width(span_years: int, finest: int) -> int:
    """How many years one bar of the time slider covers.

    Two rules, and the first is the one that matters:

    **Never finer than the coarsest dating in the collection.** A photo dated "the 1920s" has
    ``date_from`` on 1 January 1920. Drawn in yearly bars, all ten of its years would pile onto
    1920 -- a tower where in truth a decade lies. That is the mistake the whole date model exists
    to avoid, only in the display. ``finest`` is therefore 10 as soon as one decade dating exists,
    and 1 while every statement fits inside a year.

    **And wide enough that the span stays readable.** Over 130 years yearly bars would be a hedge;
    the width grows until at most ``MAX_BARS`` remain.
    """
    for width in BAR_WIDTHS:
        if width >= finest and span_years <= width * MAX_BARS:
            return width
    return BAR_WIDTHS[-1]


def date_range(
    year: int | None,
    month: int | None = None,
    day: int | None = None,
    precision: DatePrecision | None = None,
) -> tuple[date | None, date | None, DatePrecision]:
    """Turn a date statement into an interval.

    Without ``precision`` it follows from what was supplied. For ``DECADE`` the year is rounded
    down to the start of the decade, so "1934, decade" becomes 1930-1939 and not 1934-1943.
    """
    if year is None:
        return None, None, DatePrecision.UNKNOWN

    if precision is None:
        if day is not None and month is not None:
            precision = DatePrecision.DAY
        elif month is not None:
            precision = DatePrecision.MONTH
        else:
            precision = DatePrecision.YEAR

    match precision:
        case DatePrecision.DAY:
            if month is None or day is None:
                raise ValueError("day precision needs both month and day")
            exact = date(year, month, day)
            return exact, exact, DatePrecision.DAY

        case DatePrecision.MONTH:
            if month is None:
                raise ValueError("month precision needs a month")
            last = calendar.monthrange(year, month)[1]
            return date(year, month, 1), date(year, month, last), DatePrecision.MONTH

        case DatePrecision.YEAR:
            return date(year, 1, 1), date(year, 12, 31), DatePrecision.YEAR

        case DatePrecision.DECADE:
            start = year - year % 10
            return date(start, 1, 1), date(start + 9, 12, 31), DatePrecision.DECADE

        case DatePrecision.UNKNOWN:
            return None, None, DatePrecision.UNKNOWN

    raise ValueError(f"unknown precision: {precision}")


def format_label(start: date | None, end: date | None, precision: str | DatePrecision) -> str:
    """How the dating is shown to the visitor. German, because it reaches the screen."""
    if start is None:
        return "Jahr unbekannt"

    match DatePrecision(precision):
        case DatePrecision.DAY:
            return f"{start.day}. {MONTH_NAMES[start.month - 1]} {start.year}"
        case DatePrecision.MONTH:
            return f"{MONTH_NAMES[start.month - 1]} {start.year}"
        case DatePrecision.YEAR:
            return str(start.year)
        case DatePrecision.DECADE:
            return f"{start.year}er"
        case _:
            # Should not occur with start != None; better something usable than nothing.
            return (
                str(start.year)
                if end is None or end.year == start.year
                else f"{start.year}–{end.year}"
            )


def format_short(start: date | None, precision: str | DatePrecision) -> str:
    """The dating as it fits under a thumbnail on the map. German, empty where nothing is known.

    Three differences to :func:`format_label`, and each answers something the map does badly:

      * **Day and month collapse to the year.** "22. März 2014" under a 160 px picture on an
        overview map claims a precision nobody is looking for there; the year is the question a
        map answers.
      * **A decade stays a decade.** "1930er" is not a rounded year but the whole of what is
        known, and shortening it to "1930" would invent a precision.
      * **Undated is empty, not "Jahr unbekannt".** Two thirds of this collection carry no date,
        and seven hundred identical lines say nothing about seven hundred pictures. The caption
        then holds the address alone.
    """
    if start is None:
        return ""
    if DatePrecision(precision) is DatePrecision.DECADE:
        return f"{start.year}er"
    return str(start.year)


def overlaps(
    start: date | None, end: date | None, selected_start: date, selected_end: date
) -> bool:
    """Pure-Python counterpart to the SQL query -- for tests and as documentation.

    Two intervals overlap when neither lies entirely before the other. An undated photo never
    overlaps: it appears in no time selection, but in the "Hilf mit" panel instead.
    """
    if start is None or end is None:
        return False
    return start <= selected_end and end >= selected_start


def utc_now() -> datetime:
    """Now, in the shape everything stored has: UTC, without the marker saying so.

    One clock for the device. SQLite's ``func.now()`` writes UTC, the JSON state files write UTC,
    and a column filled from Python has to match -- a naive local timestamp beside a naive UTC one
    is a difference nothing in the schema catches and nothing in the reading notices. It stood in
    ``reverted_at`` for weeks: a contribution taken back immediately was logged two hours after
    itself. See docs/decisions.md, point 58.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def days_since(when: datetime, now: datetime | None = None) -> int:
    """How many days ago, counted in calendar days rather than in 24-hour blocks.

    The distinction matters because the answer is read out as a sentence: a backup made yesterday
    at 09:00 must be "1 Tag" this morning, not "Heute". Subtracting the timestamps would give a
    zero for another hour.

    Stored timestamps are UTC throughout (``func.now()`` in SQLite, ``datetime.now(UTC)`` in the
    JSON state files). The day boundary that counts, however, is the local one -- so both sides are
    converted before their dates are compared.
    """
    then = when.replace(tzinfo=UTC).astimezone()
    today = (now or datetime.now(UTC)).astimezone()
    return (today.date() - then.date()).days
