"""Tests des "Hilf mit"-Bereichs.

Der Kernpunkt: Beitraege werden direkt uebernommen, aber sie duerfen nur fuellen, was leer ist.
Ohne diesen Schutz koennte ein Besucher am oeffentlichen Touchscreen eine kuratierte Angabe
ueberschreiben -- und der naechste Besucher die des vorherigen.
"""

import json
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import Change, Photo, PhotoStatus, Place, Source
from app.services.needs import NEEDS
from app.services.places import normalize

# Holm
IN_HOLM = {"lat": 53.6205, "lon": 9.676}
WEIT_WEG = {"lat": 48.1372, "lon": 11.5756}  # München


class TestNaechsteAufgabe:
    def test_liefert_foto_ohne_ort(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, title="Ohne Ort", sha="a" * 64)
        make_photo(title="Vollstaendig", sha="b" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["photo"]["title"] == "Ohne Ort"
        assert daten["open_count"] == 1
        assert daten["photo"]["needs_location"] is True

    def test_liefert_foto_ohne_jahr(self, client: TestClient, session, make_photo):
        make_photo(year=None, title="Ohne Jahr", sha="a" * 64)
        make_photo(year=1932, title="Datiert", sha="b" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "date"}).json()

        assert daten["photo"]["title"] == "Ohne Jahr"
        assert daten["photo"]["date_label"] == "Jahr unbekannt"

    def test_weggetipptes_erscheint_nicht_sofort_wieder(
        self, client: TestClient, session, make_photo
    ):
        erst = make_photo(lat=None, lon=None, title="A", sha="a" * 64)
        make_photo(lat=None, lon=None, title="B", sha="b" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "location", "exclude": str(erst.id)}
        ).json()

        assert daten["photo"]["title"] == "B"

    def test_faengt_von_vorn_an_wenn_alles_durch_ist(self, client: TestClient, session, make_photo):
        """Lieber wiederholen als "nichts mehr da" melden, solange etwas offen ist."""
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        daten = client.get(
            "/api/contribute/next", params={"need": "location", "exclude": str(foto.id)}
        ).json()

        assert daten["photo"]["id"] == foto.id

    def test_nichts_offen(self, client: TestClient, session, make_photo):
        make_photo(sha="a" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["photo"] is None
        assert daten["open_count"] == 0

    def test_verstecktes_foto_wird_nicht_vorgelegt(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, status=PhotoStatus.DELETED, sha="a" * 64)
        session.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "location"}).json()["photo"] is None
        )


class TestEineDefinitionJeFrage:
    """Die SQL-Abfrage und die Eigenschaft am Foto muessen dasselbe sagen.

    Sie waren einmal zwei getrennte Formulierungen: ``_missing_filter`` im Endpunkt und
    ``needs_location`` am Modell. Beide sahen fuer sich richtig aus -- und genau so ein Paar
    laeuft auseinander, ohne dass es jemandem auffaellt. Die Zahl im Bereich stimmte dann nicht
    mehr mit den Fotos ueberein, die er vorlegt.
    """

    def test_die_offene_zahl_zaehlt_genau_die_fotos_die_die_eigenschaft_meldet(
        self, client: TestClient, session, make_photo
    ):
        make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(lat=None, lon=None, year=None, sha="b" * 64)
        make_photo(sha="c" * 64)
        make_photo(year=None, sha="d" * 64)
        make_photo(lat=None, lon=None, status=PhotoStatus.DELETED, sha="e" * 64)
        session.commit()

        fotos = session.scalars(select(Photo).where(Photo.status == PhotoStatus.PUBLISHED)).all()

        for frage, eigenschaft in (("location", "needs_location"), ("date", "needs_date")):
            gemeldet = client.get("/api/contribute/next", params={"need": frage}).json()
            erwartet = sum(1 for foto in fotos if getattr(foto, eigenschaft))
            assert gemeldet["open_count"] == erwartet, frage


class TestRangfolge:
    """Die Reihenfolge in ``NEEDS`` ist der Rang, und sie ist nur hier festgehalten.

    Ohne diesen Test liess sich die Reihenfolge vertauschen, ohne dass im Backend ein Test fiel --
    nachgeprueft am 11. August 2026, als sie tatsaechlich vertauscht wurde. Gemerkt hat es allein
    ein Test im Frontend, wo dieselbe Liste ein zweites Mal steht.
    """

    def test_der_ort_steht_vor_allem_anderen(self):
        """Ein Foto, das auf keiner Karte steht, ist die teuerste Luecke."""
        assert NEEDS[0] == "location"

    def test_die_hausnummer_steht_vor_dem_jahr(self):
        """Aus einer Zahl entschieden, nicht aus dem Gefuehl.

        Ein Jahr ist mehr wert als eine Hausnummer -- danach gefragt wird trotzdem spaeter. Eine
        Frage wird erst erreicht, wenn die vor ihr **leer** ist, und im Erstbestand stehen 673
        undatierte Fotos gegen 71 nachzuschaerfende. Hinter dem Jahr waere die dritte Frage nie
        erreicht worden: Der Bereich truege eine Frage, die niemand je gestellt bekommt.
        """
        assert NEEDS.index("housenumber") < NEEDS.index("date")


@pytest.fixture
def strassen(session):
    """Zwei Strassen, nur eine davon mit Adressen -- der Unterschied traegt einen ganzen Test."""

    def anlegen(name, kind, street=None, housenumber=None):
        session.add(
            Place(
                name=name,
                name_normalized=normalize(name),
                lat=53.62,
                lon=9.676,
                kind=kind,
                street=street,
                housenumber=housenumber,
            )
        )

    anlegen("Am Kamp", "strasse")
    for nummer in ("1", "2", "3"):
        anlegen(f"Am Kamp {nummer}", "adresse", street="Am Kamp", housenumber=nummer)
    # Eine Strasse ohne eine einzige Adresse -- davon hat der Ortsindex 141 von 486.
    anlegen("Feldweg", "strasse")
    anlegen("Strasse des 17. Juni", "strasse")
    anlegen("Strasse des 17. Juni 4", "adresse", street="Strasse des 17. Juni", housenumber="4")
    session.commit()
    return session


class TestNachschaerfen:
    """Wer bekommt die Frage „Genauer: welche Hausnummer?" vorgelegt.

    Der Bereich fragte bisher nur nach dem, was *fehlt*. Ein Foto auf der Mitte einer 800-m-Strasse
    galt als verortet und kam nie wieder -- dabei ist das der Fall, in dem jemand, der jeden Tag
    daran vorbeigeht, das Haus nennen koennte.
    """

    def _strassengenau(self, make_photo, **felder):
        return make_photo(
            place_name="Am Kamp",
            accuracy=150,
            location_source=Source.VISITOR,
            **felder,
        )

    def test_strassengenaues_foto_ohne_hausnummer_wird_vorgelegt(
        self, client: TestClient, strassen, make_photo
    ):
        self._strassengenau(make_photo, title="Nur die Strasse", sha="a" * 64)
        strassen.commit()

        daten = client.get("/api/contribute/next", params={"need": "housenumber"}).json()

        assert daten["photo"]["title"] == "Nur die Strasse"
        assert daten["open_count"] == 1

    def test_foto_mit_hausnummer_im_namen_wird_nicht_vorgelegt(
        self, client: TestClient, strassen, make_photo
    ):
        """Die 58 aus dem Erstbestand: Die Nummer ist bekannt, nur ihre Koordinate fehlt.

        Sie steht nicht im Ortsindex, weil das Haus aufgeteilt oder neu nummeriert wurde. Eine
        Nummernauswahl boete hier lauter Nummern an -- nur nicht die gesuchte. Das ist Arbeit fuer
        die Maschine, keine Frage an einen Besucher (siehe Backlog, Punkt 41).
        """
        make_photo(place_name="Am Kamp 11a", accuracy=150, sha="b" * 64)
        strassen.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_hausgenaues_foto_wird_nicht_vorgelegt(self, client: TestClient, strassen, make_photo):
        """Dieses Foto unterscheidet sich von einem nachschaerfbaren **nur** in der Genauigkeit.

        Der naheliegende Aufbau -- „Am Kamp 1", 15 m -- pruefte die Genauigkeit gar nicht: Das
        Foto fiele schon an der Ziffernregel heraus. Ein Gebaeudename fiele an der Adressbedingung
        heraus. Beides deckte die Gegenprobe auf, die die Genauigkeitsbedingung entfernte und alles
        gruen liess. Deshalb steht hier der blanke Strassenname bei 15 m: So haelt allein die
        Genauigkeit das Foto aus der Frage.

        Der Fall entsteht, wenn ein Kurator die Koordinate von Hand genau setzt und den
        Strassennamen stehen laesst.
        """
        make_photo(place_name="Am Kamp", accuracy=15, sha="c" * 64)
        strassen.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_foto_aus_dem_exif_wird_nicht_vorgelegt(self, client: TestClient, strassen, make_photo):
        """Seine Ungenauigkeit ist nicht schlecht, sondern *unbekannt* -- und von anderer Art.

        Das Geraet weiss, wo der Fotograf stand, nicht was er fotografiert hat. Dazu fehlt die
        Strasse, es gaebe also gar keine Nummern anzubieten. Eine eigene Frage, getrennt zu
        beantworten.
        """
        make_photo(place_name=None, accuracy=None, sha="d" * 64)
        strassen.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_strasse_ohne_adressen_wird_nicht_vorgelegt(
        self, client: TestClient, strassen, make_photo
    ):
        """Der stille Fehler: eine Frage auf dem Schirm, unter der kein einziger Knopf steht.

        141 der 486 Strassen im Ortsindex halten keine einzige Adresse. Ohne diese Bedingung
        stuende der Besucher vor „Genauer: welche Hausnummer?" und haette nichts zu tippen.
        """
        make_photo(place_name="Feldweg", accuracy=150, sha="e" * 64)
        strassen.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_kuratorenangabe_wird_ebenfalls_vorgelegt(
        self, client: TestClient, strassen, make_photo
    ):
        """Bewusst entschieden: Ein Anwohner kennt das Haus oft besser als das Archiv.

        Das weicht die Regel aus decisions.md Punkt 5 auf -- deshalb stellt die Ruecknahme die
        alte Quelle wieder her, statt aus Kuratorenwissen stillschweigend einen Besucherbeitrag
        zu machen.
        """
        make_photo(place_name="Am Kamp", accuracy=150, location_source=Source.CURATOR, sha="f" * 64)
        strassen.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 1
        )

    def test_strasse_mit_ziffer_im_namen_wird_nicht_vorgelegt(
        self, client: TestClient, strassen, make_photo
    ):
        """Die Ziffernregel irrt hier -- und zwar in die harmlose Richtung.

        „Strasse des 17. Juni" traegt eine Ziffer, ohne dass es eine Hausnummer waere. Das Foto
        wird deshalb nicht gefragt, obwohl es koennte. Lieber eine Frage zu wenig als eine
        Nummernauswahl vor jemandem, dessen Nummer laengst feststeht.
        """
        make_photo(place_name="Strasse des 17. Juni", accuracy=150, sha="g" * 64)
        strassen.commit()

        assert (
            client.get("/api/contribute/next", params={"need": "housenumber"}).json()["open_count"]
            == 0
        )

    def test_offene_andere_zaehlt_alle_uebrigen_fragen(
        self, client: TestClient, strassen, make_photo
    ):
        """``open_other`` entscheidet, ob „Weiss ich nicht" noch irgendwohin fuehrt.

        Mit drei Fragen muss es alle uebrigen zusammenzaehlen. Zaehlte es nur eine, verschwaende
        der Knopf, obwohl noch etwas offen ist.
        """
        make_photo(lat=None, lon=None, sha="h" * 64)
        make_photo(year=None, sha="i" * 64)
        strassen.commit()

        daten = client.get("/api/contribute/next", params={"need": "housenumber"}).json()

        assert daten["open_other"] == 2


class TestNummernZumFoto:
    """Was der Endpunkt anbietet -- und wann er bewusst nichts anbietet.

    Die leere Liste ist das Tor: Die Detailansicht zeigt die Auswahl, wenn hier etwas steht, und
    braucht keine eigene Regel. Eine Regel an zwei Stellen ist eine Regel, die sich irgendwann
    selbst widerspricht.
    """

    def test_liefert_die_nummern_der_strasse_des_fotos(
        self, client: TestClient, strassen, make_photo
    ):
        foto = make_photo(place_name="Am Kamp", accuracy=150, sha="a" * 64)
        strassen.commit()

        nummern = client.get(f"/api/contribute/{foto.id}/housenumbers").json()

        assert [eintrag["housenumber"] for eintrag in nummern] == ["1", "2", "3"]
        assert all(eintrag["accuracy_m"] == 15 for eintrag in nummern)

    def test_liefert_nichts_fuer_ein_bereits_hausgenaues_foto(
        self, client: TestClient, strassen, make_photo
    ):
        # Sonst bekaeme die Detailansicht Knoepfe fuer eine Frage, die keine ist.
        foto = make_photo(place_name="Am Kamp", accuracy=15, sha="b" * 64)
        strassen.commit()

        assert client.get(f"/api/contribute/{foto.id}/housenumbers").json() == []

    def test_liefert_nichts_fuer_eine_strasse_ohne_adressen(
        self, client: TestClient, strassen, make_photo
    ):
        foto = make_photo(place_name="Feldweg", accuracy=150, sha="c" * 64)
        strassen.commit()

        assert client.get(f"/api/contribute/{foto.id}/housenumbers").json() == []

    def test_unbekanntes_foto(self, client: TestClient, strassen):
        assert client.get("/api/contribute/999/housenumbers").status_code == 404


class TestHausnummerNachschaerfen:
    """Die Ausnahme zu „Besucher fuellen nur Leeres" -- und warum sie eine eigene Tuer hat.

    Der Endpunkt nimmt **keine Koordinate** entgegen, nur eine Nummer aus dem Ortsverzeichnis. Bei
    ``/location`` ist die vom Client behauptete Genauigkeit harmlos, *weil* das Feld ohnehin leer
    sein muss. Sobald sie darueber entschiede, was ueberschrieben werden darf, waere sie ein
    Schluessel -- und den haelt der Client.
    """

    def _foto(self, make_photo, **felder):
        return make_photo(place_name="Am Kamp", accuracy=150, sha="a" * 64, **felder)

    def _nummer(self, session, housenumber="2"):
        return session.scalar(
            select(Place).where(Place.kind == "adresse", Place.housenumber == housenumber)
        )

    def test_schaerft_die_strasse_zur_hausnummer(self, client: TestClient, strassen, make_photo):
        foto = self._foto(make_photo)
        strassen.commit()
        nummer = self._nummer(strassen)

        antwort = client.post(
            f"/api/contribute/{foto.id}/housenumber", json={"place_id": nummer.id}
        )

        assert antwort.status_code == 200
        assert antwort.json()["place_name"] == "Am Kamp 2"
        assert antwort.json()["location_accuracy_m"] == 15

    def test_nimmt_koordinate_und_genauigkeit_aus_dem_ortsverzeichnis(
        self, client: TestClient, strassen, make_photo
    ):
        """Der Angriffsfall: Der Client bestimmt nichts.

        Zusaetzliche Felder im Rumpf werden nicht gelesen -- Koordinate und Genauigkeit kommen aus
        der Zeile, die der Server nachschlaegt. Ginge das anders, koennte ein Aufruf mit
        ``accuracy_m: 1`` jede Angabe ersetzen.
        """
        foto = self._foto(make_photo)
        strassen.commit()
        nummer = self._nummer(strassen)

        client.post(
            f"/api/contribute/{foto.id}/housenumber",
            json={"place_id": nummer.id, "lat": 48.13, "lon": 11.57, "accuracy_m": 1},
        )
        strassen.refresh(foto)

        assert (foto.lat, foto.lon) == (nummer.lat, nummer.lon)
        assert foto.location_accuracy_m == 15

    def test_wird_mit_der_strasse_als_altwert_protokolliert(
        self, client: TestClient, strassen, make_photo
    ):
        # Der Altwert ist zugleich der Schluessel, mit dem die Ruecknahme die Strassenmitte
        # wiederfindet -- bei den beiden anderen Wegen ist er zu Recht leer.
        foto = self._foto(make_photo, location_source=Source.CURATOR)
        strassen.commit()
        nummer = self._nummer(strassen)

        client.post(f"/api/contribute/{foto.id}/housenumber", json={"place_id": nummer.id})

        eintrag = strassen.scalar(select(Change).where(Change.field == "housenumber"))
        assert eintrag.old_value == "Am Kamp"
        assert eintrag.new_value == "Am Kamp 2"
        assert eintrag.old_source == Source.CURATOR

    def test_hausnummer_einer_fremden_strasse_wird_abgewiesen(
        self, client: TestClient, strassen, make_photo
    ):
        foto = self._foto(make_photo)
        strassen.commit()
        fremd = strassen.scalar(
            select(Place).where(Place.kind == "adresse", Place.street == "Strasse des 17. Juni")
        )

        antwort = client.post(f"/api/contribute/{foto.id}/housenumber", json={"place_id": fremd.id})

        assert antwort.status_code == 422

    def test_eine_strasse_ist_keine_hausnummer(self, client: TestClient, strassen, make_photo):
        foto = self._foto(make_photo)
        strassen.commit()
        strasse = strassen.scalar(select(Place).where(Place.name == "Am Kamp"))

        antwort = client.post(
            f"/api/contribute/{foto.id}/housenumber", json={"place_id": strasse.id}
        )

        assert antwort.status_code == 404

    def test_bereits_hausgenaues_foto_wird_nicht_ueberschrieben(
        self, client: TestClient, strassen, make_photo
    ):
        foto = make_photo(place_name="Am Kamp 1", accuracy=15, sha="b" * 64)
        strassen.commit()
        nummer = self._nummer(strassen)

        antwort = client.post(
            f"/api/contribute/{foto.id}/housenumber", json={"place_id": nummer.id}
        )

        assert antwort.status_code == 409
        strassen.refresh(foto)
        assert foto.place_name == "Am Kamp 1"

    def test_unverortetes_foto_wird_nicht_geschaerft(
        self, client: TestClient, strassen, make_photo
    ):
        # Es gehoert in „Wo ist das?", nicht hierher -- und hat keine Strasse, zu der die Nummer
        # passen koennte.
        foto = make_photo(lat=None, lon=None, place_name=None, sha="c" * 64)
        strassen.commit()
        nummer = self._nummer(strassen)

        antwort = client.post(
            f"/api/contribute/{foto.id}/housenumber", json={"place_id": nummer.id}
        )

        assert antwort.status_code == 409

    def test_zweiter_besucher_kann_die_hausnummer_nicht_ersetzen(
        self, client: TestClient, strassen, make_photo
    ):
        """Die Regel „genauer darf ungenauer ersetzen, nie umgekehrt" -- in der Richtung, die
        weh tut.

        Ohne sie ueberschriebe der zweite Besucher den ersten, und genau das ist der Grund, warum
        Beitraege ueberhaupt ohne Moderation durchgehen duerfen.
        """
        foto = self._foto(make_photo)
        strassen.commit()
        erste = self._nummer(strassen, "1")
        zweite = self._nummer(strassen, "3")

        client.post(f"/api/contribute/{foto.id}/housenumber", json={"place_id": erste.id})
        antwort = client.post(
            f"/api/contribute/{foto.id}/housenumber", json={"place_id": zweite.id}
        )

        assert antwort.status_code == 409
        strassen.refresh(foto)
        assert foto.place_name == "Am Kamp 1"


class TestOrtErgaenzen:
    def test_uebernimmt_sofort(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        antwort = client.post(
            f"/api/contribute/{foto.id}/location",
            json={**IN_HOLM, "place_name": "Mühlenweg"},
        )

        assert antwort.status_code == 200
        daten = antwort.json()
        assert daten["needs_location"] is False
        assert daten["place_name"] == "Mühlenweg"
        assert daten["location_source"] == Source.VISITOR

    def test_erscheint_danach_auf_der_karte(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, year=1932, sha="a" * 64)
        session.commit()
        assert (
            client.get("/api/photos", params={"bbox": "9.60,53.57,9.75,53.67"}).json()["total"] == 0
        )

        client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)

        # Der unmittelbare Effekt ist der Reiz fuer den Besucher:
        # "mein Wissen ist jetzt auf der Karte".
        assert (
            client.get("/api/photos", params={"bbox": "9.60,53.57,9.75,53.67"}).json()["total"] == 1
        )

    def test_wird_protokolliert(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{foto.id}/location", json={**IN_HOLM, "session_id": "abc"})

        eintrag = session.scalars(select(Change).where(Change.photo_id == foto.id)).one()
        assert eintrag.field == "location"
        assert eintrag.source == Source.VISITOR
        assert eintrag.session_id == "abc"
        assert "53.62" in eintrag.new_value

    def test_besetztes_feld_wird_nicht_ueberschrieben(
        self, client: TestClient, session, make_photo
    ):
        """Was ein Kurator gesetzt hat, ist unantastbar -- und der zweite Besucher darf den
        ersten nicht ueberschreiben."""
        foto = make_photo(lat=53.61, lon=9.66, sha="a" * 64)
        session.commit()

        antwort = client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)

        assert antwort.status_code == 409
        session.refresh(foto)
        assert foto.lat == 53.61
        # Die Meldung soll den Besucher nicht als Stoerenfried behandeln.
        assert "Dank" in antwort.json()["detail"]

    def test_ort_ausserhalb_der_region(self, client: TestClient, session, settings, make_photo):
        (settings.data_dir / "region.json").write_text(
            json.dumps({"bbox": [9.60028, 53.57561, 9.75174, 53.66545]}), encoding="utf-8"
        )
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        antwort = client.post(f"/api/contribute/{foto.id}/location", json=WEIT_WEG)

        assert antwort.status_code == 422
        assert "ausserhalb" in antwort.json()["detail"].lower()

    def test_ohne_hinterlegte_region_wird_nicht_geprueft(
        self, client: TestClient, session, make_photo
    ):
        # Kein region.json vorhanden: dann lieber annehmen als grundlos ablehnen.
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        assert client.post(f"/api/contribute/{foto.id}/location", json=WEIT_WEG).status_code == 200

    def test_unbekanntes_foto(self, client: TestClient):
        assert client.post("/api/contribute/9999/location", json=IN_HOLM).status_code == 404


class TestJahrErgaenzen:
    def test_jahresangabe(self, client: TestClient, session, make_photo):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        daten = client.post(
            f"/api/contribute/{foto.id}/date", json={"year": 1932, "precision": "year"}
        ).json()

        assert daten["date_label"] == "1932"
        assert daten["needs_date"] is False
        assert daten["date_source"] == Source.VISITOR

    def test_jahrzehnt_wird_zum_intervall(self, client: TestClient, session, make_photo):
        """ "Irgendwann in den Zwanzigern" ist die haeufigste ehrliche Antwort."""
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        daten = client.post(
            f"/api/contribute/{foto.id}/date", json={"year": 1924, "precision": "decade"}
        ).json()

        assert daten["date_label"] == "1920er"
        assert daten["date_from"] == "1920-01-01"
        assert daten["date_to"] == "1929-12-31"

    def test_so_datiertes_foto_erscheint_bei_ueberlappender_auswahl(
        self, client, session, make_photo
    ):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()
        client.post(f"/api/contribute/{foto.id}/date", json={"year": 1924, "precision": "decade"})

        antwort = client.get(
            "/api/photos",
            params={"bbox": "9.60,53.57,9.75,53.67", "from_year": 1925, "to_year": 1930},
        )

        assert antwort.json()["total"] == 1

    def test_bereits_datiertes_foto(self, client: TestClient, session, make_photo):
        foto = make_photo(year=1932, sha="a" * 64)
        session.commit()

        antwort = client.post(
            f"/api/contribute/{foto.id}/date", json={"year": 1800, "precision": "year"}
        )

        assert antwort.status_code == 409
        session.refresh(foto)
        assert foto.date_from == date(1932, 1, 1)

    def test_unsinniges_jahr_wird_abgewiesen(self, client: TestClient, session, make_photo):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        assert (
            client.post(
                f"/api/contribute/{foto.id}/date", json={"year": 3000, "precision": "year"}
            ).status_code
            == 422
        )

    def test_wird_protokolliert(self, client: TestClient, session, make_photo):
        foto = make_photo(year=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{foto.id}/date", json={"year": 1924, "precision": "decade"})

        eintrag = session.scalars(select(Change).where(Change.field == "date")).one()
        assert eintrag.new_value == "1920er"
        assert eintrag.source == Source.VISITOR


class TestZusammenspiel:
    def test_beide_luecken_nacheinander_fuellen(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, year=None, sha="a" * 64)
        session.commit()

        client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)
        client.post(f"/api/contribute/{foto.id}/date", json={"year": 1955, "precision": "year"})

        daten = client.get(f"/api/photos/{foto.id}").json()
        assert daten["needs_location"] is False
        assert daten["needs_date"] is False
        assert len(session.scalars(select(Change)).all()) == 2

    def test_offene_zahl_sinkt(self, client: TestClient, session, make_photo):
        foto = make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(lat=None, lon=None, sha="b" * 64)
        session.commit()

        assert client.get("/api/contribute/next?need=location").json()["open_count"] == 2
        client.post(f"/api/contribute/{foto.id}/location", json=IN_HOLM)
        assert client.get("/api/contribute/next?need=location").json()["open_count"] == 1


class TestOrtssuche:
    def _lege_orte_an(self, session):
        from app.models import Place
        from app.services.places import normalize

        for name, art, lat, lon in [
            ("Mühlenweg", "strasse", 53.62, 9.67),
            ("Alte Mühlenstraße", "strasse", 53.63, 9.68),
            ("Mühlenteich", "natur", 53.61, 9.66),
            ("Hauptstraße", "strasse", 53.64, 9.67),
        ]:
            session.add(
                Place(name=name, name_normalized=normalize(name), lat=lat, lon=lon, kind=art)
            )
        session.commit()

    def test_findet_trotz_fehlendem_umlaut(self, client: TestClient, session):
        self._lege_orte_an(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "muhlen"}).json()]

        assert "Mühlenweg" in namen

    def test_wortanfang_steht_vorn(self, client: TestClient, session):
        """Wer "Muhl" tippt, meint den Mühlenweg, nicht die Alte Mühlenstraße."""
        self._lege_orte_an(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "muhl"}).json()]

        assert namen[0] == "Mühlenweg"
        assert "Alte Mühlenstraße" in namen

    def test_scharfes_s(self, client: TestClient, session):
        self._lege_orte_an(session)

        namen = [o["name"] for o in client.get("/api/places", params={"q": "hauptstrasse"}).json()]

        assert namen == ["Hauptstraße"]

    def test_zu_kurze_eingabe_liefert_nichts(self, client: TestClient, session):
        self._lege_orte_an(session)

        assert client.get("/api/places", params={"q": "m"}).json() == []
        assert client.get("/api/places").json() == []


class TestOrtsverzeichnisLaden:
    def test_aus_datei(self, session, settings):
        from app.services.places import load_from_file

        settings.places_file.write_text(
            json.dumps(
                [
                    {
                        "name": "Süderstraße",
                        "name_normalized": "veraltet",
                        "lat": 53.6,
                        "lon": 9.6,
                        "kind": "strasse",
                    }
                ]
            ),
            encoding="utf-8",
        )

        anzahl = load_from_file(session, settings.places_file)

        assert anzahl == 1
        from app.models import Place

        ort = session.scalars(select(Place)).one()
        # Die Normalisierung wird neu berechnet: eine aeltere Datei wuerde die Suche sonst
        # stillschweigend leer laufen lassen.
        assert ort.name_normalized == "suderstrasse"

    def test_fehlende_datei_ist_kein_fehler(self, session, settings):
        from app.services.places import load_from_file

        assert load_from_file(session, settings.data_dir / "gibtsnicht.json") == 0


class TestLetzteAufgabe:
    def test_zaehlt_auch_die_andere_frage(self, client: TestClient, session, make_photo):
        """Davon haengt ab, ob "Weiss ich nicht" ueberhaupt noch irgendwohin fuehrt.

        Ist sonst nichts offen, kaeme dasselbe Foto zurueck -- dann steht der Knopf besser gar
        nicht da.
        """
        make_photo(lat=None, lon=None, sha="a" * 64)
        make_photo(year=None, sha="b" * 64)
        make_photo(year=None, sha="c" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["open_count"] == 1, "ein Foto ohne Ort"
        assert daten["open_other"] == 2, "zwei ohne Jahr"

    def test_letzte_aufgabe_hat_nichts_daneben(self, client: TestClient, session, make_photo):
        make_photo(lat=None, lon=None, sha="a" * 64)
        session.commit()

        daten = client.get("/api/contribute/next", params={"need": "location"}).json()

        assert daten["open_count"] == 1
        assert daten["open_other"] == 0
