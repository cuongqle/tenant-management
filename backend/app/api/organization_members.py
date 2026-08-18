import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import get_or_404
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.user import UserRepository
from app.schemas.organization_member import (
    OrganizationMember,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
)

router = APIRouter(
    prefix="/organization-members",
    tags=["Organization Members"],
)


@router.get("/")
def get_organization_members(
    repository: OrganizationMemberRepository,
) -> list[OrganizationMember]:
    return repository.list()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_organization_member(
    payload: OrganizationMemberCreate,
    repository: OrganizationMemberRepository,
    organizations: OrganizationRepository,
    users: UserRepository,
) -> OrganizationMember:
    get_or_404(organizations, payload.organization_id, detail="Organization not found")
    get_or_404(users, payload.user_id, detail="User not found")
    existing = repository.get_by_organization_and_user(
        payload.organization_id,
        payload.user_id,
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this organization",
        )
    return repository.create(payload.model_dump())


@router.get("/{member_id}")
def get_organization_member(
    member_id: uuid.UUID,
    repository: OrganizationMemberRepository,
) -> OrganizationMember:
    return get_or_404(repository, member_id, detail="Organization member not found")


@router.patch("/{member_id}")
def update_organization_member(
    member_id: uuid.UUID,
    payload: OrganizationMemberUpdate,
    repository: OrganizationMemberRepository,
) -> OrganizationMember:
    member = get_or_404(repository, member_id, detail="Organization member not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    return repository.update(member, updates)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization_member(
    member_id: uuid.UUID,
    repository: OrganizationMemberRepository,
) -> Response:
    member = get_or_404(repository, member_id, detail="Organization member not found")
    repository.delete(member)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
