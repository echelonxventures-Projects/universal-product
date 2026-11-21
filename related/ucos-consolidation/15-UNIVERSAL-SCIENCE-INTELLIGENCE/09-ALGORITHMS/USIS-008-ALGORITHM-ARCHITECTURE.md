# USIS-008 — Algorithm Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-008 (Algorithm Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000010` (next free after `UCOS-USIS-000009` = USIS-009). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Algorithm Architecture (EVO-USIS-008) — establish the constitutional Algorithm-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Algorithm tier (agnostic, registry-backed method) owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, USIS-006, USIS-007, USIS-009, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Algorithm tier (USIS-004 tier 12) — the agnostic method describing how a capability computes/reasons/learns/analyzes over a model |
| DEPENDS-ON | USIS-009 · USIS-006 · USIS-004 · USIS-002 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **12 (Algorithm)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 20 (Intelligence/Analytics) · Part 21 (Learning); conforms to USIS-004 (LAW USIS-08) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the algorithm-method mandate conferred by USIS-001 (LAW USIS-04 technology neutrality) and the USIS-004 Algorithm tier, operating over the Model tier (USIS-009) and serving the Capability tier (USIS-006). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-008-ALGORITHM-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 4 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised from "AUTHORED · AWAITING UCIC AUTHORISATION" to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/09-ALGORITHMS/` per USIS-005 §2 (area 09 = ALGORITHMS) — no variance; no structure invented. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where an algorithm realizes an existing canonical instance (MIP Part 20), the canonical home governs and this architecture holds only a **reference** (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Algorithm tier** — the agnostic, registry-backed unit describing *how* a capability computes, reasons, learns, or analyzes over a model. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/09-ALGORITHMS/` home and defines the Algorithm node shape and its technology-`binding` boundary, so any present or future algorithm is registered content — swappable without changing any upper tier (LAW USIS-04). **This instrument establishes only the Algorithm-tier architecture.** It authors **no** individual algorithm or `binding` instance — those are separately-authorized later (Wave-3) per-member realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the algorithm-method mandate of USIS-001 and the Algorithm tier (12) of the USIS-004 meta-model:

- **USIS-004 Part C tier 12** — Algorithm (parent = Model/Capability; closure = algorithm appended). USIS-008 is the constitutional architecture and rule-set for this tier.
- **USIS-004 §4 Agnosticism boundary** — Algorithm (with Model) is one of the two tiers permitted an optional `binding` field carrying present-day technology; the *specification* of the algorithm remains technology-free.
- **USIS-001 LAW USIS-04** — no vendor/framework/algorithm is named in architecture; all are registered content behind agnostic registries, swappable without lifecycle change.
- **USIS-009 (Model)** — an algorithm operates over/against a model; **USIS-006 (Capability)** — an algorithm realizes a capability's method. USIS-008 `Depends-On` both and **references** them, and references **USIS-007 (Domain)** for context — never duplicating Domain, Capability, or Model Architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-008).** This architecture:
- creates the `15-…/09-ALGORITHMS/` home and this single registered architecture artifact;
- defines the Algorithm **node shape, ontology/taxonomy placement, composition, lifecycle, registration, registry model, relationships** (Parts B–I);
- founds downward-only on `USIS-009/006/004/002` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** algorithm, `binding`, or pattern instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/09-ALGORITHMS/` already classifies to USIS/VOL-024).

## PART B — Algorithm architecture (the Algorithm node)

An algorithm is a typed node of the canonical form:

```
{ id: USIS-ALG-<NAME>, home: 09-ALGORITHMS/<NAME>/, tier: 12, version: <v>,
  model: <USIS-MDL-*> (parent), capability?: <USIS-CAP-*>, io_contract,
  binding?: <present-day realization — registered content, swappable>, owner, status }
```

- The node is the meta-model parent of the Pattern tier (USIS-004): patterns compose algorithms.
- It is **specification only** — the agnostic method (inputs/outputs contract, semantics). Concrete realizations are carried as `binding` content, the sole place a present-day algorithm may be named (LAW USIS-04; Proof Obligation 1).
- Produces **no** code and binds **no** runtime directly; the Implementation/Runtime tiers are referenced (implementation/runtime independence, Parts J/K).

## PART C — Algorithm ontology (reference to USIS-005)

Every algorithm is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares the method concepts it realizes and their relations to model/capability concepts. Ontology Closure (obligation 11) governs. USIS-008 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Algorithm taxonomy (reference to USIS-005)

Every algorithm occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the algorithm taxonomy of methods (e.g. by paradigm) under its model/capability. Taxonomy Closure (obligation 12) governs. USIS-008 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Algorithm composition

- An algorithm **composes** over a Model (USIS-009) by a parent grounding edge and may reference sibling algorithms by role, never embedding their content.
- Patterns (USIS-010) compose algorithms into method shapes by reference; an algorithm exposes its I/O contract for such composition.
- A new `binding` attaches to the agnostic node by append — the node and all upper tiers are unchanged (LAW USIS-03).

## PART F — Algorithm lifecycle

An algorithm node follows, under UCIC-001:

```
DEFINED → MODELED (bound to a Model) → REGISTERED → (bound / versioned) → EVOLVING
```

Adding or swapping a `binding` is an append that leaves the node and all upper tiers unchanged (obligation 20). No stage skipped; defect-driven REOPEN only (evidence preserved).

## PART G — Algorithm registration

- Every algorithm is a versioned row in the **Algorithm Registry** (program registry under `04-REGISTRIES/`), resolving in the Architecture (#10), Knowledge (#4), and Dependency (#9) registries.
- The `binding` sub-field records a swappable concrete realization; a new version/binding **appends** and never overwrites (append-only; CR-INF-007; obligations 7/20). Identity never reused.
- The registry is open (no ceiling; obligation 21). Projection produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator/registry created (LAW USIS-02). Deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`).

## PART H — Relationship model (Domain / Capability / Model / Runtime)

| Relationship | Edge | Direction | Rule |
|--------------|------|-----------|------|
| Algorithm → Model | Parent (operates-over) | upward-to-established | grounded on a Model (USIS-009); **referenced not duplicated** |
| Algorithm → Capability | Reference (realizes) | cross | realizes a capability's method (USIS-006); **referenced not duplicated** |
| Algorithm → Domain | Reference (context) | cross | inherits its capability's domain context (USIS-007); **referenced not duplicated** |
| Algorithm → Pattern | Child | downward | patterns (USIS-010) compose algorithms (Algorithm founds Pattern) |
| Algorithm → Runtime | Reference | cross | an executed `binding` runs under the Runtime tier (USIS-013)/platform runtime; referenced, never embedded |
| Algorithm → Evidence | Reference | cross | reasoning/analytics traces (USIS-016) |

No relationship re-homes its target; all are `Depends-On`/reference edges to established nodes (LAW USIS-02/05). **Domain (USIS-007), Capability (USIS-006), and Model (USIS-009) architectures are referenced, never duplicated.**

## PART I — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-009/006/004/002`; `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). Note: the catalog number of Algorithm (008) precedes Model (009); the *dependency* runs upward to Model — a numbering-index artifact, not a cycle (Dependency Report basis).
- **Runtime independence.** The Algorithm tier is pure specification; a `binding` executes in the Software/Runtime stream (referenced), never embedded here. An algorithm is fully defined without any runtime present.

## PART J — Validation model

Discharged by USIS-014 (referenced): the agnostic node is validated for **I/O-contract completeness**, **model-grounding** (parent Model edge), and **reuse-first admissibility**. A `binding` is validated in the Software stream (referenced), with grounding + explanation coverage (LAW USIS-07).

## PART K — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms **agnosticism** (no tech outside `binding`; obligation 1), model-grounding, and **canonical ownership**. Binding certification is deferred to the realizing capability's UCIC run.

## PART L — Evidence model

Discharged by USIS-016 (referenced) using UCIC-001 Output-5: registry-row provenance, reuse-first search record (proving no duplicate), and — for executed bindings — reasoning/analytics traces with provenance (LAW USIS-07). Absence ⇒ NOT-DONE (TRACK-001).

## PART M — Reuse model

Reuse-First (LAW USIS-02): search the Algorithm Registry before creating a node; attach a new `binding` to an existing agnostic node rather than creating a parallel node. Analytics/learning algorithms owned by MIP Part 20/21 are **referenced**, never re-homed. Model (USIS-009), Capability (USIS-006), and Domain (USIS-007) context is referenced.

## PART N — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011).**
1. Duplicate algorithm catalog/registry created by USIS-008: **0** (LAW USIS-02).
2. Hard-coded present-day technology outside a `binding` field: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed/ungrounded) algorithm layers: **0** (LAW USIS-05, obligation 4).
4. Closed (finite-by-construction) algorithm registry: **0** (obligation 21; the registry is open).
5. USIS-008 edits to any frozen instrument: **0** (obligation 19).
6. Algorithm lacking a parent Model/Capability edge: **0** (grounding closure; C-00.3).
7. Circular ownership / dependency cycles: **0** (obligation 5).
8. Duplication of Domain (USIS-007) / Capability (USIS-006) / Model (USIS-009) Architecture: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- A named concrete algorithm outside a `binding` field ⇒ agnosticism violation ⇒ rejected.
- An algorithm with no parent Model/Capability ⇒ orphan ⇒ non-registerable.
- A duplicate of an existing registry algorithm ⇒ Zero-Duplication violation ⇒ reuse the canonical node (add a `binding`).
- Absence of required evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART O — Non-goals

- Authors **no** individual algorithm, `binding`, or pattern instance (Wave-3, per-member).
- Is **not** the Model tier (USIS-009), the Capability tier (USIS-006), the Domain tier (USIS-007), or the Pattern/Engine that consumes algorithms (USIS-010/011).
- Defines **no** runtime, service, or API/SDK (owned by USIS-013/012/017).
- Names **no** vendor/framework in the architecture (LAW USIS-04); creates **no** competing algorithm registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-008 · ALGORITHM ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
