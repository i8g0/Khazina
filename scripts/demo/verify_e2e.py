#!/usr/bin/env python3
"""End-to-end API verification for hackathon demo path."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import httpx

API_BASE = os.environ.get("KHAZINA_API_URL", "http://localhost:8000").rstrip("/")
DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@khazina.sa")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoExec2026!")
WORKBOOK = Path(__file__).resolve().parent / "Procurement_Q2.xlsx"
AI_TIMEOUT = int(os.environ.get("AI_TIMEOUT", "180"))
TOTAL_AI_PIPELINE_TIMEOUT = AI_TIMEOUT * 3 + 30


class StepResult:
    def __init__(self, name: str, ok: bool, detail: str, elapsed: float) -> None:
        self.name = name
        self.ok = ok
        self.detail = detail
        self.elapsed = elapsed


def _unwrap(response: httpx.Response) -> dict:
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API request failed")
    return payload["data"]


def _step(name: str, fn) -> StepResult:
    start = time.perf_counter()
    try:
        detail = fn()
        return StepResult(name, True, detail, time.perf_counter() - start)
    except Exception as exc:  # noqa: BLE001
        return StepResult(name, False, str(exc), time.perf_counter() - start)


def main() -> int:
    if not WORKBOOK.exists():
        print(f"Missing workbook: {WORKBOOK}", file=sys.stderr)
        print("Run: python scripts/demo/generate_workbook.py", file=sys.stderr)
        return 1

    results: list[StepResult] = []
    state: dict[str, str] = {}

    with httpx.Client(base_url=f"{API_BASE}/api/v1", timeout=AI_TIMEOUT + 30) as client:
        def login() -> str:
            data = _unwrap(
                client.post(
                    "/auth/login",
                    json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
                )
            )
            token = data["access_token"]
            state["token"] = token
            return "JWT received"

        results.append(_step("Login", login))

        def active_org() -> str:
            data = _unwrap(
                client.get(
                    "/organizations/active",
                    headers={"Authorization": f"Bearer {state['token']}"},
                )
            )
            state["org_id"] = data["id"]
            return f"org={data['name']}"

        results.append(_step("Active organization", active_org))

        def upload() -> str:
            with WORKBOOK.open("rb") as handle:
                data = _unwrap(
                    client.post(
                        f"/organizations/{state['org_id']}/financial-files/upload",
                        headers={"Authorization": f"Bearer {state['token']}"},
                        files={"upload": (WORKBOOK.name, handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                    )
                )
            state["file_id"] = data["financial_file"]["id"]
            snapshot = data.get("financial_snapshot")
            if snapshot:
                state["snapshot_id"] = snapshot["id"]
                state["snapshot_version"] = str(snapshot["snapshot_version"])
            return f"file={state['file_id']}"

        results.append(_step("Upload Procurement_Q2.xlsx", upload))

        def waste() -> str:
            body = {
                "title": "كشف الهدر — Q2 2026",
                "source_file_id": state["file_id"],
            }
            if "snapshot_id" in state:
                body["source_snapshot_id"] = state["snapshot_id"]
            elif "snapshot_version" in state:
                body["snapshot_version"] = int(state["snapshot_version"])
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/decisions/waste/execute",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json=body,
                )
            )
            state["waste_run_id"] = data["analysis_run"]["id"]
            return f"run={state['waste_run_id']} status={data['analysis_run']['status']}"

        results.append(_step("Waste decision", waste))

        def ai() -> str:
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/ai-recommendations/waste/generate",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json={
                        "analysis_run_id": state["waste_run_id"],
                        "regenerate": False,
                    },
                    timeout=TOTAL_AI_PIPELINE_TIMEOUT,
                )
            )
            count = data.get("recommendation_count", 0)
            if count < 1:
                raise RuntimeError("No recommendations generated")
            return f"recommendations={count}"

        results.append(_step("AI recommendations", ai))

        def scenario() -> str:
            scenarios = _unwrap(
                client.get(
                    f"/organizations/{state['org_id']}/simulation/scenarios",
                    headers={"Authorization": f"Bearer {state['token']}"},
                )
            )
            if not scenarios:
                raise RuntimeError("No scenarios bootstrapped")
            scenario_id = scenarios[0]["id"]
            body = {
                "source_file_id": state["file_id"],
                "baseline_analysis_run_id": state["waste_run_id"],
            }
            if "snapshot_id" in state:
                body["source_snapshot_id"] = state["snapshot_id"]
            elif "snapshot_version" in state:
                body["snapshot_version"] = int(state["snapshot_version"])
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/simulation/scenarios/{scenario_id}/execute",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json=body,
                )
            )
            state["simulation_run_id"] = data["simulation_run"]["id"]
            return f"simulation_run={state['simulation_run_id']}"

        results.append(_step("Scenario execute", scenario))

        def report() -> str:
            data = _unwrap(
                client.post(
                    f"/organizations/{state['org_id']}/reports/generate",
                    headers={"Authorization": f"Bearer {state['token']}"},
                    json={
                        "analysis_run_id": state["waste_run_id"],
                        "title": "تقرير تنفيذي — كشف الهدر",
                    },
                )
            )
            state["report_id"] = data["report"]["id"]
            if not data["report"].get("has_content"):
                raise RuntimeError("Report has no content")
            return f"report={state['report_id']}"

        results.append(_step("Report generate", report))

        def pdf() -> str:
            response = client.get(
                f"/organizations/{state['org_id']}/reports/{state['report_id']}/export",
                params={"format": "pdf"},
                headers={"Authorization": f"Bearer {state['token']}"},
            )
            response.raise_for_status()
            if "application/pdf" not in response.headers.get("content-type", ""):
                raise RuntimeError("Expected application/pdf")
            if len(response.content) < 1024:
                raise RuntimeError(f"PDF too small: {len(response.content)} bytes")
            return f"pdf_bytes={len(response.content)}"

        results.append(_step("PDF export", pdf))

        def notifications() -> str:
            data = _unwrap(
                client.get(
                    f"/organizations/{state['org_id']}/notifications",
                    headers={"Authorization": f"Bearer {state['token']}"},
                )
            )
            if len(data) < 3:
                raise RuntimeError(f"Expected >=3 notifications, got {len(data)}")
            return f"notifications={len(data)}"

        results.append(_step("Notifications", notifications))

    print("\nE2E verification results:")
    failed = 0
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        if not result.ok:
            failed += 1
        print(
            f"  [{status}] {result.name}: {result.detail} ({result.elapsed:.2f}s)"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
