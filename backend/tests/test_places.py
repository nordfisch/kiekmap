"""Tests des Ortsindex und der Hausnummern.

Der Kernpunkt: Eine Strasse von 800 m bekommt einen Punkt. Ohne Hausnummern liegen alle Fotos
einer Strasse uebereinander, und "hier war das" ist um bis zu 400 m falsch.

Zwei Fehler dabei passieren still:

  1. Adressen verdraengen die Strassen aus der Trefferliste -- zwoelf Plaetze sind nach den
     Hausnummern eines Muehlenwegs voll.
  2. Hausnummern werden alphabetisch sortiert. Dann kommt die 10 vor der 9.
"""

import pytest
from fastapi.testclient import TestClient

from app.models import Place
from app.services import places as place_service


@pytest.fixture
def ortsindex(session):
    """Ein Ausschnitt aus Holm: zwei Strassen, eine davon mit Hausnummern."""

    def anlegen(name, kind, lat=53.62, lon=9.676, street=None, housenumber=None):
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

    anlegen("Muehlenweg", "strasse")
    anlegen("Muehlenteich", "natur")
    anlegen("Alte Muehlenstrasse", "strasse")
    # Absichtlich in einer Reihenfolge, die alphabetisch falsch herauskaeme.
    for nummer in ("9", "10", "1a", "2", "1", "12"):
        anlegen(f"Muehlenweg {nummer}", "adresse", street="Muehlenweg", housenumber=nummer)
    session.commit()
    return session


class TestFreieSuche:
    def test_adressen_verdraengen_die_strassen_nicht(self, ortsindex):
        """Der Grund fuer die zwei Schritte.

        Ohne diese Regel waere die Liste nach den Hausnummern des Muehlenwegs voll -- und der
        Muehlenteich, den jemand vielleicht meinte, faende sich nicht mehr darin.
        """
        treffer = place_service.search(ortsindex, "muehlen")

        arten = {ort.kind for ort in treffer}
        assert "adresse" not in arten
        assert {"Muehlenweg", "Muehlenteich", "Alte Muehlenstrasse"} <= {t.name for t in treffer}

    def test_hausnummer_mit_ziffer_wird_direkt_gefunden(self, ortsindex):
        """Wer die Nummer weiss, tippt sie."""
        treffer = place_service.search(ortsindex, "muehlenweg 12")

        assert [ort.name for ort in treffer] == ["Muehlenweg 12"]

    def test_strasse_steht_weiterhin_vor_der_natur(self, ortsindex):
        treffer = place_service.search(ortsindex, "muehlen")

        assert treffer[0].name == "Muehlenweg"

    def test_umlaut_toleranz_gilt_auch_fuer_adressen(self, session):
        session.add(
            Place(
                name="Mühlenweg 12",
                name_normalized=place_service.normalize("Mühlenweg 12"),
                lat=53.62,
                lon=9.676,
                kind="adresse",
                street="Mühlenweg",
                housenumber="12",
            )
        )
        session.commit()

        assert place_service.search(session, "muhlenweg 12")


class TestHausnummern:
    def test_werden_natuerlich_sortiert(self, ortsindex):
        """Alphabetisch kaeme die 10 vor der 9 und die 1a vor der 2."""
        strasse = next(
            ort for ort in place_service.search(ortsindex, "muehlenweg") if ort.kind == "strasse"
        )

        nummern = [ort.housenumber for ort in place_service.housenumbers(ortsindex, strasse)]

        assert nummern == ["1", "1a", "2", "9", "10", "12"]

    def test_sortierschluessel_kommt_ohne_zahl_aus(self):
        # In OSM steht gelegentlich Unsinn im Feld. Absturz waere die schlechteste Antwort.
        assert place_service.sort_key("ohne") == (0, "ohne")
        assert place_service.sort_key("") == (0, "")

    def test_strasse_ohne_hausnummern_bleibt_beantwortbar(self, ortsindex):
        """Nicht jede Strasse ist in OpenStreetMap erfasst -- der Schritt entfaellt dann."""
        andere = next(
            ort for ort in place_service.search(ortsindex, "alte muehlen") if ort.kind == "strasse"
        )

        assert place_service.housenumbers(ortsindex, andere) == []


class TestStrassenZurWahl:
    """Die Strassen, die der Beitragsbereich als Knoepfe vorlegt.

    Sie ersetzen dort das Suchfeld -- ohne Tastatur ist es das einzige Bedienelement der
    Besucheransicht, das nichts annimmt.
    """

    @pytest.fixture
    def weitlaeufig(self, session):
        """Zwei Strassen im Ort, eine im Nachbardorf sieben Kilometer weiter."""

        def anlegen(name, lat, lon):
            session.add(
                Place(
                    name=name,
                    name_normalized=place_service.normalize(name),
                    lat=lat,
                    lon=lon,
                    kind="strasse",
                )
            )

        anlegen("Zippelhornweg", 53.6205, 9.6762)
        anlegen("Hauptstrasse", 53.6210, 9.6755)
        anlegen("Ferner Deich", 53.5800, 9.7400)
        session.commit()
        return session

    def test_nimmt_die_ortsnaechsten(self, weitlaeufig):
        gewaehlt = place_service.nearby_streets(weitlaeufig, (53.62053, 9.67601), limit=2)

        assert [ort.name for ort in gewaehlt] == ["Hauptstrasse", "Zippelhornweg"]

    def test_liefert_alphabetisch_und_nicht_nach_entfernung(self, weitlaeufig):
        """Der Besucher sucht seine Strasse im Alphabet, nicht im Umkreis.

        Die Naehe entscheidet nur, *welche* Strassen dabei sind.
        """
        gewaehlt = place_service.nearby_streets(weitlaeufig, (53.62053, 9.67601), limit=9)

        assert [ort.name for ort in gewaehlt] == ["Ferner Deich", "Hauptstrasse", "Zippelhornweg"]

    def test_umlaut_sortiert_wie_der_grundbuchstabe(self, session):
        """Sonst stuende der Oelmuehlenweg hinter dem Z und bekaeme einen eigenen Knopf.

        In Holm gibt es keine solche Strasse -- beim zweiten Museum faellt es sonst still auf.
        """
        for name in ("Zwickauer Weg", "Ölmühlenweg", "Ostweg"):
            session.add(
                Place(
                    name=name,
                    name_normalized=place_service.normalize(name),
                    lat=53.62,
                    lon=9.676,
                    kind="strasse",
                )
            )
        session.commit()

        gewaehlt = place_service.nearby_streets(session, (53.62, 9.676), limit=9)

        assert [ort.name for ort in gewaehlt] == ["Ölmühlenweg", "Ostweg", "Zwickauer Weg"]

    def test_ohne_region_lieber_leer_als_beliebig(self, weitlaeufig):
        """Ohne 'make tiles' gibt es keinen Mittelpunkt -- dann ist keine Strasse die naechste."""
        assert place_service.nearby_streets(weitlaeufig, None, limit=9) == []


class TestUeberDieApi:
    def test_hausnummern_ueber_die_nummer_der_strasse(self, client: TestClient, ortsindex):
        strasse = place_service.search(ortsindex, "muehlenweg")[0]

        daten = client.get(f"/api/places/{strasse.id}/housenumbers").json()

        assert [eintrag["housenumber"] for eintrag in daten] == ["1", "1a", "2", "9", "10", "12"]

    def test_unbekannte_strasse(self, client: TestClient, ortsindex):
        antwort = client.get("/api/places/9999/housenumbers")

        assert antwort.status_code == 404

    def test_strassen_zur_wahl(self, client: TestClient, ortsindex, settings):
        """'/streets' darf nicht als Ortsnummer gelesen werden -- daher stehen die Routen so."""
        import json

        settings.region_file.write_text(
            json.dumps({"center": [9.676, 53.62], "streetChoice": 1}), encoding="utf-8"
        )

        daten = client.get("/api/places/streets").json()

        assert [eintrag["name"] for eintrag in daten] == ["Alte Muehlenstrasse"]
        assert daten[0]["accuracy_m"] == place_service.ACCURACY_STREET_M

    def test_hausnummer_ist_genauer_als_die_strasse(self, client: TestClient, ortsindex):
        """Die Genauigkeit reist mit -- der Kurator sieht spaeter, worauf Verlass ist."""
        strasse = client.get("/api/places", params={"q": "muehlenweg"}).json()[0]
        nummer = client.get("/api/places", params={"q": "muehlenweg 12"}).json()[0]

        assert strasse["accuracy_m"] == place_service.ACCURACY_STREET_M
        assert nummer["accuracy_m"] == place_service.ACCURACY_ADDRESS_M
        assert nummer["accuracy_m"] < strasse["accuracy_m"]


class TestLaden:
    def test_hausnummern_kommen_aus_der_datei_mit(self, session, settings):
        import json

        settings.places_file.write_text(
            json.dumps(
                [
                    {"name": "Muehlenweg", "lat": 53.62, "lon": 9.676, "kind": "strasse"},
                    {
                        "name": "Muehlenweg 12",
                        "lat": 53.621,
                        "lon": 9.677,
                        "kind": "adresse",
                        "street": "Muehlenweg",
                        "housenumber": "12",
                    },
                ]
            ),
            encoding="utf-8",
        )

        anzahl = place_service.load_from_file(session, settings.places_file)

        assert anzahl == 2
        adresse = place_service.search(session, "muehlenweg 12")[0]
        assert (adresse.street, adresse.housenumber) == ("Muehlenweg", "12")


class TestStrasseUnterIhremNamen:
    """``street_named`` schlaegt exakt nach, ohne zu normalisieren.

    ``normalize()`` ist fuer das gedacht, was jemand tippt. Hier wird ein Wert nachgeschlagen, der
    aus dem Ortsindex in ``photo.place_name`` **kopiert** wurde -- und derselbe String ist der Weg,
    auf dem eine zurueckgenommene Nachschaerfung ihre Strassenmitte wiederfindet.
    """

    def test_findet_die_strasse_unter_ihrem_gespeicherten_namen(self, ortsindex):
        gefunden = place_service.street_named(ortsindex, "Muehlenweg")

        assert gefunden is not None
        assert gefunden.kind == "strasse"

    def test_findet_keine_adresse(self, ortsindex):
        # Sonst liefe eine Ruecknahme auf einer Hausnummer statt auf der Strassenmitte auf.
        assert place_service.street_named(ortsindex, "Muehlenweg 12") is None

    def test_normalisiert_nicht(self, ortsindex):
        """Eine andere Schreibweise ist eine andere Strasse -- lieber nichts als das Falsche."""
        assert place_service.street_named(ortsindex, "muehlenweg") is None
