import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.access import require_organization_member, tenant_ids_or_all
from app.api.deps import CurrentUser, get_or_404
from app.models.environment import Environment as EnvironmentModel
from app.repositories.environment import EnvironmentRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.project import ProjectRepository
from app.schemas.environment import Environment, EnvironmentCreate, EnvironmentUpdate

router = APIRouter(
    prefix="/environments",
    tags=["Environments"],
)


def _require_environment(
    environment_id: uuid.UUID,
    environments: EnvironmentRepository,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
    principal: CurrentUser,
) -> EnvironmentModel:
    environment = get_or_404(
        environments, environment_id, detail="Environment not found"
    )
    project = get_or_404(projects, environment.project_id, detail="Environment not found")
    require_organization_member(
        members,
        project.organization_id,
        principal,
        detail="Environment not found",
    )
    return environment


def _require_project_organization(
    project_id: uuid.UUID,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
    principal: CurrentUser,
    *,
    detail: str,
):
    project = get_or_404(projects, project_id, detail=detail)
    require_organization_member(
        members,
        project.organization_id,
        principal,
        detail=detail,
    )
    return project


@router.get("/")
def get_environments(
    principal: CurrentUser,
    repository: EnvironmentRepository,
    members: OrganizationMemberRepository,
) -> list[Environment]:
    organization_ids = tenant_ids_or_all(members, principal)
    if organization_ids is None:
        return repository.list()
    return repository.list_by_organization_ids(organization_ids)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_environment(
    payload: EnvironmentCreate,
    principal: CurrentUser,
    repository: EnvironmentRepository,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
) -> Environment:
    _require_project_organization(
        payload.project_id,
        projects,
        members,
        principal,
        detail="Project not found",
    )
    return repository.create(payload.model_dump())


@router.get("/{environment_id}")
def get_environment(
    environment_id: uuid.UUID,
    principal: CurrentUser,
    repository: EnvironmentRepository,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
) -> Environment:
    return _require_environment(
        environment_id, repository, projects, members, principal
    )


@router.patch("/{environment_id}")
def update_environment(
    environment_id: uuid.UUID,
    payload: EnvironmentUpdate,
    principal: CurrentUser,
    repository: EnvironmentRepository,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
) -> Environment:
    environment = _require_environment(
        environment_id, repository, projects, members, principal
    )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    if "project_id" in updates:
        _require_project_organization(
            updates["project_id"],
            projects,
            members,
            principal,
            detail="Project not found",
        )
    return repository.update(environment, updates)


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    environment_id: uuid.UUID,
    principal: CurrentUser,
    repository: EnvironmentRepository,
    projects: ProjectRepository,
    members: OrganizationMemberRepository,
) -> Response:
    environment = _require_environment(
        environment_id, repository, projects, members, principal
    )
    repository.delete(environment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
