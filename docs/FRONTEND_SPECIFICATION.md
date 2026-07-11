# Khazina — Frontend Specification

Official specification for every Khazina frontend page. **No page may be implemented without conforming to this document.**

For component behavior, see [COMPONENT_SPECIFICATION.md](COMPONENT_SPECIFICATION.md). For placeholder content, see [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md).

Cross-references: [ARCHITECTURE.md](ARCHITECTURE.md) · [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) · [API_CONTRACTS.md](API_CONTRACTS.md) · [HACKATHON_PLAN.md](HACKATHON_PLAN.md)

---

## Purpose

Define the structure, content boundaries, states, and integration contracts for every user-facing page in the Khazina platform so that human developers and AI assistants implement consistent, executive-grade UI without architectural drift.

---

## Scope

| In scope | Out of scope |
|----------|--------------|
| Page layout, sections, component composition | Backend business logic |
| Placeholder data binding rules | Database schema |
| Loading, empty, and error states | AI model implementation |
| Responsive and accessibility requirements | Authentication UI (single executive user — no login in MVP) |
| Future API and AI integration points | Real financial calculations |

**Target user:** Single executive (financial decision maker). No roles, no multi-user UI, no authentication screens in hackathon MVP.

**Implementation phase:** Page shells with placeholder data in hackathon MVP (Phase 7 scope per [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)); live API integration follows backend readiness.

---

## Design Principles

| Principle | Rule |
|-----------|------|
| Language | Arabic only — no English in UI |
| Direction | RTL only — `dir="rtl"`, `lang="ar"` |
| Typography | IBM Plex Sans Arabic exclusively |
| Identity | Black (`#111111`) + Gold (`#B8892D`) — no new brand colors |
| Tone | Enterprise, executive, minimal, professional |
| Mode | Light mode first; dark mode supported via theme tokens (future sprint) |
| Inspiration | Microsoft Fabric, Power BI, SAP Fiori, Oracle Fusion, Stripe Dashboard, Linear |
| Anti-patterns | No startup-dashboard aesthetic; no landing-page marketing layout |
| Data | Placeholder from [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md) until API connected |
| Logic | Presentation only — no business rules in components |

---

## Frontend Rules

1. Every page uses **AppLayout** unless explicitly exempted (none in MVP).
2. Every page uses **PageContainer** for content width (max 1440px).
3. Import placeholder data from a shared module — never duplicate strings.
4. Use components from [COMPONENT_SPECIFICATION.md](COMPONENT_SPECIFICATION.md) — no ad-hoc UI.
5. Respect maximum card/chart/table counts per page (defined below).
6. Implement all three states: loading, empty, error — even if placeholder-triggered in MVP.
7. No API calls until API client sprint approves integration pattern.
8. No Framer Motion beyond subtle transitions already in layout components.
9. File naming: App Router routes under `frontend/app/`; feature components under `frontend/components/`.
10. One `h1` per page — owned by HeroSection or PageHeader.

---

## General UX Principles

- **Executive scanability:** Key numbers visible without scrolling on desktop (1280px+).
- **Progressive disclosure:** Summary first, details in tables/charts below.
- **Calm density:** Large spacing (`space-y-8` between sections); no cramped grids.
- **Action hierarchy:** One primary action per section; secondary actions as ghost/outline buttons.
- **Feedback:** Loading skeletons match final layout dimensions — no layout shift.
- **Recovery:** Every error state offers retry or clear next step in Arabic.
- **Consistency:** Same section order patterns across similar pages (overview → detail → recommendations).

---

## Responsive Principles

| Breakpoint | Width | Layout rules |
|------------|-------|--------------|
| Mobile | <768px | Single column; drawer sidebar; stacked cards; tables scroll horizontally |
| Tablet | 768–1023px | Collapsible sidebar; 2-column KPI grid |
| Desktop | ≥1024px | Fixed sidebar; 4-column KPI grid; side-by-side chart rows |

Desktop-first design; all pages must function on mobile without hidden critical content.

---

## Component Philosophy

- **Shell vs. content:** Layout components (AppLayout, Sidebar, Header) are stable; page content swaps via App Router.
- **Composition over customization:** Pass slots (`actions`, `footer`, `children`) rather than prop explosion.
- **Typed props:** Every component fully typed in TypeScript at implementation time.
- **Presentational purity:** Pages orchestrate data; components render props.
- **Spec before code:** Update this document before adding new sections or components to a page.

---

## Route Map

| Page | Route (proposed) | Nav label |
|------|------------------|-----------|
| Dashboard | `/` or `/dashboard` | لوحة التحكم |
| Financial Waste Detection | `/financial-waste` | كشف الهدر |
| Risk Management | `/risk` | إدارة المخاطر |
| Business Simulation | `/simulation` | محاكاة الأعمال |
| Reports | `/reports` | التقارير |
| Data Management | `/data` | إدارة البيانات |

---

# Page 1 — Dashboard

## Purpose

Provide the executive with a single-screen overview of financial health, recent analyses, active risks, and priority recommendations.

## Business Goal

Enable the CFO/executive to assess organizational financial posture within 30 seconds of opening the application.

## Target User

Single executive user — الرئيس التنفيذي للشؤون المالية.

## Layout Hierarchy

```
AppLayout
└── PageContainer
    ├── HeroSection (executive summary)
    ├── KPI Grid (5 StatCards)
    ├── Charts Row (2 ChartCards — waste distribution + waste trend)
    ├── Section: Priority Recommendations (RecommendationCard grid — max 3)
    ├── Section: آخر التحديثات (Timeline — max 5 items)
    └── Section: Recent Analyses (DataTable — max 5 rows)
```

## Dashboard Philosophy

The Dashboard is an **Executive Overview**. Its purpose is awareness and prioritization. Detailed investigation belongs inside feature pages.

## Sections

| # | Section | Component(s) | Max items |
|---|---------|--------------|-----------|
| 1 | Hero | HeroSection | 1 |
| 2 | KPIs | StatCard | 5 cards |
| 3 | Charts | SectionHeader + ChartCard | 2 charts |
| 4 | Recommendations | SectionHeader + RecommendationCard | 3 cards |
| 5 | آخر التحديثات | SectionHeader + Timeline | 5 items |
| 6 | Recent analyses | SectionHeader + DataTable | 1 table, 5 rows |

**Maximum counts:** 5 KPI cards · 2 charts · 1 table · 3 recommendation cards · 5 timeline items.

## Executive KPIs

Use exactly five KPI cards. Each KPI includes a small department context badge where appropriate.

| # | KPI | Department badge |
|---|-----|------------------|
| 1 | إجمالي الهدر المالي المكتشف | المشتريات |
| 2 | عدد المخاطر الحرجة | العمليات |
| 3 | التوفير المتوقع | تقنية المعلومات |
| 4 | آخر توصية من الذكاء الاصطناعي | الموارد البشرية |
| 5 | حالة آخر تحليل | الامتثال |

Values and trends: [PLACEHOLDER_DATA.md — KPI Cards (Dashboard)](PLACEHOLDER_DATA.md).

## Dashboard Charts

Maximum two charts only. No additional dashboard charts.

**Chart 1 — توزيع الهدر حسب الإدارات**

Purpose: Allow executives to quickly identify which department contributes the most financial waste.

**Chart 2 — اتجاه الهدر المالي**

Purpose: Show the waste trend over time.

Chart data: [PLACEHOLDER_DATA.md — Dashboard Charts](PLACEHOLDER_DATA.md).

## آخر التحديثات

Display recent important financial events. Place this section **before** Recent Analyses.

- Component: Timeline (TimelineItem children)
- Maximum: 5 timeline items
- Data: [PLACEHOLDER_DATA.md — Timeline Events](PLACEHOLDER_DATA.md)

## Reusable Components

HeroSection, StatCard, SectionHeader, DataTable, RecommendationCard, ChartCard, ChartContainer, Timeline, TimelineItem, EmptyState, LoadingSkeleton, ErrorState.

## Placeholder Content

[PLACEHOLDER_DATA.md — KPI Cards, Dashboard Charts, Timeline Events, Recent Analyses](PLACEHOLDER_DATA.md)

## Future Backend Integration

| Endpoint (proposed) | Data |
|--------------------|------|
| `GET /api/v1/dashboard/summary` | KPI values |
| `GET /api/v1/dashboard/waste/by-department` | Chart 1 series |
| `GET /api/v1/dashboard/waste/trend` | Chart 2 series |
| `GET /api/v1/dashboard/analyses/recent` | Recent analyses table |
| `GET /api/v1/dashboard/recommendations` | Top recommendations |
| `GET /api/v1/dashboard/timeline` | Timeline events |

All responses use `ApiResponse` envelope per [API_CONTRACTS.md](API_CONTRACTS.md).

## Future AI Integration

AI-generated recommendation summaries and confidence scores displayed in RecommendationCard footer. Source: Phase 5 AI services via backend proxy — not direct Ollama calls from frontend.

## Loading State

- HeroSection: skeleton title + meta
- KPI grid: 5 StatCard skeletons
- Charts: 2 ChartCard skeletons
- Timeline: 5 TimelineItem skeletons
- Tables/cards: LoadingSkeletonGroup

## Empty State

Title: **لا توجد بيانات بعد** — Description: **ارفع ملفات مالية لبدء التحليل** — Action: link to Data Management page.

## Error State

ErrorState with retry — **تعذّر تحميل لوحة التحكم** — retry reloads all dashboard requests.

## Responsive Behavior

- KPI: 1 col mobile → 2 col tablet → 5 col desktop (wrap to 3+2 on medium desktop if needed)
- Charts: stack vertically on mobile; side-by-side on desktop
- Recommendations: 1 col mobile → 2 col desktop
- Timeline: full width all breakpoints

## Accessibility Notes

- Hero owns `h1`; sections use `h2` via SectionHeader
- KPI values include period context in hint text (not color alone)
- Chart requires text summary below (future)

## UX Notes

- No scrolling required to see 5 KPIs on 1440px desktop
- Gold used only for primary KPI icon accents and primary CTA
- No notification bell, user avatar, or settings in MVP header
- Dashboard prioritizes clarity over density — max 3 recommendation cards

## Design Notes

- Light background; white cards; soft shadows
- Period badge in Hero: **الربع الثاني 2026**

## Items That Must Never Appear

- Login/logout controls
- Multi-user selector
- English text
- Fake live API indicators
- More than 5 KPI cards
- More than 2 dashboard charts
- More than 3 dashboard recommendation cards
- Marketing hero imagery
- Social feeds or activity streams unrelated to finance

## Out of Scope

- Drill-down to detail pages from KPI click (future sprint)
- Real-time WebSocket updates
- Custom dashboard widget arrangement

---

# Page 2 — Financial Waste Detection

## Purpose

Allow the executive to upload financial data files and view detected waste categories, trends, and savings recommendations.

## Business Goal

Identify and quantify organizational financial waste with actionable recommendations.

## Target User

Single executive user reviewing procurement and operational spend.

## Layout

```
AppLayout
└── PageContainer
    ├── PageHeader
    ├── Upload Section (UploadArea)
    ├── Results Summary (4 StatCards — waste metrics)
    ├── Charts Row (2 ChartCards max)
    ├── Waste Breakdown (DataTable)
    └── Recommendations (RecommendationCard list — max 4)
```

## Sections

| # | Section | Max |
|---|---------|-----|
| 1 | Page header | 1 |
| 2 | Upload | 1 UploadArea |
| 3 | Summary KPIs | 4 StatCards |
| 4 | Charts | 2 charts |
| 5 | Breakdown table | 1 table |
| 6 | Recommendations | 4 cards |

**Maximum counts:** 4 cards · 2 charts · 1 table.

## Upload Section

- UploadArea accepting `.xlsx`, `.xls`, `.csv`
- Placeholder files listed in PLACEHOLDER_DATA after upload simulation
- No actual file parsing in frontend MVP — simulate success state with placeholder results

## Results Section

StatCards: total waste, waste percentage, top category, potential savings (from PLACEHOLDER_DATA).

## Charts

1. **Monthly waste trend** — line or bar chart (6 months)
2. **Waste by category** — horizontal bar or pie (max 5 categories)

## Recommendations

RecommendationCard grid from PLACEHOLDER_DATA — Waste Recommendations (4 items max).

## Placeholder Content

[PLACEHOLDER_DATA.md — Financial Waste Detection](PLACEHOLDER_DATA.md)

## Future Backend

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/waste/upload` | File upload |
| `GET /api/v1/waste/analysis/{id}` | Results |
| `GET /api/v1/waste/recommendations` | Recommendations |

## Future AI

AI categorization of waste patterns and natural-language recommendation descriptions via backend.

## States

| State | Behavior |
|-------|----------|
| Loading | Skeleton after upload; spinner in UploadArea overlay |
| Empty | No upload yet — EmptyState in results area |
| Error | Upload failed — Alert destructive + ErrorState |

## UX Rules

- Upload area always visible at top
- Results appear below only after upload (simulated in MVP)
- No auto-refresh; manual re-analyze button in PageHeader actions

## Responsive Behavior

- Charts stack vertically on mobile
- Table horizontal scroll on mobile

## Accessibility Notes

- Upload area keyboard accessible
- Chart summaries required when implemented

## Out of Scope

- Real Excel parsing in browser
- Batch upload progress for >10 files
- Comparison across quarters (future)

---

# Page 3 — Risk Management

## Purpose

Visualize organizational financial and operational risks with priority scoring, trends, and mitigation recommendations.

## Business Goal

Give the executive immediate visibility into top risks requiring attention.

## Target User

Single executive user.

## Layout

```
AppLayout
└── PageContainer
    ├── PageHeader
    ├── Risk Overview (3 StatCards — high/medium/low counts)
    ├── Risk Cards Grid (max 6 RiskCard items — use RecommendationCard pattern or dedicated RiskCard)
    ├── Priority Chart (1 ChartCard — risk by category)
    ├── Recommendations (max 3 RecommendationCards)
    └── Timeline (max 5 events)
```

## Sections

| # | Section | Max |
|---|---------|-----|
| 1 | Overview | 3 StatCards |
| 2 | Risk items | 6 cards |
| 3 | Category chart | 1 chart |
| 4 | Recommendations | 3 cards |
| 5 | Timeline | 5 events |

**Maximum counts:** 3 overview cards + 6 risk cards · 1 chart · 0 tables · 3 recommendation cards.

## Risk Overview

Three StatCards: مخاطر عالية، متوسطة، منخفضة — counts from PLACEHOLDER_DATA.

## Risk Cards

Display: name, description, priority badge, score (0–100), department, StatusBadge.

## Priority Visualization

Bar chart — risk scores by category (5 categories from PLACEHOLDER_DATA).

## Recommendations

From PLACEHOLDER_DATA — Risk Recommendations (3 items).

## Timeline

Timeline component — 5 most recent events from PLACEHOLDER_DATA.

## Placeholder Content

[PLACEHOLDER_DATA.md — Risk Management](PLACEHOLDER_DATA.md)

## Future Backend

`GET /api/v1/risks`, `GET /api/v1/risks/timeline`, `GET /api/v1/risks/recommendations`

## Future AI

AI risk scoring explanations in card footer; confidence percentage display.

## States

| State | Behavior |
|-------|----------|
| Loading | Skeleton cards + chart |
| Empty | **لا توجد مخاطر** — EmptyState |
| Error | ErrorState with retry |

## Responsive Behavior

- Risk cards: 1 col mobile → 2 col tablet → 3 col desktop
- Timeline full width

## Accessibility Notes

- Risk score not conveyed by color alone — numeric score visible
- Priority badge includes text label

## Out of Scope

- Risk creation/editing UI
- Risk assignment to users (no multi-user)
- Monte Carlo simulation

---

# Page 4 — Business Simulation

## Purpose

Build and compare what-if business scenarios with forecast visualizations.

## Business Goal

Support executive decision-making through scenario comparison without committing to changes.

## Target User

Single executive user.

## Layout

```
AppLayout
└── PageContainer
    ├── PageHeader (action: "سيناريو جديد" — disabled in MVP placeholder)
    ├── Scenario Builder (selection cards — max 3 scenarios)
    ├── Forecast Cards (3 StatCards for active scenario)
    ├── Simulation Chart (1 ChartCard — baseline vs projected)
    ├── Comparison Cards (3 metric comparison rows)
    └── Results Summary (Alert info or SectionHeader + text)
```

## Sections

| # | Section | Max |
|---|---------|-----|
| 1 | Scenario selector | 3 scenario cards |
| 2 | Forecast KPIs | 3 StatCards |
| 3 | Simulation chart | 1 chart |
| 4 | Comparison | 3 comparison cards |
| 5 | Results | 1 summary block |

**Maximum counts:** 3 scenario + 3 forecast + 3 comparison cards · 1 chart · 0 tables.

## Scenario Builder

Selectable cards from PLACEHOLDER_DATA scenarios; one active at a time; visual active state (gold border).

## Forecast Cards

Baseline, projected, delta for active scenario.

## Simulation Charts

Grouped bar or line — baseline vs projected by quarter (3 quarters from PLACEHOLDER_DATA).

## Comparison Cards

Side-by-side current vs simulated metrics.

## Placeholder Content

[PLACEHOLDER_DATA.md — Business Simulation](PLACEHOLDER_DATA.md)

## Future Backend

`GET /api/v1/simulations`, `POST /api/v1/simulations`, `GET /api/v1/simulations/{id}/forecast`

## Future AI

AI-assisted scenario parameter suggestions (future — not in page MVP).

## States

| State | Behavior |
|-------|----------|
| Loading | Skeleton on scenario + chart |
| Empty | **لا توجد سيناريوهات** — EmptyState |
| Error | ErrorState |

## Responsive Behavior

- Scenario cards horizontal scroll on mobile
- Chart full width

## Accessibility Notes

- Active scenario indicated by border + `aria-selected`
- Delta values include direction text (+/-)

## Out of Scope

- Editable scenario parameters form (future sprint)
- Running live simulation engine in frontend
- Export simulation results (see Reports page)

---

# Page 5 — Reports

## Purpose

List, filter, preview, and export generated financial reports.

## Business Goal

Provide centralized access to all analysis outputs for executive review and board preparation.

## Target User

Single executive user.

## Layout

```
AppLayout
└── PageContainer
    ├── PageHeader (export action placeholder — disabled in MVP)
    ├── FilterBar (type, department, period)
    ├── Report List (preview cards — max 5 visible)
    └── Empty/Error states as needed
```

## Sections

| # | Section | Max |
|---|---------|-----|
| 1 | Filters | 1 FilterBar (3 filters) |
| 2 | Report list | 5 preview cards |

**Maximum counts:** 5 cards · 0 charts · 0 tables (cards replace table for MVP).

## Report List

Each preview card shows: title, type badge, department, date, StatusBadge, action "معاينة" (opens Modal with placeholder preview text).

## Filters

From PLACEHOLDER_DATA — Report Filters.

## Export Buttons

Secondary buttons in PageHeader: **تصدير PDF** · **تصدير Excel** — disabled with Tooltip "قريباً" in MVP.

## Placeholder Reports

[PLACEHOLDER_DATA.md — Reports](PLACEHOLDER_DATA.md) — 5 reports.

## Future Backend

`GET /api/v1/reports`, `GET /api/v1/reports/{id}`, `GET /api/v1/reports/{id}/export?format=pdf`

## Future AI

AI-generated executive summary section inside report preview (Phase 8+).

## States

| State | Behavior |
|-------|----------|
| Loading | 5 card skeletons |
| Empty | **لا توجد تقارير** |
| Error | ErrorState |

## Responsive Behavior

- Cards: 1 col mobile → 2 col desktop
- FilterBar wraps on mobile

## Accessibility Notes

- Filter controls labeled in Arabic
- Preview modal with proper title

## Out of Scope

- Full PDF renderer in browser
- Scheduled report generation UI
- Email delivery configuration

---

# Page 6 — Data Management

## Purpose

Manage uploaded financial data files, view import history, and monitor validation status.

## Business Goal

Give the executive transparency into what data powers Khazina analyses.

## Target User

Single executive user.

## Layout

```
AppLayout
└── PageContainer
    ├── PageHeader
    ├── Upload Section (UploadArea)
    ├── Uploaded Files (DataTable — max 5 rows)
    ├── Import History (DataTable — max 4 rows)
    └── Validation Summary (4 StatCards or Alert cards)
```

## Sections

| # | Section | Max |
|---|---------|-----|
| 1 | Upload | 1 UploadArea |
| 2 | Files table | 1 table, 5 rows |
| 3 | Import history | 1 table, 4 rows |
| 4 | Validation | 4 validation cards |

**Maximum counts:** 4 validation cards · 0 charts · 2 tables.

## Uploaded Files

Columns: اسم الملف، القسم، تاريخ الرفع، الحجم، الحالة (StatusBadge).

## Import History

Columns: التاريخ، الملف، السجلات، الحالة.

## Validation Cards

Four checks from PLACEHOLDER_DATA Validation Summary.

## Placeholder Content

[PLACEHOLDER_DATA.md — Data Management](PLACEHOLDER_DATA.md)

## Future Backend

`GET /api/v1/files`, `POST /api/v1/files/upload`, `GET /api/v1/files/{id}/validation`

## Future AI

AI data quality suggestions (future — optional footer in validation section).

## States

| State | Behavior |
|-------|----------|
| Loading | Table skeletons |
| Empty | **لا توجد ملفات** — EmptyState with upload CTA |
| Error | ErrorState; failed file row shows StatusBadge "فشل" |

## Responsive Behavior

- Tables scroll horizontally on mobile
- Validation cards: 2x2 grid mobile → 4 col desktop

## Accessibility Notes

- File status not color-only — StatusBadge text
- Upload success announced via Alert

## Out of Scope

- File deletion confirmation flow (future)
- Data preview/viewer
- Column mapping UI for imports

---

## Global Page Checklist

Before marking any page implementation complete, verify:

- [ ] Conforms to section layout in this document
- [ ] Respects maximum card/chart/table counts
- [ ] Uses components from COMPONENT_SPECIFICATION only
- [ ] Placeholder data from PLACEHOLDER_DATA only
- [ ] Loading, empty, and error states implemented
- [ ] Arabic only · RTL · IBM Plex Sans Arabic
- [ ] Responsive on mobile, tablet, desktop
- [ ] No business logic · no API calls · no AI calls
- [ ] No items listed in "Must Never Appear" sections
- [ ] AppLayout + PageContainer used

---

## Related Documents

- [COMPONENT_SPECIFICATION.md](COMPONENT_SPECIFICATION.md)
- [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API_CONTRACTS.md](API_CONTRACTS.md)
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase 7 Frontend Features
- [HACKATHON_PLAN.md](HACKATHON_PLAN.md) — MVP scope reductions
