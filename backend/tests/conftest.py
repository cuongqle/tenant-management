import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid.uuid4()),
        "email": "test@example.com",
    }
    return client
