#!/usr/bin/env python3

"""Builds the sample collection under ``seed/`` -- pictures and metadata, all of it invented.

    python3 tools/build_seed.py

**Nothing here is real except the geography.** The photographs are drawn, the people are made up,
the collections and provenances are made up. Street names and coordinates are genuine, and they
have to be: the coordinates must lie inside the ``bbox`` from ``tiles/region.json`` or the map
shows nothing, and ``place_name`` must match the built gazetteer or the place search in the
"Hilf mit" panel finds nothing -- and that search is the heart of the demonstration. Streets and
coordinates are public geography out of OpenStreetMap anyway. **A personal reference would only
arise from tying names to addresses, and that tie is invented.**

Why generated and not real photographs: the real ones belong to the museum. Why a script and not
just committed files: so that the collection can be adjusted without anybody having to curate it
again, and so its origin stays checkable.

**The gaps are the point.** A collection in which everything is complete exercises half the
program. See ``GAPS`` below and ``seed/README.md``.
"""

import hashlib
import json
import random
import sys
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = ROOT / "seed"
IMAGE_DIR = SEED_DIR / "photos"

# The backend rounds a decade down; a seed that disagreed with it would contradict itself the
# moment somebody opened the editor. So the same function decides here -- and the same constant:
# a street accuracy that drifted apart would be quiet, the seed would simply stop feeding the
# sharpening question.
sys.path.insert(0, str(ROOT / "backend"))
from app.services.dates import date_range  # noqa: E402
from app.services.places import ACCURACY_STREET_M  # noqa: E402

#: One fixed start value: the same command always produces the same collection, byte for byte.
RANDOM_SEED = 20260805

#: The day this collection was designed -- not the day it was last generated. A timestamp of
#: the run would be the one field that changes on every rebuild, dirtying the repo for nothing.
CREATED = "2026-08-05T16:00:00+02:00"

#: Real addresses out of the Holm gazetteer -- see the module docstring for why they are real.
#: Test data is the documented exception to "nothing place-specific in the code" (CLAUDE.md).
ADDRESSES = {
    "Hauptstraße 14": (53.619244, 9.6747475),
    "Hauptstraße 47": (53.6243442, 9.6711054),
    "Bredhornweg 14": (53.6247861, 9.6758864),
    "Bredhornweg 18": (53.6248887, 9.6763609),
    "Friedhofsweg 30": (53.61611, 9.6707144),
    "Hauenweg 1": (53.6192181, 9.6683868),
    "Schulstraße 5": (53.6220941, 9.6745468),
    "Im Sande 2": (53.619103, 9.675636),
    "Hetlinger Straße 6": (53.6212174, 9.6688548),
    "Lehmweg 7": (53.623149, 9.6744835),
}

#: Street points from the same gazetteer -- where a photo lands that knows only its street.
#:
#: These two carry the fourth gap: without a street-precise photo the sharpening question has
#: nothing to put up, in the panel or in the detail view. The pair is chosen so that both routes
#: through the number picker are covered -- and the counts come from the gazetteer, so they are
#: what the buttons will really show:
#:
#:   * Hauptstraße, 76 addresses, 39 after merging the letter suffixes -- **with** the block step
#:   * Schulstraße, 26 addresses, 11 after merging -- **without** it, straight to the numbers
STREETS = {
    "Hauptstraße": (53.6202952, 9.6733128),
    "Schulstraße": (53.6220973, 9.6745015),
}

SEPIA = ((60, 42, 28), (232, 220, 198))


# --- the pictures -----------------------------------------------------------


def _sepia(shade: float) -> tuple[int, int, int]:
    """A tone between the two ends of ``SEPIA``. 0 is dark, 1 is light."""
    dark, light = SEPIA
    return tuple(round(low + (high - low) * shade) for low, high in zip(dark, light, strict=True))


def _house(draw: ImageDraw.ImageDraw, rng: random.Random, box, shade: float) -> None:
    """One gabled house. The whole vocabulary of these pictures -- a village needs no more."""
    left, top, right, bottom = box
    width = right - left
    ridge = top + (bottom - top) * rng.uniform(0.28, 0.45)

    draw.polygon(
        [(left - width * 0.06, ridge), ((left + right) / 2, top), (right + width * 0.06, ridge)],
        fill=_sepia(shade * 0.55),
    )
    draw.rectangle([left, ridge, right, bottom], fill=_sepia(shade))

    columns = rng.randint(2, 4)
    rows = rng.randint(1, 2)
    pane_w = width / (columns * 2 + 1)
    pane_h = (bottom - ridge) / (rows * 2.6 + 1)
    for row in range(rows):
        for column in range(columns):
            x = left + pane_w * (column * 2 + 1)
            y = ridge + pane_h * (row * 2 + 1)
            draw.rectangle([x, y, x + pane_w, y + pane_h], fill=_sepia(shade * 0.35))

    door_w = pane_w * 0.9
    door_x = left + width / 2 - door_w / 2
    draw.rectangle(
        [door_x, bottom - (bottom - ridge) * 0.32, door_x + door_w, bottom],
        fill=_sepia(shade * 0.3),
    )


def _picture(rng: random.Random, portrait: bool) -> Image.Image:
    """A drawn village view: sky, houses, ground, grain, vignette, paper edge."""
    width, height = (900, 1200) if portrait else (1400, 980)
    image = Image.new("RGB", (width, height), _sepia(0.88))
    draw = ImageDraw.Draw(image)

    horizon = height * rng.uniform(0.58, 0.68)
    for y in range(int(horizon)):  # sky, light at the top
        draw.line([(0, y), (width, y)], fill=_sepia(0.95 - 0.18 * (y / horizon)))
    draw.rectangle([0, horizon, width, height], fill=_sepia(0.44))

    for index in range(rng.randint(1, 3)):
        house_w = width * rng.uniform(0.26, 0.46)
        house_h = house_w * rng.uniform(0.75, 1.05)
        x = width * (0.08 + index * 0.31) + rng.uniform(-30, 30)
        _house(
            draw,
            rng,
            (x, horizon - house_h, x + house_w, horizon + height * 0.03),
            rng.uniform(0.60, 0.84),
        )

    for _ in range(rng.randint(0, 3)):  # a few trees
        x, size = rng.uniform(0, width), rng.uniform(40, 110)
        draw.ellipse(
            [x - size, horizon - size * 2.1, x + size, horizon + size * 0.2], fill=_sepia(0.34)
        )

    # Grain, then a soft focus -- together they take the flatness out of the flat shapes.
    noise = Image.effect_noise((width, height), 26).convert("RGB")
    image = Image.blend(image, noise, 0.10).filter(ImageFilter.GaussianBlur(1.1))

    # Vignette: a little darker towards the corners, as on an old print. Deliberately weak --
    # too strong and the bright middle reads as a fault rather than as age.
    mask = Image.new("L", (width, height), 255)
    mask_draw = ImageDraw.Draw(mask)
    for step in range(40):
        share = step / 40
        inset = share * min(width, height) * 0.55
        mask_draw.ellipse(
            [
                inset - width * 0.30,
                inset - height * 0.30,
                width - inset + width * 0.30,
                height - inset + height * 0.30,
            ],
            fill=int(150 + 105 * share),
        )
    image = Image.composite(
        image,
        Image.new("RGB", (width, height), _sepia(0.30)),
        mask.filter(ImageFilter.GaussianBlur(80)),
    )
    # The flat shapes need it: without more contrast the whole thing stays one grey mush.
    image = ImageEnhance.Contrast(image).enhance(1.35)

    # The paper the print sits on.
    border = round(min(width, height) * 0.045)
    sheet = Image.new("RGB", (width + border * 2, height + border * 2), (246, 241, 230))
    sheet.paste(image, (border, border))
    return sheet


# --- the collection ---------------------------------------------------------


class Photo(NamedTuple):
    """One entry of the sample collection. The defaults carry the ordinary case.

    Written as a table on purpose: whoever adjusts the collection should see at a glance what it
    holds and where its gaps are. Hence the defaults -- only what departs from the ordinary case
    has to be spelled out.
    """

    file: str
    title: str
    year: int | None = None
    precision: str = "year"
    address: str | None = None
    #: Only the street is known: the photo sits on the street point at 150 m, and the sharpening
    #: question may put it up. Set instead of ``address``, never alongside it.
    street: str | None = None
    #: Who stated the place. "visitor" is the ordinary way a photo becomes street-precise --
    #: somebody pressed "Reicht so — die Straße genügt"; a curator may state it too, and that one
    #: is sharpenable as well (decisions.md, point 32).
    location_source: str = "curator"
    credit: str | None = "Sammlung Heimatmuseum"
    provenance: str | None = None
    description: str | None = None
    tags: tuple[str, ...] = ("Gebäude",)
    portrait: bool = False
    status: str = "published"


GASTHOF = ("Gebäude", "Gasthof")
HOF = ("Gebäude", "Hof")

#: Deliberately uneven: messy file names beside plain ones, long descriptions beside none, one
#: photo without a credit. The collection has to show every case the admin area can display.
COLLECTION = [
    Photo("01.jpg", "Gasthof Petersen", 1910, "decade", "Hauptstraße 14", tags=GASTHOF),
    Photo(
        "02.jpg",
        "Gasthof Petersen von Nordosten",
        1935,
        address="Hauptstraße 14",
        provenance="Mappe 3, Blatt 7",
        tags=GASTHOF,
    ),
    Photo(
        "049.jpg",
        "Postkarte: Gasthof Petersen mit Saalanbau",
        1920,
        "decade",
        "Hauptstraße 14",
        credit="Nachlass Familie Wendt",
        provenance="Uebergeben 2019",
        description="Der Saal rechts wurde nach dem Krieg abgetragen.",
        tags=(*GASTHOF, "Postkarte"),
    ),
    # Without a year, and with a contribution that was taken back.
    Photo("056.jpg", "Gasthof Petersen, Hofseite", address="Hauptstraße 14", tags=GASTHOF),
    # Street-precise from a visitor: somebody pressed "Reicht so -- die Straße genügt". The long
    # route through the number picker, because Hauptstraße has too many numbers for one page.
    Photo(
        "118.jpg",
        "Gasthof Petersen mit Kastanie",
        1950,
        "decade",
        street="Hauptstraße",
        location_source="visitor",
        credit="Foto: A. Brahms",
        tags=GASTHOF,
        portrait=True,
    ),
    # Two deleted ones -- for the list that exists for them.
    Photo(
        "P1304935a (1024x683).jpg",
        "Gasthof Petersen im Schnee",
        1962,
        address="Hauptstraße 14",
        credit="Foto: A. Brahms",
        tags=("Gebäude", "Winter"),
        status="deleted",
    ),
    Photo(
        "P3099187 (1024x768).jpg",
        "Gasthof Petersen, unscharf",
        1962,
        address="Hauptstraße 14",
        credit="Foto: A. Brahms",
        status="deleted",
    ),
    Photo(
        "Scannen0092.jpg",
        "Blick über die Dächer zum Gasthof",
        1950,
        "decade",
        "Hauptstraße 14",
        provenance="Digitalisat des Museums",
        tags=("Luftaufnahme", "Gebäude"),
    ),
    Photo(
        "107.jpg",
        "Altenteil Wendt",
        1928,
        address="Bredhornweg 14",
        credit="Nachlass Familie Wendt",
        provenance="Uebergeben 2019",
        portrait=True,
    ),
    Photo(
        "108.jpg",
        "Hof Wendt",
        1930,
        "decade",
        "Bredhornweg 18",
        credit="Nachlass Familie Wendt",
        provenance="Uebergeben 2019",
        tags=HOF,
    ),
    Photo(
        "pic_158-1.jpg",
        "Ladengeschäft Rohlf",
        1950,
        "decade",
        "Friedhofsweg 30",
        description="Vorn links Jürgen Rohlf, hinten rechts das Fischgeschäft Timm.",
        tags=("Gebäude", "Laden"),
        portrait=True,
    ),
    Photo(
        "pic_158-12.jpg",
        "Ladengeschäft Rohlf, Schaufenster",
        1950,
        "decade",
        "Friedhofsweg 30",
        tags=("Gebäude", "Laden"),
    ),
    Photo(
        "052.jpg",
        "Hof Sieveking nach dem Brand",
        1943,
        address="Hauenweg 1",
        provenance="Digitalisat des Museums",
        tags=HOF,
    ),
    Photo(
        "099.jpg",
        "Hof Sieveking mit Reetdach",
        1930,
        "decade",
        "Hauenweg 1",
        provenance="Uebergeben von H. Sieveking, 2019",
        description="Aufnahme vor dem Krieg, Ecke Hauenweg und Hinterm Hof.\n"
        "In den siebziger Jahren abgetragen.\n"
        "Bewohner: Familie Sieveking, spaeter mehrere Fluechtlingsfamilien.",
        tags=HOF,
    ),
    # Without a place, and with a contribution that was taken back.
    Photo(
        "168.JPG",
        "Hof Sieveking, Rückseite",
        1930,
        "decade",
        provenance="Uebergeben von H. Sieveking, 2019",
        tags=(*HOF, "Repro"),
        portrait=True,
    ),
    # Without a year.
    Photo(
        "17.jpg",
        "Hauptstraße 47",
        address="Hauptstraße 47",
        description="Blatt 17 einer Haus-Dokumentation. Frühere Eigentümer: Familie Boysen.",
    ),
    # Neither year nor place nor credit -- the photo both questions hang on.
    Photo("pic_012.jpg", "Schule und Kindergarten", credit=None),
    # Street-precise from the curator, and sharpenable all the same -- the exception to
    # decisions.md point 5. The short route: Schulstraße fits on one page of numbers.
    Photo(
        "Bild_2024-03-11.jpg",
        "Schulstraße, heutiger Zustand",
        2019,
        street="Schulstraße",
        credit="Foto: A. Brahms",
    ),
]

#: Visitor contributions: (file, field, new value, session, taken back?)
CONTRIBUTIONS = [
    ("pic_158-1.jpg", "date", "1950er", "sitzung-2", False),
    ("pic_158-1.jpg", "location", "53.616110,9.670714 (Friedhofsweg 30)", "sitzung-2", False),
    ("pic_158-12.jpg", "date", "1950er", "sitzung-3", False),
    ("pic_158-12.jpg", "location", "53.616110,9.670714 (Friedhofsweg 30)", "sitzung-3", False),
    ("108.jpg", "date", "1930er", "sitzung-4", False),
    ("168.JPG", "location", "53.619753,9.675549", "sitzung-7", True),
    ("056.jpg", "date", "1940er", "sitzung-11", True),
    ("Scannen0092.jpg", "date", "1950er", "sitzung-15", False),
]

#: What must survive any edit to this collection -- checked at the end of every run.
GAPS = {
    "without a year": 3,
    "without a place": 2,
    "without either": 1,
    # The fourth gap, added on 10 August 2026. Two, because the number picker has two routes and
    # a single photo would only ever exercise one of them -- see ``STREETS``.
    "street-accurate only": 2,
    "deleted": 2,
    "contributions": 8,
    "withdrawn": 2,
    "without a credit": 1,
}


def main() -> int:
    rng = random.Random(RANDOM_SEED)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    for old in IMAGE_DIR.iterdir():
        old.unlink()

    photos = []
    for photo in COLLECTION:
        path = IMAGE_DIR / photo.file
        picture = _picture(rng, photo.portrait)
        picture.save(path, "JPEG", quality=82, optimize=True)

        entry: dict = {
            "file": photo.file,
            # The change detector of seed.load. Without it every load warns about all eighteen
            # files -- and a warning that always fires is one nobody reads any more.
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "title": photo.title,
            "title_source": "curator",
            "description": photo.description,
            "credit": photo.credit,
            "provenance": photo.provenance,
            "tags": list(photo.tags),
            "status": photo.status,
        }
        if photo.year is not None:
            start, end, resolved = date_range(photo.year, precision=photo.precision)
            entry |= {
                "date_from": start.isoformat(),
                "date_to": end.isoformat(),
                "date_precision": resolved,
                "date_source": "curator",
            }
        if photo.address is not None:
            lat, lon = ADDRESSES[photo.address]
            entry |= {
                "lat": lat,
                "lon": lon,
                "place_name": photo.address,
                "location_accuracy_m": 15,
                "location_source": photo.location_source,
            }
        elif photo.street is not None:
            lat, lon = STREETS[photo.street]
            entry |= {
                "lat": lat,
                "lon": lon,
                "place_name": photo.street,
                "location_accuracy_m": ACCURACY_STREET_M,
                "location_source": photo.location_source,
            }

        contributions = [c for c in CONTRIBUTIONS if c[0] == photo.file]
        if contributions:
            entry["changes"] = [
                {
                    "field": field,
                    "old_value": None,
                    "new_value": value,
                    "source": "visitor",
                    "session_id": session,
                    "reverted": reverted,
                }
                for _, field, value, session, reverted in contributions
            ]
        photos.append(entry)

    (SEED_DIR / "seed.json").write_text(
        json.dumps(
            {
                "created": CREATED,
                "photos": photos,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )

    _report(photos)
    return 0


def _report(photos: list[dict]) -> int:
    counted = {
        "without a year": sum(1 for p in photos if "date_from" not in p),
        "without a place": sum(1 for p in photos if "lat" not in p),
        "without either": sum(1 for p in photos if "date_from" not in p and "lat" not in p),
        "street-accurate only": sum(
            1 for p in photos if p.get("location_accuracy_m") == ACCURACY_STREET_M
        ),
        "deleted": sum(1 for p in photos if p["status"] != "published"),
        "contributions": sum(len(p.get("changes", [])) for p in photos),
        "withdrawn": sum(1 for p in photos for c in p.get("changes", []) if c["reverted"]),
        "without a credit": sum(1 for p in photos if not p["credit"]),
    }
    size = sum(f.stat().st_size for f in IMAGE_DIR.iterdir()) // 1024

    print(
        f"{len(photos)} pictures written to {IMAGE_DIR.relative_to(ROOT)} ({size} KB), "
        f"seed.json written."
    )
    for name, wanted in GAPS.items():
        actual = counted[name]
        state = "ok" if actual == wanted else "<-- MISSING"
        print(f"  {name:22} {actual:2}   expected {wanted:2}   {state}")
    if counted != GAPS:
        print("\nThe gaps no longer add up. They are not an oversight but the reason this")
        print("collection makes half the program testable at all.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
