"""Place search for locating photos in the "Hilf mit" panel."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db import get_session
from app.services import places as place_service

router = APIRouter(prefix="/places", tags=["orte"])


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lat: float
    lon: float
    kind: str


@router.get("", response_model=list[PlaceOut], summary="Orte im Ortsverzeichnis suchen")
def search_places(
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str, Query(description="Anfang oder Teil eines Namens", min_length=0)] = "",
) -> list[PlaceOut]:
    """Search streets, districts, buildings, waters and fields of the village.

    Below two characters nothing is returned -- a single letter would match half of Holm.
    """
    return [PlaceOut.model_validate(place) for place in place_service.search(session, q)]
