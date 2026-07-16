# Critical Risk Request Validation — Investigation Report

**Date:** 2026-07-16  
**Severity:** Release-blocking  
**Status:** **RESOLVED**  
**Error:** `Provide either source_snapshot_id or snapshot_version, not both.`

---

## 1. Executive Summary

Risk Analysis failed after upload because the frontend sent **both** snapshot identifier fields in the execute request. The API contract (shared with Waste and Simulation) requires **exactly one**.

**Root cause:** Sprint 9.6 `risk-page.tsx` included both `source_snapshot_id` and `snapshot_version` while the established waste flow sends only `source_snapshot_id`.

**Fix:** Remove `snapshot_version` from the risk execute request body — one-line frontend change, no API contract change.

---

## 2. Root Cause

### Request flow

```
Upload → beginNewFinancialDataset({ fileId, snapshotId, snapshotVersion })
       → sessionStorage holds ALL three identifiers
       → Risk "Run Analysis" builds body with BOTH snapshot fields
       → DecisionService.execute_risk_analysis() rejects at validation
```

### Offending code (before fix)

`frontend/components/risk/risk-page.tsx`:

```typescript
{
  title: "تحليل المخاطر المالية",
  source_file_id: artifacts.fileId,
  source_snapshot_id: artifacts.snapshotId,      // ← set after upload
  snapshot_version: artifacts.snapshotVersion,   // ← also set after upload
}
```

After upload, **both** values are always populated in demo artifacts, triggering backend validation:

```python
# backend/app/decision/service.py (execute_risk_analysis)
if snapshot_version is not None and source_snapshot_id is not None:
    raise BusinessValidationError(
        "Provide either source_snapshot_id or snapshot_version, not both"
    )
```

### Why it was missed

- Waste page (`waste-page.tsx`) already sends **only** `source_snapshot_id` — correct pattern.
- Simulation page uses `if snapshotId … else snapshot_version` — mutually exclusive.
- Risk page was added in Sprint 9.6 with both fields copied from artifact state without matching the mutual-exclusion contract.

This is a **frontend request builder bug**, not an auth or migration issue.

---

## 3. API Contract Confirmation

### Schema (`backend/app/schemas/risk_analysis.py`)

```python
class RiskAnalysisExecuteRequest(SchemaBase):
    title: str
    source_file_id: UUID
    source_snapshot_id: UUID | None = None
    snapshot_version: int | None = Field(None, ge=1)
    reporting_period_id: UUID | None = None
```

### Validation rule (`DecisionService`)

| Field sent | Valid |
|------------|-------|
| `source_snapshot_id` only | ✓ |
| `snapshot_version` only | ✓ |
| Both | ✗ |
| Neither | ✗ (must resolve snapshot) |

### Architecture choice

When upload returns a snapshot UUID (always in the demo flow), **`source_snapshot_id` is the correct identifier** — same as Waste (`decision.py` / `waste-page.tsx`) and aligned with ADR-010 snapshot provenance (resolve by primary key, not version number).

`snapshot_version` is for callers that know the file and version but not the snapshot UUID.

**No API contract change required.**

---

## 4. Files Modified

| File | Change |
|------|--------|
| `frontend/components/risk/risk-page.tsx` | Removed `snapshot_version` from `executeRiskAnalysis` body |

**Not modified:** backend schemas, `DecisionService`, `khazina-api.ts` (types remain optional for both — caller must send one).

---

## 5. Fix Applied

```typescript
// After fix — matches waste-page pattern
{
  title: "تحليل المخاطر المالية",
  source_file_id: artifacts.fileId,
  source_snapshot_id: artifacts.snapshotId,
}
```

---

## 6. Validation After Fix

### Automated

| Check | Result |
|-------|--------|
| `tests/decision/test_risk_decision_service.py` | Pass |
| `tests/services/test_risk_analysis_service.py` | Pass |
| `tests/api/test_risk_analysis_api.py` | Pass |
| Frontend `tsc --noEmit` | Pass |

### Expected manual workflow

| Stage | Expected |
|-------|----------|
| Upload | 201 — artifacts store `snapshotId` + `snapshotVersion` |
| Waste | 201 — uses `source_snapshot_id` only ✓ |
| Risk | 201 — uses `source_snapshot_id` only ✓ (fixed) |
| Risk AI | 200 — requires completed risk run |
| Simulation | 201 — uses `source_snapshot_id` only ✓ |
| Reports | 201 — from run ID |

---

## 7. Regression Notes

- **Waste:** unchanged — already correct.
- **Simulation:** unchanged — if/else logic already exclusive.
- **API contract:** unchanged — validation rule preserved.
- **Session artifacts:** `snapshotVersion` still stored for display/workflow; simply not sent on risk execute when `snapshotId` is available.

---

## 8. Conclusion

| Item | Status |
|------|--------|
| Root cause identified | ✓ Frontend sent both snapshot fields |
| Fix applied | ✓ Single-field request (`source_snapshot_id`) |
| API contract preserved | ✓ |
| Unrelated code unchanged | ✓ |

**Risk Analysis execute request now conforms to the platform snapshot resolution contract.**
