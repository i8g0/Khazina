# Sprint D1 — Demo User Journey Audit

**Role:** Lead UX Engineer  
**Date:** 2026-07-16  
**Scope:** Analysis only — no code changes  
**Method:** Inspection of current frontend routes, components, auth flow, demo script (`HACKATHON_DEMO_SCRIPT.md`), and post–Sprint 8.3 behavior

---

## Executive Summary

Khazina’s **core demo pipeline is functionally complete** (upload → waste → AI → simulation → report → PDF), but the **user journey is not guided**. A first-time executive lands on a **dashboard filled with five identical “no analytics yet” cards**, must discover the correct sidebar order themselves, and waits up to **three minutes on AI** with minimal progress feedback.

For a **10-minute hackathon presentation**, the canonical path works if rehearsed, but **navigation breadth, technical copy, dual upload paths, and the dashboard landing experience** create unnecessary friction and judge skepticism.

**Overall demo UX maturity:** **6.5 / 10** (functional, not yet presentation-optimized)

---

## 1. Current Journey (Step-by-Step)

### Phase A — Application startup

| Step | What happens | User sees |
|------|----------------|-----------|
| A1 | Browser opens `http://localhost:3000` | Next.js app, Arabic RTL, IBM Plex Sans Arabic |
| A2 | `AuthProvider` hydrates session from `localStorage` | **No splash, no branded loading screen** |
| A3 | If no valid session → **dev auto-login** (`demo@khazina.sa`) | Login page **skipped entirely** in local dev |
| A4 | `OrgLookupsProvider` loads departments, files, reporting period | Silent; no global progress indicator |
| A5 | Router renders `/` → `DashboardPage` | Executive shell: sidebar + header + dashboard content |

**First screen:** Dashboard (“لوحة التحكم”), not login, not data upload.

---

### Phase B — Login (when shown)

| Step | What happens | User sees |
|------|----------------|-----------|
| B1 | User navigates to `/login` or session invalid | Centered login card |
| B2 | Fields **pre-filled** with demo credentials | Email + password visible |
| B3 | Submit → `signIn()` → redirect `/` | Button: «جاري الدخول...» |
| B4 | Failure | Alert: «تعذّر تسجيل الدخول» + Arabic API error |

**Note:** Rehearsed demos often never show B1–B4 because of dev auto-login.

---

### Phase C — Dashboard (default landing)

| Step | What happens | User sees |
|------|----------------|-----------|
| C1 | Hero with org name + reporting period badge | Executive greeting |
| C2 | **5 KPI cards** | Each shows identical empty message about missing aggregation |
| C3 | **2 chart cards** | Empty states (no aggregation API) |
| C4 | Recommendations (live API) | Up to 3 cards if prior AI runs exist |
| C5 | Timeline + recent analyses (live API) | Below fold — requires scroll |

**No CTA** such as “Start by uploading data” or “Continue your analysis.”

---

### Phase D — Data upload (canonical demo step 2)

| Step | What happens | User sees |
|------|----------------|-----------|
| D1 | Sidebar → «إدارة البيانات» (`/data-management`) | Repository page |
| D2 | User selects file via `UploadDataPanel` / drag-drop | Accept `.xlsx`, `.xls`, `.csv` |
| D3 | `uploadFinancialFile` API | Panel disabled; copy: «جاري الرفع والمعالجة...» |
| D4 | Success | Alert: file name + processing status |
| D5 | `beginNewFinancialDataset()` | Clears prior analysis session IDs (Sprint 8.3) |
| D6 | File list refreshes | KPI cards update (file count, etc.) |
| D7 | Quality section | Often «لم يُقيَّم بعد» — **no auto quality run on upload** |

**No upload progress bar.** No post-upload “Next: Run waste analysis” prompt.

---

### Phase E — Waste analysis (canonical demo step 3)

| Step | What happens | User sees |
|------|----------------|-----------|
| E1 | Sidebar → «كشف الهدر» (`/financial-waste`) | Idle state if no prior run for current session |
| E2a | **Path 1:** «تشغيل تحليل الهدر» | Uses file already in session from Data Management |
| E2b | **Path 2:** «رفع ملف وتحليل» | Upload + analyze in one step on Waste page |
| E3 | `executeWasteDecision` (~seconds) | Full-page `LoadingSkeleton` |
| E4 | Results | 4 KPI cards + category table + vendor empty state |
| E5 | «توليد توصيات الذكاء الاصطناعي» | Blocked if Ollama down; else 40–180s wait |
| E6 | AI complete | Recommendation cards appear |

**Clicks from cold start (Path 1):** Dashboard → Data (1) → upload (2) → Waste (3) → run waste (4) → run AI (5) = **5+ clicks before AI wait**.

---

### Phase F — AI recommendations

| Step | What happens | User sees |
|------|----------------|-----------|
| F1 | Preflight `GET /ai/health` | Warning if Ollama unavailable |
| F2 | `generateWasteAi` | Button text only: «جاري توليد التوصيات...» |
| F3 | Success | Alert + recommendation grid |
| F4 | Failure | Generic «خطأ» + API message (may include English) |

**No progress bar, spinner with stage text, or time estimate** during the longest user-visible wait.

---

### Phase G — Simulation (canonical demo step 5)

| Step | What happens | User sees |
|------|----------------|-----------|
| G1 | Sidebar → «محاكاة الأعمال» | Scenario cards + **create-scenario form always visible** |
| G2 | Select scenario card (bootstrap seeds 3) | Highlight active scenario |
| G3 | «تشغيل السيناريو النشط» | ~instant results if waste + file in session |
| G4 | Results | Forecast KPIs, chart, comparison, impact, actions |

**No guided handoff from Waste.** User must know prerequisites (file + waste run).

---

### Phase H — Reports (canonical demo steps 6–7)

| Step | What happens | User sees |
|------|----------------|-----------|
| H1 | Sidebar → «التقارير» | Report list + stats |
| H2 | «إنشاء تقرير من تحليل الهدر» | Requires `wasteRunId` in session |
| H3 | Report appears in grid/history | Preview text from API |
| H4 | Scroll to export panel → PDF | Disabled until report generated in session |
| H5 | PDF download | Browser download `khazina-report.pdf` |

**No “workflow complete” screen.** Excel/PPTX show disabled «قريباً».

---

### Phase I — Notifications & closure (optional demo steps 8–9)

| Step | What happens | User sees |
|------|----------------|-----------|
| I1 | Header bell | Modal with recent notifications |
| I2 | Full center `/notifications` | Paginated list + preferences |
| I3 | Return to Dashboard | Timeline may show new events |

---

### Canonical 10-minute click budget (rehearsed path)

```
Open app → Data → Upload → Waste → Run waste → AI → Simulation → Run → Reports → Generate → PDF → (Bell)
   0        1      2        3         4          5       6          7       8          9        10      11
```

**Wall-clock bottleneck:** Step 5 (AI), not clicks.

---

## 2. Pain Points

| ID | Pain point | Severity | Where |
|----|------------|----------|--------|
| P1 | Dashboard landing — five duplicate empty KPI messages | Critical | `/` |
| P2 | No guided “start here” for first-time executives | Critical | Global |
| P3 | AI wait up to 180s with minimal feedback | Critical | Waste |
| P4 | Sidebar lists 10 modules including deferred Risk + admin pages | High | Navigation |
| P5 | Dual upload paths (Data vs Waste) — unclear which to use | High | Data + Waste |
| P6 | Dual waste actions («تشغيل» vs «رفع ملف وتحليل») | High | Waste |
| P7 | Dev auto-login skips login narrative | High | Auth |
| P8 | Technical copy visible to judges («API», «Ollama», model name) | High | Dashboard, Waste |
| P9 | Simulation page shows create-scenario form during demo | Medium | Simulation |
| P10 | Data quality «لم يُقيَّم بعد» after upload | Medium | Data |
| P11 | Logout (`خروج`) does not navigate explicitly to login | Medium | Header |
| P12 | Blank flash while `useRequireAuth` resolves (`return null`) | Medium | All protected pages |
| P13 | Dashboard recommendation card legacy department map unused | Low | Dashboard |
| P14 | Confidence always «بدون تصنيف ثقة» on live recs | Medium | Dashboard, Waste |
| P15 | Reports PDF requires scroll to export section | Low | Reports |
| P16 | No middleware — auth gating is client-only per page | Low | Architecture |

---

## 3. UX Problems

| Problem | Description | Impact |
|---------|-------------|--------|
| **No journey map in UI** | Product behaves as a module suite, not a single story | Judges don’t know sequence |
| **Negative first impression** | Dashboard emphasizes what is *missing* (aggregation) | Feels unfinished |
| **Cognitive overload** | Waste page: 3 primary buttons + idle workflow diagram | Decision paralysis |
| **Invisible prerequisites** | Simulation/Reports fail unless waste run exists — errors explain but don’t prevent | Recovery friction |
| **Inconsistent empty states** | Some sections excellent (vendor, charts); dashboard KPIs repetitive | Visual fatigue |
| **Admin mixed with executive** | Org/Users/Settings same nav weight as Waste | Wrong clicks during demo |
| **Risk nav trap** | Item visible; page is intentional empty state | Wasted demo time if clicked |
| **Recommendation readability** | Long LLM titles even after prefix strip | Hard to scan under pressure |
| **No completion moment** | Pipeline ends on PDF download with no summary | Anticlimactic |

---

## 4. Navigation Problems

| Issue | Detail |
|-------|--------|
| **Order vs demo script** | Sidebar: Dashboard first. Demo script: upload first. |
| **Flat 10-item nav** | No grouping (Executive / Admin / Deferred) |
| **No breadcrumbs** | Deep pages rely on sidebar highlight only |
| **No “next step” links** | Waste doesn’t link to Simulation; Reports doesn’t link from Simulation |
| **Mobile** | Hamburger + overlay — OK but adds taps on small screens |
| **Back behavior** | Browser back only; no in-app back |
| **Active state** | Gold fill on sidebar — clear enough |
| **Route naming** | URLs English (`/financial-waste`) — hidden from user |

---

## 5. Loading Problems

| Location | Loading UI | User knows what / why / how long? |
|----------|------------|-----------------------------------|
| Auth hydrate | None (blank/null) | ❌ No |
| Org lookups | None | ❌ No |
| Dashboard sections | Skeleton blocks | ⚠️ What, not why |
| Data page initial | 4 skeleton cards | ⚠️ Partial |
| Data upload | Disabled panel + text | ✅ Upload/processing |
| Waste analysis | Full skeleton | ⚠️ No “محرك القرار” label |
| **AI generation** | Button text only | ❌ **Critical gap** |
| Simulation execute | Button «جاري التنفيذ...» | ⚠️ Fast enough usually |
| Report generate | Button «جاري الإنشاء...» | ⚠️ OK |
| PDF export | Button «جاري التصدير...» | ✅ OK |
| Notification modal | «جاري التحميل...» | ✅ OK |
| Settings/Users save | Button state | ✅ OK |

**Pattern:** Short operations OK; **long AI operation lacks dedicated progress UX**.

---

## 6. Error Message Problems

| Message / pattern | Issue | Example location |
|-------------------|-------|------------------|
| Title «خطأ» only | Too generic | Most `ErrorState` usages |
| «يتطلب API تجميع لوحة التحكم» | Developer-facing | Dashboard KPI section |
| «Ollama», «qwen3.5:4b» | Infrastructure jargon | Waste AI warnings |
| «الـ API» in user admin copy | Technical | Users page footer |
| Raw backend `error.message` | May be English | Any API failure |
| «ارفع ملفاً من مستودع البيانات أولاً» | Clear but reactive | Waste/Simulation |
| «لا يوجد تقرير مرتبط بالتحليل الحالي» | Clear post–8.3 | Reports PDF |
| Login errors | Generally good Arabic | Login page |
| 401 handling | Good Arabic | `formatApiError` |

---

## 7. Missing Screens / UX Gaps

| Missing element | Why it matters |
|-----------------|----------------|
| **Demo welcome / onboarding** | First visit orientation |
| **Global auth loading shell** | Avoid blank flash |
| **Upload success → next step** | Bridge Data → Waste |
| **Waste complete → next step** | Bridge Waste → AI → Simulation |
| **AI progress modal** | Manage 60–180s expectation |
| **Pipeline progress indicator** | Show steps 1–6 completion |
| **Executive vs admin nav grouping** | Reduce wrong clicks |
| **Risk item hidden or badged «لاحقاً»** | Prevent demo detour |
| **Report preview modal** | Judge validation without PDF |
| **Workflow completion summary** | Strong demo ending |
| **Pre-demo health banner** | Ollama + backend status in UI |
| **Quality evaluation trigger** | Explain «لم يُقيَّم بعد» or auto-run |

---

## 8. Suggested Improvements

Each item includes **Priority**, **Effort**, and **Expected demo impact**.

---

### Critical

| # | Improvement | Effort | Demo impact |
|---|---------------|--------|-------------|
| C1 | **Replace dashboard landing with demo-oriented hero**: single CTA «ابدأ برفع البيانات» linking to Data Management; collapse or hide five duplicate KPI empty cards behind one executive message | Medium | Judges immediately know step 1; removes “broken product” feel |
| C2 | **AI progress modal** during `generateWasteAi`: stages («تحليل السياق»، «توليد التوصيات»)، elapsed time, cancel-safe messaging, 60–180s expectation | Medium | Prevents presenter panic; judges understand wait |
| C3 | **Demo mode nav** (env flag): show only Dashboard, Data, Waste, Simulation, Reports, Notifications — hide Risk/Org/Users/Settings or group under «إدارة» | Small | Fewer wrong clicks; saves 1–2 min |
| C4 | **Pre-warm AI in presenter checklist** (ops, not UI) + UI banner «الذكاء الاصطناعي جاهز» when `/ai/health` ok | Small | Eliminates cold-start failure in live demo |

---

### High

| # | Improvement | Effort | Demo impact |
|---|---------------|--------|-------------|
| H1 | **Unified upload entry**: one primary path — Data Management upload with post-success banner «التالي: كشف الهدر» button | Medium | Removes dual-path confusion |
| H2 | **Waste page: single primary action** when file in session — hide redundant «رفع ملف وتحليل» or demote to secondary | Small | Cleaner waste step |
| H3 | **Simulation demo mode**: hide create-scenario form; auto-select «تقليل الإنفاق 10%» with «تشغيل» as primary | Small | Less noise; faster step |
| H4 | **Replace technical copy** for judges: no «API», «Ollama», model IDs — use «خدمة الذكاء الاصطناعي» | Small | More executive, less prototype |
| H5 | **Global loading shell** while `auth.isLoading` (logo + «جاري تحميل المنصة...») | Small | Professional startup |
| H6 | **Step breadcrumb / pipeline tracker** (Upload ✓ → Waste ✓ → AI ○ → Simulation ○ → Report ○) using session artifacts | Medium | Judges see story arc |
| H7 | **Disable or badge Risk nav** («قريباً») | Small | Prevents dead-end click |
| H8 | **Reports: after generate, scroll/highlight PDF export** + success «تم إنشاء التقرير — صدّر PDF» | Small | Natural workflow end |

---

### Medium

| # | Improvement | Effort | Demo impact |
|---|---------------|--------|-------------|
| M1 | **Login page as intentional demo step**: disable dev auto-login in judge builds; keep pre-filled credentials | Small | Matches demo script narrative |
| M2 | **Upload progress indicator** (percent or indeterminate bar) on Data + Waste upload | Medium | Feedback during file transfer |
| M3 | **Waste loading label**: «جاري تشغيل محرك القرار...» on skeleton | Small | Clarifies processing |
| M4 | **Dashboard live sections first**: move timeline/analyses above empty KPI block | Small | Shows real activity sooner |
| M5 | **Remove legacy `recommendationDepartments` map** from dashboard cards | Small | Avoids confusion if IDs ever collide |
| M6 | **Logout → redirect `/login`** explicitly on signOut | Small | Clean session reset |
| M7 | **Report inline preview** (modal with executive summary) before PDF | Medium | Judge confidence without download |
| M8 | **Data quality**: either auto-snapshot on upload or hide widget until evaluated | Medium | Removes «لم يُقيَّم بعد» confusion |
| M9 | **Error titles contextualized** («تعذّر توليد التوصيات» vs «خطأ») | Small | Faster recovery |

---

### Low

| # | Improvement | Effort | Demo impact |
|---|---------------|--------|-------------|
| L1 | Password show/hide on login | Small | Minor polish |
| L2 | Notification toast on pipeline milestones (upload, waste, AI, report) | Medium | Delight; optional |
| L3 | Simulation: rename button to «تشغيل: {scenario name}» | Small | Clarity |
| L4 | Excel/PPTX export tooltips → «متاح في إصدار لاحق» vs «قريباً» | Small | Expectation setting |
| L5 | Users page: rephrase API limitation without «API» word | Small | Admin-only |
| L6 | Add `loading.tsx` per route (Next.js) for faster perceived nav | Medium | Smoother transitions |

---

## 9. Section-by-Section Audit Notes

### 4. Waste Analysis — Unnecessary clicks & feedback gaps

| Step | Unnecessary / confusing | Feedback gap |
|------|-------------------------|--------------|
| Navigate Data then Waste | Could be one guided flow | No “what’s next” after upload |
| Choose upload location | Two pages accept upload | — |
| «تشغيل» vs «رفع وتحليل» | Redundant when file exists | — |
| Run waste | — | Skeleton without label |
| Run AI | — | **No progress UI (180s)** |
| Read vendor section | Section explains empty — OK | — |
| Navigate to Simulation manually | Extra click | No completion CTA on Waste |

### 5. Simulation — Transition naturalness

**Partially natural.** Prerequisites are enforced via errors, not proactive UI. Create-scenario form competes with bootstrap scenarios. Assumptions + results layout is good once run completes.

### 6. Reports — Workflow conclusion

**Functional but not celebratory.** Generate works; PDF export is separated vertically. No prompt to view notifications or return to dashboard. Multiple historical reports may confuse which is “today’s.”

### 8. Messages — English / technical remnants

| Text | Type |
|------|------|
| `qwen3.5:4b` | Developer |
| `Ollama` | Developer (acceptable for ops, not judges) |
| `API` | Developer |
| `.xlsx`, `CSV` | Acceptable file types |
| `high risk` in AI output | English leakage from LLM (display layer) |
| `overlapping_contracts` | Mitigated by Arabic formatter on Waste |

### 10. Demo Flow — 10-minute judge risk register

| Minute | Risk | Mitigation (current / suggested) |
|--------|------|----------------------------------|
| 0–1 | Dashboard empty KPIs → “is this broken?” | **C1** demo hero |
| 1–2 | Wrong nav (Risk, Settings) | **C3** demo nav |
| 2–3 | Upload confusion | **H1** unified path |
| 3–4 | Waste button confusion | **H2** |
| 4–7 | AI silence / timeout | Pre-warm + **C2** progress modal |
| 7–8 | Simulation form noise | **H3** |
| 8–9 | Report/PDF hunt | **H8** |
| 9–10 | Weak ending | Workflow completion screen (missing) |

---

## 10. What Works Well (Preserve)

- Arabic-first RTL executive shell — polished visual language  
- Sidebar active states and executive header  
- Waste results KPIs and category table — **live data reads credibly**  
- Vendor empty state — honest, professional (post–8.3)  
- Session reset on re-upload (post–8.3)  
- Ollama health preflight (post–8.3)  
- Reports + PDF pipeline — fast once waste run exists  
- Notification bell + timeline — good “platform activity” proof  
- Risk page — clear deferred message (but shouldn’t be in demo nav path)  
- Login form — simple, pre-filled for rehearsal  

---

## 11. Recommended Demo Script Alignment (No Code — Presenter Ops)

For judges **without UI changes**, presenters should:

1. **Start at `/data-management`**, not dashboard (bookmark or direct navigate)  
2. **Pre-warm AI** via `verify_e2e.py` or one AI run before presenting  
3. **Start Ollama** before opening app  
4. **Avoid** Risk, Organization, Users, Settings in nav  
5. **Use bootstrap scenario** «تقليل الإنفاق 10%» — do not create new scenario live  
6. **Narrate AI wait** explicitly while button shows «جاري توليد التوصيات...»  
7. **Clear sessionStorage** between rehearsals (`logout` + refresh)  

---

## 12. Definition of Done (Sprint D1)

| Deliverable | Status |
|-------------|--------|
| Current journey documented | ✅ |
| Pain points | ✅ |
| UX / nav / loading / error analysis | ✅ |
| Missing screens | ✅ |
| Prioritized improvements with effort + impact | ✅ |
| No code changes | ✅ |
| No commits | ✅ |

---

## Appendix — Key Files Inspected

| Area | Files |
|------|-------|
| Auth | `lib/auth/auth-context.tsx`, `app/(shell)/login/page.tsx` |
| Routing | `lib/app-nav.tsx`, `app/(shell)/**/page.tsx` |
| Dashboard | `components/dashboard/dashboard-page.tsx`, `dashboard-charts.tsx`, `dashboard-recommendation-card.tsx` |
| Data | `components/data/data-management-page.tsx`, `upload-data-panel.tsx` |
| Waste | `components/waste/waste-page.tsx`, `waste-idle-content.tsx`, `waste-breakdown-table.tsx` |
| Simulation | `components/simulation/simulation-page.tsx` |
| Reports | `components/reports/reports-page.tsx`, `reports-export-panel.tsx` |
| Session | `lib/demo/state.ts`, `lib/demo/hooks.ts` |
| Shell | `components/layout/app-layout.tsx`, `sidebar-shell.tsx`, `notification-bell.tsx` |
| Demo script | `docs/HACKATHON_DEMO_SCRIPT.md` |

---

*End of Sprint D1 audit — analysis only.*
