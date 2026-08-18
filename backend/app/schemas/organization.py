import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Organization(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    address: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    country: str | None
    phone: str | None
    email: str | None
    website: str | None
    industry: str | None
    created_at: datetime
    updated_at: datetime


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=255)
    zip_code: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=255)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=255)
    zip_code: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=255)
