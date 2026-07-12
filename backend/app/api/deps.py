"""FastAPI dependency injection: Session → Repositories → Services."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import (
    AnalysisRepository,
    DepartmentRepository,
    FinancialRepository,
    OrganizationRepository,
    RecommendationRepository,
    ReportRepository,
    RiskRepository,
    SimulationRepository,
    TimelineRepository,
    WasteRepository,
)
from app.services import (
    AnalysisService,
    DepartmentService,
    FinancialService,
    OrganizationService,
    RecommendationService,
    ReportService,
    RiskService,
    SimulationService,
    TimelineService,
    WasteService,
)


class PaginationParams:
    """Shared limit/offset query parameters for list endpoints."""

    def __init__(
        self,
        limit: int | None = Query(None, ge=1, le=100, description="Page size"),
        offset: int | None = Query(None, ge=0, description="Number of rows to skip"),
    ) -> None:
        self.limit = limit
        self.offset = offset


def get_organization_repository(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationRepository:
    return OrganizationRepository(db)


def get_department_repository(
    db: Annotated[Session, Depends(get_db)],
) -> DepartmentRepository:
    return DepartmentRepository(db)


def get_financial_repository(
    db: Annotated[Session, Depends(get_db)],
) -> FinancialRepository:
    return FinancialRepository(db)


def get_analysis_repository(
    db: Annotated[Session, Depends(get_db)],
) -> AnalysisRepository:
    return AnalysisRepository(db)


def get_waste_repository(
    db: Annotated[Session, Depends(get_db)],
) -> WasteRepository:
    return WasteRepository(db)


def get_risk_repository(
    db: Annotated[Session, Depends(get_db)],
) -> RiskRepository:
    return RiskRepository(db)


def get_simulation_repository(
    db: Annotated[Session, Depends(get_db)],
) -> SimulationRepository:
    return SimulationRepository(db)


def get_report_repository(
    db: Annotated[Session, Depends(get_db)],
) -> ReportRepository:
    return ReportRepository(db)


def get_recommendation_repository(
    db: Annotated[Session, Depends(get_db)],
) -> RecommendationRepository:
    return RecommendationRepository(db)


def get_timeline_repository(
    db: Annotated[Session, Depends(get_db)],
) -> TimelineRepository:
    return TimelineRepository(db)


def get_organization_service(
    db: Annotated[Session, Depends(get_db)],
    repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
) -> OrganizationService:
    return OrganizationService(db, repo)


def get_department_service(
    db: Annotated[Session, Depends(get_db)],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> DepartmentService:
    return DepartmentService(db, department_repo, organization_repo)


def get_financial_service(
    db: Annotated[Session, Depends(get_db)],
    financial_repo: Annotated[FinancialRepository, Depends(get_financial_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
) -> FinancialService:
    return FinancialService(db, financial_repo, organization_repo, department_repo)


def get_analysis_service(
    db: Annotated[Session, Depends(get_db)],
    analysis_repo: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    financial_repo: Annotated[FinancialRepository, Depends(get_financial_repository)],
    timeline_repo: Annotated[TimelineRepository, Depends(get_timeline_repository)],
) -> AnalysisService:
    return AnalysisService(
        db, analysis_repo, organization_repo, financial_repo, timeline_repo
    )


def get_waste_service(
    db: Annotated[Session, Depends(get_db)],
    waste_repo: Annotated[WasteRepository, Depends(get_waste_repository)],
    analysis_repo: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
) -> WasteService:
    return WasteService(
        db, waste_repo, analysis_repo, organization_repo, department_repo
    )


def get_risk_service(
    db: Annotated[Session, Depends(get_db)],
    risk_repo: Annotated[RiskRepository, Depends(get_risk_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
) -> RiskService:
    return RiskService(db, risk_repo, organization_repo, department_repo)


def get_simulation_service(
    db: Annotated[Session, Depends(get_db)],
    simulation_repo: Annotated[SimulationRepository, Depends(get_simulation_repository)],
    analysis_repo: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> SimulationService:
    return SimulationService(db, simulation_repo, analysis_repo, organization_repo)


def get_report_service(
    db: Annotated[Session, Depends(get_db)],
    report_repo: Annotated[ReportRepository, Depends(get_report_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
    analysis_repo: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    financial_repo: Annotated[FinancialRepository, Depends(get_financial_repository)],
    timeline_repo: Annotated[TimelineRepository, Depends(get_timeline_repository)],
) -> ReportService:
    return ReportService(
        db,
        report_repo,
        organization_repo,
        department_repo,
        analysis_repo,
        financial_repo,
        timeline_repo,
    )


def get_recommendation_service(
    db: Annotated[Session, Depends(get_db)],
    recommendation_repo: Annotated[
        RecommendationRepository, Depends(get_recommendation_repository)
    ],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
    analysis_repo: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    risk_repo: Annotated[RiskRepository, Depends(get_risk_repository)],
    simulation_repo: Annotated[SimulationRepository, Depends(get_simulation_repository)],
) -> RecommendationService:
    return RecommendationService(
        db,
        recommendation_repo,
        organization_repo,
        department_repo,
        analysis_repo,
        risk_repo,
        simulation_repo,
    )


def get_timeline_service(
    db: Annotated[Session, Depends(get_db)],
    timeline_repo: Annotated[TimelineRepository, Depends(get_timeline_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> TimelineService:
    return TimelineService(db, timeline_repo, organization_repo)


OrganizationServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)]
FinancialServiceDep = Annotated[FinancialService, Depends(get_financial_service)]
AnalysisServiceDep = Annotated[AnalysisService, Depends(get_analysis_service)]
WasteServiceDep = Annotated[WasteService, Depends(get_waste_service)]
RiskServiceDep = Annotated[RiskService, Depends(get_risk_service)]
SimulationServiceDep = Annotated[SimulationService, Depends(get_simulation_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
RecommendationServiceDep = Annotated[
    RecommendationService, Depends(get_recommendation_service)
]
TimelineServiceDep = Annotated[TimelineService, Depends(get_timeline_service)]
PaginationDep = Annotated[PaginationParams, Depends()]
