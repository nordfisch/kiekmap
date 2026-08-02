"""Alembic-Umgebung.

Die Datenbank-URL kommt aus ``app.config``, nicht aus alembic.ini -- so gibt es genau eine Stelle,
an der der Pfad zur Datenbank steht, und Migrationen treffen im Container automatisch dieselbe
Datei wie die Anwendung.
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
        # SQLite kann Spalten nicht direkt aendern; Alembic baut die Tabelle dann neu.
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
        """Fremdschluessel aus, solange migriert wird -- und das ist kein Detail.

        SQLite kann Spalten und Constraints nicht aendern; Alembic baut die Tabelle deshalb neu:
        Kopie anlegen, **Original loeschen**, umbenennen. Mit eingeschalteten Fremdschluesseln
        raeumt genau dieses DROP alles ab, was daran haengt -- ``changes`` mit ON DELETE CASCADE,
        ``photo_tags`` ebenso, und ``import_log`` verliert seine Verknuepfung durch
        ON DELETE SET NULL. Der Schaden faellt nicht auf: Die Migration laeuft gruen durch, und
        erst Wochen spaeter fehlen im Museum alle Besucherbeitraege.

        ``app/db.py`` schaltet die Pruefung fuer *jede* Engine des Prozesses ein, auch fuer diese
        hier -- deshalb muss sie an dieser Stelle ausdruecklich wieder aus. Im Betrieb bleibt sie
        selbstverstaendlich an.
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
