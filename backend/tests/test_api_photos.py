"""Tests of the query API.

The most important case stands in :class:`TestTimeFilter`: a photo dated "1920er" has to appear for
the selection 1925-1930. With a query for containment instead of overlap it drops out silently --
and with it most of a local history museum's collection.
"""

import pytest
from fastapi.testclient import TestClient

from app.models import DatePrecision, PhotoStatus

# Holm and its surroundings.
BBOX = "9.60,53.57,9.75,53.67"
BBOX_ELSEWHERE = "10.50,52.00,10.60,52.10"


class TestMapViewport:
    def test_a_photo_inside_the_viewport_appears(self, client: TestClient, session, make_photo):
        make_photo()
        session.commit()

        response = client.get("/api/photos", params={"bbox": BBOX})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["photos"][0]["title"] == "Test photo"

    def test_a_photo_outside_does_not_appear(self, client: TestClient, session, make_photo):
        make_photo()
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX_ELSEWHERE}).json()["total"] == 0

    def test_a_photo_without_a_place_never_appears(self, client: TestClient, session, make_photo):
        # It belongs in the contribution panel, not on the map.
        make_photo(lat=None, lon=None)
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX}).json()["total"] == 0

    def test_a_deleted_photo_does_not_appear(self, client: TestClient, session, make_photo):
        make_photo(status=PhotoStatus.DELETED)
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX}).json()["total"] == 0

    @pytest.mark.parametrize("bbox", ["9.6,53.5", "a,b,c,d", "9.75,53.67,9.60,53.57"])
    def test_an_unusable_bbox_is_rejected(self, client: TestClient, bbox):
        assert client.get("/api/photos", params={"bbox": bbox}).status_code == 422


class TestTimeFilter:
    def test_a_decade_appears_when_the_selection_starts_inside_it(
        self, client: TestClient, session, make_photo
    ):
        """The case that goes silently missing with a naive date query."""
        make_photo(year=1920, precision=DatePrecision.DECADE, title="1920er Jahre")
        session.commit()

        response = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1925, "to_year": 1930}
        )

        assert response.json()["total"] == 1, "1920er-Foto muss in 1925-1930 erscheinen"

    def test_a_decade_outside_does_not_appear(self, client: TestClient, session, make_photo):
        make_photo(year=1920, precision=DatePrecision.DECADE)
        session.commit()

        response = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1960}
        )
        assert response.json()["total"] == 0

    def test_an_exact_year_at_the_edge_of_the_selection(
        self, client: TestClient, session, make_photo
    ):
        make_photo(year=1932)
        session.commit()

        for start, end in ((1932, 1932), (1900, 1932), (1932, 2000)):
            response = client.get(
                "/api/photos", params={"bbox": BBOX, "from_year": start, "to_year": end}
            )
            assert response.json()["total"] == 1, f"{start}-{end} muss 1932 enthalten"

    def test_swapped_years_are_turned_around(self, client: TestClient, session, make_photo):
        make_photo(year=1932)
        session.commit()

        response = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1900}
        )
        assert response.json()["total"] == 1


class TestMarkerLabels:
    """What the map needs per photo in order to put the address and the year below it."""

    def test_a_marker_carries_the_address_and_the_short_date(
        self, client: TestClient, session, make_photo
    ):
        make_photo(year=2014, month=3, day=22, place_name="Lehmweg 17b")
        session.commit()

        marker = client.get("/api/photos", params={"bbox": BBOX}).json()["photos"][0]

        assert marker["place_name"] == "Lehmweg 17b"
        # The day does not belong under a thumbnail -- on the map the year is what counts.
        assert marker["date_short"] == "2014"
        # The written-out form stays beside it: it carries the label for screen readers, where
        # the precision does not get in the way.
        assert marker["date_label"] == "22. März 2014"

    def test_an_undated_photo_gets_an_empty_short_form(
        self, client: TestClient, session, make_photo
    ):
        make_photo(year=None, place_name="Im Sande 18")
        session.commit()

        marker = client.get("/api/photos", params={"bbox": BBOX}).json()["photos"][0]

        assert marker["date_short"] == ""
        assert marker["date_label"] == "Jahr unbekannt"


class TestUndatedPhotos:
    """Photos without a year are the third case, and whoever asks decides it.

    They overlap no time range, so they dropped out of every selection -- two thirds of this
    collection, silently. ``include_undated`` is therefore a switch of its own and not a side
    effect of where the slider stands.
    """

    def test_they_stay_in_the_time_selection_by_default(
        self, client: TestClient, session, make_photo
    ):
        # The normal case: whoever touches the slider should not lose three quarters of the map
        # without being told. That used to be exactly the effect.
        make_photo(year=None)
        session.commit()

        response = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1920, "to_year": 1930}
        )

        assert response.json()["total"] == 1

    def test_they_drop_out_when_the_switch_is_off(self, client: TestClient, session, make_photo):
        make_photo(year=None)
        session.commit()

        response = client.get(
            "/api/photos",
            params={"bbox": BBOX, "from_year": 1920, "to_year": 1930, "include_undated": False},
        )

        assert response.json()["total"] == 0

    def test_the_switch_works_without_a_time_selection_too(
        self, client: TestClient, session, make_photo
    ):
        """The position the slider is in when nobody has touched it.

        Across the whole axis the kiosk deliberately sends no time filter. If the switch only took
        hold together with one, it would do nothing at exactly the place where it starts.
        """
        make_photo(year=None, sha="a" * 64)
        make_photo(year=1932, sha="b" * 64)
        session.commit()

        response = client.get("/api/photos", params={"bbox": BBOX, "include_undated": False})

        assert response.json()["total"] == 1

    def test_dated_photos_stay_untouched_by_the_switch(
        self, client: TestClient, session, make_photo
    ):
        """The counter-check: the switch widens the selection, it does not replace it.

        If ``no date OR overlap`` had accidentally become just ``no date``, nothing dated would
        stand on the map any more -- and the test above would be happy with that.
        """
        make_photo(year=1932, sha="c" * 64)
        session.commit()

        inside = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1930, "to_year": 1935}
        )
        outside = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1950, "to_year": 1955}
        )

        assert inside.json()["total"] == 1
        assert outside.json()["total"] == 0

    def test_the_histogram_always_counts_them(self, client: TestClient, session, make_photo):
        """Otherwise the switch that brings them back would vanish along with the number.

        The label beside the slider reads „670 Fotos ohne Jahr anzeigen". If the histogram counted
        only the currently visible ones, a zero would stand there after switching off -- and the
        way back would be gone.
        """
        make_photo(year=None)
        session.commit()

        response = client.get(
            "/api/photos/histogram", params={"bbox": BBOX, "include_undated": False}
        )

        assert response.json()["undated"] == 1


class TestTheLimit:
    def test_the_limit_announces_itself(self, client: TestClient, session, make_photo):
        for number in range(5):
            make_photo(title=f"Photo {number}", sha=f"{number:064d}")
        session.commit()

        response = client.get("/api/photos", params={"bbox": BBOX, "limit": 2}).json()

        assert len(response["photos"]) == 2
        assert response["total"] == 5
        assert response["truncated"] is True, "die Karte soll zum Hineinzoomen auffordern koennen"

    def test_no_notice_without_a_limit(self, client: TestClient, session, make_photo):
        make_photo()
        session.commit()

        assert client.get("/api/photos", params={"bbox": BBOX}).json()["truncated"] is False


class TestOrder:
    def test_the_most_recently_edited_photo_comes_first(
        self, client: TestClient, session, make_photo
    ):
        """Photos at the same spot lie stacked -- the one just added on top.

        That is exactly where the map travels to after a visitor contribution.
        """
        from datetime import datetime

        older = make_photo(title="Lange her", sha="a" * 64)
        newer = make_photo(title="Eben bearbeitet", sha="b" * 64)
        session.commit()
        older.updated_at = datetime(2026, 1, 1, 12, 0)
        newer.updated_at = datetime(2026, 7, 31, 12, 0)
        session.commit()

        data = client.get("/api/photos", params={"bbox": BBOX}).json()

        assert [photo["title"] for photo in data["photos"]] == ["Eben bearbeitet", "Lange her"]


class TestHistogram:
    """The bars behind the time slider -- and how wide one bar is.

    The expensive error sits in the width, not in the counting: a photo dated "1920er" carries
    ``date_from = 1920-01-01``. With year bars all ten years would then land on the bar for 1920 --
    a single tall bar where in truth a whole decade lies.
    """

    def test_a_year_precise_collection_gets_year_bars(
        self, client: TestClient, session, make_photo
    ):
        for year in (2010, 2014, 2014, 2024):
            make_photo(year=year)
        session.commit()

        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert data["step"] == 1
        assert data["bars"] == [
            {"year": 2010, "count": 1},
            {"year": 2014, "count": 2},
            {"year": 2024, "count": 1},
        ]

    def test_one_decade_dating_coarsens_everything(self, client: TestClient, session, make_photo):
        """The most important test of this class.

        As soon as *one* photo is dated to a decade, year bars are a lie -- and a silent one: you
        would see a tall bar at 1920 and have no reason to doubt it.
        """
        make_photo(year=2010)
        make_photo(year=2014)
        make_photo(year=1920, precision="decade")
        session.commit()

        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert data["step"] == 10
        assert data["bars"] == [
            {"year": 1920, "count": 1},
            {"year": 2010, "count": 2},
        ]

    def test_a_long_span_gets_wider_bundles(self, client: TestClient, session, make_photo):
        """130 years in year bars would be too narrow to read.

        How wide exactly is decided by the rule in services/dates.py -- what counts here is that
        the span is no longer split into years and fits into thirty bars.
        """
        make_photo(year=1890)
        make_photo(year=2020)
        session.commit()

        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        span = data["collection_to"] - data["collection_from"]
        assert data["step"] > 1
        assert span / data["step"] <= 30

    def test_the_span_ignores_the_map_viewport(self, client: TestClient, session, make_photo):
        """The axis of the time slider belongs to the collection, not to the viewport.

        Otherwise the same position of the slider would mean a different year after every zoom --
        and a selection made earlier would lie outside its own track.
        """
        make_photo(year=1930)
        # Far away, outside the bbox being queried.
        make_photo(year=1890, lat=48.0, lon=11.0)
        session.commit()

        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert data["bars"] == [{"year": 1930, "count": 1}], "Balken zeigen den Ausschnitt"
        assert data["collection_from"] == 1890, "die Achse zeigt den ganzen Bestand"

    def test_the_width_belongs_to_the_collection_too(self, client: TestClient, session, make_photo):
        """Otherwise the meaning of the bars would change while panning the map.

        The decade photo lies outside the viewport and coarsens the display all the same -- just
        like the axis.
        """
        make_photo(year=2014)
        make_photo(year=1920, precision="decade", lat=48.0, lon=11.0)
        session.commit()

        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert data["step"] == 10

    def test_shows_what_lies_outside_the_selection_too(
        self, client: TestClient, session, make_photo
    ):
        """The slider should show where anything lies at all -- beyond the selection too."""
        make_photo(year=1923)
        make_photo(year=1980)
        session.commit()

        data = client.get(
            "/api/photos/histogram", params={"bbox": BBOX, "from_year": 1920, "to_year": 1930}
        ).json()

        assert len(data["bars"]) == 2

    def test_undated_photos_are_counted_separately(self, client: TestClient, session, make_photo):
        make_photo(year=None)
        make_photo(year=1932)
        session.commit()

        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert data["undated"] == 1
        assert data["bars"] == [{"year": 1932, "count": 1}]

    def test_an_empty_viewport(self, client: TestClient, session):
        data = client.get("/api/photos/histogram", params={"bbox": BBOX}).json()

        assert data == {
            "bars": [],
            "step": 1,
            "undated": 0,
            "collection_from": None,
            "collection_to": None,
        }


class TestASinglePhoto:
    def test_detail(self, client: TestClient, session, make_photo):
        photo = make_photo(year=1920, precision=DatePrecision.DECADE)
        session.commit()

        data = client.get(f"/api/photos/{photo.id}").json()

        assert data["date_label"] == "1920er"
        assert data["needs_date"] is False
        assert data["needs_location"] is False
        assert data["image_url"] == f"/api/photos/{photo.id}/image"

    def test_an_unknown_id(self, client: TestClient):
        response = client.get("/api/photos/9999")

        assert response.status_code == 404
        assert "9999" in response.json()["detail"]

    def test_a_wrong_thumbnail_size_names_the_right_ones(
        self, client: TestClient, session, make_photo
    ):
        photo = make_photo()
        session.commit()

        response = client.get(f"/api/photos/{photo.id}/thumb", params={"size": 999})

        assert response.status_code == 422
        assert "240" in response.json()["detail"]


class TestServingFiles:
    """Against really imported files rather than against invented rows."""

    @pytest.fixture
    def imported_photo(self, session, settings, sample_image):
        from app.services.importer import import_file

        outcome = import_file(session, sample_image("foto_mit_gps.jpg"), settings)
        session.commit()
        return outcome.photo

    def test_a_thumbnail_is_served(self, client: TestClient, imported_photo):
        response = client.get(f"/api/photos/{imported_photo.id}/thumb", params={"size": 240})

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/webp"
        assert response.content[:4] == b"RIFF"

    def test_a_thumbnail_may_be_cached_without_limit(self, client: TestClient, imported_photo):
        # The file name is the content hash: the same name guarantees the same content.
        response = client.get(f"/api/photos/{imported_photo.id}/thumb")

        assert "immutable" in response.headers["cache-control"]

    def test_the_original_is_served(self, client: TestClient, imported_photo):
        response = client.get(f"/api/photos/{imported_photo.id}/image")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content[:2] == b"\xff\xd8", "JPEG marker"

    def test_an_imported_photo_appears_on_the_map(self, client: TestClient, imported_photo):
        """The GPS test image lies in Holm and carries a capture date of 1975."""
        response = client.get(
            "/api/photos", params={"bbox": BBOX, "from_year": 1970, "to_year": 1980}
        ).json()

        assert response["total"] == 1
        assert response["photos"][0]["date_label"] == "21. Juni 1975"


class TestFileSuffix:
    """How the serving code knows what the file on disk is called -- point 61.

    The file name is the SHA-256 plus the suffix of the format. Which suffix belongs to which MIME
    type stands in ``ALLOWED_FORMATS`` -- and stood beside it a second time in ``api/photos.py``, as
    arithmetic on the string: ``mime.split("/")[-1]``, with ``jpeg`` and ``tiff`` bent back by hand.
    Both agreed as long as every suffix is the end of its MIME type.
    """

    def test_every_allowed_type_finds_its_suffix(self):
        """The counter-check that makes drifting apart impossible.

        It checks not a list of examples but the table against itself: whatever the import may file
        away, the serving code has to be able to name.
        """
        from app.services.storage import ALLOWED_FORMATS, suffix_for_mime

        for mime, suffix in ALLOWED_FORMATS.values():
            assert suffix_for_mime(mime) == suffix, f"{mime} findet seine Endung nicht"

    def test_an_unknown_type_yields_no_suffix(self):
        from app.services.storage import suffix_for_mime

        assert suffix_for_mime("image/heic") is None
        assert suffix_for_mime("") is None

    def test_a_photo_with_an_unknown_type_reports_the_missing_file(
        self, client: TestClient, session, make_photo
    ):
        """The import never creates such a thing -- a restored backup might.

        Before, that silently produced a path that does not exist. The answer has stayed the same,
        because it is right for the visitor; the log now says what it really was.
        """
        photo = make_photo()
        photo.mime = "image/heic"
        session.commit()

        response = client.get(f"/api/photos/{photo.id}/image")

        assert response.status_code == 404
        assert response.json()["detail"] == "Originaldatei fehlt"
