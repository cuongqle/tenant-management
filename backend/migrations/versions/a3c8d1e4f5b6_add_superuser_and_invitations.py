"""add_superuser_and_invitations

Revision ID: a3c8d1e4f5b6
Revises: 872e06fe3e00
Create Date: 2026-08-19 11:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "a3c8d1e4f5b6"
down_revision: Union[str, Sequence[str], None] = "872e06fe3e00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.execute(
        sa.text("UPDATE users SET is_superuser = true WHERE email = :email").bindparams(
            email="admin@example.com"
        )
    )
    op.create_table(
        "invitations",
        sa.Column("organization_id", UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invited_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        "uq_invitations_pending_org_email",
        "invitations",
        ["organization_id", "email"],
        unique=True,
        postgresql_where=sa.text("accepted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_invitations_pending_org_email", table_name="invitations")
    op.drop_table("invitations")
    op.drop_column("users", "is_superuser")
