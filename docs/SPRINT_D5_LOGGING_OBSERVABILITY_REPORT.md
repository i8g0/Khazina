# Sprint D5 — Logging & Observability Report

**Date:** 2026-07-16  
**Role:** Lead Backend Engineer / System Reliability Engineer  
**Scope:** Production-quality logging and observability without architecture redesign, API contract changes, or DevOps infrastructure

---

## Executive Summary

Sprint D5 adds a lightweight observability layer that makes every financial analysis pipeline execution **traceable, structured, and diagnosable**. The implementation stores chronological **pipeline timelines** in existing metadata fields (`FinancialFile.file_metadata`, `AnalysisRun.runtime_metadata`), emits consistent **structured logs** at service boundaries, classifies errors into diagnostic categories, and improves **health reporting** for backend, database, and AI services.

No business logic, API response shapes (beyond additive optional health fields), or frontend workflows were redesigned.

**Verification:** 39 backend tests passed; TypeScript check passed.

---

## 1. Logging Architecture

### Layers

| Layer | Module | Purpose |
|-------|--------|---------|
| **Structured events** | `app/observability/structured_log.py` | Single-line `key=value` pipeline and HTTP logs |
| **Pipeline timeline** | `app/observability/pipeline.py` | Chronological stage records with timestamp, duration, status |
| **Persistence** | `app/observability/persistence.py` | Attach timelines to file/run metadata |
| **Error classification** | `app/observability/errors.py` | Map exceptions → diagnostic categories |
| **Health aggregation** | `app/observability/health.py` | Backend + DB + AI status |
| **HTTP middleware** | `app/core/middleware/request_logging.py` | Request method/path/status/duration |
| **Root logging** | `app/core/logging.py` | Stdout handler, sensitive-data filter (unchanged) |

### Log format

Existing format retained: `timestamp | LEVEL | logger | message`

Structured pipeline messages use embedded fields:

```
event=pipeline_stage | stage=waste_analysis_completed | status=completed | organization_id=... | analysis_run_id=... | duration_ms=31.5
```

### Context fields (standardized)

- `organization_id`
- `file_id`
- `snapshot_id`
- `analysis_run_id`
- `report_id`
- `stage`
- `status` (`started` / `completed` / `failed`)
- `duration_ms`
- `error_category`
- `message`

Noise reduced: health probe paths (`/health`, `/ai/health`) skipped by request middleware.

---

## 2. Timeline Implementation

### Stage catalog

| Stage | When recorded |
|-------|----------------|
| `upload_started` | Ingestion begins |
| `parsing` | Excel/CSV parse (orchestrator) |
| `validation` | Structural + W-1 template validation |
| `snapshot_created` | Silver snapshot persisted |
| `upload_completed` | File reaches `ready_for_analysis` or fails |
| `waste_analysis_started` / `waste_analysis_completed` | Waste decision execute |
| `ai_started` / `ai_completed` | AI recommendation generation |
| `simulation_started` / `simulation_completed` | Scenario execute (also copied to baseline waste run) |
| `report_generation` | Executive report build |
| `pdf_export` | PDF render or cache hit |
| `completed` | Full pipeline marked complete (after PDF) |
| `failed` | Terminal failure with `error_category` |

### Storage (no new tables)

| Entity | Field | Content |
|--------|-------|---------|
| `FinancialFile` | `file_metadata.pipeline_timeline` | Upload → snapshot stages |
| `AnalysisRun` | `runtime_metadata.pipeline_timeline` | Inherited upload stages + waste → PDF |

Each entry:

```json
{
  "stage": "waste_analysis_completed",
  "status": "completed",
  "timestamp": "2026-07-16T12:00:00+00:00",
  "duration_ms": 31.5
}
```

Failed entries add `error_category` and `message`.

### Instrumented services

1. `IngestionService.upload_and_ingest`
2. `IngestionOrchestrator.run` (parsing + validation sub-stages)
3. `DecisionService.execute_waste_analysis`
4. `AiRecommendationService.generate_waste_recommendations`
5. `ScenarioService.execute_scenario` (+ baseline run merge)
6. `ReportBuilderService.generate_report`
7. `ReportExportService.export_pdf`

---

## 3. Error Classification

Categories (`app/observability/errors.py`):

| Category | Examples |
|----------|----------|
| `validation` | `ValidationFailure`, `SnapshotAdapterError`, business validation |
| `excel_parsing` | `ParseError`, generic `IngestionError` |
| `file_upload` | Empty file, size limit violations |
| `ai` | Ollama connectivity, `AiRecommendationError`, `AIError` |
| `database` | `SQLAlchemyError` |
| `simulation` | `EngineError` in scenario path |
| `report_generation` | `ReportBuilderError` |
| `network` | `ConnectionError`, `TimeoutError`, `OSError` |
| `unknown` | Unclassified service errors |

Classification is logged in:

- Pipeline timeline failure entries
- Exception handlers (`SQLAlchemyError`, unhandled exceptions)
- Service-level `pipeline_stage` failure logs

API responses unchanged — classification is for logs and metadata only.

---

## 4. Health Improvements

### Before

- `GET /api/v1/health` → static `{ status: "ok" }` (no DB check)
- `GET /api/v1/ai/health` → Ollama probe only

### After

`GET /api/v1/health` returns additive optional components:

```json
{
  "status": "ok | degraded | unavailable",
  "backend": { "status": "ok", "message": "..." },
  "database": { "status": "ok", "message": "..." },
  "ai": { "status": "ok", "message": "..." }
}
```

- **Overall `ok`:** backend + database + AI all healthy
- **`degraded`:** database OK, AI unavailable
- **`unavailable`:** database down

Startup logs aggregate health via `check_system_health()`.

Existing `/api/v1/ai/health` endpoint unchanged (detailed Ollama probe for waste page).

---

## 5. Frontend Visibility

Without exposing stack traces or building a developer console:

| Surface | Change |
|---------|--------|
| **Dashboard** | `SystemStatusBanner` — backend, database, AI availability chips |
| **API types** | Optional `runtime_metadata.pipeline_timeline` on analysis runs; `file_metadata.pipeline_timeline` on files |
| **Helpers** | `lib/observability/pipeline-stages.ts` — Arabic stage labels for future UI use |
| **Waste page** | Existing AI health banner retained |

`getSystemHealth()` added to `khazina-api.ts` (calls existing `/health`).

---

## 6. Files Modified

### Backend — new

- `app/observability/pipeline.py`
- `app/observability/structured_log.py`
- `app/observability/errors.py`
- `app/observability/health.py`
- `app/observability/persistence.py`
- `app/core/middleware/request_logging.py`
- `tests/observability/test_observability.py`

### Backend — updated

- `app/main.py` — middleware, startup health log
- `app/core/exception_handlers.py` — classified error logging
- `app/schemas/response.py` — optional health components on `HealthData`
- `app/api/v1/health.py` — aggregated health
- `app/api/deps.py` — analysis repo for PDF timeline
- `app/ingestion/orchestrator.py` — parsing/validation timeline hooks
- `app/services/ingestion.py`
- `app/decision/service.py`
- `app/ai_recommendations/service.py`
- `app/scenario/service.py`
- `app/reports/service.py`
- `app/reports/export_service.py`
- `app/ai/client.py` — Ollama failures logged at WARNING
- `tests/ingestion/test_orchestrator.py` — W-1 compatible fixture

### Frontend — new

- `components/workflow/system-status-banner.tsx`
- `lib/observability/pipeline-stages.ts`

### Frontend — updated

- `lib/api/types.ts`
- `lib/api/khazina-api.ts`
- `components/dashboard/dashboard-page.tsx`

---

## 7. Regression Verification

| Check | Result |
|-------|--------|
| Backend pytest (observability + ingestion + decision + AI + reports) | **39 passed** |
| TypeScript (`pnpm exec tsc --noEmit`) | **Passed** |
| API contracts | Unchanged (health fields additive only) |
| Business logic | Unchanged |

---

## 8. Remaining Limitations

1. **Logs are stdout-only** — no log shipping, aggregation, or retention (Phase 9).
2. **Timelines are metadata-embedded** — not queryable across org without loading runs/files.
3. **Simulation timeline on baseline run** — copied from scenario execute when `baseline_analysis_run_id` is provided; standalone simulation runs keep their own timeline.
4. **No request correlation ID in API responses** — internal logs only.
5. **PDF cache hits** record `duration_ms=0` with `message=cache_hit`.
6. **Frontend shows system health, not full pipeline timeline UI** — timeline available via existing run/file metadata for admin tooling later.

---

## 9. Definition of Done

| Criterion | Met |
|-----------|-----|
| Every pipeline execution traceable | ✅ Timeline in file + run metadata |
| Errors classified | ✅ |
| Logs structured and consistent | ✅ |
| Health reporting reliable | ✅ Backend + DB + AI |
| No regression | ✅ 39 tests + tsc |
| Deliverable report | ✅ |

---

## Appendix — Example timeline query

After waste execute, fetch the analysis run — `runtime_metadata.pipeline_timeline` contains the full chronological history from upload through waste (and subsequent AI/report/PDF stages as executed).

Structured logs can be filtered by:

```
analysis_run_id=<uuid>
event=pipeline_stage
```
