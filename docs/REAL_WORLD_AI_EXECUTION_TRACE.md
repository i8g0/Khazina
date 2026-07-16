# Real-World AI Execution Trace

**Date:** 2026-07-16  
**Investigation:** Contradiction between benchmark (~9s waste) and UI (~40s) with no visible OpenAI `/chat/completions` traffic

---

## Executive Finding

The benchmark and the UI **do not execute the same path**.

| Path | HTTP calls | OpenAI endpoints | Measured LLM phase |
|------|------------|------------------|-------------------|
| **Benchmark script** | 0 (direct Python) | `/chat/completions` only | 9.1s (sample facts, parallel) |
| **Real UI (before fix)** | **2 sequential HTTP** | `/models` then `/chat/completions` | ~40s observed |
| **Production service (verified)** | 1 POST (after fix) | `/chat/completions` × 3 | **14.6s** (parallel, production facts) |

**Root cause of “no OpenAI requests during 40s”:** The UI waited on **`GET /api/v1/ai/health` first**, which calls OpenAI **`GET /v1/models`** — not `/chat/completions`. Monitoring only `chat/completions` shows **silence during the entire health phase**. If the backend was still on **Ollama**, there would be **zero OpenAI traffic** for the full 40 seconds.

---

## 1. Browser Network Timeline (Code + Measured)

### Button: “توليد توصيات الذكاء الاصطناعي” (Waste page)

**File:** `frontend/components/waste/waste-page.tsx` → `runAi()`

#### BEFORE fix (what caused the discrepancy)

```
T+0ms     User click
          ↓
T+0ms     GET /api/v1/ai/health          ← Frontend preflight (REDUNDANT: also on page load)
          ↓                              Backend → CloudProvider.check_connectivity()
          ↓                              OpenAI: GET https://api.openai.com/v1/models
T+?ms     (wait — NO /chat/completions yet)
          ↓
T+health  POST /api/v1/organizations/{orgId}/ai-recommendations/waste/generate
          ↓                              Backend → AiRecommendationService
          ↓                              → 3× CloudProvider.chat()
          ↓                              OpenAI: POST /v1/chat/completions (×3)
T+done    Response → setRecommendations()
```

**Measured health (live server 2026-07-16):** `GET /ai/health` = **1,028 ms**  
When network is slow, health can exceed **10–30s** (backend timeout up to 120s).

#### AFTER fix

- Page load still calls `GET /ai/health` once (on mount).
- **Click no longer repeats health** — goes directly to `POST .../waste/generate`.

Same endpoint mapping for Risk page (`risk-page.tsx` → `POST .../risk/generate`).

### Frontend API mapping (confirmed)

| Step | Function | HTTP |
|------|----------|------|
| Health (mount + old click) | `getAiHealth()` | `GET /api/v1/ai/health` |
| Generate waste | `generateWasteAi()` | `POST /api/v1/organizations/{orgId}/ai-recommendations/waste/generate` |
| Generate risk | `generateRiskAi()` | `POST /api/v1/organizations/{orgId}/ai-recommendations/risk/generate` |

**No other AI endpoint is called from these buttons.** No background worker. No queue.

---

## 2. Backend Execution Timeline (Production POST)

Trace instrumentation: `app/ai/execution_trace.py` + `app/ai/telemetry.py`

### Waste generate — live production service (2026-07-16)

```
Stage                          Evidence
─────────────────────────────────────────────────────────────
API POST received              POST /ai-recommendations/waste/generate
trace_started                  domain=waste
facts_loaded                   load_facts_contract(metadata)
settings_resolved              parallel=True provider=cloud
llm_tasks_completed            count=3 (parallel ThreadPoolExecutor)
validation_mapping_completed   validate_task_results + mappers
persistence_completed          DB write recommendations + ai_insights
service_completed
```

**Wall time:** **14,621 ms**  
**OpenAI `/chat/completions` calls:** **3** (parallel)

| Task | Provider | Model | Endpoint | Latency |
|------|----------|-------|----------|---------|
| executive_summary | cloud | gpt-4o-mini | .../chat/completions | 5,338 ms |
| risk_analysis | cloud | gpt-4o-mini | .../chat/completions | 9,452 ms |
| recommendations | cloud | gpt-4o-mini | .../chat/completions | 14,583 ms |

Parallel wall ≈ **max(14,583)** ≈ 14.6s ✓

---

## 3. AI Provider Timeline

Every `CloudProvider.chat()` now logs:

```
AI request completed provider=cloud model=gpt-4o-mini endpoint=.../chat/completions task=<task> latency_ms=...
```

Startup log confirms routing:

```
AI configuration loaded: AI_PROVIDER=cloud CLOUD_AI_MODEL=gpt-4o-mini ... parallel_tasks=True
```

**Factory path:** `get_ai_provider()` → `create_ai_provider(settings.ai)` → `CloudProvider`  
**No Ollama** when `AI_PROVIDER=cloud`.

### Fixed Ollama bypass

`get_ollama_client()` previously did `return OllamaClient(settings.ai)` when cloud was active — **now raises** if `AI_PROVIDER != ollama`.

---

## 4. OpenAI Request Timeline — One UI Click

### Scenario A: Cloud active, OLD frontend (2 HTTP requests)

| Order | When | OpenAI endpoint | Visible if monitoring chat/completions only? |
|-------|------|-----------------|---------------------------------------------|
| 1 | Health preflight | `GET /v1/models` | **NO** |
| 2 | Generate task 1–3 | `POST /v1/chat/completions` × 3 | YES (after health completes) |

**Gap with no chat/completions:** entire health request duration.

### Scenario B: Ollama still active (stale server / wrong env)

| Order | When | Destination |
|-------|------|-------------|
| 1 | Health | `GET localhost:11434/api/tags` |
| 2 | Generate | `POST localhost:11434/api/chat` × 3 sequential |

**OpenAI dashboard:** **zero requests** for full ~40s. Matches user observation.

### Scenario C: Cloud + parallel + fixed frontend (current)

| Order | When | OpenAI endpoint |
|-------|------|-----------------|
| 1 | (page load only) | `GET /v1/models` |
| 1 | Generate | `POST /v1/chat/completions` × 3 parallel |

Expected UI wait ≈ **14–22s** (production facts), not 40s.

---

## 5. Answers to Investigation Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Frontend calls expected endpoint? | **YES** — `POST .../ai-recommendations/waste/generate` (and risk equivalent) |
| 2 | Backend enters `CloudProvider.chat()`? | **YES** when `AI_PROVIDER=cloud` — 3 calls verified with telemetry |
| 3 | If not, where does it stop? | If Ollama: stops at `OllamaProvider.chat()` — **no OpenAI**. If cloud: health completes before chat starts |
| 4 | Another endpoint used? | **Only** `/ai/health` preflight (extra, now removed on click) |
| 5 | Hidden queue/worker? | **NO** — synchronous request/response |
| 6 | Old Ollama reachable? | **Was** via `get_ollama_client()` fallback — **fixed**. Stale process without restart still possible |
| 7 | Why no OpenAI during 40s? | Monitoring `/chat/completions` only + health uses `/models` first; **or** backend on Ollama |
| 8 | Why benchmark ≠ production? | Benchmark skips HTTP, health, auth, settings, DB; uses sample facts not production run |
| 9 | Frontend vs benchmark API? | **Different** — UI uses REST; benchmark calls pipeline directly |
| 10 | Log every invocation? | **YES** — `app/ai/telemetry.py` + execution trace stages |

---

## 6. Root Cause

**Primary:** The UI measured **end-to-end browser time** including a **redundant `GET /ai/health`** that hits OpenAI **`/models`**, while investigators watched only **`/chat/completions`**.

**Secondary:** Benchmark scripts **never simulate the frontend HTTP flow** — they call `AiTaskPipeline` directly with fixture data.

**Tertiary (if still ~40s after fix):** Backend process running **`AI_PROVIDER=ollama`** (no OpenAI at all) or **sequential** code without restart after optimization deploy.

---

## 7. Exact Fix (Applied)

| Fix | File | Effect |
|-----|------|--------|
| Remove redundant health on AI click | `waste-page.tsx`, `risk-page.tsx` | Eliminates duplicate `/ai/health` round-trip |
| Provider request telemetry | `app/ai/telemetry.py`, `cloud.py` | Every LLM call logged with provider/model/task |
| Execution stage trace | `app/ai/execution_trace.py`, `service.py` | Backend timeline in logs |
| Block Ollama DI bypass | `app/api/deps.py` | Prevents accidental Ollama when cloud configured |
| Task context for parallel | `app/ai/task_context.py`, `pipeline.py` | Correct task name in logs under parallelism |

**Operational:** Restart backend after `.env` changes. Verify startup log shows `AI_PROVIDER=cloud parallel_tasks=True`.

---

## 8. Verification Commands

```powershell
# Startup config
# Log line: AI configuration loaded: AI_PROVIDER=cloud ... parallel_tasks=True

# Health (uses /models, not chat/completions)
curl http://localhost:8000/api/v1/ai/health

# Simulate production service path
cd Khazina/backend
python scripts/trace_real_world_ai_flow.py
```

---

## References

- Latency deep-dive: `docs/REAL_WORLD_AI_LATENCY_INVESTIGATION.md`
- Pre-optimization baseline: `docs/CLOUD_AI_PERFORMANCE_ANALYSIS.md`
- Optimization report: `docs/AI_PERFORMANCE_OPTIMIZATION_REPORT.md`
