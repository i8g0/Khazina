"""Ingestion pipeline — Bronze to Silver (Sprint 6.2, ADR-010)."""

from app.ingestion.constants import PARSER_VERSION, SCHEMA_VERSION
from app.ingestion.exceptions import IngestionError, ParseError, ValidationFailure
from app.ingestion.orchestrator import IngestionOrchestrator
from app.ingestion.parser import FinancialFileParser
from app.ingestion.quality import DatasetQualityAssessor
from app.ingestion.storage import BronzeStorage
from app.ingestion.types import (
    IngestionResult,
    ParsedDataset,
    ParseMetadata,
    QualityAssessment,
    ValidationResult,
)
from app.ingestion.validator import DatasetValidator

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
