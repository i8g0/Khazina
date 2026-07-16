"""HTTP request logging middleware (Sprint D5)."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.observability.structured_log import log_pipeline_event

logger = get_logger(__name__)

_SKIP_PATHS = frozenset({"/api/v1/health", "/api/v1/ai/health"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request method, path, status, and duration without response body noise."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            log_pipeline_event(
                logger,
                "http_request",
                level=40,
                status="failed",
                duration_ms=duration_ms,
                message=f"{request.method} {request.url.path}",
            )
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_pipeline_event(
            logger,
            "http_request",
            status="completed" if response.status_code < 400 else "failed",
            duration_ms=duration_ms,
            message=f"{request.method} {request.url.path} -> {response.status_code}",
        )
        return response
