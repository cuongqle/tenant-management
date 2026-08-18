import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID

from ._base_ import Base, TimestampMixin, UUIDPrimaryKey

class Project(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="projects")
    environments = relationship("Environment", back_populates="project", cascade="all, delete-orphan")