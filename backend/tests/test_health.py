# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from fastapi.testclient import TestClient

from app import __version__


def test_health_meldet_bereit(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "bereit", "version": __version__}


def test_start_legt_datenverzeichnisse_an(client: TestClient, data_dir: Path) -> None:
    """Ein frischer Clone oder ein leerer USB-Datentraeger soll ohne Handgriffe starten."""
    client.get("/api/health")

    for name in ("photos", "thumbs", "incoming"):
        assert (data_dir / name).is_dir(), f"{name}/ wurde nicht angelegt"


def test_openapi_erreichbar(client: TestClient) -> None:
    """Die Doku unter /api/docs ist in fruehen Stufen das Admin-Interface."""
    assert client.get("/api/openapi.json").status_code == 200
