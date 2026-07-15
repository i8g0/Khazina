"""Report PDF export file persistence."""

from __future__ import annotations

import uuid
from pathlib import Path


class ReportExportStorage:
    """Stores generated PDF bytes for report exports."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        organization_id: uuid.UUID,
        report_id: uuid.UUID,
        export_fingerprint: str,
        content: bytes,
    ) -> str:
        org_dir = self._root / str(organization_id) / str(report_id)
        org_dir.mkdir(parents=True, exist_ok=True)
        destination = org_dir / f"{export_fingerprint}.pdf"
        destination.write_bytes(content)
        return str(destination)

    def read(self, storage_reference: str) -> bytes:
        path = Path(storage_reference)
        if not path.is_file():
            raise FileNotFoundError(f"Export file not found at '{storage_reference}'")
        return path.read_bytes()
