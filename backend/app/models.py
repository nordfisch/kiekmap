"""Tabellen.

Zwei Eigenheiten praegen dieses Modell, beide folgen daraus, dass historische Fotos Scans sind
(siehe docs/decisions.md, Punkt 1):

1. Jedes inhaltliche Feld traegt seine Herkunft. Ein aus EXIF geratenes Datum darf eine kuratierte
   Angabe nie ueberschreiben.
2. Datumsangaben sind Intervalle, keine Zeitpunkte. "1920er" ist die Realitaet, nicht die Ausnahme.
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Source(StrEnum):
    """Woher eine Angabe stammt. Bestimmt, was was ueberschreiben darf."""

    EXIF = "exif"
    CURATOR = "curator"
    VISITOR = "visitor"


class DatePrecision(StrEnum):
    """Wie genau die Datierung ist. Bestimmt die Beschriftung ("um 1930", "1920er")."""

    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    DECADE = "decade"
    UNKNOWN = "unknown"


class PhotoStatus(StrEnum):
    PUBLISHED = "published"
    HIDDEN = "hidden"


class ImportResult(StrEnum):
    IMPORTED = "imported"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"


def _enum_werte(enum_klasse: type[StrEnum]) -> str:
    return ", ".join(f"'{mitglied.value}'" for mitglied in enum_klasse)


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- Datei ---------------------------------------------------------------
    #
    # Der SHA-256 des Bildinhalts ist zugleich Dateiname und Dublettenschutz. Ein zweiter Import
    # derselben Datei laeuft in diese Eindeutigkeit und wird abgewiesen statt verdoppelt.
    sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime: Mapped[str] = mapped_column(String(64), nullable=False)
    bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Masse nach Anwendung der EXIF-Orientierung -- also so, wie das Bild angezeigt wird.
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)

    imported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # --- Inhalt --------------------------------------------------------------
    title: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)

    # Aufnahmezeit als Intervall. Beide NULL heisst "unbekannt" -- und genau diese Fotos landen
    # im "Hilf mit"-Bereich.
    date_from: Mapped[date | None] = mapped_column(Date)
    date_to: Mapped[date | None] = mapped_column(Date)
    date_precision: Mapped[str] = mapped_column(String(10), default=DatePrecision.UNKNOWN)

    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    place_name: Mapped[str | None] = mapped_column(String(300))
    #: Grobe Angabe eines Besuchers ("irgendwo am Dorfteich") laesst sich so kennzeichnen.
    location_accuracy_m: Mapped[int | None] = mapped_column(Integer)

    # --- Herkunft der Angaben ------------------------------------------------
    title_source: Mapped[str | None] = mapped_column(String(10))
    date_source: Mapped[str | None] = mapped_column(String(10))
    location_source: Mapped[str | None] = mapped_column(String(10))

    # --- Rohdaten aus der Datei ----------------------------------------------
    #
    # Bewusst getrennt von date_from/date_to: bei einem Scan ist das EXIF-Datum das Datum des
    # Scans, nicht der Aufnahme. Es hier aufzuheben hilft dem Kurator, es in die Zeitleiste zu
    # schreiben waere falsch. Siehe app/services/exif.py.
    exif_datetime: Mapped[datetime | None] = mapped_column(DateTime)

    status: Mapped[str] = mapped_column(String(10), default=PhotoStatus.PUBLISHED, nullable=False)

    tags: Mapped[list["Tag"]] = relationship(secondary="photo_tags", back_populates="photos")

    __table_args__ = (
        CheckConstraint(f"date_precision IN ({_enum_werte(DatePrecision)})", name="ck_precision"),
        CheckConstraint(f"status IN ({_enum_werte(PhotoStatus)})", name="ck_status"),
        CheckConstraint("(lat IS NULL) = (lon IS NULL)", name="ck_koordinatenpaar"),
        CheckConstraint("date_to IS NULL OR date_from <= date_to", name="ck_zeitraum"),
        # Die Kartenabfrage filtert ueber Ort und Zeitraum zugleich.
        Index("ix_photos_ort", "lat", "lon"),
        Index("ix_photos_zeit", "date_from", "date_to"),
        Index("ix_photos_status", "status"),
    )

    @property
    def needs_location(self) -> bool:
        return self.lat is None

    @property
    def needs_date(self) -> bool:
        return self.date_from is None


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
    """Aenderungsprotokoll, vor allem fuer Besucherbeitraege.

    Beitraege werden direkt uebernommen -- der unmittelbare Effekt ist der Reiz fuer den Besucher.
    Dieses Protokoll ist der Gegenpol dazu: der Kurator sieht, was am Kiosk passiert ist, und kann
    einzelne Aenderungen zuruecknehmen.
    """

    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    field: Mapped[str] = mapped_column(String(40), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(10), nullable=False)
    #: Unterscheidet Besucher am selben Geraet, ohne sie zu identifizieren.
    session_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    #: Gesetzt, wenn ein Kurator die Aenderung zurueckgenommen hat.
    reverted_at: Mapped[datetime | None] = mapped_column(DateTime)

    __table_args__ = (
        CheckConstraint(f"source IN ({_enum_werte(Source)})", name="ck_change_source"),
        Index("ix_changes_photo", "photo_id"),
        Index("ix_changes_zeit", "created_at"),
    )


class Place(Base):
    """Ortsverzeichnis fuer die Suche im "Hilf mit"-Bereich.

    Wird aus dem OSM-Ausschnitt erzeugt und ersetzt Nominatim fuer den einen Zweck, den wir haben:
    "Wo ist das?" mit einem Strassennamen beantworten, ohne Internet.
    """

    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    #: Kleingeschrieben und ohne Umlaute, damit "muhlenweg" den "Mühlenweg" findet.
    name_normalized: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    #: street, building, water, wood, hamlet ...
    kind: Mapped[str] = mapped_column(String(40), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "kind", "lat", "lon", name="uq_place"),
        Index("ix_places_suche", "name_normalized"),
    )


class ImportLog(Base):
    """Was wurde importiert, was abgewiesen und warum.

    Ohne dieses Protokoll waere ein stillschweigend uebersprungenes Foto nicht von einem nie
    hineinkopierten zu unterscheiden.
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
        CheckConstraint(f"result IN ({_enum_werte(ImportResult)})", name="ck_import_result"),
        Index("ix_import_log_zeit", "created_at"),
    )
