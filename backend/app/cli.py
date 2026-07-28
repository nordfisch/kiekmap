"""Command line for bulk import and inspection.

    python -m app.cli import ~/Scans/Kirchweih   take in a directory (originals stay put)
    python -m app.cli scan                       sweep the inbox folder once
    python -m app.cli stats                      what is in there, what is still missing
    python -m app.cli places                     reload the gazetteer
    python -m app.cli pin                        set the PIN for the admin area

The usual route for the museum team is the watched folder; these commands are for the initial fill
with a few thousand scans and for troubleshooting.
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
from app.services.importer import import_directory

log = logging.getLogger("photomap.cli")


def _cmd_import(args: argparse.Namespace) -> int:
    directory = Path(args.path).expanduser().resolve()
    if not directory.is_dir():
        print(f"Kein Verzeichnis: {directory}", file=sys.stderr)
        return 1

    settings = get_settings()
    settings.ensure_dirs()

    with SessionLocal() as session:
        outcomes = import_directory(session, directory, settings)
        session.commit()

    counts = Counter(outcome.result for outcome in outcomes)
    print(f"\n{len(outcomes)} Dateien angesehen:")
    print(f"  aufgenommen  {counts[ImportResult.IMPORTED]}")
    print(f"  Dubletten    {counts[ImportResult.DUPLICATE]}")
    print(f"  abgewiesen   {counts[ImportResult.REJECTED]}")

    for outcome in outcomes:
        if outcome.result == ImportResult.REJECTED:
            print(f"    ! {outcome.message}")

    return 0


def _cmd_scan(_: argparse.Namespace) -> int:
    from app.services.watcher import IncomingWatcher

    watcher = IncomingWatcher()
    # Twice: the first sweep only records file sizes, the second imports whatever has not changed
    # since.
    watcher.scan_once()
    count = watcher.scan_once()
    print(f"{count} Fotos aufgenommen.")
    return 0


def _cmd_stats(_: argparse.Namespace) -> int:
    def count(*filters) -> int:
        return session.scalar(select(func.count()).select_from(Photo).where(*filters)) or 0

    with SessionLocal() as session:
        total = count()
        without_location = count(Photo.lat.is_(None))
        without_date = count(Photo.date_from.is_(None))
        # Only photos with both place and time range appear on the map -- the view filters on
        # both at once.
        on_map = count(Photo.lat.is_not(None), Photo.date_from.is_not(None))

    print(f"Fotos gesamt            {total}")
    print(f"  auf der Karte         {on_map}")
    print(f"  ohne Ort              {without_location}")
    print(f"  ohne Jahr             {without_date}")
    if total:
        print(f"\n{100 * on_map // total} % sind vollstaendig genug fuer die Karte.")
    return 0


def _cmd_places(_: argparse.Namespace) -> int:
    from app.services.places import load_from_file

    settings = get_settings()
    with SessionLocal() as session:
        count = load_from_file(session, settings.places_file)

    if count:
        print(f"{count} Orte geladen.")
    else:
        print(f"Nichts geladen -- {settings.places_file} fehlt.")
        print("Erzeugen mit: python3 tiles/build-places.py")
    return 0


def _cmd_pin(_: argparse.Namespace) -> int:
    """Ask for a PIN twice and print the line that belongs in the .env file.

    Deliberately not written to the file automatically: the .env may hold other settings, and
    whoever sets up the device should see what they are pasting.
    """
    from getpass import getpass

    from app.services.auth import MAX_PIN_LENGTH, MIN_PIN_LENGTH, hash_pin, is_valid_pin

    print(f"PIN fuer den Admin-Bereich, {MIN_PIN_LENGTH} bis {MAX_PIN_LENGTH} Ziffern.")
    print("Die Eingabe ist nicht zu sehen.\n")

    pin = getpass("PIN:            ")
    if not is_valid_pin(pin):
        print(
            f"\nNur Ziffern, {MIN_PIN_LENGTH} bis {MAX_PIN_LENGTH} Stueck -- "
            "auf dem Tastenfeld im Museum gibt es keine Buchstaben.",
            file=sys.stderr,
        )
        return 1
    if getpass("Noch einmal:    ") != pin:
        print("\nDie beiden Eingaben sind nicht gleich.", file=sys.stderr)
        return 1

    print("\nDiese Zeile in die Datei .env eintragen (vorhandene ersetzen):\n")
    print(f"PHOTOMAP_ADMIN_PIN_HASH={hash_pin(pin)}\n")
    print("Danach den Dienst neu starten. Die PIN selbst wird nirgends gespeichert.")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")

    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    p_import = commands.add_parser("import", help="Verzeichnis aufnehmen")
    p_import.add_argument("path")
    p_import.set_defaults(handler=_cmd_import)

    p_scan = commands.add_parser("scan", help="Eingangsordner einmal durchsehen")
    p_scan.set_defaults(handler=_cmd_scan)

    p_stats = commands.add_parser("stats", help="Bestand und Luecken")
    p_stats.set_defaults(handler=_cmd_stats)

    p_places = commands.add_parser("places", help="Ortsverzeichnis neu laden")
    p_places.set_defaults(handler=_cmd_places)

    p_pin = commands.add_parser("pin", help="PIN fuer den Admin-Bereich setzen")
    p_pin.set_defaults(handler=_cmd_pin)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
