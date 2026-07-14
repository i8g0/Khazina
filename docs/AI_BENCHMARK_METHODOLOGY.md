# AI Benchmark Framework (Sprint 5.5)

Benchmark-only configuration. Production `AI_TIMEOUT` is unchanged.

```bash
pip install psutil
set OLLAMA_MODEL=qwen3:8b
set BENCHMARK_PROFILE=quick
set BENCHMARK_TIMEOUT=600
python -m scripts.ai_benchmark.run_benchmark
```

## Profiles

| Profile | Purpose |
|---------|---------|
| `quick` | Fast development validation (1 E2E task, 1 LLM iteration) |
| `standard` | Normal validation (cold + 4 warm tasks) |
| `full` | Release/demo validation (cold + warm + stability iterations) |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BENCHMARK_PROFILE` | `quick` | `quick`, `standard`, or `full` |
| `BENCHMARK_TIMEOUT` | `600` | Benchmark-only Ollama timeout (seconds) |
| `BENCHMARK_THINKING_MODE` | `disabled` | `enabled`, `disabled`, or `both` |
| `BENCHMARK_LLM_PROMPT` | short Arabic ping | LLM benchmark prompt |
| `BENCHMARK_OUTPUT_JSON` | `docs/AI_BENCHMARK_REPORT.json` | JSON output path |
| `BENCHMARK_OUTPUT_MD` | `docs/AI_BENCHMARK_REPORT.md` | Markdown output path |

## Benchmark Types

### LLM Benchmark

Measures: Prompt → Ollama → Response (pure model latency).

### End-to-End Benchmark

Measures full pipeline with per-stage timings:

- Business Engine
- Context Builder
- Prompt Engine
- LLM
- Response Parser

## CLI Options

```bash
python -m scripts.ai_benchmark.run_benchmark --profile quick --thinking-mode both
python -m scripts.ai_benchmark.run_benchmark --profile standard --benchmark-timeout 600
python -m scripts.ai_benchmark.run_benchmark --profile full --skip-cold-unload
```

## Progress Logging

Every step prints:

```
[1/N] Step label...
    Completed — details
    Elapsed: xxx ms
    Remaining steps: y
```

## Baseline Metadata

Each report records:

- Benchmark version
- Model
- Prompt version
- Facts Contract version
- Profile
- Hardware summary

For historical comparison only (no database).

## Related

- [AI_BENCHMARK_METHODOLOGY.md](AI_BENCHMARK_METHODOLOGY.md)
- [AI_BENCHMARK_REPORT.md](AI_BENCHMARK_REPORT.md)
