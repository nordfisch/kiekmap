"""Tests of the place index and the house numbers.

The core point: a street 800 m long gets one point. Without house numbers every photo of a street
lies on top of every other, and "this is where it was" is off by up to 400 m.

Two mistakes there happen silently:

  1. Addresses push the streets out of the hit list -- twelve slots are full after the house
     numbers of one Muehlenweg.
  2. House numbers are sorted alphabetically. Then the 10 comes before the 9.
"""

import pytest
from fastapi.testclient import TestClient

from app.models import Place
from app.services import places as place_service


@pytest.fixture
def place_index(session):
    """A section of Holm: two streets, one of them with house numbers."""

    def add(name, kind, lat=53.62, lon=9.676, street=None, housenumber=None):
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

    add("Muehlenweg", "strasse")
    add("Muehlenteich", "natur")
    add("Alte Muehlenstrasse", "strasse")
    # Deliberately in an order that would come out wrong alphabetically.
    for number in ("9", "10", "1a", "2", "1", "12"):
        add(f"Muehlenweg {number}", "adresse", street="Muehlenweg", housenumber=number)
    session.commit()
    return session


class TestFreeSearch:
    def test_addresses_do_not_push_out_the_streets(self, place_index):
        """The reason for the two steps.

        Without this rule the list would be full of the house numbers of the Muehlenweg -- and the
        Muehlenteich, which somebody may have meant, would no longer be in it.
        """
        hits = place_service.search(place_index, "muehlen")

        kinds = {place.kind for place in hits}
        assert "adresse" not in kinds
        assert {"Muehlenweg", "Muehlenteich", "Alte Muehlenstrasse"} <= {hit.name for hit in hits}

    def test_a_house_number_with_a_digit_is_found_directly(self, place_index):
        """Whoever knows the number types it."""
        hits = place_service.search(place_index, "muehlenweg 12")

        assert [place.name for place in hits] == ["Muehlenweg 12"]

    def test_a_street_still_comes_before_a_natural_feature(self, place_index):
        hits = place_service.search(place_index, "muehlen")

        assert hits[0].name == "Muehlenweg"

    def test_umlaut_tolerance_applies_to_addresses_too(self, session):
        session.add(
            Place(
                name="Mühlenweg 12",
                name_normalized=place_service.normalize("Mühlenweg 12"),
                lat=53.62,
                lon=9.676,
                kind="adresse",
                street="Mühlenweg",
                housenumber="12",
            )
        )
        session.commit()

        assert place_service.search(session, "muhlenweg 12")


class TestHouseNumbers:
    def test_are_sorted_naturally(self, place_index):
        """Alphabetically the 10 would come before the 9 and the 1a before the 2."""
        street = next(
            place
            for place in place_service.search(place_index, "muehlenweg")
            if place.kind == "strasse"
        )

        numbers = [place.housenumber for place in place_service.housenumbers(place_index, street)]

        assert numbers == ["1", "1a", "2", "9", "10", "12"]

    def test_the_sort_key_manages_without_a_number(self):
        # OSM occasionally holds nonsense in the field. A crash would be the worst answer.
        assert place_service.sort_key("ohne") == (0, "ohne")
        assert place_service.sort_key("") == (0, "")

    def test_a_street_without_house_numbers_stays_answerable(self, place_index):
        """Not every street is recorded in OpenStreetMap -- the step is then skipped."""
        other = next(
            place
            for place in place_service.search(place_index, "alte muehlen")
            if place.kind == "strasse"
        )

        assert place_service.housenumbers(place_index, other) == []


class TestStreetsOnOffer:
    """The streets the contribution panel offers as buttons.

    They replace the search field there -- without a keyboard it is the only control of the visitor
    view that accepts nothing.
    """

    @pytest.fixture
    def spread_out(self, session):
        """Two streets in the village, one in the next one seven kilometres away."""

        def add(name, lat, lon):
            session.add(
                Place(
                    name=name,
                    name_normalized=place_service.normalize(name),
                    lat=lat,
                    lon=lon,
                    kind="strasse",
                )
            )

        add("Zippelhornweg", 53.6205, 9.6762)
        add("Hauptstrasse", 53.6210, 9.6755)
        add("Ferner Deich", 53.5800, 9.7400)
        session.commit()
        return session

    def test_takes_the_ones_nearest_the_village(self, spread_out):
        chosen = place_service.nearby_streets(spread_out, (53.62053, 9.67601), limit=2)

        assert [place.name for place in chosen] == ["Hauptstrasse", "Zippelhornweg"]

    def test_returns_them_alphabetically_and_not_by_distance(self, spread_out):
        """The visitor looks for their street in the alphabet, not in a radius.

        Nearness decides only *which* streets are there at all.
        """
        chosen = place_service.nearby_streets(spread_out, (53.62053, 9.67601), limit=9)

        assert [place.name for place in chosen] == ["Ferner Deich", "Hauptstrasse", "Zippelhornweg"]

    def test_an_umlaut_sorts_like_its_base_letter(self, session):
        """Otherwise the Ölmühlenweg would stand behind the Z and get a button of its own.

        There is no such street in Holm -- at the second museum it would otherwise go unnoticed.
        """
        for name in ("Zwickauer Weg", "Ölmühlenweg", "Ostweg"):
            session.add(
                Place(
                    name=name,
                    name_normalized=place_service.normalize(name),
                    lat=53.62,
                    lon=9.676,
                    kind="strasse",
                )
            )
        session.commit()

        chosen = place_service.nearby_streets(session, (53.62, 9.676), limit=9)

        assert [place.name for place in chosen] == ["Ölmühlenweg", "Ostweg", "Zwickauer Weg"]

    def test_without_a_region_rather_empty_than_arbitrary(self, spread_out):
        """Without 'make tiles' there is no centre -- then no street is the nearest."""
        assert place_service.nearby_streets(spread_out, None, limit=9) == []


class TestThroughTheApi:
    def test_house_numbers_by_the_number_of_the_street(self, client: TestClient, place_index):
        street = place_service.search(place_index, "muehlenweg")[0]

        data = client.get(f"/api/places/{street.id}/housenumbers").json()

        assert [entry["housenumber"] for entry in data] == ["1", "1a", "2", "9", "10", "12"]

    def test_an_unknown_street(self, client: TestClient, place_index):
        response = client.get("/api/places/9999/housenumbers")

        assert response.status_code == 404

    def test_streets_on_offer(self, client: TestClient, place_index, settings):
        """'/streets' must not be read as a place id -- hence the order of the routes."""
        import json

        settings.region_file.write_text(
            json.dumps({"center": [9.676, 53.62], "streetChoice": 1}), encoding="utf-8"
        )

        data = client.get("/api/places/streets").json()

        assert [entry["name"] for entry in data] == ["Alte Muehlenstrasse"]
        assert data[0]["accuracy_m"] == place_service.ACCURACY_STREET_M

    def test_a_house_number_is_more_precise_than_the_street(self, client: TestClient, place_index):
        """The precision travels along -- the curator sees later what can be relied on."""
        street = client.get("/api/places", params={"q": "muehlenweg"}).json()[0]
        number = client.get("/api/places", params={"q": "muehlenweg 12"}).json()[0]

        assert street["accuracy_m"] == place_service.ACCURACY_STREET_M
        assert number["accuracy_m"] == place_service.ACCURACY_ADDRESS_M
        assert number["accuracy_m"] < street["accuracy_m"]


class TestLoading:
    def test_house_numbers_come_along_from_the_file(self, session, settings):
        import json

        settings.places_file.write_text(
            json.dumps(
                [
                    {"name": "Muehlenweg", "lat": 53.62, "lon": 9.676, "kind": "strasse"},
                    {
                        "name": "Muehlenweg 12",
                        "lat": 53.621,
                        "lon": 9.677,
                        "kind": "adresse",
                        "street": "Muehlenweg",
                        "housenumber": "12",
                    },
                ]
            ),
            encoding="utf-8",
        )

        count = place_service.load_from_file(session, settings.places_file)

        assert count == 2
        address = place_service.search(session, "muehlenweg 12")[0]
        assert (address.street, address.housenumber) == ("Muehlenweg", "12")


class TestStreetByItsName:
    """``street_named`` looks up exactly, without normalising.

    ``normalize()`` is meant for what somebody types. Here a value is looked up that was **copied**
    out of the place index into ``photo.place_name`` -- and the same string is the path on which a
    reverted refinement finds its street centre again.
    """

    def test_finds_the_street_under_its_stored_name(self, place_index):
        found = place_service.street_named(place_index, "Muehlenweg")

        assert found is not None
        assert found.kind == "strasse"

    def test_finds_no_address(self, place_index):
        # Otherwise a revert would land on a house number instead of the street centre.
        assert place_service.street_named(place_index, "Muehlenweg 12") is None

    def test_does_not_normalise(self, place_index):
        """A different spelling is a different street -- rather nothing than the wrong one."""
        assert place_service.street_named(place_index, "muehlenweg") is None


class TestAVanishedHouseNumber:
    """``address_near`` finds the house whose number has changed since the photo was taken.

    Nine addresses of the initial collection stand like that: the archive knows "Schulstrasse 2",
    the place index only "2a", because the house was split. That is machine work and no question
    for the kiosk -- where the former Schulstrasse 2 stood, a visitor knows as little as the place
    index does.
    """

    def test_finds_the_number_with_a_different_suffix(self, place_index):
        found = place_service.address_near(place_index, "Muehlenweg", "1")

        assert found is not None
        assert found.housenumber == "1"

    def test_takes_the_suffix_when_the_bare_number_is_missing(self, place_index):
        """The actual case: "1b" was asked for, the index holds only "1" and "1a"."""
        found = place_service.address_near(place_index, "Muehlenweg", "1b")

        assert found is not None
        # Walking along, the first one beginning with 1 -- "1" before "1a", see sort_key.
        assert found.housenumber == "1"

    def test_finds_nothing_when_the_number_does_not_occur_at_all(self, place_index):
        """The silent error if this boundary were missing.

        Schmidt-Isserstedt-Weg 4 lies in the place index between 2 and 8. If just any neighbour
        were taken here, the photo would sit on somebody else's house -- and then claim 15 m of
        precision, so it would not even be recognisable as imprecise any more.
        """
        assert place_service.address_near(place_index, "Muehlenweg", "7") is None

    def test_a_street_without_addresses_returns_nothing(self, place_index):
        assert place_service.address_near(place_index, "Alte Muehlenstrasse", "1") is None
