"""Business Engine exception hierarchy (Sprint 5.3A)."""

from __future__ import annotations


class EngineError(Exception):
    """Base class for all Business Engine errors."""


class InvalidInputError(EngineError):
    """Input fails structural or precondition validation."""


class MissingDataError(EngineError):
    """Required data is absent for calculation or detection."""


class ValidationError(EngineError):
    """Business validation rule failed on input."""


class CalculationError(EngineError):
    """Deterministic calculation failed."""


class DetectionError(EngineError):
    """Detector rule execution failed."""


class BusinessRuleViolationError(EngineError):
    """A deterministic domain business rule was violated."""


class RegistryFrozenError(EngineError):
    """Attempted to modify the engine registry after initialization freeze."""
