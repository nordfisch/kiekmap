"""That a migration takes nothing with it that hangs off the tables.

The occasion is a real loss: the migration that renamed ``hidden`` to ``deleted`` rebuilt the
``photos`` table -- which is how it has to be done in SQLite. On its first run it took **every
visitor contribution** with it, emptied ``photo_tags`` and released every link of the import log.

The path there is treacherous, because none of it raises an error:

  * ``app/db.py`` switches ``PRAGMA foreign_keys=ON`` on for every engine of the process -- for
    Alembic's too, because ``env.py`` imports the models.
  * Alembic's table rebuild drops the original and creates it again.
  * ``changes`` hangs off it with ON DELETE CASCADE, ``photo_tags`` likewise, and ``import_log``
    loses its link through ON DELETE SET NULL.

The result: a migration that runs green and a collection without contributions. Hence this test.

**Why a sample migration instead of the real one.** This test used to upgrade by name to the
revision that did the damage. When the migrations were squashed into an initial schema that
revision disappeared -- and the only protection against a repeat would have gone with it. The
sample under ``tests/fixtures/sample_migration/`` hangs off no revision number: it rebuilds
``photos`` and nothing else, and its ``env.py`` runs the **real** one.
"""

import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command

BACKEND = Path(__file__).resolve().parent.parent
SAMPLE = Path(__file__).resolve().parent / "fixtures" / "sample_migration"


def _sample_config() -> Config:
    """``env.py`` takes the URL from ``app.config`` -- the ``settings`` fixture points there."""
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(SAMPLE))
    return config


def test_a_table_rebuild_takes_no_visitor_contributions_with_it(session, settings):
    # The schema comes from the models, not from the migration: then ``alembic_version`` is empty
    # and the sample starts at its own revision instead of being stuck behind the real one.
    db = Path(settings.db_url.removeprefix("sqlite:///"))
    session.close()

    connection = sqlite3.connect(db)
    connection.executescript(
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
    connection.commit()
    connection.close()

    command.upgrade(_sample_config(), "head")

    connection = sqlite3.connect(db)
    contributions = connection.execute("SELECT count(*) FROM changes").fetchone()[0]
    tags = connection.execute("SELECT count(*) FROM photo_tags").fetchone()[0]
    linked = connection.execute(
        "SELECT count(*) FROM import_log WHERE photo_id IS NOT NULL"
    ).fetchone()[0]
    photos = connection.execute("SELECT count(*) FROM photos").fetchone()[0]
    connection.close()

    assert photos == 1, "the photo itself did not survive the rebuild"
    assert contributions == 1, "the visitor contribution was deleted along with the rebuild"
    assert tags == 1, "the tag assignment was deleted along with it"
    assert linked == 1, "the import log lost its link"


def test_the_initial_schema_runs_against_an_empty_database(settings):
    """That the squashed migration runs through -- on the Pi it is the starting point."""
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))

    command.upgrade(config, "head")

    db = Path(settings.db_url.removeprefix("sqlite:///"))
    connection = sqlite3.connect(db)
    tables = {
        name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    columns = {row[1] for row in connection.execute("PRAGMA table_info(photos)")}
    connection.close()

    assert {"photos", "tags", "photo_tags", "changes", "places", "import_log"} <= tables
    assert {"credit", "provenance"} <= columns


def test_migrations_and_models_describe_the_same_schema(settings, tmp_path: Path):
    """The test that was missing on 12 August 2026.

    The other tests build their schema from the models (``create_all``), not from the migrations.
    They therefore **cannot in principle** notice a missing migration: 393 green tests stood beside
    a database that could no longer be written to.

    So walk both paths once and compare. That catches both directions -- a model change without a
    migration as well as a migration that goes past the models.

    **What is compared are tables and column names, not types and indexes.** The two paths differ
    there in small ways that mean nothing -- SQLite knows only a few types anyway, and a test that
    trips over such differences gets switched off rather than read. A missing column name, by
    contrast, is exactly the error this is about.
    """
    from app.db import Base
    from app.models import Photo  # noqa: F401 -- registers every table with Base

    # Path one: the migrations, against the database of the settings fixture.
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    command.upgrade(config, "head")
    from_migrations = _schema_of(Path(settings.db_url.removeprefix("sqlite:///")))

    # Path two: the models, against an empty file beside it.
    from sqlalchemy import create_engine

    second = tmp_path / "from-models.db"
    engine = create_engine(f"sqlite:///{second}")
    Base.metadata.create_all(engine)
    engine.dispose()
    from_models = _schema_of(second)

    assert from_migrations == from_models


def _schema_of(database: Path) -> dict[str, set[str]]:
    """Tables and their column names -- without the bookkeeping of Alembic and SQLite."""
    connection = sqlite3.connect(database)
    tables = {
        name
        for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if name not in {"alembic_version"} and not name.startswith("sqlite_")
    }
    schema = {
        name: {row[1] for row in connection.execute(f"PRAGMA table_info({name})")}
        for name in tables
    }
    connection.close()
    return schema
