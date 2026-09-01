"""The one call the interface makes before it renders anything.

The language is an instance setting in the ``.env``. The frontend cannot read a ``.env``, and a
Vite variable would mean one build per language -- against the principle that the device is
switched over on the Pi without rebuilding. So the backend hands it out.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import __version__


def test_the_config_names_the_language_and_the_version(client: TestClient) -> None:
    response = client.get("/api/config")

    assert response.status_code == 200
    assert response.json() == {"language": "de", "version": __version__}


def test_the_setting_reaches_the_endpoint(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Otherwise the endpoint would answer with a constant and nobody would notice."""
    from app.config import get_settings

    monkeypatch.setenv("KIEKMAP_LANGUAGE", "en")
    get_settings.cache_clear()

    assert client.get("/api/config").json()["language"] == "en"


def test_an_unknown_language_stops_the_start(monkeypatch: pytest.MonkeyPatch) -> None:
    """The case this setting is typed for.

    A device that speaks the wrong language is noticed within a minute. One that silently ignores
    a misspelled setting and falls back to German is not -- the museum would report that the
    switch does nothing, and the ``.env`` would look right.
    """
    from app.config import Settings

    monkeypatch.setenv("KIEKMAP_LANGUAGE", "fr")
    monkeypatch.setitem(Settings.model_config, "env_file", None)

    with pytest.raises(ValidationError):
        Settings()
