"""Tests der Pfad-Schicht: was die Ordnerstruktur ueber ein Foto sagt.

Ein Museumsarchiv ist sortiert, und die Sortierung ist eine Aussage. Sie zu verwerfen hiesse,
Besucher nach dem Ort eines Fotos zu fragen, dessen Adresse im Ordnernamen steht.

Drei Fehler passieren dabei still, und jeder hat hier seinen Test:

  1. Aus "10 H Brahms" wird die Hausnummer 10h. Die gibt es nicht -- das Foto landet auf der
     Strasse statt am Haus, und niemand sieht, dass etwas schiefging.
  2. Die **Strassenmitte** ueberschreibt eine Koordinate aus der Datei. Sie ist mit 150 m groeber
     als der Punkt, den sie ersetzt: Das Foto wird ungenauer, und es sieht nach Praezisierung aus.
  3. Eine Angabe von Menschen wird ueberschrieben. Nur das EXIF gibt nach -- und das erst, seit
     nachgemessen ist, dass diese Koordinaten eingetragen und nicht gemessen wurden.

Die Regel unter 2 und 3 lief bis August 2026 andersherum: Das EXIF schlug den Ordner immer. Warum
sie gedreht wurde, steht im Modul-Docstring von ``services/foldermeta.py``.
"""

import pytest

from app.models import Place
from app.services import places as place_service
from app.services.foldermeta import (
    apply_folder_meta,
    parse_path,
    split_housenumber,
    street_names,
)
from app.services.importer import import_file


def _ort(session, name, kind, lat=53.62, lon=9.676, street=None, housenumber=None):
    session.add(
        Place(
            name=name,
            name_normalized=place_service.normalize(name),
            lat=lat,
            lon=lon,
            kind=kind,
            street=street,
            housenumber=housenumber,
        )
    )


def _strasse(session, name):
    _ort(session, name, "strasse")


@pytest.fixture
def ortsindex(session):
    """Eine Strasse aus Holm mit einigen Hausnummern -- und einer, die fehlt."""
    _ort(session, "Hauptstrasse", "strasse", lat=53.6200, lon=9.6760)
    _ort(session, "Hoernstrasse", "strasse", lat=53.6210, lon=9.6770)
    for nummer in ("10", "14", "9a"):
        _ort(
            session,
            f"Hauptstrasse {nummer}",
            "adresse",
            lat=53.6205,
            lon=9.6765,
            street="Hauptstrasse",
            housenumber=nummer,
        )
    session.commit()
    return session


class TestHausnummerLesen:
    def test_name_steht_neben_der_nummer(self):
        assert split_housenumber("14 Gasthof Petersen") == ("14", "Gasthof Petersen")

    def test_buchstabe_zaehlt_nur_ohne_leerzeichen(self):
        """Der stille Fehler: "10 H Brahms" ist Nummer 10, Familie Brahms.

        Als "10h" gelesen findet die Adresse sich im Ortsindex nicht, das Foto rutscht auf den
        Strassenpunkt -- und dass es genauer haette liegen koennen, sieht danach niemand mehr.
        """
        assert split_housenumber("10 H Brahms") == ("10", "H Brahms")
        assert split_housenumber("25a Zahnarztpraxis") == ("25a", "Zahnarztpraxis")

    def test_fuehrende_nullen_sind_ablage_keine_adresse(self):
        assert split_housenumber("009a") == ("9a", None)
        assert split_housenumber("001") == ("1", None)

    def test_bei_einer_spanne_zaehlt_die_erste_nummer(self):
        assert split_housenumber("099-105 Weltweit") == ("99", "Weltweit")
        assert split_housenumber("2-6 Hans Hinrich Petersen") == ("2", "Hans Hinrich Petersen")
        assert split_housenumber("011-011a Neubau") == ("11", "Neubau")

    def test_ordner_ohne_nummer_ist_nur_ein_name(self):
        assert split_housenumber("Glasfaser") == (None, "Glasfaser")

    def test_lauter_nullen_sind_keine_hausnummer(self):
        """ "00" ist der Ablagekorb des Archivs fuer alles ohne Adresse, nicht das Haus Nummer 0.

        Als Nummer gelesen bekaeme das Foto den Ortsnamen "Lehmweg 0" -- eine Adresse, die es
        nirgends gibt. Und weil in dem Namen eine Ziffer steht, wuerde der "Hilf mit"-Bereich
        auch nie anbieten, sie richtigzustellen (siehe services/needs.py).
        """
        assert split_housenumber("00 div") == (None, "div")
        assert split_housenumber("00") == (None, None)

    def test_zahlname_wird_kein_titel(self, ortsindex):
        """ "049" ist eine Hausnummer, kein Name -- ein Foto darunter bekommt keinen Titel.

        Sonst hiesse es "Hauptstrasse 49, 049" oder, seit dem 16. August 2026, schlicht "049".
        """
        assert split_housenumber("049") == ("49", None)

        angabe = parse_path(("Hauptstrasse", "049"), street_names(ortsindex))
        assert (angabe.address, angabe.name) == ("Hauptstrasse 49", None)


class TestPfadLesen:
    def test_der_ortsindex_erkennt_die_strasse_nicht_der_ordnername(self, ortsindex):
        """Es gibt keinen "Strassen"-Schalter im Code -- sonst waere Holm darin verdrahtet."""
        strassen = street_names(ortsindex)

        angabe = parse_path(("Strassen", "Hauptstrasse", "14 Gasthof Petersen"), strassen)

        assert angabe.street == "Hauptstrasse"
        assert angabe.housenumber == "14"
        assert angabe.name == "Gasthof Petersen"
        assert angabe.address == "Hauptstrasse 14"

    def test_ohne_bekannte_strasse_sagt_der_pfad_nichts(self, ortsindex):
        angabe = parse_path(("Urlaub", "2019"), street_names(ortsindex))

        assert angabe.street is None
        assert angabe.address is None

    def test_ein_verkuerzter_ordnername_findet_die_strasse(self, session):
        """Das Archiv kuerzt: Ordner "Wiesengrund", Strasse "Im Wiesengrund"."""
        _strasse(session, "Im Wiesengrund")
        session.commit()

        angabe = parse_path(("Wiesengrund", "07"), street_names(session))

        assert angabe.street == "Im Wiesengrund"

    def test_bei_zwei_moeglichen_strassen_wird_nicht_geraten(self, session):
        """ "Deelenweg" steckt in "Deelenweg I" und "Deelenweg II".

        Geraten laendeten die Fotos womoeglich am anderen Ende des Dorfes -- und weil sie dann
        als verortet gelten, sieht das nie jemand. Lieber unverortet und im "Hilf mit"-Bereich.
        """
        _strasse(session, "Deelenweg I")
        _strasse(session, "Deelenweg II")
        session.commit()

        angabe = parse_path(("Deelenweg", "10 Deelenhof"), street_names(session))

        assert angabe.street is None

    def test_eine_hausnummer_ist_kein_strassenname(self, session):
        """Im Ortsindex steht "Kolonie Autal 2" als Strasse -- und der Hausnummernordner "2"
        traf sie, eindeutig und voellig falsch.

        Die beiden Fotos aus "Achter de Moehl/2" landeten damit am anderen Ende des Dorfes,
        ohne Hausnummer und mit falschem Strassennamen. Nur ein Name ist eine Strasse.
        """
        _strasse(session, "Achter de Moehl")
        _strasse(session, "Kolonie Autal 2")
        session.commit()

        angabe = parse_path(("Achter de Moehl", "2"), street_names(session))

        assert (angabe.street, angabe.housenumber) == ("Achter de Moehl", "2")

    def test_ein_teilwort_ist_kein_strassenname(self, session):
        """Wortweise, nicht als Zeichenkette: "Horn" ist nicht die "Bredhornstrasse"."""
        _strasse(session, "Bredhornstrasse")
        session.commit()

        assert parse_path(("Horn",), street_names(session)).street is None

    def test_ein_unterordner_darf_die_strasse_wiederholen(self, ortsindex):
        """Das Archiv legt einen Ordner "Hauptstrasse 14" unter "Hauptstrasse" ab.

        Ungelesen wird daraus kein Haus, sondern ein Name -- und damit ein Titel "Hauptstrasse 14"
        ueber der Zeile "Hauptstrasse". Genau der Adressabklatsch, den decisions.md, Punkt 48,
        gerade abgeschafft hat.
        """
        angabe = parse_path(("Hauptstrasse", "Hauptstrasse 14"), street_names(ortsindex))

        assert (angabe.street, angabe.housenumber, angabe.name) == ("Hauptstrasse", "14", None)

    def test_ein_aehnlicher_name_wird_nicht_zerschnitten(self, session):
        """Die Gegenprobe: Der Vorsatz allein reicht nicht als Grund zum Abschneiden.

        Unter der Strasse "Twiete" liegt ein Ordner "Twietenhof". Nur nach dem Vorsatz gekuerzt
        bliebe "nhof" stehen -- ein Name, den es nie gab.
        """
        _strasse(session, "Twiete")
        session.commit()

        angabe = parse_path(("Twiete", "Twietenhof"), street_names(session))

        assert (angabe.housenumber, angabe.name) == (None, "Twietenhof")

    def test_die_strasse_darf_der_gewaehlte_ordner_selbst_sein(self, ortsindex):
        """Am Stick waehlt der Ehrenamtliche den Ordner -- oft die Strasse."""
        angabe = parse_path(("Hauptstrasse", "14 Museum"), street_names(ortsindex))

        assert (angabe.street, angabe.housenumber) == ("Hauptstrasse", "14")


class TestWasAmFotoLandet:
    def _importiere(
        self, session, settings, sample_image, unterpfad: str, bild="scan_ohne_exif.jpg"
    ):
        wurzel = settings.data_dir / "archiv"
        ziel = wurzel / unterpfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(sample_image(bild).read_bytes())

        outcome = import_file(session, ziel, settings)
        assert outcome.photo is not None
        apply_folder_meta(session, outcome.photo, ziel, wurzel, settings)
        return outcome.photo

    def test_die_hausnummer_verortet_das_foto_am_haus(
        self, session, settings, sample_image, ortsindex
    ):
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert (foto.lat, foto.lon) == (53.6205, 9.6765)
        assert foto.place_name == "Hauptstrasse 14"
        assert foto.location_accuracy_m == place_service.ACCURACY_ADDRESS_M
        assert foto.title == "Museum"

    def test_der_titel_wiederholt_die_adresse_nicht(
        self, session, settings, sample_image, ortsindex
    ):
        """Der Titel steht in der Detailansicht ueber der Adresse, nicht statt ihrer.

        Bis zum 16. August 2026 hiess dieses Foto "Hauptstrasse 14, Museum" -- und darunter stand
        noch einmal "Hauptstrasse 14". Punkt 41 hat 815 solcher Titel von Hand auseinandergenommen,
        der naechste Import schrieb 323 davon zurueck. Wo der Ordner nur eine Nummer nennt, bleibt
        der Titel leer: Eine Zeile, die nur die naechste wiederholt, ist keine.
        """
        mit_namen = self._importiere(
            session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg"
        )
        assert mit_namen.title == "Museum"
        assert mit_namen.place_name == "Hauptstrasse 14"

        # Ein anderes Bild, sonst erkennt der Import es am SHA-256 als Dublette und liefert das
        # erste Foto zurueck -- der zweite Teil des Tests pruefte dann sich selbst.
        ohne_namen = self._importiere(
            session, settings, sample_image, "Hauptstrasse/10/b.jpg", "hochkant.jpg"
        )
        assert ohne_namen.title is None
        assert ohne_namen.place_name == "Hauptstrasse 10"

    def test_ordner_ohne_hausnummer_setzt_das_foto_auf_die_strasse(
        self, session, settings, sample_image, ortsindex
    ):
        """Bis August 2026 blieb so ein Foto unverortet -- 72 Stueck im Erstbestand.

        Die Begruendung dafuer war, dass der Strassenpunkt wie eine Antwort aussieht und das Foto
        damit aus "Wo ist das?" fiele. Das galt, solange es zwei Fragen gab. Seit es die dritte
        gibt, faellt es nicht heraus, sondern in die genauere Frage hinein: Genau ein
        strassengenaues Foto ohne Hausnummer ist es, wonach das Nachschaerfen sucht.

        Die 150 m sagen weiterhin, was der Punkt wert ist. Als Schlagwort bleibt die Strasse
        ebenfalls stehen.
        """
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/119.jpg")

        assert not foto.needs_location
        assert (foto.lat, foto.lon) == (53.6200, 9.6760)
        assert foto.location_accuracy_m == place_service.ACCURACY_STREET_M
        assert foto.location_source == "curator"
        assert "Hauptstrasse" in {schlagwort.name for schlagwort in foto.tags}

    def test_unbekannte_hausnummer_faellt_auf_die_strasse_zurueck(
        self, session, settings, sample_image, ortsindex
    ):
        """Die Nummer steht nicht in OpenStreetMap, und auch keine mit derselben fuehrenden Zahl.

        Dann zaehlt der Strassenpunkt, und die 150 m sagen, was er wert ist. Der Name behaelt die
        Adresse, die uns genannt wurde: Die Beschriftung ist genauer als der Punkt.
        """
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/77 Meyer/a.jpg")

        assert (foto.lat, foto.lon) == (53.6200, 9.6760)
        assert foto.place_name == "Hauptstrasse 77"
        assert foto.location_accuracy_m == place_service.ACCURACY_STREET_M

    def test_umnummerierte_hausnummer_landet_beim_nachbarn(
        self, session, settings, sample_image, ortsindex
    ):
        """Das Archiv sagt "9", der Ortsindex kennt nur "9a" -- dasselbe Haus, aufgeteilt.

        Ohne diese Ruecknahme laegen 57 Fotos des Erstbestands auf der Strassenmitte, darunter 38
        an einer einzigen Adresse. Der Name behaelt die Nummer, die uns genannt wurde; nur der
        Punkt kommt vom Nachbarn.
        """
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/9 Meyer/a.jpg")

        assert (foto.lat, foto.lon) == (53.6205, 9.6765)
        assert foto.place_name == "Hauptstrasse 9"
        assert foto.location_accuracy_m == place_service.ACCURACY_ADDRESS_M

    def _mit_gps(self, session, settings, sample_image, unterpfad: str):
        wurzel = settings.data_dir / "archiv"
        ziel = wurzel / unterpfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(sample_image("foto_mit_gps.jpg").read_bytes())

        outcome = import_file(session, ziel, settings)
        assert outcome.photo is not None
        apply_folder_meta(session, outcome.photo, ziel, wurzel, settings)
        return outcome.photo

    def test_ordneradresse_schlaegt_die_exif_koordinate(
        self, session, settings, sample_image, ortsindex
    ):
        """Umgekehrt als bis August 2026 -- und der Grund ist nachgemessen.

        Die alte Regel las sich als Messung gegen Ablage. Im Holmer Bestand ist sie das nicht:
        278 der 413 EXIF-verorteten Fotos teilen ihre Koordinate mit einem anderen, und an einem
        Punkt haengen 20 Fotos von **vier verschiedenen Tagen**. Sechs gleiche Nachkommastellen an
        vier Tagen liefert kein Empfaenger -- das ist eingetragen, nicht gemessen. Also steht eine
        Ablage gegen die andere, und nur eine davon macht sich am Ortsindex fest. 349 Fotos sassen
        so da, bis zu 700 m von der Adresse entfernt, die ihr eigener Ordner nannte.
        """
        foto = self._mit_gps(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert (foto.lat, foto.lon) == (53.6205, 9.6765)
        assert foto.place_name == "Hauptstrasse 14"
        assert foto.location_accuracy_m == place_service.ACCURACY_ADDRESS_M
        assert foto.location_source == "curator"

    def test_strassenmitte_schlaegt_die_exif_koordinate_nicht(
        self, session, settings, sample_image, ortsindex
    ):
        """Der Fehlerfall, wenn die Regel zu weit ginge.

        Ohne Hausnummer bleibt nur der Strassenpunkt, und der ist mit 150 m **groeber** als die
        Messung, die er ersetzen wuerde. Im Erstbestand traefe das 82 Fotos: Sie wuerden ungenauer,
        und niemand saehe es.
        """
        foto = self._mit_gps(session, settings, sample_image, "Hauptstrasse/a.jpg")

        assert foto.lat == pytest.approx(53.62053)
        assert foto.lon == pytest.approx(9.67601)
        assert foto.location_accuracy_m is None
        # Betiteln, benennen und beschlagworten darf der Ordner trotzdem.
        assert foto.place_name == "Hauptstrasse"

    def test_eine_menschliche_angabe_wird_nicht_ueberschrieben(
        self, session, settings, sample_image, ortsindex
    ):
        """Nur das EXIF gibt nach. Was ein Kurator oder ein Besucher gesagt hat, bleibt stehen."""
        wurzel = settings.data_dir / "archiv"
        ziel = wurzel / "Hauptstrasse" / "14 Museum" / "a.jpg"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())

        outcome = import_file(session, ziel, settings)
        outcome.photo.lat, outcome.photo.lon = 53.5, 9.5
        outcome.photo.location_source = "visitor"
        apply_folder_meta(session, outcome.photo, ziel, wurzel, settings)

        assert (outcome.photo.lat, outcome.photo.lon) == (53.5, 9.5)

    def test_die_strasse_steht_beim_foto_als_name(self, session, settings, sample_image, ortsindex):
        """Der Name traegt die Strasse ohne Nummer -- daran erkennt das Nachschaerfen sein Foto.

        Eine Ziffer im Namen hiesse, die Hausnummer sei bekannt, und die Frage entfiele. Siehe
        ``open_filter("housenumber")`` in ``services/needs.py``.
        """
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/119.jpg")

        assert foto.place_name == "Hauptstrasse"
        assert not any(zeichen.isdigit() for zeichen in foto.place_name)

    def test_die_herkunft_zeigt_auf_das_archiv(
        self, session, settings, sample_image, ortsindex, monkeypatch
    ):
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert foto.provenance == "Archiv, Verzeichnis 01 Orte/Hauptstrasse/14 Museum/a.jpg"

    def test_der_archivpfad_kommt_zu_dem_dazu_was_die_datei_sagt(
        self, session, settings, sample_image, ortsindex, monkeypatch
    ):
        """265 Fotos hatten den Pfad nie bekommen, weil ihre Datei schon eine Herkunft nannte.

        Wer ein Foto geliehen hat und wo es im Archiv lag, sind zwei Antworten auf zwei Fragen.
        Die erste steht in der Datei, die zweite nur im Pfad -- und die zweite laesst sich aus dem
        Bild nie wieder herstellen. Bis zum 16. August 2026 fuellte diese Zeile nur ein leeres
        Feld und liess den Pfad in genau den Faellen weg, in denen ohnehin schon jemand
        mitgedacht hatte.
        """
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        wurzel = settings.data_dir / "archiv"
        ziel = wurzel / "Hauptstrasse/14 Museum/a.jpg"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())
        foto = import_file(session, ziel, settings).photo
        foto.provenance = "Familie Rissler"

        apply_folder_meta(session, foto, ziel, wurzel, settings)

        assert foto.provenance == (
            "Familie Rissler, Archiv, Verzeichnis 01 Orte/Hauptstrasse/14 Museum/a.jpg"
        )

    def test_ohne_eingestellten_vorspann_bleibt_die_herkunft_leer(
        self, session, settings, sample_image, ortsindex
    ):
        """Nichts Ortsspezifisches im Code: ohne Einstellung wird nichts erfunden."""
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert foto.provenance is None

    def test_herkunft_wird_auch_ohne_erkannte_strasse_vermerkt(
        self, session, settings, sample_image, ortsindex, monkeypatch
    ):
        """Drei Fotos des Erstbestands hatten gar keine Herkunft -- und keinen Fehler dabei.

        Die Herkunft haengt am Pfad, nicht an der Strasse. Wurde keine erkannt, stieg
        ``apply_folder_meta`` aber schon vorher aus und nahm sie mit: zwei Fotos lagen lose in der
        Importwurzel, eines unter einem mehrdeutigen Strassennamen. Gerade dort ist der Pfad das
        Einzige, was von der Ablage uebrig bleibt.
        """
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        foto = self._importiere(session, settings, sample_image, "Irgendwas/lose.jpg")

        assert foto.place_name is None, "ohne Strasse wird weiterhin nicht verortet"
        assert foto.provenance == "Archiv, Verzeichnis 01 Orte/Irgendwas/lose.jpg"
