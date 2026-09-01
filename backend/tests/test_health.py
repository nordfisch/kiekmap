from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app import __version__


def test_health_reports_ready(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "version": __version__}


def test_a_broken_database_does_not_report_why(client: TestClient) -> None:
    """This is the one endpoint that answers without a PIN, so it says nothing about the inside.

    The cause used to travel back as ``detail``. A SQLAlchemy message names the driver, the file
    and often the statement -- it belongs in the log, where the operator still finds it tomorrow.
    """
    broken = OperationalError("SELECT 1", {}, Exception("unable to open /data/kiekmap.db"))

    with patch("app.api.health.SessionLocal", side_effect=broken):
        response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "not ready", "version": __version__}
    assert "kiekmap.db" not in response.text


def test_starting_creates_the_data_directories(client: TestClient, data_dir: Path) -> None:
    """A fresh clone or an empty USB volume has to start without anyone lending a hand."""
    client.get("/api/health")

    for name in ("photos", "thumbs", "incoming"):
        assert (data_dir / name).is_dir(), f"{name}/ was not created"


def test_openapi_is_reachable(client: TestClient) -> None:
    """In the early stages the docs under /api/docs were the admin interface."""
    assert client.get("/api/openapi.json").status_code == 200
