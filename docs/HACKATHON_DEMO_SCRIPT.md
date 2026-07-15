# Hackathon Demo Script — خزينة

**Audience:** Executive presenter  
**Duration:** 8–15 minutes (8 min with pre-warmed AI; 15 min cold)  
**Prerequisites:** Docker Compose healthy or local stack running; demo bootstrap complete

---

## 1. Environment setup (before demo)

```bash
# From repository root (Khazina/)
cd docker
docker compose up --build -d

# Migrations (if fresh DB)
cd ../backend
alembic upgrade head

# Demo assets
cd ..
python scripts/demo/generate_workbook.py
python scripts/demo/bootstrap.py

# Optional: pre-warm AI (recommended)
# Run verify_e2e once or trigger AI step manually before live demo
python scripts/demo/verify_e2e.py
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 |
| Health | http://localhost:8000/api/v1/health |

---

## 2. Demo credentials

| Field | Value |
|-------|-------|
| Email | `demo@khazina.sa` |
| Password | `DemoExec2026!` |
| Organization | مجموعة النخبة القابضة (or active org from bootstrap) |
| Demo file | `scripts/demo/Procurement_Q2.xlsx` |

---

## 3. Presenter flow (canonical)

| # | Step | UI | Narration (Arabic) | Target time |
|---|------|-----|-------------------|-------------|
| 1 | Login | `/login` | تسجيل الدخول كمستخدم تنفيذي | < 30s |
| 2 | Upload | Data Management | رفع `Procurement_Q2.xlsx` | < 30s |
| 3 | Waste analysis | Financial Waste | تشغيل كشف الهدر | < 15s |
| 4 | AI | Financial Waste | توليد التوصيات بالذكاء الاصطناعي | < 180s |
| 5 | Simulation | Business Simulation | تشغيل سيناريو تقليل الإنفاق 10% | < 20s |
| 6 | Report | Reports | إنشاء التقرير التنفيذي | < 10s |
| 7 | PDF | Reports → Export | تنزيل PDF | < 10s |
| 8 | Notifications | Header bell | عرض إشعارات الإنجاز | < 30s |
| 9 | Dashboard | `/` | تأكيد الجدول الزمني والتحليلات | optional |

---

## 4. Fallback paths

| Failure | Action |
|---------|--------|
| Ollama slow | Pre-run step 4 before demo; show cached recommendations |
| AI timeout (>180s) | Narrate latency; retry with `regenerate=false` |
| Upload fails | Re-run bootstrap; use pre-uploaded file from rehearsal |
| PDF disabled | Defaults enable PDF; patch settings if migrations applied |
| Fresh DB | `alembic upgrade head` + `python scripts/demo/bootstrap.py` |

---

## 5. Reset procedure

1. Clear browser session: logout + clear localStorage/sessionStorage  
2. Re-run `python scripts/demo/bootstrap.py` (idempotent for user/scenarios)  
3. Upload fresh `Procurement_Q2.xlsx` in UI or via `verify_e2e.py`

---

## 6. Smoke timing targets

| Step | Warm | Cold |
|------|------|------|
| Login | < 2s | < 2s |
| Upload | < 30s | < 45s |
| Waste engine | < 5s | < 15s |
| AI | < 60s | < 180s |
| Scenario | < 5s | < 20s |
| Report | < 10s | < 15s |
| PDF | < 5s | < 10s |

---

## 7. Non-demo pages

- **Risk Management** — labeled `عرض توضيحي`; no Phase 6 risk engine  
- **Dashboard KPIs/charts** — labeled `عرض توضيحي`; timeline/analyses/recommendations are live
