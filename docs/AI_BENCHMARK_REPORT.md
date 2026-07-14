# Khazina AI Pipeline Benchmark Report

**Generated:** 2026-07-13T21:12:35.040662+00:00
**Methodology version:** 1.0

## Hardware Summary

- **Platform:** Windows-11-10.0.26200-SP0
- **Processor:** Intel64 Family 6 Model 154 Stepping 3, GenuineIntel
- **Logical CPUs:** 20
- **Total RAM:** 15.72 GB
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU
- **GPU VRAM (total):** 4096 MB

## Active AI Model

- **Ollama URL:** http://localhost:11434
- **Model:** `qwen3:8b`

## Benchmark Methodology

See [AI_BENCHMARK_METHODOLOGY.md](AI_BENCHMARK_METHODOLOGY.md).

## Latency Results

- **Cold start:** 170667.81 ms
- **Average warm latency:** 157750.10 ms
- **Minimum warm latency:** 151972.38 ms
- **Maximum warm latency:** 165096.07 ms
- **Executions recorded:** 13

## Resource Usage (Peaks)

- **Process RSS:** 53.32 MB
- **System RAM used:** 15314.26 MB
- **CPU utilization:** 70.8%
- **GPU utilization:** 25.0%
- **GPU VRAM used:** 3154.00 MB

## Validation

- **Functional pipeline validation:** FAIL
- **Stability validation:** FAIL

## Demo Recommendation

Do not change the development baseline yet. Stability or functional validation failed during benchmark runs.

## Notes

- Cold start measured after Ollama keep_alive=0 unload request.

## Run Details

| Task | Run Type | Success | Total ms | Facts | Parsed |
|------|----------|---------|----------|-------|--------|
| executive_summary | cold_start | True | 170667.81 | 16 | text |
| executive_summary | warm | True | 156181.84 | 16 | text |
| risk_analysis | warm | False | n/a | n/a | Ollama request timed out after 180.0s |
| recommendations | warm | True | 151972.38 | 16 | text |
| scenario_analysis | warm | False | n/a | n/a | Ollama request timed out after 180.0s |
| executive_summary | stability_1 | True | 165096.07 | 16 | text |
| risk_analysis | stability_1 | False | n/a | n/a | Ollama request timed out after 180.0s |
| recommendations | stability_1 | False | n/a | n/a | Ollama request timed out after 180.0s |
| scenario_analysis | stability_1 | False | n/a | n/a | Ollama request timed out after 180.0s |
| executive_summary | stability_2 | False | n/a | n/a | Ollama request timed out after 180.0s |
| risk_analysis | stability_2 | False | n/a | n/a | Ollama request timed out after 180.0s |
| recommendations | stability_2 | False | n/a | n/a | Ollama request timed out after 180.0s |
| scenario_analysis | stability_2 | False | n/a | n/a | Ollama request timed out after 180.0s |
