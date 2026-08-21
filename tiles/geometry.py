# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""The arithmetic behind the gazetteer: grouping ways of equal name and finding their point.

Its own module because both mistakes that lurk here happen **silently** -- the index gets built,
the script runs green, and only in the museum does somebody tap "Hauptstrasse" and get a point two
kilometres away.

A region's extract reaches beyond the museum's own village, so it holds several villages and with
them several streets of the same name. Earlier versions averaged them into one point that then lay
on none of them.

All coordinates are ``(lat, lon)`` in degrees.
"""

import math
from itertools import pairwise

Point = tuple[float, float]
Line = list[Point]

#: One degree of latitude in metres. Accurate enough within one municipality -- what happens here
#: is comparing, not surveying.
M_PER_DEGREE = 111_320.0

#: From what distance on two ways of equal name count as two different streets.
#:
#: Connected pieces of the same street share their end points, so they lie 0 m apart; two villages
#: are kilometres apart. The 150 m are the generous distance in between: even a street that skips
#: an intersection stays one.
SEPARATION_M = 150.0


def distance_m(a: Point, b: Point) -> float:
    """Distance between two points in metres, equirectangular approximation."""
    mean_latitude = math.radians((a[0] + b[0]) / 2)
    d_lat = (a[0] - b[0]) * M_PER_DEGREE
    d_lon = (a[1] - b[1]) * M_PER_DEGREE * math.cos(mean_latitude)
    return math.hypot(d_lat, d_lon)


def _nearest_on_segment(start: Point, end: Point, target: Point) -> Point:
    """The point on the segment ``start``-``end`` that lies closest to ``target``.

    The projection is clamped to the segment; outside it the nearest point is one of the two ends.
    """
    latitude = math.radians(target[0])
    # Into a local metric grid, or longitude distorts the projection.
    ax, ay = start[1] * math.cos(latitude), start[0]
    bx, by = end[1] * math.cos(latitude), end[0]
    tx, ty = target[1] * math.cos(latitude), target[0]

    dx, dy = bx - ax, by - ay
    length = dx * dx + dy * dy
    if length == 0:
        return start

    fraction = ((tx - ax) * dx + (ty - ay) * dy) / length
    fraction = max(0.0, min(1.0, fraction))
    return (
        start[0] + fraction * (end[0] - start[0]),
        start[1] + fraction * (end[1] - start[1]),
    )


def representative_point(lines: list[Line]) -> Point:
    """A point **on** the way, as near its middle as possible.

    First the centroid of all vertices, then the point of the line lying closest to it. For a
    straight street that is its middle; for a curved or L-shaped one the point of the carriageway
    that comes closest to the middle.

    The centroid alone will not do: it is precisely the centre of the bounding box and lies beside
    a crooked street -- in the unlucky case on somebody's property.
    """
    vertices = [point for line in lines for point in line]
    if not vertices:
        raise ValueError("representative_point braucht mindestens einen Punkt")

    centroid = (
        sum(p[0] for p in vertices) / len(vertices),
        sum(p[1] for p in vertices) / len(vertices),
    )

    best = vertices[0]
    shortest = distance_m(best, centroid)
    for line in lines:
        for start, end in pairwise(line):
            candidate = _nearest_on_segment(start, end, centroid)
            distance = distance_m(candidate, centroid)
            if distance < shortest:
                best, shortest = candidate, distance
    return best


def _bounding_box(line: Line) -> tuple[float, float, float, float]:
    """The enclosing rectangle (min_lat, min_lon, max_lat, max_lon)."""
    lats = [p[0] for p in line]
    lons = [p[1] for p in line]
    return (min(lats), min(lons), max(lats), max(lons))


def _boxes_near(a: tuple, b: tuple, within_m: float) -> bool:
    """Can two rectangles come closer than ``within_m``? Coarse, but never too strict."""
    d_lat = max(0.0, a[0] - b[2], b[0] - a[2]) * M_PER_DEGREE
    latitude = math.radians((a[0] + b[0]) / 2)
    d_lon = max(0.0, a[1] - b[3], b[1] - a[3]) * M_PER_DEGREE * math.cos(latitude)
    return math.hypot(d_lat, d_lon) <= within_m


def group_lines(lines: list[Line], separation_m: float = SEPARATION_M) -> list[list[int]]:
    """Split ways of equal name into spatially separate groups.

    Returns lists of indices into ``lines``. Two ways land in the same group when any vertex of
    one lies closer than ``separation_m`` to a vertex of the other -- and transitively over
    everything thereby connected. A street made of twenty pieces stays one, even when a kilometre
    lies between its ends.
    """
    parent = list(range(len(lines)))
    boxes = [_bounding_box(line) for line in lines]

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            if root(i) == root(j):
                continue
            # The bounding boxes first: the vertex-by-vertex comparison is quadratic, and it is
            # exactly the far-apart pairs -- the most common ones -- that otherwise run in full.
            if not _boxes_near(boxes[i], boxes[j], separation_m):
                continue
            if any(distance_m(p, q) <= separation_m for p in lines[i] for q in lines[j]):
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(len(lines)):
        groups.setdefault(root(i), []).append(i)
    return list(groups.values())


def nearest_group(candidates: list[Point], centre: Point) -> int:
    """Which candidate lies closest to the centre of the village? Returns the index.

    This is what decides which of seventeen "Hauptstrassen" in the extract is the museum
    village's -- without the place name standing in the code. ``centre`` comes from
    ``tiles/region.json``.
    """
    if not candidates:
        raise ValueError("nearest_group braucht mindestens einen Kandidaten")
    return min(range(len(candidates)), key=lambda i: distance_m(candidates[i], centre))


def housenumber_key(number: str) -> tuple[int, str]:
    """Order house numbers the way a postman walks -- not the way a computer sorts.

    Alphabetically "10" would come before "9" and "1a" before "2". The key is (leading number,
    remainder), so that 1, 1a, 2, 9, 10, 12 come out in that order.

    **Has to agree with ``sort_key`` in ``backend/app/services/places.py``**, or the kiosk orders
    the buttons differently from how this script worked out the middle.
    """
    digits = ""
    for character in number:
        if not character.isdigit():
            break
        digits += character
    return (int(digits) if digits else 0, number[len(digits) :].lower())


def by_housenumber(addresses: list[tuple[str, Point]]) -> list[tuple[str, Point]]:
    """Addresses in walking order. ``addresses`` is a list of (house number, point)."""
    return sorted(addresses, key=lambda entry: housenumber_key(entry[0]))


def median_housenumber(addresses: list[tuple[str, Point]]) -> Point:
    """The point of the middle house number -- the representative of a street that has addresses.

    Better than any calculated centre: the point sits at a house rather than on the carriageway,
    and for "Wo war das?" a house is the more usable answer. With an even count the lower of the
    two middle ones wins -- a choice has to be made, and it is without consequence.
    """
    if not addresses:
        raise ValueError("median_housenumber braucht mindestens eine Adresse")
    ordered = by_housenumber(addresses)
    return ordered[(len(ordered) - 1) // 2][1]


def lowest_housenumber(addresses: list[tuple[str, Point]]) -> Point:
    """The point of the lowest house number -- it decides between streets of equal name.

    In a village that grew, house number 1 lies at the centre; which street of equal name belongs
    to the museum's village can be read from that more reliably than from its middle, because a
    long street leads out of the village and drags its middle along.
    """
    if not addresses:
        raise ValueError("lowest_housenumber braucht mindestens eine Adresse")
    return by_housenumber(addresses)[0][1]
