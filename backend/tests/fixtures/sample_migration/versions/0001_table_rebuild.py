"""Rebuilds ``photos`` without changing anything else.

``recreate="always"`` forces exactly the path that once cost data: create a copy, drop the
original, rename. Without forcing it, Alembic would decide for itself whether a rebuild is needed
-- and the sample would eventually check nothing at all.

This revision is no part of the schema. It lies under ``tests/fixtures/`` and runs only in
``tests/test_migrations.py``.
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
