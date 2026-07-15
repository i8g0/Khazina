"""Organization Settings Document persistence model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization


class OrganizationSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organization_settings"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_organization_settings_org_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    settings_document: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    organization: Mapped[Organization] = relationship(
        back_populates="settings_document",
    )
