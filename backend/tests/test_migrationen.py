"""Dass eine Migration nichts mitreisst, was an den Tabellen haengt.

Der Anlass ist ein echter Verlust: Die Migration, die ``hidden`` in ``deleted`` umbenannte, baute
die Tabelle ``photos`` neu -- so muss man das in SQLite tun. Beim ersten Lauf nahm sie **alle
Besucherbeitraege** mit, leerte ``photo_tags`` und loeste jede Verknuepfung des Import-Protokolls.

Der Weg dorthin ist tueckisch, weil nichts davon einen Fehler wirft:

  * ``app/db.py`` schaltet ``PRAGMA foreign_keys=ON`` fuer jede Engine des Prozesses ein -- auch
    fuer die von Alembic, weil ``env.py`` die Modelle importiert.
  * Alembics Tabellenneubau loescht das Original und legt es neu an.
  * ``changes`` haengt mit ON DELETE CASCADE daran, ``photo_tags`` ebenso, und ``import_log``
    verliert seine Verknuepfung durch ON DELETE SET NULL.

Ergebnis: eine gruen durchlaufende Migration und ein Bestand ohne Beitraege. Deshalb dieser Test.

**Warum eine Probe-Migration statt der echten.** Frueher zog dieser Test namentlich auf die
Revision hoch, die den Schaden anrichtete. Beim Zusammenfassen der Migrationen zu einem
Anfangsschema verschwand sie -- und mit ihr waere der einzige Schutz vor der Wiederholung
gegangen. Die Probe unter ``tests/fixtures/migrationsprobe/`` haengt an keiner Revisionsnummer:
sie baut ``photos`` neu, sonst nichts, und ihre ``env.py`` fuehrt die **echte** aus.
"""

import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command

BACKEND = Path(__file__).resolve().parent.parent
PROBE = Path(__file__).resolve().parent / "fixtures" / "migrationsprobe"


def _probe_config() -> Config:
    """``env.py`` holt die URL aus ``app.config`` -- die ``settings``-Fixture zeigt dorthin."""
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(PROBE))
    return config


def test_tabellenneubau_nimmt_keine_besucherbeitraege_mit(session, settings):
    # Das Schema kommt aus den Modellen, nicht aus der Migration: dann ist ``alembic_version``
    # leer und die Probe faengt bei ihrer eigenen Revision an, statt an der echten haengenzubleiben.
    db = Path(settings.db_url.removeprefix("sqlite:///"))
    session.close()

    verbindung = sqlite3.connect(db)
    verbindung.executescript(
        """
        INSERT INTO photos (sha256, original_filename, mime, bytes, width, height,
                            date_precision, status)
        VALUES ('a', 'foto.jpg', 'image/jpeg', 1, 10, 10, 'year', 'published');

        INSERT INTO changes (photo_id, field, old_value, new_value, source)
        VALUES (1, 'date', NULL, '1932', 'visitor');

        INSERT INTO import_log (path, result, photo_id) VALUES ('foto.jpg', 'imported', 1);

        INSERT INTO tags (name) VALUES ('Kirchweih');
        INSERT INTO photo_tags (photo_id, tag_id) VALUES (1, 1);
        """
    )
    verbindung.commit()
    verbindung.close()

    command.upgrade(_probe_config(), "head")

    verbindung = sqlite3.connect(db)
    beitraege = verbindung.execute("SELECT count(*) FROM changes").fetchone()[0]
    schlagwoerter = verbindung.execute("SELECT count(*) FROM photo_tags").fetchone()[0]
    verknuepft = verbindung.execute(
        "SELECT count(*) FROM import_log WHERE photo_id IS NOT NULL"
    ).fetchone()[0]
    fotos = verbindung.execute("SELECT count(*) FROM photos").fetchone()[0]
    verbindung.close()

    assert fotos == 1, "das Foto selbst hat den Neubau nicht ueberlebt"
    assert beitraege == 1, "der Besucherbeitrag wurde beim Tabellenneubau mitgeloescht"
    assert schlagwoerter == 1, "die Schlagwort-Zuordnung wurde mitgeloescht"
    assert verknuepft == 1, "das Import-Protokoll hat seine Verknuepfung verloren"


def test_anfangsschema_laeuft_gegen_eine_leere_datenbank(settings):
    """Dass die zusammengefasste Migration durchlaeuft -- auf dem Pi ist sie der Start."""
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))

    command.upgrade(config, "head")

    db = Path(settings.db_url.removeprefix("sqlite:///"))
    verbindung = sqlite3.connect(db)
    tabellen = {
        name for (name,) in verbindung.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    spalten = {zeile[1] for zeile in verbindung.execute("PRAGMA table_info(photos)")}
    verbindung.close()

    assert {"photos", "tags", "photo_tags", "changes", "places", "import_log"} <= tabellen
    assert {"credit", "provenance"} <= spalten
