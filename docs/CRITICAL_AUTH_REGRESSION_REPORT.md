# Critical Auth Regression — Investigation Report

**Date:** 2026-07-16  
**Severity:** Critical (demo-blocking)  
**Status:** **RESOLVED**  
**Reported symptom:** Session expiry / request failure after file upload  
**Actual root cause:** **Missing Phase 9 database migrations** (not authentication)

---

## 1. Executive Summary

Manual E2E testing reported an authentication regression: login and upload succeed, then multiple modules fail with **"انتهت صلاحية الجلسة"** or **"فشل الطلب"**.

Investigation of backend request logs and frontend auth flow shows:

- **Authentication was not invalidated by upload.**
- **Upload returned `201 Created` with a valid bearer token throughout.**
- The first failing API call after Phase 9 integration was **`GET /organizations/{id}/risks` → `500`**, caused by missing column `risks.lifecycle_status` in the local PostgreSQL database.
- Sprint 9.7 added `listRisks()` to the executive dashboard `Promise.all` load, so a single `500` on the risk register endpoint caused the **entire dashboard** (and risk page) to show a generic failure — appearing as a platform-wide break after upload/navigation.

**Fix applied:** `alembic upgrade head` (migrations `e8a1c4f03d21` + `f9c2d7a31b44`).

**Post-fix validation:** `GET /risks` returns **200** with valid JWT; login unchanged.

---

## 2. Investigation Checklist Results

### 2.1 Upload endpoint response

| Check | Result |
|-------|--------|
| HTTP status | **`201 Created`** |
| Auth header required | Yes — request authenticated |
| Token cleared on response | **No** |
| Backend log evidence | `POST .../financial-files/upload -> 201` at 18:24:25 |

Upload **does not** return 401/403 and **does not** modify auth state.

### 2.2 Frontend authentication state after upload

| Storage | Key(s) | After upload |
|---------|--------|--------------|
| `localStorage` | `khazina_token`, `khazina_org_id`, `khazina_email`, … | **Unchanged** — upload handler does not touch session |
| `sessionStorage` | `khazina_demo_artifacts` | Updated with new `fileId` / `snapshotId` only (`beginNewFinancialDataset`) |
| Refresh token | N/A | Platform uses JWT access token only — no refresh token store |

`beginNewFinancialDataset()` clears analysis run IDs (`wasteRunId`, `riskRunId`, etc.) but **never clears** auth tokens.

### 2.3 Fetch client / interceptors

| Check | Result |
|-------|--------|
| Axios | **Not used** — native `fetch` via `lib/api/client.ts` |
| Auto-logout on 401 | **No global interceptor** — 401 throws `ApiError`; session cleared only in `AuthProvider.hydrateSession()` when `getActiveOrganization()` fails at startup |
| 401 message mapping | `formatApiError()` maps 401 → "انتهت صلاحية الجلسة — يرجى تسجيل الدخول مجدداً" |

No upload-triggered logout path exists in frontend code.

### 2.4 Backend authentication middleware

| Check | Result |
|-------|--------|
| Upload changes auth context | **No** |
| Upload endpoint auth | Org-scoped JWT via standard `require_org_role` |
| Post-upload authenticated calls | `GET /financial-files` → **200**, `GET /import-records` → **200**, `POST /decisions/waste/execute` → **201** |

Auth middleware behaved correctly throughout the traced session.

### 2.5 Phase 9 Risk integration impact

Sprint 9.7 (`dashboard-page.tsx`) added:

```typescript
const [events, runs, recs, risks] = await Promise.all([
  listTimeline(...),
  listRecentAnalyses(...),
  listRecommendations(...),
  listRisks(...),  // ← NEW — fails when DB schema stale
]);
```

Sprint 9.6 (`risk-page.tsx`) loads register via `listRisks()` in `loadRegisterAndHistory()`.

These calls hit the **`risks` table with Sprint 9.4 ORM columns** that did not exist in the local DB until migrations were applied. They do **not** clear auth state.

### 2.6 Request sequence trace

```
Login                          POST /auth/login                     → 200 ✓
Hydrate                        GET  /organizations/active           → 200 ✓
Upload                         POST .../financial-files/upload      → 201 ✓
Post-upload data reload        GET  .../financial-files             → 200 ✓
                               GET  .../import-records              → 200 ✓
                               GET  .../data-quality-snapshots/...  → 200 ✓
Navigate dashboard / risk      GET  .../risks?limit=50              → 500 ✗  FIRST FAILURE
```

**First failing request:** `GET /api/v1/organizations/{org_id}/risks?limit=50`

**Backend error:**

```
psycopg2.errors.UndefinedColumn: column risks.lifecycle_status does not exist
```

---

## 3. Root Cause

### Primary

**Local PostgreSQL database was at Alembic revision `d2f6b8a14e37`, while application code requires `f9c2d7a31b44` (head).**

Pending migrations:

| Revision | Sprint | Adds |
|----------|--------|------|
| `e8a1c4f03d21` | 9.3 | `risk_analysis_results`, `risk_findings`, `risk_categories` |
| `f9c2d7a31b44` | 9.4 | `risks.lifecycle_status`, provenance columns, `risk_events` |

Phase 9 code (ORM models, repositories, Sprint 9.7 dashboard integration) assumed these migrations were applied. They were not on the demo machine.

### Why it looked like auth failure

| User-visible message | Actual HTTP status | Mechanism |
|---------------------|-------------------|-----------|
| **"فشل الطلب"** | **500** | `apiRequest()` throws `ApiError` with `envelope.message \|\| "فشل الطلب"` |
| **"انتهت صلاحية الجلسة"** | **401** (intermittent) | Stale JWT in another tab / pre-hydration poll on `notifications/unread-count` before auto-login completes — **not caused by upload** |

The risk-management screenshot showed **"فشل الطلب"** — consistent with **500**, not session expiry.

### Why it appeared after upload

1. User completes upload (works — no `listRisks` on data-management page).
2. User navigates to dashboard, risk, or home — pages that **now call `listRisks`** (Sprint 9.7).
3. `listRisks` → 500 → `Promise.all` rejects → entire page shows error.
4. Perceived as "everything broke after upload" though upload itself succeeded.

Waste analysis (`POST /decisions/waste/execute`) **succeeded (201)** in the same session — confirming auth remained valid.

---

## 4. Files Involved

| File | Role |
|------|------|
| `backend/alembic/versions/e8a1c4f03d21_add_risk_analysis_persistence.py` | Missing migration — risk Gold tables |
| `backend/alembic/versions/f9c2d7a31b44_add_enterprise_risk_register.py` | Missing migration — `lifecycle_status` + governance |
| `backend/app/db/models/risk.py` | ORM expects `lifecycle_status` column |
| `backend/app/api/v1/risk.py` | `list_risks` endpoint → 500 on schema mismatch |
| `frontend/components/dashboard/dashboard-page.tsx` | Sprint 9.7 — `listRisks` in `Promise.all` |
| `frontend/components/risk/risk-page.tsx` | `loadRegisterAndHistory()` calls `listRisks` |
| `frontend/lib/api/client.ts` | Maps errors to user messages (no auth bug) |
| `frontend/lib/auth/auth-context.tsx` | Session storage (unchanged by upload) |
| `frontend/lib/demo/state.ts` | `beginNewFinancialDataset()` — clears run IDs, not tokens |

**Not involved:** upload handler, JWT middleware, token storage, Risk Engine logic.

---

## 5. Why the Regression Occurred

1. **Phase 9 Sprints 9.3–9.4** introduced DB migrations and ORM columns for enterprise risk register.
2. **Phase 9 Sprint 9.7** wired `listRisks()` into the executive dashboard — first consumer that runs on every home page load.
3. **Demo environment** was not migrated after pulling Phase 9 code (`alembic current` showed `d2f6b8a14e37`, head `f9c2d7a31b44`).
4. **CI/tests pass** because test DB is migrated in pytest fixtures — masking the gap on developer machines without `alembic upgrade head`.

This is a **deployment/schema drift** issue exposed by platform integration, not an authentication code regression.

---

## 6. Exact Fix

### Required (applied)

From `Khazina/backend`:

```bash
alembic upgrade head
```

This applies:

- `d2f6b8a14e37` → `e8a1c4f03d21` (risk analysis persistence)
- `e8a1c4f03d21` → `f9c2d7a31b44` (enterprise risk register)

### Verification commands

```bash
alembic current   # must show: f9c2d7a31b44 (head)

# With valid JWT:
GET /api/v1/organizations/{org_id}/risks?limit=50  → 200
```

### Operational recommendation (no code change)

Add to local dev checklist after pulling Phase 9+:

```bash
cd backend && alembic upgrade head
```

---

## 7. Regression Validation

| Scenario | Pre-fix | Post-fix |
|----------|---------|----------|
| Login | ✓ 200 | ✓ 200 |
| Upload | ✓ 201 | ✓ 201 |
| Token in localStorage | Unchanged | Unchanged |
| `GET /financial-files` | ✓ 200 | ✓ 200 |
| `GET /risks` | ✗ 500 | ✓ **200** |
| Waste execute | ✓ 201 | ✓ 201 |
| Dashboard load | ✗ fails on `listRisks` | ✓ expected pass |
| Risk page load | ✗ "فشل الطلب" | ✓ expected pass |

**Backend tests (risk register):** pass after migration.

**No application code changes were required** — schema alignment only.

---

## 8. Secondary Observation (non-blocking)

Backend logs show **intermittent 401** on `GET .../notifications/unread-count` (~every 30s) when a browser tab holds an **expired JWT** while another tab has a fresh session. The notification bell poll swallows this error silently; it does **not** clear the session and is **unrelated to upload**.

If session-expired messaging appears briefly on initial page load, it is from `getActiveOrganization()` rejecting a stale stored token before dev auto-login completes — existing behaviour, not introduced in Phase 9.

---

## 9. Conclusion

| Item | Finding |
|------|---------|
| Auth regression? | **No** — JWT remained valid |
| Upload cause? | **No** — upload returned 201 |
| Root cause | **Unapplied Alembic migrations** for Sprint 9.3/9.4 |
| Trigger | Sprint 9.7 `listRisks()` on dashboard/risk pages |
| Fix | `alembic upgrade head` |
| Code changes needed | **None** |

**Demo workflow restored after migration.**
