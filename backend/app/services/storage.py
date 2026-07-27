"""Dateiablage.

Bilder heissen nach dem SHA-256 ihres Inhalts. Das loest vier Dinge auf einmal: keine
Namenskollisionen, Dublettenerkennung gratis, beliebig cachebare Auslieferung und -- weil gleicher
Name garantiert gleichen Inhalt bedeutet -- eine inkrementelle Sicherung, die beim zweiten Mal nur
noch die neuen Bilder kopiert. Siehe docs/decisions.md, Punkt 3.
"""

import hashlib
from pathlib import Path

#: Groessen der vorberechneten Vorschaubilder in Pixeln (laengere Kante).
THUMBNAIL_GROESSEN = (240, 1200)

#: Was importiert werden darf. Alles andere wird mit Begruendung abgewiesen statt still ignoriert.
ERLAUBTE_FORMATE = {
    "JPEG": ("image/jpeg", ".jpg"),
    "PNG": ("image/png", ".png"),
    "TIFF": ("image/tiff", ".tif"),
    "WEBP": ("image/webp", ".webp"),
}


def sha256_der_datei(pfad: Path, blockgroesse: int = 1024 * 1024) -> str:
    """Haeppchenweise, damit auch ein 200-MB-TIFF nicht in den Speicher muss."""
    hasher = hashlib.sha256()
    with pfad.open("rb") as datei:
        while block := datei.read(blockgroesse):
            hasher.update(block)
    return hasher.hexdigest()


def _gefaechert(sha256: str) -> Path:
    """``a3f29c…`` wird zu ``a3/f2/``.

    Bei einigen tausend Dateien noch gleichgueltig, bei Wachstum der Unterschied zwischen einem
    Verzeichnis, das sich oeffnen laesst, und einem, das es nicht tut.
    """
    return Path(sha256[0:2]) / sha256[2:4]


def original_pfad(wurzel: Path, sha256: str, endung: str) -> Path:
    return wurzel / _gefaechert(sha256) / f"{sha256}{endung}"


def thumbnail_pfad(wurzel: Path, sha256: str, groesse: int) -> Path:
    return wurzel / str(groesse) / _gefaechert(sha256) / f"{sha256}.webp"
