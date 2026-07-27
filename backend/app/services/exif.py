"""Metadaten aus der Bilddatei lesen.

Der wichtigste Punkt hier ist eine Nichtaktion: **das EXIF-Datum eines Scans wird nicht als
Aufnahmedatum uebernommen.**

Bei einem eingescannten Papierabzug steht im EXIF das Datum des Scans. Uebernaehme man es, laege
ein Foto von 1932 auf der Zeitleiste bei 2019 -- schlimmer noch, es gaelte als datiert und taeuchte
nie im "Hilf mit"-Bereich auf, wo jemand es haette richtigstellen koennen. Ein falsches Datum ist
hier also schaedlicher als gar keines.

Deshalb: EXIF-Datumsangaben ab ``exif_date_max_year`` gelten als Scandatum. Sie werden in
``Photo.exif_datetime`` aufgehoben, damit der Kurator sie sieht, aber sie datieren das Foto nicht.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from PIL import ExifTags, Image, IptcImagePlugin

log = logging.getLogger(__name__)

_EXIF_IFD = 0x8769
_GPS_IFD = 0x8825

_TAG_IMAGE_DESCRIPTION = 0x010E
_TAG_XP_TITLE = 0x9C9B
_TAG_XP_KEYWORDS = 0x9C9E

_IPTC_TITLE = (2, 5)
_IPTC_KEYWORDS = (2, 25)
_IPTC_CAPTION = (2, 120)


@dataclass
class Bildinfo:
    """Was sich aus der Datei selbst herauslesen laesst."""

    breite: int
    hoehe: int
    format: str

    titel: str | None = None
    beschreibung: str | None = None
    schlagwoerter: list[str] = field(default_factory=list)

    lat: float | None = None
    lon: float | None = None

    #: Rohes EXIF-Datum. Ob es das Aufnahmedatum ist, entscheidet der Importeur.
    exif_datetime: datetime | None = None


def _text(wert: object) -> str | None:
    """EXIF-Text kommt als bytes, als UTF-16 oder mit Nullbytes am Ende."""
    if wert is None:
        return None
    if isinstance(wert, bytes):
        for kodierung in ("utf-16-le", "utf-8", "latin-1"):
            try:
                wert = wert.decode(kodierung)
                break
            except UnicodeDecodeError:
                continue
        else:
            return None
    text = str(wert).replace("\x00", "").strip()
    return text or None


def _grad(wert: object, richtung: object) -> float | None:
    """GPS steht als (Grad, Minuten, Sekunden) im EXIF."""
    try:
        grad, minuten, sekunden = (float(teil) for teil in wert)  # type: ignore[misc]
    except (TypeError, ValueError):
        return None

    dezimal = grad + minuten / 60 + sekunden / 3600
    if str(richtung).upper() in ("S", "W"):
        dezimal = -dezimal
    return round(dezimal, 7)


def _exif_datum(exif_ifd: dict) -> datetime | None:
    for tag in (ExifTags.Base.DateTimeOriginal, ExifTags.Base.DateTimeDigitized):
        roh = _text(exif_ifd.get(tag))
        if not roh:
            continue
        for muster in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d"):
            try:
                return datetime.strptime(roh, muster)
            except ValueError:
                continue
    return None


def _iptc(bild: Image.Image, info: Bildinfo) -> None:
    try:
        daten = IptcImagePlugin.getiptcinfo(bild)
    except Exception:  # noqa: BLE001 -- kaputtes IPTC darf den Import nicht aufhalten
        return
    if not daten:
        return

    if titel := _text(daten.get(_IPTC_TITLE)):
        info.titel = info.titel or titel
    if beschreibung := _text(daten.get(_IPTC_CAPTION)):
        info.beschreibung = info.beschreibung or beschreibung

    roh = daten.get(_IPTC_KEYWORDS)
    for eintrag in roh if isinstance(roh, list) else [roh] if roh else []:
        if wort := _text(eintrag):
            info.schlagwoerter.append(wort)


def lies_bildinfo(pfad: Path) -> Bildinfo:
    """Oeffnet die Datei und liest heraus, was sie ueber sich selbst verraet.

    Wirft ``OSError``/``Image.UnidentifiedImageError``, wenn es kein lesbares Bild ist -- der
    Importeur macht daraus einen Eintrag im Import-Protokoll.
    """
    with Image.open(pfad) as bild:
        # Ein hochkant gescanntes Bild traegt seine Ausrichtung im EXIF statt in den Pixeln.
        # Fuer Anzeige und Vorschau zaehlen die Masse nach dieser Drehung.
        gedreht = bild.size
        orientierung = bild.getexif().get(ExifTags.Base.Orientation)
        if orientierung in (5, 6, 7, 8):
            gedreht = (bild.size[1], bild.size[0])

        info = Bildinfo(breite=gedreht[0], hoehe=gedreht[1], format=bild.format or "")

        exif = bild.getexif()
        info.titel = _text(exif.get(_TAG_XP_TITLE)) or _text(exif.get(_TAG_IMAGE_DESCRIPTION))
        if woerter := _text(exif.get(_TAG_XP_KEYWORDS)):
            info.schlagwoerter.extend(t.strip() for t in woerter.split(";") if t.strip())

        exif_ifd = exif.get_ifd(_EXIF_IFD)
        info.exif_datetime = _exif_datum(exif_ifd)

        gps = exif.get_ifd(_GPS_IFD)
        if gps:
            info.lat = _grad(
                gps.get(ExifTags.GPS.GPSLatitude), gps.get(ExifTags.GPS.GPSLatitudeRef)
            )
            info.lon = _grad(
                gps.get(ExifTags.GPS.GPSLongitude), gps.get(ExifTags.GPS.GPSLongitudeRef)
            )
            # Nur ein vollstaendiges Paar ist brauchbar.
            if info.lat is None or info.lon is None:
                info.lat = info.lon = None

        _iptc(bild, info)

    return info


def ist_scandatum(zeitpunkt: datetime | None, hoechstes_aufnahmejahr: int) -> bool:
    """Ob ein EXIF-Datum als Scandatum zu werten ist statt als Aufnahmedatum."""
    return zeitpunkt is not None and zeitpunkt.year > hoechstes_aufnahmejahr
