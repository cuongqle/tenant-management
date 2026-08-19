import uuid
from typing import Any, Protocol

from fastapi import HTTPException, status

from app.api.deps import CurrentPrincipal


class MembershipLookup(Protocol):
    def get_by_organization_and_user(
        self, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> Any | None: ...

    def list_organization_ids_for_user(self, user_id: uuid.UUID) -> list[uuid.UUID]: ...

    def user_belongs_to_any(
        self,
        user_id: uuid.UUID,
        organization_ids: list[uuid.UUID],
    ) -> bool: ...


def tenant_ids_or_all(
    members: MembershipLookup,
    principal: CurrentPrincipal,
) -> list[uuid.UUID] | None:
    if principal.is_superuser:
        return None
    return members.list_organization_ids_for_user(principal.id)


def require_organization_member(
    members: MembershipLookup,
    organization_id: uuid.UUID,
    principal: CurrentPrincipal,
    *,
    detail: str = "Organization not found",
) -> Any:
    if principal.is_superuser:
        return None
    member = members.get_by_organization_and_user(organization_id, principal.id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return member


def require_visible_user(
    members: MembershipLookup,
    principal: CurrentPrincipal,
    user_id: uuid.UUID,
    *,
    detail: str = "User not found",
) -> None:
    if principal.is_superuser or principal.id == user_id:
        return
    organization_ids = members.list_organization_ids_for_user(principal.id)
    if not members.user_belongs_to_any(user_id, organization_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
