"""SQLAlchemy ORM models for the Khazina MVP schema."""

from app.db.base import Base
from app.db.models.analysis import AnalysisRun
from app.db.models.department import Department
from app.db.models.organization import Organization, ReportingPeriod
from app.db.models.recommendation import Recommendation
from app.db.models.reporting import Report
from app.db.models.repository import (
    DataQualityCheck,
    DataQualitySnapshot,
    FinancialFile,
    ImportRecord,
)
from app.db.models.risk import Risk, RiskMitigationPlan
from app.db.models.simulation import (
    SimulationActionItem,
    SimulationAssumption,
    SimulationChartPoint,
    SimulationComparisonMetric,
    SimulationForecastSummary,
    SimulationImpactItem,
    SimulationRun,
    SimulationScenario,
)
from app.db.models.snapshot import FinancialSnapshot
from app.db.models.timeline import TimelineEvent
from app.db.models.user import User
from app.db.models.waste import (
    WasteAnalysisResult,
    WasteCategoryBreakdown,
    WasteTrendPoint,
    WasteVendorFinding,
)

__all__ = [
    "AnalysisRun",
    "Base",
    "DataQualityCheck",
    "DataQualitySnapshot",
    "Department",
    "FinancialFile",
    "FinancialSnapshot",
    "ImportRecord",
    "Organization",
    "Recommendation",
    "Report",
    "ReportingPeriod",
    "Risk",
    "RiskMitigationPlan",
    "SimulationActionItem",
    "SimulationAssumption",
    "SimulationChartPoint",
    "SimulationComparisonMetric",
    "SimulationForecastSummary",
    "SimulationImpactItem",
    "SimulationRun",
    "SimulationScenario",
    "TimelineEvent",
    "User",
    "WasteAnalysisResult",
    "WasteCategoryBreakdown",
    "WasteTrendPoint",
    "WasteVendorFinding",
]
