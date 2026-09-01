"""What the contribution panel can ask about, and in which order.

One module rather than a condition per endpoint, because the same question is asked in three
places: how many photos are still open, which photo to put up next, and -- in the panel -- what to
move on to. Spread across three formulations they drift apart, and each of them looks right on its
own.

**The order of ``NEEDS`` is the rank.** A question is only reached from another one when
everything ahead of it has run dry -- not in a case distinction, but in the position of a word in
a tuple. Locating a photo that has no place at all comes first: it is the only question whose
photograph is on no map at all.

**Sharpening ranks above dating, and the reason is arithmetic.** Both orders are defensible from
the armchair -- a year is worth more than a house number. But on the Holm stock the dating question
holds 612 photographs and the sharpening question 116, and a question is only reached once the ones
ahead of it are *empty*. Put dating first and sharpening is never reached at all; the panel would
carry a third question that nobody is ever asked. Rank it above and it runs dry after 116 answers,
after which dating gets the panel to itself for as long as it takes.

The two counts are of 16 August 2026 and both move with every contribution; what matters is their
order of magnitude, not the digits. Sharpening grew from 71 that day -- see ``_needs_housenumber``.
"""

from typing import Literal, get_args

from sqlalchemy import ColumnElement, and_, exists, not_, select

from app.models import Photo, Place
from app.services.places import ACCURACY_ADDRESS_M

#: In rank order -- see the module docstring.
Need = Literal["location", "housenumber", "date"]
NEEDS: tuple[Need, ...] = get_args(Need)


def open_filter(need: Need) -> ColumnElement[bool]:
    """The SQL condition for "this photo still owes an answer to that question"."""
    if need == "location":
        return Photo.needs_location
    if need == "date":
        return Photo.needs_date
    return _needs_housenumber()


def _needs_housenumber() -> ColumnElement[bool]:
    """Somewhere on a named street, and the house is not known.

    Four conditions, and the last one is the reason this cannot be a property on the model.

    **It has to be on the map at all.** A photo without a coordinate owes its answer to the first
    question, not to this one -- and in the detail view, where all three buttons stand side by
    side, offering both at once would ask the visitor to place the same photo twice.

    **Not house-precise already.** Where the address is known the question is answered. Note what
    this does *not* say: it says nothing about **where the coordinate came from**.

        Until 16 August 2026 it did, and that was the bug behind backlog point 53. The condition
        read ``location_accuracy_m == ACCURACY_STREET_M``, which let in only what a curator had
        placed on a street and left out 53 photographs that carry a street name from the archive
        folder and a coordinate out of their EXIF. The reason given here was that an EXIF
        coordinate is a measurement of a different kind -- "the camera knows where the
        photographer stood, not what they photographed".

        **That premise had been refuted four days earlier** and nobody came back to this file. Of
        413 EXIF coordinates in the first stock, 278 were shared with another photograph; among
        these 53, thirty share a point, six of them on one. They are values somebody typed in, not
        measurements (decisions.md, point 34). A typed-in coordinate on a named street is exactly
        what this question is for.

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
        not_(Photo.needs_location),
        Photo.location_accuracy_m.is_distinct_from(ACCURACY_ADDRESS_M),
        Photo.place_name.is_not(None),
        # GLOB is SQLite's own, like ``func.iif`` in services/places.py. LIKE would need an escape
        # dance for the brackets and still not express a character class.
        not_(Photo.place_name.op("GLOB")("*[0-9]*")),
        exists(select(Place.id).where(Place.kind == "adresse", Place.street == Photo.place_name)),
    )
