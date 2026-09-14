"""Database wiring.

SQLite runs with a WAL journal here. That is the mode in which reads and writes do not block each
other -- important because the import thread writes while the kiosk reads -- and in which
``VACUUM INTO`` produces a consistent backup copy while the service is running.
"""

import threading
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

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

    **A restore renames the database file**, and SQLite does not survive that under an open
    connection. A pooled connection keeps writing into the renamed file, so a visitor's
    contribution during the swap lands in the set-aside state and is gone. When that connection is
    finally closed, SQLite deletes its journal by name -- and by then that name belongs to the
    restored database. SQLite's own list of ways to corrupt a database names this case.

    The gate closes only for the swap itself, which takes seconds; the copying before it runs with
    the database open. Whoever asks for a session meanwhile gets ``DatabaseClosed``.

    Every session the running service opens goes through here: requests, the readiness probe, the
    inbox watcher and the ZIP download. **Two exceptions, both deliberate.** The job's own sessions
    -- backup and stick import -- need no gate, because only one job runs at a time and a restore
    is that job. And the CLI runs in a process of its own, which no lock in this one can reach.
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
    old file. SQLite checkpoints and removes its journal while the file still has its own name.

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


def get_session() -> Iterator[Session]:
    """FastAPI dependency."""
    with gate.use(), SessionLocal() as session:
        yield session
