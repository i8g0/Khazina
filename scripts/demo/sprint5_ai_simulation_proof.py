#!/usr/bin/env python3
"""Sprint 5 — prove 10 distinct AI-native simulation scenarios via API."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(BACKEND_ROOT / ".env")

import httpx  # noqa: E402

BASE = os.environ.get("KHAZINA_API_URL", "http://127.0.0.1:8000").rstrip("/")
EMAIL = os.environ.get("DEMO_EMAIL", "demo@khazina.sa")
PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoExec2026!")

SCENARIOS = [
    "أريد زيادة الأرباح 200 ألف ريال",
    "خفض المصاريف التشغيلية 15%",
    "رفع ميزانية التسويق مليون ريال",
    "تقليل الموردين إلى النصف",
    "إغلاق أحد الفروع",
    "توظيف 20 موظفاً",
    "زيادة الرواتب 8%",
    "رفع الأسعار 3%",
    "خفض تكلفة النقل",
    "تقليل الهدر المالي 40%",
]


def main() -> int:
    report: dict = {"base": BASE, "scenarios": [], "passed": True}
    with httpx.Client(base_url=BASE, timeout=180.0) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": EMAIL, "password": PASSWORD},
        )
        login.raise_for_status()
        payload = login.json()
        if not payload.get("success"):
            print("Login failed:", payload)
            return 1
        token = payload["data"]["access_token"]
        org_resp = client.get(
            "/api/v1/organizations/active",
            headers={"Authorization": f"Bearer {token}"},
        )
        org_resp.raise_for_status()
        org_id = org_resp.json()["data"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        files = client.get(
            f"/api/v1/organizations/{org_id}/financial-files",
            headers=headers,
        ).json()["data"]
        if not files:
            print("No financial files — upload dataset first")
            return 1
        file_id = files[0]["id"]

        snapshots = client.get(
            f"/api/v1/organizations/{org_id}/financial-files/{file_id}/snapshots",
            headers=headers,
        ).json()["data"]
        snapshot_id = snapshots[0]["id"] if snapshots else None

        waste_runs = client.get(
            f"/api/v1/organizations/{org_id}/analysis-runs",
            headers=headers,
            params={"analysis_type": "waste", "status": "completed", "limit": 1},
        ).json()["data"]
        waste_run_id = waste_runs[0]["id"] if waste_runs else None

        seen_types: set[str] = set()
        for index, user_request in enumerate(SCENARIOS, start=1):
            body = {
                "user_request": user_request,
                "source_file_id": file_id,
            }
            if snapshot_id:
                body["source_snapshot_id"] = snapshot_id
            if waste_run_id:
                body["baseline_analysis_run_id"] = waste_run_id

            t0 = time.perf_counter()
            resp = client.post(
                f"/api/v1/organizations/{org_id}/simulation/ai/execute",
                headers=headers,
                json=body,
            )
            elapsed = round((time.perf_counter() - t0) * 1000, 2)
            entry = {
                "index": index,
                "user_request": user_request,
                "status_code": resp.status_code,
                "ms": elapsed,
            }
            if resp.status_code != 201:
                entry["error"] = resp.text[:500]
                report["passed"] = False
            else:
                data = resp.json()["data"]
                interpreted = data.get("interpreted_scenario", {})
                entry["scenario_type"] = interpreted.get("scenario_type")
                entry["title_ar"] = interpreted.get("title_ar")
                entry["run_id"] = data["simulation_run"]["id"]
                seen_types.add(str(interpreted.get("scenario_type")))
            report["scenarios"].append(entry)
            print(f"[{index}/10] {user_request[:40]} -> {entry.get('scenario_type', 'FAIL')}")

        report["distinct_scenario_types"] = len(seen_types)
        if len(seen_types) < 3:
            report["passed"] = False

    out = Path(__file__).resolve().parent / "sprint5_ai_simulation_proof.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {out}")
    print(f"Distinct types: {report['distinct_scenario_types']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
