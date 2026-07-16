"""Decision Engine — Silver-to-Gold deterministic execution (Sprint 6.3)."""

from app.decision.exceptions import SnapshotAdapterError

__all__ = [
    "DecisionExecutionOutcome",
    "DecisionService",
    "SnapshotAdapterError",
]


def __getattr__(name: str):
    """Lazy exports to avoid import cycles with observability (Sprint 8.1)."""
    if name in {"DecisionExecutionOutcome", "DecisionService"}:
        from app.decision.service import DecisionExecutionOutcome, DecisionService

        return DecisionExecutionOutcome if name == "DecisionExecutionOutcome" else DecisionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
