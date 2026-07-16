# Sprint 6 — Financial Reality & Executive Reasoning

## Root Cause Analysis

The simulation produced financially unrealistic outcomes because `UniversalScenarioCalculator` applied **hardcoded multipliers against total operating spend** and treated spend as revenue baseline.

| Issue | Location (pre-Sprint 6) | Effect |
|-------|-------------------------|--------|
| Revenue = % of **total spend** | `_apply_revenue()` default 10% | 10% × 78M ≈ **7.8M fake revenue** |
| `gross_revenue = baseline_total + revenue_uplift` | `_comparison_metrics()` | Spend reported as revenue |
| Hardcoded defaults | 3% prices, 8% suppliers, 4.5%×branches, 50k hire, 10% default | Unsupported assumptions |
| No validation layer | — | Impossible ROI passed through |
| Single-point forecasts | — | False precision |

**Example failure:** «افتح فرعاً بميزانية 100,000 ريال» on ~78.5M SAR dataset → millions in “revenue increase”.

---

## Solution Architecture

```
User NL → AIScenarioInterpreter (constrained prompts)
       → FinancialRealityEngine.simulate()
       → UniversalScenarioCalculator (thin delegate)
       → AISimulationExplainer (ranges + reasoning context)
       → Gold + API + Frontend
```

### New module: `financial_reality.py`

- Separates **expense baseline** from **revenue impact**
- Implied revenue = spend × 1.05 (no revenue column in waste dataset)
- Returns `MetricRange` (worst / expected / best) for expense, revenue, cash
- Returns confidence level + rationale + action reasonings + validation notes

---

## Removed Fake Multipliers

| Removed | Was | Now |
|---------|-----|-----|
| Default revenue uplift | 10% of spend | Capped organic growth ≤5%/yr on implied revenue |
| Price increase default | 3% of spend | 3% on implied revenue × 65% elasticity |
| Supplier reduction default | 8% all categories | User % on matched category only |
| Branch closure | 4.5% × branches (max 25%) | 2.5% × branches (max 12%) on operations |
| Hire unit cost | 50,000 SAR fixed | 85,000 SAR default |
| Profit target cut | 40% of category | 25% max per category, 15% total cap |
| Projected total | spend + revenue mixed | **expense categories only** |

---

## Validation Rules (`FinancialRealityEngine`)

| Rule | Limit |
|------|-------|
| Organic revenue growth | ≤ 5% per year |
| Price increase | ≤ 12% |
| Expense reduction | ≤ 40% |
| Expense increase | ≤ 35% of baseline |
| Category change | ≤ 45% per category |
| Revenue uplift vs implied | ≤ 8% × horizon years |
| Investment ROI | 8%–120% annual, capped |
| Investment payback sanity | Revenue ≤ 3× investment × horizon |
| Absolute revenue requests | Clamped to implied revenue cap |

Violations → **recalculate/clamp** + `validation_notes` + confidence penalty.

---

## Before / After (Demo Dataset ~78.5M SAR)

| Scenario | Before (buggy) | After (Sprint 6) |
|----------|----------------|------------------|
| Open branch 100k | ~7.36M revenue | ~9k–15k revenue (ROI on 0.13% of spend) |
| Open branch 10M | Unbounded | Expense +10M; revenue capped ~11M with validation |
| Increase salaries 5% | Wrong routing | +0.67% total expense (HR only) |
| Reduce transport 20% | OK-ish | ~1.5M savings on logistics |
| Marketing +1M | OK | +1M expense; modest revenue range |
| Procurement -15% | 8% default sometimes | ~2.8M savings on procurement |
| Revenue +10% | **7.85M** (10% of spend) | **~4.1M** (5% cap on implied revenue) |

---

## Acceptance Tests

`backend/tests/scenario/test_financial_reality.py` — all 9 scenarios pass.

Proof command:

```bash
cd Khazina/backend
python -m pytest tests/scenario/test_financial_reality.py -v
```

---

## API / Frontend Changes

- `financial_reality` added to `runtime_metadata`, API response, Gold `ai_metadata`
- Frontend simulation page shows:
  - Confidence level + rationale
  - Worst / expected / best ranges (revenue, expense, cash)
  - Financial reasoning bullets
  - Validation notes when values were clamped

---

## Regression

Run after backend restart:

```bash
python scripts/demo/sprint0_executive_workflow_verify.py
```

Upload → Waste → Risk → Risk AI → Simulation → Reports → PDF must remain green.

---

## Files Modified

| File | Change |
|------|--------|
| `financial_reality.py` | **NEW** — CFO constraint engine |
| `universal_calculator.py` | Delegates to reality engine |
| `ai_interpreter.py` | Financial constraint prompts |
| `ai_explainer.py` | Ranges + reasoning in context |
| `ai_simulation_service.py` | Wires financial_reality end-to-end |
| `ai_contract.py` | FinancialRealityPayload models |
| `ai_gold_mapper.py` | Persists financial_reality |
| `schemas/scenario.py` | API field |
| `simulation-page.tsx` | Ranges + confidence UI |
| `test_financial_reality.py` | **NEW** acceptance tests |
