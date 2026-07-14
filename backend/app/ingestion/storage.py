"""Bronze-layer file persistence."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.ingestion.constants import SUPPORTED_EXTENSIONS
from app.ingestion.exceptions import IngestionError


class BronzeStorage:
    """Stores original uploaded file bytes as the source of truth."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        organization_id: uuid.UUID,
        file_name: str,
        content: bytes,
    ) -> tuple[str, int]:
        if not content:
            raise IngestionError("Uploaded file is empty")
        extension = Path(file_name).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise IngestionError(
                f"Unsupported file extension '{extension}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        org_dir = self._root / str(organization_id)
        org_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid.uuid4()}{extension}"
        destination = org_dir / stored_name
        destination.write_bytes(content)
        return str(destination), len(content)

    def read(self, storage_path: str) -> bytes:
        path = Path(storage_path)
        if not path.is_file():
            raise IngestionError(f"Bronze file not found at '{storage_path}'")
        return path.read_bytes()

    @staticmethod
    def format_size_display(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"
