import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException

from app.api.auth import login, register
from app.core.config import settings
from app.core.security import hash_password
from app.main import app
from app.repositories._base_ import get_repository
from app.repositories.user import Repository as UserRepo
from app.schemas.auth import LoginRequest, RegisterRequest


def test_login_success_returns_jwt() -> None:
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="admin@example.com",
        password=hash_password("Admin123!"),
    )
    users = MagicMock()
    users.get_by_email.return_value = user

    result = login(LoginRequest(email="admin@example.com", password="Admin123!"), users)

    assert result.token_type == "bearer"
    payload = jwt.decode(
        result.access_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(user.id)
    assert payload["email"] == "admin@example.com"


def test_login_rejects_invalid_credentials() -> None:
    users = MagicMock()
    users.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        login(LoginRequest(email="missing@example.com", password="wrong"), users)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"


def test_login_endpoint_with_dependency_override(client) -> None:
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="admin@example.com",
        password=hash_password("Admin123!"),
    )
    users = MagicMock()
    users.get_by_email.return_value = user
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body


def test_register_success_creates_user_and_returns_jwt() -> None:
    created = SimpleNamespace(
        id=uuid.uuid4(),
        email="new@example.com",
        name="New User",
        password="hashed",
    )
    users = MagicMock()
    users.get_by_email.return_value = None
    users.create.return_value = created

    result = register(
        RegisterRequest(
            email="new@example.com",
            name="New User",
            password="Secret123!",
        ),
        users,
    )

    assert result.token_type == "bearer"
    users.create.assert_called_once()
    created_data = users.create.call_args.args[0]
    assert created_data["email"] == "new@example.com"
    assert created_data["name"] == "New User"
    assert created_data["password"] != "Secret123!"
    payload = jwt.decode(
        result.access_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(created.id)
    assert payload["email"] == "new@example.com"


def test_register_rejects_duplicate_email() -> None:
    users = MagicMock()
    users.get_by_email.return_value = SimpleNamespace(id=uuid.uuid4())

    with pytest.raises(HTTPException) as exc_info:
        register(
            RegisterRequest(email="admin@example.com", password="Secret123!"),
            users,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already registered"
    users.create.assert_not_called()


def test_register_endpoint_with_dependency_override(client) -> None:
    created = SimpleNamespace(
        id=uuid.uuid4(),
        email="join@example.com",
        name="Join",
        password="hashed",
    )
    users = MagicMock()
    users.get_by_email.return_value = None
    users.create.return_value = created
    app.dependency_overrides[get_repository(UserRepo)] = lambda: users

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "join@example.com",
            "name": "Join",
            "password": "Secret123!",
        },
    )

    assert response.status_code == 201, response.json()
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
