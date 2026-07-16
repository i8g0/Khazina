"""Parallel AI task execution tests."""

from __future__ import annotations

import threading
import time

from app.ai.prompts.tasks import PromptTask
from app.ai_recommendations.constants import TASK_EXECUTION_ORDER
from app.ai_recommendations.pipeline import AiTaskPipeline
from app.ai_recommendations.risk_constants import RISK_TASK_EXECUTION_ORDER
from tests.ai_recommendations.conftest import MockOllamaByTask, sample_facts_contract


class _SlowParallelMock:
    """Simulates concurrent-safe LLM with per-call delay."""

    def __init__(self, delay_s: float = 0.05) -> None:
        self.delay_s = delay_s
        self.concurrent = 0
        self.max_concurrent = 0
        self._lock = threading.Lock()

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str:
        with self._lock:
            self.concurrent += 1
            self.max_concurrent = max(self.max_concurrent, self.concurrent)
        try:
            time.sleep(self.delay_s)
            return "استجابة تجريبية للاختبار."
        finally:
            with self._lock:
                self.concurrent -= 1


def test_execute_tasks_parallel_runs_faster_than_sequential() -> None:
    mock = _SlowParallelMock(delay_s=0.08)
    pipeline = AiTaskPipeline(llm_client=mock, llm_model="test")

    t0 = time.perf_counter()
    pipeline.execute_tasks(
        sample_facts_contract(),
        TASK_EXECUTION_ORDER,
        parallel=False,
    )
    sequential_ms = (time.perf_counter() - t0) * 1000

    mock2 = _SlowParallelMock(delay_s=0.08)
    pipeline2 = AiTaskPipeline(llm_client=mock2, llm_model="test")
    t1 = time.perf_counter()
    results = pipeline2.execute_tasks(
        sample_facts_contract(),
        TASK_EXECUTION_ORDER,
        parallel=True,
    )
    parallel_ms = (time.perf_counter() - t1) * 1000

    assert len(results) == len(TASK_EXECUTION_ORDER)
    assert mock2.max_concurrent > 1
    assert parallel_ms < sequential_ms * 0.75


def test_execute_tasks_parallel_preserves_task_order() -> None:
    mock = _SlowParallelMock(delay_s=0.01)
    pipeline = AiTaskPipeline(llm_client=mock, llm_model="test")
    tasks = RISK_TASK_EXECUTION_ORDER[:3]
    results = pipeline.execute_tasks(
        sample_facts_contract(),
        tasks,
        domain="risk",
        parallel=True,
    )
    assert [r.task for r in results] == list(tasks)
