"""Business Engine layer — deterministic analysis (Sprint 5.3A architecture freeze).

See docs/BUSINESS_ENGINE_ARCHITECTURE.md for the normative specification.
No engine implementations exist until Sprint 5.3B.
"""

from app.business.base import BusinessEngine
from app.business.exceptions import (
    BusinessRuleViolationError,
    CalculationError,
    DetectionError,
    EngineError,
    InvalidInputError,
    MissingDataError,
    RegistryFrozenError,
    ValidationError,
)
from app.business.manifest import EngineManifest
from app.business.registry import (
    freeze_registry,
    get_engine,
    get_engine_manifest,
    is_registry_frozen,
    register_engine,
    registered_engine_ids,
    registered_manifests,
)

__all__ = [
    "BusinessEngine",
    "BusinessRuleViolationError",
    "CalculationError",
    "DetectionError",
    "EngineError",
    "EngineManifest",
    "InvalidInputError",
    "MissingDataError",
    "RegistryFrozenError",
    "ValidationError",
    "freeze_registry",
    "get_engine",
    "get_engine_manifest",
    "is_registry_frozen",
    "register_engine",
    "registered_engine_ids",
    "registered_manifests",
]
