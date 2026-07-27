"""Grundgeruest, noch ohne Tabellen

Revision ID: a510bd1a68f4
Revises:
Create Date: 2026-07-28 00:47:16.840291
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a510bd1a68f4"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
