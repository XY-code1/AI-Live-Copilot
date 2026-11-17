"""source sufficiency

Revision ID: 016
Revises: 015
Create Date: 2026-11-17
"""

import sqlalchemy as sa

from alembic import op

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "product_sources",
        sa.Column("sufficiency", sa.String(16), nullable=False, server_default="sufficient"),
    )


def downgrade() -> None:
    op.drop_column("product_sources", "sufficiency")
