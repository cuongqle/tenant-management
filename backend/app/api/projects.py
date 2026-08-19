import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.access import require_organization_member, tenant_ids_or_all
from app.api.deps import CurrentUser, get_or_404
from app.models.project import Project as ProjectModel
from app.repositories.environment import EnvironmentRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.project import ProjectRepository
from app.schemas.environment import Environment, EnvironmentAssign
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


def _require_project(
    project_id: uuid.UUID,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
    principal: CurrentUser,
) -> ProjectModel:
    project = get_or_404(projects, project_id, detail="Project not found")
    require_organization_member(
        members,
        project.organization_id,
        principal,
        detail="Project not found",
    )
    return project


@router.get("/")
def get_projects(
    principal: CurrentUser,
    repository: ProjectRepository,
    members: OrganizationMemberRepository,
) -> list[Project]:
    organization_ids = tenant_ids_or_all(members, principal)
    if organization_ids is None:
        return repository.list()
    return repository.list_by_organization_ids(organization_ids)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    principal: CurrentUser,
    repository: ProjectRepository,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> Project:
    get_or_404(organizations, payload.organization_id, detail="Organization not found")
    require_organization_member(
        members,
        payload.organization_id,
        principal,
        detail="Organization not found",
    )
    return repository.create(payload.model_dump())


@router.get("/{project_id}")
def get_project(
    project_id: uuid.UUID,
    principal: CurrentUser,
    repository: ProjectRepository,
    members: OrganizationMemberRepository,
) -> Project:
    return _require_project(project_id, repository, members, principal)


@router.get("/{project_id}/environments")
def get_project_environments(
    project_id: uuid.UUID,
    principal: CurrentUser,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
    environments: EnvironmentRepository,
) -> list[Environment]:
    _require_project(project_id, projects, members, principal)
    return environments.list_by_project_id(project_id)


@router.post(
    "/{project_id}/environments",
    status_code=status.HTTP_201_CREATED,
)
def add_project_environment(
    project_id: uuid.UUID,
    payload: EnvironmentAssign,
    principal: CurrentUser,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
    environments: EnvironmentRepository,
) -> Environment:
    _require_project(project_id, projects, members, principal)
    return environments.create(
        {
            **payload.model_dump(),
            "project_id": project_id,
        }
    )


@router.patch("/{project_id}")
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    principal: CurrentUser,
    repository: ProjectRepository,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
) -> Project:
    project = _require_project(project_id, repository, members, principal)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    if "organization_id" in updates:
        get_or_404(
            organizations,
            updates["organization_id"],
            detail="Organization not found",
        )
        require_organization_member(
            members,
            updates["organization_id"],
            principal,
            detail="Organization not found",
        )
    return repository.update(project, updates)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    principal: CurrentUser,
    repository: ProjectRepository,
    members: OrganizationMemberRepository,
) -> Response:
    project = _require_project(project_id, repository, members, principal)
    repository.delete(project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
