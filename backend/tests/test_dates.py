from datetime import UTC, date, datetime, timedelta

import pytest

from app.models import DatePrecision
from app.services.dates import date_range, days_since, format_label, overlaps


class TestZeitraum:
    def test_tag(self):
        assert date_range(1932, 5, 14) == (date(1932, 5, 14), date(1932, 5, 14), DatePrecision.DAY)

    def test_monat_endet_am_letzten_tag(self):
        assert date_range(1932, 2)[1] == date(1932, 2, 29), "1932 war ein Schaltjahr"
        assert date_range(1933, 2)[1] == date(1933, 2, 28)

    def test_jahr(self):
        assert date_range(1932) == (date(1932, 1, 1), date(1932, 12, 31), DatePrecision.YEAR)

    def test_jahrzehnt_rundet_auf_den_beginn_ab(self):
        # "Irgendwann in den Dreissigern" wird als 1934 eingegeben -- gemeint ist 1930-1939.
        von, bis, _ = date_range(1934, precision=DatePrecision.DECADE)
        assert (von, bis) == (date(1930, 1, 1), date(1939, 12, 31))

    def test_ohne_jahr_bleibt_alles_offen(self):
        assert date_range(None) == (None, None, DatePrecision.UNKNOWN)

    def test_genauigkeit_ergibt_sich_aus_der_angabe(self):
        assert date_range(1932)[2] == DatePrecision.YEAR
        assert date_range(1932, 5)[2] == DatePrecision.MONTH
        assert date_range(1932, 5, 14)[2] == DatePrecision.DAY

    def test_unvollstaendige_angabe_wird_abgelehnt(self):
        with pytest.raises(ValueError):
            date_range(1932, precision=DatePrecision.DAY)


class TestBeschriftung:
    @pytest.mark.parametrize(
        ("jahr", "monat", "tag", "genauigkeit", "erwartet"),
        [
            (1932, 5, 14, None, "14. Mai 1932"),
            (1932, 5, None, None, "Mai 1932"),
            (1932, None, None, None, "1932"),
            (1926, None, None, DatePrecision.DECADE, "1920er"),
            (None, None, None, None, "Jahr unbekannt"),
        ],
    )
    def test_format_label(self, jahr, monat, tag, genauigkeit, erwartet):
        von, bis, g = date_range(jahr, monat, tag, genauigkeit)
        assert format_label(von, bis, g) == erwartet


class TestUeberlappung:
    """Der Fall, der bei naiver Datumsabfrage still falsch wird."""

    def test_jahrzehnt_erscheint_bei_auswahl_mittendrin(self):
        # Ein auf "1920er" datiertes Foto MUSS erscheinen, wenn der Besucher 1925-1930 waehlt.
        # Genau das geht verloren, wenn man einen einzelnen Datumswert vergleicht.
        von, bis, _ = date_range(1920, precision=DatePrecision.DECADE)
        assert overlaps(von, bis, date(1925, 1, 1), date(1930, 12, 31))

    def test_beruehrung_am_rand_zaehlt(self):
        von, bis, _ = date_range(1920, precision=DatePrecision.DECADE)
        assert overlaps(von, bis, date(1929, 12, 31), date(1950, 1, 1))
        assert overlaps(von, bis, date(1900, 1, 1), date(1920, 1, 1))

    def test_ausserhalb_erscheint_nicht(self):
        von, bis, _ = date_range(1920, precision=DatePrecision.DECADE)
        assert not overlaps(von, bis, date(1940, 1, 1), date(1950, 1, 1))

    def test_undatiertes_foto_erscheint_in_keiner_auswahl(self):
        # Solche Fotos gehoeren in den "Hilf mit"-Bereich, nicht auf die Karte.
        assert not overlaps(None, None, date(1900, 1, 1), date(2000, 1, 1))


class TestTageSeitdem:
    """Kalendertage, nicht 24-Stunden-Bloecke -- die Uebersicht liest das Ergebnis als Satz vor."""

    @staticmethod
    def _gespeichert(zeitpunkt: datetime) -> datetime:
        """Wie das Geraet einen Zeitpunkt ablegt: UTC, ohne Zeitzonenkennung."""
        return zeitpunkt.astimezone(UTC).replace(tzinfo=None)

    def test_gestern_mittag_ist_ein_tag_her(self):
        """Der Fall, der in 24-Stunden-Bloecken still zur Null wird.

        Zwanzig Stunden sind weniger als ein Tag -- gemeint ist trotzdem "gestern", und genau das
        steht dann auf der Kachel.
        """
        heute_frueh = datetime.now().astimezone().replace(hour=8, minute=0, second=0, microsecond=0)
        gestern_mittag = heute_frueh - timedelta(hours=20)

        assert days_since(self._gespeichert(gestern_mittag), heute_frueh.astimezone(UTC)) == 1

    def test_heute_ist_null(self):
        jetzt = datetime.now().astimezone().replace(hour=14, minute=0, second=0, microsecond=0)
        vorhin = jetzt - timedelta(hours=3)

        assert days_since(self._gespeichert(vorhin), jetzt.astimezone(UTC)) == 0

    def test_abends_gespeichertes_gehoert_noch_zum_selben_tag(self):
        """Die Tagesgrenze ist die deutsche, nicht die von Greenwich.

        Um 23:30 Uhr Ortszeit ist es in UTC schon der naechste Tag. Wer stur in UTC rechnet,
        macht daraus einen Tag Unterschied.
        """
        spaet = datetime.now().astimezone().replace(hour=23, minute=30, second=0, microsecond=0)
        kurz_danach = spaet + timedelta(minutes=15)

        assert days_since(self._gespeichert(spaet), kurz_danach.astimezone(UTC)) == 0
