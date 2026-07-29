"""Backup onto a USB stick, and restoring from one.

Both take minutes, so neither happens inside the request. A thread does the work and the screen
asks how far along it is -- that is what makes the progress bar in the admin area possible, and
what keeps a two-thousand-photo backup from running into a proxy timeout.

Every message in here is German: this is the admin area, and it is read by whoever is standing in
front of the device with a stick in their hand.
"""

import logging

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
    JobState,
)
from app.services import backup as service

log = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/backup", tags=["sicherung"])


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
    )


@router.post("/acknowledge", response_model=JobState, summary="Clear a finished job")
def acknowledge(admin: Admin) -> JobState:
    """Called once the screen has shown the result. A running job is not affected."""
    service.job.reset()
    return status(admin)
