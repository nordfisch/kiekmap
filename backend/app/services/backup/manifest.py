# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""What a backup says about itself -- and how that is read back.

One reader for both shapes, the folder on the stick and the entry in the archive: a backup that
says one thing as a folder and another as an archive would be the worst kind of difference,
invisible until somebody restores from it.
"""

import json
import logging
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.config import Settings
from app.services.backup.common import (
    BACKUP_DIR_NAME,
    MANIFEST_NAME,
    place_name,
    stamp,
)

log = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    created_at: datetime
    photos: int
    bytes: int
    #: Which place wrote it. Helps when a stick has been to two museums.
    place: str = ""


def _parse_manifest(raw: bytes) -> BackupInfo | None:
    """One reader for both shapes -- the folder on the stick and the entry in the archive.

    They must never be read differently: a backup that says one thing as a folder and another as
    an archive would be the worst kind of difference, invisible until somebody restores from it.
    """
    try:
        data = json.loads(raw.decode("utf-8"))
        return BackupInfo(
            created_at=datetime.fromisoformat(data["created_at"]),
            photos=int(data["photos"]),
            bytes=int(data["bytes"]),
            place=str(data.get("place", "")),
        )
    except (json.JSONDecodeError, UnicodeDecodeError, KeyError, ValueError):
        return None


def read_manifest(folder: Path) -> BackupInfo | None:
    """The manifest of a backup, or None when there is none worth the name."""
    manifest = folder / MANIFEST_NAME
    if not manifest.is_file():
        return None
    try:
        info = _parse_manifest(manifest.read_bytes())
    except OSError:
        info = None
    if info is None:
        log.warning("Unreadable manifest at %s", manifest)
    return info


def is_restorable(folder: Path) -> bool:
    """A backup is only worth restoring when the database is in it too."""
    return read_manifest(folder) is not None and (folder / "kiekmap.db").is_file()


def manifest_bytes(photos: int, size: int, settings: Settings) -> bytes:
    """The manifest as bytes, so the stick writes a file and the archive adds an entry.

    One function, because a backup that says something different depending on the route it took
    would be the worst kind of difference: invisible until someone restores from it.
    """
    return json.dumps(
        {
            # UTC, like every other stored timestamp -- see services/dates.days_since.
            "created_at": stamp(),
            "photos": photos,
            "bytes": size,
            "place": place_name(settings),
        },
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")


def write_manifest(target: Path, photos: int, size: int, settings: Settings) -> None:
    (target / MANIFEST_NAME).write_bytes(manifest_bytes(photos, size, settings))


# --- an archive waiting in the inbox ----------------------------------------
#
# The way back for a downloaded backup: drop the file into the watched folder, and the admin area
# offers to restore from it. **It never restores by itself.** That folder otherwise does something
# additive and harmless -- one photo too many is one photo too many -- while this replaces the
# whole collection. So it is detected here and confirmed on screen, with the same question the
# stick already asks.


def looks_like_archive(name: str) -> bool:
    """Does this file name claim to be one of our backups?

    Only decides whether it is worth looking **inside**. What makes it a backup is the manifest in
    the archive -- a stranger's ZIP that happens to be named like ours is not offered.
    """
    return name.lower().startswith(BACKUP_DIR_NAME) and name.lower().endswith(".zip")


def read_archive_manifest(path: Path) -> BackupInfo | None:
    """The manifest out of a ZIP, without unpacking anything else.

    A half-copied file falls through here on its own: without its central directory ``zipfile``
    cannot open it at all. That is why the inbox watcher's size check is not needed for archives.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            entry = f"{BACKUP_DIR_NAME}/{MANIFEST_NAME}"
            if entry not in archive.namelist():
                return None
            info = _parse_manifest(archive.read(entry))
            # Only worth offering when the database is in there too.
            if info is None or f"{BACKUP_DIR_NAME}/kiekmap.db" not in archive.namelist():
                return None
            return info
    except (zipfile.BadZipFile, OSError):
        return None


def waiting_archive(settings: Settings) -> tuple[Path, BackupInfo] | None:
    """The newest backup lying in the inbox, if there is one.

    Newest by what the manifest says, not by file date: a file copied twice keeps its own date but
    not necessarily the right order. Further archives get their turn once this one is gone.
    """
    inbox = settings.incoming_dir
    if not inbox.is_dir():
        return None

    found: list[tuple[Path, BackupInfo]] = []
    for path in sorted(inbox.iterdir()):
        if not path.is_file() or not looks_like_archive(path.name):
            continue
        if (info := read_archive_manifest(path)) is not None:
            found.append((path, info))

    return max(found, key=lambda pair: pair[1].created_at) if found else None
