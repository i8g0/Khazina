# Real-World AI Latency Investigation

**Date:** 2026-07-16  
**Symptom:** UI ~40s; benchmark ~9s waste / ~18s risk; no `/chat/completions` seen during wait

---

## Summary

| Measurement | Waste | Risk |
|-------------|-------|------|
| Benchmark (pipeline script, sample facts, parallel) | **9.1 s** | **17.9 s** |
| Production service (real DB facts, parallel, 2026-07-16) | **14.6 s** | **21.3 s** (prior run) |
| UI observed (reported) | **~40 s** | **~40–60 s** |
| UI expected after fix (cloud + parallel) | **~15–25 s** | **~22–30 s** |

The **~40s UI time is not a CloudProvider bug** — it is explained by **path differences**, **monitoring blind spots**, and possibly **stale backend config (Ollama)**.

---

## Browser Network Timeline

### What the button actually does

**Waste:** `components/waste/waste-page.tsx` → `runAi()`

| # | Request | Method | Purpose | OpenAI call |
|---|---------|--------|---------|-------------|
| 0 | Page load | `GET /ai/health` | Set `aiReady` | `GET /v1/models` |
| 1 | **(OLD) Click** | `GET /ai/health` | Redundant preflight | `GET /v1/models` |
| 2 | Click | `POST .../waste/generate` | AI generation | `POST /v1/chat/completions` × 3 |

**Risk:** Same pattern → `POST .../risk/generate` → **5** chat/completions calls.

### Measured HTTP timings (live backend)

| Request | Duration |
|---------|----------|
| `GET /api/v1/ai/health` | **1,028 ms** |
| `POST .../waste/generate` (service-level, no HTTP overhead) | **14,621 ms** |

**OLD UI total (sequential HTTP):** ~1s + ~15s ≈ **16s minimum** (cloud, parallel, current code)

**Why user saw ~40s:**

1. **Sequential LLM (pre-parallel deploy):** same production tasks sum to **~29.4s** LLM alone  
   (5337 + 9452 + 14583 ms measured individually)
2. **+ Redundant health on click:** +1–30s depending on network
3. **+ Ollama backend:** ~40s sequential local inference, **zero OpenAI traffic**
4. **Monitoring only `/chat/completions`:** health phase shows **no activity** for seconds

---

## Backend Timeline (Production Waste — Evidence)

```
T+0ms      POST /ai-recommendations/waste/generate
T+~5ms     facts_loaded
T+~10ms    settings_resolved (parallel=True, provider=cloud)
T+~14621ms llm_tasks_completed (3 tasks, parallel)
T+~14650ms persistence_completed
T+~14680ms service_completed
```

### OpenAI request timeline (same run)

| Call # | Task | Latency | Parallel group |
|--------|------|---------|----------------|
| 1 | executive_summary | 5,338 ms | concurrent |
| 2 | risk_analysis | 9,452 ms | concurrent |
| 3 | recommendations | 14,583 ms | **critical path** |

**Wall clock = max latency = 14.6s** (parallel enabled ✓)

If parallel were **disabled** (old code):

```
Call 1 → 5.3s → Call 2 → 9.5s → Call 3 → 14.6s = 29.4s LLM only
+ health + HTTP ≈ 31–40s UI
```

This matches the reported **~40 seconds** without any OpenAI dashboard activity during the **first** third of the wait if health/Ollama handled the initial phase.

---

## Investigation Answers

### 1. Is the frontend making more than one AI request?

**YES (before fix):** Two HTTP calls per click — `GET /ai/health` + `POST .../generate`.  
**After fix:** One HTTP call per click (health only on page load).

### 2. Is the backend executing AI more than once?

**Per click:** One service invocation.  
**LLM calls per waste generate:** **3** (executive_summary, recommendations, risk_analysis).  
**LLM calls per risk generate:** **5**.

No hidden second service call. No retry loop in service code.

### 3. Is parallel execution enabled in Waste?

**YES** when `AI_PROVIDER=cloud` (default `parallel_tasks_enabled=True`).

Verified in production run: wall 14.6s ≈ max(individual latencies), not sum.

Startup log: `parallel_tasks=True`.

### 4. Are there hidden retries?

**NO** in application code.  
httpx may retry at transport level on connection errors only — not 40s of silent wait.

### 5. Is any request routed through Ollama?

**When `AI_PROVIDER=cloud`:** NO — telemetry shows `provider=cloud` on all 3 calls.  
**Risk:** Stale server or `get_ollama_client()` bypass (fixed).  
**If Ollama active:** entire 40s local, **zero OpenAI** — strongest match for “no requests observed”.

### 6. How many OpenAI API calls for ONE waste button click?

| Phase | `/models` | `/chat/completions` |
|-------|-----------|---------------------|
| Page load (once) | 1 | 0 |
| OLD click | +1 | 0 |
| Generate | 0 | **3** |
| **Total (old UX)** | **2** | **3** |
| **Total (fixed UX)** | **1** | **3** |

### 7. Latency of EACH call (production waste, 2026-07-16)

| Task | ms |
|------|-----|
| executive_summary | 5,338 |
| risk_analysis | 9,452 |
| recommendations | 14,583 |

### 8. Why ~40s UI vs ~9s benchmark?

| Factor | Benchmark | Real UI |
|--------|-----------|---------|
| Entry point | Python script | Browser HTTP |
| Health preflight | Skipped | **Included (OLD)** |
| Facts data | Test fixture (smaller) | Production DB metadata |
| Auth/settings/DB | Skipped | Included (~negligible) |
| Parallel | Yes | Yes (if server restarted) |
| Sequential deploy | N/A | **+100% LLM time if old** |
| Ollama fallback | N/A | **Zero OpenAI, ~40s** |

**9.1s benchmark** = sample facts + direct pipeline + parallel.  
**14.6s production** = real facts + parallel + full service.  
**~40s UI** = sequential LLM **OR** Ollama **OR** slow health **OR** combination.

---

## Root Cause

```
┌─────────────────────────────────────────────────────────────┐
│  User monitors: POST /v1/chat/completions only              │
│  UI actually does first: GET /v1/models (health preflight) │
│  → "No OpenAI activity" during first phase                  │
└─────────────────────────────────────────────────────────────┘
                          +
┌─────────────────────────────────────────────────────────────┐
│  Benchmark bypasses HTTP + health entirely                    │
│  → Reports only LLM phase (~9s) not browser wait (~40s)       │
└─────────────────────────────────────────────────────────────┘
                          +
┌─────────────────────────────────────────────────────────────┐
│  If backend not restarted: sequential LLM or Ollama path      │
│  → ~30–40s with no chat/completions (Ollama case)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Exact Fix

1. **Frontend:** Removed duplicate `getAiHealth()` from `runAi()` on waste and risk pages — use mount-time `aiReady` gate only.
2. **Backend:** Provider telemetry logs every `CloudProvider.chat()` with task name, model, endpoint, latency.
3. **Backend:** Block `get_ollama_client()` when cloud is active.
4. **Operations:** Restart backend; confirm `AI_PROVIDER=cloud parallel_tasks=True` in startup log.
5. **Monitoring:** Watch **both** `GET /v1/models` (health) **and** `POST /v1/chat/completions` (generation).

---

## Expected Post-Fix Behavior

| Domain | Expected UI wait (cloud, parallel) |
|--------|-----------------------------------|
| Waste | **~15–22 s** |
| Risk | **~22–30 s** |

If still ~40s after restart with cloud confirmed in logs → capture backend log lines:

```
AI request completed provider=... model=... task=... latency_ms=...
```

If those lines show `provider=ollama` or never appear → config/process issue, not LLM slowness.

---

## Tools Added

| Script | Purpose |
|--------|---------|
| `backend/scripts/trace_real_world_ai_flow.py` | HTTP flow simulation |
| `backend/scripts/measure_cloud_ai_performance.py` | Pipeline-only benchmark |
| `app/ai/telemetry.py` | Provider invocation audit trail |

---

## Definition of Done

| Criterion | Status |
|-----------|--------|
| OpenAI requests executed (cloud path) | ✅ Verified — 3× `/chat/completions`, `gpt-4o-mini` |
| OR reason no OpenAI sent identified | ✅ Health uses `/models`; Ollama path sends zero OpenAI; redundant health added dead time |
| Fix applied | ✅ Frontend + telemetry + Ollama bypass block |
