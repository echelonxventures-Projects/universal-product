# USIS-010 — Pattern Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-010 (Pattern Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000011` (next free after `UCOS-USIS-000010` = USIS-008). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Pattern Architecture (EVO-USIS-010) — establish the constitutional Pattern-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Pattern tier (agnostic composition of algorithms/models into reusable method shapes) owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, USIS-006, USIS-007, USIS-008, USIS-009, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Pattern tier (USIS-004 tier 13) — the technology-free composition capturing a reusable reasoning/learning/analytics/science method |
| DEPENDS-ON | USIS-008 · USIS-009 · USIS-004 · USIS-002 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **13 (Pattern)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 20 (Intelligence/Analytics) · Part 21 (Learning); conforms to USIS-004 (LAW USIS-08) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the pattern-composition mandate conferred by USIS-001 (LAW USIS-04 technology neutrality / LAW USIS-02 reuse) and the USIS-004 Pattern tier, composing the Algorithm (USIS-008) and Model (USIS-009) tiers. Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-010-PATTERN-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 5 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised from "AUTHORED · AWAITING UCIC AUTHORISATION" to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/11-PATTERNS/` per USIS-005 §2 (area 11 = PATTERNS) — no variance; no structure invented. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where a pattern realizes an existing canonical method shape (MIP Part 20/21), the canonical home governs and this architecture holds only a **reference** (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Pattern tier** — the technology-free composition of algorithms/models capturing a reusable reasoning, learning, analytics, or scientific method (an inference schema, a learning-loop shape, an analytic-pipeline shape). This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/11-PATTERNS/` home and defines the Pattern node shape as composition-over-roles, so recurring methods are named once and composed by engines without hard-coding (LAW USIS-04). **This instrument establishes only the Pattern-tier architecture.** It authors **no** individual pattern instance — those are separately-authorized later (Wave-3) per-member realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the pattern-composition mandate of USIS-001 and the Pattern tier (13) of the USIS-004 meta-model:

- **USIS-004 Part C tier 13** — Pattern (parent = Algorithm). USIS-010 is the constitutional architecture and rule-set for this tier — the last agnostic (specification) tier before Engine.
- **USIS-001 LAW USIS-04** — patterns compose algorithm/model *references*, enumerating no concrete member; the engine (USIS-011) resolves members at reference time (Zero Hard Coding).
- **USIS-001 LAW USIS-02** — a pattern reuses existing canonical algorithms (USIS-008) and models (USIS-009) by reference; it forks no method.
- **USIS-008 (Algorithm)** and **USIS-009 (Model)** are composed by reference; **USIS-006 (Capability)** and **USIS-007 (Domain)** provide context. USIS-010 `Depends-On` Algorithm/Model and **references** all four — never duplicating their architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-010).** This architecture:
- creates the `15-…/11-PATTERNS/` home and this single registered architecture artifact;
- defines the Pattern **node shape, ontology/taxonomy placement, composition, lifecycle, registration, registry model, relationships** (Parts B–I);
- founds downward-only on `USIS-008/009/004/002` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** pattern instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/11-PATTERNS/` already classifies to USIS/VOL-024).

## PART B — Pattern architecture (the Pattern node)

A pattern is a typed node of the canonical form:

```
{ id: USIS-PAT-<NAME>, home: 11-PATTERNS/<NAME>/, tier: 13,
  roles: [ { role, kind: algorithm|model, contract } ], edges: [ role→role ],
  owner, status }
```

- The node is the meta-model parent of the Engine tier (USIS-004): engines execute patterns by resolving their roles from registries.
- It is **pure specification** — a named composition of algorithm/model roles with an edge structure but **no concrete member** (LAW USIS-04; Proof Obligation 1).
- Produces **no** code and binds **no** runtime; the Engine/Runtime tiers are referenced (implementation/runtime independence, Part I).

## PART C — Pattern ontology (reference to USIS-005)

Every pattern is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares the method concepts it composes and their relations. Ontology Closure (obligation 11) governs. USIS-010 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Pattern taxonomy (reference to USIS-005)

Every pattern occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the pattern taxonomy of method shapes (reasoning / learning / analytics / science). Taxonomy Closure (obligation 12) governs. USIS-010 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Pattern composition

- A pattern **composes** Algorithm (USIS-008) and Model (USIS-009) nodes by **role reference** — each role names an algorithm/model *contract*, not an instance; members remain canonically owned by their own tiers.
- The composition is an acyclic role-edge structure; a pattern may reference sibling patterns by role.
- A pattern admits a new member role by append — no pattern is redefined to admit one (LAW USIS-03).

## PART F — Pattern lifecycle

A pattern node follows, under UCIC-001:

```
DEFINED → COMPOSED (roles bound to algorithm/model registry contracts) → REGISTERED → EVOLVING
```

Patterns admit new algorithm/model members by reference without redefinition (obligation 20). No stage skipped; defect-driven REOPEN only (evidence preserved).

## PART G — Pattern registration

- Every pattern is a row in the **Pattern Registry** (program registry under `04-REGISTRIES/`), resolving in the Architecture (#10), Knowledge (#4), and Dependency (#9) registries.
- Composition is expressed as role references to the Algorithm/Model registries, resolved deterministically. A new pattern **appends** a row + homed artifact; nothing is rewritten (append-only; CR-INF-007; obligations 7/20). Identity never reused.
- The registry is open (no ceiling; obligation 21). Projection produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator/registry created (LAW USIS-02). Deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`).

## PART H — Relationship model (Domain / Capability / Model / Algorithm / Runtime)

| Relationship | Edge | Direction | Rule |
|--------------|------|-----------|------|
| Pattern → Algorithm | Parent / composition | upward-to-established | composes algorithm roles (USIS-008); **referenced not duplicated** |
| Pattern → Model | Reference / composition | cross | composes model roles (USIS-009); **referenced not duplicated** |
| Pattern → Capability | Reference (serves) | cross | a capability's method is expressed as a pattern (USIS-006); referenced |
| Pattern → Domain | Reference (context) | cross | inherits domain context (USIS-007); referenced |
| Pattern → Engine | Child | downward | engines (USIS-011) execute patterns (Pattern founds Engine) |
| Pattern → Runtime | Reference | cross | an executed pattern runs under Engine→Runtime (USIS-013); referenced, never embedded |
| Pattern → Evidence | Reference | cross | method-explanation traces (USIS-016) |

No relationship re-homes its target; all are `Depends-On`/reference edges to established nodes (LAW USIS-02/05). **Domain (USIS-007), Capability (USIS-006), Model (USIS-009), and Algorithm (USIS-008) architectures are referenced, never duplicated.**

## PART I — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-008/009/004/002`; `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). USIS-011 (Engine) `Depends-On` this tier — Pattern founds Engine.
- **Runtime independence.** The Pattern tier is pure specification; a pattern executes only when an engine (USIS-011) resolves and runs it under a runtime (USIS-013), both referenced. A pattern is fully defined without any engine or runtime present.

## PART J — Validation model

Discharged by USIS-014 (referenced): a pattern is valid only if every composed role resolves to a registered algorithm/model contract (Dependency Closure, obligation 14), the composition is acyclic, and no concrete member is enumerated (agnosticism, obligation 1). Explanation coverage of the method is required (LAW USIS-07).

## PART K — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms **agnostic composition** (no hard-coded member; obligation 1), reuse-first admissibility, and **canonical ownership**.

## PART L — Evidence model

Discharged by USIS-016 (referenced) using UCIC-001 Output-5: role-resolution record (which registry contracts fill each role), reuse-first search record, and method-explanation trace. Absence ⇒ NOT-DONE (TRACK-001).

## PART M — Reuse model

Reuse-First (LAW USIS-02): search the Pattern Registry before creating a shape; extend an existing pattern by adding member roles rather than forking. Reasoning/learning/analytics method shapes already owned by MIP Part 20/21 are **referenced**. Algorithm (USIS-008), Model (USIS-009), Capability (USIS-006), Domain (USIS-007) are referenced.

## PART N — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011).**
1. Duplicate pattern catalog/registry created by USIS-010: **0** (LAW USIS-02).
2. Hard-coded present-day technology / enumerated concrete member in a pattern: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) pattern layers: **0** (LAW USIS-05, obligation 4).
4. Closed (finite-by-construction) pattern registry: **0** (obligation 21; the registry is open).
5. USIS-010 edits to any frozen instrument: **0** (obligation 19).
6. Pattern with an unresolved composed role: **0** (Dependency Closure; C-00.3).
7. Circular ownership / dependency / composition cycles: **0** (obligation 5).
8. Duplication of Domain/Capability/Model/Algorithm Architecture: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- An unresolved composed role ⇒ Dependency-Closure failure ⇒ rejected.
- An enumerated concrete member inside the pattern ⇒ hard-coding violation ⇒ rejected.
- A duplicate of an existing method shape ⇒ Zero-Duplication violation ⇒ reuse the canonical pattern.
- Absence of required evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART O — Non-goals

- Authors **no** individual pattern, pipeline, or concrete-member instance (Wave-3, per-member).
- Is **not** the Algorithm (USIS-008), Model (USIS-009), Capability (USIS-006), or Domain (USIS-007) tier, nor the Engine that executes patterns (USIS-011).
- Defines **no** runtime, service, or API/SDK (owned by USIS-013/012/017).
- Names **no** technology or concrete member (LAW USIS-04); creates **no** competing pattern registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-010 · PATTERN ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
