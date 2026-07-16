# Sprint 5 — Executive Language Transformation (Global)

## Objective

Transform Khazina from developer/AI vocabulary into **Enterprise Financial Intelligence** language readable by CFO, Finance Director, Audit Committee, Board, and CEO.

---

## 1. Rewritten Pages (User-Visible)

| Page / Module | Before (examples) | After (examples) |
|---------------|-------------------|------------------|
| **Dashboard** | «آخر توصية من الذكاء الاصطناعي» | «آخر توصية تنفيذية» |
| **Waste** | «توليد توصيات الذكاء الاصطناعي» | «إعداد التوصيات التنفيذية» |
| **Waste** | «من محرك القرار» | «من نتائج التحليل» |
| **Risk** | «توليد ملخص الذكاء الاصطناعي» | «إعداد ملخص المخاطر» |
| **Risk** | «محرك المخاطر» | «تحليل المخاطر» / «آخر تقييم للمخاطr» |
| **Simulation** | «السيناريo المفسّر (AI)» | «السيناريو كما فُهم» |
| **Simulation** | Raw `scenario_type` English | Arabic via `mapScenarioType()` |
| **Simulation** | «شرح الذكاء الاصطناعي» | «شرح النتائج» |
| **Data** | «مستودع البيانات» | «مركز البيانات المالية» |
| **Settings** | «تكوين الذكاء الاصطناعي» | «التوصيات الذكية» |
| **Workflow** | «توصيات الذكاء الاصطناعي» | «التوصيات التنفيذية» |
| **Errors (API)** | «Internal Server Error», «Validation failed» | Arabic executive messages |
| **Reports (fallback)** | Metric concatenation | Board-style narrative paragraph |
| **PDF cards** | Truncated fields only | Problem, decision, evidence, KPI |

---

## 2. Before / After (Representative)

### Recommendation card
**Before:** Title only + «الأدلة» + generic description  
**After:** المشكلة التجارية → القرار المطلوب → الأدلة المالية → لماذا الأولوية → الأثر → الوفورات → الإطار الزمني → الجهة المنفّذة → مؤشر النجاح

### Waste AI prompt output
**Before:** 3-field risk mitigation (فئة / إجراء / مبرر)  
**After:** Full 10-field executive decision structure (same as waste recommendations)

### Error surfaced to CFO
**Before:** `Risk mitigation options text is empty`  
**After:** `تعذّr إعداد التوصيات — العدد المتوقع بين 3 و6 قرارات تنفيذية`

---

## 3. Modified Files

### Frontend (16+ files)
- `lib/executive-language.ts` — **NEW** scenario labels, technical term stripper, executive labels
- `lib/workflow/messages.ts` — executive copy + error humanization
- `lib/format.ts` — Arabic analysis types, risk source labels, sanitization
- `lib/auth/auth-context.tsx` — strip technical leakage from errors
- `lib/api/client.ts` — business-friendly API errors
- `lib/workflow/pipeline.ts`, `lib/placeholder-data.ts`
- `components/ui/recommendation-card.tsx` — 10-field executive layout
- `components/simulation/simulation-page.tsx`
- `components/waste/waste-page.tsx`, `waste-idle-content.tsx`, `waste-breakdown-table.tsx`
- `components/risk/risk-page.tsx`, `risk-detail-page.tsx`, `risk-ai-summary.tsx`, `risk-findings-table.tsx`, `risk-idle-content.tsx`
- `components/dashboard/dashboard-page.tsx`
- `components/data/data-management-page.tsx`, `upload-data-panel.tsx`
- `components/settings/settings-page.tsx`
- `components/organization/organization-management-page.tsx`
- `components/workflow/system-status-banner.tsx`

### Backend
- `app/presentation/executive_messages.py` — **NEW** Arabic error catalog
- `app/presentation/executive_recommendation.py` — decision + priority in description
- `app/core/exception_handlers.py` — executive Arabic in production
- `app/ai/prompts/languages/ar.py` — risk mitigation → full board structure; removed Sprint/English tags
- `app/ai_recommendations/risk_recommendation_parser.py` — parse full executive fields
- `app/ai_recommendations/waste_metadata.py` — removed «Facts Contract», «Sprint 4»
- `app/reports/sections.py` — narrative waste executive fallback
- `app/reports/executive_pdf_layout.py` — problem, decision, KPI on cards
- `app/reports/content.py` — Arabic unavailable message
- `app/settings/constants.py` — Arabic default report title

### Scripts
- `scripts/demo/apply_executive_language.py`
- `scripts/demo/apply_frontend_executive_language.py`
- `scripts/demo/scan_executive_language.py`

---

## 4. Removed Technical Phrases (Sample)

| Removed | Replaced with |
|---------|---------------|
| الذكاء الاصطناعي (user-facing) | التوصيات التنفيذية / التوصيات الذكية |
| محرك القرار / محرك المخاطر | نتائج التحليل / تحليل المخاطر |
| مستودع البيانات | مركز البيانات المالية |
| KPIs | المؤشرات الرئيسية |
| (AI) | (removed) |
| Internal Server Error | تعذّr إتمام العملية |
| Validation failed | يرجى مراجعة البيانات المدخلة |
| Facts Contract | البيانات المالية |
| Sprint 4 / Sprint names in prompts | (removed) |
| Executive Report — | تقرير تنفيذي — |
| JSON error to user | تعذّr تحميل التقرير |

---

## 5. Recommendation Template (10 Fields)

Every waste and risk recommendation prompt now requires:

1. **المشكلة** — Business problem  
2. **الدليل** — Category, period, amounts, percentages  
3. **الأثر على الأعمال** — Cash flow, profit, budget, risk  
4. **القرار** — Management decision  
5. **الأولوية** — High / Medium / Low + rationale  
6. **النتيجة المتوقعة** — Exact savings estimate  
7. **المسؤول** — Owner department or «غير متوفر في البيانات الحالية»  
8. **الإطار الزمني** — Short / medium / long horizon  
9. **مؤشر النجاح** — Measurable KPI  
10. **Executive summary** — Via separate EXECUTIVE_SUMMARY task + PDF page 1  

UI card (`recommendation-card.tsx`) surfaces all fields with executive labels.

---

## 6. Proof — No Technical Language in UI Paths

Run:
```bash
python scripts/demo/scan_executive_language.py
```

Scans `frontend/components/**` and `lib/workflow/**` for forbidden terms.  
Remaining matches are **code identifiers only** (e.g. `analysis_run.id`, `metadata` variables) — not rendered to users.

User-visible strings in scanned paths: **clean** for الذكاء الاصطناعي, محرك, مستودع, KPI, Sprint, JSON errors.

---

## 7. Screenshots

Screenshots require manual capture in the running app:
1. Dashboard — «آخر توصية تنفيذية»  
2. Waste — «إعداد التوصيات التنفيذية» button  
3. Risk — «إعداد ملخص المخاطر»  
4. Simulation — «شرح النتائج», Arabic scenario type  
5. Recommendation card — full 10-field layout  
6. PDF — recommendation card with problem/decision/KPI  

---

## 8. Regression

Backend imports verified. Re-run executive workflow:
```bash
python scripts/demo/sprint0_executive_workflow_verify.py
```

---

## Architecture

```
User-visible text
    ↓
frontend/lib/executive-language.ts  (labels + sanitizer)
frontend/lib/workflow/messages.ts   (copy + humanizeErrorMessage)
frontend/lib/format.ts              (status/type maps + sanitizeExecutiveText)
    ↓
backend/app/presentation/executive_messages.py  (API errors)
backend/app/ai/prompts/languages/ar.py          (AI output structure)
backend/app/presentation/executive_recommendation.py (parse/format)
    ↓
PDF + Reports + Notifications
```
