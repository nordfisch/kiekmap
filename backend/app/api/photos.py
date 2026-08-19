"""Query and serve photos."""

import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy import Integer, and_, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.db import get_session
from app.models import DatePrecision, Photo, PhotoStatus, Tag
from app.schemas import Bar, Histogram, PhotoDetail, PhotoList, PhotoMarker
from app.services.dates import bar_width
from app.services.storage import (
    THUMBNAIL_SIZES,
    original_path,
    suffix_for_mime,
    thumbnail_path,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/photos", tags=["fotos"])

#: Upper bound per query. More markers than this make no sense on a map anyway, and the response
#: should go through in one go on a Pi.
MAX_LIMIT = 2000

#: The file name is the content hash, so an equal name guarantees equal content. The browser may
#: therefore cache indefinitely.
CACHE_IMMUTABLE = "public, max-age=31536000, immutable"


class Viewport:
    """Map viewport and time range as they arrive in the query string.

    Note on the language of error messages, here and elsewhere: the rule is "could this reach
    the kiosk or the admin area? then German, otherwise English". The bbox errors below can
    only ever be seen by someone working against the API -- the frontend always sends a valid
    one. The 404 further down, by contrast, shows up in the visitor's photo overlay.
    """

    def __init__(
        self,
        bbox: Annotated[
            str,
            Query(
                description="minLon,minLat,maxLon,maxLat in WGS84",
                examples=["9.60,53.57,9.75,53.67"],
            ),
        ],
        from_year: Annotated[
            int | None, Query(ge=1800, le=2100, description="Earliest year to include")
        ] = None,
        to_year: Annotated[
            int | None, Query(ge=1800, le=2100, description="Latest year to include")
        ] = None,
        include_undated: Annotated[
            bool,
            Query(description="Keep photos that carry no date at all, whatever the time range"),
        ] = True,
    ) -> None:
        parts = bbox.split(",")
        if len(parts) != 4:
            raise HTTPException(422, "bbox needs four comma-separated numbers")
        try:
            self.min_lon, self.min_lat, self.max_lon, self.max_lat = (float(p) for p in parts)
        except ValueError:
            raise HTTPException(422, "bbox does not contain numbers") from None

        if self.min_lon > self.max_lon or self.min_lat > self.max_lat:
            raise HTTPException(422, "bbox is inverted: min must be smaller than max")

        if from_year is not None and to_year is not None and from_year > to_year:
            from_year, to_year = to_year, from_year
        self.from_year, self.to_year = from_year, to_year
        self.include_undated = include_undated

    @property
    def time_range(self) -> tuple[date, date] | None:
        if self.from_year is None and self.to_year is None:
            return None
        return (date(self.from_year or 1800, 1, 1), date(self.to_year or 2100, 12, 31))


def _viewport_filters(viewport: Viewport):
    """Conditions for place and time.

    The time filter queries for **overlap** of the intervals, not containment. Otherwise a photo
    dated "the 1920s" would vanish from the selection 1925-1930 -- precisely the loosely dated
    photos a local history museum mostly has. See app/services/dates.py.

    **Photos without any date are a third case, and the caller decides it.** They overlap no
    period at all, so a time range drops every one of them -- in this collection two thirds of it,
    silently. ``include_undated`` therefore widens the condition to "no date **or** overlap": the
    time range then no longer holds for everything on screen, which is why the visitor has to say
    so. See the switch beside the slider.
    """
    filters = [
        Photo.status == PhotoStatus.PUBLISHED,
        Photo.lat.is_not(None),
        Photo.lat.between(viewport.min_lat, viewport.max_lat),
        Photo.lon.between(viewport.min_lon, viewport.max_lon),
    ]
    if (selection := viewport.time_range) is not None:
        selected_start, selected_end = selection
        overlaps = and_(
            Photo.date_from.is_not(None),
            Photo.date_from <= selected_end,
            Photo.date_to >= selected_start,
        )
        filters.append(
            or_(Photo.date_from.is_(None), overlaps) if viewport.include_undated else overlaps
        )
    elif not viewport.include_undated:
        # No range, but the undated are unwanted: without this the switch would do nothing at the
        # one setting where the slider covers the whole axis -- and that is where it starts.
        filters.append(Photo.date_from.is_not(None))
    return filters


@router.get("", response_model=PhotoList, summary="Photos within a viewport and time range")
def list_photos(
    viewport: Annotated[Viewport, Depends()],
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = 500,
) -> PhotoList:
    filters = _viewport_filters(viewport)

    # Most recently edited first. Photos at the same place lie on the map as one stack -- on top
    # then sits whatever was just completed, and that is exactly where the map travels after a
    # contribution. ``updated_at`` follows every visitor contribution and every edit in the admin
    # area (``onupdate`` in app/models.py).
    total = session.scalar(select(func.count()).select_from(Photo).where(*filters)) or 0
    photos = session.scalars(
        select(Photo)
        .where(*filters)
        .order_by(Photo.updated_at.desc(), Photo.imported_at.desc(), Photo.id.desc())
        .limit(limit)
    ).all()

    return PhotoList(
        photos=[PhotoMarker.from_photo(photo) for photo in photos],
        total=total,
        truncated=total > len(photos),
    )


@router.get("/histogram", response_model=Histogram, summary="Photo count per bar in the viewport")
def histogram(
    viewport: Annotated[Viewport, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> Histogram:
    """The backdrop of the time slider.

    Deliberately without the time filter: the slider should show where anything is to be found at
    all -- including outside the current selection.

    ``include_undated`` is forced on for the same reason. This endpoint reports how many undated
    photos the viewport *holds*, not how many are currently shown -- and that count is what the
    switch beside the slider is labelled with. Counted out, the label would disappear along with
    the only way of switching them back on.
    """
    viewport.from_year = viewport.to_year = None
    viewport.include_undated = True
    filters = _viewport_filters(viewport)

    # The axis, and deliberately without the viewport: it spans the whole collection and stays put
    # while the visitor pans the map. Otherwise the same spot on the slider would mean a different
    # year after every zoom -- and a selection made earlier would end up outside its own track.
    # See frontend kiosk/timeAxis.ts.
    dated = [Photo.status == PhotoStatus.PUBLISHED, Photo.date_from.is_not(None)]
    collection_from = session.scalar(
        select(func.min(cast(func.substr(Photo.date_from, 1, 4), Integer))).where(*dated)
    )
    collection_to = session.scalar(
        select(func.max(cast(func.substr(Photo.date_to, 1, 4), Integer))).where(*dated)
    )

    # How wide a bar is follows the collection, not the viewport -- otherwise the bars would change
    # meaning under the visitor's hand, the same reason the axis stands still.
    coarse = session.scalar(
        select(func.count())
        .select_from(Photo)
        .where(*dated)
        .where(Photo.date_precision == DatePrecision.DECADE)
    )
    span = (collection_to - collection_from) if collection_from and collection_to else 0
    step = bar_width(span, 10 if coarse else 1)

    # SQLite has no DATE_TRUNC. From "1932-05-14" the first four characters give the number 1932;
    # truncated division by the step and multiplication by it yields the start of the bar.
    #
    # Two traps hide in these two lines:
    #   * Do not compute with strings -- in SQLite "+" is addition, not concatenation.
    #     substr(...,1,3) + '0' would give the number 193 instead of the string "1930".
    #   * The second cast is required -- "/" is true division in SQLAlchemy, 1932/10 would be
    #     193.2 and that would turn back into 1932. Only truncation makes it 193.
    year = cast(func.substr(Photo.date_from, 1, 4), Integer)
    bar_start = cast(year / step, Integer) * step

    rows = session.execute(
        select(bar_start.label("year"), func.count().label("count"))
        .where(*filters, Photo.date_from.is_not(None))
        .group_by(bar_start)
        .order_by(bar_start)
    ).all()

    undated = (
        session.scalar(
            select(func.count())
            .select_from(Photo)
            .where(
                Photo.status == PhotoStatus.PUBLISHED,
                Photo.lat.between(viewport.min_lat, viewport.max_lat),
                Photo.lon.between(viewport.min_lon, viewport.max_lon),
                Photo.date_from.is_(None),
            )
        )
        or 0
    )

    return Histogram(
        bars=[Bar(year=int(row.year), count=row.count) for row in rows],
        step=step,
        undated=undated,
        collection_from=collection_from,
        collection_to=collection_to,
    )


def _get_photo(session: Session, photo_id: int) -> Photo:
    photo = session.scalar(
        select(Photo).where(Photo.id == photo_id).options(selectinload(Photo.tags))
    )
    if photo is None:
        raise HTTPException(404, f"Kein Foto mit der Nummer {photo_id}")
    return photo


@router.get("/{photo_id}", response_model=PhotoDetail, summary="Everything known about one photo")
def detail(photo_id: int, session: Annotated[Session, Depends(get_session)]) -> PhotoDetail:
    return PhotoDetail.from_photo(_get_photo(session, photo_id))


@router.get("/{photo_id}/thumb", summary="Thumbnail")
def thumbnail(
    photo_id: int,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    size: Annotated[int, Query(description=f"One of {THUMBNAIL_SIZES}")] = 240,
) -> Response:
    if size not in THUMBNAIL_SIZES:
        raise HTTPException(
            422, f"No thumbnail size {size}; available sizes are {list(THUMBNAIL_SIZES)}"
        )

    photo = _get_photo(session, photo_id)
    path = thumbnail_path(settings.thumbs_dir, photo.sha256, size)
    if not path.is_file():
        # A database row without files points to an incompletely restored backup.
        log.error("Thumbnail missing: %s", path)
        raise HTTPException(404, "Vorschaubild fehlt")

    return FileResponse(path, media_type="image/webp", headers={"Cache-Control": CACHE_IMMUTABLE})


@router.get("/{photo_id}/image", summary="Photo at full size")
def image(
    photo_id: int,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    photo = _get_photo(session, photo_id)
    suffix = suffix_for_mime(photo.mime)
    if suffix is None:
        # Nothing this program ever wrote: the import only stores what ALLOWED_FORMATS knows.
        # A row like that has no file to point at, so the visitor gets the same answer as for a
        # missing one -- and the log says which it was.
        log.error("Photo %s carries an unknown MIME type: %s", photo.id, photo.mime)
        raise HTTPException(404, "Originaldatei fehlt")

    path = original_path(settings.photos_dir, photo.sha256, suffix)
    if not path.is_file():
        log.error("Original file missing: %s", path)
        raise HTTPException(404, "Originaldatei fehlt")

    return FileResponse(path, media_type=photo.mime, headers={"Cache-Control": CACHE_IMMUTABLE})


@router.get("/tags/alle", response_model=list[str], summary="All tags in use")
def tags(session: Annotated[Session, Depends(get_session)]) -> list[str]:
    return list(session.scalars(select(Tag.name).order_by(Tag.name)).all())
