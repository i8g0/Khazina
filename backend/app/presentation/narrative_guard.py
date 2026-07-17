"""Number-guard retry and graceful narrative degradation (AI_ARCHITECTURE §13/§15)."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from app.ai.exceptions import AIConnectionError, AITimeoutError
from app.ai.prompts.tasks import PromptTask
from app.business.facts.contract import FactsContract
from app.core.config import settings
from app.presentation.evidence_registry import EvidenceRegistry, normalize_text

if TYPE_CHECKING:
    from app.ai_recommendations.pipeline import AiTaskPipeline, TaskExecutionResult

NARRATIVE_REJECTED = "rejected_by_guard"
NARRATIVE_LLM_UNAVAILABLE = "llm_unavailable"

_GUARD_ADDENDUM = (
    "الأرقام التالية غير موجودة في الحقائق: {numbers}. "
    "أعد الصياغة باستخدام أرقام الحقائق فقط."
)


def guard_retry_addendum(errors: list[str]) -> str:
    numbers = [
        err.split(":", 1)[1]
        for err in errors
        if err.startswith("unsupported_number:")
    ]
    if not numbers:
        numbers = [err for err in errors if err.startswith("unsupported_number")]
    return _GUARD_ADDENDUM.format(numbers=", ".join(numbers) if numbers else "—")


def apply_numbers_only_guard(
    registry: EvidenceRegistry,
    text: str,
    *,
    retry: Callable[[str], str] | None = None,
) -> tuple[str | None, str | None]:
    """Validate narrative numbers; optional single retry. Returns (text, narrative_status)."""
    normalized = normalize_text(text)
    errors = registry.validate_numbers_only(normalized)
    if not errors:
        return text, None

    max_retries = settings.ai.guard_max_retries
    if retry is not None and max_retries > 0:
        retried = retry(guard_retry_addendum(errors))
        retry_errors = registry.validate_numbers_only(normalize_text(retried))
        if not retry_errors:
            return retried, None
        return None, NARRATIVE_REJECTED

    return None, NARRATIVE_REJECTED


def retry_task_with_addendum(
    pipeline: AiTaskPipeline,
    facts: FactsContract,
    task: PromptTask,
    addendum: str,
    *,
    domain: str = "waste",
    prompt_language: str | None = None,
    prompt_supplement: str | None = None,
) -> TaskExecutionResult:
    supplement_parts = [part for part in (prompt_supplement, addendum) if part]
    merged = "\n\n".join(supplement_parts) if supplement_parts else addendum
    return pipeline.execute_task(
        facts,
        task,
        domain=domain,
        prompt_language=prompt_language,
        prompt_supplement=merged,
    )


def guard_executive_summary_task(
    task_result: TaskExecutionResult,
    facts: FactsContract,
    pipeline: AiTaskPipeline,
    *,
    domain: str = "waste",
    prompt_language: str | None = None,
    prompt_supplement: str | None = None,
) -> tuple[TaskExecutionResult, str | None]:
    registry = EvidenceRegistry.from_contract(facts)
    text = task_result.parsed_response.text
    guarded, status = apply_numbers_only_guard(
        registry,
        text,
        retry=lambda addendum: retry_task_with_addendum(
            pipeline,
            facts,
            task_result.task,
            addendum,
            domain=domain,
            prompt_language=prompt_language,
            prompt_supplement=prompt_supplement,
        ).parsed_response.text,
    )
    if guarded is None:
        return task_result, status
    if guarded == text:
        return task_result, None
    from app.ai.parsers.types import ParsedResponse
    from app.ai_recommendations.pipeline import TaskExecutionResult

    return TaskExecutionResult(
        task=task_result.task,
        composed_prompt=task_result.composed_prompt,
        llm_response_text=guarded,
        parsed_response=ParsedResponse(
            text=guarded,
            format=task_result.parsed_response.format,
            data=task_result.parsed_response.data,
        ),
    ), None


def strip_rejected_narratives(payload: dict[str, Any], *, fields: tuple[str, ...]) -> dict[str, Any]:
    updated = dict(payload)
    for field in fields:
        updated.pop(field, None)
    updated["narrative_status"] = NARRATIVE_REJECTED
    return updated


def facts_only_insights_payload(
    *,
    facts: FactsContract,
    model_name: str,
    domain: str,
    narrative_status: str,
    generated_at_iso: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "domain": domain,
        "generated_at": generated_at_iso,
        "model": model_name,
        "facts_contract_version": facts.contract_version,
        "engine_id": facts.engine_id,
        "engine_version": facts.engine_version,
        "narrative_status": narrative_status,
        "narrative": {},
    }
    if extra:
        payload.update(extra)
    return payload


def is_llm_transport_error(exc: BaseException) -> bool:
    return isinstance(exc, (AIConnectionError, AITimeoutError))


def merge_task_results(
    results: tuple[TaskExecutionResult, ...],
    replacement: TaskExecutionResult,
) -> tuple[TaskExecutionResult, ...]:
    return tuple(replacement if r.task == replacement.task else r for r in results)
