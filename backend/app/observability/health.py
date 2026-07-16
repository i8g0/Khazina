"""Application health probes (Sprint D5)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError

from app.ai.health import check_ollama_health
from app.db.session import check_database_connection


@dataclass(frozen=True, slots=True)
class ComponentHealth:
    status: str
    message: str | None = None


@dataclass(frozen=True, slots=True)
class SystemHealthResult:
    status: str
    backend: ComponentHealth
    database: ComponentHealth
    ai: ComponentHealth


def check_system_health() -> SystemHealthResult:
    """Aggregate backend, database, and AI service visibility."""
    backend = ComponentHealth(status="ok", message="API process is running")

    try:
        check_database_connection()
        database = ComponentHealth(status="ok", message="Database connection verified")
    except SQLAlchemyError as exc:
        database = ComponentHealth(
            status="unavailable",
            message=f"Database unavailable: {exc}",
        )

    ai_result = check_ollama_health()
    ai = ComponentHealth(
        status=ai_result.status,
        message=ai_result.message,
    )

    statuses = {backend.status, database.status, ai.status}
    if database.status != "ok":
        overall = "unavailable"
    elif ai.status != "ok":
        overall = "degraded"
    elif statuses == {"ok"}:
        overall = "ok"
    else:
        overall = "degraded"

    return SystemHealthResult(
        status=overall,
        backend=backend,
        database=database,
        ai=ai,
    )
