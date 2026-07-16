"""AuthService unit tests (Sprint 8.1)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.core.config.auth import AuthSettings
from app.core.security import hash_password
from app.services.auth import AuthService
from app.services.exceptions import AuthenticationError


@pytest.fixture
def auth_settings() -> AuthSettings:
    return AuthSettings(
        jwt_secret_key="test-secret-key-for-sprint-81-qa",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=60,
    )


def test_login_success_issues_bearer_token(auth_settings: AuthSettings) -> None:
    user = MagicMock()
    user.id = "11111111-1111-1111-1111-111111111111"
    user.is_active = True
    user.password_hash = hash_password("secret")

    repo = MagicMock()
    repo.get_by_email.return_value = user
    session = MagicMock()
    service = AuthService(session, repo, auth_settings)

    token = service.login(email=" Demo@Khazina.SA ", password="secret")

    repo.get_by_email.assert_called_once_with("demo@khazina.sa")
    assert token.access_token
    assert token.token_type == "bearer"


def test_login_rejects_unknown_user(auth_settings: AuthSettings) -> None:
    repo = MagicMock()
    repo.get_by_email.return_value = None
    service = AuthService(MagicMock(), repo, auth_settings)

    with pytest.raises(AuthenticationError):
        service.login(email="missing@example.com", password="secret")


def test_login_rejects_inactive_user(auth_settings: AuthSettings) -> None:
    user = MagicMock()
    user.is_active = False
    repo = MagicMock()
    repo.get_by_email.return_value = user
    service = AuthService(MagicMock(), repo, auth_settings)

    with pytest.raises(AuthenticationError):
        service.login(email="inactive@example.com", password="secret")


def test_login_rejects_wrong_password(auth_settings: AuthSettings) -> None:
    user = MagicMock()
    user.is_active = True
    user.password_hash = hash_password("secret")
    repo = MagicMock()
    repo.get_by_email.return_value = user
    service = AuthService(MagicMock(), repo, auth_settings)

    with pytest.raises(AuthenticationError):
        service.login(email="user@example.com", password="wrong-password")
