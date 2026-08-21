# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Command line for bulk import and inspection.

    python -m app.cli import ~/Scans/Kirchweih   take in a directory (originals stay put)
    python -m app.cli scan                       sweep the inbox folder once
    python -m app.cli stats                      what is in there, what is still missing
    python -m app.cli dubletten                  the same picture more than once
    python -m app.cli places                     reload the gazetteer
    python -m app.cli pin                        set the PIN for the admin area
    python -m app.cli seed-export                write the collection out to seed/
    python -m app.cli seed-load                  empty it and rebuild it from seed/
    python -m app.cli empty                      throw the whole collection away

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
from app.models import ImportResult, Photo, PhotoStatus
from app.services.importer import import_directory

log = logging.getLogger("kiekmap.cli")


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

    # Deleted photos count in none of these: they are out of the exhibition. Same convention as
    # the admin overview, so that the two never disagree in front of the same person.
    alive = Photo.status != PhotoStatus.DELETED

    with SessionLocal() as session:
        total = count(alive)
        without_location = count(alive, Photo.lat.is_(None))
        without_date = count(alive, Photo.date_from.is_(None))
        # A place is enough; an undated photo is on the map as long as no time filter is set,
        # and normally none is. Same count as the admin overview -- see api/admin.py.
        on_map = count(Photo.status == PhotoStatus.PUBLISHED, Photo.lat.is_not(None))
        deleted = count(Photo.status == PhotoStatus.DELETED)

    print(f"Fotos gesamt            {total}")
    print(f"  auf der Karte         {on_map}")
    print(f"  ohne Ort              {without_location}")
    print(f"  ohne Jahr             {without_date}")
    if deleted:
        print(f"  geloescht             {deleted}")
    if total:
        print(f"\n{100 * on_map // total} % haben einen Ort und stehen damit auf der Karte.")
    return 0


def _cmd_duplicates(args: argparse.Namespace) -> int:
    from app.services.similar import candidate_groups

    settings = get_settings()
    with SessionLocal() as session:
        groups = candidate_groups(session, settings, limit=args.abstand)

    total = sum(len(group) for group in groups)
    print(f"{len(groups)} Gruppen, {total} Fotos, Abstand bis {args.abstand}\n")
    for number, group in enumerate(groups, 1):
        print(f"--- Gruppe {number} ({len(group)} Fotos) ---")
        for photo in group:
            year = str(photo.date_from)[:4] if photo.date_from else "----"
            print(
                f"  Foto {photo.id:5} {photo.width:5}x{photo.height:<5} {year}"
                f"  {str(photo.place_name)[:24]:26} {str(photo.title)[:34]}"
            )
        print()

    if groups:
        print("Das groesste Bild ist der uebliche, nicht immer der richtige Kandidat zum")
        print("Behalten -- ein Bildtext kann auf der kleineren Fassung stehen. Bitte ansehen.")
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


def _cmd_seed_export(_: argparse.Namespace) -> int:
    from app.services import seed

    settings = get_settings()
    target = seed.seed_dir(settings)

    with SessionLocal() as session:
        photos, contributions = seed.export(session, settings, target)

    print(f"{photos} Fotos und {contributions} Besucherbeitraege nach {target} geschrieben.")
    print("Zurueckspielen mit: make seed")
    # The collection in the repo is invented; this one probably is not.
    print("\nAchtung: Der Beispielbestand im Repo ist erfunden. Echte Fotos gehoeren nicht")
    print("in einen Commit -- siehe seed/README.md.")
    return 0


def _cmd_seed_load(_: argparse.Namespace) -> int:
    """Throws the collection away and rebuilds it. That is the point, so it says so first."""
    from app.services import seed

    settings = get_settings()
    settings.ensure_dirs()
    source = seed.seed_dir(settings)

    with SessionLocal() as session:
        try:
            photos, contributions = seed.load(session, settings, source)
        except FileNotFoundError:
            print(f"Kein Beispielbestand unter {source}.", file=sys.stderr)
            print("Was dort hingehoert, steht in seed/README.md.", file=sys.stderr)
            print("Einen eigenen anlegen: python -m app.cli seed-export", file=sys.stderr)
            return 1
        session.commit()

    print(f"{photos} Fotos und {contributions} Besucherbeitraege eingelesen.")
    print("Erfundener Beispielbestand -- siehe seed/README.md.")
    return 0


def _cmd_empty(args: argparse.Namespace) -> int:
    """Throw the whole collection away, before an initial import.

    The one command here from which there is no way back. ``seed-load`` also empties the
    collection, but it puts something in its place; this leaves nothing. So it says what it is
    about to destroy, in numbers, and **asks for the number of photos to be typed back**. A "j/n"
    can be answered without reading -- a number cannot.
    """
    from app.models import Change
    from app.services import seed

    settings = get_settings()
    settings.ensure_dirs()

    with SessionLocal() as session:
        photos = session.scalar(select(func.count()).select_from(Photo)) or 0
        contributions = session.scalar(select(func.count()).select_from(Change)) or 0

        if not photos:
            print("Der Bestand ist schon leer.")
            return 0

        print(f"Im Bestand: {photos} Fotos und {contributions} Besucherbeitraege.")
        print("Geloescht werden Zeilen, Originale und Vorschaubilder -- restlos.")
        print("Ortsverzeichnis, Karte und Einstellungen bleiben.\n")
        print("Zurueckholen laesst sich das nur aus einer Sicherung:")
        print("  make seed-save    fuer den Entwicklungsbestand")
        print("  Verwaltung -> Sicherung   fuer den echten Bestand\n")

        if not args.yes:
            antwort = input(f"Zum Bestaetigen die Anzahl der Fotos eingeben ({photos}): ")
            if antwort.strip() != str(photos):
                print("\nAbgebrochen, es wurde nichts geloescht.")
                return 1

        seed.clear(session, settings)
        session.commit()

    print(f"\n{photos} Fotos geloescht. Der Bestand ist leer.")
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
    print(f"KIEKMAP_ADMIN_PIN_HASH={hash_pin(pin)}\n")
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

    p_duplicates = commands.add_parser("dubletten", help="Dasselbe Bild mehrfach im Bestand")
    p_duplicates.add_argument(
        "--abstand",
        type=int,
        default=40,
        help="Wie viele der 256 Bit abweichen duerfen (Vorgabe 40)",
    )
    p_duplicates.set_defaults(handler=_cmd_duplicates)

    p_places = commands.add_parser("places", help="Ortsverzeichnis neu laden")
    p_places.set_defaults(handler=_cmd_places)

    p_pin = commands.add_parser("pin", help="PIN fuer den Admin-Bereich setzen")
    p_pin.set_defaults(handler=_cmd_pin)

    p_seed_export = commands.add_parser("seed-export", help="Bestand nach seed/ sichern")
    p_seed_export.set_defaults(handler=_cmd_seed_export)

    p_seed_load = commands.add_parser("seed-load", help="Bestand aus seed/ wiederherstellen")
    p_seed_load.set_defaults(handler=_cmd_seed_load)

    p_empty = commands.add_parser("empty", help="Den ganzen Bestand loeschen")
    p_empty.add_argument(
        "--yes",
        action="store_true",
        help="Ohne Rueckfrage loeschen -- nur fuer Skripte",
    )
    p_empty.set_defaults(handler=_cmd_empty)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
