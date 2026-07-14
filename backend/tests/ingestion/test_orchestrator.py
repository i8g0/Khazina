"""Unit tests for ingestion orchestrator."""

from __future__ import annotations

import pandas as pd
import pytest

from app.ingestion.exceptions import ParseError, ValidationFailure
from app.ingestion.orchestrator import IngestionOrchestrator


def test_orchestrator_success_path(tmp_path) -> None:
    path = tmp_path / "procurement.xlsx"
    pd.DataFrame(
        {
            "category": ["Travel"],
            "amount": ["1500"],
            "date": ["2026-06-28"],
            "budget": ["2000"],
            "actual": ["1500"],
        }
    ).to_excel(path, index=False)
    result = IngestionOrchestrator().run(str(path), "procurement.xlsx")
    assert result.record_count == 1
    assert result.quality.overall_score > 0


def test_orchestrator_validation_failure(tmp_path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("category,amount\nTravel,not-a-number\n", encoding="utf-8")
    with pytest.raises(ValidationFailure):
        IngestionOrchestrator().run(str(path), "bad.csv")


def test_orchestrator_parse_failure(tmp_path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("category,amount\n", encoding="utf-8")
    with pytest.raises(ParseError):
        IngestionOrchestrator().run(str(path), "empty.csv")
