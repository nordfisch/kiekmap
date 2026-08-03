"""Read metadata out of the image file.

The most important thing here is an omission: **the EXIF date of a scan is not adopted as the
capture date.**

For a scanned paper print, EXIF carries the date of the scan. Adopting it would place a photo from
1932 at 2019 on the timeline -- worse, it would count as dated and therefore never surface in the
"Hilf mit" panel where someone could have corrected it. A wrong date does more damage here than no
date at all.

Hence: EXIF dates from ``exif_date_max_year`` onwards count as scan dates. They are kept in
``Photo.exif_datetime`` so the curator can see them, but they do not date the photo.
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

#: What cameras write into the title and caption fields when nobody wrote anything.
#:
#: This is the same trap as the scan date, one field over: the value is there, so the photo counts
#: as titled and never comes up for correction -- except that "OLYMPUS DIGITAL CAMERA" says
#: nothing about the picture. No title is more honest than that one, and it puts the photo back in
#: front of somebody who can supply a real one.
_CAMERA_BOILERPLATE = frozenset(
    {
        "olympus digital camera",
        "sony dsc",
        "konica minolta digital camera",
        "samsung digital camera",
        "samsung camera pictures",
        "casio computer co.,ltd",
        "picasa",
    }
)


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
    text = str(value).replace("\x00", "").strip()
    return text or None


def _text(value: object) -> str | None:
    """Text from IPTC and from the ordinary EXIF fields: bytes, mostly UTF-8."""
    return _decode(value, ("utf-8", "latin-1"))


def _statement(value: object, decode=_text) -> str | None:
    """Text that is meant to say something about the picture -- title or caption.

    Drops what the camera put there by itself; see ``_CAMERA_BOILERPLATE``.
    """
    text = decode(value)
    if text is None or text.strip().lower() in _CAMERA_BOILERPLATE:
        return None
    return text


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


def _read_iptc(image: Image.Image, info: ImageInfo) -> None:
    try:
        data = IptcImagePlugin.getiptcinfo(image)
    except Exception:  # noqa: BLE001 -- broken IPTC must not stop the import
        return
    if not data:
        return

    if title := _statement(data.get(_IPTC_TITLE)):
        info.title = info.title or title
    if caption := _statement(data.get(_IPTC_CAPTION)):
        info.description = info.description or caption

    raw = data.get(_IPTC_KEYWORDS)
    for entry in raw if isinstance(raw, list) else [raw] if raw else []:
        if word := _text(entry):
            info.keywords.append(word)


def read_image_info(path: Path) -> ImageInfo:
    """Open the file and read what it says about itself.

    Raises ``OSError``/``UnidentifiedImageError`` if it is not a readable image -- the importer
    turns that into an entry in the import log.
    """
    with Image.open(path) as image:
        # A portrait scan carries its orientation in EXIF rather than in the pixels. For display
        # and thumbnails the dimensions after that rotation are what count.
        rotated = image.size
        orientation = image.getexif().get(ExifTags.Base.Orientation)
        if orientation in (5, 6, 7, 8):
            rotated = (image.size[1], image.size[0])

        info = ImageInfo(width=rotated[0], height=rotated[1], format=image.format or "")

        exif = image.getexif()
        info.title = _statement(exif.get(_TAG_XP_TITLE), _xp_text) or _statement(
            exif.get(_TAG_IMAGE_DESCRIPTION)
        )
        if words := _xp_text(exif.get(_TAG_XP_KEYWORDS)):
            info.keywords.extend(w.strip() for w in words.split(";") if w.strip())

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

        _read_iptc(image, info)

    return info


def is_scan_date(moment: datetime | None, max_capture_year: int) -> bool:
    """Whether an EXIF date should count as a scan date rather than a capture date."""
    return moment is not None and moment.year > max_capture_year
