"""Risk analysis persistence models (Sprint 9.3)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from app.db.models.enums import RiskFindingStatus

if TYPE_CHECKING:
    from app.db.models.analysis import AnalysisRun
    from app.db.models.department import Department
    from app.db.models.organization import Organization
    from app.db.models.risk import Risk
    from app.db.models.snapshot import FinancialSnapshot


class RiskCategory(Base, CreatedAtMixin):
    """Seeded taxonomy — stable ``code`` primary key."""

    __tablename__ = "risk_categories"
    __table_args__ = (
        Index("ix_risk_categories_active_sort", "is_active", "sort_order"),
    )

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    label_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    label_en: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("true")
    )
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    findings: Mapped[list[RiskFinding]] = relationship(
        back_populates="category",
    )


class RiskAnalysisResult(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "risk_analysis_results"
    __table_args__ = (
        UniqueConstraint(
            "analysis_run_id",
            name="uq_risk_analysis_results_analysis_run_id",
        ),
        Index(
            "ix_risk_analysis_results_org_created",
            "organization_id",
            "created_at",
        ),
    )

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    total_findings: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    high_priority_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    medium_priority_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    low_priority_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    overall_posture_level: Mapped[str] = mapped_column(String(30), nullable=False)
    top_category_code: Mapped[str | None] = mapped_column(
        String(50),
        ForeignKey("risk_categories.code", ondelete="RESTRICT"),
        nullable=True,
    )
    facts_contract_version: Mapped[str] = mapped_column(String(20), nullable=False)
    source_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )

    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="risk_analysis_result",
    )
    organization: Mapped[Organization] = relationship()
    top_category: Mapped[RiskCategory | None] = relationship(
        foreign_keys=[top_category_code],
    )
    source_snapshot: Mapped[FinancialSnapshot | None] = relationship()


class RiskFinding(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "risk_findings"
    __table_args__ = (
        CheckConstraint(
            "score >= 0 AND score <= 100",
            name="ck_risk_findings_score_range",
        ),
        CheckConstraint(
            "finding_status IN ('detected', 'under_review', 'reviewed', 'promoted', 'dismissed')",
            name="ck_risk_findings_status",
        ),
        Index("ix_risk_findings_run_priority", "analysis_run_id", "priority"),
        Index(
            "ix_risk_findings_org_status_priority",
            "organization_id",
            "finding_status",
            "priority",
        ),
        Index("ix_risk_findings_promoted_risk_id", "promoted_risk_id"),
    )

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("risk_categories.code", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    likelihood: Mapped[str] = mapped_column(String(50), nullable=False)
    impact: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    detection_rule_id: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    finding_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=RiskFindingStatus.DETECTED.value,
    )
    promoted_risk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risks.id", ondelete="SET NULL"),
        nullable=True,
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )

    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="risk_findings",
    )
    organization: Mapped[Organization] = relationship()
    category: Mapped[RiskCategory] = relationship(back_populates="findings")
    promoted_risk: Mapped[Risk | None] = relationship(
        foreign_keys=[promoted_risk_id],
    )
    department: Mapped[Department | None] = relationship()
