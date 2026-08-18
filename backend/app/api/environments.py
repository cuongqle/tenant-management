import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import get_or_404
from app.repositories.environment import EnvironmentRepository
from app.repositories.project import ProjectRepository
from app.schemas.environment import Environment, EnvironmentCreate, EnvironmentUpdate

router = APIRouter(
    prefix="/environments",
    tags=["Environments"],
)


@router.get("/")
def get_environments(repository: EnvironmentRepository) -> list[Environment]:
    return repository.list()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_environment(
    payload: EnvironmentCreate,
    repository: EnvironmentRepository,
    projects: ProjectRepository,
) -> Environment:
    get_or_404(projects, payload.project_id, detail="Project not found")
    return repository.create(payload.model_dump())


@router.get("/{environment_id}")
def get_environment(
    environment_id: uuid.UUID,
    repository: EnvironmentRepository,
) -> Environment:
    return get_or_404(repository, environment_id, detail="Environment not found")


@router.patch("/{environment_id}")
def update_environment(
    environment_id: uuid.UUID,
    payload: EnvironmentUpdate,
    repository: EnvironmentRepository,
    projects: ProjectRepository,
) -> Environment:
    environment = get_or_404(repository, environment_id, detail="Environment not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    if "project_id" in updates:
        get_or_404(projects, updates["project_id"], detail="Project not found")
    return repository.update(environment, updates)


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    environment_id: uuid.UUID,
    repository: EnvironmentRepository,
) -> Response:
    environment = get_or_404(repository, environment_id, detail="Environment not found")
    repository.delete(environment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
