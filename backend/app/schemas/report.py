"""Executive reporting API schemas."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class ReportCreate(SchemaBase):
    title: str = Field(..., min_length=1, max_length=500)
    report_type: str = Field(..., max_length=50)
    summary: str = Field(..., min_length=1)
    department_id: UUID | None = None
    reporting_period_id: UUID | None = None
    source_file_id: UUID | None = None
    analysis_run_id: UUID | None = None


class ReportUpdate(SchemaBase):
    title: str | None = Field(None, min_length=1, max_length=500)
    summary: str | None = Field(None, min_length=1)


class ReportResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    department_id: UUID | None
    reporting_period_id: UUID | None
    source_file_id: UUID | None
    analysis_run_id: UUID | None
    title: str
    report_type: str
    status: str
    summary: str
    published_at: date | None
