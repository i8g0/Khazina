"""Service Layer — business logic orchestration on top of the Repository Layer.

Services receive an externally managed Session plus their repositories via
constructor injection, own all transaction boundaries (commit/rollback), and
raise business-level exceptions (``app.services.exceptions``). They contain
no HTTP concepts; translation to API responses belongs to upper layers.
"""

from app.services.base import BaseService
from app.services.exceptions import (
    AuthenticationError,
    BusinessRuleViolationError,
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    InvalidStateTransitionError,
    OwnershipViolationError,
    ResourceNotFoundError,
    ServiceError,
)

__all__ = [
    "AnalysisService",
    "AuthService",
    "AuthenticationError",
    "BaseService",
    "BusinessRuleViolationError",
    "BusinessValidationError",
    "DepartmentService",
    "DuplicateResourceError",
    "FinancialService",
    "IngestionService",
    "InvalidStateError",
    "InvalidStateTransitionError",
    "OrganizationService",
    "OwnershipViolationError",
    "RecommendationService",
    "ReportService",
    "ResourceNotFoundError",
    "RiskService",
    "ServiceError",
    "SimulationService",
    "TimelineService",
    "UserService",
    "UploadIngestionOutcome",
    "WasteService",
]

_SERVICE_EXPORTS = {
    "AnalysisService": "app.services.analysis",
    "AuthService": "app.services.auth",
    "DepartmentService": "app.services.department",
    "FinancialService": "app.services.financial",
    "IngestionService": "app.services.ingestion",
    "OrganizationService": "app.services.organization",
    "RecommendationService": "app.services.recommendation",
    "ReportService": "app.services.report",
    "RiskService": "app.services.risk",
    "SimulationService": "app.services.simulation",
    "TimelineService": "app.services.timeline",
    "UserService": "app.services.user",
    "WasteService": "app.services.waste",
    "UploadIngestionOutcome": "app.services.ingestion",
}


def __getattr__(name: str):
    if name in _SERVICE_EXPORTS:
        import importlib

        module = importlib.import_module(_SERVICE_EXPORTS[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
