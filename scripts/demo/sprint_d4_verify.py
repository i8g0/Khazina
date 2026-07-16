#!/usr/bin/env python3
"""Sprint D4 — universal Excel pipeline verification across workbook variants."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx
from openpyxl import Workbook

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.orchestrator import IngestionOrchestrator  # noqa: E402
from app.ingestion.exceptions import ValidationFailure, ParseError  # noqa: E402

API_BASE = "http://127.0.0.1:8000"
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
AI_TIMEOUT = 180
SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = SCRIPT_DIR / "sprint_d4_results.json"
FIXTURES_DIR = SCRIPT_DIR / "fixtures_d4"
DEMO_WORKBOOK = SCRIPT_DIR / "Procurement_Q2.xlsx"


def write_workbook(path: Path, sheet_name: str, headers: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    sheet = wb.active
    sheet.title = sheet_name
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    wb.save(path)


def generate_fixtures() -> dict[str, Path]:
    fixtures: dict[str, Path] = {}

    demo = DEMO_WORKBOOK
    if not demo.exists():
        write_workbook(
            demo,
            "WasteData",
            ["category", "amount", "total_spend"],
            [
                ["overlapping_contracts", 745_000, 50_000_000],
                ["operations", 520_000, 50_000_000],
                ["finance", 1_075_000, 50_000_000],
            ],
        )
    fixtures["demo_workbook"] = demo

    canonical = FIXTURES_DIR / "canonical.xlsx"
    write_workbook(
        canonical,
        "WasteData",
        ["category", "amount", "total_spend"],
        [
            ["overlapping_contracts", 745_000, 50_000_000],
            ["operations", 520_000, 50_000_000],
            ["finance", 1_075_000, 50_000_000],
        ],
    )
    fixtures["canonical"] = canonical

    different_values = FIXTURES_DIR / "different_values.xlsx"
    write_workbook(
        different_values,
        "FinancialWaste",
        ["category", "amount", "total_spend"],
        [
            ["overlapping_contracts", 1_200_000, 80_000_000],
            ["operations", 300_000, 80_000_000],
            ["finance", 450_000, 80_000_000],
        ],
    )
    fixtures["different_values"] = different_values

    extended_rows = FIXTURES_DIR / "extended_rows.xlsx"
    write_workbook(
        extended_rows,
        "Sheet1",
        ["category", "amount", "total_spend"],
        [
            ["overlapping_contracts", 100_000, 20_000_000],
            ["operations", 200_000, 20_000_000],
            ["finance", 300_000, 20_000_000],
            ["procurement", 150_000, 20_000_000],
            ["travel", 50_000, 20_000_000],
        ],
    )
    fixtures["extended_rows"] = extended_rows

    reordered = FIXTURES_DIR / "reordered_rows.xlsx"
    write_workbook(
        reordered,
        "Q2Data",
        ["category", "amount", "total_spend"],
        [
            ["finance", 1_075_000, 50_000_000],
            ["overlapping_contracts", 745_000, 50_000_000],
            ["operations", 520_000, 50_000_000],
        ],
    )
    fixtures["reordered_rows"] = reordered

    arabic = FIXTURES_DIR / "arabic_headers.xlsx"
    write_workbook(
        arabic,
        "بيانات",
        ["تصنيف", "مبلغ", "إجمالي_الإنفاق"],
        [
            ["operations", 520_000, 50_000_000],
            ["finance", 1_075_000, 50_000_000],
            ["overlapping_contracts", 745_000, 50_000_000],
        ],
    )
    fixtures["arabic_headers"] = arabic

    invalid = FIXTURES_DIR / "invalid_layout.xlsx"
    write_workbook(
        invalid,
        "Budget",
        ["department", "budget", "actual"],
        [["IT", 100_000, 90_000]],
    )
    fixtures["invalid_layout"] = invalid

    return fixtures


def local_ingest_test(path: Path) -> dict:
    orchestrator = IngestionOrchestrator()
    start = time.perf_counter()
    try:
        result = orchestrator.run(str(path), path.name)
        return {
            "accepted": True,
            "record_count": result.record_count,
            "quality_score": result.quality.overall_score,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except (ValidationFailure, ParseError) as exc:
        return {
            "accepted": False,
            "error": str(exc),
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 2),
        }


def unwrap(response: httpx.Response) -> dict:
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API failed")
    return payload["data"]


def http_pipeline(client: httpx.Client, token: str, org_id: str, workbook: Path) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    out: dict = {"file_name": workbook.name}

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
    ff = upload["financial_file"]
    snap = upload.get("financial_snapshot")
    out["file_id"] = ff["id"]
    out["status"] = ff["processing_status"]
    if snap:
        out["snapshot_id"] = snap["id"]
    if ff["processing_status"] != "ready_for_analysis":
        out["accepted"] = False
        out["error"] = ff.get("processing_status")
        return out

    body = {"title": f"D4 — {workbook.stem}", "source_file_id": ff["id"]}
    if snap:
        body["source_snapshot_id"] = snap["id"]
    waste = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/decisions/waste/execute",
            headers=headers,
            json=body,
        )
    )
    run_id = waste["analysis_run"]["id"]
    waste_result = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/analysis-runs/{run_id}/waste/result",
            headers=headers,
        )
    )
    out["waste_total"] = waste_result["total_waste_amount"]
    out["waste_pct"] = waste_result["waste_percentage"]
    out["run_id"] = run_id

    scenarios = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/simulation/scenarios",
            headers=headers,
        )
    )
    if scenarios:
        scenario = scenarios[0]
        sim_body = {
            "source_file_id": ff["id"],
            "baseline_analysis_run_id": run_id,
        }
        if snap:
            sim_body["source_snapshot_id"] = snap["id"]
        sim = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/simulation/scenarios/{scenario['id']}/execute",
                headers=headers,
                json=sim_body,
            )
        )
        out["simulation_run_id"] = sim["simulation_run"]["id"]

    ai = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/ai-recommendations/waste/generate",
            headers=headers,
            json={"analysis_run_id": run_id, "regenerate": True},
            timeout=AI_TIMEOUT * 3 + 60,
        )
    )
    out["recommendation_count"] = ai.get("recommendation_count", 0)

    report = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/reports/generate",
            headers=headers,
            json={"analysis_run_id": run_id, "title": f"Report — {workbook.stem}"},
        )
    )
    report_id = report["report"]["id"]
    out["report_id"] = report_id

    pdf = client.get(
        f"/api/v1/organizations/{org_id}/reports/{report_id}/export",
        params={"format": "pdf"},
        headers=headers,
    )
    pdf.raise_for_status()
    out["pdf_bytes"] = len(pdf.content)
    out["accepted"] = True
    return out


def main() -> int:
    fixtures = generate_fixtures()
    report: dict = {"fixtures": {k: str(v.name) for k, v in fixtures.items()}, "local": {}, "http": {}}

    print("=== Local ingestion tests ===")
    for name, path in fixtures.items():
        result = local_ingest_test(path)
        report["local"][name] = result
        status = "ACCEPT" if result.get("accepted") else "REJECT"
        print(f"  [{status}] {name}: {result}")

    try:
        httpx.get(f"{API_BASE}/api/v1/health", timeout=5).raise_for_status()
        backend_ok = True
    except Exception as exc:
        backend_ok = False
        report["http"]["error"] = f"Backend unavailable: {exc}"

    if backend_ok:
        print("\n=== HTTP pipeline tests (valid workbooks) ===")
        with httpx.Client(base_url=API_BASE, timeout=AI_TIMEOUT * 3 + 60) as client:
            token = unwrap(
                client.post("/api/v1/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
            )["access_token"]
            org_id = unwrap(
                client.get(
                    "/api/v1/organizations/active",
                    headers={"Authorization": f"Bearer {token}"},
                )
            )["id"]
            report["http"]["org_id"] = org_id
            seen_ids: dict[str, set[str]] = {
                "file_id": set(),
                "snapshot_id": set(),
                "run_id": set(),
                "report_id": set(),
            }
            pipeline_names = (
                "demo_workbook",
                "canonical",
                "different_values",
                "extended_rows",
                "reordered_rows",
                "arabic_headers",
            )
            for name in pipeline_names:
                print(f"  Running pipeline: {name}...")
                try:
                    result = http_pipeline(client, token, org_id, fixtures[name])
                    report["http"][name] = result
                    for key in seen_ids:
                        if result.get(key):
                            seen_ids[key].add(str(result[key]))
                    print(
                        f"    OK waste_total={result.get('waste_total')} "
                        f"recs={result.get('recommendation_count')} pdf={result.get('pdf_bytes')}"
                    )
                except Exception as exc:  # noqa: BLE001
                    report["http"][name] = {"accepted": False, "error": str(exc)}
                    print(f"    FAIL: {exc}")

            report["http"]["freshness"] = {
                key: {"unique_count": len(values), "all_unique": len(values) == len(pipeline_names)}
                for key, values in seen_ids.items()
            }

            invalid = fixtures["invalid_layout"]
            print("  Running invalid layout upload...")
            try:
                with invalid.open("rb") as handle:
                    resp = client.post(
                        f"/api/v1/organizations/{org_id}/financial-files/upload",
                        headers={"Authorization": f"Bearer {token}"},
                        files={
                            "upload": (
                                invalid.name,
                                handle,
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )
                        },
                    )
                payload = resp.json()
                if payload.get("success"):
                    ff = payload["data"]["financial_file"]
                    report["http"]["invalid_layout"] = {
                        "accepted": ff["processing_status"] == "ready_for_analysis",
                        "status": ff["processing_status"],
                    }
                else:
                    report["http"]["invalid_layout"] = {
                        "accepted": False,
                        "status": "rejected",
                        "message": payload.get("message"),
                    }
            except Exception as exc:  # noqa: BLE001
                report["http"]["invalid_layout"] = {"accepted": False, "error": str(exc)}

    RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {RESULTS_PATH}")

    errors = 0
    for name, result in report["local"].items():
        if name == "invalid_layout":
            if result.get("accepted"):
                errors += 1
        elif not result.get("accepted"):
            errors += 1
    if backend_ok:
        for name in (
            "demo_workbook",
            "canonical",
            "different_values",
            "extended_rows",
            "reordered_rows",
            "arabic_headers",
        ):
            if not report["http"].get(name, {}).get("accepted"):
                errors += 1
        if report["http"].get("invalid_layout", {}).get("accepted"):
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
