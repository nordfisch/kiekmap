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
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.models import Change, DatePrecision, Photo, PhotoStatus, Place, Source
from app.schemas import (
    DateContribution,
    HouseNumberContribution,
    LocationContribution,
    PhotoDetail,
    PlaceOut,
    TaskResponse,
)
from app.services import places
from app.services.dates import date_range, format_label
from app.services.needs import NEEDS, Need, open_filter
from app.services.places import ACCURACY_ADDRESS_M
from app.text import texts

log = logging.getLogger(__name__)
router = APIRouter(prefix="/contribute", tags=["contribute"])


@router.get("/next", response_model=TaskResponse, summary="A photo that is missing something")
def next_task(
    session: Annotated[Session, Depends(get_session)],
    need: Annotated[Need, Query(description="Which field should be missing")] = "location",
    exclude: Annotated[str, Query(description="Ids already shown, comma-separated")] = "",
    photo_id: Annotated[
        int | None, Query(description="Put up this photo, if it still owes this answer")
    ] = None,
) -> TaskResponse:
    """Return a random photo that is missing exactly this field.

    ``exclude`` holds the photos the visitor has just dismissed. Without that list the same image
    could reappear immediately, which feels broken.

    ``photo_id`` is a **wish, not an instruction**, and it comes from the detail view: whoever
    looks at one photograph full screen and taps "Wann war das?" means that one. Two rules keep the
    wish honest:

    * **It is checked against the same filter as any other photo.** A photo that no longer owes
      this answer -- because somebody else was quicker between the tap and this request -- would
      otherwise put a question on the screen that the write path then rejects with 409.
    * **Where it does not hold, the ordinary random pick runs.** Better a different photo than a
      dead end.

    ``exclude`` does *not* apply to it. Whoever asks for a photo by name may well have waved it
    away earlier and has now thought better of it.
    """
    skipped = {int(part) for part in exclude.split(",") if part.strip().isdigit()}

    filters = [Photo.status == PhotoStatus.PUBLISHED, open_filter(need)]
    open_count = session.scalar(select(func.count()).select_from(Photo).where(*filters)) or 0

    # What the *other* questions still hold: from it the screen decides whether "Weiss ich nicht"
    # still leads anywhere at all. With nothing else open the same photo would come back.
    #
    # A sum over all of them rather than the count of one -- with three questions a single count
    # would answer a narrower question than the panel is asking.
    open_other = sum(
        session.scalar(
            select(func.count())
            .select_from(Photo)
            .where(Photo.status == PhotoStatus.PUBLISHED, open_filter(other))
        )
        or 0
        for other in NEEDS
        if other != need
    )

    photo = None
    if photo_id is not None:
        photo = session.scalar(select(Photo).where(*filters, Photo.id == photo_id))

    if photo is None:
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


def _refinable(session: Session, photo: Photo) -> bool:
    """Is this exactly the photo the sharpening question is for?

    Asked of one photo rather than of the collection, so the same sentence decides who gets the
    question in the panel and who gets the buttons in the detail view. One rule, two readers.
    """
    return (
        session.scalar(
            select(func.count())
            .select_from(Photo)
            .where(Photo.id == photo.id, open_filter("housenumber"))
        )
        or 0
    ) > 0


@router.get(
    "/{photo_id}/housenumbers",
    response_model=list[PlaceOut],
    summary="House numbers a visitor may sharpen this photo to",
)
def photo_housenumbers(
    photo_id: int, session: Annotated[Session, Depends(get_session)]
) -> list[PlaceOut]:
    """The numbers of this photo's street -- **empty unless the photo may be sharpened at all**.

    That emptiness is the gate, and it is deliberately the only one: the detail view offers the
    picker when this list is not empty and needs no second rule of its own. A rule that lives in
    two places is a rule that will disagree with itself.
    """
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(404, texts().photos.no_such_photo(photo_id))
    if not _refinable(session, photo):
        return []
    return [
        PlaceOut.from_place(place)
        for place in places.housenumbers_of(session, photo.place_name or "")
    ]


def _require_in_region(settings: Settings, lat: float, lon: float) -> None:
    """The pin can only be dropped on the map, and the map only shows the region -- check anyway.

    The API is reachable, and a photo in the Pacific would have vanished from the view without
    anyone noticing why. Pulled out rather than copied: the sharpening route takes its coordinate
    from the gazetteer, so it cannot really fail here -- but one rule with two callers stays one
    rule.
    """
    if (bbox := settings.region_bbox()) is None:
        return
    min_lon, min_lat, max_lon, max_lat = bbox
    if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
        raise HTTPException(422, texts().contribute.outside_the_map)


def _require_empty(photo: Photo, field: str) -> None:
    """A visitor may only fill what is empty.

    Curated statements are untouchable -- and without this check the next visitor could overwrite
    the previous one's statement instead of both counting as confirmation.
    """
    taken = photo.lat is not None if field == "location" else photo.date_from is not None
    if taken:
        raise HTTPException(409, texts().contribute.already_stated)


def _get_open_photo(session: Session, photo_id: int, field: str) -> Photo:
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(404, texts().photos.no_such_photo(photo_id))
    _require_empty(photo, field)
    return photo


def _log_change(
    session: Session,
    photo: Photo,
    field: str,
    old: str | None,
    new: str,
    session_key: str | None,
    old_source: str | None = None,
) -> None:
    """Record the contribution for moderation.

    ``old`` is None for the two routes that only fill what is empty -- there is nothing to restore,
    and taking such a contribution back means clearing the field. The sharpening route is the one
    that overwrites, so it passes both the previous value and where it came from; without them a
    revert would drop the photo's location entirely and turn a curator's statement into a
    visitor's.
    """
    session.add(
        Change(
            photo_id=photo.id,
            field=field,
            old_value=old,
            old_source=old_source,
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
    _require_in_region(settings, contribution.lat, contribution.lon)

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


@router.post(
    "/{photo_id}/housenumber",
    response_model=PhotoDetail,
    summary="Sharpen a street-precise photo to one house",
)
def add_housenumber(
    photo_id: int,
    contribution: HouseNumberContribution,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PhotoDetail:
    """Move a photo from the middle of its street to one of its houses.

    **The exception to "visitors only fill what is empty"** (decisions.md, point 5) -- and it goes
    through its own door rather than loosening that check. ``_require_empty`` still reads exactly
    as it did; what stands beside it is a narrower rule: only street-precise, only to an address
    of that same street, and never the other way round.

    Curator statements may be sharpened too. That is a real widening, and it is why the change log
    carries the previous source: taking the contribution back has to give a curator's statement
    back to the curator.
    """
    photo = session.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(404, texts().photos.no_such_photo(photo_id))
    if not _refinable(session, photo):
        raise HTTPException(409, texts().contribute.already_more_precise)

    address = session.get(Place, contribution.place_id)
    if address is None or address.kind != "adresse":
        raise HTTPException(404, texts().contribute.housenumber_unknown)
    if address.street != photo.place_name:
        raise HTTPException(422, texts().contribute.housenumber_wrong_street)

    _require_in_region(settings, address.lat, address.lon)

    street = photo.place_name
    previous_source = photo.location_source

    # Everything from the gazetteer row, nothing from the request.
    photo.lat = address.lat
    photo.lon = address.lon
    photo.place_name = address.name
    photo.location_accuracy_m = ACCURACY_ADDRESS_M
    photo.location_source = Source.VISITOR

    _log_change(
        session,
        photo,
        "housenumber",
        street,
        address.name,
        contribution.session_id,
        old_source=previous_source,
    )
    session.commit()
    session.refresh(photo)

    log.info("Visitor contribution: photo %s sharpened to %s", photo.id, address.name)
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
