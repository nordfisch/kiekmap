"""The admin area.

Used once or twice a year, by volunteers, on the same touchscreen the visitors use. That shapes
three decisions:

  * A PIN instead of a password -- there is no keyboard. See app/services/auth.py for what makes
    a short secret defensible.
  * Every message in here is German. By the rule in CLAUDE.md this is admin-facing text, so it is
    written for the person at the screen, not for whoever calls the API.
  * Nothing is deleted. A photo can be hidden, a visitor contribution taken back -- both are
    reversible, and neither loses the file.
"""

import logging
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.db import get_session
from app.models import (
    Change,
    DatePrecision,
    ImportLog,
    ImportResult,
    Photo,
    PhotoStatus,
    Source,
    Tag,
)
from app.schemas import (
    BackupReminder,
    ChangeItem,
    ImportLogItem,
    LoginRequest,
    LoginResponse,
    Overview,
    PhotoAdminItem,
    PhotoAdminList,
    PhotoDetail,
    PhotoUpdate,
    UploadItem,
    UploadResult,
)
from app.services import auth, dates
from app.services.backup import read_state as read_backup_state
from app.services.dates import date_range, format_label
from app.services.importer import apply_batch_defaults, import_upload, upload_name

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

TOKEN_HEADER = "X-Admin-Token"

#: Page size of the photo list. Large enough that scrolling beats paging on a touchscreen.
DEFAULT_PAGE = 60
MAX_PAGE = 300


# --- signing in -------------------------------------------------------------


def require_admin(
    token: Annotated[str | None, Header(alias=TOKEN_HEADER)] = None,
) -> auth.AdminSession:
    """Guard for everything below. Renews the session on the way through."""
    session = auth.sessions.renew(token) if token else None
    if session is None:
        raise HTTPException(401, "Die Anmeldung ist abgelaufen. Bitte noch einmal anmelden.")
    return session


Admin = Annotated[auth.AdminSession, Depends(require_admin)]
Db = Annotated[Session, Depends(get_session)]
Config = Annotated[Settings, Depends(get_settings)]


@router.post("/login", response_model=LoginResponse, summary="Sign in with the PIN")
def login(request: LoginRequest, settings: Config) -> LoginResponse:
    if not settings.admin_pin_hash:
        raise HTTPException(
            503,
            "Es ist noch keine PIN eingerichtet. Sie wird am Rechner gesetzt, "
            "mit: python -m app.cli pin",
        )

    if (locked := auth.attempts.locked_for()) > 0:
        raise HTTPException(429, f"Zu viele Versuche. Bitte {locked} Sekunden warten.")

    if not auth.verify_pin(request.pin, settings.admin_pin_hash):
        if locked := auth.attempts.record_failure():
            raise HTTPException(429, f"Zu viele Versuche. Bitte {locked} Sekunden warten.")
        raise HTTPException(401, "Die PIN stimmt nicht.")

    auth.attempts.reset()
    session = auth.sessions.issue()
    log.info("Admin signed in")
    return LoginResponse(token=session.token, expires_in_s=session.expires_in_s)


@router.post("/logout", status_code=204, summary="Sign out")
def logout(admin: Admin) -> None:
    auth.sessions.revoke(admin.token)
    log.info("Admin signed out")


@router.get("/session", response_model=LoginResponse, summary="Is the token still good?")
def session_state(admin: Admin) -> LoginResponse:
    """Called after a reload, so the browser does not have to ask for the PIN again."""
    return LoginResponse(token=admin.token, expires_in_s=admin.expires_in_s)


# --- overview ---------------------------------------------------------------


@router.get("/overview", response_model=Overview, summary="Counts for the admin start page")
def overview(admin: Admin, session: Db, settings: Config) -> Overview:
    def count(*filters) -> int:
        return session.scalar(select(func.count()).select_from(Photo).where(*filters)) or 0

    last_import: datetime | None = session.scalar(
        select(func.max(ImportLog.created_at)).where(ImportLog.result == ImportResult.IMPORTED)
    )
    # Only what still stands: the tile leads into the moderation list, and it would be a poor
    # signpost if it announced a contribution that has since been taken back.
    last_change: datetime | None = session.scalar(
        select(func.max(Change.created_at)).where(
            Change.source == Source.VISITOR, Change.reverted_at.is_(None)
        )
    )
    backup_state = read_backup_state(settings)

    return Overview(
        total=count(),
        # Both are needed for the map: the view filters on place and time at once.
        on_map=count(
            Photo.lat.is_not(None),
            Photo.date_from.is_not(None),
            Photo.status == PhotoStatus.PUBLISHED,
        ),
        without_location=count(Photo.lat.is_(None)),
        without_date=count(Photo.date_from.is_(None)),
        hidden=count(Photo.status == PhotoStatus.HIDDEN),
        visitor_changes=session.scalar(
            select(func.count())
            .select_from(Change)
            .where(Change.source == Source.VISITOR, Change.reverted_at.is_(None))
        )
        or 0,
        days_since_import=dates.days_since(last_import) if last_import else None,
        days_since_change=dates.days_since(last_change) if last_change else None,
        backup=BackupReminder(
            last_backup_at=backup_state.last_backup_at,
            last_drive=backup_state.last_drive,
            days_since=backup_state.days_since,
            overdue=backup_state.overdue,
        ),
    )


# --- photo care -------------------------------------------------------------

# Ort und Jahr getrennt, nicht als ein "unvollstaendig": Verorten und Datieren sind zwei
# verschiedene Arbeiten. Wer die Fotos ohne Ort abarbeitet, will die ohne Jahr nicht dazwischen.
Selection = Literal["all", "without_location", "without_date", "hidden"]


@router.get("/photos", response_model=PhotoAdminList, summary="Photo list for the admin area")
def list_photos(
    admin: Admin,
    session: Db,
    show: Annotated[Selection, Query(description="Which photos to list")] = "all",
    q: Annotated[str, Query(description="Substring of title, place or file name")] = "",
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE)] = DEFAULT_PAGE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PhotoAdminList:
    """Newest import first -- that is what someone is looking for right after an upload."""
    filters = []
    if show == "without_location":
        filters.append(Photo.lat.is_(None))
    elif show == "without_date":
        filters.append(Photo.date_from.is_(None))
    elif show == "hidden":
        filters.append(Photo.status == PhotoStatus.HIDDEN)

    if term := q.strip():
        pattern = f"%{term}%"
        filters.append(
            or_(
                Photo.title.ilike(pattern),
                Photo.place_name.ilike(pattern),
                Photo.original_filename.ilike(pattern),
            )
        )

    total = session.scalar(select(func.count()).select_from(Photo).where(*filters)) or 0
    photos = session.scalars(
        select(Photo)
        .where(*filters)
        .order_by(Photo.imported_at.desc(), Photo.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return PhotoAdminList(photos=[PhotoAdminItem.from_photo(p) for p in photos], total=total)


def _get_photo(session: Session, photo_id: int) -> Photo:
    photo = session.scalar(
        select(Photo).where(Photo.id == photo_id).options(selectinload(Photo.tags))
    )
    if photo is None:
        raise HTTPException(404, f"Kein Foto mit der Nummer {photo_id}")
    return photo


def _record(session: Session, photo: Photo, field: str, old: str | None, new: str | None) -> None:
    """Log a curator's edit.

    Same log as the visitor contributions, so the history of a photo reads in one place. Curator
    entries are not offered for reverting -- see ``revert_change``.
    """
    if old == new:
        return
    session.add(
        Change(photo_id=photo.id, field=field, old_value=old, new_value=new, source=Source.CURATOR)
    )


def _location_label(photo: Photo) -> str | None:
    if photo.lat is None or photo.lon is None:
        return None
    name = f" ({photo.place_name})" if photo.place_name else ""
    return f"{photo.lat:.6f},{photo.lon:.6f}{name}"


@router.get("/photos/{photo_id}", response_model=PhotoDetail, summary="One photo, everything")
def photo_detail(photo_id: int, admin: Admin, session: Db) -> PhotoDetail:
    return PhotoDetail.from_photo(_get_photo(session, photo_id))


@router.patch("/photos/{photo_id}", response_model=PhotoDetail, summary="Edit a photo")
def update_photo(photo_id: int, update: PhotoUpdate, admin: Admin, session: Db) -> PhotoDetail:
    """Change what was supplied and leave the rest alone.

    A field that is absent from the request stays as it is; a field that is explicitly ``null``
    is cleared. Without that distinction a wrong dating could never be taken out again, only
    replaced -- see ``PhotoUpdate``.
    """
    photo = _get_photo(session, photo_id)
    supplied = update.model_fields_set

    if "title" in supplied:
        _record(session, photo, "title", photo.title, update.title)
        photo.title = update.title
        photo.title_source = Source.CURATOR if update.title else None

    if "description" in supplied:
        _record(session, photo, "description", photo.description, update.description)
        photo.description = update.description

    if "date" in supplied:
        previous = format_label(photo.date_from, photo.date_to, photo.date_precision)
        if update.date is None:
            photo.date_from = photo.date_to = None
            photo.date_precision = DatePrecision.UNKNOWN
            photo.date_source = None
        else:
            try:
                start, end, precision = date_range(
                    update.date.year,
                    update.date.month,
                    update.date.day,
                    DatePrecision(update.date.precision),
                )
            except ValueError:
                raise HTTPException(422, "Dieses Datum gibt es nicht.") from None
            photo.date_from, photo.date_to, photo.date_precision = start, end, precision
            photo.date_source = Source.CURATOR
        _record(
            session,
            photo,
            "date",
            previous,
            format_label(photo.date_from, photo.date_to, photo.date_precision),
        )

    if "location" in supplied:
        previous_location = _location_label(photo)
        if update.location is None:
            photo.lat = photo.lon = None
            photo.place_name = None
            photo.location_accuracy_m = None
            photo.location_source = None
        else:
            # Deliberately not checked against the region, unlike a visitor contribution. The
            # region guard exists to catch abuse at the public screen; a curator may well know
            # that a photo was taken on a trip to the next village.
            photo.lat, photo.lon = update.location.lat, update.location.lon
            photo.place_name = update.location.place_name
            photo.location_accuracy_m = update.location.accuracy_m
            photo.location_source = Source.CURATOR
        _record(session, photo, "location", previous_location, _location_label(photo))

    if "tags" in supplied:
        names = list(dict.fromkeys(name.strip() for name in (update.tags or []) if name.strip()))
        _record(
            session,
            photo,
            "tags",
            ", ".join(sorted(tag.name for tag in photo.tags)) or None,
            ", ".join(sorted(names)) or None,
        )
        photo.tags = [
            session.scalar(select(Tag).where(Tag.name == name)) or Tag(name=name) for name in names
        ]

    if "status" in supplied and update.status is not None:
        _record(session, photo, "status", photo.status, update.status)
        photo.status = update.status

    session.commit()
    session.refresh(photo)
    log.info("Curator edited photo %s", photo.id)
    return PhotoDetail.from_photo(photo)


# --- visitor contributions --------------------------------------------------
#
# Contributions are applied straight away at the kiosk -- that immediacy is what makes people
# join in. This is the counterweight: the curator sees what happened and can take it back.


def _still_from_visitor(photo: Photo, field: str) -> bool:
    """Does the field still carry what the visitor put there?

    If a curator has edited it since, the source says ``curator`` and reverting would throw that
    work away. The contribution then stays in the log as history, but without a button.
    """
    match field:
        case "location":
            return photo.location_source == Source.VISITOR
        case "date":
            return photo.date_source == Source.VISITOR
        case _:
            return False


@router.get("/changes", response_model=list[ChangeItem], summary="Visitor contributions")
def list_changes(
    admin: Admin,
    session: Db,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE)] = DEFAULT_PAGE,
    include_reverted: Annotated[
        bool, Query(description="Also list what was already taken back")
    ] = False,
) -> list[ChangeItem]:
    query = (
        select(Change, Photo)
        .join(Photo, Photo.id == Change.photo_id)
        .where(Change.source == Source.VISITOR)
        .order_by(Change.created_at.desc(), Change.id.desc())
        .limit(limit)
    )
    if not include_reverted:
        query = query.where(Change.reverted_at.is_(None))

    return [
        ChangeItem(
            id=change.id,
            photo_id=photo.id,
            photo_title=photo.title,
            thumb_url=f"/api/photos/{photo.id}/thumb?size=240",
            field=change.field,
            old_value=change.old_value,
            new_value=change.new_value,
            source=change.source,
            created_at=change.created_at,
            reverted_at=change.reverted_at,
            revertable=change.reverted_at is None and _still_from_visitor(photo, change.field),
        )
        for change, photo in session.execute(query).all()
    ]


@router.post(
    "/changes/{change_id}/revert",
    response_model=PhotoDetail,
    summary="Take back a visitor contribution",
)
def revert_change(change_id: int, admin: Admin, session: Db) -> PhotoDetail:
    """Clear the field the visitor filled.

    Clearing, not restoring: a visitor may only ever fill what was empty (see api/contribute.py),
    so the previous value is always "nothing". The photo goes back into the "Hilf mit" panel and
    can be answered again -- which is usually the point.
    """
    change = session.get(Change, change_id)
    if change is None:
        raise HTTPException(404, f"Kein Eintrag mit der Nummer {change_id}")
    if change.source != Source.VISITOR:
        raise HTTPException(409, "Das ist keine Angabe von Besuchern und bleibt daher stehen.")
    if change.reverted_at is not None:
        raise HTTPException(409, "Das ist bereits geschehen.")

    photo = _get_photo(session, change.photo_id)
    if not _still_from_visitor(photo, change.field):
        raise HTTPException(
            409,
            "Die Angabe ist inzwischen von Hand bearbeitet worden und bleibt daher stehen.",
        )

    if change.field == "location":
        photo.lat = photo.lon = None
        photo.place_name = None
        photo.location_accuracy_m = None
        photo.location_source = None
    else:
        photo.date_from = photo.date_to = None
        photo.date_precision = DatePrecision.UNKNOWN
        photo.date_source = None

    change.reverted_at = datetime.now()
    session.commit()
    session.refresh(photo)
    log.info("Curator reverted visitor contribution %s on photo %s", change.id, photo.id)
    return PhotoDetail.from_photo(photo)


# --- import log -------------------------------------------------------------


@router.get("/imports", response_model=list[ImportLogItem], summary="Import log")
def import_log(
    admin: Admin,
    session: Db,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE)] = DEFAULT_PAGE,
    result: Annotated[ImportResult | None, Query(description="Only this outcome")] = None,
) -> list[ImportLogItem]:
    query = select(ImportLog).order_by(ImportLog.created_at.desc(), ImportLog.id.desc())
    if result is not None:
        query = query.where(ImportLog.result == result)
    return [ImportLogItem.from_entry(entry) for entry in session.scalars(query.limit(limit)).all()]


# --- batch upload -----------------------------------------------------------


@router.post("/upload", response_model=UploadResult, summary="Upload photos")
def upload(
    admin: Admin,
    session: Db,
    settings: Config,
    files: Annotated[list[UploadFile], File(description="One or more image files")],
    year: Annotated[int | None, Form(ge=1800, le=2100)] = None,
    precision: Annotated[DatePrecision, Form()] = DatePrecision.YEAR,
    lat: Annotated[float | None, Form(ge=-90, le=90)] = None,
    lon: Annotated[float | None, Form(ge=-180, le=180)] = None,
    place_name: Annotated[str | None, Form(max_length=300)] = None,
) -> UploadResult:
    """Take in a batch, optionally dating and locating all of it at once.

    The form fields apply to every file in the request. For forty photos of one church fair that
    is the whole difference between one entry and forty.

    They only fill what the import left empty. A scan almost never brings a usable date or GPS
    with it, so in practice they apply to everything -- but where the file does know better, the
    file wins, and the row can still be corrected afterwards.

    The endpoint takes a list so a script can post a whole folder. The admin area sends one file
    per request instead, because that is what gives the person at the screen a progress count.
    """
    items: list[UploadItem] = []

    for upload_file in files:
        name = upload_name(upload_file.filename or "upload")
        outcome = import_upload(session, name, upload_file.file, settings)

        if outcome.succeeded and outcome.photo is not None:
            apply_batch_defaults(outcome.photo, year, precision, lat, lon, place_name)

        session.commit()
        if outcome.photo is not None:
            session.refresh(outcome.photo)

        items.append(
            UploadItem(
                filename=name,
                result=outcome.result,
                message=outcome.message,
                photo=PhotoDetail.from_photo(outcome.photo) if outcome.photo else None,
            )
        )

    counts = {result: 0 for result in ImportResult}
    for item in items:
        counts[ImportResult(item.result)] += 1

    log.info("Upload: %s files, %s imported", len(items), counts[ImportResult.IMPORTED])
    return UploadResult(
        items=items,
        imported=counts[ImportResult.IMPORTED],
        duplicates=counts[ImportResult.DUPLICATE],
        rejected=counts[ImportResult.REJECTED],
    )
