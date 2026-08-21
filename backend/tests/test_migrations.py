# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

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
gegangen. Die Probe unter ``tests/fixtures/sample_migration/`` haengt an keiner Revisionsnummer:
sie baut ``photos`` neu, sonst nichts, und ihre ``env.py`` fuehrt die **echte** aus.
"""

import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command

BACKEND = Path(__file__).resolve().parent.parent
PROBE = Path(__file__).resolve().parent / "fixtures" / "sample_migration"


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


def test_migrationen_und_modelle_beschreiben_dasselbe_schema(settings, tmp_path: Path):
    """Der Test, der am 12. August 2026 gefehlt hat.

    Die uebrigen Tests bauen ihr Schema aus den Modellen (``create_all``), nicht aus den
    Migrationen. Sie koennen eine fehlende Migration deshalb **grundsaetzlich** nicht bemerken:
    393 gruene Tests standen neben einer Datenbank, an der nichts mehr zu schreiben war.

    Also einmal beide Wege gehen und vergleichen. Das faengt beide Richtungen -- eine
    Modelaenderung ohne Migration ebenso wie eine Migration, die an den Modellen vorbeigeht.

    **Verglichen werden Tabellen und Spaltennamen, nicht Typen und Indizes.** Die beiden Wege
    unterscheiden sich dort in Kleinigkeiten, die nichts bedeuten -- SQLite kennt ohnehin nur
    wenige Typen, und ein Test, der an solchen Unterschieden haengenbleibt, wird abgeschaltet
    statt gelesen. Ein fehlender Spaltenname ist dagegen genau der Fehler, um den es geht.
    """
    from app.db import Base
    from app.models import Photo  # noqa: F401 -- meldet jede Tabelle an Base an

    # Weg eins: die Migrationen, gegen die Datenbank der settings-Fixture.
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    command.upgrade(config, "head")
    aus_migrationen = _schema_von(Path(settings.db_url.removeprefix("sqlite:///")))

    # Weg zwei: die Modelle, gegen eine leere Datei daneben.
    from sqlalchemy import create_engine

    zweite = tmp_path / "aus-modellen.db"
    engine = create_engine(f"sqlite:///{zweite}")
    Base.metadata.create_all(engine)
    engine.dispose()
    aus_modellen = _schema_von(zweite)

    assert aus_migrationen == aus_modellen


def _schema_von(datenbank: Path) -> dict[str, set[str]]:
    """Tabellen und ihre Spaltennamen -- ohne die Buchhaltung von Alembic und SQLite."""
    verbindung = sqlite3.connect(datenbank)
    tabellen = {
        name
        for (name,) in verbindung.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if name not in {"alembic_version"} and not name.startswith("sqlite_")
    }
    schema = {
        name: {zeile[1] for zeile in verbindung.execute(f"PRAGMA table_info({name})")}
        for name in tabellen
    }
    verbindung.close()
    return schema
