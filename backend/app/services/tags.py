"""Attaching keywords to a photo.

Its own module because both layers of the import need it -- the metadata layer for what stands in
the file, the folder layer for street and house name -- and importing one from the other would
close a circle.
"""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models import Photo, Tag


def tag_named(session: Session, name: str) -> Tag:
    """The tag of that name, created if there is none. Written out at once.

    **Inserted first, then read** -- not the other way round. Read first, the name can be created
    by a parallel import between the query and the INSERT, and the unique constraint then stops
    this one with an IntegrityError. Every import attaches ``KIEKMAP_IMPORT_TAGS``, so a new
    keyword there meets exactly that race the first time the upload and the inbox run together.

    Written out at once also matters on its own. The session runs with ``autoflush=False``, so a
    tag only added would still be invisible to the query for the next photo -- and two photos at
    the same address ("Hauptstraße 26, Hof Sieveking") would each create their own.

    **The session is flushed first.** A caller may hold a ``Tag`` of the same name that it added
    but has not written out. The INSERT below cannot see it, writes the name itself, and the
    caller's object then fails the unique constraint at the next flush. ``import_file`` used to
    flush before it attached tags, and the seed loader relied on that without saying so.
    """
    session.flush()
    session.execute(
        sqlite_insert(Tag).values(name=name).on_conflict_do_nothing(index_elements=[Tag.name])
    )
    return session.scalars(select(Tag).where(Tag.name == name)).one()


def add_tags(session: Session, photo: Photo, names: Iterable[str]) -> None:
    """Attach keywords, reusing existing tags and skipping ones the photo already carries."""
    present = {tag.name for tag in photo.tags}

    for name in dict.fromkeys(name.strip() for name in names if name.strip()):
        if name in present:
            continue
        photo.tags.append(tag_named(session, name))
        present.add(name)
