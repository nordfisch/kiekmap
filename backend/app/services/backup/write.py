"""Writing the collection onto a stick.

A folder, not a ZIP: an interrupted backup is then partly usable instead of entirely worthless,
and anyone can open it on any computer and find the pictures again. Incremental via the file
names, which are the SHA-256 of the content -- so a name already on the stick is the same image
and the second backup takes seconds.
"""

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import Settings
from app.services.backup.collection import (
    collection_size,
    copy_if_new,
    thumbnails_of,
    vacuum_into,
)
from app.services.backup.common import (
    BACKUP_DIR_NAME,
    LOOSE_FILES,
    BackupError,
    Report,
    human_size,
)
from app.services.backup.drives import Drive
from app.services.backup.manifest import write_manifest
from app.services.backup.state import record_backup

log = logging.getLogger(__name__)


def run_backup(session: Session, settings: Settings, drive: Drive, report: Report) -> str:
    """Write the collection onto the stick. Returns the German closing message."""
    target = drive.path / BACKUP_DIR_NAME
    target.mkdir(parents=True, exist_ok=True)

    photos, needed = collection_size(settings, max_age_s=0)
    if drive.free_bytes < needed:
        # Checked against the full size, not against what is still missing: an incremental backup
        # that only just fits today has no room for next year's photographs.
        raise BackupError(
            f"Auf dem Stick ist zu wenig Platz. Gebraucht werden {human_size(needed)}, "
            f"frei sind {human_size(drive.free_bytes)}."
        )

    report(0, photos, "Die Angaben werden gesichert")
    _backup_database(session, settings, target)

    written = 0
    done = 0
    for source in sorted(settings.photos_dir.rglob("*")):
        if not source.is_file():
            continue
        written += copy_if_new(source, target / "photos" / source.relative_to(settings.photos_dir))
        # The thumbnails belong to the same photo, so they travel with it. Without them a restored
        # device would spend an hour rendering them again before showing anything.
        for thumb in thumbnails_of(settings, source.stem):
            relative = thumb.relative_to(settings.thumbs_dir)
            written += copy_if_new(thumb, target / "thumbs" / relative)

        done += 1
        report(done, photos, f"Sichere Foto {done} von {photos}")

    for name in LOOSE_FILES:
        loose = settings.data_dir / name
        if loose.is_file():
            written += copy_if_new(loose, target / name)

    write_manifest(target, photos, needed, settings)
    record_backup(settings, drive.name)

    log.info("Backup finished: %s photos, %s written to %s", photos, human_size(written), target)
    # The database is rewritten every time -- the statements about the photos change even when the
    # photos do not. Only the images are incremental, and only about them can we say "nothing new".
    dazu = f"Neu dazugekommen: {human_size(written)}." if written else "Neue Bilder gab es nicht."
    # Every German message in this module is phrased so that it needs no umlaut -- they end up on
    # the screen, where "Sie koennen den Stick abziehen" would simply look wrong. See CLAUDE.md.
    return (
        f"{photos} Fotos und alle Angaben gesichert. {dazu} Der Stick kann jetzt abgezogen werden."
    )


def _backup_database(session: Session, settings: Settings, target: Path) -> None:
    """Written beside the old one and only then moved into place.

    An interrupted backup must not leave half a database on the stick, because that is exactly
    what someone would restore from a year later.
    """
    fresh = target / "kiekmap.db.neu"
    vacuum_into(session, fresh)
    fresh.replace(target / "kiekmap.db")
