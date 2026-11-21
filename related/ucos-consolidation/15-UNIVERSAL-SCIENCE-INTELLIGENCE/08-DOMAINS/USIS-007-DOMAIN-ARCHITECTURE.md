# USIS-007 — Domain Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-007 (Domain Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000007` (next free after `UCOS-USIS-000006` = USIS-005). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Domain Architecture (EVO-USIS-007) — establish the constitutional Domain/Sub-Domain architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Domain/Sub-Domain tier owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Domain tier — spans the 21 universes (USIS-002); hosts discipline domains of `USIS-U-SCI` (USIS-003) and cross-universe domains incl. the Human-Intelligence families, by reference |
| DEPENDS-ON | USIS-002 · USIS-003 · USIS-004 · USIS-005 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tiers **3 (Domain)** and **4 (Sub-Domain)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 19 (Knowledge) · Part 20 (Intelligence/Analytics) · Part 21 (Learning); discharges the **ownership-closure** and (by reference to USIS-005) **taxonomy/ontology-closure** obligations at the Domain-tier level |
| GOVERNED BY | USIS-001 (LAW USIS-01/02/05/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the domain-ownership mandate conferred by USIS-001 (LAW USIS-01/05/09), the universes established in USIS-002, the science registry in USIS-003, and the USIS-004 meta-model tiers 3/4 (LAW USIS-08). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-007-DOMAIN-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 1 · AUTHORIZED). No new constitutional knowledge is introduced; the Domain-tier architecture is carried verbatim in substance. Corrections vs the blueprint: (a) STATUS raised from "AUTHORED · AWAITING UCIC AUTHORISATION" to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), consistent with the Wave-1 registered artifacts, with dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. Where a domain cross-links an existing canonical universe/science/concern, the canonical home governs and this architecture holds only a **reference** (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Domain / Sub-Domain tier** of the Universal Science & Intelligence Substrate — the contextual home that groups capabilities under a discipline of a science universe, including the cross-universe domains and the Human-Intelligence families. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/08-DOMAINS/` home and defines how any present or future domain acquires a canonical home, ownership, hierarchy, composition, and registry membership **by registration, never by redesign** (LAW USIS-01/09). **This instrument establishes only the Domain-tier architecture.** It authors **no** individual domain, sub-domain, Human-Intelligence family, or capability instance — those are separately-authorized later (Wave-3) missions.

---

## PART A — Constitutional basis and scope

This architecture is the registered instantiation of the domain-ownership mandate of USIS-001 and the Domain/Sub-Domain tiers of the USIS-004 meta-model:

- **USIS-001 LAW USIS-01** admits *all* fields of science and intelligence as first-class, observer-relative domains under USIS.
- **USIS-004 Part C tiers 3/4** — Domain (parent = Discipline, closure = ownership closure) and Sub-Domain (parent = Domain, closure = taxonomy closure). USIS-007 is the constitutional architecture and rule-set for these two tiers.
- **USIS-002** established the 21 universes and **USIS-003** the 30-seed science registry (`USIS-U-SCI`); USIS-007 provides the **grouping layer** under which capabilities are declared, without re-homing either (LAW USIS-02).
- **USIS-005** supplies the ontology/taxonomy meaning foundation; every domain is *placed* into that foundation by reference (Ontology/Taxonomy Closure govern; USIS-007 does not duplicate them).
- **USIS-001 LAW USIS-05 (No-Orphan)** — every domain has exactly one canonical owner and one home. **LAW USIS-09 (recursive extensibility)** — a domain may host sub-domains to unbounded depth; growth is append-only.

**Scope of this instrument (Wave 2 · EVO-USIS-007).** This architecture:
- creates the `15-…/08-DOMAINS/` home and this single registered architecture artifact;
- defines the Domain/Sub-Domain **node shape, boundaries, ownership, hierarchy, composition, and registry model** (Parts B–G);
- defines the Domain **relationship model** to capabilities, universes, and sciences (Part H) and its **dependency + runtime-independence** posture (Part I);
- founds downward-only on `USIS-002`, `USIS-003`, `USIS-004`, `USIS-005` (Depends-On; parents to the USIS program root `USIS-GOV-000`), introducing no upstream change and no cycle;
- authors **no** individual domain, sub-domain, Human-Intelligence family, capability, algorithm, or model instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the existing registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), the universal registries, the canonical U24/Part-19 knowledge ontology, UCIC-001, and the governance instruments as the sole authorities — and performs **no** `config.py` edit (`^15-…/08-DOMAINS/` already classifies to USIS/VOL-024).

## PART B — Domain architecture (the Domain/Sub-Domain node)

A domain is a typed node of the canonical form:

```
{ id: USIS-DOM-<NAME>, home: 08-DOMAINS/<NAME>/, discipline: USIS-SCI-<...> (parent),
  universe: <USIS-U-*> (+ cross-links), owner, status, sub-domains[], capabilities[] }
```

- The domain sits at meta-model tier 3; a sub-domain (tier 4) has the same shape with `parent = <domain>` and is self-similar (LAW USIS-09).
- The node is **specification only** — it enumerates no algorithm/model and produces no code (technology- and implementation-independent; LAW USIS-04, Part I).
- Every domain conforms end-to-end to the USIS-004 meta-model when realized (LAW USIS-08): its downward Capability → … → Lifecycle chain is authored per-domain in later waves; USIS-007 records the Domain/Sub-Domain tier only.

## PART C — Domain boundaries (Zero-Overlap)

- A domain **owns**: the contextual grouping of a discipline's capabilities, its placement in the ontology/taxonomy (by reference), and its own sub-domain branching.
- A domain **does not own**: the science/discipline set (USIS-003), the universe set (USIS-002), the taxonomy/ontology structures (USIS-005), the capabilities themselves (Capability tier, USIS-006, when realized), or any lower realization tier (Model/Algorithm/…).
- No two domains claim the same concern; interdisciplinary domains register as **new** nodes with cross-links (e.g. a cognitive-neuroscience domain = Neuroscience × Cognitive-Science), never duplicates (Zero-Overlap; USIS-011 obligation 3).

## PART D — Domain ownership (No-Orphan; ownership closure)

- **Single canonical owner (LAW USIS-05).** Each domain owns exactly one field-context and one canonical home under `08-DOMAINS/`. Ownership closure (USIS-004 tier-3 contract): a domain with no owner or no home is **NOT integrated** (fail-closed).
- Every domain declares `Parent` (its Discipline) and `Depends-On` edges downward to already-registered nodes; the graph is acyclic and rooted at `USIS-GOV-000` (CIOA-enforced).
- Cross-universe domains (incl. the Human-Intelligence families) **reference** their source universe and are never re-homed there (LAW USIS-02).

## PART E — Domain hierarchy (recursive)

The hierarchy is a strict downward layering mirroring the meta-model:

```
Universe (USIS-002)  →  Science/Discipline (USIS-003)  →  Domain (tier 3)  →  Sub-Domain (tier 4)  →  Capability (tier 5, USIS-006)
```

- A Domain's `Parent` is a Discipline of `USIS-U-SCI` (or a cross-universe discipline); a Sub-Domain's `Parent` is a Domain.
- Recursion is unbounded (LAW USIS-09): any domain/sub-domain may host a full child chain; there is no maximum depth or breadth. New levels register append-only; no existing node is rewritten or renumbered (CR-INF-007).

## PART F — Domain composition

- A domain **composes** its member sub-domains and capabilities by **reference edges** (role membership), never by embedding their content.
- Composition is expressed as parent→child edges into the Capability/Taxonomy registries; the members remain canonically owned by their own tiers.
- A domain admits a new sub-domain or capability by appending a membership edge — no domain is redefined to admit one (LAW USIS-03).

## PART G — Registry integration

- Every domain is a row in the **Domain Registry** under `15-…/04-REGISTRIES/`, and resolves in the **Capability Registry** (Registry Manifest target #1), **Taxonomy Registry** (#3), **Architecture Registry** (#10), and **Dependency Registry** (#9).
- The machine-readable registry projection is produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); USIS-007 stands up **no** parallel allocator, ontology, taxonomy, or competing registry (LAW USIS-02).
- All writes are append-only, deterministic (idempotent regeneration), and metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`). Adding a future domain appends a row + one homed artifact and rewrites nothing (USIS-011 obligations 7/20).

## PART H — Relationship model (Capability / Universe / Science)

| Relationship | Edge | Direction | Rule |
|--------------|------|-----------|------|
| Domain → Capability | Child / composition | downward | a domain hosts capabilities (USIS-006); the capability's `Parent` is its domain/sub-domain (meta-model tier 5) |
| Domain → Science/Discipline | Parent | upward-to-established | a domain's `Parent` is a Discipline of `USIS-U-SCI` (USIS-003), referenced not re-homed |
| Domain → Universe | Reference (membership) | cross | a domain declares its universe membership (USIS-002); cross-universe domains carry multiple reference edges |
| Domain → Ontology/Taxonomy | Reference (placement) | cross | a domain is placed in USIS-005 `02-ONTOLOGY/`/`03-TAXONOMY/` by reference; Ontology/Taxonomy Closure govern |

No relationship re-homes its target; all are `Depends-On`/reference edges to already-established nodes (LAW USIS-02/05).

## PART I — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-002/003/004/005`; `Parent` is the program root (non-chained). No forward reference (a domain may only depend on an already-registered node; UCIC-001 Stage 2; USIS-011 obligation 14). Acyclic and downward-only (obligation 5).
- **Runtime independence.** The Domain tier is pure specification: it binds to **no** runtime, engine, service, or execution mode. Runtime concerns are owned by the Runtime tier (USIS-013) and the platform runtime (`08-RUNTIME`/RIE), referenced never embedded. A domain is fully defined without any runtime being present.

## PART J — Validation / Certification / Evidence models

- **Validation (→ USIS-014).** A domain is valid only with **ownership closure** (single owner/home), **taxonomy closure** (every taxon has a parent to a root; USIS-011 obligation 12), and **ontology closure** (every concept defined + placed; obligation 11) — the latter two discharged by reference to USIS-005. Grounding evidence links the domain to its discipline and universe.
- **Certification (→ USIS-015).** Domain certification confirms ownership closure and No-Orphan (obligation 4) — a structural certification discharged at registration under the reused CCE runtime, certifier ≠ executor (SoD).
- **Evidence (→ USIS-016).** Placement evidence (ontology/taxonomy edges), ownership record, and dependency-satisfaction note are emitted to the evidence store; absence ⇒ NOT integrated (C-00.3; TRACK-001, fail-closed).

## PART K — Reuse model

Reuse-First (LAW USIS-02): before creating a domain, the owner searches the Domain Registry and the Domain & Human-Intelligence Catalog for a canonical instance and reuses it. Data/Security/Runtime/Simulation concerns are **referenced** to their owning programs (`10-DATA`, `14-SECURITY`, `08-RUNTIME`/RIE, Universe U26) — never forked into a USIS domain. USIS-007 specializes the universal grouping model for science-intelligence; it does not fork it.

## PART L — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011).**
1. Duplicate domain catalog/registry created by USIS-007: **0** (LAW USIS-02).
2. Hard-coded present-day technology in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed/unparented) domain layers: **0** (LAW USIS-05, obligation 4).
4. Closed (finite-by-construction) domain registry: **0** (obligation 21; the registry is open).
5. USIS-007 edits to any frozen instrument: **0** (obligation 19).
6. Domain lacking Parent discipline + placement + ownership: **0** (C-00.3).
7. Circular ownership / dependency cycles: **0** (obligation 5).

**Failure model (per UCIC-001 Output-4).**
- A domain without a Parent Discipline ⇒ not eligible (return to selection; recoverable).
- A domain claiming a concern already owned ⇒ Zero-Overlap violation ⇒ rejected (reuse the canonical node).
- An orphan (unhomed/unparented) domain ⇒ No-Orphan gate fail ⇒ non-registerable.
- Absence of a required placement/ownership/evidence artifact ⇒ NOT-DONE (TRACK-001); the dependent gate cannot pass. Authoritative history and frozen artifacts are never mutated on rollback.

## PART M — Non-goals

- Authors **no** individual domain, sub-domain, or Human-Intelligence family instance (Wave-3, per-member).
- Is **not** the science/discipline catalog (USIS-003), the universe catalog (USIS-002), or the ontology/taxonomy foundation (USIS-005).
- Defines **no** capability, algorithm, model, engine, runtime, service, or API/SDK (owned by USIS-006/008/009/011/013/012/017).
- Names **no** technology or infrastructure (LAW USIS-04); creates **no** competing taxonomy or registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-007 · DOMAIN ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
