"""Bringing a backup back onto the device.

In three movements, and the order is the whole point: copy everything into a working folder beside
the collection, set the current state aside -- move, not delete -- and only then move the new one
into place. An interruption before the last step leaves the running collection untouched; after
it, the old state is still there under ``vorher-<date>``.
"""

import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from app.config import Settings
from app.services import schema
from app.services.backup.collection import copy_if_new, forget_size
from app.services.backup.common import (
    ARCHIVE_CHUNK,
    BACKUP_DIR_NAME,
    LOOSE_FILES,
    RESTORE_WORK_DIR,
    SET_ASIDE_PREFIX,
    BackupError,
    Report,
    human_size,
)
from app.services.backup.drives import Drive
from app.services.backup.manifest import is_restorable, read_archive_manifest, read_manifest

log = logging.getLogger(__name__)


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
    shutil.copy2(source / "kiekmap.db", work / "kiekmap.db")

    done = 0
    for path in sorted((source / "photos").rglob("*")):
        if not path.is_file():
            continue
        copy_if_new(path, work / "photos" / path.relative_to(source / "photos"))
        done += 1
        report(done, total, f"Hole Foto {done} von {total}")

    if (source / "thumbs").is_dir():
        for path in sorted((source / "thumbs").rglob("*")):
            if path.is_file():
                copy_if_new(path, work / "thumbs" / path.relative_to(source / "thumbs"))
    for name in LOOSE_FILES:
        if (source / name).is_file():
            copy_if_new(source / name, work / name)

    return _swap_in(settings, work, total, report)


def _prepare_work_dir(settings: Settings, needed: int) -> Path:
    """An empty working folder beside the collection -- and room for what goes into it."""
    free = shutil.disk_usage(settings.data_dir).free
    if free < needed:
        raise BackupError(
            f"Hier ist zu wenig Platz. Gebraucht werden {human_size(needed)}, "
            f"frei sind {human_size(free)}."
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

    **The schema is dealt with here, and the two halves sit on either side of the swap.** The
    refusal has to come first, while the collection is still untouched -- a backup this program
    cannot read must leave the device exactly as it was. The upgrade has to come last, because
    only then is the restored database the one at the configured path. See ``services/schema.py``
    for why any of this is needed.
    """
    if ahead := schema.is_ahead(work / "kiekmap.db"):
        # The working folder holds a whole collection; refusing is no reason to leave it lying
        # around. The archive it came from stays in the inbox, so nothing is lost.
        shutil.rmtree(work, ignore_errors=True)
        # Not a word about "newer": we know it is unknown, and that is a different statement.
        raise BackupError(
            "Diese Sicherung gehoert zu einer neueren Programmversion "
            f"(Schemastand {ahead}). Bitte erst das Programm aktualisieren, dann die Sicherung "
            "einspielen. Auf dem Geraet wurde nichts veraendert."
        )

    report(total, total, "Der bisherige Stand wird beiseitegelegt")
    set_aside = _set_aside(settings)

    for name in ("photos", "thumbs", "kiekmap.db", *LOOSE_FILES):
        moved = work / name
        if moved.exists():
            moved.replace(settings.data_dir / name)
    shutil.rmtree(work, ignore_errors=True)

    # Now, and not a step earlier: the file at the configured path is the restored one.
    report(total, total, "Der Schemastand wird nachgezogen")
    schema.bring_up_to_date(settings.db_path)

    # The collection is a different one now -- what was measured before says nothing any more.
    forget_size()

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

    Also takes the write-ahead log with it. A leftover ``kiekmap.db-wal`` next to a restored
    database would belong to a different database, and SQLite would try to apply it.
    """
    folder = settings.data_dir / f"{SET_ASIDE_PREFIX}{datetime.now():%Y-%m-%d-%H%M}"
    folder.mkdir(parents=True, exist_ok=True)

    for name in ("photos", "thumbs", "kiekmap.db", "kiekmap.db-wal", "kiekmap.db-shm"):
        current = settings.data_dir / name
        if current.exists():
            current.replace(folder / name)
    return folder
