# USIS-009 — Model Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-009 (Model Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000009` (next free after `UCOS-USIS-000008` = USIS-006). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Model Architecture (EVO-USIS-009) — establish the constitutional Model-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Model tier (agnostic, versioned representation) owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, USIS-006, USIS-007, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Model tier (USIS-004 tier 11) — the agnostic representation a capability reasons/learns over, grounded on a Knowledge Object (U24) |
| DEPENDS-ON | USIS-006 · USIS-004 · USIS-002 · Knowledge-Object registry (Universe U24, referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **11 (Model)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 20 (Models/Analytics) · Part 19 (Knowledge grounding) · Part 21 (Learning); conforms to USIS-004 (LAW USIS-08) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the model-representation mandate conferred by USIS-001 (LAW USIS-04 technology neutrality) and the USIS-004 Model tier, grounded on the U24 Knowledge universe and consumed by the Capability tier (USIS-006). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-009-MODEL-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 3 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised from "AUTHORED · AWAITING UCIC AUTHORISATION" to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/10-MODELS/` per USIS-005 §2 (area 10 = MODELS) — no variance; no structure invented. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where a model realizes an existing canonical instance (U24 Knowledge / MIP Part 20), the canonical home governs and this architecture holds only a **reference** (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Model tier** — the agnostic, versioned representation a capability reasons or learns over, grounded on a Knowledge Object. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/10-MODELS/` home and defines the Model node shape and its technology-`binding` boundary, so any present or future model is registered, versioned content — swappable without changing any upper tier (LAW USIS-04). **This instrument establishes only the Model-tier architecture.** It authors **no** individual model or `binding` instance — those are separately-authorized later (Wave-3) per-member realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the model-representation mandate of USIS-001 and the Model tier (11) of the USIS-004 meta-model:

- **USIS-004 Part C tier 11** — Model (parent = Knowledge Object; closure = model appended/versioned). USIS-009 is the constitutional architecture and rule-set for this tier.
- **USIS-004 §4 Agnosticism boundary** — Model (with Algorithm) is one of the two tiers permitted an optional `binding` field carrying present-day technology; the *specification* of the model remains technology-free.
- **USIS-001 LAW USIS-04** — no vendor/cloud/framework/model/language/database is named in architecture; all are registered content behind agnostic registries, swappable without lifecycle change.
- **USIS-006 (Capability)** consumes models; **USIS-008 (Algorithm)** operates over them. USIS-009 `Depends-On` the Capability tier and the Knowledge-Object registry, and **references** them, never duplicating Capability or Domain Architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-009).** This architecture:
- creates the `15-…/10-MODELS/` home and this single registered architecture artifact;
- defines the Model **node shape, grounding edge, versioning, `binding` boundary, registry model, relationships, lifecycle** (Parts B–H);
- founds downward-only on `USIS-006/004/002` and the U24 Knowledge-Object registry (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** model, `binding`, algorithm, or dataset instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, the canonical U24/Part-19 knowledge ontology, UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/10-MODELS/` already classifies to USIS/VOL-024).

## PART B — Model architecture (the Model node)

A model is a typed node of the canonical form:

```
{ id: USIS-MDL-<NAME>, home: 10-MODELS/<NAME>/, tier: 11, version: <v>,
  grounding: <USIS-knowledge-object> (parent), representation_contract,
  binding?: <present-day realization — registered content, swappable>, owner, status }
```

- The node is the meta-model parent of the Algorithm tier (USIS-004): an algorithm operates over/against a model.
- It is **specification only** — the agnostic representation (structure, parameter-contract, semantics). Concrete realizations are carried as `binding` content, the sole place a present-day model may be named (LAW USIS-04; Proof Obligation 1).
- Produces **no** code and binds **no** runtime; the Implementation/Runtime tiers are referenced (implementation/runtime independence, Part K).

## PART C — Model grounding & knowledge ownership (reference to U24)

Every model declares a **grounding edge** to a Knowledge Object owned by the U24 Knowledge universe (Registry-tier / MIP Part 19). Knowledge ownership remains with U24; USIS-009 defines the *grounding contract* and holds a **reference**, never a re-home (LAW USIS-02). Grounding closure: a model without a Knowledge-Object grounding edge is NOT integrated (fail-closed).

## PART D — Model ownership (No-Orphan)

- **Single canonical owner (LAW USIS-05).** Each model has exactly one owning family and one canonical home under `10-MODELS/`. A model missing owner/home ⇒ NOT integrated (fail-closed).
- Every model declares `Parent` (its Knowledge Object) and `Depends-On` edges downward to already-registered nodes; acyclic, rooted at `USIS-GOV-000`.
- No two models own the same canonical representation (Zero-Overlap, obligation 3); a variant registers as a new version/binding on the canonical node, not a duplicate.

## PART E — Model versioning & registry integration

- Every model is a **versioned** row in the **Model Registry** (program registry under `04-REGISTRIES/`), resolving in the Architecture (#10), Knowledge (#4), and Dependency (#9) registries.
- A new version or `binding` **appends** and never overwrites a prior (append-only; CR-INF-007; obligations 7/20); identity never reused.
- The registry is open (no compiled ceiling; obligation 21). Registry projection produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator/registry created (LAW USIS-02). Deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`).

## PART F — Relationship model (Capability / Algorithm / Knowledge / Dataset)

| Relationship | Edge | Direction | Rule |
|--------------|------|-----------|------|
| Model → Knowledge Object | Parent (grounding) | upward-to-established | grounded on a U24 Knowledge Object; **referenced not duplicated** |
| Model → Capability | Reference (serves) | cross | a capability (USIS-006) reasons/learns over the model; referenced |
| Model → Algorithm | Child | downward | an algorithm (USIS-008) operates over the model (Model founds Algorithm) |
| Model → Dataset | Reference (provenance) | cross | training/eval provenance to the Dataset Registry; referenced |
| Model → Evidence | Reference | cross | executed-binding provenance/explanation traces (USIS-016) |

No relationship re-homes its target; all are `Depends-On`/reference edges to established nodes (LAW USIS-02/05). **Domain (USIS-007) and Capability (USIS-006) architectures are referenced, never duplicated.**

## PART G — Model lifecycle

A model node follows, under UCIC-001:

```
DEFINED → GROUNDED (to a Knowledge Object) → MODELED → REGISTERED → (versioned / bound) → EVOLVING
```

New versions and bindings append; all upper tiers are untouched (LAW USIS-03; obligation 20). No stage skipped; defect-driven REOPEN only (evidence preserved).

## PART H — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-006/004/002` and the U24 Knowledge-Object registry; `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). USIS-008 (Algorithm) `Depends-On` this tier — Model founds Algorithm; the higher catalog number of Algorithm (008 vs 009) is a numbering-index artifact, not a cycle (Dependency Report basis).
- **Runtime independence.** The Model tier is pure specification; a `binding`/version executes in the Software/Runtime stream (referenced), never embedded here. A model is fully defined without any runtime present.

## PART I — Validation model

Discharged by USIS-014 (referenced): the agnostic node is validated for **grounding presence** (Knowledge-Object edge; Ontology Closure, obligation 11) and **representation-contract completeness**. A `binding`/version is validated in the Software stream (referenced), with grounding + explanation coverage (LAW USIS-07). Reuse-first admissibility is a validation precondition.

## PART J — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms **agnosticism** (no tech outside `binding`; obligation 1), **grounding closure**, and **canonical ownership**. Reproducibility of a bound model is certified in the realizing capability's UCIC run.

## PART K — Evidence model

Discharged by USIS-016 (referenced) using UCIC-001 Output-5: grounding edge, version lineage, reuse-first search record, and — for executed bindings — provenance/explanation traces (LAW USIS-07). Absence of any required evidence ⇒ NOT-DONE (TRACK-001).

## PART L — Reuse model

Reuse-First (LAW USIS-02): search the Model Registry and the U24 Knowledge universe before creating a node; add a **version/binding** to an existing model rather than forking. Analytics/knowledge models owned by MIP Part 20 / U24 are **referenced**, never re-homed. Capability (USIS-006) and Domain (USIS-007) context is referenced.

## PART M — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011).**
1. Duplicate model catalog/registry created by USIS-009: **0** (LAW USIS-02).
2. Hard-coded present-day technology outside a `binding` field: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed/ungrounded) model layers: **0** (LAW USIS-05, obligation 4).
4. Closed (finite-by-construction) model registry: **0** (obligation 21; the registry is open).
5. USIS-009 edits to any frozen instrument: **0** (obligation 19).
6. Model lacking a Knowledge-Object grounding edge: **0** (grounding closure; C-00.3).
7. Circular ownership / dependency cycles: **0** (obligation 5).
8. Duplication of Domain (USIS-007) or Capability (USIS-006) Architecture: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- A model without a Knowledge-Object grounding edge ⇒ grounding-closure failure ⇒ rejected.
- A concrete model named outside `binding` ⇒ agnosticism violation ⇒ rejected.
- A duplicate representation ⇒ Zero-Duplication violation ⇒ reuse the canonical node (add a version/binding).
- Absence of required grounding/evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART N — Non-goals

- Authors **no** individual model, version, `binding`, algorithm, or dataset instance (Wave-3, per-member).
- Is **not** the Knowledge Object / dataset owner (U24 — referenced), the Algorithm tier (USIS-008), the Capability tier (USIS-006), or the Domain tier (USIS-007).
- Defines **no** pattern, engine, runtime, service, or API/SDK (owned by USIS-010/011/013/012/017).
- Names **no** vendor/framework in the architecture (LAW USIS-04); creates **no** competing model registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-009 · MODEL ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
