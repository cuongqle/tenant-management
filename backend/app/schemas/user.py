import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str | None
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)
