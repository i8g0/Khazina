"""Benchmark report generation."""

from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from scripts.ai_benchmark.baseline import build_baseline
from scripts.ai_benchmark.config import BenchmarkConfig
from scripts.ai_benchmark.monitor import HardwareSummary
from scripts.ai_benchmark.types import BenchmarkRunRecord, LatencyStats, ThinkingSetting


@dataclass
class BenchmarkReport:
    generated_at: str
    baseline: Any
    configuration: dict[str, Any]
    runs: list[BenchmarkRunRecord]
    llm_stats_by_thinking: dict[str, LatencyStats]
    e2e_stats_by_thinking: dict[str, LatencyStats]
    cold_start_ms: float | None
    warm_stats_by_thinking: dict[str, LatencyStats]
    peak_process_rss_mb: float | None
    peak_system_ram_used_mb: float | None
    peak_cpu_percent: float | None
    peak_gpu_utilization_percent: float | None
    peak_gpu_vram_used_mb: float | None
    functional_validation_passed: bool
    stability_passed: bool
    overall_success: bool
    recommendation: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "baseline": self.baseline.to_dict(),
            "configuration": self.configuration,
            "runs": [_run_to_dict(run) for run in self.runs],
            "llm_stats_by_thinking": {
                key: asdict(value) for key, value in self.llm_stats_by_thinking.items()
            },
            "e2e_stats_by_thinking": {
                key: asdict(value) for key, value in self.e2e_stats_by_thinking.items()
            },
            "cold_start_ms": self.cold_start_ms,
            "warm_stats_by_thinking": {
                key: asdict(value) for key, value in self.warm_stats_by_thinking.items()
            },
            "peak_process_rss_mb": self.peak_process_rss_mb,
            "peak_system_ram_used_mb": self.peak_system_ram_used_mb,
            "peak_cpu_percent": self.peak_cpu_percent,
            "peak_gpu_utilization_percent": self.peak_gpu_utilization_percent,
            "peak_gpu_vram_used_mb": self.peak_gpu_vram_used_mb,
            "functional_validation_passed": self.functional_validation_passed,
            "stability_passed": self.stability_passed,
            "overall_success": self.overall_success,
            "recommendation": self.recommendation,
            "notes": list(self.notes),
        }


def _run_to_dict(run: BenchmarkRunRecord) -> dict[str, Any]:
    payload = asdict(run)
    if run.stage_timings is not None:
        payload["stage_timings"] = run.stage_timings.to_dict()
    return payload


def build_report(
    *,
    generated_at: str,
    config: BenchmarkConfig,
    hardware: HardwareSummary,
    runs: list[BenchmarkRunRecord],
    notes: list[str],
) -> BenchmarkReport:
    baseline = build_baseline(
        profile=config.profile.name.value,
        model=config.ollama_model,
        thinking_mode=config.thinking_mode.value,
        hardware=hardware,
    )

    llm_stats = _stats_for_type(runs, benchmark_type="llm")
    e2e_stats = _stats_for_type(runs, benchmark_type="e2e")
    warm_stats = _stats_for_type(
        [
            run
            for run in runs
            if run.benchmark_type == "e2e" and run.run_label == "warm"
        ],
        benchmark_type="e2e",
    )

    cold = next(
        (run for run in runs if run.run_label == "cold_start" and run.success),
        None,
    )
    cold_start_ms = cold.stage_timings.total_ms if cold and cold.stage_timings else None

    core_e2e = [
        run
        for run in runs
        if run.benchmark_type == "e2e"
        and run.run_label in {"cold_start", "warm"}
    ]
    functional_passed = bool(core_e2e) and all(run.success for run in core_e2e)

    stability_runs = [run for run in runs if run.run_label.startswith("stability_")]
    stability_passed = all(run.success for run in stability_runs) if stability_runs else True

    overall = functional_passed and stability_passed and any(run.success for run in runs)

    recommendation = _recommendation(
        config=config,
        hardware=hardware,
        cold_start_ms=cold_start_ms,
        e2e_stats=e2e_stats,
        llm_stats=llm_stats,
        overall_success=overall,
    )

    configuration = {
        "profile": config.profile.name.value,
        "benchmark_timeout": config.benchmark_timeout,
        "thinking_mode": config.thinking_mode.value,
        "ollama_url": config.ollama_url,
        "ollama_model": config.ollama_model,
        "llm_prompt": config.llm_prompt,
        "stability_iterations": config.profile.stability_iterations,
        "cooldown_seconds": config.profile.cooldown_seconds,
        "e2e_tasks": [task.value for task in config.profile.e2e_tasks],
        "llm_iterations": config.profile.llm_iterations,
    }

    return BenchmarkReport(
        generated_at=generated_at,
        baseline=baseline,
        configuration=configuration,
        runs=runs,
        llm_stats_by_thinking=llm_stats,
        e2e_stats_by_thinking=e2e_stats,
        cold_start_ms=cold_start_ms,
        warm_stats_by_thinking=warm_stats,
        peak_process_rss_mb=_peak_attr(runs, "peak_process_rss_mb"),
        peak_system_ram_used_mb=_peak_attr(runs, "peak_system_ram_used_mb"),
        peak_cpu_percent=_peak_attr(runs, "peak_cpu_percent"),
        peak_gpu_utilization_percent=_peak_attr(runs, "peak_gpu_utilization_percent"),
        peak_gpu_vram_used_mb=_peak_attr(runs, "peak_gpu_vram_used_mb"),
        functional_validation_passed=functional_passed,
        stability_passed=stability_passed,
        overall_success=overall,
        recommendation=recommendation,
        notes=notes,
    )


def _stats_for_type(
    runs: list[BenchmarkRunRecord],
    *,
    benchmark_type: str,
) -> dict[str, LatencyStats]:
    filtered = [run for run in runs if run.benchmark_type == benchmark_type and run.success]
    modes = sorted({run.thinking_mode for run in filtered})
    return {
        mode: _latency_stats([r for r in filtered if r.thinking_mode == mode])
        for mode in modes
    }


def _latency_stats(runs: list[BenchmarkRunRecord]) -> LatencyStats:
    values = [
        run.stage_timings.total_ms
        for run in runs
        if run.stage_timings is not None
    ]
    if not values:
        return LatencyStats(average_ms=None, minimum_ms=None, maximum_ms=None, sample_count=0)
    return LatencyStats(
        average_ms=round(statistics.mean(values), 2),
        minimum_ms=round(min(values), 2),
        maximum_ms=round(max(values), 2),
        sample_count=len(values),
    )


def _peak_attr(runs: list[BenchmarkRunRecord], attr: str) -> float | None:
    values = [getattr(run, attr) for run in runs]
    values = [value for value in values if value is not None]
    return max(values) if values else None


def _recommendation(
    *,
    config: BenchmarkConfig,
    hardware: HardwareSummary,
    cold_start_ms: float | None,
    e2e_stats: dict[str, LatencyStats],
    llm_stats: dict[str, LatencyStats],
    overall_success: bool,
) -> str:
    if not overall_success:
        return (
            "Use profile `quick` during development. "
            "Re-run `standard` or `full` after closing memory-heavy applications. "
            "Increase BENCHMARK_TIMEOUT if timeouts persist."
        )

    parts = [
        f"Keep `{config.ollama_model}` for hackathon demo.",
        f"Profile `{config.profile.name.value}` completed successfully.",
    ]
    disabled = e2e_stats.get("disabled") or llm_stats.get("disabled")
    enabled = e2e_stats.get("enabled") or llm_stats.get("enabled")
    if disabled and disabled.average_ms is not None:
        parts.append(f"Thinking disabled average latency: {disabled.average_ms:.0f} ms.")
    if enabled and enabled.average_ms is not None:
        parts.append(f"Thinking enabled average latency: {enabled.average_ms:.0f} ms.")
    if cold_start_ms is not None:
        parts.append(f"Cold start: {cold_start_ms:.0f} ms.")
    if hardware.gpu_available:
        parts.append("Retain GPU acceleration for demo.")
    else:
        parts.append("CPU-only execution detected; expect longer demo latencies.")
    return " ".join(parts)


def render_markdown(report: BenchmarkReport) -> str:
    hw = report.baseline.hardware
    lines = [
        "# Khazina AI Benchmark Report",
        "",
        f"**Generated:** {report.generated_at}",
        "",
        "## Benchmark Baseline",
        "",
        f"- **Benchmark Version:** {report.baseline.benchmark_version}",
        f"- **Profile:** {report.baseline.profile}",
        f"- **Model:** `{report.baseline.model}`",
        f"- **Prompt Version:** {report.baseline.prompt_version}",
        f"- **Facts Contract Version:** {report.baseline.facts_contract_version}",
        f"- **Thinking Mode Setting:** {report.baseline.thinking_mode}",
        "",
        "## Configuration",
        "",
    ]
    for key, value in sorted(report.configuration.items()):
        lines.append(f"- **{key}:** {value}")

    lines.extend(
        [
            "",
            "## Hardware Summary",
            "",
            f"- **Platform:** {hw.platform}",
            f"- **Processor:** {hw.processor}",
            f"- **Logical CPUs:** {hw.cpu_count}",
            f"- **Total RAM:** {hw.total_ram_gb} GB" if hw.total_ram_gb else "- **Total RAM:** n/a",
            f"- **GPU:** {hw.gpu_name or 'CPU-only'}",
        ]
    )
    if hw.gpu_vram_total_mb:
        lines.append(f"- **GPU VRAM (total):** {hw.gpu_vram_total_mb:.0f} MB")

    lines.extend(["", "## Results Summary", ""])
    if report.cold_start_ms is not None:
        lines.append(f"- **Cold Start:** {report.cold_start_ms:.2f} ms")
    lines.extend(
        [
            f"- **Functional Validation:** {'PASS' if report.functional_validation_passed else 'FAIL'}",
            f"- **Stability Validation:** {'PASS' if report.stability_passed else 'FAIL'}",
            f"- **Overall:** {'PASS' if report.overall_success else 'FAIL'}",
            "",
            "### LLM Benchmark Latency",
            "",
            _stats_table(report.llm_stats_by_thinking),
            "",
            "### End-to-End Benchmark Latency",
            "",
            _stats_table(report.e2e_stats_by_thinking),
            "",
            "### Resource Peaks",
            "",
            f"- **Process RSS:** {report.peak_process_rss_mb or 'n/a'} MB",
            f"- **System RAM Used:** {report.peak_system_ram_used_mb or 'n/a'} MB",
            f"- **CPU:** {report.peak_cpu_percent or 'n/a'} %",
            f"- **GPU Utilization:** {report.peak_gpu_utilization_percent or 'n/a'} %",
            f"- **GPU VRAM Used:** {report.peak_gpu_vram_used_mb or 'n/a'} MB",
            "",
            "## Recommendation",
            "",
            report.recommendation,
            "",
        ]
    )
    if report.notes:
        lines.extend(["## Notes", ""] + [f"- {n}" for n in report.notes] + [""])

    lines.extend(
        [
            "## Run Details",
            "",
            "| Type | Label | Task | Thinking | Success | Total ms | LLM ms | Engine ms |",
            "|------|-------|------|----------|---------|----------|--------|-----------|",
        ]
    )
    for run in report.runs:
        total = run.stage_timings.total_ms if run.stage_timings else "n/a"
        llm = run.stage_timings.llm_ms if run.stage_timings else "n/a"
        engine = run.stage_timings.business_engine_ms if run.stage_timings else "n/a"
        lines.append(
            f"| {run.benchmark_type} | {run.run_label} | {run.task or '-'} | "
            f"{run.thinking_mode} | {run.success} | {total} | {llm} | {engine} |"
        )
        if run.error:
            lines.append(f"| | | | | error: {run.error} | | | |")
    lines.append("")
    return "\n".join(lines)


def _stats_table(stats: dict[str, LatencyStats]) -> str:
    if not stats:
        return "_No successful samples._"
    lines = [
        "| Thinking | Avg ms | Min ms | Max ms | Samples |",
        "|----------|--------|--------|--------|---------|",
    ]
    for mode, value in sorted(stats.items()):
        lines.append(
            f"| {mode} | {value.average_ms or 'n/a'} | {value.minimum_ms or 'n/a'} | "
            f"{value.maximum_ms or 'n/a'} | {value.sample_count} |"
        )
    return "\n".join(lines)


def write_report(report: BenchmarkReport, *, json_path: str, md_path: str) -> None:
    json_file = Path(json_path)
    md_file = Path(md_path)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    md_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    md_file.write_text(render_markdown(report), encoding="utf-8")
