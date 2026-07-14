"""AI Recommendation Service REST endpoints (Sprint 6.4)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import AiRecommendationServiceDep
from app.api.permissions import RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.schemas.ai_recommendations import (
    WasteAiRecommendationsGenerateRequest,
    WasteAiRecommendationsGenerateResponse,
)
from app.schemas.recommendation import RecommendationResponse
from app.schemas.analysis import AnalysisRunResponse
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/ai-recommendations",
    tags=["ai-recommendations"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/waste/generate",
    response_model=ApiResponse[WasteAiRecommendationsGenerateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate waste AI recommendations from completed decision run",
)
def generate_waste_ai_recommendations(
    organization_id: UUID,
    body: WasteAiRecommendationsGenerateRequest,
    service: AiRecommendationServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[WasteAiRecommendationsGenerateResponse]:
    outcome = service.generate_waste_recommendations(
        organization_id,
        body.analysis_run_id,
        regenerate=body.regenerate,
    )
    return success_response(
        data=WasteAiRecommendationsGenerateResponse(
            analysis_run=AnalysisRunResponse.model_validate(outcome.analysis_run),
            recommendation_count=len(outcome.recommendations),
            ai_insights=outcome.ai_insights,
            recommendations=[
                RecommendationResponse.model_validate(rec)
                for rec in outcome.recommendations
            ],
        ),
        message="Waste AI recommendations generated",
    )
