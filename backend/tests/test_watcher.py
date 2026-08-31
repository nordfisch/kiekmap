from pathlib import Path

import pytest
from sqlalchemy import select

from app.models import Photo
from app.services.watcher import IncomingWatcher


def test_waits_until_the_file_is_written_completely(
    session, settings, sample_image, fixtures_dir: Path
):
    """The case that trips up an event-driven watch.

    A large TIFF copied over the network exists long before it is complete. Whoever reaches for it
    at the first sign of life imports half an image.
    """
    watcher = IncomingWatcher(settings, interval=0)
    complete = (fixtures_dir / "scan_ohne_exif.jpg").read_bytes()
    target = settings.incoming_dir / "wird_gerade_kopiert.jpg"

    # First half of it -- the copy is still running.
    target.write_bytes(complete[: len(complete) // 2])
    assert watcher.scan_once() == 0, "an unfinished file must not be touched"

    # Next look: the size has changed, so keep waiting.
    target.write_bytes(complete)
    assert watcher.scan_once() == 0

    # Now the size is stable.
    assert watcher.scan_once() == 1
    assert session.scalar(select(Photo).where(Photo.original_filename == target.name))


def test_an_empty_file_is_never_imported(session, settings):
    watcher = IncomingWatcher(settings, interval=0)
    (settings.incoming_dir / "leer.jpg").touch()

    assert watcher.scan_once() == 0
    assert watcher.scan_once() == 0


def test_an_empty_folder_is_not_an_error(session, settings):
    assert IncomingWatcher(settings, interval=0).scan_once() == 0


def test_the_import_runs_through_without_anyone_helping(session, settings, fixtures_dir: Path):
    watcher = IncomingWatcher(settings, interval=0)
    for name in ("scan_ohne_exif.jpg", "hochkant.jpg"):
        (settings.incoming_dir / name).write_bytes((fixtures_dir / name).read_bytes())

    watcher.scan_once()  # remember the sizes
    assert watcher.scan_once() == 2
    assert len(session.scalars(select(Photo)).all()) == 2


class TestAnAbortInTheMiddle:
    """What has already been read has to stay -- error 57.

    ``import_file`` moves each file into ``_erledigt/`` itself, before anything is committed. When
    the whole run was only committed at the end, an exception in the middle took the rows of every
    photo read before it along -- and the import log with them, because its entries hung in the
    same transaction. The source files then lay in ``_erledigt/``, and nothing said they had ever
    existed.

    ``_loop`` catches the exception and carries on at the next look, so the service runs on
    undisturbed. That is exactly why the loss occurs to nobody.
    """

    def _place_in_inbox(self, settings, fixtures_dir: Path, name: str, source: str):
        target = settings.incoming_dir / name
        target.write_bytes((fixtures_dir / source).read_bytes())

    def test_an_error_on_the_second_photo_does_not_lose_the_first(
        self, session, settings, fixtures_dir: Path, monkeypatch
    ):
        from app.models import ImportLog
        from app.services import watcher as watcher_module

        self._place_in_inbox(settings, fixtures_dir, "1_erstes.jpg", "scan_ohne_exif.jpg")
        self._place_in_inbox(settings, fixtures_dir, "2_zweites.jpg", "hochkant.jpg")

        real_import = watcher_module.import_file

        def stumbles(session_, path, *args, **kwargs):
            if path.name.startswith("2_"):
                raise RuntimeError("something unforeseen")
            return real_import(session_, path, *args, **kwargs)

        monkeypatch.setattr(watcher_module, "import_file", stumbles)

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()  # remember the sizes
        with pytest.raises(RuntimeError):
            watcher.scan_once()

        # A fresh session, because that is precisely the question: is it in the database, or only
        # in the memory of the one that was aborted?
        import app.db

        with app.db.SessionLocal() as fresh:
            photo = fresh.scalar(select(Photo).where(Photo.original_filename == "1_erstes.jpg"))
            assert photo is not None, "the abort must not take the first photo with it"
            entries = fresh.scalars(select(ImportLog)).all()
            assert [entry.path for entry in entries] != [], "the log is missing entirely"
            assert any("1_erstes.jpg" in entry.path for entry in entries)

        # And the source file lies filed away -- that is the state the row belongs to.
        assert (settings.incoming_dir / "_erledigt" / "1_erstes.jpg").is_file()

    def test_the_next_look_picks_up_what_was_left_behind(
        self, session, settings, fixtures_dir: Path, monkeypatch
    ):
        """The second half of the promise: the watcher does not give up.

        The file it failed on is still in the inbox and its size is still remembered -- on the next
        pass its turn comes round again.
        """
        from app.services import watcher as watcher_module

        self._place_in_inbox(settings, fixtures_dir, "1_erstes.jpg", "scan_ohne_exif.jpg")
        self._place_in_inbox(settings, fixtures_dir, "2_zweites.jpg", "hochkant.jpg")

        real_import = watcher_module.import_file
        stumbled = []

        def stumbles_once(session_, path, *args, **kwargs):
            if path.name.startswith("2_") and not stumbled:
                stumbled.append(path)
                raise RuntimeError("something unforeseen")
            return real_import(session_, path, *args, **kwargs)

        monkeypatch.setattr(watcher_module, "import_file", stumbles_once)

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        with pytest.raises(RuntimeError):
            watcher.scan_once()

        assert watcher.scan_once() == 1, "the second photo comes in at the next look"
        assert len(session.scalars(select(Photo)).all()) == 2


class TestFolderNames:
    """The inbox is the museum team's usual path -- and it did not read the folders.

    929 photos came in that way: street and house number stood in the path and nowhere in the
    database afterwards. No place, no title, no provenance, no tags. It was noticed only on the
    finished map, because the metadata layer ran cleanly and the collection therefore did not
    *look* broken -- only empty.

    The cause was not the forgotten line but that it could be forgotten: the path layer hung on
    the caller. It now hangs on the ``root`` parameter of ``import_file``.
    """

    def _street(self, session, name="Hauptstrasse", lat=53.62, lon=9.676):
        from app.models import Place
        from app.services.places import normalize

        session.add(
            Place(
                name=name,
                name_normalized=normalize(name),
                lat=lat,
                lon=lon,
                kind="strasse",
            )
        )
        session.commit()

    def _place_in_inbox(
        self, settings, fixtures_dir: Path, subpath: str, source="scan_ohne_exif.jpg"
    ):
        target = settings.incoming_dir / subpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((fixtures_dir / source).read_bytes())
        return target

    def test_the_inbox_reads_the_folder_names(
        self, session, settings, fixtures_dir: Path, monkeypatch
    ):
        """The test that was missing."""
        monkeypatch.setattr(settings, "import_provenance", "Archiv/")
        self._street(session)
        self._place_in_inbox(settings, fixtures_dir, "Hauptstrasse/14 Museum/023.jpg")

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        assert watcher.scan_once() == 1

        photo = session.scalars(select(Photo)).one()
        assert photo.place_name == "Hauptstrasse 14"
        assert (photo.lat, photo.lon) == (53.62, 9.676)
        assert photo.title == "Museum"
        assert photo.provenance == "Archiv/Hauptstrasse/14 Museum/023.jpg"
        assert {"Hauptstrasse", "Museum"} <= {tag.name for tag in photo.tags}

    def test_the_log_reports_no_missing_place_that_it_fills_in_at_once(
        self, session, settings, fixtures_dir: Path
    ):
        """Otherwise the import log would say "es fehlt noch: Ort" for a located photo.

        The message is built after the path layer, not before it -- a volunteer going through the
        log should not be hunting for gaps that are none.
        """
        from app.models import ImportLog

        self._street(session)
        self._place_in_inbox(settings, fixtures_dir, "Hauptstrasse/14 Museum/023.jpg")

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        watcher.scan_once()

        entry = session.scalars(select(ImportLog)).one()
        assert "Ort" not in entry.message
        assert "Jahr" in entry.message

    def test_filed_away_files_keep_their_folder(self, session, settings, fixtures_dir: Path):
        """Filed away flat, a sorted stack becomes a one-off attempt.

        The folder names are the statement about these photos. If they all end up side by side in
        _erledigt/, a second run has nothing left to read -- and files of the same name from
        different houses pile up into "023 (2).jpg".
        """
        self._street(session)
        self._place_in_inbox(settings, fixtures_dir, "Hauptstrasse/14 Museum/023.jpg")
        self._place_in_inbox(
            settings, fixtures_dir, "Hauptstrasse/16 Anders/023.jpg", "hochkant.jpg"
        )

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        assert watcher.scan_once() == 2

        done = settings.incoming_dir / "_erledigt"
        assert (done / "Hauptstrasse" / "14 Museum" / "023.jpg").is_file()
        assert (done / "Hauptstrasse" / "16 Anders" / "023.jpg").is_file()
        assert not (done / "023 (2).jpg").exists()
