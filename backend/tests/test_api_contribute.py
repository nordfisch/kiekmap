"""Tests of the contribution panel.

The core point: contributions are taken over directly, but they may only fill what is empty.
Without that protection a visitor at the public touchscreen could overwrite a curated entry -- and
the next visitor the one before them.
"""

import json
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import Change, Photo, PhotoStatus, Place, Source
from app.services.needs import NEEDS
from app.services.places import normalize

# Holm
IN_HOLM = {"lat": 53.6205, "lon": 9.676}
WEIT_WEG = {"lat": 48.1372, "lon": 11.5756}  # München


class TestTheNextTask:
    def test_offers_a_photo_without_a_place(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, title="Ohne Ort", sha="a" * 64)
        make_photo(title="Vollstaendig", sha="b" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["photo"]["title"] == "Ohne Ort"
        assert daten["open_count"] == 1
        assert daten["photo"]["needs_location"] is True

    def test_offers_a_photo_without_a_year(self, client: TestClient, session, make_photo):
        make_photo(year=None, title="Ohne Jahr", sha="a" * 64)
        make_photo(year=1932, title="Datiert", sha="b" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "date"}).json()

        assert daten["photo"]["title"] == "Ohne Jahr"
        assert daten["photo"]["date_label"] == "Jahr unbekannt"

    def test_a_skipped_photo_does_not_come_straight_back(
        self, client: TestClient, session, make_photo
    ):
        erst = make_photo(lat=None, lon=None, title="A", sha="a" * 64)
        make_photo(lat=None, lon=None, title="B", sha="b" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "location", "exclude": str(erst.id)}
        ).json()

        assert daten["photo"]["title"] == "B"

    def test_starts_over_when_everything_has_been_seen(
        self, client: TestClient, session, make_photo
    ):
        """Better to repeat than to report "nothing left" while something is still open."""
        photo = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "location", "exclude": str(photo.id)}
        ).json()

        assert daten["photo"]["id"] == photo.id

    def test_nothing_open(self, client: TestClient, session, make_photo):
        make_photo(sha="a" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["photo"] is None
        assert daten["open_count"] == 0

    def test_a_deleted_photo_is_not_offered(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, status=PhotoStatus.DELETED, sha="a" * 64)
        session.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "location"}).json()["photo"] is None
        )


class TestOneDefinitionPerQuestion:
    """The SQL query and the property on the photo have to say the same thing.

    They were once two separate formulations: ``_missing_filter`` in the endpoint and
    ``needs_location`` on the model. Each looked right on its own -- and exactly such a pair drifts
    apart without anyone noticing. The count in the panel then no longer matched the photos it
    offers.
    """

    def test_the_open_count_counts_exactly_the_photos_the_property_reports(
        self, client: TestClient, session, make_photo
    ):
        make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(lat=None, lon=None, year=None, sha="b" * 64)
        make_photo(sha="c" * 64)
        make_photo(year=None, sha="d" * 64)
        make_photo(lat=None, lon=None, status=PhotoStatus.DELETED, sha="e" * 64)
        session.commit()

        photos = session.scalars(select(Photo).where(Photo.status == PhotoStatus.PUBLISHED)).all()

        for question, property_name in (("location", "needs_location"), ("date", "needs_date")):
            reported = client.get("/api/contribute/next", params={"need": question}).json()
            expected = sum(1 for photo in photos if getattr(photo, property_name))
            assert reported["open_count"] == expected, question


class TestARequestedPhoto:
    """``photo_id`` offers a named photo -- the way from the detail view into the panel.

    A wish, not an instruction: it is checked against the same condition as any other photo, and
    where it does not hold, the ordinary random choice runs.
    """

    def test_offers_the_requested_photo(self, client: TestClient, session, make_photo):
        requested = make_photo(year=None, title="Das hier", sha="a" * 64)
        for buchstabe in "bcdefghij":
            make_photo(year=None, title="Irgendeins", sha=buchstabe * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "date", "photo_id": requested.id}
        ).json()

        assert daten["photo"]["title"] == "Das hier"

    def test_falls_back_when_the_photo_needs_nothing_more(
        self, client: TestClient, session, make_photo
    ):
        """The silent error this check prevents.

        Between the tap in the detail view and this request somebody else may have answered.
        Without the check a question would stand on the screen that is already answered -- and the
        write path would reject the answer with a 409, which sounds as though the visitor had been
        too slow.
        """
        datiert = make_photo(year=1932, title="Schon datiert", sha="a" * 64)
        make_photo(year=None, title="Braucht noch", sha="b" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "date", "photo_id": datiert.id}
        ).json()

        assert daten["photo"]["title"] == "Braucht noch"

    def test_overrides_the_skip_list(self, client: TestClient, session, make_photo):
        """Whoever calls up a photo explicitly may well have swiped it away before."""
        requested = make_photo(year=None, title="Doch nochmal", sha="a" * 64)
        make_photo(year=None, title="Anderes", sha="b" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next",
            params={"need": "date", "photo_id": requested.id, "exclude": str(requested.id)},
        ).json()

        assert daten["photo"]["title"] == "Doch nochmal"

    def test_still_counts_every_open_one(self, client: TestClient, session, make_photo):
        """The count means the collection, not the one photo -- otherwise it would read 1."""
        requested = make_photo(year=None, sha="a" * 64)
        make_photo(year=None, sha="b" * 64)
        make_photo(year=None, sha="c" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "date", "photo_id": requested.id}
        ).json()

        assert daten["open_count"] == 3

    def test_an_unknown_photo_still_yields_a_task(self, client: TestClient, session, make_photo):
        make_photo(year=None, title="Da", sha="a" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "date", "photo_id": 999999}
        ).json()

        assert daten["photo"]["title"] == "Da"


class TestTheRanking:
    """The order in ``NEEDS`` is the ranking, and it is recorded only here.

    Without this test the order could be swapped without a single backend test failing -- verified
    on 11 August 2026, when it actually was swapped. The only thing that noticed was a test in the
    frontend, where the same list stands a second time.
    """

    def test_the_place_comes_before_everything_else(self):
        """A photo that stands on no map is the most expensive gap."""
        assert NEEDS[0] == "location"

    def test_the_house_number_comes_before_the_year(self):
        """Decided from a number, not from a feeling.

        A year is worth more than a house number -- and is still asked for later. A question is only
        reached once the one before it is **empty**, and in the initial collection 673 undated
        photos stand against 71 that could be refined. Behind the year the third question would
        never have been reached: the panel would carry a question nobody is ever asked.
        """
        assert NEEDS.index("housenumber") < NEEDS.index("date")


@pytest.fixture
def streets(session):
    """Two streets, only one of them with addresses -- the difference carries a whole test."""

    def create_place(name, kind, street=None, housenumber=None):
        session.add(
            Place(
                name=name,
                name_normalized=normalize(name),
                lat=53.62,
                lon=9.676,
                kind=kind,
                street=street,
                housenumber=housenumber,
            )
        )

    create_place("Am Kamp", "strasse")
    for number in ("1", "2", "3"):
        create_place(f"Am Kamp {number}", "adresse", street="Am Kamp", housenumber=number)
    # A street without a single address -- the place index holds 141 of 486 such.
    create_place("Feldweg", "strasse")
    create_place("Strasse des 17. Juni", "strasse")
    create_place(
        "Strasse des 17. Juni 4", "adresse", street="Strasse des 17. Juni", housenumber="4"
    )
    session.commit()
    return session


class TestRefining:
    """Who gets asked for the house number.

    The panel used to ask only about what is *missing*. A photo on the middle of an 800 m street
    counted as located and never came back -- and yet that is the case where somebody who walks
    past it every day could name the house."""

    def _street_accurate(self, make_photo, **felder):
        return make_photo(
            place_name="Am Kamp",
            accuracy=150,
            location_source=Source.VISITOR,
            **felder,
        )

    def test_a_street_accurate_photo_without_a_house_number_is_offered(
        self, client: TestClient, streets, make_photo
    ):
        self._street_accurate(make_photo, title="Nur die Strasse", sha="a" * 64)
        streets.commit()

        daten = client.get("/api/contribute/next", params={"need": "housenumber"}).json()

        assert daten["photo"]["title"] == "Nur die Strasse"
        assert daten["open_count"] == 1

    def test_a_photo_with_a_house_number_in_its_name_is_not_offered(
        self, client: TestClient, streets, make_photo
    ):
        """The 58 from the initial collection: the number is known, only its coordinate is missing.

        It is not in the place index because the house was split up or renumbered. A choice of
        numbers would offer plenty of numbers here -- just not the one wanted. That is work for the
        machine, not a question for a visitor (see point 41).
        """
        make_photo(place_name="Am Kamp 11a", accuracy=150, sha="b" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_a_house_accurate_photo_is_not_offered(self, client: TestClient, streets, make_photo):
        """This photo differs from a refinable one **only** in its precision.

        The obvious setup -- a house name at 15 m -- would not check the precision at all: the
        photo would already drop out on the digit rule. A building name would drop out on the
        address condition. Both were exposed by the counter-check that removed the precision
        condition and left everything green. That is why the bare street name at 15 m stands here:
        this way the precision alone keeps the photo out of the question.

        The case arises when a curator sets the coordinate precisely by hand and leaves the street
        name standing."""
        make_photo(place_name="Am Kamp", accuracy=15, sha="c" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_a_photo_without_a_street_name_is_not_offered(
        self, client: TestClient, streets, make_photo
    ):
        """Without a street there would be no numbers to offer at all.

        Until 16 August 2026 this test was called ``..._aus_dem_exif_...`` and claimed to cover the
        EXIF case -- but its photo had no street name at all and dropped out on this condition
        already. **A test whose name says something other than its setup covers a gap instead of
        closing it:** the EXIF case stood unchecked for two weeks, and point 53 came out of it. It
        now has a test of its own, immediately below.
        """
        make_photo(place_name=None, accuracy=None, sha="d" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_a_photo_with_a_street_and_an_exif_coordinate_is_offered(
        self, client: TestClient, streets, make_photo
    ):
        """The case that led to point 53 -- 53 photos of the initial collection.

        They carry a street name from the archive folder and a coordinate from their EXIF, so **no**
        precision at all. Until 16 August 2026 the condition explicitly demanded 150 m and thereby
        left them out. The reason given was that the device knows where the photographer stood -- an
        assumption that had been refuted four days earlier: 278 of 413 EXIF coordinates of the
        initial collection were shared by two photos, so they are typed-in values and not
        measurements (decisions.md, point 34).

        It surfaced as something else: in the detail view the button seemed to be missing as soon
        as the year was known. That was a confusion of cause and company -- among the photos with a
        bare street name, those with a year are predominantly the ones from the EXIF.
        """
        make_photo(place_name="Am Kamp", accuracy=None, location_source=Source.EXIF, sha="f" * 64)
        streets.commit()

        daten = client.get("/api/contribute/next", params={"need": "housenumber"}).json()

        assert daten["open_count"] == 1

    def test_a_photo_without_a_coordinate_is_not_offered(
        self, client: TestClient, streets, make_photo
    ):
        """A photo without a place owes its answer to the **first** question, not this one.

        In the detail view all three buttons stand side by side; without this condition the
        question about the place and the question about the house number would stand there at once
        and ask for the same photo to be located twice."""
        make_photo(place_name="Am Kamp", lat=None, lon=None, accuracy=None, sha="g" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_a_street_without_addresses_is_not_offered(
        self, client: TestClient, streets, make_photo
    ):
        """The silent error: a question on the screen with not a single button under it.

        141 of the 486 streets in the place index hold not one address. Without this condition the
        visitor would face the house-number question with nothing to tap.
        """
        make_photo(place_name="Feldweg", accuracy=150, sha="e" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_a_curator_entry_is_offered_as_well(self, client: TestClient, streets, make_photo):
        """Decided deliberately: a resident often knows the house better than the archive does.

        That softens the rule from decisions.md point 5 -- which is why a revert restores the old
        source instead of silently turning curator knowledge into a visitor contribution.
        """
        make_photo(place_name="Am Kamp", accuracy=150, location_source=Source.CURATOR, sha="f" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 1
        )

    def test_a_street_with_a_digit_in_its_name_is_not_offered(
        self, client: TestClient, streets, make_photo
    ):
        """The digit rule is wrong here -- and it is wrong in the harmless direction.

        A street named after a date carries a digit without that being a house number. The photo is
        therefore not asked about, although it could be. Better one question too few than a choice
        of numbers in front of somebody whose number has long been settled."""
        make_photo(place_name="Strasse des 17. Juni", accuracy=150, sha="g" * 64)
        streets.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_the_other_count_counts_every_remaining_question(
        self, client: TestClient, streets, make_photo
    ):
        """``open_other`` decides whether the "I do not know" button still leads anywhere.

        With three questions it has to add up all the remaining ones. If it counted only one, the
        button would vanish although something is still open.
        """
        make_photo(lat=None, lon=None, sha="h" * 64)
        make_photo(year=None, sha="i" * 64)
        streets.commit()

        daten = client.get("/api/contribute/next", params={"need": "housenumber"}).json()

        assert daten["open_other"] == 2


class TestTheNumbersForAPhoto:
    """What the endpoint offers -- and when it deliberately offers nothing.

    The empty list is the gate: the detail view shows the choice when something stands here, and
    needs no rule of its own. A rule in two places is a rule that eventually contradicts itself.
    """

    def test_returns_the_numbers_of_the_photos_street(
        self, client: TestClient, streets, make_photo
    ):
        photo = make_photo(place_name="Am Kamp", accuracy=150, sha="a" * 64)
        streets.commit()

        numbers = client.get(f"/api/contribute/{photo.id}/housenumbers").json()

        assert [entry["housenumber"] for entry in numbers] == ["1", "2", "3"]
        assert all(entry["accuracy_m"] == 15 for entry in numbers)

    def test_returns_nothing_for_an_already_house_accurate_photo(
        self, client: TestClient, streets, make_photo
    ):
        # Otherwise the detail view would get buttons for a question that is none.
        photo = make_photo(place_name="Am Kamp", accuracy=15, sha="b" * 64)
        streets.commit()

        assert client.get(f"/api/contribute/{photo.id}/housenumbers").json() == []

    def test_returns_nothing_for_a_street_without_addresses(
        self, client: TestClient, streets, make_photo
    ):
        photo = make_photo(place_name="Feldweg", accuracy=150, sha="c" * 64)
        streets.commit()

        assert client.get(f"/api/contribute/{photo.id}/housenumbers").json() == []

    def test_an_unknown_photo(self, client: TestClient, streets):
        assert client.get("/api/contribute/999/housenumbers").status_code == 404


class TestRefiningToAHouseNumber:
    """The exception to "visitors fill only what is empty" -- and why it has a door of its own.

    The endpoint accepts **no coordinate**, only a number from the place index. At ``/location``
    the precision claimed by the client is harmless, *because* the field has to be empty anyway.
    The moment it decided what may be overwritten, it would be a key -- and the client holds it."""

    def _photo(self, make_photo, **felder):
        return make_photo(place_name="Am Kamp", accuracy=150, sha="a" * 64, **felder)

    def _number(self, session, housenumber="2"):
        return session.scalar(
            select(Place).where(Place.kind == "adresse", Place.housenumber == housenumber)
        )

    def test_refines_the_street_to_the_house_number(self, client: TestClient, streets, make_photo):
        photo = self._photo(make_photo)
        streets.commit()
        number = self._number(streets)

        response = client.post(
            f"/api/contribute/{photo.id}/housenumber", json={"place_id": number.id}
        )

        assert response.status_code == 200
        assert response.json()["place_name"] == "Am Kamp 2"
        assert response.json()["location_accuracy_m"] == 15

    def test_takes_the_coordinate_and_the_precision_from_the_place_index(
        self, client: TestClient, streets, make_photo
    ):
        """The attack case: the client determines nothing.

        Additional fields in the body are not read -- coordinate and precision come from the row
        the server looks up. If it were otherwise, a call with ``accuracy_m: 1`` could replace any
        entry.
        """
        photo = self._photo(make_photo)
        streets.commit()
        number = self._number(streets)

        client.post(
            f"/api/contribute/{photo.id}/housenumber",
            json={"place_id": number.id, "lat": 48.13, "lon": 11.57, "accuracy_m": 1},
        )
        streets.refresh(photo)

        assert (photo.lat, photo.lon) == (number.lat, number.lon)
        assert photo.location_accuracy_m == 15

    def test_is_logged_with_the_street_as_the_old_value(
        self, client: TestClient, streets, make_photo
    ):
        # The old value is at the same time the key with which a revert finds the street centre
        # again -- on the other two paths it is rightly empty.
        photo = self._photo(make_photo, location_source=Source.CURATOR)
        streets.commit()
        number = self._number(streets)

        client.post(f"/api/contribute/{photo.id}/housenumber", json={"place_id": number.id})

        entry = streets.scalar(select(Change).where(Change.field == "housenumber"))
        assert entry.old_value == "Am Kamp"
        assert entry.new_value == "Am Kamp 2"
        assert entry.old_source == Source.CURATOR

    def test_a_house_number_of_another_street_is_rejected(
        self, client: TestClient, streets, make_photo
    ):
        photo = self._photo(make_photo)
        streets.commit()
        fremd = streets.scalar(
            select(Place).where(Place.kind == "adresse", Place.street == "Strasse des 17. Juni")
        )

        response = client.post(
            f"/api/contribute/{photo.id}/housenumber", json={"place_id": fremd.id}
        )

        assert response.status_code == 422

    def test_a_street_is_not_a_house_number(self, client: TestClient, streets, make_photo):
        photo = self._photo(make_photo)
        streets.commit()
        street_place = streets.scalar(select(Place).where(Place.name == "Am Kamp"))

        response = client.post(
            f"/api/contribute/{photo.id}/housenumber", json={"place_id": street_place.id}
        )

        assert response.status_code == 404

    def test_an_already_house_accurate_photo_is_not_overwritten(
        self, client: TestClient, streets, make_photo
    ):
        photo = make_photo(place_name="Am Kamp 1", accuracy=15, sha="b" * 64)
        streets.commit()
        number = self._number(streets)

        response = client.post(
            f"/api/contribute/{photo.id}/housenumber", json={"place_id": number.id}
        )

        assert response.status_code == 409
        streets.refresh(photo)
        assert photo.place_name == "Am Kamp 1"

    def test_an_unlocated_photo_is_not_refined(self, client: TestClient, streets, make_photo):
        # It belongs in the first question, not here -- and has no street the number
        # passen koennte.
        photo = make_photo(lat=None, lon=None, place_name=None, sha="c" * 64)
        streets.commit()
        number = self._number(streets)

        response = client.post(
            f"/api/contribute/{photo.id}/housenumber", json={"place_id": number.id}
        )

        assert response.status_code == 409

    def test_a_second_visitor_cannot_replace_the_house_number(
        self, client: TestClient, streets, make_photo
    ):
        """The rule that a more precise entry may replace a less precise one, never the other way
        round -- in the direction that hurts.

        Without it the second visitor would overwrite the first, and that is exactly why
        contributions may go through without moderation at all."""
        photo = self._photo(make_photo)
        streets.commit()
        erste = self._number(streets, "1")
        zweite = self._number(streets, "3")

        client.post(f"/api/contribute/{photo.id}/housenumber", json={"place_id": erste.id})
        response = client.post(
            f"/api/contribute/{photo.id}/housenumber", json={"place_id": zweite.id}
        )

        assert response.status_code == 409
        streets.refresh(photo)
        assert photo.place_name == "Am Kamp 1"


class TestAddingAPlace:
    def test_takes_it_at_once(self, client: TestClient, session, make_photo):
        photo = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        response = client.post(
            f"/api/contribute/{photo.id}/location",
            json={**IN_HOLM, "place_name": "Mühlenweg"},
        )

        assert response.status_code == 200
        daten = response.json()
        assert daten["needs_location"] is False
        assert daten["place_name"] == "Mühlenweg"
        assert daten["location_source"] == Source.VISITOR

    def test_appears_on_the_map_afterwards(self, client: TestClient, session, make_photo):
        photo = make_photo(lat=None, lon=None, year=1932, sha="a" * 64)
        session.commit()
        assert (
            client.get("/api/photos", params={"bbox": "9.60,53.57,9.75,53.67"}).json()["total"] == 0
        )

        client.post(f"/api/contribute/{photo.id}/location", json=IN_HOLM)

        # The immediate effect is what makes it appealing to the visitor:
        # "mein Wissen ist jetzt auf der Karte".
        assert (
            client.get("/api/photos", params={"bbox": "9.60,53.57,9.75,53.67"}).json()["total"] == 1
        )

    def test_is_logged(self, client: TestClient, session, make_photo):
        photo = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{photo.id}/location", json={**IN_HOLM, "session_id": "abc"})

        entry = session.scalars(select(Change).where(Change.photo_id == photo.id)).one()
        assert entry.field == "location"
        assert entry.source == Source.VISITOR
        assert entry.session_id == "abc"
        assert "53.62" in entry.new_value

    def test_a_filled_field_is_not_overwritten(self, client: TestClient, session, make_photo):
        """What a curator has set is untouchable -- and the second visitor must not overwrite the
        first."""
        photo = make_photo(lat=53.61, lon=9.66, sha="a" * 64)
        session.commit()

        response = client.post(f"/api/contribute/{photo.id}/location", json=IN_HOLM)

        assert response.status_code == 409
        session.refresh(photo)
        assert photo.lat == 53.61
        # The message should not treat the visitor as a nuisance.
        assert "Dank" in response.json()["detail"]

    def test_a_place_outside_the_region(self, client: TestClient, session, settings, make_photo):
        (settings.data_dir / "region.json").write_text(
            json.dumps({"bbox": [9.60028, 53.57561, 9.75174, 53.66545]}), encoding="utf-8"
        )
        photo = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        response = client.post(f"/api/contribute/{photo.id}/location", json=WEIT_WEG)

        assert response.status_code == 422
        assert "ausserhalb" in response.json()["detail"].lower()

    def test_without_a_configured_region_nothing_is_checked(
        self, client: TestClient, session, make_photo
    ):
        # No region.json present: then rather accept than refuse without reason.
        photo = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        assert client.post(f"/api/contribute/{photo.id}/location", json=WEIT_WEG).status_code == 200

    def test_an_unknown_photo(self, client: TestClient):
        assert client.post("/api/contribute/9999/location", json=IN_HOLM).status_code == 404


class TestAddingAYear:
    def test_a_year_entry(self, client: TestClient, session, make_photo):
        photo = make_photo(year=None, sha="a" * 64)
        session.commit()

        daten = client.post(
            f"/api/contribute/{photo.id}/date", json={"year": 1932, "precision": "year"}
        ).json()

        assert daten["date_label"] == "1932"
        assert daten["needs_date"] is False
        assert daten["date_source"] == Source.VISITOR

    def test_a_decade_becomes_an_interval(self, client: TestClient, session, make_photo):
        """ "Irgendwann in den Zwanzigern" is the most frequent honest answer."""
        photo = make_photo(year=None, sha="a" * 64)
        session.commit()

        daten = client.post(
            f"/api/contribute/{photo.id}/date", json={"year": 1924, "precision": "decade"}
        ).json()

        assert daten["date_label"] == "1920er"
        assert daten["date_from"] == "1920-01-01"
        assert daten["date_to"] == "1929-12-31"

    def test_a_photo_dated_that_way_appears_for_an_overlapping_selection(
        self, client, session, make_photo
    ):
        photo = make_photo(year=None, sha="a" * 64)
        session.commit()
        client.post(f"/api/contribute/{photo.id}/date", json={"year": 1924, "precision": "decade"})

        response = client.get(
            "/api/photos",
            params={"bbox": "9.60,53.57,9.75,53.67", "from_year": 1925, "to_year": 1930},
        )

        assert response.json()["total"] == 1

    def test_an_already_dated_photo(self, client: TestClient, session, make_photo):
        photo = make_photo(year=1932, sha="a" * 64)
        session.commit()

        response = client.post(
            f"/api/contribute/{photo.id}/date", json={"year": 1800, "precision": "year"}
        )

        assert response.status_code == 409
        session.refresh(photo)
        assert photo.date_from == date(1932, 1, 1)

    def test_a_nonsensical_year_is_rejected(self, client: TestClient, session, make_photo):
        photo = make_photo(year=None, sha="a" * 64)
        session.commit()

        assert (
            client.post(
                f"/api/contribute/{photo.id}/date", json={"year": 3000, "precision": "year"}
            ).status_code
            == 422
        )

    def test_is_logged(self, client: TestClient, session, make_photo):
        photo = make_photo(year=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{photo.id}/date", json={"year": 1924, "precision": "decade"})

        entry = session.scalars(select(Change).where(Change.field == "date")).one()
        assert entry.new_value == "1920er"
        assert entry.source == Source.VISITOR


class TestTheTwoTogether:
    def test_filling_both_gaps_one_after_the_other(self, client: TestClient, session, make_photo):
        photo = make_photo(lat=None, lon=None, year=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{photo.id}/location", json=IN_HOLM)
        client.post(f"/api/contribute/{photo.id}/date", json={"year": 1955, "precision": "year"})

        daten = client.get(f"/api/photos/{photo.id}").json()
        assert daten["needs_location"] is False
        assert daten["needs_date"] is False
        assert len(session.scalars(select(Change)).all()) == 2

    def test_the_open_count_goes_down(self, client: TestClient, session, make_photo):
        photo = make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(lat=None, lon=None, sha="b" * 64)
        session.commit()

        assert client.get("/api/contribute/next?need=location").json()["open_count"] == 2
        client.post(f"/api/contribute/{photo.id}/location", json=IN_HOLM)
        assert client.get("/api/contribute/next?need=location").json()["open_count"] == 1


class TestPlaceSearch:
    def _create_places(self, session):
        from app.models import Place
        from app.services.places import normalize

        for name, art, lat, lon in [
            ("Mühlenweg", "strasse", 53.62, 9.67),
            ("Alte Mühlenstraße", "strasse", 53.63, 9.68),
            ("Mühlenteich", "natur", 53.61, 9.66),
            ("Hauptstraße", "strasse", 53.64, 9.67),
        ]:
            session.add(
                Place(name=name, name_normalized=normalize(name), lat=lat, lon=lon, kind=art)
            )
        session.commit()

    def test_finds_it_despite_a_missing_umlaut(self, client: TestClient, session):
        self._create_places(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "muhlen"}).json()]

        assert "Mühlenweg" in namen

    def test_a_word_beginning_comes_first(self, client: TestClient, session):
        """Whoever types "Muhl" means the Mühlenweg, not the Alte Mühlenstraße."""
        self._create_places(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "muhl"}).json()]

        assert namen[0] == "Mühlenweg"
        assert "Alte Mühlenstraße" in namen

    def test_the_sharp_s(self, client: TestClient, session):
        self._create_places(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "hauptstrasse"}).json()]

        assert namen == ["Hauptstraße"]

    def test_too_short_an_input_returns_nothing(self, client: TestClient, session):
        self._create_places(session)

        assert client.get("/api/places", params={"q": "m"}).json() == []
        assert client.get("/api/places").json() == []


class TestLoadingThePlaceIndex:
    def test_from_a_file(self, session, settings):
        from app.services.places import load_from_file

        settings.places_file.write_text(
            json.dumps(
                [
                    {
                        "name": "Süderstraße",
                        "name_normalized": "veraltet",
                        "lat": 53.6,
                        "lon": 9.6,
                        "kind": "strasse",
                    }
                ]
            ),
            encoding="utf-8",
        )

        count = load_from_file(session, settings.places_file)

        assert count == 1
        from app.models import Place

        place = session.scalars(select(Place)).one()
        # The normalisation is recomputed: an older file would otherwise leave the search
        # stillschweigend leer laufen lassen.
        assert place.name_normalized == "suderstrasse"

    def test_a_missing_file_is_not_an_error(self, session, settings):
        from app.services.places import load_from_file

        assert load_from_file(session, settings.data_dir / "gibtsnicht.json") == 0


class TestTheLastTask:
    def test_counts_the_other_question_too(self, client: TestClient, session, make_photo):
        """On this hangs whether the "I do not know" button still leads anywhere at all.

        If nothing else is open, the same photo would come back -- then the button had better not
        be there.
        """
        make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(year=None, sha="b" * 64)
        make_photo(year=None, sha="c" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["open_count"] == 1, "ein Foto ohne Ort"
        assert daten["open_other"] == 2, "zwei ohne Jahr"

    def test_the_last_task_has_nothing_beside_it(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["open_count"] == 1
        assert daten["open_other"] == 0
