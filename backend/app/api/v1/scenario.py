"""Scenario Analysis REST endpoints (Sprint 6.5)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import ScenarioServiceDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.analysis import AnalysisRunResponse
from app.schemas.response import ApiResponse, success_response
from app.schemas.scenario import ScenarioExecuteRequest, ScenarioExecuteResponse
from app.schemas.simulation import SimulationRunResponse

router = APIRouter(
    prefix="/organizations/{organization_id}/simulation",
    tags=["simulation"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/scenarios/{scenario_id}/execute",
    response_model=ApiResponse[ScenarioExecuteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Execute scenario analysis against a Financial Snapshot",
)
def execute_scenario(
    organization_id: UUID,
    scenario_id: UUID,
    body: ScenarioExecuteRequest,
    service: ScenarioServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[ScenarioExecuteResponse]:
    outcome = service.execute_scenario(
        organization_id,
        scenario_id,
        source_file_id=body.source_file_id,
        source_snapshot_id=body.source_snapshot_id,
        snapshot_version=body.snapshot_version,
        baseline_analysis_run_id=body.baseline_analysis_run_id,
        reporting_period_id=body.reporting_period_id,
        initiating_user_id=current_user.id,
    )
    provenance = (outcome.analysis_run.runtime_metadata or {}).get(
        "scenario_provenance", {}
    )
    return success_response(
        data=ScenarioExecuteResponse(
            analysis_run=AnalysisRunResponse.model_validate(outcome.analysis_run),
            simulation_run=SimulationRunResponse.model_validate(outcome.simulation_run),
            facts_contract_version=outcome.facts_contract.contract_version,
            engine_id=outcome.facts_contract.engine_id,
            engine_version=outcome.facts_contract.engine_version,
            snapshot_id=outcome.snapshot.id,
            snapshot_version=outcome.snapshot.snapshot_version,
            archetype=str(provenance.get("archetype", "")),
        ),
        message="Scenario executed",
    )
