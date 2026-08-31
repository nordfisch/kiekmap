"""Place search for locating photos in the "Hilf mit" panel."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.models import Place
from app.schemas import PlaceOut
from app.services import places as place_service

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=list[PlaceOut], summary="Search the gazetteer")
def search_places(
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str, Query(description="Start of a name, or part of one", min_length=0)] = "",
) -> list[PlaceOut]:
    """Search streets, districts, buildings, waters and fields of the village.

    Below two characters nothing is returned -- a single letter would match half of Holm.
    Addresses only take part once the input holds a digit; see the service for why.
    """
    return [PlaceOut.from_place(place) for place in place_service.search(session, q)]


@router.get("/streets", response_model=list[PlaceOut], summary="Streets offered as buttons")
def streets(
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[PlaceOut]:
    """The streets the "Hilf mit" panel puts up for choice, alphabetically.

    Which ones, and how many, is the service's decision -- see ``nearby_streets``. Registered
    before the ``/{place_id}`` route below, otherwise "streets" would be read as an id.
    """
    return [
        PlaceOut.from_place(place)
        for place in place_service.nearby_streets(
            session, settings.region_center(), settings.street_choice()
        )
    ]


@router.get(
    "/{place_id}/housenumbers",
    response_model=list[PlaceOut],
    summary="House numbers of one street",
)
def housenumbers(
    place_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> list[PlaceOut]:
    """The second step of locating: street first, then the number.

    Addressed by the id of the street rather than by its name -- the name would come back from
    the browser and is input, not a fact.

    An empty list is an ordinary answer, not an error: not every street in OpenStreetMap has
    addresses, and the panel skips the step then.
    """
    street = session.get(Place, place_id)
    if street is None:
        raise HTTPException(404, f"Kein Ort mit der Nummer {place_id}")
    return [PlaceOut.from_place(place) for place in place_service.housenumbers(session, street)]
