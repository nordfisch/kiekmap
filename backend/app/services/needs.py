"""What the "Hilf mit" panel can ask about, and in which order.

One module rather than a condition per endpoint, because the same question is asked in three
places: how many photos are still open, which photo to put up next, and -- in the panel -- what to
move on to. Spread across three formulations they drift apart, and each of them looks right on its
own.

**The order of ``NEEDS`` is the rank.** A question is only reached from another one when
everything ahead of it has run dry. That is where "sharpening comes last" lives: not in a case
distinction, but in the position of a word in a tuple. Locating a photo that has no place at all
is worth more than moving one from the middle of a street to its house number.
"""

from typing import Literal, get_args

from sqlalchemy import ColumnElement, and_, exists, not_, select

from app.models import Photo, Place
from app.services.places import ACCURACY_STREET_M

#: In rank order -- see the module docstring.
Need = Literal["location", "date", "housenumber"]
NEEDS: tuple[Need, ...] = get_args(Need)


def open_filter(need: Need) -> ColumnElement[bool]:
    """The SQL condition for "this photo still owes an answer to that question"."""
    if need == "location":
        return Photo.needs_location
    if need == "date":
        return Photo.needs_date
    return _needs_housenumber()


def _needs_housenumber() -> ColumnElement[bool]:
    """Located, but only as precisely as a street -- and nothing better is known.

    Four conditions, and the last one is the reason this cannot be a property on the model.

    **Only street-precise.** A house-precise photo is done; one located from EXIF alone carries no
    accuracy at all, and its imprecision is of a different kind -- the camera knows where the
    photographer stood, not what they photographed. That is a separate question (see backlog).

    **No house number in the name.** Where ``place_name`` reads "Hauptstraße 11a", the number is
    already known and only its coordinate is missing -- because the address is not in
    OpenStreetMap, mostly because the house has since been split or renumbered. Offering a picker
    there would offer every number except the right one. Those photos are a machine job, not a
    visitor question; see backlog, point 41.

    The digit test is a heuristic and errs towards not asking: a street with a digit in its name
    ("Straße des 17. Juni") is never put up. That is the harmless direction.

    **The gazetteer has to be able to answer.** 141 of 486 streets hold no addresses at all. Put a
    photo from one of those up, and the question stands on screen without a single button under
    it. This is also why the condition lives here and not on ``Photo``: whether the gazetteer can
    answer is not something a photo object knows without a session.

    Deliberately **no** filter on ``location_source``: a street-precise statement by a curator may
    be sharpened too. That widens decisions.md point 5 and is recorded there.
    """
    return and_(
        Photo.location_accuracy_m == ACCURACY_STREET_M,
        Photo.place_name.is_not(None),
        # GLOB is SQLite's own, like ``func.iif`` in services/places.py. LIKE would need an escape
        # dance for the brackets and still not express a character class.
        not_(Photo.place_name.op("GLOB")("*[0-9]*")),
        exists(select(Place.id).where(Place.kind == "adresse", Place.street == Photo.place_name)),
    )
