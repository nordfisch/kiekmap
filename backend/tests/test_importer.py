import io
import random
import struct
import zlib
from datetime import date
from pathlib import Path

import pytest
from PIL import Image, ImageFile, TiffImagePlugin
from sqlalchemy import select

from app.models import DatePrecision, ImportLog, ImportResult, Photo, Source
from app.services.importer import DONE_DIR, PROBLEM_DIR, import_directory, import_file
from app.services.storage import (
    THUMBNAIL_SIZES,
    original_path,
    sha256_of_file,
    suffix_for_mime,
    thumbnail_path,
)
from app.text import texts


class TestTheBasicCase:
    def test_a_scan_without_exif_is_taken_in(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)

        assert outcome.result == ImportResult.IMPORTED
        photo = outcome.photo
        assert photo is not None
        assert photo.original_filename == "scan_ohne_exif.jpg"
        assert (photo.width, photo.height) == (900, 640)
        # The normal case in the museum: neither place nor year known.
        assert photo.needs_location and photo.needs_date

    def test_the_original_lies_under_its_hash(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)
        sha = outcome.photo.sha256

        stored = original_path(settings.photos_dir, sha, ".jpg")
        assert stored.is_file()
        assert stored.name == f"{sha}.jpg"
        assert stored.parent.name == sha[2:4], "two-level fan-out"

    def test_thumbnails_in_both_sizes(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)

        for size in THUMBNAIL_SIZES:
            path = thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, size)
            assert path.is_file()
            with Image.open(path) as preview:
                assert preview.format == "WEBP"
                assert max(preview.size) <= size


class TestDuplicates:
    def test_the_same_file_twice(self, session, settings, sample_image):
        first = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)
        session.flush()
        second = import_file(
            session, sample_image("scan_ohne_exif.jpg", as_name="kopie.jpg"), settings
        )

        assert second.result == ImportResult.DUPLICATE
        assert second.photo.id == first.photo.id
        assert session.scalar(select(Photo).where(Photo.sha256 == first.photo.sha256))
        assert len(session.scalars(select(Photo)).all()) == 1

    def test_a_duplicate_is_logged_with_its_reason(self, session, settings, sample_image):
        import_file(session, sample_image("scan_ohne_exif.jpg"), settings)
        session.flush()
        import_file(session, sample_image("scan_ohne_exif.jpg", as_name="again.jpg"), settings)
        session.flush()

        entry = session.scalars(
            select(ImportLog).where(ImportLog.result == ImportResult.DUPLICATE)
        ).one()
        # "Something is missing" without a reason is of no use to a volunteer.
        assert "Inhaltsgleich" in entry.message


class TestDateFromExif:
    def test_a_scan_date_does_not_date_the_photo(self, session, settings, sample_image):
        """The most important case of the whole pipeline.

        The EXIF says 2019, the photo is historic. If the date were adopted, the image would sit at
        2019 on the timeline -- and it would count as dated, so it would never surface in the
        contribution panel, where somebody could have put it right.
        """
        outcome = import_file(session, sample_image("scan_mit_scandatum.jpg"), settings)
        photo = outcome.photo

        assert photo.date_from is None
        assert photo.date_precision == DatePrecision.UNKNOWN
        assert photo.needs_date, "has to appear in the contribution panel"
        # It is kept all the same: the curator should be able to see it.
        assert photo.exif_datetime.year == 2019

    def test_a_plausible_capture_date_is_adopted(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("foto_mit_gps.jpg"), settings)
        photo = outcome.photo

        assert photo.date_from == date(1975, 6, 21)
        assert photo.date_to == date(1975, 6, 21)
        assert photo.date_precision == DatePrecision.DAY
        assert photo.date_source == Source.EXIF

    def test_the_boundary_is_configurable(self, session, settings, sample_image, monkeypatch):
        """A collection with genuine digital photographs raises the boundary."""
        monkeypatch.setattr(settings, "exif_date_max_year", 2030)
        outcome = import_file(session, sample_image("scan_mit_scandatum.jpg"), settings)

        assert outcome.photo.date_from == date(2019, 3, 14)

    def test_a_scanner_date_does_not_date_the_photo(self, session, settings, sample_image):
        """The most expensive error of this import -- 116 photos of the initial collection, 91
        from a single run.

        The scanner names itself in the file, and after that the device decides, not the year.
        Without this rule a village photograph from 1910 would sit at 2015 on the timeline, count
        as dated and therefore never come up for correction.
        """
        outcome = import_file(session, sample_image("scan_vom_scanner.jpg"), settings)

        assert outcome.photo.date_from is None
        assert outcome.photo.needs_date
        assert outcome.photo.exif_datetime.year == 2015

    def test_a_scanner_date_stays_out_even_with_a_high_boundary(
        self, session, settings, sample_image, monkeypatch
    ):
        """The collection with genuine digital photographs raises the boundary -- a scanner stays
        a scanner.

        Exactly the case where the year boundary alone no longer carries: it stands high so that
        the camera photographs get through, and would let the scans through along with them.
        """
        monkeypatch.setattr(settings, "exif_date_max_year", 2030)
        outcome = import_file(session, sample_image("scan_vom_scanner.jpg"), settings)

        assert outcome.photo.date_from is None

    def test_a_camera_date_does_date_the_photo(self, session, settings, sample_image):
        """The other direction, and without it half the collection would stay undated.

        The photo is from 2014, far beyond ``exif_date_max_year``. But the year boundary is only
        the stand-in for a missing device entry -- and here that entry is in the file.
        """
        outcome = import_file(session, sample_image("kamerafoto.jpg"), settings)

        assert outcome.photo.date_from == date(2014, 3, 9)
        assert outcome.photo.date_source == Source.EXIF


class TestPlaceAndTitle:
    def test_gps_is_adopted(self, session, settings, sample_image):
        photo = import_file(session, sample_image("foto_mit_gps.jpg"), settings).photo

        assert photo.lat is not None and photo.lon is not None
        assert abs(photo.lat - 53.62053) < 0.0001
        assert abs(photo.lon - 9.67601) < 0.0001
        assert photo.location_source == Source.EXIF
        assert not photo.needs_location

    def test_a_title_from_exif(self, session, settings, sample_image):
        photo = import_file(session, sample_image("scan_mit_scandatum.jpg"), settings).photo

        assert photo.title == "Kirchweih an der Muehle"
        assert photo.title_source == Source.EXIF


class TestCameraBoilerplate:
    """What the camera writes in by itself is not a title.

    The same trap as the scan date, one field further on: "OLYMPUS DIGITAL CAMERA" really does
    stand in the title and the description field -- the photo thereby counts as titled and is never
    offered again to somebody who would know a real title. No title is more honest.
    """

    def test_a_camera_model_does_not_become_a_title(self):
        from app.services.exif import _statement

        assert _statement(b"OLYMPUS DIGITAL CAMERA") is None
        assert _statement(b"SONY DSC") is None
        assert _statement(b"Picasa") is None

    def test_a_real_title_stays(self):
        from app.services.exif import _statement

        assert _statement(b"Kirchweih an der Muehle") == "Kirchweih an der Muehle"

    def test_unknown_is_not_a_credit(self, session, settings, sample_image):
        """In 82 files of the initial collection the photographer reads literally "unbekannt".

        Adopted, the line "unbekannt" would stand under 82 photos in the kiosk -- worse than none
        at all, because it looks like information and is not.
        """
        photo = import_file(session, sample_image("scan_vom_scanner.jpg"), settings).photo

        assert photo.credit is None

    def test_a_named_photographer_stays(self, session, settings, sample_image):
        photo = import_file(session, sample_image("kamerafoto.jpg"), settings).photo

        assert photo.credit == "August Kroeger"

    def test_the_configured_credit_only_steps_in(
        self, session, settings, sample_image, monkeypatch
    ):
        """The collection as a fallback -- but only where the file names nobody."""
        monkeypatch.setattr(settings, "import_credit", "Sammlung Heimatmuseum Holm")

        without = import_file(session, sample_image("scan_ohne_exif.jpg"), settings).photo
        with_it = import_file(session, sample_image("kamerafoto.jpg"), settings).photo

        assert without.credit == "Sammlung Heimatmuseum Holm"
        assert with_it.credit == "August Kroeger"

    def test_configured_tags_reach_every_photo(self, session, settings, sample_image, monkeypatch):
        """A collection is usually about something -- in Holm about buildings.

        That does not stand in the code: otherwise the next museum would need a fork. See
        Settings.import_tags.
        """
        monkeypatch.setattr(settings, "import_tags", ["Gebaeude"])

        photo = import_file(session, sample_image("scan_ohne_exif.jpg"), settings).photo

        assert "Gebaeude" in {tag.name for tag in photo.tags}

    def test_the_description_does_not_repeat_the_title(self):
        """57 files of the initial collection carry the same sentence in both fields.

        Placed one below the other that reads as a stutter and costs the space where something the
        image really needs could stand.
        """
        from app.services.exif import ImageInfo
        from app.services.importer import _own_description

        same = ImageInfo(1, 1, "JPEG", title="Hof Sieveking")
        same.description = "hof sieveking "
        assert _own_description(same) is None

        different = ImageInfo(1, 1, "JPEG", title="Hof Sieveking")
        different.description = "Aufnahme von der Strassenseite"
        assert _own_description(different) == "Aufnahme von der Strassenseite"

    def test_a_whole_paragraph_is_a_description_not_a_title(self):
        """In the archive the whole caption stands in the title field -- 223 characters, with line
        breaks.

        As a heading in the detail view that is a wall of text. It should not be thrown away all
        the same: it moves into the description, and the folder supplies the title.
        """
        from app.services.exif import ImageInfo
        from app.services.importer import _own_description, _own_title

        long_one = ImageInfo(1, 1, "JPEG", title="Beschriftung: v. li.: " + "Johann Harms, " * 12)
        assert _own_title(long_one) is None
        assert _own_description(long_one).startswith("Beschriftung: v. li.")

        multiline = ImageInfo(1, 1, "JPEG", title="Bilderbummel S. 12\nClaus Petersen")
        assert _own_title(multiline) is None
        assert _own_description(multiline) == "Bilderbummel S. 12\nClaus Petersen"

    def test_the_boundary_is_sixty_characters(self):
        """The number is measured against the collection, not chosen.

        It stood at 120 and let eight captions of the newer archive delivery through as titles, the
        longest at 108 characters. Of the 781 titles the museum set by hand, **not one exceeds 58
        characters**; the mean is 13.
        """
        from app.services.exif import ImageInfo
        from app.services.importer import TITLE_MAX, _own_description, _own_title

        assert TITLE_MAX == 60

        caption = ImageInfo(
            1,
            1,
            "JPEG",
            title=(
                "links Hauptstrasse 27, Mitte Hauptstrasse 29, rechts im Vordergrund "
                "Schulstrasse 2a, Foto aus den 1980er Jahren"
            ),
        )
        assert _own_title(caption) is None
        assert _own_description(caption).startswith("links Hauptstrasse 27")

        short_one = ImageInfo(
            1, 1, "JPEG", title="Pizzeria und Kindergarten von der Strasse gesehen"
        )
        assert _own_title(short_one) == "Pizzeria und Kindergarten von der Strasse gesehen"

    def test_the_scanner_software_lands_in_neither_field(self):
        """ "Intel(R) JPEG Library, version [1.51.12.44]" stood as the title of 35 photos.

        It is not a shortened caption, so it must not fall back into the description the way an
        over-long title does -- that would only push the same nonsense one line lower, where it
        stands under the image in the kiosk. Point 41 removed eighteen of them by hand; with the
        next import they were back.
        """
        from app.services.exif import ImageInfo
        from app.services.importer import _own_description, _own_title

        software = ImageInfo(1, 1, "JPEG", title="Intel(R) JPEG Library, version [1.51.12.44]")
        assert _own_title(software) is None
        assert _own_description(software) is None

        also_as_description = ImageInfo(1, 1, "JPEG", title="Hof Boysen")
        also_as_description.description = "OLYMPUS DIGITAL CAMERA"
        assert _own_title(also_as_description) == "Hof Boysen"
        assert _own_description(also_as_description) is None


class TestTextEncoding:
    """Why IPTC and the XP fields have to be read differently.

    The occasion is a collection in which the tags read "牁档癩潈浬", "楗瑮牥" and "浉匠湡敤" --
    those are "ArchivHolm", "Winter" and "Im Sande", read as UTF-16. The cause is treacherous:
    **every** byte sequence of even length is valid UTF-16, so no error is ever raised and the
    fallback to UTF-8 never comes into play. Broken were therefore exactly the words of even byte
    length, intact those of odd length -- which looked like chance and was none.
    """

    def test_an_iptc_tag_of_even_byte_length_stays_readable(self):
        from app.services.exif import _text

        assert _text(b"ArchivHolm") == "ArchivHolm"
        assert _text(b"Winter") == "Winter"
        assert _text(b"Im Sande") == "Im Sande"

    def test_an_iptc_umlaut_arrives_as_utf8(self):
        from app.services.exif import _text

        assert _text("Mühlenweg".encode()) == "Mühlenweg"

    def test_a_doubly_encoded_umlaut_is_turned_back(self):
        """ "MÃ¶ller" is "Möller", put through the wrong encoding twice.

        It happens before us: one program writes UTF-8 into an EXIF field that is meant to be
        ASCII, the next reads it byte by byte. Under two photos of the initial collection a
        misspelt name would otherwise stand.
        """
        from app.services.exif import _text

        assert _text("August MÃ¶ller") == "August Möller"
        # What is already right stays untouched.
        assert _text("August Möller") == "August Möller"
        assert _text("Hof Sieveking") == "Hof Sieveking"

    def test_a_windows_field_stays_utf16(self):
        """The other direction: XPTitle and XPKeywords really are UCS2-LE."""
        from app.services.exif import _xp_text

        assert _xp_text("Kirchweih".encode("utf-16-le")) == "Kirchweih"
        assert _xp_text("Mühlenweg".encode("utf-16-le")) == "Mühlenweg"


class TestAwkwardFiles:
    def test_a_portrait_image_is_measured_the_right_way_round(
        self, session, settings, sample_image
    ):
        """The pixels are 900x600, the orientation stands in the EXIF. 600x900 is what to store."""
        photo = import_file(session, sample_image("hochkant.jpg"), settings).photo

        assert (photo.width, photo.height) == (600, 900)

    def test_a_portrait_thumbnail_is_rotated(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("hochkant.jpg"), settings)

        with Image.open(thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, 240)) as v:
            assert v.height > v.width, "the preview has to be portrait"

    def test_a_greyscale_tiff(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("graustufen.tif"), settings)

        assert outcome.result == ImportResult.IMPORTED
        assert outcome.photo.mime == "image/tiff"

    def test_cmyk_is_converted_instead_of_rejected(self, session, settings, sample_image):
        """WebP knows no CMYK. Without conversion only the last step fails."""
        outcome = import_file(session, sample_image("cmyk.tif"), settings)

        assert outcome.result == ImportResult.IMPORTED
        assert thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, 240).is_file()

    def test_a_text_file_is_rejected_with_a_reason(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("not_an_image.txt"), settings)

        assert outcome.result == ImportResult.REJECTED
        assert "kein lesbares bild" in outcome.message.lower()

    def test_a_rejected_file_leaves_nothing_behind(self, session, settings, sample_image):
        import_file(session, sample_image("not_an_image.txt"), settings)

        assert list(settings.photos_dir.rglob("*.*")) == []
        assert session.scalars(select(Photo)).all() == []


class TestParallelImports:
    """The upload, the inbox and a stick import run side by side, and may meet on one file.

    The duplicate check in step 1 is a query, and a query answers for the moment it ran. Another
    import of the same content could commit after it. The INSERT then raised an IntegrityError, and
    a thumbnail that failed afterwards deleted an original that the other import had just
    recorded.
    """

    def test_a_photo_recorded_meanwhile_makes_a_duplicate_not_an_error(
        self, session, settings, sample_image, monkeypatch
    ):
        import app.db
        from app.services import exif
        from app.services.storage import sha256_of_file

        path = sample_image("scan_ohne_exif.jpg")
        sha = sha256_of_file(path)
        read = exif.read_image_info

        def another_import_commits_first(file):
            # Past the duplicate check of this import, before its INSERT.
            with app.db.current_database().session() as other:
                other.add(
                    Photo(
                        sha256=sha,
                        original_filename="from_the_upload.jpg",
                        mime="image/jpeg",
                        bytes=1,
                        width=1,
                        height=1,
                    )
                )
                other.commit()
            return read(file)

        monkeypatch.setattr(exif, "read_image_info", another_import_commits_first)

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.DUPLICATE
        assert outcome.photo.original_filename == "from_the_upload.jpg"
        session.commit()  # the session is still usable
        assert len(session.scalars(select(Photo)).all()) == 1
        assert session.scalar(select(ImportLog.result)) == ImportResult.DUPLICATE

    def test_a_failed_thumbnail_leaves_an_original_it_did_not_write(
        self, session, settings, sample_image, monkeypatch
    ):
        """The original under this name was stored by another import, which may have recorded it."""
        from app.services import thumbnails
        from app.services.storage import sha256_of_file

        path = sample_image("scan_ohne_exif.jpg")
        stored = original_path(settings.photos_dir, sha256_of_file(path), ".jpg")
        stored.parent.mkdir(parents=True)
        stored.write_bytes(path.read_bytes())

        def stumbles(*args):
            raise OSError("No space left on device")

        monkeypatch.setattr(thumbnails, "create_thumbnails", stumbles)

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.REJECTED
        assert stored.is_file(), "deleted a file this import had not written"

    def test_no_partial_copy_is_left_behind(self, session, settings, sample_image):
        """The original is copied under a temporary name first, so a reader never sees half."""
        import_file(session, sample_image("scan_ohne_exif.jpg"), settings)

        assert list(settings.data_dir.glob("partial-*")) == []


class TestTagNamed:
    def test_an_existing_tag_is_reused_not_created_again(self, session):
        from app.models import Tag
        from app.services.tags import tag_named

        first = tag_named(session, "Gasthof")
        second = tag_named(session, "Gasthof")

        assert first.id == second.id
        assert len(session.scalars(select(Tag)).all()) == 1

    def test_a_tag_the_caller_added_but_did_not_write_out_is_not_created_twice(self, session):
        """The INSERT cannot see an object that is only pending in the session.

        Without the flush first, the name was written twice and the next flush failed the unique
        constraint -- which is how ``make seed`` broke.
        """
        from app.models import Tag
        from app.services.tags import tag_named

        pending = Tag(name="Winter")
        session.add(pending)

        tag = tag_named(session, "Winter")
        session.flush()

        assert tag is pending
        assert len(session.scalars(select(Tag)).all()) == 1


class TestTheInbox:
    def test_what_is_taken_in_is_filed_aside_not_deleted(self, session, settings, sample_image):
        source = settings.incoming_dir / "scan_ohne_exif.jpg"
        source.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())

        import_file(session, source, settings, move_aside=True)

        assert not source.exists()
        # Never delete: a helper who sees their file vanish is having a bad day.
        assert (settings.incoming_dir / DONE_DIR / "scan_ohne_exif.jpg").is_file()

    def test_a_problem_file_goes_into_the_problem_folder(self, session, settings, sample_image):
        source = settings.incoming_dir / "not_an_image.txt"
        source.write_bytes(sample_image("not_an_image.txt").read_bytes())

        import_file(session, source, settings, move_aside=True)

        assert (settings.incoming_dir / PROBLEM_DIR / "not_an_image.txt").is_file()

    def test_a_file_of_the_same_name_overwrites_nothing(self, session, settings, sample_image):
        for content in ("scan_ohne_exif.jpg", "hochkant.jpg"):
            source = settings.incoming_dir / "gleicher_name.jpg"
            source.write_bytes(sample_image(content).read_bytes())
            import_file(session, source, settings, move_aside=True)

        done = sorted(p.name for p in (settings.incoming_dir / DONE_DIR).iterdir())
        assert done == ["gleicher_name (2).jpg", "gleicher_name.jpg"]

    def test_the_special_folders_are_not_searched_again(self, session, settings, sample_image):
        source = settings.incoming_dir / "scan_ohne_exif.jpg"
        source.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())
        import_file(session, source, settings, move_aside=True)
        session.flush()

        # Without this exception the watcher would loop endlessly over _done/.
        again = import_directory(session, settings.incoming_dir, settings)
        assert again == []


class TestImportingADirectory:
    def test_everything_at_once(self, session, settings, tmp_path: Path, fixtures_dir: Path):
        source = tmp_path / "stapel"
        source.mkdir()
        for file in fixtures_dir.iterdir():
            if file.suffix in (".jpg", ".tif", ".txt"):
                (source / file.name).write_bytes(file.read_bytes())

        outcomes = import_directory(session, source, settings)
        session.flush()

        taken_in = [e for e in outcomes if e.result == ImportResult.IMPORTED]
        rejected = [e for e in outcomes if e.result == ImportResult.REJECTED]

        assert len(taken_in) == 8, "8 images, 1 text file"
        assert len(rejected) == 1
        # The user's originals stay untouched.
        assert len(list(source.iterdir())) == 9


class TestWhereThePathLayerDoesNotApply:
    """An upload has no path -- and must not invent one.

    The opposite direction to the error in the inbox. When uploading through the browser the file
    lands in a temporary directory; its name says nothing about anybody's archive. If this path got
    the path layer along with it, the entries would be freely invented but would look like ones
    that were read -- and because the import fills only empty fields, the photo would never come up
    for correction.
    """

    def test_an_upload_has_no_path_and_invents_none(
        self, session, settings, fixtures_dir: Path, monkeypatch
    ):
        from app.models import Place
        from app.services.importer import import_upload
        from app.services.places import normalize

        monkeypatch.setattr(settings, "import_provenance", "Archiv/")

        # The street is named after the data directory the files lie in. Only that way does the
        # test really hit something: the temporary folder is called "upload-a1b2c3", which no
        # street name matches. The folder above it has the same name on every device.
        street = settings.data_dir.name
        session.add(
            Place(
                name=street,
                name_normalized=normalize(street),
                lat=53.62,
                lon=9.676,
                kind="street",
            )
        )
        session.commit()

        with (fixtures_dir / "scan_ohne_exif.jpg").open("rb") as file:
            photo = import_upload(session, "023.jpg", file, settings).photo

        assert photo is not None
        assert photo.needs_location
        assert photo.place_name is None
        assert photo.title is None
        assert photo.provenance is None
        assert photo.tags == []


class TestUnwieldyFiles:
    """Files the import itself gets stuck on -- not their content, their form."""

    def test_a_tiff_with_crooked_xmp_does_not_abort_the_run(self, session, settings, tmp_path):
        """25 archive scans file their XMP in a numeric tag, and Pillow returns numbers.

        Every later ``getexif()`` runs a regular expression over it and raises ``TypeError`` --
        which ``import_file`` does not catch, because it is prepared for ``OSError`` and
        ``ValueError``. **A single such file would thereby have ended not itself but the whole
        import run**, and TIFF is an allowed format.
        """
        from PIL import TiffImagePlugin

        directory = TiffImagePlugin.ImageFileDirectory_v2()
        directory[700] = (1010792560, 1633905509)  # XMLPacket
        directory.tagtype[700] = 4  # LONG instead of BYTE -- that is how the archive files hold it
        path = tmp_path / "scan.tif"
        Image.new("RGB", (40, 30)).save(path, "TIFF", tiffinfo=directory)

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.IMPORTED
        assert (outcome.photo.width, outcome.photo.height) == (40, 30)

    def test_an_exception_outside_oserror_and_valueerror_rejects_the_file(
        self, session, settings, tmp_path, monkeypatch
    ):
        """Pillow raises more than the two, and the file is input from outside.

        ``DecompressionBombError`` derives from ``Exception`` directly. Before, it left
        ``import_file`` instead of rejecting the file -- a 500 for the upload, an aborted job for
        the stick, and for the inbox a file tried again on every sweep. ``test_watcher.py`` holds
        the real bomb; this one stands for the rest of them.
        """
        from app.services import exif

        def stumbles(path):
            raise SyntaxError("not a PNG file")

        monkeypatch.setattr(exif, "read_image_info", stumbles)
        path = tmp_path / "odd.png"
        path.write_bytes(b"\x89PNG not really")

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.REJECTED
        assert "not a PNG file" in outcome.message

    def test_a_thumbnail_that_fails_oddly_rejects_the_file_and_leaves_nothing(
        self, session, settings, sample_image, monkeypatch
    ):
        from app.services import thumbnails

        def stumbles(*args):
            raise TypeError

        monkeypatch.setattr(thumbnails, "create_thumbnails", stumbles)

        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)

        assert outcome.result == ImportResult.REJECTED
        assert "TypeError" in outcome.message, "an exception without a message still says what"
        assert list(settings.photos_dir.rglob("*.*")) == []
        assert session.scalars(select(Photo)).all() == []


def _png_header_claiming(width: int, height: int) -> bytes:
    """A PNG header claiming a size. Opening reads only the header, so no pixels are needed."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        checksum = struct.pack(">I", zlib.crc32(kind + data))
        return struct.pack(">I", len(data)) + kind + data + checksum

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IEND", b"")


class TestLargeScans:
    """A thumbnail needs a fraction of a scan's pixels, and the Pi has 4 GB beside Chromium.

    The thumbnails used to decode every scan in full and then copy it three times: rotated,
    converted, once per size. A 35 MP scan cost about half a gigabyte. Above Pillow's limit it only
    warned, so an image of up to 179 MP was decoded the same way.
    """

    #: Four times the long side of the 1200 px thumbnail: the smallest image that is reduced at all,
    #: and generated in a fraction of a second.
    SIZE = (4800, 3200)

    @pytest.fixture
    def decoded(self, monkeypatch) -> list[tuple[int, int]]:
        """The size of every image Pillow decodes from a file."""
        sizes: list[tuple[int, int]] = []
        real_load = ImageFile.ImageFile.load

        def load(image):
            if image.tile:
                sizes.append(image.size)
            return real_load(image)

        monkeypatch.setattr(ImageFile.ImageFile, "load", load)
        return sizes

    def _scan(self, tmp_path: Path, format: str) -> Path:
        path = tmp_path / f"large.{format.lower()}"
        gradient = Image.linear_gradient("L").resize(self.SIZE)
        if format == "MPO":
            gradient.save(path, "MPO", save_all=True, append_images=[gradient.rotate(180)])
        elif format == "PNG":
            gradient.save(path, "PNG", compress_level=1)
        else:
            gradient.save(path, format)
        return path

    @pytest.mark.parametrize("format", ["JPEG", "MPO"])
    def test_a_large_jpeg_is_not_decoded_in_full_for_its_thumbnails(
        self, session, settings, tmp_path, decoded, format
    ):
        path = self._scan(tmp_path, format)

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.IMPORTED
        assert decoded, "the thumbnails were made from decoded pixels"
        assert max(width * height for width, height in decoded) <= 2400 * 1600
        # What is stored describes the original, not the decode.
        assert (outcome.photo.width, outcome.photo.height) == self.SIZE
        assert outcome.photo.sha256 == sha256_of_file(path)
        with Image.open(thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, 1200)) as v:
            assert v.size == (1200, 800)

    def test_a_jpeg_is_not_decoded_below_twice_its_largest_thumbnail(
        self, session, settings, tmp_path, decoded
    ):
        """JPEG reduces by whole powers of two, which blurs. Lanczos does the last factor of two.

        Decoded straight to 1200 x 800 the draft would save more memory and cost sharpness.
        """
        outcome = import_file(session, self._scan(tmp_path, "JPEG"), settings)

        assert outcome.result == ImportResult.IMPORTED
        assert min(max(size) for size in decoded) >= 2 * max(THUMBNAIL_SIZES)

    def test_a_large_png_is_reduced_before_it_is_rotated_and_converted(
        self, session, settings, tmp_path, monkeypatch
    ):
        """PNG and TIFF decode only in full. Each copy after that is what ``reduce`` saves."""
        from app.services import thumbnails

        received: list[tuple[int, int]] = []
        real = thumbnails._for_display

        def for_display(image):
            received.append(image.size)
            return real(image)

        monkeypatch.setattr(thumbnails, "_for_display", for_display)

        outcome = import_file(session, self._scan(tmp_path, "PNG"), settings)

        assert outcome.result == ImportResult.IMPORTED
        assert received == [(2400, 1600)]

    @pytest.mark.filterwarnings("ignore::PIL.Image.DecompressionBombWarning")
    @pytest.mark.parametrize(
        "size",
        [(1200, 1000), (1500, 1500)],
        ids=["up to twice the limit, where Pillow only warns", "above twice the limit"],
    )
    def test_an_image_above_the_limit_is_rejected_and_leaves_nothing(
        self, session, settings, tmp_path, monkeypatch, size
    ):
        monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1_000_000)
        path = tmp_path / "large.jpg"
        Image.new("L", size).save(path)

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.REJECTED
        assert outcome.message == texts().imports.too_many_pixels(1)
        assert list(settings.photos_dir.rglob("*.*")) == []
        assert list(settings.thumbs_dir.rglob("*.*")) == []
        session.flush()
        assert session.scalars(select(Photo)).all() == []
        assert session.scalar(select(ImportLog.result)) == ImportResult.REJECTED

    @pytest.mark.filterwarnings("ignore::PIL.Image.DecompressionBombWarning")
    def test_the_limit_is_set_rather_than_left_to_pillow(self, tmp_path):
        """An A3 scan at 600 dpi comes in. 81 MP does not, though Pillow's default lets it pass."""
        from app.services.exif import TooManyPixels, open_image

        a3 = tmp_path / "a3.png"
        a3.write_bytes(_png_header_claiming(9921, 7016))
        with open_image(a3) as image:
            assert image.size == (9921, 7016)

        larger = tmp_path / "larger.png"
        larger.write_bytes(_png_header_claiming(9000, 9000))
        with pytest.raises(TooManyPixels):
            open_image(larger)


# --- broken files ------------------------------------------------------------------------------
#
# Generated, not kept as fixtures. A broken file is only worth anything as a test if the way it is
# broken is written down, and a file in a folder does not say how it was made.

#: The formats the import allows, each damaged in every way below.
BROKEN_FORMATS = ["JPEG", "MPO", "PNG", "TIFF", "WEBP"]

#: What the generated file is called. Not what the import decides it is -- a truncated MPO is a
#: JPEG to Pillow, and the name has no say in it either way.
_SUFFIX = {"JPEG": ".jpg", "MPO": ".mpo", "PNG": ".png", "TIFF": ".tif", "WEBP": ".webp"}

#: Small enough to generate in milliseconds, large enough that half the file is still more than a
#: header. An uncompressed TIFF of this size is 230 kB, which is the largest of them.
_SAMPLE_SIZE = (320, 240)

#: Every call that needs noise uses this one seed, so a failing case can be reproduced.
_SEED = 4711

#: The first bytes a reader uses to recognise the format. Taken from a real file rather than
#: written out per format: a WebP signature is RIFF, a length and "WEBP", and a PNG signature is
#: followed by the length of its first chunk.
_SIGNATURE_BYTES = 12

#: Enough to claim more pixels than the limit allows without holding one. 81 megapixels for the
#: formats that store the size as a number; WebP stores 14 bits per side, and 16383 is its
#: largest, which is 268 megapixels.
_HUGE = 9000
_HUGE_WEBP = 16383


def _valid_image(format: str) -> bytes:
    """A small, whole image of one format -- the starting point of every damaged one."""
    image = Image.linear_gradient("L").resize(_SAMPLE_SIZE).convert("RGB")
    buffer = io.BytesIO()
    if format == "MPO":
        image.save(buffer, "MPO", save_all=True, append_images=[image.rotate(180)])
    else:
        image.save(buffer, format)
    return buffer.getvalue()


def _truncated_after_the_header(format: str) -> bytes:
    """Signature and header, no image data -- a copy that stopped after its first block."""
    return _valid_image(format)[:64]


def _truncated_after_half_the_data(format: str) -> bytes:
    """A whole header and half the pixels. The file opens; loading it is what fails."""
    data = _valid_image(format)
    return data[: len(data) // 2]


def _random_bytes_behind_the_signature(format: str) -> bytes:
    """Recognised as its format, nonsense from the header on."""
    return _valid_image(format)[:_SIGNATURE_BYTES] + random.Random(_SEED).randbytes(512)


def _claiming_in_jpeg(data: bytes, width: int, height: int) -> bytes:
    """Overwrite the size in the SOF0 marker: length, sample precision, height, width."""
    patched = bytearray(data)
    struct.pack_into(">HH", patched, data.index(b"\xff\xc0") + 5, height, width)
    return bytes(patched)


def _claiming_in_tiff(data: bytes, width: int, height: int) -> bytes:
    """Overwrite ImageWidth and ImageLength in the first directory.

    An IFD entry is twelve bytes -- tag, type, count, value -- and Pillow writes both sizes as a
    LONG, which stands in the entry itself rather than somewhere behind it.
    """
    patched = bytearray(data)
    (directory,) = struct.unpack_from("<I", patched, 4)
    (entries,) = struct.unpack_from("<H", patched, directory)
    for index in range(entries):
        entry = directory + 2 + index * 12
        (tag,) = struct.unpack_from("<H", patched, entry)
        if tag in (256, 257):
            struct.pack_into("<I", patched, entry + 8, width if tag == 256 else height)
    return bytes(patched)


def _claiming_in_webp(data: bytes, width: int, height: int) -> bytes:
    """Overwrite the size in the VP8 frame header, which follows its three-byte start code."""
    patched = bytearray(data)
    struct.pack_into("<HH", patched, data.index(b"\x9d\x01\x2a") + 3, width, height)
    return bytes(patched)


def _a_header_claiming_huge_dimensions(format: str) -> bytes:
    """A few hundred bytes whose header claims more pixels than the limit allows.

    #59 was reproduced with such a file: a PNG of a few hundred bytes claiming 20000 x 20000. The
    header is read before a pixel is, so the claim costs nothing to make and has to be answered
    without allocating anything.
    """
    if format == "PNG":
        return _png_header_claiming(_HUGE, _HUGE)
    data = _valid_image(format)
    if format == "WEBP":
        return _claiming_in_webp(data, _HUGE_WEBP, _HUGE_WEBP)
    if format == "TIFF":
        return _claiming_in_tiff(data, _HUGE, _HUGE)
    return _claiming_in_jpeg(data, _HUGE, _HUGE)


def _forced(directory: TiffImagePlugin.ImageFileDirectory_v2, tag: int, value, kind: int) -> None:
    """Write a tag with a type the specification does not give it."""
    directory[tag] = value
    directory.tagtype[tag] = kind


_ASCII, _SHORT, _LONG = 2, 3, 4

#: The pointers to the two sub-directories of an EXIF block.
_EXIF_POINTER, _GPS_POINTER = 0x8769, 0x8825


def _crooked_directory() -> TiffImagePlugin.ImageFileDirectory_v2:
    """The tags the import reads, each holding the wrong kind of value.

    Numbers where text belongs and text where a number belongs. That is not invented: 25 TIFF
    scans of the initial collection file their XMP packet as LONG numbers, which is the last tag
    here -- see ``TestUnwieldyFiles``.
    """
    directory = TiffImagePlugin.ImageFileDirectory_v2()
    _forced(directory, 0x010E, (7,), _LONG)  # ImageDescription, ASCII by the specification
    _forced(directory, 0x010F, (1, 2, 3), _LONG)  # Make
    _forced(directory, 0x0110, (17,), _LONG)  # Model
    _forced(directory, 0x0112, "sideways", _ASCII)  # Orientation, a SHORT from 1 to 8
    _forced(directory, 0x013B, (255, 255), _SHORT)  # Artist
    _forced(directory, 0x8298, (9,), _LONG)  # Copyright
    _forced(directory, 0x9C9B, (65, 66), _LONG)  # XPTitle, bytes of UCS2
    _forced(directory, 0x9C9E, (67,), _LONG)  # XPKeywords
    _forced(directory, 700, (1010792560, 1633905509), _LONG)  # XMLPacket
    return directory


def _crooked_exif() -> bytes:
    """A whole EXIF block: the tags above plus a date and a coordinate of the wrong type.

    The block is a small TIFF file, and its two sub-directories are reached through an offset into
    it. The offsets are therefore only known once the directory before them has been laid out.
    """
    exif_ifd = TiffImagePlugin.ImageFileDirectory_v2()
    _forced(exif_ifd, 0x9003, (2019, 3, 14), _LONG)  # DateTimeOriginal, "2019:03:14 11:02:00"
    _forced(exif_ifd, 0x9004, (0,), _LONG)  # DateTimeDigitized

    gps_ifd = TiffImagePlugin.ImageFileDirectory_v2()
    _forced(gps_ifd, 0x0001, (1, 2), _LONG)  # GPSLatitudeRef, "N" or "S"
    _forced(gps_ifd, 0x0002, "53 degrees", _ASCII)  # GPSLatitude, three rational numbers
    _forced(gps_ifd, 0x0003, (78,), _LONG)  # GPSLongitudeRef
    _forced(gps_ifd, 0x0004, (9, 9), _LONG)  # GPSLongitude

    main = _crooked_directory()
    # Setting a pointer does not change the length of the directory it stands in: both are a LONG
    # and stand in the entry itself. So the first pass only measures, and the second one writes.
    _forced(main, _EXIF_POINTER, 0, _LONG)
    _forced(main, _GPS_POINTER, 0, _LONG)
    header = b"II*\x00" + struct.pack("<I", 8)
    measured = len(main.tobytes(len(header)))

    main[_EXIF_POINTER] = len(header) + measured
    exif_bytes = exif_ifd.tobytes(main[_EXIF_POINTER])
    main[_GPS_POINTER] = main[_EXIF_POINTER] + len(exif_bytes)
    gps_bytes = gps_ifd.tobytes(main[_GPS_POINTER])

    block = main.tobytes(len(header))
    assert len(block) == measured, "the pointers moved what they point at"
    return header + block + exif_bytes + gps_bytes


def _an_exif_block_of_the_wrong_type(format: str) -> bytes:
    """A whole image whose EXIF holds the wrong type in every field the import reads."""
    image = Image.linear_gradient("L").resize(_SAMPLE_SIZE).convert("RGB")
    buffer = io.BytesIO()
    if format == "TIFF":
        # A TIFF is its own EXIF: the tags stand in its first directory, and there is no block to
        # hang beside them.
        image.save(buffer, "TIFF", tiffinfo=_crooked_directory())
    elif format == "MPO":
        image.save(
            buffer, "MPO", save_all=True, append_images=[image.rotate(180)], exif=_crooked_exif()
        )
    else:
        image.save(buffer, format, exif=_crooked_exif())
    return buffer.getvalue()


#: The ways a file arrives broken. The key is the test id.
DAMAGE = {
    "truncated after the header": _truncated_after_the_header,
    "truncated after half the data": _truncated_after_half_the_data,
    "random bytes behind a valid signature": _random_bytes_behind_the_signature,
    "a header claiming huge dimensions": _a_header_claiming_huge_dimensions,
    "an EXIF block of the wrong type": _an_exif_block_of_the_wrong_type,
}


@pytest.mark.filterwarnings("ignore::PIL.Image.DecompressionBombWarning")
class TestBrokenFiles:
    """Every allowed format, damaged in five ways: the import answers, it does not raise.

    The files come from outside -- the inbox, the browser upload, somebody's stick -- and none of
    them can be assumed whole. #59 was a single file that raised instead of being rejected: it
    stayed in the inbox, failed again on every sweep, and no file sorted after it was ever taken
    in. The fix catches every exception, and that promise is what this checks, for each format
    rather than for the one file that caused it.
    """

    def _broken(self, tmp_path: Path, format: str, damage: str) -> Path:
        path = tmp_path / f"broken{_SUFFIX[format]}"
        path.write_bytes(DAMAGE[damage](format))
        return path

    @pytest.mark.parametrize("format", BROKEN_FORMATS)
    @pytest.mark.parametrize("damage", list(DAMAGE), ids=list(DAMAGE))
    def test_a_broken_file_is_answered_and_leaves_a_consistent_state(
        self, session, settings, tmp_path, format, damage
    ):
        """Three outcomes are allowed, and each of them has to hold together.

        Rejected means nothing is left behind: no original, no thumbnail, no row. Taken in means
        the opposite -- the row exists and so do its files, because a row without them is a gap in
        the kiosk that nothing repairs.
        """
        path = self._broken(tmp_path, format, damage)

        # The call is the first assertion: an exception here fails the test instead of being
        # turned into one of the three outcomes.
        outcome = import_file(session, path, settings)
        session.flush()

        assert outcome.message, "a volunteer reads this line and needs a reason in it"
        assert session.scalar(select(ImportLog.result)) == outcome.result
        assert list(settings.data_dir.glob("partial-*")) == []

        if outcome.result == ImportResult.REJECTED:
            assert session.scalars(select(Photo)).all() == []
            assert list(settings.photos_dir.rglob("*.*")) == []
            assert list(settings.thumbs_dir.rglob("*.*")) == []
            return

        photo = session.scalars(select(Photo)).one()
        assert photo.sha256 == sha256_of_file(path)
        stored = original_path(settings.photos_dir, photo.sha256, suffix_for_mime(photo.mime))
        assert stored.is_file()
        for size in THUMBNAIL_SIZES:
            assert thumbnail_path(settings.thumbs_dir, photo.sha256, size).is_file()

    @pytest.mark.parametrize("format", BROKEN_FORMATS)
    def test_a_claimed_size_is_answered_before_a_pixel_is_read(
        self, session, settings, tmp_path, format
    ):
        """The reason this case gets its own test: rejected for the right reason.

        A file the reader does not understand at all is rejected too, and would pass the test
        above without the claim ever being read. The message says which of the two happened, and
        this one has to name the limit -- the volunteer can then scan the sheet again smaller.
        """
        path = self._broken(tmp_path, format, "a header claiming huge dimensions")

        outcome = import_file(session, path, settings)

        assert outcome.result == ImportResult.REJECTED
        assert outcome.message == texts().imports.too_many_pixels(
            Image.MAX_IMAGE_PIXELS // 1_000_000
        )

    def test_an_inbox_of_broken_files_empties_itself_and_takes_in_the_whole_one(
        self, session, settings, sample_image
    ):
        """#59 itself, in the folder it happened in.

        One file that raises must not end the sweep for the files behind it, and it must not stay
        in the inbox either -- there it would fail again on every sweep. The whole image is named
        so that it sorts last, because the sweep walks the folder in order.
        """
        inbox = settings.incoming_dir
        for damage, damaged in DAMAGE.items():
            for format in BROKEN_FORMATS:
                name = f"{damage}-{format}".replace(" ", "-")
                (inbox / f"{name}{_SUFFIX[format]}").write_bytes(damaged(format))
        (inbox / "zzz-whole.jpg").write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())

        outcomes = import_directory(session, inbox, settings, move_aside=True)
        session.flush()

        assert len(outcomes) == len(DAMAGE) * len(BROKEN_FORMATS) + 1
        whole = outcomes[-1]
        assert whole.succeeded
        assert whole.photo.original_filename == "zzz-whole.jpg"
        # Every file got an answer, and the sweep wrote one line per file into the import log.
        assert len(session.scalars(select(ImportLog)).all()) == len(outcomes)

        assert sorted(entry.name for entry in inbox.iterdir()) == [DONE_DIR, PROBLEM_DIR]
        rejected = sum(1 for entry in outcomes if entry.result == ImportResult.REJECTED)
        assert len(list((inbox / PROBLEM_DIR).iterdir())) == rejected
        assert "zzz-whole.jpg" in {entry.name for entry in (inbox / DONE_DIR).iterdir()}
