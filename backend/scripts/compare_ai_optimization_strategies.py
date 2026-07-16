"""Compare sequential vs parallel vs batched AI strategies (evidence collection)."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.ai.prompts.composer import PromptComposer
from app.ai.prompts.tasks import PromptTask
from app.ai.providers.factory import create_ai_provider
from app.ai.telemetry import clear_ai_request_records, get_ai_request_records, verify_all_cloud_requests
from app.ai_recommendations.constants import TASK_EXECUTION_ORDER
from app.ai_recommendations.pipeline import AiTaskPipeline
from app.ai_recommendations.risk_constants import RISK_TASK_EXECUTION_ORDER
from app.ai_recommendations.risk_metadata import build_risk_metadata_supplement
from app.core.config import settings
from tests.ai_recommendations.conftest import sample_facts_contract
from tests.ai_recommendations.risk_conftest import (
    sample_risk_facts_contract,
    sample_risk_runtime_metadata,
)


@dataclass
class StrategyResult:
    strategy: str
    domain: str
    wall_ms: float
    task_count: int
    total_prompt_tokens: int
    total_completion_tokens: int
    provider_records: int


def _run_pipeline(
    *,
    domain: str,
    tasks: tuple[PromptTask, ...],
    parallel: bool,
    strategy: str,
) -> StrategyResult:
    clear_ai_request_records()
    provider = create_ai_provider(settings.ai)
    pipeline = AiTaskPipeline(
        llm_client=provider,
        llm_model=settings.ai.active_model,
        prompt_language=settings.ai.default_prompt_language,
    )
    facts = sample_risk_facts_contract() if domain == "risk" else sample_facts_contract()
    supplement = (
        build_risk_metadata_supplement(sample_risk_runtime_metadata())
        if domain == "risk"
        else None
    )

    started = time.perf_counter()
    pipeline.execute_tasks(
        facts,
        tasks,
        domain=domain,
        prompt_supplement=supplement,
        parallel=parallel,
    )
    wall_ms = (time.perf_counter() - started) * 1000
    records = get_ai_request_records()
    ok, message = verify_all_cloud_requests(expected_model=settings.ai.active_model)
    if not ok:
        raise RuntimeError(f"Provider verification failed: {message}")

    return StrategyResult(
        strategy=strategy,
        domain=domain,
        wall_ms=round(wall_ms, 2),
        task_count=len(tasks),
        total_prompt_tokens=sum(r.prompt_tokens or 0 for r in records),
        total_completion_tokens=sum(r.completion_tokens or 0 for r in records),
        provider_records=len(records),
    )


def _run_batched_single_request(domain: str) -> StrategyResult:
    """Option B prototype — one combined prompt (not used in production)."""
    clear_ai_request_records()
    provider = create_ai_provider(settings.ai)
    facts = sample_risk_facts_contract() if domain == "risk" else sample_facts_contract()
    composer = PromptComposer()
    tasks = RISK_TASK_EXECUTION_ORDER if domain == "risk" else TASK_EXECUTION_ORDER

    sections = []
    for task in tasks:
        composed = composer.compose(task, {}, prompt_language=settings.ai.default_prompt_language)
        sections.append(f"### {task.value}\n{composed.user_prompt[:500]}")

    messages = [
        {
            "role": "system",
            "content": (
                "Return one JSON object with keys for each section. "
                "Use Arabic. Keys: "
                + ", ".join(t.value for t in tasks)
            ),
        },
        {
            "role": "user",
            "content": "Generate all sections from these facts:\n" + "\n".join(sections),
        },
    ]

    started = time.perf_counter()
    provider.chat(messages, format_json=True)
    wall_ms = (time.perf_counter() - started) * 1000
    records = get_ai_request_records()
    ok, message = verify_all_cloud_requests(expected_model=settings.ai.active_model)
    if not ok:
        raise RuntimeError(message)

    return StrategyResult(
        strategy="batched_single_json",
        domain=domain,
        wall_ms=round(wall_ms, 2),
        task_count=1,
        total_prompt_tokens=sum(r.prompt_tokens or 0 for r in records),
        total_completion_tokens=sum(r.completion_tokens or 0 for r in records),
        provider_records=len(records),
    )


def main() -> None:
    print(f"Model={settings.ai.active_model} provider={settings.ai.ai_provider}")
    results: list[StrategyResult] = []

    for domain, tasks in (
        ("risk", RISK_TASK_EXECUTION_ORDER),
        ("waste", TASK_EXECUTION_ORDER),
    ):
        print(f"\nBenchmarking {domain}...")
        results.append(
            _run_pipeline(domain=domain, tasks=tasks, parallel=False, strategy="sequential")
        )
        results.append(
            _run_pipeline(domain=domain, tasks=tasks, parallel=True, strategy="parallel")
        )
        results.append(_run_batched_single_request(domain))

    out = Path(__file__).with_name("_optimization_benchmark.json")
    out.write_text(
        json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote {out}")
    for item in results:
        print(
            f"{item.domain:5} {item.strategy:22} wall={item.wall_ms:8.1f}ms "
            f"tokens={item.total_prompt_tokens}+{item.total_completion_tokens} "
            f"requests={item.provider_records}"
        )


if __name__ == "__main__":
    main()
