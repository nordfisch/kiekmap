# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""When the last backup was made -- a note about this device, not about the collection.

Deliberately not part of the backup itself: a stick carried to a second museum would otherwise
tell that museum when *this* device was last saved.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime

from app.config import Settings
from app.services import dates
from app.services.backup.common import OVERDUE_DAYS, STATE_FILE, stamp

log = logging.getLogger(__name__)


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
                "last_backup_at": stamp(),
                "last_drive": drive_name,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
