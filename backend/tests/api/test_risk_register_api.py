"""Risk register API route registration tests."""

from __future__ import annotations

from app.main import create_app


def test_risk_register_routes_registered() -> None:
    app = create_app()
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    prefix = "/api/v1/organizations/{organization_id}"
    assert f"{prefix}/risk-findings/{{finding_id}}/promote" in paths
    assert f"{prefix}/risk-findings/{{finding_id}}/review" in paths
    assert f"{prefix}/risks/{{risk_id}}/status" in paths
    assert f"{prefix}/risks/{{risk_id}}/review" in paths
    assert f"{prefix}/risks/{{risk_id}}/history" in paths
    assert f"{prefix}/risks/{{risk_id}}/provenance" in paths
