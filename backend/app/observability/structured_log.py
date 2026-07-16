"""Structured pipeline logging helpers (Sprint D5)."""

from __future__ import annotations

import logging
from typing import Any

from app.observability.errors import ErrorCategory


def _format_fields(**fields: Any) -> str:
    parts: list[str] = []
    for key in sorted(fields):
        value = fields[key]
        if value is None:
            continue
        parts.append(f"{key}={value}")
    return " | ".join(parts)


def log_pipeline_event(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    stage: str | None = None,
    status: str | None = None,
    duration_ms: float | None = None,
    organization_id: str | None = None,
    analysis_run_id: str | None = None,
    snapshot_id: str | None = None,
    file_id: str | None = None,
    report_id: str | None = None,
    error_category: ErrorCategory | str | None = None,
    message: str | None = None,
    **extra: Any,
) -> None:
    """Emit a single-line structured log entry for pipeline observability."""
    payload = {
        "event": event,
        "stage": stage,
        "status": status,
        "duration_ms": (
            round(duration_ms, 2) if duration_ms is not None else None
        ),
        "organization_id": organization_id,
        "analysis_run_id": analysis_run_id,
        "snapshot_id": snapshot_id,
        "file_id": file_id,
        "report_id": report_id,
        "error_category": (
            error_category.value
            if isinstance(error_category, ErrorCategory)
            else error_category
        ),
        "message": message,
        **extra,
    }
    logger.log(level, _format_fields(**payload))
