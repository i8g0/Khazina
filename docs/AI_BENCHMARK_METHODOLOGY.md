# AI Benchmark Methodology

Permanent methodology for Khazina AI pipeline performance validation (Sprint 5.5).

## Purpose

Measure production readiness of the **existing** AI execution pipeline without changing architecture or features.

## Pipeline Under Test

```
Business Engine → Facts Contract → Context Builder → Prompt Engine → Ollama → Response Parser
```

Orchestration is exercised through `AiOrchestrator.execute()` — the same path used in production.

## Fixed Inputs

All benchmark runs use identical Waste Engine input (`scripts/ai_benchmark/run_benchmark.py`):

- `total_spend`: 50,000,000
- `total_waste_amount`: 2,340,000
- Categories: overlapping_contracts (745,000), operations (520,000), finance (1,075,000)
- `organization_id`: benchmark-org
- `period`: 2026-Q2

Prompts are **not modified** between runs.

## Tasks

| Prompt Task | Identifier |
|-------------|------------|
| Executive Summary | `executive_summary` |
| Risk Analysis | `risk_analysis` |
| Recommendations | `recommendations` |
| Scenario Analysis | `scenario_analysis` |

## Metrics

| Metric | Definition |
|--------|------------|
| Cold Start | First full pipeline execution after Ollama model unload (`keep_alive=0`) |
| Warm Response | Subsequent full pipeline executions with model loaded |
| RAM | Peak process RSS and system RAM used (via `psutil`) |
| CPU | Peak system CPU utilization during runs |
| GPU | Peak utilization and VRAM via `nvidia-smi` when available |

## Stability Protocol

After cold/warm task runs, repeat all four tasks for `N` stability iterations (default `N=2`). Fail if any orchestration error occurs.

## Execution

From `backend/`:

```bash
pip install psutil
set OLLAMA_MODEL=qwen3:8b
python -m scripts.ai_benchmark.run_benchmark --stability-iterations 2
```

Outputs:

- `docs/AI_BENCHMARK_REPORT.md`
- `docs/AI_BENCHMARK_REPORT.json`

## Constraints

- Do not download new models automatically
- Do not change the development baseline model binding in code
- Do not modify Prompt Engine templates during benchmark runs
- Unit tests continue to mock Ollama; benchmarks require a running Ollama instance

## Related Documents

- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [AI_BENCHMARK_REPORT.md](AI_BENCHMARK_REPORT.md)
- [progress.md](progress.md)
