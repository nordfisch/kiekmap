#!/usr/bin/env python3

"""Builds a copy of an archive folder in which every picture is a JPEG.

    python3 tools/to_jpeg.py "~/Museum/Neue Fotos" "~/Museum/Neue Fotos zwecks Import/Straßen"

Museum archives are mixed: scans arrive as TIFF, screenshots as PNG, a website picture as WEBP.
The collection is JPEG throughout, and the reason is not tidiness. **A browser cannot display a
TIFF.** The kiosk would show a thumbnail and hand out an original that nothing opens -- and the
detail view offers exactly that file.

The tree is copied, never changed in place: what the museum sent stays as it was sent, and a
second run over the same source is a repetition, not a further step.

**The settings are measured, not chosen.** The first Holm stock had been converted before it was
imported, by a tool nobody wrote down. Its quantization tables say Pillow at quality 92 with 4:4:4
sampling and ``optimize``; against the 19 files for which both versions exist, this reproduces
four of them byte for byte and eighteen pixel for pixel. That matters beyond neatness: two runs
of the same recipe over the same file give the same SHA-256, and the SHA-256 is what the import
uses to recognize a duplicate. A different quality here would quietly take the same picture in a
second time.

    The nineteenth is ``Weidenstieg/Straßenauffahrt``, whose old JPEG carries different tables --
    somebody converted that one by hand, before the recipe existed.

**What the file says about itself comes along**: EXIF, the IPTC block and the XMP packet. It did
not until 16 August 2026, and twelve photographs paid for it -- they lost their photographer
("A. Brahms"), a caption and a date, and carried the collection's default credit instead. A
wrong attribution is worse than none: it looks like an answer.

    That does move the goalposts of the promise above, and the shift is worth naming. Two runs of
    *this* recipe over the same file still give the same SHA-256 -- but a file converted before
    that day and the same file converted today are no longer the same bytes. Nothing needs
    reconverting; the twelve were repaired in place. It matters for the next stand, where
    duplicates are recognized by picture and not by byte anyway (decisions.md, point 47).

What this does **not** do is notice that a converted TIFF already sits in the collection as a
JPEG. It cannot: the two files differ in their metadata blocks, so their SHA-256 differ, and
recognizing them means comparing pictures rather than bytes. That is backlog point 42.
"""

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageFile, IptcImagePlugin

#: Taken over unchanged -- these are already what the collection stores.
KEPT = {".jpg", ".jpeg"}

#: Converted. Anything else in the tree is not a picture and stays behind.
CONVERTED = {".png", ".tif", ".tiff", ".webp"}

#: Measured against the first stock -- see the module docstring. Do not tune.
JPEG_OPTIONS = {"quality": 92, "subsampling": 0, "optimize": True}

#: EXIF tags worth carrying from a TIFF into a JPEG -- what the picture says, not how the file is
#: laid out.
#:
#: A TIFF's first directory is mostly structure: ``StripOffsets``, ``RowsPerStrip``,
#: ``PhotometricInterpretation``. Written into a JPEG those are at best meaningless and at worst a
#: lie about where the pixels are, and ``Exif.tobytes()`` fails outright on one of the Holm scans,
#: whose ``IPTCNAA`` tag Pillow reads as a single mangled integer. So the block is rebuilt from a
#: list rather than copied -- these tags plus the two sub-directories below.
_EXIF_KEEP = frozenset(
    {
        0x010E,  # ImageDescription
        0x010F,  # Make
        0x0110,  # Model
        0x0112,  # Orientation
        0x0132,  # DateTime
        0x013B,  # Artist
        0x8298,  # Copyright
        0x9C9B,  # XPTitle
        0x9C9E,  # XPKeywords
    }
)
_EXIF_IFD = 0x8769
_GPS_IFD = 0x8825

#: TIFF tag 700, the XMP packet.
_TIFF_XMP = 700

_APP13 = b"\xff\xed"
_PHOTOSHOP_MARKER = b"Photoshop 3.0\x00"
#: A JPEG segment carries a two-byte length, so this much payload at most.
_SEGMENT_MAX = 0xFFFF - 2 - len(_PHOTOSHOP_MARKER)


def _iptc_block(parsed: dict) -> bytes:
    """Rebuild the IPTC block from what Pillow parsed, wrapped as a Photoshop resource.

    **Rebuilt rather than copied, and that is the point.** A TIFF keeps its IPTC in either of two
    places -- tag 34377 (the Photoshop resources) or tag 33723 (IPTC-NAA directly) -- and the Holm
    stock uses both. Worse, Pillow reads 33723 back as a single mangled integer, so the raw bytes
    are not available at all. What *is* available is ``getiptcinfo``, and that is the same function
    the import reads the file with later: writing back what it returned makes the round trip true
    by construction rather than by hope.

    Sorted by record and dataset, so the same input gives the same bytes -- the collection names
    its files after their SHA-256, and a conversion that wobbles would take every picture in twice.
    The order also puts dataset 1:90, the character-set marker, in front of the text it applies to.
    """
    records = bytearray()
    for (record, dataset), value in sorted(parsed.items()):
        for single in value if isinstance(value, list) else [value]:
            if not isinstance(single, bytes) or len(single) > 0x7FFF:
                continue
            records += bytes((0x1C, record, dataset)) + len(single).to_bytes(2, "big") + single
    if not records:
        return b""

    # 8BIM resource 0x0404 is the IPTC-NAA record. The empty name is a Pascal string padded to an
    # even length, and the payload is padded the same way.
    block = b"8BIM\x04\x04\x00\x00" + len(records).to_bytes(4, "big") + bytes(records)
    return block + b"\x00" * (len(block) % 2)


def _carried_metadata(picture: Image.Image, raw_xmp: object) -> tuple[dict, bytes]:
    """What of the source's metadata goes into the JPEG: save options, plus the APP13 payload."""
    options: dict = {}
    source_exif = picture.getexif()

    clean = Image.Exif()
    for tag in _EXIF_KEEP:
        if tag in source_exif:
            clean[tag] = source_exif[tag]
    for ifd in (_EXIF_IFD, _GPS_IFD):
        if content := dict(source_exif.get_ifd(ifd)):
            clean[ifd] = content
    if len(clean):
        options["exif"] = clean.tobytes()

    xmp = picture.tag_v2.get(_TIFF_XMP) if picture.format == "TIFF" else raw_xmp
    if isinstance(xmp, str):
        xmp = xmp.encode("utf-8")
    if isinstance(xmp, bytes):
        options["xmp"] = xmp

    try:
        parsed = IptcImagePlugin.getiptcinfo(picture) or {}
    except Exception:  # noqa: BLE001 -- a broken IPTC block must not stop the conversion
        parsed = {}
    photoshop = _iptc_block(parsed)
    return options, photoshop if len(photoshop) <= _SEGMENT_MAX else b""


def _splice_app13(path: Path, payload: bytes) -> None:
    """Insert the Photoshop block behind the segments Pillow wrote.

    Behind rather than in front: the JFIF header belongs first, and a reader that only looks at
    the very first segment must still find it. Everything after that is free -- ``APPn`` markers
    may stand in any order, and Pillow's own IPTC reader walks all of them.
    """
    data = path.read_bytes()
    position = 2  # behind the start-of-image marker
    while data[position : position + 1] == b"\xff" and 0xE0 <= data[position + 1] <= 0xEF:
        position += 2 + int.from_bytes(data[position + 2 : position + 4], "big")

    segment = _APP13 + (len(_PHOTOSHOP_MARKER) + len(payload) + 2).to_bytes(2, "big")
    path.write_bytes(data[:position] + segment + _PHOTOSHOP_MARKER + payload + data[position:])


def to_jpeg(source: Path, target: Path) -> None:
    """Write one picture as a JPEG, carrying over what the file says about itself.

    Straight to the file rather than through a buffer -- a 200 MB TIFF should not need its JPEG
    in memory as well, the same reason ``storage.sha256_of_file`` reads in chunks.

    The one surprise is ``ImageFile.MAXBLOCK``. With ``optimize`` libjpeg wants the whole image
    in one block, and Pillow guesses that block at one byte per pixel. A photograph at quality 92
    needs a third of that, so the Holm scans never noticed -- but a small picture full of detail
    overruns the guess and the save fails with "broken data stream when writing image file". The
    guess is only a floor, so raising it costs nothing and removes the whole class.
    """
    picture = Image.open(source)
    # Pillow trips over a TIFF whose XMP field arrives as a tuple instead of text, and 25 of the
    # Holm scans have one. It goes before anything reads it -- the packet itself is taken from
    # the TIFF tag, which is not mangled.
    raw_xmp = picture.info.pop("xmp", None)
    options = dict(JPEG_OPTIONS)
    if icc := picture.info.get("icc_profile"):
        options["icc_profile"] = icc
    if dpi := picture.info.get("dpi"):
        options["dpi"] = dpi

    carried, photoshop = _carried_metadata(picture, raw_xmp)
    options.update(carried)

    if picture.mode in ("RGBA", "LA", "P"):
        # JPEG has no transparency. White rather than black: these are scans of paper, and a
        # transparent margin is the paper's, not a hole in the picture.
        picture = picture.convert("RGBA")
        background = Image.new("RGB", picture.size, (255, 255, 255))
        background.paste(picture, mask=picture.getchannel("A"))
        picture = background
    else:
        picture = picture.convert("RGB")

    width, height = picture.size
    ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, width * height * 4)
    with target.open("wb") as handle:
        picture.save(handle, "JPEG", **options)

    if photoshop:
        _splice_app13(target, photoshop)


def build(source_root: Path, target_root: Path, dry_run: bool = False) -> Counter:
    counts: Counter = Counter()
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        suffix = path.suffix.lower()
        if suffix not in KEPT | CONVERTED:
            counts["uebergangen"] += 1
            continue

        target = target_root / path.relative_to(source_root)
        if suffix in CONVERTED:
            target = target.with_suffix(".jpg")

        if dry_run:
            counts["kopiert" if suffix in KEPT else "umgewandelt"] += 1
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if suffix in KEPT:
            shutil.copy2(path, target)
            counts["kopiert"] += 1
        else:
            try:
                to_jpeg(path, target)
            except Exception as error:  # noqa: BLE001 -- one bad file must not stop the run
                print(f"  ! {path.relative_to(source_root)}: {error}", file=sys.stderr)
                target.unlink(missing_ok=True)
                counts["gescheitert"] += 1
                continue
            # The file date is the archive's, and sometimes the only date a picture has.
            shutil.copystat(path, target)
            counts["umgewandelt"] += 1
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/to_jpeg.py",
        description="Einen Archivordner als JPEG-Kopie herstellen.",
    )
    parser.add_argument("quelle", type=Path, help="Der Ordner des Archivs, bleibt unveraendert")
    parser.add_argument("ziel", type=Path, help="Wohin die Kopie soll, darf noch nicht bestehen")
    parser.add_argument("--probelauf", action="store_true", help="Nur zaehlen, nichts schreiben")
    args = parser.parse_args(argv)

    source = args.quelle.expanduser().resolve()
    target = args.ziel.expanduser().resolve()
    if not source.is_dir():
        print(f"Kein Verzeichnis: {source}", file=sys.stderr)
        return 1
    if target.exists() and any(target.iterdir()) and not args.probelauf:
        print(f"Das Ziel ist nicht leer: {target}", file=sys.stderr)
        return 1
    if target == source or source in target.parents:
        print("Das Ziel darf nicht in der Quelle liegen.", file=sys.stderr)
        return 1

    counts = build(source, target, dry_run=args.probelauf)
    print(f"\n{sum(counts.values())} Dateien angesehen:")
    print(f"  kopiert      {counts['kopiert']}")
    print(f"  umgewandelt  {counts['umgewandelt']}")
    print(f"  uebergangen  {counts['uebergangen']}")
    if counts["gescheitert"]:
        print(f"  gescheitert  {counts['gescheitert']}")
    return 1 if counts["gescheitert"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
