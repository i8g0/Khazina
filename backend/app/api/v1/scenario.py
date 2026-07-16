"""Scenario Analysis REST endpoints (Sprint 6.5)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import AISimulationServiceDep, ScenarioServiceDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.business.facts.contract import CONTRACT_VERSION
from app.db.models.enums import UserRole
from app.schemas.analysis import AnalysisRunResponse
from app.schemas.response import ApiResponse, success_response
from app.schemas.scenario import (
    AISimulationExecuteRequest,
    AISimulationExecuteResponse,
    ScenarioExecuteRequest,
    ScenarioExecuteResponse,
)
from app.schemas.simulation import SimulationRunResponse

router = APIRouter(
    prefix="/organizations/{organization_id}/simulation",
    tags=["simulation"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/ai/execute",
    response_model=ApiResponse[AISimulationExecuteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Execute AI-native simulation from natural language",
)
def execute_ai_simulation(
    organization_id: UUID,
    body: AISimulationExecuteRequest,
    service: AISimulationServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[AISimulationExecuteResponse]:
    outcome = service.execute(
        organization_id,
        user_request=body.user_request,
        source_file_id=body.source_file_id,
        source_snapshot_id=body.source_snapshot_id,
        snapshot_version=body.snapshot_version,
        baseline_analysis_run_id=body.baseline_analysis_run_id,
        reporting_period_id=body.reporting_period_id,
        initiating_user_id=current_user.id,
    )
    metadata = outcome.analysis_run.runtime_metadata or {}
    return success_response(
        data=AISimulationExecuteResponse(
            analysis_run=AnalysisRunResponse.model_validate(outcome.analysis_run),
            simulation_run=SimulationRunResponse.model_validate(outcome.simulation_run),
            user_request=outcome.user_request,
            interpreted_scenario=metadata.get(
                "interpreted_scenario", outcome.interpreted_scenario.to_dict()
            ),
            ai_explanation=metadata.get(
                "ai_explanation", outcome.explanation.to_dict()
            ),
            facts_contract_version=CONTRACT_VERSION,
            engine_id="scenario_ai_v1",
            engine_version="1.0.0",
            snapshot_id=outcome.snapshot.id,
            snapshot_version=outcome.snapshot.snapshot_version,
        ),
        message="AI simulation executed",
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
