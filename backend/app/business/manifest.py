"""Business Engine manifest — single source of truth for engine identity (Sprint 5.3A)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EngineManifest:
    """Static engine metadata. Descriptive only — no runtime state or calculations.

    Required fields (architecture standard):
    - ``engine_id`` (ENGINE_ID)
    - ``engine_name`` (ENGINE_NAME)
    - ``engine_version`` (ENGINE_VERSION)
    - ``engine_description`` (ENGINE_DESCRIPTION)
    - ``supported_facts`` (SUPPORTED_FACTS)
    """

    engine_id: str
    engine_name: str
    engine_version: str
    engine_description: str
    supported_facts: tuple[str, ...]
    extensions: dict[str, Any] = field(default_factory=dict)
