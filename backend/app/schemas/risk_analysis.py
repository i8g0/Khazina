"""Risk analysis API schemas (Sprint 9.3)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.analysis import AnalysisRunResponse
from app.schemas.common import SchemaBase, TimestampResponse


class RiskAnalysisExecuteRequest(SchemaBase):
    title: str = Field(..., min_length=1, max_length=500)
    source_file_id: UUID
    source_snapshot_id: UUID | None = None
    snapshot_version: int | None = Field(None, ge=1)
    reporting_period_id: UUID | None = None


class RiskAnalysisResultSummary(SchemaBase):
    result_id: UUID
    total_findings: int = Field(..., ge=0)
    high_priority_count: int = Field(..., ge=0)
    medium_priority_count: int = Field(..., ge=0)
    low_priority_count: int = Field(..., ge=0)
    overall_posture_level: str
    top_category_code: str | None = None
    facts_contract_version: str
    source_snapshot_id: UUID | None = None


class RiskAnalysisExecuteResponse(SchemaBase):
    analysis_run: AnalysisRunResponse
    result_summary: RiskAnalysisResultSummary
    facts_contract_version: str
    engine_id: str
    engine_version: str
    snapshot_id: UUID
    snapshot_version: int


class RiskAnalysisRunDetailResponse(SchemaBase):
    analysis_run: AnalysisRunResponse
    result_summary: RiskAnalysisResultSummary | None = None


class RiskAnalysisResultResponse(TimestampResponse):
    id: UUID
    analysis_run_id: UUID
    organization_id: UUID
    total_findings: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    overall_posture_level: str
    top_category_code: str | None
    facts_contract_version: str
    source_snapshot_id: UUID | None


class RiskFindingResponse(TimestampResponse):
    id: UUID
    analysis_run_id: UUID
    organization_id: UUID
    category_code: str
    name: str
    description: str
    likelihood: str
    impact: str
    score: int
    priority: str
    detection_rule_id: str
    evidence: dict[str, Any]
    finding_status: str
    promoted_risk_id: UUID | None
    department_id: UUID | None
