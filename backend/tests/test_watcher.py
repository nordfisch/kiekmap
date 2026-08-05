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


class TestOrdnernamen:
    """Der Eingangsordner ist der uebliche Weg des Museumsteams -- und las die Ordner nicht mit.

    929 Fotos kamen so herein: Strasse und Hausnummer standen im Pfad und danach nirgends in der
    Datenbank. Kein Ort, kein Titel, keine Herkunft, keine Schlagwoerter. Aufgefallen ist es erst
    an der fertigen Karte, weil die Metadaten-Schicht sauber lief und der Bestand deshalb nicht
    kaputt *aussah* -- nur leer.

    Die Ursache war nicht die vergessene Zeile, sondern dass sie vergessen werden konnte: Die
    Pfad-Schicht hing am Aufrufer. Sie haengt jetzt am ``root``-Parameter von ``import_file``.
    """

    def _strasse(self, session, name="Hauptstrasse", lat=53.62, lon=9.676):
        from app.models import Place
        from app.services.places import normalize

        session.add(
            Place(
                name=name,
                name_normalized=normalize(name),
                lat=lat,
                lon=lon,
                kind="strasse",
            )
        )
        session.commit()

    def _ablegen(self, settings, fixtures_dir: Path, unterpfad: str, quelle="scan_ohne_exif.jpg"):
        ziel = settings.incoming_dir / unterpfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes((fixtures_dir / quelle).read_bytes())
        return ziel

    def test_der_eingangsordner_liest_die_ordnernamen_mit(
        self, session, settings, fixtures_dir: Path, monkeypatch
    ):
        """Der Test, der gefehlt hat."""
        monkeypatch.setattr(settings, "import_provenance", "Archiv/")
        self._strasse(session)
        self._ablegen(settings, fixtures_dir, "Hauptstrasse/14 Museum/023.jpg")

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        assert watcher.scan_once() == 1

        foto = session.scalars(select(Photo)).one()
        assert foto.place_name == "Hauptstrasse 14"
        assert (foto.lat, foto.lon) == (53.62, 9.676)
        assert foto.title == "Hauptstrasse 14, Museum"
        assert foto.provenance == "Archiv/Hauptstrasse/14 Museum/023.jpg"
        assert {"Hauptstrasse", "Museum"} <= {schlagwort.name for schlagwort in foto.tags}

    def test_das_protokoll_meldet_keinen_fehlenden_ort_den_es_gleich_ergaenzt(
        self, session, settings, fixtures_dir: Path
    ):
        """Sonst stuende im Import-Protokoll "es fehlt noch: Ort" fuer ein verortetes Foto.

        Die Meldung entsteht nach der Pfad-Schicht, nicht davor -- ein Ehrenamtlicher, der das
        Protokoll durchsieht, soll darin keine Luecken suchen, die keine sind.
        """
        from app.models import ImportLog

        self._strasse(session)
        self._ablegen(settings, fixtures_dir, "Hauptstrasse/14 Museum/023.jpg")

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        watcher.scan_once()

        eintrag = session.scalars(select(ImportLog)).one()
        assert "Ort" not in eintrag.message
        assert "Jahr" in eintrag.message

    def test_erledigte_dateien_behalten_ihren_ordner(self, session, settings, fixtures_dir: Path):
        """Flach weggeraeumt ist ein sortierter Stapel ein einmaliger Versuch.

        Die Ordnernamen sind die Aussage ueber diese Fotos. Liegen sie hinterher alle nebeneinander
        in _erledigt/, hat ein zweiter Lauf nichts mehr zu lesen -- und gleichnamige Dateien aus
        verschiedenen Haeusern stapeln sich zu "023 (2).jpg".
        """
        self._strasse(session)
        self._ablegen(settings, fixtures_dir, "Hauptstrasse/14 Museum/023.jpg")
        self._ablegen(settings, fixtures_dir, "Hauptstrasse/16 Anders/023.jpg", "hochkant.jpg")

        watcher = IncomingWatcher(settings, interval=0)
        watcher.scan_once()
        assert watcher.scan_once() == 2

        erledigt = settings.incoming_dir / "_erledigt"
        assert (erledigt / "Hauptstrasse" / "14 Museum" / "023.jpg").is_file()
        assert (erledigt / "Hauptstrasse" / "16 Anders" / "023.jpg").is_file()
        assert not (erledigt / "023 (2).jpg").exists()
