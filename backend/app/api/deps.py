"""FastAPI dependency injection: Session → Repositories → Services."""

from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.ai.client import OllamaClient
from app.core.config import settings
from app.core.jwt import decode_access_token
from app.db.models import User
from app.db.session import get_db
from app.ingestion.storage import BronzeStorage
from app.repositories import (
    AnalysisRepository,
    DepartmentRepository,
    FinancialRepository,
    FinancialSnapshotRepository,
    OrganizationRepository,
    RecommendationRepository,
    ReportRepository,
    RiskRepository,
    SimulationRepository,
    TimelineRepository,
    UserRepository,
    WasteRepository,
)
from app.decision.service import DecisionService
from app.services import (
    AnalysisService,
    AuthService,
    DepartmentService,
    FinancialService,
    IngestionService,
    OrganizationService,
    RecommendationService,
    ReportService,
    RiskService,
    SimulationService,
    TimelineService,
    UserService,
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


def get_user_repository(
    db: Annotated[Session, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db)


def get_financial_snapshot_repository(
    db: Annotated[Session, Depends(get_db)],
) -> FinancialSnapshotRepository:
    return FinancialSnapshotRepository(db)


def get_bronze_storage() -> BronzeStorage:
    return BronzeStorage(settings.bronze_storage_root)


def get_ingestion_service(
    db: Annotated[Session, Depends(get_db)],
    financial_repo: Annotated[FinancialRepository, Depends(get_financial_repository)],
    snapshot_repo: Annotated[
        FinancialSnapshotRepository, Depends(get_financial_snapshot_repository)
    ],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    department_repo: Annotated[DepartmentRepository, Depends(get_department_repository)],
    bronze_storage: Annotated[BronzeStorage, Depends(get_bronze_storage)],
) -> IngestionService:
    return IngestionService(
        db,
        financial_repo,
        snapshot_repo,
        organization_repo,
        department_repo,
        bronze_storage,
        max_upload_size_bytes=settings.max_upload_size_bytes,
    )


def get_decision_service(
    db: Annotated[Session, Depends(get_db)],
    analysis_service: Annotated[AnalysisService, Depends(get_analysis_service)],
    waste_service: Annotated[WasteService, Depends(get_waste_service)],
    snapshot_repo: Annotated[
        FinancialSnapshotRepository, Depends(get_financial_snapshot_repository)
    ],
    financial_repo: Annotated[FinancialRepository, Depends(get_financial_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    analysis_repo: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
) -> DecisionService:
    return DecisionService(
        db,
        analysis_service,
        waste_service,
        snapshot_repo,
        financial_repo,
        organization_repo,
        analysis_repo,
    )


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


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> UserService:
    return UserService(db, user_repo, organization_repo)


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(db, user_repo, settings.auth)


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_access_token(credentials.credentials, settings.auth)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from None
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from None

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    try:
        user_id = uuid.UUID(str(subject))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from None

    user = user_repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


OrganizationServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)]
FinancialServiceDep = Annotated[FinancialService, Depends(get_financial_service)]
IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]
DecisionServiceDep = Annotated[DecisionService, Depends(get_decision_service)]
AnalysisServiceDep = Annotated[AnalysisService, Depends(get_analysis_service)]
WasteServiceDep = Annotated[WasteService, Depends(get_waste_service)]
RiskServiceDep = Annotated[RiskService, Depends(get_risk_service)]
SimulationServiceDep = Annotated[SimulationService, Depends(get_simulation_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
RecommendationServiceDep = Annotated[
    RecommendationService, Depends(get_recommendation_service)
]
TimelineServiceDep = Annotated[TimelineService, Depends(get_timeline_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_ollama_client() -> OllamaClient:
    return OllamaClient(settings.ai)


OllamaClientDep = Annotated[OllamaClient, Depends(get_ollama_client)]
PaginationDep = Annotated[PaginationParams, Depends()]
