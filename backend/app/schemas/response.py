from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    errors: list[str] | None = None


class HealthData(BaseModel):
    status: str = Field(..., examples=["ok"])


def success_response(*, data: T, message: str = "Success") -> ApiResponse[T]:
    return ApiResponse(success=True, message=message, data=data)


def error_response(
    *,
    message: str,
    errors: list[str] | None = None,
) -> ApiResponse[None]:
    return ApiResponse(success=False, message=message, errors=errors)