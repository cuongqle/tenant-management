import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Environment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class EnvironmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    project_id: uuid.UUID


class EnvironmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    project_id: uuid.UUID | None = None


class EnvironmentAssign(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
