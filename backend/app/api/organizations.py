import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import get_or_404
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.schemas.organization_member import (
    OrganizationMemberAssign,
    OrganizationMemberDetail,
)
from app.schemas.project import Project, ProjectAssign

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/")
def get_organizations(repository: OrganizationRepository) -> list[Organization]:
    return repository.list()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    repository: OrganizationRepository,
) -> Organization:
    return repository.create(payload.model_dump())


@router.get("/{organization_id}")
def get_organization(
    organization_id: uuid.UUID,
    repository: OrganizationRepository,
) -> Organization:
    return get_or_404(repository, organization_id, detail="Organization not found")


@router.get("/{organization_id}/projects")
def get_organization_projects(
    organization_id: uuid.UUID,
    organizations: OrganizationRepository,
    projects: ProjectRepository,
) -> list[Project]:
    get_or_404(organizations, organization_id, detail="Organization not found")
    return projects.list_by_organization_id(organization_id)


@router.post(
    "/{organization_id}/projects",
    status_code=status.HTTP_201_CREATED,
)
def add_organization_project(
    organization_id: uuid.UUID,
    payload: ProjectAssign,
    organizations: OrganizationRepository,
    projects: ProjectRepository,
) -> Project:
    get_or_404(organizations, organization_id, detail="Organization not found")
    return projects.create(
        {
            **payload.model_dump(),
            "organization_id": organization_id,
        }
    )


@router.get("/{organization_id}/members")
def get_organization_members(
    organization_id: uuid.UUID,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> list[OrganizationMemberDetail]:
    get_or_404(organizations, organization_id, detail="Organization not found")
    return members.list_by_organization_id(organization_id)


@router.post(
    "/{organization_id}/members",
    status_code=status.HTTP_201_CREATED,
)
def add_organization_member(
    organization_id: uuid.UUID,
    payload: OrganizationMemberAssign,
    organizations: OrganizationRepository,
    users: UserRepository,
    members: OrganizationMemberRepository,
) -> OrganizationMemberDetail:
    get_or_404(organizations, organization_id, detail="Organization not found")
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


@router.patch("/{organization_id}")
def update_organization(
    organization_id: uuid.UUID,
    payload: OrganizationUpdate,
    repository: OrganizationRepository,
) -> Organization:
    organization = get_or_404(repository, organization_id, detail="Organization not found")
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
    repository: OrganizationRepository,
) -> Response:
    organization = get_or_404(repository, organization_id, detail="Organization not found")
    repository.delete(organization)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
