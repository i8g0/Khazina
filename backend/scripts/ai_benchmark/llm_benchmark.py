"""LLM-only benchmark — measures prompt → Ollama → response latency."""

from __future__ import annotations

import time
from dataclasses import dataclass

from scripts.ai_benchmark.config import BenchmarkConfig
from scripts.ai_benchmark.monitor import sample_resources
from scripts.ai_benchmark.ollama_client import BenchmarkOllamaClient
from scripts.ai_benchmark.progress import ProgressLogger
from scripts.ai_benchmark.types import BenchmarkRunRecord, StageTimingsMs, ThinkingSetting


@dataclass
class LLMBenchmarkRunner:
    config: BenchmarkConfig
    client: BenchmarkOllamaClient

    def run_iteration(
        self,
        *,
        iteration: int,
        thinking_enabled: bool,
        progress: ProgressLogger,
    ) -> BenchmarkRunRecord:
        thinking_label: ThinkingSetting = "enabled" if thinking_enabled else "disabled"
        label = f"LLM Benchmark (thinking={thinking_label}, iteration={iteration})"
        progress.begin(label)

        peak_process = peak_ram = peak_cpu = peak_gpu = peak_vram = None

        def absorb() -> None:
            nonlocal peak_process, peak_ram, peak_cpu, peak_gpu, peak_vram
            sample = sample_resources()
            peak_process = _max(peak_process, sample.process_rss_mb)
            peak_ram = _max(peak_ram, sample.system_ram_used_mb)
            peak_cpu = _max(peak_cpu, sample.cpu_percent)
            peak_gpu = _max(peak_gpu, sample.gpu_utilization_percent)
            peak_vram = _max(peak_vram, sample.gpu_vram_used_mb)

        messages = [{"role": "user", "content": self.config.llm_prompt}]
        absorb()
        start = time.perf_counter()
        try:
            response = self.client.chat(messages, thinking_enabled=thinking_enabled)
        except Exception as exc:  # noqa: BLE001 - benchmark boundary
            progress.fail(str(exc))
            return BenchmarkRunRecord(
                benchmark_type="llm",
                profile=self.config.profile.name.value,
                run_label=f"llm_{iteration}",
                task=None,
                thinking_mode=thinking_label,
                success=False,
                error=str(exc),
            )
        absorb()
        llm_ms = round((time.perf_counter() - start) * 1000, 2)
        timings = StageTimingsMs(llm_ms=llm_ms, total_ms=llm_ms)
        progress.complete(extra=f"response_chars={len(response)}")

        return BenchmarkRunRecord(
            benchmark_type="llm",
            profile=self.config.profile.name.value,
            run_label=f"llm_{iteration}",
            task=None,
            thinking_mode=thinking_label,
            success=True,
            stage_timings=timings,
            prompt_chars=len(self.config.llm_prompt),
            peak_process_rss_mb=peak_process,
            peak_system_ram_used_mb=peak_ram,
            peak_cpu_percent=peak_cpu,
            peak_gpu_utilization_percent=peak_gpu,
            peak_gpu_vram_used_mb=peak_vram,
            extensions={"response_chars": len(response)},
        )


def _max(current: float | None, value: float | None) -> float | None:
    if value is None:
        return current
    if current is None:
        return value
    return max(current, value)
