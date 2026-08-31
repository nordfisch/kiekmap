"""Configuration.

Every path hangs off a single root directory, ``data_dir``. That is deliberate: the entire mutable
state lives underneath it, so that backing up means "copy one folder".
"""

import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> backend/app -> backend -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIEKMAP_",
        env_file=(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    #: Root of all runtime data. Bind-mounted to /data inside the container.
    data_dir: Path = PROJECT_ROOT / "data"

    #: Where mounted USB sticks are looked for (stage 9).
    media_dir: Path = Path("/media")

    #: Allowed origins for the Vite dev server. Empty in production -- same origin there.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    #: For the admin area from stage 8 on. Empty means the admin API does not answer.
    admin_pin_hash: str = ""

    #: From which year on an EXIF date counts as a scan date rather than a capture date.
    #:
    #: Historical photos are scans; their EXIF carries the date of the scanning run. Adopting it
    #: would place a photo from 1932 at 2019 on the timeline -- and it would count as dated, so
    #: it would never surface in the "Hilf mit" panel where someone could correct it.
    #: Raise this if the collection also holds genuine digital photographs.
    exif_date_max_year: int = 1990

    #: Keywords every imported photo gets, on top of whatever stands in the file.
    #:
    #: A collection usually *is* about something -- in Holm the stock is buildings, and tagging
    #: them by hand afterwards would be a thousand clicks. It is a setting rather than a constant
    #: because the next museum collects something else; see docs/adaption.md.
    #: In the ``.env``: ``KIEKMAP_IMPORT_TAGS=["Gebäude"]``.
    import_tags: list[str] = []

    #: Credit line for photos whose file names nobody -- "Sammlung Heimatmuseum Holm".
    #:
    #: The last resort, not the rule: whatever the file or the upload form says comes first. Empty
    #: means the photo simply carries no credit line, which is the honest state for a scan whose
    #: origin nobody wrote down.
    import_credit: str = ""

    #: Prefix for the provenance note built from the file's own path in the archive.
    #:
    #: The folder tree is where a photo came from, and the museum's own archive is filed the same
    #: way -- so the path leads straight back to the file somebody would want to look at. Used
    #: verbatim, so it carries its own separator:
    #: ``KIEKMAP_IMPORT_PROVENANCE="Online-Archiv des Museums, Verzeichnis 01 Orte/"``.
    import_provenance: str = ""

    @property
    def db_path(self) -> Path:
        return self.data_dir / "kiekmap.db"

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"

    @property
    def photos_dir(self) -> Path:
        """Originals, named after the SHA-256 of their content."""
        return self.data_dir / "photos"

    @property
    def thumbs_dir(self) -> Path:
        return self.data_dir / "thumbs"

    @property
    def incoming_dir(self) -> Path:
        """Watched folder: whatever is copied in here gets imported."""
        return self.data_dir / "incoming"

    @property
    def places_file(self) -> Path:
        """Gazetteer, produced by ``tiles/build-places.py``."""
        return self.data_dir / "places.json"

    @property
    def region_file(self) -> Path:
        """Copy of ``tiles/region.json``, placed there by ``tiles/build-tiles.sh``.

        It lives in the data directory because that is bind-mounted into the container anyway --
        so there is still exactly one source for the region and no second place to maintain.
        """
        return self.data_dir / "region.json"

    def _region(self) -> dict:
        """The region file as a dict, empty when it is missing or broken.

        Every reader below tolerates an empty region: without ``make tiles`` there is no map
        either, and the parts that do work should keep working.
        """
        if not self.region_file.is_file():
            return {}
        try:
            content = json.loads(self.region_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return content if isinstance(content, dict) else {}

    def region_bbox(self) -> tuple[float, float, float, float] | None:
        """[minLon, minLat, maxLon, maxLat], or None when no region is configured."""
        try:
            bbox = self._region()["bbox"]
            return (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def region_center(self) -> tuple[float, float] | None:
        """(lat, lon) of the village centre, or None when no region is configured.

        Turned around against the file, which holds [lon, lat] the way GeoJSON does. Everything
        inside the backend speaks (lat, lon), and the one place to get that wrong is here.
        """
        try:
            center = self._region()["center"]
            return (float(center[1]), float(center[0]))
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def street_choice(self) -> int:
        """How many streets the "Hilf mit" panel offers as buttons -- the nearest ones.

        See the comment in ``tiles/region.json``. The fallback keeps a village without the key
        usable rather than leaving the panel empty.
        """
        try:
            return max(1, int(self._region()["streetChoice"]))
        except (KeyError, TypeError, ValueError):
            return 80

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.photos_dir, self.thumbs_dir, self.incoming_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
