# Khazina AI Layer Freeze

**Sprint:** 5.6 — AI Freeze  
**Date:** 2026-07-14  
**Status:** **APPROVED — FROZEN**

This document formally freezes the Khazina AI layer as implemented at the end of Phase 5. No architectural changes, optimizations, or new AI features are permitted without a new ADR and Tech Lead approval.

**Related documents:**

- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) — normative AI specification (Sprint 5.2)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md) — Business Engine specification (Sprint 5.3A)
- [AI_BENCHMARK_METHODOLOGY.md](AI_BENCHMARK_METHODOLOGY.md) — benchmark framework methodology (Sprint 5.5)
- [AI_BENCHMARK_REPORT.md](AI_BENCHMARK_REPORT.md) — last archived benchmark run
- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)

---

## 1. AI Architecture Status

The AI layer is **complete** for Phase 5. All planned integration components are implemented, validated, and frozen.

### Implemented Pipeline

```
Business Engine → Facts Contract → Context Builder → Prompt Engine → Ollama → Response Parser
```

The AI Orchestrator coordinates this pipeline without embedding business logic, prompt construction, or parsing rules.

### Implemented Components

| Component | Location | Role |
|-----------|----------|------|
| Ollama Client | `backend/app/ai/client.py` | Production HTTP client for Ollama `/api/chat` |
| Prompt Engine | `backend/app/ai/prompts/` | System + user prompt composition (Arabic default) |
| Context Builder | `backend/app/ai/context/` | Facts Contract → `PromptContext` adapter |
| AI Orchestrator | `backend/app/ai/services/orchestrator.py` | End-to-end pipeline coordination |
| Conversation Service | `backend/app/ai/services/conversation.py` | In-memory multi-turn context |
| Response Parser | `backend/app/ai/parsers/response_parser.py` | Deterministic LLM output parsing |
| Business Engine (Waste) | `backend/app/business/engines/waste/` | First deterministic analysis engine |
| Facts Contract | `backend/app/business/facts/contract.py` | Immutable handoff between engines and AI |
| Benchmark Framework v2 | `backend/scripts/ai_benchmark/` | Isolated performance validation |

### Phase 5 Sprint Completion

| Sprint | Deliverable | Status |
|--------|-------------|--------|
| 5.1 | AI Foundation (Ollama client, health, config) | ✅ Complete |
| 5.2 | AI Architecture Freeze + Prompt Engine | ✅ Complete |
| 5.3A | Business Engine Architecture | ✅ Complete |
| 5.3A-R | Manifest, Immutable Registry, Fact Assembler | ✅ Complete |
| 5.3B | Facts Contract + Waste Engine | ✅ Complete |
| 5.4 | Context Builder, Orchestrator, Parser | ✅ Complete |
| 5.5 | AI Performance Validation | ✅ Complete |
| 5.5-R | Benchmark Framework v2.0 | ✅ Complete |
| 5.6 | AI Freeze (this document) | ✅ Complete |

---

## 2. Production Configuration

The following configuration is **approved for production demo** and frozen after Sprint 5.6.

| Setting | Approved Value | Source |
|---------|----------------|--------|
| **Model** | `qwen3.5:2b` | `OLLAMA_MODEL` in `backend/.env` |
| **Thinking** | **Disabled** | Ollama `think: false` (benchmark + production chat) |
| **Ollama URL** | `http://localhost:11434` | `OLLAMA_URL` |
| **Production Timeout** | `180` seconds | `AI_TIMEOUT` in `backend/.env` |
| **Benchmark Timeout** | `600` seconds | `BENCHMARK_TIMEOUT` (benchmark-only) |
| **Default Prompt Language** | `ar` | `DEFAULT_PROMPT_LANGUAGE` |
| **Prompt Version** | `1.0` | `app/ai/prompts/version.py` → `PROMPT_VERSION` |
| **Facts Contract Version** | `1.0` | `app/business/facts/contract.py` → `CONTRACT_VERSION` |
| **Context Version** | Inherits Facts Contract `1.0` | `PromptContext.contract_version` — no separate version |
| **Benchmark Profile (validation)** | `quick` | `BENCHMARK_PROFILE` default |
| **Benchmark Thinking Mode** | `disabled` | `BENCHMARK_THINKING_MODE` default |

### Configuration Notes

- Production reads `backend/.env` via Pydantic Settings (`SETTINGS_CONFIG` with `env_file=".env"`).
- Benchmark reads the same `backend/.env` via `_load_backend_env()` (Sprint 5.5 config fix).
- `AI_TIMEOUT` (production) and `BENCHMARK_TIMEOUT` (benchmark-only) are intentionally separate.
- Model selection is configuration-only — no code change required to switch models.

---

## 3. Benchmark Baseline

The benchmark framework v2.0 provides the canonical measurement method for future comparisons.

### Baseline Metadata

| Field | Value |
|-------|-------|
| **Benchmark Version** | `2.0` |
| **Approved Production Model** | `qwen3.5:2b` |
| **Validation Profile** | `quick` |
| **Thinking Mode** | `disabled` |
| **Prompt Version** | `1.0` |
| **Facts Contract Version** | `1.0` |
| **E2E Task** | `executive_summary` |
| **Report Files** | `docs/AI_BENCHMARK_REPORT.json`, `docs/AI_BENCHMARK_REPORT.md` |

### Hardware Baseline (Development Laptop)

Collected during Sprint 5.5 validation runs:

| Resource | Value |
|----------|-------|
| **Platform** | Windows 11 (10.0.26200) |
| **CPU** | Intel (20 logical CPUs) |
| **RAM** | 15.72 GB |
| **GPU** | NVIDIA GeForce RTX 3050 Laptop GPU |
| **GPU VRAM** | 4096 MB |

### Model Selection Decision

Multiple local models were compared using Benchmark Framework v2.0 (`profile=quick`, `thinking=disabled`). After functional and stability validation, the approved production demo model is:

**`qwen3.5:2b`** — selected for the best balance of Arabic executive-summary quality and acceptable latency on RTX 3050 4 GB VRAM development hardware.

Models evaluated during comparison included `qwen3:8b`, `qwen3.5:2b`, and `tinyllama:latest`. The archived report (`AI_BENCHMARK_REPORT.*`, generated 2026-07-14) reflects the last framework validation run on this hardware. Re-run the benchmark after any model or hardware change:

```bash
cd backend
python -m scripts.ai_benchmark.run_benchmark --profile quick --thinking-mode disabled
```

### Last Archived Run (Framework Validation — 2026-07-14)

The on-disk report records a successful `quick` profile run (`Functional: PASS`, `Stability: PASS`, `Overall: PASS`). Reference metrics from that run (model in report: `tinyllama:latest` — comparison artifact):

| Metric | Value |
|--------|-------|
| **LLM Benchmark (avg)** | 38,894 ms |
| **E2E Benchmark (avg)** | 4,098 ms |
| **E2E — Business Engine** | 0.23 ms |
| **E2E — Context Builder** | 0.06 ms |
| **E2E — Prompt Engine** | 0.07 ms |
| **E2E — LLM** | 3,917 ms |
| **E2E — Parser** | 0.07 ms |
| **Peak CPU** | 51.4 % |
| **Peak System RAM Used** | 11,893 MB |
| **Peak GPU Utilization** | 88.0 % |
| **Peak GPU VRAM Used** | 1,667 MB |

**Purpose:** Future benchmark runs against `qwen3.5:2b` (or successor models) should use the same profile, thinking mode, and hardware class to detect regressions.

---

## 4. Approved Components (Frozen)

The following components are **frozen** as of Sprint 5.6. Changes require ADR + Tech Lead approval.

| Component | Status | Package / Path |
|-----------|--------|----------------|
| ✓ Ollama Client | Frozen | `app/ai/client.py` |
| ✓ Prompt Engine | Frozen | `app/ai/prompts/` |
| ✓ Context Builder | Frozen | `app/ai/context/` |
| ✓ AI Orchestrator | Frozen | `app/ai/services/orchestrator.py` |
| ✓ Conversation Service | Frozen | `app/ai/services/conversation.py` |
| ✓ Response Parser | Frozen | `app/ai/parsers/response_parser.py` |
| ✓ Facts Contract | Frozen | `app/business/facts/contract.py` |
| ✓ Business Engine (Waste) | Frozen | `app/business/engines/waste/` |
| ✓ Business Engine Registry | Frozen | `app/business/registry.py` |
| ✓ Benchmark Framework v2 | Frozen | `scripts/ai_benchmark/` |

**Explicitly out of scope for Phase 5 (deferred):**

- Number Guard
- Response Validation / regeneration loop
- Multi-agent orchestration
- Cloud LLM providers
- Persistent conversation storage

---

## 5. Known Limitations

Documented limitations at freeze time. **Not to be solved in Sprint 5.6.**

| Limitation | Description |
|------------|-------------|
| Local Ollama only | AI inference requires a running Ollama instance; no cloud provider integration |
| Model-specific performance | Latency and quality depend on the deployed Ollama model (`qwen3.5:2b` approved for demo) |
| Hardware-dependent latency | Benchmark baseline collected on development laptop (RTX 3050 4 GB, 16 GB RAM) |
| Thinking disabled for demo | Qwen3 thinking mode is disabled; enabling increases latency significantly |
| In-memory conversations | Conversation Service does not persist across process restarts |
| Single Business Engine | Only Waste Engine implemented; Risk, Simulation, and other engines deferred to Phase 6+ |
| No Number Guard | LLM numeric output is not yet verified against facts |
| Arabic-first prompts | Default prompt language is Arabic (`ar`); other languages require language pack configuration |
| Benchmark sampling | GPU utilization peaks are point-in-time samples; may under-report during generation |
| Production timeout vs benchmark | Production `AI_TIMEOUT` (180s) differs from benchmark `BENCHMARK_TIMEOUT` (600s) by design |

---

## 6. Acceptance Checklist

All items verified before freeze approval.

| Item | Status |
|------|--------|
| Prompt Engine validated (4 tasks, Arabic, deterministic) | ✅ |
| Context Builder validated (Facts Contract only) | ✅ |
| Business Engine validated (Waste Engine, 16 facts E2E) | ✅ |
| Response Parser validated (deterministic parsing) | ✅ |
| AI Orchestrator validated (full pipeline, mocked + live) | ✅ |
| Benchmark Framework v2.0 complete | ✅ |
| Benchmark Functional Validation PASS | ✅ |
| Benchmark Stability Validation PASS | ✅ |
| Production model selected (`qwen3.5:2b`) | ✅ |
| Thinking mode decision (disabled) | ✅ |
| Benchmark baseline documented | ✅ |
| `.env` loading fix verified (benchmark reads `backend/.env`) | ✅ |
| No production code changes in Sprint 5.6 | ✅ |
| Unit tests passing (AI + Business + Benchmark) | ✅ |

---

## 7. Freeze Decision

### AI Layer Status: **APPROVED**

| Field | Value |
|-------|-------|
| **Frozen after** | Sprint 5.6 |
| **Phase 5 status** | **Completed** |
| **Ready for** | Phase 6 — Business Features |
| **Change control** | ADR + Tech Lead approval required for any AI layer modification |

The AI layer is stable, documented, benchmark-validated, and configuration-frozen. Phase 6 may build business features on top of this baseline without modifying the frozen AI pipeline, Prompt Engine, Context Builder, Orchestrator, Parser, or Facts Contract unless explicitly approved.

---

*End of AI Freeze document.*
