import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.access import require_organization_member, tenant_ids_or_all
from app.api.deps import CurrentUser, get_or_404
from app.models.organization_member import OrganizationMember as OrganizationMemberModel
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


def _require_member_row(
    member_id: uuid.UUID,
    repository: OrganizationMemberRepository,
    principal: CurrentUser,
) -> OrganizationMemberModel:
    member = get_or_404(repository, member_id, detail="Organization member not found")
    require_organization_member(
        repository,
        member.organization_id,
        principal,
        detail="Organization member not found",
    )
    return member


@router.get("/")
def get_organization_members(
    principal: CurrentUser,
    repository: OrganizationMemberRepository,
) -> list[OrganizationMember]:
    organization_ids = tenant_ids_or_all(repository, principal)
    if organization_ids is None:
        return repository.list()
    return repository.list_by_organization_ids(organization_ids)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_organization_member(
    payload: OrganizationMemberCreate,
    principal: CurrentUser,
    repository: OrganizationMemberRepository,
    organizations: OrganizationRepository,
    users: UserRepository,
) -> OrganizationMember:
    get_or_404(organizations, payload.organization_id, detail="Organization not found")
    require_organization_member(
        repository,
        payload.organization_id,
        principal,
        detail="Organization not found",
    )
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
    principal: CurrentUser,
    repository: OrganizationMemberRepository,
) -> OrganizationMember:
    return _require_member_row(member_id, repository, principal)


@router.patch("/{member_id}")
def update_organization_member(
    member_id: uuid.UUID,
    payload: OrganizationMemberUpdate,
    principal: CurrentUser,
    repository: OrganizationMemberRepository,
) -> OrganizationMember:
    member = _require_member_row(member_id, repository, principal)
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
    principal: CurrentUser,
    repository: OrganizationMemberRepository,
) -> Response:
    member = _require_member_row(member_id, repository, principal)
    repository.delete(member)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
