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
#:
#: MPO is a JPEG carrying several frames -- some cameras write it for a burst or a 3D shot, and 28
#: files of the Holm stock are one. Its first frame is an ordinary JPEG, which is what every
#: browser shows and what the thumbnail is made from, so it is taken in as one. Rejecting it would
#: have lost 28 photographs to a container format nobody chose.
ALLOWED_FORMATS = {
    "JPEG": ("image/jpeg", ".jpg"),
    "MPO": ("image/jpeg", ".jpg"),
    "PNG": ("image/png", ".png"),
    "TIFF": ("image/tiff", ".tif"),
    "WEBP": ("image/webp", ".webp"),
}


#: The other direction of ``ALLOWED_FORMATS``: from what a row says it is to what its file is
#: called. Derived rather than written out, so the two cannot drift apart.
#:
#: Two formats share a MIME type -- JPEG and MPO are both ``image/jpeg`` and both ``.jpg``, which
#: is what makes this reversal well defined in the first place.
_SUFFIX_BY_MIME = {mime: suffix for mime, suffix in ALLOWED_FORMATS.values()}


def suffix_for_mime(mime: str) -> str | None:
    """The file ending belonging to a stored MIME type, or None for one we never wrote.

    Its own function because three callers need it and each of them used to answer it for itself.
    One of the three answered it by arithmetic on the string -- ``mime.split("/")[-1]`` with
    ``jpeg`` and ``tiff`` patched back by hand -- which happened to agree with the table and would
    have stopped agreeing the moment a format arrived whose ending is not the tail of its MIME
    type. A rule that lives in two places is a rule that will disagree with itself.
    """
    return _SUFFIX_BY_MIME.get(mime)


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
