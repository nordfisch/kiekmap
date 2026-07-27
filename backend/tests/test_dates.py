from datetime import date

import pytest

from app.models import DatePrecision
from app.services.dates import beschriftung, ueberlappt, zeitraum


class TestZeitraum:
    def test_tag(self):
        assert zeitraum(1932, 5, 14) == (date(1932, 5, 14), date(1932, 5, 14), DatePrecision.DAY)

    def test_monat_endet_am_letzten_tag(self):
        assert zeitraum(1932, 2)[1] == date(1932, 2, 29), "1932 war ein Schaltjahr"
        assert zeitraum(1933, 2)[1] == date(1933, 2, 28)

    def test_jahr(self):
        assert zeitraum(1932) == (date(1932, 1, 1), date(1932, 12, 31), DatePrecision.YEAR)

    def test_jahrzehnt_rundet_auf_den_beginn_ab(self):
        # "Irgendwann in den Dreissigern" wird als 1934 eingegeben -- gemeint ist 1930-1939.
        von, bis, _ = zeitraum(1934, genauigkeit=DatePrecision.DECADE)
        assert (von, bis) == (date(1930, 1, 1), date(1939, 12, 31))

    def test_ohne_jahr_bleibt_alles_offen(self):
        assert zeitraum(None) == (None, None, DatePrecision.UNKNOWN)

    def test_genauigkeit_ergibt_sich_aus_der_angabe(self):
        assert zeitraum(1932)[2] == DatePrecision.YEAR
        assert zeitraum(1932, 5)[2] == DatePrecision.MONTH
        assert zeitraum(1932, 5, 14)[2] == DatePrecision.DAY

    def test_unvollstaendige_angabe_wird_abgelehnt(self):
        with pytest.raises(ValueError):
            zeitraum(1932, genauigkeit=DatePrecision.DAY)


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
    def test_beschriftung(self, jahr, monat, tag, genauigkeit, erwartet):
        von, bis, g = zeitraum(jahr, monat, tag, genauigkeit)
        assert beschriftung(von, bis, g) == erwartet


class TestUeberlappung:
    """Der Fall, der bei naiver Datumsabfrage still falsch wird."""

    def test_jahrzehnt_erscheint_bei_auswahl_mittendrin(self):
        # Ein auf "1920er" datiertes Foto MUSS erscheinen, wenn der Besucher 1925-1930 waehlt.
        # Genau das geht verloren, wenn man einen einzelnen Datumswert vergleicht.
        von, bis, _ = zeitraum(1920, genauigkeit=DatePrecision.DECADE)
        assert ueberlappt(von, bis, date(1925, 1, 1), date(1930, 12, 31))

    def test_beruehrung_am_rand_zaehlt(self):
        von, bis, _ = zeitraum(1920, genauigkeit=DatePrecision.DECADE)
        assert ueberlappt(von, bis, date(1929, 12, 31), date(1950, 1, 1))
        assert ueberlappt(von, bis, date(1900, 1, 1), date(1920, 1, 1))

    def test_ausserhalb_erscheint_nicht(self):
        von, bis, _ = zeitraum(1920, genauigkeit=DatePrecision.DECADE)
        assert not ueberlappt(von, bis, date(1940, 1, 1), date(1950, 1, 1))

    def test_undatiertes_foto_erscheint_in_keiner_auswahl(self):
        # Solche Fotos gehoeren in den "Hilf mit"-Bereich, nicht auf die Karte.
        assert not ueberlappt(None, None, date(1900, 1, 1), date(2000, 1, 1))
