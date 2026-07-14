# Khazina AI Benchmark Report

**Generated:** 2026-07-14T12:32:52.921072+00:00

## Benchmark Baseline

- **Benchmark Version:** 2.0
- **Profile:** quick
- **Model:** `tinyllama:latest`
- **Prompt Version:** 1.0
- **Facts Contract Version:** 1.0
- **Thinking Mode Setting:** disabled

## Configuration

- **benchmark_timeout:** 600.0
- **cooldown_seconds:** 2.0
- **e2e_tasks:** ['executive_summary']
- **llm_iterations:** 1
- **llm_prompt:** قل كلمة واحدة فقط: مرحبا
- **ollama_model:** tinyllama:latest
- **ollama_url:** http://localhost:11434
- **profile:** quick
- **stability_iterations:** 0
- **thinking_mode:** disabled

## Hardware Summary

- **Platform:** Windows-11-10.0.26200-SP0
- **Processor:** Intel64 Family 6 Model 154 Stepping 3, GenuineIntel
- **Logical CPUs:** 20
- **Total RAM:** 15.72 GB
- **GPU:** NVIDIA GeForce RTX 3050 Laptop GPU
- **GPU VRAM (total):** 4096 MB

## Results Summary

- **Functional Validation:** PASS
- **Stability Validation:** PASS
- **Overall:** PASS

### LLM Benchmark Latency

| Thinking | Avg ms | Min ms | Max ms | Samples |
|----------|--------|--------|--------|---------|
| disabled | 38893.58 | 38893.58 | 38893.58 | 1 |

### End-to-End Benchmark Latency

| Thinking | Avg ms | Min ms | Max ms | Samples |
|----------|--------|--------|--------|---------|
| disabled | 4098.07 | 4098.07 | 4098.07 | 1 |

### Resource Peaks

- **Process RSS:** 49.33 MB
- **System RAM Used:** 11893.41 MB
- **CPU:** 51.4 %
- **GPU Utilization:** 88.0 %
- **GPU VRAM Used:** 1667.0 MB

## Recommendation

Keep `tinyllama:latest` for hackathon demo. Profile `quick` completed successfully. Thinking disabled average latency: 4098 ms. Retain GPU acceleration for demo.

## Notes

- Executing thinking_mode=disabled

## Run Details

| Type | Label | Task | Thinking | Success | Total ms | LLM ms | Engine ms |
|------|-------|------|----------|---------|----------|--------|-----------|
| llm | llm_1 | - | disabled | True | 38893.58 | 38893.58 | 0.0 |
| e2e | warm | executive_summary | disabled | True | 4098.07 | 3917.45 | 0.23 |
