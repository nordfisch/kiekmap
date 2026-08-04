"""Tests der Pfad-Schicht: was die Ordnerstruktur ueber ein Foto sagt.

Ein Museumsarchiv ist sortiert, und die Sortierung ist eine Aussage. Sie zu verwerfen hiesse,
Besucher nach dem Ort eines Fotos zu fragen, dessen Adresse im Ordnernamen steht.

Drei Fehler passieren dabei still, und jeder hat hier seinen Test:

  1. Aus "10 H Brahms" wird die Hausnummer 10h. Die gibt es nicht -- das Foto landet auf der
     Strasse statt am Haus, und niemand sieht, dass etwas schiefging.
  2. Der Ordner ueberschreibt eine Koordinate, die in der Datei stand. Die Kamera stand
     tatsaechlich dort; der Ordner ist die Ablage von jemandem.
  3. Eine Strasse ohne Hausnummer wird trotzdem verortet. Dann faellt das Foto aus "Wo ist das?"
     heraus -- und liegt bis zu 400 m falsch.
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

    def test_zahlname_wird_kein_titel(self, ortsindex):
        """ "049" ist eine Hausnummer, kein Name -- der Titel darf sie nicht doppelt fuehren.

        Sonst hiesse ein Foto "Hauptstrasse 49, 049".
        """
        assert split_housenumber("049") == ("49", None)

        angabe = parse_path(("Hauptstrasse", "049"), street_names(ortsindex))
        assert angabe.title == "Hauptstrasse 49"


class TestPfadLesen:
    def test_der_ortsindex_erkennt_die_strasse_nicht_der_ordnername(self, ortsindex):
        """Es gibt keinen "Strassen"-Schalter im Code -- sonst waere Holm darin verdrahtet."""
        strassen = street_names(ortsindex)

        angabe = parse_path(("Strassen", "Hauptstrasse", "14 Gasthof Petersen"), strassen)

        assert angabe.street == "Hauptstrasse"
        assert angabe.housenumber == "14"
        assert angabe.name == "Gasthof Petersen"
        assert angabe.title == "Hauptstrasse 14, Gasthof Petersen"

    def test_ohne_bekannte_strasse_sagt_der_pfad_nichts(self, ortsindex):
        angabe = parse_path(("Urlaub", "2019"), street_names(ortsindex))

        assert angabe.street is None
        assert angabe.title is None

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

    def test_die_strasse_darf_der_gewaehlte_ordner_selbst_sein(self, ortsindex):
        """Am Stick waehlt der Ehrenamtliche den Ordner -- oft die Strasse."""
        angabe = parse_path(("Hauptstrasse", "14 Museum"), street_names(ortsindex))

        assert (angabe.street, angabe.housenumber) == ("Hauptstrasse", "14")


class TestWasAmFotoLandet:
    def _importiere(self, session, settings, sample_image, unterpfad: str):
        wurzel = settings.data_dir / "archiv"
        ziel = wurzel / unterpfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(sample_image("scan_ohne_exif.jpg").read_bytes())

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
        assert foto.title == "Hauptstrasse 14, Museum"

    def test_strasse_ohne_hausnummer_bleibt_unverortet(
        self, session, settings, sample_image, ortsindex
    ):
        """Sonst liefe "Wo ist das?" leer -- bei 124 Fotos des Erstbestands.

        Der Strassenpunkt saehe aus wie eine Antwort. Er ist bis zu 400 m daneben, und das Foto
        gilt danach als verortet, kommt also nie mehr jemandem vor die Augen, der das Haus kennt.
        Als Schlagwort bleibt die Strasse trotzdem stehen.
        """
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/119.jpg")

        assert foto.needs_location
        assert foto.lat is None and foto.location_accuracy_m is None
        assert "Hauptstrasse" in {schlagwort.name for schlagwort in foto.tags}

    def test_unbekannte_hausnummer_faellt_auf_die_strasse_zurueck(
        self, session, settings, sample_image, ortsindex
    ):
        """Die Nummer steht nicht in OpenStreetMap -- 12 Faelle im Erstbestand.

        Dann zaehlt der Strassenpunkt, und die 150 m sagen, was er wert ist. Der Name behaelt die
        Adresse, die uns genannt wurde: Die Beschriftung ist genauer als der Punkt.
        """
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/77 Meyer/a.jpg")

        assert (foto.lat, foto.lon) == (53.6200, 9.6760)
        assert foto.place_name == "Hauptstrasse 77"
        assert foto.location_accuracy_m == place_service.ACCURACY_STREET_M

    def test_koordinate_aus_der_datei_schlaegt_den_ordner(
        self, session, settings, sample_image, ortsindex
    ):
        """Die Kamera stand dort. Der Ordner ist die Ablage von jemandem."""
        wurzel = settings.data_dir / "archiv"
        ziel = wurzel / "Hauptstrasse" / "14 Museum" / "a.jpg"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(sample_image("foto_mit_gps.jpg").read_bytes())

        outcome = import_file(session, ziel, settings)
        apply_folder_meta(session, outcome.photo, ziel, wurzel, settings)

        assert outcome.photo.lat == pytest.approx(53.62053)
        assert outcome.photo.lon == pytest.approx(9.67601)
        # Der Ordner darf trotzdem betiteln, benennen und beschlagworten -- nur nicht verorten.
        assert outcome.photo.title == "Hauptstrasse 14, Museum"
        assert outcome.photo.place_name == "Hauptstrasse 14"
        assert outcome.photo.location_accuracy_m is None

    def test_die_strasse_steht_beim_foto_auch_ohne_punkt(
        self, session, settings, sample_image, ortsindex
    ):
        """Wer im Kiosk gefragt wird "wo ist das?", soll wenigstens die Strasse dabei lesen."""
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/119.jpg")

        assert foto.place_name == "Hauptstrasse"
        assert foto.needs_location

    def test_die_herkunft_zeigt_auf_das_archiv(
        self, session, settings, sample_image, ortsindex, monkeypatch
    ):
        monkeypatch.setattr(settings, "import_provenance", "Archiv, Verzeichnis 01 Orte/")

        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert foto.provenance == "Archiv, Verzeichnis 01 Orte/Hauptstrasse/14 Museum/a.jpg"

    def test_ohne_eingestellten_vorspann_bleibt_die_herkunft_leer(
        self, session, settings, sample_image, ortsindex
    ):
        """Nichts Ortsspezifisches im Code: ohne Einstellung wird nichts erfunden."""
        foto = self._importiere(session, settings, sample_image, "Hauptstrasse/14 Museum/a.jpg")

        assert foto.provenance is None
