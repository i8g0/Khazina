# ADR 002: Next.js as the Frontend Framework

**Status:** Accepted  
**Date:** Phase 1 — Sprint 1.1  
**Phase:** Foundation

## Decision

Khazina uses Next.js with the App Router as the frontend framework.

## Why Next.js

- Production-ready React framework with server and client component support
- App Router provides file-based routing suitable for enterprise application growth
- Built-in optimization for production builds including standalone output for Docker
- Strong TypeScript support aligned with project coding standards
- Active ecosystem and long-term maintainability for enterprise projects
- Native support for environment-based configuration (`NEXT_PUBLIC_*` variables)

## Alternatives Considered

| Alternative | Reason Not Selected |
|-------------|---------------------|
| Create React App | Deprecated; no App Router or production optimization path |
| Vite + React (SPA) | Lacks built-in routing conventions and SSR capabilities needed for enterprise deployment |
| Angular | Higher learning curve; less alignment with planned React component ecosystem |
| Remix | Viable alternative; less team familiarity and smaller enterprise adoption at project start |

## Consequences

**Positive**

- Standalone Docker production builds validated in Phase 1
- RTL support configured at the root layout level
- Clear path to Phase 2 frontend foundation work

**Negative**

- Build-time injection required for public environment variables in Docker
- App Router conventions must be followed consistently across all new pages

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [ADR 004: Docker and Compose](004-docker.md)
