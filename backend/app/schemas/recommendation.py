"""Recommendation API schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


class RecommendationCreate(SchemaBase):
    domain_source: str = Field(..., max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    priority: str = Field(..., max_length=50)
    external_ref: str | None = Field(None, max_length=50)
    confidence_label: str | None = Field(None, max_length=20)
    estimated_savings_amount: float | None = Field(None, ge=0)
    department_id: UUID | None = None
    analysis_run_id: UUID | None = None
    risk_id: UUID | None = None
    simulation_run_id: UUID | None = None
    is_dashboard_featured: bool = False
    source_context: dict[str, Any] | None = None


class RecommendationResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    domain_source: str
    external_ref: str | None
    title: str
    description: str
    priority: str
    confidence_label: str | None
    estimated_savings_amount: float | None
    department_id: UUID | None
    analysis_run_id: UUID | None
    risk_id: UUID | None
    simulation_run_id: UUID | None
    is_dashboard_featured: bool
    source_context: dict[str, Any] | None
