"""Application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import admin, contribute, health, photos, places
from app.config import get_settings
from app.db import SessionLocal
from app.services.places import load_if_empty as load_places_if_empty
from app.services.watcher import IncomingWatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("photomap")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.ensure_dirs()
    log.info("Data directory: %s", settings.data_dir)

    with SessionLocal() as session:
        load_places_if_empty(session, settings.places_file)

    watcher = IncomingWatcher(settings)
    watcher.start()
    try:
        yield
    finally:
        watcher.stop()


app = FastAPI(
    title="Photomap",
    description="Photo database for historical village photographs in a local museum",
    version=__version__,
    lifespan=lifespan,
    # Same prefix as in the nginx proxy, so development and production share the same paths.
    root_path="",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

# Only needed for the Vite dev server. On the Pi, nginx serves frontend and API from the same
# origin, so this middleware never applies there.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(places.router, prefix="/api")
app.include_router(contribute.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
