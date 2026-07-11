# Khazina

Enterprise Financial Decision Intelligence Platform.

## Project Structure

```
Khazina/
├── frontend/    # Next.js application
├── backend/     # FastAPI application
├── ai/          # AI services (future sprints)
├── database/    # Database assets (future sprints)
├── docker/      # Docker Compose configuration
├── docs/        # Documentation
└── scripts/     # Utility scripts
```

## Prerequisites

- Node.js 22+
- Python 3.12+
- Docker & Docker Compose (for containerized development)

See [docs/progress.md](docs/progress.md) for sprint and phase status.

## Quick Start

### Using Docker

Docker Compose uses safe development defaults. An env file is optional.

1. (Optional) Copy Docker environment overrides:
   ```bash
   cp docker/.env.example docker/.env
   ```

2. Start all services from the repository root:
   ```bash
   docker compose -f docker/docker-compose.yml up --build
   ```

   With custom ports or credentials:
   ```bash
   docker compose -f docker/docker-compose.yml --env-file docker/.env up --build
   ```

3. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/api/v1/health
   - Ollama: http://localhost:11434

Services start in order: postgres → backend → frontend. Ollama runs independently.

> **Note:** `NEXT_PUBLIC_API_URL` is injected at frontend **build time** via Docker build args.

### Local Development

#### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
pnpm install
cp .env.example .env.local
pnpm dev
```

## API

| Method | Endpoint           | Description  |
|--------|--------------------|--------------|
| GET    | /api/v1/health     | Health check |

## License

Proprietary.
