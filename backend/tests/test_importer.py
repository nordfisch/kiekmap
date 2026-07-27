from datetime import date
from pathlib import Path

from PIL import Image
from sqlalchemy import select

from app.models import DatePrecision, ImportLog, ImportResult, Photo, Source
from app.services.importer import ERLEDIGT, PROBLEM, importiere_datei, importiere_verzeichnis
from app.services.storage import THUMBNAIL_GROESSEN, original_pfad, thumbnail_pfad


class TestGrundfall:
    def test_scan_ohne_exif_wird_aufgenommen(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("scan_ohne_exif.jpg"), settings)

        assert ergebnis.result == ImportResult.IMPORTED
        foto = ergebnis.photo
        assert foto is not None
        assert foto.original_filename == "scan_ohne_exif.jpg"
        assert (foto.width, foto.height) == (900, 640)
        # Der Normalfall im Museum: weder Ort noch Jahr bekannt.
        assert foto.needs_location and foto.needs_date

    def test_original_liegt_unter_seinem_hash(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("scan_ohne_exif.jpg"), settings)
        sha = ergebnis.photo.sha256

        abgelegt = original_pfad(settings.photos_dir, sha, ".jpg")
        assert abgelegt.is_file()
        assert abgelegt.name == f"{sha}.jpg"
        assert abgelegt.parent.name == sha[2:4], "zweistufige Faecherung"

    def test_thumbnails_in_beiden_groessen(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("scan_ohne_exif.jpg"), settings)

        for groesse in THUMBNAIL_GROESSEN:
            pfad = thumbnail_pfad(settings.thumbs_dir, ergebnis.photo.sha256, groesse)
            assert pfad.is_file()
            with Image.open(pfad) as vorschau:
                assert vorschau.format == "WEBP"
                assert max(vorschau.size) <= groesse


class TestDubletten:
    def test_dieselbe_datei_zweimal(self, session, settings, bild):
        erst = importiere_datei(session, bild("scan_ohne_exif.jpg"), settings)
        session.flush()
        zweit = importiere_datei(session, bild("scan_ohne_exif.jpg", als="kopie.jpg"), settings)

        assert zweit.result == ImportResult.DUPLICATE
        assert zweit.photo.id == erst.photo.id
        assert session.scalar(select(Photo).where(Photo.sha256 == erst.photo.sha256))
        assert len(session.scalars(select(Photo)).all()) == 1

    def test_dublette_wird_begruendet_protokolliert(self, session, settings, bild):
        importiere_datei(session, bild("scan_ohne_exif.jpg"), settings)
        session.flush()
        importiere_datei(session, bild("scan_ohne_exif.jpg", als="nochmal.jpg"), settings)
        session.flush()

        eintrag = session.scalars(
            select(ImportLog).where(ImportLog.result == ImportResult.DUPLICATE)
        ).one()
        # "Da fehlt was" ohne Grund waere fuer einen Ehrenamtlichen nicht auswertbar.
        assert "Inhaltsgleich" in eintrag.message


class TestDatumAusExif:
    def test_scandatum_datiert_das_foto_nicht(self, session, settings, bild):
        """Der wichtigste Fall der ganzen Pipeline.

        Das EXIF sagt 2019, das Foto ist historisch. Wuerde das Datum uebernommen, laege das Bild
        auf der Zeitleiste bei 2019 -- und es gaelte als datiert, taeuchte also nie im
        "Hilf mit"-Bereich auf, wo jemand es haette richtigstellen koennen.
        """
        ergebnis = importiere_datei(session, bild("scan_mit_scandatum.jpg"), settings)
        foto = ergebnis.photo

        assert foto.date_from is None
        assert foto.date_precision == DatePrecision.UNKNOWN
        assert foto.needs_date, "muss im 'Hilf mit'-Bereich erscheinen"
        # Aufgehoben bleibt es trotzdem: der Kurator soll es sehen koennen.
        assert foto.exif_datetime.year == 2019

    def test_plausibles_aufnahmedatum_wird_uebernommen(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("foto_mit_gps.jpg"), settings)
        foto = ergebnis.photo

        assert foto.date_from == date(1975, 6, 21)
        assert foto.date_to == date(1975, 6, 21)
        assert foto.date_precision == DatePrecision.DAY
        assert foto.date_source == Source.EXIF

    def test_grenze_ist_einstellbar(self, session, settings, bild, monkeypatch):
        """Eine Sammlung mit echten Digitalfotos hebt die Grenze an."""
        monkeypatch.setattr(settings, "exif_date_max_year", 2030)
        ergebnis = importiere_datei(session, bild("scan_mit_scandatum.jpg"), settings)

        assert ergebnis.photo.date_from == date(2019, 3, 14)


class TestOrtUndTitel:
    def test_gps_wird_uebernommen(self, session, settings, bild):
        foto = importiere_datei(session, bild("foto_mit_gps.jpg"), settings).photo

        assert foto.lat is not None and foto.lon is not None
        assert abs(foto.lat - 53.62053) < 0.0001
        assert abs(foto.lon - 9.67601) < 0.0001
        assert foto.location_source == Source.EXIF
        assert not foto.needs_location

    def test_titel_aus_exif(self, session, settings, bild):
        foto = importiere_datei(session, bild("scan_mit_scandatum.jpg"), settings).photo

        assert foto.title == "Kirchweih an der Muehle"
        assert foto.title_source == Source.EXIF


class TestSchwierigeDateien:
    def test_hochkant_wird_richtig_herum_vermessen(self, session, settings, bild):
        """Die Pixel sind 900x600, die Ausrichtung steht im EXIF. Gespeichert gehoert 600x900."""
        foto = importiere_datei(session, bild("hochkant.jpg"), settings).photo

        assert (foto.width, foto.height) == (600, 900)

    def test_hochkant_thumbnail_ist_gedreht(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("hochkant.jpg"), settings)

        with Image.open(thumbnail_pfad(settings.thumbs_dir, ergebnis.photo.sha256, 240)) as v:
            assert v.height > v.width, "Vorschau muss hochkant sein"

    def test_graustufen_tiff(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("graustufen.tif"), settings)

        assert ergebnis.result == ImportResult.IMPORTED
        assert ergebnis.photo.mime == "image/tiff"

    def test_cmyk_wird_umgewandelt_statt_abgewiesen(self, session, settings, bild):
        """WebP kennt CMYK nicht. Ohne Umwandlung scheitert erst der letzte Schritt."""
        ergebnis = importiere_datei(session, bild("cmyk.tif"), settings)

        assert ergebnis.result == ImportResult.IMPORTED
        assert thumbnail_pfad(settings.thumbs_dir, ergebnis.photo.sha256, 240).is_file()

    def test_textdatei_wird_mit_begruendung_abgewiesen(self, session, settings, bild):
        ergebnis = importiere_datei(session, bild("kein_bild.txt"), settings)

        assert ergebnis.result == ImportResult.REJECTED
        assert "kein lesbares bild" in ergebnis.message.lower()

    def test_abgewiesene_datei_hinterlaesst_keine_reste(self, session, settings, bild):
        importiere_datei(session, bild("kein_bild.txt"), settings)

        assert list(settings.photos_dir.rglob("*.*")) == []
        assert session.scalars(select(Photo)).all() == []


class TestEingangsordner:
    def test_aufgenommenes_wird_beiseitegeraeumt_nicht_geloescht(self, session, settings, bild):
        quelle = settings.incoming_dir / "scan_ohne_exif.jpg"
        quelle.write_bytes(bild("scan_ohne_exif.jpg").read_bytes())

        importiere_datei(session, quelle, settings, beiseiteraeumen=True)

        assert not quelle.exists()
        # Nie loeschen: ein Helfer, der seine Datei verschwinden sieht, hat einen schlechten Tag.
        assert (settings.incoming_dir / ERLEDIGT / "scan_ohne_exif.jpg").is_file()

    def test_problematisches_kommt_in_den_problemordner(self, session, settings, bild):
        quelle = settings.incoming_dir / "kein_bild.txt"
        quelle.write_bytes(bild("kein_bild.txt").read_bytes())

        importiere_datei(session, quelle, settings, beiseiteraeumen=True)

        assert (settings.incoming_dir / PROBLEM / "kein_bild.txt").is_file()

    def test_namensgleiches_ueberschreibt_nichts(self, session, settings, bild):
        for inhalt in ("scan_ohne_exif.jpg", "hochkant.jpg"):
            quelle = settings.incoming_dir / "gleicher_name.jpg"
            quelle.write_bytes(bild(inhalt).read_bytes())
            importiere_datei(session, quelle, settings, beiseiteraeumen=True)

        erledigt = sorted(p.name for p in (settings.incoming_dir / ERLEDIGT).iterdir())
        assert erledigt == ["gleicher_name (2).jpg", "gleicher_name.jpg"]

    def test_sonderordner_werden_nicht_erneut_durchsucht(self, session, settings, bild):
        quelle = settings.incoming_dir / "scan_ohne_exif.jpg"
        quelle.write_bytes(bild("scan_ohne_exif.jpg").read_bytes())
        importiere_datei(session, quelle, settings, beiseiteraeumen=True)
        session.flush()

        # Ohne diese Ausnahme liefe der Waechter in eine Endlosschleife ueber _erledigt/.
        nochmal = importiere_verzeichnis(session, settings.incoming_dir, settings)
        assert nochmal == []


class TestVerzeichnisimport:
    def test_alles_auf_einmal(self, session, settings, tmp_path: Path, fixtures_dir: Path):
        quelle = tmp_path / "stapel"
        quelle.mkdir()
        for datei in fixtures_dir.iterdir():
            if datei.suffix in (".jpg", ".tif", ".txt"):
                (quelle / datei.name).write_bytes(datei.read_bytes())

        ergebnisse = importiere_verzeichnis(session, quelle, settings)
        session.flush()

        aufgenommen = [e for e in ergebnisse if e.result == ImportResult.IMPORTED]
        abgewiesen = [e for e in ergebnisse if e.result == ImportResult.REJECTED]

        assert len(aufgenommen) == 6, "6 Bilder, 1 Textdatei"
        assert len(abgewiesen) == 1
        # Originale des Nutzers bleiben unangetastet.
        assert len(list(quelle.iterdir())) == 7
