"""End-to-end AI benchmark — full pipeline with per-stage timing."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime

from app.ai.context.builder import ContextBuilder
from app.ai.context.types import ContextBuildOptions
from app.ai.parsers.response_parser import ResponseParser
from app.ai.prompts.composer import PromptComposer
from app.ai.prompts.tasks import PromptTask
from app.business.engines.waste.engine import WasteEngine
from app.business.engines.waste.input import WasteCategoryInput, WasteEngineInput
from app.business.registry import freeze_registry, get_engine, register_engine, reset_registry_for_testing

from scripts.ai_benchmark.config import BenchmarkConfig
from scripts.ai_benchmark.monitor import sample_resources
from scripts.ai_benchmark.ollama_client import BenchmarkOllamaClient
from scripts.ai_benchmark.progress import ProgressLogger
from scripts.ai_benchmark.types import BenchmarkRunRecord, StageTimingsMs, ThinkingSetting


def fixed_waste_input() -> WasteEngineInput:
    return WasteEngineInput(
        total_spend=50_000_000.0,
        total_waste_amount=2_340_000.0,
        categories=(
            WasteCategoryInput("overlapping_contracts", 745_000.0),
            WasteCategoryInput("operations", 520_000.0),
            WasteCategoryInput("finance", 1_075_000.0),
        ),
        organization_id="benchmark-org",
        period="2026-Q2",
        generated_at=datetime(2026, 7, 13, tzinfo=UTC),
    )


def prepare_registry() -> None:
    reset_registry_for_testing()
    register_engine(WasteEngine())
    freeze_registry()


@dataclass
class E2EBenchmarkRunner:
    config: BenchmarkConfig
    client: BenchmarkOllamaClient
    context_builder: ContextBuilder
    prompt_composer: PromptComposer
    response_parser: ResponseParser

    def run(
        self,
        *,
        task: PromptTask,
        run_label: str,
        thinking_enabled: bool,
        progress: ProgressLogger,
    ) -> BenchmarkRunRecord:
        thinking_label: ThinkingSetting = "enabled" if thinking_enabled else "disabled"
        progress.begin(f"E2E / {task.value} (thinking={thinking_label}, {run_label})")

        peak_process = peak_ram = peak_cpu = peak_gpu = peak_vram = None

        def absorb() -> None:
            nonlocal peak_process, peak_ram, peak_cpu, peak_gpu, peak_vram
            sample = sample_resources()
            peak_process = _max(peak_process, sample.process_rss_mb)
            peak_ram = _max(peak_ram, sample.system_ram_used_mb)
            peak_cpu = _max(peak_cpu, sample.cpu_percent)
            peak_gpu = _max(peak_gpu, sample.gpu_utilization_percent)
            peak_vram = _max(peak_vram, sample.gpu_vram_used_mb)

        absorb()
        total_start = time.perf_counter()
        try:
            engine_start = time.perf_counter()
            engine = get_engine("waste")
            facts_contract = engine.run(fixed_waste_input())
            business_engine_ms = _elapsed_ms(engine_start)

            context_start = time.perf_counter()
            prompt_context = self.context_builder.build(
                facts_contract,
                ContextBuildOptions(task=task, domain="waste"),
            )
            context_builder_ms = _elapsed_ms(context_start)

            prompt_start = time.perf_counter()
            composed = self.prompt_composer.compose(task, prompt_context.facts)
            prompt_engine_ms = _elapsed_ms(prompt_start)

            messages = [
                {"role": "system", "content": composed.system_prompt},
                {"role": "user", "content": composed.user_prompt},
            ]
            prompt_chars = len(composed.system_prompt) + len(composed.user_prompt)

            llm_start = time.perf_counter()
            llm_response = self.client.chat(messages, thinking_enabled=thinking_enabled)
            llm_ms = _elapsed_ms(llm_start)
            absorb()

            parser_start = time.perf_counter()
            parsed = self.response_parser.parse(llm_response)
            parser_ms = _elapsed_ms(parser_start)

            total_ms = round((time.perf_counter() - total_start) * 1000, 2)
            timings = StageTimingsMs(
                business_engine_ms=business_engine_ms,
                context_builder_ms=context_builder_ms,
                prompt_engine_ms=prompt_engine_ms,
                llm_ms=llm_ms,
                parser_ms=parser_ms,
                total_ms=total_ms,
            )
        except Exception as exc:  # noqa: BLE001 - benchmark boundary
            progress.fail(str(exc))
            return BenchmarkRunRecord(
                benchmark_type="e2e",
                profile=self.config.profile.name.value,
                run_label=run_label,
                task=task.value,
                thinking_mode=thinking_label,
                success=False,
                error=str(exc),
            )

        progress.complete(
            extra=(
                f"total={timings.total_ms}ms "
                f"(engine={timings.business_engine_ms}, "
                f"context={timings.context_builder_ms}, "
                f"prompt={timings.prompt_engine_ms}, "
                f"llm={timings.llm_ms}, "
                f"parser={timings.parser_ms})"
            )
        )
        return BenchmarkRunRecord(
            benchmark_type="e2e",
            profile=self.config.profile.name.value,
            run_label=run_label,
            task=task.value,
            thinking_mode=thinking_label,
            success=True,
            stage_timings=timings,
            facts_count=len(facts_contract.facts),
            selected_facts_count=prompt_context.selected_fact_count,
            parsed_format=parsed.format,
            prompt_chars=prompt_chars,
            peak_process_rss_mb=peak_process,
            peak_system_ram_used_mb=peak_ram,
            peak_cpu_percent=peak_cpu,
            peak_gpu_utilization_percent=peak_gpu,
            peak_gpu_vram_used_mb=peak_vram,
        )


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def _max(current: float | None, value: float | None) -> float | None:
    if value is None:
        return current
    if current is None:
        return value
    return max(current, value)
