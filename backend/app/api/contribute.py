"""The "Hilf mit" panel: visitors fill in missing statements.

For historical scans, place and year are nowhere in the file. Someone who knows the village often
knows them at a glance. This path is therefore not a side feature but the main way the system
acquires data.

Contributions are applied **straight away** -- the immediate effect is what makes it appealing.
Three things catch the abuse case without slowing down the normal one:

  1. Only empty fields may be filled. What a curator set is untouchable.
  2. Coordinates must lie inside the region. Otherwise a photo ends up in the Pacific.
  3. Every change lands in ``changes`` and can be reverted individually in the admin area.
"""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.models import Change, DatePrecision, Photo, PhotoStatus, Source
from app.schemas import DateContribution, LocationContribution, PhotoDetail, TaskResponse
from app.services.dates import date_range, format_label

log = logging.getLogger(__name__)
router = APIRouter(prefix="/contribute", tags=["hilf mit"])

Need = Literal["location", "date"]


def _missing_filter(need: Need):
    return Photo.lat.is_(None) if need == "location" else Photo.date_from.is_(None)


@router.get("/next", response_model=TaskResponse, summary="A photo that is missing something")
def next_task(
    session: Annotated[Session, Depends(get_session)],
    need: Annotated[Need, Query(description="Which field should be missing")] = "location",
    exclude: Annotated[str, Query(description="Ids already shown, comma-separated")] = "",
) -> TaskResponse:
    """Return a random photo that is missing exactly this field.

    ``exclude`` holds the photos the visitor has just dismissed. Without that list the same image
    could reappear immediately, which feels broken.
    """
    skipped = {int(part) for part in exclude.split(",") if part.strip().isdigit()}

    filters = [Photo.status == PhotoStatus.PUBLISHED, _missing_filter(need)]
    open_count = session.scalar(select(func.count()).select_from(Photo).where(*filters)) or 0

    # Count the other question too: from it the screen decides whether "Weiss ich nicht" still
    # leads anywhere at all. With nothing else open the same photo would come back.
    other: Need = "date" if need == "location" else "location"
    open_other = (
        session.scalar(
            select(func.count())
            .select_from(Photo)
            .where(Photo.status == PhotoStatus.PUBLISHED, _missing_filter(other))
        )
        or 0
    )

    query = select(Photo).where(*filters)
    if skipped:
        query = query.where(Photo.id.notin_(skipped))

    photo = session.scalar(query.order_by(func.random()).limit(1))

    # Everything seen: start over rather than reporting "nothing left", as long as anything is
    # still open at all.
    if photo is None and skipped and open_count:
        photo = session.scalar(select(Photo).where(*filters).order_by(func.random()).limit(1))

    return TaskResponse(
        need=need,
        open_count=open_count,
        open_other=open_other,
        photo=PhotoDetail.from_photo(photo) if photo else None,
    )


def _require_empty(photo: Photo, field: str) -> None:
    """A visitor may only fill what is empty.

    Curated statements are untouchable -- and without this check the next visitor could overwrite
    the previous one's statement instead of both counting as confirmation.
    """
    taken = photo.lat is not None if field == "location" else photo.date_from is not None
    if taken:
        raise HTTPException(
            409,
            "Dieses Foto hat inzwischen schon eine Angabe bekommen. Vielen Dank trotzdem!",
        )


def _get_open_photo(session: Session, photo_id: int, field: str) -> Photo:
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(404, f"Kein Foto mit der Nummer {photo_id}")
    _require_empty(photo, field)
    return photo


def _log_change(
    session: Session,
    photo: Photo,
    field: str,
    old: str | None,
    new: str,
    session_key: str | None,
) -> None:
    session.add(
        Change(
            photo_id=photo.id,
            field=field,
            old_value=old,
            new_value=new,
            source=Source.VISITOR,
            session_id=session_key,
        )
    )


@router.post("/{photo_id}/location", response_model=PhotoDetail, summary="Add a location")
def add_location(
    photo_id: int,
    contribution: LocationContribution,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PhotoDetail:
    photo = _get_open_photo(session, photo_id, "location")

    # The pin can only be dropped on the map, and the map only shows the region -- check anyway:
    # the API is reachable, and a photo in the Pacific would have vanished from the view without
    # anyone noticing why.
    if (bbox := settings.region_bbox()) is not None:
        min_lon, min_lat, max_lon, max_lat = bbox
        if not (min_lat <= contribution.lat <= max_lat and min_lon <= contribution.lon <= max_lon):
            raise HTTPException(422, "Dieser Ort liegt ausserhalb der Karte.")

    photo.lat = contribution.lat
    photo.lon = contribution.lon
    photo.location_source = Source.VISITOR
    if contribution.place_name:
        photo.place_name = contribution.place_name
    if contribution.accuracy_m is not None:
        photo.location_accuracy_m = contribution.accuracy_m

    _log_change(
        session,
        photo,
        "location",
        None,
        f"{contribution.lat:.6f},{contribution.lon:.6f}"
        + (f" ({contribution.place_name})" if contribution.place_name else ""),
        contribution.session_id,
    )
    session.commit()
    session.refresh(photo)

    log.info("Visitor contribution: photo %s located", photo.id)
    return PhotoDetail.from_photo(photo)


@router.post("/{photo_id}/date", response_model=PhotoDetail, summary="Add a year")
def add_date(
    photo_id: int,
    contribution: DateContribution,
    session: Annotated[Session, Depends(get_session)],
) -> PhotoDetail:
    photo = _get_open_photo(session, photo_id, "date")

    start, end, precision = date_range(
        contribution.year,
        contribution.month,
        contribution.day,
        DatePrecision(contribution.precision),
    )
    photo.date_from, photo.date_to, photo.date_precision = start, end, precision
    photo.date_source = Source.VISITOR

    _log_change(
        session, photo, "date", None, format_label(start, end, precision), contribution.session_id
    )
    session.commit()
    session.refresh(photo)

    log.info("Visitor contribution: photo %s dated to %s", photo.id, photo.date_from)
    return PhotoDetail.from_photo(photo)
