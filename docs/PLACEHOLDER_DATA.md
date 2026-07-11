# Khazina — Official Placeholder Data

This document is the **single source of truth** for all frontend placeholder content until live backend and AI integrations replace it.

For page structure, see [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md). For component usage, see [COMPONENT_SPECIFICATION.md](COMPONENT_SPECIFICATION.md).

---

## Usage Rules

1. Import placeholder values from a shared module (`frontend/lib/placeholder-data.ts`) when pages are implemented — do not hardcode duplicate strings in page files.
2. All user-facing text must be **Arabic only**.
3. Values must remain **internally consistent** across pages (same departments, same currency format, same date references).
4. Replace placeholder data with API responses in Phase 7+ without changing page layout specifications.
5. Never invent new placeholder entities in page implementations without updating this document first.
6. Use file names from [Unified Placeholder File List](#unified-placeholder-file-list) consistently across all pages — no duplicate naming conventions.

---

## Organization Context

| Field | Value |
|-------|-------|
| Organization name | مجموعة النخبة القابضة |
| Platform name | خزينة |
| Currency | ريال سعودي (ر.س) |
| Currency symbol | ر.س |
| Locale | ar-SA |
| Fiscal year | 2026 |
| Reporting period | الربع الثاني 2026 |
| Executive user title | الرئيس التنفيذي للشؤون المالية |

---

## Departments

| ID | Name | Short name |
|----|------|------------|
| dept-finance | الشؤون المالية | المالية |
| dept-procurement | المشتريات | المشتريات |
| dept-operations | العمليات | العمليات |
| dept-hr | الموارد البشرية | الموارد البشرية |
| dept-it | تقنية المعلومات | تقنية المعلومات |
| dept-compliance | الامتثال | الامتثال |
| dept-audit | المراجعة الداخلية | المراجعة |
| dept-legal | الشؤون القانونية | القانونية |

---

## Unified Placeholder File List

These file names are reused consistently across Dashboard, Reports, Waste Detection, Data Management, Recent Analyses, and Import History.

| ID | File name | Department | Size | Typical use |
|----|-----------|------------|------|-------------|
| file-001 | Budget_Q2_2026.xlsx | الشؤون المالية | 890 KB | Budget review, reports |
| file-002 | Supplier_Contracts.xlsx | المشتريات | 3.8 MB | Supplier analysis, waste detection |
| file-003 | Procurement_Q2.xlsx | المشتريات | 2.4 MB | Procurement waste, dashboard analyses |
| file-004 | Payroll_2026.xlsx | الموارد البشرية | 1.6 MB | HR cost analysis |
| file-005 | Operating_Costs.xlsx | العمليات | 1.1 MB | Operating cost trends |

Do not introduce alternate spellings or Arabic-transliterated variants of these file names in page implementations.

---

## Financial Summary (Dashboard)

| Metric | Value | Change | Period |
|--------|-------|--------|--------|
| Total analyzed spend | 48,750,000 | +3.2% | الربع الثاني 2026 |
| Detected waste | 2,340,000 | -8.4% | الربع الثاني 2026 |
| Potential savings | 1,875,000 | +12.1% | الربع الثاني 2026 |
| Active risks | 7 | +1 | الحالي |
| Open recommendations | 14 | -2 | الحالي |
| Reports generated | 23 | +5 | 2026 |

---

## KPI Cards (Dashboard)

Use exactly five KPI cards on the Dashboard page. Each KPI includes a department context badge.

| Label | Value | Department badge | Hint | Trend |
|-------|-------|------------------|------|-------|
| إجمالي الهدر المالي المكتشف | 2.34M ر.س | المشتريات | الربع الثاني 2026 | -8.4% تحسّن |
| عدد المخاطر الحرجة | 3 | العمليات | 7 مخاطر نشطة | +1 |
| التوفير المتوقع | 1.875M ر.س | تقنية المعلومات | 14 توصية نشطة | +12.1% |
| آخر توصية من الذكاء الاصطناعي | دمج عقود الموردين | الموارد البشرية | ثقة 92% | — |
| حالة آخر تحليل | مكتمل | الامتثال | Procurement_Q2.xlsx | 2026-06-28 |

---

## Months (Charts)

Use for time-series chart labels (RTL order: oldest to newest left-to-right in data array, display RTL):

```
يناير، فبراير، مارس، أبريل، مايو، يونيو
```

Quarter label: **الربع الثاني 2026**

---

## Dashboard Charts

### Chart 1 — توزيع الهدر حسب الإدارات

| Department | Waste (ر.س) |
|------------|-------------|
| المشتريات | 745,000 |
| العمليات | 520,000 |
| الشؤون المالية | 310,000 |
| تقنية المعلومات | 185,000 |
| الموارد البشرية | 95,000 |

### Chart 2 — اتجاه الهدر المالي

Use **Waste Chart Series (Monthly)** in Financial Waste Detection section below.

---

## Expense Categories

| ID | Name |
|----|------|
| cat-travel | السفر والانتدابات |
| cat-suppliers | الموردون والمقاولون |
| cat-it | تقنية المعلومات |
| cat-facilities | المرافق والصيانة |
| cat-marketing | التسويق والعلاقات |
| cat-hr | الموارد البشرية |

---

## Supplier Names

| ID | Name | Category |
|----|------|----------|
| sup-001 | شركة الخليج للتوريدات | الموردون والمقاولون |
| sup-002 | مؤسسة التقنية المتقدمة | تقنية المعلومات |
| sup-003 | مجموعة السفر المؤسسي | السفر والانتدابات |
| sup-004 | شركة المرافق الذكية | المرافق والصيانة |
| sup-005 | وكالة الإبداع للتسويق | التسويق والعلاقات |

---

## Financial Waste Detection

### Upload Placeholder Files

Reference [Unified Placeholder File List](#unified-placeholder-file-list). Display status as **جاهز للتحليل** when shown in upload context.

| File name | Department | Size | Status |
|-----------|------------|------|--------|
| Procurement_Q2.xlsx | المشتريات | 2.4 MB | جاهز للتحليل |
| Operating_Costs.xlsx | العمليات | 1.1 MB | جاهز للتحليل |
| Supplier_Contracts.xlsx | المشتريات | 3.8 MB | جاهز للتحليل |

### Waste Analysis Results

| Category | Amount (ر.س) | Percentage | Department |
|----------|-------------|------------|------------|
| تكرار طلبات الشراء | 420,000 | 17.9% | المشتريات |
| أسعار موردين مرتفعة | 680,000 | 29.1% | المشتريات |
| سفر غير ضروري | 310,000 | 13.2% | الشؤون المالية |
| اشتراكات غير مستخدمة | 185,000 | 7.9% | تقنية المعلومات |
| عقود متداخلة | 745,000 | 31.9% | العمليات |

### Waste Chart Series (Monthly)

| Month | Detected waste (ر.س) |
|-------|---------------------|
| يناير | 380,000 |
| فبراير | 410,000 |
| مارس | 395,000 |
| أبريل | 420,000 |
| مايو | 390,000 |
| يونيو | 345,000 |

### Waste Recommendations

| ID | Title | Description | Priority | Confidence | Savings (ر.س) |
|----|-------|-------------|----------|------------|---------------|
| rec-w01 | دمج عقود الموردين المتداخلة | توحيد 3 عقود مع مؤسسة التقنية المتقدمة لتقليل التكلفة السنوية | عالية | 92% | 520,000 |
| rec-w02 | مراجعة سياسة السفر | تطبيق موافقة مسبقة للرحلات فوق 15,000 ر.س | متوسطة | 87% | 180,000 |
| rec-w03 | إلغاء اشتراكات غير مستخدمة | 12 اشتراك برمجي بدون استخدام خلال 90 يوماً | عالية | 95% | 95,000 |
| rec-w04 | إعادة التفاوض مع شركة الخليج | أسعار أعلى 18% من متوسط السوق | عالية | 89% | 340,000 |

---

## Risk Management

### Risk Overview

| Level | Count |
|-------|-------|
| عالية | 3 |
| متوسطة | 2 |
| منخفضة | 2 |

### Risk Items

| ID | Name | Description | Priority | Score | Department | Status |
|----|------|-------------|----------|-------|------------|--------|
| risk-001 | تجاوز الميزانية التشغيلية | تجاوز 8% عن ميزانية Q2 في المشتريات | عالية | 87 | المشتريات | نشط |
| risk-002 | تركّز الموردين | 62% من الإنفاق مع 3 موردين فقط | عالية | 82 | المشتريات | نشط |
| risk-003 | تأخر تحصيل الذمم | متوسط التحصيل 47 يوماً | متوسطة | 65 | الشؤون المالية | نشط |
| risk-004 | فجوة الامتثال | 2 عملية بدون موافقة مطلوبة | عالية | 78 | العمليات | قيد المعالجة |
| risk-005 | تقلب أسعار الصرف | تأثير 3.2% على تكلفة الواردات | متوسطة | 58 | الشؤون المالية | نشط |
| risk-006 | نقص البيانات | 15% من السجلات بدون تصنيف | منخفضة | 42 | تقنية المعلومات | نشط |
| risk-007 | تأخر تقارير الموردين | 4 موردين متأخرين عن الجدول | منخفضة | 38 | المشتريات | نشط |

### Risk Chart Data (By Category)

| Category | Score |
|----------|-------|
| مالي | 78 |
| تشغيلي | 65 |
| امتثال | 82 |
| استراتيجي | 55 |
| تقني | 42 |

### Risk Recommendations

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| rec-r01 | تنويع قاعدة الموردين | تقليل الاعتماد على 3 موردين رئيسيين إلى أقل من 40% | عالية |
| rec-r02 | تفعيل تنبيهات الميزانية | تنبيه تلقائي عند 90% من حد الميزانية | عالية |
| rec-r03 | مراجعة سياسة التحصيل | تقليل متوسط أيام التحصيل إلى 35 يوماً | متوسطة |

### Timeline Events

| Date | Event | Type |
|------|-------|------|
| 2026-06-28 | اكتشاف تجاوز ميزانية المشتريات | تنبيه |
| 2026-06-25 | تحليل مخاطر الموردين مكتمل | تحليل |
| 2026-06-20 | مراجعة امتثال العمليات | مراجعة |
| 2026-06-15 | تحديث نموذج تقييم المخاطر | نظام |
| 2026-06-10 | تقرير المخاطر الربعي | تقرير |

---

## Business Simulation

### Scenarios

| ID | Name | Description | Status |
|----|------|-------------|--------|
| sim-001 | تقليل الإنفاق 10% | محاكاة خفض الإنفاق التشغيلي 10% عبر جميع الأقسام | مكتمل |
| sim-002 | دمج الموردين | محاكاة دمج 5 موردين إلى 3 | مسودة |
| sim-003 | توسع السوق الخليجي | محاكاة زيادة 15% في الإيرادات مع تكلفة توسع | مسودة |

### Simulation Forecast Cards

| Scenario | Baseline (ر.س) | Projected (ر.س) | Delta | Confidence |
|----------|---------------|-----------------|-------|------------|
| sim-001 | 48,750,000 | 43,875,000 | -10.0% | 88% |
| sim-002 | 12,400,000 | 10,540,000 | -15.0% | 85% |
| sim-003 | 62,000,000 | 68,200,000 | +10.0% | 72% |

### Simulation Chart Series (sim-001)

| Quarter | Baseline | Projected |
|---------|----------|-----------|
| Q3 2026 | 16,250,000 | 14,625,000 |
| Q4 2026 | 16,250,000 | 14,625,000 |
| Q1 2027 | 16,250,000 | 14,625,000 |

### Comparison Cards

| Metric | Current | Simulated | Change |
|--------|---------|-------------|--------|
| إجمالي الإنفاق | 48.75M | 43.88M | -10.0% |
| عدد الموردين | 47 | 32 | -31.9% |
| متوسط تكلفة العقد | 265,000 | 228,000 | -14.0% |

---

## Reports

### Report List

| ID | Title | Type | Department | Source file | Date | Status |
|----|-------|------|------------|-------------|------|--------|
| rep-001 | تقرير الهدر المالي — Q2 2026 | تحليل | الشؤون المالية | Procurement_Q2.xlsx | 2026-06-30 | جاهز |
| rep-002 | تقييم المخاطر الربعي | مخاطر | العمليات | Operating_Costs.xlsx | 2026-06-25 | جاهز |
| rep-003 | ملخص محاكاة تقليل الإنفاق | محاكاة | الشؤون المالية | Budget_Q2_2026.xlsx | 2026-06-20 | جاهز |
| rep-004 | تحليل الموردين | مشتريات | المشتريات | Supplier_Contracts.xlsx | 2026-06-15 | مسودة |
| rep-005 | تقرير الامتثال الشهري | امتثال | العمليات | Payroll_2026.xlsx | 2026-06-01 | جاهز |

### Future Export Options (Backend)

Reports may later support export via backend endpoints. **Do not implement in frontend MVP.**

| Format | Endpoint (proposed) |
|--------|---------------------|
| PDF | `GET /api/v1/reports/{id}/export?format=pdf` |
| Excel | `GET /api/v1/reports/{id}/export?format=xlsx` |
| PowerPoint | `GET /api/v1/reports/{id}/export?format=pptx` |

### Report Filters (Default Options)

| Filter | Options |
|--------|---------|
| النوع | الكل، تحليل، مخاطر، محاكاة، مشتريات، امتثال |
| القسم | الكل، الشؤون المالية، المشتريات، العمليات |
| الفترة | آخر 30 يوماً، الربع الحالي، 2026 |

---

## Data Management

### Uploaded Files

Reference [Unified Placeholder File List](#unified-placeholder-file-list).

| ID | File name | Department | Upload date | Size | Status |
|----|-----------|------------|-------------|------|--------|
| file-001 | Budget_Q2_2026.xlsx | الشؤون المالية | 2026-06-18 | 890 KB | مكتمل |
| file-002 | Supplier_Contracts.xlsx | المشتريات | 2026-06-22 | 3.8 MB | قيد المعالجة |
| file-003 | Procurement_Q2.xlsx | المشتريات | 2026-06-28 | 2.4 MB | مكتمل |
| file-004 | Payroll_2026.xlsx | الموارد البشرية | 2026-06-15 | 1.6 MB | فشل |
| file-005 | Operating_Costs.xlsx | الشؤون المالية | 2026-06-25 | 1.1 MB | مكتمل |

### Import History

| Date | File | Records | Status |
|------|------|---------|--------|
| 2026-06-28 | Procurement_Q2.xlsx | 4,820 | نجح |
| 2026-06-25 | Operating_Costs.xlsx | 1,240 | نجح |
| 2026-06-22 | Supplier_Contracts.xlsx | — | قيد المعالجة |
| 2026-06-18 | Budget_Q2_2026.xlsx | 2,150 | نجح |
| 2026-06-15 | Payroll_2026.xlsx | — | فشل — تنسيق غير مدعوم |

### Validation Summary

| Check | Result | Details |
|-------|--------|---------|
| اكتمال الحقول | 94% | 312 سجل بدون تصنيف |
| تطابق الميزانية | 98% | 2 تجاوزات |
| تنسيق التاريخ | 100% | — |
| تكرار السجلات | 99.2% | 38 سجل مكرر |

---

## Recent Analyses (Dashboard)

Maximum 5 rows. Source files must match [Unified Placeholder File List](#unified-placeholder-file-list).

| ID | Title | Type | Source file | Date | Status |
|----|-------|------|-------------|------|--------|
| ana-001 | تحليل هدر المشتريات Q2 | هدر مالي | Procurement_Q2.xlsx | 2026-06-28 | مكتمل |
| ana-002 | تقييم مخاطر الموردين | مخاطر | Supplier_Contracts.xlsx | 2026-06-25 | مكتمل |
| ana-003 | محاكاة تقليل الإنفاق | محاكاة | Budget_Q2_2026.xlsx | 2026-06-20 | مكتمل |
| ana-004 | مراجعة تكاليف التشغيل | تشغيلي | Operating_Costs.xlsx | 2026-06-18 | مكتمل |
| ana-005 | تحليل الرواتب | موارد بشرية | Payroll_2026.xlsx | 2026-06-15 | قيد المعالجة |

---

## Data Table Samples

### Waste Detection Table

| المورد | الفئة | المبلغ (ر.س) | الانحراف | الحالة |
|--------|-------|-------------|----------|--------|
| شركة الخليج للتوريدات | الموردون | 680,000 | +18% | يتطلب مراجعة |
| مؤسسة التقنية المتقدمة | تقنية | 420,000 | +12% | يتطلب مراجعة |
| مجموعة السفر المؤسسي | السفر | 310,000 | +25% | حرج |

### Risk Table

| المخاطرة | الأولوية | النتيجة | القسم | الحالة |
|----------|----------|---------|-------|--------|
| تجاوز الميزانية | عالية | 87 | المشتريات | نشط |
| تركّز الموردين | عالية | 82 | المشتريات | نشط |
| تأخر التحصيل | متوسطة | 65 | المالية | نشط |

---

## Confidence Percentages

Use consistently across recommendations and AI outputs:

| Range | Label |
|-------|-------|
| 90–100% | ثقة عالية |
| 75–89% | ثقة جيدة |
| 60–74% | ثقة متوسطة |
| Below 60% | ثقة منخفضة |

---

## Empty State Messages

| Context | Title | Description |
|---------|-------|-------------|
| Dashboard — no data | لا توجد بيانات بعد | ارفع ملفات مالية لبدء التحليل |
| Waste — no upload | لم يتم رفع ملفات | ارفع ملف Excel لبدء كشف الهدر |
| Risk — no risks | لا توجد مخاطر | سيتم عرض المخاطر بعد تحليل البيانات |
| Simulation — no scenarios | لا توجد سيناريوهات | أنشئ سيناريو جديد لبدء المحاكاة |
| Reports — no reports | لا توجد تقارير | سيتم إنشاء التقارير بعد إتمام التحليلات |
| Data — no files | لا توجد ملفات | ارفع ملفات Excel أو CSV للبدء |

---

## Related Documents

- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — Page specifications
- [COMPONENT_SPECIFICATION.md](COMPONENT_SPECIFICATION.md) — Component specifications
- [ARCHITECTURE.md](ARCHITECTURE.md) — Frontend architecture
