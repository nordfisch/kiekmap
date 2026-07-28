"""Gazetteer: loading and search.

Replaces Nominatim for the single purpose we have -- answering "where is this?" with a street
name, without internet. A village has a few hundred named things; they fit in one table.

``data/places.json`` is produced by ``tiles/build-places.py``.
"""

import json
import logging
import unicodedata
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Place

log = logging.getLogger(__name__)

#: What the visitor is most likely searching for comes first.
KIND_ORDER = ["strasse", "ortsteil", "gebaeude", "natur", "flur"]

MAX_RESULTS = 12


def normalize(name: str) -> str:
    """Must match ``tiles/build-places.py``, otherwise the search finds nothing.

    The ss for the sharp s has to happen before decomposing: NFKD leaves it untouched.
    """
    without_sharp_s = name.replace("ß", "ss").replace("ẞ", "ss")
    decomposed = unicodedata.normalize("NFKD", without_sharp_s)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


def load_from_file(session: Session, path: Path) -> int:
    """Fill the table from ``places.json``. Existing entries are replaced."""
    if not path.is_file():
        log.info("No gazetteer at %s -- place search stays empty.", path)
        return 0

    places = json.loads(path.read_text(encoding="utf-8"))
    session.query(Place).delete()

    session.add_all(
        Place(
            name=place["name"],
            # Do not trust the file: if it predates the current normalization, the search would
            # silently come up empty.
            name_normalized=normalize(place["name"]),
            lat=place["lat"],
            lon=place["lon"],
            kind=place.get("kind", "flur"),
        )
        for place in places
    )
    session.commit()

    log.info("Loaded %d places from %s", len(places), path.name)
    return len(places)


def load_if_empty(session: Session, path: Path) -> int:
    """At startup: only load when nothing is there yet.

    That way a restart costs nothing, and a curator who edited entries by hand does not lose them.
    """
    existing = session.scalar(select(func.count()).select_from(Place)) or 0
    if existing:
        log.info("Gazetteer already holds %d entries", existing)
        return existing
    return load_from_file(session, path)


def search(session: Session, query: str, limit: int = MAX_RESULTS) -> list[Place]:
    """Find places matching an input.

    Matches at the start of the name come first: whoever types "Muhl" means the Muehlenweg, not
    the "Alte Muehlenstrasse". After that the kind decides -- a street is the more likely answer
    to "where is this?" than a field name.
    """
    term = normalize(query)
    if len(term) < 2:
        return []

    # Rank 0: starts with the term. Rank 1: contains it somewhere.
    match_rank = func.iif(Place.name_normalized.like(f"{term}%"), 0, 1)
    kind_rank = func.iif(
        Place.kind == "strasse",
        0,
        func.iif(Place.kind == "ortsteil", 1, func.iif(Place.kind == "gebaeude", 2, 3)),
    )

    return list(
        session.scalars(
            select(Place)
            .where(Place.name_normalized.like(f"%{term}%"))
            .order_by(match_rank, kind_rank, func.length(Place.name), Place.name)
            .limit(limit)
        ).all()
    )
