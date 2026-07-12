# Khazina — Business Domain Discovery

Official architectural reference derived from the frozen Phase 2 frontend. This document establishes the business model Khazina represents before Sprint 3.1 (Database Schema Design).

**Status:** Approved pending Technical Lead sign-off on review revisions (2026-07-12)

**Source of truth:** Frozen Phase 2 frontend (`frontend/`) and `frontend/lib/placeholder-data.ts`

---

## 1. Executive Summary

Khazina is an **Enterprise Financial Decision Intelligence Platform** for executive financial oversight within an organizational context (**مجموعة النخبة القابضة**). The frozen Phase 2 frontend defines a six-page Arabic RTL application that supports: executive overview, financial data ingestion, waste detection, risk management, business simulation, and report access.

The frontend is the **authoritative business specification**. All data is currently served from `frontend/lib/placeholder-data.ts` with **no API integration**. Business logic lives implicitly in placeholder structures and page-level UI state (idle/loading/ready), not in a backend.

The current MVP frontend presents a **single executive user experience** (CFO-level). This reflects the scope of the frozen UI, **not** a long-term backend constraint. Future multi-user support remains architecturally possible.

The application **operates within an organization context** but does **not** expose organization management workflows. This distinction is documented in Section 4.1.

Six primary business domains exist, mapped one-to-one to navigation and routes. Several cross-cutting concepts (AI recommendations, departmental context, analysis activity) appear across domains but are not standalone pages. Domains **not present** in the frontend include authentication, user management, organization management, settings, notifications, and vendor master-data management.

This document is the foundation for Sprint 3.1 (Database Schema Design). The backend must adapt to what the frontend already expresses — not reinterpret it.

---

## 2. Documentation Review

### 2.1 Governance & Standards (reviewed)

| Document | Relevant findings |
|---|---|
| **AI_PROJECT_PROFILE.md** | Phase 2 frozen; Phase 3 is Database. Single executive user in MVP scope. Monorepo structure. Foundation-first philosophy. |
| **PROJECT_ROADMAP.md** | Phase 3: SQLAlchemy models, Alembic migrations, schema aligned with domain requirements. Phase 4: Auth. Phase 5: AI. |
| **ARCHITECTURE.md** | Layered stack: Browser → Next.js → REST `/api/v1` → FastAPI → PostgreSQL → Ollama. **Stale:** "Current State (Phase 1 Complete)" still describes a placeholder home page only — contradicts Phase 2 completion. |
| **FRONTEND_SPECIFICATION.md** | Comprehensive page specs, proposed API endpoints, loading/empty/error states, single-user MVP, Arabic-only. **Partially stale** vs implementation (routes, layout width, Data Management layout, hero component). |
| **API_CONTRACTS.md** | `ApiResponse` envelope standard; pagination conventions defined for future list endpoints. Only live endpoint today: `GET /api/v1/health`. |
| **HACKATHON_PLAN.md** | Four-day MVP strategy; Day 1 includes database foundation alongside frontend. |
| **progress.md** | Phase 2 complete (Sprints 2.1–2.8). Phase 3 in progress. Maintenance entries for pnpm and encoding fixes. |
| **GLOSSARY.md** | Standard terminology; no domain-specific business glossary yet. |
| **ADR 004 (Docker)** | Compose stack: postgres, backend, frontend, ollama. Development-only. |
| **CONTRIBUTING.md / AI_GUIDELINES.md** | UTF-8 without BOM, minimal changes, sprint-scoped work. |

### 2.2 Documentation vs Frontend Alignment

Documentation correctly describes the **intended** product vision and technical stack. Several documents were written before or during Phase 2 and **lag behind the frozen frontend** in specifics (routes, page structure, data repository repositioning, density pass). The frontend and `placeholder-data.ts` are more current than `ARCHITECTURE.md`'s frontend section and parts of `FRONTEND_SPECIFICATION.md`.

---

## 3. Frontend Review

### 3.1 Application Shell

| Element | Implementation |
|---|---|
| Layout | `AppLayout` — sticky executive sidebar, header with page title + reporting period |
| Navigation | 6 items via `dashboardNavItems` / `navRouteMap` |
| Branding | `DashboardBrand` (sidebar), Khazina logo in hero sections |
| Language | Arabic RTL throughout |
| Data source | `lib/placeholder-data.ts` exclusively — **zero API calls** |
| User model | MVP assumes a single executive user experience; no login, no roles, no user profile UI. Named owners on risk items are display attributes only. |

### 3.2 Routes & Pages

| Route | Page component | Nav label |
|---|---|---|
| `/` | `DashboardPage` | لوحة التحكم |
| `/financial-waste` | `WastePage` | كشف الهدر |
| `/risk-management` | `RiskPage` | إدارة المخاطر |
| `/business-simulation` | `SimulationPage` | محاكاة الأعمال |
| `/reports` | `ReportsPage` | التقارير |
| `/data-management` | `DataManagementPage` | إدارة البيانات |

### 3.3 Shared UI Patterns

- **Hero:** `DashboardHero` on Dashboard; `PageHero` (with logo + quarter badge) on all other pages
- **KPI cards:** `DashboardStatCard` with optional `dense` variant
- **Section headers:** `DashboardSectionHeader`
- **Tables:** Custom executive tables + generic `DataTable`
- **Charts:** Recharts via `ChartContainer` in domain-specific chart components
- **Recommendations:** Domain-specific cards sharing a common visual pattern
- **Upload:** `UploadArea` (prominent on Waste page) and `UploadDataPanel` (compact on Data Management)
- **States:** Local React state simulates idle → loading → ready workflows with timed delays

### 3.4 Placeholder Data Inventory

`placeholder-data.ts` defines **69 exported constructs** including:

- Organization context (`organization`)
- Dashboard aggregates (KPIs, charts, recommendations, timeline, recent analyses)
- Waste analysis (categories, vendors, recommendations, department filters, upload file list)
- Risk register (items, matrix, mitigation plans, recommendations, severity/department charts)
- Simulation (scenarios, forecasts, assumptions, impact breakdown, comparison metrics, action items)
- Reports (catalog, filters, export formats)
- Data repository (uploaded files, import history, validation checks, summary KPIs)

### 3.5 Key Frontend Workflows (as implemented)

**Waste Detection:** idle → user uploads file → loading (1.4s) → ready (full results). Re-analysis available. Department filter on breakdown tables (partially functional — see gaps).

**Business Simulation:** select scenario → view read-only assumptions → run simulation → loading → results (forecasts, comparison, chart, impact table, recommendations, action panel). Changing scenario resets to idle.

**Data Management:** repository-first view (files, import history, validation). Compact upload at bottom. Upload triggers loading state then success alert.

**Reports:** initial loading skeleton → filterable report cards + history table + export panel.

**Risk Management:** static presentation — no state machine; all data visible immediately.

**Dashboard:** static aggregation — no loading/empty/error states implemented despite spec requirements.

---

## 4. Identified Business Domains

The following domains **actually exist** in the frozen frontend. Each maps to a primary page unless noted as cross-cutting.

| # | Domain | Primary page | Exists? |
|---|---|---|---|
| 1 | Executive Dashboard & Overview | `/` | Yes |
| 2 | Financial Data Repository | `/data-management` | Yes |
| 3 | Financial Waste Detection & Analysis | `/financial-waste` | Yes |
| 4 | Enterprise Risk Management | `/risk-management` | Yes |
| 5 | Business Scenario Simulation | `/business-simulation` | Yes |
| 6 | Executive Reporting | `/reports` | Yes |
| — | AI-Assisted Recommendations | Cross-cutting (Dashboard, Waste, Risk, Simulation) | Yes (UI only) |
| — | Executive Activity Timeline | Dashboard section only | Yes |
| — | Departmental Context | Cross-cutting attribute (not a page) | Yes (as reference data) |

**Domains explicitly absent from the frontend:** Authentication & Authorization, User Management, Organization Management, Settings/Configuration, Notifications Center, Vendor/Supplier Master Data Management, Audit Log (beyond import history).

### 4.1 Organization Context vs Organization Management

These are distinct concepts and must not be conflated when interpreting the frozen frontend.

| Concept | Definition in Khazina |
|---|---|
| **Organization Context** | The scope within which all financial data, analyses, risks, simulations, and reports are interpreted. The frozen frontend assumes a **single organization context** (مجموعة النخبة القابضة). Organization name and reporting period appear globally across pages. |
| **Organization Management** | Workflows for creating, configuring, switching, or administering organizations. **Not represented** in the current frontend. |

**Clarifications:**

- The current frontend assumes a single organization context.
- The project does **not** currently expose organization management workflows.
- This absence should **not** be interpreted as a permanent architectural limitation.

### 4.2 MVP User Scope

The frozen frontend delivers a single executive user experience. There is no authentication UI, no user profile, and no role management. Risk items display named owners (e.g., مدير المشتريات) as **presentation attributes**, not as evidence of a user-management domain.

This is an **MVP assumption based on the current frontend**. It is **not** a long-term backend constraint. Multi-user support remains architecturally possible and is expected to be addressed in later phases.

---

## 5. Domain Analysis

### 5.1 Executive Dashboard & Overview

**Business purpose:** Give the CFO a single-screen view of organizational financial health, active risks, savings potential, AI recommendations, and recent activity — enabling assessment within seconds of opening the app.

**Responsibilities:**

- Aggregate KPIs from waste, risk, simulation, and analysis domains
- Display waste distribution and trend charts
- Surface top-priority AI recommendations (max 3)
- Show recent executive timeline events (alerts, analyses, reviews, reports)
- List recent analyses with type, source file, date, and status

**Primary user interactions:** Read-only scanning; no drill-down links to detail pages implemented.

**Related pages:** `/` only.

**Related workflows:** Consumes outputs from all other domains; does not produce data.

**Cross-domain interaction:** Read-only consumer of waste metrics, risk counts, savings estimates, AI recommendations, analysis runs, and timeline events.

---

### 5.2 Financial Data Repository

**Business purpose:** Serve as the institutional **financial data repository** — transparency into what data powers Khazina analyses, including file status, import outcomes, and data quality.

**Responsibilities:**

- Track uploaded financial files (name, department, date, size, processing status)
- Maintain import history (date, file, record count, success/failure)
- Report data validation/quality metrics (field completeness, budget alignment, date format, duplicate records)
- Accept new file uploads (secondary, compact upload section)
- Provide repository-level KPIs (file count, total records, import success rate, data quality score)

**Primary user interactions:** View file inventory and import log; upload new files; observe validation summary.

**Related pages:** `/data-management`.

**Related workflows:** Upload → processing (simulated) → repository updated → success alert.

**Cross-domain interaction:** Uploaded files (`Procurement_Q2.xlsx`, `Budget_Q2_2026.xlsx`, etc.) are referenced as `sourceFile` in analyses, reports, and waste detection. This domain **owns the canonical file inventory** that other domains consume.

---

### 5.3 Financial Waste Detection & Analysis

**Business purpose:** Identify, quantify, and categorize financial waste in organizational spending, with actionable savings recommendations.

**Responsibilities:**

- Accept financial file uploads for waste analysis (Excel/CSV)
- Run analysis (simulated) producing waste KPIs, category breakdown, vendor deviations, department distribution
- Display waste trend over time
- Surface AI findings (high-priority subset of recommendations)
- Present savings opportunities with estimated amounts and confidence
- Support department-based filtering of breakdown data

**Primary user interactions:** Upload or drag-and-drop file → wait for analysis → review results → re-run analysis → filter by department.

**Related pages:** `/financial-waste`.

**Related workflows:** Three-state machine: **idle** (upload prompt + guidance) → **loading** (spinner overlay) → **ready** (full results). Independent upload path from Data Management page.

**Cross-domain interaction:** Produces waste metrics consumed by Dashboard KPIs and charts. Recommendations overlap with Dashboard recommendation IDs (`rec-w01` through `rec-w04`). Source files link to Data Repository files. Analysis appears in Dashboard "Recent Analyses" as type "هدر مالي".

---

### 5.4 Enterprise Risk Management

**Business purpose:** Monitor, classify, and plan mitigation for operational and financial risks across departments.

**Responsibilities:**

- Maintain active risk register (name, description, priority, score, department, status, owner, last updated)
- Visualize risk distribution by department and severity
- Display priority matrix (likelihood × impact)
- Present AI-generated risk mitigation recommendations
- Track mitigation plans (title, related risk, status, owner, target date)

**Primary user interactions:** Read-only review of risks, matrix, recommendations, and mitigation timeline. No create/edit/delete risk UI.

**Related pages:** `/risk-management`.

**Related workflows:** Static presentation — no upload or run trigger. Mitigation plans shown as a timeline.

**Cross-domain interaction:** Risk KPIs feed Dashboard ("عدد المخاطر الحرجة"). Timeline events reference risk analyses. Reports include "تقييم المخاطر الربعي". Recent analyses include type "مخاطر". Recommendations are domain-specific (`rec-r01`–`rec-r03`) but share visual pattern with other domains.

---

### 5.5 Business Scenario Simulation

**Business purpose:** Allow executives to model hypothetical financial scenarios (spending cuts, supplier consolidation, market expansion) and compare baseline vs projected outcomes.

**Responsibilities:**

- Manage simulation scenarios (name, description, status: draft/completed)
- Display read-only scenario assumptions
- Execute simulation run producing forecast summary, comparison metrics, quarterly chart, departmental impact breakdown
- Generate AI recommendations based on simulation results
- Propose follow-up action items for executive review

**Primary user interactions:** Select scenario → review assumptions → run simulation → review results. "New scenario" button exists but is **disabled**.

**Related pages:** `/business-simulation`.

**Related workflows:** Three-state: **idle** (scenario selected, assumptions visible) → **loading** (simulation running) → **ready** (full results). Scenario change resets to idle.

**Cross-domain interaction:** Simulation results appear in Dashboard recent analyses (type "محاكاة"). Reports include "ملخص محاكاة تقليل الإنفاق". Comparison metrics reference supplier counts and spending figures shared conceptually with waste/risk domains.

---

### 5.6 Executive Reporting

**Business purpose:** Centralize access to generated financial and analytical reports for executive review and board preparation.

**Responsibilities:**

- Catalog reports with type, department, source file, date, status (ready/draft)
- Support filtering by report type, department, and period
- Display report preview cards with executive summary text
- Maintain report history table
- Offer export formats (PDF, Excel, PowerPoint — UI present, functionality not wired)

**Primary user interactions:** Filter reports → browse cards → view history. Export buttons visible but non-functional in placeholder phase.

**Related pages:** `/reports`.

**Related workflows:** Initial loading skeleton → filterable report grid + history table.

**Cross-domain interaction:** Reports are **outputs** of waste analysis, risk assessment, simulation, compliance review, and vendor analysis. Each report references a `sourceFile` from the Data Repository. Report types mirror analysis domain types (تحليل, مخاطر, محاكاة, مشتريات, امتثال).

---

### 5.7 Cross-Cutting: AI-Assisted Recommendations

**Business purpose:** Surface AI-generated actionable insights with priority badges and confidence scores across multiple domains.

**Responsibilities:** Present recommendation title, description, priority (عالية/متوسطة), confidence percentage, and sometimes department context or estimated savings.

**Where it appears:** Dashboard (3 cards), Waste (4 savings cards + 2 AI findings), Risk (3 cards), Simulation (3 cards). Not a standalone page.

**Note:** No AI service is connected. Recommendations are static placeholder data with shared ID namespaces per domain (`rec-w*`, `rec-r*`, `rec-s*`).

---

### 5.8 Cross-Cutting: Departmental Context

**Business purpose:** Provide organizational segmentation for filtering, badge display, and chart breakdowns.

**Departments referenced:** المشتريات, العمليات, الشؤون المالية, تقنية المعلومات, الموارد البشرية, الامتثال, الاستشارات.

**Where it appears:** KPI badges, chart axes, table columns, report filters, file metadata, risk ownership, recommendation attribution.

**Note:** Departments exist only as **string literals** in placeholder data. There is no department management UI, no department entity page, and no consistent canonical list across all domains.

---

## 6. Cross-Domain Analysis

### 6.1 Primary Business Flows

```
┌─────────────────────────────────────────────────────────────────┐
│                    FINANCIAL DATA REPOSITORY                     │
│         Upload files → Import → Validate → Store records         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ source files
           ┌───────────────┼───────────────┬──────────────┐
           ▼               ▼               ▼              ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐
    │Waste Analysis│ │Risk Monitor │ │ Simulation  │ │ Reports  │
    │(upload+run)  │ │(static view)│ │(select+run) │ │(catalog) │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────┬─────┘
           │               │               │              │
           └───────────────┴───────┬───────┴──────────────┘
                                   ▼
                    ┌──────────────────────────┐
                    │   EXECUTIVE DASHBOARD    │
                    │  KPIs · Charts · Timeline│
                    │  Recommendations · Analyses│
                    └──────────────────────────┘
```

**Flow 1 — Data ingestion:** Executive uploads financial file → Data Repository records it → import history updated → validation checks run.

**Flow 2 — Waste analysis:** Executive uploads file on Waste page (or uses existing repository file) → analysis runs → waste categories, vendor deviations, and savings opportunities produced → results visible on Waste page and aggregated on Dashboard.

**Flow 3 — Risk oversight:** Risks are monitored continuously (no trigger) → mitigation plans tracked → recommendations generated → quarterly risk report available.

**Flow 4 — Scenario planning:** Executive selects scenario → reviews assumptions → runs simulation → compares baseline vs projected → reviews impact by department → action items proposed.

**Flow 5 — Report consumption:** Reports generated from prior analyses → filtered and previewed → export (future).

### 6.2 Domain Dependencies

| Domain | Depends on | Provides to |
|---|---|---|
| Data Repository | — (source of truth for files) | All analysis domains, Reports |
| Waste Analysis | Data Repository (source files) | Dashboard, Reports, AI Recommendations |
| Risk Management | Implicitly analysis outputs | Dashboard, Reports, Timeline |
| Simulation | Implicitly baseline financial data | Dashboard, Reports, AI Recommendations |
| Reporting | Waste, Risk, Simulation, Compliance outputs | Executive review (terminal consumer) |
| Dashboard | All domains (read-only aggregation) | Executive awareness (terminal consumer) |

### 6.3 Data Ownership

| Concept | Owning domain | Referenced by |
|---|---|---|
| Uploaded files & import records | Data Repository | Waste, Reports, Recent Analyses |
| Waste categories & amounts | Waste Analysis | Dashboard charts, Reports |
| Vendor deviations | Waste Analysis | Waste page only |
| Savings opportunities | Waste Analysis | Dashboard, Waste page |
| Risk register & matrix | Risk Management | Dashboard KPIs, Reports, Timeline |
| Mitigation plans | Risk Management | Risk page only |
| Simulation scenarios & results | Simulation | Dashboard, Reports |
| Report catalog | Reporting | Reports page only |
| AI recommendations | Per-domain (no central store) | Dashboard, Waste, Risk, Simulation |
| Timeline events | Dashboard (presentation) | Dashboard only |
| Organization context & reporting period | Global context | All pages |

### 6.4 User Journey

1. Executive opens app → **Dashboard** provides immediate financial posture
2. Needs detail on waste → navigates to **كشف الهدر** → uploads file → reviews analysis
3. Checks risk exposure → **إدارة المخاطر** → reviews register, matrix, mitigation plans
4. Explores what-if → **محاكاة الأعمال** → selects scenario → runs simulation
5. Prepares for board → **التقارير** → filters and previews reports
6. Manages data sources → **إدارة البيانات** → reviews file inventory, uploads new data

---

## 7. Business Workflow Summary

| Workflow | Trigger | States | Output |
|---|---|---|---|
| File upload (repository) | User selects file on Data Management | ready → loading → ready | File recorded, alert shown |
| File upload (waste) | User selects/drops file on Waste page | idle → loading → ready | Full waste analysis results |
| Waste re-analysis | "إعادة التحليل" button | ready → loading → ready | Refreshed results (same data) |
| Simulation run | "تشغيل المحاكاة" button | idle → loading → ready | Forecast, chart, impact, recommendations |
| Scenario switch | Click different scenario card | ready → idle | Assumptions update, results cleared |
| Report filtering | Filter pill selection | — | Filtered report list |
| Risk review | Page load | — (static) | Full risk presentation |

All workflows are **frontend-simulated** with `setTimeout` delays. No persistence occurs between sessions.

---

## 8. Gap Analysis

### 8.1 Documentation vs Frontend

| Area | Documentation says | Frontend implements | Discrepancy |
|---|---|---|---|
| Frontend routes | `/risk`, `/simulation`, `/data` | `/risk-management`, `/business-simulation`, `/data-management` | Route paths differ |
| ARCHITECTURE.md current state | "Placeholder home page only" | 6 full executive pages | Doc severely outdated |
| Page width | max 1440px (`PageContainer`) | max 1760px (`executivePageContainerClassName`) | Width spec exceeded |
| Hero component | `HeroSection` / `PageHeader` | `DashboardHero` / `PageHero` with logo | Component naming/structure evolved |
| Data Management layout | Upload first, prominent | Repository-first; compact upload at bottom | Layout hierarchy inverted (Sprint 2.7 repositioning) |
| Dashboard states | Loading, empty, error required | Static only — no loading/empty/error implemented | Spec states missing |
| Waste page vendor filter | Department filter applies to tables | Vendor table ignores department filter (`filteredVendorRows` returns all rows regardless) | Logic gap in implementation |
| MVP user scope | No roles, no auth UI | Risk items have named `owner` fields (مدير المشتريات, etc.) | Placeholder implies ownership labels without user management |
| API integration | Proposed endpoints documented | Zero API calls in frontend | Expected for Phase 2; documented as future |

### 8.2 Frontend Internal Inconsistencies

| Issue | Detail |
|---|---|
| Dual upload paths | Files can be uploaded on Waste page (prominent) AND Data Management page (compact) — no coordination between them |
| Recommendation ID overlap | Dashboard uses `rec-w01`–`rec-w03`; Waste domain also uses `rec-w01`–`rec-w04` — same IDs, potentially same concepts, no single recommendation registry |
| Department list inconsistency | Waste filters: 4 departments. Risk charts: 4 departments. Reports filters: 3 departments. Dashboard badges: 5 departments including الموارد البشرية and الامتثال. No canonical department list. |
| Closed risks KPI | Risk summary shows "المخاطر المغلقة: 0" but no closed/archived risk status exists in `riskItems` — metric is structurally unsupported |
| `wasteUploadFiles` unused in page | Placeholder defines `wasteUploadFiles` array but Waste page uses inline upload, not this list |
| Simulation scenario creation | "سيناريو جديد" button rendered but permanently disabled |
| Report export | Export panel rendered with PDF/Excel/PPT options but no download behavior |
| Analysis type taxonomy | Recent analyses use types: هدر مالي, مخاطر, محاكاة, تشغيلي, موارد بشرية — not aligned with report type taxonomy (تحليل, مخاطر, محاكاة, مشتريات, امتثال) |

### 8.3 Missing Functionality (documented but not in frontend)

| Feature | Documented in | Status |
|---|---|---|
| Authentication / login | Phase 4 roadmap | Not in frontend (correct for current phase) |
| API client integration | FRONTEND_SPEC, ARCHITECTURE | Not implemented |
| Dashboard loading/empty/error states | FRONTEND_SPEC | Not implemented |
| Report preview modal | FRONTEND_SPEC | Not verified in current Reports page (cards only) |
| Settings / configuration | — | Not present (correct — not specified) |
| Notifications center | — | Not present; timeline serves partial purpose |
| Vendor master data management | — | Vendors appear only as waste analysis rows |

### 8.4 Architectural Observations (not gaps — design facts)

- **Single organization context, MVP single-user experience, single reporting period** — the frozen frontend does not expose organization management, user management, or period selection UI. These are MVP presentation assumptions, not permanent backend constraints.
- **All business logic is presentation-layer simulation** — backend has only health endpoint
- **Ollama service exists in Docker** but has no frontend or backend integration
- **Departments and owners are display attributes**, not managed entities
- **Files are the central artifact** linking repository → analyses → reports

---

## 9. Domain Boundaries

This section establishes business ownership separation before database design begins. It describes what each domain is responsible for — and what it deliberately does not own.

### 9.1 Executive Dashboard & Overview

**Owns:**

- Executive-level aggregation and presentation of cross-domain KPIs
- Waste distribution and trend visualization for executive scanning
- Top-priority recommendation surfacing (limited subset)
- Executive activity timeline presentation
- Recent analyses summary list

**Does not own:**

- Source financial file ingestion or storage
- Waste analysis execution or categorization logic
- Risk register content or mitigation planning
- Simulation scenario definition or execution
- Report generation, cataloging, or export
- Department definition or management
- User identity, roles, or organization administration

---

### 9.2 Financial Data Repository

**Owns:**

- Canonical inventory of uploaded financial files
- Import history and outcome tracking
- Data validation and quality reporting at repository level
- Repository-level summary metrics (file count, record totals, success rate, quality score)

**Does not own:**

- Waste analysis results or savings recommendations
- Risk assessments or mitigation plans
- Simulation outputs or scenario comparisons
- Report content or executive summaries
- Executive dashboard aggregation
- Vendor deviation analysis
- Department master data management

---

### 9.3 Financial Waste Detection & Analysis

**Owns:**

- Waste analysis workflow (upload, run, re-run, results presentation)
- Waste KPIs, category breakdown, and trend presentation
- Vendor deviation findings within waste analysis context
- Department-filtered waste breakdown views
- Waste-domain savings opportunities and AI findings

**Does not own:**

- Canonical file repository governance (beyond waste-page upload interaction)
- Risk monitoring or mitigation
- Simulation modeling
- Report catalog or export
- Executive dashboard aggregation logic
- Vendor master data as a standalone business capability
- Cross-domain recommendation registry

---

### 9.4 Enterprise Risk Management

**Owns:**

- Active risk register presentation
- Risk distribution and severity visualization
- Priority matrix (likelihood × impact)
- Mitigation plan tracking and timeline presentation
- Risk-domain AI recommendations

**Does not own:**

- Waste detection or savings analysis
- Financial file ingestion
- Simulation scenario modeling
- Report generation (risk reports are consumed, not authored here)
- User or role management (owner names are display attributes only)
- Executive dashboard aggregation
- Organization or department administration

---

### 9.5 Business Scenario Simulation

**Owns:**

- Scenario catalog presentation and selection
- Scenario assumption display
- Simulation execution workflow and results presentation
- Baseline vs projected comparison metrics
- Departmental impact breakdown from simulation
- Simulation-domain recommendations and proposed action items

**Does not own:**

- Underlying financial data ingestion
- Waste analysis
- Risk register maintenance
- Report catalog management
- Scenario authoring UI (not present in frozen frontend)
- Executive dashboard aggregation
- AI model execution (recommendations are presentation-only)

---

### 9.6 Executive Reporting

**Owns:**

- Report catalog browsing and filtering
- Report preview card presentation
- Report history table
- Export format selection UI (presentation only in MVP)

**Does not own:**

- Analytical processes that produce report content (waste, risk, simulation)
- Source file storage or import
- Report generation engine or scheduling
- Executive dashboard KPI aggregation
- Actual file download or export execution (not wired in MVP)

---

### 9.7 Cross-Cutting: AI-Assisted Recommendations

**Owns:**

- Presentation of AI-generated insights (title, description, priority, confidence)
- Domain-scoped recommendation display within each consuming page

**Does not own:**

- AI model inference or prompt orchestration
- Central recommendation lifecycle management
- Approval workflows for acting on recommendations
- Underlying analytical data that recommendations summarize

---

### 9.8 Cross-Cutting: Departmental Context

**Owns:**

- Department labeling for filtering, badges, charts, and attribution across domains

**Does not own:**

- Department creation, hierarchy, or administration
- Department budget ownership or approval workflows
- User-to-department assignment

---

### 9.9 Cross-Cutting: Executive Activity Timeline

**Owns:**

- Chronological presentation of executive-relevant events on the Dashboard

**Does not own:**

- Event generation from source domains
- Notification delivery or alerting infrastructure
- Audit log completeness beyond displayed events

---

## 10. Architectural Decisions Pending Technical Lead Approval

The following items require explicit Technical Lead approval before Sprint 3.1 schema design proceeds. They are recorded as **architectural decisions**, not implementation tasks. No implementation engineer should resolve these independently.

| # | Decision | Context | Requires approval on |
|---|---|---|---|
| 1 | **Financial file ingestion architecture** | The frozen frontend exposes two independent upload paths: Waste page (prominent) and Data Management (compact repository upload). | Whether these represent one unified ingestion workflow or two distinct business operations, and how they relate at the architectural level. |
| 2 | **Department reference model** | Department names appear as string literals with inconsistent lists across domains (Waste filters: 4, Risk charts: 4, Reports filters: 3, Dashboard badges: 5). | Whether departments are a governed reference set shared across all domains, or remain free-text attributes on individual records. |
| 3 | **Recommendation ownership model** | AI recommendations use domain-scoped ID namespaces (`rec-w*`, `rec-r*`, `rec-s*`) with overlap between Dashboard and Waste domains. | Whether recommendations are architecturally centralized (with domain/type attribution) or remain domain-specific collections. |
| 4 | **Risk owner attribution model** | Risk items display named owners (e.g., مدير المشتريات) without a user-management domain in the frontend. | How risk ownership is represented architecturally — as display labels, abstract role references, or deferred until Phase 4 identity management. |
| 5 | **Analysis output vs report artifact boundary** | Recent analyses (Dashboard) and report catalog entries (Reports page) represent similar analytical outputs with overlapping metadata. | Whether these are one business concept at different lifecycle stages or distinct architectural domains. |
| 6 | **Vendor concept scope** | Vendor names appear only as rows in waste analysis vendor deviation tables. | Whether vendor is scoped exclusively to waste analysis findings or is a shared reference concept for future cross-domain use. |
| 7 | **Simulation scenario lifecycle** | Scenarios have status (مسودة/مكتمل) but no create/edit UI; "سيناريو جديد" is disabled. | What scenario lifecycle states the architecture must support given the frozen frontend's read-only scenario selection model. |
| 8 | **Reporting period scope** | A single global constant (`الربع الثاني 2026`) is used across all pages with no period selection UI. | Whether the architecture supports a single active reporting period only, or must accommodate multiple periods from the outset. |
| 9 | **Waste upload vs repository registration boundary** | Files uploaded on the Waste page are not coordinated with the Data Management repository inventory in the frontend. | Whether waste-page uploads are architecturally coupled to repository registration or treated as independent operations. |
| 10 | **Documentation authority during Phase 3** | `ARCHITECTURE.md` and `FRONTEND_SPECIFICATION.md` lag behind the frozen frontend in several areas. | Whether stale documentation is refreshed before schema design, or the frozen frontend remains the sole authority with documentation updated later. |

---

**Document status:** Business Domain Discovery complete. Review revisions applied. Awaiting Technical Lead approval before Sprint 3.1 (Database Schema Design).

**Related documents:** [ARCHITECTURE.md](ARCHITECTURE.md) · [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) · [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) · [progress.md](progress.md)
