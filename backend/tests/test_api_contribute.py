"""Tests des "Hilf mit"-Bereichs.

Der Kernpunkt: Beitraege werden direkt uebernommen, aber sie duerfen nur fuellen, was leer ist.
Ohne diesen Schutz koennte ein Besucher am oeffentlichen Touchscreen eine kuratierte Angabe
ueberschreiben -- und der naechste Besucher die des vorherigen.
"""

import json
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import Change, PhotoStatus, Source

# Holm
IN_HOLM = {"lat": 53.6205, "lon": 9.676}
WEIT_WEG = {"lat": 48.1372, "lon": 11.5756}  # München


class TestNaechsteAufgabe:
    def test_liefert_foto_ohne_ort(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, title="Ohne Ort", sha="a" * 64)
        make_photo(title="Vollstaendig", sha="b" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["photo"]["title"] == "Ohne Ort"
        assert daten["open_count"] == 1
        assert daten["photo"]["needs_location"] is True

    def test_liefert_foto_ohne_jahr(self, client: TestClient, session, make_photo):
        make_photo(year=None, title="Ohne Jahr", sha="a" * 64)
        make_photo(year=1932, title="Datiert", sha="b" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "date"}).json()

        assert daten["photo"]["title"] == "Ohne Jahr"
        assert daten["photo"]["date_label"] == "Jahr unbekannt"

    def test_weggetipptes_erscheint_nicht_sofort_wieder(
        self, client: TestClient, session, make_photo
    ):
        erst = make_photo(lat=None, lon=None, title="A", sha="a" * 64)
        make_photo(lat=None, lon=None, title="B", sha="b" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "location", "exclude": str(erst.id)}
        ).json()

        assert daten["photo"]["title"] == "B"

    def test_faengt_von_vorn_an_wenn_alles_durch_ist(self, client: TestClient, session, make_photo):
        """Lieber wiederholen als "nichts mehr da" melden, solange etwas offen ist."""
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "location", "exclude": str(foto.id)}
        ).json()

        assert daten["photo"]["id"] == foto.id

    def test_nichts_offen(self, client: TestClient, session, make_photo):
        make_photo(sha="a" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["photo"] is None
        assert daten["open_count"] == 0

    def test_verstecktes_foto_wird_nicht_vorgelegt(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, status=PhotoStatus.HIDDEN, sha="a" * 64)
        session.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "location"}).json()["photo"] is None
        )


class TestOrtErgaenzen:
    def test_uebernimmt_sofort(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        antwort = client.post(
            f"/api/contribute/{foto.id}/location",
            json={**IN_HOLM, "place_name": "Mühlenweg"},
        )

        assert antwort.status_code == 200
        daten = antwort.json()
        assert daten["needs_location"] is False
        assert daten["place_name"] == "Mühlenweg"
        assert daten["location_source"] == Source.VISITOR

    def test_erscheint_danach_auf_der_karte(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, year=1932, sha="a" * 64)
        session.commit()
        assert (
            client.get("/api/photos", params={"bbox": "9.60,53.57,9.75,53.67"}).json()["total"] == 0
        )

        client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)

        # Der unmittelbare Effekt ist der Reiz fuer den Besucher:
        # "mein Wissen ist jetzt auf der Karte".
        assert (
            client.get("/api/photos", params={"bbox": "9.60,53.57,9.75,53.67"}).json()["total"] == 1
        )

    def test_wird_protokolliert(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{foto.id}/location", json={**IN_HOLM, "session_id": "abc"})

        eintrag = session.scalars(select(Change).where(Change.photo_id == foto.id)).one()
        assert eintrag.field == "location"
        assert eintrag.source == Source.VISITOR
        assert eintrag.session_id == "abc"
        assert "53.62" in eintrag.new_value

    def test_besetztes_feld_wird_nicht_ueberschrieben(
        self, client: TestClient, session, make_photo
    ):
        """Was ein Kurator gesetzt hat, ist unantastbar -- und der zweite Besucher darf den
        ersten nicht ueberschreiben."""
        foto = make_photo(lat=53.61, lon=9.66, sha="a" * 64)
        session.commit()

        antwort = client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)

        assert antwort.status_code == 409
        session.refresh(foto)
        assert foto.lat == 53.61
        # Die Meldung soll den Besucher nicht als Stoerenfried behandeln.
        assert "Dank" in antwort.json()["detail"]

    def test_ort_ausserhalb_der_region(self, client: TestClient, session, settings, make_photo):
        (settings.data_dir / "region.json").write_text(
            json.dumps({"bbox": [9.60028, 53.57561, 9.75174, 53.66545]}), encoding="utf-8"
        )
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        antwort = client.post(f"/api/contribute/{foto.id}/location", json=WEIT_WEG)

        assert antwort.status_code == 422
        assert "ausserhalb" in antwort.json()["detail"].lower()

    def test_ohne_hinterlegte_region_wird_nicht_geprueft(
        self, client: TestClient, session, make_photo
    ):
        # Kein region.json vorhanden: dann lieber annehmen als grundlos ablehnen.
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        assert client.post(f"/api/contribute/{foto.id}/location", json=WEIT_WEG).status_code == 200

    def test_unbekanntes_foto(self, client: TestClient):
        assert client.post("/api/contribute/9999/location", json=IN_HOLM).status_code == 404


class TestJahrErgaenzen:
    def test_jahresangabe(self, client: TestClient, session, make_photo):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        daten = client.post(
            f"/api/contribute/{foto.id}/date", json={"year": 1932, "precision": "year"}
        ).json()

        assert daten["date_label"] == "1932"
        assert daten["needs_date"] is False
        assert daten["date_source"] == Source.VISITOR

    def test_jahrzehnt_wird_zum_intervall(self, client: TestClient, session, make_photo):
        """ "Irgendwann in den Zwanzigern" ist die haeufigste ehrliche Antwort."""
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        daten = client.post(
            f"/api/contribute/{foto.id}/date", json={"year": 1924, "precision": "decade"}
        ).json()

        assert daten["date_label"] == "1920er"
        assert daten["date_from"] == "1920-01-01"
        assert daten["date_to"] == "1929-12-31"

    def test_so_datiertes_foto_erscheint_bei_ueberlappender_auswahl(
        self, client, session, make_photo
    ):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()
        client.post(f"/api/contribute/{foto.id}/date", json={"year": 1924, "precision": "decade"})

        antwort = client.get(
            "/api/photos",
            params={"bbox": "9.60,53.57,9.75,53.67", "from_year": 1925, "to_year": 1930},
        )

        assert antwort.json()["total"] == 1

    def test_bereits_datiertes_foto(self, client: TestClient, session, make_photo):
        foto = make_photo(year=1932, sha="a" * 64)
        session.commit()

        antwort = client.post(
            f"/api/contribute/{foto.id}/date", json={"year": 1800, "precision": "year"}
        )

        assert antwort.status_code == 409
        session.refresh(foto)
        assert foto.date_from == date(1932, 1, 1)

    def test_unsinniges_jahr_wird_abgewiesen(self, client: TestClient, session, make_photo):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        assert (
            client.post(
                f"/api/contribute/{foto.id}/date", json={"year": 3000, "precision": "year"}
            ).status_code
            == 422
        )

    def test_wird_protokolliert(self, client: TestClient, session, make_photo):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{foto.id}/date", json={"year": 1924, "precision": "decade"})

        eintrag = session.scalars(select(Change).where(Change.field == "date")).one()
        assert eintrag.new_value == "1920er"
        assert eintrag.source == Source.VISITOR


class TestZusammenspiel:
    def test_beide_luecken_nacheinander_fuellen(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, year=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)
        client.post(f"/api/contribute/{foto.id}/date", json={"year": 1955, "precision": "year"})

        daten = client.get(f"/api/photos/{foto.id}").json()
        assert daten["needs_location"] is False
        assert daten["needs_date"] is False
        assert len(session.scalars(select(Change)).all()) == 2

    def test_offene_zahl_sinkt(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(lat=None, lon=None, sha="b" * 64)
        session.commit()

        assert client.get("/api/contribute/next?need=location").json()["open_count"] == 2
        client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)
        assert client.get("/api/contribute/next?need=location").json()["open_count"] == 1


class TestOrtssuche:
    def _lege_orte_an(self, session):
        from app.models import Place
        from app.services.places import normalize

        for name, art, lat, lon in [
            ("Mühlenweg", "strasse", 53.62, 9.67),
            ("Alte Mühlenstraße", "strasse", 53.63, 9.68),
            ("Mühlenteich", "natur", 53.61, 9.66),
            ("Hauptstraße", "strasse", 53.64, 9.67),
        ]:
            session.add(
                Place(name=name, name_normalized=normalize(name), lat=lat, lon=lon, kind=art)
            )
        session.commit()

    def test_findet_trotz_fehlendem_umlaut(self, client: TestClient, session):
        self._lege_orte_an(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "muhlen"}).json()]

        assert "Mühlenweg" in namen

    def test_wortanfang_steht_vorn(self, client: TestClient, session):
        """Wer "Muhl" tippt, meint den Mühlenweg, nicht die Alte Mühlenstraße."""
        self._lege_orte_an(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "muhl"}).json()]

        assert namen[0] == "Mühlenweg"
        assert "Alte Mühlenstraße" in namen

    def test_scharfes_s(self, client: TestClient, session):
        self._lege_orte_an(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "hauptstrasse"}).json()]

        assert namen == ["Hauptstraße"]

    def test_zu_kurze_eingabe_liefert_nichts(self, client: TestClient, session):
        self._lege_orte_an(session)

        assert client.get("/api/places", params={"q": "m"}).json() == []
        assert client.get("/api/places").json() == []


class TestOrtsverzeichnisLaden:
    def test_aus_datei(self, session, settings):
        from app.services.places import load_from_file

        settings.places_file.write_text(
            json.dumps(
                [
                    {
                        "name": "Süderstraße",
                        "name_normalized": "veraltet",
                        "lat": 53.6,
                        "lon": 9.6,
                        "kind": "strasse",
                    }
                ]
            ),
            encoding="utf-8",
        )

        anzahl = load_from_file(session, settings.places_file)

        assert anzahl == 1
        from app.models import Place

        ort = session.scalars(select(Place)).one()
        # Die Normalisierung wird neu berechnet: eine aeltere Datei wuerde die Suche sonst
        # stillschweigend leer laufen lassen.
        assert ort.name_normalized == "suderstrasse"

    def test_fehlende_datei_ist_kein_fehler(self, session, settings):
        from app.services.places import load_from_file

        assert load_from_file(session, settings.data_dir / "gibtsnicht.json") == 0
