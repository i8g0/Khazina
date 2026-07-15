"""Repository Layer — encapsulates all SQLAlchemy database access by business domain.

Repositories receive an externally managed Session (dependency injection) and
never commit; transaction orchestration belongs to the Service Layer.
"""

from app.repositories.analysis import AnalysisRepository
from app.repositories.base import BaseRepository
from app.repositories.department import DepartmentRepository
from app.repositories.exceptions import EntityNotFoundError
from app.repositories.financial import FinancialRepository
from app.repositories.snapshot import FinancialSnapshotRepository
from app.repositories.notification import NotificationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.recommendation import RecommendationRepository
from app.repositories.report import ReportRepository
from app.repositories.risk import RiskRepository
from app.repositories.settings import SettingsRepository
from app.repositories.simulation import SimulationRepository
from app.repositories.timeline import TimelineRepository
from app.repositories.user import UserRepository
from app.repositories.waste import WasteRepository

__all__ = [
    "AnalysisRepository",
    "BaseRepository",
    "DepartmentRepository",
    "EntityNotFoundError",
    "FinancialRepository",
    "FinancialSnapshotRepository",
    "NotificationRepository",
    "OrganizationRepository",
    "RecommendationRepository",
    "ReportRepository",
    "RiskRepository",
    "SettingsRepository",
    "SimulationRepository",
    "TimelineRepository",
    "UserRepository",
    "WasteRepository",
]
