"""Database wiring.

SQLite runs with a WAL journal here. That is the mode in which reads and writes do not block each
other -- important because the import thread writes while the kiosk reads -- and in which
``VACUUM INTO`` produces a consistent backup copy while the service is running.
"""

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


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


def get_session() -> Iterator[Session]:
    """FastAPI dependency."""
    with SessionLocal() as session:
        yield session
