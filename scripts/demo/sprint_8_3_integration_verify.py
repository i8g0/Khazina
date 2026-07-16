#!/usr/bin/env python3
"""Sprint 8.3 — Integration testing & end-to-end validation harness."""

from __future__ import annotations

import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx
from openpyxl import Workbook

API_BASE = "http://127.0.0.1:8000"
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
AI_TIMEOUT = 180
SCRIPT_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures_8_3"
RESULTS_PATH = SCRIPT_DIR / "sprint_8_3_results.json"


def write_workbook(path: Path, sheet: str, headers: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)


def generate_fixtures() -> dict[str, Path]:
    fixtures: dict[str, Path] = {}

    dataset_a = FIXTURES_DIR / "dataset_a.xlsx"
    write_workbook(
        dataset_a,
        "WasteData",
        ["category", "amount", "total_spend"],
        [
            ["overlapping_contracts", 745_000, 50_000_000],
            ["operations", 520_000, 50_000_000],
            ["finance", 1_075_000, 50_000_000],
        ],
    )
    fixtures["dataset_a"] = dataset_a

    dataset_b = FIXTURES_DIR / "dataset_b.xlsx"
    write_workbook(
        dataset_b,
        "FinancialWaste",
        ["category", "amount", "total_spend"],
        [
            ["overlapping_contracts", 1_200_000, 80_000_000],
            ["operations", 300_000, 80_000_000],
            ["finance", 450_000, 80_000_000],
        ],
    )
    fixtures["dataset_b"] = dataset_b

    invalid = FIXTURES_DIR / "invalid_layout.xlsx"
    write_workbook(
        invalid,
        "Budget",
        ["department", "budget", "actual"],
        [["IT", 100_000, 90_000]],
    )
    fixtures["invalid_layout"] = invalid

    empty = FIXTURES_DIR / "empty_sheet.xlsx"
    write_workbook(empty, "Empty", ["category", "amount", "total_spend"], [])
    fixtures["empty_sheet"] = empty

    corrupted = FIXTURES_DIR / "corrupted.xlsx"
    corrupted.write_bytes(b"NOT_A_VALID_XLSX_FILE_" + b"\x00" * 64)
    fixtures["corrupted"] = corrupted

    return fixtures


def unwrap(response: httpx.Response) -> dict:
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API failed")
    return payload["data"]


def login(client: httpx.Client) -> tuple[str, str]:
    token = unwrap(
        client.post("/api/v1/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    )["access_token"]
    org_id = unwrap(
        client.get("/api/v1/organizations/active", headers={"Authorization": f"Bearer {token}"})
    )["id"]
    return token, org_id


def upload_file(
    client: httpx.Client,
    token: str,
    org_id: str,
    workbook: Path,
) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    with workbook.open("rb") as handle:
        resp = client.post(
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
    payload = resp.json()
    return {
        "http_status": resp.status_code,
        "success": payload.get("success"),
        "message": payload.get("message"),
        "data": payload.get("data"),
    }


def full_pipeline(
    client: httpx.Client,
    token: str,
    org_id: str,
    workbook: Path,
    label: str,
) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    out: dict = {"label": label, "accepted": False}

    upload_result = upload_file(client, token, org_id, workbook)
    if not upload_result.get("success") or not upload_result.get("data"):
        out["error"] = upload_result.get("message") or "upload failed"
        out["upload"] = upload_result
        return out

    ff = upload_result["data"]["financial_file"]
    snap = upload_result["data"].get("financial_snapshot")
    out["file_id"] = ff["id"]
    out["processing_status"] = ff["processing_status"]
    if snap:
        out["snapshot_id"] = snap["id"]

    if ff["processing_status"] != "ready_for_analysis":
        out["error"] = f"processing_status={ff['processing_status']}"
        return out

    body: dict = {"title": f"8.3 — {label}", "source_file_id": ff["id"]}
    if snap:
        body["source_snapshot_id"] = snap["id"]

    waste = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/decisions/waste/execute",
            headers=headers,
            json=body,
        )
    )
    run = waste["analysis_run"]
    out["run_id"] = run["id"]
    out["run_source_file_id"] = run.get("source_file_id")
    out["run_source_snapshot_id"] = run.get("source_snapshot_id")

    waste_result = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/analysis-runs/{run['id']}/waste/result",
            headers=headers,
        )
    )
    out["waste_total"] = waste_result["total_waste_amount"]

    scenarios = unwrap(
        client.get(f"/api/v1/organizations/{org_id}/simulation/scenarios", headers=headers)
    )
    if scenarios:
        sim_body = {"source_file_id": ff["id"], "baseline_analysis_run_id": run["id"]}
        if snap:
            sim_body["source_snapshot_id"] = snap["id"]
        sim = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/simulation/scenarios/{scenarios[0]['id']}/execute",
                headers=headers,
                json=sim_body,
            )
        )
        out["simulation_run_id"] = sim["simulation_run"]["id"]

    ai = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/ai-recommendations/waste/generate",
            headers=headers,
            json={"analysis_run_id": run["id"], "regenerate": True},
            timeout=AI_TIMEOUT * 3 + 60,
        )
    )
    out["recommendation_count"] = ai.get("recommendation_count", 0)
    out["ai_run_id"] = ai["analysis_run"]["id"]

    report = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/reports/generate",
            headers=headers,
            json={"analysis_run_id": run["id"], "title": f"Report — {label}"},
        )
    )
    report_id = report["report"]["id"]
    out["report_id"] = report_id
    out["report_analysis_run_id"] = report["report"].get("analysis_run_id")

    content = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/reports/{report_id}/content",
            headers=headers,
        )
    )
    out["report_has_content"] = bool(content.get("sections"))

    pdf = client.get(
        f"/api/v1/organizations/{org_id}/reports/{report_id}/export",
        params={"format": "pdf"},
        headers=headers,
    )
    pdf.raise_for_status()
    out["pdf_bytes"] = len(pdf.content)
    out["pdf_content_type"] = pdf.headers.get("content-type")

    out["accepted"] = True
    out["integrity"] = {
        "run_matches_file": out["run_source_file_id"] == ff["id"],
        "run_matches_snapshot": (not snap) or out["run_source_snapshot_id"] == snap["id"],
        "ai_run_matches": out["ai_run_id"] == run["id"],
        "report_run_matches": out["report_analysis_run_id"] == run["id"],
        "pdf_nonempty": out["pdf_bytes"] > 1000,
    }
    return out


def test_auth_failures(client: httpx.Client, org_id: str) -> dict:
    results: dict = {}
    bad_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
    resp = client.get(
        f"/api/v1/organizations/{org_id}/analysis-runs",
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    results["invalid_token"] = {
        "status": resp.status_code,
        "success": resp.json().get("success"),
        "graceful": resp.status_code == 401 and resp.json().get("success") is False,
    }

    resp = client.get(f"/api/v1/organizations/{org_id}/analysis-runs")
    results["missing_token"] = {
        "status": resp.status_code,
        "graceful": resp.status_code == 401,
    }
    return results


def test_health_endpoints(client: httpx.Client) -> dict:
    health = unwrap(client.get("/api/v1/health"))
    ai = unwrap(client.get("/api/v1/ai/health"))
    return {
        "system_health": health,
        "ai_health": ai,
        "ai_reachable": ai.get("ollama_reachable", False),
    }


def test_failure_uploads(client: httpx.Client, token: str, org_id: str, fixtures: dict[str, Path]) -> dict:
    results: dict = {}
    for name in ("invalid_layout", "empty_sheet", "corrupted"):
        upload = upload_file(client, token, org_id, fixtures[name])
        ff = (upload.get("data") or {}).get("financial_file") if upload.get("data") else None
        status = ff["processing_status"] if ff else None
        results[name] = {
            "http_status": upload.get("http_status"),
            "api_success": upload.get("success"),
            "processing_status": status,
            "rejected": status in {"failed", None} or upload.get("success") is False,
            "message": upload.get("message"),
        }
    return results


def test_concurrent_uploads(client: httpx.Client, token: str, org_id: str, workbook: Path, count: int = 3) -> dict:
    file_ids: list[str] = []
    errors: list[str] = []

    def _upload(idx: int) -> str | None:
        copy_path = FIXTURES_DIR / f"concurrent_{idx}_{uuid.uuid4().hex[:8]}.xlsx"
        write_workbook(
            copy_path,
            "WasteData",
            ["category", "amount", "total_spend"],
            [
                ["overlapping_contracts", 100_000 + idx * 10_000, 10_000_000],
                ["operations", 200_000, 10_000_000],
                ["finance", 300_000, 10_000_000],
            ],
        )
        result = upload_file(client, token, org_id, copy_path)
        ff = (result.get("data") or {}).get("financial_file")
        if ff and ff.get("processing_status") == "ready_for_analysis":
            return ff["id"]
        errors.append(result.get("message") or "upload failed")
        return None

    with ThreadPoolExecutor(max_workers=count) as pool:
        futures = [pool.submit(_upload, i) for i in range(count)]
        for fut in as_completed(futures):
            fid = fut.result()
            if fid:
                file_ids.append(fid)

    return {
        "requested": count,
        "succeeded": len(file_ids),
        "unique_file_ids": len(set(file_ids)),
        "all_unique": len(set(file_ids)) == len(file_ids),
        "errors": errors[:5],
    }


def main() -> int:
    fixtures = generate_fixtures()
    report: dict = {
        "sprint": "8.3",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "scenarios": {},
    }
    errors = 0

    print("=== Sprint 8.3 Integration Verification ===\n")

    try:
        httpx.get(f"{API_BASE}/api/v1/health", timeout=5).raise_for_status()
    except Exception as exc:
        report["scenarios"]["backend_available"] = {"ok": False, "error": str(exc)}
        RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Backend unavailable: {exc}")
        return 1

    report["scenarios"]["backend_available"] = {"ok": True}

    with httpx.Client(base_url=API_BASE, timeout=AI_TIMEOUT * 3 + 120) as client:
        report["scenarios"]["health"] = test_health_endpoints(client)
        print(f"Health: system={report['scenarios']['health']['system_health'].get('status')} "
              f"ai_reachable={report['scenarios']['health']['ai_reachable']}")

        token, org_id = login(client)
        report["org_id"] = org_id
        report["scenarios"]["auth_failures"] = test_auth_failures(client, org_id)
        print(f"Auth failures: {report['scenarios']['auth_failures']}")

        print("\n--- Task 1: End-to-end pipeline (dataset A) ---")
        try:
            e2e = full_pipeline(client, token, org_id, fixtures["dataset_a"], "dataset_a")
            report["scenarios"]["e2e_pipeline"] = e2e
            if not e2e.get("accepted"):
                errors += 1
                print(f"  FAIL: {e2e.get('error')}")
            else:
                print(
                    f"  OK waste={e2e['waste_total']} pdf={e2e['pdf_bytes']} "
                    f"integrity={e2e.get('integrity')}"
                )
        except Exception as exc:
            report["scenarios"]["e2e_pipeline"] = {"accepted": False, "error": str(exc)}
            errors += 1
            print(f"  FAIL: {exc}")

        print("\n--- Task 2: Multiple independent datasets ---")
        multi: dict = {}
        waste_totals: list[float] = []
        all_ids: dict[str, set[str]] = {k: set() for k in ("file_id", "snapshot_id", "run_id", "report_id")}
        for label in ("dataset_a", "dataset_b"):
            print(f"  Pipeline: {label}...")
            try:
                result = full_pipeline(client, token, org_id, fixtures[label], label)
                multi[label] = result
                if result.get("accepted"):
                    waste_totals.append(float(result["waste_total"]))
                    for key in all_ids:
                        if result.get(key):
                            all_ids[key].add(str(result[key]))
                else:
                    errors += 1
                    print(f"    FAIL: {result.get('error')}")
            except Exception as exc:
                multi[label] = {"accepted": False, "error": str(exc)}
                errors += 1
                print(f"    FAIL: {exc}")

        multi["isolation"] = {
            "waste_totals_differ": len(waste_totals) >= 2 and waste_totals[0] != waste_totals[1],
            "waste_totals": waste_totals,
            "ids_all_unique": {k: len(v) for k, v in all_ids.items()},
        }
        report["scenarios"]["multiple_datasets"] = multi
        if not multi["isolation"]["waste_totals_differ"]:
            errors += 1
        print(f"  Isolation: {multi['isolation']}")

        print("\n--- Task 3: Failure scenarios (upload) ---")
        failures = test_failure_uploads(client, token, org_id, fixtures)
        report["scenarios"]["failure_uploads"] = failures
        for name, result in failures.items():
            ok = result.get("rejected")
            if not ok:
                errors += 1
            print(f"  [{('PASS' if ok else 'FAIL')}] {name}: {result}")

        print("\n--- Task 4: Concurrent uploads ---")
        concurrent = test_concurrent_uploads(client, token, org_id, fixtures["dataset_a"])
        report["scenarios"]["concurrent_uploads"] = concurrent
        if concurrent["succeeded"] < 2 or not concurrent["all_unique"]:
            errors += 1
        print(f"  {concurrent}")

    RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {RESULTS_PATH}")
    print(f"\nExit: {'PASS' if errors == 0 else 'FAIL'} ({errors} error(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
