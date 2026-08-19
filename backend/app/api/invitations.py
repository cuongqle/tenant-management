from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, get_or_404
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.user import UserRepository
from app.schemas.invitation import InvitationPreview
from app.schemas.organization_member import OrganizationMemberDetail

router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"],
)


def _preview(invitation, organization) -> InvitationPreview:
    now = datetime.now(UTC)
    return InvitationPreview(
        organization_id=invitation.organization_id,
        organization_name=organization.name,
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        accepted=invitation.accepted_at is not None,
        expired=invitation.expires_at <= now,
    )


@router.get("/{token}")
def preview_invitation(
    token: str,
    invitations: InvitationRepository,
    organizations: OrganizationRepository,
) -> InvitationPreview:
    invitation = invitations.get_by_token(token)
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    organization = get_or_404(
        organizations, invitation.organization_id, detail="Invitation not found"
    )
    return _preview(invitation, organization)


@router.post("/{token}/accept", status_code=status.HTTP_201_CREATED)
def accept_invitation(
    token: str,
    principal: CurrentUser,
    invitations: InvitationRepository,
    organizations: OrganizationRepository,
    members: OrganizationMemberRepository,
    users: UserRepository,
) -> OrganizationMemberDetail:
    invitation = invitations.get_by_token(token)
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    organization = get_or_404(
        organizations, invitation.organization_id, detail="Invitation not found"
    )
    if invitation.accepted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invitation has already been accepted",
        )
    if invitation.expires_at <= datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )
    if principal.email.lower() != invitation.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email",
        )
    user = get_or_404(users, principal.id, detail="User not found")
    existing = members.get_by_organization_and_user(organization.id, user.id)
    if existing is not None:
        invitations.update(invitation, {"accepted_at": datetime.now(UTC)})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this organization",
        )
    member = members.create(
        {
            "organization_id": organization.id,
            "user_id": user.id,
            "role": invitation.role,
        }
    )
    invitations.update(invitation, {"accepted_at": datetime.now(UTC)})
    member.user = user
    return member
