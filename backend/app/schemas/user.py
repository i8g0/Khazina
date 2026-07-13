"""User API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.db.models.enums import UserRole
from app.schemas.common import FullTimestampResponse, SchemaBase


class UserCreate(SchemaBase):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.ANALYST


class UserUpdate(SchemaBase):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, min_length=3, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=128)
    role: UserRole | None = None


class UserResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    full_name: str
    email: str
    role: UserRole
    is_active: bool
