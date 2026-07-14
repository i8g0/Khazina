"""Progress logging for long-running benchmark executions."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass


@dataclass
class ProgressLogger:
    total_steps: int
    completed_steps: int = 0
    _step_start: float = 0.0

    def begin(self, label: str) -> None:
        self.completed_steps += 1
        self._step_start = time.perf_counter()
        print(
            f"[{self.completed_steps}/{self.total_steps}] {label}...",
            flush=True,
            file=sys.stdout,
        )

    def complete(self, *, extra: str | None = None) -> None:
        elapsed_ms = round((time.perf_counter() - self._step_start) * 1000, 2)
        remaining = max(self.total_steps - self.completed_steps, 0)
        suffix = f" — {extra}" if extra else ""
        print(
            f"    Completed{suffix}\n"
            f"    Elapsed: {elapsed_ms} ms\n"
            f"    Remaining steps: {remaining}",
            flush=True,
            file=sys.stdout,
        )

    def fail(self, error: str) -> None:
        elapsed_ms = round((time.perf_counter() - self._step_start) * 1000, 2)
        print(
            f"    FAILED after {elapsed_ms} ms\n"
            f"    Error: {error}",
            flush=True,
            file=sys.stderr,
        )

    def info(self, message: str) -> None:
        print(f"    {message}", flush=True, file=sys.stdout)
