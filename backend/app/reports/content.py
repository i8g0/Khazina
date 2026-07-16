"""Report Content Representation model and deterministic serialization."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.reports.constants import BUILDER_VERSION, REPORT_DOCUMENT_VERSION


@dataclass(frozen=True, slots=True)
class ReportSection:
    key: str
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ExtendedMetadata:
    builder_version: str
    input_fingerprint: str
    sections_included: tuple[str, ...]
    ai_insights_consumed: bool
    ai_insights_generated_at: str | None
    baseline_run_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "builder_version": self.builder_version,
            "input_fingerprint": self.input_fingerprint,
            "sections_included": list(self.sections_included),
            "ai_insights_consumed": self.ai_insights_consumed,
            "ai_insights_generated_at": self.ai_insights_generated_at,
            "baseline_run_id": self.baseline_run_id,
        }


@dataclass(frozen=True, slots=True)
class ReportContentRepresentation:
    """Immutable point-in-time executive report document."""

    report_document_version: str
    profile: str
    generated_at: datetime
    source_analysis_run_id: uuid.UUID
    organization_id: uuid.UUID
    report_id: uuid.UUID | None
    sections: tuple[ReportSection, ...]
    extended_metadata: ExtendedMetadata

    def with_report_id(self, report_id: uuid.UUID) -> ReportContentRepresentation:
        return ReportContentRepresentation(
            report_document_version=self.report_document_version,
            profile=self.profile,
            generated_at=self.generated_at,
            source_analysis_run_id=self.source_analysis_run_id,
            organization_id=self.organization_id,
            report_id=report_id,
            sections=self.sections,
            extended_metadata=self.extended_metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_document_version": self.report_document_version,
            "profile": self.profile,
            "generated_at": self.generated_at.isoformat(),
            "source_analysis_run_id": str(self.source_analysis_run_id),
            "organization_id": str(self.organization_id),
            "report_id": str(self.report_id) if self.report_id else None,
            "sections": [
                {"key": section.key, "payload": section.payload}
                for section in self.sections
            ],
            "extended_metadata": self.extended_metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ReportContentRepresentation:
        sections = tuple(
            ReportSection(key=str(item["key"]), payload=dict(item["payload"]))
            for item in payload["sections"]
        )
        meta = payload["extended_metadata"]
        return cls(
            report_document_version=str(payload["report_document_version"]),
            profile=str(payload["profile"]),
            generated_at=datetime.fromisoformat(str(payload["generated_at"])),
            source_analysis_run_id=uuid.UUID(str(payload["source_analysis_run_id"])),
            organization_id=uuid.UUID(str(payload["organization_id"])),
            report_id=(
                uuid.UUID(str(payload["report_id"]))
                if payload.get("report_id")
                else None
            ),
            sections=sections,
            extended_metadata=ExtendedMetadata(
                builder_version=str(meta["builder_version"]),
                input_fingerprint=str(meta["input_fingerprint"]),
                sections_included=tuple(str(k) for k in meta["sections_included"]),
                ai_insights_consumed=bool(meta["ai_insights_consumed"]),
                ai_insights_generated_at=meta.get("ai_insights_generated_at"),
                baseline_run_id=meta.get("baseline_run_id"),
            ),
        )

    def executive_summary_text(self) -> str:
        for section in self.sections:
            if section.key == "executive_summary":
                text = section.payload.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
        return "الملخص التنفيذي غير متوفر — أكمل التحليل المالي ثم أعد إعداد التقرير."


def canonical_serialize(content: ReportContentRepresentation | dict[str, Any]) -> str:
    payload = content.to_dict() if isinstance(content, ReportContentRepresentation) else content
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def content_fingerprint(content: ReportContentRepresentation | dict[str, Any] | str) -> str:
    if isinstance(content, str):
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    serialized = canonical_serialize(content)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_extended_metadata(
    *,
    input_fingerprint: str,
    sections_included: tuple[str, ...],
    ai_insights_consumed: bool,
    ai_insights_generated_at: str | None,
    baseline_run_id: str | None,
) -> ExtendedMetadata:
    return ExtendedMetadata(
        builder_version=BUILDER_VERSION,
        input_fingerprint=input_fingerprint,
        sections_included=sections_included,
        ai_insights_consumed=ai_insights_consumed,
        ai_insights_generated_at=ai_insights_generated_at,
        baseline_run_id=baseline_run_id,
    )


def default_document_version() -> str:
    return REPORT_DOCUMENT_VERSION
