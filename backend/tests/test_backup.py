"""Tests der Sicherung auf USB-Stick.

Drei Zusagen tragen diese Stufe, und alle drei brechen still:

  1. Ein gewoehnlicher Ordner unter /media ist kein Stick. Ohne diese Pruefung landet die
     Sicherung auf derselben SD-Karte, gegen deren Ausfall sie schuetzen soll.
  2. Die zweite Sicherung kopiert nichts noch einmal. Bricht das, dauert sie eine Stunde statt
     Sekunden -- und wird nicht mehr gemacht.
  3. Wiederherstellen legt den bisherigen Bestand beiseite, statt ihn zu loeschen. Wer die
     falsche Sicherung einspielt, soll nicht alles verloren haben.
"""

import io
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.services import backup
from app.services.storage import THUMBNAIL_SIZES, original_path, thumbnail_path


@pytest.fixture
def stick(tmp_path: Path, settings, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Ein Ordner, der als USB-Stick durchgeht.

    Ein echter Einhaengepunkt laesst sich im Test nicht herstellen, deshalb steht die Pruefung
    ``_is_mounted`` fuer diesen einen Ordner still.
    """
    media = tmp_path / "media"
    drive = media / "SANDISK"
    drive.mkdir(parents=True)

    settings.media_dir = media
    monkeypatch.setattr(backup, "_is_mounted", lambda path: path == drive)
    return drive


@pytest.fixture
def collection(settings):
    """Fotos auf der Platte, so abgelegt wie der Import es tut."""

    def create(count: int = 3) -> list[str]:
        shas = []
        for index in range(count):
            sha = f"{index:064x}"
            original = original_path(settings.photos_dir, sha, ".jpg")
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes(b"bild-" + str(index).encode())
            for size in THUMBNAIL_SIZES:
                thumb = thumbnail_path(settings.thumbs_dir, sha, size)
                thumb.parent.mkdir(parents=True, exist_ok=True)
                thumb.write_bytes(b"vorschau")
            shas.append(sha)
        return shas

    return create


def _drive(settings) -> backup.Drive:
    return backup.find_drives(settings.media_dir)[0]


def _nichts_melden(done: int, total: int, message: str) -> None:
    pass


class TestDatentraegerErkennen:
    def test_ohne_stick_keine_auswahl(self, settings, tmp_path: Path):
        settings.media_dir = tmp_path / "media"

        assert backup.find_drives(settings.media_dir) == []

    def test_stick_wird_gefunden(self, settings, stick: Path):
        gefunden = backup.find_drives(settings.media_dir)

        assert len(gefunden) == 1
        assert gefunden[0].name == "SANDISK"
        assert gefunden[0].free_bytes > 0

    def test_gewoehnlicher_ordner_ist_kein_stick(self, settings, stick: Path):
        """Der wichtigste Fall hier.

        Wuerde ein liegengebliebener Ordner unter /media als Ziel angeboten, liefe die Sicherung
        auf dieselbe SD-Karte, gegen deren Ausfall sie schuetzen soll -- und niemand saehe es.
        """
        (stick.parent / "nur-ein-ordner").mkdir()

        namen = [drive.name for drive in backup.find_drives(settings.media_dir)]

        assert namen == ["SANDISK"]

    def test_stick_auch_zwei_ebenen_tief(
        self, settings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Raspberry Pi OS haengt unter /media/<benutzer>/<bezeichnung> ein."""
        media = tmp_path / "media"
        tief = media / "pi" / "USB-STICK"
        tief.mkdir(parents=True)
        settings.media_dir = media
        monkeypatch.setattr(backup, "_is_mounted", lambda path: path == tief)

        gefunden = backup.find_drives(media)

        assert [drive.name for drive in gefunden] == ["USB-STICK"]

    def test_schreibgeschuetzter_datentraeger_wird_nicht_angeboten(
        self, settings, stick: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Sonst faellt es erst auf, nachdem jemand den Knopf gedrueckt hat.

        Auf dem Mac faengt diese Pruefung ausserdem die Systemeinhaengungen unter /Volumes ab,
        die sonst als Sicherungsziel in der Liste stuenden.
        """
        monkeypatch.setattr(backup, "_is_writable", lambda path: False)

        assert backup.find_drives(settings.media_dir) == []

    def test_ausgedachter_pfad_wird_nicht_angenommen(self, settings, stick: Path):
        """Der Pfad kommt aus dem Browser zurueck -- er ist Eingabe, keine Tatsache."""
        assert backup.find_drive(settings.media_dir, "/") is None
        assert backup.find_drive(settings.media_dir, str(stick)) is not None


class TestSicherung:
    def test_fotos_und_angaben_landen_auf_dem_stick(self, session, settings, stick, collection):
        shas = collection(3)

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        ziel = stick / backup.BACKUP_DIR_NAME
        assert (ziel / "photomap.db").is_file()
        for sha in shas:
            assert (ziel / "photos" / sha[0:2] / sha[2:4] / f"{sha}.jpg").is_file()

    def test_vorschaubilder_wandern_mit(self, session, settings, stick, collection):
        """Sonst rechnete ein wiederhergestelltes Geraet erst eine Stunde, bevor es etwas zeigt."""
        sha = collection(1)[0]

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        ziel = stick / backup.BACKUP_DIR_NAME
        for size in THUMBNAIL_SIZES:
            assert (ziel / "thumbs" / str(size) / sha[0:2] / sha[2:4] / f"{sha}.webp").is_file()

    def test_zweite_sicherung_kopiert_nichts_noch_einmal(
        self, session, settings, stick, collection
    ):
        """Der Grund, warum ueberhaupt jemand ein zweites Mal sichert."""
        collection(3)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        meldung = backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        # Die Angaben werden immer neu geschrieben, die Bilder nicht.
        assert "Neue Bilder gab es nicht" in meldung

    def test_neues_foto_kommt_beim_zweiten_mal_dazu(self, session, settings, stick, collection):
        collection(2)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)
        neu = "f" * 64
        pfad = original_path(settings.photos_dir, neu, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"noch ein bild")

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        ziel = stick / backup.BACKUP_DIR_NAME / "photos" / neu[0:2] / neu[2:4] / f"{neu}.jpg"
        assert ziel.is_file()

    def test_zu_wenig_platz_wird_vorher_gesagt(self, session, settings, stick, collection):
        """Lieber gar nicht anfangen als auf halber Strecke stehen bleiben."""
        collection(2)
        laufwerk = _drive(settings)
        laufwerk.free_bytes = 1

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_backup(session, settings, laufwerk, _nichts_melden)

        assert "zu wenig Platz" in str(fehler.value)

    def test_fortschritt_zaehlt_fotos(self, session, settings, stick, collection):
        collection(3)
        schritte = []

        backup.run_backup(
            session, settings, _drive(settings), lambda d, t, m: schritte.append((d, t))
        )

        assert schritte[-1] == (3, 3)

    def test_manifest_nennt_anzahl_und_ort(self, session, settings, stick, collection):
        collection(2)
        (settings.data_dir / "region.json").write_text('{"name": "Holm"}', encoding="utf-8")

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        info = backup.read_manifest(stick / backup.BACKUP_DIR_NAME)
        assert info is not None
        assert info.photos == 2
        assert info.place == "Holm"

    def test_zustandsdatei_gehoert_nicht_in_die_sicherung(
        self, session, settings, stick, collection
    ):
        """Sie sagt etwas ueber dieses Geraet, nicht ueber die Sammlung."""
        collection(1)

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        assert not (stick / backup.BACKUP_DIR_NAME / backup.STATE_FILE).exists()
        assert (settings.data_dir / backup.STATE_FILE).is_file()


class TestWiederherstellung:
    def _sicherung_anlegen(self, session, settings, stick, collection, anzahl=2):
        shas = collection(anzahl)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)
        return shas

    def test_unvollstaendige_sicherung_wird_abgelehnt(self, settings, stick):
        (stick / backup.BACKUP_DIR_NAME).mkdir()

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert "nicht komplett" in str(fehler.value)

    def test_bestand_wird_ersetzt(self, session, settings, stick, collection):
        shas = self._sicherung_anlegen(session, settings, stick, collection)
        # Inzwischen ist auf dem Geraet etwas anderes passiert.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()

    def test_bisheriger_stand_wird_beiseitegelegt_nicht_geloescht(
        self, session, settings, stick, collection
    ):
        """Wer die falsche Sicherung einspielt, soll nicht alles verloren haben."""
        self._sicherung_anlegen(session, settings, stick, collection)
        spaeter = "e" * 64
        pfad = original_path(settings.photos_dir, spaeter, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"nach der sicherung entstanden")

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert not pfad.exists(), "in der Sicherung war es nicht"
        beiseite = list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*"))
        assert len(beiseite) == 1
        assert (beiseite[0] / "photos" / spaeter[0:2] / spaeter[2:4] / f"{spaeter}.jpg").is_file()

    def test_write_ahead_log_wandert_mit_beiseite(self, session, settings, stick, collection):
        """Ein liegengebliebenes -wal gehoert zu einer anderen Datenbank.

        Bliebe es neben der zurueckgespielten Datei liegen, versuchte SQLite es anzuwenden.
        """
        self._sicherung_anlegen(session, settings, stick, collection, anzahl=1)
        (settings.data_dir / "photomap.db-wal").write_bytes(b"altes journal")

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert not (settings.data_dir / "photomap.db-wal").exists()
        beiseite = next(iter(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*")))
        assert (beiseite / "photomap.db-wal").is_file()

    def test_arbeitsordner_bleibt_nicht_liegen(self, session, settings, stick, collection):
        self._sicherung_anlegen(session, settings, stick, collection, anzahl=1)

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert not (settings.data_dir / backup.RESTORE_WORK_DIR).exists()


class TestErinnerung:
    def test_ohne_sicherung_ist_es_ueberfaellig(self, settings):
        """Nie gesichert ist genau der Fall, der die Erinnerung braucht."""
        zustand = backup.read_state(settings)

        assert zustand.last_backup_at is None
        assert zustand.overdue is True

    def test_frische_sicherung_ist_nicht_ueberfaellig(self, settings):
        backup.record_backup(settings, "SANDISK")

        zustand = backup.read_state(settings)

        assert zustand.days_since == 0
        assert zustand.overdue is False
        assert zustand.last_drive == "SANDISK"

    def test_alte_sicherung_ist_ueberfaellig(self, settings):
        # UTC, weil `_stamp()` das schreibt und `read_state` es so liest. Mit Ortszeit war dieser
        # Test zwei Stunden am Tag rot: Ab 22 Uhr MESZ rutscht der umgerechnete Stempel auf den
        # naechsten Kalendertag, und die Differenz fiel um einen Tag kleiner aus.
        alt = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=backup.OVERDUE_DAYS + 4)
        (settings.data_dir / backup.STATE_FILE).write_text(
            f'{{"last_backup_at": "{alt.isoformat()}", "last_drive": "X"}}', encoding="utf-8"
        )

        zustand = backup.read_state(settings)

        assert zustand.days_since == backup.OVERDUE_DAYS + 4
        assert zustand.overdue is True

    def test_kaputte_zustandsdatei_gilt_als_nie_gesichert(self, settings):
        (settings.data_dir / backup.STATE_FILE).write_text("kein json", encoding="utf-8")

        assert backup.read_state(settings).last_backup_at is None


class TestAuftrag:
    def test_zweiter_auftrag_wird_abgewiesen(self):
        auftrag = backup.Job()
        laeuft = __import__("threading").Event()

        auftrag.start("backup", lambda report: (laeuft.wait(2), "fertig")[1])
        try:
            assert auftrag.start("restore", lambda report: "geht nicht") is False
        finally:
            laeuft.set()

    def test_fehler_landet_im_status(self):
        auftrag = backup.Job()

        def scheitert(report):
            raise backup.BackupError("Der Stick ist weg.")

        auftrag.start("backup", scheitert)
        _warten(auftrag)

        assert auftrag.status().phase == "error"
        assert auftrag.status().error == "Der Stick ist weg."

    def test_unerwarteter_fehler_bleibt_nicht_stumm(self):
        """Sonst stuende der Balken still und niemand wuesste, warum."""
        auftrag = backup.Job()

        def platzt(report):
            raise RuntimeError("kaputt")

        auftrag.start("backup", platzt)
        _warten(auftrag)

        assert auftrag.status().phase == "error"
        assert "schiefgegangen" in auftrag.status().error

    def test_bestaetigen_setzt_zurueck(self):
        auftrag = backup.Job()
        auftrag.start("backup", lambda report: "fertig")
        _warten(auftrag)

        auftrag.reset()

        assert auftrag.status().phase == "idle"


def _warten(auftrag: backup.Job, sekunden: float = 3.0) -> None:
    """Der Auftrag laeuft in einem Faden -- kurz warten, bis er durch ist."""
    import time

    ende = time.monotonic() + sekunden
    while auftrag.running and time.monotonic() < ende:
        time.sleep(0.01)


class TestUeberDieApi:
    """Der Weg, den die Oberflaeche geht: Laufwerke abfragen, starten, Status nachfragen."""

    def _bis_fertig(self, client, sekunden: float = 5.0) -> dict:
        import time

        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            zustand = client.get("/api/admin/backup/status").json()
            if zustand["phase"] != "running":
                return zustand
            time.sleep(0.02)
        raise AssertionError("Der Auftrag wurde nicht fertig")

    def test_ohne_anmeldung_keine_laufwerke(self, client):
        assert client.get("/api/admin/backup/drives").status_code == 401

    def test_ohne_stick_steht_die_liste_leer(self, admin_client, settings, tmp_path: Path):
        settings.media_dir = tmp_path / "media"

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["drives"] == []
        # Trotzdem beantwortbar: wie viel gesichert werden muesste und wann zuletzt.
        assert daten["reminder"]["overdue"] is True

    def test_liste_nennt_platz_und_bedarf(self, admin_client, settings, stick, collection):
        collection(2)

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["photos"] == 2
        assert daten["needed_bytes"] > 0
        assert daten["drives"][0]["name"] == "SANDISK"
        assert daten["drives"][0]["enough_space"] is True

    def test_sicherung_laeuft_durch(self, admin_client, settings, stick, collection):
        collection(2)

        gestartet = admin_client.post("/api/admin/backup/start", json={"path": str(stick)}).json()
        assert gestartet["kind"] == "backup"

        zustand = self._bis_fertig(admin_client)
        assert zustand["phase"] == "done"
        assert "2 Fotos" in zustand["message"]
        assert (stick / backup.BACKUP_DIR_NAME / "photomap.db").is_file()

    def test_erinnerung_steht_danach_in_der_uebersicht(
        self, admin_client, settings, stick, collection
    ):
        collection(1)
        admin_client.post("/api/admin/backup/start", json={"path": str(stick)})
        self._bis_fertig(admin_client)

        uebersicht = admin_client.get("/api/admin/overview").json()

        assert uebersicht["backup"]["overdue"] is False
        assert uebersicht["backup"]["last_drive"] == "SANDISK"

    def test_unbekannter_stick_wird_abgewiesen(self, admin_client, settings, stick):
        antwort = admin_client.post("/api/admin/backup/start", json={"path": "/"})

        assert antwort.status_code == 404
        assert "nicht mehr da" in antwort.json()["detail"]

    def test_bestaetigen_raeumt_den_status_ab(self, admin_client, settings, stick, collection):
        collection(1)
        admin_client.post("/api/admin/backup/start", json={"path": str(stick)})
        self._bis_fertig(admin_client)

        zustand = admin_client.post("/api/admin/backup/acknowledge").json()

        assert zustand["phase"] == "idle"

    def test_wiederherstellen_ohne_sicherung_meldet_es(self, admin_client, settings, stick):
        (stick / backup.BACKUP_DIR_NAME).mkdir()

        admin_client.post("/api/admin/backup/restore", json={"path": str(stick)})
        zustand = self._bis_fertig(admin_client)

        assert zustand["phase"] == "error"
        assert "nicht komplett" in zustand["error"]


class TestArchiv:
    """Die Sicherung als eine Datei -- der zweite Weg aus der Sammlung heraus.

    Die eine Zusage, die alles andere traegt: **Das Archiv ist der Ordner, den auch der Stick
    bekommt, nur gezippt.** Daran haengt, dass eine ZIP-Sicherung ohne Upload-Weg trotzdem
    zurueckspielbar ist -- auf einen Stick entpacken, fertig. Bricht diese Eigenschaft, ist der
    Rueckweg weg, ohne dass es jemandem auffiele.
    """

    def _archiv(self, session, settings) -> bytes:
        return b"".join(backup.stream_archive(session, settings))

    def test_entpacktes_archiv_laesst_sich_wiederherstellen(
        self, session, settings, stick, collection
    ):
        """Der wichtigste Test des Archivs: Er bindet die beiden Wege aneinander."""
        shas = collection(3)
        daten = self._archiv(session, settings)

        # Auf den Stick entpacken -- genau das, was jemand von Hand taete.
        with zipfile.ZipFile(io.BytesIO(daten)) as archiv:
            archiv.extractall(stick)

        # Und danach der ganz gewoehnliche Weg zurueck.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()
        backup.run_restore(settings, _drive(settings), _nichts_melden)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file(), (
                "das entpackte Archiv war fuer die Wiederherstellung nicht brauchbar"
            )

    def test_archiv_enthaelt_denselben_ordner_wie_der_stick(self, session, settings, collection):
        collection(2)

        with zipfile.ZipFile(io.BytesIO(self._archiv(session, settings))) as archiv:
            namen = archiv.namelist()

        assert {name.split("/")[0] for name in namen} == {backup.BACKUP_DIR_NAME}
        assert f"{backup.BACKUP_DIR_NAME}/photomap.db" in namen
        assert f"{backup.BACKUP_DIR_NAME}/{backup.MANIFEST_NAME}" in namen
        assert any(name.startswith(f"{backup.BACKUP_DIR_NAME}/photos/") for name in namen)
        assert any(name.startswith(f"{backup.BACKUP_DIR_NAME}/thumbs/") for name in namen)

    def test_archiv_wird_nicht_komprimiert(self, session, settings, collection):
        """JPEG und WebP sind schon komprimiert -- ein zweiter Durchgang kostet den Pi nur Zeit."""
        collection(2)

        with zipfile.ZipFile(io.BytesIO(self._archiv(session, settings))) as archiv:
            verfahren = {eintrag.compress_type for eintrag in archiv.infolist()}

        assert verfahren == {zipfile.ZIP_STORED}

    def test_archiv_entsteht_im_strom(self, session, settings, collection):
        """Sonst laege es vollstaendig im Speicher -- auf einem Pi mit 2 GB keine gute Idee."""
        collection(5)

        stuecke = list(backup.stream_archive(session, settings))

        assert len(stuecke) > 1, "der Erzeuger hat alles auf einmal geliefert"

    def test_abgebrochener_download_zaehlt_nicht_als_sicherung(self, session, settings, collection):
        """Was der Browser nicht bekommen hat, schuetzt niemanden -- also gilt es auch nicht."""
        collection(3)
        strom = backup.stream_archive(session, settings)
        next(strom)  # angefangen, aber nicht zu Ende gelesen
        strom.close()

        assert backup.read_state(settings).last_backup_at is None

    def test_vollstaendiger_download_setzt_die_erinnerung_zurueck(
        self, session, settings, collection
    ):
        collection(2)

        self._archiv(session, settings)

        zustand = backup.read_state(settings)
        assert zustand.last_backup_at is not None
        assert zustand.last_drive == backup.ZIP_DRIVE_NAME

    def test_dateiname_nennt_ort_und_tag(self, settings):
        settings.region_file.parent.mkdir(parents=True, exist_ok=True)
        settings.region_file.write_text('{"name": "Holm"}', encoding="utf-8")

        name = backup.archive_name(settings)

        assert name.startswith("photomap-sicherung-holm-")
        assert name.endswith(".zip")
        assert name.isascii(), "der Name steht in einem HTTP-Kopf"


class TestArchivUeberDieApi:
    def test_ohne_ticket_kein_download(self, admin_client):
        assert admin_client.get("/api/admin/backup/zip").status_code == 422

    def test_erfundenes_ticket_wird_abgewiesen(self, admin_client):
        antwort = admin_client.get("/api/admin/backup/zip", params={"ticket": "ausgedacht"})

        assert antwort.status_code == 401

    def test_ticket_gilt_nur_einmal(self, admin_client, settings, collection):
        collection(1)
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]

        erste = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})
        zweite = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})

        assert erste.status_code == 200
        assert zweite.status_code == 401, "ein Ticket darf sich nicht wiederverwenden lassen"

    def test_ticket_nur_fuer_angemeldete(self, client):
        assert client.post("/api/admin/backup/zip/ticket").status_code == 401

    def test_download_liefert_ein_archiv(self, admin_client, settings, collection):
        collection(2)
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]

        antwort = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})

        assert antwort.headers["content-type"] == "application/zip"
        assert "attachment" in antwort.headers["content-disposition"]
        with zipfile.ZipFile(io.BytesIO(antwort.content)) as archiv:
            assert archiv.testzip() is None

    def test_laufender_auftrag_blockiert_den_download(self, admin_client, settings):
        """Eine Wiederherstellung wuerde die Dateien unter dem laufenden Strom austauschen."""
        import threading

        haltepunkt = threading.Event()
        backup.job.start("backup", lambda report: (haltepunkt.wait(2), "fertig")[1])
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]
        try:
            antwort = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})
        finally:
            haltepunkt.set()

        assert antwort.status_code == 409
