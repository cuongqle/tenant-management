"""seed_initial_data

Revision ID: 872e06fe3e00
Revises: 51a6015fb56b
Create Date: 2026-08-17 19:10:00.000000

"""

from typing import Sequence, Union
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.core.security import hash_password

# revision identifiers, used by Alembic.
revision: str = "872e06fe3e00"
down_revision: Union[str, Sequence[str], None] = "51a6015fb56b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ORG_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
USER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
MEMBER_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"


def upgrade() -> None:
    organizations = sa.table(
        "organizations",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("email", sa.String),
    )
    users = sa.table(
        "users",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("email", sa.String),
        sa.column("name", sa.String),
        sa.column("password", sa.String),
    )
    organization_members = sa.table(
        "organization_members",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("organization_id", UUID(as_uuid=True)),
        sa.column("user_id", UUID(as_uuid=True)),
        sa.column("role", sa.String),
    )

    op.bulk_insert(
        organizations,
        [
            {
                "id": ORG_ID,
                "name": "Default Organization",
                "description": "Initial seeded organization",
                "email": "org@example.com",
            }
        ],
    )
    op.bulk_insert(
        users,
        [
            {
                "id": USER_ID,
                "email": ADMIN_EMAIL,
                "name": "Admin",
                "password": hash_password(ADMIN_PASSWORD),
            }
        ],
    )
    op.bulk_insert(
        organization_members,
        [
            {
                "id": MEMBER_ID,
                "organization_id": ORG_ID,
                "user_id": USER_ID,
                "role": "admin",
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM organization_members WHERE id = :id").bindparams(id=MEMBER_ID)
    )
    op.execute(sa.text("DELETE FROM users WHERE id = :id").bindparams(id=USER_ID))
    op.execute(sa.text("DELETE FROM organizations WHERE id = :id").bindparams(id=ORG_ID))
