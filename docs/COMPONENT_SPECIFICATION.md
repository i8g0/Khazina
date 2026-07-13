# Khazina — Component Specification

Official specification for every reusable frontend component. No page should use ad-hoc UI patterns outside this document.

For page layout and section rules, see [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md). For placeholder content, see [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md).

Implementation reference (Sprint 2.1): `frontend/components/`

---

## Global Component Rules

| Rule | Requirement |
|------|-------------|
| Language | Arabic labels only in rendered output |
| Direction | RTL — use logical properties (`start`/`end`, `ms`/`me`, `ps`/`pe`) |
| Typography | IBM Plex Sans Arabic only |
| Theming | Use design tokens from `frontend/lib/tokens.ts` and `globals.css` |
| Composition | Components must be reusable, typed, and composable |
| Data | Accept data via props — never fetch inside presentational components |
| Business logic | Forbidden inside UI components |

---

## AppLayout

**Purpose:** Root application shell wrapping sidebar, header, and main content.

**Props (conceptual):**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| children | ReactNode | Yes | Main page content |
| brand | ReactNode | Yes | Sidebar brand block |
| title | ReactNode | No | Header title |
| subtitle | ReactNode | No | Header subtitle |
| headerActions | ReactNode | No | Header action slot |
| navItems | SidebarNavItem[] | No | Navigation items |
| activeItemId | string | No | Active nav item ID |
| sidebarFooter | ReactNode | No | Sidebar footer slot |

**Variants:** None — single enterprise layout.

**States:** Default; sidebar collapsed (tablet); mobile drawer open/closed.

**Responsive behavior:**

| Breakpoint | Sidebar | Header |
|------------|---------|--------|
| Desktop (lg+) | Fixed, collapsible | Full width |
| Tablet (md–lg) | Collapsible inline | Full width |
| Mobile (<md) | Drawer overlay | Hamburger trigger |

**Accessibility:** Landmark regions (`header`, `main`, `nav`); focus trap in mobile drawer; keyboard nav for sidebar items.

**Future integration:** Nav items link to App Router routes; active state driven by pathname.

**Usage:** Wrap every authenticated application page. Unauthenticated users use the `/login` route (Phase 5 integration). Phase 2 shells may omit session UI until API client integration.

**Design rules:** Light background (`bg-light`); white sidebar surface; gold accent on active nav item.

**Implementation:** `components/layout/app-layout.tsx`

---

## Sidebar

**Purpose:** Primary navigation and brand area.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| brand | ReactNode | Yes | Logo and app name |
| navItems | NavItem[] | No | Navigation entries |
| activeItemId | string | No | Currently active item |
| footer | ReactNode | No | Bottom slot (e.g., version info) |
| collapsed | boolean | No | Collapsed state (tablet/desktop) |
| mobileOpen | boolean | No | Drawer visibility (mobile) |

**Variants:** Expanded (280px) | Collapsed (88px, icons only).

**States:** Default, active item, hover, collapsed, mobile drawer.

**Responsive:** See AppLayout table.

**Accessibility:** `nav` landmark; `aria-current="page"` on active item; collapse toggle labeled in Arabic.

**Future integration:** Items map to routes defined in FRONTEND_SPECIFICATION.

**Design rules:** White surface; subtle border; gold highlight for active item; no nested menus in MVP.

**Implementation:** `components/layout/sidebar-shell.tsx`

---

## Header

**Purpose:** Page-level title bar with optional actions.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | ReactNode | No | Page title |
| subtitle | ReactNode | No | Context line (period, breadcrumb text) |
| actions | ReactNode | No | Right-side actions (RTL: start-side visually) |
| onMobileMenuClick | function | No | Opens mobile sidebar |

**Variants:** Default only.

**States:** Default; sticky on scroll.

**Responsive:** Mobile menu trigger visible below `md`; actions stack on small screens.

**Accessibility:** Page title in `h1` when this is the primary heading; sticky header does not trap focus.

**Future integration:** Actions may include export, refresh, date range picker.

**Design rules:** Sticky; backdrop blur; 64px height; border-bottom subtle.

**Implementation:** `components/layout/header-shell.tsx`

---

## HeroSection

**Purpose:** Top-of-page executive summary block for high-impact pages (Dashboard only in MVP).

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Primary heading |
| description | string | No | Supporting text |
| meta | ReactNode | No | Period badge, last updated |
| actions | ReactNode | No | Primary CTA buttons (max 2) |

**Variants:** Default | Compact (reduced padding for inner pages — prefer PageHeader there).

**States:** Default, loading (skeleton).

**Responsive:** Stack title and actions vertically on mobile.

**Accessibility:** Single `h1` per page — HeroSection owns it on Dashboard.

**Future integration:** Meta shows last sync time from API.

**Usage example:** Dashboard — "نظرة تنفيذية" with Q2 2026 period badge.

**Design rules:** No background gradients; white or light surface; generous padding (`p-8`); gold accent on primary action only.

**Status:** To be implemented — not in Sprint 2.1.

---

## PageHeader

**Purpose:** Standard page title block for non-dashboard pages.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Page title |
| description | string | No | One-line purpose statement |
| breadcrumbs | BreadcrumbItem[] | No | Optional trail (max 3 levels) |
| actions | ReactNode | No | Page-level actions |

**Variants:** Default | With breadcrumbs.

**States:** Default, loading.

**Responsive:** Breadcrumbs truncate on mobile; actions move below title.

**Accessibility:** `h1` for title; breadcrumb nav with `aria-label="مسار التنقل"`.

**Future integration:** Breadcrumbs generated from route metadata.

**Usage example:** Financial Waste — "كشف الهدر المالي" with upload action.

**Design rules:** Less prominent than HeroSection; sits inside PageContainer.

**Status:** To be implemented — use SectionHeader temporarily if needed.

---

## SectionHeader

**Purpose:** Section divider with title, description, and optional action.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Section title |
| description | string | No | Section description |
| action | ReactNode | No | Section-level action (one button or link) |

**Variants:** Default only.

**States:** Default.

**Responsive:** Title and action stack on mobile (`flex-col`).

**Accessibility:** Section title as `h2`; do not skip heading levels.

**Future integration:** None — purely presentational.

**Usage example:** "التوصيات" with "عرض الكل" link.

**Design rules:** `text-2xl` semibold title; muted description; max one action per section.

**Implementation:** `components/ui/section-header.tsx`

---

## KpiCard (StatCard)

**Purpose:** Display a single executive KPI metric.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| label | string | Yes | Metric name |
| value | ReactNode | Yes | Formatted value |
| hint | string | No | Period or context |
| icon | ReactNode | No | Lucide icon |
| trend | ReactNode | No | Change indicator |

**Variants:** Default only.

**States:** Default, loading (skeleton matching card dimensions), error (show "—").

**Responsive:** Grid of 2 columns on mobile, 4 on desktop.

**Accessibility:** Label associated with value; trend includes text not color alone.

**Future integration:** Values from `GET /api/v1/dashboard/kpis` or equivalent.

**Usage example:** See PLACEHOLDER_DATA — KPI Cards section.

**Design rules:** White card; soft shadow; gold icon background tint; value `text-3xl` semibold.

**Implementation:** `components/ui/stat-card.tsx` (exported as StatCard; alias KpiCard in specs)

---

## RecommendationCard

**Purpose:** Display an AI or rules-engine recommendation.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Recommendation title |
| description | string | Yes | Detail text |
| badge | string | No | Priority or category label |
| badgeVariant | BadgeVariant | No | Visual priority |
| footer | ReactNode | No | Actions (accept, dismiss, details) |

**Variants:** Priority via badge: عالية | متوسطة | منخفضة.

**States:** Default, hover (border gold tint).

**Responsive:** Full width in lists; 2-column grid on xl screens (max 4 visible).

**Accessibility:** Title as `h3`; badge text readable; footer actions keyboard accessible.

**Future integration:** Source from AI analysis API; confidence score in footer.

**Design rules:** No icons clutter; description max 3 lines with truncate option.

**Implementation:** `components/ui/recommendation-card.tsx`

---

## ChartCard

**Purpose:** Container for a chart with title, description, and empty state.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Chart title |
| description | string | No | Chart subtitle |
| action | ReactNode | No | Chart controls (period selector) |
| children | ReactNode | No | ChartContainer + Recharts chart |
| emptyTitle | string | No | Empty state title |
| emptyDescription | string | No | Empty state description |
| height | number | No | Min height (default 320) |

**Variants:** Default | Compact (height 240).

**States:** Empty (no children), loading (skeleton), populated, error.

**Responsive:** Full width; height fixed minimum; horizontal scroll forbidden — chart must reflow.

**Accessibility:** Chart requires text alternative summary below chart (future); title describes purpose.

**Future integration:** Data from API; export button in action slot.

**Design rules:** Light inner background; border subtle; no chart junk — minimal axes.

**Implementation:** `components/ui/chart-card.tsx`

---

## ChartContainer

**Purpose:** Responsive Recharts wrapper with Khazina theme colors.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| children | ReactElement | Yes | Recharts chart element |
| height | number | No | Container height |
| className | string | No | Additional classes |

**Variants:** None.

**States:** Default.

**Responsive:** `ResponsiveContainer` width 100%.

**Accessibility:** Parent ChartCard must provide summary text.

**Future integration:** Theme tokens from `chartTheme` in `chart-container.tsx`.

**Design rules:** Primary series color gold-primary; grid lines `#E8E8E4`; no 3D effects.

**Implementation:** `components/ui/chart-container.tsx`

---

## UploadArea

**Purpose:** Drag-and-drop and click-to-upload zone.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | No | Primary instruction |
| description | string | No | Supported formats hint |
| accept | string | No | File accept attribute |
| multiple | boolean | No | Allow multiple files |
| disabled | boolean | No | Disable interaction |
| onFilesSelected | function | No | Callback with FileList |

**Variants:** Default | Compact (reduced height 120px).

**States:** Default, dragging, disabled, uploading (future).

**Responsive:** Full width; min-height 180px default.

**Accessibility:** Keyboard activatable; `role="button"`; Arabic instructions; file input labeled.

**Future integration:** Upload to `POST /api/v1/files/upload`; progress indicator overlay.

**Design rules:** Dashed border; gold tint on drag; upload icon in gold circle.

**Implementation:** `components/ui/upload-area.tsx`

---

## DataTable

**Purpose:** Generic typed data table with empty state.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| columns | DataTableColumn[] | Yes | Column definitions |
| data | T[] | Yes | Row data |
| emptyMessage | string | No | Empty row message |

**Variants:** Default | Compact (reduced row padding).

**States:** Empty, populated, loading (skeleton rows — future wrapper).

**Responsive:** Horizontal scroll on mobile; min-width 640px table; sticky header optional (future).

**Accessibility:** `table` with `thead`/`tbody`; column headers scope; sortable headers (future) with `aria-sort`.

**Future integration:** Server-side pagination; sorting; filtering via FilterBar.

**Design rules:** Zebra hover only; no vertical borders; header uppercase muted text.

**Implementation:** `components/ui/data-table.tsx`

---

## SearchBar

**Purpose:** Search input with icon for filtering lists and tables.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| placeholder | string | No | Arabic placeholder |
| value | string | No | Controlled value |
| onChange | function | No | Change handler |
| disabled | boolean | No | Disabled state |

**Variants:** Default | Full-width.

**States:** Default, focused, disabled.

**Responsive:** Full width in FilterBar; max-width 320px standalone.

**Accessibility:** `type="search"`; visible label or `aria-label="بحث"`.

**Implementation:** `components/ui/search-input.tsx` (SearchInput — alias SearchBar in specs)

---

## Button

**Purpose:** Primary interactive action element.

**Props:** Standard button props plus `variant`, `size`, `asChild`.

**Variants:**

| Variant | Use |
|---------|-----|
| primary | Main action (gold) |
| secondary | Secondary action (white bordered) |
| ghost | Tertiary / icon toolbar |
| outline | Gold outline |
| destructive | Delete / irreversible |
| link | Inline text action |

**Sizes:** sm | md (default) | lg | icon.

**States:** Default, hover, active, focus-visible, disabled.

**Responsive:** Full-width on mobile when sole primary action.

**Accessibility:** Focus ring; disabled state; loading state (future: spinner + aria-busy).

**Future integration:** Form submit; API action triggers.

**Design rules:** Max one primary button per section; no gradient buttons.

**Implementation:** `components/ui/button.tsx`

---

## Input

**Purpose:** Single-line text input.

**Props:** Standard input props plus `error` boolean.

**Variants:** Default | Error.

**States:** Default, focus, disabled, error.

**Responsive:** Full width in forms.

**Accessibility:** Associated `<label>` required in forms; error announced via `aria-invalid`.

**Implementation:** `components/ui/input.tsx`

---

## Textarea

**Purpose:** Multi-line text input.

**Props:** Standard textarea props plus `error` boolean.

**Variants:** Default | Error.

**States:** Same as Input.

**Design rules:** Min-height 120px.

**Implementation:** `components/ui/textarea.tsx`

---

## Badge

**Purpose:** Compact status or category label.

**Variants:** default (gold tint) | secondary | success | warning | destructive | outline.

**States:** Static only.

**Accessibility:** Not interactive unless inside button — use `<span>` semantics.

**Implementation:** `components/ui/badge.tsx`

---

## Modal

**Purpose:** Focused overlay dialog for confirmations and detail views.

**Props:** Radix Dialog composition — Trigger, Content, Title, Description, Footer.

**Variants:** Default (max-w-lg) | Wide (max-w-2xl — future).

**States:** Open, closed; focus trapped when open.

**Responsive:** Full-screen on mobile (future enhancement); centered on desktop.

**Accessibility:** Focus trap; Escape to close; title required; close button labeled "إغلاق".

**Future integration:** Detail views for recommendations, report preview.

**Implementation:** `components/ui/modal.tsx`

---

## Tooltip

**Purpose:** Contextual hint on hover/focus.

**Props:** Trigger + Content via Radix composition.

**States:** Open, closed.

**Accessibility:** Content available on focus; do not hide critical info in tooltips only.

**Implementation:** `components/ui/tooltip.tsx` + `providers/tooltip-provider.tsx`

---

## Alert

**Purpose:** Inline informational or warning banner.

**Variants:** default | info | success | warning | destructive.

**Props:** `title`, `children`, `variant`.

**States:** Static; dismissible (future).

**Accessibility:** `role="alert"` for destructive/warning; icon decorative with text present.

**Implementation:** `components/ui/alert.tsx`

---

## EmptyState

**Purpose:** Zero-data placeholder with optional action.

**Props:** `title`, `description`, `actionLabel`, `onAction`, `icon`.

**States:** Default only.

**Accessibility:** Heading + description; action button when provided.

**Usage:** See PLACEHOLDER_DATA — Empty State Messages.

**Implementation:** `components/ui/empty-state.tsx`

---

## LoadingSkeleton

**Purpose:** Placeholder shimmer during data fetch.

**Props:** `className`; LoadingSkeletonGroup with `lines` count.

**States:** Animated pulse.

**Accessibility:** `aria-hidden="true"` — pair with live region or spinner for screen readers.

**Implementation:** `components/ui/loading-skeleton.tsx`

---

## LoadingSpinner

**Purpose:** Inline loading indicator.

**Props:** `size` (sm|md|lg), `label` (Arabic, default "جاري التحميل").

**Accessibility:** `role="status"`; sr-only label.

**Implementation:** `components/ui/loading-spinner.tsx`

---

## ErrorState

**Purpose:** Recoverable error display with retry.

**Props:** `title`, `description`, `retryLabel`, `onRetry`.

**Accessibility:** `role="alert"`; retry button labeled.

**Implementation:** `components/ui/error-state.tsx`

---

## TimelineItem

**Purpose:** Render a single chronological event within a Timeline list.

**Responsibilities:**

- Display event date, title, type, and optional description
- Apply type-specific visual indicator (dot color/icon)
- Remain purely presentational — no data fetching

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| id | string | Yes | Unique event identifier |
| date | string | Yes | ISO date or formatted Arabic date |
| title | string | Yes | Event title |
| type | string | Yes | Event category (تنبيه، تحليل، مراجعة، نظام، تقرير) |
| description | string | No | Optional detail text |

**States:** Default only.

**Responsive behavior:** Date column fixed width on desktop; stacks above title on mobile.

**Accessibility:** Wrap date in `<time datetime>`; title as list item heading.

**Future backend integration:** Event data from `GET /api/v1/dashboard/timeline` or audit log API.

**Design rules:** Gold dot for type **تنبيه**; muted connector line to next item; no animation per item.

**Usage examples:**

- Dashboard — **آخر التحديثات** section (max 5 TimelineItem children)
- Risk Management — timeline section

**Status:** To be implemented.

---

## Timeline

**Purpose:** Vertical chronological event list (Dashboard **آخر التحديثات** and Risk Management page).

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| events | TimelineEvent[] | Yes | Ordered events (newest first) |
| maxVisible | number | No | Limit before "show more" (default 5) |

**TimelineEvent:** `{ id, date, title, type, description? }`

**Composition:** Timeline renders a list of **TimelineItem** components as its repeated child — one TimelineItem per event.

**Variants:** Default | Compact.

**States:** Empty (hide section), populated.

**Responsive:** Full width; date column fixed width on desktop.

**Accessibility:** List semantics; each child TimelineItem provides `<time datetime>`.

**Future integration:** Events from audit log API or `GET /api/v1/dashboard/timeline`.

**Design rules:** Gold dot for alerts; muted line connector; no animation overload.

**Status:** To be implemented.

---

## StatusBadge

**Purpose:** Semantic status indicator for files, reports, analyses.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| status | StatusEnum | Yes | Status key |
| label | string | No | Override display text |

**StatusEnum mapping:**

| Status | Label | Variant |
|--------|-------|---------|
| completed | مكتمل | success |
| processing | قيد المعالجة | warning |
| failed | فشل | destructive |
| draft | مسودة | secondary |
| ready | جاهز | default |

**Implementation:** Compose from Badge component — no separate file required unless logic grows.

**Status:** Pattern documented; implement as helper or thin wrapper.

---

## FilterBar

**Purpose:** Horizontal filter controls for list/report pages.

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| filters | FilterConfig[] | Yes | Filter definitions |
| values | Record | Yes | Current values |
| onChange | function | Yes | Change handler |
| onReset | function | No | Clear all filters |

**Variants:** Default | Inline (embedded in section header).

**States:** Default; active filters show count badge.

**Responsive:** Wrap filters on mobile; SearchBar full width first row.

**Accessibility:** Each filter labeled; reset button "إعادة تعيين".

**Future integration:** Query params sync with URL.

**Status:** To be implemented.

---

## StatCard

See **KpiCard** — same component. Use `StatCard` export name in code.

---

## Related Documents

- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md)
- [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md)
- [ARCHITECTURE.md](ARCHITECTURE.md) — Frontend architecture
