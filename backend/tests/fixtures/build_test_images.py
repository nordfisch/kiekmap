# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Erzeugt die Testbilder in diesem Verzeichnis.

Aufruf: ``python tests/fixtures/build_test_images.py``

Die Bilder decken bewusst die Faelle ab, an denen ein Import scheitert oder -- schlimmer -- still
etwas Falsches tut:

    scan_ohne_exif.jpg      der Normalfall: ein Scan ohne jede Angabe
    scan_mit_scandatum.jpg  EXIF-Datum von 2019, obwohl das Foto historisch ist
    scan_vom_scanner.jpg    dasselbe, aber das Geraet nennt sich: "HP Scanjet 3670"
    kamerafoto.jpg          Kamera und Datum von 2014 -- ein echtes Aufnahmedatum
    foto_mit_gps.jpg        echtes Digitalfoto mit Koordinaten und Aufnahmedatum
    hochkant.jpg            Ausrichtung steht im EXIF, nicht in den Pixeln
    graustufen.tif          TIFF ohne Farbe, wie es Buchscanner liefern
    cmyk.tif                CMYK -- WebP kennt diesen Farbraum nicht
    kein_bild.txt           Textdatei mit Bildendung
"""

import io
from pathlib import Path

import piexif
from PIL import Image, ImageDraw

HIER = Path(__file__).parent


def _bild(breite: int, hoehe: int, text: str, farbe: str = "#c8bfae") -> Image.Image:
    bild = Image.new("RGB", (breite, hoehe), farbe)
    zeichner = ImageDraw.Draw(bild)
    zeichner.rectangle([8, 8, breite - 8, hoehe - 8], outline="#3a3128", width=3)
    zeichner.text((20, hoehe // 2), text, fill="#3a3128")
    return bild


def _mit_exif(bild: Image.Image, ziel: Path, exif_dict: dict) -> None:
    puffer = io.BytesIO()
    bild.save(puffer, "JPEG", quality=90)
    piexif.insert(piexif.dump(exif_dict), puffer.getvalue(), str(ziel))


def _grad_nach_dms(grad: float) -> tuple:
    grad = abs(grad)
    d = int(grad)
    m = int((grad - d) * 60)
    s = round((grad - d - m / 60) * 3600, 4)
    return ((d, 1), (m, 1), (int(s * 10000), 10000))


def main() -> None:
    # 1. Der Normalfall: gescannter Papierabzug, keinerlei Metadaten.
    _bild(900, 640, "Scan ohne EXIF").save(HIER / "scan_ohne_exif.jpg", "JPEG", quality=90)

    # 2. Der gefaehrliche Fall: das EXIF traegt das Datum des Scanvorgangs. Wuerde es uebernommen,
    #    laege ein Foto von 1932 auf der Zeitleiste bei 2019 -- und wuerde nie nachgefragt.
    _mit_exif(
        _bild(900, 640, "Scan, EXIF = Scandatum 2019"),
        HIER / "scan_mit_scandatum.jpg",
        {
            "0th": {piexif.ImageIFD.ImageDescription: b"Kirchweih an der Muehle"},
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2019:03:14 11:22:33"},
        },
    )

    # 2b. Derselbe Fall, aber die Datei sagt, womit sie entstanden ist. Der Geraetename entscheidet
    #     dann statt der Jahresgrenze -- und "unbekannt" als Fotograf ist kein Bildnachweis.
    _mit_exif(
        _bild(900, 640, "Scan vom Flachbettscanner, 2015"),
        HIER / "scan_vom_scanner.jpg",
        {
            "0th": {
                piexif.ImageIFD.Make: b"HP",
                piexif.ImageIFD.Model: b"HP Scanjet 3670",
                piexif.ImageIFD.Artist: b"unbekannt",
            },
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2015:04:02 09:15:00"},
        },
    )

    # 2c. Die Gegenrichtung: eine Kamera. Ihr Datum ist ein Aufnahmedatum, auch wenn es weit hinter
    #     exif_date_max_year liegt -- die Jahresgrenze ist nur der Ersatz fuer eine Geraeteangabe.
    _mit_exif(
        _bild(900, 640, "Kamerafoto 2014", farbe="#b6c8b0"),
        HIER / "kamerafoto.jpg",
        {
            "0th": {
                piexif.ImageIFD.Make: b"OLYMPUS IMAGING CORP.",
                piexif.ImageIFD.Model: b"E-500",
                piexif.ImageIFD.Artist: "August Kroeger".encode("latin-1"),
            },
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2014:03:09 16:41:20"},
        },
    )

    # 3. Echtes Digitalfoto: Datum und Ort duerfen uebernommen werden. Koordinaten in Holm.
    _mit_exif(
        _bild(900, 640, "Digitalfoto mit GPS", farbe="#b6c8b0"),
        HIER / "foto_mit_gps.jpg",
        {
            "Exif": {piexif.ExifIFD.DateTimeOriginal: b"1975:06:21 14:05:00"},
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: b"N",
                piexif.GPSIFD.GPSLatitude: _grad_nach_dms(53.62053),
                piexif.GPSIFD.GPSLongitudeRef: b"E",
                piexif.GPSIFD.GPSLongitude: _grad_nach_dms(9.67601),
            },
        },
    )

    # 4. Hochkant gescannt: die Pixel sind quer, die Ausrichtung steht im EXIF. Ohne Beachtung
    #    liegen Vorschaubild und gespeicherte Masse falsch herum.
    _mit_exif(
        _bild(900, 600, "hochkant (Orientation 6)"),
        HIER / "hochkant.jpg",
        {"0th": {piexif.ImageIFD.Orientation: 6}},
    )

    # 5. Graustufen-TIFF, wie es Buchscanner liefern.
    _bild(800, 600, "Graustufen").convert("L").save(HIER / "graustufen.tif", "TIFF")

    # 6. CMYK -- diesen Farbraum kann WebP nicht speichern.
    _bild(800, 600, "CMYK").convert("CMYK").save(HIER / "cmyk.tif", "TIFF")

    # 7. Keine Bilddatei, trotz Endung.
    (HIER / "kein_bild.txt").write_text("Das hier ist kein Bild.\n", encoding="utf-8")

    for pfad in sorted(HIER.iterdir()):
        if pfad.name != Path(__file__).name:
            print(f"  {pfad.name:28} {pfad.stat().st_size:>8} Bytes")


if __name__ == "__main__":
    main()
