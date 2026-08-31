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

This used to be one file of 938 lines doing six different things. The split follows the comment
bars that were already in it -- and this module is the door, so that ``from app.services import
backup`` keeps meaning what it always meant. That was the condition under which the split was
worth doing at all: the 908 lines of tests beside it had to stay as they were, because they are
the proof that nothing changed. Where to look:

    common.py      names, errors, the shared vocabulary
    manifest.py    what a backup says about itself, on a stick and inside an archive
    drives.py      which removable drives there are, and what is on them
    collection.py  what "the collection" is on disk: its size, and how it is copied
    write.py       writing it onto a stick
    archive.py     the same, as one downloadable file
    restore.py     bringing it back
    state.py       when the last backup was made
    job.py         the one long-running job, shared with the stick import

See docs/decisions.md, point 61.
"""

from app.services.backup.archive import ZIP_DRIVE_NAME, archive_name, stream_archive
from app.services.backup.collection import collection_size
from app.services.backup.common import (
    BACKUP_DIR_NAME,
    LOOSE_FILES,
    MANIFEST_NAME,
    OVERDUE_DAYS,
    RESTORE_WORK_DIR,
    SET_ASIDE_PREFIX,
    STATE_FILE,
    BackupError,
    JobResult,
    Report,
)
from app.services.backup.drives import Drive, find_drive, find_drives
from app.services.backup.job import Job, JobStatus, job
from app.services.backup.manifest import (
    BackupInfo,
    is_restorable,
    looks_like_archive,
    read_archive_manifest,
    read_manifest,
    waiting_archive,
)
from app.services.backup.restore import run_restore, run_restore_from_archive
from app.services.backup.state import BackupState, read_state, record_backup
from app.services.backup.write import run_backup

__all__ = [
    "BACKUP_DIR_NAME",
    "LOOSE_FILES",
    "MANIFEST_NAME",
    "OVERDUE_DAYS",
    "RESTORE_WORK_DIR",
    "SET_ASIDE_PREFIX",
    "STATE_FILE",
    "ZIP_DRIVE_NAME",
    "BackupError",
    "BackupInfo",
    "BackupState",
    "Drive",
    "Job",
    "JobResult",
    "JobStatus",
    "Report",
    "archive_name",
    "collection_size",
    "find_drive",
    "find_drives",
    "is_restorable",
    "job",
    "looks_like_archive",
    "read_archive_manifest",
    "read_manifest",
    "read_state",
    "record_backup",
    "run_backup",
    "run_restore",
    "run_restore_from_archive",
    "stream_archive",
    "waiting_archive",
]
