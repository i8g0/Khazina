# ADR 010: Financial Snapshot Architecture

**Status:** Accepted  
**Date:** Phase 6 — Pre–Sprint 6.2 Architecture Decision, 2026-07-15  
**Phase:** Business Features (Financial Data Ingestion)

## Official Architecture Decision

**APPROVED.**

Khazina adopts the **Financial Snapshot** as the immutable, versioned representation of parsed financial data. Business Engines consume Financial Snapshots — never raw uploaded files and never reparsed spreadsheets at analysis time. Sprint 6.2 implementation must conform to this decision.

---

## Decision Summary

Khazina introduces a new architectural artifact — the **Financial Snapshot** — positioned between file ingestion and Business Engine execution:

```
Uploaded Financial File (Bronze — Source of Truth)
        ↓
     Parser
        ↓
Financial Snapshot (Silver — Immutable Parsed Dataset)
        ↓
  Business Engine
        ↓
  Facts Contract (Gold — Deterministic Business Results)
        ↓
        AI
        ↓
   Reports / Executive Decision
```

The Financial Snapshot closes the architectural gap identified during Phase 6 review: the repository already defines file inventory (`financial_files`), import outcomes (`import_records`), quality summaries, analysis runs, and reports — but had no approved home for the **parsed financial dataset itself**. This ADR assigns that responsibility to the Financial Snapshot.

---

## Context

### Platform identity

Khazina is an **Enterprise Financial Decision Intelligence Platform**. It is **not** ERP, accounting software, or a spreadsheet editor. Its role is to ingest organizational financial data, run deterministic analysis, and support executive decision-making with auditable facts and bounded AI interpretation.

### Established pipeline (frozen)

Per [ADR 008](008-ai-architecture.md) and [ADR 009](009-business-engine-architecture.md):

- **Business Engines** perform all calculations.
- **AI** interprets Facts; it never calculates or receives raw business data.
- The Parser is the ingestion boundary that maps external formats to internal structures ([AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §5).

### Problem discovered in Phase 6 review

The approved schema provides:

| Existing artifact | Responsibility |
|---|---|
| `financial_files` | File inventory, processing status, upload metadata |
| `import_records` | Import attempt outcomes and aggregate record counts |
| `data_quality_snapshots` / `data_quality_checks` | Repository-level validation summaries |
| `analysis_runs` | Analytical process execution |
| `reports` | Published executive artifacts |

None of these entities is designated to hold the **parsed financial dataset** — the structured output of the Parser after Excel/CSV ingestion. [AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §9 explicitly deferred implementation details including storage to subsequent sprints. Sprint 6.2 cannot proceed without this decision.

---

## 1. Why the Uploaded File Remains the Source of Truth

The original uploaded file (Bronze layer) is the **legal and operational source of truth** for what the organization actually submitted.

**Rationale:**

| Principle | Explanation |
|---|---|
| **Provenance** | Every Financial Snapshot must trace to exactly one uploaded file. Executives, auditors, and regulators ask: “What document did this analysis come from?” The file — not a derived structure — answers that question. |
| **Non-destructive ingestion** | Khazina interprets data; it does not replace the organization’s source systems or original exports. The file is preserved as submitted. |
| **Dispute resolution** | When an analysis is challenged, the authoritative artifact is the file the user uploaded — not an internal reinterpretation that may have drifted through re-parsing. |
| **Alignment with existing schema** | `financial_files` is already the canonical inventory ([DATABASE_SCHEMA_DESIGN.md](../DATABASE_SCHEMA_DESIGN.md) DD-02). The file entity owns upload origin, department association, and processing lifecycle. The Financial Snapshot extends this model; it does not replace the file. |
| **Separation of concerns** | The file answers *what was received*. The snapshot answers *how Khazina understood it at a point in time*. These are different questions and must not be collapsed. |

The uploaded file is immutable once accepted. Parser output is a **derivative** of the file, not a substitute for it.

---

## 2. Why Parser Output Becomes a Financial Snapshot

The Parser converts ERP exports, Excel workbooks, and CSV files into Khazina’s **internal structures** ([AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §5). That conversion is expensive, error-prone, and version-sensitive. The output must be **captured and named** as a first-class artifact.

**Why “Financial Snapshot” and not “parsed rows in memory” or “metadata only”:**

| Reason | Explanation |
|---|---|
| **Defined handoff point** | Business Engines require a **validated dataset reference** ([BUSINESS_ENGINE_ARCHITECTURE.md](../BUSINESS_ENGINE_ARCHITECTURE.md)). The Financial Snapshot is that reference — a stable, addressable unit of parsed data. |
| **Beyond file metadata** | `financial_files.metadata` JSONB is approved for parse metadata (column mappings, sheet names, row counts) — not for the dataset itself ([DATABASE_SCHEMA_DESIGN.md](../DATABASE_SCHEMA_DESIGN.md) §11). The snapshot holds the parsed content; metadata describes how parsing occurred. |
| **Pipeline completeness** | The frozen AI pipeline is: Parser → Validation → Quality → Business Engines. Validation and quality operate on parsed structures. Those structures must persist as a snapshot before engines run — not evaporate after each import. |
| **Domain language** | Khazina serves executive financial oversight within a reporting period and organizational context. “Snapshot” communicates a **point-in-time financial dataset** — appropriate for quarterly reviews, waste analysis, and board-ready reporting. |
| **Distinct from Gold** | Engine outputs (waste totals, risk scores, simulation projections) are **business results** — calculated, derived, and versioned separately. The snapshot is the **input substrate** those engines consumed. Conflating Silver and Gold destroys auditability. |

---

## 3. Why the Financial Snapshot Is Immutable

Once a Financial Snapshot is created and associated with a successful parse, it **must not be modified in place**.

**Rationale:**

| Principle | Explanation |
|---|---|
| **Auditability** | An auditor must verify that analysis results correspond to a fixed dataset. If the snapshot could be edited after the fact, the chain of evidence from file → parse → calculation → report is broken. |
| **Reproducibility** | Deterministic engines guarantee same input → same output ([ADR 009](009-business-engine-architecture.md)). Immutability ensures the input dataset cannot silently change between re-runs of the same analysis reference. |
| **Deterministic analysis** | Business Engines are synchronous and deterministic. Their correctness depends on stable inputs. Mutable parsed data introduces non-determinism unrelated to engine logic. |
| **Enterprise governance** | Financial decision platforms require frozen analytical inputs for period close, board review, and regulatory inquiry. Immutability is standard governance for derived datasets in enterprise analytics — analogous to sealed evidence in audit workflows. |
| **Correction model** | Errors are corrected by creating a **new snapshot** (new version), not by overwriting the old one. Both remain addressable; analyses explicitly reference which snapshot they used. |

Immutability applies to snapshot **content**. Version metadata may be appended for lineage; the parsed dataset itself is write-once.

---

## 4. Why Business Engines Read Financial Snapshots Instead of Reparsing Excel

Business Engines must consume **validated, stable internal structures** — not external file formats.

**Rationale:**

| Principle | Explanation |
|---|---|
| **Single parse, many analyses** | One uploaded file may feed waste detection, future financial ratio engines, and cross-domain reports. Parsing once into a snapshot amortizes cost and guarantees all engines see identical input. |
| **Engine boundary** | Engines implement business rules and calculations. File format decoding (sheet detection, encoding, column inference) is Parser responsibility — not Calculator or Detector responsibility ([AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §5 constraints). |
| **Performance** | Executive workflows expect responsive analysis. Reparsing large Excel workbooks on every engine invocation adds latency unacceptable for interactive decision support. |
| **Validation gate** | Data Validation and Data Quality assess parsed structures before engine access ([AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §6–7). A snapshot represents data that passed (or was explicitly flagged through) those gates. Engines must not bypass them by reading raw files directly. |
| **Facts integrity** | Facts Contract provenance includes `source` referencing dataset and period ([AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) §9). A snapshot ID provides a precise, auditable source reference — “parser output from file X at version Y” — not “whatever the parser would produce today.” |

---

## 5. Why Reparsing Historical Files After Parser Improvements Is Dangerous

When the Parser improves (bug fixes, new column mappings, better sheet detection), re-running it against old files produces **different internal structures** than those used for historical analyses.

**Risks:**

| Risk | Impact |
|---|---|
| **Retroactive metric drift** | Waste percentages, savings estimates, and dashboard KPIs change without any business event — only because the parser changed. Executives lose trust in reported figures. |
| **Broken audit trail** | An analysis completed in Q2 2026 cannot be explained if its underlying dataset no longer exists and re-parsing yields different record counts or field values. |
| **Non-reproducible decisions** | Board decisions documented against Analysis Run A cannot be reconstructed if the parser that fed A is not the parser that would run today. |
| **Governance violation** | Period-close and compliance workflows assume frozen inputs. Silent re-interpretation of historical files violates that assumption. |
| **Comparability loss** | Quarter-over-quarter and year-over-year comparisons become invalid when the same filename produces structurally different snapshots across time. |

**Correct model:** Parser improvements produce **new snapshot versions**. Historical `analysis_runs` continue referencing the snapshot version that existed when they executed. New analyses may opt into newer snapshots explicitly.

This preserves auditability, reproducibility, deterministic analysis, and enterprise governance — the four pillars named in the Phase 6 review.

---

## 6. Bronze / Silver / Gold Architecture

Khazina adopts a three-layer data maturity model aligned with enterprise analytics practice (medallion / tiered data architecture):

```
┌─────────────────────────────────────────────────────────────┐
│  BRONZE — Original Uploaded File                            │
│  Source of Truth · Immutable · Provenance anchor            │
│  Artifact: financial_files (+ blob storage via storage_path)│
└────────────────────────────┬────────────────────────────────┘
                             │ Parser (once per version)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  SILVER — Financial Snapshot                                │
│  Immutable parsed dataset · Validated internal structures   │
│  Artifact: Financial Snapshot (this ADR)                    │
└────────────────────────────┬────────────────────────────────┘
                             │ Business Engine(s)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  GOLD — Business Results                                    │
│  Deterministic calculations · Facts Contract · Engine output│
│  Artifacts: analysis_runs, waste_analysis_results, reports, │
│             simulation_runs, recommendations, etc.          │
└────────────────────────────┬────────────────────────────────┘
                             │ AI (interpretation only)
                             ▼
                    Executive Decision / Reports
```

### Why this fits Khazina

| Layer | Fit with Khazina |
|---|---|
| **Bronze** | Khazina is not the system of record for transactions. It **receives** exports. Bronze preserves exactly what arrived — matching the Financial Data Repository domain ([BUSINESS_DOMAIN_DISCOVERY.md](../BUSINESS_DOMAIN_DISCOVERY.md) §5.2, §9.2). |
| **Silver** | Khazina’s value begins when unstructured spreadsheets become **governed, validated, internal datasets**. Silver is the decision-intelligence substrate — parsed but not yet interpreted. |
| **Gold** | Khazina’s differentiation is **deterministic business analysis** feeding bounded AI. Gold is where engines compute waste, risk, simulation, and future financial metrics — then Facts flow to AI. Gold maps to existing result tables and the Facts Contract. |

**Explicit boundaries:**

- Bronze does not contain business calculations.
- Silver does not contain engine-derived KPIs or AI narrative.
- Gold does not contain raw spreadsheet cells or unparsed CSV lines.
- AI operates on Gold (Facts), never on Bronze or Silver directly ([ADR 008](008-ai-architecture.md)).

---

## 7. Versioning — Required Metadata and Architectural Responsibility

Each Financial Snapshot must carry versioning and context metadata. This ADR defines **architectural responsibility** for each field. Exact storage shape is deferred to Sprint 6.2 implementation design.

| Field | Architectural responsibility | Why it exists |
|---|---|---|
| **`snapshot_version`** | Identifies this specific immutable snapshot instance for a given file. Increments when a new snapshot is created for the same source file (re-import, re-parse, correction). | Enables multiple snapshots per file without overwriting. Analysis runs bind to a specific snapshot version — not “the file” generically. |
| **`parser_version`** | Records which Parser implementation produced this snapshot (semantic version of parser logic). | When parser behavior changes, provenance is explicit. Auditors can determine whether historical results used parser v1 or v2. Supports the “new parser → new snapshot” model (§8). |
| **`schema_version`** | Records the version of Khazina’s **internal snapshot schema** — the structure Parser maps into. | Parser logic and output shape evolve independently. Schema version tells engines and validators which internal field layout to expect. Prevents silent structural mismatch. |
| **`created_at`** | Timestamp when the snapshot was materialized (parse completion). | Establishes temporal ordering, supports import history alignment, and satisfies audit timeline requirements. |
| **`organization_id`** | Scopes the snapshot to the organizational tenant. | Khazina interprets all data within organizational context ([DATABASE_SCHEMA_DESIGN.md](../DATABASE_SCHEMA_DESIGN.md) §3.1). Snapshots are never cross-org addressable. |
| **`reporting_period_id`** | Associates the snapshot with the active or selected reporting period. | Executive oversight is period-scoped (Q2 2026, etc.). Financial datasets belong to a period for comparability, filtering, and governance — even when the schema supports multiple periods. |

**Additional lineage (recommended, not optional in spirit):**

- **Source file reference** — every snapshot must link to exactly one Bronze file (`financial_files`). Without this, provenance is lost.
- **Import record reference** — linkage to the import attempt that produced the snapshot supports the existing import history UX and failure auditing.

---

## 8. Future Parser Improvements — Versioning Workflow

Parser evolution must never mutate historical analytical inputs.

### Scenario: Parser v1 in production

```
financial_file (Bronze)
        ↓ Parser v1
Financial Snapshot v1  (parser_version=1.x, schema_version=1.x)
        ↓ Waste Engine
analysis_run → waste_analysis_results (Gold)
        ↓ Facts → AI → Report
```

Executives review Q2 waste analysis. Analysis run references **Snapshot v1**.

### Scenario: Parser v2 deployed later

```
Same financial_file (Bronze — unchanged)
        ↓ Parser v2  (explicit re-parse or new import trigger)
Financial Snapshot v2  (parser_version=2.x, schema_version=may differ)
        ↓ Waste Engine
New analysis_run → new waste_analysis_results (Gold)
```

### Why historical analyses must continue referencing Snapshot v1

| Reason | Explanation |
|---|---|
| **Reproducibility** | Re-running the same analysis against Snapshot v1 must yield identical Gold results. Snapshot v1 still exists and is immutable. |
| **Audit defense** | “Why did we report 12.4% waste in June?” must be answerable with the exact dataset used in June — not today’s improved parser. |
| **Explicit upgrade** | Moving to Snapshot v2 is a **conscious re-analysis decision**, not a silent background refresh. Executives should know when figures change because parsing improved vs. because spending changed. |
| **Schema coexistence** | Parser v2 may introduce fields v1 lacked. Engines and validators use `schema_version` to handle both without corrupting v1 consumers. |

**Operational rule:** Parser upgrades create new snapshots. They do not update, replace, or delete existing snapshots. Retention policy for old snapshots is an operational concern — not an architectural permission to mutate them.

---

## 9. Rejected Alternatives

### Alternative A: Reparse Excel on Every Analysis

**Description:** Business Engines (or a pre-engine step) read the original file from Bronze and invoke the Parser fresh for each `analysis_run`.

| Advantages | Disadvantages |
|---|---|
| Always uses latest parser logic — no stale snapshots | **Retroactively changes historical results** when parser improves (§5) |
| No Silver storage layer to design or maintain | **Non-deterministic operational behavior** — same analysis request may yield different inputs at different times |
| Simpler initial data model | **Repeated parse cost** on every engine invocation |
| | **Bypasses validation/quality gate** as a stable checkpoint — validation runs per request, not per governed dataset |
| | **Breaks Facts provenance** — `source` cannot point to a fixed dataset identifier |
| | **Violates enterprise governance** — no frozen input for period close |

**Rejection rationale:** Reparsing optimizes for parser freshness at the expense of auditability, reproducibility, and deterministic analysis — the core requirements of a financial decision intelligence platform. Khazina is not a stateless spreadsheet viewer; it is a governed analytical system. **Rejected.**

---

### Alternative B: Normalized Relational Storage for Parsed Rows

**Description:** Parser output is decomposed into relational tables — one row per spreadsheet row, with normalized account, transaction, vendor, or line-item entities and foreign keys throughout.

| Advantages | Disadvantages |
|---|---|
| Efficient SQL queries on individual fields | **Schema explosion** — every new file type, department export, and column layout requires migration or nullable-column sprawl |
| Familiar to database-centric teams | **Premature domain modeling** — Khazina is not ERP; inventing `accounts`, `ledger_entries`, or `transactions` tables implies ownership Khazina explicitly does not claim |
| Strong referential integrity per cell | **Conflicts with approved JSONB policy** — `financial_files.metadata` was scoped for parse metadata precisely to “avoid schema churn for ingestion pipeline evolution” ([DATABASE_SCHEMA_DESIGN.md](../DATABASE_SCHEMA_DESIGN.md) §11) |
| Good for high-volume transactional systems | **Mismatch with engine input pattern** — Business Engines consume validated dataset references and DTOs, not arbitrary JOINs across import tables ([BUSINESS_ENGINE_ARCHITECTURE.md](../BUSINESS_ENGINE_ARCHITECTURE.md)) |
| | **Blurs Silver/Gold boundary** — normalized rows tempt engines to embed calculation logic in SQL rather than deterministic engine code |
| | **Import pipeline rigidity** — executive uploads are heterogeneous Excel/CSV exports (budget, procurement, payroll), not uniform transactional feeds |

**Rejection rationale:** Normalized row storage treats Khazina as a data warehouse for operational transactions. The platform ingests **heterogeneous executive datasets** and produces **deterministic analytical facts** — not a normalized chart of accounts. The Financial Snapshot captures parser output as a **cohesive, versioned dataset unit** without prematurely modeling every possible spreadsheet column as a relational entity. Normalized storage may be reconsidered in a future ADR if a specific engine domain requires it — it is not the default ingestion architecture. **Rejected as the Sprint 6.2 default.**

---

## Relationship to Existing Schema

This ADR **does not replace** existing entities. It defines a new Silver-layer artifact and clarifies responsibilities:

| Existing entity | Role after this ADR |
|---|---|
| `financial_files` | Bronze inventory — source file metadata, processing lifecycle, blob reference |
| `import_records` | Import attempt log — links file to snapshot creation outcome |
| `data_quality_snapshots` / `data_quality_checks` | Quality assessment **of a snapshot** (or file-to-snapshot pipeline), not a substitute for snapshot storage |
| `analysis_runs` | Gold process parent — must reference the Financial Snapshot version used, in addition to `source_file_id` |
| `reports` | Gold published artifact — provenance chain: report → analysis → snapshot → file |

Sprint 6.2 implementation will introduce Financial Snapshot persistence conforming to this ADR. Schema details require a follow-on design artifact — not defined here per ADR scope rules.

---

## Consequences

### Positive

- Closes the Phase 6 architectural gap — parsed data has an approved home
- Preserves audit trail: file → snapshot → analysis → report
- Aligns with frozen AI and Business Engine architectures (ADR 008, ADR 009)
- Enables safe parser evolution without retroactive metric drift
- Bronze/Silver/Gold model is industry-recognizable for enterprise data governance
- Sprint 6.2 has a normative target to implement against

### Negative

- New artifact and persistence layer to design and implement in Sprint 6.2
- Storage strategy for snapshot payload (format, retention, size limits) still requires implementation design within ADR constraints
- `analysis_runs` provenance model extends — must bind to snapshot version, not file alone
- Additional operational concern: snapshot retention and storage growth as files accumulate

### Neutral / Deferred

- Exact snapshot serialization format (structured document, columnar, etc.) — implementation sprint
- Re-parse triggers and UX for “analyze with latest parser” — future sprint
- Financial Engine (ratios, liquidity) consumption of snapshots — future engine sprints

---

## Compliance Requirements for Sprint 6.2

Implementation **must**:

1. Create immutable Financial Snapshots from Parser output — one snapshot per successful parse version.
2. Preserve Bronze files as source of truth — never delete or mutate files to “fix” snapshots.
3. Bind Business Engine execution to a specific snapshot version — not to live file reparsing.
4. Record `snapshot_version`, `parser_version`, `schema_version`, `created_at`, `organization_id`, and `reporting_period_id` on every snapshot.
5. Ensure historical `analysis_runs` retain their original snapshot reference when new snapshots are created.
6. Keep AI isolated from Bronze and Silver — engines produce Facts from snapshots; AI consumes Facts only.

Implementation **must not**:

1. Reparse Excel/CSV at analysis time as the default path.
2. Store parsed rows as normalized relational entities without a future ADR.
3. Mutate existing snapshots in place.
4. Allow Business Engines to read raw uploaded files directly.

---

## Related Documents

- [AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) — Parser, Validation, Quality, pipeline stages
- [BUSINESS_ENGINE_ARCHITECTURE.md](../BUSINESS_ENGINE_ARCHITECTURE.md) — Engine input and Facts Contract
- [DATABASE_SCHEMA_DESIGN.md](../DATABASE_SCHEMA_DESIGN.md) — Existing Bronze-adjacent entities
- [BUSINESS_DOMAIN_DISCOVERY.md](../BUSINESS_DOMAIN_DISCOVERY.md) — Financial Data Repository domain
- [ADR 008: AI Architecture](008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](009-business-engine-architecture.md)

---

## Approval

| Role | Decision |
|---|---|
| **Architecture Decision** | **APPROVED** |
| **Status** | **Accepted** — effective immediately for Sprint 6.2 and subsequent ingestion work |
| **Rationale** | Financial Snapshot provides the missing Silver layer, satisfies auditability and deterministic analysis requirements, aligns with frozen engine and AI boundaries, and rejects alternatives that compromise enterprise governance |

Sprint 6.2 implementation shall follow this ADR as the authoritative storage and handoff architecture for parsed financial data.
