# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Readiness probe.

The kiosk service on the Pi waits for this endpoint before starting Chromium. It must therefore
not blindly return 200 but actually touch the database -- otherwise the browser starts against a
backend that cannot answer yet, and the museum greets its visitors with an error page.
"""

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app import __version__
from app.db import SessionLocal

router = APIRouter(tags=["system"])


@router.get("/health", summary="Is the backend ready?")
def health(response: Response) -> dict[str, str]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception as error:  # noqa: BLE001 -- the cause belongs in the response
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "nicht bereit", "version": __version__, "detail": str(error)}

    return {"status": "bereit", "version": __version__}
