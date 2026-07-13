"""Authentication REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.response import ApiResponse, success_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
)
def login(
    body: LoginRequest,
    service: AuthServiceDep,
) -> ApiResponse[TokenResponse]:
    token = service.login(email=body.email, password=body.password)
    return success_response(data=token, message="Login successful")
