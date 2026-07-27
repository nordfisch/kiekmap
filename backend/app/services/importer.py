"""Fotos in die Datenbank aufnehmen.

Ablauf pro Datei: Hash bilden, gegen Dubletten pruefen, Bild lesen, Metadaten herausholen, Original
ablegen, Vorschaubilder erzeugen, Zeile schreiben. Jeder Ausgang -- aufgenommen, Dublette,
abgewiesen -- landet im Import-Protokoll. Ohne das waere ein still uebersprungenes Foto nicht von
einem nie hineinkopierten zu unterscheiden.

Aus dem ueberwachten Ordner werden Dateien danach beiseitegeraeumt, nie geloescht:

    data/incoming/            was noch zu tun ist
    data/incoming/_erledigt/  aufgenommen
    data/incoming/_problem/   nicht lesbar oder unbekanntes Format
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
from app.services import exif as exif_dienst
from app.services import thumbnails
from app.services.dates import zeitraum
from app.services.storage import ERLAUBTE_FORMATE, original_pfad, sha256_der_datei

log = logging.getLogger(__name__)

ERLEDIGT = "_erledigt"
PROBLEM = "_problem"
#: Unterordner des Eingangs, die nicht selbst durchsucht werden.
SONDERORDNER = {ERLEDIGT, PROBLEM}


@dataclass
class Ergebnis:
    result: ImportResult
    message: str
    photo: Photo | None = None
    pfad: Path | None = None

    @property
    def erfolgreich(self) -> bool:
        return self.result == ImportResult.IMPORTED


def _protokolliere(
    session: Session,
    pfad: Path,
    ergebnis: Ergebnis,
    sha256: str | None = None,
) -> None:
    session.add(
        ImportLog(
            path=str(pfad),
            sha256=sha256,
            result=ergebnis.result,
            message=ergebnis.message,
            photo_id=ergebnis.photo.id if ergebnis.photo else None,
        )
    )


def _freier_name(ordner: Path, name: str) -> Path:
    """Verhindert, dass beim Beiseiteraeumen etwas ueberschrieben wird."""
    ziel = ordner / name
    if not ziel.exists():
        return ziel
    stamm, endung = Path(name).stem, Path(name).suffix
    for zaehler in range(2, 1000):
        ziel = ordner / f"{stamm} ({zaehler}){endung}"
        if not ziel.exists():
            return ziel
    raise RuntimeError(f"Kein freier Name fuer {name} in {ordner}")


def _raeume_beiseite(pfad: Path, eingang: Path, unterordner: str) -> None:
    ziel_ordner = eingang / unterordner
    ziel_ordner.mkdir(parents=True, exist_ok=True)
    shutil.move(str(pfad), _freier_name(ziel_ordner, pfad.name))


def importiere_datei(
    session: Session,
    pfad: Path,
    settings: Settings,
    *,
    beiseiteraeumen: bool = False,
) -> Ergebnis:
    """Nimmt eine einzelne Datei auf.

    ``beiseiteraeumen`` gilt fuer den ueberwachten Ordner. Beim Import aus einem beliebigen
    Verzeichnis bleiben die Dateien des Nutzers unberuehrt.
    """
    eingang = settings.incoming_dir

    # 1. Hash zuerst: er entscheidet ueber Dublette und ist zugleich der spaetere Dateiname.
    try:
        sha256 = sha256_der_datei(pfad)
    except OSError as fehler:
        ergebnis = Ergebnis(ImportResult.REJECTED, f"Datei nicht lesbar: {fehler}")
        _protokolliere(session, pfad, ergebnis)
        return ergebnis

    vorhanden = session.scalar(select(Photo).where(Photo.sha256 == sha256))
    if vorhanden:
        ergebnis = Ergebnis(
            ImportResult.DUPLICATE,
            f"Inhaltsgleich mit Foto {vorhanden.id} ({vorhanden.original_filename})",
            photo=vorhanden,
        )
        _protokolliere(session, pfad, ergebnis, sha256)
        if beiseiteraeumen:
            _raeume_beiseite(pfad, eingang, ERLEDIGT)
        return ergebnis

    # 2. Bild lesen.
    try:
        info = exif_dienst.lies_bildinfo(pfad)
    except (UnidentifiedImageError, OSError, ValueError) as fehler:
        ergebnis = Ergebnis(ImportResult.REJECTED, f"Kein lesbares Bild: {fehler}")
        _protokolliere(session, pfad, ergebnis, sha256)
        if beiseiteraeumen:
            _raeume_beiseite(pfad, eingang, PROBLEM)
        return ergebnis

    if info.format not in ERLAUBTE_FORMATE:
        ergebnis = Ergebnis(
            ImportResult.REJECTED,
            f"Format {info.format or 'unbekannt'} wird nicht unterstuetzt "
            f"(erlaubt: {', '.join(sorted(ERLAUBTE_FORMATE))})",
        )
        _protokolliere(session, pfad, ergebnis, sha256)
        if beiseiteraeumen:
            _raeume_beiseite(pfad, eingang, PROBLEM)
        return ergebnis

    mime, endung = ERLAUBTE_FORMATE[info.format]

    # 3. Original ablegen und Vorschaubilder erzeugen -- vor dem Datenbankeintrag, damit kein
    #    Datensatz entsteht, zu dem die Dateien fehlen.
    ziel = original_pfad(settings.photos_dir, sha256, endung)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if not ziel.exists():
        shutil.copy2(pfad, ziel)

    try:
        thumbnails.erzeuge_thumbnails(ziel, settings.thumbs_dir, sha256)
    except (OSError, ValueError, Image.DecompressionBombError) as fehler:
        ziel.unlink(missing_ok=True)
        thumbnails.entferne_thumbnails(settings.thumbs_dir, sha256)
        ergebnis = Ergebnis(ImportResult.REJECTED, f"Vorschaubild fehlgeschlagen: {fehler}")
        _protokolliere(session, pfad, ergebnis, sha256)
        if beiseiteraeumen:
            _raeume_beiseite(pfad, eingang, PROBLEM)
        return ergebnis

    # 4. Datensatz.
    foto = Photo(
        sha256=sha256,
        original_filename=pfad.name,
        mime=mime,
        bytes=pfad.stat().st_size,
        width=info.breite,
        height=info.hoehe,
        title=info.titel,
        description=info.beschreibung,
        title_source=Source.EXIF if info.titel else None,
        exif_datetime=info.exif_datetime,
        date_precision=DatePrecision.UNKNOWN,
    )

    # Das EXIF-Datum wird nur uebernommen, wenn es plausibel ein Aufnahmedatum ist. Bei einem Scan
    # ist es das Datum des Scanvorgangs -- siehe app/services/exif.py.
    zeitpunkt = info.exif_datetime
    if zeitpunkt and not exif_dienst.ist_scandatum(zeitpunkt, settings.exif_date_max_year):
        foto.date_from, foto.date_to, genauigkeit = zeitraum(
            zeitpunkt.year, zeitpunkt.month, zeitpunkt.day
        )
        foto.date_precision = genauigkeit
        foto.date_source = Source.EXIF

    if info.lat is not None and info.lon is not None:
        foto.lat, foto.lon = info.lat, info.lon
        foto.location_source = Source.EXIF

    for name in dict.fromkeys(info.schlagwoerter):
        schlagwort = session.scalar(select(Tag).where(Tag.name == name)) or Tag(name=name)
        foto.tags.append(schlagwort)

    session.add(foto)
    session.flush()  # vergibt die id fuer das Protokoll

    fehlt = [was for was, leer in (("Ort", foto.needs_location), ("Jahr", foto.needs_date)) if leer]
    meldung = "Aufgenommen" + (f", es fehlt noch: {' und '.join(fehlt)}" if fehlt else "")

    ergebnis = Ergebnis(ImportResult.IMPORTED, meldung, photo=foto, pfad=ziel)
    _protokolliere(session, pfad, ergebnis, sha256)

    if beiseiteraeumen:
        _raeume_beiseite(pfad, eingang, ERLEDIGT)

    return ergebnis


def importiere_verzeichnis(
    session: Session,
    verzeichnis: Path,
    settings: Settings,
    *,
    beiseiteraeumen: bool = False,
) -> list[Ergebnis]:
    """Alle Bilder eines Verzeichnisses, rekursiv, in stabiler Reihenfolge."""
    ergebnisse: list[Ergebnis] = []

    for pfad in sorted(verzeichnis.rglob("*")):
        if not pfad.is_file() or pfad.name.startswith("."):
            continue
        if SONDERORDNER & set(pfad.relative_to(verzeichnis).parts):
            continue

        ergebnisse.append(
            importiere_datei(session, pfad, settings, beiseiteraeumen=beiseiteraeumen)
        )

    return ergebnisse
