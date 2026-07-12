"""Financial Waste Detection services: waste result recording and retrieval."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    AnalysisRun,
    WasteAnalysisResult,
    WasteCategoryBreakdown,
    WasteTrendPoint,
    WasteVendorFinding,
)
from app.db.models.enums import AnalysisType
from app.repositories import (
    AnalysisRepository,
    DepartmentRepository,
    OrganizationRepository,
    WasteRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    ResourceNotFoundError,
)


class WasteService(BaseService):
    """Business use cases for waste analysis outcomes.

    Results attach 1:1 to a ``financial_waste`` analysis run; breakdowns,
    vendor findings, and trend points are recorded as part of the same
    workflow. AI detection itself is out of scope — this service persists
    and validates the outcome the engine will produce.
    """

    def __init__(
        self,
        session: Session,
        waste_repository: WasteRepository,
        analysis_repository: AnalysisRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
    ) -> None:
        super().__init__(session)
        self._waste = waste_repository
        self._analyses = analysis_repository
        self._organizations = organization_repository
        self._departments = department_repository

    # -- result recording ------------------------------------------------------

    def record_result(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        total_waste_amount: float,
        waste_percentage: float,
        top_category_name: str | None = None,
        top_category_percentage: float | None = None,
        potential_savings_amount: float | None = None,
        active_savings_opportunities: int | None = None,
        category_breakdowns: list[dict[str, Any]] | None = None,
        vendor_findings: list[dict[str, Any]] | None = None,
    ) -> WasteAnalysisResult:
        """Records the full waste outcome for a run in a single transaction."""
        run = self._waste_run(organization_id, analysis_run_id)
        if self._waste.get_result_for_run(run.id) is not None:
            raise DuplicateResourceError(
                f"Analysis run '{run.id}' already has a waste result"
            )
        if total_waste_amount < 0:
            raise BusinessValidationError("Total waste amount must not be negative")
        self._validate_percentage(waste_percentage, "Waste percentage")
        if top_category_percentage is not None:
            self._validate_percentage(
                top_category_percentage, "Top category percentage"
            )

        breakdown_rows = self._build_breakdowns(
            organization_id, run.id, category_breakdowns or []
        )
        finding_rows = self._build_findings(run.id, vendor_findings or [])

        result = WasteAnalysisResult(
            analysis_run_id=run.id,
            total_waste_amount=total_waste_amount,
            waste_percentage=waste_percentage,
            top_category_name=top_category_name,
            top_category_percentage=top_category_percentage,
            potential_savings_amount=potential_savings_amount,
            active_savings_opportunities=active_savings_opportunities,
        )
        with self._transaction():
            self._waste.create_result(result)
            if breakdown_rows:
                self._waste.add_category_breakdowns(breakdown_rows)
            if finding_rows:
                self._waste.add_vendor_findings(finding_rows)
        return result

    # -- retrieval -----------------------------------------------------------------

    def get_result_for_run(
        self, organization_id: uuid.UUID, analysis_run_id: uuid.UUID
    ) -> WasteAnalysisResult:
        run = self._waste_run(organization_id, analysis_run_id)
        result = self._waste.get_result_for_run(run.id)
        if result is None:
            raise ResourceNotFoundError("WasteAnalysisResult", analysis_run_id)
        return result

    def list_category_breakdowns(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        department_id: uuid.UUID | None = None,
    ) -> list[WasteCategoryBreakdown]:
        run = self._waste_run(organization_id, analysis_run_id)
        return self._waste.list_category_breakdowns(
            run.id, department_id=department_id
        )

    def list_vendor_findings(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[WasteVendorFinding]:
        run = self._waste_run(organization_id, analysis_run_id)
        return self._waste.list_vendor_findings(run.id, limit=limit, offset=offset)

    # -- trend points ------------------------------------------------------------------

    def upsert_trend_point(
        self,
        organization_id: uuid.UUID,
        *,
        month_label: str,
        month_order: int,
        waste_amount: float,
        reporting_period_id: uuid.UUID | None = None,
    ) -> WasteTrendPoint:
        """Creates or updates the unique (org, period, month) trend point."""
        self._require_organization(organization_id)
        month_label = month_label.strip()
        if not month_label:
            raise BusinessValidationError("Month label must not be empty")
        if waste_amount < 0:
            raise BusinessValidationError("Waste amount must not be negative")
        if reporting_period_id is not None:
            period = self._organizations.get_reporting_period(reporting_period_id)
            if period is None:
                raise ResourceNotFoundError("ReportingPeriod", reporting_period_id)
            self._check_ownership(period, "ReportingPeriod", organization_id)

        existing = self._waste.get_trend_point(
            organization_id, reporting_period_id, month_label
        )
        with self._transaction():
            if existing is not None:
                point = self._waste.update_trend_point(
                    existing,
                    {"waste_amount": waste_amount, "month_order": month_order},
                )
            else:
                point = self._waste.create_trend_point(
                    WasteTrendPoint(
                        organization_id=organization_id,
                        reporting_period_id=reporting_period_id,
                        month_label=month_label,
                        month_order=month_order,
                        waste_amount=waste_amount,
                    )
                )
        return point

    def list_trend_points(
        self,
        organization_id: uuid.UUID,
        *,
        reporting_period_id: uuid.UUID | None = None,
    ) -> list[WasteTrendPoint]:
        self._require_organization(organization_id)
        return self._waste.list_trend_points(
            organization_id, reporting_period_id=reporting_period_id
        )

    # -- internals ---------------------------------------------------------------------

    def _waste_run(
        self, organization_id: uuid.UUID, analysis_run_id: uuid.UUID
    ) -> AnalysisRun:
        run = self._analyses.get(analysis_run_id)
        if run is None:
            raise ResourceNotFoundError("AnalysisRun", analysis_run_id)
        self._check_ownership(run, "AnalysisRun", organization_id)
        if run.analysis_type != AnalysisType.FINANCIAL_WASTE:
            raise InvalidStateError(
                "Waste results can only attach to 'financial_waste' runs "
                f"(run type: '{run.analysis_type}')"
            )
        return run

    def _build_breakdowns(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID,
        breakdowns: list[dict[str, Any]],
    ) -> list[WasteCategoryBreakdown]:
        rows: list[WasteCategoryBreakdown] = []
        for order, item in enumerate(breakdowns):
            category_name = str(item.get("category_name", "")).strip()
            if not category_name:
                raise BusinessValidationError(
                    "Each category breakdown requires a category_name"
                )
            amount = item.get("amount")
            percentage = item.get("percentage")
            if amount is None or amount < 0:
                raise BusinessValidationError(
                    "Each category breakdown requires a non-negative amount"
                )
            self._validate_percentage(percentage, "Category percentage")
            department_id = item.get("department_id")
            if department_id is not None:
                department = self._departments.get(department_id)
                if department is None:
                    raise ResourceNotFoundError("Department", department_id)
                self._check_ownership(department, "Department", organization_id)
            rows.append(
                WasteCategoryBreakdown(
                    analysis_run_id=analysis_run_id,
                    department_id=department_id,
                    category_name=category_name,
                    amount=amount,
                    percentage=percentage,
                    display_order=item.get("display_order", order),
                )
            )
        return rows

    @staticmethod
    def _build_findings(
        analysis_run_id: uuid.UUID, findings: list[dict[str, Any]]
    ) -> list[WasteVendorFinding]:
        rows: list[WasteVendorFinding] = []
        for item in findings:
            vendor_name = str(item.get("vendor_name", "")).strip()
            status = str(item.get("status", "")).strip()
            amount = item.get("amount")
            if not vendor_name or not status:
                raise BusinessValidationError(
                    "Each vendor finding requires vendor_name and status"
                )
            if amount is None or amount < 0:
                raise BusinessValidationError(
                    "Each vendor finding requires a non-negative amount"
                )
            rows.append(
                WasteVendorFinding(
                    analysis_run_id=analysis_run_id,
                    vendor_name=vendor_name,
                    category_label=item.get("category_label"),
                    amount=amount,
                    deviation_label=item.get("deviation_label"),
                    status=status,
                )
            )
        return rows

    @staticmethod
    def _validate_percentage(value: float | None, label: str) -> None:
        if value is None or not 0 <= value <= 100:
            raise BusinessValidationError(f"{label} must be between 0 and 100")

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
