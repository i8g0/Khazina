# Skill 03 — Architecture Rules

Protect Khazina architecture from unauthorized AI changes.

Full architecture: [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)

---

## Never Without Explicit Tech Lead Approval

- Rename folders or move modules
- Replace frameworks (FastAPI, Next.js, PostgreSQL, etc.)
- Change architecture or layered structure
- Change API standards (`ApiResponse`, `/api/v1/` versioning)
- Change folder structure or monorepo layout
- Introduce new dependencies or packages
- Modify Docker configuration outside approved sprint scope
- Create database models or migrations (Phase 3 gate)
- Implement authentication (Phase 4 gate)
- Add AI business logic or services (Phase 5 gate)
- Delete shared infrastructure code

---

## Fixed Architecture Elements

These are governed by documentation and ADRs. Do not alter autonomously:

| Element | Authority |
|---------|-----------|
| Monorepo layout | [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) |
| Backend framework | [docs/ADR/001-fastapi.md](../../docs/ADR/001-fastapi.md) |
| Frontend framework | [docs/ADR/002-nextjs.md](../../docs/ADR/002-nextjs.md) |
| Database | [docs/ADR/003-postgresql.md](../../docs/ADR/003-postgresql.md) |
| Docker / Compose | [docs/ADR/004-docker.md](../../docs/ADR/004-docker.md) |
| ApiResponse envelope | [docs/ADR/005-api-response.md](../../docs/ADR/005-api-response.md) |
| Ollama service | [docs/ADR/006-ollama.md](../../docs/ADR/006-ollama.md) |
| API naming and status codes | [docs/API_CONTRACTS.md](../../docs/API_CONTRACTS.md) |

---

## Backend Dependency Rules

```
api/  →  schemas/, core/, db/
schemas/  →  (no upward dependencies)
core/  →  (no upward dependencies to api/)
db/  →  core/config only
```

Do not introduce circular imports or violate layer boundaries.

---

## If Architecture Changes Are Requested

1. Read [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
2. Read relevant ADR files under [docs/ADR/](../../docs/ADR/)
3. Explain the proposed change, impact, and risks
4. **Stop and wait for Tech Lead approval**
5. Do not implement until approved
6. If approved: update ARCHITECTURE.md and create/update ADR as appropriate

---

## Phase Gates

| Feature | Earliest Phase |
|---------|----------------|
| Database models and migrations | Phase 3 |
| Authentication | Phase 4 |
| AI business logic | Phase 5 |
| CI/CD pipeline | Phase 9 |
| Production deployment | Phase 10 |

Never implement gated features early, even if the developer prompt requests it.

---

## References

- Architecture (authoritative): [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- Phase plan: [docs/PROJECT_ROADMAP.md](../../docs/PROJECT_ROADMAP.md)
- Forbidden AI tasks: [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md)
