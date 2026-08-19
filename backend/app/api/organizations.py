import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status

from app.api.access import require_organization_member, tenant_ids_or_all
from app.api.deps import CurrentUser, get_or_404
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.invitation import Invitation, InvitationCreate
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.schemas.organization_member import (
    OrganizationMemberAssign,
    OrganizationMemberDetail,
)
from app.schemas.project import Project, ProjectAssign

INVITE_TTL = timedelta(days=7)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


def _require_organization(
    organization_id: uuid.UUID,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    principal: CurrentUser,
) -> Organization:
    organization = get_or_404(
        organizations, organization_id, detail="Organization not found"
    )
    require_organization_member(
        members,
        organization.id,
        principal,
        detail="Organization not found",
    )
    return organization


@router.get("/")
def get_organizations(
    principal: CurrentUser,
    repository: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> list[Organization]:
    organization_ids = tenant_ids_or_all(members, principal)
    if organization_ids is None:
        return repository.list()
    return repository.list_by_ids(organization_ids)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    principal: CurrentUser,
    repository: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> Organization:
    organization = repository.create(payload.model_dump())
    if not principal.is_superuser:
        members.create(
            {
                "organization_id": organization.id,
                "user_id": principal.id,
                "role": "admin",
            }
        )
    return organization


@router.get("/{organization_id}")
def get_organization(
    organization_id: uuid.UUID,
    principal: CurrentUser,
    repository: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> Organization:
    return _require_organization(
        organization_id, repository, members, principal
    )


@router.get("/{organization_id}/projects")
def get_organization_projects(
    organization_id: uuid.UUID,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    projects: ProjectRepository,
) -> list[Project]:
    _require_organization(organization_id, organizations, members, principal)
    return projects.list_by_organization_id(organization_id)


@router.post(
    "/{organization_id}/projects",
    status_code=status.HTTP_201_CREATED,
)
def add_organization_project(
    organization_id: uuid.UUID,
    payload: ProjectAssign,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    projects: ProjectRepository,
) -> Project:
    _require_organization(organization_id, organizations, members, principal)
    return projects.create(
        {
            **payload.model_dump(),
            "organization_id": organization_id,
        }
    )


@router.get("/{organization_id}/members")
def get_organization_members(
    organization_id: uuid.UUID,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> list[OrganizationMemberDetail]:
    _require_organization(organization_id, organizations, members, principal)
    return members.list_by_organization_id(organization_id)


@router.post(
    "/{organization_id}/members",
    status_code=status.HTTP_201_CREATED,
)
def add_organization_member(
    organization_id: uuid.UUID,
    payload: OrganizationMemberAssign,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    users: UserRepository,
    members: OrganizationMemberRepository,
) -> OrganizationMemberDetail:
    _require_organization(organization_id, organizations, members, principal)
    user = get_or_404(users, payload.user_id, detail="User not found")
    existing = members.get_by_organization_and_user(organization_id, payload.user_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this organization",
        )
    member = members.create(
        {
            "organization_id": organization_id,
            "user_id": payload.user_id,
            "role": payload.role,
        }
    )
    member.user = user
    return member


@router.get("/{organization_id}/invitations")
def get_organization_invitations(
    organization_id: uuid.UUID,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    invitations: InvitationRepository,
) -> list[Invitation]:
    _require_organization(organization_id, organizations, members, principal)
    return invitations.list_pending_by_organization_id(organization_id)


@router.post(
    "/{organization_id}/invitations",
    status_code=status.HTTP_201_CREATED,
)
def create_organization_invitation(
    organization_id: uuid.UUID,
    payload: InvitationCreate,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    invitations: InvitationRepository,
    users: UserRepository,
) -> Invitation:
    _require_organization(organization_id, organizations, members, principal)
    email = str(payload.email).lower()
    existing_user = users.get_by_email(email)
    if existing_user is not None:
        membership = members.get_by_organization_and_user(
            organization_id, existing_user.id
        )
        if membership is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this organization",
            )
    pending = invitations.get_pending_by_organization_and_email(organization_id, email)
    if pending is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An invitation is already pending for this email",
        )
    return invitations.create(
        {
            "organization_id": organization_id,
            "email": email,
            "role": payload.role,
            "token": secrets.token_urlsafe(32),
            "expires_at": datetime.now(UTC) + INVITE_TTL,
            "invited_by_id": principal.id,
        }
    )


@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organization_invitation(
    organization_id: uuid.UUID,
    invitation_id: uuid.UUID,
    principal: CurrentUser,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    invitations: InvitationRepository,
) -> Response:
    _require_organization(organization_id, organizations, members, principal)
    invitation = get_or_404(invitations, invitation_id, detail="Invitation not found")
    if invitation.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    invitations.delete(invitation)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{organization_id}")
def update_organization(
    organization_id: uuid.UUID,
    payload: OrganizationUpdate,
    principal: CurrentUser,
    repository: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> Organization:
    organization = _require_organization(
        organization_id, repository, members, principal
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    return repository.update(organization, updates)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: uuid.UUID,
    principal: CurrentUser,
    repository: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> Response:
    organization = _require_organization(
        organization_id, repository, members, principal
    )
    repository.delete(organization)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
