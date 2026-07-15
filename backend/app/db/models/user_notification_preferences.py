"""Per-user notification preference persistence (Sprint 6.9)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.user import User


class UserNotificationPreferences(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_notification_preferences"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_user_notification_preferences_org_user",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    preferences_document: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    organization: Mapped[Organization] = relationship()
    user: Mapped[User] = relationship()
