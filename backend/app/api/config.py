"""What the frontend has to know before it renders anything.

One call, and it exists for a single reason: the language is an instance setting in the ``.env``,
and the interface has to know it before the first text appears. Reading it out of a Vite variable
instead would need one build per language -- against the principle that the device is switched
over on the Pi, without rebuilding.

The kiosk service waits for ``/health`` before it starts Chromium, so the backend is already up by
the time this is asked.
"""

from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.schemas import InstanceConfig

router = APIRouter(tags=["system"])


@router.get("/config", summary="Language and version of this instance")
def instance_config() -> InstanceConfig:
    return InstanceConfig(language=get_settings().language, version=__version__)
