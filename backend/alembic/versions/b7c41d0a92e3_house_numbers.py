"""House numbers in the gazetteer

Two columns on ``places``, both only filled for ``kind="adresse"``. The table itself is refilled
from ``places.json`` on every ``python -m app.cli places``, so no data has to be migrated -- but
the photographs beside it must survive, which is why this is a migration and not a rebuild.

Revision ID: b7c41d0a92e3
Revises: 85f5993e7f4f
Create Date: 2026-07-29 12:04:11.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7c41d0a92e3"
down_revision: str | None = "85f5993e7f4f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("places", sa.Column("street", sa.String(length=200), nullable=True))
    op.add_column("places", sa.Column("housenumber", sa.String(length=20), nullable=True))
    op.create_index("ix_places_street", "places", ["street"])


def downgrade() -> None:
    op.drop_index("ix_places_street", table_name="places")
    op.drop_column("places", "housenumber")
    op.drop_column("places", "street")
