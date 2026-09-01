"""Tests of the path layer: what the folder structure says about a photo.

A museum archive is sorted, and the sorting is a statement. Discarding it would mean asking
visitors for the place of a photo whose address stands in its folder name.

Three mistakes happen silently there, and each has its test here:

  1. "10 H Brahms" becomes house number 10h. There is no such number -- the photo lands on the
     street instead of at the house, and nobody sees that anything went wrong.
  2. The **street centre** overwrites a coordinate from the file. At 150 m it is coarser than the
     point it replaces: the photo becomes less precise, and it looks like a refinement.
  3. A statement made by a person is overwritten. Only the EXIF gives way -- and only since it was
     measured that these coordinates were typed in rather than recorded.

The rule under 2 and 3 ran the other way round until August 2026: the EXIF always beat the folder.
Why it was turned around stands in the module docstring of ``services/foldermeta.py``.
"""

import pytest

from app.models import Place
from app.services import places as place_service
from app.services.foldermeta import (
    apply_folder_meta,
    parse_path,
    split_housenumber,
    street_names,
)
from app.services.importer import import_file


def _place(session, name, kind, lat=53.62, lon=9.676, street=None, housenumber=None):
    session.add(
        Place(
            name=name,
            name_normalized=place_service.normalize(name),
            lat=lat,
            lon=lon,
            kind=kind,
            street=street,
            housenumber=housenumber,
        )
    )


def _street(session, name):
    _place(session, name, "strasse")


@pytest.fixture
def place_index(session):
    """One street from Holm with a few house numbers -- and one that is missing."""
    _place(session, "Hauptstrasse", "strasse", lat=53.6200, lon=9.6760)
    _place(session, "Hoernstrasse", "strasse", lat=53.6210, lon=9.6770)
    for number in ("10", "14", "9a"):
        _place(
            session,
            f"Hauptstrasse {number}",
            "adresse",
            lat=53.6205,
            lon=9.6765,
            street="Hauptstrasse",
            housenumber=number,
        )
    session.commit()
    return session


class TestReadingAHouseNumber:
    def test_a_name_stands_beside_the_number(self):
        assert split_housenumber("14 Gasthof Petersen") == ("14", "Gasthof Petersen")

    def test_a_letter_counts_only_without_a_space(self):
        """The silent error: "10 H Brahms" is number 10, the Brahms family.

        Read as "10h" the address is not found in the place index, the photo slides onto the street
        point -- and afterwards nobody sees that it could have lain more precisely.
        """
        assert split_housenumber("10 H Brahms") == ("10", "H Brahms")
        assert split_housenumber("25a Zahnarztpraxis") == ("25a", "Zahnarztpraxis")

    def test_leading_zeros_are_filing_not_an_address(self):
        assert split_housenumber("009a") == ("9a", None)
        assert split_housenumber("001") == ("1", None)

    def test_with_a_range_the_first_number_counts(self):
        assert split_housenumber("099-105 Weltweit") == ("99", "Weltweit")
        assert split_housenumber("2-6 Gasthof Petersen") == ("2", "Gasthof Petersen")
        assert split_housenumber("011-011a Neubau") == ("11", "Neubau")

    def test_a_folder_without_a_number_is_only_a_name(self):
        assert split_housenumber("Glasfaser") == (None, "Glasfaser")

    def test_nothing_but_zeros_is_no_house_number(self):
        """ "00" is the archive's catch-all for everything without an address, not house number 0.

        Read as a number the photo would get the place name "Lehmweg 0" -- an address that exists
        nowhere. And because that name holds a digit, the contribution panel would never offer to
        put it right either (see services/needs.py).
        """
        assert split_housenumber("00 div") == (None, "div")
        assert split_housenumber("00") == (None, None)

    def test_a_number_as_a_name_does_not_become_a_title(self, place_index):
        """ "049" is a house number, not a name -- a photo under it gets no title.

        Otherwise it would read "Hauptstrasse 49, 049" or, since 16 August 2026, simply "049".
        """
        assert split_housenumber("049") == ("49", None)

        found = parse_path(("Hauptstrasse", "049"), street_names(place_index))
        assert (found.address, found.name) == ("Hauptstrasse 49", None)


class TestReadingThePath:
    def test_the_place_index_recognises_the_street_not_the_folder_name(self, place_index):
        """There is no "streets" switch in the code -- otherwise Holm would be wired into it."""
        streets = street_names(place_index)

        found = parse_path(("Strassen", "Hauptstrasse", "14 Gasthof Petersen"), streets)

        assert found.street == "Hauptstrasse"
        assert found.housenumber == "14"
        assert found.name == "Gasthof Petersen"
        assert found.address == "Hauptstrasse 14"

    def test_without_a_known_street_the_path_says_nothing(self, place_index):
        found = parse_path(("Urlaub", "2019"), street_names(place_index))

        assert found.street is None
        assert found.address is None

    def test_a_shortened_folder_name_finds_the_street(self, session):
        """The archive shortens: folder "Wiesengrund", street "Im Wiesengrund"."""
        _street(session, "Im Wiesengrund")
        session.commit()

        found = parse_path(("Wiesengrund", "07"), street_names(session))

        assert found.street == "Im Wiesengrund"

    def test_with_two_possible_streets_nothing_is_guessed(self, session):
        """ "Deelenweg" sits inside "Deelenweg I" and "Deelenweg II".

        Guessed, the photos might land at the other end of the village -- and because they then
        count as located, nobody ever sees it. Better unlocated and in the contribution panel.
        """
        _street(session, "Deelenweg I")
        _street(session, "Deelenweg II")
        session.commit()

        found = parse_path(("Deelenweg", "10 Deelenhof"), street_names(session))

        assert found.street is None

    def test_a_house_number_is_not_a_street_name(self, session):
        """The place index holds "Kolonie Autal 2" as a street -- and the house-number folder "2"
        matched it, unambiguously and completely wrongly.

        The two photos from "Achter de Moehl/2" thereby landed at the other end of the village,
        without a house number and with the wrong street name. Only a name is a street.
        """
        _street(session, "Achter de Moehl")
        _street(session, "Kolonie Autal 2")
        session.commit()

        found = parse_path(("Achter de Moehl", "2"), street_names(session))

        assert (found.street, found.housenumber) == ("Achter de Moehl", "2")

    def test_a_part_of_a_word_is_not_a_street_name(self, session):
        """Word by word, not as a string: "Horn" is not the "Bredhornstrasse"."""
        _street(session, "Bredhornstrasse")
        session.commit()

        assert parse_path(("Horn",), street_names(session)).street is None

    def test_a_subfolder_may_repeat_the_street(self, place_index):
        """The archive files a folder "Hauptstrasse 14" under "Hauptstrasse".

        Unread that becomes not a house but a name -- and thereby a title "Hauptstrasse 14" above
        the line "Hauptstrasse". Exactly the echo of the address that decisions.md, point 48, has
        just abolished.
        """
        found = parse_path(("Hauptstrasse", "Hauptstrasse 14"), street_names(place_index))

        assert (found.street, found.housenumber, found.name) == ("Hauptstrasse", "14", None)

    def test_a_similar_name_is_not_cut_apart(self, session):
        """The counter-check: the prefix alone is not reason enough to cut.

        Under the street "Twiete" lies a folder "Twietenhof". Shortened by the prefix alone,
        "nhof" would remain -- a name that never existed.
        """
        _street(session, "Twiete")
        session.commit()

        found = parse_path(("Twiete", "Twietenhof"), street_names(session))

        assert (found.housenumber, found.name) == (None, "Twietenhof")

    def test_the_street_may_be_the_chosen_folder_itself(self, place_index):
        """On the stick the volunteer chooses the folder -- often the street."""
        found = parse_path(("Hauptstrasse", "14 Museum"), street_names(place_index))

        assert (found.street, found.housenumber) == ("Hauptstrasse", "14")


class TestWhatEndsUpOnThePhoto:
    def _import(self, session, settings, sample_image, subpath: str, image="scan_ohne_exif.jpg"):
        root = settings.data_dir / "archiv"
        target = root / subpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sample_image(image).read_bytes())

        outcome = import_file(session, target, settings)
        assert outcome.photo is not None
        apply_folder_meta(session, outcome.photo, target, root, settings)
        return outcome.photo

    def test_the_house_number_places_the_photo_at_the_house(
        self, session, settings, sample_image, place_index
    ):
        photo = self._import(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert (photo.lat, photo.lon) == (53.6205, 9.6765)
        assert photo.place_name == "Hauptstrasse 14"
        assert photo.location_accuracy_m == place_service.ACCURACY_ADDRESS_M
        assert photo.title == "Museum"

    def test_the_title_does_not_repeat_the_address(
        self, session, settings, sample_image, place_index
    ):
        """The title stands above the address in the detail view, not instead of it.

        Until 16 August 2026 this photo was called "Hauptstrasse 14, Museum" -- and below it stood
        "Hauptstrasse 14" once more. Point 41 took 815 such titles apart by hand, and the next
        import wrote 323 of them back. Where the folder names only a number, the title stays empty:
        a line that only repeats the next one is not a line.
        """
        with_name = self._import(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")
        assert with_name.title == "Museum"
        assert with_name.place_name == "Hauptstrasse 14"

        # A different image, otherwise the import recognises it by its SHA-256 as a duplicate and
        # returns the first photo -- the second half of the test would then check itself.
        without_name = self._import(
            session, settings, sample_image, "Hauptstrasse/10/b.jpg", "hochkant.jpg"
        )
        assert without_name.title is None
        assert without_name.place_name == "Hauptstrasse 10"

    def test_a_folder_without_a_house_number_puts_the_photo_on_the_street(
        self, session, settings, sample_image, place_index
    ):
        """Until August 2026 such a photo stayed unlocated -- 72 of them in the initial collection.

        The reason was that the street point looks like an answer and the photo would thereby drop
        out of "where is this?". That held while there were two questions. Since there is a third,
        it does not drop out but falls into the more precise question: exactly one street-accurate
        photo without a house number is what the refinement looks for.

        The 150 m still say what the point is worth. The street also stays as a tag.
        """
        photo = self._import(session, settings, sample_image, "Hauptstrasse/119.jpg")

        assert not photo.needs_location
        assert (photo.lat, photo.lon) == (53.6200, 9.6760)
        assert photo.location_accuracy_m == place_service.ACCURACY_STREET_M
        assert photo.location_source == "curator"
        assert "Hauptstrasse" in {tag.name for tag in photo.tags}

    def test_an_unknown_house_number_falls_back_to_the_street(
        self, session, settings, sample_image, place_index
    ):
        """The number is not in OpenStreetMap, and neither is one with the same leading digits.

        Then the street point counts, and the 150 m say what it is worth. The name keeps the
        address we were given: the label is more precise than the point.
        """
        photo = self._import(session, settings, sample_image, "Hauptstrasse/77 Timm/a.jpg")

        assert (photo.lat, photo.lon) == (53.6200, 9.6760)
        assert photo.place_name == "Hauptstrasse 77"
        assert photo.location_accuracy_m == place_service.ACCURACY_STREET_M

    def test_a_renumbered_house_number_lands_at_the_neighbour(
        self, session, settings, sample_image, place_index
    ):
        """The archive says "9", the place index knows only "9a" -- the same house, split up.

        Without this fallback 57 photos of the initial collection would lie on the street centre,
        38 of them at a single address. The name keeps the number we were given; only the point
        comes from the neighbour.
        """
        photo = self._import(session, settings, sample_image, "Hauptstrasse/9 Timm/a.jpg")

        assert (photo.lat, photo.lon) == (53.6205, 9.6765)
        assert photo.place_name == "Hauptstrasse 9"
        assert photo.location_accuracy_m == place_service.ACCURACY_ADDRESS_M

    def _with_gps(self, session, settings, sample_image, subpath: str):
        root = settings.data_dir / "archiv"
        target = root / subpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sample_image("foto_mit_gps.jpg").read_bytes())

        outcome = import_file(session, target, settings)
        assert outcome.photo is not None
        apply_folder_meta(session, outcome.photo, target, root, settings)
        return outcome.photo

    def test_the_folder_address_beats_the_exif_coordinate(
        self, session, settings, sample_image, place_index
    ):
        """The other way round than until August 2026 -- and the reason is measured.

        The old rule read as measurement against filing. In the Holm collection it is not that: 278
        of the 413 EXIF-located photos share their coordinate with another one, and at one point
        hang 20 photos from **four different days**. Six identical decimal places on four days is
        what no receiver delivers -- that is typed in, not measured. So one filing stands against
        another, and only one of them is anchored to the place index. 349 photos sat like that, up
        to 700 m away from the address their own folder named.
        """
        photo = self._with_gps(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert (photo.lat, photo.lon) == (53.6205, 9.6765)
        assert photo.place_name == "Hauptstrasse 14"
        assert photo.location_accuracy_m == place_service.ACCURACY_ADDRESS_M
        assert photo.location_source == "curator"

    def test_the_street_centre_does_not_beat_the_exif_coordinate(
        self, session, settings, sample_image, place_index
    ):
        """The failure case if the rule went too far.

        Without a house number only the street point remains, and at 150 m it is **coarser** than
        the measurement it would replace. In the initial collection that would hit 82 photos: they
        would become less precise, and nobody would see it.
        """
        photo = self._with_gps(session, settings, sample_image, "Hauptstrasse/a.jpg")

        assert photo.lat == pytest.approx(53.62053)
        assert photo.lon == pytest.approx(9.67601)
        assert photo.location_accuracy_m is None
        # Titling, naming and tagging by the folder is still allowed.
        assert photo.place_name == "Hauptstrasse"

    def test_a_statement_by_a_person_is_not_overwritten(
        self, session, settings, sample_image, place_index
    ):
        """Only the EXIF gives way. What a curator or a visitor said stays."""
        root = settings.data_dir / "archiv"
        target = root / "Hauptstrasse" / "14 Museum" / "a.jpg"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())

        outcome = import_file(session, target, settings)
        outcome.photo.lat, outcome.photo.lon = 53.5, 9.5
        outcome.photo.location_source = "visitor"
        apply_folder_meta(session, outcome.photo, target, root, settings)

        assert (outcome.photo.lat, outcome.photo.lon) == (53.5, 9.5)

    def test_the_street_stands_at_the_photo_as_its_name(
        self, session, settings, sample_image, place_index
    ):
        """The name carries the street without a number -- that is how the refinement finds it.

        A digit in the name would mean the house number is known, and the question would fall away.
        See ``open_filter("housenumber")`` in ``services/needs.py``.
        """
        photo = self._import(session, settings, sample_image, "Hauptstrasse/119.jpg")

        assert photo.place_name == "Hauptstrasse"
        assert not any(char.isdigit() for char in photo.place_name)

    def test_the_provenance_points_at_the_archive(
        self, session, settings, sample_image, place_index, monkeypatch
    ):
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        photo = self._import(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert photo.provenance == "Archiv, Verzeichnis 01 Orte/Hauptstrasse/14 Museum/a.jpg"

    def test_the_archive_path_is_added_to_what_the_file_says(
        self, session, settings, sample_image, place_index, monkeypatch
    ):
        """265 photos never got the path, because their file already named a provenance.

        Who lent a photo and where it lay in the archive are two answers to two questions. The
        first stands in the file, the second only in the path -- and the second can never be
        recovered from the image. Until 16 August 2026 this line filled only an empty field and
        left the path out in exactly the cases where somebody had already thought along.
        """
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        root = settings.data_dir / "archiv"
        target = root / "Hauptstrasse/14 Museum/a.jpg"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())
        photo = import_file(session, target, settings).photo
        photo.provenance = "Familie Wendt"

        apply_folder_meta(session, photo, target, root, settings)

        assert photo.provenance == (
            "Familie Wendt, Archiv, Verzeichnis 01 Orte/Hauptstrasse/14 Museum/a.jpg"
        )

    def test_without_a_configured_prefix_the_provenance_stays_empty(
        self, session, settings, sample_image, place_index
    ):
        """Nothing place-specific in the code: without the setting nothing is invented."""
        photo = self._import(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert photo.provenance is None

    def test_the_provenance_is_recorded_even_without_a_recognised_street(
        self, session, settings, sample_image, place_index, monkeypatch
    ):
        """Three photos of the initial collection had no provenance at all -- and no error with it.

        The provenance hangs on the path, not on the street. When none was recognised,
        ``apply_folder_meta`` bailed out earlier and took the provenance with it: two photos lay
        loose in the import root, one under an ambiguous street name. It is precisely there that
        the path is the only thing left of the filing.
        """
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        photo = self._import(session, settings, sample_image, "Irgendwas/lose.jpg")

        assert photo.place_name is None, "without a street it is still not located"
        assert photo.provenance == "Archiv, Verzeichnis 01 Orte/Irgendwas/lose.jpg"
