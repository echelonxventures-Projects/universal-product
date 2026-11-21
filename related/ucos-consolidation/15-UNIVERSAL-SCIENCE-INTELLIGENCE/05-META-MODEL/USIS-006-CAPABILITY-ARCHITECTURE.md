# USIS-006 — Capability Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-006 (Capability Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000008` (next free after `UCOS-USIS-000007` = USIS-007). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Capability Architecture (EVO-USIS-006) — establish the constitutional Capability-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Capability tier (the unit of realization) owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, USIS-007, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Capability tier — the meta-model pivot (USIS-004 tier 5) hosted under domains (USIS-007) across the 21 universes (USIS-002) |
| DEPENDS-ON | USIS-007 · USIS-004 · USIS-005 · USIS-002 · USIS-003 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **5 (Capability)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 19 (Knowledge) · Part 20 (Intelligence/Analytics) · Part 21 (Learning); instantiates UCIC-001 Output-2 (per-capability execution contract) and Output-6 (Universal Completion Definition) as the meta-model Capability tier |
| GOVERNED BY | USIS-001 (LAW USIS-00 C-00.3 / USIS-02/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the capability-realization mandate conferred by USIS-001 (LAW USIS-08 meta-model conformance) and the USIS-004 Capability tier, hosted by the Domain tier (USIS-007). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-006-CAPABILITY-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 2 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised from "AUTHORED · AWAITING UCIC AUTHORISATION" to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`); (d) **canonical home resolved to `05-META-MODEL/`** — the Capability tier's definitional home co-located with USIS-004 (LAW USIS-08). This supersedes the EVO-USIS-006 mission-brief "08-CAPABILITIES" shorthand: Repository Truth (USIS-005 §2 21-area tree) defines no `08-CAPABILITIES` area (area 08 = `08-DOMAINS`, owned by USIS-007) and co-homes CAPABILITIES at `05-META-MODEL`+`08-DOMAINS`. Per the conflict rule, the ratified structure specification governs; no new area is invented (EXTENDING; nothing renumbered). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where a capability cross-links an existing canonical concern, the canonical home governs and this architecture holds only a **reference** (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Capability tier** — the single unit of realization in USIS, the meta-model pivot at which a science/intelligence concern becomes a governed, testable, evidenced, certified deliverable. This instrument defines how any present or future capability is declared, owned, placed (ontology/taxonomy), decomposed, composed, registered, and driven through the meta-model chain — uniformly, deterministically, and machine-checkably — so **no capability can exist partially** (LAW USIS-08). **This instrument establishes only the Capability-tier architecture.** It authors **no** individual capability instance — those are separately-authorized later (Wave-3) per-member realizations under UCIC-001.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the capability-realization mandate of USIS-001 and the Capability tier (5) of the USIS-004 meta-model:

- **USIS-004 Part C tier 5** — Capability (parent = Sub-Domain/Domain; closure = capability closure). USIS-006 is the constitutional architecture and rule-set for this tier.
- **USIS-004 §3 Conformance rule** — a capability is *realized* only if every tier Science → Lifecycle is present, owned, edged, and evidenced; a missing tier ⇒ NOT realized (partial realization is not a valid state).
- **USIS-001 LAW USIS-00 C-00.3** — every integrated entity carries the seven integration facets (ontology + taxonomy + registry + governance + validation + certification + traceability); absence of any ⇒ NOT integrated (fail-closed).
- **UCIC-001 Output-2/6** — the per-capability execution contract and Universal Completion Definition; USIS-006 is the meta-model expression of these for the science-intelligence stream.
- **USIS-007 (Domain)** — provides the host context; the Capability tier `Depends-On` the Domain tier and **references** it, never duplicating Domain Architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-006).** This architecture:
- creates the canonical Capability-tier architecture artifact under `15-…/05-META-MODEL/` (the Capability tier's definitional home; capability *instances* are later homed under `08-DOMAINS/` per USIS-005 §2);
- defines the Capability **node shape, ontology/taxonomy placement, ownership, hierarchy, lifecycle, composition, and registration** (Parts B–I);
- defines the Capability **relationships** to domains, universes, and sciences (Part J) and its **dependency + runtime-independence** posture (Part K);
- founds downward-only on `USIS-007/004/005/002/003` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** capability, algorithm, model, or lower-tier instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, UCIC-001, USIS-005 ontology/taxonomy, and the governance instruments as the sole authorities — and performs **no** `config.py` edit (`^15-…/` already classifies to USIS/VOL-024).

## PART B — Capability architecture (the Capability node)

A capability is a typed node of the canonical form:

```
{ id: USIS-CAP-<NAME>, home: 08-DOMAINS/<DOMAIN>/<CAP>/ (instance), tier: 5,
  parent: <domain|sub-domain> (USIS-007), objective, dependencies[], governing_determination,
  constitutional_anchor, additive_surfaces[], acceptance_criteria, evidence, validation,
  certification, required_repo_updates, completion_definition, chain{ theory..lifecycle } }
```

- The node is the meta-model pivot: it specializes UCIC-001 Output-2 (the execution contract) for the science-intelligence stream (LAW USIS-08).
- It is **specification only** — it produces no code and names no technology (LAW USIS-04; implementation/runtime independence, Parts K/N). The Implementation tier (Software/Infrastructure stream) is referenced, not embedded.
- Each capability owns its downward chain (Theory → Ontology → Taxonomy → Registry → Knowledge-Object → Model → Algorithm → Pattern → Engine → Runtime → Service → API → SDK → Implementation → Validation → Certification → Evidence) at its own later realization; USIS-006 records the Capability tier only.

## PART C — Capability ontology (reference to USIS-005)

Every capability is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares the concepts it realizes and their relations. Ontology Closure (USIS-011 obligation 11) governs — every concept a capability names is defined and placed. USIS-006 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Capability taxonomy (reference to USIS-005)

Every capability occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) under its domain/sub-domain. Taxonomy Closure (obligation 12) governs — every capability taxon has a parent to a root. USIS-006 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Capability ownership (No-Orphan; capability closure)

- **Single canonical owner (LAW USIS-05).** Each capability has exactly one owning family and one canonical home (instance home under `08-DOMAINS/<domain>/`). Capability closure (USIS-004 §3): a capability missing any chain tier, owner, or home is **NOT realized** (fail-closed).
- Every capability declares `Parent` (its domain/sub-domain, USIS-007) and `Depends-On` edges downward to already-registered nodes; acyclic, rooted at `USIS-GOV-000`.
- No two capabilities own the same concern (Zero-Overlap, obligation 3).

## PART F — Capability hierarchy

```
Domain / Sub-Domain (USIS-007)  →  Capability (tier 5)  →  Sub-Capability (recursive)  →  realization chain (tiers 6–24)
```

- A capability's `Parent` is a Domain or Sub-Domain; a capability may decompose into sub-capabilities recursively (LAW USIS-09) without redesign — decomposition is append-only.
- There is no maximum breadth or depth; new sub-capabilities register append-only (CR-INF-007).

## PART G — Capability lifecycle

A capability advances through the SCIENCE_INTELLIGENCE lifecycle (Execution-Stream deliverable) mapped onto UCIC-001:

```
DEFINED → GROUNDED → MODELED → REASONED → VALIDATED → CERTIFIED → EVOLVING
```

executed under the UCIC-001 15 stages and 6 gates (READY_TO_IMPLEMENT → IMPLEMENTED → VALIDATED → CERTIFIED → READY_TO_COMMIT → READY_FOR_PRODUCTION). No stage is skipped; the sole backward transition is a defect-driven REOPEN (evidence preserved). USIS-006 references the lifecycle; it does not re-define UCIC-001.

## PART H — Capability composition

- A capability **composes** its downward realization tiers (Model/Algorithm/Pattern/…) by **reference edges**, never by embedding their content; members remain canonically owned by their own tiers (USIS-008/009/010/…).
- A capability composes sub-capabilities by parent→child membership edges.
- Composition admits a new member by appending an edge — no capability is redefined to admit one (LAW USIS-03).

## PART I — Capability registration

- Every capability is a row in the **Capability Registry** (Registry Manifest target #1) under `15-…/04-REGISTRIES/`, and resolves in the Architecture (#10), Knowledge (#4), Dependency (#9), Validation (#6), Certification (#7), Evidence (#8), and Implementation (#12) registries across its lifecycle.
- The machine-readable registry projection is produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); USIS-006 stands up **no** parallel allocator or competing registry (LAW USIS-02).
- All writes are append-only, deterministic (idempotent), metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`); the registry is open (no ceiling; obligation 21). Adding a future capability appends a row + homed artifact and rewrites nothing (obligations 7/20).

## PART J — Relationship model (Domain / Universe / Science)

| Relationship | Edge | Direction | Rule |
|--------------|------|-----------|------|
| Capability → Domain/Sub-Domain | Parent | upward-to-established | the capability's `Parent` is a domain/sub-domain (USIS-007), **referenced not duplicated** |
| Capability → Universe | Reference (membership) | cross | inherits its domain's universe membership (USIS-002); cross-universe capabilities carry multiple reference edges |
| Capability → Science/Discipline | Reference (lineage) | cross | traces to the discipline of `USIS-U-SCI` (USIS-003) via its domain |
| Capability → realization tiers | Child / composition | downward | Model/Algorithm/Pattern/Engine/Runtime/Service/API-SDK/Validation/Certification/Evidence (USIS-008…017) |

No relationship re-homes its target; all are `Depends-On`/reference edges to established nodes (LAW USIS-02/05). **Domain Architecture (USIS-007) is referenced as the host context and is not duplicated.**

## PART K — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-007/004/005/002/003`; `Parent` is the program root (non-chained). No forward reference (a capability may only depend on an already-registered node; UCIC-001 Stage 2; obligation 14). Acyclic, downward-only (obligation 5).
- **Runtime independence.** The Capability tier is pure specification; it binds to **no** runtime, engine, or service. Runtime concerns are owned by USIS-013 and the platform runtime (`08-RUNTIME`/RIE), referenced never embedded. A capability is fully declared without any runtime present.

## PART L — Validation model

Discharged by USIS-014 (referenced): a capability is VALIDATED only with grounding + explanation-coverage evidence (LAW USIS-07) and UCIC-001 Stages 5–9 PASS. Capability-specific acceptance criteria are declared in the Output-2 contract and are objective and checkable. Ontology/Taxonomy closure (obligations 11/12) and capability closure (obligation 13) are validation preconditions.

## PART M — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS with certifier ≠ executor (SoD). Certification confirms the capability satisfies the seven integration facets (C-00.3) and its declared Universal Completion Definition (UCIC-001 Output-6). Certification Closure (obligation 17) applies.

## PART N — Evidence model

Discharged by USIS-016 (referenced) using UCIC-001 Output-5: dependency-verification, declaration/source diff, static/dynamic/test/coverage reports, validation/certification records, and traceability edges (Vision→Certification). Absence of any required evidence ⇒ capability NOT-DONE (TRACK-001, fail-closed).

## PART O — Reuse model

Reuse-First (LAW USIS-02): before declaring a capability the owner searches the Capability Registry for a canonical instance and reuses it; a new capability is admissible only if none exists. Human-Intelligence and cross-universe concerns reuse existing domain (USIS-007) and science (USIS-003) nodes rather than forking them (Knowledge-Once, C-00.2). Data/Security/Runtime/Simulation are referenced to their owning programs, never re-homed.

## PART P — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011).**
1. Duplicate capability catalog/registry created by USIS-006: **0** (LAW USIS-02).
2. Hard-coded present-day technology in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed/unparented) capability layers: **0** (LAW USIS-05, obligation 4).
4. Closed (finite-by-construction) capability registry: **0** (obligation 21; the registry is open).
5. USIS-006 edits to any frozen instrument: **0** (obligation 19).
6. Capability lacking the seven integration facets or a complete meta-model chain: **0** (C-00.3; obligation 13).
7. Circular ownership / dependency cycles: **0** (obligation 5).
8. Duplication of Domain Architecture (USIS-007): **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- Missing governing determination/anchor or SoD violation ⇒ non-recoverable for the attempt (escalate; Stage 3).
- Multi-capability scope in one realization ⇒ non-recoverable ⇒ rollback (Stage 4).
- Failed certification ⇒ REOPEN to ACTIVE with evidence preserved (Stage 10).
- A capability lacking any of the seven integration facets or any chain tier ⇒ fail-closed NOT realized (C-00.3; USIS-004 §3). Authoritative history and frozen artifacts are never mutated on rollback.

## PART Q — Non-goals

- Authors **no** individual capability, sub-capability, algorithm, or model instance (Wave-3, per-member, under UCIC-001).
- Is **not** the meta-model definition (USIS-004), the lifecycle engine (UCIC-001), the Domain Architecture (USIS-007), or the ontology/taxonomy foundation (USIS-005) — all referenced.
- Defines **no** model, algorithm, pattern, engine, runtime, service, or API/SDK (owned by USIS-008/009/010/011/012/013/017).
- Names **no** technology or infrastructure (LAW USIS-04); creates **no** competing capability registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-006 · CAPABILITY ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
