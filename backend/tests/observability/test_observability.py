"""Observability unit tests (Sprint D5)."""

from __future__ import annotations

import pytest

from app.ingestion.exceptions import ParseError, ValidationFailure
from app.observability.errors import ErrorCategory, classify_exception
from app.observability.health import check_system_health
from app.observability.pipeline import PipelineStage, PipelineTimeline


def test_pipeline_timeline_records_stages() -> None:
    timeline = PipelineTimeline(organization_id="org-1")
    with timeline.track(PipelineStage.PARSING):
        pass
    timeline.complete_stage(PipelineStage.UPLOAD_COMPLETED)
    entries = timeline.to_list()
    assert entries[0]["stage"] == PipelineStage.PARSING.value
    assert entries[0]["status"] == "started"
    assert entries[-1]["stage"] == PipelineStage.UPLOAD_COMPLETED.value
    assert entries[-1]["status"] == "completed"


def test_pipeline_timeline_failure_classification() -> None:
    timeline = PipelineTimeline(organization_id="org-1")
    try:
        with timeline.track(PipelineStage.VALIDATION):
            raise ValidationFailure("invalid workbook")
    except ValidationFailure:
        pass
    failed = [e for e in timeline.to_list() if e["status"] == "failed"]
    assert failed
    assert failed[0]["error_category"] == ErrorCategory.VALIDATION.value


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (ParseError("bad xlsx", file_name="f.xlsx"), ErrorCategory.EXCEL_PARSING),
        (ValidationFailure("bad data"), ErrorCategory.VALIDATION),
    ],
)
def test_classify_exception(exc: Exception, expected: ErrorCategory) -> None:
    assert classify_exception(exc) == expected


def test_classify_snapshot_adapter_error_by_name() -> None:
    from app.decision.exceptions import SnapshotAdapterError

    exc = SnapshotAdapterError(error_code="W1_MISSING_COLUMN", message="missing category")
    assert classify_exception(exc) == ErrorCategory.VALIDATION


def test_system_health_returns_components() -> None:
    result = check_system_health()
    assert result.backend.status == "ok"
    assert result.database.status in {"ok", "unavailable"}
    assert result.ai.status in {"ok", "unavailable"}
    assert result.status in {"ok", "degraded", "unavailable"}

