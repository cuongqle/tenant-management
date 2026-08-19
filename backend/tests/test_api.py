import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.main import app
from app.repositories._base_ import get_repository
from app.repositories.environment import Repository as EnvironmentRepo
from app.repositories.invitation import Repository as InvitationRepo
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
    projects.get_by_id.return_value = SimpleNamespace(
        id=project_id,
        organization_id=uuid.uuid4(),
    )
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
    projects.get_by_id.return_value = SimpleNamespace(
        id=project_id,
        organization_id=uuid.uuid4(),
    )
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


def test_get_organization_members(auth_client, current_user_id) -> None:
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
    members.get_by_organization_and_user.return_value = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        user_id=current_user_id,
        role="member",
    )
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


def test_add_organization_member(auth_client, current_user_id) -> None:
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

    def membership_lookup(_organization_id: uuid.UUID, lookup_user_id: uuid.UUID):
        if lookup_user_id == current_user_id:
            return SimpleNamespace(
                id=uuid.uuid4(),
                organization_id=organization_id,
                user_id=current_user_id,
                role="admin",
            )
        return None

    members.get_by_organization_and_user.side_effect = membership_lookup
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


def test_add_organization_member_rejects_duplicate(auth_client, current_user_id) -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    users = MagicMock()
    users.get_by_id.return_value = SimpleNamespace(id=user_id)
    members = MagicMock()

    def membership_lookup(_organization_id: uuid.UUID, lookup_user_id: uuid.UUID):
        if lookup_user_id == current_user_id:
            return SimpleNamespace(id=uuid.uuid4())
        if lookup_user_id == user_id:
            return SimpleNamespace(id=uuid.uuid4())
        return None

    members.get_by_organization_and_user.side_effect = membership_lookup

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.post(
        f"/api/v1/organizations/{organization_id}/members",
        json={"user_id": str(user_id), "role": "member"},
    )

    assert response.status_code == 409
    members.create.assert_not_called()


def test_list_organizations_scoped_to_membership(auth_client, current_user_id) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    organization = SimpleNamespace(
        id=organization_id,
        name="Acme",
        description=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone=None,
        email=None,
        website=None,
        industry=None,
        created_at=now,
        updated_at=now,
    )
    members = MagicMock()
    members.list_organization_ids_for_user.return_value = [organization_id]
    organizations = MagicMock()
    organizations.list_by_ids.return_value = [organization]

    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members
    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations

    response = auth_client.get("/api/v1/organizations/")

    assert response.status_code == 200, response.json()
    assert response.json()[0]["name"] == "Acme"
    members.list_organization_ids_for_user.assert_called_once_with(current_user_id)
    organizations.list_by_ids.assert_called_once_with([organization_id])
    organizations.list.assert_not_called()


def test_get_organization_hidden_when_not_a_member(auth_client) -> None:
    organization_id = uuid.uuid4()
    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.get(f"/api/v1/organizations/{organization_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Organization not found"


def test_create_organization_adds_creator_as_admin(auth_client, current_user_id) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    created = SimpleNamespace(
        id=organization_id,
        name="New Org",
        description=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone=None,
        email=None,
        website=None,
        industry=None,
        created_at=now,
        updated_at=now,
    )
    organizations = MagicMock()
    organizations.create.return_value = created
    members = MagicMock()

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.post("/api/v1/organizations/", json={"name": "New Org"})

    assert response.status_code == 201, response.json()
    members.create.assert_called_once_with(
        {
            "organization_id": organization_id,
            "user_id": current_user_id,
            "role": "admin",
        }
    )


def test_get_project_hidden_when_not_a_member(auth_client) -> None:
    project_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    project = SimpleNamespace(
        id=project_id,
        name="Secret",
        description=None,
        start_date=now,
        end_date=None,
        status="active",
        organization_id=organization_id,
        created_at=now,
        updated_at=now,
    )
    projects = MagicMock()
    projects.get_by_id.return_value = project
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None

    app.dependency_overrides[get_repository(ProjectRepo)] = lambda: projects
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_superuser_lists_all_organizations(superuser_client) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    organization = SimpleNamespace(
        id=organization_id,
        name="Globex",
        description=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone=None,
        email=None,
        website=None,
        industry=None,
        created_at=now,
        updated_at=now,
    )
    organizations = MagicMock()
    organizations.list.return_value = [organization]
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = superuser_client.get("/api/v1/organizations/")

    assert response.status_code == 200, response.json()
    assert response.json()[0]["name"] == "Globex"
    organizations.list.assert_called_once()
    organizations.list_by_ids.assert_not_called()
    members.list_organization_ids_for_user.assert_not_called()


def test_superuser_can_open_organization_without_membership(superuser_client) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    organization = SimpleNamespace(
        id=organization_id,
        name="Globex",
        description=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone=None,
        email=None,
        website=None,
        industry=None,
        created_at=now,
        updated_at=now,
    )
    organizations = MagicMock()
    organizations.get_by_id.return_value = organization
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = superuser_client.get(f"/api/v1/organizations/{organization_id}")

    assert response.status_code == 200, response.json()
    assert response.json()["name"] == "Globex"
    members.get_by_organization_and_user.assert_not_called()


def test_superuser_create_organization_skips_membership(
    superuser_client, current_user_id
) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    created = SimpleNamespace(
        id=organization_id,
        name="Shell Org",
        description=None,
        address=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone=None,
        email=None,
        website=None,
        industry=None,
        created_at=now,
        updated_at=now,
    )
    organizations = MagicMock()
    organizations.create.return_value = created
    members = MagicMock()

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = superuser_client.post(
        "/api/v1/organizations/", json={"name": "Shell Org"}
    )

    assert response.status_code == 201, response.json()
    members.create.assert_not_called()


def test_create_organization_invitation(auth_client, current_user_id) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    created = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        email="join@example.com",
        role="member",
        token="invite-token",
        expires_at=now,
        accepted_at=None,
        invited_by_id=current_user_id,
        created_at=now,
        updated_at=now,
    )
    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(id=organization_id)
    users = MagicMock()
    users.get_by_email.return_value = None
    invitations = MagicMock()
    invitations.get_pending_by_organization_and_email.return_value = None
    invitations.create.return_value = created

    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(InvitationRepo)] = lambda: invitations

    response = auth_client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        json={"email": "join@example.com", "role": "member"},
    )

    assert response.status_code == 201, response.json()
    assert response.json()["email"] == "join@example.com"
    created_data = invitations.create.call_args.args[0]
    assert created_data["email"] == "join@example.com"
    assert created_data["role"] == "member"
    assert created_data["organization_id"] == organization_id
    assert created_data["invited_by_id"] == current_user_id
    assert "token" in created_data


def test_preview_invitation_is_public(client) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    invitation = SimpleNamespace(
        organization_id=organization_id,
        email="join@example.com",
        role="admin",
        expires_at=now,
        accepted_at=None,
    )
    invitations = MagicMock()
    invitations.get_by_token.return_value = invitation
    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(
        id=organization_id, name="Acme"
    )

    app.dependency_overrides[get_repository(InvitationRepo)] = lambda: invitations
    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations

    response = client.get("/api/v1/invitations/invite-token")

    assert response.status_code == 200, response.json()
    body = response.json()
    assert body["organization_name"] == "Acme"
    assert body["email"] == "join@example.com"
    assert body["accepted"] is False


def test_accept_invitation(auth_client, current_user_id) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    invitation = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        email="test@example.com",
        role="member",
        expires_at=now + timedelta(days=7),
        accepted_at=None,
    )
    user = SimpleNamespace(
        id=current_user_id,
        email="test@example.com",
        name="Test",
        created_at=now,
        updated_at=now,
    )
    member = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        user_id=current_user_id,
        role="member",
        created_at=now,
        updated_at=now,
        user=user,
    )
    invitations = MagicMock()
    invitations.get_by_token.return_value = invitation
    organizations = MagicMock()
    organizations.get_by_id.return_value = SimpleNamespace(
        id=organization_id, name="Acme"
    )
    users = MagicMock()
    users.get_by_id.return_value = user
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None
    members.create.return_value = member

    app.dependency_overrides[get_repository(InvitationRepo)] = lambda: invitations
    app.dependency_overrides[get_repository(OrganizationRepo)] = lambda: organizations
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.post("/api/v1/invitations/invite-token/accept")

    assert response.status_code == 201, response.json()
    assert response.json()["role"] == "member"
    members.create.assert_called_once()
    invitations.update.assert_called_once()


def test_list_users_scoped_to_shared_organizations(auth_client, current_user_id) -> None:
    organization_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    user = SimpleNamespace(
        id=current_user_id,
        email="test@example.com",
        name="Test",
        created_at=now,
        updated_at=now,
    )
    members = MagicMock()
    members.list_organization_ids_for_user.return_value = [organization_id]
    users = MagicMock()
    users.list_by_organization_ids.return_value = [user]

    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users

    response = auth_client.get("/api/v1/users/")

    assert response.status_code == 200, response.json()
    users.list_by_organization_ids.assert_called_once_with([organization_id])
    users.list.assert_not_called()


def test_get_user_hidden_when_not_in_shared_organization(auth_client) -> None:
    user_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    users = MagicMock()
    users.get_by_id.return_value = SimpleNamespace(
        id=user_id,
        email="other@example.com",
        name="Other",
        created_at=now,
        updated_at=now,
    )
    members = MagicMock()
    members.list_organization_ids_for_user.return_value = [uuid.uuid4()]
    members.user_belongs_to_any.return_value = False

    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = auth_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user_forbidden_for_member(auth_client) -> None:
    response = auth_client.post(
        "/api/v1/users/",
        json={
            "email": "new@example.com",
            "name": "New",
            "password": "Secret123!",
        },
    )

    assert response.status_code == 403


def test_superuser_lists_all_users(superuser_client, current_user_id) -> None:
    now = datetime.now(timezone.utc)
    user = SimpleNamespace(
        id=current_user_id,
        email="admin@example.com",
        name="Admin",
        created_at=now,
        updated_at=now,
    )
    users = MagicMock()
    users.list.return_value = [user]
    members = MagicMock()

    app.dependency_overrides[get_repository(UserRepo)] = lambda: users
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members

    response = superuser_client.get("/api/v1/users/")

    assert response.status_code == 200, response.json()
    users.list.assert_called_once()
    users.list_by_organization_ids.assert_not_called()


def test_protected_route_without_token_returns_401(client) -> None:
    response = client.get("/api/v1/organizations/")
    assert response.status_code == 401


def test_protected_route_with_invalid_token_returns_401(client) -> None:
    response = client.get(
        "/api/v1/organizations/",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401
