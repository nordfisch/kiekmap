"""Finding the same image twice -- ``services/similar.py``.

The SHA-256 recognises a copy of the *file*. It does not recognise the same paper print scanned
twice, nor the same scan stored once large and once small. A collection that has grown over decades
is full of exactly that: 1,324 photos of the Holm stock held 44 such groups.

The fingerprint is therefore allowed to be **imprecise** -- it has to survive brightness, a colour
cast and downscaling. What it must not do is throw two different images together.
"""

import pytest
from PIL import Image, ImageEnhance

from app.models import Photo, PhotoStatus
from app.services.similar import candidate_groups, distance, fingerprint
from app.services.storage import THUMBNAIL_SIZES, thumbnail_path


@pytest.fixture
def house(tmp_path):
    """An image with structure -- a plain surface has no fingerprint."""
    image = Image.new("RGB", (400, 300), (200, 205, 215))
    for x in range(60, 340):
        for y in range(120, 260):
            image.putpixel((x, y), (150 - (x % 40), 90, 70))
    for x in range(100, 300, 60):
        for y in range(150, 200):
            for dx in range(30):
                image.putpixel((x + dx, y), (250, 250, 230))
    path = tmp_path / "house.png"
    image.save(path)
    return path


class TestFingerprint:
    def test_the_same_file_gives_the_same_fingerprint(self, house):
        assert fingerprint(house) == fingerprint(house)

    def test_the_small_copy_stays_close(self, house, tmp_path):
        """The most frequent case in the collection: one scan, stored once large and once small."""
        small = tmp_path / "small.png"
        Image.open(house).resize((160, 120), Image.Resampling.LANCZOS).save(small)

        assert distance(fingerprint(house), fingerprint(small)) <= 40

    def test_brighter_and_colour_shifted_stays_close(self, house, tmp_path):
        """Two runs over the same paper print differ in exactly this way."""
        changed = tmp_path / "changed.png"
        image = ImageEnhance.Brightness(Image.open(house)).enhance(1.4)
        ImageEnhance.Color(image).enhance(0.2).save(changed)

        assert distance(fingerprint(house), fingerprint(changed)) <= 40

    def test_a_different_image_stays_far(self, house, tmp_path):
        """The counter-check. Without it a fingerprint saying the same thing always would pass."""
        other = tmp_path / "other.png"
        image = Image.new("RGB", (400, 300), (240, 240, 235))
        for x in range(400):
            for y in range(x % 7, 300, 11):
                image.putpixel((x, y), (30, 80, 40))
        image.save(other)

        assert distance(fingerprint(house), fingerprint(other)) > 40


class TestGroups:
    def _photo(self, session, settings, house, transform=lambda image: image) -> Photo:
        from app.services.storage import sha256_of_file

        number = len(session.query(Photo).all()) + 1
        image = transform(Image.open(house).convert("RGB"))
        photo = Photo(
            sha256=f"{number:064x}",
            original_filename=f"{number}.jpg",
            mime="image/jpeg",
            bytes=1,
            width=image.width,
            height=image.height,
            date_precision="unknown",
            status=PhotoStatus.PUBLISHED,
        )
        session.add(photo)
        session.flush()
        target = thumbnail_path(settings.thumbs_dir, photo.sha256, min(THUMBNAIL_SIZES))
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, "WEBP")
        assert sha256_of_file(target)
        return photo

    def test_both_photos_are_in_the_group(self, session, settings, house):
        """The error this line has had once already.

        When grouping through a union-find structure, one photo is the root of its group. Whoever
        collects only the non-roots loses one photo from **every** group -- and a pair thereby
        shrinks to one and drops out of the report. On the collection that looked like "no
        duplicates found".
        """
        large = self._photo(session, settings, house)
        small = self._photo(
            session, settings, house, lambda i: i.resize((160, 120), Image.Resampling.LANCZOS)
        )
        session.commit()

        groups = candidate_groups(session, settings)

        assert len(groups) == 1
        assert {photo.id for photo in groups[0]} == {large.id, small.id}

    def test_the_largest_comes_first(self, session, settings, house):
        self._photo(session, settings, house, lambda i: i.resize((160, 120)))
        large = self._photo(session, settings, house)
        session.commit()

        assert candidate_groups(session, settings)[0][0].id == large.id

    def test_a_withdrawn_photo_does_not_come_up_again(self, session, settings, house):
        """Otherwise the command would offer the same duplicate again on its next run."""
        self._photo(session, settings, house)
        withdrawn = self._photo(session, settings, house, lambda i: i.resize((160, 120)))
        withdrawn.status = PhotoStatus.DELETED
        session.commit()

        assert candidate_groups(session, settings) == []
