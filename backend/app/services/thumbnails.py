"""Vorschaubilder.

Zwei Groessen, beide beim Import erzeugt: 240 px fuer die Marker auf der Karte, 1200 px fuer das
Overlay und den "Hilf mit"-Bereich. Auf einem Pi waere das Rechnen zur Anzeigezeit spuerbar, beim
Import faellt es nicht auf.

WebP, weil es bei gleicher Qualitaet deutlich kleiner ist als JPEG -- und die Karte laedt schnell
mal fuenfzig Marker auf einmal.
"""

import logging
from pathlib import Path

from PIL import Image, ImageOps

from app.services.storage import THUMBNAIL_GROESSEN, thumbnail_pfad

log = logging.getLogger(__name__)

_QUALITAET = 82


def _fuer_anzeige(bild: Image.Image) -> Image.Image:
    """Dreht nach EXIF und bringt in einen Farbraum, den WebP kennt.

    Gescannte Vorlagen kommen oft als CMYK-TIFF oder mit Graustufen-Palette. Ohne Umwandlung
    scheitert das Speichern -- und zwar erst beim letzten Schritt, nach aller Rechenarbeit.
    """
    bild = ImageOps.exif_transpose(bild) or bild
    if bild.mode in ("RGBA", "LA"):
        return bild.convert("RGBA")
    if bild.mode != "RGB":
        return bild.convert("RGB")
    return bild


def erzeuge_thumbnails(quelle: Path, ziel_wurzel: Path, sha256: str) -> list[Path]:
    """Erzeugt alle Groessen und gibt die geschriebenen Pfade zurueck."""
    geschrieben: list[Path] = []

    with Image.open(quelle) as roh:
        anzeige = _fuer_anzeige(roh)

        for groesse in THUMBNAIL_GROESSEN:
            ziel = thumbnail_pfad(ziel_wurzel, sha256, groesse)
            ziel.parent.mkdir(parents=True, exist_ok=True)

            verkleinert = anzeige.copy()
            verkleinert.thumbnail((groesse, groesse), Image.Resampling.LANCZOS)
            verkleinert.save(ziel, "WEBP", quality=_QUALITAET, method=6)
            geschrieben.append(ziel)

    return geschrieben


def entferne_thumbnails(ziel_wurzel: Path, sha256: str) -> None:
    for groesse in THUMBNAIL_GROESSEN:
        thumbnail_pfad(ziel_wurzel, sha256, groesse).unlink(missing_ok=True)
