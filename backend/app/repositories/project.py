import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.models.project import Project
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[Project]):
    model = Project
    order_by_column = Project.name

    def list_by_organization_id(self, organization_id: uuid.UUID) -> list[Project]:
        statement = (
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.name)
        )
        return list(self.db.scalars(statement).all())


ProjectRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
