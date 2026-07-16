"""Production AI execution trace — stage timestamps for real-request debugging."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock

from app.core.logging import get_logger

logger = get_logger(__name__)

_lock = Lock()
_traces: list[ExecutionTrace] = []


@dataclass
class StageMark:
    stage: str
    elapsed_ms: float
    detail: str | None = None


@dataclass
class ExecutionTrace:
    trace_id: str
    domain: str
    started_at: float
    stages: list[StageMark] = field(default_factory=list)

    def mark(self, stage: str, *, detail: str | None = None) -> None:
        elapsed_ms = round((time.perf_counter() - self.started_at) * 1000, 2)
        self.stages.append(StageMark(stage=stage, elapsed_ms=elapsed_ms, detail=detail))
        logger.info(
            "AI execution trace [%s] %s @ %.2fms%s",
            self.trace_id,
            stage,
            elapsed_ms,
            f" ({detail})" if detail else "",
        )


def begin_trace(trace_id: str, domain: str) -> ExecutionTrace:
    trace = ExecutionTrace(
        trace_id=trace_id,
        domain=domain,
        started_at=time.perf_counter(),
    )
    with _lock:
        _traces.append(trace)
    trace.mark("trace_started", detail=domain)
    return trace


def get_traces() -> tuple[ExecutionTrace, ...]:
    with _lock:
        return tuple(_traces)


def clear_traces() -> None:
    with _lock:
        _traces.clear()
