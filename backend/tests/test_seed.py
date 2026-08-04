"""Der Beispielbestand: sichern, wegwerfen, zurueckholen.

Die eine Zusage, an der alles haengt: **Was gesichert wurde, kommt vollstaendig zurueck.** Ein
Ausgangszustand, der bei jedem Zurueckholen ein wenig anders aussieht, ist keiner -- und der
Unterschied faellt erst auf, wenn man einen Fehler sucht, den es gar nicht gibt.

Der zweite Grund fuer diese Tests ist die Form: Bilddateien plus JSON statt eines
Datenbankabzugs, damit eine neue Spalte den Bestand nicht wertlos macht. Die Kehrseite ist, dass
das Auflegen der Metadaten Handarbeit im Code ist -- genau die Sorte Code, die still danebengreift.
"""

from datetime import date

from sqlalchemy import select

from app.models import Change, Photo, PhotoStatus, Source, Tag
from app.services import seed


def _bestand(session, settings, sample_image, fixtures_dir) -> Photo:
    """Ein Foto mit allem dran: Datierung, Ort, Schlagwoerter, Nachweis, Herkunft, Beitrag."""
    from app.services.importer import import_file

    foto = import_file(session, sample_image("scan_ohne_exif.jpg"), settings).photo
    assert foto is not None
    foto.title = "Gasthof Petersen"
    foto.description = "Blick von der Hauptstrasse."
    foto.credit = "Sammlung Heimatmuseum Holm"
    foto.provenance = "Leihgabe H. Meyer, Freigabe liegt vor"
    foto.date_from, foto.date_to = date(1920, 1, 1), date(1929, 12, 31)
    foto.date_precision = "decade"
    foto.date_source = Source.CURATOR
    foto.lat, foto.lon = 53.6196, 9.652
    foto.place_name = "Hauptstrasse 14"
    foto.location_source = Source.VISITOR
    foto.location_accuracy_m = 15
    foto.tags = [Tag(name="Gasthof"), Tag(name="ArchivHolm")]
    session.add(
        Change(
            photo_id=foto.id,
            field="location",
            old_value=None,
            new_value="53.6196,9.652 (Hauptstrasse 14)",
            source=Source.VISITOR,
        )
    )
    session.commit()
    return foto


class TestRundlauf:
    def test_ausgangszustand_uebersteht_das_hin_und_zurueck(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        vorher = _bestand(session, settings, sample_image, fixtures_dir)
        erwartet = {
            feld: getattr(vorher, feld) for feld in (*seed.FIELDS, "sha256", "original_filename")
        }
        erwartete_tags = sorted(tag.name for tag in vorher.tags)

        ziel = tmp_path / "seed"
        seed.export(session, settings, ziel)
        session.commit()

        seed.load(session, settings, ziel)
        session.commit()

        nachher = session.scalars(select(Photo)).one()
        for feld, wert in erwartet.items():
            assert getattr(nachher, feld) == wert, f"{feld} kam anders zurueck"
        assert sorted(tag.name for tag in nachher.tags) == erwartete_tags

    def test_besucherbeitrag_kommt_mit(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        """Sonst waere die Sichtungsliste der Verwaltung nach jedem ``make seed`` leer."""
        _bestand(session, settings, sample_image, fixtures_dir)
        ziel = tmp_path / "seed"

        seed.export(session, settings, ziel)
        session.commit()
        seed.load(session, settings, ziel)
        session.commit()

        beitrag = session.scalars(select(Change)).one()
        assert beitrag.source == Source.VISITOR
        assert beitrag.new_value == "53.6196,9.652 (Hauptstrasse 14)"
        assert beitrag.photo_id == session.scalars(select(Photo)).one().id

    def test_geloeschtes_foto_bleibt_geloescht(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        """Dass zwei Fotos im Papierkorb liegen, gehoert zum Zustand -- sonst ist die Liste leer."""
        foto = _bestand(session, settings, sample_image, fixtures_dir)
        foto.status = PhotoStatus.DELETED
        session.commit()
        ziel = tmp_path / "seed"

        seed.export(session, settings, ziel)
        session.commit()
        seed.load(session, settings, ziel)
        session.commit()

        assert session.scalars(select(Photo)).one().status == PhotoStatus.DELETED

    def test_luecken_bleiben_luecken(self, session, settings, sample_image, tmp_path):
        """Ein Foto ohne Ort und ohne Jahr ist der Fall, den der Hilf-mit-Bereich braucht.

        Beim Zurueckholen laeuft es durch den echten Import, und der liest aus der Datei, was er
        findet. Wuerde er dabei etwas eintragen, verschwaende das Foto aus dem Beitragsbereich --
        die Luecke muss also die staerkere Angabe sein.
        """
        foto = _bestand(session, settings, sample_image, None)
        foto.date_from = foto.date_to = None
        foto.date_precision = "unknown"
        foto.date_source = None
        foto.lat = foto.lon = None
        foto.place_name = None
        foto.location_source = None
        session.commit()
        ziel = tmp_path / "seed"

        seed.export(session, settings, ziel)
        session.commit()
        seed.load(session, settings, ziel)
        session.commit()

        nachher = session.scalars(select(Photo)).one()
        assert nachher.needs_date, "die fehlende Datierung wurde beim Einlesen zugeschuettet"
        assert nachher.needs_location, "der fehlende Ort wurde beim Einlesen zugeschuettet"


class TestFehlenderBestand:
    def test_ohne_seed_verzeichnis_gibt_es_eine_klare_meldung(self, session, settings, tmp_path):
        """Kein Stapelauszug, sondern etwas Lesbares -- die CLI macht einen Satz daraus."""
        import pytest

        with pytest.raises(FileNotFoundError):
            seed.load(session, settings, tmp_path / "gibt-es-nicht")

    def test_leeren_raeumt_fotos_und_vorschaubilder_weg(
        self, session, settings, sample_image, fixtures_dir
    ):
        _bestand(session, settings, sample_image, fixtures_dir)
        assert list(settings.photos_dir.rglob("*.jpg"))

        seed.clear(session, settings)
        session.commit()

        assert session.scalars(select(Photo)).all() == []
        assert session.scalars(select(Change)).all() == []
        assert list(settings.photos_dir.rglob("*.jpg")) == []
        assert list(settings.thumbs_dir.rglob("*.webp")) == []

    def test_sichern_raeumt_geloeschte_dateien_weg(
        self, session, settings, sample_image, fixtures_dir, tmp_path
    ):
        """Sonst waere seed/ ein Ordner, der nur waechst -- und kein Abbild eines Zustands."""
        from app.services.importer import import_file

        _bestand(session, settings, sample_image, fixtures_dir)
        zweites = import_file(session, sample_image("hochkant.jpg"), settings).photo
        session.commit()
        ziel = tmp_path / "seed"
        seed.export(session, settings, ziel)
        assert (ziel / seed.IMAGE_DIR_NAME / "hochkant.jpg").exists()

        session.delete(zweites)
        session.commit()
        seed.export(session, settings, ziel)

        assert not (ziel / seed.IMAGE_DIR_NAME / "hochkant.jpg").exists()
        assert (ziel / seed.IMAGE_DIR_NAME / "scan_ohne_exif.jpg").exists()


class TestBestandLeeren:
    """``make empty`` -- der einzige Befehl, aus dem kein Weg zurueckfuehrt.

    ``seed-load`` wirft den Bestand auch weg, setzt aber etwas an seine Stelle. Dieser hier laesst
    nichts. Der Fehlerfall ist deshalb nicht "es loescht nicht", sondern **"es loescht, obwohl
    jemand etwas anderes gemeint hat"** -- und der faellt erst auf, wenn 929 Fotos weg sind.
    """

    def test_eine_falsche_antwort_loescht_nichts(
        self, session, settings, sample_image, fixtures_dir, monkeypatch, capsys
    ):
        from app.cli import main

        _bestand(session, settings, sample_image, fixtures_dir)
        monkeypatch.setattr("builtins.input", lambda _: "ja")

        assert main(["empty"]) == 1

        assert len(session.scalars(select(Photo)).all()) == 1
        assert list(settings.photos_dir.rglob("*.jpg"))
        assert "Abgebrochen" in capsys.readouterr().out

    def test_die_anzahl_der_fotos_ist_die_bestaetigung(
        self, session, settings, sample_image, fixtures_dir, monkeypatch
    ):
        """Getippt werden muss die Zahl, die eine Zeile weiter oben steht.

        Ein "j/n" laesst sich beantworten, ohne gelesen zu haben. Eine Zahl nicht.
        """
        from app.cli import main

        _bestand(session, settings, sample_image, fixtures_dir)
        monkeypatch.setattr("builtins.input", lambda _: "1")

        assert main(["empty"]) == 0

        assert session.scalars(select(Photo)).all() == []
        assert list(settings.photos_dir.rglob("*.jpg")) == []

    def test_ohne_rueckfrage_nur_mit_der_ausdruecklichen_option(
        self, session, settings, sample_image, fixtures_dir, monkeypatch
    ):
        """--yes ist fuer Skripte. Wird es gesetzt, darf nichts mehr nachfragen."""
        from app.cli import main

        _bestand(session, settings, sample_image, fixtures_dir)

        def keine_eingabe(_):
            raise AssertionError("es wurde trotz --yes nachgefragt")

        monkeypatch.setattr("builtins.input", keine_eingabe)

        assert main(["empty", "--yes"]) == 0
        assert session.scalars(select(Photo)).all() == []

    def test_ein_leerer_bestand_fragt_gar_nicht_erst(self, session, settings, monkeypatch):
        from app.cli import main

        def keine_eingabe(_):
            raise AssertionError("ein leerer Bestand braucht keine Bestaetigung")

        monkeypatch.setattr("builtins.input", keine_eingabe)

        assert main(["empty"]) == 0

    def test_der_ortsindex_bleibt_stehen(
        self, session, settings, sample_image, fixtures_dir, monkeypatch
    ):
        """Er kommt aus einem Overpass-Lauf und hat mit den Fotos nichts zu tun.

        Mitgeloescht muesste er ueber `make places` neu gebaut werden -- mit Netz, das der Pi im
        Museum nicht hat.
        """
        from app.cli import main
        from app.models import Place

        _bestand(session, settings, sample_image, fixtures_dir)
        session.add(
            Place(
                name="Hauptstrasse",
                name_normalized="hauptstrasse",
                lat=53.62,
                lon=9.676,
                kind="strasse",
            )
        )
        session.commit()
        monkeypatch.setattr("builtins.input", lambda _: "1")

        assert main(["empty"]) == 0

        # Erst wenn wirklich geloescht wurde, sagt der Ortsindex etwas aus.
        assert session.scalars(select(Photo)).all() == []
        assert session.scalars(select(Place)).all() != []
