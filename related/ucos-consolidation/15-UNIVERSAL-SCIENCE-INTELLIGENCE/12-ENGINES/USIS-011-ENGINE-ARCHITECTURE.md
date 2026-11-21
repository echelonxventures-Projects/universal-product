# USIS-011 — Engine Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-011 (Engine Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000012` (next free after `UCOS-USIS-000011` = USIS-010). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Engine Architecture (EVO-USIS-011) — establish the constitutional Engine-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Engine tier (registry-resolving pattern executor) owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, USIS-006, USIS-007, USIS-008, USIS-009, USIS-010, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Engine tier (USIS-004 tier 14) — executes patterns by resolving algorithm/model registry contracts at reference time, enumerating no member |
| DEPENDS-ON | USIS-010 · USIS-008 · USIS-009 · USIS-004 · USIS-002 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **14 (Engine)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 20 (Intelligence/Analytics) · Part 21 (Learning); conforms to USIS-004 (LAW USIS-08); the constitutional Zero-Hard-Coding surface (USIS-001 Part C) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the engine-execution mandate conferred by USIS-001 (LAW USIS-04 zero hard coding) and the USIS-004 Engine tier, executing the Pattern tier (USIS-010) by resolving Algorithm (USIS-008)/Model (USIS-009) registry contracts. Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-011-ENGINE-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 6 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised from "AUTHORED · AWAITING UCIC AUTHORISATION" to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/12-ENGINES/` per USIS-005 §2 (area 12 = ENGINES) — no variance; no structure invented. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where an engine realizes an existing canonical execution concern (`08-RUNTIME` / U26), the canonical home governs and this architecture holds only a **reference** (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Engine tier** — the tier that *executes* patterns by resolving algorithm/model registry contracts at reference time, enumerating no member. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/12-ENGINES/` home and defines the Engine node shape and its zero-hard-coding contract, so a single engine shape orchestrates all present and future methods by registration — independent of any technology, framework, runtime, infrastructure, vendor, or implementation (LAW USIS-04). **This instrument establishes only the Engine-tier architecture.** It authors **no** individual engine instance — those are separately-authorized later (Wave-3) per-member realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the engine-execution mandate of USIS-001 and the Engine tier (14) of the USIS-004 meta-model:

- **USIS-004 Part C tier 14** — Engine (parent = Pattern; closure = zero-hard-coding). USIS-011 is the constitutional architecture and rule-set for this tier — the first execution-oriented tier that yet remains architecture (references registries, enumerates nothing).
- **USIS-001 LAW USIS-04 / Part C (Zero Hard Coding)** — no engine contains an enumerated list of algorithms/models/domains; all are resolved from registries by contract.
- **USIS-010 (Pattern)** is executed; **USIS-008 (Algorithm)** and **USIS-009 (Model)** are resolved by registry contract; **USIS-006 (Capability)** and **USIS-007 (Domain)** provide context. USIS-011 `Depends-On` Pattern (+ Algorithm/Model registries) and **references** all — never duplicating their architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-011).** This architecture:
- creates the `15-…/12-ENGINES/` home and this single registered architecture artifact;
- defines the Engine **node shape, ontology/taxonomy placement, lifecycle, composition, orchestration, pattern-execution model, registry model, relationships** (Parts B–J);
- founds downward-only on `USIS-010/008/009/004/002` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** engine instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/12-ENGINES/` already classifies to USIS/VOL-024).

## PART B — Engine architecture (the Engine node)

An engine is a typed node of the canonical form:

```
{ id: USIS-ENG-<NAME>, home: 12-ENGINES/<NAME>/, tier: 14,
  executes: <USIS-PAT-* pattern contract>, resolves: [ registry-contract refs ],
  execution_contract, owner, status }
```

- The node is the meta-model parent of the Runtime tier (USIS-004): a runtime hosts an engine.
- It is a **resolver contract** — it binds pattern roles to registry members at reference time and holds registry *contracts*, not rows or enumerations (LAW USIS-04; Proof Obligation 1).
- Produces **no** code and embeds **no** runtime; the Runtime/Implementation tiers are referenced (runtime independence, Part I).

## PART C — Engine ontology (reference to USIS-005)

Every engine is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares the execution concepts it realizes and their relations to pattern/algorithm/model concepts. Ontology Closure (obligation 11) governs. USIS-011 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Engine taxonomy (reference to USIS-005)

Every engine occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the engine taxonomy of execution kinds (reasoning / analytics / learning / simulation orchestration). Taxonomy Closure (obligation 12) governs. USIS-011 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Engine lifecycle

An engine node follows, under UCIC-001:

```
DEFINED → BOUND-BY-CONTRACT (to pattern + registries) → REGISTERED → EVOLVING
```

New members become executable purely by registry append — the engine is never edited to admit one (LAW USIS-03; obligation 20). No stage skipped; defect-driven REOPEN only (evidence preserved).

## PART F — Engine composition & orchestration

- **Composition.** An engine composes a Pattern (USIS-010) by reference and resolves the pattern's algorithm/model roles from the Algorithm/Model registries at reference time; it may compose sub-engines by contract.
- **Orchestration.** The engine's execution contract sequences the resolved members according to the pattern's edge structure — the *orchestration of pattern execution* — without embedding any member or ordering literal beyond the pattern contract. Orchestration is deterministic given the resolved registry state.

## PART G — Pattern execution & upper-tier realization models

| Realized | Model (how the engine realizes it, by reference) |
|----------|--------------------------------------------------|
| **Pattern execution** | resolves the pattern's roles from registries and executes its edge structure (the engine is the pattern executor; USIS-010 founds USIS-011) |
| **Algorithm execution** | invokes each resolved Algorithm (USIS-008) through its registry I/O contract; a concrete `binding` runs in the Software/Runtime stream (referenced) |
| **Model realization** | operates over each resolved Model (USIS-009) via its representation contract; concrete model bindings are registered content (referenced) |
| **Capability realization** | an engine realizes a Capability's (USIS-006) method by executing the capability's pattern; the engine is the execution surface of the capability, referenced |
| **Domain realization** | inherits the capability's Domain (USIS-007) context by reference |

All realization is by **reference/registry contract**; the engine enumerates and re-homes nothing (LAW USIS-02/04).

## PART H — Registry integration

- Engines are recorded in the **Architecture Registry** (target #10) and resolve, at reference time, against the Algorithm/Model/Pattern registries (`04-REGISTRIES/`).
- The engine holds registry *contracts*, not rows; resolution is deterministic and open (adding a member changes no engine; obligation 20). A new engine **appends** a homed artifact; nothing is rewritten (append-only; CR-INF-007). Identity never reused.
- Projection produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator/registry created (LAW USIS-02). Deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`).

## PART I — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-010/008/009/004/002`; `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). USIS-013 (Runtime) `Depends-On` this tier — Engine founds Runtime.
- **Runtime independence.** The Engine tier is architecture, not runtime: it defines *what* is resolved and orchestrated, not *where/how* it runs. Execution occurs only when a runtime (USIS-013)/platform runtime (`08-RUNTIME`/RIE) hosts the engine, referenced never embedded. An engine is fully defined independent of technology, framework, runtime, infrastructure, vendor, or implementation.

## PART J — Validation model

Discharged by USIS-014 (referenced): an engine is valid only if it contains **zero member enumeration** (grep audit, obligation 1) and **every referenced registry contract resolves** (Dependency Closure, obligation 14). Explanation coverage of executed reasoning is required (LAW USIS-07).

## PART K — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms **zero hard coding**, registry-contract resolution, and **canonical ownership**. An engine that enumerates members cannot be certified (fail-closed).

## PART L — Evidence model

Discharged by USIS-016 (referenced) using UCIC-001 Output-5: zero-hard-coding audit record, registry-resolution log, and execution/reasoning traces with provenance (LAW USIS-07). Absence ⇒ NOT-DONE (TRACK-001).

## PART M — Reuse model

Reuse-First (LAW USIS-02): search the Architecture Registry for an engine shape before creating one; extend behavior by registering new patterns/members, not by adding engines. Runtime/simulation execution owned by `08-RUNTIME`/U26 is **referenced**, never duplicated. Pattern (USIS-010), Algorithm (USIS-008), Model (USIS-009), Capability (USIS-006), Domain (USIS-007) are referenced.

## PART N — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations).**
1. Duplicate engine catalog/registry created by USIS-011: **0** (LAW USIS-02).
2. Hard-coded present-day technology / enumerated member in an engine: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) engine layers: **0** (LAW USIS-05, obligation 4).
4. Closed (finite-by-construction) engine set: **0** (obligation 21; open).
5. USIS-011 edits to any frozen instrument: **0** (obligation 19).
6. Engine with an unresolved registry contract: **0** (Dependency Closure; C-00.3).
7. Circular ownership / dependency cycles: **0** (obligation 5).
8. Duplication of Pattern/Algorithm/Model/Capability/Domain Architecture: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- Any enumerated member in an engine ⇒ hard-coding violation ⇒ non-certifiable/rejected.
- An unresolved registry contract ⇒ Dependency-Closure failure ⇒ rejected.
- Two engines claiming the same execution concern ⇒ Zero-Overlap violation.
- Absence of required evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART O — Non-goals

- Authors **no** individual engine instance (Wave-3, per-member).
- Is **not** the Pattern (USIS-010), Algorithm (USIS-008), Model (USIS-009), Capability (USIS-006), or Domain (USIS-007) tier, nor the Runtime that hosts engines (USIS-013), nor the platform runtime/simulation (`08-RUNTIME`/U26).
- Defines **no** service or API/SDK (owned by USIS-012/017).
- Enumerates no algorithm/model/domain; names **no** technology/framework/infrastructure/vendor (LAW USIS-04); creates **no** competing registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-011 · ENGINE ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
