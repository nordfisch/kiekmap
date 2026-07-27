"""Konfiguration.

Alle Pfade haengen an einem einzigen Wurzelverzeichnis ``data_dir``. Das ist Absicht: der gesamte
veraenderliche Zustand liegt darunter, damit Sichern "einen Ordner kopieren" heisst.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> backend/app -> backend -> Projektwurzel
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PHOTOMAP_",
        env_file=(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    #: Wurzel aller Laufzeitdaten. Im Container per Bind-Mount auf /data.
    data_dir: Path = PROJECT_ROOT / "data"

    #: Wo eingehaengte USB-Sticks gesucht werden (Stufe 9).
    media_dir: Path = Path("/media")

    #: Erlaubte Herkuenfte fuer den Vite-Dev-Server. In Produktion leer, da gleiche Origin.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    #: Fuer den Admin-Bereich ab Stufe 8. Leer heisst: Admin-API antwortet nicht.
    admin_pin_hash: str = ""

    @property
    def db_path(self) -> Path:
        return self.data_dir / "photomap.db"

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"

    @property
    def photos_dir(self) -> Path:
        """Originale, benannt nach dem SHA-256 ihres Inhalts."""
        return self.data_dir / "photos"

    @property
    def thumbs_dir(self) -> Path:
        return self.data_dir / "thumbs"

    @property
    def incoming_dir(self) -> Path:
        """Ueberwachter Ordner: was hier hineinkopiert wird, wird importiert."""
        return self.data_dir / "incoming"

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.photos_dir, self.thumbs_dir, self.incoming_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
