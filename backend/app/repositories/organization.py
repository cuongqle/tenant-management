import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.models.organization import Organization
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[Organization]):
    model = Organization
    order_by_column = Organization.name

    def list_by_ids(self, organization_ids: list[uuid.UUID]) -> list[Organization]:
        if not organization_ids:
            return []
        statement = (
            select(Organization)
            .where(Organization.id.in_(organization_ids))
            .order_by(Organization.name)
        )
        return list(self.db.scalars(statement).all())


OrganizationRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
