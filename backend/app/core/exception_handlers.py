from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.schemas.response import error_response

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


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