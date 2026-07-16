# PDF Executive Review

**Date:** 2026-07-16  
**Phase:** 1 — Investigation ONLY  
**Verdict:** PDF renderer is **NOT executive-ready** despite Sprint 2 Arabic infrastructure fixes

---

## Required Executive Structure vs Actual

| Required section | Waste report | Risk report | Simulation report |
|------------------|--------------|-------------|-------------------|
| Executive Summary | ✅ `executive_summary` | ✅ risk summary sections | ✅ scenario overview |
| Financial Highlights | ⚠️ via `key_metrics` (technical) | ⚠️ same | ⚠️ partial |
| Waste Analysis | ✅ `waste_analysis` | N/A | N/A |
| Risk Analysis | N/A | ✅ `top_risks`, etc. | N/A |
| Scenario Analysis | N/A | N/A | ✅ forecast sections |
| Strategic Recommendations | ✅ `recommendations` | ✅ | ✅ `impact_and_actions` |
| Financial Impact | ⚠️ embedded in text | ⚠️ partial | ✅ |
| Priority Actions | ⚠️ in recommendations | ⚠️ | ✅ action_items |
| Appendix | ❌ **Technical provenance** | ❌ same | ❌ scenario_provenance |

**Structure exists in section builder; presentation layer fails executive bar.**

---

## Sprint 2 Improvements (Verified)

| Fix | File | Status |
|-----|------|--------|
| Noto Naskh Arabic font | `pdf_renderer.py` + TTF asset | ✅ Embedded |
| arabic-reshaper + python-bidi | `requirements.txt` | ✅ |
| List expansion for nested items | `pdf_renderer.py` `_LIST_ITEM_KEYS` | ✅ |
| Page numbers | `pdf_renderer.py` | ✅ |
| Arabic section titles | `_ARABIC_LABELS` map | ✅ |
| Arabic report titles | `settings/resolver.py` | ✅ |
| Smoke test | `test_pdf_export.py` | ✅ Pass |

---

## Critical Defects (Production Blockers)

### PDF-01: Cover business data skipped

**Root cause:** Synthetic cover page renders `report_title`, `platform_name`, `profile` (English code), ISO `generated_at` — then **skips** persisted `cover` section payload.

**Evidence:** `pdf_renderer.py:304-348` synthetic cover; `353-354` skips `key == "cover"` section.

**Missing from PDF:**
- Organization name
- Period label
- Source file name
- Run completion date (localized)

**Impact:** User issue #7 — important business data hidden.

### PDF-02: key_metrics dumps Facts Contract

**Root cause:** `build_key_metrics_section()` serializes `_fact_dicts(facts)` with internal metric keys.

**Evidence:** `sections.py:111-118`

```python
payload: dict[str, Any] = {"facts": _fact_dicts(facts)}
```

**Impact:** User issues #3, #8 — `waste.top_category`, engine IDs, contract version in executive PDF.

### PDF-03: Provenance appendix exposes technical metadata

**Root cause:** `build_waste_provenance_section()` includes:
- `facts_contract_version`
- `engine_id`, `engine_version`
- Analysis run UUIDs
- AI model metadata

**Evidence:** `sections.py:181-207`

**Impact:** User issue #8 — technical garbage in appendix.

### PDF-04: Risk report section ordering

**Root cause:** Risk profile assembly may place `key_metrics` at high sort index (999), appearing after recommendations instead of in Financial Highlights position.

**Impact:** Illogical executive flow.

### PDF-05: Arabic truncation

**Root cause:** `_draw_line` / text wrapping uses ~120 character limits in places — truncates Arabic mid-word.

**Impact:** User issue #6 — poor Arabic rendering for long labels.

### PDF-06: English profile codes on cover

**Evidence:** `pdf_renderer.py:326-336` — `profile` rendered as raw code (e.g. `waste_executive`), not localized label.

### PDF-07: Wrong report exported (upstream)

Not a renderer bug — `resolveExportReportId()` may pass wrong `report_id`. Renderer faithfully renders wrong content.

**Evidence:** `report-export.ts:38-42` risk run prioritized over waste.

### PDF-08: AI recommendation text in PDF

Recommendations section pulls same unsanitized AI text as UI — includes metric key leakage.

---

## What Must NOT Appear (Audit Checklist)

| Forbidden content | Present today | Location |
|-------------------|---------------|----------|
| `facts_contract` | ✅ Yes | key_metrics.facts |
| Internal metric keys (`waste.*`) | ✅ Yes | key_metrics, recommendations |
| `engine_id` / UUIDs | ✅ Yes | provenance |
| `metadata` JSON | ✅ Yes | provenance, scenario_provenance |
| Debug `source` fields | ✅ Yes | executive_summary payload |
| Raw JSON blobs | ⚠️ Partial | Nested payload formatting |

---

## Renderer Architecture

```
Report DB row → content JSON (sections[])
    → pdf_renderer.render_pdf()
        → Synthetic cover (title only)
        → For each section: _format_payload_lines()
            → Recursive key-value with _ARABIC_LABELS
            → Lists expanded for items/facts/etc.
```

**Gap:** No executive sanitization layer between persisted content and line formatting.

---

## Recommended Fix Design (Phase 2)

### Executive Safe Mode (default for demo)

1. **Cover:** Merge synthetic title page WITH `cover` section fields (org, period, file, dates)
2. **key_metrics:** Render headline numbers only; map facts to Arabic labels; drop raw contract
3. **provenance:** Omit from demo PDF OR render single line "Generated by Khazina Platform"
4. **Recommendations:** Use sanitized executive text (same fix as AI quality)
5. **Profile label:** Use `format_report_title()` output, not raw code
6. **Dates:** Apply `date_display_format` from org settings

### Regression tests

- Extend `test_pdf_export.py`:
  - Assert PDF bytes do not contain `waste.top_category`, `engine_id`, `facts_contract_version`
  - Assert cover contains organization name when present in section payload
  - Arabic string integrity (no mojibake; minimum length preserved)

---

## Acceptance Criteria (FINAL RULE)

PDF bug closed only when:
1. Real UI workflow → export PDF → open file → executive sections readable in Arabic
2. No technical keys in document text search
3. Org name, period, file name visible on cover
4. F5 + re-export same report → identical content
5. Waste/risk/simulation exports each match selected domain

**Phase 1 complete. No code modified.**
