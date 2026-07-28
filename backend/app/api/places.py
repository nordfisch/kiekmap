"""Ortssuche fuer die Verortung im "Hilf mit"-Bereich."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db import get_session
from app.services import places as ortsdienst

router = APIRouter(prefix="/places", tags=["orte"])


class Ort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lat: float
    lon: float
    kind: str


@router.get("", response_model=list[Ort], summary="Orte im Ortsverzeichnis suchen")
def suche(
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str, Query(description="Anfang oder Teil eines Namens", min_length=0)] = "",
) -> list[Ort]:
    """Sucht in Strassen, Ortsteilen, Gebaeuden, Gewaessern und Fluren des Ortes.

    Unter zwei Zeichen wird nichts geliefert -- ein einzelner Buchstabe traefe halb Holm.
    """
    return [Ort.model_validate(ort) for ort in ortsdienst.suche(session, q)]
