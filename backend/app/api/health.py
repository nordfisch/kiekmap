"""Bereitschaftsanzeige.

Auf diesen Endpunkt wartet der Kiosk-Dienst auf dem Pi, bevor er Chromium startet. Er darf deshalb
nicht blind 200 liefern, sondern muss die Datenbank tatsaechlich anfassen -- sonst startet der
Browser auf ein Backend, das noch nicht antworten kann, und das Museum begruesst seine Besucher
morgens mit einer Fehlerseite.
"""

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app import __version__
from app.db import SessionLocal

router = APIRouter(tags=["system"])


@router.get("/health", summary="Ist das Backend bereit?")
def health(response: Response) -> dict[str, str]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 -- die Ursache gehoert in die Antwort
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "nicht bereit", "version": __version__, "detail": str(exc)}

    return {"status": "bereit", "version": __version__}
