#!/usr/bin/env python3
"""Baut den Ortsindex fuer die Suche im "Hilf mit"-Bereich.

    python3 tiles/build-places.py

Fragt einmalig die Overpass-API nach benannten Dingen im Ausschnitt aus ``tiles/region.json`` --
Strassen, Gebaeude, Gewaesser, Fluren, Ortsteile -- und schreibt sie nach ``data/places.json``.
Das Backend laedt die Datei beim Start.

Warum nicht Nominatim: fuer den einen Zweck, den wir haben -- "Wo ist das?" mit einem Strassennamen
beantworten -- waere ein vollwertiger Geokodierer auf einem Pi ueberdimensioniert. Ein Dorf hat
einige hundert benannte Dinge; die passen in eine Tabelle und werden mit LIKE durchsucht.

Laeuft auf dem Entwicklungsrechner mit Internet, nicht auf dem Pi.
"""

import json
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
REGION = WURZEL / "tiles" / "region.json"
ZIEL = WURZEL / "data" / "places.json"

OVERPASS = "https://overpass-api.de/api/interpreter"

#: Overpass weist Anfragen ohne aussagekraeftigen User-Agent mit "406 Not Acceptable" ab.
#: Die Kennung soll erkennen lassen, wer da fragt -- so will es die Nutzungsordnung.
KENNUNG = "photomap-museum/0.1 (Ortsindex fuer einen Museums-Kiosk, einmaliger Aufruf)"

#: Was gesucht wird und unter welcher Art es abgelegt wird. Die Reihenfolge bestimmt bei
#: Mehrfachtreffern, welche Art gewinnt.
ABFRAGEN = [
    ('way["highway"]["name"]', "strasse"),
    ('node["place"]["name"]', "ortsteil"),
    ('way["place"]["name"]', "ortsteil"),
    ('way["building"]["name"]', "gebaeude"),
    ('node["amenity"]["name"]', "gebaeude"),
    ('way["amenity"]["name"]', "gebaeude"),
    ('way["natural"~"water|wood"]["name"]', "natur"),
    ('way["waterway"]["name"]', "natur"),
    ('way["leisure"]["name"]', "natur"),
    ('way["landuse"]["name"]', "flur"),
]


def normalisiere(name: str) -> str:
    """Kleinschreibung ohne diakritische Zeichen, damit "Muhlenweg" den "Mühlenweg" findet.

    Das ss fuer ß muss vor dem Zerlegen stehen: NFKD laesst ß unangetastet.
    """
    ohne_scharf = name.replace("ß", "ss").replace("ẞ", "ss")
    zerlegt = unicodedata.normalize("NFKD", ohne_scharf)
    return "".join(z for z in zerlegt if not unicodedata.combining(z)).lower().strip()


def lade_region() -> tuple[str, list[float]]:
    region = json.loads(REGION.read_text(encoding="utf-8"))
    if region["name"] == "PLATZHALTER":
        sys.exit("tiles/region.json enthaelt noch den Platzhalter.")
    return region["name"], region["bbox"]


def baue_abfrage(bbox: list[float]) -> str:
    # Overpass erwartet sued,west,nord,ost -- genau umgekehrt zu unserer bbox.
    min_lon, min_lat, max_lon, max_lat = bbox
    rahmen = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    teile = "\n  ".join(f"{muster}({rahmen});" for muster, _ in ABFRAGEN)
    return f"[out:json][timeout:120];\n(\n  {teile}\n);\nout center tags;"


def frage_overpass(abfrage: str, versuche: int = 3) -> dict:
    daten = urllib.parse.urlencode({"data": abfrage}).encode()

    for versuch in range(1, versuche + 1):
        anfrage = urllib.request.Request(
            OVERPASS, data=daten, headers={"User-Agent": KENNUNG, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(anfrage, timeout=180) as antwort:
                return json.load(antwort)
        except urllib.error.HTTPError as fehler:
            # 429 und 504 heissen "gerade zu viel los" und gehen von selbst vorbei. Alles andere
            # im 4xx-Bereich liegt an der Anfrage selbst -- da hilft Warten nicht.
            if fehler.code not in (429, 504) or versuch == versuche:
                raise
            wartezeit = 15 * versuch
            print(f"  Overpass ist ausgelastet ({fehler.code}), warte {wartezeit} s ...")
            time.sleep(wartezeit)
        except (urllib.error.URLError, TimeoutError) as fehler:
            if versuch == versuche:
                raise
            wartezeit = 10 * versuch
            print(f"  Versuch {versuch} fehlgeschlagen ({fehler}), warte {wartezeit} s ...")
            time.sleep(wartezeit)

    raise RuntimeError("nicht erreichbar")


def art_fuer(tags: dict) -> str:
    if "highway" in tags:
        return "strasse"
    if "place" in tags:
        return "ortsteil"
    if "building" in tags or "amenity" in tags:
        return "gebaeude"
    if "natural" in tags or "waterway" in tags or "leisure" in tags:
        return "natur"
    return "flur"


def main() -> int:
    name, bbox = lade_region()
    print(f"Ortsindex fuer {name} bauen ...")

    antwort = frage_overpass(baue_abfrage(bbox))
    elemente = antwort.get("elements", [])
    print(f"  {len(elemente)} Elemente von Overpass erhalten")

    # Eine Strasse besteht aus vielen Wegstuecken mit demselben Namen. Zusammenfassen und den
    # Mittelpunkt aller Stuecke nehmen -- sonst landet der Pin am Ende eines Teilstuecks.
    gesammelt: dict[tuple[str, str], list[tuple[float, float]]] = {}

    for element in elemente:
        tags = element.get("tags", {})
        ort_name = (tags.get("name") or "").strip()
        if not ort_name:
            continue

        mitte = element.get("center") or element
        lat, lon = mitte.get("lat"), mitte.get("lon")
        if lat is None or lon is None:
            continue

        gesammelt.setdefault((ort_name, art_fuer(tags)), []).append((lat, lon))

    orte = []
    for (ort_name, art), punkte in sorted(gesammelt.items()):
        orte.append(
            {
                "name": ort_name,
                "name_normalized": normalisiere(ort_name),
                "lat": round(sum(p[0] for p in punkte) / len(punkte), 7),
                "lon": round(sum(p[1] for p in punkte) / len(punkte), 7),
                "kind": art,
            }
        )

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(json.dumps(orte, ensure_ascii=False, indent=1), encoding="utf-8")

    nach_art: dict[str, int] = {}
    for ort in orte:
        nach_art[ort["kind"]] = nach_art.get(ort["kind"], 0) + 1

    print(f"\n{len(orte)} Orte nach {ZIEL.relative_to(WURZEL)} geschrieben:")
    for art, anzahl in sorted(nach_art.items(), key=lambda x: -x[1]):
        print(f"  {art:12} {anzahl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
