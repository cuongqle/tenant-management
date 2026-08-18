import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import contains_eager

from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[OrganizationMember]):
    model = OrganizationMember
    order_by_column = OrganizationMember.role

    def list_by_organization_id(
        self, organization_id: uuid.UUID
    ) -> list[OrganizationMember]:
        statement = (
            select(OrganizationMember)
            .join(User, User.id == OrganizationMember.user_id)
            .where(OrganizationMember.organization_id == organization_id)
            .options(contains_eager(OrganizationMember.user))
            .order_by(User.email)
        )
        return list(self.db.scalars(statement).unique().all())

    def get_by_organization_and_user(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrganizationMember | None:
        statement = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        return self.db.scalars(statement).first()


OrganizationMemberRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
