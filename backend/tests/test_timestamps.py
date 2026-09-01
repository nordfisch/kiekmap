"""What the API says about the time of day -- and what it deliberately does not say.

Everything is stored in UTC: ``func.now()`` in SQLite, ``dates.utc_now()`` in Python, the JSON
state files. Written out without a zone marker that is not a statement but a trap: by the standard,
``new Date("2026-08-18T19:25:21")`` reads a marker-less ISO time as **local time**. The admin view
therefore showed every visitor contribution two hours too early.

``exif_datetime`` is the exception and has a test of its own: it comes from a camera or a scanner,
which write the wall clock of wherever they stand and know of no zone at all.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models import Change, Source


def _as_read(raw: str) -> datetime:
    """How the browser reads the value -- ``new Date(...)`` in one line of Python."""
    return datetime.fromisoformat(raw)


class TestStoredTimestamps:
    def test_the_import_time_names_its_zone(self, client, make_photo, session):
        """Without a marker the display would be off by the zone offset."""
        photo = make_photo()
        session.commit()

        response = client.get(f"/api/photos/{photo.id}")
        assert response.status_code == 200

        raw = response.json()["imported_at"]
        assert _as_read(raw).tzinfo is not None, f"{raw} carries no zone"
        # And the zone is the right one: the moment is now, not two hours beside it.
        assert abs(_as_read(raw) - datetime.now(UTC)) < timedelta(minutes=5)

    def test_a_visitor_contribution_is_reported_with_its_zone(
        self, admin_client, make_photo, session, settings
    ):
        photo = make_photo(lat=None, lon=None)
        session.commit()

        contribution = admin_client.post(
            f"/api/contribute/{photo.id}/location",
            json={"lat": 53.62, "lon": 9.676, "place_name": "Hauptstrasse 1"},
        )
        assert contribution.status_code == 200

        entry = admin_client.get("/api/admin/changes").json()["changes"][0]
        assert abs(_as_read(entry["created_at"]) - datetime.now(UTC)) < timedelta(minutes=5)

    def test_the_backup_reminder_names_its_zone(self, admin_client, settings):
        """Here the offset does not shift the time of day but the day itself.

        The tile shows only the date. A backup at half past midnight is 22:30 UTC of the day
        before -- and without a marker it would stand there under the wrong day.
        """
        from app.services import backup

        backup.record_backup(settings, "Teststick")

        reminder = admin_client.get("/api/admin/overview").json()["backup"]
        as_read = _as_read(reminder["last_backup_at"])
        assert as_read.tzinfo is not None
        assert abs(as_read - datetime.now(UTC)) < timedelta(minutes=5)


class TestTheException:
    def test_the_scan_date_stays_without_a_zone(self, client, make_photo, session):
        """The EXIF date is a wall-clock time, not a UTC statement.

        A scanner writes the clock of wherever it stands and knows of no zone. Stamping UTC onto
        it moves a scan from 14:00 to 16:00 and thereby invents a fact.
        """
        photo = make_photo()
        photo.exif_datetime = datetime(2019, 3, 14, 14, 0, 0)
        session.commit()

        raw = client.get(f"/api/photos/{photo.id}").json()["exif_datetime"]
        assert _as_read(raw).tzinfo is None, f"{raw} should carry no zone"
        assert raw.startswith("2019-03-14T14:00")


class TestOneClockInTheDevice:
    def test_reverting_writes_the_same_clock_as_creating(self, admin_client, make_photo, session):
        """The error that stood in the database rather than only in the display.

        ``created_at`` came from SQLite and was UTC, ``reverted_at`` from ``datetime.now()`` and
        was local time. A contribution reverted at once therefore stood two hours after itself --
        and no check in the schema catches that, because both values are valid timestamps.
        """
        photo = make_photo(year=None)
        session.commit()

        assert (
            admin_client.post(
                f"/api/contribute/{photo.id}/date", json={"year": 1932, "precision": "year"}
            ).status_code
            == 200
        )

        entry = session.scalars(select(Change).where(Change.source == Source.VISITOR)).one()
        assert admin_client.post(f"/api/admin/changes/{entry.id}/revert").status_code == 200
        session.refresh(entry)

        distance = abs(entry.reverted_at - entry.created_at)
        assert distance < timedelta(minutes=5), f"two clocks in the device: {distance}"

    def test_utc_now_returns_the_form_that_is_stored(self):
        """Naive, but UTC -- exactly what ``func.now()`` writes into the column."""
        from app.services.dates import utc_now

        now = utc_now()
        assert now.tzinfo is None
        assert abs(now - datetime.now(UTC).replace(tzinfo=None)) < timedelta(seconds=5)
