# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Where the database schema stands, and how it is brought up to date.

Alembic normally runs from the command line, once, at startup
(``backend/docker-entrypoint.sh``). This module is what lets the application ask the same
questions while it is running -- and it exists because of a failure that went unnoticed for two
days.

**A backup brings its own schema.** Restoring swaps the database file as a whole
(``backup.restore._swap_in``); the running service is then merely re-attached to it
(``api/backup._reopen_database``). No migration happens in between, because migrations happen at
*start*, and a restore is not a start. On 12 August 2026 that meant a device that looked entirely
normal -- photos, map, timeline -- while **every write ended in a 500**:

    sqlite3.OperationalError: table changes has no column named old_source

The remedy was a restart, and it stood in the manuals as a caveat the museum team had to know.
Since 15 August 2026 the restore does it itself, and the caveat is gone.

**Both directions matter, and they need opposite answers.** A backup older than the program is
brought up (``upgrade``). A backup *newer* than the program cannot be: this program does not know
those migrations, and running them is not a thing that can be improvised. It has to be refused --
before anything is swapped, while the collection on the device is still untouched. That is what
``is_ahead`` is for.
"""

import logging
import sqlite3
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command

log = logging.getLogger(__name__)

#: backend/app/services/schema.py -> backend
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _config() -> Config:
    """An Alembic configuration that does not care where it was called from.

    ``alembic.ini`` names its script folder relatively, which is fine on the command line
    (``cd backend && alembic ...``) and wrong everywhere else -- the service runs with whatever
    working directory uvicorn was started in.
    """
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    return config


def known_revisions() -> set[str]:
    """Every revision this program carries, not just the newest one.

    The whole set, because the question is not "is it the same as ours" but "do we know it at
    all": a backup from an older device names a revision that is somewhere in our history, and
    that one can be upgraded from.
    """
    return {script.revision for script in ScriptDirectory.from_config(_config()).walk_revisions()}


def head_revision() -> str:
    """The newest revision this program carries -- what ``upgrade head`` aims at."""
    return ScriptDirectory.from_config(_config()).get_current_head() or ""


def revision_of(database: Path) -> str | None:
    """The schema stamp inside a database file, or None when there is none.

    None is an ordinary answer with two meanings -- the file has no ``alembic_version`` table at
    all, or the table is empty. Both mean the same thing here: nothing that could be ahead of us.
    """
    if not database.is_file():
        return None
    connection = sqlite3.connect(str(database))
    try:
        row = connection.execute("select version_num from alembic_version").fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        connection.close()
    return row[0] if row else None


def is_ahead(database: Path) -> str | None:
    """The revision of a database that this program does not know -- else None.

    Deliberately phrased as "does not know" rather than "is newer". A revision we cannot place is
    a revision we must not touch, whether it comes from a newer program, a different branch of the
    project, or a file that is not ours at all.
    """
    revision = revision_of(database)
    if revision is None or revision in known_revisions():
        return None
    return revision


def bring_up_to_date(database: Path) -> str | None:
    """Migrate the database at the configured path, and say where it started.

    ``database`` is only read, to decide *whether* to migrate; the migration itself goes through
    ``app.config`` by way of ``alembic/env.py`` -- the same file the application uses, which is
    the point of that indirection. Returns the revision it came from, or None when nothing was
    done.

    **An unstamped database is left alone**, and that is a decision rather than an oversight.
    Without ``alembic_version`` there is no telling what the file is, and Alembic would start from
    the very first migration against tables that already exist -- turning a restore that would
    have worked into an error. In the museum this cannot arise: every database there was created
    by migrations, so every backup carries a stamp. It arises in the test suite, where the schema
    comes straight from the models, and that is exactly a case where migrating would be wrong.
    """
    revision = revision_of(database)
    if revision is None:
        log.warning("Restored database carries no schema stamp -- not migrating")
        return None

    command.upgrade(_config(), "head")
    log.info("Schema brought up from %s to head", revision)
    return revision
