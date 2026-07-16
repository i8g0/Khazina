"""Authentication API tests (Sprint 8.1)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_auth_service
from app.main import create_app
from app.schemas.auth import TokenResponse
from app.services.exceptions import AuthenticationError


def test_login_requires_email_and_password(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["message"] == "Validation failed"


def test_login_rejects_empty_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": ""},
    )
    assert response.status_code == 422


def test_login_success_returns_token_envelope() -> None:
    app = create_app()
    mock_service = MagicMock()
    mock_service.login.return_value = TokenResponse(access_token="signed-jwt-token")

    app.dependency_overrides[get_auth_service] = lambda: mock_service
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "demo@khazina.sa", "password": "secret"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["access_token"] == "signed-jwt-token"
    assert payload["data"]["token_type"] == "bearer"
    mock_service.login.assert_called_once_with(
        email="demo@khazina.sa",
        password="secret",
    )


def test_login_invalid_credentials_returns_401() -> None:
    app = create_app()
    mock_service = MagicMock()
    mock_service.login.side_effect = AuthenticationError("Invalid email or password")

    app.dependency_overrides[get_auth_service] = lambda: mock_service
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "demo@khazina.sa", "password": "wrong"},
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
    assert payload["message"] == "Invalid email or password"
