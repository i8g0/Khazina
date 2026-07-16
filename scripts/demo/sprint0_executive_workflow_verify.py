#!/usr/bin/env python3
"""Sprint 0 — full executive workflow verification (no shortcuts)."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

API_BASE = os.environ.get("KHAZINA_API_URL", "http://127.0.0.1:8000").rstrip("/")
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
AI_TIMEOUT = 180
WORKBOOK = Path(__file__).resolve().parents[2] / "Khazina_Demo_Dataset_v2.xlsx"
RESULTS = Path(__file__).resolve().parent / "sprint0_workflow_results.json"


def log(msg: str) -> None:
    ts = datetime.now(UTC).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def unwrap(resp: httpx.Response, step: str) -> dict:
    if resp.status_code >= 400:
        body = resp.text[:4000]
        raise RuntimeError(f"{step} failed HTTP {resp.status_code}: {body}")
    payload = resp.json()
    if not payload.get("success"):
        raise RuntimeError(f"{step} failed: {payload.get('message')} | {payload}")
    return payload["data"]


def main() -> int:
    if not WORKBOOK.exists():
        log(f"ERROR: workbook missing: {WORKBOOK}")
        return 1

    report: dict = {
        "started_at": datetime.now(UTC).isoformat(),
        "workbook": str(WORKBOOK),
        "steps": {},
        "ok": False,
    }

    try:
        httpx.get(f"{API_BASE}/api/v1/health", timeout=15).raise_for_status()
    except Exception as exc:
        log(f"Backend unavailable: {exc}")
        return 1

    try:
        with httpx.Client(base_url=API_BASE, timeout=AI_TIMEOUT * 3 + 120) as client:
            # Login
            t0 = time.perf_counter()
            token = unwrap(
                client.post("/api/v1/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}),
                "login",
            )["access_token"]
            org_id = unwrap(
                client.get("/api/v1/organizations/active", headers={"Authorization": f"Bearer {token}"}),
                "active org",
            )["id"]
            report["steps"]["login"] = {"org_id": org_id, "ms": round((time.perf_counter() - t0) * 1000, 2)}
            log(f"Login OK — org={org_id}")
            h = {"Authorization": f"Bearer {token}"}

            # Upload
            t0 = time.perf_counter()
            with WORKBOOK.open("rb") as handle:
                upload = unwrap(
                    client.post(
                        f"/api/v1/organizations/{org_id}/financial-files/upload",
                        headers=h,
                        files={
                            "upload": (
                                WORKBOOK.name,
                                handle,
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )
                        },
                    ),
                    "upload",
                )
            ff = upload["financial_file"]
            snap = upload.get("financial_snapshot")
            if ff["processing_status"] != "ready_for_analysis":
                raise RuntimeError(f"upload rejected: {ff['processing_status']}")
            report["steps"]["upload"] = {
                "file_id": ff["id"],
                "snapshot_id": snap["id"] if snap else None,
                "status": ff["processing_status"],
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"Upload OK — file={ff['id']}")

            body: dict = {"title": "Sprint0 Executive Workflow", "source_file_id": ff["id"]}
            if snap:
                body["source_snapshot_id"] = snap["id"]

            # Waste
            t0 = time.perf_counter()
            waste = unwrap(
                client.post(f"/api/v1/organizations/{org_id}/decisions/waste/execute", headers=h, json=body),
                "waste execute",
            )
            waste_run_id = waste["analysis_run"]["id"]
            wres = unwrap(
                client.get(
                    f"/api/v1/organizations/{org_id}/analysis-runs/{waste_run_id}/waste/result",
                    headers=h,
                ),
                "waste result",
            )
            report["steps"]["waste"] = {
                "run_id": waste_run_id,
                "total": wres["total_waste_amount"],
                "pct": wres["waste_percentage"],
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"Waste OK — {wres['total_waste_amount']} ({wres['waste_percentage']}%)")

            # Waste AI
            t0 = time.perf_counter()
            wai = unwrap(
                client.post(
                    f"/api/v1/organizations/{org_id}/ai-recommendations/waste/generate",
                    headers=h,
                    json={"analysis_run_id": waste_run_id, "regenerate": True},
                    timeout=600,
                ),
                "waste AI",
            )
            report["steps"]["waste_ai"] = {
                "count": wai.get("recommendation_count", 0),
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"Waste AI OK — {report['steps']['waste_ai']['count']} recommendations")

            # Risk (run twice to prove duplicate-key fix)
            for attempt in (1, 2):
                t0 = time.perf_counter()
                risk = unwrap(
                    client.post(
                        f"/api/v1/organizations/{org_id}/risk-analyses/execute",
                        headers=h,
                        json={
                            "title": f"Sprint0 Risk attempt {attempt}",
                            "source_file_id": ff["id"],
                            **({"source_snapshot_id": snap["id"]} if snap else {}),
                        },
                    ),
                    f"risk execute attempt {attempt}",
                )
                risk_run_id = risk["analysis_run"]["id"]
                risk_result = unwrap(
                    client.get(
                        f"/api/v1/organizations/{org_id}/risk-analyses/{risk_run_id}/result",
                        headers=h,
                    ),
                    f"risk result attempt {attempt}",
                )
                findings = unwrap(
                    client.get(
                        f"/api/v1/organizations/{org_id}/risk-analyses/{risk_run_id}/findings",
                        headers=h,
                    ),
                    f"risk findings attempt {attempt}",
                )
                report["steps"][f"risk_{attempt}"] = {
                    "run_id": risk_run_id,
                    "findings": len(findings),
                    "posture": risk_result["overall_posture_level"],
                    "ms": round((time.perf_counter() - t0) * 1000, 2),
                }
                log(
                    f"Risk attempt {attempt} OK — {len(findings)} findings, "
                    f"posture={risk_result['overall_posture_level']}"
                )

            # Risk AI (latest run)
            t0 = time.perf_counter()
            rai = unwrap(
                client.post(
                    f"/api/v1/organizations/{org_id}/ai-recommendations/risk/generate",
                    headers=h,
                    json={"analysis_run_id": risk_run_id, "regenerate": True},
                    timeout=600,
                ),
                "risk AI",
            )
            report["steps"]["risk_ai"] = {
                "count": rai.get("recommendation_count", 0),
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"Risk AI OK — {report['steps']['risk_ai']['count']} recommendations")

            # Simulation (AI-native)
            t0 = time.perf_counter()
            sim_body = {
                "user_request": "أريد رفع الأرباح بمقدار 200 ألف ريال",
                "source_file_id": ff["id"],
                "baseline_analysis_run_id": waste_run_id,
            }
            if snap:
                sim_body["source_snapshot_id"] = snap["id"]
            sim = unwrap(
                client.post(
                    f"/api/v1/organizations/{org_id}/simulation/ai/execute",
                    headers=h,
                    json=sim_body,
                ),
                "simulation ai execute",
            )
            report["steps"]["simulation"] = {
                "run_id": sim["simulation_run"]["id"],
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"Simulation OK — run={sim['simulation_run']['id']}")

            # Report
            t0 = time.perf_counter()
            rep = unwrap(
                client.post(
                    f"/api/v1/organizations/{org_id}/reports/generate",
                    headers=h,
                    json={"analysis_run_id": waste_run_id, "title": "Sprint0 Executive Report"},
                ),
                "report generate",
            )
            report_id = rep["report"]["id"]
            report["steps"]["report"] = {
                "id": report_id,
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"Report OK — id={report_id}")

            # PDF
            t0 = time.perf_counter()
            pdf = client.get(
                f"/api/v1/organizations/{org_id}/reports/{report_id}/export",
                params={"format": "pdf"},
                headers=h,
            )
            if pdf.status_code >= 400:
                raise RuntimeError(f"PDF export failed HTTP {pdf.status_code}: {pdf.text[:2000]}")
            report["steps"]["pdf"] = {
                "bytes": len(pdf.content),
                "ms": round((time.perf_counter() - t0) * 1000, 2),
            }
            log(f"PDF OK — {len(pdf.content)} bytes")

            report["ok"] = True
            report["finished_at"] = datetime.now(UTC).isoformat()

    except Exception as exc:
        report["error"] = str(exc)
        report["finished_at"] = datetime.now(UTC).isoformat()
        log(f"FAILED: {exc}")
        RESULTS.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 1

    RESULTS.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log("ALL STEPS PASSED")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
