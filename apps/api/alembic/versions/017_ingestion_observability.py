"""ingestion run observability

Revision ID: 017
Revises: 016
Create Date: 2026-11-18
"""

import sqlalchemy as sa

from alembic import op

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingestion_runs", sa.Column("requested_url", sa.Text(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("fetch_duration_ms", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("raw_size_bytes", sa.Integer(), nullable=True))
    op.add_column("ingestion_runs", sa.Column("cleaned_text_length", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("ingestion_runs", "cleaned_text_length")
    op.drop_column("ingestion_runs", "raw_size_bytes")
    op.drop_column("ingestion_runs", "fetch_duration_ms")
    op.drop_column("ingestion_runs", "requested_url")
