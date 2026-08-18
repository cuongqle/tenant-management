import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.main import app
from app.repositories._base_ import get_repository
from app.repositories.environment import Repository as EnvironmentRepo
from app.repositories.organization import Repository as OrganizationRepo
from app.repositories.organization_member import Repository as OrganizationMemberRepo
from app.repositories.project import Repository as ProjectRepo
from app.repositories.user import Repository as UserRepo


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_organization_projects(auth_client) -> None:
    organization_id = uuid.uuid4()
    project = SimpleNamespace(
        id=uuid.uuid4(),
        name="Demo",
        description=None,
        start_date=datetime.now(timezone.utc),
        end_date=None,
        status="active",
        organization_id=organization_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    projects = MagicMock()
    projects.list_by_organization_id.return_value = [project]

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(ProjectRepo)] = lambda: projects

    response = auth_client.get(f"/api/v1/organizations/{organization_id}/projects")

    assert response.status_code == 200, response.json()
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Demo"
    projects.list_by_organization_id.assert_called_once_with(organization_id)


def test_add_organization_project(auth_client) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    created = SimpleNamespace(
        id=uuid.uuid4(),
        name="Nested",
        description=None,
        start_date=now,
        end_date=None,
        status="active",
        organization_id=organization_id,
        created_at=now,
        updated_at=now,
    )

    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    projects = MagicMock()
    projects.create.return_value = created

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(ProjectRepo)] = lambda: projects

    response = auth_client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        json={
            "name": "Nested",
            "start_date": now.isoformat(),
            "status": "active",
        },
    )

    assert response.status_code == 201, response.json()
    assert response.json()["name"] == "Nested"
    projects.create.assert_called_once()
    created_data = projects.create.call_args.args[0]
    assert created_data["organization_id"] == organization_id
    assert created_data["name"] == "Nested"


def test_get_project_environments(auth_client) -> None:
    project_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    environment = SimpleNamespace(
        id=uuid.uuid4(),
        name="staging",
        description=None,
        project_id=project_id,
        created_at=now,
        updated_at=now,
    )

    projects = MagicMock()
    projects.get_by_id.return_value = SimpleNamespace(id=project_id)
    environments = MagicMock()
    environments.list_by_project_id.return_value = [environment]

    app.dependency_overrides[get_repository(ProjectRepo)] = lambda: projects
    app.dependency_overrides[get_repository(EnvironmentRepo)] = lambda: environments

    response = auth_client.get(f"/api/v1/projects/{project_id}/environments")

    assert response.status_code == 200, response.json()
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "staging"
    environments.list_by_project_id.assert_called_once_with(project_id)


def test_add_project_environment(auth_client) -> None:
    project_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    created = SimpleNamespace(
        id=uuid.uuid4(),
        name="prod",
        description=None,
        project_id=project_id,
        created_at=now,
        updated_at=now,
    )

    projects = MagicMock()
    projects.get_by_id.return_value = SimpleNamespace(id=project_id)
    environments = MagicMock()
    environments.create.return_value = created

    app.dependency_overrides[get_repository(ProjectRepo)] = lambda: projects
    app.dependency_overrides[get_repository(EnvironmentRepo)] = lambda: environments

    response = auth_client.post(
        f"/api/v1/projects/{project_id}/environments",
        json={"name": "prod"},
    )

    assert response.status_code == 201, response.json()
    assert response.json()["name"] == "prod"
    created_data = environments.create.call_args.args[0]
    assert created_data["project_id"] == project_id
    assert created_data["name"] == "prod"


def test_get_organization_members(auth_client) -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    user = SimpleNamespace(
        id=user_id,
        email="member@example.com",
        name="Member",
        created_at=now,
        updated_at=now,
    )
    member = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        user_id=user_id,
        role="admin",
        created_at=now,
        updated_at=now,
        user=user,
    )

    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    members = MagicMock()
    members.list_by_organization_id.return_value = [member]

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.get(f"/api/v1/organizations/{organization_id}/members")

    assert response.status_code == 200, response.json()
    body = response.json()
    assert len(body) == 1
    assert body[0]["role"] == "admin"
    assert body[0]["user"]["email"] == "member@example.com"
    members.list_by_organization_id.assert_called_once_with(organization_id)


def test_add_organization_member(auth_client) -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    user = SimpleNamespace(
        id=user_id,
        email="new@example.com",
        name="New",
        created_at=now,
        updated_at=now,
    )
    created = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        user_id=user_id,
        role="member",
        created_at=now,
        updated_at=now,
        user=user,
    )

    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    users = MagicMock()
    users.get_by_id.return_value = user
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None
    members.create.return_value = created

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={"user_id": str(user_id), "role": "member"},
    )

    assert response.status_code == 201, response.json()
    assert response.json()["user"]["email"] == "new@example.com"
    members.create.assert_called_once()


def test_add_organization_member_rejects_duplicate(auth_client) -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    users = MagicMock()
    users.get_by_id.return_value = SimpleNamespace(id=user_id)
    members = MagicMock()
    members.get_by_organization_and_user.return_value = SimpleNamespace(id=uuid.uuid4())

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={"user_id": str(user_id), "role": "member"},
    )

    assert response.status_code == 409
    members.create.assert_not_called()


def test_protected_route_without_token_returns_401(client) -> None:
    response = client.get("/api/v1/organizations/")
    assert response.status_code == 401


def test_protected_route_with_invalid_token_returns_401(client) -> None:
    response = client.get(
        "/api/v1/organizations/",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401
