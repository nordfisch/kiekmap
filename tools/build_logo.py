#!/usr/bin/env python3

"""Builds the placeholder emblem at ``frontend/public/logo.png``.

    python3 tools/build_logo.py

**Why a script for one file that never changes:** so that its origin is checkable. A municipal
coat of arms is an official emblem -- copyright-free under § 5 UrhG, but restricted in its use
regardless (see docs/decisions.md). What ships with this repo must therefore belong to nobody,
and the shortest proof of that is the code that draws it.

The museum replaces the file on its own device; see docs/adaption.md, "Wappen austauschen".
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "frontend" / "public" / "logo.png"

#: The palette of frontend/src/styles/global.css -- the emblem sits on the map beside the title.
PAPER, INK, ACCENT, LIGHT = "#faf8f4", "#2b2723", "#8c5a2b", "#d9b48a"

#: Drawn this many times larger and scaled down at the end. That downscale *is* the antialiasing;
#: Pillow's drawing primitives have none of their own, and on a shield outline it shows.
SCALE = 8

WIDTH, HEIGHT = 1146, 1345


def curve(start, control, end, steps: int = 60):
    """A quadratic Bézier as a list of points."""
    return [
        (
            (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0],
            (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1],
        )
        for step in range(steps + 1)
        for t in [step / steps]
    ]


def main() -> int:
    image = Image.new("RGBA", (WIDTH * SCALE, HEIGHT * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = 8 * SCALE
    left, right = margin, WIDTH * SCALE - margin
    top, bottom = margin, HEIGHT * SCALE - margin
    # Straight flanks down to half height, then both sides into the point.
    shoulder = top + (bottom - top) * 0.50
    middle = (left + right) / 2

    shield = [(left, top), (right, top), (right, shoulder)]
    shield += curve(
        (right, shoulder), (right, bottom - (bottom - shoulder) * 0.30), (middle, bottom)
    )
    shield += curve((middle, bottom), (left, bottom - (bottom - shoulder) * 0.30), (left, shoulder))

    draw.polygon(shield, fill=PAPER)
    draw.line([*shield, shield[0]], fill=INK, width=9 * SCALE, joint="curve")

    # Three bars, narrowing downwards. Deliberately nothing heraldic: it should read as "an emblem
    # goes here", not as somebody's coat of arms. They sit in the straight part, not in the point.
    for index, (share, colour) in enumerate([(0.50, ACCENT), (0.36, LIGHT), (0.22, ACCENT)]):
        height = (bottom - top) * 0.085
        y = top + (bottom - top) * (0.20 + index * 0.155)
        half = (right - left) * share / 2
        draw.rounded_rectangle(
            [middle - half, y, middle + half, y + height], radius=height / 2, fill=colour
        )

    image.resize((WIDTH, HEIGHT), Image.LANCZOS).save(TARGET, "PNG", optimize=True)
    print(f"{TARGET.relative_to(ROOT)} written ({TARGET.stat().st_size // 1024} KB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
