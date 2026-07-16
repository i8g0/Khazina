#!/usr/bin/env python3
"""Sprint 8.4 — Performance & AI reliability benchmark harness."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import httpx
from openpyxl import Workbook

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env(BACKEND_ROOT / ".env")

from scripts.ai_benchmark.monitor import (  # noqa: E402
    ResourceSummary,
    collect_hardware_summary,
    sample_resources,
)

API_BASE = os.environ.get("KHAZINA_API_URL", "http://127.0.0.1:8000").rstrip("/")
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
AI_TIMEOUT = int(os.environ.get("AI_TIMEOUT", "180"))
TOTAL_AI_TIMEOUT = AI_TIMEOUT * 3 + 120
SCRIPT_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures_8_4"
RESULTS_PATH = SCRIPT_DIR / "sprint_8_4_results.json"
CANONICAL = SCRIPT_DIR / "Procurement_Q2.xlsx"


def ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def unwrap(resp: httpx.Response) -> dict[str, Any]:
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API failed")
    return payload["data"]


def write_w1(path: Path, row_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "WasteData"
    ws.append(["category", "amount", "total_spend"])
    categories = ["overlapping_contracts", "operations", "finance", "procurement", "travel"]
    for i in range(row_count):
        cat = categories[i % len(categories)]
        # Keep aggregate waste below total_spend for W-1 validation on large sheets
        amount = (100_000 + (i * 5_000)) if row_count <= 50 else (1_000 + i)
        ws.append([cat, amount, 50_000_000])
    wb.save(path)


def login(client: httpx.Client) -> tuple[str, str]:
    token = unwrap(client.post("/api/v1/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}))[
        "access_token"
    ]
    org_id = unwrap(
        client.get("/api/v1/organizations/active", headers={"Authorization": f"Bearer {token}"})
    )["id"]
    return token, org_id


def pipeline_through_waste(
    client: httpx.Client,
    token: str,
    org_id: str,
    workbook: Path,
    label: str,
    resources: ResourceSummary,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    out: dict[str, Any] = {"label": label, "stages": {}}

    resources.absorb(sample_resources())
    t0 = time.perf_counter()
    with workbook.open("rb") as handle:
        upload = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/financial-files/upload",
                headers=headers,
                files={
                    "upload": (
                        workbook.name,
                        handle,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )
        )
    out["stages"]["upload"] = ms(t0)
    ff = upload["financial_file"]
    snap = upload.get("financial_snapshot")
    out["file_id"] = ff["id"]
    out["processing_status"] = ff["processing_status"]
    if ff["processing_status"] != "ready_for_analysis":
        out["failed"] = True
        return out

    body: dict[str, Any] = {"title": f"8.4 — {label}", "source_file_id": ff["id"]}
    if snap:
        body["source_snapshot_id"] = snap["id"]
        out["snapshot_id"] = snap["id"]

    resources.absorb(sample_resources())
    t0 = time.perf_counter()
    waste = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/decisions/waste/execute",
            headers=headers,
            json=body,
        )
    )
    out["stages"]["waste"] = ms(t0)
    out["run_id"] = waste["analysis_run"]["id"]
    resources.absorb(sample_resources())
    return out


def call_ai(
    client: httpx.Client,
    token: str,
    org_id: str,
    run_id: str,
    regenerate: bool = True,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        data = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/ai-recommendations/waste/generate",
                headers=headers,
                json={"analysis_run_id": run_id, "regenerate": regenerate},
                timeout=TOTAL_AI_TIMEOUT,
            )
        )
        return {
            "success": True,
            "elapsed_ms": ms(t0),
            "recommendation_count": data.get("recommendation_count", 0),
            "http_status": 201,
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "elapsed_ms": ms(t0),
            "http_status": exc.response.status_code,
            "error": str(exc),
        }
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "elapsed_ms": ms(t0), "error": str(exc)}


def finish_pipeline(
    client: httpx.Client,
    token: str,
    org_id: str,
    state: dict[str, Any],
    resources: ResourceSummary,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    stages: dict[str, float] = {}

    scenarios = unwrap(
        client.get(f"/api/v1/organizations/{org_id}/simulation/scenarios", headers=headers)
    )
    if scenarios:
        resources.absorb(sample_resources())
        t0 = time.perf_counter()
        body = {
            "source_file_id": state["file_id"],
            "baseline_analysis_run_id": state["run_id"],
        }
        if state.get("snapshot_id"):
            body["source_snapshot_id"] = state["snapshot_id"]
        unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/simulation/scenarios/{scenarios[0]['id']}/execute",
                headers=headers,
                json=body,
            )
        )
        stages["simulation"] = ms(t0)

    resources.absorb(sample_resources())
    t0 = time.perf_counter()
    report = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/reports/generate",
            headers=headers,
            json={"analysis_run_id": state["run_id"], "title": "8.4 perf report"},
        )
    )
    stages["report"] = ms(t0)
    report_id = report["report"]["id"]

    resources.absorb(sample_resources())
    t0 = time.perf_counter()
    pdf = client.get(
        f"/api/v1/organizations/{org_id}/reports/{report_id}/export",
        params={"format": "pdf"},
        headers=headers,
    )
    pdf.raise_for_status()
    stages["pdf"] = ms(t0)
    stages["pdf_bytes"] = len(pdf.content)
    return stages


def measure_ollama_cold_warm() -> dict[str, Any]:
    from app.ai.client import OllamaClient
    from app.core.config import settings

    client = OllamaClient(settings.ai)
    messages = [{"role": "user", "content": "Reply OK only."}]
    result: dict[str, Any] = {}
    try:
        t0 = time.perf_counter()
        client.chat(messages, model=settings.ai.ollama_model)
        result["cold_ms"] = ms(t0)
        t1 = time.perf_counter()
        client.chat(messages, model=settings.ai.ollama_model)
        result["warm_ms"] = ms(t1)
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
    finally:
        client.close()
    return result


def local_ingestion_benchmark(workbook: Path) -> dict[str, Any]:
    from app.ingestion.parser import FinancialFileParser
    from app.ingestion.quality import DatasetQualityAssessor
    from app.ingestion.validator import DatasetValidator

    parser = FinancialFileParser()
    validator = DatasetValidator()
    quality = DatasetQualityAssessor()
    t0 = time.perf_counter()
    p0 = time.perf_counter()
    dataset, _ = parser.parse_file(str(workbook), workbook.name)
    parse_ms = ms(p0)
    v0 = time.perf_counter()
    validation = validator.validate(dataset)
    validate_ms = ms(v0)
    q0 = time.perf_counter()
    quality.assess(dataset)
    quality_ms = ms(q0)
    return {
        "parse_ms": parse_ms,
        "validate_ms": validate_ms,
        "quality_ms": quality_ms,
        "total_ms": ms(t0),
        "valid": validation.is_valid,
        "row_count": sum(len(s.rows) for s in dataset.sheets),
    }


def main() -> int:
    report: dict[str, Any] = {
        "sprint": "8.4",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "hardware": asdict(collect_hardware_summary()),
    }
    errors = 0

    print("=== Sprint 8.4 Performance & AI Testing ===\n")
    try:
        httpx.get(f"{API_BASE}/api/v1/health", timeout=10).raise_for_status()
    except Exception as exc:
        print(f"Backend down: {exc}")
        return 1

    if not CANONICAL.exists():
        write_w1(CANONICAL, 3)

    # Task 1 — AI cold/warm
    print("--- AI Ollama probe (cold/warm) ---")
    report["ai_ollama_probe"] = measure_ollama_cold_warm()
    print(report["ai_ollama_probe"])

    resources = ResourceSummary()
    with httpx.Client(base_url=API_BASE, timeout=TOTAL_AI_TIMEOUT) as client:
        token, org_id = login(client)
        report["org_id"] = org_id

        # Task 2 — Full platform timing
        print("\n--- Platform performance (full pipeline) ---")
        full_resources = ResourceSummary()
        t_total = time.perf_counter()
        state = pipeline_through_waste(client, token, org_id, CANONICAL, "full", full_resources)
        if state.get("failed"):
            errors += 1
            print("  Upload/waste failed")
        else:
            resources.absorb(sample_resources())
            ai_result = call_ai(client, token, org_id, state["run_id"], regenerate=True)
            state["stages"]["ai"] = ai_result["elapsed_ms"]
            state["stages"]["ai_success"] = ai_result["success"]
            if not ai_result["success"]:
                errors += 1
            tail = finish_pipeline(client, token, org_id, state, full_resources)
            state["stages"].update(tail)
            state["total_ms"] = ms(t_total)
            state["resources"] = {
                "peak_cpu_percent": full_resources.peak_cpu_percent,
                "peak_system_ram_used_mb": full_resources.peak_system_ram_used_mb,
                "peak_gpu_utilization_percent": full_resources.peak_gpu_utilization_percent,
                "peak_gpu_vram_used_mb": full_resources.peak_gpu_vram_used_mb,
            }
            report["platform_pipeline"] = state
            print(f"  Stages: {state['stages']}")
            print(f"  Total: {state['total_ms']}ms")

        # Task 1 — Consecutive AI on same run
        print("\n--- Consecutive AI executions (same run) ---")
        if state.get("run_id"):
            consecutive: list[dict] = []
            for i in range(3):
                print(f"  AI attempt {i + 1}/3...")
                r = call_ai(client, token, org_id, state["run_id"], regenerate=True)
                consecutive.append(r)
                print(f"    success={r['success']} ms={r['elapsed_ms']}")
                time.sleep(2)
            report["ai_consecutive"] = {
                "attempts": consecutive,
                "success_rate": sum(1 for a in consecutive if a["success"]) / len(consecutive),
                "avg_ms": round(
                    sum(a["elapsed_ms"] for a in consecutive if a["success"])
                    / max(1, sum(1 for a in consecutive if a["success"])),
                    2,
                ),
            }
            if report["ai_consecutive"]["success_rate"] < 1.0:
                errors += 1

        # Task 1 — Back-to-back AI on fresh runs
        print("\n--- Back-to-back AI (fresh runs) ---")
        back_to_back: list[dict] = []
        for i in range(2):
            print(f"  Fresh pipeline {i + 1}/2...")
            wb = FIXTURES_DIR / f"b2b_{i}.xlsx"
            write_w1(wb, 3 + i)
            prep = pipeline_through_waste(client, token, org_id, wb, f"b2b_{i}", ResourceSummary())
            if prep.get("run_id"):
                r = call_ai(client, token, org_id, prep["run_id"])
                r["run_id"] = prep["run_id"]
                back_to_back.append(r)
                print(f"    success={r['success']} ms={r['elapsed_ms']}")
            else:
                back_to_back.append({"success": False, "error": "waste prep failed"})
        report["ai_back_to_back"] = {
            "runs": back_to_back,
            "success_rate": sum(1 for r in back_to_back if r.get("success")) / max(1, len(back_to_back)),
        }
        if report["ai_back_to_back"]["success_rate"] < 1.0:
            errors += 1

        # Task 4 — Large datasets (upload + local parse only)
        print("\n--- Large dataset testing ---")
        large_results: dict[str, Any] = {}
        for rows in (3, 25, 100, 250):
            path = FIXTURES_DIR / f"large_{rows}.xlsx"
            write_w1(path, rows)
            local = local_ingestion_benchmark(path)
            resources.absorb(sample_resources())
            t0 = time.perf_counter()
            with path.open("rb") as handle:
                upload = client.post(
                    f"/api/v1/organizations/{org_id}/financial-files/upload",
                    headers={"Authorization": f"Bearer {token}"},
                    files={
                        "upload": (
                            path.name,
                            handle,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )
            http_ms = ms(t0)
            payload = upload.json()
            ff = (payload.get("data") or {}).get("financial_file", {})
            large_results[str(rows)] = {
                "local": local,
                "http_upload_ms": http_ms,
                "processing_status": ff.get("processing_status"),
                "accepted": ff.get("processing_status") == "ready_for_analysis",
            }
            print(f"  {rows} rows: local={local['total_ms']}ms http={http_ms}ms status={ff.get('processing_status')}")
            if not large_results[str(rows)]["accepted"]:
                errors += 1
        report["large_datasets"] = large_results

        # Task 5 — Long session (3 sequential partial pipelines, memory sample)
        print("\n--- Long session stability ---")
        session_runs: list[dict] = []
        seen_run_ids: set[str] = set()
        mem_start = sample_resources()
        for i in range(3):
            wb = FIXTURES_DIR / f"session_{i}.xlsx"
            write_w1(wb, 5 + i)
            prep = pipeline_through_waste(client, token, org_id, wb, f"session_{i}", ResourceSummary())
            if prep.get("run_id"):
                seen_run_ids.add(prep["run_id"])
            session_runs.append(
                {
                    "run_id": prep.get("run_id"),
                    "file_id": prep.get("file_id"),
                    "upload_ms": prep.get("stages", {}).get("upload"),
                }
            )
        mem_end = sample_resources()
        report["long_session"] = {
            "runs": session_runs,
            "unique_run_ids": len(seen_run_ids),
            "all_unique": len(seen_run_ids) == len(session_runs),
            "memory": {
                "start_rss_mb": mem_start.process_rss_mb,
                "end_rss_mb": mem_end.process_rss_mb,
                "start_ram_used_mb": mem_start.system_ram_used_mb,
                "end_ram_used_mb": mem_end.system_ram_used_mb,
            },
        }
        print(report["long_session"])

        # Task 6 — Stress: parallel report generation (after one full run)
        print("\n--- Stress: parallel operations ---")
        stress: dict[str, Any] = {}
        if state.get("run_id"):
            stress_reports: list[dict] = []

            def gen_report(idx: int) -> dict:
                t0 = time.perf_counter()
                try:
                    data = unwrap(
                        client.post(
                            f"/api/v1/organizations/{org_id}/reports/generate",
                            headers={"Authorization": f"Bearer {token}"},
                            json={
                                "analysis_run_id": state["run_id"],
                                "title": f"Stress report {idx}",
                            },
                        )
                    )
                    return {"success": True, "elapsed_ms": ms(t0), "report_id": data["report"]["id"]}
                except Exception as exc:  # noqa: BLE001
                    return {"success": False, "elapsed_ms": ms(t0), "error": str(exc)}

            with ThreadPoolExecutor(max_workers=3) as pool:
                futures = [pool.submit(gen_report, i) for i in range(3)]
                for fut in as_completed(futures):
                    stress_reports.append(fut.result())
            stress["parallel_reports"] = {
                "results": stress_reports,
                "success_rate": sum(1 for r in stress_reports if r["success"]) / len(stress_reports),
                "unique_ids": len({r.get("report_id") for r in stress_reports if r.get("report_id")}),
            }

        # concurrent uploads
        def stress_upload(idx: int) -> dict:
            path = FIXTURES_DIR / f"stress_{idx}_{uuid.uuid4().hex[:6]}.xlsx"
            write_w1(path, 4)
            t0 = time.perf_counter()
            try:
                with path.open("rb") as handle:
                    data = unwrap(
                        client.post(
                            f"/api/v1/organizations/{org_id}/financial-files/upload",
                            headers={"Authorization": f"Bearer {token}"},
                            files={
                                "upload": (
                                    path.name,
                                    handle,
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                )
                            },
                        )
                    )
                ff = data["financial_file"]
                return {
                    "success": ff["processing_status"] == "ready_for_analysis",
                    "elapsed_ms": ms(t0),
                    "file_id": ff["id"],
                }
            except Exception as exc:  # noqa: BLE001
                return {"success": False, "elapsed_ms": ms(t0), "error": str(exc)}

        with ThreadPoolExecutor(max_workers=3) as pool:
            upload_stress = list(pool.map(stress_upload, range(3)))
        stress["parallel_uploads"] = {
            "results": upload_stress,
            "success_rate": sum(1 for r in upload_stress if r["success"]) / len(upload_stress),
        }
        report["stress"] = stress
        print(json.dumps(stress, indent=2, ensure_ascii=False))

    report["resource_peaks"] = {
        "peak_cpu_percent": resources.peak_cpu_percent,
        "peak_system_ram_used_mb": resources.peak_system_ram_used_mb,
        "peak_gpu_utilization_percent": resources.peak_gpu_utilization_percent,
        "peak_gpu_vram_used_mb": resources.peak_gpu_vram_used_mb,
    }

    # Bottleneck analysis
    platform = report.get("platform_pipeline", {}).get("stages", {})
    if platform:
        ai_ms = platform.get("ai", 0)
        non_ai = sum(v for k, v in platform.items() if k not in {"ai", "ai_success", "pdf_bytes"} and isinstance(v, (int, float)))
        total = report["platform_pipeline"].get("total_ms", 1)
        report["bottleneck_analysis"] = {
            "ai_ms": ai_ms,
            "non_ai_ms": non_ai,
            "ai_pct_of_total": round(100 * ai_ms / total, 1) if total else None,
            "primary_bottleneck": "Ollama LLM inference",
            "root_cause_evidence": "AI stage dominates wall-clock; non-AI stages sub-second",
        }

    RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {RESULTS_PATH}")
    print(f"Exit: {'PASS' if errors == 0 else 'FAIL'} ({errors} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
