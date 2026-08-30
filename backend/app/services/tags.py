# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Attaching keywords to a photo.

Its own module because both layers of the import need it -- the metadata layer for what stands in
the file, the folder layer for street and house name -- and importing one from the other would
close a circle.
"""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Photo, Tag


def add_tags(session: Session, photo: Photo, names: Iterable[str]) -> None:
    """Attach keywords, reusing existing tags and skipping ones the photo already carries.

    A new tag is written out right away. The session runs with ``autoflush=False``, so without
    that a tag created for one photo would still be invisible to the query for the next -- and
    two photos at the same address ("Hauptstraße 26, Hof Sieveking") would each create their
    own, until the unique constraint stopped the whole import.
    """
    present = {tag.name for tag in photo.tags}
    fresh = False

    for name in dict.fromkeys(name.strip() for name in names if name.strip()):
        if name in present:
            continue
        tag = session.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag, fresh = Tag(name=name), True
            session.add(tag)
        photo.tags.append(tag)
        present.add(name)

    if fresh:
        session.flush()
