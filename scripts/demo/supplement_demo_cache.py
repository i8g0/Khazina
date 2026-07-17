#!/usr/bin/env python3
"""Supplement demo_cache with additional read endpoints used by UI pages."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = REPO_ROOT / "demo_cache"
MANIFEST = CACHE_DIR / "manifest.json"
API_BASE = os.environ.get("KHAZINA_API_URL", "http://localhost:8000").rstrip("/")
DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@khazina.sa")
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoExec2026!")


def main() -> int:
    if not MANIFEST.exists():
        print("Run warm_demo_cache.py first", file=sys.stderr)
        return 1

    sys.path.insert(0, str(REPO_ROOT / "backend"))
    from app.demo_cache.store import DemoCacheStore

    golden = json.loads(MANIFEST.read_text(encoding="utf-8"))["golden_ids"]
    org = golden["org_id"]
    waste = golden["waste_run_id"]
    risk = golden["risk_run_id"]
    sim = golden["simulation_run_id"]
    file_id = golden["file_id"]
    report = golden["report_id"]

    store = DemoCacheStore(CACHE_DIR)

    with httpx.Client(base_url=f"{API_BASE}/api/v1", timeout=60) as client:
        login = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        login.raise_for_status()
        token = login.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        endpoints: list[tuple[str, str, dict | None]] = [
            ("GET", f"/organizations/{org}/notifications/unread-count", None),
            ("GET", f"/organizations/{org}/risk-analyses/{risk}", None),
            ("GET", f"/organizations/{org}/mitigation-plans", {"limit": "20"}),
            ("GET", f"/organizations/{org}/analysis-runs/{waste}", None),
            ("GET", f"/organizations/{org}/analysis-runs/{sim}", None),
            ("GET", f"/organizations/{org}/financial-files/{file_id}/import-records", None),
            ("GET", f"/organizations/{org}/recommendations", {"domain_source": "risk", "limit": "20"}),
            ("GET", f"/organizations/{org}/recommendations", {"domain_source": "waste", "limit": "20"}),
            ("GET", f"/organizations/{org}/recommendations", {"limit": "50"}),
            ("GET", f"/organizations/{org}/simulation/scenarios", {"limit": "20"}),
            ("GET", f"/organizations/{org}/risk-analyses", {"limit": "20"}),
            ("GET", f"/organizations/{org}/analysis-runs/recent-completed", {"limit": "5"}),
            ("GET", f"/organizations/{org}/analysis-runs/recent-completed", {"limit": "10"}),
            ("GET", f"/organizations/{org}/timeline/events", {"limit": "20"}),
            ("GET", f"/organizations/{org}/data-quality-snapshots/latest", None),
        ]

        for method, path, params in endpoints:
            try:
                resp = client.request(method, path, headers=headers, params=params)
                resp.raise_for_status()
                from app.demo_cache.keys import build_cache_key

                query = ""
                if params:
                    from urllib.parse import urlencode

                    query = urlencode(sorted(params.items()))
                key = build_cache_key(method, path, query)
                store.save_from_http(
                    method=method,
                    path=path,
                    query=query,
                    status_code=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                )
                print(f"[OK] cached {key}")
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] {method} {path}: {exc}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["response_count"] = len(list((CACHE_DIR / "responses").glob("*.json")))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done. {manifest['response_count']} total responses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
