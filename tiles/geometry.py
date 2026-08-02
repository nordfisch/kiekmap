"""Die Rechnung hinter dem Ortsindex: Gruppieren gleichnamiger Wege und ihr Vertreterpunkt.

Als eigenes Modul, weil beide Fehler, die hier lauern, **still** passieren -- der Index wird
gebaut, das Skript laeuft gruen durch, und erst im Museum tippt jemand auf "Hauptstrasse" und
bekommt einen Punkt zwei Kilometer weiter.

Der Ausschnitt einer Region reicht ueber den Museumsort hinaus, also liegen darin mehrere Doerfer
und damit mehrere Strassen desselben Namens. Fruehere Fassungen mittelten sie zu einem Punkt, der
dann auf keiner von ihnen lag.

Alle Koordinaten sind ``(lat, lon)`` in Grad.
"""

import math
from itertools import pairwise

Punkt = tuple[float, float]
Linie = list[Punkt]

#: Ein Grad Breite in Metern. Fuer Entfernungen innerhalb einer Gemeinde genau genug -- hier wird
#: verglichen und nicht vermessen.
M_JE_GRAD = 111_320.0

#: Ab welchem Abstand zwei gleichnamige Wege als zwei verschiedene Strassen gelten.
#:
#: Zusammenhaengende Stuecke derselben Strasse teilen ihre Endpunkte, liegen also 0 m auseinander;
#: zwei Doerfer trennen Kilometer. Die 150 m sind der grosszuegige Abstand dazwischen: Auch eine
#: Strasse, die eine Kreuzung ueberspringt, bleibt damit eine.
TRENNUNG_M = 150.0


def entfernung_m(a: Punkt, b: Punkt) -> float:
    """Abstand zweier Punkte in Metern, aequirektangulaer genaehert."""
    mittlere_breite = math.radians((a[0] + b[0]) / 2)
    d_lat = (a[0] - b[0]) * M_JE_GRAD
    d_lon = (a[1] - b[1]) * M_JE_GRAD * math.cos(mittlere_breite)
    return math.hypot(d_lat, d_lon)


def _naechster_auf_strecke(anfang: Punkt, ende: Punkt, ziel: Punkt) -> Punkt:
    """Der Punkt auf der Strecke ``anfang``–``ende``, der ``ziel`` am naechsten liegt.

    Die Projektion wird auf die Strecke geklammert; ausserhalb liegt der naechste Punkt auf einem
    der beiden Enden.
    """
    breite = math.radians(ziel[0])
    # In ein lokales Meterraster, sonst verzerrt der Laengengrad die Projektion.
    ax, ay = anfang[1] * math.cos(breite), anfang[0]
    bx, by = ende[1] * math.cos(breite), ende[0]
    zx, zy = ziel[1] * math.cos(breite), ziel[0]

    dx, dy = bx - ax, by - ay
    laenge = dx * dx + dy * dy
    if laenge == 0:
        return anfang

    anteil = ((zx - ax) * dx + (zy - ay) * dy) / laenge
    anteil = max(0.0, min(1.0, anteil))
    return (
        anfang[0] + anteil * (ende[0] - anfang[0]),
        anfang[1] + anteil * (ende[1] - anfang[1]),
    )


def vertreterpunkt(linien: list[Linie]) -> Punkt:
    """Ein Punkt **auf** dem Weg, moeglichst in seiner Mitte.

    Erst der Schwerpunkt aller Stuetzpunkte, dann der Punkt der Linie, der ihm am naechsten liegt.
    Bei einer geraden Strasse ist das ihre Mitte; bei einer gebogenen oder L-foermigen der Punkt
    der Fahrbahn, der der Mitte am naechsten kommt.

    Der Schwerpunkt allein taugt nicht: Genau er ist die Mitte des umschliessenden Rechtecks und
    liegt bei einer krummen Strasse neben ihr -- im ungluecklichen Fall auf einem Grundstueck.
    """
    stuetzpunkte = [punkt for linie in linien for punkt in linie]
    if not stuetzpunkte:
        raise ValueError("vertreterpunkt braucht mindestens einen Punkt")

    schwerpunkt = (
        sum(p[0] for p in stuetzpunkte) / len(stuetzpunkte),
        sum(p[1] for p in stuetzpunkte) / len(stuetzpunkte),
    )

    bester = stuetzpunkte[0]
    kleinster_abstand = entfernung_m(bester, schwerpunkt)
    for linie in linien:
        for anfang, ende in pairwise(linie):
            kandidat = _naechster_auf_strecke(anfang, ende, schwerpunkt)
            abstand = entfernung_m(kandidat, schwerpunkt)
            if abstand < kleinster_abstand:
                bester, kleinster_abstand = kandidat, abstand
    return bester


def _kasten(linie: Linie) -> tuple[float, float, float, float]:
    """Das umschliessende Rechteck (min_lat, min_lon, max_lat, max_lon)."""
    lats = [p[0] for p in linie]
    lons = [p[1] for p in linie]
    return (min(lats), min(lons), max(lats), max(lons))


def _kaesten_nah(a: tuple, b: tuple, abstand_m: float) -> bool:
    """Koennen sich zwei Rechtecke naeher als ``abstand_m`` kommen? Grob, aber nie zu streng."""
    d_lat = max(0.0, a[0] - b[2], b[0] - a[2]) * M_JE_GRAD
    breite = math.radians((a[0] + b[0]) / 2)
    d_lon = max(0.0, a[1] - b[3], b[1] - a[3]) * M_JE_GRAD * math.cos(breite)
    return math.hypot(d_lat, d_lon) <= abstand_m


def gruppiere(linien: list[Linie], trennung_m: float = TRENNUNG_M) -> list[list[int]]:
    """Gleichnamige Wege in raeumlich getrennte Gruppen zerlegen.

    Gibt Listen von Indizes in ``linien`` zurueck. Zwei Wege landen in derselben Gruppe, wenn
    irgendein Stuetzpunkt des einen naeher als ``trennung_m`` an einem des anderen liegt -- und
    transitiv ueber alles, was dadurch verbunden ist. Eine Strasse aus zwanzig Stuecken bleibt so
    eine, auch wenn ihre Enden einen Kilometer trennen.
    """
    eltern = list(range(len(linien)))
    kaesten = [_kasten(linie) for linie in linien]

    def wurzel(i: int) -> int:
        while eltern[i] != i:
            eltern[i] = eltern[eltern[i]]
            i = eltern[i]
        return i

    def verbinde(a: int, b: int) -> None:
        wa, wb = wurzel(a), wurzel(b)
        if wa != wb:
            eltern[wb] = wa

    for i in range(len(linien)):
        for j in range(i + 1, len(linien)):
            if wurzel(i) == wurzel(j):
                continue
            # Erst die umschliessenden Rechtecke: Der punktweise Vergleich ist quadratisch, und
            # gerade die weit entfernten Paare -- die haeufigsten -- laufen sonst komplett durch.
            if not _kaesten_nah(kaesten[i], kaesten[j], trennung_m):
                continue
            if any(entfernung_m(p, q) <= trennung_m for p in linien[i] for q in linien[j]):
                verbinde(i, j)

    gruppen: dict[int, list[int]] = {}
    for i in range(len(linien)):
        gruppen.setdefault(wurzel(i), []).append(i)
    return list(gruppen.values())


def naechste_gruppe(kandidaten: list[Punkt], zentrum: Punkt) -> int:
    """Welcher Kandidat liegt dem Ortsmittelpunkt am naechsten? Gibt den Index zurueck.

    So entscheidet sich, welche von siebzehn "Hauptstrassen" im Ausschnitt die des Museumsortes
    ist -- ohne dass der Ortsname im Code steht. ``zentrum`` kommt aus ``tiles/region.json``.
    """
    if not kandidaten:
        raise ValueError("naechste_gruppe braucht mindestens einen Kandidaten")
    return min(range(len(kandidaten)), key=lambda i: entfernung_m(kandidaten[i], zentrum))


def hausnummer_schluessel(nummer: str) -> tuple[int, str]:
    """Hausnummern so ordnen, wie ein Briefträger geht -- nicht, wie ein Rechner sortiert.

    Alphabetisch stuende "10" vor "9" und "1a" vor "2". Der Schluessel ist (fuehrende Zahl, Rest),
    damit 1, 1a, 2, 9, 10, 12 in dieser Reihenfolge herauskommen.

    **Muss mit ``sort_key`` in ``backend/app/services/places.py`` uebereinstimmen**, sonst ordnet
    der Kiosk die Knoepfe anders, als dieses Skript die Mitte bestimmt hat.
    """
    ziffern = ""
    for zeichen in nummer:
        if not zeichen.isdigit():
            break
        ziffern += zeichen
    return (int(ziffern) if ziffern else 0, nummer[len(ziffern) :].lower())


def nach_hausnummer(adressen: list[tuple[str, Punkt]]) -> list[tuple[str, Punkt]]:
    """Adressen in Gehreihenfolge. ``adressen`` ist eine Liste aus (Hausnummer, Punkt)."""
    return sorted(adressen, key=lambda eintrag: hausnummer_schluessel(eintrag[0]))


def mittlere_hausnummer(adressen: list[tuple[str, Punkt]]) -> Punkt:
    """Der Punkt der mittleren Hausnummer -- der Vertreter einer Strasse, die Adressen hat.

    Besser als jede gerechnete Mitte: Der Punkt liegt an einem Haus statt auf der Fahrbahn, und
    fuer "Wo war das?" ist ein Haus die brauchbarere Antwort. Bei gerader Anzahl gewinnt die
    kleinere der beiden mittleren -- eine Wahl muss getroffen werden, und sie ist ohne Folgen.
    """
    if not adressen:
        raise ValueError("mittlere_hausnummer braucht mindestens eine Adresse")
    geordnet = nach_hausnummer(adressen)
    return geordnet[(len(geordnet) - 1) // 2][1]


def niedrigste_hausnummer(adressen: list[tuple[str, Punkt]]) -> Punkt:
    """Der Punkt der niedrigsten Hausnummer -- er entscheidet bei gleichnamigen Strassen.

    Die Hausnummer 1 liegt in einem gewachsenen Dorf am Ortskern; welche gleichnamige Strasse zum
    Museumsort gehoert, laesst sich daran zuverlaessiger ablesen als an ihrer Mitte, denn eine
    lange Strasse fuehrt aus dem Ort heraus und zieht ihre Mitte mit.
    """
    if not adressen:
        raise ValueError("niedrigste_hausnummer braucht mindestens eine Adresse")
    return nach_hausnummer(adressen)[0][1]
