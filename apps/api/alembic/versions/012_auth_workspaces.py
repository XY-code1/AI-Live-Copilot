"""add authentication and workspace memberships

Revision ID: 012
Revises: 011
Create Date: 2026-11-16
"""

import uuid

import sqlalchemy as sa

from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("workspaces", sa.Column("owner_user_id", sa.String(255), nullable=True))
    op.execute("UPDATE workspaces SET owner_user_id = 'legacy-user' WHERE owner_user_id IS NULL")
    with op.batch_alter_table("workspaces") as batch_op:
        batch_op.alter_column("owner_user_id", nullable=False)
    bind = op.get_bind()
    workspace_id = bind.execute(sa.text("SELECT id FROM workspaces ORDER BY created_at LIMIT 1")).scalar()
    if workspace_id is None:
        workspace_id = uuid.uuid4().hex
        bind.execute(
            sa.text(
                "INSERT INTO workspaces (id, name, plan, owner_user_id) "
                "VALUES (:id, '迁移工作区', 'trial', 'legacy-user')"
            ),
            {"id": workspace_id},
        )
    for table in ("products", "competitors", "comparisons", "scripts"):
        bind.execute(
            sa.text(f"UPDATE {table} SET workspace_id = :workspace_id WHERE workspace_id IS NULL"),
            {"workspace_id": workspace_id},
        )
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column("workspace_id", nullable=False)

    op.create_table(
        "workspace_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_membership"),
    )
    op.create_index("ix_workspace_memberships_user_id", "workspace_memberships", ["user_id"])
    op.execute(
        "INSERT INTO workspace_memberships (id, workspace_id, user_id, role) "
        "SELECT id, id, owner_user_id, 'owner' FROM workspaces"
    )


def downgrade() -> None:
    op.drop_index("ix_workspace_memberships_user_id", table_name="workspace_memberships")
    op.drop_table("workspace_memberships")
    for table in ("products", "competitors", "comparisons", "scripts"):
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column("workspace_id", nullable=True)
    op.drop_column("workspaces", "owner_user_id")

