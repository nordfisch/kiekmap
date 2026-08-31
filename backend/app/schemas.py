"""API payload shapes."""

from datetime import UTC, date, datetime
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.models import DatePrecision, ImportLog, Photo, PhotoStatus, Place
from app.services.dates import format_label, format_short
from app.services.places import ACCURACY_ADDRESS_M, ACCURACY_STREET_M


def _as_utc(value: datetime) -> datetime:
    """Say out loud what a stored timestamp already is."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


#: A stored timestamp on its way out -- and the marker that makes it readable at the other end.
#:
#: Everything this program stores is UTC: SQLite's ``func.now()``, the JSON state files,
#: ``dates.utc_now``. Written out without a time zone, that is a trap rather than a value --
#: ``new Date("2026-08-18T19:25:21")`` reads a marker-less ISO time as **local** by specification,
#: so the admin area showed every visitor contribution and every import two hours before it
#: happened, and a backup made after 22:00 UTC on the day before it was made.
#:
#: The fix belongs here rather than in the three places that display it: one end has to name the
#: zone, and the end that knows it is this one. See docs/decisions.md, point 58.
#:
#: **``Photo.exif_datetime`` deliberately does not get this**, and that is the whole subtlety: it
#: comes out of a camera or a scanner, which write the wall clock where they stood and no zone at
#: all. Reading it as local time is exactly right; stamping UTC on it would move a scan of 14:00
#: to 16:00 and invent a fact.
UtcDatetime = Annotated[datetime, AfterValidator(_as_utc)]


class PhotoMarker(BaseModel):
    """What the map needs per photo -- and no more.

    Deliberately narrow: with several hundred markers in view the response size matters, and
    description, tags and origin fields are only needed once a photo is tapped.

    **``place_name`` is the one deliberate exception to that narrowness.** It is what stands under
    the thumbnail, and the rule above would have kept it out. The cost was measured rather than
    guessed: no address in this collection exceeds thirty characters, so five hundred markers add
    some 13 kB -- on a device that serves its own map from the next room. The rule holds for
    everything else.
    """

    id: int
    lat: float
    lon: float
    title: str | None
    #: The address, as it stands under the thumbnail. Absent for a photo located from EXIF alone.
    place_name: str | None
    #: Ready-made German label ("1932", "1920er") so the frontend does no date arithmetic.
    #: Spelled out, for screen readers -- what is *shown* is ``date_short``.
    date_label: str
    #: The same dating as it fits on a map: the year, a decade as "1930er", undated empty.
    date_short: str
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
            place_name=photo.place_name,
            date_label=format_label(photo.date_from, photo.date_to, photo.date_precision),
            date_short=format_short(photo.date_from, photo.date_precision),
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
    #: The photo's identity independent of any database -- the file name is this hash. A rebuilt
    #: collection hands out new running numbers, but the same scan keeps its hash. The overlay
    #: shows the first eight characters, and the admin search finds a photo by them.
    sha256: str
    width: int
    height: int
    bytes: int
    imported_at: UtcDatetime

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
            sha256=photo.sha256,
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


class Bar(BaseModel):
    """One bar in the histogram behind the time slider."""

    year: int = Field(description="First year the bar covers, e.g. 1920 or 2014")
    count: int


class Histogram(BaseModel):
    """The bars behind the time slider -- and the axis they hang on.

    The two are scoped differently on purpose, which is why they are not called ``earliest`` and
    ``latest`` any more: the bars belong to the viewport, the axis to the whole collection.
    """

    bars: list[Bar]
    #: How many years one bar covers. Follows the collection rather than being fixed at a decade --
    #: see ``bar_width`` in services/dates.py for why that matters.
    step: int
    #: Photos without a date. In no time selection, but in the "Hilf mit" panel.
    undated: int
    #: Span of the whole collection, deliberately **not** of the viewport: the slider axis must not
    #: move under the visitor's hand while they pan the map. See frontend kiosk/timeAxis.ts.
    collection_from: int | None
    collection_to: int | None


class PlaceOut(BaseModel):
    """One row of the gazetteer, as the panel needs it."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lat: float
    lon: float
    kind: str
    #: Only for kind="adresse": the number on its own, for a button that says "12" rather than
    #: "Mühlenweg 12".
    housenumber: str | None = None
    #: How precise this point is, in metres. Travels along with a visitor's contribution.
    accuracy_m: int | None = None

    @classmethod
    def from_place(cls, place: Place) -> "PlaceOut":
        # Derived from the kind rather than stored: a row either names a house or a street, and
        # the distinction is what the kind already says.
        accuracy = ACCURACY_ADDRESS_M if place.kind == "adresse" else ACCURACY_STREET_M
        return cls(
            id=place.id,
            name=place.name,
            lat=place.lat,
            lon=place.lon,
            kind=place.kind,
            housenumber=place.housenumber,
            accuracy_m=accuracy,
        )


class DateInput(BaseModel):
    """What a visitor or curator may state as a date."""

    year: int = Field(ge=1800, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)
    precision: DatePrecision = DatePrecision.YEAR


# --- the "Hilf mit" panel ---------------------------------------------------


class LocationContribution(BaseModel):
    """A visitor drops the pin."""

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    place_name: str | None = Field(default=None, max_length=300)
    #: Mark a rough statement ("somewhere by the village pond").
    accuracy_m: int | None = Field(default=None, ge=0, le=100_000)
    #: Distinguishes visitors at the same device without identifying them.
    session_id: str | None = Field(default=None, max_length=64)


class HouseNumberContribution(BaseModel):
    """A visitor sharpens a street-precise photo to one house.

    **No coordinate, no accuracy -- deliberately.** ``LocationContribution`` takes both from the
    client, and that is harmless there only because the field it writes to has to be empty. The
    moment accuracy decided what may be overwritten, it would become a key the client holds: a
    call claiming one metre could replace anything. So the visitor names a row of the gazetteer
    and the server reads the coordinate off it.
    """

    place_id: int
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
    imported_at: UtcDatetime

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
    created_at: UtcDatetime
    reverted_at: UtcDatetime | None
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
    created_at: UtcDatetime

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

    last_backup_at: UtcDatetime | None
    last_drive: str
    days_since: int | None
    #: True when it is time, and also when there has never been a backup at all.
    overdue: bool


class DownloadTicket(BaseModel):
    """A one-shot permit for the archive download. See app/services/auth.py, TicketStore."""

    ticket: str
    expires_in_s: int


class BackupOnDrive(BaseModel):
    created_at: UtcDatetime
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


class WaitingBackup(BackupOnDrive):
    """A backup lying in the inbox and waiting to be confirmed.

    It travels along with the drive query the backup area makes every few seconds anyway -- a
    second polling loop for it would be effort without gain.
    """

    #: The file name. It goes back on restore so that the file finally taken is exactly the one
    #: that stood on screen -- and not one that has arrived in the meantime.
    file: str


class DriveList(BaseModel):
    drives: list[DriveItem]
    #: How many photos would be written, and how much room that takes.
    photos: int
    needed_bytes: int
    reminder: BackupReminder
    #: A backup waiting in the inbox to be confirmed.
    incoming: WaitingBackup | None = None


class DriveChoice(BaseModel):
    path: str


class IncomingChoice(BaseModel):
    """Which file from the inbox is to be restored."""

    file: str = Field(max_length=255)


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
    #: Keywords for the whole batch, separated by commas. Unlike the fields above they are *added*
    #: to what the file itself brought, because a keyword list is a set -- see
    #: ``importer.apply_batch_defaults``.
    tags: str | None = Field(default=None, max_length=200)


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
    #: Published photos with a place. A date is not required: without a time filter -- the normal
    #: case -- undated photos are on the map too. See the comment in api/admin.overview.
    on_map: int
    without_location: int
    without_date: int
    #: Deleted here means: taken out of the exhibition. File and row stay.
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
