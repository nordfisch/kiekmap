"""The sample collection: save it, throw it away, fetch it back.

The one promise everything hangs on: **what was saved comes back complete.** A starting state that
looks a little different after every restore is not one -- and the difference is only noticed while
hunting a bug that does not exist.

The second reason for these tests is the form: image files plus JSON instead of a database dump, so
that a new column does not make the collection worthless. The other side of that is that applying
the metadata is handwritten code -- exactly the kind that reaches silently past its target.
"""

from datetime import date

from sqlalchemy import select

from app.models import Change, Photo, PhotoStatus, Source, Tag
from app.services import seed


def _photo_with_everything(session, settings, sample_image, fixtures_dir) -> Photo:
    """A photo with all of it: dating, place, tags, credit, provenance, contribution."""
    from app.services.importer import import_file

    photo = import_file(session, sample_image("scan_ohne_exif.jpg"), settings).photo
    assert photo is not None
    photo.title = "Gasthof Petersen"
    photo.description = "Blick von der Hauptstrasse."
    photo.credit = "Sammlung Heimatmuseum Holm"
    photo.provenance = "Leihgabe H. Timm, Freigabe liegt vor"
    photo.date_from, photo.date_to = date(1920, 1, 1), date(1929, 12, 31)
    photo.date_precision = "decade"
    photo.date_source = Source.CURATOR
    photo.lat, photo.lon = 53.6196, 9.652
    photo.place_name = "Hauptstrasse 14"
    photo.location_source = Source.VISITOR
    photo.location_accuracy_m = 15
    photo.tags = [Tag(name="Gasthof"), Tag(name="ArchivHolm")]
    session.add(
        Change(
            photo_id=photo.id,
            field="location",
            old_value=None,
            new_value="53.6196,9.652 (Hauptstrasse 14)",
            source=Source.VISITOR,
        )
    )
    session.commit()
    return photo


class TestRoundTrip:
    def test_the_starting_state_survives_the_way_out_and_back(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        before = _photo_with_everything(session, settings, sample_image, fixtures_dir)
        expected = {
            field: getattr(before, field) for field in (*seed.FIELDS, "sha256", "original_filename")
        }
        expected_tags = sorted(tag.name for tag in before.tags)

        target = tmp_path / "seed"
        seed.export(session, settings, target)
        session.commit()

        seed.load(session, settings, target)
        session.commit()

        after = session.scalars(select(Photo)).one()
        for field, value in expected.items():
            assert getattr(after, field) == value, f"{field} came back different"
        assert sorted(tag.name for tag in after.tags) == expected_tags

    def test_the_visitor_contribution_comes_along(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        """Otherwise the admin review list would be empty after every ``make seed``."""
        _photo_with_everything(session, settings, sample_image, fixtures_dir)
        target = tmp_path / "seed"

        seed.export(session, settings, target)
        session.commit()
        seed.load(session, settings, target)
        session.commit()

        contribution = session.scalars(select(Change)).one()
        assert contribution.source == Source.VISITOR
        assert contribution.new_value == "53.6196,9.652 (Hauptstrasse 14)"
        assert contribution.photo_id == session.scalars(select(Photo)).one().id

    def test_a_deleted_photo_stays_deleted(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        """Two photos in the bin are part of the state -- otherwise the list is empty."""
        photo = _photo_with_everything(session, settings, sample_image, fixtures_dir)
        photo.status = PhotoStatus.DELETED
        session.commit()
        target = tmp_path / "seed"

        seed.export(session, settings, target)
        session.commit()
        seed.load(session, settings, target)
        session.commit()

        assert session.scalars(select(Photo)).one().status == PhotoStatus.DELETED

    def test_gaps_stay_gaps(self, session, settings, sample_image, tmp_path):
        """A photo without a place and without a year is the case the contribution panel needs.

        On the way back it runs through the real import, and that reads from the file whatever it
        finds. If it entered something there, the photo would vanish from the contribution panel --
        so the gap has to be the stronger statement.
        """
        photo = _photo_with_everything(session, settings, sample_image, None)
        photo.date_from = photo.date_to = None
        photo.date_precision = "unknown"
        photo.date_source = None
        photo.lat = photo.lon = None
        photo.place_name = None
        photo.location_source = None
        session.commit()
        target = tmp_path / "seed"

        seed.export(session, settings, target)
        session.commit()
        seed.load(session, settings, target)
        session.commit()

        after = session.scalars(select(Photo)).one()
        assert after.needs_date, "the missing dating was filled in while reading back"
        assert after.needs_location, "the missing place was filled in while reading back"


class TestAMissingCollection:
    def test_without_a_seed_directory_there_is_a_clear_message(self, session, settings, tmp_path):
        """Not a stack trace but something readable -- the CLI turns it into a sentence."""
        import pytest

        with pytest.raises(FileNotFoundError):
            seed.load(session, settings, tmp_path / "does-not-exist")

    def test_clearing_removes_photos_and_thumbnails(
        self, session, settings, sample_image, fixtures_dir
    ):
        _photo_with_everything(session, settings, sample_image, fixtures_dir)
        assert list(settings.photos_dir.rglob("*.jpg"))

        seed.clear(session, settings)
        session.commit()

        assert session.scalars(select(Photo)).all() == []
        assert session.scalars(select(Change)).all() == []
        assert list(settings.photos_dir.rglob("*.jpg")) == []
        assert list(settings.thumbs_dir.rglob("*.webp")) == []

    def test_exporting_removes_deleted_files(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        """Otherwise seed/ would be a folder that only grows -- not the image of a state."""
        from app.services.importer import import_file

        _photo_with_everything(session, settings, sample_image, fixtures_dir)
        second = import_file(session, sample_image("hochkant.jpg"), settings).photo
        session.commit()
        target = tmp_path / "seed"
        seed.export(session, settings, target)
        assert (target / seed.IMAGE_DIR_NAME / "hochkant.jpg").exists()

        session.delete(second)
        session.commit()
        seed.export(session, settings, target)

        assert not (target / seed.IMAGE_DIR_NAME / "hochkant.jpg").exists()
        assert (target / seed.IMAGE_DIR_NAME / "scan_ohne_exif.jpg").exists()


class TestEmptyingTheCollection:
    """``make empty`` -- the only command with no way back.

    ``seed-load`` throws the collection away too, but puts something in its place. This one leaves
    nothing. The failure case is therefore not "it does not delete" but **"it deletes although
    somebody meant something else"** -- and that is only noticed once 929 photos are gone.
    """

    def test_a_wrong_answer_deletes_nothing(
        self, session, settings, sample_image, fixtures_dir, monkeypatch, capsys
    ):
        from app.cli import main

        _photo_with_everything(session, settings, sample_image, fixtures_dir)
        monkeypatch.setattr("builtins.input", lambda _: "ja")

        assert main(["empty"]) == 1

        assert len(session.scalars(select(Photo)).all()) == 1
        assert list(settings.photos_dir.rglob("*.jpg"))
        assert "Abgebrochen" in capsys.readouterr().out

    def test_the_number_of_photos_is_the_confirmation(
        self, session, settings, sample_image, fixtures_dir, monkeypatch
    ):
        """What has to be typed is the number standing one line above.

        A "y/n" can be answered without having read. A number cannot.
        """
        from app.cli import main

        _photo_with_everything(session, settings, sample_image, fixtures_dir)
        monkeypatch.setattr("builtins.input", lambda _: "1")

        assert main(["empty"]) == 0

        assert session.scalars(select(Photo)).all() == []
        assert list(settings.photos_dir.rglob("*.jpg")) == []

    def test_no_prompt_only_with_the_explicit_option(
        self, session, settings, sample_image, fixtures_dir, monkeypatch
    ):
        """--yes is for scripts. Once it is set, nothing may ask any more."""
        from app.cli import main

        _photo_with_everything(session, settings, sample_image, fixtures_dir)

        def no_input(_):
            raise AssertionError("it asked despite --yes")

        monkeypatch.setattr("builtins.input", no_input)

        assert main(["empty", "--yes"]) == 0
        assert session.scalars(select(Photo)).all() == []

    def test_an_empty_collection_does_not_even_ask(self, session, settings, monkeypatch):
        from app.cli import main

        def no_input(_):
            raise AssertionError("an empty collection needs no confirmation")

        monkeypatch.setattr("builtins.input", no_input)

        assert main(["empty"]) == 0

    def test_the_place_index_stays(
        self, session, settings, sample_image, fixtures_dir, monkeypatch
    ):
        """It comes from an Overpass run and has nothing to do with the photos.

        Deleted along with them it would have to be rebuilt through `make places` -- with the
        internet, which the Pi in the museum does not have.
        """
        from app.cli import main
        from app.models import Place

        _photo_with_everything(session, settings, sample_image, fixtures_dir)
        session.add(
            Place(
                name="Hauptstrasse",
                name_normalized="hauptstrasse",
                lat=53.62,
                lon=9.676,
                kind="strasse",
            )
        )
        session.commit()
        monkeypatch.setattr("builtins.input", lambda _: "1")

        assert main(["empty"]) == 0

        # Only once something really was deleted does the place index say anything.
        assert session.scalars(select(Photo)).all() == []
        assert session.scalars(select(Place)).all() != []
