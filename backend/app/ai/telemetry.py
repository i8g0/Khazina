"""AI request telemetry — provider routing verification and latency evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from app.core.logging import get_logger

logger = get_logger(__name__)

_lock = Lock()
_records: list[AiRequestRecord] = []


@dataclass(frozen=True, slots=True)
class AiRequestRecord:
    provider: str
    model: str
    endpoint: str
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    task: str | None = None
    recorded_at: datetime | None = None


def record_ai_request(
    *,
    provider: str,
    model: str,
    endpoint: str,
    latency_ms: float,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    task: str | None = None,
) -> AiRequestRecord:
    entry = AiRequestRecord(
        provider=provider,
        model=model,
        endpoint=endpoint,
        latency_ms=round(latency_ms, 2),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        task=task,
        recorded_at=datetime.now(UTC),
    )
    with _lock:
        _records.append(entry)
    logger.info(
        "AI request completed provider=%s model=%s endpoint=%s task=%s latency_ms=%.2f "
        "prompt_tokens=%s completion_tokens=%s",
        provider,
        model,
        endpoint,
        task or "-",
        latency_ms,
        prompt_tokens,
        completion_tokens,
    )
    return entry


def get_ai_request_records() -> tuple[AiRequestRecord, ...]:
    with _lock:
        return tuple(_records)


def clear_ai_request_records() -> None:
    with _lock:
        _records.clear()


def verify_all_cloud_requests(*, expected_model: str) -> tuple[bool, str]:
    """Return whether every recorded request used cloud + expected model."""
    records = get_ai_request_records()
    if not records:
        return False, "No AI requests recorded"
    for index, item in enumerate(records, start=1):
        if item.provider != "cloud":
            return False, f"Request #{index} used provider={item.provider!r}"
        if item.model != expected_model:
            return False, f"Request #{index} used model={item.model!r}"
        if "ollama" in item.endpoint.lower():
            return False, f"Request #{index} endpoint looks like Ollama: {item.endpoint}"
    return True, f"All {len(records)} requests used cloud/{expected_model}"
