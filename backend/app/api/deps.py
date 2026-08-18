import uuid
from typing import Annotated, Any, TypeVar

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.repositories._base_ import BaseRepository

TModel = TypeVar("TModel")

http_bearer = HTTPBearer(auto_error=False)

def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_or_404(
    repository: BaseRepository[TModel],
    entity_id: uuid.UUID,
    *,
    detail: str = "Resource not found",
) -> TModel:
    entity = repository.get_by_id(entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return entity


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        payload = decode_access_token(credentials.credentials)
        uuid.UUID(str(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise _unauthorized() from None

    return payload
