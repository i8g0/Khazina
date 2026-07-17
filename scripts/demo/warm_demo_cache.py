#!/usr/bin/env python3
"""Warm demo_cache/ by running the complete Khazina workflow once (live execution).

Requires backend running with:
  DEMO_CACHE_MODE=false
  DEMO_CACHE_RECORD=true

After warming, enable DEMO_CACHE_MODE=true for instant hackathon demos.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = REPO_ROOT / "demo_cache"
WORKBOOK = Path(__file__).resolve().parent / "Procurement_Q2.xlsx"

API_BASE = os.environ.get("KHAZINA_API_URL", "http://localhost:8000").rstrip("/")
DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@khazina.sa")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoExec2026!")
AI_TIMEOUT = int(os.environ.get("AI_TIMEOUT", "180"))
TOTAL_AI_PIPELINE_TIMEOUT = AI_TIMEOUT * 3 + 30


def _unwrap(response: httpx.Response) -> dict:
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API request failed")
    return payload["data"]


def _save_response(
    method: str,
    path: str,
    query: str,
    response: httpx.Response,
) -> None:
    from app.demo_cache.keys import build_cache_key, cache_key_to_filename
    from app.demo_cache.store import DemoCacheStore

    store = DemoCacheStore(CACHE_DIR)
    store.ensure_layout()
    cache_key = build_cache_key(method, path, query)
    headers = {k.lower(): v for k, v in response.headers.items()}
    store.save_from_http(
        method=method,
        path=path,
        query=query,
        status_code=response.status_code,
        headers=headers,
        body=response.content,
    )
    print(f"  cached: {cache_key}")


def _request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict | None = None,
    files: dict | None = None,
    params: dict | None = None,
    timeout: float | None = None,
) -> httpx.Response:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url_path = path if path.startswith("/") else f"/{path}"
    full_path = f"/api/v1{url_path}" if not url_path.startswith("/api/v1") else url_path
    response = client.request(
        method,
        full_path,
        headers=headers,
        json=json_body,
        files=files,
        params=params,
        timeout=timeout,
    )
    query = ""
    if params:
        from urllib.parse import urlencode

        query = urlencode(sorted(params.items()))
    _save_response(
        method,
        full_path.replace("/api/v1", ""),
        query,
        response,
    )
    return response


def _capture_reads(client: httpx.Client, state: dict[str, str]) -> None:
    org = state["org_id"]
    token = state["token"]
    waste = state.get("waste_run_id")
    risk = state.get("risk_run_id")
    report = state.get("report_id")

    reads: list[tuple[str, str, dict | None]] = [
        ("GET", f"/organizations/{org}/financial-files", None),
        ("GET", f"/organizations/{org}/departments", {"limit": "100", "active_only": "true"}),
        ("GET", f"/organizations/{org}/reporting-periods", {"limit": "100"}),
        ("GET", f"/organizations/{org}/recommendations", {"limit": "50"}),
        ("GET", f"/organizations/{org}/risks", {"limit": "50"}),
        ("GET", f"/organizations/{org}/timeline/events", {"limit": "20"}),
        ("GET", f"/organizations/{org}/reports", None),
        ("GET", f"/organizations/{org}/settings", None),
        ("GET", f"/organizations/{org}/data-quality-snapshots/latest", None),
        ("GET", f"/organizations/{org}/analysis-runs/recent-completed", {"limit": "10"}),
    ]
    if waste:
        reads.extend(
            [
                ("GET", f"/organizations/{org}/analysis-runs/{waste}/waste/result", None),
                (
                    "GET",
                    f"/organizations/{org}/analysis-runs/{waste}/waste/category-breakdowns",
                    None,
                ),
                (
                    "GET",
                    f"/organizations/{org}/analysis-runs/{waste}/waste/vendor-findings",
                    {"limit": "20"},
                ),
            ]
        )
    if risk:
        reads.extend(
            [
                ("GET", f"/organizations/{org}/risk-analyses/{risk}/result", None),
                (
                    "GET",
                    f"/organizations/{org}/risk-analyses/{risk}/findings",
                    {"limit": "50"},
                ),
                ("GET", f"/organizations/{org}/risk-analyses", {"limit": "10"}),
            ]
        )
    if report:
        reads.append(
            (
                "GET",
                f"/organizations/{org}/reports/{report}/content",
                None,
            )
        )

    for method, path, params in reads:
        try:
            _request(client, method, path, token=token, params=params)
        except Exception as exc:  # noqa: BLE001
            print(f"  warn: could not cache {method} {path}: {exc}")


def main() -> int:
    if not WORKBOOK.exists():
        print(f"Missing workbook: {WORKBOOK}", file=sys.stderr)
        print("Run: python scripts/demo/generate_workbook.py", file=sys.stderr)
        return 1

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    state: dict[str, str] = {}
    started = time.perf_counter()

    print(f"Warming demo cache at {CACHE_DIR}")
    print("Backend must have DEMO_CACHE_RECORD=true and DEMO_CACHE_MODE=false")

    with httpx.Client(base_url=API_BASE, timeout=AI_TIMEOUT + 30) as client:
        # 1 Login
        login = _unwrap(
            _request(
                client,
                "POST",
                "/auth/login",
                json_body={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
            )
        )
        state["token"] = login["access_token"]
        print("[OK] Login")

        # 2 Active org
        org = _unwrap(
            _request(
                client,
                "GET",
                "/organizations/active",
                token=state["token"],
            )
        )
        state["org_id"] = org["id"]
        print(f"[OK] Organization {org['name']}")

        # 3 Upload
        with WORKBOOK.open("rb") as handle:
            upload_resp = _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/financial-files/upload",
                token=state["token"],
                files={
                    "upload": (
                        WORKBOOK.name,
                        handle,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )
        upload = _unwrap(upload_resp)
        state["file_id"] = upload["financial_file"]["id"]
        snapshot = upload.get("financial_snapshot")
        if snapshot:
            state["snapshot_id"] = snapshot["id"]
            state["snapshot_version"] = str(snapshot["snapshot_version"])
        print(f"[OK] Upload file={state['file_id']}")

        # 4 Waste
        waste_body: dict = {
            "title": "كشف الهدر — Q2 2026",
            "source_file_id": state["file_id"],
        }
        if "snapshot_id" in state:
            waste_body["source_snapshot_id"] = state["snapshot_id"]
        elif "snapshot_version" in state:
            waste_body["snapshot_version"] = int(state["snapshot_version"])
        waste = _unwrap(
            _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/decisions/waste/execute",
                token=state["token"],
                json_body=waste_body,
            )
        )
        state["waste_run_id"] = waste["analysis_run"]["id"]
        print(f"[OK] Waste run={state['waste_run_id']}")

        # 5 AI waste
        ai = _unwrap(
            _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/ai-recommendations/waste/generate",
                token=state["token"],
                json_body={
                    "analysis_run_id": state["waste_run_id"],
                    "regenerate": False,
                },
                timeout=TOTAL_AI_PIPELINE_TIMEOUT,
            )
        )
        print(f"[OK] AI waste recommendations={ai.get('recommendation_count', 0)}")

        # 6 Risk
        risk_body: dict = {
            "title": "تحليل المخاطر — Demo Cache Warm",
            "source_file_id": state["file_id"],
        }
        if "snapshot_id" in state:
            risk_body["source_snapshot_id"] = state["snapshot_id"]
        risk = _unwrap(
            _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/risk-analyses/execute",
                token=state["token"],
                json_body=risk_body,
            )
        )
        state["risk_run_id"] = risk["analysis_run"]["id"]
        print(f"[OK] Risk run={state['risk_run_id']}")

        # 7 Risk AI (optional but cached if called)
        try:
            _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/ai-recommendations/risk/generate",
                token=state["token"],
                json_body={
                    "analysis_run_id": state["risk_run_id"],
                    "regenerate": False,
                },
                timeout=TOTAL_AI_PIPELINE_TIMEOUT,
            )
            print("[OK] AI risk recommendations")
        except Exception as exc:  # noqa: BLE001
            print(f"  warn: risk AI skipped: {exc}")

        # 8 Simulation
        sim_body: dict = {
            "user_request": "تقليل الإنفاق 10%",
            "source_file_id": state["file_id"],
            "baseline_analysis_run_id": state["waste_run_id"],
        }
        if "snapshot_id" in state:
            sim_body["source_snapshot_id"] = state["snapshot_id"]
        sim = _unwrap(
            _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/simulation/ai/execute",
                token=state["token"],
                json_body=sim_body,
                timeout=TOTAL_AI_PIPELINE_TIMEOUT,
            )
        )
        state["simulation_run_id"] = sim["simulation_run"]["id"]
        print(f"[OK] Simulation run={state['simulation_run_id']}")

        # 9 Report
        report = _unwrap(
            _request(
                client,
                "POST",
                f"/organizations/{state['org_id']}/reports/generate",
                token=state["token"],
                json_body={
                    "analysis_run_id": state["waste_run_id"],
                    "title": "تقرير تنفيذي — كشف الهدر",
                },
            )
        )
        state["report_id"] = report["report"]["id"]
        print(f"[OK] Report {state['report_id']}")

        # 10 PDF
        pdf = _request(
            client,
            "GET",
            f"/organizations/{state['org_id']}/reports/{state['report_id']}/export",
            token=state["token"],
            params={"format": "pdf"},
        )
        pdf.raise_for_status()
        print(f"[OK] PDF ({len(pdf.content)} bytes)")

        # 11 Notifications + dashboard
        notifs = _unwrap(
            _request(
                client,
                "GET",
                f"/organizations/{state['org_id']}/notifications",
                token=state["token"],
            )
        )
        print(f"[OK] Notifications ({len(notifs)})")

        _request(
            client,
            "GET",
            f"/organizations/{state['org_id']}/analysis-runs/recent-completed",
            token=state["token"],
            params={"limit": "5"},
        )
        print("[OK] Dashboard recent runs")

        # Extended read endpoints for UI pages
        print("Capturing read endpoints for dashboard / waste / risk / reports...")
        _capture_reads(client, state)

        dataset_dir = CACHE_DIR / "dataset"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        import shutil

        shutil.copy2(WORKBOOK, dataset_dir / WORKBOOK.name)

    manifest = {
        "purpose": "TEMPORARY hackathon demo cache — do not merge to production",
        "warmed_at": datetime.now(UTC).isoformat(),
        "workbook": WORKBOOK.name,
        "api_base": API_BASE,
        "golden_ids": state,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "response_count": len(list((CACHE_DIR / "responses").glob("*.json"))),
    }
    (CACHE_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nDone. {manifest['response_count']} responses cached in {CACHE_DIR}")
    print("Next: set DEMO_CACHE_MODE=true in backend/.env and restart uvicorn")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO_ROOT / "backend"))
    raise SystemExit(main())
