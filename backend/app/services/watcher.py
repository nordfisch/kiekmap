# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

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
from app.services import backup
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
            # A backup is not a photo. Without this line it would run into ``import_file``, be
            # "Kein lesbares Bild" there and land in ``_problem/``. Instead it stays put until
            # somebody in the admin area agrees -- see ``waiting_archive`` in
            # services/backup/manifest.py.
            # The inbox is to replace nothing of its own accord.
            and not backup.looks_like_archive(path.name)
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
                # ``root`` is the inbox itself: whoever copies in a stack filed by street has
                # said something about every photo in it -- see services/foldermeta.py.
                outcome = import_file(
                    session, path, self.settings, move_aside=True, root=self.settings.incoming_dir
                )
                self._sizes.pop(path, None)
                # Per file, not once for the whole sweep -- and that is not a matter of taste.
                # ``import_file`` moves the file to ``_erledigt/`` inside itself, before anything
                # is written down. Committed at the end, an exception on the fifth file would take
                # the rows of the first four with it while their sources lie in ``_erledigt/`` --
                # and the import log along with them, because its entries hang in the same
                # transaction. The one record that would have shown it is the one that is lost.
                # ``importer.import_from_folder`` has always done it this way.
                session.commit()
                log.info("%s: %s -- %s", outcome.result, path.name, outcome.message)
                if outcome.succeeded:
                    count += 1

        return count
