"""Converting the archive to JPEG -- ``tools/to_jpeg.py``.

The promise everything hangs on: **the same file gives the same SHA-256 twice.** The import
recognises a duplicate by the hash of the file. Whoever adjusts the quality here gets different
bytes out of the same scan -- and with the next archive delivery every image already present would
come in a second time without anyone noticing. That is not a blemish but the most expensive silent
error this tool can have.

The tool lives outside the backend, because it runs before the import, on the archive folder.
Hence the path entry -- the only test that needs it.
"""

import hashlib
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import to_jpeg as tool  # noqa: E402

from app.services.exif import read_image_info  # noqa: E402


@pytest.fixture
def scan(tmp_path: Path) -> Path:
    """A TIFF full of fine structure -- the most awkward case, on purpose.

    A photograph compresses at quality 92 to roughly a third of a byte per pixel; this one needs
    more than a whole one. That is exactly what the conversion fails on without the larger
    ``MAXBLOCK`` -- see ``to_jpeg``.
    """
    image = Image.new("RGB", (400, 300))
    for x in range(400):
        for y in range(0, 300, 3):
            image.putpixel((x, y), (x % 256, (x * y) % 256, y % 256))
    path = tmp_path / "Scan.TIF"
    image.save(path, "TIFF")
    return path


def _converted(scan: Path, name: str) -> bytes:
    target = scan.parent / name
    tool.to_jpeg(scan, target)
    return target.read_bytes()


def test_converting_twice_gives_the_same_hash(scan: Path) -> None:
    """Otherwise the same photo would come in again with the next archive delivery."""
    first = hashlib.sha256(_converted(scan, "first.jpg")).hexdigest()
    second = hashlib.sha256(_converted(scan, "second.jpg")).hexdigest()
    assert first == second


def test_a_different_quality_gives_different_bytes(scan: Path, monkeypatch) -> None:
    """The counter-check to the test above: the hash really does hang on the setting.

    Without it the promise could also be kept by a tool that ignores every setting -- and the
    promise would be worth nothing.
    """
    before = _converted(scan, "before.jpg")
    monkeypatch.setattr(tool, "JPEG_OPTIONS", {"quality": 90, "subsampling": 0, "optimize": True})
    assert _converted(scan, "after.jpg") != before


def test_a_small_image_full_of_detail_does_not_abort(scan: Path) -> None:
    """Pillow guesses the buffer from the image size and is wrong for images like this.

    The abort reads "broken data stream when writing image file" and would hit exactly the
    originals an archive sends along on the side -- maps, newspaper cuttings, screenshots.
    """
    target = scan.parent / "tight.jpg"
    tool.to_jpeg(scan, target)
    assert Image.open(target).size == (400, 300)


def test_the_measured_setting_is_fixed() -> None:
    """Quality 92, 4:4:4, optimize -- measured against the initial collection, not chosen.

    See the docstring of ``tools/to_jpeg.py``: four out of 19 files come out bit-identical this
    way, eighteen pixel-identical. With quality 90 not a single one.
    """
    assert tool.JPEG_OPTIONS == {"quality": 92, "subsampling": 0, "optimize": True}


def test_a_transparent_png_gets_a_white_background(tmp_path: Path) -> None:
    """JPEG knows no transparency, and a scan lies on paper, not in nothing.

    On a black background the transparent edge of a cut-out scan would become a mourning border.
    """
    image = Image.new("RGBA", (20, 20), (255, 0, 0, 0))
    path = tmp_path / "cutout.png"
    image.save(path)

    tool.to_jpeg(path, tmp_path / "cutout.jpg")
    assert Image.open(tmp_path / "cutout.jpg").convert("RGB").getpixel((10, 10)) == (255, 255, 255)


def test_the_tree_is_copied_and_the_source_is_left_alone(tmp_path: Path) -> None:
    """What the museum sent stays as it was sent."""
    source = tmp_path / "Archiv" / "Hauptstraße" / "14 Museum"
    source.mkdir(parents=True)
    Image.new("RGB", (10, 10)).save(source / "scan.tif")
    Image.new("RGB", (10, 10)).save(source / "foto.jpg")
    (source / "Notiz.txt").write_text("not an image file")
    before = sorted(path.name for path in source.iterdir())

    target = tmp_path / "Kopie"
    counted = tool.build(tmp_path / "Archiv", target)

    assert counted["umgewandelt"] == 1
    assert counted["kopiert"] == 1
    assert counted["uebergangen"] == 1
    assert (target / "Hauptstraße" / "14 Museum" / "scan.jpg").exists()
    assert (target / "Hauptstraße" / "14 Museum" / "foto.jpg").exists()
    assert not (target / "Hauptstraße" / "14 Museum" / "Notiz.txt").exists()
    assert sorted(path.name for path in source.iterdir()) == before


def test_the_target_must_not_lie_inside_the_source(tmp_path: Path) -> None:
    """Otherwise the conversion runs over its own output -- and does so endlessly."""
    (tmp_path / "Archiv").mkdir()
    assert tool.main([str(tmp_path / "Archiv"), str(tmp_path / "Archiv" / "Kopie")]) == 1


class TestMetadataComesAlong:
    """What the source file says about itself, the copy has to say too.

    Measured with the reader of the import, not with one of its own: the question is not whether
    the bytes came along, but whether the program sees the same thing afterwards.

    **It was once not so.** The conversion passed through only the colour profile and the
    resolution; twelve photos of the newer archive delivery lost their photographer ("A. Brahms"),
    a caption and a date -- and afterwards carried the collection's default credit, which is worse
    than none: a wrong attribution looks like an answer.
    """

    def _tiff_with_iptc(self, path: Path, fields: dict[tuple[int, int], bytes]) -> None:
        """A TIFF the way the archive delivers it: IPTC raw in tag 33723.

        Assembled by hand and not produced with the code this test checks -- otherwise it would be
        checking itself. The format is IPTC-IIM: per field one 0x1C, record, dataset, two bytes of
        length, content.

        **Tag 33723 and not the Photoshop block:** in a TIFF, Pillow reads the IPTC only from
        there, and does so straight from the raw bytes, past its own mangled value. In the JPEG the
        same content then stands in ``APP13``, behind the marker "Photoshop 3.0" -- two places for
        the same thing, and the conversion leads from one into the other.
        """
        from PIL import TiffImagePlugin

        records = b"".join(
            bytes((0x1C, record, dataset)) + len(value).to_bytes(2, "big") + value
            for (record, dataset), value in sorted(fields.items())
        )
        directory = TiffImagePlugin.ImageFileDirectory_v2()
        directory[33723] = records
        directory.tagtype[33723] = 1  # BYTE
        Image.new("RGB", (40, 30), (200, 180, 160)).save(path, "TIFF", tiffinfo=directory)

    def test_photographer_and_caption_survive(self, tmp_path: Path) -> None:
        source = tmp_path / "scan.tif"
        self._tiff_with_iptc(
            source,
            {
                (2, 80): b"A. Brahms",  # By-line, the photographer
                (2, 120): b"Collage aus der Niederstrasse",  # Caption
            },
        )

        target = tmp_path / "scan.jpg"
        tool.to_jpeg(source, target)

        found = read_image_info(target)
        assert found.credit == "A. Brahms"
        assert found.description == "Collage aus der Niederstrasse"

    def test_the_coordinate_survives(self, tmp_path: Path) -> None:
        """A file of the new archive delivery carries GPS -- and lost it in the conversion."""
        exif = Image.Exif()
        exif[0x8825] = {
            1: "N",
            2: (53.0, 37.0, 9.0),
            3: "E",
            4: (9.0, 40.0, 28.0),
        }
        source = tmp_path / "foto.png"
        Image.new("RGB", (40, 30)).save(source, "PNG", exif=exif.tobytes())

        target = tmp_path / "foto.jpg"
        tool.to_jpeg(source, target)

        found = read_image_info(target)
        assert found.lat is not None and found.lon is not None
        assert abs(found.lat - 53.6191) < 0.001
        assert abs(found.lon - 9.6744) < 0.001

    def test_two_runs_stay_equal_with_metadata_too(self, tmp_path: Path) -> None:
        """The promise from point 46 still holds -- metadata blocks must not wobble."""
        source = tmp_path / "scan.tif"
        self._tiff_with_iptc(source, {(2, 80): b"A. Brahms", (2, 25): b"Gebaeude"})

        first, second = tmp_path / "a.jpg", tmp_path / "b.jpg"
        tool.to_jpeg(source, first)
        tool.to_jpeg(source, second)

        assert hashlib.sha256(first.read_bytes()).hexdigest() == (
            hashlib.sha256(second.read_bytes()).hexdigest()
        )
