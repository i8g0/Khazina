#!/usr/bin/env python3
"""End-to-end verification for Khazina_Demo_Dataset_v2.xlsx."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

API_BASE = "http://127.0.0.1:8000"
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
AI_TIMEOUT = 180
WORKBOOK = Path(__file__).resolve().parent / "Khazina_Demo_Dataset_v2.xlsx"
RESULTS = Path(__file__).resolve().parent / "khazina_demo_v2_verify.json"


def unwrap(resp: httpx.Response) -> dict:
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API failed")
    return payload["data"]


def main() -> int:
    if not WORKBOOK.exists():
        print(f"Missing workbook: {WORKBOOK}", file=sys.stderr)
        return 1

    report: dict = {"workbook": str(WORKBOOK), "stages": {}, "ok": False}
    try:
        httpx.get(f"{API_BASE}/api/v1/health", timeout=5).raise_for_status()
    except Exception as exc:
        print(f"Backend unavailable: {exc}", file=sys.stderr)
        return 1

    with httpx.Client(base_url=API_BASE, timeout=AI_TIMEOUT * 3 + 120) as client:
        token = unwrap(
            client.post("/api/v1/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        )["access_token"]
        org_id = unwrap(
            client.get("/api/v1/organizations/active", headers={"Authorization": f"Bearer {token}"})
        )["id"]
        headers = {"Authorization": f"Bearer {token}"}

        t0 = time.perf_counter()
        with WORKBOOK.open("rb") as handle:
            upload = unwrap(
                client.post(
                    f"/api/v1/organizations/{org_id}/financial-files/upload",
                    headers=headers,
                    files={
                        "upload": (
                            WORKBOOK.name,
                            handle,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )
            )
        report["stages"]["upload_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        ff = upload["financial_file"]
        snap = upload.get("financial_snapshot")
        report["file_id"] = ff["id"]
        report["processing_status"] = ff["processing_status"]
        if ff["processing_status"] != "ready_for_analysis":
            print(f"Upload rejected: {ff['processing_status']}", file=sys.stderr)
            RESULTS.write_text(json.dumps(report, indent=2), encoding="utf-8")
            return 1

        body: dict = {"title": "NovaTech Gulf — Demo v2", "source_file_id": ff["id"]}
        if snap:
            body["source_snapshot_id"] = snap["id"]
            report["snapshot_id"] = snap["id"]

        t0 = time.perf_counter()
        waste = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/decisions/waste/execute",
                headers=headers,
                json=body,
            )
        )
        run_id = waste["analysis_run"]["id"]
        report["run_id"] = run_id
        report["stages"]["waste_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        waste_result = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/analysis-runs/{run_id}/waste/result",
                headers=headers,
            )
        )
        report["waste_total"] = waste_result["total_waste_amount"]
        report["waste_pct"] = waste_result["waste_percentage"]

        t0 = time.perf_counter()
        waste_ai = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/ai-recommendations/waste/generate",
                headers=headers,
                json={"analysis_run_id": run_id, "regenerate": True},
            )
        )
        report["stages"]["waste_ai_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        report["waste_recommendations"] = waste_ai.get("recommendation_count", 0)

        t0 = time.perf_counter()
        risk = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/risk-analyses/execute",
                headers=headers,
                json={
                    "title": "NovaTech Risk v2",
                    "source_file_id": ff["id"],
                    **({"source_snapshot_id": snap["id"]} if snap else {}),
                },
            )
        )
        risk_run_id = risk["analysis_run"]["id"]
        report["risk_run_id"] = risk_run_id
        report["stages"]["risk_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        risk_result = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/risk-analyses/{risk_run_id}/result",
                headers=headers,
            )
        )
        report["risk_score"] = risk_result.get("overall_risk_score")
        report["risk_findings"] = len(risk_result.get("findings") or [])

        t0 = time.perf_counter()
        risk_ai = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/ai-recommendations/risk/generate",
                headers=headers,
                json={"analysis_run_id": risk_run_id, "regenerate": True},
            )
        )
        report["stages"]["risk_ai_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        report["risk_recommendations"] = risk_ai.get("recommendation_count", 0)

        scenarios = unwrap(
            client.get(f"/api/v1/organizations/{org_id}/simulation/scenarios", headers=headers)
        )
        if scenarios:
            sim_body = {
                "source_file_id": ff["id"],
                "baseline_analysis_run_id": run_id,
            }
            if snap:
                sim_body["source_snapshot_id"] = snap["id"]
            t0 = time.perf_counter()
            sim = unwrap(
                client.post(
                    f"/api/v1/organizations/{org_id}/simulation/scenarios/{scenarios[0]['id']}/execute",
                    headers=headers,
                    json=sim_body,
                )
            )
            report["stages"]["simulation_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            report["simulation_run_id"] = sim["simulation_run"]["id"]

        t0 = time.perf_counter()
        report_doc = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/reports/generate",
                headers=headers,
                json={"analysis_run_id": run_id, "title": "NovaTech Executive Report v2"},
            )
        )
        report_id = report_doc["report"]["id"]
        report["report_id"] = report_id
        report["stages"]["report_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        t0 = time.perf_counter()
        pdf = client.get(
            f"/api/v1/organizations/{org_id}/reports/{report_id}/export",
            params={"format": "pdf"},
            headers=headers,
        )
        pdf.raise_for_status()
        report["stages"]["pdf_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        report["pdf_bytes"] = len(pdf.content)

        report["ok"] = True

    RESULTS.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
