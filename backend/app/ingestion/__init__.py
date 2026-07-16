"""Ingestion pipeline — Bronze to Silver (Sprint 6.2, ADR-010)."""

from app.ingestion.constants import PARSER_VERSION, SCHEMA_VERSION
from app.ingestion.exceptions import IngestionError, ParseError, ValidationFailure
from app.ingestion.types import (
    IngestionResult,
    ParsedDataset,
    ParseMetadata,
    QualityAssessment,
    ValidationResult,
)

__all__ = [
    "PARSER_VERSION",
    "SCHEMA_VERSION",
    "BronzeStorage",
    "DatasetQualityAssessor",
    "DatasetValidator",
    "FinancialFileParser",
    "IngestionError",
    "IngestionOrchestrator",
    "IngestionResult",
    "ParseError",
    "ParseMetadata",
    "ParsedDataset",
    "QualityAssessment",
    "ValidationFailure",
    "ValidationResult",
]


def __getattr__(name: str):
    """Lazy exports to avoid import cycles with observability (Sprint 8.1)."""
    if name == "BronzeStorage":
        from app.ingestion.storage import BronzeStorage

        return BronzeStorage
    if name == "DatasetQualityAssessor":
        from app.ingestion.quality import DatasetQualityAssessor

        return DatasetQualityAssessor
    if name == "DatasetValidator":
        from app.ingestion.validator import DatasetValidator

        return DatasetValidator
    if name == "FinancialFileParser":
        from app.ingestion.parser import FinancialFileParser

        return FinancialFileParser
    if name == "IngestionOrchestrator":
        from app.ingestion.orchestrator import IngestionOrchestrator

        return IngestionOrchestrator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
