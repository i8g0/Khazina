"""Risk management API schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class RiskCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    priority: str = Field(..., max_length=50)
    score: int = Field(..., ge=0, le=100)
    department_id: UUID | None = None
    reporting_period_id: UUID | None = None
    owner_label: str | None = Field(None, max_length=200)
    likelihood: str | None = Field(None, max_length=50)
    impact: str | None = Field(None, max_length=50)
    category_label: str | None = Field(None, max_length=100)


class RiskUpdate(SchemaBase):
    name: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, min_length=1)
    priority: str | None = Field(None, max_length=50)
    score: int | None = Field(None, ge=0, le=100)
    owner_label: str | None = Field(None, max_length=200)
    likelihood: str | None = Field(None, max_length=50)
    impact: str | None = Field(None, max_length=50)
    category_label: str | None = Field(None, max_length=100)


class RiskTransitionRequest(SchemaBase):
    status: str = Field(..., max_length=50)


class RiskResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    department_id: UUID | None
    reporting_period_id: UUID | None
    name: str
    description: str
    priority: str
    score: int
    status: str
    lifecycle_status: str | None = None
    owner_label: str | None
    likelihood: str | None
    impact: str | None
    category_label: str | None
    category_code: str | None = None
    source_type: str | None = None
    source_analysis_run_id: UUID | None = None
    source_finding_id: UUID | None = None
    source_snapshot_id: UUID | None = None
    detected_at: datetime | None = None
    last_updated_at: date


class MitigationPlanCreate(SchemaBase):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1, max_length=50)
    target_date: date
    owner_label: str | None = Field(None, max_length=200)


class MitigationPlanUpdate(SchemaBase):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, min_length=1)
    status: str | None = Field(None, min_length=1, max_length=50)
    target_date: date | None = None
    owner_label: str | None = Field(None, max_length=200)


class MitigationPlanResponse(FullTimestampResponse):
    id: UUID
    risk_id: UUID
    title: str
    description: str
    status: str
    target_date: date
    owner_label: str | None
