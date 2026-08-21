# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""The same backup, as one file -- built while it is being sent.

The second route out of the collection: a download through the browser, for when no stick is at
hand. It is the **addition**, not the replacement -- see docs/decisions.md, point 11. The stick
writes only what is new and stays usable when it breaks off halfway; this packs everything every
time and an interrupted download is worthless.

What makes the addition defensible is the shape: **the archive is the very folder the stick gets,
only zipped.** Unpack it onto a stick and the existing restore takes it. That property is the
reason a missing upload route is an inconvenience rather than a gap, and tests/test_backup.py
guards it.
"""

import logging
import tempfile
import zipfile
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import Settings
from app.services import places
from app.services.backup.collection import collection_size, thumbnails_of, vacuum_into
from app.services.backup.common import (
    ARCHIVE_CHUNK,
    BACKUP_DIR_NAME,
    LOOSE_FILES,
    MANIFEST_NAME,
    human_size,
    place_name,
)
from app.services.backup.manifest import manifest_bytes
from app.services.backup.state import record_backup

log = logging.getLogger(__name__)

#: Stands where a stick would put its name, so the admin area can say which route it was.
ZIP_DRIVE_NAME = "Download"


class _ArchiveStream:
    """A sink for ``zipfile`` that keeps nothing.

    ``zipfile`` writes into this, the generator drains it after every slice, and the bytes go
    straight out to the browser. Three methods carry it:

      * ``write`` collects what was just produced,
      * ``tell`` counts along, because ``zipfile`` computes its offsets from it,
      * ``seekable`` says **no** -- and that is the switch that matters. It makes ``zipfile`` use
        data descriptors instead of jumping back to patch headers it has already handed out. There
        is deliberately no ``seek``: were there one, the class would silently start lying.
    """

    def __init__(self) -> None:
        self._parts: list[bytes] = []
        self._written = 0

    def write(self, data: bytes) -> int:
        self._parts.append(bytes(data))
        self._written += len(data)
        return len(data)

    def tell(self) -> int:
        return self._written

    def flush(self) -> None:
        pass

    def seekable(self) -> bool:
        return False

    def take(self) -> bytes:
        """Everything produced since the last call. Empties the buffer."""
        data = b"".join(self._parts)
        self._parts.clear()
        return data


def _add_to_archive(
    archive: "zipfile.ZipFile", stream: _ArchiveStream, source: Path, name: str
) -> Iterator[bytes]:
    with archive.open(name, "w") as target, source.open("rb") as handle:
        while chunk := handle.read(ARCHIVE_CHUNK):
            target.write(chunk)
            if data := stream.take():
                yield data
    # Closing the entry writes its data descriptor -- that belongs to the stream too.
    if data := stream.take():
        yield data


def archive_name(settings: Settings) -> str:
    """``kiekmap-sicherung-holm-2026-08-03.zip``.

    Plain ASCII: it travels in an HTTP header and lands as a file name on somebody's computer.

    **Local time, unlike everything that gets stored.** The rule that runs through this module is
    "stored is UTC" (``dates.utc_now``) -- and a file name is not stored, it is read. Whoever
    downloads a backup at half past midnight looks for today's date, not yesterday's. The
    set-aside folder beside it has always been named this way; since 19 August 2026 the two
    agree.
    """
    slug = "".join(c for c in places.normalize(place_name(settings)) if c.isalnum() or c == "-")
    place = f"-{slug}" if slug else ""
    return f"{BACKUP_DIR_NAME}{place}-{datetime.now():%Y-%m-%d}.zip"


def stream_archive(session: Session, settings: Settings) -> Iterator[bytes]:
    """The whole collection as one ZIP, produced while it is being sent.

    Not compressed, and that is not laziness: JPEG and WebP are compressed already, a second pass
    costs a Pi real time and saves nothing. ZIP64 is on because two thousand scans go past the
    four-gigabyte limit of the old format without trying.

    The last thing that happens -- after the final byte -- is the note that a backup was made. An
    interrupted download therefore does not count as one, which is the honest answer: what the
    browser did not receive protects nobody.
    """
    photos, size = collection_size(settings, max_age_s=0)
    stream = _ArchiveStream()

    # The database is the one thing that cannot be streamed off the disk as it lies: it has to be
    # written out consistently first. Only the database, though -- the photographs, which are the
    # gigabytes, never touch the card a second time.
    with tempfile.TemporaryDirectory(dir=settings.data_dir, prefix="archiv-") as tmp:
        database = Path(tmp) / "kiekmap.db"
        vacuum_into(session, database)

        with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED, allowZip64=True) as archive:
            yield from _add_to_archive(archive, stream, database, f"{BACKUP_DIR_NAME}/kiekmap.db")

            for source in sorted(settings.photos_dir.rglob("*")):
                if not source.is_file():
                    continue
                relative = source.relative_to(settings.photos_dir).as_posix()
                yield from _add_to_archive(
                    archive, stream, source, f"{BACKUP_DIR_NAME}/photos/{relative}"
                )
                # The thumbnails travel with their photo, exactly as onto the stick: without them
                # a restored device spends an hour rendering before it shows anything.
                for thumb in thumbnails_of(settings, source.stem):
                    relative = thumb.relative_to(settings.thumbs_dir).as_posix()
                    yield from _add_to_archive(
                        archive, stream, thumb, f"{BACKUP_DIR_NAME}/thumbs/{relative}"
                    )

            for name in LOOSE_FILES:
                loose = settings.data_dir / name
                if loose.is_file():
                    yield from _add_to_archive(archive, stream, loose, f"{BACKUP_DIR_NAME}/{name}")

            archive.writestr(
                f"{BACKUP_DIR_NAME}/{MANIFEST_NAME}", manifest_bytes(photos, size, settings)
            )
            if data := stream.take():
                yield data

    # Closing the archive wrote the central directory into the stream.
    if data := stream.take():
        yield data

    record_backup(settings, ZIP_DRIVE_NAME)
    log.info("Archive streamed: %s photos, %s", photos, human_size(size))
