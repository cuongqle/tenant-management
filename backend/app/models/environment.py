import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ._base_ import Base, TimestampMixin, UUIDPrimaryKey

class Environment(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "environments"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="environments")