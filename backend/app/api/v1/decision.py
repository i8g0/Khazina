"""Decision Engine REST endpoints (Sprint 6.3)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import DecisionServiceDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.analysis import AnalysisRunResponse
from app.schemas.decision import WasteDecisionExecuteRequest, WasteDecisionExecuteResponse
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/decisions",
    tags=["decisions"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/waste/execute",
    response_model=ApiResponse[WasteDecisionExecuteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Execute waste decision from Financial Snapshot",
)
def execute_waste_decision(
    organization_id: UUID,
    body: WasteDecisionExecuteRequest,
    service: DecisionServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[WasteDecisionExecuteResponse]:
    outcome = service.execute_waste_analysis(
        organization_id,
        title=body.title,
        source_file_id=body.source_file_id,
        source_snapshot_id=body.source_snapshot_id,
        snapshot_version=body.snapshot_version,
        reporting_period_id=body.reporting_period_id,
    )
    return success_response(
        data=WasteDecisionExecuteResponse(
            analysis_run=AnalysisRunResponse.model_validate(outcome.analysis_run),
            facts_contract_version=outcome.facts_contract.contract_version,
            engine_id=outcome.facts_contract.engine_id,
            engine_version=outcome.facts_contract.engine_version,
            snapshot_id=outcome.snapshot.id,
            snapshot_version=outcome.snapshot.snapshot_version,
        ),
        message="Waste decision executed",
    )
