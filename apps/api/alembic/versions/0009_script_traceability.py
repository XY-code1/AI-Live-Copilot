"""script traceability: unique versions and section source reference

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("scripts") as batch:
        batch.create_unique_constraint(
            "uq_scripts_series_version", ["series_id", "version"]
        )
    op.add_column(
        "script_sections",
        sa.Column("source_reference", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("script_sections", "source_reference")
    op.drop_constraint("uq_scripts_series_version", "scripts", type_="unique")
