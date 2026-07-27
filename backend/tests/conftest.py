"""Gemeinsame Test-Vorbereitung.

Jeder Testlauf bekommt ein frisches, temporaeres Datenverzeichnis. Das muss geschehen, *bevor*
``app.db`` importiert wird, denn dort entsteht die Engine beim Import -- daher der
``get_settings.cache_clear()``-Tanz und der Import erst innerhalb der Fixture.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setenv("PHOTOMAP_DATA_DIR", str(tmp_path / "data"))

    from app.config import get_settings

    get_settings.cache_clear()
    yield Path(os.environ["PHOTOMAP_DATA_DIR"])
    get_settings.cache_clear()


@pytest.fixture
def client(data_dir: Path) -> Iterator[TestClient]:
    import app.db

    app.db.engine = app.db.create_db_engine()
    app.db.SessionLocal.configure(bind=app.db.engine)

    from app.main import app as fastapi_app

    with TestClient(fastapi_app) as test_client:
        yield test_client
