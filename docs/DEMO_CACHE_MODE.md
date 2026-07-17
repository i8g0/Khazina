# Demo Cache Mode (TEMPORARY — Hackathon Only)

> **WARNING:** This feature is for **local hackathon presentations only**.  
> It must **never** be merged into production. After the event, delete `backend/app/demo_cache/`, revert related wiring in `main.py` and `deps.py`, and remove `demo_cache/` data.

## Purpose

Make the full Khazina executive workflow feel instant on a local machine by replaying **genuine API responses** captured after one successful live run. The frontend behaves identically; JSON contracts are unchanged.

Nothing is fabricated:

- No fake AI text
- No altered financial calculations
- No modified API schemas

Only outputs from a real successful execution are stored and replayed.

## Architecture

```
┌─────────────┐     HTTP      ┌──────────────────────────────┐
│  Frontend   │ ────────────► │  FastAPI + DemoCacheMiddleware│
└─────────────┘               │  DEMO_CACHE_MODE=true         │
                              │         │                     │
                              │    cache hit?                 │
                              │    ├─ yes → demo_cache/       │
                              │    └─ no  → Live Execution    │
                              └──────────────────────────────┘
```

### Components (all temporary)

| Path | Role |
|------|------|
| `backend/app/demo_cache/` | Isolated cache module (middleware, store, AI wrapper) |
| `demo_cache/` | Root cache folder (responses, binary, AI transcripts, manifest) |
| `scripts/demo/warm_demo_cache.py` | Runs full workflow once and populates cache |

### Cache structure

```
demo_cache/
├── README.md
├── manifest.json          # golden UUIDs + warm metadata
├── responses/             # JSON API payloads keyed by normalized route
├── binary/                # (reserved; PDFs stored in responses as base64)
├── ai/                    # Genuine LLM outputs keyed by prompt hash
└── dataset/               # Copy of warmed Excel file (optional reference)
```

Cache keys normalize UUID path segments to `{id}` so the same cached response serves any org/run ID that matches the warmed demo database state.

## Prerequisites

1. PostgreSQL with demo org bootstrapped (`python scripts/demo/bootstrap.py`)
2. Backend running on `http://localhost:8000`
3. Demo workbook: `python scripts/demo/generate_workbook.py`

## Warm the cache (one time)

Run with **live execution** (expensive — ~minutes):

```bash
# backend/.env
DEMO_CACHE_MODE=false
DEMO_CACHE_RECORD=true
```

Restart backend, then:

```bash
cd Khazina
python scripts/demo/warm_demo_cache.py
```

This executes:

1. Login → Upload → Waste → AI → Risk → Risk AI → Simulation → Report → PDF  
2. Dashboard, notifications, and all read endpoints used by the UI  
3. Saves every response under `demo_cache/`

**Important:** Use the **same database** for warming and presentation. Cached responses reference golden IDs stored in `manifest.json` that must exist in PostgreSQL.

## Enable demo mode (presentation)

```bash
# backend/.env
DEMO_CACHE_MODE=true
DEMO_CACHE_RECORD=false
```

Restart backend:

```bash
cd backend
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start frontend as usual (`pnpm dev`). Logs show:

- `Demo Cache HIT: GET /organizations/{id}/...` — instant replay  
- `Live Execution: ...` — cache miss, normal GitHub behavior  

## Disable demo mode

```bash
DEMO_CACHE_MODE=false
DEMO_CACHE_RECORD=false
```

Restart backend. Application behaves exactly like the GitHub version.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEMO_CACHE_MODE` | `false` | Serve cached API responses when available |
| `DEMO_CACHE_RECORD` | `false` | Record live API + AI responses into `demo_cache/` |
| `DEMO_CACHE_DIR` | `<repo>/demo_cache` | Override cache directory |

## Cleanup after hackathon

```bash
# Remove cache data
rm -rf demo_cache/responses demo_cache/ai demo_cache/binary demo_cache/manifest.json

# Remove temporary code
rm -rf backend/app/demo_cache

# Revert main.py and deps.py wiring (or git checkout those files)
git checkout main -- backend/app/main.py backend/app/api/deps.py
```

## Production safety

When `DEMO_CACHE_MODE=false`:

- Middleware is inert (pass-through)
- AI provider wrapper is not applied
- No cache reads or writes
- Identical behavior to GitHub `main`

## Never commit

Add to local workflow only — do **not** push:

- `demo_cache/responses/`
- `demo_cache/ai/`
- `demo_cache/manifest.json`
- `demo_cache/dataset/`

These paths are listed in `.gitignore`.
