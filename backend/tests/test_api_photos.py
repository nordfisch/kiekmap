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
        make_photo(status=PhotoStatus.HIDDEN)
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

    def test_undatiertes_foto_erscheint_in_keiner_zeitauswahl(
        self, client: TestClient, session, make_photo
    ):
        make_photo(year=None)
        session.commit()

        mit_zeit = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1800, "to_year": 2100}
        )
        assert mit_zeit.json()["total"] == 0
        # Ohne Zeitauswahl aber schon -- sonst waere es unsichtbar.
        assert client.get("/api/photos", params={"bbox": BBOX}).json()["total"] == 1

    def test_vertauschte_jahre_werden_gedreht(self, client: TestClient, session, make_photo):
        make_photo(year=1932)
        session.commit()

        antwort = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1900}
        )
        assert antwort.json()["total"] == 1


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


class TestHistogramm:
    def test_zaehlt_je_jahrzehnt(self, client: TestClient, session, make_photo):
        for jahr, titel in ((1923, "a"), (1927, "b"), (1955, "c")):
            make_photo(year=jahr, title=titel, sha=f"{jahr:064d}")
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["decades"] == [
            {"decade": 1920, "count": 2},
            {"decade": 1950, "count": 1},
        ]
        assert daten["earliest"] == 1920
        assert daten["latest"] == 1959

    def test_zeigt_auch_ausserhalb_der_auswahl(self, client: TestClient, session, make_photo):
        """Der Schieber soll zeigen, wo ueberhaupt etwas liegt -- auch jenseits der Auswahl."""
        make_photo(year=1923, sha=f"{1923:064d}")
        make_photo(year=1980, sha=f"{1980:064d}")
        session.commit()

        daten = client.get(
            "/api/photos/histogram", params={"bbox": BBOX, "from_year": 1920, "to_year": 1930}
        ).json()

        assert len(daten["decades"]) == 2

    def test_undatierte_werden_getrennt_gezaehlt(self, client: TestClient, session, make_photo):
        make_photo(year=None, sha="a" * 64)
        make_photo(year=1932, sha="b" * 64)
        session.commit()

        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten["undated"] == 1
        assert daten["decades"] == [{"decade": 1930, "count": 1}]

    def test_leerer_ausschnitt(self, client: TestClient, session):
        daten = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert daten == {"decades": [], "undated": 0, "earliest": None, "latest": None}


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
