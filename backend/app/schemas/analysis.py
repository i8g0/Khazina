"""Analysis run API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class AnalysisRunCreate(SchemaBase):
    analysis_type: str = Field(..., max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    source_file_id: UUID | None = None
    reporting_period_id: UUID | None = None
    runtime_metadata: dict[str, Any] | None = None


class AnalysisRunResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    reporting_period_id: UUID | None
    source_file_id: UUID | None
    analysis_type: str
    title: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    runtime_metadata: dict[str, Any] | None


class FailAnalysisRunRequest(SchemaBase):
    failure_details: dict[str, Any] | None = None
