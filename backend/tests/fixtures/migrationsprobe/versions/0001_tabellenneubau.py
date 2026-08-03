"""Baut ``photos`` neu, ohne sonst etwas zu aendern.

``recreate="always"`` erzwingt genau den Weg, der einmal Daten gekostet hat: Kopie anlegen,
Original loeschen, umbenennen. Ohne das Erzwingen entschiede Alembic je nach Aenderung selbst, ob
ein Neubau noetig ist -- und die Probe pruefte irgendwann nichts mehr.

Diese Revision ist kein Teil des Schemas. Sie liegt unter ``tests/fixtures/`` und laeuft nur in
``tests/test_migrationen.py``.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("photos", recreate="always"):
        pass


def downgrade() -> None:
    pass
