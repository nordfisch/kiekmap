"""Was die API ueber die Uhrzeit sagt -- und was sie bewusst nicht sagt.

Gespeichert wird ueberall UTC: ``func.now()`` in SQLite, ``dates.utc_now()`` in Python, die
JSON-Zustandsdateien. Ohne Zonenmarker hinausgeschrieben ist das keine Angabe, sondern eine Falle:
``new Date("2026-08-18T19:25:21")`` liest eine markerlose ISO-Zeit laut Norm als **Ortszeit**. Der
Verwaltungsbereich zeigte deshalb jeden Besucherbeitrag zwei Stunden zu frueh.

Das ``exif_datetime`` ist die Ausnahme und hat einen eigenen Test: Es kommt aus einer Kamera oder
einem Scanner, die die Wanduhr ihres Standorts schreiben und gar keine Zone kennen.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models import Change, Source


def _gelesen(rohwert: str) -> datetime:
    """Wie der Browser den Wert liest -- ``new Date(...)`` in einer Zeile Python."""
    return datetime.fromisoformat(rohwert)


class TestGespeicherteStempel:
    def test_der_importzeitpunkt_nennt_seine_zone(self, client, make_photo, session):
        """Ohne Marker laege die Anzeige um den Zonenversatz daneben."""
        foto = make_photo()
        session.commit()

        antwort = client.get(f"/api/photos/{foto.id}")
        assert antwort.status_code == 200

        roh = antwort.json()["imported_at"]
        assert _gelesen(roh).tzinfo is not None, f"{roh} traegt keine Zone"
        # Und die Zone ist die richtige: der Zeitpunkt liegt jetzt, nicht zwei Stunden daneben.
        assert abs(_gelesen(roh) - datetime.now(UTC)) < timedelta(minutes=5)

    def test_ein_besucherbeitrag_wird_mit_zone_gemeldet(
        self, admin_client, make_photo, session, settings
    ):
        foto = make_photo(lat=None, lon=None)
        session.commit()

        beitrag = admin_client.post(
            f"/api/contribute/{foto.id}/location",
            json={"lat": 53.62, "lon": 9.676, "place_name": "Hauptstrasse 1"},
        )
        assert beitrag.status_code == 200

        eintrag = admin_client.get("/api/admin/changes").json()["changes"][0]
        assert abs(_gelesen(eintrag["created_at"]) - datetime.now(UTC)) < timedelta(minutes=5)

    def test_die_sicherungserinnerung_nennt_ihre_zone(self, admin_client, settings):
        """Hier verschiebt der Versatz nicht die Uhrzeit, sondern den Tag.

        Die Kachel zeigt nur das Datum. Eine Sicherung um halb eins nachts ist 22:30 UTC vom
        Vortag -- und stuende ohne Marker mit dem falschen Tag da.
        """
        from app.services import backup

        backup.record_backup(settings, "Teststick")

        erinnerung = admin_client.get("/api/admin/overview").json()["backup"]
        gelesen = _gelesen(erinnerung["last_backup_at"])
        assert gelesen.tzinfo is not None
        assert abs(gelesen - datetime.now(UTC)) < timedelta(minutes=5)


class TestDieAusnahme:
    def test_das_scandatum_bleibt_ohne_zone(self, client, make_photo, session):
        """Das EXIF-Datum ist eine Wanduhrzeit, keine UTC-Angabe.

        Ein Scanner schreibt die Uhr seines Standorts und weiss von keiner Zone. Wer ihm UTC
        aufstempelt, verschiebt einen Scan von 14:00 auf 16:00 und erfindet damit eine Tatsache.
        """
        foto = make_photo()
        foto.exif_datetime = datetime(2019, 3, 14, 14, 0, 0)
        session.commit()

        roh = client.get(f"/api/photos/{foto.id}").json()["exif_datetime"]
        assert _gelesen(roh).tzinfo is None, f"{roh} sollte keine Zone tragen"
        assert roh.startswith("2019-03-14T14:00")


class TestEineUhrImGeraet:
    def test_zuruecknehmen_schreibt_dieselbe_uhr_wie_das_anlegen(
        self, admin_client, make_photo, session
    ):
        """Der Fehler, der in der Datenbank stand statt nur in der Anzeige.

        ``created_at`` kam aus SQLite und war UTC, ``reverted_at`` aus ``datetime.now()`` und war
        Ortszeit. Ein sofort zurueckgenommener Beitrag stand damit zwei Stunden nach sich selbst --
        und keine Pruefung im Schema faengt so etwas, weil beide Werte gueltige Zeitstempel sind.
        """
        foto = make_photo(year=None)
        session.commit()

        assert (
            admin_client.post(
                f"/api/contribute/{foto.id}/date", json={"year": 1932, "precision": "year"}
            ).status_code
            == 200
        )

        eintrag = session.scalars(select(Change).where(Change.source == Source.VISITOR)).one()
        assert admin_client.post(f"/api/admin/changes/{eintrag.id}/revert").status_code == 200
        session.refresh(eintrag)

        abstand = abs(eintrag.reverted_at - eintrag.created_at)
        assert abstand < timedelta(minutes=5), f"zwei Uhren im Geraet: {abstand}"

    def test_utc_now_gibt_die_form_zurueck_die_gespeichert_wird(self):
        """Naiv, aber UTC -- genau das, was ``func.now()`` in die Spalte schreibt."""
        from app.services.dates import utc_now

        jetzt = utc_now()
        assert jetzt.tzinfo is None
        assert abs(jetzt - datetime.now(UTC).replace(tzinfo=None)) < timedelta(seconds=5)
