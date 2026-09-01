#!/usr/bin/env python3

"""Builds the gazetteer for the search in the "Hilf mit" panel.

    python3 tiles/build-places.py

Asks the Overpass API once for the streets inside the extent from ``tiles/region.json`` and for
their house numbers, and writes both to ``data/places.json``. The backend loads that file at
startup.

Why not Nominatim: for the one purpose we have -- answering "where is this?" with a street name --
a full geocoder would be oversized on a Pi. A village has a few hundred named things; they fit in
one table and are searched with LIKE.

Runs on the development machine with internet, not on the Pi.
"""

import json
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from geometry import (
    Line,
    Point,
    by_housenumber,
    distance_m,
    group_lines,
    lowest_housenumber,
    median_housenumber,
    nearest_group,
    representative_point,
)

ROOT = Path(__file__).resolve().parent.parent
REGION = ROOT / "tiles" / "region.json"
TARGET = ROOT / "data" / "places.json"

OVERPASS = "https://overpass-api.de/api/interpreter"

#: Overpass rejects requests without a meaningful user agent with "406 Not Acceptable".
#: The identifier should show who is asking -- the terms of use ask for that.
USER_AGENT = "kiekmap-museum/0.1 (Ortsindex fuer einen Museums-Kiosk, einmaliger Aufruf)"

#: Streets come back with their full course, addresses as single points.
#:
#: `out center` returns the centre of the bounding box -- on a curved street that lies beside the
#: carriageway. Streets therefore need `out geom`.
STREET_QUERY = 'way["highway"]["name"]'

#: Addresses. Without them every photo of an 800 m street would get the same point. Both forms
#: occur: an address node of its own, and a building outline carrying address tags.
ADDRESS_QUERIES = [
    'node["addr:housenumber"]["addr:street"]',
    'way["addr:housenumber"]["addr:street"]',
]


def normalize(name: str) -> str:
    """Lowercased and without diacritics, so that "muhlenweg" finds the "Mühlenweg".

    The ss for the sharp s has to happen before decomposing: NFKD leaves it untouched.
    """
    without_sharp_s = name.replace("ß", "ss").replace("ẞ", "ss")
    decomposed = unicodedata.normalize("NFKD", without_sharp_s)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


def load_region() -> tuple[str, list[float], Point]:
    """Name, extent and the centre of the village.

    The centre decides which of several streets of equal name is the museum village's -- the
    extent reaches beyond the village and holds neighbouring ones with the same street names.
    """
    region = json.loads(REGION.read_text(encoding="utf-8"))
    if region["name"] == "PLACEHOLDER":
        sys.exit("tiles/region.json enthaelt noch den Platzhalter.")
    lon, lat = region["center"]
    return region["name"], region["bbox"], (lat, lon)


def build_query(bbox: list[float]) -> str:
    # Overpass expects south,west,north,east -- exactly the other way round from our bbox.
    min_lon, min_lat, max_lon, max_lat = bbox
    frame = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    addresses = "\n  ".join(f"{pattern}({frame});" for pattern in ADDRESS_QUERIES)
    # Two outputs in one request: streets with their course, addresses with their point. Fetching
    # everything with `out geom` would be a multiple of the data, needed nowhere.
    return (
        "[out:json][timeout:180];\n"
        f"({STREET_QUERY}({frame});)->.strassen;\n"
        f"(\n  {addresses}\n)->.adressen;\n"
        ".strassen out geom tags;\n"
        ".adressen out center tags;"
    )


def ask_overpass(query: str, attempts: int = 3) -> dict:
    data = urllib.parse.urlencode({"data": query}).encode()

    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            OVERPASS, data=data, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            # 429 and 504 mean "busy right now" and pass by themselves. Anything else in the 4xx
            # range is about the request itself -- waiting does not help there.
            if error.code not in (429, 504) or attempt == attempts:
                raise
            pause = 15 * attempt
            print(f"  Overpass is busy ({error.code}), waiting {pause} s ...")
            time.sleep(pause)
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == attempts:
                raise
            pause = 10 * attempt
            print(f"  attempt {attempt} failed ({error}), waiting {pause} s ...")
            time.sleep(pause)

    raise RuntimeError("not reachable")


def address_of(tags: dict) -> tuple[str, str] | None:
    """(street, house number) -- or None when this is not an address element."""
    street = (tags.get("addr:street") or "").strip()
    number = (tags.get("addr:housenumber") or "").strip()
    return (street, number) if street and number else None


def point_of(element: dict) -> Point | None:
    """An element's centre -- for a node itself, for a way its ``center``."""
    centre = element.get("center") or element
    lat, lon = centre.get("lat"), centre.get("lon")
    return None if lat is None or lon is None else (lat, lon)


def course_of(element: dict) -> Line:
    """The way's course out of ``out geom``, or an empty list."""
    return [(p["lat"], p["lon"]) for p in element.get("geometry") or []]


def choose_street(
    groups: list[list[Line]],
    addresses_per_group: list[list[tuple[str, Point]]],
    centre: Point,
) -> int:
    """Which of several streets of equal name is the museum village's?

    **House number 1 decides.** In a village that grew it lies at the centre, and it stays there
    even when the street leads far out. A street's middle is worse for this: a long street drags
    it out of the village along with itself.

    If none of the groups has house numbers -- about a third of the streets in the extent have
    none at all -- the course decides instead.
    """
    with_addresses = [i for i, addresses in enumerate(addresses_per_group) if addresses]
    if with_addresses:
        candidates = [lowest_housenumber(addresses_per_group[i]) for i in with_addresses]
        return with_addresses[nearest_group(candidates, centre)]
    return nearest_group([representative_point(lines) for lines in groups], centre)


def in_region(point: Point, bbox: list[float]) -> bool:
    """Is the point inside the extent? Outside it the backend refuses a contribution anyway."""
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lat <= point[0] <= max_lat and min_lon <= point[1] <= max_lon


def main() -> int:
    name, bbox, centre = load_region()
    print(f"Building the place index for {name} (centre {centre[0]:.5f}, {centre[1]:.5f}) ...")

    response = ask_overpass(build_query(bbox))
    elements = response.get("elements", [])
    print(f"  {len(elements)} elements received from Overpass")

    street_pieces: dict[str, list[Line]] = {}
    addresses: dict[str, list[tuple[str, Point]]] = {}

    for element in elements:
        tags = element.get("tags", {})

        # Addresses first, and BEFORE the check for "name": an address node has no name. Without
        # this branch every address would silently drop out here -- the query would run green and
        # the gazetteer stay empty.
        if (address := address_of(tags)) is not None:
            street, number = address
            point = point_of(element)
            if point is not None and in_region(point, bbox):
                addresses.setdefault(street, []).append((number, point))
            continue

        place_name = (tags.get("name") or "").strip()
        if not place_name:
            continue

        # Clipped to the extent: Overpass returns every way in full as soon as it touches the
        # bbox. A representative point on the piece outside would be useless for a contribution --
        # the backend refuses it.
        course = [point for point in course_of(element) if in_region(point, bbox)]
        if course:
            street_pieces.setdefault(place_name, []).append(course)

    places: list[dict] = []
    foreign_housenumbers = 0

    for place_name in sorted(street_pieces):
        pieces = street_pieces[place_name]
        groups = [[pieces[i] for i in indices] for indices in group_lines(pieces)]

        # Every house number belongs to the street of equal name lying closest to it. With only
        # one group there is nothing to decide -- and that is the normal case.
        addresses_per_group: list[list[tuple[str, Point]]] = [[] for _ in groups]
        for number, point in addresses.get(place_name, []):
            nearest = min(
                range(len(groups)),
                key=lambda k: min(
                    distance_m(point, vertex) for line in groups[k] for vertex in line
                ),
            )
            addresses_per_group[nearest].append((number, point))

        chosen = choose_street(groups, addresses_per_group, centre)
        own = addresses_per_group[chosen]
        foreign_housenumbers += sum(
            len(a) for i, a in enumerate(addresses_per_group) if i != chosen
        )

        # The representative point sits at a house where there is one: for "Wo war das?" the
        # middle house number is a more usable answer than a point on the carriageway.
        lat, lon = median_housenumber(own) if own else representative_point(groups[chosen])
        places.append(
            {
                "name": place_name,
                "name_normalized": normalize(place_name),
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "kind": "strasse",
            }
        )

        for number, (address_lat, address_lon) in by_housenumber(own):
            full_name = f"{place_name} {number}"
            places.append(
                {
                    "name": full_name,
                    "name_normalized": normalize(full_name),
                    "lat": round(address_lat, 7),
                    "lon": round(address_lon, 7),
                    "kind": "adresse",
                    "street": place_name,
                    "housenumber": number,
                }
            )

    without_way = sorted(set(addresses) - set(street_pieces))
    if without_way:
        print(f"  {len(without_way)} streets known only as an address, without a way -- left out")
    if foreign_housenumbers:
        print(f"  {foreign_housenumbers} house numbers of same-named streets elsewhere removed")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(places, ensure_ascii=False, indent=1), encoding="utf-8")

    by_kind: dict[str, int] = {}
    for place in places:
        by_kind[place["kind"]] = by_kind.get(place["kind"], 0) + 1

    print(f"\n{len(places)} places written to {TARGET.relative_to(ROOT)}:")
    for kind, count in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"  {kind:12} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
