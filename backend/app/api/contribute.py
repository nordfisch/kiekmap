"""Der "Hilf mit"-Bereich: Besucher ergaenzen fehlende Angaben.

Bei historischen Scans stehen Ort und Jahr nirgends in der Datei. Wer den Ort kennt, weiss es aber
oft auf den ersten Blick. Dieser Weg ist deshalb nicht Beiwerk, sondern der Hauptweg, auf dem das
System an Daten kommt.

Beitraege werden **direkt** uebernommen -- der unmittelbare Effekt ist der Reiz fuer den Besucher.
Drei Dinge fangen den Missbrauchsfall auf, ohne den Normalfall auszubremsen:

  1. Nur leere Felder duerfen gefuellt werden. Was ein Kurator gesetzt hat, ist unantastbar.
  2. Koordinaten muessen in der Region liegen. Sonst landet ein Foto im Pazifik.
  3. Jede Aenderung steht in ``changes`` und ist im Admin einzeln zuruecknehmbar.
"""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.models import Change, DatePrecision, Photo, PhotoStatus, Source
from app.schemas import AufgabeAntwort, DatumsBeitrag, OrtsBeitrag, PhotoDetail
from app.services.dates import beschriftung, zeitraum

log = logging.getLogger(__name__)
router = APIRouter(prefix="/contribute", tags=["hilf mit"])

Bedarf = Literal["location", "date"]


def _fehlt_bedingung(bedarf: Bedarf):
    return Photo.lat.is_(None) if bedarf == "location" else Photo.date_from.is_(None)


@router.get("/next", response_model=AufgabeAntwort, summary="Ein Foto, dem etwas fehlt")
def naechste_aufgabe(
    session: Annotated[Session, Depends(get_session)],
    bedarf: Annotated[Bedarf, Query(alias="need", description="Was fehlen soll")] = "location",
    exclude: Annotated[
        str, Query(description="Bereits gezeigte Nummern, durch Komma getrennt")
    ] = "",
) -> AufgabeAntwort:
    """Liefert zufaellig ein Foto, dem genau dieses Feld fehlt.

    ``exclude`` sind die Fotos, die der Besucher gerade schon weggetippt hat. Ohne diese Liste
    koennte dasselbe Bild sofort wieder erscheinen -- das wirkt kaputt.
    """
    uebersprungen = {int(teil) for teil in exclude.split(",") if teil.strip().isdigit()}

    bedingungen = [Photo.status == PhotoStatus.PUBLISHED, _fehlt_bedingung(bedarf)]
    offen = session.scalar(select(func.count()).select_from(Photo).where(*bedingungen)) or 0

    abfrage = select(Photo).where(*bedingungen)
    if uebersprungen:
        abfrage = abfrage.where(Photo.id.notin_(uebersprungen))

    foto = session.scalar(abfrage.order_by(func.random()).limit(1))

    # Alles durchgesehen: lieber von vorn anfangen als "nichts mehr da" melden, solange es
    # ueberhaupt offene Fotos gibt.
    if foto is None and uebersprungen and offen:
        foto = session.scalar(select(Photo).where(*bedingungen).order_by(func.random()).limit(1))

    return AufgabeAntwort(
        need=bedarf,
        open_count=offen,
        photo=PhotoDetail.von(foto) if foto else None,
    )


def _pruefe_offen(foto: Photo, feld: str) -> None:
    """Ein Besucher darf nur fuellen, was leer ist.

    Kuratierte Angaben sind unantastbar -- und ohne diese Pruefung koennte auch der naechste
    Besucher die Angabe des vorherigen ueberschreiben, statt dass beide als Bestaetigung zaehlen.
    """
    besetzt = foto.lat is not None if feld == "location" else foto.date_from is not None
    if besetzt:
        raise HTTPException(
            409,
            "Dieses Foto hat inzwischen schon eine Angabe bekommen. Vielen Dank trotzdem!",
        )


def _hole_offenes(session: Session, foto_id: int, feld: str) -> Photo:
    foto = session.get(Photo, foto_id)
    if foto is None:
        raise HTTPException(404, f"Kein Foto mit der Nummer {foto_id}")
    _pruefe_offen(foto, feld)
    return foto


def _protokolliere(
    session: Session, foto: Photo, feld: str, alt: str | None, neu: str, sitzung: str | None
) -> None:
    session.add(
        Change(
            photo_id=foto.id,
            field=feld,
            old_value=alt,
            new_value=neu,
            source=Source.VISITOR,
            session_id=sitzung,
        )
    )


@router.post("/{foto_id}/location", response_model=PhotoDetail, summary="Ort ergänzen")
def ergaenze_ort(
    foto_id: int,
    beitrag: OrtsBeitrag,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PhotoDetail:
    foto = _hole_offenes(session, foto_id, "location")

    # Der Pin laesst sich nur auf der Karte setzen, die Karte zeigt nur die Region -- trotzdem
    # pruefen: die API ist erreichbar, und ein Foto im Pazifik waere aus der Ansicht verschwunden,
    # ohne dass jemand merkt, warum.
    if (bbox := settings.region_bbox()) is not None:
        min_lon, min_lat, max_lon, max_lat = bbox
        if not (min_lat <= beitrag.lat <= max_lat and min_lon <= beitrag.lon <= max_lon):
            raise HTTPException(422, "Dieser Ort liegt ausserhalb der Karte.")

    foto.lat = beitrag.lat
    foto.lon = beitrag.lon
    foto.location_source = Source.VISITOR
    if beitrag.place_name:
        foto.place_name = beitrag.place_name
    if beitrag.accuracy_m is not None:
        foto.location_accuracy_m = beitrag.accuracy_m

    _protokolliere(
        session,
        foto,
        "location",
        None,
        f"{beitrag.lat:.6f},{beitrag.lon:.6f}"
        + (f" ({beitrag.place_name})" if beitrag.place_name else ""),
        beitrag.session_id,
    )
    session.commit()
    session.refresh(foto)

    log.info("Besucherbeitrag: Foto %s verortet", foto.id)
    return PhotoDetail.von(foto)


@router.post("/{foto_id}/date", response_model=PhotoDetail, summary="Jahr ergänzen")
def ergaenze_datum(
    foto_id: int,
    beitrag: DatumsBeitrag,
    session: Annotated[Session, Depends(get_session)],
) -> PhotoDetail:
    foto = _hole_offenes(session, foto_id, "date")

    von, bis, genauigkeit = zeitraum(
        beitrag.year, beitrag.month, beitrag.day, DatePrecision(beitrag.precision)
    )
    foto.date_from, foto.date_to, foto.date_precision = von, bis, genauigkeit
    foto.date_source = Source.VISITOR

    _protokolliere(
        session, foto, "date", None, beschriftung(von, bis, genauigkeit), beitrag.session_id
    )
    session.commit()
    session.refresh(foto)

    log.info("Besucherbeitrag: Foto %s datiert auf %s", foto.id, foto.date_from)
    return PhotoDetail.von(foto)
