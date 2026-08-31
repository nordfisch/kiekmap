"""Tests of the backup to a USB stick.

Four promises carry this stage, and all four break silently:

  1. An ordinary folder under /media is no stick. Without this check the backup lands on the very
     SD card whose failure it is meant to protect against.
  2. The second backup copies nothing twice. If that breaks, it takes an hour instead of seconds
     -- and stops being made.
  3. Restoring sets the previous collection aside instead of deleting it. Whoever plays in the
     wrong backup should not have lost everything.
  4. A restored backup brings its schema with it, and the program catches that up. Without it the
     device looks normal and still accepts nothing any more.
"""

import io
import sqlite3
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.services import backup, schema
from app.services.storage import THUMBNAIL_SIZES, original_path, thumbnail_path

#: The initial schema -- the revision a backup from before the first migration stands at.
#: Named explicitly, because this revision is exactly the case of 12 August 2026.
INITIAL_SCHEMA = "1cf9ccd28cd7"


@pytest.fixture
def stick(tmp_path: Path, settings, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A folder that passes for a USB stick.

    A real mount point cannot be produced in a test, so the check ``drives._is_mounted`` is held
    still for this one folder.
    """
    media = tmp_path / "media"
    drive = media / "SANDISK"
    drive.mkdir(parents=True)

    settings.media_dir = media
    monkeypatch.setattr(backup.drives, "_is_mounted", lambda path: path == drive)
    return drive


@pytest.fixture
def collection(settings):
    """Photos on disk, filed the way the import files them."""

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


def _report_nothing(done: int, total: int, message: str) -> None:
    pass


class TestRecognisingDrives:
    def test_without_a_stick_there_is_no_choice(self, settings, tmp_path: Path):
        settings.media_dir = tmp_path / "media"

        assert backup.find_drives(settings.media_dir) == []

    def test_a_stick_is_found(self, settings, stick: Path):
        gefunden = backup.find_drives(settings.media_dir)

        assert len(gefunden) == 1
        assert gefunden[0].name == "SANDISK"
        assert gefunden[0].free_bytes > 0

    def test_an_ordinary_folder_is_no_stick(self, settings, stick: Path):
        """The most important case here.

        If a folder left lying under /media were offered as a target, the backup would run onto the
        very SD card whose failure it is meant to protect against -- and nobody would see it.
        """
        (stick.parent / "nur-ein-ordner").mkdir()

        namen = [drive.name for drive in backup.find_drives(settings.media_dir)]

        assert namen == ["SANDISK"]

    def test_a_stick_two_levels_down_too(
        self, settings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Raspberry Pi OS mounts under /media/<user>/<label>."""
        media = tmp_path / "media"
        tief = media / "pi" / "USB-STICK"
        tief.mkdir(parents=True)
        settings.media_dir = media
        monkeypatch.setattr(backup.drives, "_is_mounted", lambda path: path == tief)

        gefunden = backup.find_drives(media)

        assert [drive.name for drive in gefunden] == ["USB-STICK"]

    def test_a_symlink_is_no_drive(self, settings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """The case that really happened on 14 August 2026.

        A symlink under /media looks like an ordinary folder, because ``os.path.ismount`` says no
        for a symlink on principle. The search therefore descends one level -- the level needed for
        ``/media/<user>/<label>`` -- and follows it wherever it leads. On the development Mac a
        ``/Volumes/Danger`` pointed at the root, and the admin view offered the data directory
        itself as a backup target. The backup landed in the folder it backs up -- with a manifest,
        so looking like a real one.
        """
        media = tmp_path / "media"
        media.mkdir()
        anderswo = tmp_path / "anderswo"
        mounted = anderswo / "data"
        mounted.mkdir(parents=True)
        (media / "Danger").symlink_to(anderswo)
        settings.media_dir = media
        # Compared resolved, not literally: otherwise the check in place does not model the
        # symlink at all, and the test would be green even without the safeguard.
        monkeypatch.setattr(
            backup.drives, "_is_mounted", lambda path: path.resolve() == mounted.resolve()
        )

        assert backup.find_drives(media) == []

    def test_a_write_protected_drive_is_not_offered(
        self, settings, stick: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Otherwise it is only noticed after somebody has pressed the button.

        On the Mac this check also catches the system mounts under /Volumes, which would otherwise
        stand in the list as backup targets.
        """
        monkeypatch.setattr(backup.drives, "_is_writable", lambda path: False)

        assert backup.find_drives(settings.media_dir) == []

    def test_an_invented_path_is_not_accepted(self, settings, stick: Path):
        """The path comes back from the browser -- it is input, not fact."""
        assert backup.find_drive(settings.media_dir, "/") is None
        assert backup.find_drive(settings.media_dir, str(stick)) is not None


class TestBackingUp:
    def test_photos_and_entries_end_up_on_the_stick(self, session, settings, stick, collection):
        shas = collection(3)

        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        target = stick / backup.BACKUP_DIR_NAME
        assert (target / "kiekmap.db").is_file()
        for sha in shas:
            assert (target / "photos" / sha[0:2] / sha[2:4] / f"{sha}.jpg").is_file()

    def test_thumbnails_come_along(self, session, settings, stick, collection):
        """Otherwise a restored device would compute for an hour before showing anything."""
        sha = collection(1)[0]

        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        target = stick / backup.BACKUP_DIR_NAME
        for size in THUMBNAIL_SIZES:
            assert (target / "thumbs" / str(size) / sha[0:2] / sha[2:4] / f"{sha}.webp").is_file()

    def test_a_second_backup_copies_nothing_twice(self, session, settings, stick, collection):
        """The reason anybody makes a second backup at all."""
        collection(3)
        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        message = backup.run_backup(session, settings, _drive(settings), _report_nothing)

        # The entries are always rewritten, the images are not.
        assert "Neue Bilder gab es nicht" in message

    def test_a_new_photo_is_added_the_second_time(self, session, settings, stick, collection):
        collection(2)
        backup.run_backup(session, settings, _drive(settings), _report_nothing)
        fresh = "f" * 64
        pfad = original_path(settings.photos_dir, fresh, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"noch ein bild")

        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        target = (
            stick / backup.BACKUP_DIR_NAME / "photos" / fresh[0:2] / fresh[2:4] / f"{fresh}.jpg"
        )
        assert target.is_file()

    def test_too_little_space_is_said_beforehand(self, session, settings, stick, collection):
        """Better not to start at all than to stop half way."""
        collection(2)
        laufwerk = _drive(settings)
        laufwerk.free_bytes = 1

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_backup(session, settings, laufwerk, _report_nothing)

        assert "zu wenig Platz" in str(fehler.value)

    def test_progress_counts_photos(self, session, settings, stick, collection):
        collection(3)
        steps = []

        backup.run_backup(session, settings, _drive(settings), lambda d, t, m: steps.append((d, t)))

        assert steps[-1] == (3, 3)

    def test_the_manifest_names_the_count_and_the_place(self, session, settings, stick, collection):
        collection(2)
        (settings.data_dir / "region.json").write_text('{"name": "Holm"}', encoding="utf-8")

        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        info = backup.read_manifest(stick / backup.BACKUP_DIR_NAME)
        assert info is not None
        assert info.photos == 2
        assert info.place == "Holm"

    def test_the_state_file_does_not_belong_in_the_backup(
        self, session, settings, stick, collection
    ):
        """It says something about this device, not about the collection."""
        collection(1)

        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        assert not (stick / backup.BACKUP_DIR_NAME / backup.STATE_FILE).exists()
        assert (settings.data_dir / backup.STATE_FILE).is_file()


class TestRestoring:
    def _make_backup(self, session, settings, stick, collection, count=2):
        shas = collection(count)
        backup.run_backup(session, settings, _drive(settings), _report_nothing)
        return shas

    def test_an_incomplete_backup_is_refused(self, settings, stick):
        (stick / backup.BACKUP_DIR_NAME).mkdir()

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore(settings, _drive(settings), _report_nothing)

        assert "nicht komplett" in str(fehler.value)

    def test_the_collection_is_replaced(self, session, settings, stick, collection):
        shas = self._make_backup(session, settings, stick, collection)
        # Meanwhile something else has happened on the device.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        backup.run_restore(settings, _drive(settings), _report_nothing)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()

    def test_the_previous_state_is_set_aside_not_deleted(
        self, session, settings, stick, collection
    ):
        """Whoever plays in the wrong backup should not have lost everything."""
        self._make_backup(session, settings, stick, collection)
        later = "e" * 64
        pfad = original_path(settings.photos_dir, later, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"nach der sicherung entstanden")

        backup.run_restore(settings, _drive(settings), _report_nothing)

        assert not pfad.exists(), "in der Sicherung war es nicht"
        beiseite = list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*"))
        assert len(beiseite) == 1
        assert (beiseite[0] / "photos" / later[0:2] / later[2:4] / f"{later}.jpg").is_file()

    def test_the_write_ahead_log_is_set_aside_too(self, session, settings, stick, collection):
        """A -wal left lying belongs to a different database.

        If it stayed beside the restored file, SQLite would try to apply it.
        """
        self._make_backup(session, settings, stick, collection, count=1)
        (settings.data_dir / "kiekmap.db-wal").write_bytes(b"altes journal")

        backup.run_restore(settings, _drive(settings), _report_nothing)

        assert not (settings.data_dir / "kiekmap.db-wal").exists()
        beiseite = next(iter(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*")))
        assert (beiseite / "kiekmap.db-wal").is_file()

    def test_the_working_folder_is_not_left_behind(self, session, settings, stick, collection):
        self._make_backup(session, settings, stick, collection, count=1)

        backup.run_restore(settings, _drive(settings), _report_nothing)

        assert not (settings.data_dir / backup.RESTORE_WORK_DIR).exists()


class TestSchemaRevisionOnRestore:
    """The error that ran unnoticed for two days on 12 August 2026.

    A backup brings its schema with it. Restoring replaces the file as a whole, and the running
    program merely reattaches to it -- migrations do not run then, because they run at *start*. If
    the schema afterwards lacks a column today's program wants to write, the exhibition looks
    entirely normal, and **every visitor contribution ends in a 500**.
    """

    def _backup_at_schema_revision(
        self, session, settings, stick, collection, revision: str, drop_column: bool = False
    ):
        """A backup whose database stands at a particular revision.

        ``drop_column`` turns it into a backup from **before** the migration, and without that the
        reconstruction would be a contradiction: the test database is built from the models and has
        carried ``old_source`` all along. Turning back only the stamp would yield a state that never
        existed -- and the migration would fail on a column that is already there.
        """
        collection(1)
        backup.run_backup(session, settings, _drive(settings), _report_nothing)

        gesichert = stick / backup.BACKUP_DIR_NAME / "kiekmap.db"
        connection = sqlite3.connect(gesichert)
        if drop_column:
            connection.execute("alter table changes drop column old_source")
        connection.execute("create table if not exists alembic_version (version_num varchar(32))")
        connection.execute("delete from alembic_version")
        connection.execute("insert into alembic_version values (?)", (revision,))
        connection.commit()
        connection.close()

    def test_an_old_backup_is_upgraded(self, session, settings, stick, collection):
        """The actual case: what is played in is a state from before the migration."""
        self._backup_at_schema_revision(
            session, settings, stick, collection, INITIAL_SCHEMA, drop_column=True
        )

        backup.run_restore(settings, _drive(settings), _report_nothing)

        assert schema.revision_of(settings.db_path) == schema.head_revision()
        # And really so: the column it failed on back then is there.
        connection = sqlite3.connect(settings.db_path)
        columns = {row[1] for row in connection.execute("pragma table_info(changes)")}
        connection.close()
        assert "old_source" in columns

    def test_a_newer_backup_is_refused(self, session, settings, stick, collection):
        """The reverse case, and it is the more awkward one.

        A schema revision this program does not know cannot be upgraded -- the migrations for it do
        not exist here at all. So do not touch it in the first place.
        """
        self._backup_at_schema_revision(session, settings, stick, collection, "aus der zukunft")

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore(settings, _drive(settings), _report_nothing)

        assert "neueren Programmversion" in str(fehler.value)

    def test_on_refusal_the_device_stays_untouched(self, session, settings, stick, collection):
        """The promise the order in the code hangs on.

        The refusal happens **before** anything is swapped -- otherwise the museum would stand
        there with a half-replaced collection, and that because of a backup that was not readable
        at all.
        """
        self._backup_at_schema_revision(session, settings, stick, collection, "aus der zukunft")
        later = "f" * 64
        pfad = original_path(settings.photos_dir, later, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"nach der sicherung entstanden")

        with pytest.raises(backup.BackupError):
            backup.run_restore(settings, _drive(settings), _report_nothing)

        assert pfad.is_file(), "der Bestand haette nicht angefasst werden duerfen"
        assert list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*")) == []
        assert not (settings.data_dir / backup.RESTORE_WORK_DIR).exists()


class TestTheReminder:
    def test_without_a_backup_it_is_overdue(self, settings):
        """Never backed up is exactly the case the reminder is for."""
        zustand = backup.read_state(settings)

        assert zustand.last_backup_at is None
        assert zustand.overdue is True

    def test_a_fresh_backup_is_not_overdue(self, settings):
        backup.record_backup(settings, "SANDISK")

        zustand = backup.read_state(settings)

        assert zustand.days_since == 0
        assert zustand.overdue is False
        assert zustand.last_drive == "SANDISK"

    def test_an_old_backup_is_overdue(self, settings):
        # UTC, because `_stamp()` writes it that way and `read_state` reads it that way. With local
        # time this test was red for two hours a day: from 22:00 CEST the converted stamp slips to
        # the next calendar day, and the difference came out one day smaller.
        previous = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=backup.OVERDUE_DAYS + 4)
        (settings.data_dir / backup.STATE_FILE).write_text(
            f'{{"last_backup_at": "{previous.isoformat()}", "last_drive": "X"}}', encoding="utf-8"
        )

        zustand = backup.read_state(settings)

        assert zustand.days_since == backup.OVERDUE_DAYS + 4
        assert zustand.overdue is True

    def test_a_broken_state_file_counts_as_never_backed_up(self, settings):
        (settings.data_dir / backup.STATE_FILE).write_text("kein json", encoding="utf-8")

        assert backup.read_state(settings).last_backup_at is None


class TestTheJob:
    def test_a_second_job_is_rejected(self):
        auftrag = backup.Job()
        running = __import__("threading").Event()

        auftrag.start("backup", lambda report: (running.wait(2), "fertig")[1])
        try:
            assert auftrag.start("restore", lambda report: "geht nicht") is False
        finally:
            running.set()

    def test_an_error_ends_up_in_the_status(self):
        auftrag = backup.Job()

        def fails(report):
            raise backup.BackupError("Der Stick ist weg.")

        auftrag.start("backup", fails)
        _warten(auftrag)

        assert auftrag.status().phase == "error"
        assert auftrag.status().error == "Der Stick ist weg."

    def test_an_unexpected_error_does_not_stay_silent(self):
        """Otherwise the progress bar would stand still and nobody would know why."""
        auftrag = backup.Job()

        def bursts(report):
            raise RuntimeError("kaputt")

        auftrag.start("backup", bursts)
        _warten(auftrag)

        assert auftrag.status().phase == "error"
        assert "schiefgegangen" in auftrag.status().error

    def test_acknowledging_resets(self):
        auftrag = backup.Job()
        auftrag.start("backup", lambda report: "fertig")
        _warten(auftrag)

        auftrag.reset()

        assert auftrag.status().phase == "idle"


def _warten(auftrag: backup.Job, sekunden: float = 3.0) -> None:
    """The job runs in a thread -- wait briefly until it is through."""
    import time

    ende = time.monotonic() + sekunden
    while auftrag.running and time.monotonic() < ende:
        time.sleep(0.01)


class TestThroughTheApi:
    """The path the interface takes: query the drives, start, poll the status."""

    def _bis_fertig(self, client, sekunden: float = 5.0) -> dict:
        import time

        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            zustand = client.get("/api/admin/backup/status").json()
            if zustand["phase"] != "running":
                return zustand
            time.sleep(0.02)
        raise AssertionError("Der Auftrag wurde nicht fertig")

    def test_no_drives_without_signing_in(self, client):
        assert client.get("/api/admin/backup/drives").status_code == 401

    def test_without_a_stick_the_list_stays_empty(self, admin_client, settings, tmp_path: Path):
        settings.media_dir = tmp_path / "media"

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["drives"] == []
        # Answerable all the same: how much would have to be backed up, and when it last was.
        assert daten["reminder"]["overdue"] is True

    def test_the_list_names_the_space_and_what_is_needed(
        self, admin_client, settings, stick, collection
    ):
        collection(2)

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["photos"] == 2
        assert daten["needed_bytes"] > 0
        assert daten["drives"][0]["name"] == "SANDISK"
        assert daten["drives"][0]["enough_space"] is True

    def test_the_backup_runs_through(self, admin_client, settings, stick, collection):
        collection(2)

        gestartet = admin_client.post("/api/admin/backup/start", json={"path": str(stick)}).json()
        assert gestartet["kind"] == "backup"

        zustand = self._bis_fertig(admin_client)
        assert zustand["phase"] == "done"
        assert "2 Fotos" in zustand["message"]
        assert (stick / backup.BACKUP_DIR_NAME / "kiekmap.db").is_file()

    def test_the_reminder_then_stands_in_the_overview(
        self, admin_client, settings, stick, collection
    ):
        collection(1)
        admin_client.post("/api/admin/backup/start", json={"path": str(stick)})
        self._bis_fertig(admin_client)

        overview = admin_client.get("/api/admin/overview").json()

        assert overview["backup"]["overdue"] is False
        assert overview["backup"]["last_drive"] == "SANDISK"

    def test_an_unknown_stick_is_rejected(self, admin_client, settings, stick):
        response = admin_client.post("/api/admin/backup/start", json={"path": "/"})

        assert response.status_code == 404
        assert "nicht mehr da" in response.json()["detail"]

    def test_acknowledging_clears_the_status(self, admin_client, settings, stick, collection):
        collection(1)
        admin_client.post("/api/admin/backup/start", json={"path": str(stick)})
        self._bis_fertig(admin_client)

        zustand = admin_client.post("/api/admin/backup/acknowledge").json()

        assert zustand["phase"] == "idle"

    def test_restoring_without_a_backup_says_so(self, admin_client, settings, stick):
        (stick / backup.BACKUP_DIR_NAME).mkdir()

        admin_client.post("/api/admin/backup/restore", json={"path": str(stick)})
        zustand = self._bis_fertig(admin_client)

        assert zustand["phase"] == "error"
        assert "nicht komplett" in zustand["error"]


class TestTheArchive:
    """The backup as a single file -- the second way out of the collection.

    The one promise everything else rests on: **the archive is the folder the stick gets too, only
    zipped.** On that hangs the fact that a ZIP backup can be restored even without an upload path
    -- unpack it onto a stick and you are done. If that property breaks, the way back is gone
    without anyone noticing.
    """

    def _archiv(self, session, settings) -> bytes:
        return b"".join(backup.stream_archive(session, settings))

    def test_an_unpacked_archive_can_be_restored(self, session, settings, stick, collection):
        """The most important test of the archive: it ties the two paths together."""
        shas = collection(3)
        daten = self._archiv(session, settings)

        # Unpack onto the stick -- exactly what somebody would do by hand.
        with zipfile.ZipFile(io.BytesIO(daten)) as archiv:
            archiv.extractall(stick)

        # And after that the entirely ordinary way back.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()
        backup.run_restore(settings, _drive(settings), _report_nothing)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file(), (
                "das entpackte Archiv war fuer die Wiederherstellung nicht brauchbar"
            )

    def test_the_archive_holds_the_same_folder_as_the_stick(self, session, settings, collection):
        collection(2)

        with zipfile.ZipFile(io.BytesIO(self._archiv(session, settings))) as archiv:
            namen = archiv.namelist()

        assert {name.split("/")[0] for name in namen} == {backup.BACKUP_DIR_NAME}
        assert f"{backup.BACKUP_DIR_NAME}/kiekmap.db" in namen
        assert f"{backup.BACKUP_DIR_NAME}/{backup.MANIFEST_NAME}" in namen
        assert any(name.startswith(f"{backup.BACKUP_DIR_NAME}/photos/") for name in namen)
        assert any(name.startswith(f"{backup.BACKUP_DIR_NAME}/thumbs/") for name in namen)

    def test_the_archive_is_not_compressed(self, session, settings, collection):
        """JPEG and WebP are already compressed -- a second pass only costs the Pi time."""
        collection(2)

        with zipfile.ZipFile(io.BytesIO(self._archiv(session, settings))) as archiv:
            verfahren = {entry.compress_type for entry in archiv.infolist()}

        assert verfahren == {zipfile.ZIP_STORED}

    def test_the_archive_is_built_as_a_stream(self, session, settings, collection):
        """Otherwise it would sit entirely in memory -- on a Pi with 2 GB not a good idea."""
        collection(5)

        pieces = list(backup.stream_archive(session, settings))

        assert len(pieces) > 1, "der Erzeuger hat alles auf einmal geliefert"

    def test_an_aborted_download_does_not_count_as_a_backup(self, session, settings, collection):
        """What the browser did not receive protects nobody -- so it does not count either."""
        collection(3)
        strom = backup.stream_archive(session, settings)
        next(strom)  # started, but not read to the end
        strom.close()

        assert backup.read_state(settings).last_backup_at is None

    def test_a_complete_download_resets_the_reminder(self, session, settings, collection):
        collection(2)

        self._archiv(session, settings)

        zustand = backup.read_state(settings)
        assert zustand.last_backup_at is not None
        assert zustand.last_drive == backup.ZIP_DRIVE_NAME

    def test_the_file_name_names_the_place_and_the_day(self, settings):
        settings.region_file.parent.mkdir(parents=True, exist_ok=True)
        settings.region_file.write_text('{"name": "Holm"}', encoding="utf-8")

        name = backup.archive_name(settings)

        assert name.startswith("kiekmap-sicherung-holm-")
        assert name.endswith(".zip")
        assert name.isascii(), "der Name steht in einem HTTP-Kopf"


class TestTheArchiveThroughTheApi:
    def test_no_download_without_a_ticket(self, admin_client):
        assert admin_client.get("/api/admin/backup/zip").status_code == 422

    def test_an_invented_ticket_is_rejected(self, admin_client):
        response = admin_client.get("/api/admin/backup/zip", params={"ticket": "ausgedacht"})

        assert response.status_code == 401

    def test_a_ticket_is_valid_only_once(self, admin_client, settings, collection):
        collection(1)
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]

        erste = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})
        zweite = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})

        assert erste.status_code == 200
        assert zweite.status_code == 401, "ein Ticket darf sich nicht wiederverwenden lassen"

    def test_a_ticket_only_for_signed_in_users(self, client):
        assert client.post("/api/admin/backup/zip/ticket").status_code == 401

    def test_the_download_delivers_an_archive(self, admin_client, settings, collection):
        collection(2)
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]

        response = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})

        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        with zipfile.ZipFile(io.BytesIO(response.content)) as archiv:
            assert archiv.testzip() is None

    def test_a_running_job_blocks_the_download(self, admin_client, settings):
        """A restore would swap the files out from under the running stream."""
        import threading

        breakpoint = threading.Event()
        backup.job.start("backup", lambda report: (breakpoint.wait(2), "fertig")[1])
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]
        try:
            response = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})
        finally:
            breakpoint.set()

        assert response.status_code == 409


class TestABackupFromTheInbox:
    """The way back: put a downloaded file into the inbox.

    **It never plays itself in.** The folder otherwise takes in photos -- adding, without
    consequence -- while this replaces the whole collection. It is recognised here and confirmed in
    the admin view.
    """

    def _ablegen(self, session, settings, name: str = "kiekmap-sicherung-holm-2026-08-03.zip"):
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        target = settings.incoming_dir / name
        with target.open("wb") as file_name:
            for teil in backup.stream_archive(session, settings):
                file_name.write(teil)
        return target

    def test_a_downloaded_archive_comes_back_through_the_inbox(self, session, settings, collection):
        """The most important test: it closes the circle that until now only the detour over the
        stick closed."""
        shas = collection(3)
        self._ablegen(session, settings)

        # Meanwhile something else has happened on the device.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        gefunden = backup.waiting_archive(settings)
        assert gefunden is not None, "die abgelegte Sicherung wurde nicht erkannt"
        backup.run_restore_from_archive(settings, gefunden[0], _report_nothing)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()
            for size in THUMBNAIL_SIZES:
                assert thumbnail_path(settings.thumbs_dir, sha, size).is_file()

    def test_a_waiting_backup_is_reported_with_its_date_and_count(
        self, session, settings, collection
    ):
        """Without both, the question in the admin view could not be answered."""
        collection(2)
        self._ablegen(session, settings)

        gefunden = backup.waiting_archive(settings)

        assert gefunden is not None
        _, info = gefunden
        assert info.photos == 2
        assert info.created_at is not None

    def test_a_half_copied_file_is_not_offered(self, session, settings, collection):
        """A truncated ZIP has no central directory -- it fails of its own accord."""
        collection(2)
        pfad = self._ablegen(session, settings)
        daten = pfad.read_bytes()
        pfad.write_bytes(daten[: len(daten) // 2])

        assert backup.waiting_archive(settings) is None

    def test_a_foreign_zip_is_ignored(self, settings):
        """A matching name, no manifest -- the name only decides whether to look inside."""
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        fremd = settings.incoming_dir / "kiekmap-sicherung-fremd.zip"
        with zipfile.ZipFile(fremd, "w") as archiv:
            archiv.writestr("irgendwas.txt", "kein Bestand")

        assert backup.waiting_archive(settings) is None

    def test_a_zip_in_the_inbox_does_not_land_in_the_problem_folder(
        self, session, settings, collection
    ):
        """Without this promise none of it does anything: the watcher would file it away."""
        from app.services.watcher import IncomingWatcher

        collection(1)
        pfad = self._ablegen(session, settings)
        watcher = IncomingWatcher(settings)

        watcher.scan_once()
        watcher.scan_once()

        assert pfad.is_file(), "der Watcher hat die Sicherung angefasst"
        assert not (settings.incoming_dir / "_problem").exists()

    def test_a_photo_beside_it_is_still_taken_in(self, session, settings, collection, sample_image):
        """The exception applies only to backups, not to the whole folder."""
        import shutil as _shutil

        from app.services.watcher import IncomingWatcher

        collection(1)
        self._ablegen(session, settings)
        _shutil.copy2(sample_image("scan_ohne_exif.jpg"), settings.incoming_dir / "neu.jpg")

        watcher = IncomingWatcher(settings)
        watcher.scan_once()
        aufgenommen = watcher.scan_once()

        assert aufgenommen == 1

    def test_the_previous_state_is_set_aside(self, session, settings, collection):
        collection(2)
        pfad = self._ablegen(session, settings)
        before = {p.name for p in settings.photos_dir.rglob("*") if p.is_file()}

        backup.run_restore_from_archive(settings, pfad, _report_nothing)

        beiseite = list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*"))
        assert len(beiseite) == 1, "der bisherige Stand wurde nicht beiseitegelegt"
        assert before <= {p.name for p in beiseite[0].rglob("*") if p.is_file()}

    def test_the_archive_moves_to_the_done_folder(self, session, settings, collection):
        collection(1)
        pfad = self._ablegen(session, settings)

        backup.run_restore_from_archive(settings, pfad, _report_nothing)

        assert not pfad.exists(), "die Datei liegt noch im Eingang"
        assert (settings.incoming_dir / "_erledigt" / pfad.name).is_file()
        assert backup.waiting_archive(settings) is None

    def test_an_incomplete_file_is_refused(self, settings):
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        keine = settings.incoming_dir / "kiekmap-sicherung-kaputt.zip"
        keine.write_bytes(b"kein zip")

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore_from_archive(settings, keine, _report_nothing)

        assert "keine vollstaendige Sicherung" in str(fehler.value)


class TestEingangUeberDieApi:
    def _bis_fertig(self, client, sekunden: float = 5.0) -> dict:
        import time

        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            zustand = client.get("/api/admin/backup/status").json()
            if zustand["phase"] != "running":
                return zustand
            time.sleep(0.02)
        raise AssertionError("Der Auftrag wurde nicht fertig")

    def _ablegen(self, session, settings) -> str:
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        name = "kiekmap-sicherung-holm-2026-08-03.zip"
        with (settings.incoming_dir / name).open("wb") as file_name:
            for teil in backup.stream_archive(session, settings):
                file_name.write(teil)
        return name

    def test_the_drive_list_reports_the_waiting_backup(
        self, admin_client, session, settings, collection
    ):
        collection(2)
        name = self._ablegen(session, settings)

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["incoming"] is not None
        assert daten["incoming"]["file"] == name
        assert daten["incoming"]["photos"] == 2

    def test_without_a_file_the_list_reports_nothing(self, admin_client, settings):
        assert admin_client.get("/api/admin/backup/drives").json()["incoming"] is None

    def test_restoring_through_the_api(self, admin_client, session, settings, collection):
        shas = collection(2)
        name = self._ablegen(session, settings)
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        response = admin_client.post("/api/admin/backup/incoming/restore", json={"file": name})
        assert response.status_code == 200
        zustand = self._bis_fertig(admin_client)

        assert zustand["phase"] == "done", zustand
        assert "_erledigt" in zustand["message"]
        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()

    def test_an_invented_file_name_is_rejected(self, admin_client, settings):
        response = admin_client.post(
            "/api/admin/backup/incoming/restore", json={"file": "gibt-es-nicht.zip"}
        )

        assert response.status_code == 404

    def test_a_path_out_of_the_folder_is_rejected(self, admin_client, settings):
        """The name comes from the browser -- without the check every file could be played in."""
        response = admin_client.post(
            "/api/admin/backup/incoming/restore", json={"file": "../kiekmap.db"}
        )

        assert response.status_code == 404
