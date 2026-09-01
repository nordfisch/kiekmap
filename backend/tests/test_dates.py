from datetime import UTC, date, datetime, timedelta

import pytest

from app.models import DatePrecision
from app.services.dates import (
    MAX_BARS,
    bar_width,
    date_range,
    days_since,
    format_label,
    format_short,
    overlaps,
)


class TestBarWidth:
    """How many years one bar of the time slider covers.

    The rule guards against a silent error in the *display*: a photo dated "1920er" carries
    ``date_from = 1920-01-01``, and with year bars all ten years of it would land on a single bar.
    """

    def test_a_year_precise_collection_gets_year_bars(self):
        assert bar_width(span_years=15, finest=1) == 1

    def test_one_decade_in_the_collection_forbids_year_bars(self):
        """Even for a short span -- the precision decides, not the length."""
        assert bar_width(span_years=15, finest=10) == 10

    def test_a_long_span_is_bundled(self):
        """Otherwise 130 bars would stand side by side, too narrow to read."""
        width = bar_width(span_years=130, finest=1)

        assert width > 1
        assert 130 / width <= MAX_BARS

    def test_the_span_always_fits_in_thirty_bars(self):
        for span in (0, 1, 29, 30, 31, 200, 500):
            width = bar_width(span_years=span, finest=1)
            assert span / width <= MAX_BARS, f"span {span} exceeds the bar limit"

    def test_a_very_old_collection_stays_within_the_widths(self):
        """Beyond the widest step nothing is calculated; the widest one is taken as it is."""
        assert bar_width(span_years=5000, finest=1) == 50

    def test_an_empty_collection_stays_with_the_year(self):
        """Without datings the span is zero -- that must not become a division by zero."""
        assert bar_width(span_years=0, finest=1) == 1


class TestDateRange:
    def test_day(self):
        assert date_range(1932, 5, 14) == (date(1932, 5, 14), date(1932, 5, 14), DatePrecision.DAY)

    def test_a_month_ends_on_its_last_day(self):
        assert date_range(1932, 2)[1] == date(1932, 2, 29), "1932 was a leap year"
        assert date_range(1933, 2)[1] == date(1933, 2, 28)

    def test_year(self):
        assert date_range(1932) == (date(1932, 1, 1), date(1932, 12, 31), DatePrecision.YEAR)

    def test_a_decade_rounds_down_to_its_beginning(self):
        # "Irgendwann in den Dreissigern" is entered as 1934 -- what is meant is 1930-1939.
        start, end, _ = date_range(1934, precision=DatePrecision.DECADE)
        assert (start, end) == (date(1930, 1, 1), date(1939, 12, 31))

    def test_without_a_year_everything_stays_open(self):
        assert date_range(None) == (None, None, DatePrecision.UNKNOWN)

    def test_precision_follows_from_what_was_given(self):
        assert date_range(1932)[2] == DatePrecision.YEAR
        assert date_range(1932, 5)[2] == DatePrecision.MONTH
        assert date_range(1932, 5, 14)[2] == DatePrecision.DAY

    def test_an_incomplete_entry_is_rejected(self):
        with pytest.raises(ValueError):
            date_range(1932, precision=DatePrecision.DAY)


class TestLabel:
    @pytest.mark.parametrize(
        ("year", "month", "day", "precision", "expected"),
        [
            (1932, 5, 14, None, "14. Mai 1932"),
            (1932, 5, None, None, "Mai 1932"),
            (1932, None, None, None, "1932"),
            (1926, None, None, DatePrecision.DECADE, "1920er"),
            (None, None, None, None, "Jahr unbekannt"),
        ],
    )
    def test_format_label(self, year, month, day, precision, expected):
        start, end, found = date_range(year, month, day, precision)
        assert format_label(start, end, found) == expected


class TestShortLabel:
    """What stands under a thumbnail on the map.

    Three differences from the written-out form, and each one fixes something the map does badly.
    The day does not belong under an image 160 px wide; a decade stays a decade; and „Jahr
    unbekannt" seven hundred times below one another says nothing about seven hundred images.
    """

    @pytest.mark.parametrize(
        ("year", "month", "day", "precision", "expected"),
        [
            (2014, 3, 22, None, "2014"),
            (1955, 6, None, None, "1955"),
            (1932, None, None, None, "1932"),
            (1926, None, None, DatePrecision.DECADE, "1920er"),
            (None, None, None, None, ""),
        ],
    )
    def test_format_short(self, year, month, day, precision, expected):
        start, _, found = date_range(year, month, day, precision)
        assert format_short(start, found) == expected

    def test_a_decade_is_not_shortened_to_a_year(self):
        """The case that would silently invent a precision that does not exist.

        Shortening „1930er" to „1930" looks like tidying up and claims a year nobody knows -- the
        same mistake the whole data model works with intervals to avoid.
        """
        start, _, found = date_range(1937, None, None, DatePrecision.DECADE)

        assert format_short(start, found) == "1930er"

    def test_without_a_dating_the_line_stays_empty(self):
        # Not „Jahr unbekannt": the address then stands under the image on its own, and that is
        # information rather than a notice of absence.
        assert format_short(None, DatePrecision.UNKNOWN) == ""


class TestOverlap:
    """The case that goes silently wrong with a naive date query."""

    def test_a_decade_appears_when_the_selection_starts_inside_it(self):
        # A photo dated "1920er" MUST appear when the visitor selects 1925-1930. That is exactly
        # what is lost by comparing a single date value.
        start, end, _ = date_range(1920, precision=DatePrecision.DECADE)
        assert overlaps(start, end, date(1925, 1, 1), date(1930, 12, 31))

    def test_touching_at_the_edge_counts(self):
        start, end, _ = date_range(1920, precision=DatePrecision.DECADE)
        assert overlaps(start, end, date(1929, 12, 31), date(1950, 1, 1))
        assert overlaps(start, end, date(1900, 1, 1), date(1920, 1, 1))

    def test_outside_does_not_appear(self):
        start, end, _ = date_range(1920, precision=DatePrecision.DECADE)
        assert not overlaps(start, end, date(1940, 1, 1), date(1950, 1, 1))

    def test_an_undated_photo_appears_in_no_selection(self):
        # Such photos belong in the contribution panel, not on the map.
        assert not overlaps(None, None, date(1900, 1, 1), date(2000, 1, 1))


class TestDaysSince:
    """Calendar days, not 24-hour blocks -- the overview reads the result out as a sentence."""

    @staticmethod
    def _stored(moment: datetime) -> datetime:
        """How the device files a point in time: UTC, without a time zone marker."""
        return moment.astimezone(UTC).replace(tzinfo=None)

    def test_yesterday_noon_is_one_day_ago(self):
        """The case that silently becomes zero in 24-hour blocks.

        Twenty hours are less than a day -- what is meant is still "yesterday", and that is what
        the tile then says.
        """
        now = datetime.now().astimezone()
        this_morning = now.replace(hour=8, minute=0, second=0, microsecond=0)
        yesterday_noon = this_morning - timedelta(hours=20)

        assert days_since(self._stored(yesterday_noon), this_morning.astimezone(UTC)) == 1

    def test_today_is_zero(self):
        now = datetime.now().astimezone().replace(hour=14, minute=0, second=0, microsecond=0)
        earlier = now - timedelta(hours=3)

        assert days_since(self._stored(earlier), now.astimezone(UTC)) == 0

    def test_saved_in_the_evening_still_belongs_to_the_same_day(self):
        """The day boundary is the German one, not the one at Greenwich.

        At 23:30 local time it is already the next day in UTC. Calculating strictly in UTC turns
        that into a difference of one day.
        """
        late = datetime.now().astimezone().replace(hour=23, minute=30, second=0, microsecond=0)
        shortly_after = late + timedelta(minutes=15)

        assert days_since(self._stored(late), shortly_after.astimezone(UTC)) == 0
