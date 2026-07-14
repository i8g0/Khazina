"""Benchmark-specific configuration — isolated from production AI settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.ai.prompts.tasks import PromptTask

from scripts.ai_benchmark.types import BenchmarkProfileName, ThinkingModeOption

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_ROOT / ".env"

DEFAULT_BENCHMARK_TIMEOUT = 600.0
DEFAULT_BENCHMARK_COOLDOWN_SECONDS = 5.0
DEFAULT_LLM_PROMPT = "قل كلمة واحدة فقط: مرحبا"


@dataclass(frozen=True, slots=True)
class ProfileDefinition:
    """Configurable benchmark profile — values are data, not hardcoded in runners."""

    name: BenchmarkProfileName
    e2e_tasks: tuple[PromptTask, ...]
    run_cold_start: bool
    run_cold_unload: bool
    stability_iterations: int
    cooldown_seconds: float
    llm_iterations: int
    run_llm_benchmark: bool
    run_e2e_benchmark: bool


PROFILE_DEFINITIONS: dict[BenchmarkProfileName, ProfileDefinition] = {
    BenchmarkProfileName.QUICK: ProfileDefinition(
        name=BenchmarkProfileName.QUICK,
        e2e_tasks=(PromptTask.EXECUTIVE_SUMMARY,),
        run_cold_start=False,
        run_cold_unload=False,
        stability_iterations=0,
        cooldown_seconds=2.0,
        llm_iterations=1,
        run_llm_benchmark=True,
        run_e2e_benchmark=True,
    ),
    BenchmarkProfileName.STANDARD: ProfileDefinition(
        name=BenchmarkProfileName.STANDARD,
        e2e_tasks=(
            PromptTask.EXECUTIVE_SUMMARY,
            PromptTask.RISK_ANALYSIS,
            PromptTask.RECOMMENDATIONS,
            PromptTask.SCENARIO_ANALYSIS,
        ),
        run_cold_start=True,
        run_cold_unload=True,
        stability_iterations=0,
        cooldown_seconds=5.0,
        llm_iterations=2,
        run_llm_benchmark=True,
        run_e2e_benchmark=True,
    ),
    BenchmarkProfileName.FULL: ProfileDefinition(
        name=BenchmarkProfileName.FULL,
        e2e_tasks=(
            PromptTask.EXECUTIVE_SUMMARY,
            PromptTask.RISK_ANALYSIS,
            PromptTask.RECOMMENDATIONS,
            PromptTask.SCENARIO_ANALYSIS,
        ),
        run_cold_start=True,
        run_cold_unload=True,
        stability_iterations=2,
        cooldown_seconds=10.0,
        llm_iterations=3,
        run_llm_benchmark=True,
        run_e2e_benchmark=True,
    ),
}


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    profile: ProfileDefinition
    benchmark_timeout: float
    thinking_mode: ThinkingModeOption
    ollama_url: str
    ollama_model: str
    llm_prompt: str
    output_json_path: str
    output_md_path: str
    skip_cold_unload: bool = False

    @property
    def thinking_modes_to_run(self) -> tuple[bool, ...]:
        if self.thinking_mode is ThinkingModeOption.BOTH:
            return (False, True)
        return (self.thinking_mode is ThinkingModeOption.ENABLED,)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return float(raw)


def _env_profile(name: str | None) -> BenchmarkProfileName:
    raw = (name or os.environ.get("BENCHMARK_PROFILE", BenchmarkProfileName.QUICK.value)).strip().lower()
    return BenchmarkProfileName(raw)


def _env_thinking(name: str | None) -> ThinkingModeOption:
    raw = (name or os.environ.get("BENCHMARK_THINKING_MODE", ThinkingModeOption.DISABLED.value)).strip().lower()
    return ThinkingModeOption(raw)


def _load_backend_env() -> None:
    """Load backend/.env into os.environ (same source as Pydantic Settings)."""
    if _ENV_FILE.is_file():
        load_dotenv(_ENV_FILE, encoding="utf-8")


def load_benchmark_config(
    *,
    profile: str | None = None,
    thinking_mode: str | None = None,
    benchmark_timeout: float | None = None,
    output_json: str | None = None,
    output_md: str | None = None,
    skip_cold_unload: bool = False,
) -> BenchmarkConfig:
    """Load benchmark configuration from env and CLI overrides."""
    _load_backend_env()
    profile_name = _env_profile(profile)
    profile_def = PROFILE_DEFINITIONS[profile_name]
    return BenchmarkConfig(
        profile=profile_def,
        benchmark_timeout=benchmark_timeout
        if benchmark_timeout is not None
        else _env_float("BENCHMARK_TIMEOUT", DEFAULT_BENCHMARK_TIMEOUT),
        thinking_mode=_env_thinking(thinking_mode),
        ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "qwen3:8b"),
        llm_prompt=os.environ.get("BENCHMARK_LLM_PROMPT", DEFAULT_LLM_PROMPT),
        output_json_path=output_json or os.environ.get(
            "BENCHMARK_OUTPUT_JSON", "docs/AI_BENCHMARK_REPORT.json"
        ),
        output_md_path=output_md or os.environ.get(
            "BENCHMARK_OUTPUT_MD", "docs/AI_BENCHMARK_REPORT.md"
        ),
        skip_cold_unload=skip_cold_unload,
    )


def ensure_runtime_env() -> None:
    """Set minimal app env vars required to import Khazina modules."""
    _load_backend_env()
    os.environ.setdefault(
        "DATABASE_URL", "postgresql://benchmark:benchmark@localhost/benchmark"
    )
    os.environ.setdefault("JWT_SECRET_KEY", "benchmark-secret-key-32-characters!!")
    os.environ.setdefault("OLLAMA_URL", os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    os.environ.setdefault("OLLAMA_MODEL", os.environ.get("OLLAMA_MODEL", "qwen3:8b"))
