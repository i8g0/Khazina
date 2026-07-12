from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, SmallInteger, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.organization import Organization
    from app.db.models.recommendation import Recommendation
    from app.db.models.repository import FinancialFile
    from app.db.models.reporting import Report
    from app.db.models.risk import Risk
    from app.db.models.waste import WasteCategoryBreakdown


class Department(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("organization_id", "name_ar", name="uq_departments_org_name_ar"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    organization: Mapped[Organization] = relationship(
        back_populates="departments",
    )
    financial_files: Mapped[list[FinancialFile]] = relationship(
        back_populates="department",
    )
    waste_category_breakdowns: Mapped[list[WasteCategoryBreakdown]] = relationship(
        back_populates="department",
    )
    risks: Mapped[list[Risk]] = relationship(
        back_populates="department",
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="department",
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="department",
    )
