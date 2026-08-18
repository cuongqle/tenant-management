from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base_ import Base, TimestampMixin, UUIDPrimaryKey

if TYPE_CHECKING:
    from .organization_member import OrganizationMember
    from .project import Project


class Organization(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(255), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)

    members: Mapped[list[OrganizationMember]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list[Project]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
