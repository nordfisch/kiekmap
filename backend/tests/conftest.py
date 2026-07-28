"""Shared test setup.

Every test gets a fresh, temporary data directory. That has to happen *before* ``app.db`` is used,
because the engine is created at import time -- hence the ``get_settings.cache_clear()`` dance and
the rebinding of the session.
"""

import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """The test images. Produced by ``tests/fixtures/erzeuge_testbilder.py``."""
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

    configured = get_settings()
    configured.ensure_dirs()
    return configured


@pytest.fixture
def session(settings) -> Iterator[Session]:
    """Fresh database with all tables.

    Tables are created straight from the models rather than through Alembic -- faster, and the
    migrations themselves run at container start anyway.
    """
    import app.db
    from app.db import Base
    from app.models import Photo  # noqa: F401 -- registers every table on Base

    app.db.engine = app.db.create_db_engine()
    app.db.SessionLocal.configure(bind=app.db.engine)
    Base.metadata.create_all(app.db.engine)

    with app.db.SessionLocal() as db_session:
        yield db_session


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    from app.main import app as fastapi_app

    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture
def make_photo(session: Session):
    """Create a photo row without files -- for tests that only care about queries.

    Defaults to Holm and the year 1932; every field is overridable. ``year=None`` and ``lat=None``
    produce the gaps the "Hilf mit" panel is about.
    """
    from app.models import Photo, PhotoStatus, Source
    from app.services.dates import date_range

    counter = 0

    def create(
        *,
        lat: float | None = 53.62,
        lon: float | None = 9.676,
        year: int | None = 1932,
        precision=None,
        title: str = "Testfoto",
        status: str = PhotoStatus.PUBLISHED,
        sha: str | None = None,
    ) -> Photo:
        nonlocal counter
        counter += 1

        start, end, resolved = date_range(year, precision=precision)
        photo = Photo(
            sha256=sha or f"{counter:064d}",
            original_filename=f"{title}.jpg",
            mime="image/jpeg",
            bytes=1000,
            width=900,
            height=640,
            title=title,
            lat=lat,
            lon=lon,
            date_from=start,
            date_to=end,
            date_precision=resolved,
            date_source=Source.CURATOR if start else None,
            location_source=Source.CURATOR if lat is not None else None,
            status=status,
        )
        session.add(photo)
        session.flush()
        return photo

    return create


@pytest.fixture
def sample_image(tmp_path: Path):
    """Copy a test image somewhere writable and return the path.

    Copied because the import may move files aside, and the templates in the repo must stay put.
    """
    work_dir = tmp_path / "source"
    work_dir.mkdir()

    def fetch(name: str, as_name: str | None = None) -> Path:
        target = work_dir / (as_name or name)
        shutil.copy2(FIXTURES / name, target)
        return target

    return fetch
