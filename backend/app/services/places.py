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
KIND_ORDER = ["strasse", "ortsteil", "gebaeude", "natur", "flur", "adresse"]

MAX_RESULTS = 12

#: How precise a statement is, in metres. Goes into ``Photo.location_accuracy_m``.
#:
#: A street of 800 m has one point; standing anywhere on it, you are a few hundred metres from it.
#: A house number is the house. The curator can tell the two apart afterwards without anybody
#: having had to write it down.
ACCURACY_STREET_M = 150
ACCURACY_ADDRESS_M = 15


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
            street=place.get("street"),
            housenumber=place.get("housenumber"),
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

    **Addresses only appear once a digit is typed.** A village street has dozens of house numbers;
    without this the twelve places in the list would be "Muehlenweg 1" to "Muehlenweg 12" and
    every other street would have fallen out. Whoever knows the number types it -- and whoever
    does not gets the street and picks the number in the second step (see ``housenumbers``).
    """
    term = normalize(query)
    if len(term) < 2:
        return []

    # Rank 0: starts with the term. Rank 1: contains it somewhere.
    match_rank = func.iif(Place.name_normalized.like(f"{term}%"), 0, 1)
    kind_rank = func.iif(
        Place.kind == "strasse",
        0,
        func.iif(
            Place.kind == "ortsteil",
            1,
            func.iif(Place.kind == "gebaeude", 2, func.iif(Place.kind == "adresse", 4, 3)),
        ),
    )

    filters = [Place.name_normalized.like(f"%{term}%")]
    if not any(character.isdigit() for character in term):
        filters.append(Place.kind != "adresse")

    return list(
        session.scalars(
            select(Place)
            .where(*filters)
            .order_by(match_rank, kind_rank, func.length(Place.name), Place.name)
            .limit(limit)
        ).all()
    )


def sort_key(housenumber: str) -> tuple[int, str]:
    """Sort house numbers the way a postman walks them, not the way a computer sorts strings.

    Alphabetically "10" comes before "9" and "1a" before "2" -- the classic quiet mistake. The
    key is (leading number, remainder), so 1, 1a, 2, 9, 10, 12 come out in that order.
    """
    digits = ""
    for character in housenumber:
        if not character.isdigit():
            break
        digits += character
    return (int(digits) if digits else 0, housenumber[len(digits) :].lower())


def housenumbers(session: Session, street: Place) -> list[Place]:
    """The house numbers of one street, in walking order.

    Empty for a street OpenStreetMap has no addresses for -- which is common enough that the
    panel has to cope with it rather than showing an empty step.
    """
    found = session.scalars(
        select(Place).where(Place.kind == "adresse", Place.street == street.name)
    ).all()
    return sorted(found, key=lambda place: sort_key(place.housenumber or ""))
