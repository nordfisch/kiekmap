"""The sample collection: writing it out, and putting it back.

A development state that cannot be restored is not a state, it is a coincidence. This is what
makes one reproducible -- ``seed-export`` writes the running collection to ``seed/``,
``seed-load`` turns it back into a database.

Three decisions shape the form:

  * **Image files plus a JSON file, not a database dump.** A dump is worthless the moment a column
    is added -- and that is precisely what keeps happening. A new column costs one line per photo
    here; the collection itself does not have to be curated again.
  * **Loading goes through the real import pipeline** rather than writing rows. That is slower and
    right: it produces the thumbnails, fills the import log, and checks the pipeline on the way.
  * **Visitor contributions hang off their photo**, not in a list of their own. Photo ids are
    handed out afresh on every load, so a reference by id would not survive the round trip.

The keys mirror the column names in ``models.py`` one for one. Where a column is added, the
exporter picks it up on its own -- which is why ``FIELDS`` exists rather than a hand-written dict.
"""

import json
import logging
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Change, ImportLog, Photo, PhotoTag, Tag
from app.services.importer import import_file
from app.services.storage import original_path, suffix_for_mime

log = logging.getLogger(__name__)

#: Where the sample collection lives. Beside ``data/``, not inside it -- ``data/`` is what gets
#: emptied, and a backup that lies in the thing it restores is none.
SEED_DIR_NAME = "seed"
IMAGE_DIR_NAME = "fotos"
INDEX_NAME = "seed.json"

#: Photo columns that belong to the collection rather than to this device. Everything about the
#: file itself -- sha256, size, dimensions, mime -- is left out on purpose: it is read back off
#: the image, and a copy of it here could only ever go stale.
FIELDS = (
    "title",
    "description",
    "date_from",
    "date_to",
    "date_precision",
    "lat",
    "lon",
    "place_name",
    "location_accuracy_m",
    "title_source",
    "date_source",
    "location_source",
    "credit",
    "provenance",
    "status",
    "exif_datetime",
)

#: Change columns worth keeping. ``photo_id`` is missing because the nesting says it, ``id`` and
#: ``created_at`` because they are handed out anew.
CHANGE_FIELDS = ("field", "old_value", "new_value", "source", "session_id")


def seed_dir(settings: Settings) -> Path:
    """``data/`` is under the project root, and so is ``seed/``."""
    return settings.data_dir.parent / SEED_DIR_NAME


def _as_json(value: object) -> object:
    if isinstance(value, datetime | date):
        return value.isoformat()
    return value


def _from_json(field: str, value: object) -> object:
    if value is None:
        return None
    if field in ("date_from", "date_to"):
        return date.fromisoformat(str(value))
    if field == "exif_datetime":
        return datetime.fromisoformat(str(value))
    return value


def _free_name(taken: set[str], name: str) -> str:
    """Two scans may well have arrived under the same file name."""
    if name not in taken:
        return name
    stem, suffix = Path(name).stem, Path(name).suffix
    for counter in range(2, 1000):
        candidate = f"{stem} ({counter}){suffix}"
        if candidate not in taken:
            return candidate
    raise RuntimeError(f"kein freier Name fuer {name}")


# --- writing out -------------------------------------------------------------


def export(session: Session, settings: Settings, target: Path) -> tuple[int, int]:
    """Write every photo and its contributions to ``target``. Returns (photos, contributions).

    Deleted photos come along: that two of them are in the collection is part of the state, not a
    leftover -- otherwise the "Geloescht" list is empty and nobody can check it.
    """
    images = target / IMAGE_DIR_NAME
    images.mkdir(parents=True, exist_ok=True)

    taken: set[str] = set()
    entries: list[dict] = []
    contributions = 0

    for photo in session.scalars(select(Photo).order_by(Photo.id)):
        suffix = suffix_for_mime(photo.mime)
        if suffix is None:
            log.warning("Foto %s: unbekanntes Format %s -- uebersprungen", photo.id, photo.mime)
            continue

        source = original_path(settings.photos_dir, photo.sha256, suffix)
        if not source.exists():
            log.warning("Foto %s: die Datei %s fehlt -- uebersprungen", photo.id, source)
            continue

        name = _free_name(taken, photo.original_filename)
        taken.add(name)
        shutil.copy2(source, images / name)

        changes = session.scalars(
            select(Change).where(Change.photo_id == photo.id).order_by(Change.id)
        ).all()
        contributions += len(changes)

        entries.append(
            {
                "file": name,
                "sha256": photo.sha256,
                **{field: _as_json(getattr(photo, field)) for field in FIELDS},
                "tags": [tag.name for tag in photo.tags],
                "changes": [
                    {
                        **{field: getattr(change, field) for field in CHANGE_FIELDS},
                        "reverted": change.reverted_at is not None,
                    }
                    for change in changes
                ],
            }
        )

    # What is no longer in the collection has no business here. Without this tidying every photo
    # ever deleted would stay behind as a file -- and a folder that only grows is no
    # Abbild eines Zustands mehr.
    for datei in images.iterdir():
        if datei.is_file() and datei.name not in taken:
            datei.unlink()

    index = {
        "created": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "photos": entries,
    }
    (target / INDEX_NAME).write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return len(entries), contributions


# --- putting it back ---------------------------------------------------------


def clear(session: Session, settings: Settings) -> None:
    """Empty the collection -- rows, originals, thumbnails.

    The gazetteer stays: it comes from an Overpass run and has nothing to do with the photos.
    """
    session.execute(delete(PhotoTag))
    session.execute(delete(Change))
    session.execute(delete(ImportLog))
    session.execute(delete(Photo))
    session.execute(delete(Tag))
    session.flush()

    for folder in (settings.photos_dir, settings.thumbs_dir):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True, exist_ok=True)


def load(session: Session, settings: Settings, source: Path) -> tuple[int, int]:
    """Empty the collection and rebuild it from ``source``. Returns (photos, contributions).

    Raises ``FileNotFoundError`` if there is no sample collection -- the caller turns that into a
    sentence for the reader rather than a stack trace.
    """
    index_file = source / INDEX_NAME
    if not index_file.exists():
        raise FileNotFoundError(index_file)

    index = json.loads(index_file.read_text(encoding="utf-8"))
    images = source / IMAGE_DIR_NAME

    clear(session, settings)

    photos = 0
    contributions = 0
    for entry in index.get("photos", []):
        path = images / entry["file"]
        if not path.exists():
            log.warning("%s fehlt -- uebersprungen", path)
            continue

        outcome = import_file(session, path, settings)
        if not outcome.succeeded or outcome.photo is None:
            log.warning("%s: %s", entry["file"], outcome.message)
            continue

        photo = outcome.photo
        if photo.sha256 != entry.get("sha256"):
            log.warning("%s hat sich seit dem Sichern geaendert", entry["file"])

        # The import has read title, date and tags out of the file. What is noted here counts
        # more -- it is the curated statement, the file only ever held a guess.
        for field in FIELDS:
            if field in entry:
                setattr(photo, field, _from_json(field, entry[field]))

        photo.tags.clear()
        for name in dict.fromkeys(entry.get("tags", [])):
            photo.tags.append(session.scalar(select(Tag).where(Tag.name == name)) or Tag(name=name))

        for change in entry.get("changes", []):
            session.add(
                Change(
                    photo_id=photo.id,
                    **{field: change.get(field) for field in CHANGE_FIELDS},
                    reverted_at=datetime.now(UTC).replace(tzinfo=None)
                    if change.get("reverted")
                    else None,
                )
            )
            contributions += 1

        photos += 1

    # The import creates tags out of the files; the line above detaches them again when the
    # collection prescribes different ones. Without this tidying orphaned entries would pile up,
    # and the admin area's tag list would fill with words attached to no photo.
    session.flush()
    session.execute(delete(Tag).where(~Tag.photos.any()))
    session.flush()
    return photos, contributions
