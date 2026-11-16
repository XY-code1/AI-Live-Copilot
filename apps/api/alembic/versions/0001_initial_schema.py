"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("plan", sa.String(40), nullable=False, server_default="trial"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(120), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False, server_default="CNY"),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "ready",
                "archived",
                name="product_status",
                native_enum=False,
                length=32,
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
    op.create_index("ix_products_workspace_id", "products", ["workspace_id"])
    op.create_index("ix_products_status", "products", ["status"])

    op.create_table(
        "product_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum(
                "pdf",
                "image",
                "url",
                "manual",
                name="product_source_type",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("reference", sa.String(255), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "ready",
                "processing",
                "failed",
                name="product_source_status",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="ready",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "product_attributes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            sa.Uuid(),
            sa.ForeignKey("product_sources.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("value", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "status",
            sa.Enum(
                "unconfirmed",
                "confirmed",
                "doubtful",
                name="confirmation_status",
                native_enum=False,
                length=16,
            ),
            nullable=False,
            server_default="unconfirmed",
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
    op.create_index("ix_attributes_product_id", "product_attributes", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_attributes_product_id", table_name="product_attributes")
    op.drop_table("product_attributes")
    op.drop_table("product_sources")
    op.drop_index("ix_products_status", table_name="products")
    op.drop_index("ix_products_workspace_id", table_name="products")
    op.drop_table("products")
    op.drop_table("workspaces")
