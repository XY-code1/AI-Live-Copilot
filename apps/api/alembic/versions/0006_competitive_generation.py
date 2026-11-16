"""competitor material and difference origin

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "competitors",
        sa.Column("material", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "comparison_differences",
        sa.Column("origin", sa.String(16), nullable=False, server_default="manual"),
    )


def downgrade() -> None:
    op.drop_column("comparison_differences", "origin")
    op.drop_column("competitors", "material")
