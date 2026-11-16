"""add extracted source content

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product_sources", sa.Column("content_text", sa.Text(), nullable=True))
    op.add_column("product_sources", sa.Column("page_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("product_sources", "page_count")
    op.drop_column("product_sources", "content_text")
