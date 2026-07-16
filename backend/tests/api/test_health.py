"""Health endpoint API tests (Sprint 8.1)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_success_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] in {"ok", "degraded", "unavailable"}
    assert payload["data"]["backend"]["status"] == "ok"
    assert payload["data"]["database"]["status"] in {"ok", "unavailable"}
    assert payload["data"]["ai"]["status"] in {"ok", "unavailable"}


def test_health_does_not_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
