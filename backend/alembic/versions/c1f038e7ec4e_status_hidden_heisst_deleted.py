"""Status hidden heisst deleted

Aus "Verstecken" wird "Loeschen" -- derselbe Status unter dem Wort, unter dem das Museumsteam ihn
sucht. Geloescht heisst weiterhin: aus der Ausstellung genommen, nicht von der Platte entfernt.

**Drei Schritte, und keiner davon ist wegzulassen.** Der Check-Constraint kennt nur die beiden
Werte seiner Zeit, also beisst sich jede der beiden naheliegenden Reihenfolgen: Zuerst die Zeilen
umzuschreiben scheitert am alten Constraint, zuerst den neuen zu setzen scheitert beim Kopieren
der noch vorhandenen 'hidden'-Zeilen. Der Ausweg ist ein Zwischenzustand, der beide Werte erlaubt.

SQLite kann einen Constraint nicht aendern; ``batch_alter_table`` baut die Tabelle dazu jedes Mal
neu und kopiert die Daten hinueber. Bei knapp dreissig Zeilen ist das ohne Belang.

Revision ID: c1f038e7ec4e
Revises: b7c41d0a92e3
Create Date: 2026-08-02 21:47:50.304461
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c1f038e7ec4e"
down_revision: str | None = "b7c41d0a92e3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ALT = "hidden"
NEU = "deleted"


def _schreibe_status(von: str, nach: str) -> None:
    op.execute(
        sa.text("UPDATE photos SET status = :nach WHERE status = :von").bindparams(
            von=von, nach=nach
        )
    )


def _setze_constraint(*erlaubt: str) -> None:
    werte = ", ".join(f"'{wert}'" for wert in ("published", *erlaubt))
    with op.batch_alter_table("photos", schema=None) as batch:
        batch.drop_constraint("ck_status", type_="check")
        batch.create_check_constraint("ck_status", f"status IN ({werte})")


def _wechsle(von: str, nach: str) -> None:
    _setze_constraint(von, nach)  # Zwischenzustand: beide Werte sind erlaubt
    _schreibe_status(von, nach)
    _setze_constraint(nach)


def upgrade() -> None:
    _wechsle(ALT, NEU)


def downgrade() -> None:
    _wechsle(NEU, ALT)
