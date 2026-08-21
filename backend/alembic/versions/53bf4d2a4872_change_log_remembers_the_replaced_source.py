# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""change log remembers the replaced source

Needed since visitors may sharpen a street-precise location to a house number -- the one route
that *replaces* rather than fills. Without this column reverting such a contribution would hand a
curator's statement back as a visitor's. Existing rows stay NULL and behave exactly as before.

Revision ID: 53bf4d2a4872
Revises: 1cf9ccd28cd7
Create Date: 2026-08-10 16:17:01.518899
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "53bf4d2a4872"
down_revision: str | None = "1cf9ccd28cd7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("changes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("old_source", sa.String(length=10), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("changes", schema=None) as batch_op:
        batch_op.drop_column("old_source")
