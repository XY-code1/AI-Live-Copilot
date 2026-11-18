"""segment locators and hashes

Revision ID: 018
Revises: 017
Create Date: 2026-11-18
"""

import sqlalchemy as sa

from alembic import op

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("source_segments", sa.Column("source_locator", sa.Text(), nullable=True))
    op.add_column("source_segments", sa.Column("heading_level", sa.Integer(), nullable=True))
    op.add_column("source_segments", sa.Column("content_hash", sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column("source_segments", "content_hash")
    op.drop_column("source_segments", "heading_level")
    op.drop_column("source_segments", "source_locator")
