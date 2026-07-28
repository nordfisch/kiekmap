"""Ortsverzeichnis: Suche und Laden.

Ersetzt Nominatim fuer den einen Zweck, den wir haben -- "Wo ist das?" mit einem Strassennamen
beantworten, ohne Internet. Ein Dorf hat einige hundert benannte Dinge; die passen in eine Tabelle.

Erzeugt wird ``data/places.json`` von ``tiles/build-places.py``.
"""

import json
import logging
import unicodedata
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Place

log = logging.getLogger(__name__)

#: Wonach der Besucher am ehesten sucht, kommt zuerst.
ARTEN_REIHENFOLGE = ["strasse", "ortsteil", "gebaeude", "natur", "flur"]

HOECHSTZAHL_TREFFER = 12


def normalisiere(name: str) -> str:
    """Muss mit ``tiles/build-places.py`` uebereinstimmen, sonst findet die Suche nichts.

    Das ss fuer ss muss vor dem Zerlegen stehen: NFKD laesst das scharfe s unangetastet.
    """
    ohne_scharf = name.replace("ß", "ss").replace("ẞ", "ss")
    zerlegt = unicodedata.normalize("NFKD", ohne_scharf)
    return "".join(z for z in zerlegt if not unicodedata.combining(z)).lower().strip()


def lade_aus_datei(session: Session, pfad: Path) -> int:
    """Fuellt die Tabelle aus ``places.json``. Vorhandene Eintraege werden ersetzt."""
    if not pfad.is_file():
        log.info("Kein Ortsverzeichnis unter %s -- die Ortssuche bleibt leer.", pfad)
        return 0

    orte = json.loads(pfad.read_text(encoding="utf-8"))
    session.query(Place).delete()

    session.add_all(
        Place(
            name=ort["name"],
            # Nicht der Datei vertrauen: falls sie aelter ist als die aktuelle Normalisierung,
            # wuerde die Suche sonst stillschweigend nichts finden.
            name_normalized=normalisiere(ort["name"]),
            lat=ort["lat"],
            lon=ort["lon"],
            kind=ort.get("kind", "flur"),
        )
        for ort in orte
    )
    session.commit()

    log.info("%d Orte aus %s geladen", len(orte), pfad.name)
    return len(orte)


def lade_wenn_leer(session: Session, pfad: Path) -> int:
    """Beim Start: nur laden, wenn noch nichts da ist.

    So kostet ein Neustart nichts, und ein Kurator, der von Hand nachgepflegt hat, verliert seine
    Aenderungen nicht.
    """
    vorhanden = session.scalar(select(func.count()).select_from(Place)) or 0
    if vorhanden:
        log.info("Ortsverzeichnis enthaelt bereits %d Eintraege", vorhanden)
        return vorhanden
    return lade_aus_datei(session, pfad)


def suche(session: Session, anfrage: str, limit: int = HOECHSTZAHL_TREFFER) -> list[Place]:
    """Findet Orte zu einer Eingabe.

    Treffer am Wortanfang stehen vorn: wer "Muhl" tippt, meint den Muehlenweg und nicht die
    "Alte Muehlenstrasse". Danach entscheidet die Art -- eine Strasse ist die wahrscheinlichere
    Antwort auf "Wo ist das?" als eine Flurbezeichnung.
    """
    begriff = normalisiere(anfrage)
    if len(begriff) < 2:
        return []

    # Rang 0: beginnt mit dem Begriff. Rang 1: enthaelt ihn irgendwo.
    rang = func.iif(Place.name_normalized.like(f"{begriff}%"), 0, 1)
    art_rang = func.iif(
        Place.kind == "strasse",
        0,
        func.iif(Place.kind == "ortsteil", 1, func.iif(Place.kind == "gebaeude", 2, 3)),
    )

    return list(
        session.scalars(
            select(Place)
            .where(Place.name_normalized.like(f"%{begriff}%"))
            .order_by(rang, art_rang, func.length(Place.name), Place.name)
            .limit(limit)
        ).all()
    )
