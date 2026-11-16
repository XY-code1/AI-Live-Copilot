"""verification schema

Revision ID: 010
Revises: 0009
Create Date: 2026-11-16
"""

import sqlalchemy as sa

from alembic import op

revision = "010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scripts",
        sa.Column(
            "verification_status", sa.String(16), nullable=False, server_default="unverified"
        ),
    )
    op.create_table(
        "script_verifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "script_id",
            sa.Uuid(),
            sa.ForeignKey("scripts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "unverified", "pass", "issue",
                name="verification_status", native_enum=False, length=16,
            ),
            nullable=False,
            server_default="unverified",
        ),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_verifications_script_id", "script_verifications", ["script_id"]
    )
    op.create_table(
        "verification_issues",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "verification_id",
            sa.Uuid(),
            sa.ForeignKey("script_verifications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "section_id",
            sa.Uuid(),
            sa.ForeignKey("script_sections.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "type",
            sa.Enum(
                "unsupported_claim", "exaggeration", "absolute_wording",
                "price_mismatch", "missing_restriction", "source_missing",
                name="issue_type", native_enum=False, length=24,
            ),
            nullable=False,
            server_default="unsupported_claim",
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "high", "medium", "low",
                name="issue_severity", native_enum=False, length=16,
            ),
            nullable=False,
            server_default="medium",
        ),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("quote", sa.Text(), nullable=True),
        sa.Column("suggestion", sa.Text(), nullable=True),
        sa.Column("origin", sa.String(16), nullable=False, server_default="ai"),
    )
    op.create_index(
        "ix_issues_verification_id", "verification_issues", ["verification_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_issues_verification_id", table_name="verification_issues")
    op.drop_table("verification_issues")
    op.drop_index("ix_verifications_script_id", table_name="script_verifications")
    op.drop_table("script_verifications")
    op.drop_column("scripts", "verification_status")
