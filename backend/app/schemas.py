"""Datenformen der API."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import DatePrecision, Photo
from app.services.dates import beschriftung


class PhotoMarker(BaseModel):
    """Was die Karte pro Foto braucht -- und nicht mehr.

    Bewusst schmal gehalten: bei mehreren hundert Markern im Ausschnitt geht es um die Groesse der
    Antwort, und Beschreibung, Schlagwoerter und Herkunftsangaben werden erst beim Antippen
    gebraucht.
    """

    id: int
    lat: float
    lon: float
    title: str | None
    #: Fertig formuliert ("1932", "1920er"), damit das Frontend keine Datumsarithmetik betreibt.
    date_label: str
    width: int
    height: int
    thumb_url: str

    @classmethod
    def von(cls, foto: Photo) -> "PhotoMarker":
        return cls(
            id=foto.id,
            lat=foto.lat,  # type: ignore[arg-type] -- die Abfrage schliesst NULL aus
            lon=foto.lon,  # type: ignore[arg-type]
            title=foto.title,
            date_label=beschriftung(foto.date_from, foto.date_to, foto.date_precision),
            width=foto.width,
            height=foto.height,
            thumb_url=f"/api/photos/{foto.id}/thumb?size=240",
        )


class PhotoDetail(BaseModel):
    """Alles zu einem Foto, fuer das Overlay und den Admin-Bereich."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    description: str | None

    date_from: date | None
    date_to: date | None
    date_precision: str
    date_label: str

    lat: float | None
    lon: float | None
    place_name: str | None
    location_accuracy_m: int | None

    title_source: str | None
    date_source: str | None
    location_source: str | None
    #: Bei einem Scan das Datum des Scanvorgangs. Steht hier, damit der Kurator es sieht -- es
    #: datiert das Foto absichtlich nicht.
    exif_datetime: datetime | None

    original_filename: str
    width: int
    height: int
    bytes: int
    imported_at: datetime

    tags: list[str]
    needs_location: bool
    needs_date: bool

    image_url: str
    thumb_url: str

    @classmethod
    def von(cls, foto: Photo) -> "PhotoDetail":
        return cls(
            id=foto.id,
            title=foto.title,
            description=foto.description,
            date_from=foto.date_from,
            date_to=foto.date_to,
            date_precision=foto.date_precision,
            date_label=beschriftung(foto.date_from, foto.date_to, foto.date_precision),
            lat=foto.lat,
            lon=foto.lon,
            place_name=foto.place_name,
            location_accuracy_m=foto.location_accuracy_m,
            title_source=foto.title_source,
            date_source=foto.date_source,
            location_source=foto.location_source,
            exif_datetime=foto.exif_datetime,
            original_filename=foto.original_filename,
            width=foto.width,
            height=foto.height,
            bytes=foto.bytes,
            imported_at=foto.imported_at,
            tags=[schlagwort.name for schlagwort in foto.tags],
            needs_location=foto.needs_location,
            needs_date=foto.needs_date,
            image_url=f"/api/photos/{foto.id}/image",
            thumb_url=f"/api/photos/{foto.id}/thumb?size=1200",
        )


class PhotoListe(BaseModel):
    photos: list[PhotoMarker]
    #: Gesamtzahl im Ausschnitt, auch wenn ``limit`` weniger geliefert hat.
    total: int
    #: Wahr, wenn ``limit`` gegriffen hat -- dann sollte die Karte zum Hineinzoomen auffordern.
    truncated: bool


class Jahrzehnt(BaseModel):
    """Ein Balken im Histogramm hinter dem Zeitschieber."""

    decade: int = Field(description="Beginn des Jahrzehnts, z. B. 1920")
    count: int


class Histogramm(BaseModel):
    decades: list[Jahrzehnt]
    #: Fotos ohne Datierung. Erscheinen in keiner Zeitauswahl, aber im "Hilf mit"-Bereich.
    undated: int
    earliest: int | None
    latest: int | None


class DatumsAngabe(BaseModel):
    """Was ein Besucher oder Kurator als Datierung angeben kann."""

    year: int = Field(ge=1800, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)
    precision: DatePrecision = DatePrecision.YEAR


# --- "Hilf mit" -------------------------------------------------------------


class OrtsBeitrag(BaseModel):
    """Ein Besucher setzt den Pin."""

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    place_name: str | None = Field(default=None, max_length=300)
    #: Grobe Angabe kennzeichnen ("irgendwo am Dorfteich").
    accuracy_m: int | None = Field(default=None, ge=0, le=100_000)
    #: Unterscheidet Besucher am selben Geraet, ohne sie zu identifizieren.
    session_id: str | None = Field(default=None, max_length=64)


class DatumsBeitrag(DatumsAngabe):
    """Ein Besucher gibt ein Jahr an."""

    session_id: str | None = Field(default=None, max_length=64)


class AufgabeAntwort(BaseModel):
    """Ein Foto, dem etwas fehlt -- plus wie viele noch offen sind."""

    need: str
    #: Zum Anzeigen im Panel: "noch 214 Fotos ohne Ort". Das motiviert.
    open_count: int
    #: None heisst: es fehlt nichts mehr. Ein schoener Zustand.
    photo: PhotoDetail | None
