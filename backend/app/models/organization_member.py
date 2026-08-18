import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ._base_ import Base, TimestampMixin, UUIDPrimaryKey

class OrganizationMember(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "organization_members"

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="members")
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="organizations")
    role: Mapped[str] = mapped_column(String(50), nullable=False,default="member")