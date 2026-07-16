# Database Integrity Review

**Date:** 2026-07-16  
**Phase:** 1 — Investigation ONLY  
**Database:** PostgreSQL via SQLAlchemy + Alembic

---

## Migration State (Verified)

| Check | Result |
|-------|--------|
| Alembic head | `f9c2d7a31b44` |
| Dev machine current | `f9c2d7a31b44 (head)` ✅ |
| Risk 500 on unmigrated DB | **Expected** — missing `lifecycle_status`, `risk_events` |

**Ops requirement:** Demo machine MUST run `alembic upgrade head` before hackathon.

---

## Schema Integrity

### Foreign Key Relationships (Critical Path)

```
organizations
    └── financial_files (organization_id)
            └── snapshots (file_id)
                    └── analysis_runs (snapshot_id)
                            ├── waste_analysis_results
                            ├── risk_analysis_results → risks
                            ├── ai_recommendation_runs → ai_recommendation_items
                            └── reports → report_sections
                    └── simulation_runs (may link analysis_run_id)
```

**Migrations define FK constraints** — orphan rows at DB level blocked on normal paths.

---

## Integrity Risks Found

### DB-01: Duplicate reports (KHZ-026)

| Table | Issue | Root cause |
|-------|-------|------------|
| `reports` | Multiple rows per `analysis_run_id` | No UNIQUE constraint on `(organization_id, analysis_run_id, profile)` |

**Symptom:** Export/list picks wrong report; stale content.

### DB-02: Orphan risks (transaction boundary)

| Scenario | Risk |
|----------|------|
| Risk run marked completed; Gold persist fails | `analysis_runs` completed but empty/partial `risks` |

**Mitigation in code:** Should be single transaction — verify in Phase 2 audit of `risk_service.py`.

### DB-03: Stale recommendations after re-run

| Scenario | Behavior |
|----------|----------|
| New waste run | Old `ai_recommendation_items` remain keyed to old `analysis_run_id` |
| Frontend | Must query by current `wasteRunId` only |

**Status:** Correct if frontend uses current run ID ✅ (Sprint 1). Stale rows exist in DB but are not read.

### DB-04: Stale risk/simulation runs after re-upload

| Scenario | Behavior |
|----------|----------|
| Re-upload clears artifact IDs | Old DB rows persist |
| Frontend | Must not query without valid run ID |

**Gap:** Risk page shows cached React state when ID null (KHZ-011) — **UI integrity**, not DB corruption.

### DB-05: Invalid FK on manual operations

| Path | Status |
|------|--------|
| API validation | Pydantic + service checks on normal paths ✅ |
| KHZ-035 manual risk register | May skip category_code FK | ⚠️ Low demo impact |

### DB-06: Cross-org data access (KHZ-008)

| Endpoint | DB row exists | Org check | Result |
|----------|---------------|-----------|--------|
| `GET /risks/{id}` | Yes | Missing | **200 with wrong org data** |

**Security integrity failure** — not orphan rows but unauthorized reads.

---

## Audit Queries (Phase 2 Verification)

Run after full LAW workflow on test org:

```sql
-- Orphan analysis runs (no snapshot)
SELECT id FROM analysis_runs WHERE snapshot_id IS NULL;

-- Duplicate reports per run
SELECT organization_id, analysis_run_id, COUNT(*)
FROM reports
GROUP BY organization_id, analysis_run_id
HAVING COUNT(*) > 1;

-- Risks without matching analysis run
SELECT r.id FROM risks r
LEFT JOIN analysis_runs ar ON r.analysis_run_id = ar.id
WHERE ar.id IS NULL;

-- AI items pointing to non-existent runs
SELECT i.id FROM ai_recommendation_items i
LEFT JOIN ai_recommendation_runs run ON i.recommendation_run_id = run.id
WHERE run.id IS NULL;
```

Expected on clean workflow: **all queries return zero rows** (except duplicate reports if KHZ-026 reproduced).

---

## Persistence vs Database Truth

| Layer | Source of truth | Drift scenario |
|-------|-----------------|----------------|
| Analysis results | PostgreSQL | None if correct run ID |
| Artifact pointers | localStorage | Cleared on upload; may reference deleted runs if DB wiped |
| React UI state | Memory | Stale until re-fetch (KHZ-011) |

**Enterprise rule:** DB is truth; localStorage is cache. Phase 2 should add DB hydration fallback when cache empty.

---

## Caching

| Cache | Location | Invalidation |
|-------|----------|--------------|
| Org lookups | React context | KHZ-018 — not refreshed after mutations |
| AI responses | DB persisted | Per run ID |
| PDF | Generated on demand | No cache |

No Redis/application cache layer found — DB-direct reads.

---

## Re-upload Reset Correctness

| Entity | Cleared in localStorage | Old DB rows | UI reads |
|--------|-------------------------|-------------|----------|
| fileId | Replaced with new | Old file remains | New file ✅ |
| wasteRunId | Cleared then set | Old run remains | New run if executed ✅ |
| riskRunId | Cleared on upload | Old run remains | **Stale UI if not cleared** ❌ |
| lastReportId | Cleared on upload | Old reports remain | New if regenerated ⚠️ |

**Partial re-run (waste only):** Does not clear `riskRunId` / `simulationRunId` — cross-domain stale pointers possible.

---

## Recommendations (Phase 2)

1. Add idempotency constraint or upsert for reports
2. Risk page: reset UI when `riskRunId === null`
3. On any new analysis run in domain X, clear downstream artifact IDs (risk, sim, reports)
4. Optional: `GET /workflow/state?file_id=` backend endpoint returning latest run IDs per domain
5. Pre-demo SQL integrity check script

**Phase 1 complete. No code modified.**
