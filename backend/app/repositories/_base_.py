import uuid
from collections.abc import Callable, Mapping
from typing import Any, ClassVar, Generic, TypeVar

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models._base_ import Base

TRepository = TypeVar("TRepository", bound="BaseRepository")
TModel = TypeVar("TModel", bound=Base)


class BaseRepository(Generic[TModel]):
    model: ClassVar[type[Base]]
    order_by_column: ClassVar[Any | None] = None

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[TModel]:
        model = type(self).model
        order_by_column = type(self).order_by_column
        statement = select(model)
        if order_by_column is not None:
            statement = statement.order_by(order_by_column)
        return list(self.db.scalars(statement).all())

    def get_by_id(self, entity_id: uuid.UUID) -> TModel | None:
        return self.db.get(type(self).model, entity_id)

    def create(self, data: Mapping[str, Any]) -> TModel:
        entity = type(self).model(**data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: TModel, data: Mapping[str, Any]) -> TModel:
        for field, value in data.items():
            setattr(entity, field, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: TModel) -> None:
        self.db.delete(entity)
        self.db.commit()


_repository_dependencies: dict[type, Callable[..., Any]] = {}


def get_repository(repo: type[TRepository]) -> Callable[..., TRepository]:
    if repo not in _repository_dependencies:

        def dependency(db: Session = Depends(get_db)) -> TRepository:
            return repo(db)

        _repository_dependencies[repo] = dependency
    return _repository_dependencies[repo]  # type: ignore[return-value]
