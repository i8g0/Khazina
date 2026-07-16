from fastapi import APIRouter

from app.observability.health import check_system_health
from app.schemas.response import ApiResponse, HealthData, success_response

router = APIRouter()


@router.get("/health", response_model=ApiResponse[HealthData])
def health_check() -> ApiResponse[HealthData]:
    result = check_system_health()
    message = "Service is healthy"
    if result.status == "degraded":
        message = "Service is running with degraded dependencies"
    elif result.status == "unavailable":
        message = "Service is unavailable"

    return success_response(
        data=HealthData(
            status=result.status,
            backend={"status": result.backend.status, "message": result.backend.message or ""},
            database={"status": result.database.status, "message": result.database.message or ""},
            ai={"status": result.ai.status, "message": result.ai.message or ""},
        ),
        message=message,
    )
