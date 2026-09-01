"""Builds the test images in this directory.

Call: ``python tests/fixtures/build_test_images.py``

The images deliberately cover the cases where an import fails or -- worse -- silently does
something wrong:

    scan_ohne_exif.jpg      the normal case: a scan without any entry at all
    scan_mit_scandatum.jpg  EXIF date of 2019, although the photo is historic
    scan_vom_scanner.jpg    the same, but the device names itself: "HP Scanjet 3670"
    kamerafoto.jpg          camera and a date of 2014 -- a genuine capture date
    foto_mit_gps.jpg        a genuine digital photo with coordinates and a capture date
    hochkant.jpg            the orientation stands in the EXIF, not in the pixels
    graustufen.tif          TIFF without colour, the way book scanners deliver it
    cmyk.tif                CMYK -- WebP does not know this colour space
    not_an_image.txt           a text file with an image suffix
"""

import io
from pathlib import Path

import piexif
from PIL import Image, ImageDraw

HERE = Path(__file__).parent


def _image(width: int, height: int, text: str, colour: str = "#c8bfae") -> Image.Image:
    image = Image.new("RGB", (width, height), colour)
    draw = ImageDraw.Draw(image)
    draw.rectangle([8, 8, width - 8, height - 8], outline="#3a3128", width=3)
    draw.text((20, height // 2), text, fill="#3a3128")
    return image


def _with_exif(image: Image.Image, target: Path, exif_dict: dict) -> None:
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=90)
    piexif.insert(piexif.dump(exif_dict), buffer.getvalue(), str(target))


def _degrees_to_dms(degrees: float) -> tuple:
    degrees = abs(degrees)
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = round((degrees - d - m / 60) * 3600, 4)
    return ((d, 1), (m, 1), (int(s * 10000), 10000))


def main() -> None:
    # 1. The normal case: a scanned paper print, no metadata whatsoever.
    _image(900, 640, "Scan ohne EXIF").save(HERE / "scan_ohne_exif.jpg", "JPEG", quality=90)

    # 2. The dangerous case: the EXIF carries the date of the scanning run. If it were adopted, a
    #    photo from 1932 would sit at 2019 on the timeline -- and would never be asked about.
    _with_exif(
        _image(900, 640, "Scan, EXIF = Scandatum 2019"),
        HERE / "scan_mit_scandatum.jpg",
        {
            "0th": {piexif.ImageIFD.ImageDescription: b"Kirchweih an der Muehle"},
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2019:03:14 11:22:33"},
        },
    )

    # 2b. The same case, but the file says what it was made with. The device name then decides
    #     instead of the year boundary -- and "unbekannt" as a photographer is no credit.
    _with_exif(
        _image(900, 640, "Scan vom Flachbettscanner, 2015"),
        HERE / "scan_vom_scanner.jpg",
        {
            "0th": {
                piexif.ImageIFD.Make: b"HP",
                piexif.ImageIFD.Model: b"HP Scanjet 3670",
                piexif.ImageIFD.Artist: b"unbekannt",
            },
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2015:04:02 09:15:00"},
        },
    )

    # 2c. The other direction: a camera. Its date is a capture date even when it lies far beyond
    #     exif_date_max_year -- the year boundary is only the stand-in for a device entry.
    _with_exif(
        _image(900, 640, "Kamerafoto 2014", colour="#b6c8b0"),
        HERE / "kamerafoto.jpg",
        {
            "0th": {
                piexif.ImageIFD.Make: b"OLYMPUS IMAGING CORP.",
                piexif.ImageIFD.Model: b"E-500",
                piexif.ImageIFD.Artist: "August Kroeger".encode("latin-1"),
            },
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2014:03:09 16:41:20"},
        },
    )

    # 3. A genuine digital photo: date and place may be adopted. Coordinates in Holm.
    _with_exif(
        _image(900, 640, "Digitalfoto mit GPS", colour="#b6c8b0"),
        HERE / "foto_mit_gps.jpg",
        {
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"1975:06:21 14:05:00"},
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: b"N",
                piexif.GPSIFD.GPSLatitude: _degrees_to_dms(53.62053),
                piexif.GPSIFD.GPSLongitudeRef: b"E",
                piexif.GPSIFD.GPSLongitude: _degrees_to_dms(9.67601),
            },
        },
    )

    # 4. Scanned in portrait: the pixels are landscape, the orientation stands in the EXIF.
    #    Ignored, the thumbnail and the stored dimensions end up the wrong way round.
    _with_exif(
        _image(900, 600, "hochkant (Orientation 6)"),
        HERE / "hochkant.jpg",
        {"0th": {piexif.ImageIFD.Orientation: 6}},
    )

    # 5. A greyscale TIFF, the way book scanners deliver it.
    _image(800, 600, "Graustufen").convert("L").save(HERE / "graustufen.tif", "TIFF")

    # 6. CMYK -- WebP cannot store this colour space.
    _image(800, 600, "CMYK").convert("CMYK").save(HERE / "cmyk.tif", "TIFF")

    # 7. Not an image file, despite the suffix.
    (HERE / "not_an_image.txt").write_text("This is not an image.\n", encoding="utf-8")

    for path in sorted(HERE.iterdir()):
        if path.name != Path(__file__).name:
            print(f"  {path.name:28} {path.stat().st_size:>8} Bytes")


if __name__ == "__main__":
    main()
