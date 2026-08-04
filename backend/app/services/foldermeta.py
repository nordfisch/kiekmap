"""Read the folder structure a collection was sorted into.

A museum archive is rarely a flat pile. Holm's is filed by address::

    Straßen/Hauptstraße/14 Gasthof Petersen/P4139276.JPG
    Straßen/Hörnstraße/10 H Brahms/023.jpg
    Straßen/Rehnaer Straße/119.jpg

That is a statement about every one of those files, made by whoever sorted them -- and throwing it
away would mean asking visitors "where is this?" about a photo whose address we were told.

**The gazetteer decides what a street is, not a folder called "Straßen".** A path segment counts
as a street when ``places`` knows one by that name. So this works on a USB stick filed differently,
on a folder in a different language, and in a village that never had a "Straßen" folder -- and no
place name ends up in the code (see CLAUDE.md, "Nichts Ortsspezifisches gehört in den Code").

Everything here only fills fields the file itself left empty. A coordinate out of the EXIF beats
the folder every time: the camera stood somewhere, the folder is somebody's filing.
"""

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Photo, Place, Source
from app.services import places as place_service
from app.services.tags import add_tags

log = logging.getLogger(__name__)

#: Characters that separate a house number from what follows it.
_RANGE_MARKS = "-–/"


@dataclass(frozen=True)
class FolderMeta:
    """What the path says. Every field may be empty."""

    #: Spelled as the gazetteer spells it, not as the folder does.
    street: str | None = None
    #: Normalized: "009a" becomes "9a", so it matches the gazetteer.
    housenumber: str | None = None
    #: What stood beside the number: "Gasthof Petersen", "ehemalige Sparkasse".
    name: str | None = None

    @property
    def address(self) -> str | None:
        """ "Hauptstraße 14", or just the street, or nothing."""
        if not self.street:
            return None
        return f"{self.street} {self.housenumber}" if self.housenumber else self.street

    @property
    def title(self) -> str | None:
        """ "Hauptstraße 14, Gasthof Petersen" -- what the archive would call this picture."""
        parts = [part for part in (self.address, self.name) if part]
        return ", ".join(parts) or None


def split_housenumber(folder: str) -> tuple[str | None, str | None]:
    """Split a folder name into house number and whatever else stands there.

    The cases are all real, and each of them is a way to get it wrong:

    * ``"14 Gasthof Petersen"`` -> ``("14", "Gasthof Petersen")``
    * ``"25a Zahnarztpraxis"`` -> ``("25a", "Zahnarztpraxis")`` -- a letter glued to the digits is
      part of the number
    * ``"10 H Brahms"`` -> ``("10", "H Brahms")`` -- **the same letter with a space in front
      is an initial, not a number.** Read the other way this becomes house number 10h, which does
      not exist, and the photo lands on the street instead of at the house
    * ``"099-105 Weltweit"`` -> ``("99", "Weltweit")`` -- a range: the first number locates it
      well enough, and the second must not survive into the name
    * ``"Glasfaser"`` -> ``(None, "Glasfaser")`` -- not every folder is an address
    """
    text = folder.strip()

    digits = ""
    for character in text:
        if not character.isdigit():
            break
        digits += character
    if not digits:
        return None, text or None

    rest = text[len(digits) :]

    letters = ""
    while rest and rest[0].isalpha():
        letters, rest = letters + rest[0], rest[1:]

    # A range mark right behind the number means the folder covers several houses. The next token
    # is the other end of the range -- "099-105" -- and belongs in neither field.
    if rest[:1] and rest[0] in _RANGE_MARKS:
        rest = rest.lstrip(_RANGE_MARKS).lstrip()
        rest = rest.split(" ", 1)[1] if rest[:1].isdigit() and " " in rest else ""

    # Leading zeros are the archive's padding, not part of the address: the gazetteer has "9a".
    number = str(int(digits)) + letters
    return number, rest.strip(" " + _RANGE_MARKS + ",_") or None


def _match_street(folder: str, streets: Mapping[str, str]) -> str | None:
    """Which street a folder names -- exactly, or unmistakably.

    The archive shortens: a folder "Wiesengrund" for the street OpenStreetMap calls "Im
    Wiesengrund". So a folder also counts when its words appear inside exactly one street name.

    Two guards, and both caught a real mistake on the Holm stock:

    * **Exactly one match.** "Deelenweg" sits inside both "Deelenweg I" and "Deelenweg II";
      guessing between them would put five photographs at the wrong end of the village, and
      nobody would ever see that it had happened.
    * **Every word has a letter in it.** The house-number folder "2" under "Achter de Möhl"
      matched the street "Kolonie Autal 2" -- unambiguously, and completely wrong. A number is a
      house number; only a name is a street.

    Where neither holds, there is no match: the photo goes into "Wo ist das?", where somebody
    from Holm answers it properly.
    """
    normalized = place_service.normalize(folder)
    if not normalized:
        return None
    if exact := streets.get(normalized):
        return exact

    words = normalized.split()
    if not all(any(character.isalpha() for character in word) for word in words):
        return None
    candidates = {
        street for name, street in streets.items() if _contains_words(name.split(), words)
    }
    return candidates.pop() if len(candidates) == 1 else None


def _contains_words(haystack: Sequence[str], needle: Sequence[str]) -> bool:
    """Whether the words of ``needle`` appear in ``haystack`` in a row.

    Word by word rather than as a substring, so that "Sande" finds "Im Sande" but "Hof" does not
    turn up inside "Hofstelle".
    """
    return any(
        list(haystack[start : start + len(needle)]) == list(needle)
        for start in range(len(haystack) - len(needle) + 1)
    )


def parse_path(parts: Sequence[str], streets: Mapping[str, str]) -> FolderMeta:
    """Read street, house number and name out of the directory parts of a relative path.

    ``parts`` are the directories only, without the file name. ``streets`` maps a normalized
    folder name to the street's proper spelling -- anything not in it is filing, not an address.

    Searched from the back: the deepest folder that names a street wins, so an archive filed
    ``Straßen/Hauptstraße/...`` and one filed ``Hauptstraße/...`` come out the same.
    """
    for index in range(len(parts) - 1, -1, -1):
        street = _match_street(parts[index], streets)
        if street is None:
            continue
        # Only the folder directly below the street is read as a house number. Anything deeper
        # would be a filing scheme we know nothing about.
        below = parts[index + 1] if index + 1 < len(parts) else None
        number, name = split_housenumber(below) if below else (None, None)
        return FolderMeta(street=street, housenumber=number, name=name)

    return FolderMeta()


def _relative(path: Path, root: Path) -> Path:
    """The file's path below the import root -- or its bare name if it lies outside."""
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)


def street_names(session: Session) -> dict[str, str]:
    """Normalized name -> proper spelling, for every street in the gazetteer."""
    return {
        place_service.normalize(name): name
        for name in session.scalars(select(Place.name).where(Place.kind == "strasse")).all()
    }


def _address_place(session: Session, meta: FolderMeta) -> Place | None:
    """The house number as a point -- or nothing, if the gazetteer does not have it."""
    if not meta.housenumber:
        return None
    return session.scalar(
        select(Place).where(
            Place.kind == "adresse",
            Place.street == meta.street,
            Place.housenumber == meta.housenumber,
        )
    )


def _street_place(session: Session, meta: FolderMeta) -> Place | None:
    return session.scalar(select(Place).where(Place.kind == "strasse", Place.name == meta.street))


def apply_folder_meta(
    session: Session,
    photo: Photo,
    path: Path,
    root: Path,
    settings: Settings,
) -> FolderMeta:
    """Fill the photo's empty fields from its place in the folder tree.

    ``path`` is the file, ``root`` the folder the import was started on. The two are needed for
    different things, and the difference matters:

    * the **street is looked for in the whole path**, not only below ``root``. Otherwise starting
      an import on ``Straßen/Hauptstraße`` itself would lose the street that names the folder --
      and on a USB stick the volunteer picks the folder, so that is not a corner case.
    * the **provenance note keeps the path relative to** ``root``, because that is the part that
      also exists in the museum's own archive.

    Returns what was read, so a caller can report on it. Only empty fields are touched -- what the
    file said about itself stands.
    """
    meta = parse_path(path.parts[:-1], street_names(session))
    if not meta.street:
        return meta

    _locate(session, photo, meta)

    # The name is set even where the point came from the file: where the camera stood does not
    # say what the house is called, and "Hauptstraße 14" is the line a visitor looks for under
    # the picture. It is also the context somebody needs to answer "where is this?" -- a photo
    # without a house number stays unlocated but now says which street it is on.
    if not photo.place_name:
        photo.place_name = meta.address

    if not photo.title:
        photo.title = meta.title
        photo.title_source = Source.CURATOR

    if not photo.provenance and settings.import_provenance:
        photo.provenance = settings.import_provenance + str(_relative(path, root))

    # The street goes on *every* photo below it, house number or not. For the ones without a
    # number it is the only trace left; for the rest it makes the whole street findable at once.
    add_tags(session, photo, [meta.street, *([meta.name] if meta.name else [])])

    return meta


def _locate(session: Session, photo: Photo, meta: FolderMeta) -> None:
    """Put the photo on the map, as precisely as the folder allows.

    **A folder without a house number leaves the photo unlocated**, even though the street is
    known. Setting it to the middle of the street would look like an answer, and the photo would
    drop out of "Wo ist das?" -- where somebody who walks past that house every day could have
    said which one it is. The street survives as a keyword, which is the honest version of the
    same statement.
    """
    if not photo.needs_location or not meta.housenumber:
        return

    place = _address_place(session, meta)
    accuracy = place_service.ACCURACY_ADDRESS_M
    if place is None:
        # The number is not in OpenStreetMap. The street still is, and 150 m says how much that
        # is worth -- while ``place_name`` keeps the address we were actually told.
        place = _street_place(session, meta)
        accuracy = place_service.ACCURACY_STREET_M
    if place is None:
        return

    photo.lat, photo.lon = place.lat, place.lon
    photo.place_name = meta.address
    photo.location_accuracy_m = accuracy
    photo.location_source = Source.CURATOR
