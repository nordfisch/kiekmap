"""Gemeinsame Testeinrichtung.

Jeder Test bekommt ein frisches, temporaeres Datenverzeichnis. Das muss geschehen, *bevor*
``app.db`` benutzt wird, denn die Engine entsteht beim Import -- daher der Tanz um
``get_settings.cache_clear()`` und das Neubinden der Sitzung.
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
    """Die Testbilder. Erzeugt von ``tests/fixtures/build_test_images.py``."""
    return FIXTURES


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setenv("PHOTOMAP_DATA_DIR", str(tmp_path / "data"))

    from app.config import Settings, get_settings

    # Die ``.env`` des Entwicklers bleibt draussen. Sonst haengt das Ergebnis eines Tests davon
    # ab, was auf *diesem* Rechner eingestellt ist -- und ein Eintrag wie PHOTOMAP_IMPORT_CREDIT
    # laesst Tests fehlschlagen, die mit den Voreinstellungen rechnen.
    monkeypatch.setitem(Settings.model_config, "env_file", None)

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
    """Frische Datenbank mit allen Tabellen.

    Die Tabellen entstehen direkt aus den Modellen statt ueber Alembic -- schneller, und die
    Migrationen selbst laufen ohnehin beim Containerstart.
    """
    import app.db
    from app.db import Base
    from app.models import Photo  # noqa: F401 -- meldet jede Tabelle an Base an

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


#: Die PIN des Testgeraets. Vier beliebige Ziffern -- wichtig ist nur, dass sie nicht der Hash ist.
TEST_PIN = "4711"


@pytest.fixture(autouse=True)
def reset_process_state() -> Iterator[None]:
    """Alles, was der Dienst im Speicher haelt statt in der Datenbank.

    Anmeldungen, der Fehlversuchszaehler und der eine Sicherungsauftrag ueberleben sonst einen
    Test -- einer, der die PIN fuenfmal falsch eingibt, risse die ganze Testreihe mit, und ein
    fertiger Sicherungsauftrag wuerde dem naechsten Test noch gemeldet.
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
    """Eine PIN fuer das Geraet einrichten -- mit weit weniger Runden als im Betrieb.

    Die echten 200 000 Runden kosten mit Absicht rund eine Zehntelsekunde je Anmeldung. Diese
    Testreihe meldet sich dutzendfach an. Die Rundenzahl steht im Hash, die Pruefung zieht also
    von selbst mit.
    """
    from app.services import auth

    monkeypatch.setattr(auth, "ROUNDS", 1_000)
    settings.admin_pin_hash = auth.hash_pin(TEST_PIN)
    return TEST_PIN


@pytest.fixture
def admin_client(client: TestClient, admin_pin: str) -> TestClient:
    """Ein angemeldeter Client. Der Token steht danach im Kopf jeder Anfrage."""
    response = client.post("/api/admin/login", json={"pin": admin_pin})
    assert response.status_code == 200, response.text
    client.headers["X-Admin-Token"] = response.json()["token"]
    return client


@pytest.fixture
def make_photo(session: Session):
    """Eine Fotozeile ohne Dateien -- fuer Tests, denen es nur um Abfragen geht.

    Voreingestellt sind Holm und das Jahr 1932; jedes Feld laesst sich ueberschreiben.
    ``year=None`` und ``lat=None`` erzeugen genau die Luecken, um die es im "Hilf mit"-Bereich
    geht.
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
        title: str = "Testfoto",
        place_name: str | None = None,
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
    """Ein Testbild an eine beschreibbare Stelle kopieren und den Pfad zurueckgeben.

    Kopiert, weil der Import Dateien beiseiteraeumen kann und die Vorlagen im Repo liegen
    bleiben muessen.
    """
    work_dir = tmp_path / "source"
    work_dir.mkdir()

    def fetch(name: str, as_name: str | None = None) -> Path:
        target = work_dir / (as_name or name)
        shutil.copy2(FIXTURES / name, target)
        return target

    return fetch
