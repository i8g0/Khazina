"""Unit tests for ingestion parser."""

from __future__ import annotations

import pandas as pd
import pytest

from app.ingestion.constants import PARSER_VERSION, SCHEMA_VERSION
from app.ingestion.exceptions import ParseError
from app.ingestion.parser import FinancialFileParser


def test_parse_csv_bytes_success() -> None:
    content = b"category,amount,date\nProcurement,1000,2026-06-01\n"
    dataset, metadata = FinancialFileParser.parse_csv_bytes(content, "test.csv")
    assert dataset.record_count == 1
    assert dataset.sheets[0].columns == ("category", "amount", "date")
    assert metadata.parser_version == PARSER_VERSION
    assert metadata.schema_version == SCHEMA_VERSION


def test_parse_excel_file_success(tmp_path) -> None:
    path = tmp_path / "budget.xlsx"
    frame = pd.DataFrame(
        {
            "category": ["Travel"],
            "amount": ["500"],
            "date": ["2026-06-15"],
        }
    )
    frame.to_excel(path, index=False)
    parser = FinancialFileParser()
    dataset, metadata = parser.parse_file(str(path), "budget.xlsx")
    assert dataset.record_count == 1
    assert metadata.sheet_names == ["Sheet1"]


def test_parse_empty_sheet_raises() -> None:
    content = b"category,amount\n"
    with pytest.raises(ParseError):
        FinancialFileParser.parse_csv_bytes(content, "empty.csv")


def test_parse_unsupported_extension(tmp_path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")
    parser = FinancialFileParser()
    with pytest.raises(ParseError):
        parser.parse_file(str(path), "notes.txt")
