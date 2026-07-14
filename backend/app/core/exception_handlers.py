from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.schemas.response import error_response
from app.decision.exceptions import SnapshotAdapterError
from app.reports.exceptions import ReportBuilderError
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

_SENSITIVE_FIELD_NAMES = frozenset({"password", "password_hash"})


def _status_for_service_error(exc: ServiceError) -> int:
    for exc_type, status_code in _SERVICE_EXCEPTION_STATUS.items():
        if isinstance(exc, exc_type):
            return status_code
    return 500


def _service_error_message(exc: ServiceError) -> str:
    if isinstance(exc, AuthenticationError):
        return "Invalid email or password"
    if isinstance(exc, BusinessRuleViolationError) and not settings.debug:
        return "The operation violates a data integrity rule"
    return str(exc)


def _http_error_message(exc: HTTPException) -> tuple[str, list[str] | None]:
    if settings.debug:
        errors = [str(exc.detail)] if exc.detail else None
        return "Request failed", errors
    if exc.status_code == 401:
        return "Authentication failed", None
    if exc.status_code == 403:
        return "Forbidden", None
    return "Request failed", None


def _format_validation_errors(exc: RequestValidationError) -> list[str]:
    errors: list[str] = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error["loc"])
        if not settings.debug and any(
            str(part) in _SENSITIVE_FIELD_NAMES for part in error["loc"]
        ):
            errors.append(f"{loc}: invalid value")
            continue
        errors.append(f"{loc}: {error['msg']}")
    return errors


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SnapshotAdapterError, snapshot_adapter_error_handler)
    app.add_exception_handler(AiRecommendationError, ai_recommendation_error_handler)
    app.add_exception_handler(ReportBuilderError, report_builder_error_handler)
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def snapshot_adapter_error_handler(
    _: Request, exc: SnapshotAdapterError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_response(
            message=exc.message,
            errors=[exc.error_code],
        ).model_dump(),
    )


async def ai_recommendation_error_handler(
    _: Request, exc: AiRecommendationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_response(
            message=exc.message,
            errors=[exc.error_code],
        ).model_dump(),
    )


async def report_builder_error_handler(
    _: Request, exc: ReportBuilderError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_response(
            message=exc.message,
            errors=[exc.code],
        ).model_dump(),
    )


async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=_status_for_service_error(exc),
        content=error_response(message=_service_error_message(exc)).model_dump(),
    )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    if settings.debug or exc.status_code < 500:
        message = exc.message
        errors = exc.errors
    else:
        message = "Internal server error"
        errors = None
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=message, errors=errors).model_dump(),
    )


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message, errors = _http_error_message(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=message, errors=errors).model_dump(),
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_response(
            message="Validation failed",
            errors=_format_validation_errors(exc),
        ).model_dump(),
    )


async def sqlalchemy_error_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error")
    message = "Internal server error"
    errors = [str(exc)] if settings.debug else None
    if settings.debug:
        message = str(exc)
    return JSONResponse(
        status_code=500,
        content=error_response(message=message, errors=errors).model_dump(),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    errors = [str(exc)] if settings.debug else None
    message = str(exc) if settings.debug else "Internal server error"
    return JSONResponse(
        status_code=500,
        content=error_response(message=message, errors=errors).model_dump(),
    )
