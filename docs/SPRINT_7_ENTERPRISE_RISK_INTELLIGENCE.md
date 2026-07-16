# Sprint 7 — Enterprise Risk Intelligence & Demo Hardening

## Summary

Transformed the Risk module from developer-style English templates into a **CFO-ready Arabic risk center** with data-backed findings, executive cards, enriched matrix/charts, and a 20k-row enterprise demo dataset.

**Sprint 6 (Financial Reality) preserved** — all `test_financial_reality.py` tests pass.

---

## PART A–G: Executive Risk Intelligence

### Backend — Risk Engine (`financial_reality` unchanged; risk engine upgraded)

| Change | File |
|--------|------|
| Arabic finding titles & descriptions | `rules/__init__.py` |
| Executive evidence (department, supplier, exposure, savings, owner, timeline) | `rules/evidence.py`, `rules/ar.py` |
| Department/supplier aggregation from uploaded rows | `decision/adapters/risk_v1.py` |
| Category & department hotspot rules (data-driven) | `rules/__init__.py` |
| Extended metrics on calculator | `calculator.py`, `input.py` |

Every finding now includes in `evidence`:
- `department_ar`, `supplier_ar`, `amount_exposed_label`
- `estimated_savings_label`, `recommended_action_ar`
- `owner_ar`, `target_timeline_ar`, `confidence_score`
- `executive_summary_ar`, `if_ignored_ar`, `business_impact_ar`

**No evidence = no finding** — rules return empty tuple when thresholds not met.

### Frontend

| Component | Change |
|-----------|--------|
| `risk-executive-card.tsx` | **NEW** — full 16-field executive card |
| `risk-page.tsx` | Executive cards grid, matrix click-to-detail |
| `risk-priority-matrix.tsx` | Arabic tooltips, department chips, selection |
| `risk-charts.tsx` | Exposure by dept/supplier, savings, top 10 |
| `mappers.ts` | Evidence extraction, chart builders from findings |

---

## PART I: Enterprise Dataset

**File:** `Demo_Enterprise_Dataset_v2.xlsx`

| Metric | Value |
|--------|-------|
| Rows | 20,500 |
| Departments | 12 (Arabic names) |
| Suppliers | 120 |
| Total spend | 285M SAR |
| Total waste | ~22M SAR (7.72%) |
| Ingestion quality | 99.76 |

**Generator:** `scripts/demo/generate_enterprise_dataset_v2.py`

Includes scenarios: duplicates, budget overruns, subscriptions, late payments, vendor concentration.

Schema: W-1 core (`category`, `amount`, `total_spend`) + `department`, `supplier`, `transaction_type`, `planned_amount`, `spent_amount`.

---

## PART J–K: Organizations & Users (Audit)

| Module | Status |
|--------|--------|
| Org edit, departments, reporting periods | Working (FE + BE) |
| User CRUD, roles, deactivate | Working |
| Org switch / multi-tenant | Not in MVP scope |
| FE RBAC | Gap (KHZ-007) — documented, not Sprint 7 scope |
| Department PATCH UI | Gap (KHZ-038) — API exists |

No regressions introduced to org/user flows.

---

## PART H / L / M: Regression

```bash
cd Khazina/backend
python -m pytest tests/business/test_risk_executive_s7.py tests/business/test_risk_engine.py tests/scenario/test_financial_reality.py -v
```

**Result:** 19/19 passed (Sprint 6 + Sprint 7 risk tests).

Full workflow (requires running backend + Ollama):

```bash
python scripts/demo/sprint0_executive_workflow_verify.py
```

---

## Before / After — Risk Findings

| Before | After |
|--------|-------|
| "Elevated financial waste exposure" | "تعرّض مالي مرتفع — هدر X% من الإنفاق" |
| No department | `department_ar` from category/data |
| No supplier | `supplier_ar` when dataset has suppliers |
| No financial exposure | `amount_exposed_label` in SAR |
| Empty matrix chips | Arabic title + department + tooltip |
| Department chart empty until promote | Built from findings evidence |
| Generic English descriptions | Arabic executive narrative + if ignored |

---

## Remaining Issues

1. **Strategic/forecast rules** — still require `simulation_summary` in decision service (deferred).
2. **FE RBAC** — all roles see admin pages (KHZ-007).
3. **Risk GET IDOR** — KHZ-008 (pre-existing).
4. **Budget variance rule** — needs `budget`/`actual` columns on snapshot (enterprise dataset uses `planned_amount`/`spent_amount` to avoid W-1 conflict).

---

## Files Changed (Sprint 7)

**Backend:** `rules/__init__.py`, `rules/ar.py`, `rules/evidence.py`, `calculator.py`, `input.py`, `detector.py`, `risk_v1.py`, `constants.py`, `test_risk_executive_s7.py`

**Frontend:** `risk-page.tsx`, `risk-charts.tsx`, `risk-priority-matrix.tsx`, `risk-executive-card.tsx`, `mappers.ts`, `view-types.ts`

**Data:** `Demo_Enterprise_Dataset_v2.xlsx`, `generate_enterprise_dataset_v2.py`
