# USIS-015 — Certification Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-015 (Certification Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000018` (next free after `UCOS-USIS-000017` = USIS-014). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Certification Architecture (EVO-USIS-015) — establish the constitutional Certification-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Certification tier (governed certification model) owned by the substrate (subordinate to USIS-001…014, USIS-017, USIS-INT-001, and to LAW Ω∞-000 / MIP Parts 19/20/21/22/32) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Certification tier (USIS-004 tier **21 — Certification**; parent tier Validation/20) — the certification model (fail-closed gates, separation of duties, certified standing) that discharges the meta-model's **certification closure** obligation |
| DEPENDS-ON | USIS-014 · USIS-INT-001 · USIS-017 · USIS-013 · USIS-012 · USIS-011 · USIS-010 · USIS-009 · USIS-008 · USIS-006 · USIS-007 · USIS-004 · `engine/universal_certification` (UCOS-EPIC-006) / `platform/certification` (EC2-EPIC-011) (referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **21 (Certification)** — discharges the tier's **certification closure** obligation (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · CEP-005 (Constitutional Certification Constitution) · UCIC-001 (certification gate); the SCIENCE_INTELLIGENCE lifecycle `CERTIFIED` stage (USIS-008); the Digital-Twin Certification Runtime (UMB-IMP-006 / UMB-017) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/07/08/09) · USIS-004 (24-tier meta-model) · CEP-005 (Constitutional Certification Constitution) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the certification mandate conferred by USIS-001 and the USIS-004 Certification tier, gating the validated spine (USIS-006…017 + USIS-INT-001, discharged VALID by USIS-014) and referencing the executable certifiers (`ukbx certify`, `ukbx twin --check`, `engine/universal_certification`, `platform/certification`). It confers a certification *verdict* only; it creates no new governance authority and authorizes no code. Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Authored under EVO-USIS-015 (parent programme EVO-USIS-014) as the Wave-2 Certification-tier architecture named "pending" by USIS-INT-001 (Part C — "Certification ownership \| USIS-015 (pending)"), USIS-013 Part N, and USIS-014 (which foreshadows certification SoD). No new constitutional knowledge is introduced: certification law is inherited from CEP-005 and the meta-model; the executable certifiers are **referenced** as-is. Canonical home `15-…/16-CERTIFICATION/` per USIS-005 §2 (area 16 = CERTIFICATION) and §3 (USIS-006…017 per-layer architectures) — no variance; no structure invented; no `config.py` edit (`^15-…/` already classifies to USIS/VOL-024). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The executable certifiers (`engine/universal_certification` EC-1, `platform/certification` EC-2, `ukbx certify`) are **referenced**; the canonical home governs and this architecture holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Certification tier** — the tier that confers, deterministically and fail-closed, **certified standing** on a validated capability (and, cross-layer, the architecture / implementation / runtime / registry / knowledge / governance / validation / evidence / Digital-Twin surfaces it spans, and future UCOS universes). This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/16-CERTIFICATION/` home and defines the Certification node shape, its ontology/taxonomy placement, certification lifecycle, certification model, execution model, governance, orchestration, dependency model, evidence model, traceability, coverage, and **certification authority** — plus the Digital-Twin, runtime, registry, knowledge, and cross-layer certification contracts — while remaining technology-/implementation-/infrastructure-/platform-agnostic and vendor-neutral, and **never duplicating** the executable certifiers. **This instrument establishes only the Certification-tier architecture.** It authors **no** individual certification record or capability instance — those are produced by the referenced certifiers, not by this architecture.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the certification mandate of USIS-001, CEP-005, and the Certification tier (21) of the USIS-004 meta-model:

- **USIS-004 Part C tier 21** — Certification (parent = Validation, tier 20). USIS-015 is the constitutional architecture and rule-set for this tier; its closure obligation is **certification closure**.
- **CEP-005 (Constitutional Certification Constitution)** — the frozen constitutional source of certification law; USIS-015 **references** it and specializes it for the science-intelligence substrate, never forking it (LAW USIS-02).
- **USIS-001 LAW USIS-07 (explainability & grounding)** — a certification verdict carries grounding, evidence, and an explanation; unexplained certification is not a valid state.
- **USIS-001 LAW USIS-04** — certification is architecture, not technology: it names no CI system/attestation vendor; the executable certifiers (`ukbx certify`, `engine/universal_certification`, `platform/certification`) are referenced.
- **The validated spine is the certification subject:** USIS-006…013/017 + USIS-INT-001 (adjudicated `VALID` by USIS-014) are the surfaces certified, reached **by reference**; USIS-015 `Depends-On` USIS-014 and re-homes nothing (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-015).** This architecture:
- creates the `15-…/16-CERTIFICATION/` home and this single registered architecture artifact;
- defines the Certification **node shape, ontology/taxonomy placement, certification lifecycle, certification model, certification-execution model, certification governance, certification orchestration, dependency model, evidence model, traceability, coverage, and certification authority**, and the **Digital-Twin / runtime / registry / knowledge / cross-layer** certification contracts (Parts B–T);
- founds downward-only on `USIS-014/INT-001/017/013/012/011/010/009/008/006/007/004` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** certification record, gate implementation, or capability instance, and begins **no** Wave-3/5 realization;
- reuses, without duplication, the executable certifiers (`ukbx certify`, `ukbx twin --check`, `engine/universal_certification`, `platform/certification`), CEP-005, UCIC-001, GOV-002, TRACK-001, and the governance instruments — and performs **no** `config.py` edit.

## PART B — Certification architecture (the Certification node)

A certification is a typed node of the canonical form:

```
{ id: USIS-CRT-<NAME>, home: 16-CERTIFICATION/<NAME>/, tier: 21,
  subject: <validated tier node | composition | cross-layer set>,
  validation_ref: <USIS-014 verdict = VALID (precondition)>,
  gate_set: <CCE 10 fail-closed gates>, separation_of_duties: certifier ≠ author/executor,
  verdict: CERTIFIED | NOT-CERTIFIED (fail-closed; no partial),
  certifier_ref: <ukbx certify | ukbx twin --check | engine/universal_certification | platform/certification>,
  evidence_ref, explanation_contract, owner, status }
```

- The node is the meta-model parent of the Evidence tier (USIS-004 tier 22): evidence bundles a certification verdict.
- It is a **gate + attestation contract** — it binds a validated subject to a gate set and yields a fail-closed certified verdict under separation of duties, executed by a **referenced** certifier. It embeds no CI runner and names no vendor (LAW USIS-04).
- Produces **no** code and **no** certifier; certification is performed by the referenced engines (certification independence, Part S).

## PART C — Certification ontology (reference to USIS-005)

Every certification is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares certification concepts (subject, gate, verdict, certified-standing, attestation, separation-of-duties, defect) and their relations. Ontology Closure (USIS-011 obligation 11) governs. USIS-015 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Certification taxonomy (reference to USIS-005)

Every certification occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the certification taxonomy of **certification kinds**: artifact-level (a capability), integrity-domain (the 10 Digital-Twin domains), and cross-layer (spanning the certification surfaces of Part R). Taxonomy Closure (USIS-011 obligation 12) governs. USIS-015 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Certification lifecycle

A certification node follows, under UCIC-001:

```
DEFINED → PRECONDITIONED (subject is VALID per USIS-014) → GATED (CCE gate set evaluated, referenced) → ATTESTED (CERTIFIED | NOT-CERTIFIED) → REGISTERED → EVOLVING
```

Certification **discharges** the `CERTIFIED` stage of the capability lifecycle (DEFINED→GROUNDED→MODELED→REASONED→VALIDATED→**CERTIFIED**→EVOLVING; USIS-008) — it does not redefine that lifecycle (UCIC-001 / USIS-006/008 own it; referenced). Validation (`VALIDATED`, USIS-014) is a **hard precondition**: a subject that is not `VALID` cannot be `CERTIFIED` (no stage skipping; fail-closed).

## PART F — Certification model

The certification model is the deterministic gate set a validated subject must pass to be `CERTIFIED`:

| Gate class | Contract (what "certified" requires) | Discharged by (referenced) |
|------------|--------------------------------------|----------------------------|
| **Validation precondition** | subject adjudicated `VALID` (USIS-014) | USIS-014 verdict |
| **Ten integrity domains** | Identity · Registry · Traceability · Knowledge-Graph · Change · Version · Lineage · Synchronization · Twin-Intelligence · Execution all PASS | `ukbx certify` (UMB-IMP-006) |
| **Twin hard checks** | UKB-014 hard checks (C-04/05/07/08/09/10/11) PASS | `ukbx twin --check` |
| **Separation of duties** | certifier ≠ author ≠ executor of the subject | CEP-005; certification governance (Part H) |
| **Grounding / explanation** | verdict grounded in evidence + explained (LAW USIS-07) | certification record + `ukbx certify` |
| **Certification closure** | the tier chain up to Certification is present, owned, edged | USIS-011 obligations |

**Fail-closed rule.** A subject is `CERTIFIED` **iff every** gate passes. Any failed gate ⇒ `NOT-CERTIFIED`; there is no partial-certification state (mirrors USIS-004 Part D completeness law).

## PART G — Certification-execution model

Certification is executed by **referenced** certifiers bound at the node's `certifier_ref`; the architecture specifies *what* is attested, never *how* a runner works:

| Execution surface | Referenced certifier | Attestation |
|-------------------|----------------------|-------------|
| Repository / twin certification runtime | `ukbx certify` | 10 integrity domains over the real corpus |
| Twin hard checks | `ukbx twin --check` | UKB-014 hard checks 7/7 |
| Software-stream certification | `engine/universal_certification` (UCOS-EPIC-006) / `platform/certification` (EC2-EPIC-011) | referenced as-is (frozen/EC-certified) |
| Per-capability certification gate | UCIC-001 + CCE | 10 fail-closed gates + SoD |

Execution is deterministic and idempotent (re-running on unchanged inputs yields the identical verdict + append-only audit); the architecture adds no certifier of its own.

## PART H — Certification governance

Certification is **governed** and separated: the certifier is **not** the author or executor of the subject it certifies (separation of duties, CEP-005). A verdict of `NOT-CERTIFIED` is fail-closed — it **blocks** promotion of the subject (to Evidence/frozen standing) until the defect is remediated append-only and re-certified. No certification is inferred from mere existence or from validation alone (STATUS-001 non-projection); certified standing is conferred only by a certifier run recorded in the append-only certification audit (`.runtime/governance/certification-audit.json`).

## PART I — Certification orchestration

The Certification tier **orchestrates the gate ordering**: validation-precondition before integrity-domain gates before cross-layer certification, so a failed precondition short-circuits fail-closed before deeper gates run. Orchestration of *validation obligations* is USIS-014's concern; the Certification tier orchestrates *gate evaluation order and SoD*, not validation — no overlap (Zero-Overlap, USIS-011 obligation 3).

## PART J — Digital Twin certification

Digital-Twin certification is the tier's canonical execution surface: `ukbx certify` (the Digital-Twin Certification Runtime, UMB-IMP-006 / UMB-017) attests the **10 integrity domains** over the real Digital Twin, and `ukbx twin --check` attests the **UKB-014 hard checks (7/7)**. A subject is Digital-Twin-certified iff both pass with append-only evidence in `00-BOOK/DATA/certification.json`. USIS-015 owns the *Digital-Twin-certification contract*; the twin and its runtime are owned by UMB-002 / UMB-IMP-006 — referenced, never duplicated (LAW USIS-02).

## PART K — Runtime certification

Runtime certification (the surface named by USIS-013 Part N) attests, by reference: **bounded autonomy** (no unbounded self-modification), **reversibility-or-justification** of self-* effects, **canonical ownership**, and that every self-* pathway is gated. An ungated self-* pathway ⇒ `NOT-CERTIFIED` (fail-closed). USIS-015 owns the *runtime-certification contract*; USIS-013 owns the runtime; the platform runtime executes — referenced.

## PART L — Registry certification

Registry certification attests that all registers (REG-AUTO-001 §2) are synchronized and append-only: **count parity**, **no duplicate ID/page**, **referential integrity**, and **no parallel registry** (LAW USIS-02). Discharged by `ukbx certify` domain 2 (Registry) + `ukb validate`. USIS-015 owns the *registry-certification contract*; the registers are owned by the universal mechanism — referenced.

## PART M — Knowledge certification

Knowledge certification attests **Knowledge-Once**: no duplicated constitutional knowledge; every knowledge node singly-owned and homed (No-Orphan); every reference resolves; the knowledge graph navigable with no orphan. Discharged by `ukbx certify` domain 4 (Knowledge Graph) + C-08 navigation. USIS-015 owns the *knowledge-certification contract*; the knowledge graph is owned by UMB-006 — referenced.

## PART N — Cross-layer certification

Cross-layer certification attests integrity of references **across** the surfaces the mission enumerates — architecture (USIS-006…013/017), implementation (USIS-INT-001), runtime (USIS-013), registry (REG-AUTO-001), knowledge (UMB-006), governance (UCIC-001 / GOV instruments), validation (USIS-014), evidence (USIS-016 / TRACK-001), Digital Twin (UMB-002), and **future UCOS universes** (USIS-002 reserved slots `USIS-U-FUT`/`USIS-U-UNK`). A subject is cross-layer-certified iff every cross-layer reference resolves, the composite dependency graph remains acyclic, and no surface contradicts another. Discharged by `ukbx certify` (10 domains, whole-corpus) + `ukb validate` (referential integrity + acyclicity).

## PART O — Certification authority

Certification confers **certified standing** — a derived, evidence-backed attestation that a subject has passed its gate set — and **nothing more**. It is **AUTHORITY = NONE (DERIVED)**: it creates no new governance authority, ratifies no constitution, and authorizes no EC-series step or code. Absolute FINALIZED standing remains subject to the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). Certified standing is append-only and revocable-by-re-certification only (a later defect drives `NOT-CERTIFIED` on re-run; prior audit entries are never mutated).

## PART P — Dependency model & Certification independence

- **Dependency model.** `Depends-On` runs downward to USIS-014 (Validation, the parent tier) and the full Wave-2 spine (USIS-INT-001/017/013/012/011/010/009/008/006/007/004) and references `engine/universal_certification`, `platform/certification`, `ukbx`; `Parent` is the program root (non-chained). No forward reference (USIS-011 obligation 14). Acyclic, downward-only (obligation 5). USIS-016 (Evidence, tier 22) `Depends-On` this tier — Certification founds Evidence.
- **Certification independence.** The Certification tier is architecture: it defines certification *gates, verdicts, authority, and governance*, not a concrete CI/attestation technology. Execution occurs in the referenced certifiers, never embedded. The certification architecture is fully defined independent of technology, implementation, infrastructure, platform, or vendor (LAW USIS-04).

## PART Q — Certification coverage model

Certification **coverage** is the completeness measure of the certification tier, and is the basis for the programme's Coverage Closure Certificate:

| Coverage dimension | Definition (100% ⇔) |
|--------------------|----------------------|
| Gate coverage | every gate class (Part F) evaluated for the subject |
| Integrity-domain coverage | all 10 `ukbx certify` domains attested |
| Surface coverage | all cross-layer surfaces (Part N) certified |
| Whole-corpus coverage | every registered artifact in certification scope (not only the new one) |
| Grounding coverage | every verdict grounded (LAW USIS-07) |
| Explanation coverage | every verdict explained (LAW USIS-07) |
| Evidence coverage | every verdict carries an evidence reference (Part R evidence model) |

Coverage is machine-derived from the certifier's outputs; a coverage gap is itself a defect (fail-closed). **Zero missing scope** ⇔ all dimensions = 100%.

## PART R — Certification evidence model & traceability

- **Evidence model.** Discharged by USIS-016 (Evidence tier, referenced) using UCIC-001 Output-5 + the certifier's own outputs: each certification records the **subject reference, validation precondition, gate set evaluated, certifier run + result, grounding trace, explanation, and verdict**, written to `00-BOOK/DATA/certification.json` + `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md` and the append-only audit `.runtime/governance/certification-audit.json`. Absence ⇒ NOT-DONE (TRACK-001) ⇒ `NOT-CERTIFIED`.
- **Traceability.** Every certification node is traceable end-to-end (GOV-002): `Certifies`/`Depends-On` up to each subject and the USIS-014 validation verdict; `Evidenced-By` down to its evidence bundle; materialized into `relationships.json` + the Knowledge-Graph Registry by the reused mechanism.

## PART S — Reuse model

Reuse-First (LAW USIS-02): CEP-005 (certification law), `ukbx certify` / `ukbx twin --check` (Digital-Twin certifier), `engine/universal_certification` (UCOS-EPIC-006) and `platform/certification` (EC2-EPIC-011) (Software-stream certifiers), UCIC-001 + CCE (10 gates + SoD), USIS-014 (validation precondition), GOV-002 (traceability), and TRACK-001 (evidence) are **referenced**, never re-homed or re-implemented. USIS-015 adds only the science-intelligence **certification-tier specialization** (the gate set, verdict semantics, authority, coverage/cross-layer contracts). It creates no second certifier, no competing certification registry, and no parallel attestation pipeline.

## PART T — Certification (constitutional) invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations).**
1. Duplicate certifier / competing certification registry created by USIS-015: **0** (LAW USIS-02).
2. Hard-coded present-day technology/CI/vendor in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) certification layers: **0** (LAW USIS-05, obligation 4).
4. Partial-certification state (a subject neither CERTIFIED nor NOT-CERTIFIED): **0** (Part F fail-closed).
5. Certification without a VALID precondition (validation skipped): **0** (Part E).
6. Certifier = author/executor (SoD violation): **0** (Part H; CEP-005).
7. USIS-015 edits to any frozen instrument or Software-stream certifier: **0** (obligation 19; `engine/**`,`platform/**` untouched — referenced).
8. Circular ownership / dependency cycles: **0** (obligation 5; Depends-On downward-only).
9. Duplication of any certified surface or of any executable certifier: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- A failed gate ⇒ `NOT-CERTIFIED` ⇒ subject promotion blocked (fail-closed) until append-only remediation + re-certification.
- A missing validation precondition ⇒ blocked before gating (Part E).
- An SoD violation ⇒ non-certifiable (Part H).
- A duplicated certifier/registry ⇒ Zero-Duplication violation ⇒ reference the canonical certifier.
- Absence of required evidence ⇒ NOT-DONE (TRACK-001) ⇒ `NOT-CERTIFIED`. Authoritative history, frozen artifacts, and prior certification-audit entries are never mutated on remediation; correction is forward-only and append-only.

## PART U — Non-goals

- Authors **no** certification record, gate implementation, CI pipeline, attestation, or capability instance (Wave-3/5, per-member); those are produced by the referenced certifiers.
- Is **not** `ukbx certify`, `engine/universal_certification`, `platform/certification`, or the Digital-Twin Certification Runtime — all referenced.
- Defines **no** validation verdict or evidence store (owned by USIS-014 / USIS-016); does **not** re-certify by its own logic — it specifies the contract the referenced certifier fulfils.
- Confers **no** new governance authority and **no** FINALIZED standing (Part O); names **no** technology/CI/vendor (LAW USIS-04); creates **no** competing certifier or certification registry (LAW USIS-02); produces **no** code; admits **no** partial or ungrounded certification (LAW USIS-07; Part F).

---

*END — USIS-015 · CERTIFICATION ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
