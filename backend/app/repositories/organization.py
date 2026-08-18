from typing import Annotated

from fastapi import Depends

from app.models.organization import Organization
from app.repositories._base_ import BaseRepository, get_repository


class Repository(BaseRepository[Organization]):
    model = Organization
    order_by_column = Organization.name


OrganizationRepository = Annotated[
    Repository,
    Depends(get_repository(Repository)),
]
