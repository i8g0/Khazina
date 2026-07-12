from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.organization import Organization
    from app.db.models.risk import Risk
    from app.db.models.simulation import SimulationRun


class Recommendation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recommendations"
    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(analysis_run_id, risk_id, simulation_run_id) <= 1",
            name="ck_recommendations_at_most_one_source_fk",
        ),
        Index(
            "ix_recommendations_org_domain_priority",
            "organization_id",
            "domain_source",
            "priority",
        ),
        Index(
            "ix_recommendations_dashboard_featured",
            "organization_id",
            postgresql_where=text("is_dashboard_featured IS TRUE"),
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    domain_source: Mapped[str] = mapped_column(String(50), nullable=False)
    external_ref: Mapped[str | None] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_savings_amount: Mapped[float | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    analysis_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    risk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risks.id", ondelete="SET NULL"),
        nullable=True,
    )
    simulation_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_dashboard_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    source_context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    organization: Mapped[Organization] = relationship(
        back_populates="recommendations",
    )
    department: Mapped[Department | None] = relationship(
        back_populates="recommendations",
    )
    analysis_run: Mapped[AnalysisRun | None] = relationship(
        back_populates="recommendations",
    )
    risk: Mapped[Risk | None] = relationship(
        back_populates="recommendations",
    )
    simulation_run: Mapped[SimulationRun | None] = relationship(
        back_populates="recommendations",
    )
