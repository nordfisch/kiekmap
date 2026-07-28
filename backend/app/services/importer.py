"""Take photos into the database.

Per file: hash it, check for duplicates, read the image, extract metadata, store the original,
create thumbnails, write the row. Every outcome -- imported, duplicate, rejected -- lands in the
import log. Without it, a silently skipped photo would be indistinguishable from one that was
never copied in.

Files from the watched folder are moved aside afterwards, never deleted:

    data/incoming/            still to do
    data/incoming/_erledigt/  imported
    data/incoming/_problem/   unreadable or unsupported format
"""

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import DatePrecision, ImportLog, ImportResult, Photo, Source, Tag
from app.services import exif as exif_service
from app.services import thumbnails
from app.services.dates import date_range
from app.services.storage import ALLOWED_FORMATS, original_path, sha256_of_file

log = logging.getLogger(__name__)

# German directory names: the museum team sees these in the file manager.
DONE_DIR = "_erledigt"
PROBLEM_DIR = "_problem"
#: Subfolders of the inbox that are not scanned themselves.
SPECIAL_DIRS = {DONE_DIR, PROBLEM_DIR}


@dataclass
class ImportOutcome:
    result: ImportResult
    #: German -- this text reaches the curator through the import log.
    message: str
    photo: Photo | None = None
    path: Path | None = None

    @property
    def succeeded(self) -> bool:
        return self.result == ImportResult.IMPORTED


def _log_outcome(
    session: Session,
    path: Path,
    outcome: ImportOutcome,
    sha256: str | None = None,
) -> None:
    session.add(
        ImportLog(
            path=str(path),
            sha256=sha256,
            result=outcome.result,
            message=outcome.message,
            photo_id=outcome.photo.id if outcome.photo else None,
        )
    )


def _free_name(folder: Path, name: str) -> Path:
    """Make sure nothing is overwritten when moving files aside."""
    target = folder / name
    if not target.exists():
        return target
    stem, suffix = Path(name).stem, Path(name).suffix
    for counter in range(2, 1000):
        target = folder / f"{stem} ({counter}){suffix}"
        if not target.exists():
            return target
    raise RuntimeError(f"no free name for {name} in {folder}")


def _move_aside(path: Path, inbox: Path, subfolder: str) -> None:
    target_folder = inbox / subfolder
    target_folder.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), _free_name(target_folder, path.name))


def import_file(
    session: Session,
    path: Path,
    settings: Settings,
    *,
    move_aside: bool = False,
) -> ImportOutcome:
    """Take in a single file.

    ``move_aside`` applies to the watched folder. When importing from an arbitrary directory the
    user's files are left untouched.
    """
    inbox = settings.incoming_dir

    # 1. Hash first: it decides duplicate-or-not and is the later file name.
    try:
        sha256 = sha256_of_file(path)
    except OSError as error:
        outcome = ImportOutcome(ImportResult.REJECTED, f"Datei nicht lesbar: {error}")
        _log_outcome(session, path, outcome)
        return outcome

    existing = session.scalar(select(Photo).where(Photo.sha256 == sha256))
    if existing:
        outcome = ImportOutcome(
            ImportResult.DUPLICATE,
            f"Inhaltsgleich mit Foto {existing.id} ({existing.original_filename})",
            photo=existing,
        )
        _log_outcome(session, path, outcome, sha256)
        if move_aside:
            _move_aside(path, inbox, DONE_DIR)
        return outcome

    # 2. Read the image.
    try:
        info = exif_service.read_image_info(path)
    except (UnidentifiedImageError, OSError, ValueError) as error:
        outcome = ImportOutcome(ImportResult.REJECTED, f"Kein lesbares Bild: {error}")
        _log_outcome(session, path, outcome, sha256)
        if move_aside:
            _move_aside(path, inbox, PROBLEM_DIR)
        return outcome

    if info.format not in ALLOWED_FORMATS:
        outcome = ImportOutcome(
            ImportResult.REJECTED,
            f"Format {info.format or 'unbekannt'} wird nicht unterstuetzt "
            f"(erlaubt: {', '.join(sorted(ALLOWED_FORMATS))})",
        )
        _log_outcome(session, path, outcome, sha256)
        if move_aside:
            _move_aside(path, inbox, PROBLEM_DIR)
        return outcome

    mime, suffix = ALLOWED_FORMATS[info.format]

    # 3. Store the original and create thumbnails -- before the database row, so that no record
    #    can exist whose files are missing.
    target = original_path(settings.photos_dir, sha256, suffix)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(path, target)

    try:
        thumbnails.create_thumbnails(target, settings.thumbs_dir, sha256)
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        target.unlink(missing_ok=True)
        thumbnails.remove_thumbnails(settings.thumbs_dir, sha256)
        outcome = ImportOutcome(ImportResult.REJECTED, f"Vorschaubild fehlgeschlagen: {error}")
        _log_outcome(session, path, outcome, sha256)
        if move_aside:
            _move_aside(path, inbox, PROBLEM_DIR)
        return outcome

    # 4. The record.
    photo = Photo(
        sha256=sha256,
        original_filename=path.name,
        mime=mime,
        bytes=path.stat().st_size,
        width=info.width,
        height=info.height,
        title=info.title,
        description=info.description,
        title_source=Source.EXIF if info.title else None,
        exif_datetime=info.exif_datetime,
        date_precision=DatePrecision.UNKNOWN,
    )

    # The EXIF date is only adopted when it is plausibly a capture date. For a scan it is the date
    # of the scanning run -- see app/services/exif.py.
    moment = info.exif_datetime
    if moment and not exif_service.is_scan_date(moment, settings.exif_date_max_year):
        photo.date_from, photo.date_to, precision = date_range(
            moment.year, moment.month, moment.day
        )
        photo.date_precision = precision
        photo.date_source = Source.EXIF

    if info.lat is not None and info.lon is not None:
        photo.lat, photo.lon = info.lat, info.lon
        photo.location_source = Source.EXIF

    for name in dict.fromkeys(info.keywords):
        tag = session.scalar(select(Tag).where(Tag.name == name)) or Tag(name=name)
        photo.tags.append(tag)

    session.add(photo)
    session.flush()  # assigns the id for the log entry

    missing = [
        label
        for label, empty in (("Ort", photo.needs_location), ("Jahr", photo.needs_date))
        if empty
    ]
    message = "Aufgenommen" + (f", es fehlt noch: {' und '.join(missing)}" if missing else "")

    outcome = ImportOutcome(ImportResult.IMPORTED, message, photo=photo, path=target)
    _log_outcome(session, path, outcome, sha256)

    if move_aside:
        _move_aside(path, inbox, DONE_DIR)

    return outcome


def import_directory(
    session: Session,
    directory: Path,
    settings: Settings,
    *,
    move_aside: bool = False,
) -> list[ImportOutcome]:
    """Every image in a directory, recursively, in stable order."""
    outcomes: list[ImportOutcome] = []

    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if SPECIAL_DIRS & set(path.relative_to(directory).parts):
            continue

        outcomes.append(import_file(session, path, settings, move_aside=move_aside))

    return outcomes
