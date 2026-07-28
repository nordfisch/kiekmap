"""Watching the inbox folder.

Whatever is copied in here ends up in the database -- no login, no interface. For the museum team
this is the most convenient way to feed in a whole stack of scans.

**Why polling rather than file events:** A file event fires as soon as the file is created, not
when it has finished being written. An 80 MB TIFF copied over the network would therefore be
imported half-complete. On top of that, files dropped in while the service was restarting would
have events nobody heard. A sweep every few seconds that only touches files whose size has not
changed since the last look solves both at once -- and costs nothing on a Pi for one directory.
"""

import logging
import threading
from pathlib import Path

from app.config import Settings, get_settings
from app.db import SessionLocal
from app.services.importer import SPECIAL_DIRS, import_file

log = logging.getLogger(__name__)

#: How often to look.
INTERVAL_S = 5.0


class IncomingWatcher:
    def __init__(self, settings: Settings | None = None, interval: float = INTERVAL_S) -> None:
        self.settings = settings or get_settings()
        self.interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        #: File size at the previous sweep. Only once it stops changing is the file complete.
        self._sizes: dict[Path, int] = {}

    # --- lifecycle ----------------------------------------------------------

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="incoming", daemon=True)
        self._thread.start()
        log.info("Watching inbox folder: %s", self.settings.incoming_dir)

    def stop(self, timeout: float = 10.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            self._thread = None

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.scan_once()
            except Exception:  # noqa: BLE001 -- the watcher must never give up
                log.exception("Error while sweeping the inbox folder")
            self._stop.wait(self.interval)

    # --- one sweep ----------------------------------------------------------

    def _candidates(self) -> list[Path]:
        inbox = self.settings.incoming_dir
        if not inbox.is_dir():
            return []
        return [
            path
            for path in sorted(inbox.rglob("*"))
            if path.is_file()
            and not path.name.startswith(".")
            and not SPECIAL_DIRS & set(path.relative_to(inbox).parts)
        ]

    def scan_once(self) -> int:
        """Import whatever has finished being written. Returns how many."""
        seen: dict[Path, int] = {}
        ready: list[Path] = []

        for path in self._candidates():
            try:
                size = path.stat().st_size
            except OSError:
                continue  # vanished in the meantime
            seen[path] = size
            # Size unchanged since the last look -- and not zero, because a freshly created file
            # is empty at first.
            if size > 0 and self._sizes.get(path) == size:
                ready.append(path)

        self._sizes = seen

        if not ready:
            return 0

        count = 0
        with SessionLocal() as session:
            for path in ready:
                outcome = import_file(session, path, self.settings, move_aside=True)
                self._sizes.pop(path, None)
                log.info("%s: %s -- %s", outcome.result, path.name, outcome.message)
                if outcome.succeeded:
                    count += 1
            session.commit()

        return count
