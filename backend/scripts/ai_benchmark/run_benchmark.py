"""Deterministic AI pipeline benchmark runner (Sprint 5.5)."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import httpx

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.ai_benchmark.monitor import (  # noqa: E402
    HardwareSummary,
    collect_hardware_summary,
    require_psutil,
    sample_resources,
)
from app.ai.prompts.tasks import PromptTask  # noqa: E402
from app.ai.services.orchestrator import AiOrchestrator  # noqa: E402
from app.ai.services.types import AiExecutionRequest  # noqa: E402
from app.business.engines.waste.engine import WasteEngine  # noqa: E402
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput  # noqa: E402
from app.business.registry import freeze_registry, register_engine, reset_registry_for_testing  # noqa: E402

BENCHMARK_TASKS: tuple[PromptTask, ...] = (
    PromptTask.EXECUTIVE_SUMMARY,
    PromptTask.RISK_ANALYSIS,
    PromptTask.RECOMMENDATIONS,
    PromptTask.SCENARIO_ANALYSIS,
)


@dataclass(frozen=True, slots=True)
class StageTimings:
    total_ms: float


@dataclass
class RunResult:
    task: str
    run_type: str
    success: bool
    timings: StageTimings | None = None
    error: str | None = None
    facts_count: int | None = None
    selected_facts_count: int | None = None
    parsed_format: str | None = None
    peak_process_rss_mb: float | None = None
    peak_system_ram_used_mb: float | None = None
    peak_cpu_percent: float | None = None
    peak_gpu_utilization_percent: float | None = None
    peak_gpu_vram_used_mb: float | None = None


@dataclass
class BenchmarkReport:
    generated_at: str
    hardware: HardwareSummary
    ollama_url: str
    model: str
    methodology_version: str
    executions_per_task: int
    stability_iterations: int
    cold_start_ms: float | None
    warm_latencies_ms: list[float]
    task_results: list[RunResult]
    functional_validation_passed: bool
    stability_passed: bool
    average_latency_ms: float | None
    min_latency_ms: float | None
    max_latency_ms: float | None
    peak_process_rss_mb: float | None
    peak_system_ram_used_mb: float | None
    peak_cpu_percent: float | None
    peak_gpu_utilization_percent: float | None
    peak_gpu_vram_used_mb: float | None
    demo_recommendation: str
    notes: list[str] = field(default_factory=list)


def _fixed_waste_input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="benchmark-org",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )


def _ensure_env() -> tuple[str, str]:
    os.environ.setdefault(
        "DATABASE_URL", "postgresql://benchmark:benchmark@localhost/benchmark"
    )
    os.environ.setdefault("JWT_SECRET_KEY", "benchmark-secret-key-32-characters!!")
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
    os.environ.setdefault("OLLAMA_URL", ollama_url)
    os.environ.setdefault("OLLAMA_MODEL", model)
    return ollama_url, model


def _prepare_registry() -> None:
    reset_registry_for_testing()
    register_engine(WasteEngine())
    freeze_registry()


def _unload_model(ollama_url: str, model: str) -> None:
    url = f"{ollama_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "stream": False,
        "keep_alive": 0,
    }
    try:
        httpx.post(url, json=payload, timeout=120.0)
    except httpx.HTTPError:
        pass


def _execute_full(orchestrator: AiOrchestrator, task: PromptTask, run_type: str) -> RunResult:
    peak_process: float | None = None
    peak_ram: float | None = None
    peak_cpu: float | None = None
    peak_gpu: float | None = None
    peak_vram: float | None = None

    def absorb() -> None:
        nonlocal peak_process, peak_ram, peak_cpu, peak_gpu, peak_vram
        sample = sample_resources()
        peak_process = _max(peak_process, sample.process_rss_mb)
        peak_ram = _max(peak_ram, sample.system_ram_used_mb)
        peak_cpu = _max(peak_cpu, sample.cpu_percent)
        peak_gpu = _max(peak_gpu, sample.gpu_utilization_percent)
        peak_vram = _max(peak_vram, sample.gpu_vram_used_mb)

    absorb()
    start = time.perf_counter()
    try:
        result = orchestrator.execute(
            AiExecutionRequest(
                engine_id="waste",
                engine_input=_fixed_waste_input(),
                task=task,
                domain="waste",
            )
        )
    except Exception as exc:  # noqa: BLE001 - benchmark boundary
        absorb()
        return RunResult(task=task.value, run_type=run_type, success=False, error=str(exc))
    absorb()
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return RunResult(
        task=task.value,
        run_type=run_type,
        success=True,
        timings=StageTimings(total_ms=elapsed_ms),
        facts_count=len(result.facts_contract.facts),
        selected_facts_count=result.prompt_context.selected_fact_count,
        parsed_format=result.parsed_response.format,
        peak_process_rss_mb=peak_process,
        peak_system_ram_used_mb=peak_ram,
        peak_cpu_percent=peak_cpu,
        peak_gpu_utilization_percent=peak_gpu,
        peak_gpu_vram_used_mb=peak_vram,
    )


def _max(current: float | None, value: float | None) -> float | None:
    if value is None:
        return current
    if current is None:
        return value
    return max(current, value)


def run_benchmark(
    *,
    stability_iterations: int = 2,
    skip_cold_unload: bool = False,
) -> BenchmarkReport:
    require_psutil()
    ollama_url, model = _ensure_env()
    _prepare_registry()
    hardware = collect_hardware_summary()
    orchestrator = AiOrchestrator()
    results: list[RunResult] = []
    notes: list[str] = []

    if not skip_cold_unload:
        _unload_model(ollama_url, model)
        notes.append("Cold start measured after Ollama keep_alive=0 unload request.")

    cold = _execute_full(orchestrator, BENCHMARK_TASKS[0], "cold_start")
    results.append(cold)
    cold_start_ms = cold.timings.total_ms if cold.success and cold.timings else None

    warm_latencies: list[float] = []
    for task in BENCHMARK_TASKS:
        run = _execute_full(orchestrator, task, "warm")
        results.append(run)
        if run.success and run.timings:
            warm_latencies.append(run.timings.total_ms)

    stability_passed = True
    for iteration in range(stability_iterations):
        for task in BENCHMARK_TASKS:
            run = _execute_full(orchestrator, task, f"stability_{iteration + 1}")
            results.append(run)
            if not run.success:
                stability_passed = False
            elif run.timings:
                warm_latencies.append(run.timings.total_ms)

    functional_validation_passed = all(
        run.success
        and run.facts_count
        and run.selected_facts_count
        and run.parsed_format in {"json", "text"}
        for run in results
        if run.run_type in {"cold_start", "warm"}
    )

    demo_recommendation = _build_demo_recommendation(
        model=model,
        hardware=hardware,
        cold_start_ms=cold_start_ms,
        avg_latency_ms=round(statistics.mean(warm_latencies), 2) if warm_latencies else None,
        peak_vram_mb=_peak_attr(results, "peak_gpu_vram_used_mb"),
        stability_passed=stability_passed,
        functional_validation_passed=functional_validation_passed,
    )

    return BenchmarkReport(
        generated_at=datetime.now(UTC).isoformat(),
        hardware=hardware,
        ollama_url=ollama_url,
        model=model,
        methodology_version="1.0",
        executions_per_task=1 + stability_iterations,
        stability_iterations=stability_iterations,
        cold_start_ms=cold_start_ms,
        warm_latencies_ms=warm_latencies,
        task_results=results,
        functional_validation_passed=functional_validation_passed,
        stability_passed=stability_passed,
        average_latency_ms=round(statistics.mean(warm_latencies), 2)
        if warm_latencies
        else None,
        min_latency_ms=round(min(warm_latencies), 2) if warm_latencies else None,
        max_latency_ms=round(max(warm_latencies), 2) if warm_latencies else None,
        peak_process_rss_mb=_peak_attr(results, "peak_process_rss_mb"),
        peak_system_ram_used_mb=_peak_attr(results, "peak_system_ram_used_mb"),
        peak_cpu_percent=_peak_attr(results, "peak_cpu_percent"),
        peak_gpu_utilization_percent=_peak_attr(results, "peak_gpu_utilization_percent"),
        peak_gpu_vram_used_mb=_peak_attr(results, "peak_gpu_vram_used_mb"),
        demo_recommendation=demo_recommendation,
        notes=notes,
    )


def _peak_attr(results: list[RunResult], attr: str) -> float | None:
    values = [getattr(run, attr) for run in results]
    values = [value for value in values if value is not None]
    return max(values) if values else None


def _build_demo_recommendation(
    *,
    model: str,
    hardware: HardwareSummary,
    cold_start_ms: float | None,
    avg_latency_ms: float | None,
    peak_vram_mb: float | None,
    stability_passed: bool,
    functional_validation_passed: bool,
) -> str:
    if not stability_passed or not functional_validation_passed:
        return (
            "Do not change the development baseline yet. "
            "Stability or functional validation failed during benchmark runs."
        )
    if avg_latency_ms is None:
        return "Insufficient latency data to recommend a demo model."

    parts = [
        f"Keep `{model}` as the hackathon demo model.",
        "Measured pipeline completed all benchmark tasks without orchestration failures.",
    ]
    if cold_start_ms is not None:
        parts.append(f"Cold start latency was {cold_start_ms:.0f} ms.")
    parts.append(f"Average warm latency was {avg_latency_ms:.0f} ms.")
    if hardware.gpu_available and peak_vram_mb is not None:
        parts.append(
            f"Peak GPU VRAM during runs was {peak_vram_mb:.0f} MB on {hardware.gpu_name}."
        )
        parts.append("Retain GPU acceleration in Ollama for demo deployments.")
    else:
        parts.append("Environment executed in CPU-only mode; document longer latencies for demo.")
    return " ".join(parts)


def _report_to_markdown(report: BenchmarkReport) -> str:
    hw = report.hardware
    lines = [
        "# Khazina AI Pipeline Benchmark Report",
        "",
        f"**Generated:** {report.generated_at}",
        f"**Methodology version:** {report.methodology_version}",
        "",
        "## Hardware Summary",
        "",
        f"- **Platform:** {hw.platform}",
        f"- **Processor:** {hw.processor}",
        f"- **Logical CPUs:** {hw.cpu_count}",
        f"- **Total RAM:** {hw.total_ram_gb} GB" if hw.total_ram_gb else "- **Total RAM:** n/a",
        f"- **GPU:** {hw.gpu_name or 'Not detected (CPU-only)'}",
    ]
    if hw.gpu_vram_total_mb:
        lines.append(f"- **GPU VRAM (total):** {hw.gpu_vram_total_mb:.0f} MB")
    lines.extend(
        [
            "",
            "## Active AI Model",
            "",
            f"- **Ollama URL:** {report.ollama_url}",
            f"- **Model:** `{report.model}`",
            "",
            "## Benchmark Methodology",
            "",
            "See [AI_BENCHMARK_METHODOLOGY.md](AI_BENCHMARK_METHODOLOGY.md).",
            "",
            "## Latency Results",
            "",
            f"- **Cold start:** {report.cold_start_ms:.2f} ms"
            if report.cold_start_ms is not None
            else "- **Cold start:** n/a",
            f"- **Average warm latency:** {report.average_latency_ms:.2f} ms"
            if report.average_latency_ms is not None
            else "- **Average warm latency:** n/a",
            f"- **Minimum warm latency:** {report.min_latency_ms:.2f} ms"
            if report.min_latency_ms is not None
            else "- **Minimum warm latency:** n/a",
            f"- **Maximum warm latency:** {report.max_latency_ms:.2f} ms"
            if report.max_latency_ms is not None
            else "- **Maximum warm latency:** n/a",
            f"- **Executions recorded:** {len(report.task_results)}",
            "",
            "## Resource Usage (Peaks)",
            "",
            f"- **Process RSS:** {report.peak_process_rss_mb:.2f} MB"
            if report.peak_process_rss_mb
            else "- **Process RSS:** n/a",
            f"- **System RAM used:** {report.peak_system_ram_used_mb:.2f} MB"
            if report.peak_system_ram_used_mb
            else "- **System RAM used:** n/a",
            f"- **CPU utilization:** {report.peak_cpu_percent:.1f}%"
            if report.peak_cpu_percent is not None
            else "- **CPU utilization:** n/a",
            f"- **GPU utilization:** {report.peak_gpu_utilization_percent:.1f}%"
            if report.peak_gpu_utilization_percent is not None
            else "- **GPU utilization:** n/a (CPU-only or nvidia-smi unavailable)",
            f"- **GPU VRAM used:** {report.peak_gpu_vram_used_mb:.2f} MB"
            if report.peak_gpu_vram_used_mb is not None
            else "- **GPU VRAM used:** n/a",
            "",
            "## Validation",
            "",
            f"- **Functional pipeline validation:** {'PASS' if report.functional_validation_passed else 'FAIL'}",
            f"- **Stability validation:** {'PASS' if report.stability_passed else 'FAIL'}",
            "",
            "## Demo Recommendation",
            "",
            report.demo_recommendation,
            "",
        ]
    )
    if report.notes:
        lines.extend(["## Notes", ""] + [f"- {note}" for note in report.notes] + [""])
    lines.extend(
        [
            "## Run Details",
            "",
            "| Task | Run Type | Success | Total ms | Facts | Parsed |",
            "|------|----------|---------|----------|-------|--------|",
        ]
    )
    for run in report.task_results:
        total = run.timings.total_ms if run.timings else "n/a"
        lines.append(
            f"| {run.task} | {run.run_type} | {run.success} | {total} | "
            f"{run.facts_count or 'n/a'} | {run.parsed_format or run.error or 'n/a'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Khazina AI pipeline benchmarks.")
    parser.add_argument(
        "--stability-iterations",
        type=int,
        default=2,
        help="Number of stability iterations per task (default: 2).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=BACKEND_ROOT.parent / "docs" / "AI_BENCHMARK_REPORT.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=BACKEND_ROOT.parent / "docs" / "AI_BENCHMARK_REPORT.md",
    )
    parser.add_argument(
        "--skip-cold-unload",
        action="store_true",
        help="Skip Ollama model unload before cold start measurement.",
    )
    args = parser.parse_args()

    report = run_benchmark(
        stability_iterations=args.stability_iterations,
        skip_cold_unload=args.skip_cold_unload,
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    payload["hardware"] = asdict(report.hardware)
    payload["task_results"] = [
        {
            **asdict(run),
            "timings": asdict(run.timings) if run.timings else None,
        }
        for run in report.task_results
    ]
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.output_md.write_text(_report_to_markdown(report), encoding="utf-8")
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()
