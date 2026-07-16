"""Authorization boundary tests for protected routes (Sprint 8.1)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/v1/organizations/active"),
        ("GET", f"/api/v1/organizations/{uuid.uuid4()}/analysis-runs"),
        ("POST", f"/api/v1/organizations/{uuid.uuid4()}/decisions/waste/execute"),
        ("POST", f"/api/v1/organizations/{uuid.uuid4()}/reports/generate"),
        ("GET", f"/api/v1/organizations/{uuid.uuid4()}/settings"),
    ],
)
def test_protected_routes_reject_missing_token(
    client: TestClient,
    method: str,
    path: str,
) -> None:
    response = client.request(method, path, json={} if method == "POST" else None)
    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False


def test_protected_routes_reject_invalid_bearer_token(client: TestClient) -> None:
    org_id = uuid.uuid4()
    response = client.get(
        f"/api/v1/organizations/{org_id}/analysis-runs",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
