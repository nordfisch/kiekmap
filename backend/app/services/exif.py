"""Read metadata out of the image file.

The most important thing here is an omission: **the EXIF date of a scan is not adopted as the
capture date.**

For a scanned paper print, EXIF carries the date of the scan. Adopting it would place a photo from
1932 at 2019 on the timeline -- worse, it would count as dated and therefore never surface in the
"Hilf mit" panel where someone could have corrected it. A wrong date does more damage here than no
date at all.

Two things decide it, and the order matters -- see ``is_scan`` and ``is_scan_date``:

1. **The device.** A file that names ``HP Scanjet 3670`` is a scan and gets no date, whatever the
   year says. A file that names a camera was taken by that camera, and its date counts.
2. **The year**, for files that name no device at all: from ``exif_date_max_year`` onwards the
   date is treated as a scan date.

Either way the raw value stays in ``Photo.exif_datetime`` so the curator can see it.
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

_TAG_MAKE = 0x010F
_TAG_MODEL = 0x0110
_TAG_ARTIST = 0x013B
_TAG_COPYRIGHT = 0x8298

_IPTC_TITLE = (2, 5)
_IPTC_KEYWORDS = (2, 25)
_IPTC_BYLINE = (2, 80)
_IPTC_CREDIT = (2, 110)
_IPTC_SOURCE = (2, 115)
_IPTC_COPYRIGHT = (2, 116)
_IPTC_CAPTION = (2, 120)

#: Values that fill a field without saying anything -- and therefore count as empty.
#:
#: This is the same trap as the scan date, one field over: the value is there, so the photo counts
#: as titled (or credited) and never comes up for correction -- except that "OLYMPUS DIGITAL
#: CAMERA" says nothing about the picture and "unbekannt" says nothing about who took it. Nothing
#: is more honest than either, and it puts the photo back in front of somebody who knows.
#:
#: Two sources feed this list: what a camera writes by itself, and what a person types when the
#: form insists on an answer. "unbekannt" stands in 82 files of the Holm stock.
_NON_VALUES = frozenset(
    {
        "olympus digital camera",
        "sony dsc",
        "konica minolta digital camera",
        "samsung digital camera",
        "samsung camera pictures",
        "casio computer co.,ltd",
        "picasa",
        "unbekannt",
        "unknown",
        "default",
        "single",
        # A language marker out of XMP that ends up in the title when the text beside it is empty.
        "x-default",
    }
)

#: Words in the device name that mark a scanner rather than a camera.
#:
#: Deliberately a substring test on a lowercased name, and "scan" alone catches Scanjet, CanoScan
#: and CoolScan. The other two are makes that do not say it. That the *model* is read as well is
#: not a nicety: "DIGITAL CAMERA Film Scanner" calls itself a camera in the make field.
_SCANNER_WORDS = ("scan", "perfection", "mustek")


@dataclass
class ImageInfo:
    """What the file reveals about itself."""

    width: int
    height: int
    format: str

    title: str | None = None
    description: str | None = None
    keywords: list[str] = field(default_factory=list)

    lat: float | None = None
    lon: float | None = None

    #: Raw EXIF date. Whether it is the capture date is decided by the importer.
    exif_datetime: datetime | None = None

    #: Make and model in one line: "HP HP Scanjet 3670", "Panasonic DMC-GX8". Empty for a file
    #: that names no device -- and *that* is the case where the year limit has to decide alone.
    device: str | None = None

    #: Who is named beside the picture: photographer first, then whoever provided it.
    credit: str | None = None
    #: Where it came from -- IPTC Source, "Sammlung Jan Wendt". Never shown to visitors.
    source: str | None = None


def _decode(value: object, encodings: tuple[str, ...]) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        for encoding in encodings:
            try:
                value = value.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            return None
    text = _repair(str(value).replace("\x00", "").strip())
    return text or None


def _repair(text: str) -> str:
    """Undo a UTF-8 text that was once read as Latin-1: "MÃ¶ller" -> "Möller".

    It happens before the file ever reaches us -- a program writes UTF-8 bytes into an EXIF field
    that is specified as ASCII, and the next program reads them back byte by byte. Two files of
    the Holm stock carry it, and the wrong name would then stand under the photograph.

    Safe because German never spells "Ã" or "Â": without one of those nothing is attempted, and
    the round trip has to succeed or the original stands.
    """
    if not any(mark in text for mark in ("Ã", "Â")):
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _text(value: object) -> str | None:
    """Text from IPTC and from the ordinary EXIF fields: bytes, mostly UTF-8."""
    return _decode(value, ("utf-8", "latin-1"))


def _statement(value: object, decode=_text) -> str | None:
    """Text that is meant to say something -- a title, a caption, a name.

    Drops what nobody actually stated; see ``_NON_VALUES``.
    """
    text = decode(value)
    if text is None or text.strip().lower() in _NON_VALUES:
        return None
    return text


def _first(*values: object) -> str | None:
    """The first of several fields that holds a real statement."""
    for value in values:
        if text := _statement(value):
            return text
    return None


def _xp_text(value: object) -> str | None:
    """Only for the ``XP*`` EXIF fields -- and only for those, which is the whole point.

    Windows stores ``XPTitle`` and ``XPKeywords`` as UCS2 little-endian, so UTF-16 has to be tried
    first there. Trying it first *everywhere* is what went wrong before: **every** byte string of
    even length is valid UTF-16, so nothing ever raises and the fallback never happens. IPTC
    keywords came out as ``b"ArchivHolm"`` -> "牁档癩潈浬" -- and only the ones of even length,
    which is why it looked like random corruption rather than a rule.
    """
    return _decode(value, ("utf-16-le", "utf-8", "latin-1"))


def _degrees(value: object, reference: object) -> float | None:
    """GPS is stored as (degrees, minutes, seconds) in EXIF."""
    try:
        degrees, minutes, seconds = (float(part) for part in value)  # type: ignore[misc]
    except (TypeError, ValueError):
        return None

    decimal = degrees + minutes / 60 + seconds / 3600
    if str(reference).upper() in ("S", "W"):
        decimal = -decimal
    return round(decimal, 7)


def _exif_datetime(exif_ifd: dict) -> datetime | None:
    for tag in (ExifTags.Base.DateTimeOriginal, ExifTags.Base.DateTimeDigitized):
        raw = _text(exif_ifd.get(tag))
        if not raw:
            continue
        for pattern in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d"):
            try:
                return datetime.strptime(raw, pattern)
            except ValueError:
                continue
    return None


def _read_iptc(image: Image.Image) -> dict:
    """The IPTC block, or an empty dict. Broken IPTC must not stop the import."""
    try:
        return IptcImagePlugin.getiptcinfo(image) or {}
    except Exception:  # noqa: BLE001
        return {}


def open_image(path: Path) -> Image.Image:
    """Open an image file for reading, with one Pillow trap defused.

    **A TIFF may keep its XMP packet in a numeric tag, and Pillow then hands it back as a tuple of
    integers.** Any later ``getexif()`` runs a regular expression over that value and raises
    ``TypeError`` -- which ``import_file`` does not catch, because it is prepared for ``OSError``
    and ``ValueError``. A single such file would therefore end the whole import run instead of
    being rejected on its own, and TIFF is an allowed format. 25 of the Holm scans are like this.

    Every reader has to pass through here, not just this module: ``ImageOps.exif_transpose`` in
    ``thumbnails`` walks into the same trap, one step further along.
    """
    image = Image.open(path)
    if not isinstance(image.info.get("xmp"), str | bytes):
        image.info.pop("xmp", None)
    return image


def read_image_info(path: Path) -> ImageInfo:
    """Open the file and read what it says about itself.

    Raises ``OSError``/``UnidentifiedImageError`` if it is not a readable image -- the importer
    turns that into an entry in the import log.
    """
    with open_image(path) as image:
        # A portrait scan carries its orientation in EXIF rather than in the pixels. For display
        # and thumbnails the dimensions after that rotation are what count.
        rotated = image.size
        orientation = image.getexif().get(ExifTags.Base.Orientation)
        if orientation in (5, 6, 7, 8):
            rotated = (image.size[1], image.size[0])

        info = ImageInfo(width=rotated[0], height=rotated[1], format=image.format or "")

        exif = image.getexif()
        iptc = _read_iptc(image)

        info.title = _first(
            _xp_text(exif.get(_TAG_XP_TITLE)),
            exif.get(_TAG_IMAGE_DESCRIPTION),
            iptc.get(_IPTC_TITLE),
        )
        info.description = _statement(iptc.get(_IPTC_CAPTION))

        if words := _xp_text(exif.get(_TAG_XP_KEYWORDS)):
            info.keywords.extend(w.strip() for w in words.split(";") if w.strip())
        raw = iptc.get(_IPTC_KEYWORDS)
        for entry in raw if isinstance(raw, list) else [raw] if raw else []:
            if word := _text(entry):
                info.keywords.append(word)

        # Make and model together: the make alone lies ("DIGITAL CAMERA" for a film scanner), the
        # model alone is often just a number.
        info.device = (
            " ".join(
                part for part in (_text(exif.get(_TAG_MAKE)), _text(exif.get(_TAG_MODEL))) if part
            )
            or None
        )

        # Sorted by what the field *means*, not by which block it sits in: first whoever took the
        # picture, then whoever supplied it, then whoever holds the rights. A credit line beside a
        # photo names the photographer if anybody knows one, and the institution only when nobody
        # does -- and both blocks can carry either.
        info.credit = _first(
            iptc.get(_IPTC_BYLINE),
            exif.get(_TAG_ARTIST),
            iptc.get(_IPTC_CREDIT),
            iptc.get(_IPTC_COPYRIGHT),
            exif.get(_TAG_COPYRIGHT),
        )
        info.source = _statement(iptc.get(_IPTC_SOURCE))

        exif_ifd = exif.get_ifd(_EXIF_IFD)
        info.exif_datetime = _exif_datetime(exif_ifd)

        gps = exif.get_ifd(_GPS_IFD)
        if gps:
            info.lat = _degrees(
                gps.get(ExifTags.GPS.GPSLatitude), gps.get(ExifTags.GPS.GPSLatitudeRef)
            )
            info.lon = _degrees(
                gps.get(ExifTags.GPS.GPSLongitude), gps.get(ExifTags.GPS.GPSLongitudeRef)
            )
            # Only a complete pair is usable.
            if info.lat is None or info.lon is None:
                info.lat = info.lon = None

    return info


def is_scan(info: ImageInfo) -> bool:
    """Whether the device that wrote this file is a scanner."""
    return info.device is not None and any(word in info.device.lower() for word in _SCANNER_WORDS)


def is_scan_date(moment: datetime | None, max_capture_year: int) -> bool:
    """Whether an EXIF date should count as a scan date rather than a capture date."""
    return moment is not None and moment.year > max_capture_year


def capture_year(info: ImageInfo, max_capture_year: int) -> datetime | None:
    """The EXIF date, but only where it plausibly dates the *picture*.

    Three cases, and the middle one is the reason this function exists:

    * **A scanner wrote the file** -- no date. The date belongs to the scanning run, not to the
      photograph. 116 files of the Holm stock fall here, 91 of them from a single run in 2015.
    * **A camera wrote the file** -- the date counts, *even past* ``max_capture_year``. The year
      limit is a stand-in for "this is probably a scan"; where the file names the device, the
      stand-in is not needed and would only throw away what we know. Without this the recent
      photographs of the village -- taken with an Olympus in 2014, a Panasonic in 2018 -- would
      all arrive undated.
    * **No device at all** -- the year limit decides alone, as it always did.
    """
    moment = info.exif_datetime
    if moment is None or is_scan(info):
        return None
    if info.device is None and is_scan_date(moment, max_capture_year):
        return None
    return moment
