import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.models.environment import Environment
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[Environment]):
    model = Environment
    order_by_column = Environment.name

    def list_by_project_id(self, project_id: uuid.UUID) -> list[Environment]:
        statement = (
            select(Environment)
            .where(Environment.project_id == project_id)
            .order_by(Environment.name)
        )
        return list(self.db.scalars(statement).all())


EnvironmentRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
