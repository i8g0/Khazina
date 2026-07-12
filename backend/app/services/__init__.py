"""Service Layer — business logic orchestration on top of the Repository Layer.

Services receive an externally managed Session plus their repositories via
constructor injection, own all transaction boundaries (commit/rollback), and
raise business-level exceptions (``app.services.exceptions``). They contain
no HTTP concepts; translation to API responses belongs to upper layers.
"""

from app.services.analysis import AnalysisService
from app.services.base import BaseService
from app.services.department import DepartmentService
from app.services.exceptions import (
    BusinessRuleViolationError,
    BusinessValidationError,
    DuplicateResourceError,
    InvalidStateError,
    InvalidStateTransitionError,
    OwnershipViolationError,
    ResourceNotFoundError,
    ServiceError,
)
from app.services.financial import FinancialService
from app.services.organization import OrganizationService
from app.services.recommendation import RecommendationService
from app.services.report import ReportService
from app.services.risk import RiskService
from app.services.simulation import SimulationService
from app.services.timeline import TimelineService
from app.services.waste import WasteService

__all__ = [
    "AnalysisService",
    "BaseService",
    "BusinessRuleViolationError",
    "BusinessValidationError",
    "DepartmentService",
    "DuplicateResourceError",
    "FinancialService",
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
    "WasteService",
]
