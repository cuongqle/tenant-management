import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import get_or_404
from app.repositories.environment import EnvironmentRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.project import ProjectRepository
from app.schemas.environment import Environment, EnvironmentAssign
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("/")
def get_projects(repository: ProjectRepository) -> list[Project]:
    return repository.list()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    repository: ProjectRepository,
    organizations: OrganizationRepository,
) -> Project:
    get_or_404(organizations, payload.organization_id, detail="Organization not found")
    return repository.create(payload.model_dump())


@router.get("/{project_id}")
def get_project(project_id: uuid.UUID, repository: ProjectRepository) -> Project:
    return get_or_404(repository, project_id, detail="Project not found")


@router.get("/{project_id}/environments")
def get_project_environments(
    project_id: uuid.UUID,
    projects: ProjectRepository,
    environments: EnvironmentRepository,
) -> list[Environment]:
    get_or_404(projects, project_id, detail="Project not found")
    return environments.list_by_project_id(project_id)


@router.post(
    "/{project_id}/environments",
    status_code=status.HTTP_201_CREATED,
)
def add_project_environment(
    project_id: uuid.UUID,
    payload: EnvironmentAssign,
    projects: ProjectRepository,
    environments: EnvironmentRepository,
) -> Environment:
    get_or_404(projects, project_id, detail="Project not found")
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
    repository: ProjectRepository,
    organizations: OrganizationRepository,
) -> Project:
    project = get_or_404(repository, project_id, detail="Project not found")
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
    return repository.update(project, updates)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, repository: ProjectRepository) -> Response:
    project = get_or_404(repository, project_id, detail="Project not found")
    repository.delete(project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
