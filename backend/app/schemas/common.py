"""Shared Pydantic schema utilities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchemaBase(BaseModel):
    """Base for API schemas with ORM attribute mapping."""

    model_config = ConfigDict(from_attributes=True)


class TimestampResponse(SchemaBase):
    created_at: datetime


class FullTimestampResponse(SchemaBase):
    created_at: datetime
    updated_at: datetime


class MessageResponse(SchemaBase):
    """Empty success payload for delete and action endpoints."""

    detail: str = Field(..., examples=["Operation completed successfully"])


class UUIDParam(BaseModel):
    """Reusable UUID path parameter documentation."""

    id: UUID
