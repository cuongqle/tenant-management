import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[User]):
    model = User
    order_by_column = User.email

    def list_by_organization_id(self, organization_id: uuid.UUID) -> list[User]:
        statement = (
            select(User)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .where(OrganizationMember.organization_id == organization_id)
            .order_by(User.email)
        )
        return list(self.db.scalars(statement).all())

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalars(statement).first()


UserRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
