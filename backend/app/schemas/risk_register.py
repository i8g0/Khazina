"""Enterprise Risk Register governance API schemas (Sprint 9.4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import ConfigDict, Field

from app.schemas.common import SchemaBase, TimestampResponse
from app.schemas.risk import RiskResponse


class RiskReviewRequest(SchemaBase):
    action: str = Field(..., max_length=50)
    reason: str | None = Field(None, max_length=2000)


class RiskPromoteRequest(SchemaBase):
    owner_label: str | None = Field(None, max_length=200)
    department_id: UUID | None = None
    reason: str | None = Field(None, max_length=2000)


class RiskLifecycleStatusUpdate(SchemaBase):
    lifecycle_status: str = Field(..., max_length=50)
    reason: str | None = Field(None, max_length=2000)


class RiskEventResponse(TimestampResponse):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    risk_id: UUID | None
    organization_id: UUID
    event_type: str
    from_status: str | None
    to_status: str | None
    actor_user_id: UUID | None
    reason: str | None
    metadata: dict[str, Any] = Field(validation_alias="event_metadata")


class RiskPromotionResponse(SchemaBase):
    finding_id: UUID
    finding_status: str
    risk: RiskResponse


class RiskProvenanceResponse(SchemaBase):
    risk_id: UUID
    source_type: str | None
    source_snapshot_id: UUID | None
    source_analysis_run_id: UUID | None
    source_finding_id: UUID | None
    detected_at: datetime | None
    finding: dict[str, Any] | None
    analysis_run: dict[str, Any] | None
