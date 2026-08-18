from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base_ import Base, TimestampMixin, UUIDPrimaryKey

if TYPE_CHECKING:
    from .organization_member import OrganizationMember


class User(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    organizations: Mapped[list[OrganizationMember]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
