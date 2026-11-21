# USIS-014 — Validation Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-014 (Validation Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000017` (next free after `UCOS-USIS-000016` = USIS-INT-001). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Validation Architecture (EVO-USIS-014) — establish the constitutional Validation-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Validation tier (governed validation model) owned by the substrate (subordinate to USIS-001…013, USIS-017, USIS-INT-001, and to LAW Ω∞-000 / MIP Parts 19/20/21/22/32) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Validation tier (USIS-004 tier **20 — Validation**; parent tier Implementation/19) — the validation model (grounding, explanation coverage, cross-layer integrity) that discharges the meta-model's **validation closure** obligation |
| DEPENDS-ON | USIS-INT-001 · USIS-017 · USIS-013 · USIS-012 · USIS-011 · USIS-010 · USIS-009 · USIS-008 · USIS-006 · USIS-007 · USIS-004 · `engine/validation` (EPIC-007) / `platform/validation` (EC2-EPIC-010) (referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **20 (Validation)** — discharges the tier's **validation closure** obligation (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · CEP-004 (Constitutional Validation Constitution) · UCIC-001 Stages 5–9 (validation stages); LAW USIS-07 (explainability / grounding); the SCIENCE_INTELLIGENCE lifecycle `VALIDATED` stage (USIS-008) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/07/08/09) · USIS-004 (24-tier meta-model) · CEP-004 (Constitutional Validation Constitution) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the validation mandate conferred by USIS-001 (LAW USIS-07) and the USIS-004 Validation tier, gating the certified spine (USIS-006…017) and its Implementation composition (USIS-INT-001) and referencing the executable validators (`ukb validate`, `ukbx validate`, `engine/validation`, `platform/validation`). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Authored under EVO-USIS-014 as the Wave-2 Validation-tier architecture named "pending" by USIS-INT-001 (Part C — "Validation ownership \| USIS-014 (pending)") and by USIS-013 Part M ("Discharged by USIS-014 (referenced)"). No new constitutional knowledge is introduced: validation laws are inherited from CEP-004 and USIS-001 LAW USIS-07; the executable validators are **referenced** as-is. Canonical home `15-…/15-VALIDATION/` per USIS-005 §2 (area 15 = VALIDATION) and §3 (USIS-006…017 per-layer architectures) — no variance; no structure invented; no `config.py` edit (`^15-…/` already classifies to USIS/VOL-024). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The executable validators (`engine/validation` EC-1, `platform/validation` EC-2, `ukb`/`ukbx`) are **referenced**; the canonical home governs and this architecture holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Validation tier** — the tier that determines, deterministically and fail-closed, whether a realized capability (and, cross-layer, the architecture / implementation / runtime / knowledge / registry / dependency / governance / evidence surfaces it spans) is **valid**. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/15-VALIDATION/` home and defines the Validation node shape, its ontology/taxonomy placement, validation lifecycle, validation model, execution model, governance, orchestration, dependency model, coverage model, evidence model, and traceability model — plus the runtime, registry, knowledge, and cross-layer validation contracts — while remaining independent of any technology, framework, infrastructure, or vendor and **never duplicating** the executable validators. **This instrument establishes only the Validation-tier architecture.** It authors **no** individual validation record or capability instance — those are separately-authorized later (Wave-3/5) realizations, and they are produced by the referenced validators, not by this architecture.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the validation mandate of USIS-001, CEP-004, and the Validation tier (20) of the USIS-004 meta-model:

- **USIS-004 Part C tier 20** — Validation (parent = Implementation, tier 19). USIS-014 is the constitutional architecture and rule-set for this tier; its closure obligation is **validation closure**.
- **USIS-001 LAW USIS-07 (explainability & grounding)** — every claim of validity carries grounding and an explanation; unexplained/ungrounded validity is not a valid state.
- **CEP-004 (Constitutional Validation Constitution)** — the frozen constitutional source of validation law; USIS-014 **references** it and specializes it for the science-intelligence substrate, never forking it (LAW USIS-02).
- **USIS-001 LAW USIS-04** — validation is architecture, not technology: it names no test framework/linter/CI system; the executable validators (`ukb validate`, `ukbx validate`, `engine/validation`, `platform/validation`) are referenced.
- **The spine is the validation subject:** USIS-006…013/017 (architecture tiers) and USIS-INT-001 (Implementation composition) are the surfaces validated, reached **by reference**; USIS-014 `Depends-On` them and re-homes nothing (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-014).** This architecture:
- creates the `15-…/15-VALIDATION/` home and this single registered architecture artifact;
- defines the Validation **node shape, ontology/taxonomy placement, validation lifecycle, validation model, validation-execution model, validation governance, validation orchestration, dependency model, coverage model, evidence model, traceability model**, and the **runtime / registry / knowledge / cross-layer** validation contracts (Parts B–S);
- founds downward-only on `USIS-INT-001/017/013/012/011/010/009/008/006/007/004` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** validation record, test, or capability instance, and begins **no** Wave-3/5 realization;
- reuses, without duplication, the executable validators (`ukb validate`, `ukbx validate`, `engine/validation`, `platform/validation`), CEP-004, UCIC-001 Stages 5–9, GOV-002, TRACK-001, and the governance instruments — and performs **no** `config.py` edit.

## PART B — Validation architecture (the Validation node)

A validation is a typed node of the canonical form:

```
{ id: USIS-VAL-<NAME>, home: 15-VALIDATION/<NAME>/, tier: 20,
  subject: <tier node | composition | cross-layer set under validation>,
  obligation_set: <grounding, explanation-coverage, closure, integrity checks>,
  verdict: VALID | INVALID (fail-closed; no partial),
  validator_ref: <ukb validate | ukbx validate | engine/validation | platform/validation>,
  grounding_contract, explanation_contract, evidence_ref, owner, status }
```

- The node is the meta-model parent of the Certification tier (USIS-004 tier 21): certification consumes a validation verdict.
- It is a **judgement + gate contract** — it binds a subject to an obligation set and yields a fail-closed verdict, executed by a **referenced** validator. It embeds no test runner and names no CI/technology (LAW USIS-04).
- Produces **no** code and **no** validator; validation is performed by the referenced engines (validation independence, Part R).

## PART C — Validation ontology (reference to USIS-005)

Every validation is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares validation concepts (subject, obligation, grounding, explanation-coverage, verdict, defect) and their relations. Ontology Closure (USIS-011 obligation 11) governs. USIS-014 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Validation taxonomy (reference to USIS-005)

Every validation occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the validation taxonomy of **validation kinds**: structural (schema/edges), semantic (grounding/explanation), integrity (append-only/closure), and cross-layer (spanning architecture/implementation/runtime/knowledge/registry/dependency/governance/evidence). Taxonomy Closure (USIS-011 obligation 12) governs. USIS-014 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Validation lifecycle

A validation node follows, under UCIC-001 (Stages 5–9):

```
DEFINED → BOUND (subject + obligation set) → EXECUTED (validator run, referenced) → ADJUDICATED (VALID | INVALID) → REGISTERED → EVOLVING
```

Validation **discharges** the `VALIDATED` stage of the capability lifecycle (DEFINED→GROUNDED→MODELED→REASONED→**VALIDATED**→CERTIFIED→EVOLVING; USIS-008) — it does not redefine that lifecycle (UCIC-001 / USIS-006/008 own it; referenced). No stage skipped; a defect drives a governed REOPEN, never a silent pass (fail-closed).

## PART F — Validation model

The validation model is the deterministic obligation set a subject must discharge to be `VALID`:

| Obligation class | Contract (what "valid" requires) | Discharged by (referenced) |
|------------------|----------------------------------|----------------------------|
| **Structural** | schema conformance; every `Parent`/`Depends-On`/edge endpoint resolves | `ukb validate` (referential integrity) |
| **Append-only** | no duplicate Universal IDs / pages; contiguous append; no renumber | `ukb validate` (append-only ledger) |
| **Acyclic dependency** | the Depends-On graph is a DAG (downward-only) | `ukb validate` / `ukbx` (C-07) |
| **Grounding** | every validity claim is grounded in a registered subject + evidence (LAW USIS-07) | validation record + `ukbx validate` |
| **Explanation coverage** | every decision carries an explanation; coverage complete (LAW USIS-07) | validation record + `ukbx validate` |
| **Closure** | the meta-model tier chain is present, owned, edged (validation closure) | USIS-011 obligations + `ukb build` |
| **Secret-free / provenance** | no secrets; provenance present | `ukbx validate` |

**Fail-closed rule.** A subject is `VALID` **iff every** applicable obligation holds. Any unmet obligation ⇒ `INVALID`; there is no partial-validity state (mirrors USIS-004 Part D completeness law).

## PART G — Validation-execution model

Validation is executed by **referenced** validators bound at the node's `validator_ref`; the architecture specifies *what* is asserted, never *how* a runner works:

| Execution surface | Referenced validator | Assertion |
|-------------------|----------------------|-----------|
| Repository / registry structure | `ukb validate` | append-only, no dup ID/page, referential integrity, acyclic |
| Signal / twin integrity | `ukbx validate` | signals append-only, subjects resolve, provenance present, secret-free |
| Twin certification hard checks | `ukbx twin --check` | UKB-014 hard checks (C-04/05/07/08/09/10/11) |
| Software-stream validation | `engine/validation` (EPIC-007) / `platform/validation` (EC2-EPIC-010) | referenced as-is (frozen/EC-certified) |
| Capability validation stages | UCIC-001 Stages 5–9 | grounding / explanation / closure per capability |

Execution is deterministic and idempotent (re-running on unchanged inputs yields the identical verdict); the architecture adds no execution engine of its own.

## PART H — Validation governance

Validation is **governed** and separated: the validator is not the author of the subject it validates (separation of duties, foreshadowing certification SoD in USIS-015). A verdict of `INVALID` is fail-closed — it **blocks** promotion of the subject (to CERTIFIED, tier 21) until the defect is remediated append-only and re-validated. No validity is inferred from mere existence (STATUS-001 non-projection); no self-attested pass without a validator run is admissible.

## PART I — Validation orchestration

The Validation tier **orchestrates the ordering of obligation discharge** across a subject's surfaces: structural before semantic before cross-layer, so a lower defect short-circuits fail-closed before higher checks run. Orchestration of *engine/pattern internals* is the Engine/Runtime concern (USIS-011/013); the Validation tier orchestrates *obligation evaluation order*, not member resolution — no overlap (Zero-Overlap, USIS-011 obligation 3).

## PART J — Runtime validation

Runtime validation (the runtime surface named by USIS-013 Part M) asserts, by reference: **every self-* pathway is gated** (no ungoverned autonomy), the **governed-autonomy envelope** is declared, and **explanation coverage** of runtime decisions is present (LAW USIS-07). Drift / hallucination / contradiction monitoring is declared by reference to Part 20 models. An ungated self-* pathway ⇒ `INVALID` (fail-closed). USIS-014 owns the *runtime-validation contract*; USIS-013 owns the runtime; the platform runtime executes — referenced.

## PART K — Registry validation

Registry validation asserts that all registers (the seven synchronized registers of REG-AUTO-001 §2) agree with the filesystem: **count parity** (every in-scope artifact registered), **append-only** identity/page allocation, **referential integrity** of every registry edge, and **no parallel/competing registry** (LAW USIS-02). Discharged by `ukb validate` + REG-AUTO-001 §15 (V1–V8). USIS-014 owns the *registry-validation contract*; the registers are owned by the universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`) — referenced, never re-homed.

## PART L — Knowledge validation

Knowledge validation asserts **Knowledge-Once**: no duplicated constitutional knowledge; every knowledge node has exactly one canonical owner and one home (LAW USIS-02/05, GOV-001-T3 No-Orphan); every knowledge reference resolves (no dead reference); the knowledge graph is navigable with no orphan (C-08). Discharged by `ukb validate` (navigability, referential integrity) + `ukbx validate` (twin/knowledge-graph integrity). USIS-014 owns the *knowledge-validation contract*; the knowledge graph is owned by UMB-006 / the universal mechanism — referenced.

## PART M — Cross-layer validation

Cross-layer validation is the tier's distinctive concern: it asserts integrity of references **across** the eight surfaces the mission enumerates — architecture (USIS-006…013/017), implementation (USIS-INT-001), runtime (USIS-013 / `08-RUNTIME`), knowledge (UMB-006), registry (REG-AUTO-001 registers), dependency (Depends-On DAG), governance (UCIC-001 / GOV instruments), and evidence (USIS-016 / TRACK-001). A subject is cross-layer-valid iff **every** cross-layer reference resolves to a registered node, the composite dependency graph remains **acyclic**, and no surface contradicts another (e.g. a registered runtime binding whose engine is unregistered ⇒ `INVALID`). Discharged by `ukb validate` (whole-corpus referential integrity + acyclicity) + `ukbx certify` (integrity domains).

## PART N — Dependency model & Validation independence

- **Dependency model.** `Depends-On` runs downward to the full Wave-2 spine (USIS-INT-001 directly — the Implementation parent tier — and USIS-017/013/012/011/010/009/008/006/007/004 transitively) and references `engine/validation`, `platform/validation`, `ukb`/`ukbx`; `Parent` is the program root (non-chained). No forward reference (USIS-011 obligation 14). Acyclic, downward-only (obligation 5). USIS-015 (Certification, tier 21) `Depends-On` this tier — Validation founds Certification.
- **Validation independence.** The Validation tier is architecture: it defines validation *obligations, verdicts, and governance*, not a concrete test framework/linter/CI. Execution occurs in the referenced validators, never embedded. The validation architecture is fully defined independent of technology, framework, infrastructure, or vendor (LAW USIS-04).

## PART O — Coverage model

Validation **coverage** is the completeness measure of the validation tier itself, and is the basis for the programme's Coverage Closure Certificate:

| Coverage dimension | Definition (100% ⇔) |
|--------------------|----------------------|
| Obligation coverage | every applicable obligation class (Part F) evaluated for the subject |
| Surface coverage | all eight cross-layer surfaces (Part M) validated |
| Spine coverage | every certified Wave-2 layer (USIS-006…017 + INT-001) reachable and referenced |
| Grounding coverage | every validity claim grounded (LAW USIS-07) — no ungrounded PASS |
| Explanation coverage | every verdict carries an explanation (LAW USIS-07) |
| Evidence coverage | every verdict carries an evidence reference (Part P) |

Coverage is machine-derived from the referenced validators' outputs; a coverage gap is itself a defect (fail-closed). **Zero missing scope** ⇔ all dimensions = 100%.

## PART P — Evidence model

Discharged by USIS-016 (Evidence tier, referenced) using UCIC-001 Output-5: each validation records the **subject reference, obligation set evaluated, validator run + result, grounding trace, explanation, and verdict**, appended to the validation evidence trail (TRACK-001). Absence of required evidence ⇒ NOT-DONE (TRACK-001), which is itself an `INVALID` verdict. USIS-014 owns the *evidence contract for validation*; the evidence store is owned by USIS-016 — referenced.

## PART Q — Traceability model

Every validation node is traceable end-to-end (GOV-002): it carries a `Validates`/`Depends-On` edge up to each subject it asserts, and an `Evidenced-By` edge down to its evidence bundle, materialized into `relationships.json` + the Knowledge-Graph Registry by the reused mechanism. Bidirectional resolution (subject ⇄ verdict ⇄ evidence) is itself a validation obligation (Part F structural). USIS-014 owns the *traceability contract for validation*; the traceability spine is owned by UMB-007 / GOV-002 — referenced.

## PART R — Reuse model

Reuse-First (LAW USIS-02): CEP-004 (validation law), `ukb validate` / `ukbx validate` (structural + twin validators), `engine/validation` (EPIC-007) and `platform/validation` (EC2-EPIC-010) (Software-stream validators), UCIC-001 Stages 5–9 (per-capability validation), GOV-002 (traceability), and TRACK-001 (evidence) are **referenced**, never re-homed or re-implemented. USIS-014 adds only the science-intelligence **validation-tier specialization** (the obligation set, verdict semantics, coverage/cross-layer contracts). It creates no second validator, no competing validation registry, and no parallel test framework.

## PART S — Validation (constitutional) invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations).**
1. Duplicate validator / competing validation registry created by USIS-014: **0** (LAW USIS-02).
2. Hard-coded present-day technology/framework/CI in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) validation layers: **0** (LAW USIS-05, obligation 4).
4. Partial-validity state (a subject neither VALID nor INVALID, or "valid with unmet obligations"): **0** (Part F fail-closed).
5. Ungrounded / unexplained validity claim: **0** (LAW USIS-07; Parts F/O).
6. USIS-014 edits to any frozen instrument or Software-stream validator: **0** (obligation 19; `engine/**`, `platform/**` untouched — referenced).
7. Circular ownership / dependency cycles: **0** (obligation 5; Depends-On downward-only).
8. Duplication of Architecture/Implementation/Runtime/Knowledge/Registry/Evidence surface or of any executable validator: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- An unmet obligation ⇒ `INVALID` ⇒ subject promotion blocked (fail-closed) until append-only remediation + re-validation.
- An unresolved cross-layer reference ⇒ Cross-Layer failure (Part M) ⇒ `INVALID`.
- A duplicated validator/registry ⇒ Zero-Duplication violation ⇒ reference the canonical validator.
- Absence of required evidence ⇒ NOT-DONE (TRACK-001) ⇒ `INVALID`. Authoritative history and frozen artifacts are never mutated on remediation; correction is forward-only and append-only.

## PART T — Non-goals

- Authors **no** validation record, test, linter, CI pipeline, or capability instance (Wave-3/5, per-member); those are produced by the referenced validators.
- Is **not** `engine/validation`, `platform/validation`, `ukb validate`, or `ukbx validate` — all referenced.
- Defines **no** certification verdict or evidence store (owned by USIS-015 / USIS-016).
- Names **no** technology/framework/CI/vendor (LAW USIS-04); creates **no** competing validator or validation registry (LAW USIS-02); produces **no** code (implementation independence); admits **no** partial or ungrounded validity (LAW USIS-07; Part F).

---

*END — USIS-014 · VALIDATION ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
