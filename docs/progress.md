# Khazina - Development Tracker

Official progress tracker for the Khazina project.

---

## Project Status

| Item           | Value                                                         |
| -------------- | ------------------------------------------------------------- |
| Project        | Khazina - Enterprise Financial Decision Intelligence Platform |
| Current Phase  | Phase 2 – Frontend Foundation                                 |
| Current Sprint | 2.6                                                           |
| Overall Status | Phase 2 in progress                                           |
| Last Updated   | 2026-07-11                                                    |

---

## Phase Progress

| Phase                         | Status             |
| ----------------------------- | ------------------ |
| Phase 1 – Foundation          | ✅ Completed (5/5) |
| Phase 2 – Frontend Foundation | 🔄 In Progress      |
| Phase 3 – Database            | ⏸ Pending          |
| Phase 4 – Authentication      | ⏸ Pending          |
| Phase 5 – AI Integration      | ⏸ Pending          |

---

## Sprint Summary

| Sprint | Phase      | Title                                | Status    | Review   | Commit              |
| ------ | ---------- | ------------------------------------ | --------- | -------- | ------------------- |
| 1.1    | Foundation | Repository & Project Bootstrap       | Completed | Approved | 3998ece             |
| 1.2    | Foundation | Development Environment Validation   | Completed | Approved | Included in 3998ece |
| 1.3    | Foundation | Core Backend Infrastructure          | Completed | Approved | 1cac03a             |
| 1.4    | Foundation | Docker & Local Development Stability | Completed | Approved | 0dc4184             |
| 1.5    | Foundation | Foundation Freeze                    | Completed | Approved | Pending             |
| 2.1    | Frontend   | Design System Foundation             | Completed | Pending  | Pending             |
| 2.2    | Frontend   | Dashboard Page                       | Completed | Pending | Pending             |
| 2.3    | Frontend   | Financial Waste Detection            | Completed | Pending | Pending             |
| 2.4    | Frontend   | Risk Management                      | Completed | Pending | Pending             |
| 2.5    | Frontend   | Business Simulation                  | Completed | Pending | Pending             |
| 2.6    | Frontend   | Reports & Data Management            | Completed | Pending | Pending             |

---

## Sprint Details

### Sprint 1.1 - Repository & Project Bootstrap

**Objective:** Prepare the repository with a clean, scalable project foundation (frontend, backend, database, Docker, and environment setup) so the team can start development.

**Delivered:**

- Next.js frontend (TypeScript, Tailwind, App Router, RTL)
- FastAPI backend (config, logging, API v1, DB connection, Alembic init)
- PostgreSQL connection infrastructure
- Docker Compose (frontend, backend, postgres, ollama)
- `.env.example` files
- Project folder structure (frontend, backend, ai, database, docker, docs, scripts)

**Deferred:**

- Business logic, models, migrations, AI services, authentication

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ✅ Approved
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: `3998ece`
- Base commit: `75f9a92` (first commit)

---

### Sprint 1.2 - Development Environment Validation

**Objective:** Validate that the Sprint 1.1 project foundation starts correctly before implementing application features.

**Delivered:**

- Local FastAPI backend startup verified
- Local Next.js frontend startup verified
- `GET /api/v1/health` returns HTTP 200
- Frontend loads in browser (HTTP 200, Khazina content)
- Docker Compose startup configuration fix (removed missing `env_file` references)

**Deferred:**

- Full Docker Compose runtime validation (Docker Desktop not installed on dev machine)
- Database connection runtime test (no PostgreSQL running locally)

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ✅ Approved
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Included in Sprint 1.1 (`3998ece`)

**Validation Results:**

| Check                     | Result    | Notes                                     |
| ------------------------- | --------- | ----------------------------------------- |
| FastAPI backend starts    | ✅ Pass   | Uvicorn on `http://127.0.0.1:8000`        |
| Next.js frontend starts   | ✅ Pass   | Dev server on `http://localhost:3000`     |
| `GET /api/v1/health`      | ✅ Pass   | HTTP 200, `{"status":"ok"}`               |
| Frontend browser load     | ✅ Pass   | HTTP 200, page renders Khazina            |
| Docker Compose (postgres) | ⏸ Blocked | Not validated on this development machine |
| Docker Compose (backend)  | ⏸ Blocked | Not validated on this development machine |
| Docker Compose (frontend) | ⏸ Blocked | Not validated on this development machine |
| Docker Compose (ollama)   | ⏸ Blocked | Not validated on this development machine |

---

### Sprint 1.3 - Core Backend Infrastructure

**Objective:** Build shared backend infrastructure (config, responses, exceptions, logging) to be reused across the application.

**Delivered:**

- Configuration layer split into domain-specific settings (`app`, `database`, `logging`)
- Standardized `ApiResponse` model with success/error helpers
- Global exception handlers (`AppError`, `HTTPException`, `RequestValidationError`, unhandled)
- Health endpoint refactored to use standard response model
- Logging constants extracted for easier extension

**Deferred:**

- Authentication, database models, migrations, business logic, AI

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ✅ Approved
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: `1cac03a`

**Validation Results:**

| Check                         | Result  | Notes                                           |
| ----------------------------- | ------- | ----------------------------------------------- |
| Backend imports               | ✅ Pass | All modules load without errors                 |
| Backend starts                | ✅ Pass | Uvicorn on `http://127.0.0.1:8001`              |
| `GET /api/v1/health`          | ✅ Pass | HTTP 200, standard `ApiResponse` format         |
| Config backward compatibility | ✅ Pass | Existing `settings.*` property access preserved |
| Alembic config import         | ✅ Pass | `settings.database_url` accessible              |

---

### Sprint 1.4 - Docker & Local Development Stability

**Objective:** Complete and stabilize the local development environment without adding business features.

**Delivered:**

- Docker Compose project name, service healthchecks, and startup ordering
- Removed redundant runtime `NEXT_PUBLIC_API_URL` from frontend service (moved to build args)
- Backend Dockerfile: non-root user, healthcheck
- Frontend Dockerfile: build-time API URL arg, healthcheck, explicit lockfile copy
- Centralized compose env defaults in `docker/.env.example` (including `LOG_LEVEL`)
- README Quick Start updated for optional Docker env file and local dev on Windows
- `backend/.env.example` clarified for local vs Docker database host

**Deferred:**

- Full Docker Compose runtime validation on this machine (Docker not installed)
- Application features, authentication, database tables

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ✅ Approved
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: `0dc4184`

**Validation Results:**

| Check                       | Result    | Notes                                             |
| --------------------------- | --------- | ------------------------------------------------- |
| Compose file encoding       | ✅ Pass   | UTF-8, readable `git diff`                        |
| Compose service definitions | ✅ Pass   | postgres, backend, frontend, ollama configured    |
| Build contexts              | ✅ Pass   | `../backend`, `../frontend` relative to `docker/` |
| Env defaults                | ✅ Pass   | `${VAR:-default}` pattern throughout compose      |
| Backend Dockerfile          | ✅ Pass   | Non-root user, layer caching, healthcheck         |
| Frontend Dockerfile         | ✅ Pass   | Multi-stage build, build arg for public env       |
| Docker Compose runtime      | ⏸ Blocked | Not validated on this development machine         |

---

### Sprint 1.5 - Foundation Freeze

**Objective:** Final review and cleanup of the Phase 1 foundation before Phase 2.

**Delivered:**

- Backend `.env.example` aligned with settings (removed unused HOST/PORT)
- Alembic `env.py` online migration engine fixed to use app settings
- Frontend site metadata centralized in `app/site.ts`
- Frontend `.env.example` simplified and documented
- Duplicate Dockerfile healthchecks removed (compose owns orchestration healthchecks)
- README linked to progress tracker
- Sprint 1.2 review status corrected in tracker

**Deferred:**

- Database models, migrations, authentication, AI, business logic (Phase 2+)
- Docker Compose runtime validation on this machine

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ✅ Approved
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: fd789b5

**Validation Results:**

| Check                     | Result    | Notes                                     |
| ------------------------- | --------- | ----------------------------------------- |
| Backend imports           | ✅ Pass   | `from app.main import app`                |
| Frontend production build | ✅ Pass   | `npm run build`                           |
| Alembic config            | ✅ Pass   | `alembic.ini` and `env.py` present        |
| Docker compose file       | ✅ Pass   | UTF-8, four services configured           |
| Docker Compose runtime    | ⏸ Blocked | Not validated on this development machine |

---

### Sprint 2.1 - Design System Foundation

**Objective:** Build the complete reusable design system (layout shells, UI primitives, tokens, and state components) for the Khazina frontend without business logic or backend integration.

**Delivered:**

- IBM Plex Sans Arabic typography and Khazina color tokens in Tailwind v4 theme
- Design tokens module (`lib/tokens.ts`) and motion utilities (`lib/motion.ts`)
- Layout components: AppLayout, SidebarShell, HeaderShell, PageContainer, ResponsiveContainer
- UI primitives: Button, Input, Textarea, SearchInput, Badge, Alert, Card, Modal, Tooltip
- State components: LoadingSpinner, LoadingSkeleton, EmptyState, ErrorState
- Domain shells: SectionHeader, StatCard, ChartCard, ChartContainer (Recharts), RecommendationCard, UploadArea, DataTable
- Responsive sidebar: fixed (desktop), collapsible (tablet), drawer (mobile)
- Dependencies added: shadcn/ui pattern (Radix + CVA), Framer Motion, Lucide React, Recharts
- Arabic RTL root layout with TooltipProvider
- Minimal foundation home page using AppLayout (no business features)

**Deferred:**

- Dashboard, financial analysis, API integration, authentication, AI features
- Business data, charts with data, feature-specific pages

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ⏸ Pending
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Pending

**Validation Results:**

| Check                     | Result  | Notes                                      |
| ------------------------- | ------- | ------------------------------------------ |
| Frontend production build | ✅ Pass | `npm run build`                            |
| TypeScript / lint         | ✅ Pass | Build includes type check and ESLint       |
| RTL / Arabic layout       | ✅ Pass | `lang="ar"`, `dir="rtl"`, IBM Plex Arabic  |
| Business logic added      | ✅ Pass | None — design system components only       |
| Backend integration       | ✅ Pass | None — no API calls                        |

---

### Sprint 2.2 - Dashboard Page

**Objective:** Implement the executive Dashboard page using the Sprint 2.1 design system and official placeholder data only.

**Delivered:**

- Dashboard route at `/` replacing the design-system placeholder home page
- Shared placeholder data module (`frontend/lib/placeholder-data.ts`) per PLACEHOLDER_DATA.md
- HeroSection with executive summary (**نظرة تنفيذية**) and period badge (**الربع الثاني 2026**)
- Five KPI StatCards with department context badges
- Two dashboard charts: **توزيع الهدر حسب الإدارات** (bar) and **اتجاه الهدر المالي** (line)
- Three priority RecommendationCards from waste recommendations (w01–w03)
- Timeline section **آخر التحديثات** (5 events)
- Recent Analyses DataTable (5 rows)
- New minimal UI components: HeroSection, Timeline, TimelineItem
- Minimal StatCard extension: optional `departmentBadge` prop for KPI department context
- UI/UX polish pass: executive sidebar (dark, official logo, nav icons), premium hero/KPI/chart/recommendation/timeline/table styling, increased whitespace
- Visual calibration pass: Stitch-aligned proportions — wider content (1720px), dominant hero/KPI typography, light executive sidebar with gold active state, stronger section hierarchy and vertical rhythm

**Deferred:**

- All other application pages, backend integration, API client, authentication, AI

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ⏸ Pending
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Pending

**Validation Results:**

| Check | Result | Notes |
| ----- | ------ | ----- |
| Frontend production build | ✅ Pass | `npm run build` |
| TypeScript / lint | ✅ Pass | Build includes type check and ESLint |
| Dashboard hierarchy | ✅ Pass | AppLayout → Hero → 5 KPIs → 2 charts → 3 recs → Timeline → table |
| Arabic / RTL only | ✅ Pass | All user-facing dashboard text in Arabic |
| Placeholder data only | ✅ Pass | Data from `lib/placeholder-data.ts`; no API calls |
| Backend / auth / AI | ✅ Pass | None implemented |
| Scope boundary | ✅ Pass | Dashboard page only; no other pages modified |
| Screenshot | ✅ Pass | `docs/screenshots/sprint-2.2-dashboard-calibrated.png` |

---

### Sprint 2.3 - Financial Waste Detection

**Objective:** Implement the Financial Waste Detection page using the Dashboard executive visual language and official placeholder data only.

**Delivered:**

- Route at `/financial-waste` with executive AppLayout shell matching Dashboard
- PageHeader (**كشف الهدر المالي**) with re-analyze action
- UploadArea with simulated upload → loading → results flow (no backend)
- Four waste summary StatCards (total waste, percentage, top category, potential savings)
- Two charts: monthly waste trend (line) and waste by category (bar)
- Department breakdown section with progress bars per department
- Filters by department on breakdown tables
- Waste breakdown table (analysis results) and vendor details table
- AI findings cards (top high-priority recommendations)
- Savings opportunity cards (4 recommendations with savings amounts)
- Empty state (idle), loading skeletons/spinner, ready results state
- Shared navigation config (`lib/app-nav.tsx`) with sidebar routing to Dashboard and Waste pages
- Extended `lib/placeholder-data.ts` with waste-specific placeholder data
- PageHeader UI component for non-dashboard pages
- Sprint 2.3 UI refinement: compact PageHeader, prominent UploadArea, helper badges, workflow steps, executive idle empty state

**Deferred:**

- Risk, simulation, reports, data pages; backend upload API; real file parsing; authentication; AI services

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ⏸ Pending
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Pending

**Validation Results:**

| Check | Result | Notes |
| ----- | ------ | ----- |
| Frontend production build | ✅ Pass | `npm run build` — `/financial-waste` route generated |
| TypeScript / lint | ✅ Pass | Build includes type check and ESLint |
| Page hierarchy | ✅ Pass | PageHeader → Upload → Summary → Charts → Dept breakdown → Tables → AI → Savings |
| Arabic / RTL only | ✅ Pass | All user-facing text in Arabic |
| Placeholder data only | ✅ Pass | Data from `lib/placeholder-data.ts`; no API calls |
| Visual consistency | ✅ Pass | Reuses Dashboard executive components and spacing |
| Scope boundary | ✅ Pass | Waste page only; no backend/auth/AI |
| Screenshot | ✅ Pass | `docs/screenshots/sprint-2.3-waste-detection-idle-refined.png` |

---

### Sprint 2.4 - Risk Management

**Objective:** Implement the Risk Management page using the Dashboard executive visual language and official placeholder data only.

**Delivered:**

- Route at `/risk-management` with executive AppLayout shell matching Dashboard and Waste pages
- PageHeader (**إدارة المخاطر**) with reporting period badge
- Four risk summary StatCards (total, critical, medium, closed)
- Two distribution charts: by department (bar) and by severity level (bar)
- Risk priority matrix visualization (likelihood × impact grid with placeholder positions)
- Active risks table via DataTable (risk, department, priority, status, owner, last updated)
- AI recommendation cards (3 placeholder recommendations)
- Mitigation plans timeline (4 placeholder plans with status, target date, owner)
- Shared navigation config updated with `risk` → `/risk-management`
- Extended `lib/placeholder-data.ts` with risk-specific placeholder data
- Sprint 2.4 UI polish: emphasized KPI cards, chart breathing room, Dashboard-aligned recommendation cards, taller mitigation cards, tighter page header, consistent section rhythm

**Deferred:**

- Simulation, reports, data pages; backend API; real risk calculations; authentication; AI services

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ⏸ Pending
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Pending

**Validation Results:**

| Check | Result | Notes |
| ----- | ------ | ----- |
| Frontend production build | ✅ Pass | `npm run build` — `/risk-management` route generated |
| TypeScript / lint | ✅ Pass | Build includes type check and ESLint |
| Page hierarchy | ✅ Pass | PageHeader → KPIs → Charts → Matrix → Table → AI → Mitigation |
| Arabic / RTL only | ✅ Pass | All user-facing text in Arabic |
| Placeholder data only | ✅ Pass | Data from `lib/placeholder-data.ts`; no API calls |
| Visual consistency | ✅ Pass | Reuses Dashboard executive components and spacing |
| Scope boundary | ✅ Pass | Risk page only; no backend/auth/AI |
| Screenshot | ✅ Pass | `docs/screenshots/sprint-2.4-risk-management.png` |

---

### Sprint 2.5 - Business Simulation

**Objective:** Implement the Business Simulation page using the Dashboard executive visual language and official placeholder data only.

**Delivered:**

- Route at `/business-simulation` with executive AppLayout shell matching Dashboard, Waste, and Risk pages
- PageHeader (**محاكاة الأعمال**) with disabled "سيناريو جديد" action and reporting period badge
- Scenario selection cards (3 scenarios) with active gold border state and `aria-selected`
- Assumptions panel (read-only placeholder parameters per scenario)
- Fake "تشغيل المحاكاة" flow with local React state (idle → loading → ready)
- Loading skeletons during simulated run
- Results summary KPIs (baseline, projected, delta) with info alert
- Comparison metric cards (3 per scenario)
- Baseline vs projected grouped bar chart by quarter
- Financial impact breakdown table via DataTable
- AI recommendation cards (3 placeholder recommendations via DashboardRecommendationCard)
- Action summary panel (3 proposed action cards)
- Shared navigation config updated with `simulation` → `/business-simulation`
- Extended `lib/placeholder-data.ts` with simulation-specific placeholder data
- Seven simulation components under `components/simulation/`

**Deferred:**

- Reports, data pages; backend simulation API; editable scenario parameters; live simulation engine; authentication; AI services

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ⏸ Pending
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Pending

**Validation Results:**

| Check | Result | Notes |
| ----- | ------ | ----- |
| Frontend production build | ✅ Pass | `npm run build` — `/business-simulation` route generated |
| TypeScript / lint | ✅ Pass | Build includes type check and ESLint |
| Page hierarchy | ✅ Pass | Header → Scenarios → Assumptions → Run → Results → Comparison → Chart → Impact → AI → Actions |
| Arabic / RTL only | ✅ Pass | All user-facing text in Arabic |
| Placeholder data only | ✅ Pass | Data from `lib/placeholder-data.ts`; no API calls |
| Visual consistency | ✅ Pass | Reuses Dashboard executive components and spacing |
| Scope boundary | ✅ Pass | Simulation page only; no backend/auth/AI |
| Screenshot | ✅ Pass | `docs/screenshots/sprint-2.5-business-simulation.png` |

---

### Sprint 2.6 - Reports & Data Management

**Objective:** Implement the final two frontend pages (Reports and Data Management) using the Dashboard executive visual language and official placeholder data only.

**Delivered:**

- Route at `/reports` with executive AppLayout shell
- Reports PageHeader, 4 summary KPIs, filter bar (type/department/period)
- 5 generated report preview cards with modal preview ("معاينة")
- Reports history DataTable
- Export panel (PDF / Excel / PowerPoint) — UI only, disabled with tooltip
- Route at `/data-management` with executive AppLayout shell
- Data Management PageHeader, UploadArea panel, uploaded files table, import history table
- Dataset summary KPIs + validation summary cards
- Empty / loading / ready states with local React state (simulated upload flow)
- Shared navigation config updated with `reports` → `/reports`, `data` → `/data-management`
- Extended `lib/placeholder-data.ts` with reports and data management placeholder data
- Four reports components and five data components

**Deferred:**

- Backend report/file APIs; real export; authentication; AI; file deletion; data preview viewer

**Review Status:**

- Cursor: ✅ Completed
- Tech Lead: ⏸ Pending
- Claude: ⏭ Not Required

**Git Information:**

- Branch: `main`
- Commit: Pending

**Validation Results:**

| Check | Result | Notes |
| ----- | ------ | ----- |
| Frontend production build | ✅ Pass | `npm run build` — `/reports` and `/data-management` routes generated |
| TypeScript / lint | ✅ Pass | Build includes type check and ESLint |
| Reports page hierarchy | ✅ Pass | Header → KPIs → Filters → Cards → History → Export |
| Data page hierarchy | ✅ Pass | Header → Upload → KPIs → Files → Import → Validation |
| Arabic / RTL only | ✅ Pass | All user-facing text in Arabic |
| Placeholder data only | ✅ Pass | Data from `lib/placeholder-data.ts`; no API calls |
| Visual consistency | ✅ Pass | Reuses Dashboard executive components and spacing |
| Scope boundary | ✅ Pass | Reports + Data pages only; Phase 2 frontend complete |
| Screenshots | ✅ Pass | `docs/screenshots/sprint-2.6-reports.png`, `docs/screenshots/sprint-2.6-data-management.png` |

---

<!-- Add new sprint rows to Sprint Summary and matching Sprint Details sections below -->
