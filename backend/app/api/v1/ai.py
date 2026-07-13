"""AI infrastructure REST endpoints (Sprint 5.1)."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.ai.health import check_ollama_health
from app.api.deps import OllamaClientDep
from app.schemas.ai import AiHealthData
from app.schemas.response import ApiResponse, success_response

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get(
    "/health",
    response_model=ApiResponse[AiHealthData],
    status_code=status.HTTP_200_OK,
    summary="Check Ollama connectivity",
)
def ai_health(client: OllamaClientDep) -> ApiResponse[AiHealthData]:
    result = check_ollama_health(client)
    data = AiHealthData(
        status=result.status,
        ollama_reachable=result.ollama_reachable,
        configured_model=result.configured_model,
        message=result.message,
    )
    message = (
        "AI infrastructure is healthy"
        if result.ollama_reachable
        else "AI infrastructure is unavailable"
    )
    return success_response(data=data, message=message)
