from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization, ReportingPeriod


class TimelineEvent(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "timeline_events"
    __table_args__ = (
        Index("ix_timeline_events_org_event_date", "organization_id", "event_date"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reporting_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    related_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    organization: Mapped[Organization] = relationship(
        back_populates="timeline_events",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="timeline_events",
    )
