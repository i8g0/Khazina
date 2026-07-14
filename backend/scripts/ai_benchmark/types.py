"""Benchmark framework shared types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal

BenchmarkType = Literal["llm", "e2e"]
ThinkingSetting = Literal["enabled", "disabled"]


class BenchmarkProfileName(StrEnum):
    QUICK = "quick"
    STANDARD = "standard"
    FULL = "full"


class ThinkingModeOption(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    BOTH = "both"


@dataclass(frozen=True, slots=True)
class StageTimingsMs:
    business_engine_ms: float = 0.0
    context_builder_ms: float = 0.0
    prompt_engine_ms: float = 0.0
    llm_ms: float = 0.0
    parser_ms: float = 0.0
    total_ms: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "business_engine_ms": self.business_engine_ms,
            "context_builder_ms": self.context_builder_ms,
            "prompt_engine_ms": self.prompt_engine_ms,
            "llm_ms": self.llm_ms,
            "parser_ms": self.parser_ms,
            "total_ms": self.total_ms,
        }


@dataclass(frozen=True, slots=True)
class LatencyStats:
    average_ms: float | None
    minimum_ms: float | None
    maximum_ms: float | None
    sample_count: int


@dataclass
class BenchmarkRunRecord:
    benchmark_type: BenchmarkType
    profile: str
    run_label: str
    task: str | None
    thinking_mode: ThinkingSetting
    success: bool
    stage_timings: StageTimingsMs | None = None
    error: str | None = None
    facts_count: int | None = None
    selected_facts_count: int | None = None
    parsed_format: str | None = None
    prompt_chars: int | None = None
    peak_process_rss_mb: float | None = None
    peak_system_ram_used_mb: float | None = None
    peak_cpu_percent: float | None = None
    peak_gpu_utilization_percent: float | None = None
    peak_gpu_vram_used_mb: float | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
