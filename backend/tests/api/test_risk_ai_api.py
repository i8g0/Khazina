"""Risk AI API route registration tests."""

from __future__ import annotations

from app.main import create_app


def test_risk_ai_generate_route_registered() -> None:
    app = create_app()
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert (
        "/api/v1/organizations/{organization_id}/ai-recommendations/risk/generate"
        in paths
    )
