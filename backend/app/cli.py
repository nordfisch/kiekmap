"""Command line for bulk import and inspection.

    python -m app.cli import ~/Scans/Kirchweih   take in a directory (originals stay put)
    python -m app.cli scan                       sweep the inbox folder once
    python -m app.cli stats                      what is in there, what is still missing
    python -m app.cli duplicates                 the same picture more than once
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
        print(f"Not a directory: {directory}", file=sys.stderr)
        return 1

    settings = get_settings()
    settings.ensure_dirs()

    with SessionLocal() as session:
        outcomes = import_directory(session, directory, settings)
        session.commit()

    counts = Counter(outcome.result for outcome in outcomes)
    print(f"\n{len(outcomes)} files looked at:")
    print(f"  taken in    {counts[ImportResult.IMPORTED]}")
    print(f"  duplicates  {counts[ImportResult.DUPLICATE]}")
    print(f"  rejected    {counts[ImportResult.REJECTED]}")

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
    print(f"{count} photos taken in.")
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

    print(f"Photos in total       {total}")
    print(f"  on the map          {on_map}")
    print(f"  without a place     {without_location}")
    print(f"  without a year      {without_date}")
    if deleted:
        print(f"  deleted             {deleted}")
    if total:
        print(f"\n{100 * on_map // total} % have a place and are therefore on the map.")
    return 0


def _cmd_duplicates(args: argparse.Namespace) -> int:
    from app.services.similar import candidate_groups

    settings = get_settings()
    with SessionLocal() as session:
        groups = candidate_groups(session, settings, limit=args.distance)

    total = sum(len(group) for group in groups)
    print(f"{len(groups)} groups, {total} photos, distance up to {args.distance}\n")
    for number, group in enumerate(groups, 1):
        print(f"--- group {number} ({len(group)} photos) ---")
        for photo in group:
            year = str(photo.date_from)[:4] if photo.date_from else "----"
            print(
                f"  photo {photo.id:5} {photo.width:5}x{photo.height:<5} {year}"
                f"  {str(photo.place_name)[:24]:26} {str(photo.title)[:34]}"
            )
        print()

    if groups:
        print("The largest image is the usual candidate to keep, not always the right one --")
        print("a caption may sit on the smaller version. Please look at them.")
    return 0


def _cmd_places(_: argparse.Namespace) -> int:
    from app.services.places import load_from_file

    settings = get_settings()
    with SessionLocal() as session:
        count = load_from_file(session, settings.places_file)

    if count:
        print(f"{count} places loaded.")
    else:
        print(f"Nothing loaded -- {settings.places_file} is missing.")
        print("Build it with: python3 tiles/build-places.py")
    return 0


def _cmd_seed_export(_: argparse.Namespace) -> int:
    from app.services import seed

    settings = get_settings()
    target = seed.seed_dir(settings)

    with SessionLocal() as session:
        photos, contributions = seed.export(session, settings, target)

    print(f"{photos} photos and {contributions} visitor contributions written to {target}.")
    print("Read them back with: make seed")
    # The collection in the repo is invented; this one probably is not.
    print("\nCareful: the sample collection in the repository is invented. Real photos do not")
    print("belong in a commit -- see seed/README.md.")
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
            print(f"No sample collection under {source}.", file=sys.stderr)
            print("What belongs there is described in seed/README.md.", file=sys.stderr)
            print("Create one of your own: python -m app.cli seed-export", file=sys.stderr)
            return 1
        session.commit()

    print(f"{photos} photos and {contributions} visitor contributions read in.")
    print("An invented sample collection -- see seed/README.md.")
    return 0


def _cmd_empty(args: argparse.Namespace) -> int:
    """Throw the whole collection away, before an initial import.

    The one command here from which there is no way back. ``seed-load`` also empties the
    collection, but it puts something in its place; this leaves nothing. So it says what it is
    about to destroy, in numbers, and **asks for the number of photos to be typed back**. A "y/n"
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
            print("The collection is empty already.")
            return 0

        print(f"In the collection: {photos} photos and {contributions} visitor contributions.")
        print("Rows, originals and thumbnails will be deleted -- all of them.")
        print("Gazetteer, map and settings stay.\n")
        print("Only a backup brings this back:")
        print("  make seed-save             for the development collection")
        print("  admin view -> backup       for the real one\n")

        if not args.yes:
            answer = input(f"To confirm, type the number of photos ({photos}): ")
            if answer.strip() != str(photos):
                print("\nCancelled, nothing was deleted.")
                return 1

        seed.clear(session, settings)
        session.commit()

    print(f"\n{photos} photos deleted. The collection is empty.")
    return 0


def _cmd_pin(_: argparse.Namespace) -> int:
    """Ask for a PIN twice and print the line that belongs in the .env file.

    Deliberately not written to the file automatically: the .env may hold other settings, and
    whoever sets up the device should see what they are pasting.
    """
    from getpass import getpass

    from app.services.auth import MAX_PIN_LENGTH, MIN_PIN_LENGTH, hash_pin, is_valid_pin

    print(f"PIN for the admin area, {MIN_PIN_LENGTH} to {MAX_PIN_LENGTH} digits.")
    print("The input stays invisible.\n")

    pin = getpass("PIN:           ")
    if not is_valid_pin(pin):
        print(
            f"\nDigits only, {MIN_PIN_LENGTH} to {MAX_PIN_LENGTH} of them -- "
            "the keypad in the museum has no letters.",
            file=sys.stderr,
        )
        return 1
    if getpass("Once again:    ") != pin:
        print("\nThe two inputs differ.", file=sys.stderr)
        return 1

    print("\nPut this line into the .env file, replacing an existing one:\n")
    print(f"KIEKMAP_ADMIN_PIN_HASH={hash_pin(pin)}\n")
    print("Then restart the service. The PIN itself is stored nowhere.")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")

    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    p_import = commands.add_parser("import", help="take in a directory")
    p_import.add_argument("path")
    p_import.set_defaults(handler=_cmd_import)

    p_scan = commands.add_parser("scan", help="sweep the inbox folder once")
    p_scan.set_defaults(handler=_cmd_scan)

    p_stats = commands.add_parser("stats", help="the collection and its gaps")
    p_stats.set_defaults(handler=_cmd_stats)

    p_duplicates = commands.add_parser("duplicates", help="the same picture more than once")
    p_duplicates.add_argument(
        "--distance",
        type=int,
        default=40,
        help="how many of the 256 bits may differ (default 40)",
    )
    p_duplicates.set_defaults(handler=_cmd_duplicates)

    p_places = commands.add_parser("places", help="reload the gazetteer")
    p_places.set_defaults(handler=_cmd_places)

    p_pin = commands.add_parser("pin", help="set the PIN for the admin area")
    p_pin.set_defaults(handler=_cmd_pin)

    p_seed_export = commands.add_parser("seed-export", help="save the collection to seed/")
    p_seed_export.set_defaults(handler=_cmd_seed_export)

    p_seed_load = commands.add_parser("seed-load", help="restore the collection from seed/")
    p_seed_load.set_defaults(handler=_cmd_seed_load)

    p_empty = commands.add_parser("empty", help="delete the whole collection")
    p_empty.add_argument(
        "--yes",
        action="store_true",
        help="delete without asking -- for scripts only",
    )
    p_empty.set_defaults(handler=_cmd_empty)

    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
