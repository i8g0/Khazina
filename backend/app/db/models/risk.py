from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import EnterpriseRiskLifecycleStatus, RiskStatus

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.organization import Organization, ReportingPeriod
    from app.db.models.recommendation import Recommendation
    from app.db.models.risk_analysis import RiskCategory, RiskFinding
    from app.db.models.risk_event import RiskEvent
    from app.db.models.snapshot import FinancialSnapshot


class Risk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "risks"
    __table_args__ = (
        CheckConstraint(
            "score >= 0 AND score <= 100",
            name="ck_risks_score_range",
        ),
        CheckConstraint(
            "source_type IS NULL OR source_type IN ('manual', 'engine', 'import')",
            name="ck_risks_source_type",
        ),
        CheckConstraint(
            "lifecycle_status IN ('accepted', 'monitoring', 'mitigated', 'resolved', 'archived')",
            name="ck_risks_lifecycle_status",
        ),
        Index("ix_risks_org_status_priority", "organization_id", "status", "priority"),
        Index("ix_risks_org_department", "organization_id", "department_id"),
        Index("ix_risks_org_category_status", "organization_id", "category_code", "status"),
        Index("ix_risks_org_lifecycle", "organization_id", "lifecycle_status"),
        Index("ix_risks_source_finding_id", "source_finding_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    reporting_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reporting_periods.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=RiskStatus.ACTIVE.value,
    )
    lifecycle_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=EnterpriseRiskLifecycleStatus.ACCEPTED.value,
    )
    owner_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    likelihood: Mapped[str | None] = mapped_column(String(50), nullable=True)
    impact: Mapped[str | None] = mapped_column(String(50), nullable=True)
    category_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_code: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("risk_categories.code", ondelete="RESTRICT"),
        nullable=True,
    )
    source_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_analysis_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_finding_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk_findings.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    detected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_updated_at: Mapped[date] = mapped_column(Date, nullable=False)

    organization: Mapped[Organization] = relationship(
        back_populates="risks",
    )
    department: Mapped[Department | None] = relationship(
        back_populates="risks",
    )
    reporting_period: Mapped[ReportingPeriod | None] = relationship(
        back_populates="risks",
    )
    category: Mapped[RiskCategory | None] = relationship(
        foreign_keys=[category_code],
    )
    source_analysis_run: Mapped[AnalysisRun | None] = relationship(
        foreign_keys=[source_analysis_run_id],
    )
    source_finding: Mapped[RiskFinding | None] = relationship(
        foreign_keys=[source_finding_id],
    )
    source_snapshot: Mapped[FinancialSnapshot | None] = relationship(
        foreign_keys=[source_snapshot_id],
    )
    mitigation_plans: Mapped[list[RiskMitigationPlan]] = relationship(
        back_populates="risk",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="risk",
    )
    events: Mapped[list[RiskEvent]] = relationship(
        back_populates="risk",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RiskMitigationPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "risk_mitigation_plans"

    risk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risks.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    owner_label: Mapped[str | None] = mapped_column(String(200), nullable=True)

    risk: Mapped[Risk] = relationship(
        back_populates="mitigation_plans",
    )
