# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Tests der Abfrage-API.

Der wichtigste Fall steht in :class:`TestZeitfilter`: ein auf "1920er" datiertes Foto muss bei der
Auswahl 1925-1930 erscheinen. Bei einer Abfrage auf Enthaltensein statt Ueberlappung faellt es
lautlos heraus -- und mit ihm der Grossteil eines Heimatmuseumsbestands.
"""

import pytest
from fastapi.testclient import TestClient

from app.models import DatePrecision, PhotoStatus

# Holm und Umgebung.
BBOX = "9.60,53.57,9.75,53.67"
BBOX_WOANDERS = "10.50,52.00,10.60,52.10"


class TestKartenausschnitt:
    def test_foto_im_ausschnitt_erscheint(self, client: TestClient, session, make_photo):
        make_photo()
        session.commit()

        antwort = client.get("/api/photos", params={"bbox": BBOX})

        assert antwort.status_code == 200
        daten = antwort.json()
        assert daten["total"] == 1
        assert daten["photos"][0]["title"] == "Testfoto"

    def test_foto_ausserhalb_erscheint_nicht(self, client: TestClient, session, make_photo):
        make_photo()
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX_WOANDERS}).json()["total"] == 0

    def test_foto_ohne_ort_erscheint_nie(self, client: TestClient, session, make_photo):
        # Es gehoert in den "Hilf mit"-Bereich, nicht auf die Karte.
        make_photo(lat=None, lon=None)
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX}).json()["total"] == 0

    def test_verstecktes_foto_erscheint_nicht(self, client: TestClient, session, make_photo):
        make_photo(status=PhotoStatus.DELETED)
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX}).json()["total"] == 0

    @pytest.mark.parametrize("bbox", ["9.6,53.5", "a,b,c,d", "9.75,53.67,9.60,53.57"])
    def test_unbrauchbare_bbox_wird_abgewiesen(self, client: TestClient, bbox):
        assert client.get("/api/photos", params={"bbox": bbox}).status_code == 422


class TestZeitfilter:
    def test_jahrzehnt_erscheint_bei_auswahl_mittendrin(
        self, client: TestClient, session, make_photo
    ):
        """Der Fall, der bei naiver Datumsabfrage still verloren geht."""
        make_photo(year=1920, precision=DatePrecision.DECADE, title="1920er Jahre")
        session.commit()

        antwort = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1925, "to_year": 1930}
        )

        assert antwort.json()["total"] == 1, "1920er-Foto muss in 1925-1930 erscheinen"

    def test_jahrzehnt_ausserhalb_erscheint_nicht(self, client: TestClient, session, make_photo):
        make_photo(year=1920, precision=DatePrecision.DECADE)
        session.commit()

        antwort = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1960}
        )
        assert antwort.json()["total"] == 0

    def test_genaues_jahr_am_rand_der_auswahl(self, client: TestClient, session, make_photo):
        make_photo(year=1932)
        session.commit()

        for von, bis in ((1932, 1932), (1900, 1932), (1932, 2000)):
            antwort = client.get(
                "/api/photos", params={"bbox": BBOX, "from_year": von, "to_year": bis}
            )
            assert antwort.json()["total"] == 1, f"{von}-{bis} muss 1932 enthalten"

    def test_vertauschte_jahre_werden_gedreht(self, client: TestClient, session, make_photo):
        make_photo(year=1932)
        session.commit()

        antwort = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1900}
        )
        assert antwort.json()["total"] == 1


class TestMarkerbeschriftung:
    """Was die Karte je Foto braucht, um Adresse und Jahr darunter zu setzen."""

    def test_marker_traegt_adresse_und_kurzes_datum(self, client: TestClient, session, make_photo):
        make_photo(year=2014, month=3, day=22, place_name="Lehmweg 17b")
        session.commit()

        marker = client.get("/api/photos", params={"bbox": BBOX}).json()["photos"][0]

        assert marker["place_name"] == "Lehmweg 17b"
        # Der Tag gehoert nicht unter ein Vorschaubild -- auf der Karte zaehlt das Jahr.
        assert marker["date_short"] == "2014"
        # Die ausgeschriebene Form bleibt daneben stehen: Sie traegt die Beschriftung fuer
        # Vorlesewerkzeuge, wo die Genauigkeit nicht stoert.
        assert marker["date_label"] == "22. März 2014"

    def test_undatiertes_foto_bekommt_eine_leere_kurzform(
        self, client: TestClient, session, make_photo
    ):
        make_photo(year=None, place_name="Im Sande 18")
        session.commit()

        marker = client.get("/api/photos", params={"bbox": BBOX}).json()["photos"][0]

        assert marker["date_short"] == ""
        assert marker["date_label"] == "Jahr unbekannt"


class TestUndatierte:
    """Fotos ohne Jahr sind der dritte Fall, und wer fragt, entscheidet ihn.

    Sie ueberlappen keinen Zeitraum, fielen also aus jeder Auswahl heraus -- in diesem Bestand
    zwei Drittel davon, lautlos. ``include_undated`` ist deshalb ein eigener Schalter und nicht
    eine Nebenwirkung der Schieberstellung.
    """

    def test_bleiben_standardmaessig_in_der_zeitauswahl(
        self, client: TestClient, session, make_photo
    ):
        # Der Regelfall: Wer den Schieber anfasst, soll nicht ohne Ansage drei Viertel der Karte
        # verlieren. Frueher war genau das die Wirkung.
        make_photo(year=None)
        session.commit()

        antwort = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1920, "to_year": 1930}
        )

        assert antwort.json()["total"] == 1

    def test_fallen_heraus_wenn_der_schalter_aus_ist(self, client: TestClient, session, make_photo):
        make_photo(year=None)
        session.commit()

        antwort = client.get(
            "/api/photos",
            params={"bbox": BBOX, "from_year": 1920, "to_year": 1930, "include_undated": False},
        )

        assert antwort.json()["total"] == 0

    def test_der_schalter_wirkt_auch_ohne_zeitauswahl(
        self, client: TestClient, session, make_photo
    ):
        """Die Stellung, bei der der Schieber steht, wenn niemand ihn angefasst hat.

        Ueber die ganze Achse schickt der Kiosk bewusst keinen Zeitfilter. Griffe der Schalter
        nur zusammen mit einem, taete er ausgerechnet dort nichts, wo er anfaengt.
        """
        make_photo(year=None, sha="a" * 64)
        make_photo(year=1932, sha="b" * 64)
        session.commit()

        antwort = client.get("/api/photos", params={"bbox": BBOX, "include_undated": False})

        assert antwort.json()["total"] == 1

    def test_datierte_bleiben_von_dem_schalter_unberuehrt(
        self, client: TestClient, session, make_photo
    ):
        """Die Gegenprobe: Der Schalter erweitert die Auswahl, er ersetzt sie nicht.

        Waere aus ``kein Datum ODER Ueberlappung`` versehentlich nur ``kein Datum``, stuende
        ploetzlich nichts Datiertes mehr auf der Karte -- und der Test oben faende das gut.
        """
        make_photo(year=1932, sha="c" * 64)
        session.commit()

        drin = client.get("/api/photos", params={"bbox": BBOX, "from_year": 1930, "to_year": 1935})
        draussen = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1955}
        )

        assert drin.json()["total"] == 1
        assert draussen.json()["total"] == 0

    def test_das_histogramm_zaehlt_sie_immer(self, client: TestClient, session, make_photo):
        """Sonst verschwaende mit der Zahl auch der Schalter, der sie zurueckholt.

        Das Etikett neben dem Schieber heisst „670 Fotos ohne Jahr anzeigen". Zaehlte das
        Histogramm nur die gerade sichtbaren, stuende dort nach dem Abschalten eine Null -- und
        der Weg zurueck waere weg.
        """
        make_photo(year=None)
        session.commit()

        antwort = client.get(
            "/api/photos/histogram", params={"bbox": BBOX, "include_undated": False}
        )

        assert antwort.json()["undated"] == 1


class TestBegrenzung:
    def test_limit_meldet_sich(self, client: TestClient, session, make_photo):
        for nummer in range(5):
            make_photo(title=f"Foto {nummer}", sha=f"{nummer:064d}")
        session.commit()

        antwort = client.get("/api/photos", params={"bbox": BBOX, "limit": 2}).json()

        assert len(antwort["photos"]) == 2
        assert antwort["total"] == 5
        assert antwort["truncated"] is True, "die Karte soll zum Hineinzoomen auffordern koennen"

    def test_ohne_begrenzung_kein_hinweis(self, client: TestClient, session, make_photo):
        make_photo()
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX}).json()["truncated"] is False


class TestReihenfolge:
    def test_zuletzt_bearbeitetes_foto_kommt_zuerst(self, client: TestClient, session, make_photo):
        """Fotos am selben Ort liegen als Stapel uebereinander -- oben das eben Ergaenzte.

        Genau dorthin faehrt die Karte nach einem Besucherbeitrag.
        """
        from datetime import datetime

        alt = make_photo(title="Lange her", sha="a" * 64)
        neu = make_photo(title="Eben bearbeitet", sha="b" * 64)
        session.commit()
        alt.updated_at = datetime(2026, 1, 1, 12, 0)
        neu.updated_at = datetime(2026, 7, 31, 12, 0)
        session.commit()

        daten = client.get("/api/photos", params={"bbox": BBOX}).json()

        assert [foto["title"] for foto in daten["photos"]] == ["Eben bearbeitet", "Lange her"]


class TestHistogramm:
    """Die Balken hinter dem Zeitschieber -- und wie breit ein Balken ist.

    Der teure Fehler steckt in der Breite, nicht in der Zaehlung: Ein auf "1920er" datiertes Foto
    traegt ``date_from = 1920-01-01``. In Jahresbalken tuermten sich dann zehn Jahrgaenge auf dem
    Balken 1920 -- ein Turm, wo in Wahrheit ein Jahrzehnt liegt.
    """

    def test_jahrgenauer_bestand_bekommt_jahresbalken(
        self, client: TestClient, session, make_photo
    ):
        for jahr in (2010, 2014, 2014, 2024):
            make_photo(year=jahr)
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["step"] == 1
        assert daten["bars"] == [
            {"year": 2010, "count": 1},
            {"year": 2014, "count": 2},
            {"year": 2024, "count": 1},
        ]

    def test_eine_jahrzehnt_datierung_vergroebert_alles(
        self, client: TestClient, session, make_photo
    ):
        """Der wichtigste Test dieser Klasse.

        Sobald *ein* Foto auf ein Jahrzehnt datiert ist, sind Jahresbalken eine Luege -- und zwar
        eine stille: Man saehe einen Turm auf 1920 und haette keinen Anlass, ihn anzuzweifeln.
        """
        make_photo(year=2010)
        make_photo(year=2014)
        make_photo(year=1920, precision="decade")
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["step"] == 10
        assert daten["bars"] == [
            {"year": 1920, "count": 1},
            {"year": 2010, "count": 2},
        ]

    def test_lange_spanne_bekommt_breitere_buendel(self, client: TestClient, session, make_photo):
        """130 Jahre in Jahresbalken waeren eine Hecke, kein Bild.

        Wie breit genau, entscheidet die Regel in services/dates.py -- hier zaehlt, dass die
        Spanne nicht mehr in Jahren zerlegt wird und in dreissig Balken passt.
        """
        make_photo(year=1890)
        make_photo(year=2020)
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        spanne = daten["collection_to"] - daten["collection_from"]
        assert daten["step"] > 1
        assert spanne / daten["step"] <= 30

    def test_spanne_ignoriert_den_kartenausschnitt(self, client: TestClient, session, make_photo):
        """Die Achse des Zeitschiebers gehoert der Sammlung, nicht dem Ausschnitt.

        Sonst bedeutete dieselbe Stelle des Schiebers nach jedem Zoom ein anderes Jahr -- und eine
        vorher getroffene Auswahl laege ausserhalb ihrer eigenen Bahn.
        """
        make_photo(year=1930)
        # Weit weg, ausserhalb der abgefragten bbox.
        make_photo(year=1890, lat=48.0, lon=11.0)
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["bars"] == [{"year": 1930, "count": 1}], "Balken zeigen den Ausschnitt"
        assert daten["collection_from"] == 1890, "die Achse zeigt den ganzen Bestand"

    def test_die_breite_gehoert_ebenfalls_der_sammlung(
        self, client: TestClient, session, make_photo
    ):
        """Sonst wechselte die Bedeutung der Balken beim Verschieben der Karte.

        Das Jahrzehnt-Foto liegt ausserhalb des Ausschnitts und vergroebert die Anzeige trotzdem --
        genau wie die Achse.
        """
        make_photo(year=2014)
        make_photo(year=1920, precision="decade", lat=48.0, lon=11.0)
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["step"] == 10

    def test_zeigt_auch_ausserhalb_der_auswahl(self, client: TestClient, session, make_photo):
        """Der Schieber soll zeigen, wo ueberhaupt etwas liegt -- auch jenseits der Auswahl."""
        make_photo(year=1923)
        make_photo(year=1980)
        session.commit()

        daten = client.get(
            "/api/photos/histogram", params={"bbox": BBOX, "from_year": 1920, "to_year": 1930}
        ).json()

        assert len(daten["bars"]) == 2

    def test_undatierte_werden_getrennt_gezaehlt(self, client: TestClient, session, make_photo):
        make_photo(year=None)
        make_photo(year=1932)
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["undated"] == 1
        assert daten["bars"] == [{"year": 1932, "count": 1}]

    def test_leerer_ausschnitt(self, client: TestClient, session):
        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten == {
            "bars": [],
            "step": 1,
            "undated": 0,
            "collection_from": None,
            "collection_to": None,
        }


class TestEinzelnesFoto:
    def test_detail(self, client: TestClient, session, make_photo):
        foto = make_photo(year=1920, precision=DatePrecision.DECADE)
        session.commit()

        daten = client.get(f"/api/photos/{foto.id}").json()

        assert daten["date_label"] == "1920er"
        assert daten["needs_date"] is False
        assert daten["needs_location"] is False
        assert daten["image_url"] == f"/api/photos/{foto.id}/image"

    def test_unbekannte_nummer(self, client: TestClient):
        antwort = client.get("/api/photos/9999")

        assert antwort.status_code == 404
        assert "9999" in antwort.json()["detail"]

    def test_falsche_thumbnailgroesse_nennt_die_richtigen(
        self, client: TestClient, session, make_photo
    ):
        foto = make_photo()
        session.commit()

        antwort = client.get(f"/api/photos/{foto.id}/thumb", params={"size": 999})

        assert antwort.status_code == 422
        assert "240" in antwort.json()["detail"]


class TestAuslieferung:
    """Gegen echte importierte Dateien statt gegen erfundene Zeilen."""

    @pytest.fixture
    def importiertes_foto(self, session, settings, sample_image):
        from app.services.importer import import_file

        outcome = import_file(session, sample_image("foto_mit_gps.jpg"), settings)
        session.commit()
        return outcome.photo

    def test_thumbnail_wird_ausgeliefert(self, client: TestClient, importiertes_foto):
        antwort = client.get(f"/api/photos/{importiertes_foto.id}/thumb", params={"size": 240})

        assert antwort.status_code == 200
        assert antwort.headers["content-type"] == "image/webp"
        assert antwort.content[:4] == b"RIFF"

    def test_thumbnail_darf_beliebig_gecacht_werden(self, client: TestClient, importiertes_foto):
        # Der Dateiname ist der Inhalts-Hash: gleicher Name heisst garantiert gleicher Inhalt.
        antwort = client.get(f"/api/photos/{importiertes_foto.id}/thumb")

        assert "immutable" in antwort.headers["cache-control"]

    def test_original_wird_ausgeliefert(self, client: TestClient, importiertes_foto):
        antwort = client.get(f"/api/photos/{importiertes_foto.id}/image")

        assert antwort.status_code == 200
        assert antwort.headers["content-type"] == "image/jpeg"
        assert antwort.content[:2] == b"\xff\xd8", "JPEG-Kennung"

    def test_importiertes_foto_erscheint_auf_der_karte(self, client: TestClient, importiertes_foto):
        """Das GPS-Testbild liegt in Holm und traegt ein Aufnahmedatum von 1975."""
        antwort = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1970, "to_year": 1980}
        ).json()

        assert antwort["total"] == 1
        assert antwort["photos"][0]["date_label"] == "21. Juni 1975"


class TestDateiendung:
    """Woher die Auslieferung weiss, wie die Datei auf der Platte heisst -- Punkt 61.

    Der Dateiname ist der SHA-256 plus die Endung des Formats. Welche Endung zu welchem MIME-Typ
    gehoert, steht in ``ALLOWED_FORMATS`` -- und stand daneben ein zweites Mal in ``api/photos.py``,
    als Rechnung auf dem String: ``mime.split("/")[-1]``, mit ``jpeg`` und ``tiff`` von Hand
    zurueckgebogen. Beide stimmten ueberein, solange jede Endung das Ende ihres MIME-Typs ist.
    """

    def test_jeder_erlaubte_typ_findet_seine_endung(self):
        """Die Gegenprobe, die das Auseinanderlaufen unmoeglich macht.

        Sie prueft nicht eine Liste von Beispielen, sondern die Tabelle gegen sich selbst: Was der
        Import ablegen darf, muss die Auslieferung benennen koennen.
        """
        from app.services.storage import ALLOWED_FORMATS, suffix_for_mime

        for mime, endung in ALLOWED_FORMATS.values():
            assert suffix_for_mime(mime) == endung, f"{mime} findet seine Endung nicht"

    def test_ein_unbekannter_typ_ergibt_keine_endung(self):
        from app.services.storage import suffix_for_mime

        assert suffix_for_mime("image/heic") is None
        assert suffix_for_mime("") is None

    def test_ein_foto_mit_unbekanntem_typ_meldet_die_fehlende_datei(
        self, client: TestClient, session, make_photo
    ):
        """So etwas legt der Import nie an -- eine zurueckgespielte Sicherung aber vielleicht.

        Vorher entstand daraus stillschweigend ein Pfad, den es nicht gibt. Die Antwort ist
        dieselbe geblieben, weil sie fuer den Besucher stimmt; im Protokoll steht jetzt, woran es
        wirklich lag.
        """
        foto = make_photo()
        foto.mime = "image/heic"
        session.commit()

        antwort = client.get(f"/api/photos/{foto.id}/image")

        assert antwort.status_code == 404
        assert antwort.json()["detail"] == "Originaldatei fehlt"
