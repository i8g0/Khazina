"""Immutable Business Engine registry (Sprint 5.3A architecture standard).

Registry lifecycle:
    Initialization → Registration → Freeze → Read Only
"""

from __future__ import annotations

from app.business.base import BusinessEngine
from app.business.exceptions import EngineError, RegistryFrozenError
from app.business.manifest import EngineManifest

_REGISTRY: dict[str, BusinessEngine] = {}
_FROZEN: bool = False


def register_engine(engine: BusinessEngine) -> None:
    """Register a concrete engine during initialization only."""
    if _FROZEN:
        raise RegistryFrozenError(
            "Engine registry is frozen; registration is not allowed after startup"
        )
    manifest = engine.manifest
    if manifest.engine_id in _REGISTRY:
        raise EngineError(f"Engine already registered: {manifest.engine_id}")
    _REGISTRY[manifest.engine_id] = engine


def freeze_registry() -> None:
    """Freeze the registry after all engines are registered. Idempotent."""
    global _FROZEN
    _FROZEN = True


def is_registry_frozen() -> bool:
    """Return whether the registry has been frozen."""
    return _FROZEN


def get_engine(engine_id: str) -> BusinessEngine:
    """Return a registered engine by manifest ``engine_id`` (read-only)."""
    try:
        return _REGISTRY[engine_id]
    except KeyError as exc:
        raise KeyError(f"No Business Engine registered for: {engine_id}") from exc


def get_engine_manifest(engine_id: str) -> EngineManifest:
    """Return manifest for a registered engine (Registry consumes Manifest)."""
    return get_engine(engine_id).manifest


def registered_engine_ids() -> tuple[str, ...]:
    """Return all registered engine identifiers from manifests."""
    return tuple(sorted(_REGISTRY.keys()))


def registered_manifests() -> tuple[EngineManifest, ...]:
    """Return all registered engine manifests."""
    return tuple(_REGISTRY[eid].manifest for eid in registered_engine_ids())
