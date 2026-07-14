"""AI Recommendation API schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.analysis import AnalysisRunResponse
from app.schemas.common import SchemaBase
from app.schemas.recommendation import RecommendationResponse


class WasteAiRecommendationsGenerateRequest(SchemaBase):
    analysis_run_id: UUID
    regenerate: bool = False


class WasteAiRecommendationsGenerateResponse(SchemaBase):
    analysis_run: AnalysisRunResponse
    recommendation_count: int
    ai_insights: dict[str, Any]
    recommendations: list[RecommendationResponse]
