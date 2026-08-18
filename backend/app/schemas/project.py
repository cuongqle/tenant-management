import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    start_date: datetime
    end_date: datetime | None
    status: str
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    start_date: datetime
    end_date: datetime | None = None
    status: str = Field(min_length=1, max_length=255)
    organization_id: uuid.UUID


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = Field(default=None, min_length=1, max_length=255)
    organization_id: uuid.UUID | None = None


class ProjectAssign(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    start_date: datetime
    end_date: datetime | None = None
    status: str = Field(default="active", min_length=1, max_length=255)
