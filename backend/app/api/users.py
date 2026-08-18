import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import get_or_404
from app.core.security import hash_password
from app.repositories.user import UserRepository
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/")
def get_users(repository: UserRepository) -> list[User]:
    return repository.list()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, repository: UserRepository) -> User:
    data = payload.model_dump()
    data["password"] = hash_password(data["password"])
    return repository.create(data)


@router.get("/{user_id}")
def get_user(user_id: uuid.UUID, repository: UserRepository) -> User:
    return get_or_404(repository, user_id, detail="User not found")


@router.patch("/{user_id}")
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    repository: UserRepository,
) -> User:
    user = get_or_404(repository, user_id, detail="User not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    if "password" in updates and updates["password"] is not None:
        updates["password"] = hash_password(updates["password"])
    return repository.update(user, updates)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: uuid.UUID, repository: UserRepository) -> Response:
    user = get_or_404(repository, user_id, detail="User not found")
    repository.delete(user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
