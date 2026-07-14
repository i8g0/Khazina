"""Deterministic Excel/CSV parser — no calculations, no LLM."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

from app.ingestion.constants import PARSER_VERSION, SCHEMA_VERSION
from app.ingestion.exceptions import ParseError
from app.ingestion.types import ParseMetadata, ParsedDataset, ParsedRow, ParsedSheet


class FinancialFileParser:
    """Maps external spreadsheet formats to internal structures (schema v1)."""

    def parse_file(self, file_path: str, file_name: str) -> tuple[ParsedDataset, ParseMetadata]:
        path = Path(file_path)
        extension = path.suffix.lower()
        if extension == ".csv":
            return self._parse_csv(path, file_name)
        if extension in {".xlsx", ".xls"}:
            return self._parse_excel(path, file_name)
        raise ParseError(
            f"Unsupported extension '{extension}'",
            file_name=file_name,
        )

    def _parse_csv(self, path: Path, file_name: str) -> tuple[ParsedDataset, ParseMetadata]:
        try:
            frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        except Exception as exc:
            raise ParseError(str(exc), file_name=file_name) from exc
        sheet = self._frame_to_sheet("Sheet1", frame, file_name)
        dataset = ParsedDataset(source_file_name=file_name, sheets=(sheet,))
        metadata = self._build_metadata(dataset)
        return dataset, metadata

    def _parse_excel(self, path: Path, file_name: str) -> tuple[ParsedDataset, ParseMetadata]:
        try:
            workbook = pd.read_excel(
                path,
                sheet_name=None,
                dtype=str,
                keep_default_na=False,
            )
        except Exception as exc:
            raise ParseError(str(exc), file_name=file_name) from exc
        if not workbook:
            raise ParseError("Workbook contains no sheets", file_name=file_name)
        sheets: list[ParsedSheet] = []
        for sheet_name, frame in workbook.items():
            sheets.append(self._frame_to_sheet(str(sheet_name), frame, file_name))
        dataset = ParsedDataset(source_file_name=file_name, sheets=tuple(sheets))
        metadata = self._build_metadata(dataset)
        return dataset, metadata

    def _frame_to_sheet(
        self,
        sheet_name: str,
        frame: pd.DataFrame,
        file_name: str,
    ) -> ParsedSheet:
        if frame.empty:
            raise ParseError(
                "Sheet is empty",
                file_name=file_name,
                sheet_name=sheet_name,
            )
        columns = tuple(str(column).strip() for column in frame.columns)
        if not any(columns):
            raise ParseError(
                "Sheet has no column headers",
                file_name=file_name,
                sheet_name=sheet_name,
            )
        rows: list[ParsedRow] = []
        for index, row in frame.iterrows():
            row_number = int(index) + 2
            values = {
                columns[col_index]: self._normalize_cell(row.iloc[col_index])
                for col_index in range(len(columns))
            }
            rows.append(ParsedRow(row_number=row_number, values=values))
        return ParsedSheet(name=sheet_name, columns=columns, rows=tuple(rows))

    @staticmethod
    def _normalize_cell(value: object) -> str | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _build_metadata(dataset: ParsedDataset) -> ParseMetadata:
        column_mappings = {
            sheet.name: list(sheet.columns) for sheet in dataset.sheets
        }
        row_counts = {sheet.name: len(sheet.rows) for sheet in dataset.sheets}
        return ParseMetadata(
            column_mappings=column_mappings,
            sheet_names=[sheet.name for sheet in dataset.sheets],
            row_counts=row_counts,
            parser_version=PARSER_VERSION,
            schema_version=SCHEMA_VERSION,
        )

    @staticmethod
    def parse_csv_bytes(content: bytes, file_name: str) -> tuple[ParsedDataset, ParseMetadata]:
        """Helper for tests — parse in-memory CSV."""
        try:
            frame = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
        except Exception as exc:
            raise ParseError(str(exc), file_name=file_name) from exc
        parser = FinancialFileParser()
        sheet = parser._frame_to_sheet("Sheet1", frame, file_name)
        dataset = ParsedDataset(source_file_name=file_name, sheets=(sheet,))
        return dataset, parser._build_metadata(dataset)
