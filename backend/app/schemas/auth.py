"""Authentication API schemas."""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaBase


class LoginRequest(SchemaBase):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(SchemaBase):
    access_token: str
    token_type: str = "bearer"
