import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.models.invitation import Invitation
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[Invitation]):
    model = Invitation
    order_by_column = Invitation.created_at

    def get_by_token(self, token: str) -> Invitation | None:
        statement = select(Invitation).where(Invitation.token == token)
        return self.db.scalars(statement).first()

    def get_pending_by_organization_and_email(
        self,
        organization_id: uuid.UUID,
        email: str,
    ) -> Invitation | None:
        statement = select(Invitation).where(
            Invitation.organization_id == organization_id,
            Invitation.email == email,
            Invitation.accepted_at.is_(None),
        )
        return self.db.scalars(statement).first()

    def list_pending_by_organization_id(
        self, organization_id: uuid.UUID
    ) -> list[Invitation]:
        statement = (
            select(Invitation)
            .where(
                Invitation.organization_id == organization_id,
                Invitation.accepted_at.is_(None),
            )
            .order_by(Invitation.created_at.desc())
        )
        return list(self.db.scalars(statement).all())


InvitationRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
