"""Executive reporting API schemas."""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

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
    has_content: bool = False

    @model_validator(mode="wrap")
    @classmethod
    def include_content_flag(cls, value: Any, handler: Any) -> ReportResponse:
        has_content = False
        if hasattr(value, "content_representation"):
            has_content = bool(value.content_representation)
        result = handler(value)
        if has_content:
            result.has_content = True
        return result


class ReportGenerateRequest(SchemaBase):
    analysis_run_id: UUID
    title: str | None = Field(None, min_length=1, max_length=500)
    department_id: UUID | None = None


class ReportGenerateResponse(SchemaBase):
    report: ReportResponse
    profile: str
    sections_included: list[str]
    export_fingerprint: str


class ReportContentResponse(SchemaBase):
    report_id: UUID
    content: dict[str, Any]


class ReportExportResponse(SchemaBase):
    report_id: UUID
    serialization: str
    fingerprint: str
