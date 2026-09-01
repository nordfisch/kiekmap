"""Tables.

Two traits shape this model, both following from the fact that historical photos are scans
(see docs/decisions.md, point 1):

1. Every content field carries its origin. A date guessed from EXIF must never overwrite a
   curated statement.
2. Dates are intervals, not points in time. "the 1920s" is the reality, not the exception.
"""

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Source(StrEnum):
    """Where a statement came from. Decides what may overwrite what."""

    EXIF = "exif"
    CURATOR = "curator"
    VISITOR = "visitor"


class DatePrecision(StrEnum):
    """How precise the dating is. Drives the label shown ("um 1930", "1920er")."""

    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    DECADE = "decade"
    UNKNOWN = "unknown"


class PhotoStatus(StrEnum):
    """Whether a photo belongs to the collection.

    ``DELETED`` means *taken out of the exhibition*, not *removed from the disk*: the row stays,
    the image file stays, and "Wiederherstellen" brings both back. The status used to be called
    ``hidden`` -- but nobody on the museum team looks under "hide" for deleting, and a botched
    scan wants deleting, not hiding.
    """

    PUBLISHED = "published"
    DELETED = "deleted"


class ImportResult(StrEnum):
    IMPORTED = "imported"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"


def _enum_values(enum_class: type[StrEnum]) -> str:
    return ", ".join(f"'{member.value}'" for member in enum_class)


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- file ----------------------------------------------------------------
    #
    # The SHA-256 of the image content is both the file name and the duplicate guard. A second
    # import of the same file runs into this uniqueness and is rejected rather than duplicated.
    sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime: Mapped[str] = mapped_column(String(64), nullable=False)
    bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Dimensions after applying the EXIF orientation -- i.e. as the image is displayed.
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)

    imported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # --- content -------------------------------------------------------------
    title: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)

    # Capture time as an interval. Both NULL means "unknown" -- and exactly those photos end up
    # in the contribution panel.
    date_from: Mapped[date | None] = mapped_column(Date)
    date_to: Mapped[date | None] = mapped_column(Date)
    date_precision: Mapped[str] = mapped_column(String(10), default=DatePrecision.UNKNOWN)

    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    place_name: Mapped[str | None] = mapped_column(String(300))
    #: Lets a rough visitor statement ("somewhere by the village pond") be marked as such.
    location_accuracy_m: Mapped[int | None] = mapped_column(Integer)

    # --- rights and where it came from -----------------------------------------
    #
    # Two fields rather than one, because they have different readers. The credit line belongs
    # beside the picture; who lent it and whether they released it is an internal note that must
    # never reach the kiosk -- which is why ``PhotoDetail`` has no such field at all.
    #: Credit line, one line, shown to visitors: "Sammlung Heimatmuseum Holm", "Foto: H. Meyer".
    credit: Mapped[str | None] = mapped_column(String(200))
    #: Where it came from: donor or lender, whether a release exists. Admin area only.
    provenance: Mapped[str | None] = mapped_column(Text)

    # --- origin of each statement ---------------------------------------------
    title_source: Mapped[str | None] = mapped_column(String(10))
    date_source: Mapped[str | None] = mapped_column(String(10))
    location_source: Mapped[str | None] = mapped_column(String(10))

    # --- raw data from the file -----------------------------------------------
    #
    # Deliberately separate from date_from/date_to: for a scan the EXIF date is the date of the
    # scan, not of the capture. Keeping it here helps the curator; writing it onto the timeline
    # would be wrong. See app/services/exif.py.
    exif_datetime: Mapped[datetime | None] = mapped_column(DateTime)

    status: Mapped[str] = mapped_column(String(10), default=PhotoStatus.PUBLISHED, nullable=False)

    tags: Mapped[list["Tag"]] = relationship(secondary="photo_tags", back_populates="photos")

    __table_args__ = (
        CheckConstraint(f"date_precision IN ({_enum_values(DatePrecision)})", name="ck_precision"),
        CheckConstraint(f"status IN ({_enum_values(PhotoStatus)})", name="ck_status"),
        CheckConstraint("(lat IS NULL) = (lon IS NULL)", name="ck_coordinate_pair"),
        CheckConstraint("date_to IS NULL OR date_from <= date_to", name="ck_date_order"),
        # The map query filters on location and time range at once.
        Index("ix_photos_location", "lat", "lon"),
        Index("ix_photos_time", "date_from", "date_to"),
        Index("ix_photos_status", "status"),
    )

    # Hybrid, not plain properties: read on an instance they answer for that photo, read on the
    # class they are a SQL condition. That is what lets the query for the next open task and the
    # flag in the API payload come from **one** sentence.
    #
    # They used to be plain properties, and ``api/contribute.py`` carried a second, parallel
    # formulation for the query. Two definitions of "what is missing" that look right on their own
    # are the kind of pair that drifts without anyone noticing -- see the test that holds them
    # together.
    @hybrid_property
    def needs_location(self) -> bool:
        return self.lat is None

    @needs_location.expression  # type: ignore[no-redef]
    def needs_location(cls):
        return cls.lat.is_(None)

    @hybrid_property
    def needs_date(self) -> bool:
        return self.date_from is None

    @needs_date.expression  # type: ignore[no-redef]
    def needs_date(cls):
        return cls.date_from.is_(None)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    photos: Mapped[list[Photo]] = relationship(secondary="photo_tags", back_populates="tags")


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Change(Base):
    """Change log, above all for visitor contributions.

    Contributions are applied straight away -- the immediate effect is what makes it appealing.
    This log is the counterweight: the curator sees what happened at the kiosk and can revert
    individual changes.
    """

    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    field: Mapped[str] = mapped_column(String(40), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text)
    #: Where the replaced value came from, for the routes that replace rather than fill.
    #:
    #: Null for everything else, and that is not an omission: a contribution that only fills an
    #: empty field has no previous source, and reverting it means clearing. Only sharpening a
    #: location overwrites -- and a curator's statement has to come back as the curator's.
    old_source: Mapped[str | None] = mapped_column(String(10))
    new_value: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10), nullable=False)
    #: Distinguishes visitors at the same device without identifying them.
    session_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    #: Set once a curator has reverted the change.
    reverted_at: Mapped[datetime | None] = mapped_column(DateTime)

    __table_args__ = (
        CheckConstraint(f"source IN ({_enum_values(Source)})", name="ck_change_source"),
        Index("ix_changes_photo", "photo_id"),
        Index("ix_changes_created", "created_at"),
    )


class Place(Base):
    """Gazetteer for the search in the contribution panel.

    Built from the OSM extract; replaces Nominatim for the single purpose we have: answering
    "where is this?" with a street name, without internet.
    """

    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    #: Lowercased and without diacritics, so that "muhlenweg" finds the "Mühlenweg".
    name_normalized: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    #: strasse, ortsteil, gebaeude, natur, flur, adresse -- German, matching tiles/build-places.py
    kind: Mapped[str] = mapped_column(String(40), nullable=False)

    # --- only for kind="adresse" ----------------------------------------------
    #
    # A street of 800 m gets one point, so every photo on it lands in the same spot. The house
    # number is what makes "here it was" mean a house rather than a street.
    #
    # Kept as its own column rather than parsed back out of ``name``: the link to the street has
    # to be exact, and "Am Markt 3" would have to be told apart from "Am Markt" by guesswork.
    street: Mapped[str | None] = mapped_column(String(200))
    #: The number itself, with any letter: "12", "1a". Sorted naturally, not alphabetically.
    housenumber: Mapped[str | None] = mapped_column(String(20))

    __table_args__ = (
        UniqueConstraint("name", "kind", "lat", "lon", name="uq_place"),
        Index("ix_places_search", "name_normalized"),
        Index("ix_places_street", "street"),
    )


class ImportLog(Base):
    """What was imported, what was rejected, and why.

    Without this log a silently skipped photo would be indistinguishable from one that was never
    copied in.
    """

    __tablename__ = "import_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    sha256: Mapped[str | None] = mapped_column(String(64))
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    photo_id: Mapped[int | None] = mapped_column(ForeignKey("photos.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(f"result IN ({_enum_values(ImportResult)})", name="ck_import_result"),
        Index("ix_import_log_created", "created_at"),
    )
