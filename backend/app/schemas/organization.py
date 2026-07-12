"""Organization and reporting period API schemas."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import Field

from app.schemas.common import FullTimestampResponse, SchemaBase


# -- Organization --------------------------------------------------------------


class OrganizationCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=255)
    platform_name: str | None = Field(None, max_length=100)
    executive_title: str | None = Field(None, max_length=255)


class OrganizationUpdate(SchemaBase):
    name: str | None = Field(None, min_length=1, max_length=255)
    platform_name: str | None = Field(None, max_length=100)
    executive_title: str | None = Field(None, max_length=255)


class OrganizationResponse(FullTimestampResponse):
    id: UUID
    name: str
    platform_name: str
    executive_title: str | None
    is_active: bool


# -- Reporting period ----------------------------------------------------------


class ReportingPeriodCreate(SchemaBase):
    label: str = Field(..., min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    activate: bool = False


class ReportingPeriodUpdate(SchemaBase):
    label: str | None = Field(None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None


class ReportingPeriodResponse(FullTimestampResponse):
    id: UUID
    organization_id: UUID
    label: str
    start_date: date | None
    end_date: date | None
    is_active: bool
