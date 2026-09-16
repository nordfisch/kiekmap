"""Database wiring.

SQLite runs with a WAL journal here. That is the mode in which reads and writes do not block each
other -- important because the import thread writes while the kiosk reads -- and in which
``VACUUM INTO`` produces a consistent backup copy while the service is running.

**Importing this module creates nothing.** ``Database`` is built at startup -- by the ``lifespan``
of ``app.main``, by ``app.cli``, or by a test fixture -- and ``current_database`` hands it out. An
engine at module level would read the settings and create the data directories on every import of
``app.db``, models and services included, and a test could only get one of its own by rebinding a
module attribute after the fact.
"""

import fcntl
import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import Settings

#: How long a restore waits for the sessions in use to finish before it gives up.
#:
#: Long enough for the watcher to finish the file it is importing, a large TIFF on a Pi included.
#: A ZIP download holds its session for minutes, so the gate does not wait for one at all; see
#: ``DatabaseGate.use``.
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


def _create_engine(settings: Settings) -> Engine:
    settings.ensure_dirs()
    return create_engine(
        settings.db_url,
        # The inbox watcher runs in its own thread and does not need the same connection.
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


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
        self._lasting = 0
        self._closed = False

    @contextmanager
    def use(self, *, lasting: bool = False) -> Iterator[None]:
        """Hold a session through the gate.

        ``lasting`` marks a session held for minutes: the ZIP download. A swap does not wait for
        one. The gate closes the moment it starts waiting, and every visitor request gets 503 until
        the wait ends. Waiting out a download would keep the kiosk at 503 for the whole timeout,
        only to refuse at its end.
        """
        with self._condition:
            if self._closed:
                raise DatabaseClosed
            self._in_use += 1
            self._lasting += lasting
        try:
            yield
        finally:
            with self._condition:
                self._in_use -= 1
                self._lasting -= lasting
                self._condition.notify_all()

    @property
    def lasting_in_use(self) -> int:
        """How many lasting sessions are in use. A restore reads it before it starts copying."""
        with self._condition:
            return self._lasting

    @contextmanager
    def closed(self, timeout_s: float) -> Iterator[None]:
        """Refuse new sessions, wait until none is in use, and open again afterwards.

        Refuses at once, without closing, while a lasting session is in use.
        """
        with self._condition:
            if self._lasting:
                raise DatabaseInUse
            self._closed = True
            if not self._condition.wait_for(lambda: self._in_use == 0, timeout_s):
                self._closed = False
                raise DatabaseInUse
        try:
            yield
        finally:
            with self._condition:
                self._closed = False


class Database:
    """The engine of one process, the sessions on it, and the gate in front of them.

    Built at startup from the settings it is handed, so that nothing about it depends on the
    moment a module was imported. Whoever needs it during a request, a job or a CLI command asks
    ``current_database``.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.gate = DatabaseGate()
        self.engine = _create_engine(settings)
        self._sessions = sessionmaker(autoflush=False, expire_on_commit=False, bind=self.engine)

    def session(self) -> Session:
        """A session on the current engine, without the gate.

        Whoever opens one while the service runs takes ``gate.use()`` around it, as ``get_session``
        does for a request. The two exceptions are named in ``DatabaseGate``.
        """
        return self._sessions()

    def reopen(self) -> None:
        """Connect to whatever lies at the configured path now.

        The restore moves a different file there, and ``closed_for_swap`` has disposed the old
        engine by then. The sessionmaker keeps its settings and only changes what it binds to.
        """
        self.engine = _create_engine(self.settings)
        self._sessions.configure(bind=self.engine)

    @contextmanager
    def closed_for_swap(self, timeout_s: float | None = None) -> Iterator[None]:
        """Close every connection, let the caller swap the file, and reopen on what is there then.

        ``dispose()`` closes only the connections that are back in the pool. That is why the gate
        comes first: once no session is in use, every connection is back, and none stays open on
        the old file when it is renamed.

        Raises ``DatabaseInUse`` before anything is closed, so a refusal leaves the service as it
        was.
        """
        with self.gate.closed(CLOSE_TIMEOUT_S if timeout_s is None else timeout_s):
            self.engine.dispose()
            try:
                yield
            finally:
                self.reopen()


#: The database of this process. ``open_database`` fills it, ``current_database`` reads it.
_database: Database | None = None


def open_database(settings: Settings) -> Database:
    """The database of this process, created on the first call and handed out on every later one.

    **One per process, and the second caller gets the first one.** ``DatabaseGate`` counts the
    sessions of the engine it belongs to; a second engine on the same file would open connections
    outside that count, and a restore would swap the file under them. The backend is a single
    process for the same kind of reason; see ``process_lock``.

    A test fixture opens the database before it starts the app, so that the test and the service
    share one engine and one gate. ``close_database`` gives the next test a clean process.
    """
    global _database

    if _database is None:
        _database = Database(settings)
    return _database


def close_database() -> None:
    """Close the database of this process, so that the next ``open_database`` builds a new one."""
    global _database

    if _database is not None:
        _database.engine.dispose()
        _database = None


def current_database() -> Database:
    """The database of this process. Raises if startup has not opened one."""
    if _database is None:
        raise RuntimeError(
            "No database is open in this process. app.main opens it in its lifespan, app.cli at "
            "the start of a command, and the tests in the database fixture."
        )
    return _database


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
    database = current_database()
    with database.gate.use(), database.session() as session:
        yield session
