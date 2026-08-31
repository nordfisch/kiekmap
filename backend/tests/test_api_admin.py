"""Tests of the admin view.

Two promises carry this area, and both break silently when they break:

  1. When editing, a *missing* field means "leave unchanged" and an *empty* field means "delete".
     Without that difference a wrong dating could never be taken out again.
  2. Uploaded photos are in the database at once, not only after "Uebernehmen". A closed browser
     must not cost uploads."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import (
    Change,
    DatePrecision,
    ImportLog,
    ImportResult,
    Photo,
    PhotoStatus,
    Place,
    Source,
)
from app.services.places import normalize

HOLM = {"lat": 53.6205, "lon": 9.676}


def _image(fixtures_dir, name: str = "scan_ohne_exif.jpg") -> bytes:
    return (fixtures_dir / name).read_bytes()


class TestSigningIn:
    def test_no_access_without_a_token(self, client: TestClient):
        assert client.get("/api/admin/overview").status_code == 401

    def test_ausgedachtes_token_kein_zugang(self, client: TestClient):
        response = client.get("/api/admin/overview", headers={"X-Admin-Token": "ausgedacht"})

        assert response.status_code == 401

    def test_without_a_configured_pin_the_device_says_so_plainly(
        self, client: TestClient, settings
    ):
        """An empty admin_pin_hash must not pass for "any PIN will do"."""
        settings.admin_pin_hash = ""

        response = client.post("/api/admin/login", json={"pin": "4711"})

        assert response.status_code == 503
        assert "app.cli pin" in response.json()["detail"]

    def test_a_wrong_pin(self, client: TestClient, admin_pin):
        response = client.post("/api/admin/login", json={"pin": "0000"})

        assert response.status_code == 401

    def test_too_many_attempts_lock_the_keypad(self, client: TestClient, admin_pin):
        """The actual protection of a four-digit PIN."""
        for _ in range(5):
            client.post("/api/admin/login", json={"pin": "0000"})

        # Even the right PIN no longer gets through now.
        response = client.post("/api/admin/login", json={"pin": admin_pin})

        assert response.status_code == 429
        assert "Sekunden" in response.json()["detail"]

    def test_richtige_pin_gibt_ein_token(self, client: TestClient, admin_pin):
        response = client.post("/api/admin/login", json={"pin": admin_pin})

        assert response.status_code == 200
        assert response.json()["token"]
        assert response.json()["expires_in_s"] > 0

    def test_signing_out_ends_the_session(self, admin_client: TestClient):
        assert admin_client.post("/api/admin/logout").status_code == 204

        assert admin_client.get("/api/admin/overview").status_code == 401

    def test_the_session_survives_a_page_reload(self, admin_client: TestClient):
        """So that an accidental reload does not demand the PIN all over again."""
        response = admin_client.get("/api/admin/session")

        assert response.status_code == 200
        assert response.json()["expires_in_s"] > 0


class TestTheOverview:
    def test_counts_what_is_missing(self, admin_client: TestClient, session, make_photo):
        make_photo(sha="a" * 64)
        make_photo(lat=None, lon=None, sha="b" * 64)
        make_photo(year=None, sha="c" * 64)
        make_photo(status=PhotoStatus.DELETED, sha="d" * 64)
        session.commit()

        data = admin_client.get("/api/admin/overview").json()

        # What is deleted no longer belongs to the collection: three of four photos, not four.
        assert data["total"] == 3
        assert data["without_location"] == 1
        assert data["without_date"] == 1
        # On the map: with a place and not deleted. The photo without a year counts too.
        assert data["on_map"] == 2
        assert data["deleted"] == 1

    def test_a_photo_without_a_year_stands_on_the_map(
        self, admin_client: TestClient, session, make_photo
    ):
        """Undated is not invisible -- the normal case is the map without a time filter.

        With the slider across the whole axis the kiosk sends no time filter at all, and
        ``_viewport_filters`` then does not attach the date conditions. If the tile counted the
        year all the same, it would report 252 visible photos of the initial collection where 854
        are visible -- and send the team off to date what has long been on the map."""
        make_photo(year=None, sha="f" * 64)
        session.commit()

        data = admin_client.get("/api/admin/overview").json()

        assert data["on_map"] == 1
        assert data["without_date"] == 1

    def test_a_photo_without_a_place_does_not(self, admin_client: TestClient, session, make_photo):
        """The counter-check: without a place there is no marker, year or no year."""
        make_photo(lat=None, lon=None, sha="g" * 64)
        session.commit()

        assert admin_client.get("/api/admin/overview").json()["on_map"] == 0

    def test_a_deleted_photo_counts_in_no_work_tile(
        self, admin_client: TestClient, session, make_photo
    ):
        """Otherwise the tile would send somebody into a list the photo does not stand in.

        A deleted photo without a place meets both conditions -- without the status filter it would
        count under "without a place" while the list behind it leaves it out. The number and the
        list have to say the same thing."""
        make_photo(lat=None, lon=None, year=None, status=PhotoStatus.DELETED, sha="e" * 64)
        session.commit()

        data = admin_client.get("/api/admin/overview").json()

        assert data["total"] == 0
        assert data["without_location"] == 0
        assert data["without_date"] == 0
        assert data["deleted"] == 1

    def test_a_reverted_contribution_no_longer_counts(
        self, admin_client: TestClient, session, make_photo
    ):
        """The tile leads into moderation -- it must report nothing that does not stand there.

        Otherwise "there was a visitor contribution today" would stand above an empty list."""
        photo = make_photo(sha="a" * 64)
        session.add(
            Change(
                photo_id=photo.id,
                field="date",
                old_value=None,
                new_value="1932",
                source=Source.VISITOR,
                created_at=datetime.now(),
                reverted_at=datetime.now(),
            )
        )
        session.commit()

        data = admin_client.get("/api/admin/overview").json()

        assert data["visitor_changes"] == 0
        assert data["days_since_change"] is None

    def test_an_open_contribution_dates_the_tile(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo(sha="a" * 64)
        session.add(
            Change(
                photo_id=photo.id,
                field="date",
                old_value=None,
                new_value="1932",
                source=Source.VISITOR,
                created_at=datetime.now(UTC).replace(tzinfo=None),
            )
        )
        session.commit()

        data = admin_client.get("/api/admin/overview").json()

        assert data["days_since_change"] == 0


class TestThePhotoList:
    def test_the_place_filter_leaves_out_the_undated(
        self, admin_client: TestClient, session, make_photo
    ):
        """The reason for the split.

        Locating and dating are two jobs. Whoever works through the photos without a place does not
        want the ones without a year in between -- under a common "incomplete" they got them."""
        make_photo(title="Vollstaendig", sha="a" * 64)
        make_photo(title="Ohne Ort", lat=None, lon=None, sha="b" * 64)
        make_photo(title="Ohne Jahr", year=None, sha="c" * 64)
        session.commit()

        data = admin_client.get("/api/admin/photos", params={"show": "without_location"}).json()

        assert [photo["title"] for photo in data["photos"]] == ["Ohne Ort"]

    def test_the_year_filter_leaves_out_the_unplaced(
        self, admin_client: TestClient, session, make_photo
    ):
        make_photo(title="Vollstaendig", sha="a" * 64)
        make_photo(title="Ohne Ort", lat=None, lon=None, sha="b" * 64)
        make_photo(title="Ohne Jahr", year=None, sha="c" * 64)
        session.commit()

        data = admin_client.get("/api/admin/photos", params={"show": "without_date"}).json()

        assert [photo["title"] for photo in data["photos"]] == ["Ohne Jahr"]

    def test_a_deleted_photo_stands_in_no_other_list(
        self, admin_client: TestClient, session, make_photo
    ):
        """Otherwise deleting would have no effect exactly where anybody looks.

        A deleted photo without a place and without a year meets all three remaining filters.
        Without the status filter the two work lists would offer it for editing again and again --
        the very photo somebody has just sorted out."""
        make_photo(title="Bleibt", sha="a" * 64)
        make_photo(
            title="Geloescht",
            lat=None,
            lon=None,
            year=None,
            status=PhotoStatus.DELETED,
            sha="b" * 64,
        )
        session.commit()

        def title(show: str) -> list[str]:
            data = admin_client.get("/api/admin/photos", params={"show": show}).json()
            return [photo["title"] for photo in data["photos"]]

        assert title("all") == ["Bleibt"]
        assert title("without_location") == []
        assert title("without_date") == []
        assert title("deleted") == ["Geloescht"]

    def test_a_restored_photo_shows_up_again(self, admin_client: TestClient, session, make_photo):
        """Deleting has to be reversible -- a slip must not be final."""
        photo = make_photo(title="Zurueck", status=PhotoStatus.DELETED, sha="a" * 64)
        session.commit()

        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"status": "published"})

        data = admin_client.get("/api/admin/photos", params={"show": "all"}).json()
        assert [f["title"] for f in data["photos"]] == ["Zurueck"]
        assert (
            admin_client.get("/api/admin/photos", params={"show": "deleted"}).json()["total"] == 0
        )

    def test_the_search_finds_by_file_name(self, admin_client: TestClient, session, make_photo):
        """After a batch upload one searches for what stood on the scanner."""
        make_photo(title="Kirchweih 1932", sha="a" * 64)
        make_photo(title="Umzug", sha="b" * 64)
        session.commit()

        data = admin_client.get("/api/admin/photos", params={"q": "kirchweih"}).json()

        assert data["total"] == 1
        assert data["photos"][0]["original_filename"] == "Kirchweih 1932.jpg"

    def test_no_list_without_signing_in(self, client: TestClient):
        assert client.get("/api/admin/photos").status_code == 401


class TestPaging:
    """The total carries the page count.

    If it is taken from the paged query, "page 1 of 1" stands everywhere and nobody ever gets to
    page 2."""

    def test_the_total_counts_without_paging(self, admin_client: TestClient, session, make_photo):
        for number in range(5):
            make_photo(title=f"Foto {number}", sha=str(number) * 64)
        session.commit()

        data = admin_client.get("/api/admin/photos", params={"limit": 2}).json()

        assert len(data["photos"]) == 2
        assert data["total"] == 5

    def test_the_second_page_shows_different_photos(
        self, admin_client: TestClient, session, make_photo
    ):
        for number in range(5):
            make_photo(title=f"Foto {number}", sha=str(number) * 64)
        session.commit()

        first = admin_client.get("/api/admin/photos", params={"limit": 2}).json()["photos"]
        second = admin_client.get("/api/admin/photos", params={"limit": 2, "offset": 2}).json()[
            "photos"
        ]

        assert {photo["id"] for photo in first}.isdisjoint({photo["id"] for photo in second})

    def test_the_second_page_shows_different_contributions(
        self, admin_client: TestClient, session, make_photo
    ):
        for number in range(3):
            photo = make_photo(lat=None, lon=None, sha=str(number) * 64)
            session.commit()
            admin_client.post(f"/api/contribute/{photo.id}/location", json=HOLM)

        data = admin_client.get("/api/admin/changes", params={"limit": 2, "offset": 2}).json()

        assert data["total"] == 3
        assert len(data["changes"]) == 1

    def test_the_log_pages_as_well(self, admin_client: TestClient, session):
        for number in range(4):
            session.add(
                ImportLog(
                    path=f"/tmp/{number}.jpg",
                    result=ImportResult.IMPORTED,
                    created_at=datetime(2026, 3, number + 1, 12, 0),
                )
            )
        session.commit()

        data = admin_client.get("/api/admin/imports", params={"limit": 3, "offset": 3}).json()

        assert data["total"] == 4
        assert [entry["filename"] for entry in data["entries"]] == ["0.jpg"]


class TestEditingAPhoto:
    def test_a_missing_field_stays_untouched(self, admin_client: TestClient, session, make_photo):
        """Whoever changes only the title must not lose the dating."""
        photo = make_photo(title="Alt", year=1932)
        session.commit()

        data = admin_client.patch(f"/api/admin/photos/{photo.id}", json={"title": "Neu"}).json()

        assert data["title"] == "Neu"
        assert data["date_label"] == "1932"
        assert data["lat"] is not None

    def test_an_empty_field_clears_the_dating(self, admin_client: TestClient, session, make_photo):
        """The opposite case -- an explicit null takes a wrong entry out.

        Without that difference the curator could only replace a wrong year with another one, never
        with "nobody knows"."""
        photo = make_photo(year=1932)
        session.commit()

        data = admin_client.patch(f"/api/admin/photos/{photo.id}", json={"date": None}).json()

        assert data["date_label"] == "Jahr unbekannt"
        assert data["needs_date"] is True

    def test_a_cleared_dating_offers_the_photo_again(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo(year=1932)
        session.commit()
        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"date": None})

        task = admin_client.get("/api/contribute/next", params={"need": "date"}).json()

        assert task["photo"]["id"] == photo.id

    def test_an_impossible_date_is_rejected(self, admin_client: TestClient, session, make_photo):
        photo = make_photo()
        session.commit()

        response = admin_client.patch(
            f"/api/admin/photos/{photo.id}",
            json={"date": {"year": 1932, "month": 2, "day": 30, "precision": "day"}},
        )

        assert response.status_code == 422

    def test_a_decade_becomes_an_interval(self, admin_client: TestClient, session, make_photo):
        photo = make_photo(year=None)
        session.commit()

        data = admin_client.patch(
            f"/api/admin/photos/{photo.id}",
            json={"date": {"year": 1934, "precision": "decade"}},
        ).json()

        # Rounded down to the start of the decade, not 1934 to 1943.
        assert data["date_from"] == "1930-01-01"
        assert data["date_to"] == "1939-12-31"
        assert data["date_label"] == "1930er"

    def test_an_edit_is_logged(self, admin_client: TestClient, session, make_photo):
        photo = make_photo(title="Alt")
        session.commit()

        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"title": "Neu"})

        entry = session.scalars(select(Change).where(Change.field == "title")).one()
        assert (entry.old_value, entry.new_value) == ("Alt", "Neu")
        assert entry.source == Source.CURATOR

    def test_the_same_value_makes_no_entry(self, admin_client: TestClient, session, make_photo):
        """Otherwise the contribution list drowns in entries that say nothing."""
        photo = make_photo(title="Alt")
        session.commit()

        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"title": "Alt"})

        assert session.scalars(select(Change)).all() == []

    def test_a_curator_may_place_outside_the_region(
        self, admin_client: TestClient, session, make_photo
    ):
        """Unlike a visitor: the curator may know about an outing."""
        photo = make_photo(lat=None, lon=None)
        session.commit()

        response = admin_client.patch(
            f"/api/admin/photos/{photo.id}",
            json={"location": {"lat": 48.1372, "lon": 11.5756, "place_name": "Muenchen"}},
        )

        assert response.status_code == 200
        assert response.json()["location_source"] == "curator"

    def test_a_deleted_photo_vanishes_from_the_map(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo()
        session.commit()

        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"status": "deleted"})

        map_photos = admin_client.get("/api/photos", params={"bbox": "9.5,53.5,9.8,53.7"}).json()
        assert map_photos["total"] == 0
        # It is not deleted -- in the admin view it stays findable.
        assert admin_client.get(f"/api/admin/photos/{photo.id}").status_code == 200

    def test_tags_are_replaced_not_added_to(self, admin_client: TestClient, session, make_photo):
        photo = make_photo()
        session.commit()
        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"tags": ["Muehle", "Umzug"]})

        data = admin_client.patch(f"/api/admin/photos/{photo.id}", json={"tags": ["Muehle"]}).json()

        assert data["tags"] == ["Muehle"]

    def test_an_unknown_photo(self, admin_client: TestClient):
        response = admin_client.patch("/api/admin/photos/9999", json={"title": "Neu"})

        assert response.status_code == 404
        assert "9999" in response.json()["detail"]


class TestVisitorContributions:
    def _contribution(self, client: TestClient, photo_id: int) -> int:
        client.post(f"/api/contribute/{photo_id}/location", json=HOLM)
        return client.get("/api/admin/changes").json()["changes"][0]["id"]

    def test_the_list_shows_what_happened_at_the_kiosk(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo(lat=None, lon=None, title="Ohne Ort")
        session.commit()
        admin_client.post(f"/api/contribute/{photo.id}/location", json=HOLM)

        data = admin_client.get("/api/admin/changes").json()

        assert data["total"] == 1
        assert data["changes"][0]["photo_title"] == "Ohne Ort"
        assert data["changes"][0]["field"] == "location"
        assert data["changes"][0]["revertable"] is True

    def test_reverting_offers_the_photo_again(self, admin_client: TestClient, session, make_photo):
        """The point of the whole thing: a wrong entry becomes an open question again."""
        photo = make_photo(lat=None, lon=None)
        session.commit()
        contribution = self._contribution(admin_client, photo.id)

        data = admin_client.post(f"/api/admin/changes/{contribution}/revert").json()

        assert data["needs_location"] is True
        assert data["lat"] is None
        task = admin_client.get("/api/contribute/next", params={"need": "location"}).json()
        assert task["photo"]["id"] == photo.id

    def test_reverting_twice_is_not_possible(self, admin_client: TestClient, session, make_photo):
        photo = make_photo(lat=None, lon=None)
        session.commit()
        contribution = self._contribution(admin_client, photo.id)
        admin_client.post(f"/api/admin/changes/{contribution}/revert")

        response = admin_client.post(f"/api/admin/changes/{contribution}/revert")

        assert response.status_code == 409

    def test_what_was_edited_by_hand_is_not_reverted(
        self, admin_client: TestClient, session, make_photo
    ):
        """Otherwise the revert would throw the curator's work away with it."""
        photo = make_photo(lat=None, lon=None)
        session.commit()
        contribution = self._contribution(admin_client, photo.id)
        admin_client.patch(
            f"/api/admin/photos/{photo.id}", json={"location": {"lat": 53.63, "lon": 9.68}}
        )

        response = admin_client.post(f"/api/admin/changes/{contribution}/revert")

        assert response.status_code == 409
        assert admin_client.get("/api/admin/changes").json()["changes"][0]["revertable"] is False

    def test_a_curator_edit_does_not_stand_in_the_contribution_list(
        self, admin_client: TestClient, session, make_photo
    ):
        """The list is there for reviewing what strangers have entered."""
        photo = make_photo(title="Alt")
        session.commit()
        admin_client.patch(f"/api/admin/photos/{photo.id}", json={"title": "Neu"})

        assert admin_client.get("/api/admin/changes").json()["changes"] == []

    def test_what_was_reverted_stays_visible_on_request(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo(lat=None, lon=None)
        session.commit()
        contribution = self._contribution(admin_client, photo.id)
        admin_client.post(f"/api/admin/changes/{contribution}/revert")

        assert admin_client.get("/api/admin/changes").json()["changes"] == []
        with_everything = admin_client.get(
            "/api/admin/changes", params={"include_reverted": True}
        ).json()
        assert with_everything["total"] == 1
        assert with_everything["changes"][0]["reverted_at"] is not None


class TestBatchUpload:
    def test_no_upload_without_signing_in(self, client: TestClient, fixtures_dir):
        response = client.post(
            "/api/admin/upload", files=[("files", ("scan.jpg", _image(fixtures_dir), "image/jpeg"))]
        )

        assert response.status_code == 401

    def test_a_photo_is_in_the_database_right_after_uploading(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        """No queue model: a closed browser must not cost uploads.

        The table in the admin view is a follow-up list. Whatever is left lying there surfaces in
        the contribution panel -- it is never lost."""
        response = admin_client.post(
            "/api/admin/upload", files=[("files", ("scan.jpg", _image(fixtures_dir), "image/jpeg"))]
        )

        assert response.json()["imported"] == 1
        session.expire_all()
        assert len(session.scalars(select(Photo)).all()) == 1

    def test_the_year_applies_to_the_whole_batch(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        response = admin_client.post(
            "/api/admin/upload",
            files=[
                ("files", ("a.jpg", _image(fixtures_dir, "scan_ohne_exif.jpg"), "image/jpeg")),
                ("files", ("b.jpg", _image(fixtures_dir, "hochkant.jpg"), "image/jpeg")),
            ],
            data={"year": "1932"},
        )

        data = response.json()
        assert data["imported"] == 2
        assert [entry["photo"]["date_label"] for entry in data["items"]] == ["1932", "1932"]

    def test_the_place_applies_to_the_whole_batch(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        response = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("a.jpg", _image(fixtures_dir), "image/jpeg"))],
            data={"lat": "53.6205", "lon": "9.676", "place_name": "Kirche"},
        )

        photo = response.json()["items"][0]["photo"]
        assert photo["place_name"] == "Kirche"
        assert photo["location_source"] == "curator"

    def test_the_tag_applies_to_the_whole_batch(
        self, admin_client: TestClient, session, fixtures_dir, settings, monkeypatch
    ):
        """Whoever uploads a hundred photos out of one folder types it once.

        And unlike every other batch entry, a tag **displaces** nothing: it stands beside what the
        file says and beside the device setting. A field holds one value, a tag list is a set."""
        monkeypatch.setattr(settings, "import_tags", ["Gebäude"])

        response = admin_client.post(
            "/api/admin/upload",
            files=[
                ("files", ("a.jpg", _image(fixtures_dir, "scan_ohne_exif.jpg"), "image/jpeg")),
                ("files", ("b.jpg", _image(fixtures_dir, "hochkant.jpg"), "image/jpeg")),
            ],
            data={"tags": "Feuerwehr, Neubau"},
        )

        assert response.json()["imported"] == 2
        for photo in session.scalars(select(Photo)).all():
            names = {tag.name for tag in photo.tags}
            assert {"Feuerwehr", "Neubau", "Gebäude"} <= names

    def test_a_batch_entry_overwrites_nothing_that_exists(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        """The image brings GPS with it. What the file knows beats the batch entry."""
        response = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("gps.jpg", _image(fixtures_dir, "foto_mit_gps.jpg"), "image/jpeg"))],
            data={"lat": "48.1372", "lon": "11.5756"},
        )

        photo = response.json()["items"][0]["photo"]
        assert abs(photo["lat"] - 53.62053) < 0.001
        assert photo["location_source"] == "exif"

    def test_a_duplicate_is_named_not_kept_quiet(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        """ "3 were already there" is information, silence is not."""
        image = _image(fixtures_dir)
        admin_client.post("/api/admin/upload", files=[("files", ("a.jpg", image, "image/jpeg"))])

        data = admin_client.post(
            "/api/admin/upload", files=[("files", ("nochmal.jpg", image, "image/jpeg"))]
        ).json()

        assert data["duplicates"] == 1
        assert data["imported"] == 0
        assert "Inhaltsgleich" in data["items"][0]["message"]
        # The photo already present is delivered too -- the admin should see which one is meant.
        assert data["items"][0]["photo"] is not None

    def test_a_text_file_is_rejected_with_a_reason(self, admin_client: TestClient, fixtures_dir):
        data = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("liste.txt", _image(fixtures_dir, "kein_bild.txt"), "text/plain"))],
        ).json()

        assert data["rejected"] == 1
        assert "Kein lesbares Bild" in data["items"][0]["message"]

    def test_a_path_in_the_file_name_has_no_effect(
        self, admin_client: TestClient, settings, fixtures_dir
    ):
        """A file name from the browser is input, not a route description."""
        data = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("../../boese.jpg", _image(fixtures_dir), "image/jpeg"))],
        ).json()

        assert data["items"][0]["filename"] == "boese.jpg"
        assert not (settings.data_dir.parent / "boese.jpg").exists()

    def test_an_upload_lands_in_the_import_log(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        admin_client.post(
            "/api/admin/upload", files=[("files", ("scan.jpg", _image(fixtures_dir), "image/jpeg"))]
        )

        log = admin_client.get("/api/admin/imports").json()

        assert log["total"] == 1
        # Not the path in the temporary folder but the name the admin knows.
        assert log["entries"][0]["filename"] == "scan.jpg"
        assert log["entries"][0]["result"] == "imported"


class TestTheImportLog:
    def test_only_the_rejected_ones_on_request(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        admin_client.post(
            "/api/admin/upload",
            files=[
                ("files", ("gut.jpg", _image(fixtures_dir), "image/jpeg")),
                ("files", ("schlecht.txt", _image(fixtures_dir, "kein_bild.txt"), "text/plain")),
            ],
        )

        data = admin_client.get("/api/admin/imports", params={"result": "rejected"}).json()

        assert [entry["filename"] for entry in data["entries"]] == ["schlecht.txt"]

    def test_newest_first(self, admin_client: TestClient, session):
        from app.models import ImportLog, ImportResult

        for number, tag in enumerate([1, 2, 3], start=1):
            session.add(
                ImportLog(
                    path=f"/tmp/{number}.jpg",
                    result=ImportResult.IMPORTED,
                    created_at=datetime(2026, 3, tag, 12, 0),
                )
            )
        session.commit()

        data = admin_client.get("/api/admin/imports").json()

        assert [entry["filename"] for entry in data["entries"]] == ["3.jpg", "2.jpg", "1.jpg"]


class TestUntouchedFields:
    def test_a_dating_without_precision_becomes_a_year(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo(year=None)
        session.commit()

        data = admin_client.patch(
            f"/api/admin/photos/{photo.id}", json={"date": {"year": 1955}}
        ).json()

        assert data["date_precision"] == DatePrecision.YEAR
        assert data["date_label"] == "1955"


class TestCreditAndProvenance:
    """Two fields with two different readers -- and the separation is the actual promise.

    The credit stands beside the image in the museum. The provenance -- who handed it in, whether
    a release exists -- is an internal note. Passed through to the visitor screen, the name of a
    lender would stand there whom nobody ever asked about it."""

    def test_both_can_be_set(self, admin_client: TestClient, session, make_photo):
        photo = make_photo()
        session.commit()

        data = admin_client.patch(
            f"/api/admin/photos/{photo.id}",
            json={"credit": "Sammlung Heimatmuseum Holm", "provenance": "Leihgabe H. Meyer"},
        ).json()

        assert data["credit"] == "Sammlung Heimatmuseum Holm"
        assert data["provenance"] == "Leihgabe H. Meyer"

    def test_the_provenance_does_not_appear_in_the_visitor_view(
        self, admin_client: TestClient, session, make_photo
    ):
        photo = make_photo()
        photo.credit = "Sammlung Heimatmuseum Holm"
        photo.provenance = "Leihgabe H. Meyer, Freigabe liegt vor"
        session.commit()

        data = admin_client.get(f"/api/photos/{photo.id}").json()

        assert data["credit"] == "Sammlung Heimatmuseum Holm", "der Nachweis gehoert ans Bild"
        assert "provenance" not in data, "die Herkunft darf den Kiosk nie erreichen"
        assert "Meyer" not in str(data)

    def test_an_empty_field_clears_the_credit(self, admin_client: TestClient, session, make_photo):
        """As in the whole editor: a missing field means unchanged, an empty one means delete."""
        photo = make_photo()
        photo.credit = "Falsche Angabe"
        session.commit()

        data = admin_client.patch(f"/api/admin/photos/{photo.id}", json={"credit": None}).json()

        assert data["credit"] is None

    def test_a_batch_upload_sets_both_for_all_of_them(
        self, admin_client: TestClient, session, fixtures_dir
    ):
        response = admin_client.post(
            "/api/admin/upload",
            files=[("files", ("a.jpg", _image(fixtures_dir, "scan_ohne_exif.jpg"), "image/jpeg"))],
            data={"credit": "Sammlung Heimatmuseum Holm", "provenance": "Kiste Dachboden Petersen"},
        )

        assert response.status_code == 200
        photo = session.scalars(select(Photo)).one()
        assert photo.credit == "Sammlung Heimatmuseum Holm"
        assert photo.provenance == "Kiste Dachboden Petersen"


class TestSearchingByHash:
    """The eight characters from the detail view have to lead back through the admin view.

    Otherwise an identifier would stand there that can be looked up nowhere -- decoration instead
    of information. It is the way back to a photo whose title is exactly the wrong one."""

    def test_finds_a_photo_by_the_start_of_its_hash(
        self, admin_client: TestClient, session, make_photo
    ):
        make_photo(sha="abc12345" + "0" * 56, title="Falsch beschriftet")
        make_photo(sha="f" * 64, title="Ein anderes")
        session.commit()

        data = admin_client.get("/api/admin/photos", params={"q": "abc12345"}).json()

        assert data["total"] == 1
        assert data["photos"][0]["title"] == "Falsch beschriftet"

    def test_the_hash_stands_in_the_detail_view(self, client: TestClient, session, make_photo):
        # And in the public one at that: the visitor view shows it under the credit.
        photo = make_photo(sha="abc12345" + "0" * 56)
        session.commit()

        assert client.get(f"/api/photos/{photo.id}").json()["sha256"].startswith("abc12345")


@pytest.fixture
def place_index(session):
    """A street with three house numbers -- the place index the refinement needs."""

    def add(name, kind, street=None, housenumber=None, lat=53.62, lon=9.676):
        session.add(
            Place(
                name=name,
                name_normalized=normalize(name),
                lat=lat,
                lon=lon,
                kind=kind,
                street=street,
                housenumber=housenumber,
            )
        )

    add("Am Kamp", "strasse", lat=53.6200, lon=9.6760)
    for number, lat in (("1", 53.6201), ("2", 53.6202), ("3", 53.6203)):
        add(f"Am Kamp {number}", "adresse", street="Am Kamp", housenumber=number, lat=lat)
    session.commit()
    return session


class TestRevertingARefinement:
    """Reverting here means **resetting**, not deleting.

    With the place and the year the previous value was always nothing -- visitors fill only what is
    empty there, so deleting *is* restoring. The house number replaces. If it were deleted on a
    revert, the photo would lose its place entirely: a punishment for a contribution that was
    merely too precise."""

    def _refine(self, client: TestClient, session, photo, number="2") -> int:
        address = session.scalar(
            select(Place).where(Place.kind == "adresse", Place.housenumber == number)
        )
        client.post(f"/api/contribute/{photo.id}/housenumber", json={"place_id": address.id})
        return client.get("/api/admin/changes").json()["changes"][0]["id"]

    def _photo(self, make_photo, **fields):
        return make_photo(place_name="Am Kamp", accuracy=150, lat=53.62, lon=9.676, **fields)

    def test_reverting_falls_back_to_the_street_centre(
        self, admin_client: TestClient, place_index, make_photo
    ):
        photo = self._photo(make_photo)
        place_index.commit()
        contribution = self._refine(admin_client, place_index, photo)

        data = admin_client.post(f"/api/admin/changes/{contribution}/revert").json()

        assert data["lat"] is not None, "das Foto behaelt seinen Ort"
        assert data["place_name"] == "Am Kamp"
        assert data["location_accuracy_m"] == 150

    def test_reverting_restores_the_curator_source(
        self, admin_client: TestClient, place_index, make_photo
    ):
        """Otherwise curator knowledge would silently become a visitor contribution.

        And the next visitor could refine it again, because the source permitted it.
        """
        photo = self._photo(make_photo, location_source=Source.CURATOR)
        place_index.commit()
        contribution = self._refine(admin_client, place_index, photo)

        admin_client.post(f"/api/admin/changes/{contribution}/revert")
        place_index.refresh(photo)

        assert photo.location_source == Source.CURATOR

    def test_the_photo_is_asked_for_its_house_number_again(
        self, admin_client: TestClient, place_index, make_photo
    ):
        photo = self._photo(make_photo, location_source=Source.VISITOR)
        place_index.commit()
        contribution = self._refine(admin_client, place_index, photo)

        admin_client.post(f"/api/admin/changes/{contribution}/revert")

        task = admin_client.get("/api/contribute/next", params={"need": "housenumber"}).json()
        assert task["photo"]["id"] == photo.id

    def test_an_older_place_entry_only_after_the_newer_one(
        self, admin_client: TestClient, place_index, make_photo
    ):
        """The state one can otherwise produce quietly.

        First a visitor locates the photo, then somebody refines it. If the curator reverts the
        *first* entry, the place is emptied -- and the second revert then restores a street nobody
        contributed. Top to bottom is the only order that works out."""
        photo = make_photo(lat=None, lon=None, place_name=None, accuracy=None, sha="z" * 64)
        place_index.commit()
        admin_client.post(
            f"/api/contribute/{photo.id}/location",
            json={"lat": 53.62, "lon": 9.676, "place_name": "Am Kamp", "accuracy_m": 150},
        )
        older_one = admin_client.get("/api/admin/changes").json()["changes"][0]["id"]
        self._refine(admin_client, place_index, photo)

        response = admin_client.post(f"/api/admin/changes/{older_one}/revert")

        assert response.status_code == 409
        entries = admin_client.get("/api/admin/changes").json()["changes"]
        older_entry = next(e for e in entries if e["id"] == older_one)
        assert older_entry["revertable"] is False, "kein Knopf, der nur 409 liefert"

    def test_without_the_street_in_the_place_index_nothing_is_reverted(
        self, admin_client: TestClient, place_index, make_photo
    ):
        """Better to refuse than to take the photo's place away entirely.

        A newly built place index may have renamed a street; ``place_name`` is a string and not a
        foreign key."""
        photo = self._photo(make_photo)
        place_index.commit()
        contribution = self._refine(admin_client, place_index, photo)
        street_name = place_index.scalar(select(Place).where(Place.name == "Am Kamp"))
        place_index.delete(street_name)
        place_index.commit()

        response = admin_client.post(f"/api/admin/changes/{contribution}/revert")

        assert response.status_code == 409
        place_index.refresh(photo)
        assert photo.place_name == "Am Kamp 2", "die Angabe bleibt stehen"

    def test_a_house_number_edited_by_hand_stays(
        self, admin_client: TestClient, place_index, make_photo
    ):
        photo = self._photo(make_photo)
        place_index.commit()
        contribution = self._refine(admin_client, place_index, photo)
        admin_client.patch(
            f"/api/admin/photos/{photo.id}", json={"location": {"lat": 53.63, "lon": 9.68}}
        )

        assert admin_client.post(f"/api/admin/changes/{contribution}/revert").status_code == 409
