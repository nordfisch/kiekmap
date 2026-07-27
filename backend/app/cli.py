"""Kommandozeile fuer den Massenimport.

    python -m app.cli import ~/Scans/Kirchweih     Verzeichnis aufnehmen (Originale bleiben liegen)
    python -m app.cli scan                         Eingangsordner einmal durchsehen
    python -m app.cli stats                        Was ist drin, was fehlt noch

Der uebliche Weg fuer das Museumsteam ist der ueberwachte Ordner; diese Kommandos sind fuer die
erste Befuellung mit ein paar tausend Scans und fuer die Fehlersuche.
"""

import argparse
import logging
import sys
from collections import Counter
from pathlib import Path

from sqlalchemy import func, select

from app.config import get_settings
from app.db import SessionLocal
from app.models import ImportResult, Photo
from app.services.importer import importiere_verzeichnis

log = logging.getLogger("photomap.cli")


def _befehl_import(argumente: argparse.Namespace) -> int:
    verzeichnis = Path(argumente.pfad).expanduser().resolve()
    if not verzeichnis.is_dir():
        print(f"Kein Verzeichnis: {verzeichnis}", file=sys.stderr)
        return 1

    settings = get_settings()
    settings.ensure_dirs()

    with SessionLocal() as session:
        ergebnisse = importiere_verzeichnis(session, verzeichnis, settings)
        session.commit()

    zaehler = Counter(e.result for e in ergebnisse)
    print(f"\n{len(ergebnisse)} Dateien angesehen:")
    print(f"  aufgenommen  {zaehler[ImportResult.IMPORTED]}")
    print(f"  Dubletten    {zaehler[ImportResult.DUPLICATE]}")
    print(f"  abgewiesen   {zaehler[ImportResult.REJECTED]}")

    for ergebnis in ergebnisse:
        if ergebnis.result == ImportResult.REJECTED:
            print(f"    ! {ergebnis.message}")

    return 0


def _befehl_scan(_: argparse.Namespace) -> int:
    from app.services.watcher import Eingangswaechter

    waechter = Eingangswaechter()
    # Zweimal: der erste Durchlauf merkt sich nur die Groessen, der zweite importiert, was sich
    # seither nicht geaendert hat.
    waechter.durchlauf()
    anzahl = waechter.durchlauf()
    print(f"{anzahl} Fotos aufgenommen.")
    return 0


def _befehl_stats(_: argparse.Namespace) -> int:
    def zaehle(*bedingungen) -> int:
        return session.scalar(select(func.count()).select_from(Photo).where(*bedingungen)) or 0

    with SessionLocal() as session:
        gesamt = zaehle()
        ohne_ort = zaehle(Photo.lat.is_(None))
        ohne_datum = zaehle(Photo.date_from.is_(None))
        # Nur Fotos mit Ort *und* Zeitraum erscheinen auf der Karte -- die Ansicht filtert ueber
        # beides zugleich.
        auf_der_karte = zaehle(Photo.lat.is_not(None), Photo.date_from.is_not(None))

    print(f"Fotos gesamt            {gesamt}")
    print(f"  auf der Karte         {auf_der_karte}")
    print(f"  ohne Ort              {ohne_ort}")
    print(f"  ohne Jahr             {ohne_datum}")
    if gesamt:
        print(f"\n{100 * auf_der_karte // gesamt} % sind vollstaendig genug fuer die Karte.")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")

    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__)
    unterbefehle = parser.add_subparsers(dest="befehl", required=True)

    p_import = unterbefehle.add_parser("import", help="Verzeichnis aufnehmen")
    p_import.add_argument("pfad")
    p_import.set_defaults(funktion=_befehl_import)

    p_scan = unterbefehle.add_parser("scan", help="Eingangsordner einmal durchsehen")
    p_scan.set_defaults(funktion=_befehl_scan)

    p_stats = unterbefehle.add_parser("stats", help="Bestand und Luecken")
    p_stats.set_defaults(funktion=_befehl_stats)

    argumente = parser.parse_args(argv)
    return argumente.funktion(argumente)


if __name__ == "__main__":
    raise SystemExit(main())
