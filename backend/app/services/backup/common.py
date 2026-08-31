"""Names, errors and the two or three things every part of the backup needs.

No logic of its own -- it exists so that the modules beside it do not have to import each other
just to agree on what a folder is called.
"""

import json
import logging
from collections.abc import Callable

from app.config import Settings
from app.services import dates

log = logging.getLogger(__name__)

# Fixed English, not translated. These are names in a file system: were they to follow
# ``KIEKMAP_LANGUAGE``, changing that setting would have to rename folders on the device and on
# every stick already written. The museum team sees them in a file manager, and the manual names
# them.
BACKUP_DIR_NAME = "kiekmap-backup"
MANIFEST_NAME = "backup.json"
SET_ASIDE_PREFIX = "before-"
RESTORE_WORK_DIR = "restore"

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

#: Read and write in slices this big. Large enough that a Pi is not doing syscalls all day, small
#: enough that an archive never sits in memory -- which is the whole point of streaming it.
ARCHIVE_CHUNK = 1024 * 1024


def stamp() -> str:
    """Now, as it goes into the JSON files -- the same clock the database writes.

    One clock for the whole device. A state file in local time next to a database in UTC would
    make every difference computed across the two wrong by the offset -- enough to turn last
    night's backup into "vorgestern". Since 19 August 2026 that clock has a name of its own, so
    that a third place cannot pick a different one; see ``dates.utc_now``.
    """
    return dates.utc_now().isoformat(timespec="seconds")


def place_name(settings: Settings) -> str:
    """The name of the village, from ``region.json``. Empty when it cannot be read."""
    if not (region := settings.region_file).is_file():
        return ""
    try:
        return str(json.loads(region.read_text(encoding="utf-8")).get("name", ""))
    except (json.JSONDecodeError, OSError):
        return ""


class BackupError(Exception):
    """Something the person at the screen has to know. The message is German."""


def human_size(size: int) -> str:
    """German, with a comma -- this text ends up on the screen."""
    for unit, factor in (("GB", 1000**3), ("MB", 1000**2), ("kB", 1000)):
        if size >= factor:
            return f"{size / factor:.1f}".replace(".", ",") + f" {unit}"
    return f"{size} Bytes"
