from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.schemas.response import error_response
from app.services.exceptions import (
    AuthenticationError,
    BusinessRuleViolationError,
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    OwnershipViolationError,
    ResourceNotFoundError,
    ServiceError,
)

logger = get_logger(__name__)

_SERVICE_EXCEPTION_STATUS: dict[type[ServiceError], int] = {
    ResourceNotFoundError: 404,
    BusinessValidationError: 400,
    DuplicateResourceError: 409,
    OwnershipViolationError: 403,
    InvalidStateError: 409,
    BusinessRuleViolationError: 409,
    AuthenticationError: 401,
}


def _status_for_service_error(exc: ServiceError) -> int:
    for exc_type, status_code in _SERVICE_EXCEPTION_STATUS.items():
        if isinstance(exc, exc_type):
            return status_code
    return 500


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=_status_for_service_error(exc),
        content=error_response(message=str(exc)).model_dump(),
    )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.message, errors=exc.errors).model_dump(),
    )


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    errors = [str(exc.detail)] if exc.detail else None
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message="Request failed", errors=errors).model_dump(),
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_response(message="Validation failed", errors=errors).model_dump(),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    errors = [str(exc)] if settings.debug else None
    message = str(exc) if settings.debug else "Internal server error"
    return JSONResponse(
        status_code=500,
        content=error_response(message=message, errors=errors).model_dump(),
    )