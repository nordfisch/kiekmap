"""API payload shapes."""

from datetime import date, datetime
from typing import Self

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
    """Everything about one photo that a visitor may see.

    The admin area gets ``PhotoAdminDetail`` on top of this. What is *not* here is the point:
    ``provenance`` is missing, so the public endpoint cannot leak it even by accident.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    description: str | None
    #: Credit line, shown under the description in the overlay.
    credit: str | None

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
    def from_photo(cls, photo: Photo) -> Self:
        return cls(**cls._values(photo))

    @classmethod
    def _values(cls, photo: Photo) -> dict:
        """Split out from ``from_photo`` so a subclass can add to it instead of repeating it."""
        return dict(
            id=photo.id,
            title=photo.title,
            description=photo.description,
            credit=photo.credit,
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


class PhotoAdminDetail(PhotoDetail):
    """The same photo, as the curator sees it.

    ``provenance`` is the reason this class exists. Who lent the picture and whether a release
    was given is a note for the museum, not for the screen in the exhibition room -- and the
    surest way to keep it off that screen is a public schema that has no field for it.
    """

    provenance: str | None

    @classmethod
    def _values(cls, photo: Photo) -> dict:
        return {**super()._values(photo), "provenance": photo.provenance}


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
    """The bars behind the time slider -- and the axis they hang on.

    The two are scoped differently on purpose, which is why they are not called ``earliest`` and
    ``latest`` any more: the bars belong to the viewport, the axis to the whole collection.
    """

    decades: list[DecadeCount]
    #: Photos without a date. In no time selection, but in the "Hilf mit" panel.
    undated: int
    #: Span of the whole collection, deliberately **not** of the viewport: the slider axis must not
    #: move under the visitor's hand while they pan the map. See frontend kiosk/zeitachse.ts.
    collection_from: int | None
    collection_to: int | None


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
    #: Open tasks of the *other* kind. Tells the panel whether "Weiß ich nicht" still leads
    #: anywhere -- with nothing else left, the same photo would simply come back.
    open_other: int
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
    credit: str | None = Field(default=None, max_length=200)
    provenance: str | None = None
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


class ChangeList(BaseModel):
    changes: list[ChangeItem]
    #: Total matching the filter, not just the page returned -- the page count is built from it.
    total: int


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


class ImportLogList(BaseModel):
    entries: list[ImportLogItem]
    #: Total matching the filter, not just the page returned.
    total: int


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


class ImportFolderItem(BaseModel):
    """A folder on a plugged-in drive that holds images."""

    path: str
    #: Relative to the drive, so it is recognisable: "Scans2024/Kirchweih".
    name: str
    drive: str
    images: int


class ImportFolders(BaseModel):
    """What could be taken in -- and, separately, whether anything is plugged in at all.

    Without the drive names an empty folder list would mean two different things: no stick, or a
    stick without images. The screen would then tell someone who has just plugged one in to plug
    one in -- the kind of dead end where a volunteer gives up.
    """

    drives: list[str]
    folders: list[ImportFolderItem]


class ImportRequest(DriveChoice):
    """Which folder to take in, and what applies to all of it."""

    year: int | None = Field(default=None, ge=1800, le=2100)
    precision: DatePrecision = DatePrecision.YEAR
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)
    place_name: str | None = Field(default=None, max_length=300)
    #: A box of scans usually comes from one person -- so both of these belong to the whole batch.
    credit: str | None = Field(default=None, max_length=200)
    provenance: str | None = None


class JobState(BaseModel):
    """How far along backup or restore is."""

    kind: str
    phase: str
    done: int
    total: int
    #: German -- goes straight onto the screen.
    message: str
    error: str | None
    #: Rows for the review table, when the finished job produced few enough to be worth showing.
    #: See REVIEW_LIMIT in app/api/backup.py.
    items: list["UploadItem"] | None = None


class Overview(BaseModel):
    """The numbers on the admin start page."""

    total: int
    #: Photos with both a place and a date -- only those appear on the map.
    on_map: int
    without_location: int
    without_date: int
    #: Geloescht heisst hier: aus der Ausstellung genommen. Datei und Zeile bleiben.
    deleted: int
    #: Visitor contributions not yet reverted. Something to look through, not a problem.
    visitor_changes: int
    #: Days, not timestamps: the start page asks "wie lange ist das her?", and the answer depends
    #: on where the day boundary lies -- a question the browser cannot answer, because a stored
    #: stamp carries no time zone and JavaScript would read it as local time. See
    #: services/dates.days_since.
    days_since_import: int | None
    days_since_change: int | None
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
