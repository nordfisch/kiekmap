"""Tests des Imports vom USB-Stick.

Die eine Zusage, die diese Funktion von der Ordnerueberwachung unterscheidet: **Der Stick gehoert
jemand anderem.** Im ueberwachten Eingangsordner werden aufgenommene Dateien beiseitegeraeumt --
auf einem fremden Datentraeger wird nur gelesen. Wer seinen Stick nach dem Import mit fehlenden
Dateien zurueckbekommt, vertraut dem Geraet nie wieder.

Der zweite Punkt ist der Pfad: Er kommt aus dem Browser zurueck und ist Eingabe, keine Tatsache.
Ohne Pruefung waere der Admin-Bereich ein Weg, jeden Ordner des Geraets einzulesen.
"""

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import Photo
from app.services import backup, importer


@pytest.fixture
def stick(tmp_path: Path, settings, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Ein Ordner, der als USB-Stick durchgeht."""
    media = tmp_path / "media"
    drive = media / "SCANSTICK"
    drive.mkdir(parents=True)

    settings.media_dir = media
    monkeypatch.setattr(backup, "_is_mounted", lambda path: path == drive)
    return drive


@pytest.fixture
def bilder_auf_dem_stick(stick: Path, fixtures_dir: Path):
    """Legt Bilder in einen Ordner auf dem Stick und gibt ihn zurueck."""

    def anlegen(unterordner: str = "Scans2024", namen=("scan_ohne_exif.jpg", "hochkant.jpg")):
        ordner = stick / unterordner
        ordner.mkdir(parents=True, exist_ok=True)
        for name in namen:
            shutil.copy2(fixtures_dir / name, ordner / name)
        return ordner

    return anlegen


class TestOrdnerFinden:
    def test_ordner_mit_bildern_werden_angeboten(self, settings, stick, bilder_auf_dem_stick):
        bilder_auf_dem_stick("Scans2024")

        gefunden = importer.find_image_folders(stick)

        assert [ordner.name for ordner in gefunden] == ["Scans2024"]
        assert gefunden[0].images == 2

    def test_ordner_ohne_bilder_werden_nicht_angeboten(self, settings, stick):
        (stick / "Rechnungen").mkdir()
        (stick / "Rechnungen" / "brief.txt").write_text("nichts", encoding="utf-8")

        assert importer.find_image_folders(stick) == []

    def test_die_eigene_sicherung_wird_uebergangen(self, settings, stick, bilder_auf_dem_stick):
        """Sonst laese das Geraet seine eigene Sicherung als Stapel neuer Fotos wieder ein."""
        bilder_auf_dem_stick(f"{backup.BACKUP_DIR_NAME}/photos")

        assert importer.find_image_folders(stick) == []

    def test_versteckte_ordner_bleiben_aussen_vor(self, settings, stick, bilder_auf_dem_stick):
        bilder_auf_dem_stick(".Trashes")

        assert importer.find_image_folders(stick) == []


class TestAufnehmen:
    def test_dateien_auf_dem_stick_bleiben_liegen(
        self, session, settings, stick, bilder_auf_dem_stick
    ):
        """Die wichtigste Zusage dieser Funktion.

        Der ueberwachte Eingangsordner raeumt Aufgenommenes nach _erledigt/ -- dort ist das
        richtig, es ist unser Ordner. Auf einem fremden Stick waere es ein Uebergriff.
        """
        ordner = bilder_auf_dem_stick()
        vorher = sorted(p.name for p in ordner.iterdir())

        importer.import_from_folder(session, ordner, settings)

        assert sorted(p.name for p in ordner.iterdir()) == vorher
        assert not (ordner / importer.DONE_DIR).exists()

    def test_fotos_landen_in_der_sammlung(self, session, settings, stick, bilder_auf_dem_stick):
        ordner = bilder_auf_dem_stick()

        meldung = importer.import_from_folder(session, ordner, settings)

        assert len(session.scalars(select(Photo)).all()) == 2
        assert "2 Fotos aufgenommen" in meldung
        assert "abgezogen werden" in meldung

    def test_dubletten_werden_gezaehlt_nicht_verschwiegen(
        self, session, settings, stick, bilder_auf_dem_stick
    ):
        ordner = bilder_auf_dem_stick()
        importer.import_from_folder(session, ordner, settings)

        meldung = importer.import_from_folder(session, ordner, settings)

        assert "0 Fotos aufgenommen" in meldung
        assert "2 waren schon da" in meldung

    def test_jahr_gilt_fuer_den_ganzen_ordner(self, session, settings, stick, bilder_auf_dem_stick):
        from app.models import DatePrecision

        ordner = bilder_auf_dem_stick()

        importer.import_from_folder(
            session,
            ordner,
            settings,
            defaults=lambda foto: importer.apply_batch_defaults(
                foto, 1932, DatePrecision.YEAR, None, None, "Kirche"
            ),
        )

        fotos = session.scalars(select(Photo)).all()
        assert all(foto.date_from.year == 1932 for foto in fotos)
        assert all(foto.place_name == "Kirche" for foto in fotos)

    def test_fortschritt_zaehlt_die_bilder(self, session, settings, stick, bilder_auf_dem_stick):
        ordner = bilder_auf_dem_stick()
        schritte = []

        importer.import_from_folder(
            session, ordner, settings, report=lambda d, t, m: schritte.append((d, t))
        )

        assert schritte == [(1, 2), (2, 2)]

    def test_abgebrochenes_laesst_das_bisherige_stehen(
        self, session, settings, stick, bilder_auf_dem_stick
    ):
        """Wird der Stick mittendrin abgezogen, ist gelesen, was gelesen war.

        Deshalb wird Foto fuer Foto festgeschrieben und nicht erst am Ende.
        """
        ordner = bilder_auf_dem_stick()

        def nach_dem_ersten(done, total, message):
            if done == 1:
                raise OSError("Stick abgezogen")

        with pytest.raises(OSError):
            importer.import_from_folder(session, ordner, settings, report=nach_dem_ersten)

        session.expire_all()
        assert len(session.scalars(select(Photo)).all()) == 1


class TestUeberDieApi:
    def test_ohne_anmeldung_keine_ordner(self, client: TestClient):
        assert client.get("/api/admin/import/folders").status_code == 401

    def test_ordner_werden_mit_laufwerk_genannt(
        self, admin_client: TestClient, stick, bilder_auf_dem_stick
    ):
        bilder_auf_dem_stick()

        daten = admin_client.get("/api/admin/import/folders").json()

        assert daten[0]["drive"] == "SCANSTICK"
        assert daten[0]["name"] == "Scans2024"
        assert daten[0]["images"] == 2

    def test_pfad_ausserhalb_des_sticks_wird_abgewiesen(
        self, admin_client: TestClient, stick, tmp_path: Path
    ):
        """Sonst waere der Admin-Bereich ein Weg, jeden Ordner des Geraets einzulesen."""
        fremd = tmp_path / "woanders"
        fremd.mkdir()

        antwort = admin_client.post("/api/admin/import/start", json={"path": str(fremd)})

        assert antwort.status_code == 404

    def test_hinaufsteigen_hilft_auch_nicht(self, admin_client: TestClient, stick):
        antwort = admin_client.post("/api/admin/import/start", json={"path": f"{stick}/../../etc"})

        assert antwort.status_code == 404

    def test_import_laeuft_durch(
        self, admin_client: TestClient, session, stick, bilder_auf_dem_stick
    ):
        import time

        ordner = bilder_auf_dem_stick()

        gestartet = admin_client.post(
            "/api/admin/import/start", json={"path": str(ordner), "year": 1932}
        ).json()
        assert gestartet["kind"] == "import"

        ende = time.monotonic() + 5
        while time.monotonic() < ende:
            zustand = admin_client.get("/api/admin/backup/status").json()
            if zustand["phase"] != "running":
                break
            time.sleep(0.02)

        assert zustand["phase"] == "done"
        assert "2 Fotos aufgenommen" in zustand["message"]

    def test_neben_einer_sicherung_laeuft_kein_import(
        self, admin_client: TestClient, stick, bilder_auf_dem_stick
    ):
        """Ein Auftrag fuer das Geraet. Zwei gleichzeitig schrieben sich gegenseitig um."""
        ordner = bilder_auf_dem_stick()
        laeuft = __import__("threading").Event()
        backup.job.start("backup", lambda report: (laeuft.wait(2), "fertig")[1])

        try:
            antwort = admin_client.post("/api/admin/import/start", json={"path": str(ordner)})
            assert antwort.status_code == 409
        finally:
            laeuft.set()
