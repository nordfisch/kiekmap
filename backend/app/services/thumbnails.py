"""Thumbnails.

Two sizes, both created at import time: 240 px for the markers on the map, 1200 px for the overlay
and the contribution panel. Computing them at display time would be noticeable on a Pi; at import
time nobody notices.

WebP, because at equal quality it is considerably smaller than JPEG -- and the map easily loads
fifty markers at once.
"""

import logging
import math
from pathlib import Path

from PIL import Image, ImageOps

from app.services.exif import open_image
from app.services.storage import THUMBNAIL_SIZES, thumbnail_path

log = logging.getLogger(__name__)

_QUALITY = 82
_REDUCING_GAP = 2


def _for_display(image: Image.Image) -> Image.Image:
    """Rotate per EXIF and convert into a colour space WebP knows.

    Scanned originals often arrive as CMYK TIFF or with a greyscale palette. Without conversion
    saving fails -- and only at the very last step, after all the resizing work.
    """
    image = ImageOps.exif_transpose(image) or image
    if image.mode in ("RGBA", "LA"):
        return image.convert("RGBA")
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def _decode_reduced(image: Image.Image, longest: int) -> Image.Image:
    """Decode no more pixels than the largest thumbnail needs.

    A thumbnail does not need the full scan, and decoding it in full costs 3 bytes per pixel for
    RGB before the first copy. A JPEG decodes at 1/2, 1/4 or 1/8 of its size when asked before
    loading (``draft``). Other formats decode in full, and ``reduce`` shrinks the result before
    rotation, conversion and the copy per size each duplicate it.

    Both stop at twice the thumbnail's long side. That is the ``reducing_gap`` Pillow's own
    ``thumbnail`` uses: the reduction by whole factors is coarse, and Lanczos over the last factor
    of two keeps the thumbnail as sharp as one made from the full scan.
    """
    needed = longest * _REDUCING_GAP
    if max(image.size) // needed < 2:
        return image

    ratio = needed / max(image.size)
    image.draft(None, (math.ceil(image.width * ratio), math.ceil(image.height * ratio)))

    factor = max(image.size) // needed
    return image.reduce(factor) if factor >= 2 else image


def create_thumbnails(source: Path, target_root: Path, sha256: str) -> list[Path]:
    """Create every size and return the paths written."""
    written: list[Path] = []

    with open_image(source) as raw:
        display = _for_display(_decode_reduced(raw, max(THUMBNAIL_SIZES)))

    for size in THUMBNAIL_SIZES:
        target = thumbnail_path(target_root, sha256, size)
        target.parent.mkdir(parents=True, exist_ok=True)

        scaled = display.copy()
        scaled.thumbnail((size, size), Image.Resampling.LANCZOS)
        scaled.save(target, "WEBP", quality=_QUALITY, method=6)
        written.append(target)

    return written


def remove_thumbnails(target_root: Path, sha256: str) -> None:
    for size in THUMBNAIL_SIZES:
        thumbnail_path(target_root, sha256, size).unlink(missing_ok=True)
