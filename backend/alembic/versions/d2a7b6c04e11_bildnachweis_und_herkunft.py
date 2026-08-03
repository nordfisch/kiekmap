"""Bildnachweis und Herkunft

Two columns on ``photos``, both nullable and both empty to begin with -- there is nowhere to take
them from. A scanner does not know who lent the picture.

They are deliberately two rather than one: ``credit`` is shown to visitors, ``provenance`` never
leaves the admin area. See docs/decisions.md.

Revision ID: d2a7b6c04e11
Revises: c1f038e7ec4e
Create Date: 2026-08-03 13:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d2a7b6c04e11"
down_revision: str | None = "c1f038e7ec4e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("photos", sa.Column("credit", sa.String(length=200), nullable=True))
    op.add_column("photos", sa.Column("provenance", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("photos", "provenance")
    op.drop_column("photos", "credit")
