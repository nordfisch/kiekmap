"""Application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import ExitStack, asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import __version__
from app.api import admin, backup, config, contribute, health, photos, places
from app.api.body_limit import BodyLimit
from app.config import get_settings
from app.db import BackendAlreadyRunning, DatabaseClosed, SessionLocal, process_lock
from app.services.places import load_if_empty as load_places_if_empty
from app.services.watcher import IncomingWatcher
from app.text import texts

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("kiekmap")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.ensure_dirs()
    log.info("Data directory: %s", settings.data_dir)

    with ExitStack() as held:
        # Before anything writes: a second process must stop before it reads in places or starts
        # a watcher of its own. See ``app.db.process_lock``.
        try:
            held.enter_context(process_lock(settings))
        except BackendAlreadyRunning as refusal:
            # Logged on its own line, so that the reason stands above the traceback.
            log.error("%s", refusal)
            raise

        with SessionLocal() as session:
            load_places_if_empty(session, settings.places_file)

        watcher = IncomingWatcher(settings)
        watcher.start()
        try:
            yield
        finally:
            watcher.stop()


app = FastAPI(
    title="Kiekmap",
    description="Photo database for historical village photographs in a local museum",
    version=__version__,
    lifespan=lifespan,
    # Same prefix as in the nginx proxy, so development and production share the same paths.
    root_path="",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

app.add_middleware(BodyLimit)


@app.exception_handler(DatabaseClosed)
async def database_closed(request: Request, error: DatabaseClosed) -> JSONResponse:
    """A restore is swapping the database file -- for seconds, see ``app.db.DatabaseGate``.

    503 rather than a 500: nothing is broken, and the same request succeeds a moment later. The
    body has the shape of an ``HTTPException``, so the screens show it like any other refusal.
    """
    return JSONResponse(
        status_code=503,
        content={"detail": texts().backup.restore_swapping},
        headers={"Retry-After": "10"},
    )


app.include_router(health.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(places.router, prefix="/api")
app.include_router(contribute.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(backup.router, prefix="/api")
app.include_router(backup.import_router, prefix="/api")
