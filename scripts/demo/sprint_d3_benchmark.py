#!/usr/bin/env python3
"""Sprint D3 — full pipeline benchmark with per-stage timing and resource sampling."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

import httpx

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BACKEND_ROOT / ".env")

from scripts.ai_benchmark.monitor import (  # noqa: E402
    ResourceSummary,
    collect_hardware_summary,
    sample_resources,
)

API_BASE = os.environ.get("KHAZINA_API_URL", "http://localhost:8000").rstrip("/")
DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@khazina.sa")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoExec2026!")
WORKBOOK = Path(__file__).resolve().parent / "Procurement_Q2.xlsx"
AI_TIMEOUT = int(os.environ.get("AI_TIMEOUT", "180"))
TOTAL_AI_TIMEOUT = AI_TIMEOUT * 3 + 60
RESULTS_PATH = Path(__file__).resolve().parent / "sprint_d3_benchmark_results.json"


@dataclass
class StageTiming:
    name: str
    elapsed_ms: float
    success: bool
    detail: str = ""


@dataclass
class AiTaskTiming:
    task: str
    context_ms: float
    prompt_ms: float
    llm_ms: float
    parser_ms: float
    total_ms: float


@dataclass
class IngestionSubTiming:
    parse_ms: float
    validate_ms: float
    quality_ms: float
    total_ms: float


@dataclass
class BenchmarkRun:
    label: str
    stages: list[StageTiming] = field(default_factory=list)
    ingestion_sub: IngestionSubTiming | None = None
    ai_tasks: list[AiTaskTiming] = field(default_factory=list)
    ollama_cold_ms: float | None = None
    ollama_warm_ms: float | None = None
    total_ms: float = 0.0
    resources: dict[str, Any] = field(default_factory=dict)


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def _unwrap(response: httpx.Response) -> dict[str, Any]:
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API request failed")
    return payload["data"]


def _step(name: str, fn: Callable[[], str], resources: ResourceSummary) -> StageTiming:
    resources.absorb(sample_resources())
    start = time.perf_counter()
    try:
        detail = fn()
        resources.absorb(sample_resources())
        return StageTiming(name, _elapsed_ms(start), True, detail)
    except Exception as exc:  # noqa: BLE001
        resources.absorb(sample_resources())
        return StageTiming(name, _elapsed_ms(start), False, str(exc))


def benchmark_ingestion_substages(workbook: Path) -> IngestionSubTiming:
    from app.ingestion.parser import FinancialFileParser
    from app.ingestion.quality import DatasetQualityAssessor
    from app.ingestion.validator import DatasetValidator

    parser = FinancialFileParser()
    validator = DatasetValidator()
    quality = DatasetQualityAssessor()

    total_start = time.perf_counter()
    p0 = time.perf_counter()
    dataset, _ = parser.parse_file(str(workbook), workbook.name)
    parse_ms = _elapsed_ms(p0)

    v0 = time.perf_counter()
    validation = validator.validate(dataset)
    validate_ms = _elapsed_ms(v0)
    if not validation.is_valid:
        raise RuntimeError(validation.error_message or "Validation failed")

    q0 = time.perf_counter()
    quality.assess(dataset)
    quality_ms = _elapsed_ms(q0)

    return IngestionSubTiming(
        parse_ms=parse_ms,
        validate_ms=validate_ms,
        quality_ms=quality_ms,
        total_ms=_elapsed_ms(total_start),
    )


def benchmark_ai_substages(
    organization_id: uuid.UUID,
    analysis_run_id: uuid.UUID,
) -> list[AiTaskTiming]:
    from app.ai.client import OllamaClient
    from app.ai.context.builder import ContextBuilder
    from app.ai.context.types import ContextBuildOptions
    from app.ai.parsers.response_parser import ResponseParser
    from app.ai.prompts.composer import PromptComposer
    from app.ai.prompts.tasks import PromptTask
    from app.ai_recommendations.constants import TASK_EXECUTION_ORDER
    from app.ai_recommendations.facts_loader import load_facts_contract
    from app.core.config import settings
    from app.db.session import SessionLocal
    from app.repositories import AnalysisRepository

    session = SessionLocal()
    try:
        repo = AnalysisRepository(session)
        run = repo.get(analysis_run_id)
        if run is None:
            raise RuntimeError(f"Analysis run {analysis_run_id} not found")
        facts = load_facts_contract(dict(run.runtime_metadata or {}))
    finally:
        session.close()

    client = OllamaClient(settings.ai)
    context_builder = ContextBuilder()
    prompt_composer = PromptComposer()
    response_parser = ResponseParser()
    timings: list[AiTaskTiming] = []

    try:
        for task in TASK_EXECUTION_ORDER:
            total_start = time.perf_counter()
            c0 = time.perf_counter()
            prompt_context = context_builder.build(
                facts,
                ContextBuildOptions(task=task, domain="waste"),
            )
            context_ms = _elapsed_ms(c0)

            p0 = time.perf_counter()
            composed = prompt_composer.compose(task, prompt_context.facts)
            prompt_ms = _elapsed_ms(p0)

            messages = [
                {"role": "system", "content": composed.system_prompt},
                {"role": "user", "content": composed.user_prompt},
            ]
            l0 = time.perf_counter()
            llm_response = client.chat(messages, model=settings.ai.ollama_model)
            llm_ms = _elapsed_ms(l0)

            r0 = time.perf_counter()
            response_parser.parse(llm_response)
            parser_ms = _elapsed_ms(r0)

            timings.append(
                AiTaskTiming(
                    task=task.value,
                    context_ms=context_ms,
                    prompt_ms=prompt_ms,
                    llm_ms=llm_ms,
                    parser_ms=parser_ms,
                    total_ms=_elapsed_ms(total_start),
                )
            )
    finally:
        client.close()

    return timings


def measure_ollama_latency() -> tuple[float | None, float | None]:
    from app.ai.client import OllamaClient
    from app.core.config import settings

    client = OllamaClient(settings.ai)
    cold_ms: float | None = None
    warm_ms: float | None = None
    try:
        messages = [
            {"role": "system", "content": "Reply with OK only."},
            {"role": "user", "content": "OK"},
        ]
        t0 = time.perf_counter()
        try:
            client.chat(messages, model=settings.ai.ollama_model)
            cold_ms = _elapsed_ms(t0)
        except Exception:
            cold_ms = None

        t1 = time.perf_counter()
        try:
            client.chat(messages, model=settings.ai.ollama_model)
            warm_ms = _elapsed_ms(t1)
        except Exception:
            warm_ms = None
    finally:
        client.close()
    return cold_ms, warm_ms


def run_http_pipeline(label: str) -> tuple[BenchmarkRun, dict[str, str]]:
    if not WORKBOOK.exists():
        raise FileNotFoundError(
            f"Missing workbook {WORKBOOK} — run generate_workbook.py first"
        )

    resources = ResourceSummary()
    run = BenchmarkRun(label=label)
    state: dict[str, str] = {}
    total_start = time.perf_counter()

    with httpx.Client(base_url=f"{API_BASE}/api/v1", timeout=TOTAL_AI_TIMEOUT) as client:
        def login() -> str:
            data = _unwrap(
                client.post(
                    "/auth/login",
                    json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
                )
            )
            state["token"] = data["access_token"]
            return "authenticated"

        run.stages.append(_step("login", login, resources))

        def active_org() -> str:
            data = _unwrap(
                client.get(
                    "/organizations/active",
                    headers={"Authorization": f"Bearer {state['token']}"},
                )
            )
            state["org_id"] = data["id"]
            return data["name"]

        run.stages.append(_step("active_organization", active_org, resources))

        def upload() -> str:
            with WORKBOOK.open("rb") as handle:
                data = _unwrap(
                    client.post(
                        f"/organizations/{state['org_id']}/financial-files/upload",
                        headers={"Authorization": f"Bearer {state['token']}"},
                        files={
                            "upload": (
                                WORKBOOK.name,
                                handle,
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )
                        },
                    )
                )
            state["file_id"] = data["financial_file"]["id"]
            snapshot = data.get("financial_snapshot")
            if snapshot:
                state["snapshot_id"] = snapshot["id"]
            return state["file_id"]

        run.stages.append(_step("excel_upload_and_snapshot", upload, resources))

        def waste() -> str:
            body: dict[str, Any] = {
                "title": "Sprint D3 benchmark waste",
                "source_file_id": state["file_id"],
            }
            if "snapshot_id" in state:
                body["source_snapshot_id"] = state["snapshot_id"]
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/decisions/waste/execute",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json=body,
                )
            )
            state["waste_run_id"] = data["analysis_run"]["id"]
            return state["waste_run_id"]

        run.stages.append(_step("waste_analysis", waste, resources))

        def ai() -> str:
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/ai-recommendations/waste/generate",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json={
                        "analysis_run_id": state["waste_run_id"],
                        "regenerate": True,
                    },
                    timeout=TOTAL_AI_TIMEOUT,
                )
            )
            count = data.get("recommendation_count", 0)
            return f"recommendations={count}"

        run.stages.append(_step("ai_recommendations", ai, resources))

        def simulation() -> str:
            scenarios = _unwrap(
                client.get(
                    f"/organizations/{state['org_id']}/simulation/scenarios",
                    headers={"Authorization": f"Bearer {state['token']}"},
                )
            )
            scenario_id = scenarios[0]["id"]
            body = {
                "source_file_id": state["file_id"],
                "baseline_analysis_run_id": state["waste_run_id"],
            }
            if "snapshot_id" in state:
                body["source_snapshot_id"] = state["snapshot_id"]
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/simulation/scenarios/{scenario_id}/execute",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json=body,
                )
            )
            state["simulation_run_id"] = data["simulation_run"]["id"]
            return state["simulation_run_id"]

        run.stages.append(_step("simulation", simulation, resources))

        def report() -> str:
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/reports/generate",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json={
                        "analysis_run_id": state["waste_run_id"],
                        "title": "Sprint D3 benchmark report",
                    },
                )
            )
            state["report_id"] = data["report"]["id"]
            return state["report_id"]

        run.stages.append(_step("report_generation", report, resources))

        def pdf() -> str:
            response = client.get(
                f"/organizations/{state['org_id']}/reports/{state['report_id']}/export",
                params={"format": "pdf"},
                headers={"Authorization": f"Bearer {state['token']}"},
            )
            response.raise_for_status()
            return f"bytes={len(response.content)}"

        run.stages.append(_step("pdf_export", pdf, resources))

    run.total_ms = _elapsed_ms(total_start)
    run.resources = {
        "peak_process_rss_mb": resources.peak_process_rss_mb,
        "peak_system_ram_used_mb": resources.peak_system_ram_used_mb,
        "peak_cpu_percent": resources.peak_cpu_percent,
        "peak_gpu_utilization_percent": resources.peak_gpu_utilization_percent,
        "peak_gpu_vram_used_mb": resources.peak_gpu_vram_used_mb,
    }
    return run, state


def main() -> int:
    print("Sprint D3 — AI Pipeline Benchmark")
    print(f"API: {API_BASE}")
    print(f"Workbook: {WORKBOOK}")

    hardware = collect_hardware_summary()
    print(f"Hardware: {hardware.processor}, RAM={hardware.total_ram_gb}GB, GPU={hardware.gpu_name}")

    # Health check
    try:
        httpx.get(f"{API_BASE}/api/v1/health", timeout=10).raise_for_status()
    except Exception as exc:
        print(f"Backend unavailable: {exc}", file=sys.stderr)
        return 1

    results: dict[str, Any] = {
        "hardware": asdict(hardware),
        "runs": [],
    }

    try:
        results["ingestion_substages"] = asdict(benchmark_ingestion_substages(WORKBOOK))
    except Exception as exc:
        results["ingestion_substages_error"] = str(exc)

    cold_ollama, warm_ollama = measure_ollama_latency()
    results["ollama_probe"] = {"cold_ms": cold_ollama, "warm_ms": warm_ollama}

    print("\n--- Full pipeline run ---")
    cold, cold_state = run_http_pipeline("full_pipeline")
    results["runs"].append(_serialize_run(cold))

    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults written to {RESULTS_PATH}")

    failed = sum(1 for r in results["runs"] for s in r["stages"] if not s["success"])
    _print_summary(results)
    return 1 if failed else 0


def _serialize_run(run: BenchmarkRun) -> dict[str, Any]:
    return {
        "label": run.label,
        "total_ms": run.total_ms,
        "stages": [asdict(s) for s in run.stages],
        "resources": run.resources,
    }


def _print_summary(results: dict[str, Any]) -> None:
    print("\n=== Benchmark Summary ===")
    for run in results.get("runs", []):
        print(f"\n{run['label']} — total {run['total_ms']}ms")
        for stage in run["stages"]:
            status = "OK" if stage["success"] else "FAIL"
            print(f"  [{status}] {stage['name']}: {stage['elapsed_ms']}ms — {stage['detail'][:80]}")
    if "ai_substages" in results:
        print("\nAI sub-stages (direct instrumentation):")
        for task in results["ai_substages"]:
            print(
                f"  {task['task']}: total={task['total_ms']}ms "
                f"(llm={task['llm_ms']}, ctx={task['context_ms']}, prompt={task['prompt_ms']}, parse={task['parser_ms']})"
            )
    probe = results.get("ollama_probe", {})
    if probe.get("cold_ms"):
        print(f"\nOllama probe: cold={probe['cold_ms']}ms warm={probe.get('warm_ms')}ms")


if __name__ == "__main__":
    raise SystemExit(main())
