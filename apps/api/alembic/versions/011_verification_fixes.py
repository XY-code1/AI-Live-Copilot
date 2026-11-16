"""verification status values and issue source reference

Revision ID: 011
Revises: 010
Create Date: 2026-11-16
"""

import sqlalchemy as sa
from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE script_verifications SET status = 'pass' WHERE status = 'pass_'")
    op.add_column(
        "verification_issues",
        sa.Column("source_reference", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("verification_issues", "source_reference")
    op.execute("UPDATE script_verifications SET status = 'pass_' WHERE status = 'pass'")
