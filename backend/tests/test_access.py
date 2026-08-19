import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.access import require_organization_member, require_visible_user
from app.api.deps import CurrentPrincipal


def test_require_organization_member_returns_membership() -> None:
    organization_id = uuid.uuid4()
    principal = CurrentPrincipal(
        id=uuid.uuid4(),
        email="test@example.com",
        is_superuser=False,
    )
    membership = object()
    members = MagicMock()
    members.get_by_organization_and_user.return_value = membership

    assert (
        require_organization_member(members, organization_id, principal) is membership
    )
    members.get_by_organization_and_user.assert_called_once_with(
        organization_id, principal.id
    )


def test_require_organization_member_raises_when_missing() -> None:
    principal = CurrentPrincipal(
        id=uuid.uuid4(),
        email="test@example.com",
        is_superuser=False,
    )
    members = MagicMock()
    members.get_by_organization_and_user.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        require_organization_member(
            members,
            uuid.uuid4(),
            principal,
            detail="Project not found",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_require_organization_member_skips_for_superuser() -> None:
    principal = CurrentPrincipal(
        id=uuid.uuid4(),
        email="admin@example.com",
        is_superuser=True,
    )
    members = MagicMock()

    assert require_organization_member(members, uuid.uuid4(), principal) is None
    members.get_by_organization_and_user.assert_not_called()


def test_require_visible_user_allows_self() -> None:
    user_id = uuid.uuid4()
    principal = CurrentPrincipal(
        id=user_id,
        email="test@example.com",
        is_superuser=False,
    )
    members = MagicMock()

    require_visible_user(members, principal, user_id)
    members.user_belongs_to_any.assert_not_called()


def test_require_visible_user_hides_outsiders() -> None:
    principal = CurrentPrincipal(
        id=uuid.uuid4(),
        email="test@example.com",
        is_superuser=False,
    )
    members = MagicMock()
    members.list_organization_ids_for_user.return_value = [uuid.uuid4()]
    members.user_belongs_to_any.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        require_visible_user(members, principal, uuid.uuid4())

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
