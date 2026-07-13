"""Abstract Business Engine interface (Sprint 5.3A — architecture only)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.business.manifest import EngineManifest


class BusinessEngine(ABC):
    """Common interface every Business Engine must implement (Sprint 5.3B+)."""

    @property
    @abstractmethod
    def manifest(self) -> EngineManifest:
        """Static engine identity — single source of truth consumed by the Registry."""

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """Execute the full engine lifecycle and return a Facts Contract."""

    def analyze(self, input_data: Any) -> Any:
        """Optional orchestration entry point; defaults to ``run()``."""
        return self.run(input_data)

    @abstractmethod
    def assemble_facts(self, calculation_result: Any, detection_result: Any) -> Any:
        """Assemble Facts Contract from calculator and detector outputs via Fact Assembler."""
