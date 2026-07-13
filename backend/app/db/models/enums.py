from enum import StrEnum


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    READY_FOR_ANALYSIS = "ready_for_analysis"


class UploadSource(StrEnum):
    REPOSITORY = "repository"
    WASTE_ANALYSIS = "waste_analysis"


class ImportStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PROCESSING = "processing"


class AnalysisType(StrEnum):
    FINANCIAL_WASTE = "financial_waste"
    RISK = "risk"
    SIMULATION = "simulation"
    OPERATIONAL = "operational"
    HUMAN_RESOURCES = "human_resources"


class AnalysisRunStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskStatus(StrEnum):
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SimulationScenarioStatus(StrEnum):
    DRAFT = "draft"
    COMPLETED = "completed"


class MetricDirection(StrEnum):
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class SimulationActionStatus(StrEnum):
    PROPOSED = "proposed"


class ReportType(StrEnum):
    ANALYSIS = "analysis"
    RISK = "risk"
    SIMULATION = "simulation"
    PROCUREMENT = "procurement"
    COMPLIANCE = "compliance"


class ReportStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"


class RecommendationDomain(StrEnum):
    WASTE = "waste"
    RISK = "risk"
    SIMULATION = "simulation"
    DASHBOARD = "dashboard"


class RecommendationPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"


class TimelineEventType(StrEnum):
    ALERT = "alert"
    ANALYSIS = "analysis"
    REVIEW = "review"
    SYSTEM = "system"
    REPORT = "report"


class RelatedEntityType(StrEnum):
    ANALYSIS_RUN = "analysis_run"
    REPORT = "report"
    RISK = "risk"


class UserRole(StrEnum):
    ADMIN = "admin"
    EXECUTIVE = "executive"
    ANALYST = "analyst"
