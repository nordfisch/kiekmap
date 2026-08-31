"""Tests fuer die Rechnung hinter dem Ortsindex.

Die Zahlen stammen aus dem echten Fall: Im Ausschnitt fuer Holm liegen siebzehn Strassen namens
"Hauptstrasse". Der Index fuehrte sie als eine und mittelte ihre Punkte -- der Vertreter lag
danach 490 m von der naechsten echten Hauptstrasse entfernt und 2,26 km von Holms Ortsmitte.
"""

from itertools import pairwise

import pytest
from geometry import (
    by_housenumber,
    distance_m,
    group_lines,
    lowest_housenumber,
    median_housenumber,
    nearest_group,
    representative_point,
)

#: Holms Ortsmitte aus tiles/region.json, als (lat, lon).
HOLM = (53.62053, 9.67601)


class TestVertreterpunkt:
    def test_gerade_strasse_wird_in_der_mitte_vertreten(self):
        linie = [(53.620, 9.670), (53.620, 9.680)]
        lat, lon = representative_point([linie])
        assert lat == pytest.approx(53.620, abs=1e-6)
        assert lon == pytest.approx(9.675, abs=1e-4)

    def test_punkt_liegt_auf_der_strasse_und_nicht_daneben(self):
        # Eine L-foermige Strasse. Der Schwerpunkt ihrer Stuetzpunkte liegt in der Ecke des
        # umschliessenden Rechtecks -- also neben der Fahrbahn. Genau das war der Fehler.
        linie = [(53.620, 9.670), (53.620, 9.680), (53.630, 9.680)]
        punkt = representative_point([linie])

        abstand = min(_abstand_zur_strecke(punkt, a, b) for a, b in pairwise(linie))
        assert abstand < 1.0, "der Vertreterpunkt muss auf dem Strassenverlauf liegen"

    def test_lange_strasse_ohne_zwischenpunkte_endet_nicht_am_rand(self):
        # Zwei Stuetzpunkte, ein Kilometer dazwischen. Wer nur unter den Stuetzpunkten sucht,
        # landet an einem Ende -- deshalb wird auf die Strecke projiziert.
        linie = [(53.615, 9.676), (53.624, 9.676)]
        punkt = representative_point([linie])
        assert distance_m(punkt, linie[0]) > 400
        assert distance_m(punkt, linie[1]) > 400

    def test_mehrere_stuecke_werden_zusammen_vertreten(self):
        stueck_a = [(53.620, 9.670), (53.620, 9.675)]
        stueck_b = [(53.620, 9.675), (53.620, 9.680)]
        assert representative_point([stueck_a, stueck_b]) == pytest.approx(
            representative_point([[(53.620, 9.670), (53.620, 9.680)]]), abs=1e-4
        )

    def test_ohne_punkte_wird_nicht_geraten(self):
        with pytest.raises(ValueError):
            representative_point([])


class TestGruppieren:
    def test_zwei_doerfer_ergeben_zwei_strassen(self):
        # Der eigentliche Fehlerfall: gleicher Name, kilometerweit auseinander.
        in_holm = [(53.6205, 9.6727), (53.6210, 9.6740)]
        im_nachbarort = [(53.6550, 9.6582), (53.6555, 9.6590)]
        assert len(group_lines([in_holm, im_nachbarort])) == 2

    def test_anschliessende_stuecke_bleiben_eine_strasse(self):
        # Aufeinanderfolgende Wegstuecke teilen ihren Endpunkt -- Abstand null.
        erst = [(53.620, 9.670), (53.620, 9.675)]
        dann = [(53.620, 9.675), (53.620, 9.680)]
        assert len(group_lines([erst, dann])) == 1

    def test_eine_lange_strasse_zerfaellt_nicht(self):
        # Drei Stuecke, Anfang und Ende ueber einen Kilometer auseinander. Ohne die transitive
        # Verkettung wuerde die Strasse in Teile zerfallen und jedes Teil einen Punkt bekommen.
        stuecke = [
            [(53.615, 9.676), (53.618, 9.676)],
            [(53.618, 9.676), (53.621, 9.676)],
            [(53.621, 9.676), (53.624, 9.676)],
        ]
        gruppen = group_lines(stuecke)
        assert len(gruppen) == 1
        assert sorted(gruppen[0]) == [0, 1, 2]

    def test_reihenfolge_der_stuecke_aendert_nichts(self):
        stuecke = [
            [(53.621, 9.676), (53.624, 9.676)],
            [(53.6550, 9.6582), (53.6555, 9.6590)],
            [(53.618, 9.676), (53.621, 9.676)],
        ]
        gruppen = sorted(sorted(g) for g in group_lines(stuecke))
        assert gruppen == [[0, 2], [1]]


class TestNaechsteGruppe:
    def test_die_strasse_im_museumsort_gewinnt(self):
        # Aus dem echten Bestand: Holms Hauptstrasse liegt 0,2 km von der Ortsmitte, die
        # groesste gleichnamige Gruppe 2,0 km entfernt in einem Nachbarort. Die Mehrheit der
        # Hausnummern entscheidet also gerade nicht -- die Naehe zum Ort entscheidet.
        kandidaten = [(53.6304, 9.6498), (53.6205, 9.6727), (53.6111, 9.6305)]
        assert nearest_group(kandidaten, HOLM) == 1

    def test_der_gemittelte_punkt_haette_verloren(self):
        # Der alte Wert: der Durchschnitt aller siebzehn Hauptstrassen. Er liegt weiter von Holm
        # entfernt als Holms eigene Hauptstrasse -- der Beleg, dass Mitteln der falsche Griff war.
        gemittelt = (53.6405036, 9.669539)
        in_holm = (53.6205, 9.6727)
        assert distance_m(gemittelt, HOLM) > distance_m(in_holm, HOLM)
        assert distance_m(gemittelt, HOLM) == pytest.approx(2260, abs=150)

    def test_ohne_kandidaten_wird_nicht_geraten(self):
        with pytest.raises(ValueError):
            nearest_group([], HOLM)


class TestHausnummern:
    def test_gehreihenfolge_statt_alphabet(self):
        # Alphabetisch kaeme "10" vor "9" und "1a" vor "2" -- der klassische stille Fehler.
        adressen = [(n, (53.62, 9.67)) for n in ["10", "1a", "2", "9", "1", "12"]]
        assert [n for n, _ in by_housenumber(adressen)] == [
            "1",
            "1a",
            "2",
            "9",
            "10",
            "12",
        ]

    def test_median_housenumber_vertritt_die_strasse(self):
        adressen = [
            ("1", (53.620, 9.670)),
            ("3", (53.620, 9.672)),
            ("5", (53.620, 9.674)),
        ]
        assert median_housenumber(adressen) == (53.620, 9.672)

    def test_reihenfolge_der_eingabe_aendert_die_mitte_nicht(self):
        adressen = [("9", (53.62, 9.679)), ("1", (53.62, 9.671)), ("5", (53.62, 9.675))]
        assert median_housenumber(adressen) == (53.62, 9.675)
        assert median_housenumber(list(reversed(adressen))) == (53.62, 9.675)

    def test_bei_gerader_anzahl_gewinnt_die_kleinere(self):
        adressen = [("1", (53.62, 9.671)), ("2", (53.62, 9.672))]
        assert median_housenumber(adressen) == (53.62, 9.671)

    def test_lowest_housenumber_ignoriert_die_lage_in_der_liste(self):
        adressen = [
            ("12", (53.62, 9.679)),
            ("1a", (53.62, 9.671)),
            ("1", (53.62, 9.670)),
        ]
        assert lowest_housenumber(adressen) == (53.62, 9.670)

    def test_die_hausnummer_eins_entscheidet_zwischen_zwei_doerfern(self):
        # Der Fall, um den es geht: zwei "Hauptstrassen". Die im Nachbarort ist laenger und ihre
        # Mitte zufaellig naeher am Museumsort -- ihre Nummer 1 aber nicht.
        in_holm = [("1", (53.6205, 9.6727)), ("40", (53.6180, 9.6690))]
        im_nachbarort = [("1", (53.6550, 9.6582)), ("2", (53.6300, 9.6600))]
        kandidaten = [
            lowest_housenumber(in_holm),
            lowest_housenumber(im_nachbarort),
        ]
        assert nearest_group(kandidaten, HOLM) == 0

    def test_ohne_adressen_wird_nicht_geraten(self):
        with pytest.raises(ValueError):
            median_housenumber([])
        with pytest.raises(ValueError):
            lowest_housenumber([])


def _abstand_zur_strecke(punkt, anfang, ende):
    """Nur fuer den Test: liegt der Punkt wirklich auf der Strecke?"""
    from geometry import _nearest_on_segment

    return distance_m(punkt, _nearest_on_segment(anfang, ende, punkt))
