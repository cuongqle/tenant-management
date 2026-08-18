import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import User


class OrganizationMember(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    created_at: datetime
    updated_at: datetime


class OrganizationMemberCreate(BaseModel):
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: str = Field(default="member", min_length=1, max_length=50)


class OrganizationMemberUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=1, max_length=50)


class OrganizationMemberAssign(BaseModel):
    user_id: uuid.UUID
    role: str = Field(default="member", min_length=1, max_length=50)


class OrganizationMemberDetail(OrganizationMember):
    user: User
