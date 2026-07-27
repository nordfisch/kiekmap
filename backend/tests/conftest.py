"""Gemeinsame Test-Vorbereitung.

Jeder Test bekommt ein frisches, temporaeres Datenverzeichnis. Das muss geschehen, *bevor*
``app.db`` benutzt wird, denn dort entsteht die Engine beim Import -- daher der
``get_settings.cache_clear()``-Tanz und das Neubinden der Session.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Die Testbilder. Erzeugt von ``tests/fixtures/erzeuge_testbilder.py``."""
    return FIXTURES


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setenv("PHOTOMAP_DATA_DIR", str(tmp_path / "data"))

    from app.config import get_settings

    get_settings.cache_clear()
    yield Path(os.environ["PHOTOMAP_DATA_DIR"])
    get_settings.cache_clear()


@pytest.fixture
def settings(data_dir: Path):
    from app.config import get_settings

    einstellungen = get_settings()
    einstellungen.ensure_dirs()
    return einstellungen


@pytest.fixture
def session(settings) -> Iterator[Session]:
    """Frische Datenbank mit allen Tabellen.

    Die Tabellen werden direkt aus den Modellen erzeugt statt ueber Alembic -- schneller, und die
    Migrationen selbst werden ohnehin beim Containerstart gefahren.
    """
    import app.db
    from app.db import Base
    from app.models import Photo  # noqa: F401 -- registriert alle Tabellen an Base

    app.db.engine = app.db.create_db_engine()
    app.db.SessionLocal.configure(bind=app.db.engine)
    Base.metadata.create_all(app.db.engine)

    with app.db.SessionLocal() as sitzung:
        yield sitzung


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    from app.main import app as fastapi_app

    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture
def bild(tmp_path: Path):
    """Legt ein Testbild an einen beschreibbaren Ort und gibt den Pfad zurueck.

    Kopiert, weil der Import Dateien beiseiteraeumen kann und die Vorlagen im Repo bleiben sollen.
    """
    import shutil

    arbeitsordner = tmp_path / "quelle"
    arbeitsordner.mkdir()

    def hole(name: str, als: str | None = None) -> Path:
        ziel = arbeitsordner / (als or name)
        shutil.copy2(FIXTURES / name, ziel)
        return ziel

    return hole
