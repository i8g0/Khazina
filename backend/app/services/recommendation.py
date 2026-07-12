"""AI Recommendations services: centralized recommendation registry workflow."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Recommendation
from app.db.models.enums import RecommendationDomain, RecommendationPriority
from app.repositories import (
    AnalysisRepository,
    DepartmentRepository,
    OrganizationRepository,
    RecommendationRepository,
    RiskRepository,
    SimulationRepository,
)
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    InvalidStateError,
    ResourceNotFoundError,
)


class RecommendationService(BaseService):
    """Business use cases for AI-generated recommendations.

    Enforces the approved exclusive-source rule: a recommendation may link to
    at most one of analysis run, risk, or simulation run. AI generation is
    out of scope; this service registers and manages the outcomes.
    """

    def __init__(
        self,
        session: Session,
        recommendation_repository: RecommendationRepository,
        organization_repository: OrganizationRepository,
        department_repository: DepartmentRepository,
        analysis_repository: AnalysisRepository,
        risk_repository: RiskRepository,
        simulation_repository: SimulationRepository,
    ) -> None:
        super().__init__(session)
        self._recommendations = recommendation_repository
        self._organizations = organization_repository
        self._departments = department_repository
        self._analyses = analysis_repository
        self._risks = risk_repository
        self._simulations = simulation_repository

    # -- registration ------------------------------------------------------------

    def register_recommendation(
        self,
        organization_id: uuid.UUID,
        *,
        domain_source: str,
        title: str,
        description: str,
        priority: str,
        external_ref: str | None = None,
        confidence_label: str | None = None,
        estimated_savings_amount: float | None = None,
        department_id: uuid.UUID | None = None,
        analysis_run_id: uuid.UUID | None = None,
        risk_id: uuid.UUID | None = None,
        simulation_run_id: uuid.UUID | None = None,
        is_dashboard_featured: bool = False,
        source_context: dict[str, Any] | None = None,
    ) -> Recommendation:
        self._require_organization(organization_id)
        title = title.strip()
        description = description.strip()
        if not title or not description:
            raise BusinessValidationError(
                "Recommendation title and description must not be empty"
            )
        if domain_source not in set(RecommendationDomain):
            raise BusinessValidationError(
                f"Unknown recommendation domain '{domain_source}'"
            )
        if priority not in set(RecommendationPriority):
            raise BusinessValidationError(
                f"Unknown recommendation priority '{priority}'"
            )
        if estimated_savings_amount is not None and estimated_savings_amount < 0:
            raise BusinessValidationError(
                "Estimated savings amount must not be negative"
            )

        source_fks = [analysis_run_id, risk_id, simulation_run_id]
        if sum(fk is not None for fk in source_fks) > 1:
            raise BusinessValidationError(
                "A recommendation may reference at most one source "
                "(analysis run, risk, or simulation run)"
            )
        self._validate_source_ownership(
            organization_id, analysis_run_id, risk_id, simulation_run_id
        )
        if department_id is not None:
            department = self._departments.get(department_id)
            if department is None:
                raise ResourceNotFoundError("Department", department_id)
            self._check_ownership(department, "Department", organization_id)

        recommendation = Recommendation(
            organization_id=organization_id,
            domain_source=domain_source,
            external_ref=external_ref,
            title=title,
            description=description,
            priority=priority,
            confidence_label=confidence_label,
            estimated_savings_amount=estimated_savings_amount,
            department_id=department_id,
            analysis_run_id=analysis_run_id,
            risk_id=risk_id,
            simulation_run_id=simulation_run_id,
            is_dashboard_featured=is_dashboard_featured,
            source_context=source_context,
        )
        with self._transaction():
            self._recommendations.create(recommendation)
        return recommendation

    # -- retrieval -----------------------------------------------------------------

    def get_recommendation(self, recommendation_id: uuid.UUID) -> Recommendation:
        return self._found(
            self._recommendations.get(recommendation_id),
            "Recommendation",
            recommendation_id,
        )

    def list_recommendations(
        self,
        organization_id: uuid.UUID,
        *,
        domain_source: str | None = None,
        priority: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Recommendation]:
        self._require_organization(organization_id)
        return self._recommendations.list_for_organization(
            organization_id,
            domain_source=domain_source,
            priority=priority,
            limit=limit,
            offset=offset,
        )

    def list_dashboard_featured(
        self, organization_id: uuid.UUID, *, limit: int = 5
    ) -> list[Recommendation]:
        self._require_organization(organization_id)
        return self._recommendations.list_dashboard_featured(
            organization_id, limit=limit
        )

    # -- dashboard surfacing ----------------------------------------------------------

    def feature_on_dashboard(
        self, organization_id: uuid.UUID, recommendation_id: uuid.UUID
    ) -> Recommendation:
        recommendation = self._owned(organization_id, recommendation_id)
        if recommendation.is_dashboard_featured:
            raise InvalidStateError("Recommendation is already dashboard-featured")
        with self._transaction():
            self._recommendations.update(
                recommendation, {"is_dashboard_featured": True}
            )
        return recommendation

    def unfeature_from_dashboard(
        self, organization_id: uuid.UUID, recommendation_id: uuid.UUID
    ) -> Recommendation:
        recommendation = self._owned(organization_id, recommendation_id)
        if not recommendation.is_dashboard_featured:
            raise InvalidStateError("Recommendation is not dashboard-featured")
        with self._transaction():
            self._recommendations.update(
                recommendation, {"is_dashboard_featured": False}
            )
        return recommendation

    def delete_recommendation(
        self, organization_id: uuid.UUID, recommendation_id: uuid.UUID
    ) -> None:
        recommendation = self._owned(organization_id, recommendation_id)
        with self._transaction():
            self._recommendations.delete(recommendation)

    # -- internals ---------------------------------------------------------------------

    def _owned(
        self, organization_id: uuid.UUID, recommendation_id: uuid.UUID
    ) -> Recommendation:
        recommendation = self.get_recommendation(recommendation_id)
        self._check_ownership(recommendation, "Recommendation", organization_id)
        return recommendation

    def _validate_source_ownership(
        self,
        organization_id: uuid.UUID,
        analysis_run_id: uuid.UUID | None,
        risk_id: uuid.UUID | None,
        simulation_run_id: uuid.UUID | None,
    ) -> None:
        if analysis_run_id is not None:
            run = self._analyses.get(analysis_run_id)
            if run is None:
                raise ResourceNotFoundError("AnalysisRun", analysis_run_id)
            self._check_ownership(run, "AnalysisRun", organization_id)
        if risk_id is not None:
            risk = self._risks.get(risk_id)
            if risk is None:
                raise ResourceNotFoundError("Risk", risk_id)
            self._check_ownership(risk, "Risk", organization_id)
        if simulation_run_id is not None:
            simulation_run = self._simulations.get_run(simulation_run_id)
            if simulation_run is None:
                raise ResourceNotFoundError("SimulationRun", simulation_run_id)
            scenario = self._simulations.get_scenario(simulation_run.scenario_id)
            if scenario is None:
                raise ResourceNotFoundError(
                    "SimulationScenario", simulation_run.scenario_id
                )
            self._check_ownership(
                scenario, "SimulationScenario", organization_id
            )

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
