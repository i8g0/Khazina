"""Report binary export persistence (Sprint 6.9)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.reporting import Report


class ReportExport(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "report_exports"
    __table_args__ = (
        UniqueConstraint(
            "report_id",
            "export_format",
            "content_fingerprint",
            "preferences_fingerprint",
            name="uq_report_exports_dedup",
        ),
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    export_format: Mapped[str] = mapped_column(String(16), nullable=False)
    content_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    preferences_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    export_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(1024), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    report: Mapped[Report] = relationship()
