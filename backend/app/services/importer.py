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
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

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
    #: Where the image was stored. Only set when it was actually taken in.
    path: Path | None = None
    #: The file it came from. ``import_file`` is handed a path but does not keep it -- the caller
    #: fills this in where the original name still matters, as the review table does.
    source: Path | None = None

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
            f"Format {info.format or 'unbekannt'} passt nicht "
            f"(erlaubt sind: {', '.join(sorted(ALLOWED_FORMATS))})",
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


# --- taking in a folder from a USB stick -------------------------------------
#
# The stick belongs to somebody else. Nothing here moves or deletes a single file on it, unlike
# the watched inbox where moving aside is the whole point. Read and copy, that is all.

#: File endings that count as an image when looking around a stick.
IMAGE_SUFFIXES = {suffix for _, suffix in ALLOWED_FORMATS.values()} | {".jpeg", ".tiff"}

#: Folders never worth offering: our own backup, and what the operating systems leave behind.
SKIPPED_FOLDERS = {
    "photomap-sicherung",
    "System Volume Information",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    "$RECYCLE.BIN",
    DONE_DIR,
    PROBLEM_DIR,
}


@dataclass
class ImportFolder:
    path: Path
    #: Relative to the drive, so the admin recognises it: "Scans2024/Kirchweih".
    name: str
    images: int


def count_images(folder: Path) -> int:
    try:
        return sum(
            1
            for entry in folder.iterdir()
            if entry.is_file() and entry.suffix.lower() in IMAGE_SUFFIXES
        )
    except OSError:
        return 0


def find_image_folders(root: Path, max_depth: int = 4) -> list[ImportFolder]:
    """Folders on a drive that hold images, the drive itself included.

    Only where the images actually are: a folder whose pictures all sit in subfolders is not
    offered, because importing it would take in nothing. Depth is capped -- a stick with a whole
    backup of somebody's home directory should not cost a minute of walking.
    """
    found: list[ImportFolder] = []

    def look(folder: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if (images := count_images(folder)) > 0:
            relative = folder.relative_to(root)
            found.append(
                ImportFolder(
                    path=folder,
                    name=str(relative) if str(relative) != "." else folder.name,
                    images=images,
                )
            )
        try:
            children = sorted(entry for entry in folder.iterdir() if entry.is_dir())
        except OSError:
            return
        for child in children:
            if child.name in SKIPPED_FOLDERS or child.name.startswith("."):
                continue
            look(child, depth + 1)

    if root.is_dir():
        look(root, 0)
    return found


def apply_batch_defaults(
    photo: Photo,
    year: int | None,
    precision: DatePrecision,
    lat: float | None,
    lon: float | None,
    place_name: str | None,
    *,
    credit: str | None = None,
    provenance: str | None = None,
) -> None:
    """Statements that apply to a whole batch -- from the upload form or the stick.

    They only fill what the import left empty. A scan almost never brings a usable date or GPS
    with it, so in practice they apply to everything -- but where the file does know better, the
    file wins.
    """
    if year is not None and photo.needs_date:
        photo.date_from, photo.date_to, photo.date_precision = date_range(
            year, precision=DatePrecision(precision)
        )
        photo.date_source = Source.CURATOR

    if lat is not None and lon is not None and photo.needs_location:
        photo.lat, photo.lon = lat, lon
        photo.location_source = Source.CURATOR

    if place_name and not photo.place_name:
        photo.place_name = place_name

    # Neither of these can come out of the file -- a scanner does not know who lent the picture.
    # They are therefore always the batch statement, and only skipped if something is there.
    if credit and not photo.credit:
        photo.credit = credit

    if provenance and not photo.provenance:
        photo.provenance = provenance


def import_from_folder(
    session: Session,
    folder: Path,
    settings: Settings,
    defaults: Callable[[Photo], None] | None = None,
    report: Callable[[int, int, str], None] | None = None,
) -> tuple[str, list[ImportOutcome]]:
    """Take in every image of one folder.

    Returns the German closing message and what became of each file -- the caller decides whether
    a list that long is still worth showing (see REVIEW_LIMIT in app/api/backup.py).

    Committed photo by photo, not at the end: a stick pulled out halfway then leaves behind what
    was already read, instead of nothing.
    """
    images = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    counts = {result: 0 for result in ImportResult}
    outcomes: list[ImportOutcome] = []

    for index, path in enumerate(images, start=1):
        # move_aside stays False -- see the note at the top of this section.
        outcome = import_file(session, path, settings)
        if outcome.succeeded and outcome.photo is not None and defaults:
            defaults(outcome.photo)
        session.commit()

        outcome.source = path
        outcomes.append(outcome)
        counts[outcome.result] += 1
        if report:
            report(index, len(images), f"Lese Foto {index} von {len(images)}")

    log.info("Stick import from %s: %s", folder, dict(counts))

    teile = [f"{counts[ImportResult.IMPORTED]} Fotos aufgenommen"]
    if counts[ImportResult.DUPLICATE]:
        waren = "war" if counts[ImportResult.DUPLICATE] == 1 else "waren"
        teile.append(f"{counts[ImportResult.DUPLICATE]} {waren} schon da")
    if counts[ImportResult.REJECTED]:
        teile.append(f"{counts[ImportResult.REJECTED]} abgewiesen")

    return ", ".join(teile) + ". Der Stick kann jetzt abgezogen werden.", outcomes


def upload_name(filename: str) -> str:
    """Strip everything but the bare file name off a browser-supplied name.

    Two things are being fended off. A name like ``../../etc/passwd`` must not escape the
    directory -- and a Windows browser sends ``C:\\Scans\\Kirchweih\\bild.jpg``, which
    ``Path().name`` leaves untouched on Linux because a backslash is an ordinary character there.
    """
    return Path(filename.replace("\\", "/")).name or "upload"


def import_upload(
    session: Session,
    filename: str,
    stream: BinaryIO,
    settings: Settings,
) -> ImportOutcome:
    """Take in a file that arrived over HTTP.

    Written to disk first rather than held in memory: a batch of scans is a gigabyte in no time,
    and the Pi has less RAM than that. From there on it is the ordinary import -- the watched
    folder, the CLI and the upload all go through the same code.
    """
    settings.ensure_dirs()
    # Inside the data directory, so the later copy to photos/ stays on one filesystem.
    with tempfile.TemporaryDirectory(dir=settings.data_dir, prefix="upload-") as temporary:
        path = Path(temporary) / upload_name(filename)
        with path.open("wb") as target:
            shutil.copyfileobj(stream, target)
        return import_file(session, path, settings)


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
