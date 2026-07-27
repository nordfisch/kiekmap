"""Fotos abfragen und ausliefern."""

import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.db import get_session
from app.models import Photo, PhotoStatus, Tag
from app.schemas import Histogramm, Jahrzehnt, PhotoDetail, PhotoListe, PhotoMarker
from app.services.storage import THUMBNAIL_GROESSEN, original_pfad, thumbnail_pfad

log = logging.getLogger(__name__)
router = APIRouter(prefix="/photos", tags=["fotos"])

#: Obergrenze pro Abfrage. Mehr Marker als das ergeben auf einer Karte ohnehin keinen Sinn, und die
#: Antwort soll auf einem Pi in einem Rutsch durchgehen.
HOECHSTZAHL = 2000

#: Dateiname ist der Inhalts-Hash, gleicher Name heisst also garantiert gleicher Inhalt.
#: Deshalb darf der Browser beliebig lange cachen.
CACHE_UNVERAENDERLICH = "public, max-age=31536000, immutable"


class Ausschnitt:
    """Kartenausschnitt und Zeitraum, wie sie aus der Abfragezeichenkette kommen."""

    def __init__(
        self,
        bbox: Annotated[
            str,
            Query(
                description="minLon,minLat,maxLon,maxLat in WGS84",
                examples=["9.60,53.57,9.75,53.67"],
            ),
        ],
        von: Annotated[int | None, Query(ge=1800, le=2100, description="Jahr ab")] = None,
        bis: Annotated[int | None, Query(ge=1800, le=2100, description="Jahr bis")] = None,
    ) -> None:
        teile = bbox.split(",")
        if len(teile) != 4:
            raise HTTPException(422, "bbox braucht vier durch Komma getrennte Zahlen")
        try:
            self.min_lon, self.min_lat, self.max_lon, self.max_lat = (float(t) for t in teile)
        except ValueError:
            raise HTTPException(422, "bbox enthaelt keine Zahlen") from None

        if self.min_lon > self.max_lon or self.min_lat > self.max_lat:
            raise HTTPException(422, "bbox ist verdreht: min muss kleiner als max sein")

        if von is not None and bis is not None and von > bis:
            von, bis = bis, von
        self.von_jahr, self.bis_jahr = von, bis

    @property
    def zeitraum(self) -> tuple[date, date] | None:
        if self.von_jahr is None and self.bis_jahr is None:
            return None
        return (
            date(self.von_jahr or 1800, 1, 1),
            date(self.bis_jahr or 2100, 12, 31),
        )


def _im_ausschnitt(ausschnitt: Ausschnitt):
    """Bedingungen fuer Ort und Zeit.

    Der Zeitfilter fragt auf **Ueberlappung** der Intervalle ab, nicht auf Enthaltensein. Sonst
    verschwaende ein auf "1920er" datiertes Foto aus der Auswahl 1925-1930 -- also genau die
    unscharf datierten Fotos, die ein Heimatmuseum ueberwiegend hat. Siehe app/services/dates.py.
    """
    bedingungen = [
        Photo.status == PhotoStatus.PUBLISHED,
        Photo.lat.is_not(None),
        Photo.lat.between(ausschnitt.min_lat, ausschnitt.max_lat),
        Photo.lon.between(ausschnitt.min_lon, ausschnitt.max_lon),
    ]
    if (zeitraum := ausschnitt.zeitraum) is not None:
        auswahl_von, auswahl_bis = zeitraum
        bedingungen += [
            Photo.date_from.is_not(None),
            Photo.date_from <= auswahl_bis,
            Photo.date_to >= auswahl_von,
        ]
    return bedingungen


@router.get("", response_model=PhotoListe, summary="Fotos im Kartenausschnitt und Zeitraum")
def liste(
    ausschnitt: Annotated[Ausschnitt, Depends()],
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=HOECHSTZAHL)] = 500,
) -> PhotoListe:
    bedingungen = _im_ausschnitt(ausschnitt)

    gesamt = session.scalar(select(func.count()).select_from(Photo).where(*bedingungen)) or 0
    fotos = session.scalars(
        select(Photo).where(*bedingungen).order_by(Photo.date_from, Photo.id).limit(limit)
    ).all()

    return PhotoListe(
        photos=[PhotoMarker.von(foto) for foto in fotos],
        total=gesamt,
        truncated=gesamt > len(fotos),
    )


@router.get("/histogram", response_model=Histogramm, summary="Fotos je Jahrzehnt im Ausschnitt")
def histogramm(
    ausschnitt: Annotated[Ausschnitt, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> Histogramm:
    """Der Hintergrund des Zeitschiebers.

    Bewusst ohne den Zeitfilter: der Schieber soll zeigen, wo im Zeitraum ueberhaupt etwas zu
    finden ist -- auch ausserhalb dessen, was gerade ausgewaehlt ist.
    """
    ausschnitt.von_jahr = ausschnitt.bis_jahr = None
    bedingungen = _im_ausschnitt(ausschnitt)

    # SQLite kennt kein DATE_TRUNC. Aus "1932-05-14" wird ueber die ersten vier Zeichen die Zahl
    # 1932, abgeschnitten durch zehn geteilt und wieder mal zehn ergibt 1930.
    #
    # Zwei Fallen sitzen in diesen zwei Zeilen:
    #   * Nicht mit Zeichenketten rechnen -- in SQLite ist "+" Addition, nicht Verkettung.
    #     substr(...,1,3) + '0' ergaebe die Zahl 193 statt der Zeichenkette "1930".
    #   * Der zweite cast ist noetig -- "/" ist in SQLAlchemy echte Division, 1932/10 waere 193.2
    #     und daraus wuerde wieder 1932. Erst das Abschneiden macht daraus 193.
    jahr = cast(func.substr(Photo.date_from, 1, 4), Integer)
    jahrzehnt = cast(jahr / 10, Integer) * 10

    zeilen = session.execute(
        select(jahrzehnt.label("jahrzehnt"), func.count().label("anzahl"))
        .where(*bedingungen, Photo.date_from.is_not(None))
        .group_by(jahrzehnt)
        .order_by(jahrzehnt)
    ).all()

    undatiert = (
        session.scalar(
            select(func.count())
            .select_from(Photo)
            .where(
                Photo.status == PhotoStatus.PUBLISHED,
                Photo.lat.between(ausschnitt.min_lat, ausschnitt.max_lat),
                Photo.lon.between(ausschnitt.min_lon, ausschnitt.max_lon),
                Photo.date_from.is_(None),
            )
        )
        or 0
    )

    jahrzehnte = [Jahrzehnt(decade=int(zeile.jahrzehnt), count=zeile.anzahl) for zeile in zeilen]
    return Histogramm(
        decades=jahrzehnte,
        undated=undatiert,
        earliest=jahrzehnte[0].decade if jahrzehnte else None,
        latest=jahrzehnte[-1].decade + 9 if jahrzehnte else None,
    )


def _hole(session: Session, foto_id: int) -> Photo:
    foto = session.scalar(
        select(Photo).where(Photo.id == foto_id).options(selectinload(Photo.tags))
    )
    if foto is None:
        raise HTTPException(404, f"Kein Foto mit der Nummer {foto_id}")
    return foto


@router.get("/{foto_id}", response_model=PhotoDetail, summary="Alle Angaben zu einem Foto")
def detail(foto_id: int, session: Annotated[Session, Depends(get_session)]) -> PhotoDetail:
    return PhotoDetail.von(_hole(session, foto_id))


@router.get("/{foto_id}/thumb", summary="Vorschaubild")
def thumbnail(
    foto_id: int,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    size: Annotated[int, Query(description=f"Eine von {THUMBNAIL_GROESSEN}")] = 240,
) -> Response:
    if size not in THUMBNAIL_GROESSEN:
        raise HTTPException(
            422, f"Groesse {size} gibt es nicht, verfuegbar sind {list(THUMBNAIL_GROESSEN)}"
        )

    foto = _hole(session, foto_id)
    pfad = thumbnail_pfad(settings.thumbs_dir, foto.sha256, size)
    if not pfad.is_file():
        # Datenbankzeile ohne Datei -- deutet auf eine unvollstaendig zurueckgespielte
        # Sicherung hin.
        log.error("Vorschaubild fehlt: %s", pfad)
        raise HTTPException(404, "Vorschaubild fehlt")

    return FileResponse(
        pfad, media_type="image/webp", headers={"Cache-Control": CACHE_UNVERAENDERLICH}
    )


@router.get("/{foto_id}/image", summary="Foto in voller Groesse")
def bild(
    foto_id: int,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    foto = _hole(session, foto_id)
    endung = "." + foto.mime.split("/")[-1].replace("jpeg", "jpg").replace("tiff", "tif")
    pfad = original_pfad(settings.photos_dir, foto.sha256, endung)
    if not pfad.is_file():
        log.error("Originaldatei fehlt: %s", pfad)
        raise HTTPException(404, "Originaldatei fehlt")

    return FileResponse(
        pfad,
        media_type=foto.mime,
        headers={"Cache-Control": CACHE_UNVERAENDERLICH},
    )


@router.get("/tags/alle", response_model=list[str], summary="Alle vergebenen Schlagwoerter")
def schlagwoerter(session: Annotated[Session, Depends(get_session)]) -> list[str]:
    return list(session.scalars(select(Tag.name).order_by(Tag.name)).all())
