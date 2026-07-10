# ADR 003: PostgreSQL as the Primary Database

**Status:** Accepted  
**Date:** Phase 1 — Sprint 1.1  
**Phase:** Foundation

## Decision

Khazina uses PostgreSQL 16 as the primary relational database, accessed through SQLAlchemy and versioned with Alembic.

## Why PostgreSQL

- Full ACID compliance required for financial data integrity
- Advanced indexing, constraints, and query optimization for analytical workloads
- Strong JSON support for semi-structured financial data when needed
- Mature ecosystem with SQLAlchemy and Alembic first-class support
- Production-proven at enterprise scale
- Available as a stable official Docker image (`postgres:16-alpine`) in the local development stack

## Why Not MySQL

- PostgreSQL offers stronger support for complex queries and analytical functions relevant to financial reporting
- Better alignment with SQLAlchemy advanced features used in enterprise applications
- Stricter standards compliance reduces subtle data integrity issues

## Why Not SQLite

- SQLite is file-based and not suitable for multi-service Docker deployments
- No concurrent write scalability for multi-user enterprise usage
- Lacks the production operational tooling (replication, backup strategies) required for Phase 10 deployment
- Acceptable only for isolated unit tests, not as the primary datastore

## Consequences

**Positive**

- Single database engine across local, Docker, and future production environments
- Alembic migration infrastructure initialized in Phase 1, ready for Phase 3 schema work

**Negative**

- Requires PostgreSQL running locally or via Docker for database-dependent development
- Operational complexity higher than SQLite for quick prototypes

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [ADR 004: Docker and Compose](004-docker.md)
