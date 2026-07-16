"""AI infrastructure API schemas."""

from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaBase


class AiHealthData(SchemaBase):
    status: str = Field(..., examples=["ok", "unavailable"])
    provider: str = Field(..., examples=["ollama", "cloud"])
    provider_reachable: bool
    ollama_reachable: bool
    configured_model: str
    message: str
