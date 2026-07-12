"""Department API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class DepartmentCreate(SchemaBase):
    name_ar: str = Field(..., min_length=1, max_length=100)
    code: str | None = Field(None, max_length=50)
    display_order: int = Field(0, ge=0)


class DepartmentUpdate(SchemaBase):
    name_ar: str | None = Field(None, min_length=1, max_length=100)
    code: str | None = Field(None, max_length=50)
    display_order: int | None = Field(None, ge=0)


class DepartmentResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    name_ar: str
    code: str | None
    display_order: int
    is_active: bool
