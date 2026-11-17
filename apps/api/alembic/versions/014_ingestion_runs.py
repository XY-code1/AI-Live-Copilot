"""ingestion runs and source evidence

Revision ID: 014
Revises: 013
Create Date: 2026-11-17
"""

import sqlalchemy as sa
from alembic import op

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("product_sources.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="running"),
        sa.Column("parser", sa.String(120), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("snapshot_path", sa.Text(), nullable=True),
        sa.Column("final_url", sa.Text(), nullable=True),
        sa.Column("redirect_chain", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_runs_source_id", "ingestion_runs", ["source_id"])
    op.create_index("ix_runs_product_id", "ingestion_runs", ["product_id"])

    op.add_column(
        "product_sources",
        sa.Column("run_id", sa.Uuid(), nullable=True),
    )
    op.add_column("product_sources", sa.Column("content_hash", sa.String(64), nullable=True))
    op.add_column("product_sources", sa.Column("parser", sa.String(120), nullable=True))
    with op.batch_alter_table("product_sources") as batch:
        batch.create_foreign_key(
            "fk_sources_run", "ingestion_runs", ["run_id"], ["id"], ondelete="SET NULL"
        )


def downgrade() -> None:
    with op.batch_alter_table("product_sources") as batch:
        batch.drop_constraint("fk_sources_run", type_="foreignkey")
    op.drop_column("product_sources", "parser")
    op.drop_column("product_sources", "content_hash")
    op.drop_column("product_sources", "run_id")
    op.drop_index("ix_runs_product_id", table_name="ingestion_runs")
    op.drop_index("ix_runs_source_id", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
