# Khazina AI Benchmark Report

**Generated:** 2026-07-16T11:38:18.467001+00:00

## Benchmark Baseline

- **Benchmark Version:** 2.0
- **Profile:** quick
- **Model:** `qwen3.5:4b`
- **Prompt Version:** 1.0
- **Facts Contract Version:** 1.0
- **Thinking Mode Setting:** disabled

## Configuration

- **benchmark_timeout:** 600.0
- **cooldown_seconds:** 2.0
- **e2e_tasks:** ['executive_summary']
- **llm_iterations:** 1
- **llm_prompt:** قل كلمة واحدة فقط: مرحبا
- **ollama_model:** qwen3.5:4b
- **ollama_url:** http://localhost:11434
- **profile:** quick
- **stability_iterations:** 0
- **thinking_mode:** disabled

## Hardware Summary

- **Platform:** Windows-11-10.0.26200-SP0
- **Processor:** Intel64 Family 6 Model 183 Stepping 1, GenuineIntel
- **Logical CPUs:** 20
- **Total RAM:** 15.63 GB
- **GPU:** NVIDIA GeForce RTX 4060 Laptop GPU
- **GPU VRAM (total):** 8188 MB

## Results Summary

- **Functional Validation:** PASS
- **Stability Validation:** PASS
- **Overall:** PASS

### LLM Benchmark Latency

| Thinking | Avg ms | Min ms | Max ms | Samples |
|----------|--------|--------|--------|---------|
| disabled | 10148.18 | 10148.18 | 10148.18 | 1 |

### End-to-End Benchmark Latency

| Thinking | Avg ms | Min ms | Max ms | Samples |
|----------|--------|--------|--------|---------|
| disabled | 6558.38 | 6558.38 | 6558.38 | 1 |

### Resource Peaks

- **Process RSS:** 83.38 MB
- **System RAM Used:** 12832.99 MB
- **CPU:** 26.0 %
- **GPU Utilization:** 91.0 %
- **GPU VRAM Used:** 5361.0 MB

## Recommendation

Keep `qwen3.5:4b` for hackathon demo. Profile `quick` completed successfully. Thinking disabled average latency: 6558 ms. Retain GPU acceleration for demo.

## Notes

- Executing thinking_mode=disabled

## Run Details

| Type | Label | Task | Thinking | Success | Total ms | LLM ms | Engine ms |
|------|-------|------|----------|---------|----------|--------|-----------|
| llm | llm_1 | - | disabled | True | 10148.18 | 10148.18 | 0.0 |
| e2e | warm | executive_summary | disabled | True | 6558.38 | 6390.26 | 0.17 |
