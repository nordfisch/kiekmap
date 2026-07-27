"""Unscharfe Datierung.

Bei historischen Fotos ist "1920er" oder "um 1930" der Normalfall, nicht die Ausnahme. Deshalb
speichert jedes Foto ein Intervall statt eines Zeitpunkts, und der Zeitraum-Filter fragt auf
Ueberlappung ab.

Der Fallstrick, den das vermeidet: Bei naiver Abfrage ("Datum liegt zwischen von und bis")
verschwinden genau die unscharf datierten Fotos aus der Ansicht -- also die interessanten. Das
passiert ohne Fehlermeldung, weshalb es dafuer eigene Tests gibt.
"""

import calendar
from datetime import date

from app.models import DatePrecision

MONATSNAMEN = (
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)


def zeitraum(
    jahr: int | None,
    monat: int | None = None,
    tag: int | None = None,
    genauigkeit: DatePrecision | None = None,
) -> tuple[date | None, date | None, DatePrecision]:
    """Rechnet eine Angabe in ein Intervall um.

    Ohne ``genauigkeit`` ergibt sie sich aus dem, was angegeben wurde. Bei ``DECADE`` wird das Jahr
    auf den Jahrzehntbeginn abgerundet, damit "1934, Jahrzehnt" zu 1930-1939 wird und nicht zu
    1934-1943.
    """
    if jahr is None:
        return None, None, DatePrecision.UNKNOWN

    if genauigkeit is None:
        if tag is not None and monat is not None:
            genauigkeit = DatePrecision.DAY
        elif monat is not None:
            genauigkeit = DatePrecision.MONTH
        else:
            genauigkeit = DatePrecision.YEAR

    match genauigkeit:
        case DatePrecision.DAY:
            if monat is None or tag is None:
                raise ValueError("Tagesgenauigkeit braucht Monat und Tag")
            genau = date(jahr, monat, tag)
            return genau, genau, DatePrecision.DAY

        case DatePrecision.MONTH:
            if monat is None:
                raise ValueError("Monatsgenauigkeit braucht einen Monat")
            letzter = calendar.monthrange(jahr, monat)[1]
            return date(jahr, monat, 1), date(jahr, monat, letzter), DatePrecision.MONTH

        case DatePrecision.YEAR:
            return date(jahr, 1, 1), date(jahr, 12, 31), DatePrecision.YEAR

        case DatePrecision.DECADE:
            beginn = jahr - jahr % 10
            return date(beginn, 1, 1), date(beginn + 9, 12, 31), DatePrecision.DECADE

        case DatePrecision.UNKNOWN:
            return None, None, DatePrecision.UNKNOWN

    raise ValueError(f"Unbekannte Genauigkeit: {genauigkeit}")


def beschriftung(von: date | None, bis: date | None, genauigkeit: str | DatePrecision) -> str:
    """Wie die Datierung dem Besucher gezeigt wird."""
    if von is None:
        return "Jahr unbekannt"

    match DatePrecision(genauigkeit):
        case DatePrecision.DAY:
            return f"{von.day}. {MONATSNAMEN[von.month - 1]} {von.year}"
        case DatePrecision.MONTH:
            return f"{MONATSNAMEN[von.month - 1]} {von.year}"
        case DatePrecision.YEAR:
            return str(von.year)
        case DatePrecision.DECADE:
            return f"{von.year}er"
        case _:
            # Sollte mit von != None nicht vorkommen; lieber etwas Brauchbares zeigen als leer.
            return (
                str(von.year) if bis is None or bis.year == von.year else f"{von.year}–{bis.year}"
            )


def ueberlappt(von: date | None, bis: date | None, auswahl_von: date, auswahl_bis: date) -> bool:
    """Reines Python-Gegenstueck zur SQL-Abfrage -- fuer Tests und zur Erlaeuterung.

    Zwei Intervalle ueberlappen, wenn keines vollstaendig vor dem anderen liegt. Ein Foto ohne
    Datierung ueberlappt nie: es taucht in keiner Zeitraumauswahl auf, sondern im
    "Hilf mit"-Bereich.
    """
    if von is None or bis is None:
        return False
    return von <= auswahl_bis and bis >= auswahl_von
