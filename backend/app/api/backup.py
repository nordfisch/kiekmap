"""Backup onto a USB stick, and restoring from one.

Both take minutes, so neither happens inside the request. A thread does the work and the screen
asks how far along it is -- that is what makes the progress bar in the admin area possible, and
what keeps a two-thousand-photo backup from running into a proxy timeout.

Every message in here is German: this is the admin area, and it is read by whoever is standing in
front of the device with a stick in their hand.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.admin import Admin, Config
from app.config import Settings
from app.db import SessionLocal
from app.schemas import (
    BackupOnDrive,
    BackupReminder,
    DriveChoice,
    DriveItem,
    DriveList,
    ImportFolderItem,
    ImportFolders,
    ImportRequest,
    JobState,
    PhotoDetail,
    UploadItem,
)
from app.services import backup as service
from app.services import importer

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/backup", tags=["sicherung"])

# Der Stick-Import wohnt hier, obwohl er kein Backup ist: Er teilt sich das Erkennen der
# Datentraeger und den einen Auftrag mit der Sicherung. Beides zweimal zu haben waere schlimmer
# als ein Modul, das zwei Dinge kann.
import_router = APIRouter(prefix="/admin/import", tags=["import"])


def _reminder(settings: Settings) -> BackupReminder:
    state = service.read_state(settings)
    return BackupReminder(
        last_backup_at=state.last_backup_at,
        last_drive=state.last_drive,
        days_since=state.days_since,
        overdue=state.overdue,
    )


@router.get("/drives", response_model=DriveList, summary="Removable drives and what is on them")
def drives(admin: Admin, settings: Config) -> DriveList:
    """Polled by the admin area, so that plugging a stick in is enough -- no reload, no button."""
    photos, needed = service.collection_size(settings)

    return DriveList(
        drives=[
            DriveItem(
                path=str(drive.path),
                name=drive.name,
                total_bytes=drive.total_bytes,
                free_bytes=drive.free_bytes,
                enough_space=drive.free_bytes >= needed,
                backup=(
                    BackupOnDrive(
                        created_at=drive.backup.created_at,
                        photos=drive.backup.photos,
                        bytes=drive.backup.bytes,
                        place=drive.backup.place,
                    )
                    if drive.backup
                    else None
                ),
            )
            for drive in service.find_drives(settings.media_dir)
        ],
        photos=photos,
        needed_bytes=needed,
        reminder=_reminder(settings),
    )


def _pick(settings: Settings, path: str) -> service.Drive:
    """Only a drive that was actually found counts -- the path comes from the browser."""
    drive = service.find_drive(settings.media_dir, path)
    if drive is None:
        raise HTTPException(404, "Dieser Stick ist nicht mehr da. Bitte neu einstecken.")
    return drive


@router.post("/start", response_model=JobState, summary="Start a backup")
def start(choice: DriveChoice, admin: Admin, settings: Config) -> JobState:
    drive = _pick(settings, choice.path)

    def work(report: service.Report) -> str:
        # Its own session: this runs in a thread, and the request's session belongs to the request.
        with SessionLocal() as session:
            return service.run_backup(session, settings, drive, report)

    if not service.job.start("backup", work):
        raise HTTPException(409, "Es ist schon etwas im Gange. Bitte warten, bis es fertig ist.")

    log.info("Backup to %s started", drive.path)
    return status(admin)


@router.post("/restore", response_model=JobState, summary="Restore from a backup")
def restore(choice: DriveChoice, admin: Admin, settings: Config) -> JobState:
    """Replaces the collection on the device with the one from the stick.

    The previous state is set aside, not deleted -- see app/services/backup.py.
    """
    drive = _pick(settings, choice.path)

    def work(report: service.Report) -> str:
        message = service.run_restore(settings, drive, report)
        _reopen_database()
        return message

    if not service.job.start("restore", work):
        raise HTTPException(409, "Es ist schon etwas im Gange. Bitte warten, bis es fertig ist.")

    log.info("Restore from %s started", drive.path)
    return status(admin)


def _reopen_database() -> None:
    """Point the engine at the file that is now there.

    The database was swapped underneath the running service. Every pooled connection still holds
    the old, already moved file open -- reads would keep working and writes would land in a file
    nobody can see any more. Disposing and rebuilding is the same dance the test fixtures do.
    """
    import app.db

    app.db.engine.dispose()
    app.db.engine = app.db.create_db_engine()
    app.db.SessionLocal.configure(bind=app.db.engine)
    log.info("Database reopened after restore")


@import_router.get("/folders", response_model=ImportFolders, summary="Image folders on a stick")
def import_folders(admin: Admin, settings: Config) -> ImportFolders:
    """What could be taken in from the drives currently plugged in.

    Polled like the drive list, so plugging a stick in is enough. The drive names travel along:
    "no stick" and "a stick without images" need different words on screen.
    """
    drives = service.find_drives(settings.media_dir)
    folders = []
    for drive in drives:
        for folder in importer.find_image_folders(drive.path):
            folders.append(
                ImportFolderItem(
                    path=str(folder.path),
                    name=folder.name,
                    drive=drive.name,
                    images=folder.images,
                )
            )
    return ImportFolders(drives=[drive.name for drive in drives], folders=folders)


@import_router.post("/start", response_model=JobState, summary="Take in a folder from a stick")
def import_from_stick(request: ImportRequest, admin: Admin, settings: Config) -> JobState:
    """Read a folder off a stick, with place and year optionally applying to all of it.

    **Nothing on the stick is touched.** Unlike the watched inbox, where imported files are moved
    aside, a stranger's drive is only ever read from -- see app/services/importer.py.
    """
    folder = _pick_folder(settings, request.path)

    def work(report: service.Report) -> service.JobResult:
        with SessionLocal() as session:
            message, outcomes = importer.import_from_folder(
                session,
                folder,
                settings,
                defaults=lambda photo: importer.apply_batch_defaults(
                    photo,
                    request.year,
                    request.precision,
                    request.lat,
                    request.lon,
                    request.place_name,
                    credit=request.credit,
                    provenance=request.provenance,
                ),
                report=report,
            )
            return message, _review_rows(outcomes)

    if not service.job.start("import", work):
        raise HTTPException(409, "Es ist schon etwas im Gange. Bitte warten, bis es fertig ist.")

    log.info("Stick import from %s started", folder)
    return status(admin)


#: Bis hierher lohnt sich die Nacharbeits-Tabelle, darueber nicht mehr.
#:
#: Wer vierzig ausgesuchte Bilder hochlaedt, will sie gleich beschriften. Wer einen Ordner mit
#: zweihundert einliest, will keine Tabelle mit zweihundert Zeilen -- fuer den ist die
#: "Ohne Ort"-Liste die Arbeitsflaeche. Die Zahl steht auch im Frontend; beide Seiten nennen die
#: jeweils andere im Kommentar.
REVIEW_LIMIT = 30


def _review_rows(outcomes: list[importer.ImportOutcome]) -> list[dict] | None:
    """Die Zeilen fuer die Nacharbeit -- oder None, wenn es zu viele waeren.

    Sie reisen im Auftragsstatus mit, der im Sekundentakt abgefragt wird. Zweihundert Fotos darin
    waeren eine Nutzlast, die bei jeder Abfrage neu ueber die Leitung ginge.
    """
    if len(outcomes) > REVIEW_LIMIT:
        return None

    return [
        UploadItem(
            filename=outcome.source.name if outcome.source else "",
            result=outcome.result,
            message=outcome.message,
            photo=PhotoDetail.from_photo(outcome.photo) if outcome.photo else None,
        ).model_dump(mode="json")
        for outcome in outcomes
    ]


def _pick_folder(settings: Settings, path: str) -> Path:
    """Only a folder that really sits on a plugged-in drive.

    The path comes back from the browser, so it is input, not a fact. Without this check the
    admin area would be a way to read any folder on the device into the collection -- and a
    resolved path is compared, so ``..`` gets nobody out of the drive either.
    """
    wanted = Path(path).resolve()
    for drive in service.find_drives(settings.media_dir):
        root = drive.path.resolve()
        if wanted == root or root in wanted.parents:
            if wanted.is_dir():
                return wanted
            break
    raise HTTPException(404, "Diesen Ordner gibt es auf dem Stick nicht mehr.")


@router.get("/status", response_model=JobState, summary="How far along backup or restore is")
def status(admin: Admin) -> JobState:
    current = service.job.status()
    return JobState(
        kind=current.kind,
        phase=current.phase,
        done=current.done,
        total=current.total,
        message=current.message,
        error=current.error,
        items=current.items,
    )


@router.post("/acknowledge", response_model=JobState, summary="Clear a finished job")
def acknowledge(admin: Admin) -> JobState:
    """Called once the screen has shown the result. A running job is not affected."""
    service.job.reset()
    return status(admin)
