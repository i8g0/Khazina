"""Chronological pipeline execution timeline (Sprint D5)."""

from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Iterator

from app.observability.errors import ErrorCategory, classify_exception


class PipelineStage(StrEnum):
    UPLOAD_STARTED = "upload_started"
    UPLOAD_COMPLETED = "upload_completed"
    VALIDATION = "validation"
    PARSING = "parsing"
    SNAPSHOT_CREATED = "snapshot_created"
    WASTE_ANALYSIS_STARTED = "waste_analysis_started"
    WASTE_ANALYSIS_COMPLETED = "waste_analysis_completed"
    RISK_ANALYSIS_STARTED = "risk_analysis_started"
    RISK_ANALYSIS_COMPLETED = "risk_analysis_completed"
    AI_STARTED = "ai_started"
    AI_COMPLETED = "ai_completed"
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_COMPLETED = "simulation_completed"
    REPORT_GENERATION = "report_generation"
    PDF_EXPORT = "pdf_export"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(StrEnum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class PipelineTimeline:
    """In-memory chronological stage tracker persisted to entity metadata."""

    def __init__(
        self,
        *,
        organization_id: str,
        file_id: str | None = None,
        snapshot_id: str | None = None,
        analysis_run_id: str | None = None,
        inherited: list[dict[str, Any]] | None = None,
    ) -> None:
        self.organization_id = organization_id
        self.file_id = file_id
        self.snapshot_id = snapshot_id
        self.analysis_run_id = analysis_run_id
        self._entries: list[dict[str, Any]] = list(inherited or [])
        self._open_starts: dict[str, float] = {}

    def inherit(self, prior: list[dict[str, Any]] | None) -> None:
        if prior:
            self._entries.extend(prior)

    def start_stage(self, stage: PipelineStage | str) -> None:
        key = str(stage)
        self._open_starts[key] = time.perf_counter()
        self._entries.append(
            {
                "stage": key,
                "status": StageStatus.STARTED.value,
                "timestamp": _utc_now_iso(),
                "duration_ms": None,
            }
        )

    def complete_stage(
        self,
        stage: PipelineStage | str,
        *,
        duration_ms: float | None = None,
    ) -> None:
        key = str(stage)
        elapsed = duration_ms
        if elapsed is None:
            started = self._open_starts.pop(key, None)
            if started is not None:
                elapsed = round((time.perf_counter() - started) * 1000, 2)
        self._entries.append(
            {
                "stage": key,
                "status": StageStatus.COMPLETED.value,
                "timestamp": _utc_now_iso(),
                "duration_ms": elapsed,
            }
        )

    def fail_stage(
        self,
        stage: PipelineStage | str,
        exc: BaseException,
        *,
        duration_ms: float | None = None,
    ) -> ErrorCategory:
        key = str(stage)
        category = classify_exception(exc)
        elapsed = duration_ms
        if elapsed is None:
            started = self._open_starts.pop(key, None)
            if started is not None:
                elapsed = round((time.perf_counter() - started) * 1000, 2)
        self._entries.append(
            {
                "stage": key,
                "status": StageStatus.FAILED.value,
                "timestamp": _utc_now_iso(),
                "duration_ms": elapsed,
                "error_category": category.value,
                "message": str(exc),
            }
        )
        self._entries.append(
            {
                "stage": PipelineStage.FAILED.value,
                "status": StageStatus.FAILED.value,
                "timestamp": _utc_now_iso(),
                "duration_ms": None,
                "error_category": category.value,
                "message": str(exc),
            }
        )
        return category

    def mark_completed(self) -> None:
        self._entries.append(
            {
                "stage": PipelineStage.COMPLETED.value,
                "status": StageStatus.COMPLETED.value,
                "timestamp": _utc_now_iso(),
                "duration_ms": None,
            }
        )

    @contextmanager
    def track(self, stage: PipelineStage | str) -> Iterator[None]:
        self.start_stage(stage)
        try:
            yield
            self.complete_stage(stage)
        except Exception as exc:
            self.fail_stage(stage, exc)
            raise

    def to_list(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def append_entries(self, entries: list[dict[str, Any]]) -> None:
        self._entries.extend(entries)


def load_pipeline_timeline(metadata: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not metadata:
        return []
    timeline = metadata.get("pipeline_timeline")
    return list(timeline) if isinstance(timeline, list) else []


def attach_pipeline_timeline(
    metadata: dict[str, Any] | None,
    timeline: list[dict[str, Any]],
) -> dict[str, Any]:
    merged = dict(metadata or {})
    merged["pipeline_timeline"] = timeline
    return merged
