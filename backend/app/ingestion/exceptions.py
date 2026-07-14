"""Ingestion-layer exceptions — separate from service and AI parsers."""


class IngestionError(Exception):
    """Base error for the ingestion pipeline."""


class ParseError(IngestionError):
    """Raised when a file cannot be parsed."""

    def __init__(
        self,
        message: str,
        *,
        file_name: str | None = None,
        sheet_name: str | None = None,
        row_number: int | None = None,
    ) -> None:
        location_parts = [part for part in (file_name, sheet_name, row_number) if part]
        if location_parts:
            location = " / ".join(str(part) for part in location_parts)
            message = f"{location}: {message}"
        super().__init__(message)
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.row_number = row_number


class ValidationFailure(IngestionError):
    """Raised when parsed data fails validation gates."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
