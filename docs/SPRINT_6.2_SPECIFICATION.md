# Sprint 6.2 — Financial Statements (Ingestion & Financial Snapshot)

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.1 — Architecture validation; [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md) (Accepted)  
**Status:** Specification — awaiting Technical Lead approval before implementation  
**Date:** 2026-07-15  

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) §4–7 (Parser, Validation, Quality pipeline stages)
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md)
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) §5.2, §6.1, §9.2

**Tracker alignment:** Phase 3 DoD deferred “No Excel/CSV upload or parsing; no pandas/openpyxl → Phase 6, sprint 6.2 (Financial Statements upload/parsing)” (`progress.md` line 43). This specification implements that deferral under ADR-010.

---

## 1. Sprint Goal

Sprint 6.2 delivers the **complete Bronze-to-Silver ingestion pipeline** for Khazina’s Financial Data Repository:

> **Real financial file upload → deterministic parsing → validation → data quality assessment → immutable Financial Snapshot creation → file marked ready for Business Engine consumption.**

After this sprint:

- Uploaded Excel/CSV files are **stored** as Bronze artifacts (not metadata-only registration).
- Parser output is **persisted** as versioned, immutable Financial Snapshots per ADR-010.
- The existing `financial_files` processing lifecycle (`pending` → `processing` → `completed`/`failed` → `ready_for_analysis`) is **driven by actual ingestion**, not caller-supplied transitions.
- `import_records` contain **real** `record_count` values derived from parsing.
- `financial_files.metadata` is populated with **parse metadata** (column mappings, sheet names, row counts) — not snapshot payload.
- Downstream domains have a **stable, addressable Silver-layer dataset** to bind future `analysis_runs` and Business Engines against.

Sprint 6.2 does **not** run Business Engines, produce Facts, invoke AI, or deliver frontend integration.

---

## 2. Business Objective

### Capability unlocked

Executives and analysts gain a **governed financial data ingestion capability**: the organization can upload departmental financial datasets (budget, procurement, payroll, operating costs, supplier contracts — per placeholder inventory), have Khazina **parse and validate** them once, and retain an **auditable, immutable snapshot** that future analyses will reference.

### Business value

| Before Sprint 6.2 | After Sprint 6.2 |
|---|---|
| File inventory is metadata-only; no bytes stored or parsed | Canonical Bronze files preserved; Silver snapshots created |
| Import history shows placeholder or caller-supplied record counts | Import history reflects real parse outcomes |
| Validation summary is static placeholder data | Quality checks derived from parsed snapshot assessment |
| Business Engines have no dataset reference from ingestion | `ready_for_analysis` files have an associated Financial Snapshot version |
| “Financial Statements upload/parsing” deferred since Phase 3 | Deferral closed; ingestion pipeline operational on backend |

### Alignment with platform identity

Per ADR-010 and `BUSINESS_DOMAIN_DISCOVERY.md` §9.2, Khazina remains a **decision intelligence platform** — not ERP or accounting software. Sprint 6.2 makes the **Financial Data Repository** domain operational at the data layer, enabling future waste, financial, and cross-domain analysis without re-parsing source files.

---

## 3. Scope

### 3.1 INCLUDED (strict)

| # | Item | Evidence basis |
|---|---|---|
| I-01 | **Binary file upload** for financial datasets | Phase 3 deferral (`progress.md`); `storage_path` field exists but unused (`DATABASE_SCHEMA_DESIGN.md` §4.4) |
| I-02 | **Bronze file persistence** — original uploaded file preserved as source of truth | ADR-010 §1, §6 Bronze layer |
| I-03 | **Deterministic ingestion Parser** — Excel/CSV to internal structures | `AI_ARCHITECTURE.md` §5; Phase 3 deferral names `pandas`/`openpyxl` |
| I-04 | **Data Validation layer** on parsed structures | `AI_ARCHITECTURE.md` §6 |
| I-05 | **Data Quality assessment** producing repository-level checks | `AI_ARCHITECTURE.md` §7; placeholder checks in `PLACEHOLDER_DATA.md` §Validation Summary |
| I-06 | **Financial Snapshot** creation — immutable Silver artifact | ADR-010 (entire decision) |
| I-07 | **Snapshot versioning metadata** — `snapshot_version`, `parser_version`, `schema_version`, `created_at`, `organization_id`, `reporting_period_id` | ADR-010 §7 |
| I-08 | **Integration with existing `FinancialService` lifecycle** — automated state transitions tied to ingestion outcomes | `backend/app/services/financial.py`; `DATABASE_SCHEMA_DESIGN.md` §4.4 processing statuses |
| I-09 | **`import_records`** populated with real outcomes (`record_count`, `status`, `error_message`) | `DATABASE_SCHEMA_DESIGN.md` §4.5 |
| I-10 | **`financial_files.metadata` JSONB** populated with parse metadata only (not snapshot body) | `DATABASE_SCHEMA_DESIGN.md` §11 |
| I-11 | **Unified upload paths** — both `upload_source` values (`repository`, `waste_analysis`) create `financial_files` rows per DD-02 | `DATABASE_SCHEMA_DESIGN.md` §2 decision #1, #9 |
| I-12 | **Approved dependencies** — `pandas`, `openpyxl` added to backend requirements | `progress.md` line 43 |
| I-13 | **New persistence** for Financial Snapshot entity (schema migration) | ADR-010 §Relationship to Existing Schema; ADR compliance requirement #1 |
| I-14 | **Repository and service layer** for snapshot CRUD (read + create; no in-place update) | Phase 3 layered architecture pattern |
| I-15 | **Organization-scoped access** with existing auth/permission model | `backend/app/api/v1/financial.py` — `require_org_role`, `RequireOrgExecutive` for uploads |
| I-16 | **Unit and integration tests** for ingestion pipeline (parse success, parse failure, validation failure, snapshot immutability) | Phase 3+ sprint convention |
| I-17 | **Sprint completion entry** in `progress.md` upon TL approval | Project tracker convention |

### 3.2 EXCLUDED (strict)

| # | Item | Reason |
|---|---|---|
| E-01 | **Business Engine execution** (Waste, Financial, or any engine) | ADR-010 ends Sprint 6.2 at Silver; Gold is engine output. Engines frozen (`AI_FREEZE.md`, ADR-009) |
| E-02 | **Facts Contract changes** | Frozen — `CONTRACT_VERSION` 1.0 (`AI_FREEZE.md`) |
| E-03 | **AI / Ollama / Orchestrator / Context Builder / Prompt Engine** | Phase 5 frozen (`AI_FREEZE.md`) |
| E-04 | **Response Parser changes** | Distinct from ingestion Parser; AI frozen |
| E-05 | **`analysis_run` creation or execution** | Gold-layer process; requires engine sprint |
| E-06 | **Waste analysis results, recommendations, reports, dashboard data** | Downstream domains (`BUSINESS_DOMAIN_DISCOVERY.md` §9.3+) |
| E-07 | **Frontend API integration or UI changes** | Phase 2 frozen without API calls (`FRONTEND_SPECIFICATION.md` global checklist); Phase 7 per `PROJECT_ROADMAP.md` |
| E-08 | **Column mapping UI** | Explicitly out of scope (`FRONTEND_SPECIFICATION.md` §Data Management) |
| E-09 | **Data preview/viewer** | Explicitly out of scope (`FRONTEND_SPECIFICATION.md` §Data Management) |
| E-10 | **Normalized relational tables for parsed rows** | Rejected in ADR-010 §9 Alternative B |
| E-11 | **Reparse-at-analysis-time** | Rejected in ADR-010 §9 Alternative A |
| E-12 | **ERP-specific connectors or live ERP integration** | Mentioned as source type in `AI_ARCHITECTURE.md` §5 only; no connector spec exists |
| E-13 | **Formal accounting statement types** (Balance Sheet, Income Statement, Cash Flow, Trial Balance) | Not referenced anywhere in repository |
| E-14 | **Financial Engine** (ratios, liquidity, profitability) | Planned in `AI_ARCHITECTURE.md` §8; not implemented |
| E-15 | **Number Guard** | Deferred at freeze (`AI_FREEZE.md` §5) |
| E-16 | **Notifications, email, scheduled imports** | Not in repository scope |
| E-17 | **Multi-organization management UI** | Organization context exists; management UI absent (`DATABASE_SCHEMA_DESIGN.md` DD-01) |
| E-18 | **Snapshot re-parse UX** (“analyze with latest parser”) | ADR-010 §Consequences — deferred |
| E-19 | **Modifications to frozen AI or Business Engine modules** | Requires new ADR + TL approval |
| E-20 | **Cloud blob storage providers** (S3, Azure Blob, etc.) | ADR-010 §14.3 defers blob integration; local/filesystem Bronze acceptable for sprint unless TL directs otherwise in implementation design |

---

## 4. Inputs

### 4.1 Supported file types (repository evidence)

| Format | Source |
|---|---|
| `.xlsx` | `frontend/components/data/upload-data-panel.tsx` — `accept=".xlsx,.xls,.csv"` |
| `.xls` | Same |
| `.csv` | Same |
| ERP exports | `AI_ARCHITECTURE.md` §5 — “Read ERP exports, Excel workbooks, and CSV files” |

**Sprint 6.2 minimum:** Parser must handle **Excel (`.xlsx`, `.xls`) and CSV (`.csv`)** — the only formats explicitly wired in the approved frontend upload component. ERP exports are accepted only when delivered as these file formats; no live ERP integration.

### 4.2 Supported “financial statements” (repository evidence)

The tracker label “Financial Statements” (`progress.md` line 43) pairs with **Excel/CSV upload/parsing** — not named GAAP statement types. No Balance Sheet, Income Statement, Cash Flow, or Trial Balance appears in the repository.

**Supported datasets** are heterogeneous **departmental financial spreadsheets** represented by the Unified Placeholder File List (`PLACEHOLDER_DATA.md`):

| Example file | Department | Typical use |
|---|---|---|
| `Budget_Q2_2026.xlsx` | الشؤون المالية | Budget review, reports |
| `Supplier_Contracts.xlsx` | المشتريات | Supplier analysis, waste detection |
| `Procurement_Q2.xlsx` | المشتريات | Procurement waste |
| `Payroll_2026.xlsx` | الموارد البشرية | HR cost analysis |
| `Operating_Costs.xlsx` | العمليات | Operating cost trends |

Sprint 6.2 Parser must tolerate **variable column layouts** across these dataset types without assuming a single accounting statement schema.

### 4.3 Existing assumptions Sprint 6.2 builds on

| Assumption | Source |
|---|---|
| `financial_files` is canonical file inventory with `upload_source` discriminator | `DATABASE_SCHEMA_DESIGN.md` DD-02 |
| Processing lifecycle: `pending` → `processing` → `completed`/`failed` → `ready_for_analysis` | `ProcessingStatus` enum; `financial.py` service |
| Waste uploads create `financial_files` rows (not a separate inventory) | `DATABASE_SCHEMA_DESIGN.md` decision #9 |
| `financial_files.metadata` holds parse metadata; snapshot body is separate | `DATABASE_SCHEMA_DESIGN.md` §11; ADR-010 §2 |
| Single organization with `organization_id` on all entities | Phase 3 schema |
| `reporting_periods` with one active period | `DATABASE_SCHEMA_DESIGN.md` decision #8 |
| `departments` governed reference table | `DATABASE_SCHEMA_DESIGN.md` decision #2 |
| Auth: minimum `ANALYST` org role for financial routes; `EXECUTIVE` for upload registration | `backend/app/api/v1/financial.py` |
| Parser is deterministic — no calculations, no business rules, no LLM | `AI_ARCHITECTURE.md` §5 constraints |
| Validation dimensions: required fields, types, dates, currencies, missing values | `AI_ARCHITECTURE.md` §6 |
| Quality dimensions: completeness, consistency, confidence gating | `AI_ARCHITECTURE.md` §7 |
| Four validation check names from placeholder UX: field completeness, budget alignment, date format, duplicate records | `PLACEHOLDER_DATA.md` §Validation Summary |
| Import failure requires mandatory `error_message` | `FinancialService.fail_processing`; schema check constraint |
| Files referenced by analyses cannot be deleted (FK RESTRICT) | `FinancialService.delete_file` docstring |
| AI and Business Engine layers are frozen | `AI_FREEZE.md`; ADR-008, ADR-009 |

---

## 5. Expected User Flow

End-to-end workflow Sprint 6.2 must implement on the **backend** (frontend remains simulated per Phase 2 freeze):

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. UPLOAD                                                       │
│    User (Executive+) submits file bytes via upload channel      │
│    upload_source = repository | waste_analysis                    │
│    Optional: department_id, reporting_period_id                 │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. BRONZE REGISTRATION                                          │
│    financial_files created — status: pending                      │
│    Original file stored; storage_path populated                 │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PROCESSING START                                             │
│    status → processing                                          │
│    import_records entry — status: processing                    │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PARSE (deterministic ingestion Parser)                       │
│    Excel/CSV → internal structures                              │
│    Parse metadata captured (sheets, columns, row locations)       │
│    On fatal parse error → step 8 (failure path)                 │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. VALIDATE                                                     │
│    Structural/semantic checks per AI_ARCHITECTURE.md §6         │
│    Invalid records rejected, quarantined, or flagged            │
│    On validation failure → step 8 (failure path)                │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. DATA QUALITY ASSESSMENT                                      │
│    Completeness, consistency, confidence per §7                 │
│    Produces data_quality_snapshots + data_quality_checks        │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. FINANCIAL SNAPSHOT CREATION (Silver — immutable)             │
│    Snapshot vN created with required version metadata (ADR-010) │
│    financial_files.metadata updated (parse metadata only)         │
│    import_records — status: success, record_count set           │
│    status → completed → ready_for_analysis                      │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. FAILURE PATH (alternative from steps 4–6)                    │
│    import_records — status: failed, error_message mandatory     │
│    status → failed                                              │
│    No snapshot created (or partial snapshot discarded per design) │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. READY FOR BUSINESS ENGINE (terminal success state)           │
│    File status: ready_for_analysis                                │
│    Snapshot addressable by version ID                             │
│    NO engine execution in Sprint 6.2                            │
└─────────────────────────────────────────────────────────────────┘
```

### Flow notes

- Aligns with `BUSINESS_DOMAIN_DISCOVERY.md` Flow 1: upload → repository records → import history → validation checks.
- Aligns with ADR-010 Bronze → Silver pipeline; stops before Business Engine (Gold).
- Dual upload path (`repository` vs `waste_analysis`) uses the **same pipeline**; only `upload_source` metadata differs (DD-02).
- Re-upload or re-parse of the same Bronze file creates **Snapshot vN+1**; prior snapshots remain immutable (ADR-010 §8).

---

## 6. Deliverables

Components Sprint 6.2 **must** produce. Listed by architectural responsibility — not implementation technology.

| # | Deliverable | Responsibility |
|---|---|---|
| D-01 | **Bronze storage subsystem** | Persist original uploaded file bytes; populate `storage_path`; preserve file as source of truth |
| D-02 | **Upload ingestion entry point** | Accept file bytes + metadata; create `financial_files` row; trigger pipeline |
| D-03 | **Ingestion Parser module** | Deterministic Excel/CSV → internal structures; report errors with file/sheet/row location; expose `parser_version` |
| D-04 | **Internal snapshot schema definition (v1)** | Documented shape Parser maps into; expose `schema_version` |
| D-05 | **Data Validation module** | Enforce §6 dimensions; gate snapshot creation |
| D-06 | **Data Quality module** | Assess §7 dimensions; produce the four named check categories matching placeholder UX |
| D-07 | **Financial Snapshot persistence** | Immutable Silver storage; all ADR-010 §7 metadata fields |
| D-08 | **Snapshot repository** | Create and read snapshots; no in-place mutation |
| D-09 | **Ingestion orchestration service** | Coordinates lifecycle: storage → parse → validate → quality → snapshot → status transitions |
| D-10 | **`FinancialService` extension** | Replace caller-driven transitions with orchestrated ingestion for upload-triggered workflows |
| D-11 | **Import history integration** | Real `import_records` from pipeline outcomes |
| D-12 | **Parse metadata writer** | Populate `financial_files.metadata` JSONB per §11 |
| D-13 | **Quality snapshot integration** | Populate `data_quality_snapshots` and `data_quality_checks` from assessment |
| D-14 | **Snapshot retrieval capability** | Read snapshot by ID/version for verification and future engine binding |
| D-15 | **Schema migration** | New Financial Snapshot persistence (ADR-010); no changes to frozen AI/Engine tables beyond approved provenance fields if required |
| D-16 | **Dependency manifest update** | `pandas`, `openpyxl` in backend requirements |
| D-17 | **Test suite** | Parser, validation, quality, snapshot immutability, lifecycle transitions, failure paths |
| D-18 | **Sprint documentation** | `progress.md` entry; reference to this specification |

### Explicitly NOT deliverables of Sprint 6.2

Engine runner, Facts assembler output, AI orchestration, frontend client, dashboard aggregation, waste results, report generation, recommendation registration.

---

## 7. Out of Scope (Later Sprints)

| Domain | Deferred to |
|---|---|
| Business Engine execution against snapshots | Phase 6+ engine sprint (e.g., waste analysis trigger) |
| `analysis_runs` creation bound to snapshot version | Engine/analysis sprint |
| AI narrative, recommendations, Number Guard | Phase 6+ / post-freeze ADR |
| Financial Engine (ratios, liquidity, profitability) | `AI_ARCHITECTURE.md` §8 — future engine |
| Risk, Simulation engine implementations | `AI_FREEZE.md` §5 |
| Frontend upload → backend wiring | `PROJECT_ROADMAP.md` Phase 7 |
| Dashboard live KPIs from ingested data | Phase 7–8 |
| Report catalog population from ingestion | Phase 8 (`PROJECT_ROADMAP.md`) |
| Column mapping UI | `FRONTEND_SPECIFICATION.md` |
| Data preview/viewer | `FRONTEND_SPECIFICATION.md` |
| Export (PDF/Excel/PPT) | `DATABASE_SCHEMA_DESIGN.md` A-05 |
| ERP live connectors | No specification exists |
| Snapshot retention policy / archival automation | Operations — post-MVP |
| Re-parse UX and parser upgrade workflows | ADR-010 deferred |
| Cloud blob storage integration | ADR-010 §14.3 deferred |
| `analysis_runs.source_snapshot_id` schema binding | Engine sprint (provenance extension per ADR-010) |
| Notifications and scheduled ingestion | Not in repository |

---

## 8. Acceptance Criteria

Sprint 6.2 is **complete only when every criterion passes** Technical Lead review.

### 8.1 Upload and Bronze

| ID | Criterion |
|---|---|
| AC-01 | Executive-role caller can upload a `.xlsx` file; `financial_files` row created with `processing_status = pending` and non-null `storage_path` |
| AC-02 | Uploaded Bronze file bytes are retrievable and match submitted content |
| AC-03 | Upload with `upload_source = repository` and `upload_source = waste_analysis` both succeed through identical pipeline |
| AC-04 | Upload without valid organization membership is rejected (existing auth model) |

### 8.2 Parsing

| ID | Criterion |
|---|---|
| AC-05 | `pandas` and `openpyxl` are declared backend dependencies |
| AC-06 | Valid `.xlsx` file parses to internal structures without LLM invocation |
| AC-07 | Valid `.csv` file parses to internal structures |
| AC-08 | Parse failure produces `processing_status = failed` and `import_records.status = failed` with non-empty `error_message` |
| AC-09 | Parse error identifies source location (file name; sheet and/or row where applicable) |
| AC-10 | Parser performs no calculations, no business rules, no AI calls (`AI_ARCHITECTURE.md` §5 constraints) |

### 8.3 Validation and Quality

| ID | Criterion |
|---|---|
| AC-11 | Structurally invalid data is rejected before snapshot creation |
| AC-12 | Successful ingestion produces `data_quality_snapshots` with at least one `data_quality_checks` row |
| AC-13 | Quality checks cover the four placeholder categories: field completeness, budget alignment, date format, duplicate records |
| AC-14 | Failed validation does not produce a `ready_for_analysis` file |

### 8.4 Financial Snapshot (ADR-010)

| ID | Criterion |
|---|---|
| AC-15 | Successful parse creates exactly one immutable Financial Snapshot per import attempt |
| AC-16 | Snapshot carries: `snapshot_version`, `parser_version`, `schema_version`, `created_at`, `organization_id`, `reporting_period_id` |
| AC-17 | Snapshot links to exactly one source `financial_files` record |
| AC-18 | Snapshot content cannot be modified in place after creation |
| AC-19 | Re-ingestion of same Bronze file creates a new snapshot version; prior snapshot unchanged |
| AC-20 | `financial_files.metadata` contains parse metadata only — not full snapshot payload |

### 8.5 Lifecycle integration

| ID | Criterion |
|---|---|
| AC-21 | Successful pipeline: `pending` → `processing` → `completed` → `ready_for_analysis` |
| AC-22 | `import_records.record_count` reflects actual parsed record count on success |
| AC-23 | Existing manual lifecycle endpoints remain functional for backward compatibility OR are superseded with documented migration — no orphaned states |
| AC-24 | `ready_for_analysis` file has retrievable snapshot reference |

### 8.6 Freeze compliance

| ID | Criterion |
|---|---|
| AC-25 | Zero modifications to frozen AI modules (`app/ai/` pipeline, Prompt Engine, Orchestrator, Response Parser) |
| AC-26 | Zero modifications to Business Engine internals (`app/business/engines/`, Facts Contract structure, Registry freeze) |
| AC-27 | No normalized relational tables for individual parsed spreadsheet rows |
| AC-28 | No Business Engine or AI invocation in ingestion pipeline |

### 8.7 Testing and documentation

| ID | Criterion |
|---|---|
| AC-29 | Unit tests cover Parser, Validation, Quality, and Snapshot immutability |
| AC-30 | Integration test covers full success path: upload → snapshot → `ready_for_analysis` |
| AC-31 | Integration test covers failure path with mandatory error message |
| AC-32 | `progress.md` updated with Sprint 6.2 completion entry |
| AC-33 | No regression in existing Phase 3–5 test suites |

---

## 9. Technical Risks

Architectural risks identified from repository evidence. **No solutions proposed in this specification.**

| ID | Risk | Source |
|---|---|---|
| R-01 | **Snapshot payload format undecided** — ADR-010 defers serialization format; size and query characteristics unknown | ADR-010 §Consequences |
| R-02 | **Storage growth** — immutable snapshots accumulate; no retention policy in repository | ADR-010 §Consequences |
| R-03 | **Heterogeneous spreadsheet schemas** — placeholder files imply varied layouts; Parser may not generalize without per-type rules | `PLACEHOLDER_DATA.md` file list |
| R-04 | **Ambiguity A-04 unresolved** — org-wide vs per-import quality snapshots | `DATABASE_SCHEMA_DESIGN.md` §15 |
| R-05 | **Bronze storage backend unspecified** — `storage_path` designed for future blob storage; local filesystem may not scale | `DATABASE_SCHEMA_DESIGN.md` §4.4, §14.3 |
| R-06 | **10 MB upload limit** — frontend states “حتى 10 ميغابايت”; backend enforcement not defined | `upload-data-panel.tsx` |
| R-07 | **Payroll failure placeholder** — `Payroll_2026.xlsx` shows “فشل — تنسيق غير مدعوم”; Parser must define supported format boundaries | `PLACEHOLDER_DATA.md` import history |
| R-08 | **Ingestion Parser location** — must not collide with frozen `app/ai/parsers/response_parser.py` namespace | `AI_FREEZE.md`; `AI_ARCHITECTURE.md` §5 vs §AI pipeline |
| R-09 | **Provenance gap until engine sprint** — `analysis_runs` lacks `source_snapshot_id` until future sprint; snapshot may exist without consumer | ADR-010 §Relationship; deferred binding |
| R-10 | **Phase naming divergence** — `progress.md` “Business Features” vs `PROJECT_ROADMAP.md` “Financial Core” may cause scope creep | Both documents |
| R-11 | **Manual lifecycle API coexistence** — existing caller-driven `complete_processing`/`fail_processing` may conflict with automated pipeline | `financial.py` current behavior |
| R-12 | **Validation/quarantine storage** — `AI_ARCHITECTURE.md` §6 allows quarantine; no quarantine table approved | Architecture investigation gap |

---

## 10. Dependencies

### 10.1 Frozen architecture decisions

| Dependency | Role in Sprint 6.2 |
|---|---|
| **ADR-010 Financial Snapshot** | Defines Silver artifact, immutability, versioning, rejected alternatives |
| **ADR-008 AI Architecture** | Parser/Validation/Quality stage definitions (§4–7) |
| **ADR-009 Business Engine Architecture** | Confirms engines consume dataset references — not built this sprint |
| **AI_FREEZE.md** | Boundary — no AI changes |

### 10.2 Existing backend modules (Phase 3–4 — frozen core)

| Module | Role |
|---|---|
| `OrganizationService` / `OrganizationRepository` | Single-active-org validation |
| `FinancialService` / `FinancialRepository` | File lifecycle, import records, quality snapshots |
| `DepartmentRepository` | Optional `department_id` on files |
| Reporting period model | `reporting_period_id` scoping |
| `financial_files`, `import_records`, `data_quality_snapshots`, `data_quality_checks` ORM models | Extended, not replaced |
| Alembic migration framework | New snapshot entity |
| Auth (`require_org_role`, JWT, org membership) | Upload authorization |
| Exception handling / `ApiResponse` envelope | Consistent API surface |
| Layered architecture: Router → Service → Repository | Pattern compliance |

### 10.3 Explicitly NOT a runtime dependency

| Module | Why |
|---|---|
| Waste Engine | No engine execution |
| AI Orchestrator / Ollama client | Frozen; not in ingestion path |
| Facts Contract / Context Builder | Downstream of engines |
| Frontend | Phase 2 frozen without API calls |

### 10.4 New external dependencies

| Dependency | Mandate source |
|---|---|
| `pandas` | `progress.md` line 43 |
| `openpyxl` | `progress.md` line 43 |

---

## 11. Financial Snapshot Contract

This section defines the **architectural contract** of the Financial Snapshot artifact. It is **not** a JSON schema, **not** a database schema, and **not** an implementation specification. It establishes the rules, boundaries, and responsibilities that Sprint 6.2 implementation must honour.

**Implementation gate:** Sprint 6.2 coding may **only begin after this contract is approved** by the Technical Lead.

### 11.1 Purpose

The Financial Snapshot exists to provide a **stable, immutable, versioned representation** of how Khazina understood a uploaded financial dataset at a specific point in time — after deterministic parsing, validation, and quality assessment, and **before** any Business Engine calculation.

It closes the Silver-layer gap identified in ADR-010: the platform must persist parsed financial data as a first-class artifact, not as ephemeral Parser output, file metadata alone, or normalized spreadsheet rows.

The contract ensures that future analyses can reference **exactly one frozen dataset** without re-reading Excel, without reinterpretation, and without ambiguity about provenance.

### 11.2 Responsibilities

The Financial Snapshot **is responsible for**:

| Responsibility | Description |
|---|---|
| **Capture parsed dataset** | Hold the complete internal structures produced by the ingestion Parser after a successful parse-and-validate cycle |
| **Preserve provenance** | Maintain an immutable link to exactly one Bronze source file and the import attempt that created it |
| **Expose version identity** | Carry `snapshot_version`, `parser_version`, and `schema_version` so consumers know what they are reading |
| **Scope organizational context** | Bind every snapshot to `organization_id` and `reporting_period_id` |
| **Record temporal fact** | Carry `created_at` as the moment the snapshot was materialized |
| **Serve as engine input reference** | Provide the validated dataset reference that Business Engines consume in future sprints |

The Financial Snapshot **is not responsible for**:

| Exclusion | Owner |
|---|---|
| Storing the original uploaded file bytes | Bronze (`financial_files` + storage) |
| Tracking upload/processing UI status | Bronze lifecycle on `financial_files` |
| Recording import attempt outcomes alone | `import_records` |
| Aggregated validation summary metrics | `data_quality_snapshots` / `data_quality_checks` |
| Business calculations or derived KPIs | Business Engines (Gold) |
| AI narrative or recommendations | AI layer (Facts consumer) |
| Parse metadata (column mappings, sheet names, row counts) | `financial_files.metadata` JSONB |

### 11.3 Ownership

| Aspect | Owner |
|---|---|
| **Business domain** | Financial Data Repository (`BUSINESS_DOMAIN_DISCOVERY.md` §9.2) |
| **Architectural authority** | ADR-010 Financial Snapshot Architecture |
| **Creation** | Ingestion pipeline (Parser → Validation → Quality → Snapshot materialization) |
| **Mutation** | **None** — snapshots are write-once; no domain may edit snapshot content after creation |
| **Deletion** | Governed by future retention policy; deletion of snapshots referenced by completed analyses is restricted (analogous to Bronze file FK RESTRICT on `analysis_runs`) |
| **Consumption** | Business Engines (future sprints); not AI, not Frontend directly |

### 11.4 Lifecycle

```
Bronze file accepted
        ↓
Ingestion pipeline starts (financial_files → processing)
        ↓
Parse → Validate → Quality assessment
        ↓
[Success path]  Financial Snapshot created (immutable)
        ↓
financial_files → completed → ready_for_analysis
        ↓
Snapshot available for future Business Engine binding
        ↓
[Terminal]  Snapshot persists unchanged for audit lifetime

[Failure path]  Parse/validation/quality fatal failure
        ↓
No snapshot created (or discarded if partially materialized)
        ↓
financial_files → failed; import_records records error
```

A snapshot is born at **successful pipeline completion**. It has no active processing state of its own — its existence is binary: **created and immutable**, or **not created**.

### 11.5 State Transitions

The Financial Snapshot artifact itself has **no mutable states**. State transitions apply to the **Bronze file lifecycle** that governs when snapshot creation is attempted and when a snapshot becomes consumable:

| Bronze state (`financial_files`) | Snapshot contract rule |
|---|---|
| `pending` | No snapshot exists |
| `processing` | No snapshot exists; creation in progress |
| `completed` | Snapshot must exist for successful ingestion |
| `failed` | No snapshot exists |
| `ready_for_analysis` | Snapshot must exist and be retrievable by version reference |

**Snapshot-level transitions (versioning only):**

| Event | Contract rule |
|---|---|
| First successful parse of a Bronze file | Creates Snapshot v1 |
| Re-parse or re-import of same Bronze file | Creates Snapshot vN+1; v1…vN unchanged |
| Parser upgrade | New snapshots use new `parser_version`; old snapshots retained |
| Schema evolution | New snapshots use new `schema_version`; old snapshots remain valid for their version |

No transition may modify an existing snapshot's content.

### 11.6 Versioning Principles

| Principle | Rule |
|---|---|
| **Monotonic versioning** | `snapshot_version` increments per new snapshot for the same Bronze file; never reused |
| **Parser traceability** | Every snapshot records `parser_version` — the Parser implementation that produced it |
| **Schema traceability** | Every snapshot records `schema_version` — the internal structure contract version it conforms to |
| **Independent evolution** | `parser_version` and `schema_version` may change independently; both must be recorded |
| **Historical preservation** | New versions do not invalidate, replace, or mutate prior versions |
| **Consumer binding** | Future `analysis_runs` bind to a specific `snapshot_version` — not to “latest” implicitly |
| **Correction model** | Data errors are corrected by creating a new snapshot version — never by editing an existing one |

### 11.7 Immutability Rules

| Rule | Enforcement |
|---|---|
| **Write-once** | Snapshot content is set at creation and never updated |
| **No in-place correction** | Administrative, parser, or engine logic must not patch snapshot data |
| **No derived overwrite** | Business Engine results must not flow back into snapshot content |
| **Append-only versioning** | Corrections and parser improvements produce new snapshots — not revisions |
| **Audit integrity** | Any completed analysis referencing a snapshot version must find identical content on re-read |
| **Metadata immutability** | Version metadata (`snapshot_version`, `parser_version`, `schema_version`, `created_at`, org/period binding) is fixed at creation |

### 11.8 Relationship with Bronze

| Relationship | Contract rule |
|---|---|
| **Provenance** | Every snapshot derives from exactly one Bronze file (`financial_files`) |
| **Source of truth** | Bronze remains the legal/operational source of what was submitted; snapshot is a derivative interpretation |
| **Non-substitution** | Snapshot does not replace Bronze; both are retained |
| **Cardinality** | One Bronze file may produce many snapshot versions (v1, v2, …); each snapshot references one Bronze file |
| **Metadata separation** | Bronze `metadata` JSONB holds parse metadata only; snapshot holds parsed dataset body |
| **Lifecycle coupling** | Snapshot creation is a success outcome of Bronze ingestion pipeline — not an independent upload |

### 11.9 Relationship with Business Engine

| Relationship | Contract rule |
|---|---|
| **Input role** | Financial Snapshot is the **validated dataset reference** Business Engines read ([BUSINESS_ENGINE_ARCHITECTURE.md](../BUSINESS_ENGINE_ARCHITECTURE.md)) |
| **Consumption timing** | Engines consume snapshots in sprints **after** 6.2; Sprint 6.2 creates snapshots only |
| **No engine in creation** | Snapshot materialization must not invoke Business Engines |
| **No calculation in snapshot** | Parser and snapshot layer perform no business calculations ([AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §5) |
| **Gold separation** | Engine outputs (waste totals, ratios, facts) are Gold — stored in engine result entities, not in snapshot |
| **Determinism** | Same snapshot version + same engine version → same Gold results (ADR-009) |
| **Binding** | Future engine execution must reference explicit `snapshot_version` — not reparse Bronze |

### 11.10 Relationship with AI

| Relationship | Contract rule |
|---|---|
| **No direct access** | AI must not receive Financial Snapshot content directly ([ADR 008](ADR/008-ai-architecture.md), [AI_FREEZE.md](AI_FREEZE.md)) |
| **No AI in creation** | Snapshot materialization must not invoke LLM, Orchestrator, or Prompt Engine |
| **Downstream only** | AI consumes **Facts Contract** produced by Business Engines from snapshot-derived calculations |
| **Pipeline position** | Snapshot is Silver — upstream of Gold (Facts) and AI |
| **Frozen boundary** | Sprint 6.2 must not modify any frozen AI module to read snapshots |

### 11.11 Business Constraints

| Constraint | Rule |
|---|---|
| **Platform identity** | Khazina is decision intelligence — not ERP, accounting software, or spreadsheet editor (ADR-010) |
| **Heterogeneous inputs** | Snapshots must tolerate varied departmental datasets (budget, procurement, payroll, etc.) — not a single GAAP statement schema |
| **Organization scope** | Snapshots are always org-scoped; never cross-tenant addressable |
| **Period scope** | Snapshots associate with a reporting period for executive comparability |
| **Governance** | Snapshots support period-close audit, board review, and reproducible decision defense |
| **No normalized row mandate** | Parsed data is stored as a cohesive snapshot unit — not decomposed into relational ledger/account/transaction tables (ADR-010 §9 Alternative B rejected) |
| **No reparse-at-analysis** | Analyses must not silently reparse Bronze when a snapshot version exists (ADR-010 §9 Alternative A rejected) |
| **Quality gate** | Only data passing validation and minimum quality thresholds may be snapshotted |
| **Import accountability** | Every snapshot links to an import attempt with real `record_count` on success or `error_message` on failure |
| **Dual upload path** | Both `upload_source` values (`repository`, `waste_analysis`) produce snapshots through the same contract — only upload channel metadata differs |

### 11.12 Contract Approval

| Field | Requirement |
|---|---|
| **Approver** | Technical Lead |
| **Prerequisite for** | Sprint 6.2 Step 2 onward (all implementation) |
| **Status** | **Pending approval** until TL sign-off recorded in `progress.md` |
| **Deviation policy** | Any implementation that violates this contract requires TL approval and, if architectural, a new ADR |

---

## 12. Implementation Order

Logical sequence for implementation engineers. **Do not skip ordering** — each step depends on prior steps.

### Step 1 — Financial Snapshot Contract approval

The Financial Snapshot Contract (§11) must be reviewed and **approved by the Technical Lead**. Sprint implementation may **only begin after this contract is approved**. No coding, migration, or persistence design may proceed before approval.

### Step 2 — Database migration

Introduce Financial Snapshot persistence entity. Extend provenance fields only as approved under the Financial Snapshot Contract (§11). Run migration against PostgreSQL 16.

### Step 3 — Bronze storage subsystem

Implement original file byte persistence and `storage_path` population. Define storage root configuration.

### Step 4 — Internal structure v1 and Parser

Define internal structure shape per approved Financial Snapshot Contract, `schema_version`, and `parser_version` constants. Implement ingestion Parser for `.xlsx`, `.xls`, `.csv` using approved libraries.

### Step 5 — Data Validation module

Implement validation per `AI_ARCHITECTURE.md` §6. Integrate with Parser output.

### Step 6 — Data Quality module

Implement quality assessment per §7. Map results to the four placeholder check categories.

### Step 7 — Financial Snapshot repository and service

Immutable create-and-read persistence. Enforce no in-place updates. Wire version metadata.

### Step 8 — Ingestion orchestration service

Coordinate full pipeline; drive `FinancialService` lifecycle transitions automatically; write `import_records`, `metadata`, and quality snapshots.

### Step 9 — Upload entry point

Wire upload ingestion to orchestration service. Enforce auth, org scope, `upload_source` discriminator.

### Step 10 — Test suite

Unit tests (Steps 4–7) and integration tests (Step 8–9). Verify AC-01 through AC-33.

### Step 11 — Documentation and TL review

Update `progress.md`. Submit sprint for Technical Lead acceptance against this specification.

---

## 13. Final Recommendation (Technical Lead Review)

### Recommendation: **APPROVE implementation — conditional on Financial Snapshot Contract approval**

### Rationale for approval

| Factor | Assessment |
|---|---|
| **Architectural readiness** | ADR-010 closes the blocking gap identified in Phase 6 review. Sprint 6.2 has a normative target. |
| **Scope discipline** | This specification strictly bounds work to Bronze→Silver ingestion. AI and Business Engine freezes are preserved. |
| **Existing foundation** | Phase 3 `financial_files` lifecycle, import history, and quality tables provide the envelope. Sprint 6.2 fills the payload — it does not redesign the platform. |
| **Tracker alignment** | Implements the sole explicit Sprint 6.2 deferral from Phase 3 DoD (`progress.md` line 43). |
| **Measurable acceptance** | 33 acceptance criteria provide objective completion gates. |

### Conditions before coding starts

1. **Financial Snapshot Contract approved (§11)** — TL sign-off recorded. Implementation may not begin until this contract is approved.
2. **Ingestion module namespace confirmed** — ingestion Parser must live outside frozen `app/ai/parsers/` (Response Parser). Recommend `app/ingestion/` or equivalent — TL to confirm before Step 4.
3. **Manual vs automated lifecycle policy** — clarify whether existing caller-driven processing endpoints remain for admin use or are deprecated when orchestration ships (R-11).

### Rationale for conditional (not unconditional) approval

Sprint 6.2 is **architecturally approved** via ADR-010 and this specification, but **implementation is gated on Financial Snapshot Contract approval (§11)**. Attempting implementation before contract approval risks violating immutability, ownership, and layer-boundary rules defined in ADR-010.

### What success looks like

At sprint end, an operator can upload `Procurement_Q2.xlsx` via the backend, observe a real import history record count, retrieve an immutable Financial Snapshot v1 with full version metadata, and see the file in `ready_for_analysis` — with **no engine run, no AI call, and no frontend change**. That state unblocks the next sprint to bind the Waste Engine (or Financial Engine) to snapshot references.

### TL decision

| Field | Value |
|---|---|
| **Specification status** | **APPROVED** for use as Sprint 6.2 implementation authority |
| **Implementation start** | **Approved after Financial Snapshot Contract (§11) sign-off** |
| **Scope creep policy** | Any request to add engine execution, AI, frontend integration, or normalized row tables within Sprint 6.2 is **out of scope** and requires a new sprint definition |

---

## Related Documents

- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md)
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md)
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md)
- [PLACEHOLDER_DATA.md](PLACEHOLDER_DATA.md)
- [progress.md](progress.md)
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)

---

**Document authority:** This specification is the official implementation guide for Sprint 6.2. Implementation that deviates from this document or ADR-010 requires Technical Lead approval and, where architectural, a new ADR.
