#!/usr/bin/env python3
"""Sprint 8.2 dynamic verification — extended E2E with dataset comparison."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx
from openpyxl import Workbook

API_BASE = "http://127.0.0.1:8000"
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
AI_TIMEOUT = 180
SCRIPT_DIR = Path(__file__).resolve().parent
WORKBOOK_A = SCRIPT_DIR / "Procurement_Q2.xlsx"
WORKBOOK_B = SCRIPT_DIR / "Procurement_Q2_variant.xlsx"


def make_variant_workbook() -> None:
    wb = Workbook()
    sheet = wb.active
    sheet.title = "WasteData"
    sheet.append(["category", "amount", "total_spend"])
    # Deliberately different amounts vs canonical demo file
    for category, amount, total_spend in [
        ("overlapping_contracts", 1_200_000, 80_000_000),
        ("operations", 300_000, 80_000_000),
        ("finance", 450_000, 80_000_000),
    ]:
        sheet.append([category, amount, total_spend])
    wb.save(WORKBOOK_B)


def unwrap(response: httpx.Response) -> dict:
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(payload.get("message") or "API failed")
    return payload["data"]


def login(client: httpx.Client) -> tuple[str, str]:
    data = unwrap(client.post("/api/v1/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}))
    token = data["access_token"]
    org = unwrap(client.get("/api/v1/organizations/active", headers={"Authorization": f"Bearer {token}"}))
    return token, org["id"]


def run_pipeline(
    client: httpx.Client,
    token: str,
    org_id: str,
    workbook: Path,
    label: str,
) -> dict:
    result: dict = {"label": label, "timings": {}, "ids": {}, "waste": {}, "ai": {}, "scenarios": [], "report": {}}
    headers = {"Authorization": f"Bearer {token}"}

    t0 = time.perf_counter()
    with workbook.open("rb") as handle:
        upload = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/financial-files/upload",
                headers=headers,
                files={"upload": (workbook.name, handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        )
    result["timings"]["upload"] = time.perf_counter() - t0
    ff = upload["financial_file"]
    snap = upload.get("financial_snapshot")
    result["ids"]["file_id"] = ff["id"]
    result["ids"]["file_name"] = ff["file_name"]
    result["ids"]["processing_status"] = ff["processing_status"]
    if snap:
        result["ids"]["snapshot_id"] = snap["id"]
        result["ids"]["snapshot_version"] = snap["snapshot_version"]
        result["ids"]["record_count"] = snap.get("record_count")

    # Quality
    t0 = time.perf_counter()
    try:
        qsnap = unwrap(client.get(f"/api/v1/organizations/{org_id}/data-quality/snapshots/latest", headers=headers))
        checks = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/data-quality/snapshots/{qsnap['id']}/checks",
                headers=headers,
            )
        )
        result["quality"] = {
            "overall_score": qsnap.get("overall_score"),
            "checks_count": len(checks),
            "checks": [{"name": c["check_name"], "percent": c["result_percent"]} for c in checks[:5]],
        }
    except Exception as exc:  # noqa: BLE001
        result["quality"] = {"error": str(exc)}
    result["timings"]["quality"] = time.perf_counter() - t0

    # Waste
    body = {"title": f"كشف الهدر — {label}", "source_file_id": result["ids"]["file_id"]}
    if snap:
        body["source_snapshot_id"] = snap["id"]
    t0 = time.perf_counter()
    waste_exec = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/decisions/waste/execute",
            headers=headers,
            json=body,
        )
    )
    result["timings"]["waste_execute"] = time.perf_counter() - t0
    run_id = waste_exec["analysis_run"]["id"]
    result["ids"]["waste_run_id"] = run_id

    t0 = time.perf_counter()
    waste_result = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/analysis-runs/{run_id}/waste/result",
            headers=headers,
        )
    )
    breakdowns = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/analysis-runs/{run_id}/waste/category-breakdowns",
            headers=headers,
        )
    )
    vendors = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/analysis-runs/{run_id}/waste/vendor-findings",
            headers=headers,
        )
    )
    result["timings"]["waste_fetch"] = time.perf_counter() - t0
    result["waste"] = {
        "total_waste_amount": waste_result["total_waste_amount"],
        "waste_percentage": waste_result["waste_percentage"],
        "potential_savings_amount": waste_result.get("potential_savings_amount"),
        "active_savings_opportunities": waste_result.get("active_savings_opportunities"),
        "categories": [
            {
                "name": b["category_name"],
                "amount": b["amount"],
                "percentage": b["percentage"],
                "department_id": b.get("department_id"),
            }
            for b in breakdowns
        ],
        "vendor_count": len(vendors),
        "vendors": vendors[:5],
    }

    # AI
    t0 = time.perf_counter()
    ai = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/ai-recommendations/waste/generate",
            headers=headers,
            json={"analysis_run_id": run_id, "regenerate": True},
            timeout=AI_TIMEOUT + 30,
        )
    )
    result["timings"]["ai"] = time.perf_counter() - t0
    recs = ai.get("recommendations", [])
    result["ai"] = {
        "recommendation_count": ai.get("recommendation_count", len(recs)),
        "titles": [r["title"] for r in recs],
        "priorities": [r["priority"] for r in recs],
        "confidence_labels": [r.get("confidence_label") for r in recs],
        "estimated_savings": [r.get("estimated_savings_amount") for r in recs],
        "descriptions_sample": [r["description"][:120] for r in recs[:3]],
        "insights_keys": list((ai.get("ai_insights") or {}).keys()),
    }

    # All scenarios
    scenarios = unwrap(
        client.get(f"/api/v1/organizations/{org_id}/simulation/scenarios", headers=headers)
    )
    for scenario in scenarios:
        sbody = {
            "source_file_id": result["ids"]["file_id"],
            "baseline_analysis_run_id": run_id,
        }
        if snap:
            sbody["source_snapshot_id"] = snap["id"]
        t0 = time.perf_counter()
        sim = unwrap(
            client.post(
                f"/api/v1/organizations/{org_id}/simulation/scenarios/{scenario['id']}/execute",
                headers=headers,
                json=sbody,
            )
        )
        sim_run_id = sim["simulation_run"]["id"]
        elapsed = time.perf_counter() - t0
        forecast = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/simulation/runs/{sim_run_id}/forecast-summary",
                headers=headers,
            )
        )
        assumptions = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/simulation/scenarios/{scenario['id']}/assumptions",
                headers=headers,
            )
        )
        impacts = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/simulation/runs/{sim_run_id}/impact-items",
                headers=headers,
            )
        )
        actions = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/simulation/runs/{sim_run_id}/action-items",
                headers=headers,
            )
        )
        chart = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/simulation/runs/{sim_run_id}/chart-points",
                headers=headers,
            )
        )
        metrics = unwrap(
            client.get(
                f"/api/v1/organizations/{org_id}/simulation/runs/{sim_run_id}/comparison-metrics",
                headers=headers,
            )
        )
        result["scenarios"].append(
            {
                "name": scenario["name"],
                "scenario_id": scenario["id"],
                "simulation_run_id": sim_run_id,
                "elapsed_s": round(elapsed, 2),
                "assumptions_count": len(assumptions),
                "assumptions": [{"label": a["label"], "value": a["value"]} for a in assumptions],
                "forecast": forecast,
                "impact_count": len(impacts),
                "action_count": len(actions),
                "chart_points": len(chart),
                "comparison_metrics": len(metrics),
                "baseline_projected_sample": chart[0] if chart else None,
            }
        )

    # Report + PDF
    t0 = time.perf_counter()
    report_gen = unwrap(
        client.post(
            f"/api/v1/organizations/{org_id}/reports/generate",
            headers=headers,
            json={"analysis_run_id": run_id, "title": f"تقرير — {label}"},
        )
    )
    result["timings"]["report"] = time.perf_counter() - t0
    report_id = report_gen["report"]["id"]
    result["ids"]["report_id"] = report_id

    content = unwrap(
        client.get(
            f"/api/v1/organizations/{org_id}/reports/{report_id}/content",
            headers=headers,
        )
    )
    sections = content.get("content", {}).get("sections", [])
    result["report"] = {
        "title": report_gen["report"]["title"],
        "has_content": report_gen["report"].get("has_content"),
        "section_keys": [s["key"] for s in sections],
        "executive_summary_preview": _section_text(sections, "executive_summary"),
        "waste_summary_preview": _section_text(sections, "waste_summary"),
    }

    t0 = time.perf_counter()
    pdf_resp = client.get(
        f"/api/v1/organizations/{org_id}/reports/{report_id}/export",
        params={"format": "pdf"},
        headers=headers,
    )
    pdf_resp.raise_for_status()
    result["timings"]["pdf"] = time.perf_counter() - t0
    result["report"]["pdf_bytes"] = len(pdf_resp.content)
    result["report"]["pdf_content_type"] = pdf_resp.headers.get("content-type")

    return result


def _section_text(sections: list, key: str) -> str:
    for section in sections:
        if section.get("key") == key:
            payload = section.get("payload") or {}
            text = payload.get("text") or payload.get("summary") or json.dumps(payload, ensure_ascii=False)
            return str(text)[:300]
    return ""


def compare_runs(a: dict, b: dict) -> dict:
    return {
        "waste_total_changed": a["waste"]["total_waste_amount"] != b["waste"]["total_waste_amount"],
        "waste_pct_changed": a["waste"]["waste_percentage"] != b["waste"]["waste_percentage"],
        "waste_a_total": a["waste"]["total_waste_amount"],
        "waste_b_total": b["waste"]["total_waste_amount"],
        "waste_a_pct": a["waste"]["waste_percentage"],
        "waste_b_pct": b["waste"]["waste_percentage"],
        "ai_titles_identical": a["ai"]["titles"] == b["ai"]["titles"],
        "ai_titles_a": a["ai"]["titles"],
        "ai_titles_b": b["ai"]["titles"],
        "scenario_forecasts_a": [s["forecast"] for s in a["scenarios"]],
        "scenario_forecasts_b": [s["forecast"] for s in b["scenarios"]],
        "report_exec_a": a["report"]["executive_summary_preview"][:200],
        "report_exec_b": b["report"]["executive_summary_preview"][:200],
    }


def main() -> int:
    if not WORKBOOK_A.exists():
        print("Missing workbook A", file=sys.stderr)
        return 1
    make_variant_workbook()

    out_path = SCRIPT_DIR / "sprint_8_2_results.json"
    report: dict = {"environment": {}, "run_a": None, "run_b": None, "comparison": None}

    # Environment checks
    with httpx.Client(timeout=10) as client:
        try:
            health = client.get(f"{API_BASE}/api/v1/health").json()
            report["environment"]["backend"] = health.get("data", {}).get("status") == "ok"
        except Exception as exc:  # noqa: BLE001
            report["environment"]["backend"] = False
            report["environment"]["backend_error"] = str(exc)
        try:
            fe = client.get("http://localhost:3000")
            report["environment"]["frontend"] = fe.status_code == 200
        except Exception as exc:  # noqa: BLE001
            report["environment"]["frontend"] = False
            report["environment"]["frontend_error"] = str(exc)
        try:
            ollama = client.get("http://127.0.0.1:11434/api/tags")
            tags = ollama.json().get("models", [])
            report["environment"]["ollama"] = True
            report["environment"]["ollama_models"] = [m.get("name") for m in tags]
        except Exception as exc:  # noqa: BLE001
            report["environment"]["ollama"] = False
            report["environment"]["ollama_error"] = str(exc)

    with httpx.Client(base_url=API_BASE, timeout=AI_TIMEOUT + 60) as client:
        token, org_id = login(client)
        report["environment"]["login"] = True
        report["environment"]["org_id"] = org_id

        print("Running pipeline A (canonical workbook)...")
        report["run_a"] = run_pipeline(client, token, org_id, WORKBOOK_A, "canonical")
        print("Running pipeline B (variant workbook)...")
        report["run_b"] = run_pipeline(client, token, org_id, WORKBOOK_B, "variant")
        report["comparison"] = compare_runs(report["run_a"], report["run_b"])

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")
    print("\n=== SUMMARY ===")
    print(json.dumps(report["comparison"], ensure_ascii=False, indent=2))
    print("\n=== TIMINGS A ===")
    print(json.dumps(report["run_a"]["timings"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
