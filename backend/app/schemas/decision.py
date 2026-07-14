"""Decision Engine API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.analysis import AnalysisRunResponse
from app.schemas.common import SchemaBase


class WasteDecisionExecuteRequest(SchemaBase):
    title: str = Field(..., min_length=1, max_length=500)
    source_file_id: UUID
    source_snapshot_id: UUID | None = None
    snapshot_version: int | None = Field(None, ge=1)
    reporting_period_id: UUID | None = None


class WasteDecisionExecuteResponse(SchemaBase):
    analysis_run: AnalysisRunResponse
    facts_contract_version: str
    engine_id: str
    engine_version: str
    snapshot_id: UUID
    snapshot_version: int
