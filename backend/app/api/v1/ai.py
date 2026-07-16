"""AI infrastructure REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.ai.health import check_ai_provider_health
from app.api.deps import AIProviderDep
from app.schemas.ai import AiHealthData
from app.schemas.response import ApiResponse, success_response

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get(
    "/health",
    response_model=ApiResponse[AiHealthData],
    status_code=status.HTTP_200_OK,
    summary="Check AI provider connectivity",
)
def ai_health(provider: AIProviderDep) -> ApiResponse[AiHealthData]:
    result = check_ai_provider_health(provider)
    data = AiHealthData(
        status=result.status,
        provider=result.provider,
        provider_reachable=result.provider_reachable,
        ollama_reachable=result.ollama_reachable,
        configured_model=result.configured_model,
        message=result.message,
    )
    message = (
        "AI infrastructure is healthy"
        if result.provider_reachable
        else "AI infrastructure is unavailable"
    )
    return success_response(data=data, message=message)
