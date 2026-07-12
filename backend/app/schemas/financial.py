"""Financial data repository API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampResponse


class FinancialFileCreate(SchemaBase):
    file_name: str = Field(..., min_length=1, max_length=500)
    upload_source: str = Field("repository", max_length=50)
    department_id: UUID | None = None
    reporting_period_id: UUID | None = None
    storage_path: str | None = Field(None, max_length=1000)
    size_bytes: int | None = Field(None, ge=0)
    size_display: str | None = Field(None, max_length=50)
    mime_type: str | None = Field(None, max_length=100)
    file_metadata: dict[str, Any] | None = None


class FinancialFileResponse(SchemaBase):
    id: UUID
    organization_id: UUID
    department_id: UUID | None
    reporting_period_id: UUID | None
    file_name: str
    storage_path: str | None
    size_bytes: int | None
    size_display: str | None
    mime_type: str | None
    processing_status: str
    upload_source: str
    uploaded_at: datetime
    file_metadata: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class CompleteProcessingRequest(SchemaBase):
    record_count: int | None = Field(None, ge=0)


class FailProcessingRequest(SchemaBase):
    error_message: str = Field(..., min_length=1)


class ImportRecordResponse(TimestampResponse):
    id: UUID
    financial_file_id: UUID
    imported_at: datetime
    record_count: int | None
    status: str
    error_message: str | None


class DataQualityCheckInput(SchemaBase):
    check_name: str = Field(..., min_length=1, max_length=200)
    result_percent: float = Field(..., ge=0, le=100)
    details: str | None = None
    display_order: int = Field(0, ge=0)


class DataQualitySnapshotCreate(SchemaBase):
    overall_score: float | None = Field(None, ge=0, le=100)
    reporting_period_id: UUID | None = None
    checks: list[DataQualityCheckInput] | None = None


class DataQualityCheckResponse(TimestampResponse):
    id: UUID
    snapshot_id: UUID
    check_name: str
    result_percent: float
    details: str | None
    display_order: int


class DataQualitySnapshotResponse(TimestampResponse):
    id: UUID
    organization_id: UUID
    reporting_period_id: UUID | None
    overall_score: float | None
    evaluated_at: datetime
