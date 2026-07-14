"""Benchmark framework orchestrator."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.ai.context.builder import ContextBuilder
from app.ai.parsers.response_parser import ResponseParser
from app.ai.prompts.composer import PromptComposer
from app.ai.prompts.tasks import PromptTask

from scripts.ai_benchmark.config import BenchmarkConfig
from scripts.ai_benchmark.e2e_benchmark import E2EBenchmarkRunner, prepare_registry
from scripts.ai_benchmark.llm_benchmark import LLMBenchmarkRunner
from scripts.ai_benchmark.monitor import collect_hardware_summary, require_psutil
from scripts.ai_benchmark.ollama_client import BenchmarkOllamaClient
from scripts.ai_benchmark.progress import ProgressLogger
from scripts.ai_benchmark.report import BenchmarkReport, build_report, write_report
from scripts.ai_benchmark.types import BenchmarkRunRecord


@dataclass
class BenchmarkFramework:
    config: BenchmarkConfig
    runs: list[BenchmarkRunRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def execute(self) -> BenchmarkReport:
        require_psutil()
        prepare_registry()
        hardware = collect_hardware_summary()
        client = BenchmarkOllamaClient(self.config)
        llm_runner = LLMBenchmarkRunner(self.config, client)
        e2e_runner = E2EBenchmarkRunner(
            self.config,
            client,
            ContextBuilder(),
            PromptComposer(),
            ResponseParser(),
        )

        total_steps = self._count_steps()
        progress = ProgressLogger(total_steps=total_steps)
        print(
            f"Khazina AI Benchmark v2 — profile={self.config.profile.name.value}, "
            f"thinking={self.config.thinking_mode.value}, steps={total_steps}",
            flush=True,
        )

        for thinking_enabled in self.config.thinking_modes_to_run:
            thinking_label = "enabled" if thinking_enabled else "disabled"
            self.notes.append(f"Executing thinking_mode={thinking_label}")

            if self.config.profile.run_llm_benchmark:
                for iteration in range(1, self.config.profile.llm_iterations + 1):
                    self._cooldown(progress)
                    record = llm_runner.run_iteration(
                        iteration=iteration,
                        thinking_enabled=thinking_enabled,
                        progress=progress,
                    )
                    self.runs.append(record)

            if not self.config.profile.run_e2e_benchmark:
                continue

            if (
                self.config.profile.run_cold_unload
                and not self.config.skip_cold_unload
            ):
                progress.begin(f"Pre-cold unload (thinking={thinking_label})")
                client.unload_model()
                progress.complete(extra="model unload requested (keep_alive=0)")
                self.notes.append("Pre-cold unload executed before cold start.")

            tasks = list(self.config.profile.e2e_tasks)
            if self.config.profile.run_cold_start and tasks:
                self._cooldown(progress)
                cold_task = tasks[0]
                record = e2e_runner.run(
                    task=cold_task,
                    run_label="cold_start",
                    thinking_enabled=thinking_enabled,
                    progress=progress,
                )
                self.runs.append(record)

            for task in tasks:
                self._cooldown(progress)
                record = e2e_runner.run(
                    task=task,
                    run_label="warm",
                    thinking_enabled=thinking_enabled,
                    progress=progress,
                )
                self.runs.append(record)

            for iteration in range(1, self.config.profile.stability_iterations + 1):
                for task in tasks:
                    self._cooldown(progress)
                    record = e2e_runner.run(
                        task=task,
                        run_label=f"stability_{iteration}",
                        thinking_enabled=thinking_enabled,
                        progress=progress,
                    )
                    self.runs.append(record)

        report = build_report(
            generated_at=datetime.now(UTC).isoformat(),
            config=self.config,
            hardware=hardware,
            runs=self.runs,
            notes=self.notes,
        )
        write_report(
            report,
            json_path=self.config.output_json_path,
            md_path=self.config.output_md_path,
        )
        print(f"Wrote {self.config.output_json_path}")
        print(f"Wrote {self.config.output_md_path}")
        return report

    def _cooldown(self, progress: ProgressLogger) -> None:
        seconds = self.config.profile.cooldown_seconds
        if seconds <= 0:
            return
        progress.info(f"Cooldown {seconds}s...")
        time.sleep(seconds)

    def _count_steps(self) -> int:
        steps = 0
        modes = len(self.config.thinking_modes_to_run)
        profile = self.config.profile

        if profile.run_llm_benchmark:
            steps += modes * profile.llm_iterations

        if profile.run_e2e_benchmark:
            per_mode = len(profile.e2e_tasks)
            if profile.run_cold_start:
                per_mode += 1
            per_mode += profile.stability_iterations * len(profile.e2e_tasks)
            if profile.run_cold_unload and not self.config.skip_cold_unload:
                per_mode += 1
            steps += modes * per_mode

        return max(steps, 1)
