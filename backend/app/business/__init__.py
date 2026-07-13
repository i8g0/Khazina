"""Business Engine layer — deterministic analysis (Sprint 5.3A architecture freeze).

See docs/BUSINESS_ENGINE_ARCHITECTURE.md for the normative specification.
"""

from app.business.base import BusinessEngine
from app.business.bootstrap import initialize_business_engines
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
from app.business.facts import CONTRACT_VERSION, Fact, FactsContract
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
    "CONTRACT_VERSION",
    "BusinessEngine",
    "BusinessRuleViolationError",
    "CalculationError",
    "DetectionError",
    "EngineError",
    "EngineManifest",
    "Fact",
    "FactsContract",
    "InvalidInputError",
    "MissingDataError",
    "RegistryFrozenError",
    "ValidationError",
    "freeze_registry",
    "get_engine",
    "get_engine_manifest",
    "initialize_business_engines",
    "is_registry_frozen",
    "register_engine",
    "registered_engine_ids",
    "registered_manifests",
]
