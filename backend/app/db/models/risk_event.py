"""Enterprise risk governance audit events (Sprint 9.4)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.risk import Risk
    from app.db.models.user import User


class RiskEvent(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "risk_events"
    __table_args__ = (
        Index("ix_risk_events_risk_created", "risk_id", "created_at"),
        Index(
            "ix_risk_events_org_type_created",
            "organization_id",
            "event_type",
            "created_at",
        ),
    )

    risk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risks.id", ondelete="CASCADE"),
        nullable=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    risk: Mapped[Risk | None] = relationship(back_populates="events")
    organization: Mapped[Organization] = relationship()
    actor: Mapped[User | None] = relationship()
