"""Tests des Admin-Bereichs.

Zwei Zusagen tragen diesen Bereich, und beide brechen still, wenn sie brechen:

  1. Beim Bearbeiten heisst *fehlendes* Feld "unveraendert lassen" und *leeres* Feld "loeschen".
     Ohne diesen Unterschied liesse sich eine falsche Datierung nie wieder herausnehmen.
  2. Hochgeladene Fotos sind sofort in der Datenbank, nicht erst nach "Uebernehmen". Ein
     geschlossener Browser darf keine Uploads kosten.
"""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import Change, DatePrecision, Photo, PhotoStatus, Source

HOLM = {"lat": 53.6205, "lon": 9.676}


def _bild(fixtures_dir, name: str = "scan_ohne_exif.jpg") -> bytes:
    return (fixtures_dir / name).read_bytes()


class TestAnmeldung:
    def test_ohne_token_kein_zugang(self, client: TestClient):
        assert client.get("/api/admin/overview").status_code == 401

    def test_ausgedachtes_token_kein_zugang(self, client: TestClient):
        antwort = client.get("/api/admin/overview", headers={"X-Admin-Token": "ausgedacht"})

        assert antwort.status_code == 401

    def test_ohne_eingerichtete_pin_sagt_das_geraet_es_deutlich(self, client: TestClient, settings):
        """Ein leeres admin_pin_hash darf nicht als "jede PIN passt" durchgehen."""
        settings.admin_pin_hash = ""

        antwort = client.post("/api/admin/login", json={"pin": "4711"})

        assert antwort.status_code == 503
        assert "app.cli pin" in antwort.json()["detail"]

    def test_falsche_pin(self, client: TestClient, admin_pin):
        antwort = client.post("/api/admin/login", json={"pin": "0000"})

        assert antwort.status_code == 401

    def test_zu_viele_versuche_sperren_das_tastenfeld(self, client: TestClient, admin_pin):
        """Der eigentliche Schutz einer vierstelligen PIN."""
        for _ in range(5):
            client.post("/api/admin/login", json={"pin": "0000"})

        # Auch die richtige PIN kommt jetzt nicht mehr durch.
        antwort = client.post("/api/admin/login", json={"pin": admin_pin})

        assert antwort.status_code == 429
        assert "Sekunden" in antwort.json()["detail"]

    def test_richtige_pin_gibt_ein_token(self, client: TestClient, admin_pin):
        antwort = client.post("/api/admin/login", json={"pin": admin_pin})

        assert antwort.status_code == 200
        assert antwort.json()["token"]
        assert antwort.json()["expires_in_s"] > 0

    def test_abmelden_beendet_die_sitzung(self, admin_client: TestClient):
        assert admin_client.post("/api/admin/logout").status_code == 204

        assert admin_client.get("/api/admin/overview").status_code == 401

    def test_sitzung_ueberlebt_das_neuladen_der_seite(self, admin_client: TestClient):
        """Damit ein versehentliches Neuladen nicht die PIN-Eingabe von vorn verlangt."""
        antwort = admin_client.get("/api/admin/session")

        assert antwort.status_code == 200
        assert antwort.json()["expires_in_s"] > 0


class TestUebersicht:
    def test_zaehlt_was_fehlt(self, admin_client: TestClient, session, make_photo):
        make_photo(sha="a" * 64)
        make_photo(lat=None, lon=None, sha="b" * 64)
        make_photo(year=None, sha="c" * 64)
        make_photo(status=PhotoStatus.HIDDEN, sha="d" * 64)
        session.commit()

        daten = admin_client.get("/api/admin/overview").json()

        assert daten["total"] == 4
        assert daten["without_location"] == 1
        assert daten["without_date"] == 1
        # Auf der Karte: mit Ort, mit Jahr und nicht versteckt.
        assert daten["on_map"] == 1
        assert daten["hidden"] == 1

    def test_zurueckgenommener_beitrag_zaehlt_nicht_mehr(
        self, admin_client: TestClient, session, make_photo
    ):
        """Die Kachel fuehrt in die Moderation -- sie darf nichts melden, was dort nicht steht.

        Sonst stuende "Heute gab es einen Besucherbeitrag" ueber einer leeren Liste.
        """
        foto = make_photo(sha="a" * 64)
        session.add(
            Change(
                photo_id=foto.id,
                field="date",
                old_value=None,
                new_value="1932",
                source=Source.VISITOR,
                created_at=datetime.now(),
                reverted_at=datetime.now(),
            )
        )
        session.commit()

        daten = admin_client.get("/api/admin/overview").json()

        assert daten["visitor_changes"] == 0
        assert daten["days_since_change"] is None

    def test_offener_beitrag_datiert_die_kachel(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo(sha="a" * 64)
        session.add(
            Change(
                photo_id=foto.id,
                field="date",
                old_value=None,
                new_value="1932",
                source=Source.VISITOR,
                created_at=datetime.now(UTC).replace(tzinfo=None),
            )
        )
        session.commit()

        daten = admin_client.get("/api/admin/overview").json()

        assert daten["days_since_change"] == 0


class TestFotoliste:
    def test_filter_ohne_ort_zeigt_nicht_die_ohne_jahr(
        self, admin_client: TestClient, session, make_photo
    ):
        """Der Grund fuer die Aufteilung.

        Verorten und Datieren sind zwei Arbeiten. Wer die Fotos ohne Ort abarbeitet, will die
        ohne Jahr nicht dazwischen -- unter einem gemeinsamen "unvollstaendig" bekam er sie.
        """
        make_photo(title="Vollstaendig", sha="a" * 64)
        make_photo(title="Ohne Ort", lat=None, lon=None, sha="b" * 64)
        make_photo(title="Ohne Jahr", year=None, sha="c" * 64)
        session.commit()

        daten = admin_client.get("/api/admin/photos", params={"show": "without_location"}).json()

        assert [foto["title"] for foto in daten["photos"]] == ["Ohne Ort"]

    def test_filter_ohne_jahr_zeigt_nicht_die_ohne_ort(
        self, admin_client: TestClient, session, make_photo
    ):
        make_photo(title="Vollstaendig", sha="a" * 64)
        make_photo(title="Ohne Ort", lat=None, lon=None, sha="b" * 64)
        make_photo(title="Ohne Jahr", year=None, sha="c" * 64)
        session.commit()

        daten = admin_client.get("/api/admin/photos", params={"show": "without_date"}).json()

        assert [foto["title"] for foto in daten["photos"]] == ["Ohne Jahr"]

    def test_suche_findet_ueber_den_dateinamen(self, admin_client: TestClient, session, make_photo):
        """Nach einem Stapel-Upload sucht man nach dem, was auf dem Scanner stand."""
        make_photo(title="Kirchweih 1932", sha="a" * 64)
        make_photo(title="Umzug", sha="b" * 64)
        session.commit()

        daten = admin_client.get("/api/admin/photos", params={"q": "kirchweih"}).json()

        assert daten["total"] == 1
        assert daten["photos"][0]["original_filename"] == "Kirchweih 1932.jpg"

    def test_ohne_anmeldung_keine_liste(self, client: TestClient):
        assert client.get("/api/admin/photos").status_code == 401


class TestFotoBearbeiten:
    def test_fehlendes_feld_bleibt_unangetastet(
        self, admin_client: TestClient, session, make_photo
    ):
        """Wer nur den Titel aendert, darf die Datierung nicht verlieren."""
        foto = make_photo(title="Alt", year=1932)
        session.commit()

        daten = admin_client.patch(f"/api/admin/photos/{foto.id}", json={"title": "Neu"}).json()

        assert daten["title"] == "Neu"
        assert daten["date_label"] == "1932"
        assert daten["lat"] is not None

    def test_leeres_feld_loescht_die_datierung(self, admin_client: TestClient, session, make_photo):
        """Der Gegenfall -- ausdrueckliches null nimmt eine falsche Angabe heraus.

        Ohne diesen Unterschied koennte der Kurator eine falsche Jahreszahl nur durch eine andere
        ersetzen, nie durch "weiss man nicht".
        """
        foto = make_photo(year=1932)
        session.commit()

        daten = admin_client.patch(f"/api/admin/photos/{foto.id}", json={"date": None}).json()

        assert daten["date_label"] == "Jahr unbekannt"
        assert daten["needs_date"] is True

    def test_geloeschte_datierung_legt_das_foto_wieder_vor(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo(year=1932)
        session.commit()
        admin_client.patch(f"/api/admin/photos/{foto.id}", json={"date": None})

        aufgabe = admin_client.get("/api/contribute/next", params={"need": "date"}).json()

        assert aufgabe["photo"]["id"] == foto.id

    def test_unmoegliches_datum_wird_abgewiesen(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo()
        session.commit()

        antwort = admin_client.patch(
            f"/api/admin/photos/{foto.id}",
            json={"date": {"year": 1932, "month": 2, "day": 30, "precision": "day"}},
        )

        assert antwort.status_code == 422

    def test_jahrzehnt_wird_zum_intervall(self, admin_client: TestClient, session, make_photo):
        foto = make_photo(year=None)
        session.commit()

        daten = admin_client.patch(
            f"/api/admin/photos/{foto.id}",
            json={"date": {"year": 1934, "precision": "decade"}},
        ).json()

        # Abgerundet auf den Anfang des Jahrzehnts, nicht 1934 bis 1943.
        assert daten["date_from"] == "1930-01-01"
        assert daten["date_to"] == "1939-12-31"
        assert daten["date_label"] == "1930er"

    def test_bearbeitung_wird_protokolliert(self, admin_client: TestClient, session, make_photo):
        foto = make_photo(title="Alt")
        session.commit()

        admin_client.patch(f"/api/admin/photos/{foto.id}", json={"title": "Neu"})

        eintrag = session.scalars(select(Change).where(Change.field == "title")).one()
        assert (eintrag.old_value, eintrag.new_value) == ("Alt", "Neu")
        assert eintrag.source == Source.CURATOR

    def test_gleicher_wert_erzeugt_keinen_eintrag(
        self, admin_client: TestClient, session, make_photo
    ):
        """Sonst ersaeuft die Beitragsliste in Eintraegen ohne Aussage."""
        foto = make_photo(title="Alt")
        session.commit()

        admin_client.patch(f"/api/admin/photos/{foto.id}", json={"title": "Alt"})

        assert session.scalars(select(Change)).all() == []

    def test_kurator_darf_ausserhalb_der_region_verorten(
        self, admin_client: TestClient, session, make_photo
    ):
        """Anders als ein Besucher: der Kurator weiss vielleicht von einem Ausflug."""
        foto = make_photo(lat=None, lon=None)
        session.commit()

        antwort = admin_client.patch(
            f"/api/admin/photos/{foto.id}",
            json={"location": {"lat": 48.1372, "lon": 11.5756, "place_name": "Muenchen"}},
        )

        assert antwort.status_code == 200
        assert antwort.json()["location_source"] == "curator"

    def test_verstecktes_foto_verschwindet_von_der_karte(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo()
        session.commit()

        admin_client.patch(f"/api/admin/photos/{foto.id}", json={"status": "hidden"})

        karte = admin_client.get("/api/photos", params={"bbox": "9.5,53.5,9.8,53.7"}).json()
        assert karte["total"] == 0
        # Geloescht ist es nicht -- im Admin-Bereich bleibt es auffindbar.
        assert admin_client.get(f"/api/admin/photos/{foto.id}").status_code == 200

    def test_schlagworte_werden_ersetzt_nicht_ergaenzt(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo()
        session.commit()
        admin_client.patch(f"/api/admin/photos/{foto.id}", json={"tags": ["Muehle", "Umzug"]})

        daten = admin_client.patch(f"/api/admin/photos/{foto.id}", json={"tags": ["Muehle"]}).json()

        assert daten["tags"] == ["Muehle"]

    def test_unbekanntes_foto(self, admin_client: TestClient):
        antwort = admin_client.patch("/api/admin/photos/9999", json={"title": "Neu"})

        assert antwort.status_code == 404
        assert "9999" in antwort.json()["detail"]


class TestBesucherbeitraege:
    def _beitrag(self, client: TestClient, foto_id: int) -> int:
        client.post(f"/api/contribute/{foto_id}/location", json=HOLM)
        return client.get("/api/admin/changes").json()[0]["id"]

    def test_liste_zeigt_was_am_kiosk_passiert_ist(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo(lat=None, lon=None, title="Ohne Ort")
        session.commit()
        admin_client.post(f"/api/contribute/{foto.id}/location", json=HOLM)

        daten = admin_client.get("/api/admin/changes").json()

        assert len(daten) == 1
        assert daten[0]["photo_title"] == "Ohne Ort"
        assert daten[0]["field"] == "location"
        assert daten[0]["revertable"] is True

    def test_zuruecknehmen_legt_das_foto_wieder_vor(
        self, admin_client: TestClient, session, make_photo
    ):
        """Der Sinn der Sache: eine falsche Angabe wird wieder zur offenen Frage."""
        foto = make_photo(lat=None, lon=None)
        session.commit()
        beitrag = self._beitrag(admin_client, foto.id)

        daten = admin_client.post(f"/api/admin/changes/{beitrag}/revert").json()

        assert daten["needs_location"] is True
        assert daten["lat"] is None
        aufgabe = admin_client.get("/api/contribute/next", params={"need": "location"}).json()
        assert aufgabe["photo"]["id"] == foto.id

    def test_zweimal_zuruecknehmen_geht_nicht(self, admin_client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None)
        session.commit()
        beitrag = self._beitrag(admin_client, foto.id)
        admin_client.post(f"/api/admin/changes/{beitrag}/revert")

        antwort = admin_client.post(f"/api/admin/changes/{beitrag}/revert")

        assert antwort.status_code == 409

    def test_von_hand_bearbeitetes_wird_nicht_zurueckgenommen(
        self, admin_client: TestClient, session, make_photo
    ):
        """Sonst wuerfe das Zuruecknehmen die Arbeit des Kurators mit weg."""
        foto = make_photo(lat=None, lon=None)
        session.commit()
        beitrag = self._beitrag(admin_client, foto.id)
        admin_client.patch(
            f"/api/admin/photos/{foto.id}", json={"location": {"lat": 53.63, "lon": 9.68}}
        )

        antwort = admin_client.post(f"/api/admin/changes/{beitrag}/revert")

        assert antwort.status_code == 409
        assert admin_client.get("/api/admin/changes").json()[0]["revertable"] is False

    def test_kuratorenaenderung_steht_nicht_in_der_beitragsliste(
        self, admin_client: TestClient, session, make_photo
    ):
        """Die Liste ist zum Sichten dessen da, was Fremde eingetragen haben."""
        foto = make_photo(title="Alt")
        session.commit()
        admin_client.patch(f"/api/admin/photos/{foto.id}", json={"title": "Neu"})

        assert admin_client.get("/api/admin/changes").json() == []

    def test_zurueckgenommenes_bleibt_auf_wunsch_sichtbar(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo(lat=None, lon=None)
        session.commit()
        beitrag = self._beitrag(admin_client, foto.id)
        admin_client.post(f"/api/admin/changes/{beitrag}/revert")

        assert admin_client.get("/api/admin/changes").json() == []
        mit_allem = admin_client.get("/api/admin/changes", params={"include_reverted": True}).json()
        assert len(mit_allem) == 1
        assert mit_allem[0]["reverted_at"] is not None


class TestStapelUpload:
    def test_ohne_anmeldung_kein_upload(self, client: TestClient, fixtures_dir):
        antwort = client.post(
            "/api/admin/upload", files=[("files", ("scan.jpg", _bild(fixtures_dir), "image/jpeg"))]
        )

        assert antwort.status_code == 401

    def test_foto_ist_schon_nach_dem_hochladen_in_der_datenbank(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        """Kein Warteschlangenmodell: ein geschlossener Browser darf keine Uploads kosten.

        Die Tabelle im Admin-Bereich ist eine Nacharbeitsliste. Was dort liegen bleibt, taucht im
        "Hilf mit"-Bereich auf -- verloren ist es nie.
        """
        antwort = admin_client.post(
            "/api/admin/upload", files=[("files", ("scan.jpg", _bild(fixtures_dir), "image/jpeg"))]
        )

        assert antwort.json()["imported"] == 1
        session.expire_all()
        assert len(session.scalars(select(Photo)).all()) == 1

    def test_jahr_gilt_fuer_den_ganzen_stapel(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        antwort = admin_client.post(
            "/api/admin/upload",
            files=[
                ("files", ("a.jpg", _bild(fixtures_dir, "scan_ohne_exif.jpg"), "image/jpeg")),
                ("files", ("b.jpg", _bild(fixtures_dir, "hochkant.jpg"), "image/jpeg")),
            ],
            data={"year": "1932"},
        )

        daten = antwort.json()
        assert daten["imported"] == 2
        assert [eintrag["photo"]["date_label"] for eintrag in daten["items"]] == ["1932", "1932"]

    def test_ort_gilt_fuer_den_ganzen_stapel(self, admin_client: TestClient, session, fixtures_dir):
        antwort = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("a.jpg", _bild(fixtures_dir), "image/jpeg"))],
            data={"lat": "53.6205", "lon": "9.676", "place_name": "Kirche"},
        )

        foto = antwort.json()["items"][0]["photo"]
        assert foto["place_name"] == "Kirche"
        assert foto["location_source"] == "curator"

    def test_stapelangabe_ueberschreibt_nichts_vorhandenes(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        """Das Bild bringt GPS mit. Was die Datei weiss, schlaegt die Sammelangabe."""
        antwort = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("gps.jpg", _bild(fixtures_dir, "foto_mit_gps.jpg"), "image/jpeg"))],
            data={"lat": "48.1372", "lon": "11.5756"},
        )

        foto = antwort.json()["items"][0]["photo"]
        assert abs(foto["lat"] - 53.62053) < 0.001
        assert foto["location_source"] == "exif"

    def test_dublette_wird_benannt_nicht_verschwiegen(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        """ "3 waren schon da" ist eine Auskunft, Schweigen ist keine."""
        bild = _bild(fixtures_dir)
        admin_client.post("/api/admin/upload", files=[("files", ("a.jpg", bild, "image/jpeg"))])

        daten = admin_client.post(
            "/api/admin/upload", files=[("files", ("nochmal.jpg", bild, "image/jpeg"))]
        ).json()

        assert daten["duplicates"] == 1
        assert daten["imported"] == 0
        assert "Inhaltsgleich" in daten["items"][0]["message"]
        # Das schon vorhandene Foto wird mitgeliefert -- der Admin soll sehen, welches gemeint ist.
        assert daten["items"][0]["photo"] is not None

    def test_textdatei_wird_mit_begruendung_abgewiesen(
        self, admin_client: TestClient, fixtures_dir
    ):
        daten = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("liste.txt", _bild(fixtures_dir, "kein_bild.txt"), "text/plain"))],
        ).json()

        assert daten["rejected"] == 1
        assert "Kein lesbares Bild" in daten["items"][0]["message"]

    def test_pfad_im_dateinamen_bleibt_ohne_wirkung(
        self, admin_client: TestClient, settings, fixtures_dir
    ):
        """Ein Dateiname aus dem Browser ist Eingabe, keine Wegbeschreibung."""
        daten = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("../../boese.jpg", _bild(fixtures_dir), "image/jpeg"))],
        ).json()

        assert daten["items"][0]["filename"] == "boese.jpg"
        assert not (settings.data_dir.parent / "boese.jpg").exists()

    def test_upload_landet_im_importprotokoll(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        admin_client.post(
            "/api/admin/upload", files=[("files", ("scan.jpg", _bild(fixtures_dir), "image/jpeg"))]
        )

        protokoll = admin_client.get("/api/admin/imports").json()

        assert len(protokoll) == 1
        # Nicht der Pfad im temporaeren Ordner, sondern der Name, den der Admin kennt.
        assert protokoll[0]["filename"] == "scan.jpg"
        assert protokoll[0]["result"] == "imported"


class TestImportprotokoll:
    def test_nur_abgewiesene_auf_wunsch(self, admin_client: TestClient, session, fixtures_dir):
        admin_client.post(
            "/api/admin/upload",
            files=[
                ("files", ("gut.jpg", _bild(fixtures_dir), "image/jpeg")),
                ("files", ("schlecht.txt", _bild(fixtures_dir, "kein_bild.txt"), "text/plain")),
            ],
        )

        daten = admin_client.get("/api/admin/imports", params={"result": "rejected"}).json()

        assert [eintrag["filename"] for eintrag in daten] == ["schlecht.txt"]

    def test_neueste_zuerst(self, admin_client: TestClient, session):
        from app.models import ImportLog, ImportResult

        for nummer, tag in enumerate([1, 2, 3], start=1):
            session.add(
                ImportLog(
                    path=f"/tmp/{nummer}.jpg",
                    result=ImportResult.IMPORTED,
                    created_at=datetime(2026, 3, tag, 12, 0),
                )
            )
        session.commit()

        daten = admin_client.get("/api/admin/imports").json()

        assert [eintrag["filename"] for eintrag in daten] == ["3.jpg", "2.jpg", "1.jpg"]


class TestUnberuehrteFelder:
    def test_datierung_ohne_genauigkeit_wird_zum_jahr(
        self, admin_client: TestClient, session, make_photo
    ):
        foto = make_photo(year=None)
        session.commit()

        daten = admin_client.patch(
            f"/api/admin/photos/{foto.id}", json={"date": {"year": 1955}}
        ).json()

        assert daten["date_precision"] == DatePrecision.YEAR
        assert daten["date_label"] == "1955"
