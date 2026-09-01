"""The one long-running job of the device.

Backup, restore and the stick import share it: they run in a thread, the screen asks how far along
they are, and only one may run at a time. Two backups onto the same stick would fight over the
same files, and a restore during a backup would produce a copy of two different states.
"""

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass

from app.services.backup.common import BackupError, JobResult, Report
from app.text import texts

log = logging.getLogger(__name__)


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
            self._status = JobStatus(kind=kind, phase="running", message=texts().backup.preparing)

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
                self._fail(texts().backup.something_went_wrong(str(error)))

        self._thread = threading.Thread(target=run, name=f"kiekmap-{kind}", daemon=True)
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


#: One job for the process.
job = Job()
