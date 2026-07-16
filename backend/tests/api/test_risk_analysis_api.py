"""Risk analysis API route registration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_risk_analysis_routes_registered() -> None:
    app = create_app()
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    prefix = "/api/v1/organizations/{organization_id}/risk-analyses"
    assert f"{prefix}/execute" in paths
    assert prefix in paths
    assert f"{prefix}/{{run_id}}" in paths
    assert f"{prefix}/{{run_id}}/result" in paths
    assert f"{prefix}/{{run_id}}/findings" in paths
    assert f"{prefix}/{{run_id}}/findings/{{finding_id}}" in paths


def test_risk_analysis_execute_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/organizations/00000000-0000-0000-0000-000000000001/risk-analyses/execute",
        json={
            "title": "Risk Q2",
            "source_file_id": "00000000-0000-0000-0000-000000000002",
        },
    )
    assert response.status_code in {401, 403}
