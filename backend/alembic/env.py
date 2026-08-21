# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Alembic environment.

The database URL comes from ``app.config``, not from alembic.ini -- so there is exactly one place
where the path to the database stands, and inside the container migrations automatically hit the
same file as the application.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, event, pool

from alembic import context
from app.config import get_settings
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
settings.ensure_dirs()
config.set_main_option("sqlalchemy.url", settings.db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite cannot alter columns directly; Alembic rebuilds the table in that case.
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    @event.listens_for(connectable, "connect")
    def _migrations_without_cascades(dbapi_connection, connection_record) -> None:
        """Foreign keys off while migrating -- and that is not a detail.

        SQLite cannot alter columns or constraints; Alembic therefore rebuilds the table: make a
        copy, **drop the original**, rename. With foreign keys switched on it is exactly that DROP
        which clears out everything hanging off it -- ``changes`` with ON DELETE CASCADE,
        ``photo_tags`` likewise, and ``import_log`` loses its link through ON DELETE SET NULL. The
        damage does not show: the migration runs green, and only weeks later are all visitor
        contributions missing in the museum.

        ``app/db.py`` switches the check on for *every* engine in the process, this one included --
        which is why it has to be explicitly switched off again here. In production it stays on, of
        course.
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
