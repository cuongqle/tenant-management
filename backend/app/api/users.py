import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.access import require_visible_user, tenant_ids_or_all
from app.api.deps import CurrentUser, get_or_404
from app.core.security import hash_password
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.user import UserRepository
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def _require_superuser(principal: CurrentUser) -> None:
    if not principal.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a super admin can do that. Invite people to an organization instead.",
        )


@router.get("/")
def get_users(
    principal: CurrentUser,
    repository: UserRepository,
    members: OrganizationMemberRepository,
) -> list[User]:
    organization_ids = tenant_ids_or_all(members, principal)
    if organization_ids is None:
        return repository.list()
    return repository.list_by_organization_ids(organization_ids)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    principal: CurrentUser,
    repository: UserRepository,
) -> User:
    _require_superuser(principal)
    data = payload.model_dump()
    data["password"] = hash_password(data["password"])
    data["is_superuser"] = False
    return repository.create(data)


@router.get("/{user_id}")
def get_user(
    user_id: uuid.UUID,
    principal: CurrentUser,
    repository: UserRepository,
    members: OrganizationMemberRepository,
) -> User:
    user = get_or_404(repository, user_id, detail="User not found")
    require_visible_user(members, principal, user.id, detail="User not found")
    return user


@router.patch("/{user_id}")
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    principal: CurrentUser,
    repository: UserRepository,
    members: OrganizationMemberRepository,
) -> User:
    user = get_or_404(repository, user_id, detail="User not found")
    require_visible_user(members, principal, user.id, detail="User not found")
    if not principal.is_superuser and principal.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own account",
        )
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
def delete_user(
    user_id: uuid.UUID,
    principal: CurrentUser,
    repository: UserRepository,
    members: OrganizationMemberRepository,
) -> Response:
    _require_superuser(principal)
    user = get_or_404(repository, user_id, detail="User not found")
    repository.delete(user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
