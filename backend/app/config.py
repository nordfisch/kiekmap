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
        env_prefix="PHOTOMAP_",
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

    @property
    def db_path(self) -> Path:
        return self.data_dir / "photomap.db"

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

    def region_bbox(self) -> tuple[float, float, float, float] | None:
        """[minLon, minLat, maxLon, maxLat], or None when no region is configured."""
        if not self.region_file.is_file():
            return None
        try:
            bbox = json.loads(self.region_file.read_text(encoding="utf-8"))["bbox"]
            return (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError):
            return None

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.photos_dir, self.thumbs_dir, self.incoming_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
