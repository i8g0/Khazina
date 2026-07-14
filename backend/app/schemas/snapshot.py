"""Financial Snapshot API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampResponse
from app.schemas.financial import FinancialFileResponse


class FinancialSnapshotResponse(TimestampResponse):
    id: UUID
    financial_file_id: UUID
    import_record_id: UUID | None
    organization_id: UUID
    reporting_period_id: UUID | None
    snapshot_version: int = Field(..., ge=1)
    parser_version: str
    schema_version: str
    record_count: int | None
    materialized_at: datetime


class FinancialSnapshotDetailResponse(FinancialSnapshotResponse):
    payload: dict[str, Any]


class UploadIngestionResponse(SchemaBase):
    financial_file: FinancialFileResponse
    financial_snapshot: FinancialSnapshotResponse | None
    quality_snapshot_id: UUID | None
    import_record_id: UUID | None
