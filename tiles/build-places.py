#!/usr/bin/env python3
"""Baut den Ortsindex fuer die Suche im "Hilf mit"-Bereich.

    python3 tiles/build-places.py

Fragt einmalig die Overpass-API nach den Strassen im Ausschnitt aus ``tiles/region.json`` und
nach ihren Hausnummern, und schreibt beides nach ``data/places.json``.
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

from geometry import (
    Linie,
    Punkt,
    entfernung_m,
    gruppiere,
    mittlere_hausnummer,
    nach_hausnummer,
    naechste_gruppe,
    niedrigste_hausnummer,
    vertreterpunkt,
)

WURZEL = Path(__file__).resolve().parent.parent
REGION = WURZEL / "tiles" / "region.json"
ZIEL = WURZEL / "data" / "places.json"

OVERPASS = "https://overpass-api.de/api/interpreter"

#: Overpass weist Anfragen ohne aussagekraeftigen User-Agent mit "406 Not Acceptable" ab.
#: Die Kennung soll erkennen lassen, wer da fragt -- so will es die Nutzungsordnung.
KENNUNG = "photomap-museum/0.1 (Ortsindex fuer einen Museums-Kiosk, einmaliger Aufruf)"

#: Strassen kommen mit vollem Verlauf zurueck, Adressen als einzelne Punkte.
#:
#: `out center` liefert die Mitte des umschliessenden Rechtecks -- bei einer gebogenen Strasse
#: liegt die neben der Fahrbahn. Fuer Strassen wird deshalb `out geom` gebraucht.
STRASSEN_ABFRAGE = 'way["highway"]["name"]'

#: Adressen. Ohne sie bekaeme jedes Foto einer 800 m langen Strasse denselben Punkt. Beide Formen
#: kommen vor: ein eigener Adressknoten und ein Gebaeudeumriss mit Adresstags.
ADRESS_ABFRAGEN = [
    'node["addr:housenumber"]["addr:street"]',
    'way["addr:housenumber"]["addr:street"]',
]


def normalisiere(name: str) -> str:
    """Kleinschreibung ohne diakritische Zeichen, damit "Muhlenweg" den "Mühlenweg" findet.

    Das ss fuer ß muss vor dem Zerlegen stehen: NFKD laesst ß unangetastet.
    """
    ohne_scharf = name.replace("ß", "ss").replace("ẞ", "ss")
    zerlegt = unicodedata.normalize("NFKD", ohne_scharf)
    return "".join(z for z in zerlegt if not unicodedata.combining(z)).lower().strip()


def lade_region() -> tuple[str, list[float], Punkt]:
    """Name, Ausschnitt und Ortsmitte.

    Die Mitte entscheidet bei gleichnamigen Strassen, welche die des Museumsortes ist -- der
    Ausschnitt reicht ueber den Ort hinaus und enthaelt Nachbardoerfer mit denselben Namen.
    """
    region = json.loads(REGION.read_text(encoding="utf-8"))
    if region["name"] == "PLATZHALTER":
        sys.exit("tiles/region.json enthaelt noch den Platzhalter.")
    lon, lat = region["center"]
    return region["name"], region["bbox"], (lat, lon)


def baue_abfrage(bbox: list[float]) -> str:
    # Overpass erwartet sued,west,nord,ost -- genau umgekehrt zu unserer bbox.
    min_lon, min_lat, max_lon, max_lat = bbox
    rahmen = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    adressen = "\n  ".join(f"{muster}({rahmen});" for muster in ADRESS_ABFRAGEN)
    # Zwei Ausgaben in einer Anfrage: Strassen mit Verlauf, Adressen mit ihrem Punkt. Alles mit
    # `out geom` zu holen waere ein Vielfaches an Daten, ohne irgendwo gebraucht zu werden.
    return (
        "[out:json][timeout:180];\n"
        f"({STRASSEN_ABFRAGE}({rahmen});)->.strassen;\n"
        f"(\n  {adressen}\n)->.adressen;\n"
        ".strassen out geom tags;\n"
        ".adressen out center tags;"
    )


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


def adresse_von(tags: dict) -> tuple[str, str] | None:
    """(Strasse, Hausnummer) -- oder None, wenn das kein Adresselement ist."""
    strasse = (tags.get("addr:street") or "").strip()
    nummer = (tags.get("addr:housenumber") or "").strip()
    return (strasse, nummer) if strasse and nummer else None


def punkt_von(element: dict) -> Punkt | None:
    """Der Mittelpunkt eines Elements -- bei Knoten es selbst, bei Wegen ihr ``center``."""
    mitte = element.get("center") or element
    lat, lon = mitte.get("lat"), mitte.get("lon")
    return None if lat is None or lon is None else (lat, lon)


def verlauf_von(element: dict) -> Linie:
    """Der Wegverlauf aus ``out geom``, oder eine leere Liste."""
    return [(p["lat"], p["lon"]) for p in element.get("geometry") or []]


def waehle_strasse(
    gruppen: list[list[Linie]],
    adressen_je_gruppe: list[list[tuple[str, Punkt]]],
    zentrum: Punkt,
) -> int:
    """Welche von mehreren gleichnamigen Strassen ist die des Museumsortes?

    **Die Hausnummer 1 entscheidet.** In einem gewachsenen Dorf liegt sie am Ortskern, und sie
    bleibt dort, auch wenn die Strasse weit hinausfuehrt. Die Mitte einer Strasse taugt dafuer
    schlechter: Eine lange Strasse zieht sie mit sich aus dem Ort heraus.

    Hat keine der Gruppen Hausnummern -- rund ein Drittel der Strassen im Ausschnitt hat gar
    keine --, entscheidet ersatzweise der Verlauf.
    """
    mit_adressen = [i for i, adressen in enumerate(adressen_je_gruppe) if adressen]
    if mit_adressen:
        kandidaten = [niedrigste_hausnummer(adressen_je_gruppe[i]) for i in mit_adressen]
        return mit_adressen[naechste_gruppe(kandidaten, zentrum)]
    return naechste_gruppe([vertreterpunkt(linien) for linien in gruppen], zentrum)


def in_region(punkt: Punkt, bbox: list[float]) -> bool:
    """Liegt der Punkt im Ausschnitt? Draussen weist ihn das Backend beim Beitrag ohnehin ab."""
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lat <= punkt[0] <= max_lat and min_lon <= punkt[1] <= max_lon


def main() -> int:
    name, bbox, zentrum = lade_region()
    print(f"Ortsindex fuer {name} bauen (Ortsmitte {zentrum[0]:.5f}, {zentrum[1]:.5f}) ...")

    antwort = frage_overpass(baue_abfrage(bbox))
    elemente = antwort.get("elements", [])
    print(f"  {len(elemente)} Elemente von Overpass erhalten")

    strassenstuecke: dict[str, list[Linie]] = {}
    adressen: dict[str, list[tuple[str, Punkt]]] = {}

    for element in elemente:
        tags = element.get("tags", {})

        # Adressen zuerst, und zwar VOR der Pruefung auf "name": ein Adressknoten hat keinen
        # Namen. Ohne diesen Zweig faellt jede Adresse hier still heraus -- die Abfrage liefe
        # gruen durch und der Index bliebe leer.
        if (adresse := adresse_von(tags)) is not None:
            strasse, nummer = adresse
            punkt = punkt_von(element)
            if punkt is not None and in_region(punkt, bbox):
                adressen.setdefault(strasse, []).append((nummer, punkt))
            continue

        ort_name = (tags.get("name") or "").strip()
        if not ort_name:
            continue

        # Auf den Ausschnitt zuschneiden: Overpass liefert jeden Weg vollstaendig, sobald er die
        # bbox beruehrt. Ein Vertreterpunkt auf dem Stueck ausserhalb waere fuer einen Beitrag
        # unbrauchbar -- das Backend weist ihn ab.
        verlauf = [punkt for punkt in verlauf_von(element) if in_region(punkt, bbox)]
        if verlauf:
            strassenstuecke.setdefault(ort_name, []).append(verlauf)

    orte: list[dict] = []
    fremde_hausnummern = 0

    for ort_name in sorted(strassenstuecke):
        stuecke = strassenstuecke[ort_name]
        gruppen = [[stuecke[i] for i in indizes] for indizes in gruppiere(stuecke)]

        # Jede Hausnummer gehoert zu der gleichnamigen Strasse, die ihr am naechsten liegt. Bei
        # nur einer Gruppe ist nichts zu entscheiden -- und das ist der Normalfall.
        adressen_je_gruppe: list[list[tuple[str, Punkt]]] = [[] for _ in gruppen]
        for nummer, punkt in adressen.get(ort_name, []):
            naechste = min(
                range(len(gruppen)),
                key=lambda k: min(
                    entfernung_m(punkt, stuetz) for linie in gruppen[k] for stuetz in linie
                ),
            )
            adressen_je_gruppe[naechste].append((nummer, punkt))

        gewaehlt = waehle_strasse(gruppen, adressen_je_gruppe, zentrum)
        eigene = adressen_je_gruppe[gewaehlt]
        fremde_hausnummern += sum(len(a) for i, a in enumerate(adressen_je_gruppe) if i != gewaehlt)

        # Der Vertreterpunkt liegt an einem Haus, wenn es eines gibt: Fuer "Wo war das?" ist die
        # mittlere Hausnummer die brauchbarere Antwort als ein Punkt auf der Fahrbahn.
        lat, lon = mittlere_hausnummer(eigene) if eigene else vertreterpunkt(gruppen[gewaehlt])
        orte.append(
            {
                "name": ort_name,
                "name_normalized": normalisiere(ort_name),
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "kind": "strasse",
            }
        )

        for nummer, (adr_lat, adr_lon) in nach_hausnummer(eigene):
            voller_name = f"{ort_name} {nummer}"
            orte.append(
                {
                    "name": voller_name,
                    "name_normalized": normalisiere(voller_name),
                    "lat": round(adr_lat, 7),
                    "lon": round(adr_lon, 7),
                    "kind": "adresse",
                    "street": ort_name,
                    "housenumber": nummer,
                }
            )

    ohne_weg = sorted(set(adressen) - set(strassenstuecke))
    if ohne_weg:
        print(f"  {len(ohne_weg)} Strassen nur als Adresse bekannt, ohne Weg -- weggelassen")
    if fremde_hausnummern:
        print(f"  {fremde_hausnummern} Hausnummern gleichnamiger Strassen anderer Orte entfernt")

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
