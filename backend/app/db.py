"""Datenbankanbindung.

SQLite laeuft hier mit WAL-Journal. Das ist der Modus, in dem Lesen und Schreiben sich nicht
gegenseitig blockieren -- wichtig, weil der Import-Thread schreibt, waehrend der Kiosk liest --
und in dem ``VACUUM INTO`` im laufenden Betrieb eine konsistente Sicherungskopie erzeugt.
"""

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Basisklasse aller Tabellen. Die Modelle folgen in Stufe 3."""


@event.listens_for(Engine, "connect")
def _configure_sqlite(dbapi_connection, connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    # Kompromiss aus Geschwindigkeit und Sicherheit; mit WAL bleibt die Datenbank auch bei
    # Stromausfall konsistent, im schlimmsten Fall fehlt die letzte Transaktion.
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def create_db_engine() -> Engine:
    settings = get_settings()
    settings.ensure_dirs()
    return create_engine(
        settings.db_url,
        # Der watchdog-Import laeuft in einem eigenen Thread und braucht dieselbe Verbindung nicht.
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """FastAPI-Dependency."""
    with SessionLocal() as session:
        yield session
