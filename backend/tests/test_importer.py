from datetime import date
from pathlib import Path

from PIL import Image
from sqlalchemy import select

from app.models import DatePrecision, ImportLog, ImportResult, Photo, Source
from app.services.importer import DONE_DIR, PROBLEM_DIR, import_directory, import_file
from app.services.storage import THUMBNAIL_SIZES, original_path, thumbnail_path


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
