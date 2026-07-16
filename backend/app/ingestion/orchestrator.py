"""Ingestion pipeline orchestration — parse, validate, quality."""

from __future__ import annotations

from app.ingestion.exceptions import ParseError, ValidationFailure
from app.ingestion.parser import FinancialFileParser
from app.ingestion.quality import DatasetQualityAssessor
from app.ingestion.types import IngestionResult
from app.ingestion.validator import DatasetValidator
from app.ingestion.waste_template import validate_waste_template
from app.observability.pipeline import PipelineStage, PipelineTimeline


class IngestionOrchestrator:
    """Coordinates deterministic ingestion stages without business logic or AI."""

    # Sprint D4: W-1 template gate runs after structural validation.

    def __init__(
        self,
        parser: FinancialFileParser | None = None,
        validator: DatasetValidator | None = None,
        quality_assessor: DatasetQualityAssessor | None = None,
    ) -> None:
        self._parser = parser or FinancialFileParser()
        self._validator = validator or DatasetValidator()
        self._quality = quality_assessor or DatasetQualityAssessor()

    def run(
        self,
        file_path: str,
        file_name: str,
        *,
        timeline: PipelineTimeline | None = None,
    ) -> IngestionResult:
        try:
            if timeline is not None:
                with timeline.track(PipelineStage.PARSING):
                    dataset, parse_metadata = self._parser.parse_file(
                        file_path, file_name
                    )
            else:
                dataset, parse_metadata = self._parser.parse_file(file_path, file_name)
        except ParseError:
            raise
        except Exception as exc:
            raise ParseError(str(exc), file_name=file_name) from exc

        if timeline is not None:
            with timeline.track(PipelineStage.VALIDATION):
                validation = self._validator.validate(dataset)
                if not validation.is_valid:
                    raise ValidationFailure(validation.error_message)
                validate_waste_template(dataset)
        else:
            validation = self._validator.validate(dataset)
            if not validation.is_valid:
                raise ValidationFailure(validation.error_message)
            validate_waste_template(dataset)

        quality = self._quality.assess(dataset)
        return IngestionResult(
            record_count=dataset.record_count,
            parse_metadata=parse_metadata,
            dataset=dataset,
            validation=validation,
            quality=quality,
        )
