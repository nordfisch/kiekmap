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
import re
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
from app.models import DatePrecision, ImportLog, ImportResult, Photo, Source
from app.services import exif as exif_service
from app.services import foldermeta, thumbnails
from app.services.dates import date_range
from app.services.storage import ALLOWED_FORMATS, original_path, sha256_of_file
from app.services.tags import add_tags

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


def _free_name(target: Path) -> Path:
    """Make sure nothing is overwritten when moving files aside."""
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    for counter in range(2, 1000):
        candidate = target.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"no free name for {target.name} in {target.parent}")


def _move_aside(path: Path, inbox: Path, subfolder: str) -> None:
    """File a finished photo away under ``_erledigt/`` or ``_problem/`` -- **keeping its folders**.

    ``incoming/Hauptstraße/14 Museum/x.jpg`` becomes ``_erledigt/Hauptstraße/14 Museum/x.jpg``,
    not ``_erledigt/x.jpg``. Flattened, a stack filed by street was a one-way trip: the folder
    names are what say where those photos are (see foldermeta.py), so a second run or even a spot
    check afterwards had nothing left to read -- and equal file names from different houses piled
    up as "023 (2).jpg", "023 (3).jpg".
    """
    target = inbox / subfolder / foldermeta.relative_to_root(path, inbox)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), _free_name(target))


def move_to_done(path: Path, inbox: Path) -> None:
    """File a finished file away -- public, because the backup needs it too.

    A restored archive moves to ``_erledigt`` like every photo that came through this folder. Its
    own name rather than a public ``move_aside``: a parameter of ``import_file`` is called that,
    and it would shadow the function inside its scope.
    """
    _move_aside(path, inbox, DONE_DIR)


#: Beyond this many characters, what stands in the title field is a caption.
#:
#: Whoever filled in the archive wrote what they knew, and the title field was where the cursor
#: was: "Beschriftung: v. li.: Johann Harms, Tina Harms (Mutter v. Grete, verwitw. ...)",
#: 223 characters, sometimes with line breaks. As a heading in the detail view that is a wall of
#: text; as a description it is exactly right, and the folder supplies a heading that fits on one
#: line.
#:
#: **The number is measured, not chosen.** It stood at 120 and let through eight titles of the
#: newer archive stand that are plainly captions -- "links Hauptstraße 27, Mitte Hauptstraße 29,
#: rechts im Vordergrund Schulstraße 2a, Foto aus den 1980er Jahren", 108 characters. The 781
#: titles the museum curated by hand have a ceiling: **not one exceeds 58 characters**, the median
#: is 13. Sixty is that ceiling with room to spare, and everything above it is a caption in the
#: title field.
TITLE_MAX = 60

#: What the scanning software says about itself, standing in the title field.
#:
#: "Intel(R) JPEG Library, version [1.51.12.44]" arrived as the title of 35 photographs of the
#: newer archive stand, "OLYMPUS DIGITAL CAMERA" as the description of others. It is not a
#: shortened caption and does not belong in the description either -- it says nothing about the
#: picture. Punkt 41 removed eighteen of these by hand; they came back with the next import.
_SOFTWARE = re.compile(
    r"^\s*(intel\(r\)|olympus digital camera|lead technologies|picasa|hp scanjet|epson scan)",
    re.I,
)


def _is_software(text: str | None) -> bool:
    return bool(text and _SOFTWARE.match(text))


def _own_title(info: exif_service.ImageInfo) -> str | None:
    if _is_software(info.title):
        return None
    if info.title and (len(info.title) > TITLE_MAX or "\n" in info.title):
        return None
    return info.title


def _own_description(info: exif_service.ImageInfo) -> str | None:
    """The caption -- unless it only repeats the title.

    Many scanning programs write the same sentence into both fields. Shown one under the other in
    the detail view that reads like a stutter, and it costs the space where something the picture
    actually needs could stand. 57 files of the Holm stock do it.

    A title too long to be one lands here instead of being thrown away; see ``TITLE_MAX``. What
    the scanning software wrote about itself does not -- see ``_SOFTWARE``, it would only move the
    same nonsense one line down.
    """
    long_title = info.title if _own_title(info) is None and not _is_software(info.title) else None
    description = None if _is_software(info.description) else info.description
    description = description or long_title
    if not description:
        return None
    if long_title and info.description:
        description = f"{long_title}\n\n{info.description}"

    title = _own_title(info)
    if title and description.strip().lower() == title.strip().lower():
        return None
    return description


def import_file(
    session: Session,
    path: Path,
    settings: Settings,
    *,
    move_aside: bool = False,
    root: Path | None = None,
) -> ImportOutcome:
    """Take in a single file.

    ``move_aside`` applies to the watched folder. When importing from an arbitrary directory the
    user's files are left untouched.

    ``root`` is the folder the import was started on. Given one, the import reads the folder names
    below it as statements about the photo -- street, house number, name; see
    app/services/foldermeta.py. Without one it reads only the file itself.

    **That this decision sits here and not at the call site is the point.** It used to be a line
    each caller had to remember, and the busiest of them -- the watched inbox, which CLAUDE.md
    calls the museum team's usual route -- did not have it. 929 photographs came in with their
    street standing in the path and nowhere in the database. A fifth import route now has to
    *answer* the question "what is this file's root?" rather than silently skip it; the browser
    upload answers it with ``None``, because a browser sends no path.
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
        title=_own_title(info),
        description=_own_description(info),
        title_source=Source.EXIF if _own_title(info) else None,
        # Whoever the file names, else the collection as a whole -- see Settings.import_credit.
        credit=info.credit or settings.import_credit or None,
        provenance=info.source,
        exif_datetime=info.exif_datetime,
        date_precision=DatePrecision.UNKNOWN,
    )

    # The EXIF date is only adopted when it plausibly dates the picture rather than the scanning
    # run -- see exif.capture_year, which is where that decision lives.
    if moment := exif_service.capture_year(info, settings.exif_date_max_year):
        photo.date_from, photo.date_to, precision = date_range(
            moment.year, moment.month, moment.day
        )
        photo.date_precision = precision
        photo.date_source = Source.EXIF

    if info.lat is not None and info.lon is not None:
        photo.lat, photo.lon = info.lat, info.lon
        photo.location_source = Source.EXIF

    session.add(photo)
    session.flush()  # assigns the id for the log entry

    # After the flush, not before: add_tags writes a new tag out at once, and doing that while
    # the photo is still transient would drop the link between the two.
    add_tags(session, photo, [*info.keywords, *settings.import_tags])

    # And before the closing message is put together, so that it tells the truth: a photo the
    # folder is about to locate must not be logged as "es fehlt noch: Ort".
    if root is not None:
        foldermeta.apply_folder_meta(session, photo, path, root, settings)

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
    "kiekmap-sicherung",
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


def _is_image(entry: Path) -> bool:
    return (
        entry.is_file()
        and not entry.name.startswith(".")
        and entry.suffix.lower() in IMAGE_SUFFIXES
    )


def images_in(folder: Path) -> list[Path]:
    """Every image below a folder, subfolders included, in stable order.

    Recursive because an archive is filed, not piled -- and the folder names carry statements of
    their own; see app/services/foldermeta.py. A stick has to behave like the watched folder,
    which walks recursively too.
    """
    found = [entry for entry in folder.rglob("*") if _is_image(entry)]
    return sorted(
        entry
        for entry in found
        if not (SKIPPED_FOLDERS & set(entry.relative_to(folder).parts[:-1]))
    )


def count_images(folder: Path) -> int:
    """How many images an import of this folder would take in -- subfolders included."""
    try:
        return len(images_in(folder))
    except OSError:
        return 0


def _direct_images(folder: Path) -> int:
    try:
        return sum(1 for entry in folder.iterdir() if _is_image(entry))
    except OSError:
        return 0


def find_image_folders(root: Path, max_depth: int = 4) -> list[ImportFolder]:
    """Folders on a drive that hold images, the drive itself included.

    Offered are the folders whose pictures lie directly in them -- plus the drive itself, which
    since the import walks subfolders takes in everything at once. Without that entry an archive
    filed by street would have to be imported street by street, thirty-eight times.

    The count is what the import would take in, subfolders included, not what lies directly in
    the folder. Depth is capped -- a stick with a whole backup of somebody's home directory
    should not cost a minute of walking.
    """
    found: list[ImportFolder] = []

    def look(folder: Path, depth: int) -> None:
        if depth > max_depth:
            return
        images = count_images(folder)
        if images > 0 and (depth == 0 or _direct_images(folder) > 0):
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


def batch_tags(text: str | None) -> list[str]:
    """The batch keyword field, split into keywords.

    Commas separate, because somebody who knows the box holds "Feuerwehr, Neubau" should not need
    a second field for it. That this is the same split that once turned whole sentences into
    keywords (see backlog, point 1) is not the same case: there a machine cut up a caption, here
    a person types into a field labelled "Schlagwörter".
    """
    return [word.strip() for word in (text or "").split(",") if word.strip()]


def apply_batch_defaults(
    session: Session,
    photo: Photo,
    year: int | None,
    precision: DatePrecision,
    lat: float | None,
    lon: float | None,
    place_name: str | None,
    *,
    credit: str | None = None,
    provenance: str | None = None,
    tags: str | None = None,
) -> None:
    """Statements that apply to a whole batch -- from the upload form or the stick.

    They only fill what the import left empty. A scan almost never brings a usable date or GPS
    with it, so in practice they apply to everything -- but where the file does know better, the
    file wins.

    **The keywords are the exception, and they have to be.** Every other field here holds one
    value, so filling it means deciding between the file and the form. A keyword list is a *set*:
    the batch word joins what the file brought rather than replacing it. Three sources end up in
    it, and this is their order -- ``KIEKMAP_IMPORT_TAGS`` for every import on this device, then
    what the file says about itself, then the batch word from the form. ``add_tags`` skips what
    the photo already carries, so the order costs nothing and only decides who creates a name.
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

    if words := batch_tags(tags):
        add_tags(session, photo, words)


def import_from_folder(
    session: Session,
    folder: Path,
    settings: Settings,
    defaults: Callable[[Photo], None] | None = None,
    report: Callable[[int, int, str], None] | None = None,
) -> tuple[str, list[ImportOutcome]]:
    """Take in every image of one folder, subfolders included.

    Returns the German closing message and what became of each file -- the caller decides whether
    a list that long is still worth showing (see REVIEW_LIMIT in app/api/backup.py).

    Committed photo by photo, not at the end: a stick pulled out halfway then leaves behind what
    was already read, instead of nothing.
    """
    images = images_in(folder)
    counts = {result: 0 for result in ImportResult}
    outcomes: list[ImportOutcome] = []

    for index, path in enumerate(images, start=1):
        # move_aside stays False -- see the note at the top of this section. The folder names are
        # read inside import_file; the batch form comes after, because both only fill what is
        # empty and the form's statement ("all of these are from the Kirchweih") is the coarser.
        outcome = import_file(session, path, settings, root=folder)
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

    **No ``root``, deliberately.** A browser sends a bare file name; the temporary directory this
    writes to says nothing about anybody's archive. What the whole batch has in common comes from
    the form instead, through ``apply_batch_defaults``.
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

        outcomes.append(import_file(session, path, settings, move_aside=move_aside, root=directory))

    return outcomes
