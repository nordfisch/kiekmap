"""Shared test setup.

Every test gets a fresh, temporary data directory. That has to happen *before* ``app.db`` is
used, because the engine is created on import -- hence the detour through
``get_settings.cache_clear()`` and rebinding the session.
"""

import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _keep_the_local_env_out(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """No test may depend on what is configured on *this* machine.

    ``data_dir`` does the same for the tests that ask for it. This one is autouse, because since
    the language became a setting there are tests that read the configuration without wanting a
    data directory: ``format_label`` asks ``texts()``, and ``texts()`` asks the settings. On
    31 August 2026 a single line ``KIEKMAP_LANGUAGE=en`` in the developer's ``.env`` turned eight
    tests red -- the code was right, the test setup was not.

    German is the default, so the assertions that quote a German sentence stand on the default
    rather than on a machine.
    """
    from app.config import Settings, get_settings

    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.delenv("KIEKMAP_LANGUAGE", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def fixtures_dir() -> Path:
    """The test images. Built by ``tests/fixtures/build_test_images.py``."""
    return FIXTURES


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setenv("KIEKMAP_DATA_DIR", str(tmp_path / "data"))

    from app.config import Settings, get_settings

    # The developer's ``.env`` stays out. Otherwise the outcome of a test depends on what is
    # configured on *this* machine -- and an entry like KIEKMAP_IMPORT_CREDIT makes tests fail
    # that expect the defaults.
    monkeypatch.setitem(Settings.model_config, "env_file", None)

    get_settings.cache_clear()
    yield Path(os.environ["KIEKMAP_DATA_DIR"])
    get_settings.cache_clear()


@pytest.fixture
def settings(data_dir: Path):
    from app.config import get_settings

    configured = get_settings()
    configured.ensure_dirs()
    return configured


@pytest.fixture
def session(settings) -> Iterator[Session]:
    """A fresh database with every table.

    The tables are created straight from the models rather than through Alembic -- faster, and the
    migrations themselves run at container start anyway.
    """
    import app.db
    from app.db import Base
    from app.models import Photo  # noqa: F401 -- registers every table with Base

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


#: The PIN of the test device. Any four digits -- all that matters is that it is not the hash.
TEST_PIN = "4711"


@pytest.fixture(autouse=True)
def reset_process_state() -> Iterator[None]:
    """Everything the service keeps in memory rather than in the database.

    Sessions, the failed-attempt counter and the single backup job would otherwise outlive a test
    -- one that enters the PIN wrongly five times would take the whole run down with it, and a
    finished backup job would still be reported to the next test.
    """
    from app.services import auth, backup

    def clear() -> None:
        auth.sessions.clear()
        auth.attempts.reset()
        auth.tickets.clear()
        backup.job.reset()

    clear()
    yield
    clear()


@pytest.fixture
def admin_pin(settings, monkeypatch: pytest.MonkeyPatch) -> str:
    """Set up a PIN for the device -- with far fewer rounds than in operation.

    The real 200,000 rounds deliberately cost about a tenth of a second per sign-in. This test run
    signs in dozens of times. The number of rounds stands in the hash, so verification follows
    along on its own.
    """
    from app.services import auth

    monkeypatch.setattr(auth, "ROUNDS", 1_000)
    settings.admin_pin_hash = auth.hash_pin(TEST_PIN)
    return TEST_PIN


@pytest.fixture
def admin_client(client: TestClient, admin_pin: str) -> TestClient:
    """A signed-in client. The token stands in the header of every request afterwards."""
    response = client.post("/api/admin/login", json={"pin": admin_pin})
    assert response.status_code == 200, response.text
    client.headers["X-Admin-Token"] = response.json()["token"]
    return client


@pytest.fixture
def make_photo(session: Session):
    """A photo row without files -- for tests that are only about queries.

    The defaults are Holm and the year 1932; every field can be overridden. ``year=None`` and
    ``lat=None`` create exactly the gaps the contribution panel is about.
    """
    from app.models import Photo, PhotoStatus, Source
    from app.services.dates import date_range

    counter = 0

    def create(
        *,
        lat: float | None = 53.62,
        lon: float | None = 9.676,
        year: int | None = 1932,
        month: int | None = None,
        day: int | None = None,
        precision=None,
        title: str = "Test photo",
        place_name: str | None = None,
        accuracy: int | None = None,
        location_source: str | None = None,
        status: str = PhotoStatus.PUBLISHED,
        sha: str | None = None,
    ) -> Photo:
        nonlocal counter
        counter += 1

        start, end, resolved = date_range(year, month, day, precision)
        photo = Photo(
            sha256=sha or f"{counter:064d}",
            original_filename=f"{title}.jpg",
            mime="image/jpeg",
            bytes=1000,
            width=900,
            height=640,
            title=title,
            place_name=place_name,
            lat=lat,
            lon=lon,
            date_from=start,
            date_to=end,
            date_precision=resolved,
            location_accuracy_m=accuracy,
            date_source=Source.CURATOR if start else None,
            location_source=(location_source or (Source.CURATOR if lat is not None else None)),
            status=status,
        )
        session.add(photo)
        session.flush()
        return photo

    return create


@pytest.fixture
def sample_image(tmp_path: Path):
    """Copy a test image to a writable place and return the path.

    Copied, because the import may file images away and the originals have to stay in the
    repository.
    """
    work_dir = tmp_path / "source"
    work_dir.mkdir()

    def fetch(name: str, as_name: str | None = None) -> Path:
        target = work_dir / (as_name or name)
        shutil.copy2(FIXTURES / name, target)
        return target

    return fetch
