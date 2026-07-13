"""Facts Contract — immutable, versioned handoff between Business Engines and AI layer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

CONTRACT_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class Fact:
    """Single deterministic analytical output. No narrative fields."""

    domain: str
    metric: str
    value: str
    source: str
    unit: str | None = None
    severity: str | None = None
    confidence: str | None = None
    organization_id: str | None = None
    period: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    fact_schema_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "domain": self.domain,
            "metric": self.metric,
            "value": self.value,
            "source": self.source,
        }
        if self.unit is not None:
            payload["unit"] = self.unit
        if self.severity is not None:
            payload["severity"] = self.severity
        if self.confidence is not None:
            payload["confidence"] = self.confidence
        if self.organization_id is not None:
            payload["organization_id"] = self.organization_id
        if self.period is not None:
            payload["period"] = self.period
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        if self.fact_schema_version is not None:
            payload["fact_schema_version"] = self.fact_schema_version
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Fact:
        return cls(
            domain=str(data["domain"]),
            metric=str(data["metric"]),
            value=str(data["value"]),
            source=str(data["source"]),
            unit=data.get("unit"),
            severity=data.get("severity"),
            confidence=data.get("confidence"),
            organization_id=data.get("organization_id"),
            period=data.get("period"),
            metadata=dict(data.get("metadata") or {}),
            fact_schema_version=data.get("fact_schema_version"),
        )


@dataclass(frozen=True, slots=True)
class FactsContract:
    """Immutable versioned collection of facts produced by a Business Engine."""

    contract_version: str
    engine_id: str
    engine_version: str
    generated_at: datetime
    facts: tuple[Fact, ...]
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "generated_at": self.generated_at.astimezone(UTC).isoformat(),
            "facts": [fact.to_dict() for fact in self.facts],
        }
        if self.extensions:
            payload["extensions"] = dict(self.extensions)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FactsContract:
        generated_at = data["generated_at"]
        if isinstance(generated_at, str):
            generated_at = datetime.fromisoformat(generated_at)
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=UTC)
        return cls(
            contract_version=str(data["contract_version"]),
            engine_id=str(data["engine_id"]),
            engine_version=str(data["engine_version"]),
            generated_at=generated_at,
            facts=tuple(Fact.from_dict(item) for item in data["facts"]),
            extensions=dict(data.get("extensions") or {}),
        )
