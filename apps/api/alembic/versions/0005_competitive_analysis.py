"""competitive analysis schema

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "competitors",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("brand", sa.String(120), nullable=False, server_default=""),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_competitors_workspace_id", "competitors", ["workspace_id"])

    op.create_table(
        "comparisons",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "competitor_id",
            sa.Uuid(),
            sa.ForeignKey("competitors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "ready",
                "failed",
                name="comparison_status",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("missing_info", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_comparisons_product_id", "comparisons", ["product_id"])
    op.create_index("ix_comparisons_competitor_id", "comparisons", ["competitor_id"])

    op.create_table(
        "comparison_differences",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "comparison_id",
            sa.Uuid(),
            sa.ForeignKey("comparisons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("field", sa.String(120), nullable=False),
        sa.Column("ours", sa.Text(), nullable=False, server_default=""),
        sa.Column("theirs", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "evidence_type",
            sa.Enum(
                "source",
                "inferred",
                "speculative",
                name="evidence_type",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="source",
        ),
        sa.Column(
            "side",
            sa.Enum(
                "ours",
                "theirs",
                "neutral",
                name="advantage_side",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="neutral",
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("comparison_differences")
    op.drop_index("ix_comparisons_competitor_id", table_name="comparisons")
    op.drop_index("ix_comparisons_product_id", table_name="comparisons")
    op.drop_table("comparisons")
    op.drop_index("ix_competitors_workspace_id", table_name="competitors")
    op.drop_table("competitors")
