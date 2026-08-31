"""Tests of the import from a USB stick.

The one promise that separates this function from the folder watch: **the stick belongs to
somebody else.** In the watched inbox, files taken in are filed away -- on somebody else's volume
only reading happens. Whoever gets their stick back with files missing never trusts the device
again.

The second point is the path: it comes back from the browser and is input, not fact. Without a
check the admin view would be a way to read in every folder of the device.
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
    """A folder that passes for a USB stick."""
    media = tmp_path / "media"
    drive = media / "SCANSTICK"
    drive.mkdir(parents=True)

    settings.media_dir = media
    monkeypatch.setattr(backup.drives, "_is_mounted", lambda path: path == drive)
    return drive


@pytest.fixture
def images_on_the_stick(stick: Path, fixtures_dir: Path):
    """Puts images into a folder on the stick and returns it."""

    def create(subfolder: str = "Scans2024", names=("scan_ohne_exif.jpg", "hochkant.jpg")):
        folder = stick / subfolder
        folder.mkdir(parents=True, exist_ok=True)
        for name in names:
            shutil.copy2(fixtures_dir / name, folder / name)
        return folder

    return create


class TestFindingFolders:
    def test_folders_with_images_are_offered(self, settings, stick, images_on_the_stick):
        images_on_the_stick("Scans2024")

        found = importer.find_image_folders(stick)

        # The drive itself is in front: it takes everything at once.
        assert [folder.name for folder in found] == ["SCANSTICK", "Scans2024"]
        assert [folder.images for folder in found] == [2, 2]

    def test_the_drive_counts_the_subfolders_too(self, settings, stick, images_on_the_stick):
        """Otherwise the entry for the whole stick would read zero while it carries 900 photos.

        An archive filed by street has not a single file lying at the top. The number has to say
        what an import would take in -- not what happens to lie directly in the folder.
        """
        images_on_the_stick("Strassen/Hauptstrasse", ("scan_ohne_exif.jpg",))
        images_on_the_stick("Strassen/Niederstrasse", ("hochkant.jpg",))

        found = {folder.name: folder.images for folder in importer.find_image_folders(stick)}

        assert found["SCANSTICK"] == 2
        assert "Strassen" not in found  # nothing lies there immediately

    def test_folders_without_images_are_not_offered(self, settings, stick):
        (stick / "Rechnungen").mkdir()
        (stick / "Rechnungen" / "brief.txt").write_text("nothing", encoding="utf-8")

        assert importer.find_image_folders(stick) == []

    def test_the_device_s_own_backup_is_skipped(self, settings, stick, images_on_the_stick):
        """Otherwise the device would read its own backup in again as a batch of new photos."""
        images_on_the_stick(f"{backup.BACKUP_DIR_NAME}/photos")

        assert importer.find_image_folders(stick) == []

    def test_hidden_folders_stay_out(self, settings, stick, images_on_the_stick):
        images_on_the_stick(".Trashes")

        assert importer.find_image_folders(stick) == []


class TestTakingImagesIn:
    def test_files_on_the_stick_stay_where_they_are(
        self, session, settings, stick, images_on_the_stick
    ):
        """The most important promise of this function.

        The watched inbox moves what it has taken in to _erledigt/ -- there that is right, it is
        our folder. On somebody else's stick it would be an intrusion.
        """
        folder = images_on_the_stick()
        before = sorted(path.name for path in folder.iterdir())

        importer.import_from_folder(session, folder, settings)

        assert sorted(path.name for path in folder.iterdir()) == before
        assert not (folder / importer.DONE_DIR).exists()

    def test_photos_end_up_in_the_collection(self, session, settings, stick, images_on_the_stick):
        folder = images_on_the_stick()

        message, rows = importer.import_from_folder(session, folder, settings)

        assert len(session.scalars(select(Photo)).all()) == 2
        assert [row.source.name for row in rows] == sorted(path.name for path in folder.iterdir())
        assert "2 Fotos aufgenommen" in message
        assert "abgezogen werden" in message

    def test_a_stick_reads_subfolders_too(self, session, settings, stick, images_on_the_stick):
        """A stick has to behave like the inbox, which already reads recursively.

        Otherwise it would depend on the way into the house whether the folder names of an archive
        are evaluated -- and a stick filed by street would take in no photos at all.
        """
        images_on_the_stick("Archiv/Hauptstrasse", ("scan_ohne_exif.jpg",))
        images_on_the_stick("Archiv/Hauptstrasse/14 Museum", ("hochkant.jpg",))

        message, rows = importer.import_from_folder(session, stick / "Archiv", settings)

        assert len(session.scalars(select(Photo)).all()) == 2
        assert "2 Fotos aufgenommen" in message

    def test_duplicates_are_counted_not_kept_quiet(
        self, session, settings, stick, images_on_the_stick
    ):
        folder = images_on_the_stick()
        importer.import_from_folder(session, folder, settings)

        message, _ = importer.import_from_folder(session, folder, settings)

        assert "0 Fotos aufgenommen" in message
        assert "2 waren schon da" in message

    def test_the_year_applies_to_the_whole_folder(
        self, session, settings, stick, images_on_the_stick
    ):
        from app.models import DatePrecision

        folder = images_on_the_stick()

        importer.import_from_folder(
            session,
            folder,
            settings,
            defaults=lambda photo: importer.apply_batch_defaults(
                session, photo, 1932, DatePrecision.YEAR, None, None, "Kirche"
            ),
        )

        photos = session.scalars(select(Photo)).all()
        assert all(photo.date_from.year == 1932 for photo in photos)
        assert all(photo.place_name == "Kirche" for photo in photos)

    def test_the_batch_tag_stands_beside_the_one_from_the_file(
        self, session, settings, stick, images_on_the_stick, monkeypatch
    ):
        """The trap in this point: tags are one field less than they are a set.

        Every other batch entry fills only *what is empty* -- where the file knows better, the file
        wins. A tag, though, displaces nothing; it is added. Whoever uploads a hundred photos out of
        a folder called "Feuerwehr" wants both: what the file says **and** "Feuerwehr".
        """
        from app.models import DatePrecision

        monkeypatch.setattr(settings, "import_tags", ["Gebäude"])
        folder = images_on_the_stick()

        importer.import_from_folder(
            session,
            folder,
            settings,
            defaults=lambda photo: importer.apply_batch_defaults(
                session, photo, None, DatePrecision.YEAR, None, None, None, tags="Feuerwehr, Neubau"
            ),
        )

        for photo in session.scalars(select(Photo)).all():
            names = {tag.name for tag in photo.tags}
            assert {"Feuerwehr", "Neubau"} <= names
            assert "Gebäude" in names, "the device setting stays beside it"

    def test_without_a_batch_tag_nothing_changes(
        self, session, settings, stick, images_on_the_stick, monkeypatch
    ):
        """The counter-check -- an empty field must not create an empty tag."""
        from app.models import DatePrecision, Tag

        monkeypatch.setattr(settings, "import_tags", ["Gebäude"])
        folder = images_on_the_stick()

        importer.import_from_folder(
            session,
            folder,
            settings,
            defaults=lambda photo: importer.apply_batch_defaults(
                session, photo, None, DatePrecision.YEAR, None, None, None, tags="  ,  "
            ),
        )

        assert {tag.name for tag in session.scalars(select(Tag)).all()} == {"Gebäude"}

    def test_progress_counts_the_images(self, session, settings, stick, images_on_the_stick):
        folder = images_on_the_stick()
        steps = []

        importer.import_from_folder(
            session,
            folder,
            settings,
            report=lambda done, total, message: steps.append((done, total)),
        )

        assert steps == [(1, 2), (2, 2)]

    def test_an_abort_leaves_what_was_read_so_far(
        self, session, settings, stick, images_on_the_stick
    ):
        """If the stick is pulled mid-run, what was read is read.

        That is why each photo is committed on its own and not only at the end.
        """
        folder = images_on_the_stick()

        def after_the_first(done, total, message):
            if done == 1:
                raise OSError("stick pulled")

        with pytest.raises(OSError):
            importer.import_from_folder(session, folder, settings, report=after_the_first)

        session.expire_all()
        assert len(session.scalars(select(Photo)).all()) == 1


class TestThroughTheApi:
    def test_no_folders_without_signing_in(self, client: TestClient):
        assert client.get("/api/admin/import/folders").status_code == 401

    def test_folders_are_named_with_their_drive(
        self, admin_client: TestClient, stick, images_on_the_stick
    ):
        images_on_the_stick()

        data = admin_client.get("/api/admin/import/folders").json()

        assert data["folders"][1]["drive"] == "SCANSTICK"
        assert data["folders"][1]["name"] == "Scans2024"
        assert data["folders"][1]["images"] == 2

    def test_a_stick_without_images_still_names_the_drive(self, admin_client: TestClient, stick):
        """Otherwise an empty list would mean two things: no stick, or a stick without images.

        The screen would answer somebody who has just plugged one in with "Bitte USB-Stick
        einstecken" -- the kind of dead end at which somebody gives up.
        """
        data = admin_client.get("/api/admin/import/folders").json()

        assert data["drives"] == ["SCANSTICK"]
        assert data["folders"] == []

    def test_a_path_outside_the_stick_is_rejected(
        self, admin_client: TestClient, stick, tmp_path: Path
    ):
        """Otherwise the admin view would be a way to read in every folder of the device."""
        elsewhere = tmp_path / "woanders"
        elsewhere.mkdir()

        response = admin_client.post("/api/admin/import/start", json={"path": str(elsewhere)})

        assert response.status_code == 404

    def test_climbing_upwards_does_not_help_either(self, admin_client: TestClient, stick):
        response = admin_client.post("/api/admin/import/start", json={"path": f"{stick}/../../etc"})

        assert response.status_code == 404

    def test_the_import_runs_through(
        self, admin_client: TestClient, session, stick, images_on_the_stick
    ):
        import time

        folder = images_on_the_stick()

        started = admin_client.post(
            "/api/admin/import/start", json={"path": str(folder), "year": 1932}
        ).json()
        assert started["kind"] == "import"

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            state = admin_client.get("/api/admin/backup/status").json()
            if state["phase"] != "running":
                break
            time.sleep(0.02)

        assert state["phase"] == "done"
        assert "2 Fotos aufgenommen" in state["message"]

    def test_no_import_runs_beside_a_backup(
        self, admin_client: TestClient, stick, images_on_the_stick
    ):
        """One job for the device. Two at once would overwrite each other."""
        folder = images_on_the_stick()
        running = __import__("threading").Event()
        backup.job.start("backup", lambda report: (running.wait(2), "fertig")[1])

        try:
            response = admin_client.post("/api/admin/import/start", json={"path": str(folder)})
            assert response.status_code == 409
        finally:
            running.set()


class TestRowsForTheFollowUp:
    """Up to 30 images the job delivers the rows along with it, above that it does not.

    They travel in the status, which is polled every second -- two hundred photos in it would go
    over the wire again with every poll.
    """

    def _until_done(self, client) -> dict:
        import time

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            state = client.get("/api/admin/backup/status").json()
            if state["phase"] != "running":
                return state
            time.sleep(0.02)
        raise AssertionError("the job did not finish")

    def test_a_small_batch_delivers_the_rows(
        self, admin_client: TestClient, stick, images_on_the_stick
    ):
        folder = images_on_the_stick()

        admin_client.post("/api/admin/import/start", json={"path": str(folder)})
        state = self._until_done(admin_client)

        assert state["phase"] == "done"
        assert [row["filename"] for row in state["items"]] == [
            "hochkant.jpg",
            "scan_ohne_exif.jpg",
        ]

    def test_a_large_batch_delivers_no_rows(
        self, admin_client: TestClient, stick, fixtures_dir, monkeypatch
    ):
        import shutil

        from app.api import backup as api

        monkeypatch.setattr(api, "REVIEW_LIMIT", 1)
        folder = stick / "Viele"
        folder.mkdir()
        for name in ("scan_ohne_exif.jpg", "hochkant.jpg"):
            shutil.copy2(fixtures_dir / name, folder / name)

        admin_client.post("/api/admin/import/start", json={"path": str(folder)})
        state = self._until_done(admin_client)

        assert state["phase"] == "done"
        assert state["items"] is None
        # The message stays -- only the table is dropped.
        assert "2 Fotos aufgenommen" in state["message"]
