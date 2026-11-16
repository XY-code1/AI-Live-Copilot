"""scripts schema

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scripts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("series_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "comparison_id",
            sa.Uuid(),
            sa.ForeignKey("comparisons.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("scenario", sa.String(120), nullable=False, server_default=""),
        sa.Column("audience", sa.String(120), nullable=False, server_default=""),
        sa.Column("style", sa.String(120), nullable=False, server_default=""),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "verified",
                "issue",
                name="script_status",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="draft",
        ),
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
    op.create_index("ix_scripts_series_id", "scripts", ["series_id"])
    op.create_index("ix_scripts_product_id", "scripts", ["product_id"])

    op.create_table(
        "script_sections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "script_id",
            sa.Uuid(),
            sa.ForeignKey("scripts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kind",
            sa.Enum(
                "opening",
                "intro",
                "selling_points",
                "differentiation",
                "interaction",
                "closing",
                "risk",
                name="script_section_kind",
                native_enum=False,
                length=24,
            ),
            nullable=False,
            server_default="intro",
        ),
        sa.Column("title", sa.String(120), nullable=False, server_default=""),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("origin", sa.String(16), nullable=False, server_default="ai"),
    )


def downgrade() -> None:
    op.drop_table("script_sections")
    op.drop_index("ix_scripts_product_id", table_name="scripts")
    op.drop_index("ix_scripts_series_id", table_name="scripts")
    op.drop_table("scripts")
