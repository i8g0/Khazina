from fastapi import APIRouter

from app.schemas.response import ApiResponse, HealthData, success_response

router = APIRouter()


@router.get("/health", response_model=ApiResponse[HealthData])
def health_check() -> ApiResponse[HealthData]:
    return success_response(
        data=HealthData(status="ok"),
        message="Service is healthy",
    )