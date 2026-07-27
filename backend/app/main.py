"""Einstiegspunkt der Anwendung."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import health
from app.config import get_settings
from app.services.watcher import Eingangswaechter

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("photomap")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.ensure_dirs()
    log.info("Datenverzeichnis: %s", settings.data_dir)

    waechter = Eingangswaechter(settings)
    waechter.start()
    try:
        yield
    finally:
        waechter.stop()


app = FastAPI(
    title="Photomap",
    description="Bilddatenbank fuer historische Ortsfotos im Heimatmuseum",
    version=__version__,
    lifespan=lifespan,
    # Gleiches Praefix wie im nginx-Proxy, damit Entwicklung und Betrieb dieselben Pfade haben.
    root_path="",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

# Nur fuer den Vite-Dev-Server noetig. Auf dem Pi liefert nginx Frontend und API unter derselben
# Herkunft aus, dort greift diese Middleware nie.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
