"""Readiness probe.

The kiosk service on the Pi waits for this endpoint before starting Chromium. It must therefore
not blindly return 200 but actually touch the database -- otherwise the browser starts against a
backend that cannot answer yet, and the museum greets its visitors with an error page.

``status`` is English in both languages. It is a machine value that the kiosk service reads, not
prose that reaches anybody's screen.
"""

import logging

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app import __version__
from app.db import SessionLocal

router = APIRouter(tags=["system"])

log = logging.getLogger(__name__)


@router.get("/health", summary="Is the backend ready?")
def health(response: Response) -> dict[str, str]:
    """Whether the database answers. The only endpoint that needs no PIN.

    **The cause goes to the log, not into the response.** It used to travel back as ``detail``,
    on the thought that whoever debugs the Pi wants to read it. Two things are wrong with that:
    this endpoint is the one thing on the device that answers without authentication, and a
    SQLAlchemy error names the driver, the file and often the statement. The log is also the
    better place for the operator -- ``docker compose logs backend`` still holds it tomorrow,
    a curl response does not. Found by CodeQL, ``py/stack-trace-exposure``.
    """
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 -- any failure means not ready, and the log gets the cause
        log.exception("The readiness probe could not reach the database")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready", "version": __version__}

    return {"status": "ready", "version": __version__}
