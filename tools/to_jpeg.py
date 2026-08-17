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

What this does **not** do is notice that a converted TIFF already sits in the collection as a
JPEG. It cannot: the two files differ in their metadata blocks, so their SHA-256 differ, and
recognizing them means comparing pictures rather than bytes. That is backlog point 42.
"""

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageFile

#: Taken over unchanged -- these are already what the collection stores.
KEPT = {".jpg", ".jpeg"}

#: Converted. Anything else in the tree is not a picture and stays behind.
CONVERTED = {".png", ".tif", ".tiff", ".webp"}

#: Measured against the first stock -- see the module docstring. Do not tune.
JPEG_OPTIONS = {"quality": 92, "subsampling": 0, "optimize": True}


def to_jpeg(source: Path, target: Path) -> None:
    """Write one picture as a JPEG, colour profile and resolution carried over.

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
    # Holm scans have one. The field says nothing we keep, so it goes before anything reads it.
    picture.info.pop("xmp", None)
    options = dict(JPEG_OPTIONS)
    if icc := picture.info.get("icc_profile"):
        options["icc_profile"] = icc
    if dpi := picture.info.get("dpi"):
        options["dpi"] = dpi

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
