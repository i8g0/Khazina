#!/usr/bin/env python
"""Simulate the real frontend HTTP flow for AI generation (evidence collection)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

BASE = "http://127.0.0.1:8000/api/v1"
EMAIL = "admin@khazina.demo"
PASSWORD = "demo-password-123"


def _elapsed(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def main() -> None:
    timeline: list[dict] = []
    t0 = time.perf_counter()

    with httpx.Client(timeout=180.0) as client:
        t_login = time.perf_counter()
        login = client.post(
            f"{BASE}/auth/login",
            json={"email": EMAIL, "password": PASSWORD},
        )
        login.raise_for_status()
        token = login.json()["data"]["access_token"]
        timeline.append(
            {
                "stage": "auth_login",
                "elapsed_ms": _elapsed(t0),
                "duration_ms": _elapsed(t_login),
            }
        )

        headers = {"Authorization": f"Bearer {token}"}

        t_health = time.perf_counter()
        health = client.get(f"{BASE}/ai/health", headers=headers)
        health.raise_for_status()
        health_data = health.json()["data"]
        timeline.append(
            {
                "stage": "GET /ai/health (frontend preflight)",
                "elapsed_ms": _elapsed(t0),
                "duration_ms": _elapsed(t_health),
                "provider": health_data.get("provider"),
                "model": health_data.get("configured_model"),
            }
        )

        # Find a waste run without ai_insights
        from app.db.session import SessionLocal
        from app.db.models import AnalysisRun
        from app.db.models.enums import AnalysisRunStatus, AnalysisType

        session = SessionLocal()
        try:
            run = (
                session.query(AnalysisRun)
                .filter(
                    AnalysisRun.analysis_type == AnalysisType.FINANCIAL_WASTE,
                    AnalysisRun.status == AnalysisRunStatus.COMPLETED,
                )
                .order_by(AnalysisRun.created_at.desc())
                .first()
            )
            if run is None:
                raise RuntimeError("No completed waste run found")
            org_id = str(run.organization_id)
            run_id = str(run.id)
            has_ai = bool((run.runtime_metadata or {}).get("ai_insights"))
        finally:
            session.close()

        t_gen = time.perf_counter()
        generate = client.post(
            f"{BASE}/organizations/{org_id}/ai-recommendations/waste/generate",
            headers=headers,
            json={"analysis_run_id": run_id, "regenerate": has_ai},
        )
        gen_duration = _elapsed(t_gen)
        timeline.append(
            {
                "stage": "POST /ai-recommendations/waste/generate",
                "elapsed_ms": _elapsed(t0),
                "duration_ms": gen_duration,
                "status": generate.status_code,
            }
        )
        if generate.status_code >= 400:
            timeline.append({"error": generate.text[:500]})
        else:
            payload = generate.json()["data"]
            timeline.append(
                {
                    "recommendation_count": payload.get("recommendation_count"),
                }
            )

    from app.ai.telemetry import get_ai_request_records

    records = [
        {
            "provider": r.provider,
            "model": r.model,
            "endpoint": r.endpoint,
            "task": r.task,
            "latency_ms": r.latency_ms,
        }
        for r in get_ai_request_records()
    ]

    report = {
        "total_ms": _elapsed(t0),
        "timeline": timeline,
        "openai_chat_completions_calls": len(records),
        "provider_records": records,
    }
    out = Path(__file__).with_name("_real_world_http_trace.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
