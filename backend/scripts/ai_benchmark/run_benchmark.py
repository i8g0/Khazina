"""Khazina AI Benchmark Framework — CLI entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = BACKEND_ROOT.parent / "docs"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def main() -> None:
    from scripts.ai_benchmark.config import ensure_runtime_env, load_benchmark_config
    from scripts.ai_benchmark.framework import BenchmarkFramework
    from scripts.ai_benchmark.types import BenchmarkProfileName, ThinkingModeOption

    parser = argparse.ArgumentParser(
        description="Khazina AI Benchmark Framework (Sprint 5.5)."
    )
    parser.add_argument(
        "--profile",
        choices=[item.value for item in BenchmarkProfileName],
        default=None,
        help="Benchmark profile (default: BENCHMARK_PROFILE or quick).",
    )
    parser.add_argument(
        "--thinking-mode",
        choices=[item.value for item in ThinkingModeOption],
        default=None,
        help="Thinking mode: enabled, disabled, or both (default: BENCHMARK_THINKING_MODE or disabled).",
    )
    parser.add_argument(
        "--benchmark-timeout",
        type=float,
        default=None,
        help="Benchmark-only timeout in seconds (default: BENCHMARK_TIMEOUT or 600).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=DOCS_ROOT / "AI_BENCHMARK_REPORT.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=DOCS_ROOT / "AI_BENCHMARK_REPORT.md",
    )
    parser.add_argument(
        "--skip-cold-unload",
        action="store_true",
        help="Skip Ollama model unload before cold start.",
    )
    args = parser.parse_args()

    ensure_runtime_env()
    config = load_benchmark_config(
        profile=args.profile,
        thinking_mode=args.thinking_mode,
        benchmark_timeout=args.benchmark_timeout,
        output_json=str(args.output_json),
        output_md=str(args.output_md),
        skip_cold_unload=args.skip_cold_unload,
    )

    report = BenchmarkFramework(config).execute()
    if not report.overall_success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
