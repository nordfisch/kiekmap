"""File storage.

Images are named after the SHA-256 of their content. That solves four things at once: no name
collisions, duplicate detection for free, arbitrarily cacheable delivery, and -- because an equal
name guarantees equal content -- an incremental backup that only copies new images on the second
run. See docs/decisions.md, point 3.
"""

import hashlib
from pathlib import Path

#: Sizes of the pre-rendered thumbnails in pixels (longer edge).
THUMBNAIL_SIZES = (240, 1200)

#: What may be imported. Anything else is rejected with a reason rather than silently ignored.
ALLOWED_FORMATS = {
    "JPEG": ("image/jpeg", ".jpg"),
    "PNG": ("image/png", ".png"),
    "TIFF": ("image/tiff", ".tif"),
    "WEBP": ("image/webp", ".webp"),
}


def sha256_of_file(path: Path, block_size: int = 1024 * 1024) -> str:
    """Chunked, so that even a 200 MB TIFF never has to fit into memory."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            hasher.update(block)
    return hasher.hexdigest()


def _fanned_out(sha256: str) -> Path:
    """``a3f29c…`` becomes ``a3/f2/``.

    Irrelevant at a few thousand files, but the difference between a directory that opens and one
    that does not once the collection grows.
    """
    return Path(sha256[0:2]) / sha256[2:4]


def original_path(root: Path, sha256: str, suffix: str) -> Path:
    return root / _fanned_out(sha256) / f"{sha256}{suffix}"


def thumbnail_path(root: Path, sha256: str, size: int) -> Path:
    return root / str(size) / _fanned_out(sha256) / f"{sha256}.webp"
