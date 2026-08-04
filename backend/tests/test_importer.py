from datetime import date
from pathlib import Path

from PIL import Image
from sqlalchemy import select

from app.models import DatePrecision, ImportLog, ImportResult, Photo, Source
from app.services.importer import DONE_DIR, PROBLEM_DIR, import_directory, import_file
from app.services.storage import THUMBNAIL_SIZES, original_path, thumbnail_path


class TestGrundfall:
    def test_scan_ohne_exif_wird_aufgenommen(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)

        assert outcome.result == ImportResult.IMPORTED
        foto = outcome.photo
        assert foto is not None
        assert foto.original_filename == "scan_ohne_exif.jpg"
        assert (foto.width, foto.height) == (900, 640)
        # Der Normalfall im Museum: weder Ort noch Jahr bekannt.
        assert foto.needs_location and foto.needs_date

    def test_original_liegt_unter_seinem_hash(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)
        sha = outcome.photo.sha256

        abgelegt = original_path(settings.photos_dir, sha, ".jpg")
        assert abgelegt.is_file()
        assert abgelegt.name == f"{sha}.jpg"
        assert abgelegt.parent.name == sha[2:4], "zweistufige Faecherung"

    def test_thumbnails_in_beiden_groessen(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)

        for groesse in THUMBNAIL_SIZES:
            pfad = thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, groesse)
            assert pfad.is_file()
            with Image.open(pfad) as vorschau:
                assert vorschau.format == "WEBP"
                assert max(vorschau.size) <= groesse


class TestDubletten:
    def test_dieselbe_datei_zweimal(self, session, settings, sample_image):
        erst = import_file(session, sample_image("scan_ohne_exif.jpg"), settings)
        session.flush()
        zweit = import_file(
            session, sample_image("scan_ohne_exif.jpg", as_name="kopie.jpg"), settings
        )

        assert zweit.result == ImportResult.DUPLICATE
        assert zweit.photo.id == erst.photo.id
        assert session.scalar(select(Photo).where(Photo.sha256 == erst.photo.sha256))
        assert len(session.scalars(select(Photo)).all()) == 1

    def test_dublette_wird_begruendet_protokolliert(self, session, settings, sample_image):
        import_file(session, sample_image("scan_ohne_exif.jpg"), settings)
        session.flush()
        import_file(session, sample_image("scan_ohne_exif.jpg", as_name="nochmal.jpg"), settings)
        session.flush()

        eintrag = session.scalars(
            select(ImportLog).where(ImportLog.result == ImportResult.DUPLICATE)
        ).one()
        # "Da fehlt was" ohne Grund waere fuer einen Ehrenamtlichen nicht auswertbar.
        assert "Inhaltsgleich" in eintrag.message


class TestDatumAusExif:
    def test_scandatum_datiert_das_foto_nicht(self, session, settings, sample_image):
        """Der wichtigste Fall der ganzen Pipeline.

        Das EXIF sagt 2019, das Foto ist historisch. Wuerde das Datum uebernommen, laege das Bild
        auf der Zeitleiste bei 2019 -- und es gaelte als datiert, taeuchte also nie im
        "Hilf mit"-Bereich auf, wo jemand es haette richtigstellen koennen.
        """
        outcome = import_file(session, sample_image("scan_mit_scandatum.jpg"), settings)
        foto = outcome.photo

        assert foto.date_from is None
        assert foto.date_precision == DatePrecision.UNKNOWN
        assert foto.needs_date, "muss im 'Hilf mit'-Bereich erscheinen"
        # Aufgehoben bleibt es trotzdem: der Kurator soll es sehen koennen.
        assert foto.exif_datetime.year == 2019

    def test_plausibles_aufnahmedatum_wird_uebernommen(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("foto_mit_gps.jpg"), settings)
        foto = outcome.photo

        assert foto.date_from == date(1975, 6, 21)
        assert foto.date_to == date(1975, 6, 21)
        assert foto.date_precision == DatePrecision.DAY
        assert foto.date_source == Source.EXIF

    def test_grenze_ist_einstellbar(self, session, settings, sample_image, monkeypatch):
        """Eine Sammlung mit echten Digitalfotos hebt die Grenze an."""
        monkeypatch.setattr(settings, "exif_date_max_year", 2030)
        outcome = import_file(session, sample_image("scan_mit_scandatum.jpg"), settings)

        assert outcome.photo.date_from == date(2019, 3, 14)

    def test_scannerdatum_datiert_das_foto_nicht(self, session, settings, sample_image):
        """Der teuerste Fehler dieses Imports -- 116 Fotos des Erstbestands, 91 aus einem Lauf.

        Der Scanner nennt sich in der Datei, und danach entscheidet das Geraet, nicht das Jahr.
        Ohne diese Regel laege ein Ortsbild von 1910 auf der Zeitleiste bei 2015, gaelte als
        datiert und kaeme deshalb nie zur Korrektur.
        """
        outcome = import_file(session, sample_image("scan_vom_scanner.jpg"), settings)

        assert outcome.photo.date_from is None
        assert outcome.photo.needs_date
        assert outcome.photo.exif_datetime.year == 2015

    def test_scannerdatum_bleibt_auch_bei_hoher_grenze_draussen(
        self, session, settings, sample_image, monkeypatch
    ):
        """Die Sammlung mit echten Digitalfotos hebt die Grenze -- der Scanner bleibt ein Scanner.

        Genau der Fall, in dem die Jahresgrenze allein nicht mehr traegt: Sie steht hoch, damit
        die Kamerafotos durchkommen, und wuerde die Scans gleich mit hindurchlassen.
        """
        monkeypatch.setattr(settings, "exif_date_max_year", 2030)
        outcome = import_file(session, sample_image("scan_vom_scanner.jpg"), settings)

        assert outcome.photo.date_from is None

    def test_kameradatum_datiert_das_foto(self, session, settings, sample_image):
        """Die Gegenrichtung, und ohne sie bliebe der halbe Bestand undatiert.

        Das Foto ist von 2014, also weit hinter ``exif_date_max_year``. Die Jahresgrenze ist aber
        nur der Ersatz fuer eine fehlende Geraeteangabe -- und hier steht sie in der Datei.
        """
        outcome = import_file(session, sample_image("kamerafoto.jpg"), settings)

        assert outcome.photo.date_from == date(2014, 3, 9)
        assert outcome.photo.date_source == Source.EXIF


class TestOrtUndTitel:
    def test_gps_wird_uebernommen(self, session, settings, sample_image):
        foto = import_file(session, sample_image("foto_mit_gps.jpg"), settings).photo

        assert foto.lat is not None and foto.lon is not None
        assert abs(foto.lat - 53.62053) < 0.0001
        assert abs(foto.lon - 9.67601) < 0.0001
        assert foto.location_source == Source.EXIF
        assert not foto.needs_location

    def test_titel_aus_exif(self, session, settings, sample_image):
        foto = import_file(session, sample_image("scan_mit_scandatum.jpg"), settings).photo

        assert foto.title == "Kirchweih an der Muehle"
        assert foto.title_source == Source.EXIF


class TestKameraTextbausteine:
    """Was die Kamera von sich aus hineinschreibt, ist kein Titel.

    Dieselbe Falle wie das Scandatum, ein Feld weiter: "OLYMPUS DIGITAL CAMERA" steht wirklich im
    Titel- und im Beschreibungsfeld -- das Foto gilt damit als betitelt und wird nie wieder
    jemandem vorgelegt, der einen echten Titel wuesste. Kein Titel ist ehrlicher.
    """

    def test_kameramodell_wird_nicht_zum_titel(self):
        from app.services.exif import _statement

        assert _statement(b"OLYMPUS DIGITAL CAMERA") is None
        assert _statement(b"SONY DSC") is None
        assert _statement(b"Picasa") is None

    def test_echter_titel_bleibt(self):
        from app.services.exif import _statement

        assert _statement(b"Kirchweih an der Muehle") == "Kirchweih an der Muehle"

    def test_unbekannt_ist_kein_bildnachweis(self, session, settings, sample_image):
        """In 82 Dateien des Erstbestands steht als Fotograf woertlich "unbekannt".

        Uebernommen stuende unter 82 Fotos im Kiosk die Zeile "unbekannt" -- schlechter als gar
        keine, denn sie sieht aus wie eine Auskunft und ist keine.
        """
        foto = import_file(session, sample_image("scan_vom_scanner.jpg"), settings).photo

        assert foto.credit is None

    def test_ein_genannter_fotograf_bleibt(self, session, settings, sample_image):
        foto = import_file(session, sample_image("kamerafoto.jpg"), settings).photo

        assert foto.credit == "August Kroeger"

    def test_eingestellter_bildnachweis_springt_nur_ein(
        self, session, settings, sample_image, monkeypatch
    ):
        """Die Sammlung als Rueckfall -- aber nur, wo die Datei niemanden nennt."""
        monkeypatch.setattr(settings, "import_credit", "Sammlung Heimatmuseum Holm")

        ohne = import_file(session, sample_image("scan_ohne_exif.jpg"), settings).photo
        mit = import_file(session, sample_image("kamerafoto.jpg"), settings).photo

        assert ohne.credit == "Sammlung Heimatmuseum Holm"
        assert mit.credit == "August Kroeger"

    def test_eingestellte_schlagwoerter_kommen_an_jedes_foto(
        self, session, settings, sample_image, monkeypatch
    ):
        """Eine Sammlung ist meist ueber etwas -- in Holm ueber Gebaeude.

        Im Code steht das nicht: sonst brauchte das naechste Museum einen Fork. Siehe
        Settings.import_tags.
        """
        monkeypatch.setattr(settings, "import_tags", ["Gebaeude"])

        foto = import_file(session, sample_image("scan_ohne_exif.jpg"), settings).photo

        assert "Gebaeude" in {schlagwort.name for schlagwort in foto.tags}

    def test_beschreibung_wiederholt_den_titel_nicht(self):
        """57 Dateien des Erstbestands tragen denselben Satz in beiden Feldern.

        Untereinander gestellt liest sich das wie ein Stottern und kostet den Platz, an dem etwas
        stehen koennte, was das Bild wirklich braucht.
        """
        from app.services.exif import ImageInfo
        from app.services.importer import _own_description

        gleich = ImageInfo(1, 1, "JPEG", title="Hof Hinrich Petersen")
        gleich.description = "hof hinrich petersen "
        assert _own_description(gleich) is None

        verschieden = ImageInfo(1, 1, "JPEG", title="Hof Hinrich Petersen")
        verschieden.description = "Aufnahme von der Strassenseite"
        assert _own_description(verschieden) == "Aufnahme von der Strassenseite"

    def test_ein_ganzer_absatz_ist_kein_titel_sondern_eine_beschreibung(self):
        """Im Archiv steht die ganze Bildunterschrift im Titelfeld -- 223 Zeichen, mit Umbruechen.

        Als Ueberschrift in der Detailansicht ist das eine Textwand. Weggeworfen gehoert sie
        trotzdem nicht: Sie wandert in die Beschreibung, und den Titel liefert der Ordner.
        """
        from app.services.exif import ImageInfo
        from app.services.importer import _own_description, _own_title

        lang = ImageInfo(1, 1, "JPEG", title="Beschriftung: v. li.: " + "Johann Harms, " * 12)
        assert _own_title(lang) is None
        assert _own_description(lang).startswith("Beschriftung: v. li.")

        mehrzeilig = ImageInfo(1, 1, "JPEG", title="Bilderbummel S. 12\nClaus Petersen")
        assert _own_title(mehrzeilig) is None
        assert _own_description(mehrzeilig) == "Bilderbummel S. 12\nClaus Petersen"


class TestTextkodierung:
    """Warum IPTC und die XP-Felder verschieden gelesen werden muessen.

    Anlass ist ein Bestand, in dem die Schlagwoerter "牁档癩潈浬", "楗瑮牥" und "浉匠湡敤"
    standen -- das sind "ArchivHolm", "Winter" und "Im Sande", als UTF-16 gelesen.
    Die Ursache ist tueckisch:
    **Jede** Bytefolge gerader Laenge ist gueltiges UTF-16, es fliegt also nie ein Fehler und der
    Rueckfall auf UTF-8 kommt nie zum Zug. Kaputt waren deshalb genau die Woerter mit gerader
    Byte-Laenge, heil die mit ungerader -- was wie Zufall aussah und keiner war.
    """

    def test_iptc_schlagwort_mit_gerader_bytelaenge_bleibt_lesbar(self):
        from app.services.exif import _text

        assert _text(b"ArchivHolm") == "ArchivHolm"
        assert _text(b"Winter") == "Winter"
        assert _text(b"Im Sande") == "Im Sande"

    def test_iptc_umlaut_kommt_als_utf8_an(self):
        from app.services.exif import _text

        assert _text("Mühlenweg".encode()) == "Mühlenweg"

    def test_doppelt_kodierter_umlaut_wird_zurueckgedreht(self):
        """ "MÃ¶ller" ist "Möller", zweimal durch die falsche Kodierung gedreht.

        Passiert vor uns: Ein Programm schreibt UTF-8 in ein EXIF-Feld, das ASCII sein soll, das
        naechste liest es Byte fuer Byte. Unter zwei Fotos des Erstbestands stuende sonst ein
        falsch geschriebener Name.
        """
        from app.services.exif import _text

        assert _text("August MÃ¶ller") == "August Möller"
        # Was schon richtig ist, bleibt unangetastet.
        assert _text("August Möller") == "August Möller"
        assert _text("Hof Hinrich Petersen") == "Hof Hinrich Petersen"

    def test_windows_feld_bleibt_utf16(self):
        """Die Gegenrichtung: XPTitle und XPKeywords sind wirklich UCS2-LE."""
        from app.services.exif import _xp_text

        assert _xp_text("Kirchweih".encode("utf-16-le")) == "Kirchweih"
        assert _xp_text("Mühlenweg".encode("utf-16-le")) == "Mühlenweg"


class TestSchwierigeDateien:
    def test_hochkant_wird_richtig_herum_vermessen(self, session, settings, sample_image):
        """Die Pixel sind 900x600, die Ausrichtung steht im EXIF. Gespeichert gehoert 600x900."""
        foto = import_file(session, sample_image("hochkant.jpg"), settings).photo

        assert (foto.width, foto.height) == (600, 900)

    def test_hochkant_thumbnail_ist_gedreht(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("hochkant.jpg"), settings)

        with Image.open(thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, 240)) as v:
            assert v.height > v.width, "Vorschau muss hochkant sein"

    def test_graustufen_tiff(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("graustufen.tif"), settings)

        assert outcome.result == ImportResult.IMPORTED
        assert outcome.photo.mime == "image/tiff"

    def test_cmyk_wird_umgewandelt_statt_abgewiesen(self, session, settings, sample_image):
        """WebP kennt CMYK nicht. Ohne Umwandlung scheitert erst der letzte Schritt."""
        outcome = import_file(session, sample_image("cmyk.tif"), settings)

        assert outcome.result == ImportResult.IMPORTED
        assert thumbnail_path(settings.thumbs_dir, outcome.photo.sha256, 240).is_file()

    def test_textdatei_wird_mit_begruendung_abgewiesen(self, session, settings, sample_image):
        outcome = import_file(session, sample_image("kein_bild.txt"), settings)

        assert outcome.result == ImportResult.REJECTED
        assert "kein lesbares bild" in outcome.message.lower()

    def test_abgewiesene_datei_hinterlaesst_keine_reste(self, session, settings, sample_image):
        import_file(session, sample_image("kein_bild.txt"), settings)

        assert list(settings.photos_dir.rglob("*.*")) == []
        assert session.scalars(select(Photo)).all() == []


class TestEingangsordner:
    def test_aufgenommenes_wird_beiseitegeraeumt_nicht_geloescht(
        self, session, settings, sample_image
    ):
        quelle = settings.incoming_dir / "scan_ohne_exif.jpg"
        quelle.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())

        import_file(session, quelle, settings, move_aside=True)

        assert not quelle.exists()
        # Nie loeschen: ein Helfer, der seine Datei verschwinden sieht, hat einen schlechten Tag.
        assert (settings.incoming_dir / DONE_DIR / "scan_ohne_exif.jpg").is_file()

    def test_problematisches_kommt_in_den_problemordner(self, session, settings, sample_image):
        quelle = settings.incoming_dir / "kein_bild.txt"
        quelle.write_bytes(sample_image("kein_bild.txt").read_bytes())

        import_file(session, quelle, settings, move_aside=True)

        assert (settings.incoming_dir / PROBLEM_DIR / "kein_bild.txt").is_file()

    def test_namensgleiches_ueberschreibt_nichts(self, session, settings, sample_image):
        for inhalt in ("scan_ohne_exif.jpg", "hochkant.jpg"):
            quelle = settings.incoming_dir / "gleicher_name.jpg"
            quelle.write_bytes(sample_image(inhalt).read_bytes())
            import_file(session, quelle, settings, move_aside=True)

        erledigt = sorted(p.name for p in (settings.incoming_dir / DONE_DIR).iterdir())
        assert erledigt == ["gleicher_name (2).jpg", "gleicher_name.jpg"]

    def test_sonderordner_werden_nicht_erneut_durchsucht(self, session, settings, sample_image):
        quelle = settings.incoming_dir / "scan_ohne_exif.jpg"
        quelle.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())
        import_file(session, quelle, settings, move_aside=True)
        session.flush()

        # Ohne diese Ausnahme liefe der Waechter in eine Endlosschleife ueber _erledigt/.
        nochmal = import_directory(session, settings.incoming_dir, settings)
        assert nochmal == []


class TestVerzeichnisimport:
    def test_alles_auf_einmal(self, session, settings, tmp_path: Path, fixtures_dir: Path):
        quelle = tmp_path / "stapel"
        quelle.mkdir()
        for datei in fixtures_dir.iterdir():
            if datei.suffix in (".jpg", ".tif", ".txt"):
                (quelle / datei.name).write_bytes(datei.read_bytes())

        outcomes = import_directory(session, quelle, settings)
        session.flush()

        aufgenommen = [e for e in outcomes if e.result == ImportResult.IMPORTED]
        abgewiesen = [e for e in outcomes if e.result == ImportResult.REJECTED]

        assert len(aufgenommen) == 8, "8 Bilder, 1 Textdatei"
        assert len(abgewiesen) == 1
        # Originale des Nutzers bleiben unangetastet.
        assert len(list(quelle.iterdir())) == 9
