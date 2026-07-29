"""API payload shapes."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import DatePrecision, ImportLog, Photo, PhotoStatus
from app.services.dates import format_label


class PhotoMarker(BaseModel):
    """What the map needs per photo -- and no more.

    Deliberately narrow: with several hundred markers in view the response size matters, and
    description, tags and origin fields are only needed once a photo is tapped.
    """

    id: int
    lat: float
    lon: float
    title: str | None
    #: Ready-made German label ("1932", "1920er") so the frontend does no date arithmetic.
    date_label: str
    width: int
    height: int
    thumb_url: str

    @classmethod
    def from_photo(cls, photo: Photo) -> "PhotoMarker":
        return cls(
            id=photo.id,
            lat=photo.lat,  # type: ignore[arg-type] -- the query excludes NULL
            lon=photo.lon,  # type: ignore[arg-type]
            title=photo.title,
            date_label=format_label(photo.date_from, photo.date_to, photo.date_precision),
            width=photo.width,
            height=photo.height,
            thumb_url=f"/api/photos/{photo.id}/thumb?size=240",
        )


class PhotoDetail(BaseModel):
    """Everything about one photo, for the overlay and the admin area."""

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
    #: For a scan, the date of the scanning run. Shown so the curator can see it -- it
    #: deliberately does not date the photo.
    exif_datetime: datetime | None

    original_filename: str
    width: int
    height: int
    bytes: int
    imported_at: datetime

    tags: list[str]
    needs_location: bool
    needs_date: bool
    status: str

    image_url: str
    thumb_url: str

    @classmethod
    def from_photo(cls, photo: Photo) -> "PhotoDetail":
        return cls(
            id=photo.id,
            title=photo.title,
            description=photo.description,
            date_from=photo.date_from,
            date_to=photo.date_to,
            date_precision=photo.date_precision,
            date_label=format_label(photo.date_from, photo.date_to, photo.date_precision),
            lat=photo.lat,
            lon=photo.lon,
            place_name=photo.place_name,
            location_accuracy_m=photo.location_accuracy_m,
            title_source=photo.title_source,
            date_source=photo.date_source,
            location_source=photo.location_source,
            exif_datetime=photo.exif_datetime,
            original_filename=photo.original_filename,
            width=photo.width,
            height=photo.height,
            bytes=photo.bytes,
            imported_at=photo.imported_at,
            tags=[tag.name for tag in photo.tags],
            needs_location=photo.needs_location,
            needs_date=photo.needs_date,
            status=photo.status,
            image_url=f"/api/photos/{photo.id}/image",
            thumb_url=f"/api/photos/{photo.id}/thumb?size=1200",
        )


class PhotoList(BaseModel):
    photos: list[PhotoMarker]
    #: Total in the viewport, even if ``limit`` returned fewer.
    total: int
    #: True when ``limit`` kicked in -- then the map should invite zooming in.
    truncated: bool


class DecadeCount(BaseModel):
    """One bar in the histogram behind the time slider."""

    decade: int = Field(description="Start of the decade, e.g. 1920")
    count: int


class Histogram(BaseModel):
    decades: list[DecadeCount]
    #: Photos without a date. In no time selection, but in the "Hilf mit" panel.
    undated: int
    earliest: int | None
    latest: int | None


class DateInput(BaseModel):
    """What a visitor or curator may state as a date."""

    year: int = Field(ge=1800, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)
    precision: DatePrecision = DatePrecision.YEAR


# --- "Hilf mit" -------------------------------------------------------------


class LocationContribution(BaseModel):
    """A visitor drops the pin."""

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    place_name: str | None = Field(default=None, max_length=300)
    #: Mark a rough statement ("somewhere by the village pond").
    accuracy_m: int | None = Field(default=None, ge=0, le=100_000)
    #: Distinguishes visitors at the same device without identifying them.
    session_id: str | None = Field(default=None, max_length=64)


class DateContribution(DateInput):
    """A visitor states a year."""

    session_id: str | None = Field(default=None, max_length=64)


class TaskResponse(BaseModel):
    """A photo missing something -- plus how many are still open."""

    need: str
    #: Shown in the panel: "noch 214 Fotos ohne Ort". It motivates.
    open_count: int
    #: None means nothing is missing any more. A pleasant state.
    photo: PhotoDetail | None


# --- admin area -------------------------------------------------------------


class LoginRequest(BaseModel):
    pin: str = Field(min_length=1, max_length=32)


class LoginResponse(BaseModel):
    token: str
    #: Remaining seconds rather than a point in time -- the Pi's clock is not to be trusted.
    #: See app/services/auth.py.
    expires_in_s: int


class LocationUpdate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    place_name: str | None = Field(default=None, max_length=300)
    accuracy_m: int | None = Field(default=None, ge=0, le=100_000)


class PhotoUpdate(BaseModel):
    """What a curator may change about one photo.

    Every field is optional in two different ways, and the difference matters: a field that is
    **absent** stays as it is, a field that is explicitly **null** is cleared. Pydantic keeps the
    two apart in ``model_fields_set``, which is why the endpoint reads ``exclude_unset``.

    Without that distinction the editor could only ever add, never remove a wrong dating.
    """

    title: str | None = Field(default=None, max_length=300)
    description: str | None = None
    date: DateInput | None = None
    location: LocationUpdate | None = None
    tags: list[str] | None = None
    #: Hidden photos disappear from the map and the "Hilf mit" panel, but are not deleted.
    status: PhotoStatus | None = None


class PhotoAdminItem(BaseModel):
    """One row of the photo list in the admin area."""

    id: int
    title: str | None
    date_label: str
    place_name: str | None
    thumb_url: str
    needs_location: bool
    needs_date: bool
    status: str
    original_filename: str
    imported_at: datetime

    @classmethod
    def from_photo(cls, photo: Photo) -> "PhotoAdminItem":
        return cls(
            id=photo.id,
            title=photo.title,
            date_label=format_label(photo.date_from, photo.date_to, photo.date_precision),
            place_name=photo.place_name,
            thumb_url=f"/api/photos/{photo.id}/thumb?size=240",
            needs_location=photo.needs_location,
            needs_date=photo.needs_date,
            status=photo.status,
            original_filename=photo.original_filename,
            imported_at=photo.imported_at,
        )


class PhotoAdminList(BaseModel):
    photos: list[PhotoAdminItem]
    #: Total matching the filter, not just the page returned.
    total: int


class ChangeItem(BaseModel):
    """One visitor contribution, as the curator sees it."""

    id: int
    photo_id: int
    photo_title: str | None
    thumb_url: str
    field: str
    old_value: str | None
    new_value: str | None
    source: str
    created_at: datetime
    reverted_at: datetime | None
    #: False when the field has since been curated -- reverting would then destroy that work.
    revertable: bool


class ImportLogItem(BaseModel):
    id: int
    #: Just the file name: the full path leads into a container or a temp folder and helps nobody.
    filename: str
    result: str
    message: str | None
    photo_id: int | None
    created_at: datetime

    @classmethod
    def from_entry(cls, entry: ImportLog) -> "ImportLogItem":
        return cls(
            id=entry.id,
            filename=entry.path.rsplit("/", 1)[-1],
            result=entry.result,
            message=entry.message,
            photo_id=entry.photo_id,
            created_at=entry.created_at,
        )


class BackupReminder(BaseModel):
    """Nudge for the start page: "Letzte Sicherung vor 34 Tagen". Never an automatism."""

    last_backup_at: datetime | None
    last_drive: str
    days_since: int | None
    #: True when it is time, and also when there has never been a backup at all.
    overdue: bool


class BackupOnDrive(BaseModel):
    created_at: datetime
    photos: int
    bytes: int
    place: str


class DriveItem(BaseModel):
    path: str
    name: str
    total_bytes: int
    free_bytes: int
    #: Enough room for the whole collection, not just for what is still missing.
    enough_space: bool
    #: What is already on this stick, if anything.
    backup: BackupOnDrive | None


class DriveList(BaseModel):
    drives: list[DriveItem]
    #: How many photos would be written, and how much room that takes.
    photos: int
    needed_bytes: int
    reminder: BackupReminder


class DriveChoice(BaseModel):
    path: str


class JobState(BaseModel):
    """How far along backup or restore is."""

    kind: str
    phase: str
    done: int
    total: int
    #: German -- goes straight onto the screen.
    message: str
    error: str | None


class Overview(BaseModel):
    """The numbers on the admin start page."""

    total: int
    #: Photos with both a place and a date -- only those appear on the map.
    on_map: int
    without_location: int
    without_date: int
    hidden: int
    #: Visitor contributions not yet reverted. Something to look through, not a problem.
    visitor_changes: int
    last_import_at: datetime | None
    #: "Letzte Sicherung vor 34 Tagen" belongs on the start page, not only in its own section.
    backup: BackupReminder


class UploadItem(BaseModel):
    """What became of one uploaded file."""

    filename: str
    result: str
    #: German -- this text goes straight into the admin's upload list.
    message: str
    #: Set for imported files and for duplicates; the duplicate points at the photo already there.
    photo: PhotoDetail | None


class UploadResult(BaseModel):
    items: list[UploadItem]
    imported: int
    #: Named rather than silently skipped: "3 waren schon da" is information, silence is not.
    duplicates: int
    rejected: int
