"""Persist pipeline timelines to entity metadata."""

from __future__ import annotations

from typing import Any

from app.db.models import AnalysisRun, FinancialFile
from app.observability.pipeline import attach_pipeline_timeline, load_pipeline_timeline, PipelineTimeline


def load_file_timeline(file: FinancialFile) -> list[dict[str, Any]]:
    return load_pipeline_timeline(file.file_metadata)


def file_metadata_with_timeline(
    file: FinancialFile,
    timeline: list[dict[str, Any]],
) -> dict[str, Any]:
    return attach_pipeline_timeline(file.file_metadata, timeline)


def run_metadata_with_timeline(
    run: AnalysisRun,
    timeline: list[dict[str, Any]],
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged = {**(run.runtime_metadata or {}), **(extra or {})}
    return attach_pipeline_timeline(merged, timeline)


def merge_run_timeline(
    run: AnalysisRun,
    timeline: PipelineTimeline,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return run_metadata_with_timeline(run, timeline.to_list(), extra=extra)
