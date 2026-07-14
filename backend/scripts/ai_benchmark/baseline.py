"""Benchmark baseline metadata for historical comparison."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from app.ai.prompts.version import PROMPT_VERSION
from app.business.facts.contract import CONTRACT_VERSION
from scripts.ai_benchmark.monitor import HardwareSummary
from scripts.ai_benchmark.version import BENCHMARK_VERSION


@dataclass(frozen=True, slots=True)
class BenchmarkBaseline:
    benchmark_version: str
    profile: str
    model: str
    model_version: str | None
    prompt_version: str
    facts_contract_version: str
    thinking_mode: str
    hardware: HardwareSummary

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["hardware"] = asdict(self.hardware)
        return payload


def build_baseline(
    *,
    profile: str,
    model: str,
    thinking_mode: str,
    hardware: HardwareSummary,
    model_version: str | None = None,
) -> BenchmarkBaseline:
    return BenchmarkBaseline(
        benchmark_version=BENCHMARK_VERSION,
        profile=profile,
        model=model,
        model_version=model_version,
        prompt_version=PROMPT_VERSION,
        facts_contract_version=CONTRACT_VERSION,
        thinking_mode=thinking_mode,
        hardware=hardware,
    )
