# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Tests der Sicherung auf USB-Stick.

Drei Zusagen tragen diese Stufe, und alle drei brechen still:

  1. Ein gewoehnlicher Ordner unter /media ist kein Stick. Ohne diese Pruefung landet die
     Sicherung auf derselben SD-Karte, gegen deren Ausfall sie schuetzen soll.
  2. Die zweite Sicherung kopiert nichts noch einmal. Bricht das, dauert sie eine Stunde statt
     Sekunden -- und wird nicht mehr gemacht.
  3. Wiederherstellen legt den bisherigen Bestand beiseite, statt ihn zu loeschen. Wer die
     falsche Sicherung einspielt, soll nicht alles verloren haben.
  4. Eine zurueckgespielte Sicherung bringt ihr Schema mit, und das Programm zieht es nach.
     Ohne das sieht das Geraet normal aus und nimmt trotzdem nichts mehr an.
"""

import io
import sqlite3
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.services import backup, schema
from app.services.storage import THUMBNAIL_SIZES, original_path, thumbnail_path

#: Das Anfangsschema -- der Stand, auf dem eine Sicherung von vor der ersten Migration steht.
#: Namentlich, weil genau diese Revision der Fall vom 12. August 2026 war.
ANFANGSSCHEMA = "1cf9ccd28cd7"


@pytest.fixture
def stick(tmp_path: Path, settings, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Ein Ordner, der als USB-Stick durchgeht.

    Ein echter Einhaengepunkt laesst sich im Test nicht herstellen, deshalb steht die Pruefung
    ``drives._is_mounted`` fuer diesen einen Ordner still.
    """
    media = tmp_path / "media"
    drive = media / "SANDISK"
    drive.mkdir(parents=True)

    settings.media_dir = media
    monkeypatch.setattr(backup.drives, "_is_mounted", lambda path: path == drive)
    return drive


@pytest.fixture
def collection(settings):
    """Fotos auf der Platte, so abgelegt wie der Import es tut."""

    def create(count: int = 3) -> list[str]:
        shas = []
        for index in range(count):
            sha = f"{index:064x}"
            original = original_path(settings.photos_dir, sha, ".jpg")
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes(b"bild-" + str(index).encode())
            for size in THUMBNAIL_SIZES:
                thumb = thumbnail_path(settings.thumbs_dir, sha, size)
                thumb.parent.mkdir(parents=True, exist_ok=True)
                thumb.write_bytes(b"vorschau")
            shas.append(sha)
        return shas

    return create


def _drive(settings) -> backup.Drive:
    return backup.find_drives(settings.media_dir)[0]


def _nichts_melden(done: int, total: int, message: str) -> None:
    pass


class TestDatentraegerErkennen:
    def test_ohne_stick_keine_auswahl(self, settings, tmp_path: Path):
        settings.media_dir = tmp_path / "media"

        assert backup.find_drives(settings.media_dir) == []

    def test_stick_wird_gefunden(self, settings, stick: Path):
        gefunden = backup.find_drives(settings.media_dir)

        assert len(gefunden) == 1
        assert gefunden[0].name == "SANDISK"
        assert gefunden[0].free_bytes > 0

    def test_gewoehnlicher_ordner_ist_kein_stick(self, settings, stick: Path):
        """Der wichtigste Fall hier.

        Wuerde ein liegengebliebener Ordner unter /media als Ziel angeboten, liefe die Sicherung
        auf dieselbe SD-Karte, gegen deren Ausfall sie schuetzen soll -- und niemand saehe es.
        """
        (stick.parent / "nur-ein-ordner").mkdir()

        namen = [drive.name for drive in backup.find_drives(settings.media_dir)]

        assert namen == ["SANDISK"]

    def test_stick_auch_zwei_ebenen_tief(
        self, settings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Raspberry Pi OS haengt unter /media/<benutzer>/<bezeichnung> ein."""
        media = tmp_path / "media"
        tief = media / "pi" / "USB-STICK"
        tief.mkdir(parents=True)
        settings.media_dir = media
        monkeypatch.setattr(backup.drives, "_is_mounted", lambda path: path == tief)

        gefunden = backup.find_drives(media)

        assert [drive.name for drive in gefunden] == ["USB-STICK"]

    def test_ein_symlink_ist_kein_datentraeger(
        self, settings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Der Fall, der am 14. August 2026 wirklich passiert ist.

        Ein Symlink unter /media sieht wie ein gewoehnlicher Ordner aus, denn ``os.path.ismount``
        sagt fuer einen Symlink grundsaetzlich nein. Damit steigt die Suche eine Ebene hinab --
        die Ebene, die es fuer ``/media/<benutzer>/<bezeichnung>`` braucht -- und folgt ihm
        dabei ueberallhin. Auf dem Entwicklungsmac zeigte ein ``/Volumes/Danger`` auf die Wurzel,
        und der Verwaltungsbereich bot das Datenverzeichnis selbst als Sicherungsziel an. Die
        Sicherung landete im Ordner, den sie sichert -- mit Handzettel, also aussehend wie eine
        richtige.
        """
        media = tmp_path / "media"
        media.mkdir()
        anderswo = tmp_path / "anderswo"
        eingehaengt = anderswo / "data"
        eingehaengt.mkdir(parents=True)
        (media / "Danger").symlink_to(anderswo)
        settings.media_dir = media
        # Aufgeloest verglichen, nicht woertlich: Sonst bildet die eingesetzte Pruefung den
        # Symlink gar nicht ab, und der Test waere auch ohne die Absicherung gruen.
        monkeypatch.setattr(
            backup.drives, "_is_mounted", lambda path: path.resolve() == eingehaengt.resolve()
        )

        assert backup.find_drives(media) == []

    def test_schreibgeschuetzter_datentraeger_wird_nicht_angeboten(
        self, settings, stick: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Sonst faellt es erst auf, nachdem jemand den Knopf gedrueckt hat.

        Auf dem Mac faengt diese Pruefung ausserdem die Systemeinhaengungen unter /Volumes ab,
        die sonst als Sicherungsziel in der Liste stuenden.
        """
        monkeypatch.setattr(backup.drives, "_is_writable", lambda path: False)

        assert backup.find_drives(settings.media_dir) == []

    def test_ausgedachter_pfad_wird_nicht_angenommen(self, settings, stick: Path):
        """Der Pfad kommt aus dem Browser zurueck -- er ist Eingabe, keine Tatsache."""
        assert backup.find_drive(settings.media_dir, "/") is None
        assert backup.find_drive(settings.media_dir, str(stick)) is not None


class TestSicherung:
    def test_fotos_und_angaben_landen_auf_dem_stick(self, session, settings, stick, collection):
        shas = collection(3)

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        ziel = stick / backup.BACKUP_DIR_NAME
        assert (ziel / "kiekmap.db").is_file()
        for sha in shas:
            assert (ziel / "photos" / sha[0:2] / sha[2:4] / f"{sha}.jpg").is_file()

    def test_vorschaubilder_wandern_mit(self, session, settings, stick, collection):
        """Sonst rechnete ein wiederhergestelltes Geraet erst eine Stunde, bevor es etwas zeigt."""
        sha = collection(1)[0]

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        ziel = stick / backup.BACKUP_DIR_NAME
        for size in THUMBNAIL_SIZES:
            assert (ziel / "thumbs" / str(size) / sha[0:2] / sha[2:4] / f"{sha}.webp").is_file()

    def test_zweite_sicherung_kopiert_nichts_noch_einmal(
        self, session, settings, stick, collection
    ):
        """Der Grund, warum ueberhaupt jemand ein zweites Mal sichert."""
        collection(3)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        meldung = backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        # Die Angaben werden immer neu geschrieben, die Bilder nicht.
        assert "Neue Bilder gab es nicht" in meldung

    def test_neues_foto_kommt_beim_zweiten_mal_dazu(self, session, settings, stick, collection):
        collection(2)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)
        neu = "f" * 64
        pfad = original_path(settings.photos_dir, neu, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"noch ein bild")

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        ziel = stick / backup.BACKUP_DIR_NAME / "photos" / neu[0:2] / neu[2:4] / f"{neu}.jpg"
        assert ziel.is_file()

    def test_zu_wenig_platz_wird_vorher_gesagt(self, session, settings, stick, collection):
        """Lieber gar nicht anfangen als auf halber Strecke stehen bleiben."""
        collection(2)
        laufwerk = _drive(settings)
        laufwerk.free_bytes = 1

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_backup(session, settings, laufwerk, _nichts_melden)

        assert "zu wenig Platz" in str(fehler.value)

    def test_fortschritt_zaehlt_fotos(self, session, settings, stick, collection):
        collection(3)
        schritte = []

        backup.run_backup(
            session, settings, _drive(settings), lambda d, t, m: schritte.append((d, t))
        )

        assert schritte[-1] == (3, 3)

    def test_manifest_nennt_anzahl_und_ort(self, session, settings, stick, collection):
        collection(2)
        (settings.data_dir / "region.json").write_text('{"name": "Holm"}', encoding="utf-8")

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        info = backup.read_manifest(stick / backup.BACKUP_DIR_NAME)
        assert info is not None
        assert info.photos == 2
        assert info.place == "Holm"

    def test_zustandsdatei_gehoert_nicht_in_die_sicherung(
        self, session, settings, stick, collection
    ):
        """Sie sagt etwas ueber dieses Geraet, nicht ueber die Sammlung."""
        collection(1)

        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        assert not (stick / backup.BACKUP_DIR_NAME / backup.STATE_FILE).exists()
        assert (settings.data_dir / backup.STATE_FILE).is_file()


class TestWiederherstellung:
    def _sicherung_anlegen(self, session, settings, stick, collection, anzahl=2):
        shas = collection(anzahl)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)
        return shas

    def test_unvollstaendige_sicherung_wird_abgelehnt(self, settings, stick):
        (stick / backup.BACKUP_DIR_NAME).mkdir()

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert "nicht komplett" in str(fehler.value)

    def test_bestand_wird_ersetzt(self, session, settings, stick, collection):
        shas = self._sicherung_anlegen(session, settings, stick, collection)
        # Inzwischen ist auf dem Geraet etwas anderes passiert.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()

    def test_bisheriger_stand_wird_beiseitegelegt_nicht_geloescht(
        self, session, settings, stick, collection
    ):
        """Wer die falsche Sicherung einspielt, soll nicht alles verloren haben."""
        self._sicherung_anlegen(session, settings, stick, collection)
        spaeter = "e" * 64
        pfad = original_path(settings.photos_dir, spaeter, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"nach der sicherung entstanden")

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert not pfad.exists(), "in der Sicherung war es nicht"
        beiseite = list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*"))
        assert len(beiseite) == 1
        assert (beiseite[0] / "photos" / spaeter[0:2] / spaeter[2:4] / f"{spaeter}.jpg").is_file()

    def test_write_ahead_log_wandert_mit_beiseite(self, session, settings, stick, collection):
        """Ein liegengebliebenes -wal gehoert zu einer anderen Datenbank.

        Bliebe es neben der zurueckgespielten Datei liegen, versuchte SQLite es anzuwenden.
        """
        self._sicherung_anlegen(session, settings, stick, collection, anzahl=1)
        (settings.data_dir / "kiekmap.db-wal").write_bytes(b"altes journal")

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert not (settings.data_dir / "kiekmap.db-wal").exists()
        beiseite = next(iter(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*")))
        assert (beiseite / "kiekmap.db-wal").is_file()

    def test_arbeitsordner_bleibt_nicht_liegen(self, session, settings, stick, collection):
        self._sicherung_anlegen(session, settings, stick, collection, anzahl=1)

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert not (settings.data_dir / backup.RESTORE_WORK_DIR).exists()


class TestSchemastandBeimZurueckspielen:
    """Der Fehler, der am 12. August 2026 zwei Tage lang unbemerkt lief.

    Eine Sicherung bringt ihr Schema mit. Zurueckgespielt wird die Datei im Ganzen, und das
    laufende Programm haengt sich nur neu an sie -- Migrationen laufen dabei nicht, denn die
    laufen beim *Start*. Fehlt dem Schema danach eine Spalte, die das heutige Programm schreiben
    will, sieht die Ausstellung voellig normal aus, und **jeder Besucherbeitrag endet mit 500**.
    """

    def _sicherung_mit_schemastand(
        self, session, settings, stick, collection, revision: str, spalte_entfernen: bool = False
    ):
        """Eine Sicherung, deren Datenbank auf einem bestimmten Stand steht.

        ``spalte_entfernen`` macht daraus eine Sicherung von **vor** der Migration, und ohne das
        waere die Nachbildung ein Widerspruch: Die Testdatenbank entsteht aus den Modellen und
        traegt ``old_source`` laengst. Nur den Stempel zurueckzudrehen ergaebe einen Stand, den es
        nie gab -- und die Migration scheiterte an einer Spalte, die schon da ist.
        """
        collection(1)
        backup.run_backup(session, settings, _drive(settings), _nichts_melden)

        gesichert = stick / backup.BACKUP_DIR_NAME / "kiekmap.db"
        verbindung = sqlite3.connect(gesichert)
        if spalte_entfernen:
            verbindung.execute("alter table changes drop column old_source")
        verbindung.execute("create table if not exists alembic_version (version_num varchar(32))")
        verbindung.execute("delete from alembic_version")
        verbindung.execute("insert into alembic_version values (?)", (revision,))
        verbindung.commit()
        verbindung.close()

    def test_alte_sicherung_wird_angehoben(self, session, settings, stick, collection):
        """Der eigentliche Fall: eingespielt wird ein Stand von vor der Migration."""
        self._sicherung_mit_schemastand(
            session, settings, stick, collection, ANFANGSSCHEMA, spalte_entfernen=True
        )

        backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert schema.revision_of(settings.db_path) == schema.head_revision()
        # Und zwar wirklich: die Spalte, an der es damals scheiterte, ist da.
        verbindung = sqlite3.connect(settings.db_path)
        spalten = {zeile[1] for zeile in verbindung.execute("pragma table_info(changes)")}
        verbindung.close()
        assert "old_source" in spalten

    def test_neuere_sicherung_wird_abgelehnt(self, session, settings, stick, collection):
        """Der umgekehrte Fall, und er ist der unangenehmere.

        Ein Schemastand, den dieses Programm nicht kennt, laesst sich nicht anheben -- die
        zugehoerigen Migrationen gibt es hier gar nicht. Also gar nicht erst anfassen.
        """
        self._sicherung_mit_schemastand(session, settings, stick, collection, "aus der zukunft")

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert "neueren Programmversion" in str(fehler.value)

    def test_bei_ablehnung_bleibt_das_geraet_unberuehrt(self, session, settings, stick, collection):
        """Die Zusage, an der die Reihenfolge im Code haengt.

        Abgelehnt wird, **bevor** irgendetwas getauscht ist -- sonst stuende das Museum mit einer
        halb ersetzten Sammlung da, und zwar wegen einer Sicherung, die gar nicht lesbar war.
        """
        self._sicherung_mit_schemastand(session, settings, stick, collection, "aus der zukunft")
        spaeter = "f" * 64
        pfad = original_path(settings.photos_dir, spaeter, ".jpg")
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(b"nach der sicherung entstanden")

        with pytest.raises(backup.BackupError):
            backup.run_restore(settings, _drive(settings), _nichts_melden)

        assert pfad.is_file(), "der Bestand haette nicht angefasst werden duerfen"
        assert list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*")) == []
        assert not (settings.data_dir / backup.RESTORE_WORK_DIR).exists()


class TestErinnerung:
    def test_ohne_sicherung_ist_es_ueberfaellig(self, settings):
        """Nie gesichert ist genau der Fall, der die Erinnerung braucht."""
        zustand = backup.read_state(settings)

        assert zustand.last_backup_at is None
        assert zustand.overdue is True

    def test_frische_sicherung_ist_nicht_ueberfaellig(self, settings):
        backup.record_backup(settings, "SANDISK")

        zustand = backup.read_state(settings)

        assert zustand.days_since == 0
        assert zustand.overdue is False
        assert zustand.last_drive == "SANDISK"

    def test_alte_sicherung_ist_ueberfaellig(self, settings):
        # UTC, weil `_stamp()` das schreibt und `read_state` es so liest. Mit Ortszeit war dieser
        # Test zwei Stunden am Tag rot: Ab 22 Uhr MESZ rutscht der umgerechnete Stempel auf den
        # naechsten Kalendertag, und die Differenz fiel um einen Tag kleiner aus.
        alt = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=backup.OVERDUE_DAYS + 4)
        (settings.data_dir / backup.STATE_FILE).write_text(
            f'{{"last_backup_at": "{alt.isoformat()}", "last_drive": "X"}}', encoding="utf-8"
        )

        zustand = backup.read_state(settings)

        assert zustand.days_since == backup.OVERDUE_DAYS + 4
        assert zustand.overdue is True

    def test_kaputte_zustandsdatei_gilt_als_nie_gesichert(self, settings):
        (settings.data_dir / backup.STATE_FILE).write_text("kein json", encoding="utf-8")

        assert backup.read_state(settings).last_backup_at is None


class TestAuftrag:
    def test_zweiter_auftrag_wird_abgewiesen(self):
        auftrag = backup.Job()
        laeuft = __import__("threading").Event()

        auftrag.start("backup", lambda report: (laeuft.wait(2), "fertig")[1])
        try:
            assert auftrag.start("restore", lambda report: "geht nicht") is False
        finally:
            laeuft.set()

    def test_fehler_landet_im_status(self):
        auftrag = backup.Job()

        def scheitert(report):
            raise backup.BackupError("Der Stick ist weg.")

        auftrag.start("backup", scheitert)
        _warten(auftrag)

        assert auftrag.status().phase == "error"
        assert auftrag.status().error == "Der Stick ist weg."

    def test_unerwarteter_fehler_bleibt_nicht_stumm(self):
        """Sonst stuende der Balken still und niemand wuesste, warum."""
        auftrag = backup.Job()

        def platzt(report):
            raise RuntimeError("kaputt")

        auftrag.start("backup", platzt)
        _warten(auftrag)

        assert auftrag.status().phase == "error"
        assert "schiefgegangen" in auftrag.status().error

    def test_bestaetigen_setzt_zurueck(self):
        auftrag = backup.Job()
        auftrag.start("backup", lambda report: "fertig")
        _warten(auftrag)

        auftrag.reset()

        assert auftrag.status().phase == "idle"


def _warten(auftrag: backup.Job, sekunden: float = 3.0) -> None:
    """Der Auftrag laeuft in einem Faden -- kurz warten, bis er durch ist."""
    import time

    ende = time.monotonic() + sekunden
    while auftrag.running and time.monotonic() < ende:
        time.sleep(0.01)


class TestUeberDieApi:
    """Der Weg, den die Oberflaeche geht: Laufwerke abfragen, starten, Status nachfragen."""

    def _bis_fertig(self, client, sekunden: float = 5.0) -> dict:
        import time

        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            zustand = client.get("/api/admin/backup/status").json()
            if zustand["phase"] != "running":
                return zustand
            time.sleep(0.02)
        raise AssertionError("Der Auftrag wurde nicht fertig")

    def test_ohne_anmeldung_keine_laufwerke(self, client):
        assert client.get("/api/admin/backup/drives").status_code == 401

    def test_ohne_stick_steht_die_liste_leer(self, admin_client, settings, tmp_path: Path):
        settings.media_dir = tmp_path / "media"

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["drives"] == []
        # Trotzdem beantwortbar: wie viel gesichert werden muesste und wann zuletzt.
        assert daten["reminder"]["overdue"] is True

    def test_liste_nennt_platz_und_bedarf(self, admin_client, settings, stick, collection):
        collection(2)

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["photos"] == 2
        assert daten["needed_bytes"] > 0
        assert daten["drives"][0]["name"] == "SANDISK"
        assert daten["drives"][0]["enough_space"] is True

    def test_sicherung_laeuft_durch(self, admin_client, settings, stick, collection):
        collection(2)

        gestartet = admin_client.post("/api/admin/backup/start", json={"path": str(stick)}).json()
        assert gestartet["kind"] == "backup"

        zustand = self._bis_fertig(admin_client)
        assert zustand["phase"] == "done"
        assert "2 Fotos" in zustand["message"]
        assert (stick / backup.BACKUP_DIR_NAME / "kiekmap.db").is_file()

    def test_erinnerung_steht_danach_in_der_uebersicht(
        self, admin_client, settings, stick, collection
    ):
        collection(1)
        admin_client.post("/api/admin/backup/start", json={"path": str(stick)})
        self._bis_fertig(admin_client)

        uebersicht = admin_client.get("/api/admin/overview").json()

        assert uebersicht["backup"]["overdue"] is False
        assert uebersicht["backup"]["last_drive"] == "SANDISK"

    def test_unbekannter_stick_wird_abgewiesen(self, admin_client, settings, stick):
        antwort = admin_client.post("/api/admin/backup/start", json={"path": "/"})

        assert antwort.status_code == 404
        assert "nicht mehr da" in antwort.json()["detail"]

    def test_bestaetigen_raeumt_den_status_ab(self, admin_client, settings, stick, collection):
        collection(1)
        admin_client.post("/api/admin/backup/start", json={"path": str(stick)})
        self._bis_fertig(admin_client)

        zustand = admin_client.post("/api/admin/backup/acknowledge").json()

        assert zustand["phase"] == "idle"

    def test_wiederherstellen_ohne_sicherung_meldet_es(self, admin_client, settings, stick):
        (stick / backup.BACKUP_DIR_NAME).mkdir()

        admin_client.post("/api/admin/backup/restore", json={"path": str(stick)})
        zustand = self._bis_fertig(admin_client)

        assert zustand["phase"] == "error"
        assert "nicht komplett" in zustand["error"]


class TestArchiv:
    """Die Sicherung als eine Datei -- der zweite Weg aus der Sammlung heraus.

    Die eine Zusage, die alles andere traegt: **Das Archiv ist der Ordner, den auch der Stick
    bekommt, nur gezippt.** Daran haengt, dass eine ZIP-Sicherung ohne Upload-Weg trotzdem
    zurueckspielbar ist -- auf einen Stick entpacken, fertig. Bricht diese Eigenschaft, ist der
    Rueckweg weg, ohne dass es jemandem auffiele.
    """

    def _archiv(self, session, settings) -> bytes:
        return b"".join(backup.stream_archive(session, settings))

    def test_entpacktes_archiv_laesst_sich_wiederherstellen(
        self, session, settings, stick, collection
    ):
        """Der wichtigste Test des Archivs: Er bindet die beiden Wege aneinander."""
        shas = collection(3)
        daten = self._archiv(session, settings)

        # Auf den Stick entpacken -- genau das, was jemand von Hand taete.
        with zipfile.ZipFile(io.BytesIO(daten)) as archiv:
            archiv.extractall(stick)

        # Und danach der ganz gewoehnliche Weg zurueck.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()
        backup.run_restore(settings, _drive(settings), _nichts_melden)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file(), (
                "das entpackte Archiv war fuer die Wiederherstellung nicht brauchbar"
            )

    def test_archiv_enthaelt_denselben_ordner_wie_der_stick(self, session, settings, collection):
        collection(2)

        with zipfile.ZipFile(io.BytesIO(self._archiv(session, settings))) as archiv:
            namen = archiv.namelist()

        assert {name.split("/")[0] for name in namen} == {backup.BACKUP_DIR_NAME}
        assert f"{backup.BACKUP_DIR_NAME}/kiekmap.db" in namen
        assert f"{backup.BACKUP_DIR_NAME}/{backup.MANIFEST_NAME}" in namen
        assert any(name.startswith(f"{backup.BACKUP_DIR_NAME}/photos/") for name in namen)
        assert any(name.startswith(f"{backup.BACKUP_DIR_NAME}/thumbs/") for name in namen)

    def test_archiv_wird_nicht_komprimiert(self, session, settings, collection):
        """JPEG und WebP sind schon komprimiert -- ein zweiter Durchgang kostet den Pi nur Zeit."""
        collection(2)

        with zipfile.ZipFile(io.BytesIO(self._archiv(session, settings))) as archiv:
            verfahren = {eintrag.compress_type for eintrag in archiv.infolist()}

        assert verfahren == {zipfile.ZIP_STORED}

    def test_archiv_entsteht_im_strom(self, session, settings, collection):
        """Sonst laege es vollstaendig im Speicher -- auf einem Pi mit 2 GB keine gute Idee."""
        collection(5)

        stuecke = list(backup.stream_archive(session, settings))

        assert len(stuecke) > 1, "der Erzeuger hat alles auf einmal geliefert"

    def test_abgebrochener_download_zaehlt_nicht_als_sicherung(self, session, settings, collection):
        """Was der Browser nicht bekommen hat, schuetzt niemanden -- also gilt es auch nicht."""
        collection(3)
        strom = backup.stream_archive(session, settings)
        next(strom)  # angefangen, aber nicht zu Ende gelesen
        strom.close()

        assert backup.read_state(settings).last_backup_at is None

    def test_vollstaendiger_download_setzt_die_erinnerung_zurueck(
        self, session, settings, collection
    ):
        collection(2)

        self._archiv(session, settings)

        zustand = backup.read_state(settings)
        assert zustand.last_backup_at is not None
        assert zustand.last_drive == backup.ZIP_DRIVE_NAME

    def test_dateiname_nennt_ort_und_tag(self, settings):
        settings.region_file.parent.mkdir(parents=True, exist_ok=True)
        settings.region_file.write_text('{"name": "Holm"}', encoding="utf-8")

        name = backup.archive_name(settings)

        assert name.startswith("kiekmap-sicherung-holm-")
        assert name.endswith(".zip")
        assert name.isascii(), "der Name steht in einem HTTP-Kopf"


class TestArchivUeberDieApi:
    def test_ohne_ticket_kein_download(self, admin_client):
        assert admin_client.get("/api/admin/backup/zip").status_code == 422

    def test_erfundenes_ticket_wird_abgewiesen(self, admin_client):
        antwort = admin_client.get("/api/admin/backup/zip", params={"ticket": "ausgedacht"})

        assert antwort.status_code == 401

    def test_ticket_gilt_nur_einmal(self, admin_client, settings, collection):
        collection(1)
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]

        erste = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})
        zweite = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})

        assert erste.status_code == 200
        assert zweite.status_code == 401, "ein Ticket darf sich nicht wiederverwenden lassen"

    def test_ticket_nur_fuer_angemeldete(self, client):
        assert client.post("/api/admin/backup/zip/ticket").status_code == 401

    def test_download_liefert_ein_archiv(self, admin_client, settings, collection):
        collection(2)
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]

        antwort = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})

        assert antwort.headers["content-type"] == "application/zip"
        assert "attachment" in antwort.headers["content-disposition"]
        with zipfile.ZipFile(io.BytesIO(antwort.content)) as archiv:
            assert archiv.testzip() is None

    def test_laufender_auftrag_blockiert_den_download(self, admin_client, settings):
        """Eine Wiederherstellung wuerde die Dateien unter dem laufenden Strom austauschen."""
        import threading

        haltepunkt = threading.Event()
        backup.job.start("backup", lambda report: (haltepunkt.wait(2), "fertig")[1])
        ticket = admin_client.post("/api/admin/backup/zip/ticket").json()["ticket"]
        try:
            antwort = admin_client.get("/api/admin/backup/zip", params={"ticket": ticket})
        finally:
            haltepunkt.set()

        assert antwort.status_code == 409


class TestSicherungAusDemEingang:
    """Der Rueckweg: eine heruntergeladene Datei in den Eingangsordner legen.

    **Sie spielt sich nie von selbst ein.** Der Ordner nimmt sonst Fotos auf -- hinzufuegend und
    folgenlos --, waehrend dies den ganzen Bestand ersetzt. Erkannt wird sie hier, bestaetigt wird
    sie im Verwaltungsbereich.
    """

    def _ablegen(self, session, settings, name: str = "kiekmap-sicherung-holm-2026-08-03.zip"):
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        ziel = settings.incoming_dir / name
        with ziel.open("wb") as datei:
            for teil in backup.stream_archive(session, settings):
                datei.write(teil)
        return ziel

    def test_heruntergeladenes_archiv_kommt_ueber_den_eingang_zurueck(
        self, session, settings, collection
    ):
        """Der wichtigste Test: Er schliesst den Kreis, den bisher nur der Umweg ueber den Stick
        schloss."""
        shas = collection(3)
        self._ablegen(session, settings)

        # Inzwischen ist auf dem Geraet etwas anderes passiert.
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        gefunden = backup.waiting_archive(settings)
        assert gefunden is not None, "die abgelegte Sicherung wurde nicht erkannt"
        backup.run_restore_from_archive(settings, gefunden[0], _nichts_melden)

        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()
            for size in THUMBNAIL_SIZES:
                assert thumbnail_path(settings.thumbs_dir, sha, size).is_file()

    def test_wartende_sicherung_wird_mit_datum_und_anzahl_gemeldet(
        self, session, settings, collection
    ):
        """Ohne beides waere die Rueckfrage im Verwaltungsbereich nicht zu beantworten."""
        collection(2)
        self._ablegen(session, settings)

        gefunden = backup.waiting_archive(settings)

        assert gefunden is not None
        _, info = gefunden
        assert info.photos == 2
        assert info.created_at is not None

    def test_halb_kopierte_datei_wird_nicht_angeboten(self, session, settings, collection):
        """Ein abgeschnittenes ZIP hat kein Zentralverzeichnis -- es faellt von selbst durch."""
        collection(2)
        pfad = self._ablegen(session, settings)
        daten = pfad.read_bytes()
        pfad.write_bytes(daten[: len(daten) // 2])

        assert backup.waiting_archive(settings) is None

    def test_fremde_zip_wird_ignoriert(self, settings):
        """Passender Name, kein Manifest -- der Name entscheidet nur, ob hineingesehen wird."""
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        fremd = settings.incoming_dir / "kiekmap-sicherung-fremd.zip"
        with zipfile.ZipFile(fremd, "w") as archiv:
            archiv.writestr("irgendwas.txt", "kein Bestand")

        assert backup.waiting_archive(settings) is None

    def test_zip_im_eingang_landet_nicht_im_problemordner(self, session, settings, collection):
        """Ohne diese Zusage tut nichts von alledem etwas: Der Watcher wuerde sie wegraeumen."""
        from app.services.watcher import IncomingWatcher

        collection(1)
        pfad = self._ablegen(session, settings)
        watcher = IncomingWatcher(settings)

        watcher.scan_once()
        watcher.scan_once()

        assert pfad.is_file(), "der Watcher hat die Sicherung angefasst"
        assert not (settings.incoming_dir / "_problem").exists()

    def test_ein_foto_daneben_wird_weiterhin_aufgenommen(
        self, session, settings, collection, sample_image
    ):
        """Die Ausnahme gilt nur fuer Sicherungen, nicht fuer den ganzen Ordner."""
        import shutil as _shutil

        from app.services.watcher import IncomingWatcher

        collection(1)
        self._ablegen(session, settings)
        _shutil.copy2(sample_image("scan_ohne_exif.jpg"), settings.incoming_dir / "neu.jpg")

        watcher = IncomingWatcher(settings)
        watcher.scan_once()
        aufgenommen = watcher.scan_once()

        assert aufgenommen == 1

    def test_bisheriger_stand_wird_beiseitegelegt(self, session, settings, collection):
        collection(2)
        pfad = self._ablegen(session, settings)
        vorher = {p.name for p in settings.photos_dir.rglob("*") if p.is_file()}

        backup.run_restore_from_archive(settings, pfad, _nichts_melden)

        beiseite = list(settings.data_dir.glob(f"{backup.SET_ASIDE_PREFIX}*"))
        assert len(beiseite) == 1, "der bisherige Stand wurde nicht beiseitegelegt"
        assert vorher <= {p.name for p in beiseite[0].rglob("*") if p.is_file()}

    def test_archiv_wandert_nach_erledigt(self, session, settings, collection):
        collection(1)
        pfad = self._ablegen(session, settings)

        backup.run_restore_from_archive(settings, pfad, _nichts_melden)

        assert not pfad.exists(), "die Datei liegt noch im Eingang"
        assert (settings.incoming_dir / "_erledigt" / pfad.name).is_file()
        assert backup.waiting_archive(settings) is None

    def test_unvollstaendige_datei_wird_abgelehnt(self, settings):
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        keine = settings.incoming_dir / "kiekmap-sicherung-kaputt.zip"
        keine.write_bytes(b"kein zip")

        with pytest.raises(backup.BackupError) as fehler:
            backup.run_restore_from_archive(settings, keine, _nichts_melden)

        assert "keine vollstaendige Sicherung" in str(fehler.value)


class TestEingangUeberDieApi:
    def _bis_fertig(self, client, sekunden: float = 5.0) -> dict:
        import time

        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            zustand = client.get("/api/admin/backup/status").json()
            if zustand["phase"] != "running":
                return zustand
            time.sleep(0.02)
        raise AssertionError("Der Auftrag wurde nicht fertig")

    def _ablegen(self, session, settings) -> str:
        settings.incoming_dir.mkdir(parents=True, exist_ok=True)
        name = "kiekmap-sicherung-holm-2026-08-03.zip"
        with (settings.incoming_dir / name).open("wb") as datei:
            for teil in backup.stream_archive(session, settings):
                datei.write(teil)
        return name

    def test_laufwerksliste_meldet_die_wartende_sicherung(
        self, admin_client, session, settings, collection
    ):
        collection(2)
        name = self._ablegen(session, settings)

        daten = admin_client.get("/api/admin/backup/drives").json()

        assert daten["incoming"] is not None
        assert daten["incoming"]["file"] == name
        assert daten["incoming"]["photos"] == 2

    def test_ohne_datei_meldet_die_liste_nichts(self, admin_client, settings):
        assert admin_client.get("/api/admin/backup/drives").json()["incoming"] is None

    def test_einspielen_ueber_die_api(self, admin_client, session, settings, collection):
        shas = collection(2)
        name = self._ablegen(session, settings)
        for sha in shas:
            original_path(settings.photos_dir, sha, ".jpg").unlink()

        antwort = admin_client.post("/api/admin/backup/incoming/restore", json={"file": name})
        assert antwort.status_code == 200
        zustand = self._bis_fertig(admin_client)

        assert zustand["phase"] == "done", zustand
        assert "_erledigt" in zustand["message"]
        for sha in shas:
            assert original_path(settings.photos_dir, sha, ".jpg").is_file()

    def test_erfundener_dateiname_wird_abgewiesen(self, admin_client, settings):
        antwort = admin_client.post(
            "/api/admin/backup/incoming/restore", json={"file": "gibt-es-nicht.zip"}
        )

        assert antwort.status_code == 404

    def test_pfad_aus_dem_ordner_heraus_wird_abgewiesen(self, admin_client, settings):
        """Der Name kommt aus dem Browser -- ohne die Pruefung waere jede Datei einspielbar."""
        antwort = admin_client.post(
            "/api/admin/backup/incoming/restore", json={"file": "../kiekmap.db"}
        )

        assert antwort.status_code == 404
