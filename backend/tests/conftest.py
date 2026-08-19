import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.repositories._base_ import get_repository
from app.repositories.organization_member import Repository as OrganizationMemberRepo


@pytest.fixture
def current_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client: TestClient, current_user_id: uuid.UUID) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(current_user_id),
        "email": "test@example.com",
        "is_superuser": False,
    }
    members = MagicMock()
    members.get_by_organization_and_user.return_value = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=current_user_id,
        role="member",
    )
    members.list_organization_ids_for_user.return_value = []
    members.list_by_organization_ids.return_value = []
    app.dependency_overrides[get_repository(OrganizationMemberRepo)] = lambda: members
    return client


@pytest.fixture
def superuser_client(auth_client: TestClient, current_user_id: uuid.UUID) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(current_user_id),
        "email": "admin@example.com",
        "is_superuser": True,
    }
    return auth_client
