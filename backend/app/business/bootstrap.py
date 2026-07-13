"""Business Engine registry initialization."""

from __future__ import annotations

from app.business.engines.waste import WasteEngine
from app.business.registry import freeze_registry, is_registry_frozen, register_engine


def initialize_business_engines() -> None:
    """Register all Business Engines and freeze the registry at startup."""
    if is_registry_frozen():
        return
    register_engine(WasteEngine())
    freeze_registry()
