"""Scenario Analysis API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.analysis import AnalysisRunResponse
from app.schemas.common import SchemaBase
from app.schemas.simulation import SimulationRunResponse


class ScenarioExecuteRequest(SchemaBase):
    source_file_id: UUID
    source_snapshot_id: UUID | None = None
    snapshot_version: int | None = Field(None, ge=1)
    baseline_analysis_run_id: UUID | None = None
    reporting_period_id: UUID | None = None


class ScenarioExecuteResponse(SchemaBase):
    analysis_run: AnalysisRunResponse
    simulation_run: SimulationRunResponse
    facts_contract_version: str
    engine_id: str
    engine_version: str
    snapshot_id: UUID
    snapshot_version: int
    archetype: str
