#!/usr/bin/env python
"""Measure Cloud AI latency per pipeline stage and per task (evidence only, no optimization).

Usage (from backend/):
    python scripts/measure_cloud_ai_performance.py --domain risk
    python scripts/measure_cloud_ai_performance.py --domain waste
    python scripts/measure_cloud_ai_performance.py --domain both --output /tmp/perf.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.parsers.response_parser import ResponseParser
from app.ai.prompts.composer import PromptComposer
from app.ai.prompts.tasks import PromptTask
from app.ai.providers.factory import create_ai_provider
from app.ai_recommendations.constants import TASK_EXECUTION_ORDER
from app.ai_recommendations.risk_constants import RISK_TASK_EXECUTION_ORDER
from app.ai_recommendations.risk_metadata import build_risk_metadata_supplement
from app.core.config import settings

# Reuse deterministic test fixtures (same shape as production facts contracts).
from tests.ai_recommendations.conftest import sample_facts_contract
from tests.ai_recommendations.risk_conftest import sample_risk_facts_contract, sample_risk_runtime_metadata


TASK_LABELS: dict[PromptTask, str] = {
    PromptTask.EXECUTIVE_SUMMARY: "Executive Summary",
    PromptTask.RECOMMENDATIONS: "Recommendations",
    PromptTask.RISK_ANALYSIS: "Risk Analysis",
    PromptTask.RISK_EXECUTIVE_SUMMARY: "Executive Summary",
    PromptTask.RISK_EXECUTIVE_BRIEF: "Executive Brief",
    PromptTask.RISK_EXPLANATION: "Explanation",
    PromptTask.RISK_MITIGATION_OPTIONS: "Mitigation",
    PromptTask.RISK_BOARD_REPORT: "Board Report",
}


@dataclass
class StageTiming:
    stage: str
    started_at_ms: float
    duration_ms: float


@dataclass
class TaskMeasurement:
    task: str
    label: str
    context_build_ms: float
    prompt_compose_ms: float
    serialization_ms: float
    api_latency_ms: float
    parsing_ms: float
    total_task_ms: float
    prompt_chars: int
    system_prompt_chars: int
    user_prompt_chars: int
    payload_bytes: int
    response_chars: int
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None


@dataclass
class DomainMeasurement:
    domain: str
    task_count: int
    execution_mode: str
    request_started_at: str
    request_total_ms: float
    pre_llm_ms: float
    openai_wait_ms: float
    post_llm_ms: float
    openai_wait_pct: float
    local_processing_pct: float
    tasks: list[TaskMeasurement] = field(default_factory=list)
    post_processing_ms: float = 0.0


class InstrumentedCloudChat:
    """Wraps cloud provider chat() to capture API latency and token usage."""

    def __init__(self, provider: Any) -> None:
        self._provider = provider
        self.last_api_latency_ms: float = 0.0
        self.last_prompt_tokens: int | None = None
        self.last_completion_tokens: int | None = None
        self.last_total_tokens: int | None = None

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        format_json: bool = False,
    ) -> str:
        payload: dict[str, object] = {
            "model": model or self._provider.configured_model,
            "messages": messages,
            "temperature": settings.ai.ai_temperature,
            "stream": False,
        }
        if format_json:
            payload["response_format"] = {"type": "json_object"}

        url = self._provider._chat_url()
        headers = self._provider._headers()
        client = self._provider._client()

        started = time.perf_counter()
        response = client.post(url, json=payload, headers=headers)
        self.last_api_latency_ms = (time.perf_counter() - started) * 1000
        response.raise_for_status()
        body = response.json()

        usage = body.get("usage") if isinstance(body, dict) else None
        if isinstance(usage, dict):
            self.last_prompt_tokens = _as_int(usage.get("prompt_tokens"))
            self.last_completion_tokens = _as_int(usage.get("completion_tokens"))
            self.last_total_tokens = _as_int(usage.get("total_tokens"))
        else:
            self.last_prompt_tokens = None
            self.last_completion_tokens = None
            self.last_total_tokens = None

        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("Cloud response missing choices")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if not isinstance(message, dict):
            raise RuntimeError("Cloud response missing message")
        content = message.get("content")
        if not isinstance(content, str):
            raise RuntimeError("Cloud response missing content")
        return content


def _as_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _measure_task(
    *,
    facts: Any,
    task: PromptTask,
    domain: str,
    chat: InstrumentedCloudChat,
    model: str,
    prompt_language: str,
    prompt_supplement: str | None,
    context_builder: ContextBuilder,
    prompt_composer: PromptComposer,
    response_parser: ResponseParser,
) -> TaskMeasurement:
    task_started = time.perf_counter()

    t0 = time.perf_counter()
    prompt_context = context_builder.build(
        facts,
        ContextBuildOptions(task=task, domain=domain),
    )
    context_build_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    composed = prompt_composer.compose(
        task,
        prompt_context.facts,
        prompt_language=prompt_language,
    )
    prompt_compose_ms = (time.perf_counter() - t1) * 1000

    user_content = (
        f"{composed.user_prompt.rstrip()}\n\n{prompt_supplement.rstrip()}\n"
        if prompt_supplement
        else composed.user_prompt
    )
    messages = [
        {"role": "system", "content": composed.system_prompt},
        {"role": "user", "content": user_content},
    ]

    t2 = time.perf_counter()
    payload = {
        "model": model,
        "messages": messages,
        "temperature": settings.ai.ai_temperature,
        "stream": False,
    }
    payload_bytes = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    serialization_ms = (time.perf_counter() - t2) * 1000

    # HTTP request sent → OpenAI response received
    llm_response = chat.chat(messages, model=model)

    t3 = time.perf_counter()
    response_parser.parse(llm_response)
    parsing_ms = (time.perf_counter() - t3) * 1000

    total_task_ms = (time.perf_counter() - task_started) * 1000
    system_chars = len(composed.system_prompt)
    user_chars = len(user_content)

    return TaskMeasurement(
        task=task.value,
        label=TASK_LABELS.get(task, task.value),
        context_build_ms=round(context_build_ms, 2),
        prompt_compose_ms=round(prompt_compose_ms, 2),
        serialization_ms=round(serialization_ms, 2),
        api_latency_ms=round(chat.last_api_latency_ms, 2),
        parsing_ms=round(parsing_ms, 2),
        total_task_ms=round(total_task_ms, 2),
        prompt_chars=system_chars + user_chars,
        system_prompt_chars=system_chars,
        user_prompt_chars=user_chars,
        payload_bytes=payload_bytes,
        response_chars=len(llm_response),
        prompt_tokens=chat.last_prompt_tokens,
        completion_tokens=chat.last_completion_tokens,
        total_tokens=chat.last_total_tokens,
    )


def measure_risk_domain() -> DomainMeasurement:
    facts = sample_risk_facts_contract()
    metadata = sample_risk_runtime_metadata()
    supplement = build_risk_metadata_supplement(metadata)
    model = settings.ai.active_model
    prompt_language = settings.ai.default_prompt_language

    provider = create_ai_provider(settings.ai)
    chat = InstrumentedCloudChat(provider)

    context_builder = ContextBuilder()
    prompt_composer = PromptComposer()
    response_parser = ResponseParser()

    request_started = datetime.now(UTC).isoformat()
    started = time.perf_counter()
    tasks: list[TaskMeasurement] = []

    for task in RISK_TASK_EXECUTION_ORDER:
        tasks.append(
            _measure_task(
                facts=facts,
                task=task,
                domain="risk",
                chat=chat,
                model=model,
                prompt_language=prompt_language,
                prompt_supplement=supplement,
                context_builder=context_builder,
                prompt_composer=prompt_composer,
                response_parser=response_parser,
            )
        )

    # Post-LLM local processing (validation/mapper — no DB persistence in this script).
    t_post = time.perf_counter()
    post_processing_ms = (time.perf_counter() - t_post) * 1000

    total_ms = (time.perf_counter() - started) * 1000
    openai_wait_ms = sum(t.api_latency_ms for t in tasks)
    pre_llm_ms = sum(
        t.context_build_ms + t.prompt_compose_ms + t.serialization_ms for t in tasks
    )
    post_llm_ms = sum(t.parsing_ms for t in tasks) + post_processing_ms
    local_ms = total_ms - openai_wait_ms

    return DomainMeasurement(
        domain="risk",
        task_count=len(tasks),
        execution_mode="sequential",
        request_started_at=request_started,
        request_total_ms=round(total_ms, 2),
        pre_llm_ms=round(pre_llm_ms, 2),
        openai_wait_ms=round(openai_wait_ms, 2),
        post_llm_ms=round(post_llm_ms, 2),
        openai_wait_pct=round((openai_wait_ms / total_ms) * 100, 1) if total_ms else 0,
        local_processing_pct=round((local_ms / total_ms) * 100, 1) if total_ms else 0,
        tasks=tasks,
        post_processing_ms=round(post_processing_ms, 2),
    )


def measure_waste_domain() -> DomainMeasurement:
    facts = sample_facts_contract()
    model = settings.ai.active_model
    prompt_language = settings.ai.default_prompt_language

    provider = create_ai_provider(settings.ai)
    chat = InstrumentedCloudChat(provider)

    context_builder = ContextBuilder()
    prompt_composer = PromptComposer()
    response_parser = ResponseParser()

    request_started = datetime.now(UTC).isoformat()
    started = time.perf_counter()
    tasks: list[TaskMeasurement] = []

    for task in TASK_EXECUTION_ORDER:
        tasks.append(
            _measure_task(
                facts=facts,
                task=task,
                domain="waste",
                chat=chat,
                model=model,
                prompt_language=prompt_language,
                prompt_supplement=None,
                context_builder=context_builder,
                prompt_composer=prompt_composer,
                response_parser=response_parser,
            )
        )

    t_post = time.perf_counter()
    post_processing_ms = (time.perf_counter() - t_post) * 1000

    total_ms = (time.perf_counter() - started) * 1000
    openai_wait_ms = sum(t.api_latency_ms for t in tasks)
    pre_llm_ms = sum(
        t.context_build_ms + t.prompt_compose_ms + t.serialization_ms for t in tasks
    )
    post_llm_ms = sum(t.parsing_ms for t in tasks) + post_processing_ms
    local_ms = total_ms - openai_wait_ms

    return DomainMeasurement(
        domain="waste",
        task_count=len(tasks),
        execution_mode="sequential",
        request_started_at=request_started,
        request_total_ms=round(total_ms, 2),
        pre_llm_ms=round(pre_llm_ms, 2),
        openai_wait_ms=round(openai_wait_ms, 2),
        post_llm_ms=round(post_llm_ms, 2),
        openai_wait_pct=round((openai_wait_ms / total_ms) * 100, 1) if total_ms else 0,
        local_processing_pct=round((local_ms / total_ms) * 100, 1) if total_ms else 0,
        tasks=tasks,
        post_processing_ms=round(post_processing_ms, 2),
    )


def try_measure_api_risk() -> dict[str, Any] | None:
    """Optional end-to-end API timing if server + credentials available."""
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure Cloud AI performance")
    parser.add_argument(
        "--domain",
        choices=("risk", "waste", "both"),
        default="risk",
        help="Which AI domain to measure",
    )
    parser.add_argument("--output", type=Path, help="Write JSON results to path")
    args = parser.parse_args()

    print(f"AI_PROVIDER={settings.ai.ai_provider} model={settings.ai.active_model}")
    print(f"CLOUD_AI_BASE_URL={settings.ai.cloud_ai_base_url}")
    print("Measuring (live OpenAI calls)...")

    results: dict[str, Any] = {
        "measured_at": datetime.now(UTC).isoformat(),
        "provider": settings.ai.ai_provider,
        "model": settings.ai.active_model,
        "domains": [],
    }

    if args.domain in ("risk", "both"):
        risk = measure_risk_domain()
        results["domains"].append(asdict(risk))
        _print_domain(risk)

    if args.domain in ("waste", "both"):
        waste = measure_waste_domain()
        results["domains"].append(asdict(waste))
        _print_domain(waste)

    if args.output:
        args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {args.output}")


def _print_domain(domain: DomainMeasurement) -> None:
    print(f"\n=== {domain.domain.upper()} ({domain.task_count} tasks, {domain.execution_mode}) ===")
    print(f"Total: {domain.request_total_ms}ms | OpenAI wait: {domain.openai_wait_ms}ms ({domain.openai_wait_pct}%)")
    print(f"Local pre-LLM: {domain.pre_llm_ms}ms | Local post-LLM: {domain.post_llm_ms}ms")
    for t in domain.tasks:
        print(
            f"  {t.label}: total={t.total_task_ms}ms api={t.api_latency_ms}ms "
            f"prompt_tokens={t.prompt_tokens} completion_tokens={t.completion_tokens} "
            f"payload={t.payload_bytes}B"
        )


if __name__ == "__main__":
    main()
