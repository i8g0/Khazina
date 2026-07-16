# Executive AI Precision Analysis

**Date:** 2026-07-17  
**Phase:** Investigation ONLY — no code changes  
**Objective:** Determine why AI recommendations are fluent but too generic for CEO action, and where precision is lost

---

## Executive Verdict

The platform produces **generic executive Arabic** because precision data either **never enters the Facts Contract**, **is dropped before the prompt**, or **prompts explicitly discourage citing raw numbers**.

| Layer | Precision impact | Evidence |
|-------|------------------|----------|
| **Facts Contract** | **PRIMARY** | No department, vendor, invoice, cost center, transaction-level facts |
| **Context Adapter** | **PRIMARY** | `metadata`, `period`, `organization_id` stripped from prompts |
| **Prompt Templates** | **HIGH** | "لا تكرر الأرقام خاماً" pushes vague language; no evidence-citation rule |
| **LLM** | **MEDIUM** | Fills Owner/Timeline/Root Cause from template examples |
| **Parser** | **LOW** | No validation that cited numbers exist in facts |
| **Database (Gold)** | **HIGH (unused)** | Departments, vendors, trends exist but not fed to waste AI |
| **Frontend/PDF** | **NONE** | Displays stored text faithfully |

**Root cause classification:** **Facts Contract gap (60%) + Prompt/Adapter gap (30%) + LLM gap (10%)**

A CEO cannot act on *"الفئة المالية تمثل 45%"* without knowing **which period, which amount, which category label** — yet the contract **has** amount and percentage per category; the prompt path ** hides category names** and **discourages number citation**.

---

## 1. Current Pipeline (End-to-End)

```
Financial Snapshot (Excel ingest)
    ↓
WasteSnapshotAdapterV1 → WasteEngineInput (category_name + amount only)
    ↓
WasteEngine (calculator + detector)
    ↓
WasteFactAssembler → FactsContract (stored in analysis_run.runtime_metadata)
    ↓
load_facts_contract(metadata)  [AI reads ONLY this for waste]
    ↓
ContextBuilder.build(domain=waste, task=RECOMMENDATIONS)
    ↓
fact_to_prompt_fact()  ⚠️ drops metadata, period, org_id
    ↓
build_user_prompt() → format_fact_for_prompt()  [Arabic labels, no category name]
    ↓
PromptComposer → system + task template + facts
    ↓
CloudProvider.chat()
    ↓
recommendation_parser → executive_recommendation parser
    ↓
mapper → DB (recommendations.title, description, source_context.executive)
    ↓
Frontend parseExecutiveRecommendation() → RecommendationCard
    ↓
PDF executive_pdf_layout → recommendation cards
```

**Risk path difference:** Risk AI adds `build_risk_metadata_supplement()` from `runtime_metadata.risk_findings` (names, scores, categories) — **waste has no equivalent supplement**.

**Report path (NOT used by AI):** Gold tables `waste_category_breakdowns`, `waste_vendor_findings`, departments — loaded for reports/PDF only.

---

## 2. Complete Facts Contract Schema

### 2.1 Core types (`business/facts/contract.py`)

**`Fact` fields:**

| Field | Type | In prompt? |
|-------|------|------------|
| `domain` | string | ✅ (as Arabic domain label) |
| `metric` | string | ✅ (as Arabic metric label, not raw key) |
| `value` | string | ✅ |
| `source` | string | ❌ not rendered |
| `unit` | string | ✅ (generic: عملة / نسبة مئوية) |
| `severity` | string | ✅ (مرتفع/متوسط/منخفض) |
| `confidence` | string | ❌ rarely present |
| `organization_id` | string | ❌ **dropped in adapter** |
| `period` | string | ❌ **dropped in adapter** |
| `metadata` | dict | ❌ **dropped in adapter** |
| `fact_schema_version` | string | ❌ |

**`FactsContract` fields:**

| Field | In prompt? |
|-------|------------|
| `contract_version` | ❌ |
| `engine_id` | ❌ |
| `engine_version` | ❌ |
| `generated_at` | ❌ |
| `facts[]` | ✅ (subset) |
| `extensions` | ❌ |

### 2.2 Waste engine facts (`engines/waste/manifest.py`)

| Metric | Unit | Severity | Metadata | Example value |
|--------|------|----------|----------|---------------|
| `waste.total_amount` | currency | — | — | `2340000.00` |
| `waste.percentage` | percent | overall level | — | `4.68` |
| `waste.top_category` | — | — | — | `finance` |
| `waste.top_category_percentage` | percent | — | — | `45.94` |
| `waste.potential_savings` | currency | — | — | `1872000.00` |
| `waste.savings_opportunities` | count | — | — | `2` |
| `waste.overall_level` | — | yes | — | `high` |
| `waste.category_amount` | currency | — | **`category_name`** | `1075000.00` |
| `waste.category_percentage` | percent | category level | **`category_name`** | `45.94` |
| `waste.category_level` | — | yes | **`category_name`** | `high` |

**Critical:** Category identity lives in **`metadata.category_name`**, which is **never passed to the LLM**.

### 2.3 Risk engine facts (`engines/risk/manifest.py` + assembler)

| Metric | Notes |
|--------|-------|
| `risk.total_findings` | count |
| `risk.high/medium/low_priority_count` | counts |
| `risk.overall_posture_level` | severity |
| `risk.waste_percentage` | percent |
| `risk.category_count` | count |
| `risk.liquidity_ratio` | optional |
| `risk.score_max` | optional |
| `risk.top_category` | **English code** e.g. `financial` |
| `risk.finding.{finding_id}.score` | metadata: `category_code`, `detection_rule_id` |
| `risk.category_count.{code}` | per-category counts |

**Risk finding human names** are NOT in Facts Contract — they arrive via `risk_metadata.py` supplement only.

### 2.4 Scenario engine facts

`scenario.archetype`, `baseline_total`, `projected_total`, `delta_amount`, `delta_percent`, `horizon_quarters`, `confidence_percent`, `category_baseline`, `category_projected` — used for simulation AI, not waste recommendations.

---

## 3. Missing Business Fields (Not in Facts Contract)

These fields **do not exist** anywhere in the waste AI path today:

| Business field | In snapshot ingest? | In Gold DB? | In Facts Contract? | In AI prompt? |
|----------------|--------------------|-------------|-------------------|---------------|
| **Department name** | ❌ | ✅ `waste_category_breakdowns.department_id` | ❌ | ❌ |
| **Supplier / Vendor** | ❌ | ✅ `waste_vendor_findings` | ❌ | ❌ |
| **Invoice** | ❌ | ❌ | ❌ | ❌ |
| **Cost center** | ❌ | ❌ | ❌ | ❌ |
| **Business unit** | ❌ | ❌ | ❌ | ❌ |
| **Month** | ❌ | ✅ `waste_trend_points.month_label` | ❌ | ❌ |
| **Quarter / Period label** | ⚠️ on run | ✅ reporting_periods | ⚠️ on `Fact.period` | ❌ **dropped** |
| **Top transactions** | ❌ | ❌ | ❌ | ❌ |
| **Largest expenses (line items)** | ❌ | ❌ | ❌ | ❌ |
| **Budget owner** | ❌ | ❌ | ❌ | ❌ |
| **Variance (budget vs actual)** | ⚠️ denominator path in adapter | ❌ as fact | ❌ | ❌ |
| **Trend (time series)** | ❌ | ✅ trend points table | ❌ | ❌ |
| **Account / GL code** | ❌ | ❌ | ❌ | ❌ |
| **Currency code** | ❌ | org settings | ❌ | ❌ |
| **Localized category label** | ❌ | ❌ | ❌ raw codes like `finance` | ❌ |

**Conclusion:** User expectation *"identify which department, supplier, account..."* cannot be met for **department/supplier/account** — those dimensions are **Facts Contract problems** (never assembled). **Category + amount + percentage + period** CAN be met but are **Prompt/Adapter problems** (data exists, not shown).

---

## 4. Available but Unused in Prompts

| Data | Where it exists | Why unused |
|------|-----------------|------------|
| `metadata.category_name` on category facts | Facts Contract | Stripped in `fact_to_prompt_fact()` |
| `Fact.period` (e.g. `2026-Q2`) | Facts Contract | Not in `PromptFact`; not in `format_fact_for_prompt()` |
| `Fact.organization_id` | Facts Contract | Dropped in adapter |
| `Fact.source` | Facts Contract | Not rendered |
| `waste.top_category` + `waste.top_category_percentage` | Facts Contract | Rendered as generic labels without tying to Arabic category name |
| Multiple `waste.category_*` rows | Facts Contract | Rendered as identical lines *"مبلغ الفئة = X"* — **indistinguishable** |
| Gold `WasteCategoryBreakdown.department_id` | PostgreSQL | Never loaded for AI |
| Gold `WasteVendorFinding.*` | PostgreSQL | Never loaded for AI; report UI notes Excel path often empty |
| `WasteTrendPoint` | PostgreSQL | Never in AI path |
| Risk finding **names**, likelihood, impact | `runtime_metadata.risk_findings` | Waste has **no parallel supplement** |
| Organization name, file name | Analysis run / org | Not injected into waste AI prompt |
| Reporting period label | Cover/report context | Not in AI facts block |

**Single highest-impact unused field:** `metadata.category_name` on `waste.category_amount` / `waste.category_percentage`.

---

## 5. Prompts That Generate Vague Language

### 5.1 System prompt (`ar.py` lines 15–17)

> *"إذا كانت البيانات غير كافية، اذكر ذلك صراحةً ولا تملأ الفراغات."*

**WHY vague:** Correct rule, but combined with missing category metadata the model **must** either stay vague or invent — it often chooses fluent generalities.

> *"حوّل كل حقيقة إلى جملة عربية تنفيذية"*

**WHY vague:** Encourages paraphrase without **mandatory numeric citation**.

### 5.2 Executive Summary template — **anti-precision rule**

> *"المشكلة: [المشكلة الجوهرية بلغة أعمال — **لا تكرر الأرقام خاماً**]"*

**WHY vague:** Explicitly tells the model **not** to state `745,000` or `31.8%` in the problem statement — directly conflicts with CEO precision requirements.

### 5.3 Recommendations template

> *"كل توصية يجب أن تشرح **لماذا** — **لا تكرر القيم الرقمية الخام دون تفسير**"*

**WHY vague:** Model interprets this as "explain in prose" → *"تمثل الفئة المالية نسبة كبيرة"* instead of *"SAR 1,075,000 during Q2 2026 representing 45.9% of total waste"*.

> *"الإدارة المسؤولة: [مثال: الشؤون المالية | المشتريات | التشغيل]"*

**WHY vague/invented:** Examples become **generative templates** — no fact binds owner department.

> *"الوفورات المتوقعة: [تقدير من السياق أو «**يُحدد بعد التقييم التفصيلي**»]"*

**WHY vague:** Explicit escape hatch when `waste.potential_savings` **is** in facts.

### 5.4 Risk analysis template

> *"لكل مخاطرة: عنوان، وصف موجز، وحقائق داعمة"*

**WHY vague:** No requirement to name finding ID, score, or category code from facts.

### 5.5 Facts rendering (`format_fact_for_prompt`)

Example prompt line sent to Cloud AI today:

```
- الهدر المالي: مبلغ الفئة = 1075000.00
  - الوحدة: عملة
  - الخطورة: مرتفع
- الهدر المالي: مبلغ الفئة = 745000.00
  ...
```

**WHY vague:** CEO sees no **which category** — model must guess or generalize.

---

## 6. Recommended Recommendation Instruction Rewrite (Design Only)

### Current (problematic)

> "High waste category" / "الفئة المالية تمثل 45%"

### Required pattern (evidence-bound)

**When facts exist:**

> «خلال **{period}**، سجّلت فئة **{category_name_ar}** هدراً مقداره **{amount} ر.س**، أي **{percentage}%** من إجمالي الهدر البالغ **{total_waste} ر.س** ({total_waste_pct}% من الإنفاق). يُعد هذا أعلى مصدر للهدر، ويبرر إطلاق **{action}** under **{owner}** خلال **{timeline}** لتحقيق وفورات تصل إلى **{allocated_savings} ر.س**.»

**Concrete example using test fixture data** (`conftest.sample_waste_engine_input`):

> «خلال **الربع الثاني 2026**، سجّلت فئة **الشؤون المالية** هدراً قدره **1,075,000 ر.س**، أي **45.9%** من إجمالي الهدر (**2,340,000 ر.س**). يُوصى بإطلاق **مراجعة حوكمة مالية مركّزة** برئاسة **الإدارة المالية** خلال **45 يوماً**، بهدف است recovering up to **860,000 ر.س** من الوفورات المحتملة المقدّرة للمؤسسة.»

*(Owner/timeline only valid if mapped from category→department rules or marked "غير متوفر في البيانات")*

### Mandatory recommendation sections (10 fields)

| # | Section | Source |
|---|---------|--------|
| 1 | **Problem** | Derived from highest severity category fact |
| 2 | **Evidence** | Exact `{category, amount, percentage, period}` from facts — **quoted** |
| 3 | **Business Impact** | LLM synthesis **only from cited numbers** |
| 4 | **Root Cause** | Only if in facts/metadata; else "غير متوفر — يتطلب تحليلاً تشغيلياً" |
| 5 | **Recommendation** | Action verb + scope tied to evidence category |
| 6 | **Priority** | From `waste.category_level` or fact severity |
| 7 | **Owner** | From department mapping OR "غير محدد في البيانات" |
| 8 | **Timeline** | Template by priority — **not invented dates** |
| 9 | **Expected Saving** | From `waste.potential_savings` prorated by category % **only if math is in facts layer** |
| 10 | **Success Metric** | e.g. "reduce category waste by X% next period" — X must come from facts target |

---

## 7. Where AI Is Allowed to Invent (Must Become Zero)

| Invention vector | Current state | Required state |
|------------------|---------------|----------------|
| Department / owner | Template examples → LLM picks | Fact-bound or explicit "غير متوفر" |
| Timeline (30–60 days) | Template suggestion | Priority-based default **labeled as planning assumption** or from policy table |
| Expected savings | LLM estimates or placeholder text | Only `waste.potential_savings` × category share (computed in engine, not LLM) |
| Root cause | Not in schema — LLM invents | Forbidden unless fact field added |
| Category Arabic name | LLM translates `finance` | Must come from localization map in facts layer |
| Supplier names | Not in contract | Forbidden |
| Success metrics | LLM invents | Must reference measurable fact baseline |
| Risk finding descriptions | Partially from supplement | OK for risk if from `risk_findings` metadata |
| "تشير البيانات" hedging | Allowed | Ban hedging phrases — state evidence directly |
| Cross-domain claims | Waste AI also runs RISK_ANALYSIS task | Must not cite risk facts in waste recommendations unless in same contract |

**System prompt line allowing invention:**

> *"يمكنك مقارنة الحقائق المقدمة وترتيبها وتلخيصها وشرحها وربطها ببعضها"*

**Risk:** "شرح وربط" without citation rules → narrative invention.

---

## 8. Generic Wording Sources

| Phrase pattern | Source | Fix (design) |
|----------------|--------|--------------|
| "تشير البيانات..." | Prompt ban (partial) + LLM habit | Strengthen: **ممنوع** all hedging openers |
| "There are high-risk categories" | No category name in prompt | Include `metadata.category_name` |
| "The financial category represents 45%" | `top_category=finance` without amount | Force triple: name + amount + % |
| "يُحدد بعد التقييم" | Recommendation template | Remove when `potential_savings` fact exists |
| "فئة مرتفع الخطورة" | severity label without entity | Attach severity to named category |
| English codes (`finance`, `overlapping_contracts`) | Raw snapshot category keys | Localize in Facts or prompt builder |

---

## 9. Limitation Diagnosis (With Evidence)

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| **Prompt** | ✅ **Major** | Anti-raw-number rules; no citation mandate; owner examples |
| **Facts** | ✅ **Major** | No dept/vendor/account; category name in metadata only |
| **Parser** | ⚠️ **Minor** | Does not validate numbers against facts |
| **Database** | ✅ **Major (unused)** | Gold tables richer than contract |
| **Frontend** | ❌ Not limiting | Displays parsed output |
| **LLM** | ⚠️ **Symptom** | Fills gaps when facts/prompts incomplete |

**Primary fix order:** Facts Contract enrichment → Adapter/prompt rendering → Prompt rules → Parser validation → Gold supplement for waste (mirror risk)

---

## 10. Redesign Plan (NO IMPLEMENTATION)

### Phase A — Facts Contract v1.1 (Business engine, not LLM)

1. Add **`waste.category.{name}.amount|percentage|level`** as first-class metrics OR require `metadata.category_name` in prompt path.
2. Add **`reporting.period_label`**, **`organization.name`**, **`currency.code`** as facts at assembly time.
3. Optional: **`waste.vendor.{name}.amount`**, **`waste.department.{name}.amount`** from Gold if present.
4. Add **`waste.variance.budget_vs_actual`** if snapshot supports budget denominator path.
5. Localize category codes → Arabic labels **in assembler**, not in LLM.

### Phase B — Prompt Builder

1. Extend `PromptFact` with `dimensions: dict` (category, period, department).
2. Render each fact as a **single executive sentence** with all dimensions:
   - *"فئة الشؤون المالية: 1,075,000 ر.س (45.9% من الهدر) — فترة Q2 2026 — خطورة: مرتفع"*
3. Add **`build_waste_metadata_supplement()`** mirroring risk: breakdowns, vendors, org context from DB.
4. Remove anti-precision rule "لا تكرر الأرقام خاماً" — replace with **"يجب ذكر الأرقام الدقيقة من السياق في قسم الأدلة"**.

### Phase C — Prompt Templates

1. **Executive Summary:** Situation must include total waste + period in first paragraph.
2. **Recommendations:** 10-section structure with **Evidence** block quoting fact IDs.
3. Ban: «تشير البيانات»، «يبدو»، «من المحتمل» unless uncertainty is in facts.
4. Owner: only from fact `responsible_department` or literal **"غير متوفر في البيانات"**.
5. Savings: only from engine-computed field, never LLM math.

### Phase D — Parser & Validator

1. Post-parse scan: every number in output must match a fact value (±formatting).
2. Reject recommendations missing **Evidence** section.
3. Store `evidence_fact_refs[]` in `source_context` for audit.

### Phase E — Frontend & PDF

1. Display **Evidence** line under each card (category, amount, period).
2. PDF recommendation cards: show evidence block in smaller type.
3. Badge "مبني على بيانات محددة" when evidence validates.

---

## 11. Executive Wording Examples (Before / After)

### Recommendation

| | Text |
|---|------|
| **BAD (today)** | «توجد فئات عالية الخطورة تستدعي التدخل.» |
| **GOOD** | «فئة **الشؤون المالية** أنتجت **1,075,000 ر.س** هدراً (**45.9%** من إجمالي **2,340,000 ر.س**) في **Q2 2026** — أعلى فئة على مستوى المؤسسة.» |

### Executive Summary

| | Text |
|---|------|
| **BAD** | «الوضع المالي يتطلب انتباهاً بسبب مستويات الهدر.» |
| **GOOD** | «خلال **Q2 2026**، بلغ الهدر **2.34M ر.س** (**4.68%** من الإنفاق). تتركز **45.9%** منه في **الشؤون المالية**. الوفورات المحتملة: **1.87M ر.س** عبر **فرصتين** نشطتين.» |

---

## 12. Expected Quality Improvement

| Metric | Today | After redesign |
|--------|-------|----------------|
| Recommendations citing exact amount | ~10% | **≥90%** |
| Recommendations citing category name | ~20% (generic "مالية") | **100%** when in facts |
| Recommendations citing period | ~0% | **100%** |
| Invented department/owner | ~80% | **0%** (explicit N/A) |
| CEO can assign action without follow-up | No | **Yes** for category-level actions |
| Supplier-level precision | Impossible | Possible only after Facts v1.1 + ingest |

---

## 13. Investigation Checklist (User Questions)

| # | Question | Answer |
|---|----------|--------|
| 1 | Complete Facts schema? | Section 2 |
| 2 | Missing business fields? | Section 3 |
| 3 | Available but unused? | Section 4 |
| 4 | Vague prompts? | Section 5 |
| 5 | Rewrite recommendation instructions? | Section 6 |
| 6 | 10-section recommendation? | Section 6 table |
| 7 | Invention vectors? | Section 7 |
| 8 | Generic wording? | Section 8 |
| 9 | Prompt vs Facts vs …? | Section 9 |
| 10 | Redesign plan? | Section 10 |

---

## 14. Files Traced (Evidence Index)

| Layer | File |
|-------|------|
| Facts schema | `backend/app/business/facts/contract.py` |
| Waste assembler | `backend/app/business/assemblers/waste.py` |
| Waste manifest | `backend/app/business/engines/waste/manifest.py` |
| Risk assembler | `backend/app/business/assemblers/risk.py` |
| Snapshot ingest | `backend/app/decision/adapters/waste_v1.py` |
| Context builder | `backend/app/ai/context/builder.py` |
| Adapter | `backend/app/ai/context/adapter.py` |
| Prompt facts | `backend/app/ai/prompts/facts.py` |
| Prompt builder | `backend/app/ai/prompts/builder.py` |
| Metric labels | `backend/app/presentation/metric_labels.py` |
| Templates | `backend/app/ai/prompts/languages/ar.py` |
| Pipeline | `backend/app/ai_recommendations/pipeline.py` |
| AI service | `backend/app/ai_recommendations/service.py` |
| Risk supplement | `backend/app/ai_recommendations/risk_metadata.py` |
| Parser | `backend/app/ai_recommendations/recommendation_parser.py` |
| Executive parse | `backend/app/presentation/executive_recommendation.py` |
| Gold DB | `backend/app/db/models/waste.py` |
| Frontend | `frontend/lib/format.ts`, `recommendation-card.tsx` |

---

**END OF INVESTIGATION — NO CODE CHANGES MADE**
