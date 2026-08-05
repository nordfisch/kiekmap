"""Backup onto a USB stick, and restoring from one.

Deliberately a feature with a screen and a progress bar, not a shell script. The people who do
this are volunteers, once or twice a year; a script means in practice that it never runs. See
docs/decisions.md, point 11.

Four decisions shape what happens here:

  * **A folder, not a ZIP.** An interrupted backup is then partly usable instead of entirely
    worthless, and anyone can open it on any computer and find the pictures again.
  * **Incremental via the file names.** They are the SHA-256 of the content, so a name that is
    already on the stick is the same image. The second backup takes seconds.
  * **``VACUUM INTO``** writes the database out consistently while the kiosk keeps running -- and
    produces a single file without a write-ahead log beside it.
  * **Restoring never destroys the running collection.** Everything is copied in beside it and
    only swapped at the very end; what was there is set aside, not deleted.
"""

import json
import logging
import os
import shutil
import tempfile
import threading
import time
import zipfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings
from app.services import dates, places

log = logging.getLogger(__name__)

# German names: the museum team sees these in a file manager on any computer.
BACKUP_DIR_NAME = "photomap-sicherung"
MANIFEST_NAME = "sicherung.json"
SET_ASIDE_PREFIX = "vorher-"
RESTORE_WORK_DIR = "wiederherstellung"

#: Where the date of the last backup is noted. In the data directory, but deliberately *not* part
#: of the backup: it says something about this device, not about the collection.
STATE_FILE = "backup-state.json"

#: From this many days on, the admin area shows the reminder in red.
OVERDUE_DAYS = 30

#: Files in the data directory that belong in the backup. The inbox is missing on purpose -- it is
#: a working folder, and what was imported from it is in the collection anyway.
LOOSE_FILES = ("region.json", "places.json")

#: Report progress: done, total, message.
Report = Callable[[int, int, str], None]

#: What a job hands back: the closing message, or that plus rows for the screen. The backup and
#: the restore have nothing to show afterwards, so they return the message alone.
JobResult = str | tuple[str, list[dict] | None]


def _stamp() -> str:
    """Now, as it goes into the JSON files: UTC, and without the marker saying so.

    One clock for the whole device. The database writes UTC anyway (``func.now()``), and a state
    file in local time next to it would make every difference computed across the two wrong by the
    offset -- enough to turn last night's backup into "vorgestern".
    """
    return datetime.now(UTC).replace(tzinfo=None).isoformat(timespec="seconds")


# --- what is on the stick ---------------------------------------------------


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
    return read_manifest(folder) is not None and (folder / "photomap.db").is_file()


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
            if info is None or f"{BACKUP_DIR_NAME}/photomap.db" not in archive.namelist():
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


# --- drives -----------------------------------------------------------------


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
    development ``PHOTOMAP_MEDIA_DIR=/Volumes`` does the same job.

    Only actual mount points count, and only writable ones. Without the first check an ordinary
    leftover folder under /media would be offered as a target -- and the backup would land on the
    same SD card it is supposed to protect against. The second sorts out system mounts and
    write-protected media, which would otherwise fail only after the button had been pressed.
    """
    if not media_dir.is_dir():
        return []

    mounted: list[Path] = []
    try:
        entries = sorted(media_dir.iterdir())
    except OSError:
        return []

    for entry in entries:
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if _is_mounted(entry):
            mounted.append(entry)
            continue
        try:
            mounted.extend(
                sub for sub in sorted(entry.iterdir()) if sub.is_dir() and _is_mounted(sub)
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


# --- size of the collection -------------------------------------------------


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


# --- the backup -------------------------------------------------------------


def _copy_if_new(source: Path, target: Path) -> int:
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


def run_backup(session: Session, settings: Settings, drive: Drive, report: Report) -> str:
    """Write the collection onto the stick. Returns the German closing message."""
    target = drive.path / BACKUP_DIR_NAME
    target.mkdir(parents=True, exist_ok=True)

    photos, needed = collection_size(settings, max_age_s=0)
    if drive.free_bytes < needed:
        # Checked against the full size, not against what is still missing: an incremental backup
        # that only just fits today has no room for next year's photographs.
        raise BackupError(
            f"Auf dem Stick ist zu wenig Platz. Gebraucht werden {_human(needed)}, "
            f"frei sind {_human(drive.free_bytes)}."
        )

    report(0, photos, "Die Angaben werden gesichert")
    _backup_database(session, settings, target)

    written = 0
    done = 0
    for source in sorted(settings.photos_dir.rglob("*")):
        if not source.is_file():
            continue
        written += _copy_if_new(source, target / "photos" / source.relative_to(settings.photos_dir))
        # The thumbnails belong to the same photo, so they travel with it. Without them a restored
        # device would spend an hour rendering them again before showing anything.
        for thumb in _thumbnails_of(settings, source.stem):
            relative = thumb.relative_to(settings.thumbs_dir)
            written += _copy_if_new(thumb, target / "thumbs" / relative)

        done += 1
        report(done, photos, f"Sichere Foto {done} von {photos}")

    for name in LOOSE_FILES:
        loose = settings.data_dir / name
        if loose.is_file():
            written += _copy_if_new(loose, target / name)

    _write_manifest(target, photos, needed, settings)
    record_backup(settings, drive.name)

    log.info("Backup finished: %s photos, %s written to %s", photos, _human(written), target)
    # The database is rewritten every time -- the statements about the photos change even when the
    # photos do not. Only the images are incremental, and only about them can we say "nothing new".
    dazu = f"Neu dazugekommen: {_human(written)}." if written else "Neue Bilder gab es nicht."
    # Every German message in this module is phrased so that it needs no umlaut -- they end up on
    # the screen, where "Sie koennen den Stick abziehen" would simply look wrong. See CLAUDE.md.
    return (
        f"{photos} Fotos und alle Angaben gesichert. {dazu} Der Stick kann jetzt abgezogen werden."
    )


def _thumbnails_of(settings: Settings, sha256: str):
    for size_dir in sorted(settings.thumbs_dir.glob("*")):
        candidate = size_dir / sha256[0:2] / sha256[2:4] / f"{sha256}.webp"
        if candidate.is_file():
            yield candidate


def _vacuum_into(session: Session, target: Path) -> None:
    """``VACUUM INTO`` writes a consistent copy while the kiosk keeps reading.

    Refuses to overwrite, hence the unlink first. Both ways out of the collection use this -- the
    stick and the archive -- so that neither ever copies the live file with its write-ahead log
    beside it.
    """
    target.unlink(missing_ok=True)
    session.execute(text("VACUUM INTO :target"), {"target": str(target)})
    session.commit()


def _backup_database(session: Session, settings: Settings, target: Path) -> None:
    """Written beside the old one and only then moved into place.

    An interrupted backup must not leave half a database on the stick, because that is exactly
    what someone would restore from a year later.
    """
    fresh = target / "photomap.db.neu"
    _vacuum_into(session, fresh)
    fresh.replace(target / "photomap.db")


def _place(settings: Settings) -> str:
    """The name of the village, from ``region.json``. Empty when it cannot be read."""
    if not (region := settings.region_file).is_file():
        return ""
    try:
        return str(json.loads(region.read_text(encoding="utf-8")).get("name", ""))
    except (json.JSONDecodeError, OSError):
        return ""


def _manifest_bytes(photos: int, size: int, settings: Settings) -> bytes:
    """The manifest as bytes, so the stick writes a file and the archive adds an entry.

    One function, because a backup that says something different depending on the route it took
    would be the worst kind of difference: invisible until someone restores from it.
    """
    return json.dumps(
        {
            # UTC, like every other stored timestamp -- see services/dates.days_since.
            "created_at": _stamp(),
            "photos": photos,
            "bytes": size,
            "place": _place(settings),
        },
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")


def _write_manifest(target: Path, photos: int, size: int, settings: Settings) -> None:
    (target / MANIFEST_NAME).write_bytes(_manifest_bytes(photos, size, settings))


class BackupError(Exception):
    """Something the person at the screen has to know. The message is German."""


# --- the same backup, as one file -------------------------------------------
#
# The second route out of the collection: a download through the browser, for when no stick is at
# hand. It is the **addition**, not the replacement -- see docs/decisions.md, point 11. The stick
# writes only what is new and stays usable when it breaks off halfway; this packs everything every
# time and an interrupted download is worthless.
#
# What makes the addition defensible is the shape: **the archive is the very folder the stick
# gets, only zipped.** Unpack it onto a stick and the existing restore takes it. That property is
# the reason a missing upload route is an inconvenience rather than a gap, and
# tests/test_backup.py guards it.

#: Read in slices this big. Large enough that a Pi is not doing syscalls all day, small enough
#: that the archive never sits in memory -- which is the whole point of streaming it.
ARCHIVE_CHUNK = 1024 * 1024

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
    """``photomap-sicherung-holm-2026-08-03.zip``.

    Plain ASCII: it travels in an HTTP header and lands as a file name on somebody's computer.
    """
    slug = "".join(c for c in places.normalize(_place(settings)) if c.isalnum() or c == "-")
    place = f"-{slug}" if slug else ""
    return f"{BACKUP_DIR_NAME}{place}-{datetime.now(UTC):%Y-%m-%d}.zip"


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
        database = Path(tmp) / "photomap.db"
        _vacuum_into(session, database)

        with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED, allowZip64=True) as archive:
            yield from _add_to_archive(archive, stream, database, f"{BACKUP_DIR_NAME}/photomap.db")

            for source in sorted(settings.photos_dir.rglob("*")):
                if not source.is_file():
                    continue
                relative = source.relative_to(settings.photos_dir).as_posix()
                yield from _add_to_archive(
                    archive, stream, source, f"{BACKUP_DIR_NAME}/photos/{relative}"
                )
                # The thumbnails travel with their photo, exactly as onto the stick: without them
                # a restored device spends an hour rendering before it shows anything.
                for thumb in _thumbnails_of(settings, source.stem):
                    relative = thumb.relative_to(settings.thumbs_dir).as_posix()
                    yield from _add_to_archive(
                        archive, stream, thumb, f"{BACKUP_DIR_NAME}/thumbs/{relative}"
                    )

            for name in LOOSE_FILES:
                loose = settings.data_dir / name
                if loose.is_file():
                    yield from _add_to_archive(archive, stream, loose, f"{BACKUP_DIR_NAME}/{name}")

            archive.writestr(
                f"{BACKUP_DIR_NAME}/{MANIFEST_NAME}", _manifest_bytes(photos, size, settings)
            )
            if data := stream.take():
                yield data

    # Closing the archive wrote the central directory into the stream.
    if data := stream.take():
        yield data

    record_backup(settings, ZIP_DRIVE_NAME)
    log.info("Archive streamed: %s photos, %s", photos, _human(size))


# --- restoring --------------------------------------------------------------


def run_restore(settings: Settings, drive: Drive, report: Report) -> str:
    """Bring a backup from the stick back onto the device.

    In three movements, and the order is the whole point:

      1. Copy everything from the stick into a working folder beside the collection.
      2. Set the current state aside -- move, not delete.
      3. Move the new one into place.

    An interruption before step 3 leaves the running collection untouched. After step 3 the old
    state is still there under ``vorher-<date>``, so even a restore of the wrong backup is not
    the end.
    """
    source = drive.path / BACKUP_DIR_NAME
    if not is_restorable(source):
        raise BackupError("Auf diesem Stick fehlt eine Sicherung, oder sie ist nicht komplett.")

    manifest = read_manifest(source)
    assert manifest is not None  # is_restorable checked it

    work = _prepare_work_dir(settings, manifest.bytes)

    total = sum(1 for path in (source / "photos").rglob("*") if path.is_file())
    report(0, total, "Zuerst kommen die Angaben")
    shutil.copy2(source / "photomap.db", work / "photomap.db")

    done = 0
    for path in sorted((source / "photos").rglob("*")):
        if not path.is_file():
            continue
        _copy_if_new(path, work / "photos" / path.relative_to(source / "photos"))
        done += 1
        report(done, total, f"Hole Foto {done} von {total}")

    if (source / "thumbs").is_dir():
        for path in sorted((source / "thumbs").rglob("*")):
            if path.is_file():
                _copy_if_new(path, work / "thumbs" / path.relative_to(source / "thumbs"))
    for name in LOOSE_FILES:
        if (source / name).is_file():
            _copy_if_new(source / name, work / name)

    return _swap_in(settings, work, total, report)


def _prepare_work_dir(settings: Settings, needed: int) -> Path:
    """An empty working folder beside the collection -- and room for what goes into it."""
    free = shutil.disk_usage(settings.data_dir).free
    if free < needed:
        raise BackupError(
            f"Hier ist zu wenig Platz. Gebraucht werden {_human(needed)}, frei sind {_human(free)}."
        )

    work = settings.data_dir / RESTORE_WORK_DIR
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    return work


def _swap_in(settings: Settings, work: Path, total: int, report: Report) -> str:
    """Movements two and three: set the old state aside, then move the new one into place.

    Shared by both routes -- the stick and the archive -- because this is the part that must not
    differ. Everything before it only fills the working folder; from here on the collection on the
    device changes, and it changes the same way whatever the backup came in as.
    """
    report(total, total, "Der bisherige Stand wird beiseitegelegt")
    set_aside = _set_aside(settings)

    for name in ("photos", "thumbs", "photomap.db", *LOOSE_FILES):
        moved = work / name
        if moved.exists():
            moved.replace(settings.data_dir / name)
    shutil.rmtree(work, ignore_errors=True)

    # The collection is a different one now -- what was measured before says nothing any more.
    global _size_cache
    _size_cache = None

    log.info("Restore finished: %s photos, previous state at %s", total, set_aside)
    return (
        f"{total} Fotos und alle Angaben sind wieder da. Der bisherige Stand liegt im Ordner "
        f"{set_aside.name} und kann weg, sobald alles stimmt."
    )


def run_restore_from_archive(settings: Settings, archive: Path, report: Report) -> str:
    """The same restore, out of a ZIP file lying in the inbox.

    **Unpacked straight into the working folder**, not first beside it: otherwise the archive, the
    unpacked copy, the working folder and the old state would all lie there at once -- four times
    the collection. This way it stays at three, and three is the floor as long as the archive is
    its own source.

    Afterwards the file moves to ``_erledigt/``, like every photo that came through this folder.
    It keeps taking up room there, which is why the closing message says so.
    """
    info = read_archive_manifest(archive)
    if info is None:
        raise BackupError("Diese Datei ist keine vollstaendige Sicherung.")

    work = _prepare_work_dir(settings, info.bytes)
    prefix = f"{BACKUP_DIR_NAME}/"

    with zipfile.ZipFile(archive) as opened:
        entries = [e for e in opened.infolist() if not e.is_dir() and e.filename.startswith(prefix)]
        total = sum(1 for e in entries if e.filename.startswith(f"{prefix}photos/"))

        report(0, total, "Zuerst kommen die Angaben")
        done = 0
        for entry in entries:
            relative = entry.filename[len(prefix) :]
            # An entry that leads out of the work directory did not come from our archive.
            target = (work / relative).resolve()
            if not target.is_relative_to(work.resolve()):
                raise BackupError("Die Datei enthaelt einen unerwarteten Eintrag.")

            target.parent.mkdir(parents=True, exist_ok=True)
            with opened.open(entry) as source, target.open("wb") as sink:
                shutil.copyfileobj(source, sink, ARCHIVE_CHUNK)

            if relative.startswith("photos/"):
                done += 1
                report(done, total, f"Hole Foto {done} von {total}")

    message = _swap_in(settings, work, total, report)

    # Imported here rather than at module level, where it would close a ring: the importer in
    # turn is to know nothing about the backup.
    from app.services.importer import DONE_DIR, move_to_done

    move_to_done(archive, settings.incoming_dir)
    return (
        f"{message} Die eingespielte Datei liegt jetzt im Ordner {DONE_DIR} und kann ebenfalls weg."
    )


def _set_aside(settings: Settings) -> Path:
    """Move the current state out of the way -- never delete it.

    Also takes the write-ahead log with it. A leftover ``photomap.db-wal`` next to a restored
    database would belong to a different database, and SQLite would try to apply it.
    """
    folder = settings.data_dir / f"{SET_ASIDE_PREFIX}{datetime.now():%Y-%m-%d-%H%M}"
    folder.mkdir(parents=True, exist_ok=True)

    for name in ("photos", "thumbs", "photomap.db", "photomap.db-wal", "photomap.db-shm"):
        current = settings.data_dir / name
        if current.exists():
            current.replace(folder / name)
    return folder


# --- when was the last one? -------------------------------------------------


@dataclass
class BackupState:
    last_backup_at: datetime | None = None
    last_drive: str = ""

    @property
    def days_since(self) -> int | None:
        if self.last_backup_at is None:
            return None
        return dates.days_since(self.last_backup_at)

    @property
    def overdue(self) -> bool:
        """Never backed up counts as overdue -- that is the case worth nagging about."""
        days = self.days_since
        return days is None or days >= OVERDUE_DAYS


def read_state(settings: Settings) -> BackupState:
    path = settings.data_dir / STATE_FILE
    if not path.is_file():
        return BackupState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return BackupState(
            last_backup_at=datetime.fromisoformat(data["last_backup_at"]),
            last_drive=str(data.get("last_drive", "")),
        )
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return BackupState()


def record_backup(settings: Settings, drive_name: str) -> None:
    (settings.data_dir / STATE_FILE).write_text(
        json.dumps(
            {
                "last_backup_at": _stamp(),
                "last_drive": drive_name,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# --- the one long-running job -----------------------------------------------


@dataclass
class JobStatus:
    kind: str = "none"
    phase: str = "idle"
    done: int = 0
    total: int = 0
    message: str = ""
    error: str | None = None
    #: What the finished job produced, when that is worth passing on -- the stick import puts its
    #: rows here so the screen can offer the same review table as the upload does. Plain data, so
    #: the job stays free of the API's shapes; the caller decides how much is worth sending.
    items: list[dict] | None = None


class Job:
    """Backup and restore run in a thread; the screen asks how far along it is.

    Only one at a time, for the whole device. Two backups onto the same stick would fight over
    the same files, and a restore during a backup would produce a copy of two different states.

    Like the admin sessions this lives in memory: a restart cancels the job, which is the honest
    outcome anyway -- the thread does not survive it either.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._status = JobStatus()
        self._thread: threading.Thread | None = None

    def status(self) -> JobStatus:
        with self._lock:
            return JobStatus(**self._status.__dict__)

    @property
    def running(self) -> bool:
        with self._lock:
            return self._status.phase == "running"

    def start(self, kind: str, work: Callable[[Report], "JobResult"]) -> bool:
        """False when something is already running.

        ``work`` returns the closing message, and optionally rows for the screen to show.
        """
        with self._lock:
            if self._status.phase == "running":
                return False
            self._status = JobStatus(kind=kind, phase="running", message="Wird vorbereitet")

        def run() -> None:
            try:
                outcome = work(self._report)
                message, items = outcome if isinstance(outcome, tuple) else (outcome, None)
                with self._lock:
                    self._status.phase = "done"
                    self._status.message = message
                    self._status.items = items
                    self._status.done = self._status.total
            except BackupError as error:
                self._fail(str(error))
            except Exception as error:  # noqa: BLE001 -- the screen must not just stop moving
                log.exception("%s failed", kind)
                self._fail(f"Es ist etwas schiefgegangen: {error}")

        self._thread = threading.Thread(target=run, name=f"photomap-{kind}", daemon=True)
        self._thread.start()
        return True

    def _report(self, done: int, total: int, message: str) -> None:
        with self._lock:
            self._status.done, self._status.total, self._status.message = done, total, message

    def _fail(self, message: str) -> None:
        with self._lock:
            self._status.phase = "error"
            self._status.error = message

    def reset(self) -> None:
        """Back to idle after the screen has shown the result."""
        with self._lock:
            if self._status.phase != "running":
                self._status = JobStatus()


#: One job for the process.
job = Job()


# --- formatting -------------------------------------------------------------


def _human(size: int) -> str:
    """German, with a comma -- this text ends up on the screen."""
    for unit, factor in (("GB", 1000**3), ("MB", 1000**2), ("kB", 1000)):
        if size >= factor:
            return f"{size / factor:.1f}".replace(".", ",") + f" {unit}"
    return f"{size} Bytes"
