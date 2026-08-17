"""Finding the same picture twice.

The SHA-256 of a file recognizes a copy of the file. It does **not** recognize the same
photograph scanned twice, or the same scan saved once large and once small -- and that is what a
grown archive is full of. 1324 photographs of the Holm stock held 44 such groups.

**A difference hash over the thumbnails.** Each 240 px preview is reduced to 17x16 greyscale
pixels; every pixel is compared with its right-hand neighbour, which gives 256 bits. Two pictures
are close when few of those bits differ. The hash survives brightness, contrast, colour cast and
scaling -- exactly what separates two runs of the same paper print -- and it costs nothing: the
thumbnails already exist, and 876 000 comparisons are one XOR each.

**It finds candidates, not verdicts**, and the threshold says so. Sixty pairs of the Holm stock
were looked at by eye: up to a distance of 12 it is beyond doubt the same picture, up to 30 almost
always, and even at 37 to 40 most pairs still are. The signal does not stop, it blurs -- so the
default is generous and a person decides. What the hash cannot do is see a caption burnt into the
smaller copy, or a lorry parked in one of two otherwise identical street views; both happened.
"""

from pathlib import Path

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Photo, PhotoStatus
from app.services.storage import THUMBNAIL_SIZES, thumbnail_path

#: Bits that may differ, out of 256. Measured by eye -- see the module docstring.
DEFAULT_DISTANCE = 40

_WIDTH, _HEIGHT = 17, 16


def fingerprint(path: Path) -> int:
    """The 256-bit difference hash of one image."""
    with Image.open(path) as image:
        small = image.convert("L").resize((_WIDTH, _HEIGHT), Image.Resampling.LANCZOS)
        # tobytes rather than getdata: one byte per pixel in "L" mode, and it outlives Pillow 14.
        pixels = small.tobytes()

    bits = 0
    for row in range(_HEIGHT):
        base = row * _WIDTH
        for column in range(_WIDTH - 1):
            bits = (bits << 1) | (pixels[base + column] > pixels[base + column + 1])
    return bits


def distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def candidate_groups(
    session: Session, settings: Settings, limit: int = DEFAULT_DISTANCE
) -> list[list[Photo]]:
    """Photographs that appear more than once, grouped.

    Grouped transitively: a photograph belongs to the group when it is close enough to **any**
    member, not to all of them. A large scan, a small copy and a copy of the copy form one chain,
    and the two ends of it can be further apart than the threshold.

    Each group comes back sorted by pixel count, largest first -- the usual, though not always
    right, candidate to keep.
    """
    photos = list(session.scalars(select(Photo).where(Photo.status == PhotoStatus.PUBLISHED)).all())
    marks: list[tuple[Photo, int]] = []
    for photo in photos:
        path = thumbnail_path(settings.thumbs_dir, photo.sha256, min(THUMBNAIL_SIZES))
        if path.exists():
            marks.append((photo, fingerprint(path)))

    parent: dict[int, int] = {}

    def root(item: int) -> int:
        while parent.get(item, item) != item:
            item = parent[item]
        return item

    for index, (left, left_mark) in enumerate(marks):
        for right, right_mark in marks[index + 1 :]:
            if distance(left_mark, right_mark) <= limit:
                a, b = root(left.id), root(right.id)
                if a != b:
                    parent[a] = b

    by_root: dict[int, list[Photo]] = {}
    for photo, _ in marks:
        by_root.setdefault(root(photo.id), []).append(photo)

    groups = [group for group in by_root.values() if len(group) > 1]
    for group in groups:
        group.sort(key=lambda photo: -(photo.width * photo.height))
    return sorted(groups, key=lambda group: -(group[0].width * group[0].height))
