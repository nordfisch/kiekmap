"""Dass eine Migration nichts mitreisst, was an den Tabellen haengt.

Der Anlass ist ein echter Verlust: Die Migration, die ``hidden`` in ``deleted`` umbenennt, baut die
Tabelle ``photos`` neu -- so muss man das in SQLite tun. Beim ersten Lauf nahm sie **alle
Besucherbeitraege** mit, leerte ``photo_tags`` und loeste jede Verknuepfung des Import-Protokolls.

Der Weg dorthin ist tueckisch, weil nichts davon einen Fehler wirft:

  * ``app/db.py`` schaltet ``PRAGMA foreign_keys=ON`` fuer jede Engine des Prozesses ein -- auch
    fuer die von Alembic, weil ``env.py`` die Modelle importiert.
  * Alembics Tabellenneubau loescht das Original und legt es neu an.
  * ``changes`` haengt mit ON DELETE CASCADE daran, ``import_log`` mit ON DELETE SET NULL.

Ergebnis: eine gruen durchlaufende Migration und ein Bestand ohne Beitraege. Deshalb dieser Test.
"""

import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command

BACKEND = Path(__file__).resolve().parent.parent


def _alembic_config() -> Config:
    """``env.py`` holt die URL aus ``app.config`` -- die ``settings``-Fixture zeigt dorthin."""
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return config


def test_tabellenneubau_nimmt_keine_besucherbeitraege_mit(settings):
    db = Path(settings.db_url.removeprefix("sqlite:///"))
    config = _alembic_config()

    # Bis vor die fragliche Migration hochziehen und Daten anlegen, die daran haengen.
    command.upgrade(config, "b7c41d0a92e3")

    verbindung = sqlite3.connect(db)
    verbindung.executescript(
        """
        INSERT INTO photos (sha256, original_filename, mime, bytes, width, height,
                            date_precision, status)
        VALUES ('a', 'foto.jpg', 'image/jpeg', 1, 10, 10, 'year', 'hidden');

        INSERT INTO changes (photo_id, field, old_value, new_value, source)
        VALUES (1, 'date', NULL, '1932', 'visitor');

        INSERT INTO import_log (path, result, photo_id) VALUES ('foto.jpg', 'imported', 1);

        INSERT INTO tags (name) VALUES ('Kirchweih');
        INSERT INTO photo_tags (photo_id, tag_id) VALUES (1, 1);
        """
    )
    verbindung.commit()
    verbindung.close()

    command.upgrade(config, "head")

    verbindung = sqlite3.connect(db)
    beitraege = verbindung.execute("SELECT count(*) FROM changes").fetchone()[0]
    schlagwoerter = verbindung.execute("SELECT count(*) FROM photo_tags").fetchone()[0]
    verknuepft = verbindung.execute(
        "SELECT count(*) FROM import_log WHERE photo_id IS NOT NULL"
    ).fetchone()[0]
    status = verbindung.execute("SELECT status FROM photos").fetchone()[0]
    verbindung.close()

    assert beitraege == 1, "der Besucherbeitrag wurde beim Tabellenneubau mitgeloescht"
    assert schlagwoerter == 1, "die Schlagwort-Zuordnung wurde mitgeloescht"
    assert verknuepft == 1, "das Import-Protokoll hat seine Verknuepfung verloren"
    assert status == "deleted", "der Status wurde nicht umbenannt"
