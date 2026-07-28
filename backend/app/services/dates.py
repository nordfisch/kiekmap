"""Fuzzy dating.

For historical photos, "the 1920s" or "around 1930" is the normal case, not the exception. Each
photo therefore stores an interval rather than a point in time, and the time filter queries for
overlap.

The pitfall this avoids: with the obvious query ("date between from and to") exactly the loosely
dated photos drop out of the view -- the interesting ones. It happens silently, which is why there
are dedicated tests for it.
"""

import calendar
from datetime import date

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
