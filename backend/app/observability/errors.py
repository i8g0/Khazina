"""Error classification for pipeline diagnostics (Sprint D5)."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy.exc import SQLAlchemyError

from app.ai.exceptions import AIConnectionError, AITimeoutError, AIError
from app.business.exceptions import EngineError
from app.ingestion.exceptions import ParseError, ValidationFailure, IngestionError
from app.reports.exceptions import ReportBuilderError
from app.services.exceptions import BusinessValidationError, ServiceError


class ErrorCategory(StrEnum):
    VALIDATION = "validation"
    AI = "ai"
    DATABASE = "database"
    FILE_UPLOAD = "file_upload"
    EXCEL_PARSING = "excel_parsing"
    SIMULATION = "simulation"
    REPORT_GENERATION = "report_generation"
    NETWORK = "network"
    UNKNOWN = "unknown"


def classify_exception(exc: BaseException) -> ErrorCategory:
    """Map an exception to a diagnostic category without changing API behavior."""
    exc_name = type(exc).__name__

    if isinstance(exc, ValidationFailure):
        return ErrorCategory.VALIDATION
    if exc_name == "SnapshotAdapterError":
        return ErrorCategory.VALIDATION
    if isinstance(exc, ParseError):
        return ErrorCategory.EXCEL_PARSING
    if isinstance(exc, IngestionError):
        return ErrorCategory.EXCEL_PARSING
    if isinstance(exc, BusinessValidationError):
        message = str(exc).lower()
        if "upload" in message or "file" in message:
            return ErrorCategory.FILE_UPLOAD
        return ErrorCategory.VALIDATION
    if isinstance(exc, (AIError, AIConnectionError, AITimeoutError)):
        return ErrorCategory.AI
    if exc_name == "AiRecommendationError":
        return ErrorCategory.AI
    if isinstance(exc, SQLAlchemyError):
        return ErrorCategory.DATABASE
    if isinstance(exc, ReportBuilderError):
        return ErrorCategory.REPORT_GENERATION
    if isinstance(exc, EngineError):
        return ErrorCategory.SIMULATION
    if isinstance(exc, ServiceError):
        name = exc_name.lower()
        if "auth" in name:
            return ErrorCategory.UNKNOWN
        if "notfound" in name or "ownership" in name:
            return ErrorCategory.VALIDATION
        return ErrorCategory.UNKNOWN
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return ErrorCategory.NETWORK
    return ErrorCategory.UNKNOWN
