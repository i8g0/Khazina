"""Waste analysis API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampResponse


class WasteCategoryBreakdownInput(SchemaBase):
    category_name: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)
    department_id: UUID | None = None
    display_order: int = Field(0, ge=0)


class WasteVendorFindingInput(SchemaBase):
    vendor_name: str = Field(..., min_length=1, max_length=300)
    amount: float = Field(..., ge=0)
    status: str = Field(..., min_length=1, max_length=50)
    category_label: str | None = Field(None, max_length=100)
    deviation_label: str | None = Field(None, max_length=20)


class WasteResultCreate(SchemaBase):
    total_waste_amount: float = Field(..., ge=0)
    waste_percentage: float = Field(..., ge=0, le=100)
    top_category_name: str | None = Field(None, max_length=200)
    top_category_percentage: float | None = Field(None, ge=0, le=100)
    potential_savings_amount: float | None = None
    active_savings_opportunities: int | None = Field(None, ge=0)
    category_breakdowns: list[WasteCategoryBreakdownInput] | None = None
    vendor_findings: list[WasteVendorFindingInput] | None = None


class WasteAnalysisResultResponse(TimestampResponse):
    id: UUID
    analysis_run_id: UUID
    total_waste_amount: float
    waste_percentage: float
    top_category_name: str | None
    top_category_percentage: float | None
    potential_savings_amount: float | None
    active_savings_opportunities: int | None


class WasteCategoryBreakdownResponse(TimestampResponse):
    id: UUID
    analysis_run_id: UUID
    department_id: UUID | None
    category_name: str
    amount: float
    percentage: float
    display_order: int


class WasteVendorFindingResponse(TimestampResponse):
    id: UUID
    analysis_run_id: UUID
    vendor_name: str
    category_label: str | None
    amount: float
    deviation_label: str | None
    status: str


class WasteTrendPointUpsert(SchemaBase):
    month_label: str = Field(..., min_length=1, max_length=50)
    month_order: int = Field(..., ge=0)
    waste_amount: float = Field(..., ge=0)
    reporting_period_id: UUID | None = None


class WasteTrendPointResponse(SchemaBase):
    id: UUID
    organization_id: UUID
    reporting_period_id: UUID | None
    month_label: str
    month_order: int
    waste_amount: float
    created_at: datetime
    updated_at: datetime
