"""Database wiring.

SQLite runs with a WAL journal here. That is the mode in which reads and writes do not block each
other -- important because the import thread writes while the kiosk reads -- and in which
``VACUUM INTO`` produces a consistent backup copy while the service is running.
"""

import fcntl
import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Settings, get_settings

#: How long a restore waits for the sessions in use to finish before it gives up.
#:
#: Long enough for the watcher to finish the file it is importing, a large TIFF on a Pi included.
#: A ZIP download holds its session for minutes; the restore should fail and say so, not wait.
CLOSE_TIMEOUT_S = 60.0


class Base(DeclarativeBase):
    """Base class for all tables."""


@event.listens_for(Engine, "connect")
def _configure_sqlite(dbapi_connection, connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    # Trade-off between speed and safety; with WAL the database stays consistent even on power
    # loss -- at worst the last transaction is missing.
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def create_db_engine() -> Engine:
    settings = get_settings()
    settings.ensure_dirs()
    return create_engine(
        settings.db_url,
        # The inbox watcher runs in its own thread and does not need the same connection.
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class DatabaseClosed(Exception):
    """The database file is being swapped. ``app.main`` answers 503 for it."""


class DatabaseInUse(Exception):
    """A session stayed in use for longer than a swap may wait."""


class DatabaseGate:
    """Counts the sessions in use, so that a restore can swap the file under none of them.

    **A restore renames the database file.** A pooled connection keeps writing into the renamed
    file, so a visitor's contribution during the swap lands in the set-aside state and is gone.
    SQLite's documentation also lists renaming a database file while it is in use among the ways to
    corrupt it. See ``docs/developer/decisions.md``, point 84, for what a test found about that.

    The gate closes only for the swap itself, which takes seconds; the copying before it runs with
    the database open. Whoever asks for a session meanwhile gets ``DatabaseClosed``.

    Every session the running service opens goes through here: requests, the readiness probe, the
    inbox watcher and the ZIP download. **Two exceptions, both deliberate.** The job's own sessions
    -- backup and stick import -- need no gate, because only one job runs at a time and a restore
    is that job. And the CLI runs in a process of its own, which no lock in this one can reach;
    ``collection_lock`` below keeps it apart from a restore instead.
    """

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._in_use = 0
        self._closed = False

    @contextmanager
    def use(self) -> Iterator[None]:
        with self._condition:
            if self._closed:
                raise DatabaseClosed
            self._in_use += 1
        try:
            yield
        finally:
            with self._condition:
                self._in_use -= 1
                self._condition.notify_all()

    @contextmanager
    def closed(self, timeout_s: float) -> Iterator[None]:
        """Refuse new sessions, wait until none is in use, and open again afterwards."""
        with self._condition:
            self._closed = True
            if not self._condition.wait_for(lambda: self._in_use == 0, timeout_s):
                self._closed = False
                raise DatabaseInUse
        try:
            yield
        finally:
            with self._condition:
                self._closed = False


gate = DatabaseGate()


@contextmanager
def closed_for_swap(timeout_s: float | None = None) -> Iterator[None]:
    """Close every connection, let the caller swap the file, and connect to what is there then.

    ``dispose()`` closes only the connections that are back in the pool. That is why the gate
    comes first: once no session is in use, every connection is back, and none stays open on the
    old file when it is renamed.

    Raises ``DatabaseInUse`` before anything is closed, so a refusal leaves the service as it was.
    """
    global engine

    with gate.closed(CLOSE_TIMEOUT_S if timeout_s is None else timeout_s):
        engine.dispose()
        try:
            yield
        finally:
            engine = create_db_engine()
            SessionLocal.configure(bind=engine)


class CollectionLocked(Exception):
    """The other side holds the lock file: a restore, or a CLI command that writes."""


@contextmanager
def collection_lock(settings: Settings, *, exclusive: bool) -> Iterator[None]:
    """Keep a restore and the writing CLI commands apart, across processes.

    ``DatabaseGate`` counts sessions in this process only; ``python -m app.cli`` runs in its own.
    A command that kept writing through a restore wrote its rows into the database that was set
    aside, and its files into ``photos/`` on either side of the move -- and reported success.

    **Shared** for the CLI, so that two commands do not exclude each other. **Exclusive** for the
    restore, so that it excludes every command, and every command excludes it.

    **Both sides refuse rather than wait.** A command waiting for a restore of twenty minutes looks
    like a command that hangs; a restore waiting for an import of a few thousand scans looks like a
    progress bar that hangs.

    ``flock`` rather than a marker file, because the kernel releases the lock when the process
    ends -- after a crash and a power cut too. A marker file outlives both and blocks the next
    restore for no reason. The lock also reaches a command run in a second container, because on
    Linux every container sees the same inode. **Not under Docker Desktop on a Mac:** its file
    sharing ignores ``flock``, even inside one container. See ``docs/developer/decisions.md``,
    point 84.
    """
    try:
        fd = _flock(settings.lock_path, exclusive=exclusive)
    except BlockingIOError:
        raise CollectionLocked from None
    try:
        yield
    finally:
        # Closing the descriptor releases the lock.
        os.close(fd)


class BackendAlreadyRunning(Exception):
    """Another backend process holds the process lock on the same data directory."""


@contextmanager
def process_lock(settings: Settings) -> Iterator[None]:
    """Let exactly one backend process run on a data directory.

    Admin sessions, download tickets, the PIN lockout, the one backup job and ``DatabaseGate`` live
    in the memory of one process. A second worker -- ``--workers 2`` or ``WEB_CONCURRENCY`` --
    would drop sign-ins depending on which process answers, allow the lockout's attempts once per
    process, run two jobs at once, and leave the gate protecting nothing.

    Exclusive and non-blocking: the second process ends at startup instead of waiting. Under
    ``uvicorn --workers 2`` that stops the parent too, because the worker fails before it serves.

    **A file of its own, not ``kiekmap.lock``.** The writing CLI commands take that one shared while
    the backend runs; an exclusive lock there for the life of the backend would refuse every one of
    them. See ``collection_lock``.

    ``uvicorn --reload`` still works: the reloader ends the old process before it starts the new
    one. **Not under Docker Desktop on a Mac:** its file sharing ignores ``flock``, so there the
    lock lets a second process through.
    """
    try:
        fd = _flock(settings.process_lock_path, exclusive=True)
    except BlockingIOError:
        raise BackendAlreadyRunning(
            f"Another Kiekmap backend is already running: it holds {settings.process_lock_path}. "
            "This process stops, because a second one would split sign-ins, the PIN lockout and "
            "the backup job between them."
        ) from None
    try:
        yield
    finally:
        os.close(fd)


def _flock(path: Path, *, exclusive: bool) -> int:
    """Take ``flock`` on ``path`` and return the descriptor that holds it.

    Raises ``BlockingIOError`` at once if another descriptor holds a conflicting lock -- one in the
    same process included. Closing the returned descriptor releases the lock.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Read-only is enough for flock, and it opens a lock file another user created.
    fd = os.open(path, os.O_RDONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
    except BaseException:
        os.close(fd)
        raise
    return fd


def get_session() -> Iterator[Session]:
    """FastAPI dependency."""
    with gate.use(), SessionLocal() as session:
        yield session
