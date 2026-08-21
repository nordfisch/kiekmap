# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""What "the collection" is on the disk -- how big it is, and how it is copied.

Shared by all three routes out of it: the stick, the archive and the restore. That it lives in one
module rather than in each of them is the point -- the stick and the archive have to copy the same
set of files, or an archive unpacked onto a stick would no longer be a backup.
"""

import logging
import shutil
import time
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings
from app.services.backup.common import LOOSE_FILES

log = logging.getLogger(__name__)


#: Last measurement: (data directory, taken at, result). See ``collection_size``.
#:
#: Keyed by the directory, not just by time -- otherwise a second data directory would be handed
#: the numbers of the first, which is exactly what happens in the test suite.
_size_cache: tuple[Path, float, tuple[int, int]] | None = None
SIZE_CACHE_S = 20.0


def collection_size(settings: Settings, *, max_age_s: float = SIZE_CACHE_S) -> tuple[int, int]:
    """(number of photos, bytes of everything that goes onto the stick).

    Measured on the filesystem rather than taken from the database: the files are what gets
    copied, and a database that has drifted from them must not produce a wrong promise.

    Briefly cached, because the drive list is polled every few seconds while someone stands in
    front of the screen with a stick in their hand -- and walking several thousand files that
    often is real work on a Pi. The backup itself passes ``max_age_s=0``: there the number
    decides whether the stick is big enough, and it has to be current.
    """
    global _size_cache

    if (
        _size_cache is not None
        and _size_cache[0] == settings.data_dir
        and time.monotonic() - _size_cache[1] <= max_age_s
    ):
        return _size_cache[2]

    photos = 0
    total = 0

    for path in settings.photos_dir.rglob("*"):
        if path.is_file():
            photos += 1
            total += path.stat().st_size
    for path in settings.thumbs_dir.rglob("*"):
        if path.is_file():
            total += path.stat().st_size
    if settings.db_path.is_file():
        total += settings.db_path.stat().st_size
    for name in LOOSE_FILES:
        if (settings.data_dir / name).is_file():
            total += (settings.data_dir / name).stat().st_size

    _size_cache = (settings.data_dir, time.monotonic(), (photos, total))
    return photos, total


def forget_size() -> None:
    """Throw the measurement away.

    Called by the restore: the collection is a different one afterwards, and what was measured
    before says nothing any more. Its own function because the cache lives here -- before the
    split the restore reached into it with ``global``, which only worked while both stood in the
    same file.
    """
    global _size_cache
    _size_cache = None


def copy_if_new(source: Path, target: Path) -> int:
    """Copy unless the same file is already there. Returns the bytes written.

    "The same" means equal name and equal size. The name is the SHA-256 of the content, so an
    equal name already guarantees equal content; the size only catches a copy that broke off
    halfway.
    """
    size = source.stat().st_size
    if target.is_file() and target.stat().st_size == size:
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return size


def thumbnails_of(settings: Settings, sha256: str):
    for size_dir in sorted(settings.thumbs_dir.glob("*")):
        candidate = size_dir / sha256[0:2] / sha256[2:4] / f"{sha256}.webp"
        if candidate.is_file():
            yield candidate


def vacuum_into(session: Session, target: Path) -> None:
    """``VACUUM INTO`` writes a consistent copy while the kiosk keeps reading.

    Refuses to overwrite, hence the unlink first. Both ways out of the collection use this -- the
    stick and the archive -- so that neither ever copies the live file with its write-ahead log
    beside it.
    """
    target.unlink(missing_ok=True)
    session.execute(text("VACUUM INTO :target"), {"target": str(target)})
    session.commit()
