import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Invitation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: str
    token: str
    expires_at: datetime
    accepted_at: datetime | None
    invited_by_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = Field(default="member", min_length=1, max_length=50)


class InvitationPreview(BaseModel):
    organization_id: uuid.UUID
    organization_name: str
    email: EmailStr
    role: str
    expires_at: datetime
    accepted: bool
    expired: bool
