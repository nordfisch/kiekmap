"""Removable drives, as the device sees them.

The one module that talks to the operating system about mount points -- and the one where a
symlink under /media has already cost a backup that landed inside the folder it was backing up.
"""

import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from app.services.backup.common import BACKUP_DIR_NAME
from app.services.backup.manifest import BackupInfo, read_manifest

log = logging.getLogger(__name__)


@dataclass
class Drive:
    path: Path
    #: The volume label, as it appears in a file manager.
    name: str
    total_bytes: int
    free_bytes: int
    #: The backup already on this stick, if there is one.
    backup: BackupInfo | None = None


def _is_mounted(path: Path) -> bool:
    """Own function so tests can stand in for it -- a real mount cannot be faked."""
    return path.is_mount()


def _is_writable(path: Path) -> bool:
    """A target that cannot be written to is no target.

    This is what sorts out the mounts that are technically there but useless: system mounts the
    service may not write to, a write-protected stick, a CD. Without the check they would be
    offered, and the backup would fail after the person had already pressed the button.
    """
    return os.access(path, os.W_OK)


def find_drives(media_dir: Path) -> list[Drive]:
    """Removable drives, as the device sees them.

    Two levels deep, because the naming differs: Raspberry Pi OS mounts under
    ``/media/<user>/<label>``, other systems directly under ``/media/<label>``. On a Mac during
    development ``KIEKMAP_MEDIA_DIR=/Volumes`` does the same job.

    Only actual mount points count, and only writable ones. Without the first check an ordinary
    leftover folder under /media would be offered as a target -- and the backup would land on the
    same SD card it is supposed to protect against. The second sorts out system mounts and
    write-protected media, which would otherwise fail only after the button had been pressed.

    **A symlink is never a drive**, and that is not a detail: ``os.path.ismount`` answers False
    for one on principle ("a symlink can never be a mount point"). A symlink under /media would
    therefore look like an ordinary folder, the descent one level down would follow it, and
    whatever mounts lie behind it would be offered as backup targets.

    **On macOS that was the rule, not an accident:** /Volumes always holds a symlink to ``/``
    named after the internal volume. Measured on 14 August 2026 -- the panel offered the data
    directory itself, and the backup landed inside the very folder it was backing up, with a
    manifest that made it look real. Exactly the failure the mount check above exists to prevent.
    """
    if not media_dir.is_dir():
        return []

    mounted: list[Path] = []
    try:
        entries = sorted(media_dir.iterdir())
    except OSError:
        return []

    for entry in entries:
        if entry.is_symlink() or not entry.is_dir() or entry.name.startswith("."):
            continue
        if _is_mounted(entry):
            mounted.append(entry)
            continue
        try:
            mounted.extend(
                sub
                for sub in sorted(entry.iterdir())
                if not sub.is_symlink() and sub.is_dir() and _is_mounted(sub)
            )
        except OSError:
            continue

    drives = []
    for path in mounted:
        if not _is_writable(path):
            continue
        try:
            usage = shutil.disk_usage(path)
        except OSError:
            continue
        drives.append(
            Drive(
                path=path,
                name=path.name,
                total_bytes=usage.total,
                free_bytes=usage.free,
                backup=read_manifest(path / BACKUP_DIR_NAME),
            )
        )
    return drives


def find_drive(media_dir: Path, path: str) -> Drive | None:
    """Look up a drive the browser named. Never trust the path itself.

    The path comes back from the client, so it is input, not a fact. Only what ``find_drives``
    found counts -- otherwise ``/`` would be an acceptable backup target.
    """
    wanted = Path(path)
    return next((drive for drive in find_drives(media_dir) if drive.path == wanted), None)
