from pathlib import Path

from fastapi.testclient import TestClient

from app import __version__


def test_health_reports_ready(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "bereit", "version": __version__}


def test_starting_creates_the_data_directories(client: TestClient, data_dir: Path) -> None:
    """A fresh clone or an empty USB volume has to start without anyone lending a hand."""
    client.get("/api/health")

    for name in ("photos", "thumbs", "incoming"):
        assert (data_dir / name).is_dir(), f"{name}/ was not created"


def test_openapi_is_reachable(client: TestClient) -> None:
    """In the early stages the docs under /api/docs were the admin interface."""
    assert client.get("/api/openapi.json").status_code == 200
