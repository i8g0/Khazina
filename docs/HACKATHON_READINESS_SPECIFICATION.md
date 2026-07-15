# Hackathon Readiness Sprint — Specification

**Sprint class:** Integration and demonstration certification — **not a feature sprint**  
**Predecessor:** Phase 6 — Business Features — **Complete and frozen** (Sprints 6.1–6.9)  
**Status:** **DRAFT** — Awaiting Technical Lead review  
**Date:** 2026-07-15  

**Normative references (frozen — must not be modified unless integration-blocking):**

- [AI_FREEZE.md](AI_FREEZE.md) — Phase 5 AI layer freeze
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md) — ADR-009
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [ARCHITECTURE.md](ARCHITECTURE.md) — Phase 3 Backend Core freeze; Phase 4 Authentication freeze
- [API_CONTRACTS.md](API_CONTRACTS.md) — `ApiResponse` envelope, JWT contract
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — page layout, states, integration contracts
- [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md) — demo narrative alignment (مجموعة النخبة القابضة)
- [HACKATHON_PLAN.md](HACKATHON_PLAN.md) — demo checklist, smoke-test strategy, AI validation
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — hackathon scope rules
- [progress.md](progress.md) — Phase 6 completion evidence (170 tests)
- [SPRINT_6.2_SPECIFICATION.md](SPRINT_6.2_SPECIFICATION.md) through [SPRINT_6.9_SPECIFICATION.md](SPRINT_6.9_SPECIFICATION.md)

**Tracker alignment:** Backend business capabilities are operational (`progress.md` Sprints 6.1–6.9). Frontend Phase 2 pages use **placeholder data only** (`frontend/lib/placeholder-data.ts` — no API client, no `/login` route). This sprint closes the **integration gap** between frozen backend and existing frontend shells for a live hackathon demonstration.

**TL pattern expectation:** Reduce scope via integration discipline — wire existing APIs to existing pages; fix blocking bugs; prepare reproducible demo assets. Do **not** introduce Phase 7 analytics APIs, new business engines, or new product features.

---

## Terminology Mapping (Repository Authority)

| Term | Repository authority | Meaning |
|---|---|---|
| **Hackathon Readiness** | [HACKATHON_PLAN.md](HACKATHON_PLAN.md) Day 4 | Stable, reproducible end-to-end demo without manual fixes |
| **Integration sprint** | [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) §Authentication | JWT client, org-scoped API calls — deferred since Phase 2 |
| **Demo-critical path** | User E2E flow (§6) | Login → Upload → Snapshot → Decision → AI → Scenario → Report → PDF → Notifications |
| **Demo-supporting pages** | Discovery §6.1 flows | Dashboard partial wiring; Data Management full wiring |
| **Non-demo pages** | Backend gap evidence | Risk Management — no Phase 6 risk engine; remains placeholder |
| **Demo dataset** | `PLACEHOLDER_DATA.md` file-003 `Procurement_Q2.xlsx`; Sprint 6.3 adapter contract | Spreadsheet matching Waste Engine v1 input shape |
| **Connection-only change** | User rules | CORS, auth context, API client — not new business APIs |

---

## 1. Sprint Goal

Make the **existing Khazina platform fully operational** for a **complete, live, end-to-end hackathon demonstration** — without adding new business capabilities.

After this sprint:

- A presenter can execute the **canonical demo script** (§6) from a fresh environment using documented setup steps.
- The frontend **consumes real backend APIs** on all demo-critical pages with JWT authentication.
- **Placeholder data is replaced** with live API responses on demo-critical paths; non-critical sections may retain curated static content where no backend aggregation exists.
- **Backend, database, Ollama, and frontend** run together via Docker Compose (or documented local equivalent).
- A **rehearsed demo** completes without manual database edits, code changes, or undisclosed workarounds.
- **Blocking bugs** discovered during integration are fixed; non-blocking issues are logged for post-hackathon work.

This sprint does **not** add product features, analytics APIs, new engines, or architectural contracts.

---

## 2. Business Objective

### Capability unlocked

| Before Hackathon Readiness | After Hackathon Readiness |
|---|---|
| Backend delivers full Phase 6 business pipeline; frontend shows static placeholders | **Live demo** shows real ingestion, analysis, AI, reports, export, and notifications |
| Integration exists only in backend tests (170 pytest) | **Browser-based E2E** validates the executive story |
| Demo requires API tools (curl/Postman) and tribal knowledge | **Documented demo script** with org, user, file, and timing guidance |
| Hackathon checklist in `HACKATHON_PLAN.md` unchecked | **Demo checklist fully satisfied** with recorded validation |

### Executive value

| Stakeholder need | Sprint response |
|---|---|
| Convincing live demonstration | Full pipeline visible in Arabic RTL UI |
| Credibility of AI layer | Real Ollama inference in demo path (frozen `qwen3.5:2b` per `AI_FREEZE.md`) |
| Enterprise presentation quality | Loading, empty, and error states on wired pages; UX polish on demo path |
| Reproducibility | Seeded org/user, canonical `Procurement_Q2.xlsx`, scripted reset procedure |
| Phase discipline | No scope creep into analytics dashboards or new domains |

### Repository gap analysis

| Gap ID | Current state | Evidence | Sprint action |
|---|---|---|---|
| H-01 | No frontend API client | No `fetch` to `/api/v1` in `frontend/` | Build API client + auth context |
| H-02 | No login page | `FRONTEND_SPECIFICATION.md` proposes `/login`; not implemented | Implement login route + session handling |
| H-03 | All pages use `placeholder-data.ts` | 30+ frontend imports of placeholder module | Replace on demo-critical pages |
| H-04 | No CORS middleware | `backend/app/main.py` — no CORS | Add browser integration config (connection-only) |
| H-05 | No demo spreadsheet in repo | `Glob **/*.xlsx` — zero files; tests build fixtures inline | Add canonical demo file under `scripts/demo/` or `database/demo/` |
| H-06 | No demo org/user seed procedure | No `seed` scripts in repository | Document + automate demo bootstrap |
| H-07 | Dashboard APIs proposed but not implemented | `FRONTEND_SPECIFICATION.md` §Future Backend — `/dashboard/*` | Partial compose from existing endpoints; no new dashboard API |
| H-08 | Risk page has no Phase 6 engine | `BUSINESS_DOMAIN_DISCOVERY.md` Flow 3 — monitoring domain | Exclude from demo-critical path; optional static page |
| H-09 | PDF export button disabled in UI | `FRONTEND_SPECIFICATION.md` Page 5 — "قريباً" | Enable wired to `?format=pdf` (Sprint 6.9) |
| H-10 | Notification bell not in header | `FRONTEND_SPECIFICATION.md` Page 1 — deferred MVP | Add minimal notifications access for demo closure |

---

## 3. Scope

### 3.1 INCLUDED (strict)

| ID | Item | Repository basis |
|---|---|---|
| I-01 | **Backend readiness verification** — health, migrations, engine bootstrap, storage paths, Ollama connectivity | `docker/docker-compose.yml`; `progress.md` Sprint 6.9 |
| I-02 | **Frontend ↔ Backend integration** — `NEXT_PUBLIC_API_URL`, JWT Bearer, `ApiResponse` parsing | `API_CONTRACTS.md`; `frontend/.env.example` |
| I-03 | **Authentication UI** — `/login`, redirect guards, 401/403 handling | `FRONTEND_SPECIFICATION.md` §Authentication |
| I-04 | **API client layer** — typed wrappers for demo endpoints; org ID from session | `ARCHITECTURE.md` frontend rules |
| I-05 | **Replace mock data (demo-critical)** — Data Management, Waste, Simulation, Reports, Notifications | `PLACEHOLDER_DATA.md` parity targets |
| I-06 | **API integration verification** — each demo step mapped to existing endpoint | §6 endpoint table |
| I-07 | **End-to-end workflow validation** — scripted rehearsal with pass/fail record | `HACKATHON_PLAN.md` §Testing Strategy |
| I-08 | **Demo dataset preparation** — `Procurement_Q2.xlsx` matching Waste v1 adapter | Sprint 6.3 §11; `tests/decision/conftest.py` sheet shape |
| I-09 | **Demo organization preparation** — org matching placeholder identity (optional name override via Settings) | `PLACEHOLDER_DATA.md` §Organization Context |
| I-10 | **Demo account preparation** — executive user (primary demo persona) + documented credentials | `FRONTEND_SPECIFICATION.md` target user |
| I-11 | **Simulation scenario bootstrap** — three archetype scenarios aligned with placeholder (`sim-001`–`003`) | Sprint 6.5; `placeholder-data.ts` |
| I-12 | **Error handling verification** — Arabic ErrorState, retry, 401 redirect, AI timeout messaging | `FRONTEND_SPECIFICATION.md` §States |
| I-13 | **Deployment readiness checklist** — Docker Compose healthy; env templates complete | `HACKATHON_PLAN.md` §Demo Checklist |
| I-14 | **Demo script validation** — written script with timings, fallback paths | New: `docs/HACKATHON_DEMO_SCRIPT.md` |
| I-15 | **Bug fixing** — blocking defects on demo path only | `HACKATHON_PLAN.md` Day 4 |
| I-16 | **UX polish** — demo-path loading skeletons, success feedback, disable broken actions | `FRONTEND_SPECIFICATION.md` §UX |
| I-17 | **Performance smoke validation** — upload, engine, AI, PDF latency recorded | `AI_FREEZE.md` §3; `HACKATHON_PLAN.md` §AI Performance |
| I-18 | **CORS / browser connectivity** — if required for local/Docker demo | Integration infrastructure (not new API) |
| I-19 | **`progress.md` update** — sprint completion, demo validation results | Tracker rules |

### 3.2 EXCLUDED (strict)

| ID | Item | Reason |
|---|---|---|
| E-01 | **New business features** | Phase 6 frozen |
| E-02 | **New AI capabilities** | `AI_FREEZE.md` |
| E-03 | **New Business Engines** | ADR-009 |
| E-04 | **New analytics APIs** — Executive Dashboard, Repository Summary | Sprint 6.9 E-01, E-02 |
| E-05 | **New ERP / external integrations** | Out of product scope |
| E-06 | **Architecture redesign** | Freeze discipline |
| E-07 | **Major refactoring** | Integration-first; minimal diffs |
| E-08 | **SQL schema changes / migrations** | No new persistence contracts |
| E-09 | **Risk Management live integration** | No Phase 6 risk engine; CRUD-only backend insufficient for demo story |
| E-10 | **Excel/PowerPoint export** | Sprint 6.9 — PDF v1 only |
| E-11 | **Email, SMS, push notifications** | Sprint 6.7 E-05 |
| E-12 | **Full Dashboard aggregation** | No backend dashboard API; partial compose only |
| E-13 | **CI pipeline / comprehensive QA** | Phase 9 |
| E-14 | **Production hardening** — rate limiting, refresh tokens | Sprint 4.5 technical debt |
| E-15 | **New mapping contract documents** | TL pattern |
| E-16 | **Modification of frozen AI pipeline or Waste Engine internals** | Phase 5/6 freeze |
| E-17 | **Editable scenario parameter forms** | `FRONTEND_SPECIFICATION.md` Page 4 Out of Scope |
| E-18 | **Number Guard / AI response validation** | Sprint 6.4 deferred |

### 3.3 Demo-critical vs demo-supporting pages

| Page | Route | Integration level | Notes |
|---|---|---|---|
| **Login** | `/login` | **Full** — new | Entry point for demo |
| **Data Management** | `/data-management` | **Full** | Upload, files, import outcomes |
| **Financial Waste** | `/financial-waste` | **Full** | Display waste Gold + trigger decision/AI from UI |
| **Business Simulation** | `/business-simulation` | **Full** | List scenarios, execute, show Gold results |
| **Reports** | `/reports` | **Full** | List, generate, preview content, PDF download |
| **Notifications** | header panel or `/notifications` | **Full** | Unread count, list, mark read |
| **Dashboard** | `/` | **Partial** | Timeline, recent analyses, recommendations from existing APIs; KPI/charts may use composed or residual placeholder with demo label |
| **Risk Management** | `/risk-management` | **Static/placeholder** | No engine — not on demo-critical path |
| **Settings** | optional | **Optional** | Org branding if time permits; not blocking |

---

## 4. Inputs

All inputs are **existing platform artifacts**. No new business contracts.

### 4.1 Backend (frozen Phase 6)

| Capability | Primary endpoints | Sprint source |
|---|---|---|
| Authentication | `POST /api/v1/auth/login` | Phase 4 |
| Health | `GET /api/v1/health` | Phase 1 |
| Organizations | `POST/GET /api/v1/organizations` | Phase 3 |
| Users | `POST /api/v1/organizations/{id}/users` | Phase 4 |
| Financial upload | `POST .../financial-files/upload` | Sprint 6.2 |
| Financial snapshots | `GET .../financial-snapshots/{id}`, `GET .../financial-files/{id}/snapshots/latest` | Sprint 6.2 |
| Waste decision | `POST .../decisions/waste/execute` | Sprint 6.3 |
| Waste results | `GET .../waste-analysis-results`, breakdowns | Phase 3 + 6.3 Gold |
| AI recommendations | `POST .../ai-recommendations/waste/generate` | Sprint 6.4 |
| Recommendations registry | `GET .../recommendations` | Phase 3 + 6.4 |
| Simulation scenarios | `POST/GET .../simulation/scenarios` | Phase 3 + 6.5 |
| Scenario execute | `POST .../simulation/scenarios/{id}/execute` | Sprint 6.5 |
| Simulation results | `GET .../simulation/runs/{id}/...` | Phase 3 + 6.5 Gold |
| Analysis runs | `GET .../analysis-runs` | Phase 3 |
| Report generate | `POST .../reports/generate` | Sprint 6.6 |
| Report list/content | `GET .../reports`, `GET .../reports/{id}/content` | Sprint 6.6 |
| PDF export | `GET .../reports/{id}/export?format=pdf` | Sprint 6.9 |
| Notifications | `GET .../notifications`, `POST .../notifications/{id}/read` | Sprint 6.7 |
| Timeline | `GET .../timeline/events` | Phase 3 |
| Settings | `GET/PATCH .../settings` | Sprint 6.8 (optional) |

### 4.2 Frontend (Phase 2 shells)

| Input | Location | State |
|---|---|---|
| Page components | `frontend/components/*/`, `frontend/app/` | Layout-complete, placeholder-fed |
| Placeholder SSOT | `frontend/lib/placeholder-data.ts`, `PLACEHOLDER_DATA.md` | Demo narrative reference |
| Design system | `frontend/components/ui/`, `COMPONENT_SPECIFICATION.md` | Reuse — no ad-hoc UI |
| Docker build | `frontend/Dockerfile`, `NEXT_PUBLIC_API_URL` build arg | `docker/docker-compose.yml` |

### 4.3 Infrastructure

| Input | Location | Requirement |
|---|---|---|
| PostgreSQL | `docker-compose.yml` service `postgres` | Migrated schema at Alembic head |
| Ollama | `docker-compose.yml` service `ollama` | Model pulled: `qwen3.5:2b` per `AI_FREEZE.md` |
| Environment | `backend/.env.example`, `docker/.env.example` | `DATABASE_URL`, `JWT_SECRET_KEY`, `OLLAMA_MODEL`, storage roots |
| Approved AI timeout | `AI_TIMEOUT=180` | `AI_FREEZE.md` production config |

### 4.4 Demo narrative anchors (from placeholder SSOT)

| Field | Value |
|---|---|
| Organization name | مجموعة النخبة القابضة |
| Platform name | خزينة |
| Primary demo file | `Procurement_Q2.xlsx` (file-003) |
| Reporting period | الربع الثاني 2026 |
| Demo persona | Executive (الرئيس التنفيذي للشؤون المالية) |

---

## 5. Outputs

**A production-ready hackathon demonstration** — defined as:

| Output | Description |
|---|---|
| **Operational integrated platform** | Frontend pages on demo path consume live APIs |
| **Reproducible environment** | `docker compose up` (or documented local stack) reaches healthy state |
| **Demo bootstrap package** | Org, user, scenarios, and spreadsheet prepared via script or documented API sequence |
| **Validated demo script** | Step-by-step presenter guide with timings and fallbacks |
| **Recorded smoke metrics** | Upload, engine, AI, PDF latencies documented in `progress.md` |
| **Demo checklist signed** | All items in `HACKATHON_PLAN.md` §Demo Checklist checked |
| **Known gaps list** | Non-demo pages and limitations explicitly labeled for judges |

**Primary documentation deliverables:**

| Document | Purpose |
|---|---|
| `docs/HACKATHON_DEMO_SCRIPT.md` | Presenter script (new) |
| `docs/HACKATHON_READINESS_CHECKLIST.md` | Environment + E2E verification (new, optional merge into demo script) |
| `docs/progress.md` | Sprint completion and validation record |

---

## 6. End-to-End Flow

### 6.1 Canonical demo pipeline

```
Login (JWT)
    ↓
Upload Financial File (Procurement_Q2.xlsx)
    ↓
Financial Snapshot (Silver — ready_for_analysis)
    ↓
Decision Engine (Waste execute → Gold)
    ↓
AI Recommendations (Ollama — executive insights + recommendations)
    ↓
Scenario Analysis (execute scenario vs same snapshot)
    ↓
Executive Report (generate from completed run)
    ↓
PDF Export (binary download)
    ↓
Notifications (completion + failure kinds visible)
    ↓
Complete Demo
```

### 6.2 Step-by-step API mapping (normative)

| Step | UI location | API call | Success signal |
|---|---|---|---|
| 0 — Setup | — | `alembic upgrade head`; demo bootstrap | Org ID + user credentials known |
| 1 — Login | `/login` | `POST /api/v1/auth/login` | `access_token` received |
| 2 — Upload | Data Management or Waste | `POST .../financial-files/upload` (multipart) | `financial_snapshot` with `ready_for_analysis` |
| 3 — Snapshot confirm | Data Management | `GET .../financial-files/{id}/snapshots/latest` | Snapshot version matches upload response |
| 4 — Waste decision | Waste page action | `POST .../decisions/waste/execute` | `analysis_run.status = completed` |
| 5 — AI recommendations | Waste page action | `POST .../ai-recommendations/waste/generate` | `recommendation_count >= 1`; `ai_insights` populated |
| 6 — Scenario execute | Simulation page | `POST .../simulation/scenarios/{id}/execute` | `simulation_run` + `analysis_run` completed |
| 7 — Report generate | Reports page | `POST .../reports/generate` | Report with `content_representation` |
| 8 — PDF export | Reports page | `GET .../reports/{id}/export?format=pdf` | `Content-Type: application/pdf`; downloadable file |
| 9 — Notifications | Header/panel | `GET .../notifications` | Events for analysis, AI, report steps |
| 10 — Dashboard confirm | `/` (optional) | `GET .../timeline/events`, `GET .../analysis-runs` | Recent activity reflects demo steps |

### 6.3 Presenter narrative (Arabic executive story)

1. **تسجيل الدخول** — المستخدم التنفيذي يدخل إلى منصة خزينة.
2. **رفع البيانات** — رفع `Procurement_Q2.xlsx` من مستودع البيانات.
3. **التحليل المالي** — تشغيل كشف الهدر على اللقطة المالية.
4. **الذكاء الاصطناعي** — توليد التوصيات والرؤى التنفيذية.
5. **محاكاة السيناريو** — مقارنة سيناريو تقليل الإنفاق مقابل خط الأساس.
6. **التقرير التنفيذي** — إنشاء تقرير مجلس الإدارة.
7. **التصدير** — تحميل PDF جاهز للعرض.
8. **الإشعارات** — إظهار إشعارات الإنجاز للمستخدم المبادر.

### 6.4 Fallback paths (demo resilience)

| Failure | Fallback |
|---|---|
| Ollama slow/unavailable | Pre-run AI step before demo; show cached recommendations via `GET .../recommendations`; narrate AI latency per `AI_FREEZE.md` |
| AI timeout (>180s) | Use `regenerate=false` idempotent return if prior run exists |
| Upload parse failure | Pre-seed snapshot via rehearsal; use second canonical file if prepared |
| PDF export disabled in settings | PATCH settings `pdf_export_enabled=true` during bootstrap |
| Fresh DB | Run documented bootstrap script before every demo |

---

## 7. Deliverables

| # | Deliverable | Type |
|---|---|---|
| D-01 | Frontend API client + auth session module | Code |
| D-02 | `/login` page + route guards | Code |
| D-03 | CORS or equivalent browser connectivity fix | Code (config only) |
| D-04 | Data Management page — live API integration | Code |
| D-05 | Financial Waste page — live results + action triggers | Code |
| D-06 | Business Simulation page — scenario list, execute, results | Code |
| D-07 | Reports page — list, generate, preview, PDF download | Code |
| D-08 | Notifications UI (header entry + list/read) | Code |
| D-09 | Dashboard partial integration (timeline, analyses, recommendations) | Code |
| D-10 | Demo spreadsheet `Procurement_Q2.xlsx` | Asset |
| D-11 | Demo bootstrap script or documented API sequence | Script/docs |
| D-12 | `docs/HACKATHON_DEMO_SCRIPT.md` | Documentation |
| D-13 | `docs/HACKATHON_READINESS_CHECKLIST.md` (or equivalent section) | Documentation |
| D-14 | `docs/progress.md` — Hackathon Readiness sprint entry | Documentation |
| D-15 | Bug-fix commits for demo-blocking defects | Code |
| D-16 | Smoke timing record (upload, engine, AI, PDF) | Documentation in `progress.md` |

**Explicitly not delivered:** New backend business endpoints, new engines, analytics APIs, Risk page integration, Excel export, email notifications.

---

## 8. Acceptance Criteria

### Environment readiness

| ID | Criterion | Measurable target |
|---|---|---|
| AC-01 | `docker compose up` — postgres, backend, frontend, ollama reach healthy | 4/4 services healthy within 3 minutes |
| AC-02 | `GET /api/v1/health` returns success | `success: true` |
| AC-03 | Alembic at head | `alembic current` matches latest migration (`b9d4e7f16a21` or successor) |
| AC-04 | Ollama model available | `OLLAMA_MODEL` responds to test chat |
| AC-05 | Backend test suite still green | `pytest tests/ -q` — 170 tests pass (no regression) |

### Integration readiness

| ID | Criterion | Measurable target |
|---|---|---|
| AC-06 | Login page authenticates demo executive user | JWT returned; redirect to `/` |
| AC-07 | Unauthenticated access to business routes redirects to `/login` | 100% of protected app routes |
| AC-08 | API client attaches `Authorization: Bearer` on org-scoped calls | Verified in network trace |
| AC-09 | `ApiResponse` envelope parsed correctly on all wired calls | No unhandled `success: false` |
| AC-10 | 401 clears session and redirects to login | Manual + automated check |
| AC-11 | 403 shows Arabic forbidden message | Per `FRONTEND_SPECIFICATION.md` |

### End-to-end demo (measurable)

| ID | Criterion | Measurable target |
|---|---|---|
| AC-12 | Upload `Procurement_Q2.xlsx` succeeds | Snapshot status `ready_for_analysis` within 30s |
| AC-13 | Waste decision completes | `analysis_run.status = completed` within 15s |
| AC-14 | AI recommendations generated | `recommendation_count >= 1` within `AI_TIMEOUT` (180s) |
| AC-15 | Scenario execution completes | `simulation_run` persisted; analysis run completed within 20s |
| AC-16 | Executive report generated | Report row with non-empty `content_representation` within 10s |
| AC-17 | PDF export downloads valid file | `Content-Type: application/pdf`; size ≥ 1 KB; opens in viewer |
| AC-18 | Notifications list shows demo events | ≥ 3 notifications after full run (analysis, AI/report, publish) |
| AC-19 | Full demo script completes without manual DB/SQL intervention | 100% success on 2 consecutive rehearsals |
| AC-20 | Full demo completes within time budget | ≤ 15 minutes including AI step (or ≤ 8 minutes with pre-warmed AI) |
| AC-21 | Demo reset procedure documented and tested | Second demo run succeeds from reset state |

### UX and polish

| ID | Criterion | Measurable target |
|---|---|---|
| AC-22 | Demo-critical pages implement loading, empty, error states | 5/5 pages per `FRONTEND_SPECIFICATION.md` |
| AC-23 | No English text on demo path | Arabic-only UI |
| AC-24 | PDF export button enabled and functional | Replaces "قريباً" disabled state on Reports page |
| AC-25 | Risk page labeled if placeholder remains | Clear "عرض توضيحي" or nav de-emphasis — no false live indicators |

### Scope compliance

| ID | Criterion |
|---|---|
| AC-26 | No new business API endpoints introduced |
| AC-27 | No modifications to frozen `app/ai/` pipeline or Waste Engine internals |
| AC-28 | No new SQL migrations |
| AC-29 | `HACKATHON_PLAN.md` demo checklist — all items checked |
| AC-30 | `progress.md` updated with validation results and smoke timings |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **AI latency exceeds demo slot** | Live failure at step 5 | Pre-warm Ollama; pre-run AI; idempotent retry; fallback to cached recommendations |
| R-02 | **No CORS — browser blocks API** | Frontend cannot call backend | Add CORS middleware for dev/demo origins early in sprint |
| R-03 | **Demo spreadsheet missing/wrong shape** | Upload or waste execute fails | Author file from `tests/decision/conftest.py` contract; validate in rehearsal |
| R-04 | **Simulation scenarios not bootstrapped** | Step 6 blocked | Bootstrap three scenarios with Sprint 6.5 archetype labels during demo prep |
| R-05 | **Org/user bootstrap complexity** | Presenter cannot start demo | Single `scripts/demo/bootstrap.py` calling existing APIs |
| R-06 | **Docker frontend API URL mismatch** | UI calls wrong host | Verify `NEXT_PUBLIC_API_URL` build arg matches browser-reachable backend URL |
| R-07 | **JWT secret / env misconfiguration** | Login or startup fails | Fail-fast checklist from `.env.example`; document minimum env vars |
| R-08 | **Dashboard KPI gap** — no aggregation API | Dashboard looks inconsistent | Partial wiring + honest labeling; do not invent dashboard API |
| R-09 | **Scope creep into analytics** | Phase boundary violation | TL review on every new endpoint proposal |
| R-10 | **Number Guard absent** — AI numbers unverified | Demo credibility risk | Narrate as known limitation per Sprint 6.4; do not block demo |
| R-11 | **Vendor filter bug on waste page** | UI inconsistency if porting placeholder logic | Map from API data only; do not port known placeholder bug (`BUSINESS_DOMAIN_DISCOVERY.md` §5.7) |
| R-12 | **Storage paths in Docker** | Bronze/PDF write failures | Mount `data/` volumes or document ephemeral container limits |

---

## 10. Dependencies

### Hard dependencies (must be complete)

| Dependency | Status | Evidence |
|---|---|---|
| Phase 6 business backend | ✅ Complete | `progress.md` Sprints 6.1–6.9 |
| Phase 5 AI freeze | ✅ Frozen | `AI_FREEZE.md` |
| Phase 4 authentication | ✅ Frozen | `progress.md` Sprint 4.5 |
| Phase 2 frontend shells | ✅ Complete | `progress.md` Sprints 2.1–2.8 |
| Docker Compose stack | ✅ Available | `docker/docker-compose.yml` |
| Sprint 6.9 PDF export | ✅ Complete | `GET .../export?format=pdf` |

### Runtime dependencies (demo environment)

| Dependency | Requirement |
|---|---|
| PostgreSQL 16 | Running, migrated |
| Ollama | Running with `qwen3.5:2b` pulled |
| Python 3.12 backend | Healthy on port 8000 |
| Next.js frontend | Healthy on port 3000 |
| Disk storage | `BRONZE_STORAGE_ROOT`, `report_export_storage_root` writable |

### Soft dependencies (recommended)

| Dependency | Use |
|---|---|
| `HACKATHON_PLAN.md` | Team roles, Day 4 checklist |
| `AI_BENCHMARK_REPORT.md` | Latency expectations for presenter |
| `BUSINESS_DOMAIN_DISCOVERY.md` | Page/domain alignment |
| Sprint 6.10 freeze doc (when complete) | Phase 6 baseline reference |

### Parallel work constraints

| Constraint | Rule |
|---|---|
| Phase 6 frozen | Bug fixes only — no feature additions |
| AI frozen | No prompt/orchestrator changes unless demo-blocking |
| Backend Core frozen | No layer boundary changes |

---

## 11. Implementation Order

### Step 1 — Specification approval

- This document reviewed and approved (Technical Lead sign-off).
- Demo scope confirmed: §6 canonical flow only.

### Step 2 — Environment and backend verification

- `docker compose up --build`; verify 4 services healthy.
- `alembic upgrade head`; confirm storage directories exist.
- Ollama model pull and smoke chat.
- Record `pytest tests/ -q` baseline (170 pass).

### Step 3 — Integration infrastructure

- CORS (if needed for browser demo).
- Frontend API client (`ApiResponse` parsing, error mapping).
- Auth context (token storage, org ID resolution, route guards).
- `/login` page.

### Step 4 — Demo asset and bootstrap preparation

- Create `Procurement_Q2.xlsx` from adapter contract.
- Bootstrap script: organization, executive user, departments (if required), three simulation scenarios.
- Configure settings: `pdf_export_enabled=true`, notification kinds enabled.
- Document credentials in `HACKATHON_DEMO_SCRIPT.md` (dev-only; not production secrets).

### Step 5 — Page integration (demo-critical order)

1. Data Management — upload + file/snapshot list.
2. Financial Waste — decision trigger + Gold display + AI trigger.
3. Business Simulation — scenario select + execute + results.
4. Reports — list, generate, content preview, PDF download.
5. Notifications — header entry, list, mark read.
6. Dashboard — partial (timeline, analyses, recommendations).

### Step 6 — Error handling and UX polish

- Loading/empty/error states on wired pages.
- Arabic error messages; retry actions.
- Disable or label non-functional controls (Excel export, Risk live data).
- Enable PDF export button.

### Step 7 — End-to-end rehearsal and bug fixing

- Run full demo script twice.
- Fix blocking bugs only.
- Record smoke timings (upload, waste, AI, scenario, report, PDF).
- Document fallbacks.

### Step 8 — Documentation and sign-off

- Finalize `HACKATHON_DEMO_SCRIPT.md` and readiness checklist.
- Update `progress.md`.
- Complete `HACKATHON_PLAN.md` demo checklist.
- Tech Lead demo sign-off.

---

## 12. Technical Lead Recommendation

### Recommendation: **APPROVE FOR EXECUTION** *(pending TL sign-off)*

| Factor | Assessment |
|---|---|
| **Timing** | Phase 6 backend complete; frontend integration is the critical path for hackathon |
| **Scope discipline** | Integration-only — aligns with user mandate and freeze documents |
| **Demo value** | Canonical flow showcases full platform differentiation (engines + AI + reports + PDF) |
| **Risk** | AI latency and CORS are highest risks — address in Steps 2–3 |
| **Precedent** | `HACKATHON_PLAN.md` Day 4 explicitly scopes demo readiness work |
| **Phase boundary** | Correctly excludes dashboard analytics API and risk engine |

### Conditions for sprint start

1. **Phase 6 frozen** — no new business capabilities.
2. **Demo-critical path only** — Risk page may remain placeholder.
3. **No new business APIs** — connection infrastructure (CORS, client) allowed.
4. **Canonical demo file** — `Procurement_Q2.xlsx` validated before UI wiring.
5. **Ollama required** for live AI step — document fallback if hardware constrained.
6. **Two successful rehearsals** required before demo sign-off (AC-19).

### Suggested team allocation (from `HACKATHON_PLAN.md`)

| Role | Focus |
|---|---|
| Frontend | API client, login, page wiring, UX polish |
| Backend | CORS, bootstrap script, demo-blocking bug fixes only |
| Integration / Tech Lead | E2E rehearsals, demo script, checklist sign-off |
| AI | Ollama pre-warm, latency validation, fallback narration |
| Database | Migration verify, demo reset procedure |

### Post-hackathon

Remaining `PROJECT_ROADMAP.md` work continues: full Phase 7 frontend features, analytics APIs, Risk engine integration, CI/QA (Phase 9), production deployment (Phase 10). Hackathon Readiness does **not** close Phase 7 — it certifies **demonstrability** of the frozen Phase 6 backend through existing UI shells.

---

## Appendix A — Endpoint Quick Reference (Demo Path)

```
POST   /api/v1/auth/login
POST   /api/v1/organizations
POST   /api/v1/organizations/{org_id}/users
POST   /api/v1/organizations/{org_id}/financial-files/upload
GET    /api/v1/organizations/{org_id}/financial-files/{file_id}/snapshots/latest
POST   /api/v1/organizations/{org_id}/decisions/waste/execute
POST   /api/v1/organizations/{org_id}/ai-recommendations/waste/generate
GET    /api/v1/organizations/{org_id}/recommendations
POST   /api/v1/organizations/{org_id}/simulation/scenarios
POST   /api/v1/organizations/{org_id}/simulation/scenarios/{scenario_id}/execute
POST   /api/v1/organizations/{org_id}/reports/generate
GET    /api/v1/organizations/{org_id}/reports
GET    /api/v1/organizations/{org_id}/reports/{report_id}/export?format=pdf
GET    /api/v1/organizations/{org_id}/notifications
POST   /api/v1/organizations/{org_id}/notifications/{id}/read
GET    /api/v1/organizations/{org_id}/timeline/events
GET    /api/v1/organizations/{org_id}/analysis-runs
```

---

## Appendix B — Smoke Timing Targets (Record in progress.md)

| Step | Target (warm) | Target (cold) | Notes |
|---|---|---|---|
| Login | < 2s | < 2s | |
| Upload + ingest | < 30s | < 45s | File size ~2.4 MB placeholder reference |
| Waste engine | < 5s | < 15s | Deterministic — sub-second engine per benchmark |
| AI recommendations | < 60s | < 180s | `AI_TIMEOUT` hard cap |
| Scenario engine | < 5s | < 20s | |
| Report generate | < 10s | < 15s | No AI/engines |
| PDF export | < 5s | < 10s | Idempotent on repeat |
| **Full run** | **< 8 min** | **< 15 min** | With pre-warmed AI |

---

## Document Control

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Author** | Platform specification (Hackathon Readiness) |
| **Review status** | **Draft** — Awaiting Technical Lead review |
| **Implementation authorized** | No — pending approval |
| **Supersedes** | — (first Hackathon Readiness specification) |
