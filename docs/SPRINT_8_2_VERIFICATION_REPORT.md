# Sprint 8.2 — Dynamic Data Verification Report

**Date:** 2026-07-16  
**Method:** Real API pipeline (no mocked responses, no DB edits)  
**Account:** `demo@khazina.sa`  
**Org ID:** `7dd234e7-58dd-4844-a38e-92a4fa67d0ed`  
**Evidence:** `scripts/demo/sprint_8_2_results.json` (dual-dataset run)

---

## Executive Conclusion

Khazina **is a real decision pipeline** over parsed Excel snapshots and PostgreSQL persistence. Changing the input workbook **materially changes** waste totals, category mix, AI recommendations, simulation baselines/projections, and executive report narrative.

However, several layers remain **partially dynamic or static** (fixed engine formulas, seeded scenario assumptions, empty vendor findings, dashboard aggregation absent, client-side demo artifact caching). A careful judge would **mostly believe** the waste → AI → simulation → report chain is data-driven, but could become **suspicious** about vendor analysis, dashboard emptiness, identical scenario *percentage* deltas, and UI stale-run behavior after re-upload.

**Judge confidence (overall):** **7/10** — credible core pipeline; not yet a fully polished enterprise demo.

---

## Phase 1 — Environment Verification

| Check | Status | Notes |
|-------|--------|-------|
| Backend (`/api/v1/health`) | ✅ PASS | `200`, status `ok` |
| Frontend (`localhost:3000`) | ✅ PASS | `200` |
| PostgreSQL | ✅ PASS | 33 tables; `financial_files` query succeeded |
| Ollama | ⚠️ Started for test | Was **not running** at sprint start; started via `ollama serve` |
| AI model | ✅ PASS | `qwen3.5:4b` (matches `backend/.env`) |
| Demo login | ✅ PASS | JWT + active org retrieved |

**Immediate failure at start:** Ollama was down. Required manual start before AI phase.

---

## Phase 2 — Upload Verification (Canonical Workbook)

**File:** `scripts/demo/Procurement_Q2.xlsx`  
**Sheet:** `WasteData` — 3 rows (`category`, `amount`, `total_spend`)

| Step | Result | IDs / Details |
|------|--------|---------------|
| Upload | ✅ ~54ms | `file_id=0ca6c549-…`, `snapshot_id=86f67973-…`, `snapshot_version=1`, `record_count=3` |
| Processing status | ✅ | `ready_for_analysis` |
| Repository list | ✅ | File appears in org file list (3 total files in DB after both runs) |
| Quality checks | ❌ Not auto-created | `GET .../data-quality/snapshots/latest` → **404** until explicit POST |

**Note:** Upload creates snapshot from parsed Excel; quality snapshot is a **separate API** not invoked by upload alone.

---

## Phase 3 — Waste Analysis (Run A)

**Run ID:** `b33b454b-8527-4cf9-b015-28b6aaf590f1`  
**Execute time:** ~35ms

| Metric | Value | Source |
|--------|-------|--------|
| Total waste | **2,340,000** | Sum of Excel amounts (745k + 520k + 1,075k) |
| Waste % | **4.68%** | 2.34M / 150M total spend (3×50M rows) |
| Potential savings | **1,872,000** | Engine: 80% recoverable rate |
| Savings opportunities | **3** | All categories ≥15% threshold |

**Categories (from API):**

| Category | Amount | % of waste |
|----------|--------|------------|
| finance | 1,075,000 | 45.94% |
| overlapping_contracts | 745,000 | 31.84% |
| operations | 520,000 | 22.22% |

**Departments:** `department_id` null on all breakdowns (Excel has no department column).  
**Vendors:** **0 findings** — endpoint works but decision engine does not populate vendors.

✅ No hardcoded KPI numbers in API responses — values derive from workbook rows + fixed formulas.

---

## Phase 4 — AI Recommendations (Run A)

| Metric | Value |
|--------|-------|
| Response time | **~52.5s** |
| Count | **5** recommendations |
| Model | `qwen3.5:4b` (in `ai_insights`) |
| Confidence labels | **All null** |
| Estimated savings on rec rows | **All null** |

**Sample titles (abbreviated):**
- References **745,000**, **520,000**, **45.94%**, **4.68%**, **3 opportunities**
- Wording pattern: every title begins with **"الإجراء المقترح:"** (template feel)

**Quality observations:**
- ✅ References real numeric facts from waste run
- ⚠️ **Category confusion** — e.g. cites finance as 45.94% but attributes 745,000 to wrong narrative in places
- ⚠️ Generic phrasing despite embedded numbers
- ❌ No supplier/vendor references (none in facts)
- ❌ No confidence scores persisted on recommendation rows

---

## Phase 5 — Scenario Simulation (All 3 Scenarios, Run A)

**Baseline from snapshot total spend:** **50.00M ر.س** (single row `total_spend`; not summed across rows)

| Scenario | Execute | Assumptions | Forecast baseline → projected | Delta | Confidence | Impact | Actions | Chart pts |
|----------|---------|-------------|-------------------------------|-------|------------|--------|---------|-----------|
| تقليل الإنفاق 10% | ~40ms | 2 | 50M → 45M | **-10.0%** | **88%** | 3 | 1 | 3 |
| دمج الموردين | ~40ms | 4 | 50M → 39M | **-22.0%** | **85%** | 3 | 1 | 3 |
| توسع السوق الخليجي | ~40ms | 3 | 50M → 55M | **+10.0%** | **72%** | 3 | 1 | 3 |

✅ Assumptions loaded from DB (bootstrap seed).  
✅ Charts and comparison metrics generated.  
⚠️ **Delta percentages and confidence scores are archetype-fixed** — same across datasets (see Phase 7).

---

## Phase 6 — Executive Report (Run A)

**Report ID:** `cecadbbe-3b86-46da-94f5-cb9b6d78b6d5`  
**Generate time:** ~57ms | **PDF:** ~56ms, **3,383 bytes**

**Sections present:**
`cover`, `executive_summary`, `key_metrics`, `waste_analysis`, `risk_explanation`, `recommendations`, `provenance`

**Executive summary excerpt:** References ~2.34M waste, ~1.87M savings opportunity, finance as largest category.

⚠️ Uses **"دولار"** in Arabic summary while platform settings imply SAR context — currency inconsistency.

✅ PDF returns `application/pdf` with non-trivial binary (though very small — thin document).

---

## Phase 7 — Dynamic Verification (Dual Dataset)

**Variant workbook:** `Procurement_Q2_variant.xlsx` — same schema, **different amounts** (1.2M / 300k / 450k, total_spend 80M per row)

### Comparison Matrix

| Stage | Run A (canonical) | Run B (variant) | Changed? | Classification |
|-------|-------------------|-----------------|----------|----------------|
| **Upload / snapshot** | 3 records, v1 | 3 records, v1 | ✅ New IDs | **Dynamic** |
| **Waste total** | 2,340,000 | 1,950,000 | ✅ | **Dynamic** |
| **Waste %** | 4.68% | 2.44% | ✅ | **Dynamic** |
| **Category amounts** | finance 1.075M top | overlapping 1.2M top | ✅ | **Dynamic** |
| **Potential savings** | 1,872,000 | 1,560,000 | ✅ | **Dynamic** (80% formula) |
| **Opportunity count** | 3 | 3 | ❌ Same | **Partially Dynamic** (threshold logic; often 3 with 3-row demo files) |
| **Vendor findings** | 0 | 0 | ❌ | **Static (empty)** |
| **AI titles** | 5 distinct | 5 distinct | ✅ Different | **Dynamic** (LLM + facts) |
| **AI references** | 745k, 4.68%, 45.94% | 61.54%, 1.56M, overlapping_contracts | ✅ | **Dynamic** |
| **Simulation baseline** | 50.00M | 80.00M | ✅ | **Dynamic** |
| **Simulation projected $** | 45M / 39M / 55M | 72M / 62.4M / 89.5M | ✅ | **Dynamic** |
| **Simulation delta %** | -10%, -22%, +10% | -10%, -22%, +11.9% | ⚠️ Mostly same | **Partially Dynamic** |
| **Scenario confidence** | 88/85/72% | 88/85/72% | ❌ | **Static** |
| **Report executive summary** | 2.34M narrative | 1.95M / 61.54% overlapping | ✅ | **Dynamic** |
| **Dashboard KPIs/charts** | Empty states | Empty states | ❌ | **Static (no aggregation API)** |

### Pipeline Answer

**If a judge uploads a different Excel workbook with the same schema:**

| Will change | Will NOT change (without further work) |
|-------------|----------------------------------------|
| Waste totals, %, category breakdown | Vendor table (always empty) |
| AI recommendation text & cited numbers | Dashboard executive KPIs/charts |
| Simulation baseline & projected amounts | Scenario assumption labels/values (DB seed) |
| Report narrative & key metrics sections | Scenario delta % for spending/supplier archetypes |
| PDF content (tied to report) | Fixed confidence scores (88/85/72) |
| | Department names (unless `department_id` on file) |
| | Quality score UI (unless quality snapshot POST) |

---

## Phase 8 — Static Component Audit

| Component | Type | Verdict |
|-----------|------|---------|
| Waste recoverable rate (80%) | Fixed formula | **Expected** (frozen engine) |
| Savings opportunity threshold (15%) | Fixed rule | **Expected** |
| Risk severity thresholds (5/10/15/30%) | Fixed rules | **Expected** |
| Scenario archetype formulas | Fixed math | **Expected** |
| Scenario confidence (88/85/72%) | Constant | **Technical debt** (looks fake to judges) |
| Bootstrap scenario assumptions | DB seed | **Expected** for demo |
| Vendor findings pipeline | Never populated | **Bug / gap** (API exists, engine empty) |
| Dashboard aggregation | Not implemented | **Future enhancement** (Phase 8+) |
| `sessionStorage` demo artifacts | Client cache | **Technical debt** — stale runs after re-upload |
| AI prompt templates (Arabic) | Fixed structure | **Expected** |
| `"الإجراء المقترح:"` title prefix | LLM pattern | **Technical debt** ( repetitive) |
| Recommendation `confidence_label` null | Not mapped from AI | **Bug / gap** |
| Category keys in English (`finance`) | Parser preserves Excel values | **Expected** but **weak UX** for Arabic demo |
| PDF size ~3.4KB | Minimal ReportLab output | **Expected** MVP; **weak judge impression** |
| Risk page | Empty state only | **Expected** (deferred engine) |

---

## Phase 9 — AI Quality Review

| Criterion | Assessment |
|-----------|------------|
| Uses uploaded data? | **Yes** — amounts and percentages match waste Gold output |
| Generic advice? | **Partially** — numbers embedded but prose is repetitive |
| References departments? | **No** — not in facts |
| References suppliers? | **No** — vendor facts absent |
| References categories? | **Yes** — finance, operations, overlapping_contracts |
| References amounts? | **Yes** — e.g. 745,000 / 1,560,000 / 61.54% |
| Reasoning quality | **Mixed** — occasional **category/amount mismatches** |
| Confidence | **Not surfaced** to UI (null) |
| Executive summary in report | **Data-linked** but currency wording inconsistent |

**Verdict:** AI is **genuinely conditioned on Facts Contract from the waste run**, not a pure static template — but output quality and presentation would not fully convince a skeptical finance judge.

---

## Phase 10 — Judge Simulation (Suspicion Log)

Moments a hackathon judge might doubt authenticity:

1. **Dashboard** — five KPI cards all say "no executive analytics yet" — looks incomplete, not "live BI."
2. **Re-upload same session** — Waste page may still show **previous run** until user clicks "تشغيل تحليل الهدر" again (`sessionStorage` `wasteRunId`).
3. **Vendor section always empty** — after waste analysis, judge expects supplier findings.
4. **English category slugs** in Arabic UI (`overlapping_contracts`, `finance`).
5. **No department labels** on breakdown rows — "لم يُربط بقسم" everywhere.
6. **AI titles** all start identically — feels templated.
7. **Scenario deltas** -10% and -22% **identical** across two very different datasets — judge may think scenarios are fake.
8. **Confidence 88/85/72%** never varies — looks seeded.
9. **Data quality** shows "لم يُقيَّم بعد" unless separate workflow — upload doesn't auto-evaluate.
10. **PDF** downloads but is **tiny** (~3KB) — may look like a stub.
11. **Report mentions "دولار"** in Arabic executive context.
12. **Risk page** entirely deferred — acceptable if explained, but breaks "full platform" narrative.

---

## Deliverable 1 — End-to-End Pipeline Status

```
Excel Upload → Parse → Financial Snapshot → Waste Engine → Gold Tables
     → AI (Ollama) → Recommendations → Scenario Engine → Simulation Gold
     → Report Assembler → PDF Export → Notifications
```

| Step | Status |
|------|--------|
| Upload | ✅ Live |
| Snapshot | ✅ Live |
| Waste execute | ✅ Live |
| Waste result/breakdowns | ✅ Live |
| Vendor findings | ⚠️ API live, data always empty |
| AI generate | ✅ Live (requires Ollama running) |
| Scenario execute (×3) | ✅ Live |
| Report generate | ✅ Live |
| PDF export | ✅ Live |
| Dashboard exec view | ❌ Empty state only |
| Risk module | ❌ Deferred empty state |

---

## Deliverable 2 — Dynamic vs Static Matrix

| Stage | Live | Dynamic | Static | Reason |
|-------|------|---------|--------|--------|
| Financial ingestion | ✅ | ✅ | — | Parses uploaded Excel into snapshot payload |
| Snapshot | ✅ | ✅ | — | Versioned per upload |
| Waste analysis | ✅ | ✅ | ⚠️ formulas | Amounts from data; thresholds/rates fixed |
| Category breakdown | ✅ | ✅ | — | Mirrors Excel categories |
| Vendor findings | ✅ | — | ✅ | Engine never writes vendors |
| AI recommendations | ✅ | ✅ | ⚠️ prompts | Facts-driven; template phrasing |
| Simulation baseline | ✅ | ✅ | — | From snapshot `total_spend` |
| Simulation assumptions | ✅ | — | ✅ | Bootstrap seed in DB |
| Simulation deltas | ✅ | ⚠️ | ⚠️ | $ dynamic; % fixed per archetype (mostly) |
| Report content | ✅ | ✅ | ⚠️ layout | Sections fixed; payloads from run |
| PDF | ✅ | ✅ | — | Generated from report |
| Dashboard | ✅ | — | ✅ | No aggregation API |
| Risk | ✅ | — | ✅ | Intentionally deferred |
| UI demo state | ✅ | — | ⚠️ | sessionStorage can stale |

---

## Deliverable 3 — AI Quality Assessment

**Score: 6.5/10**

- **Strengths:** Non-identical output across datasets; numeric grounding; executive summary in report reflects run metrics.
- **Weaknesses:** Repetitive structure; category misattribution; no confidence on cards; no vendors/departments; currency inconsistency; 50s latency.

---

## Deliverable 4 — Performance Measurements

| Operation | Run A | Run B |
|-----------|-------|-------|
| Upload | 54 ms | 32 ms |
| Waste execute | 35 ms | 27 ms |
| Waste fetch | 19 ms | 16 ms |
| **AI generate** | **52.5 s** | **41.1 s** |
| Scenario ×3 (total) | ~0.12 s | ~0.15 s |
| Report generate | 57 ms | 34 ms |
| PDF export | 56 ms | 21 ms |
| **Full pipeline (excl. login)** | **~53 s** | **~42 s** |

**Bottleneck:** Ollama inference (~40–53s per AI call).

---

## Deliverable 5 — Judge Confidence Assessment

**Would I believe real financial data drives decisions?**

**For the core demo path (Data → Waste → AI → Simulation → Report): Yes, with reservations.**

Evidence: side-by-side workbooks produced different waste totals (2.34M vs 1.95M), different top category, different AI text, different simulation baselines (50M vs 80M), and different report summaries — all via API with no manual DB edits.

**Reservations:** empty vendors, static scenario percentages, dashboard gap, stale UI cache, and AI polish issues would erode trust under cross-examination.

---

## Deliverable 6 — Remaining Blockers (by Severity)

| Rank | Blocker | Severity |
|------|---------|----------|
| 1 | **Ollama not auto-started** — AI step fails silently without ops setup | Critical (ops) |
| 2 | **`sessionStorage` stale run IDs** after re-upload | High (judge-visible) |
| 3 | **Vendor findings always empty** | High |
| 4 | **Dashboard has no live executive aggregation** | High (first impression) |
| 5 | **Scenario delta % identical across datasets** | Medium |
| 6 | **Fixed confidence 88/85/72%** | Medium |
| 7 | **AI recommendation confidence null in UI** | Medium |
| 8 | **English category keys in Arabic UI** | Medium |
| 9 | **Quality checks not auto-run on upload** | Low–Medium |
| 10 | **Thin PDF / currency wording** | Low |

---

## Deliverable 7 — Recommendations (Impact Order)

1. **Clear demo artifacts on new upload** — reset `wasteRunId`, `simulationRunId`, `lastReportId` when a new file is ingested (frontend-only, high judge impact).
2. **Document/start Ollama in demo script** — preflight check before judging (`ollama serve` + model pull).
3. **Wire vendor findings from waste engine** OR hide vendor UI section until populated — avoid empty table after analysis.
4. **Dashboard aggregation API** (Phase 8+) — first screen must show live KPIs from latest completed analysis.
5. **Map AI confidence to recommendation rows** — surface in UI.
6. **Localize category display names** — Arabic labels in breakdown/report.
7. **Link departments** — optional `department_id` on upload or mapping from Excel.
8. **Auto-run quality snapshot** on successful ingest — or hide quality widgets until data exists.
9. **Vary scenario confidence or derive from run** — reduce "seeded demo" appearance.
10. **Enrich PDF template** — branding, charts, SAR formatting.

---

## Artifacts

- Raw JSON: `scripts/demo/sprint_8_2_results.json`
- Verification script: `scripts/demo/sprint_8_2_verify.py` (reproducible; not required for production)
- Canonical workbook: `scripts/demo/Procurement_Q2.xlsx`
- Variant workbook: `scripts/demo/Procurement_Q2_variant.xlsx`

**No code changes to application logic. No commits.**

---

## Definition of Done — Sprint 8.2

| Criterion | Met? |
|-----------|------|
| Know which parts are data-driven | ✅ |
| Know which parts remain static | ✅ |
| Know if changing input changes decisions | ✅ **Yes** for core pipeline |
| Know if AI reasons over financial data | ✅ **Partially** — facts-driven with quality gaps |
| Know if demo convinces as executive intelligence platform | ⚠️ **Mostly** — core yes, presentation gaps no |
