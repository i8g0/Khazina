"""JWT access-token utilities."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config.auth import AuthSettings


def create_access_token(*, subject: str, auth_settings: AuthSettings) -> str:
    """Create a signed JWT access token for the given subject (user id)."""
    expire = datetime.now(UTC) + timedelta(
        minutes=auth_settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(
        payload,
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )


def decode_access_token(token: str, auth_settings: AuthSettings) -> dict:
    """Decode and validate a JWT access token; raises ``jwt.PyJWTError`` on failure."""
    return jwt.decode(
        token,
        auth_settings.jwt_secret_key,
        algorithms=[auth_settings.jwt_algorithm],
    )
