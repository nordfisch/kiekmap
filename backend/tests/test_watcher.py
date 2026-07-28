from pathlib import Path

from sqlalchemy import select

from app.models import Photo
from app.services.watcher import IncomingWatcher


def test_wartet_bis_die_datei_fertig_geschrieben_ist(
    session, settings, sample_image, fixtures_dir: Path
):
    """Der Fall, der eine ereignisgesteuerte Ueberwachung stolpern laesst.

    Ein grosses TIFF, ueber das Netz kopiert, existiert lange bevor es vollstaendig ist. Wer beim
    ersten Lebenszeichen zugreift, importiert ein halbes Bild.
    """
    watcher = IncomingWatcher(settings, interval=0)
    vollstaendig = (fixtures_dir / "scan_ohne_exif.jpg").read_bytes()
    ziel = settings.incoming_dir / "wird_gerade_kopiert.jpg"

    # Erst die Haelfte -- der Kopiervorgang laeuft noch.
    ziel.write_bytes(vollstaendig[: len(vollstaendig) // 2])
    assert watcher.scan_once() == 0, "unfertige Datei darf nicht angefasst werden"

    # Naechster Blick: die Groesse hat sich geaendert, also weiter warten.
    ziel.write_bytes(vollstaendig)
    assert watcher.scan_once() == 0

    # Jetzt ist die Groesse stabil.
    assert watcher.scan_once() == 1
    assert session.scalar(select(Photo).where(Photo.original_filename == ziel.name))


def test_leere_datei_wird_nie_importiert(session, settings):
    watcher = IncomingWatcher(settings, interval=0)
    (settings.incoming_dir / "leer.jpg").touch()

    assert watcher.scan_once() == 0
    assert watcher.scan_once() == 0


def test_leerer_ordner_ist_kein_fehler(session, settings):
    assert IncomingWatcher(settings, interval=0).scan_once() == 0


def test_import_laeuft_ohne_zutun_durch(session, settings, fixtures_dir: Path):
    watcher = IncomingWatcher(settings, interval=0)
    for name in ("scan_ohne_exif.jpg", "hochkant.jpg"):
        (settings.incoming_dir / name).write_bytes((fixtures_dir / name).read_bytes())

    watcher.scan_once()  # Groessen merken
    assert watcher.scan_once() == 2
    assert len(session.scalars(select(Photo)).all()) == 2
