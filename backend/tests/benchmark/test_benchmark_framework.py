"""Benchmark framework unit tests (no Ollama)."""

from __future__ import annotations

import os

import pytest

from scripts.ai_benchmark.config import (
    PROFILE_DEFINITIONS,
    load_benchmark_config,
)
from scripts.ai_benchmark.framework import BenchmarkFramework
from scripts.ai_benchmark.report import build_report, render_markdown
from scripts.ai_benchmark.types import (
    BenchmarkProfileName,
    BenchmarkRunRecord,
    StageTimingsMs,
    ThinkingModeOption,
)


@pytest.fixture(autouse=True)
def _benchmark_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://benchmark:benchmark@localhost/benchmark")
    monkeypatch.setenv("JWT_SECRET_KEY", "benchmark-secret-key-32-characters!!")
    monkeypatch.setenv("OLLAMA_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3:8b")


def test_profiles_are_configurable() -> None:
    quick = PROFILE_DEFINITIONS[BenchmarkProfileName.QUICK]
    full = PROFILE_DEFINITIONS[BenchmarkProfileName.FULL]
    assert len(quick.e2e_tasks) < len(full.e2e_tasks)
    assert full.stability_iterations > quick.stability_iterations


def test_benchmark_config_uses_benchmark_timeout_not_production_default() -> None:
    os.environ["BENCHMARK_TIMEOUT"] = "450"
    os.environ["AI_TIMEOUT"] = "30"
    config = load_benchmark_config(profile="quick")
    assert config.benchmark_timeout == 450.0
    assert config.thinking_mode is ThinkingModeOption.DISABLED


def test_thinking_mode_both_expands_to_two_runs() -> None:
    config = load_benchmark_config(profile="quick", thinking_mode="both")
    assert config.thinking_modes_to_run == (False, True)


def test_framework_step_count_quick_profile() -> None:
    config = load_benchmark_config(profile="quick", thinking_mode="disabled")
    framework = BenchmarkFramework(config)
    # 1 llm + 1 e2e
    assert framework._count_steps() == 2


def test_report_builder_is_deterministic_structure() -> None:
    from scripts.ai_benchmark.monitor import HardwareSummary

    config = load_benchmark_config(profile="quick")
    hardware = HardwareSummary(
        platform="test",
        processor="cpu",
        cpu_count=4,
        total_ram_gb=16.0,
        gpu_name=None,
        gpu_vram_total_mb=None,
        gpu_available=False,
    )
    runs = [
        BenchmarkRunRecord(
            benchmark_type="llm",
            profile="quick",
            run_label="llm_1",
            task=None,
            thinking_mode="disabled",
            success=True,
            stage_timings=StageTimingsMs(llm_ms=100.0, total_ms=100.0),
        ),
        BenchmarkRunRecord(
            benchmark_type="e2e",
            profile="quick",
            run_label="warm",
            task="executive_summary",
            thinking_mode="disabled",
            success=True,
            stage_timings=StageTimingsMs(
                business_engine_ms=1.0,
                context_builder_ms=1.0,
                prompt_engine_ms=1.0,
                llm_ms=1000.0,
                parser_ms=1.0,
                total_ms=1004.0,
            ),
            facts_count=16,
            selected_facts_count=16,
            parsed_format="text",
        ),
    ]
    report = build_report(
        generated_at="2026-07-14T00:00:00+00:00",
        config=config,
        hardware=hardware,
        runs=runs,
        notes=["test"],
    )
    md = render_markdown(report)
    assert "Benchmark Baseline" in md
    assert "LLM Benchmark Latency" in md
    assert report.baseline.prompt_version == "1.0"
    assert report.baseline.facts_contract_version == "1.0"
