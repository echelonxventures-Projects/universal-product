# UCOS Ω∞ — UNIVERSAL SECURITY TAXONOMY

> **STATUS DOMAIN:** ROADMAP EXECUTION (FOUNDATION)
> **STATUS BASIS:** SECURITY-003 (Universal Security Ontology — RATIFIED; `ONT-E-01…32`, `ONT-INV-1…16`) + SECURITY-002 (Universal Security Theory — RATIFIED) + SECURITY-001 (Universal Security Constitution — RATIFIED; USL-001…015) + SECURITY-GOV-000 (PHASE-008 ESTABLISHED · ACTIVE) + EC3 Band-13 CLOSED (Infrastructure Baseline frozen `2dee20b`) + AUTH-INF-001 + STATUS-001 + REG-AUTO-001 + UCI-001
> **DOCUMENT PROVENANCE:** Assembled incrementally (append-only) under the UCOS Large Artifact Protocol in validated passes, resilient to session interruption, then sealed as this single canonical artifact — substantive content preserved verbatim (USL-015). See §27 Implementation Notes. The authoritative status is §26 Final Determination.

| Field | Value |
|-------|-------|
| ARTIFACT ID | SECURITY-004 |
| ARTIFACT | Universal Security Taxonomy |
| PROGRAM | SECURITY |
| CATEGORY | SEC |
| VOLUME | VOL-023 |
| FAMILY | SECURITY-FOUNDATION |
| PACKAGE | Security Foundation Package |
| CLASSIFICATION | Foundational Security Artifact — Implementation-Independent Taxonomy (closes partition/coverage/family/archetype over the Ontology's semantic universe; no implementation, no technology, no runtime, no enforcement) |
| STATUS | RATIFIED · ACTIVE |
| PROGRAM POSITION | Fourth security roadmap artifact (SECURITY-004, SL-3); continues the SECURITY foundation chain 001…005 |
| PREDECESSOR | SECURITY-003 (Universal Security Ontology) |
| DEPENDS ON | SECURITY-003; SECURITY-002; SECURITY-001; SECURITY-GOV-000; Infrastructure Baseline (INFRASTRUCTURE-001…018; EC3-B13-U01…U10) frozen; ENG-000; ENG-001…005 (EL-1); RUNTIME-GOV-003 (RL-F2); PLATFORM-017 (PL-F2, incl. platform/security); DATA-017 (DF-2); SERVICE-017 (SF-2); APPLICATION-018 (AF-3, incl. APPLICATION-013 Security); STATUS-001; AUTH-INF-001; REG-AUTO-001; UCI-001 |
| SECURITY LAYER | SL-3 (Security Taxonomy) |
| AUTHORIZATION BASIS | SECURITY-GOV-000 (OUTPUT 13 roadmap authorization) + SECURITY-001 §20 (evolution) + SECURITY-003 §57/§59 (names SECURITY-004 as next authorized artifact) |
| CONSTITUENT AUTHORITY | NONE |
| GOVERNANCE AUTHORITY | NONE |
| RATIFICATION AUTHORITY | NONE |
| EC-1 AUTHORITY | NONE |
| BRANCH | governance-reconciliation |
| IMPLEMENTATION ANCHOR | `081ecb0` (SECURITY-003 committed; Infrastructure Baseline frozen) |
| BASELINE DATE | 2026-07-22 |

*This artifact fixes the **canonical taxonomy** of the UCOS Ω∞ Universal Security Domain: the single, exhaustive, disjoint classification scheme over the semantic universe fixed by SECURITY-003. Where SECURITY-003 (Ontology) *framed* the entity catalog (`ONT-E-01…32`), the Subject/Object partition, the seven object families, and the Principal archetypes — and explicitly deferred their **closure** to this layer — SECURITY-004 **closes** them: it proves partition exhaustiveness/disjointness (PR-1/PR-2/PR-3), object-family closure, subject-archetype closure (ST-4), control-kind closure, and constitutional coverage (CAT-1), and fixes the total, deterministic classification function by which every well-formed security construct is placed in exactly one taxonomic leaf. It contains **no implementation, no runtime, no enforcement logic, and no technology/algorithm/vendor/cloud/platform selection**. It **consumes all lower architectural layers strictly by reference** and **duplicates nothing** — it re-owns, re-implements, and redefines no lower construct, mints no new entity, primitive, authority, registry system, identifier scheme, or lifecycle (USL-015), and introduces **no new taxonomy beyond the Ontology's catalog**. Subordinate to SECURITY-003, SECURITY-002, SECURITY-001, the frozen corpus, and AUTH-INF-001; where any statement herein would conflict with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict. Every conclusion recorded here is a **technical, non-constitutive** governance record (ID-01, AUTH-06).*

---

## TABLE OF CONTENTS

1. Repository Verification
2. Purpose
3. Taxonomy Overview
4. Foundational Principles (Taxonomic) — `TXP-1…10`
5. Taxonomy Scope
6. Taxonomy Boundaries
7. Taxonomy Design Principles — `TDP-1…10`
8. The Canonical Taxonomic Ranks
9. Rank-0 / Rank-1 — Root & Partition Taxonomy + Partition Closure
10. Rank-2 (Subject Side) — Subject Family & Principal Archetype Taxonomy + Archetype Closure
11. Rank-2 (Object Side) — The Seven Object Families + Family Closure
12. Rank-3 / Rank-4 — Per-Family Leaf Taxonomy
13. Control Sub-Taxonomy + Sub-Kind Closures
14. The Complete Canonical Leaf Register — `TAX-L-01…32`
15. Coverage Closure (CAT-1) — Constitutional & Ontological Coverage Matrix
16. The Canonical Classification Function
17. Taxonomic Invariants — `TAX-INV-1…N`
18. Closure Theorems & Proofs — `TAX-CLO-1…N`
19. Taxonomy ↔ Ontology Consistency
20. Validation Mappings
21. Certification Mappings
22. Acceptance Mappings
23. Dependency Model
24. Taxonomy Evolution Rules — `TEV-1…N`
25. Readiness Assessment
26. Final Determination
27. Implementation Notes
- STATUS-001 Validation Self-Check (§5, R1–R5)

---

## SECTION 1 — REPOSITORY VERIFICATION

This taxonomy is founded on a verified, physically-present substrate. The following state was confirmed prior to authoring, and no prerequisite is assumed:

| Check | Requirement | Result |
|-------|-------------|--------|
| Branch | `governance-reconciliation` | ✅ confirmed |
| HEAD | `081ecb0` (SECURITY-003 committed) | ✅ confirmed |
| SECURITY foundation chain committed | SECURITY-GOV-000 → SECURITY-001 → SECURITY-002 → SECURITY-003 (`c1e245a` → `45856e7` → `1951c72` → `081ecb0`) | ✅ confirmed |
| SECURITY-001 (Universal Security Constitution) | RATIFIED · ACTIVE | ✅ RATIFIED |
| SECURITY-002 (Universal Security Theory) | RATIFIED · ACTIVE | ✅ RATIFIED |
| SECURITY-003 (Universal Security Ontology) | RATIFIED · ACTIVE (`ONT-E-01…32`; `ONT-INV-1…16`) | ✅ RATIFIED |
| SECURITY-003 §59 names next artifact | SECURITY-004 (Universal Security Taxonomy) | ✅ authorized |
| Infrastructure Baseline (EC3 Band-13, U01–U10; IF-3) | PROVISIONALLY RATIFIED & FROZEN (`2dee20b`) | ✅ frozen |
| SECURITY-004 pre-existing? | must not already exist (append-only, no duplication) | ✅ absent → newly authored |
| REG-AUTO-001 registration | append-only allocation `UCOS-SEC-000005` on file creation | ✅ allocated & synchronized |

**Working-tree note (provenance honesty, STATUS-001 R4).** At authoring time the working tree carried **unrelated, in-progress uncommitted work in other domains** (engine/platform/intelligence/repository-operations/cert-004 expansion). That work is **out of scope for, independent of, and non-founding for** SECURITY-004: this taxonomy founds downward-only, strictly by reference, on the **committed and frozen** substrate above (HEAD `081ecb0` and the frozen Infrastructure Baseline `2dee20b`), and consumes none of the uncommitted material. No claim in this artifact rests on any uncommitted file. Consequently the `register.sh --guard` drift gate cannot be asserted clean over the whole tree while that unrelated work is uncommitted; the SECURITY-004 registration itself (`UCOS-SEC-000005`) completed atomically and is recorded in the append-only ledger (§27).

**Verification verdict:** every prerequisite for authoring SECURITY-004 is satisfied on physical evidence (STATUS-001 R4). The predecessor chain SECURITY-GOV-000 → SECURITY-001 → SECURITY-002 → SECURITY-003 is complete and RATIFIED, and SECURITY-003 §59 names SECURITY-004 (Universal Security Taxonomy) as the next authorized artifact.

---

## SECTION 2 — PURPOSE

The Universal Security Taxonomy fixes, **once and canonically**, the **classification of the semantic universe** the Ontology defined: it takes the entity catalog (`ONT-E-01…32`), the Subject/Object partition, the seven object families, and the Principal archetypes that SECURITY-003 *framed* and expressly deferred, and it **closes** them — proving they form a single, exhaustive, disjoint, terminating classification and supplying the total decision procedure by which any well-formed security construct is placed in exactly one taxonomic leaf.

Where SECURITY-001 fixed the constitutional laws (USL-001…015), SECURITY-002 furnished the theory, and SECURITY-003 supplied the authoritative vocabulary and entity model, SECURITY-004 supplies the **authoritative classification** on which SECURITY-005 (Meta-Model) and every downstream concern architecture rely for a decidable "what kind of security thing is this?".

Its purposes are:

1. **Canonical ranks.** To fix the taxonomic ranks (Root → Partition → Family → Class → Leaf) — a strict, single-parent, acyclic classification tree rooted at `SecurityConstruct`.
2. **Closure.** To **prove** the closures the Ontology deferred: partition exhaustiveness/disjointness (PR-1/PR-2/PR-3), object-family closure (§12 of SECURITY-003), Principal-archetype closure (ST-4), and control-kind closure.
3. **Coverage.** To **prove** constitutional coverage (CAT-1): every SECURITY-001 §7 concept (25) plus the two ontological refinements (`Role`, `Vulnerability`) plus the five §8 supporting entities is classified, with no gap and no invented taxon.
4. **Classification function.** To fix the **total, deterministic** function `classify(c) → leaf` that assigns every well-formed `SecurityConstruct` to exactly one leaf, defaulting ambiguity/absence to `indeterminate → reject` (default-deny; USL-005).
5. **Consistency.** To bind the taxonomy to the Ontology (entities, invariants, relationships) and to the validation/certification/acceptance pipelines strictly **by reference**, redefining none of them.

The taxonomy remains **implementation-independent**, **technology-neutral**, and **assurance-not-enforcement** (USL-014): it *classifies* security constructs; it never executes, selects technology, or enforces. It **introduces no new entity** — every taxon is a class already named in the Ontology (USL-015).

---

## SECTION 3 — TAXONOMY OVERVIEW

The Universal Security Taxonomy is a **single, rooted, acyclic classification tree** over the Ontology's entity catalog. Its nodes are **taxa** (classes); every taxon is a class already fixed by SECURITY-003 (the abstract families and the concrete leaves) — the taxonomy **mints no new class** (USL-015). Its edges are the Ontology's inheritance relation `isA` (`⊑`, `R-01`), restricted to a **single-parent** discipline so the structure is a tree, not merely a DAG.

**Structural summary:**

- **Rank 0 — Root.** One abstract root taxon, `SecurityConstruct` (`⊑ ENG-002::Object`, by reference). Every security thing is classified beneath it (SECURITY-003 §8.1; FP-2).
- **Rank 1 — Partition.** Two abstract partition taxa — `SecuritySubject` and `SecurityObject` — that are **exhaustive** and **disjoint** over all non-abstract constructs (SECURITY-003 §8.2 PR-1/PR-2/PR-3; closed here in §9).
- **Rank 2 — Family.** On the Object side, **seven** abstract object families (`AccessObject`, `RelationObject`, `AuthorityObject`, `ProtectionObject`, `RiskObject`, `AssuranceObject`, `PropertyObject`); on the Subject side, one concrete family, `Principal` (SECURITY-003 §12/§13; closed here in §10–§11).
- **Rank 3 — Class/Leaf.** The **32 catalog entities** (`ONT-E-01…32`): one Subject leaf (`Principal`) and 31 Object leaves distributed across the seven families (assigned in §12, registered in §14).
- **Rank 4 — Sub-kind (typed refinement).** Where the Ontology fixed typed refinements that mint no new entity — the four `Principal` archetypes (§10) and the three `Control` kinds (§13) — the taxonomy records them as **sub-kinds**, not new taxa, and proves their closure.

**Relationship to the Ontology.** SECURITY-003 §8.2 stated the partition rules and repeatedly recorded "*closure proven in SECURITY-004*" (§8.2, §11 CAT-1, §12, §13 ST-4). SECURITY-004 **discharges exactly those deferred obligations** and nothing more: it adds no entity, no attribute, no relationship, and no invariant to the Ontology; it **proves properties of** the Ontology's structure and fixes the classification procedure over it.

**What the taxonomy is not.** It is not a runtime type system, a persisted schema, or a wire format; it is a **decidable classification reference** for architecture. It selects no technology and enforces nothing (USL-014). It is **non-terminal** (AUTH-INF-001): leaf numbering is sequence, not ceiling — future entities admitted by the Ontology are classified additively (§24).

---

## SECTION 4 — FOUNDATIONAL PRINCIPLES (TAXONOMIC)

The taxonomy inherits and instantiates — it does not restate or amend — the foundational principles of SECURITY-001 §5, the theoretical pillars of SECURITY-002 §2, and the ontological principles of SECURITY-003 §4 (`FP-1…10`). The following principles govern the **taxonomic layer specifically** and bind every taxon, rank, closure, and classification decision fixed in this document:

| # | Taxonomic Principle | Basis |
|---|---------------------|-------|
| **TXP-1 Root-anchored classification** | Every taxon descends from the single abstract root `SecurityConstruct ⊑ ENG-002::Object`; nothing is classified outside the root. | SECURITY-003 FP-2/IH-2; USL-003 |
| **TXP-2 No new taxon** | Every taxon is a class already named in the Ontology catalog (`ONT-E-01…32`) or an abstract family/partition the Ontology fixed (§8.2/§12/§13); the taxonomy mints no entity, class, primitive, authority, registry, identifier, or lifecycle. | SECURITY-003 CAT-3; USL-015 |
| **TXP-3 Exhaustiveness** | At every rank the child taxa **cover** their parent: every non-abstract construct of the parent belongs to ≥1 child taxon (no unclassifiable construct). | SECURITY-003 PR-1; closed §18 |
| **TXP-4 Disjointness** | At every rank the child taxa are **pairwise disjoint**: no non-abstract construct belongs to two sibling taxa (no dual classification). | SECURITY-003 PR-2; closed §18 |
| **TXP-5 Single-parent tree** | Classification uses single inheritance: every taxon has exactly one direct parent; the classification structure is a rooted tree (a fortiori acyclic). | SECURITY-003 IH-1/IH-3 |
| **TXP-6 Determinism & totality** | `classify(c)` is a total function on well-formed constructs; identical inputs yield identical leaves; ambiguity/absence resolves to `indeterminate → reject` (default-deny). | SECURITY-003 ONT-INV-6/8; USL-005/012 |
| **TXP-7 Evidence-decidable classification** | Every classification step is decidable from the construct's immutable, evidenced attributes (`type`, partition role, family criteria); no classification is inferred without evidence. | SECURITY-003 FP-5/ONT-INV-7; USL-012 |
| **TXP-8 Coverage of the constitution** | The leaf taxa jointly cover every SECURITY-001 §7 constitutional concept plus the ontological refinements admitted by SECURITY-003; no constitutional concept is left unclassified (CAT-1 closure). | SECURITY-001 §7; SECURITY-003 CAT-1 |
| **TXP-9 Assurance, not enforcement** | Classification is descriptive/evaluative; assigning a construct to `ProtectionObject` (or any taxon) names what it *is*, never enforces anything — enforcement stays delegated by reference to frozen lower mechanisms. | SECURITY-003 FP-7/ONT-INV-15; USL-014 |
| **TXP-10 Non-constitutive evolution** | The taxonomy grows append-only / supersession-only with mandatory backward traceability; new leaves/sub-kinds are admitted additively as the Ontology admits new entities, never by rewrite. | SECURITY-003 FP-10; USL-015; AUTH-INF-001 |

These ten principles are **complete over the concerns of the taxonomic layer** (rooting, non-mintage, exhaustiveness, disjointness, tree-structure, determinism, evidence, coverage, enforcement-boundary, evolution) and non-overlapping in obligation. Any future taxonomic principle is admitted **additively** (`TXP-11…`), never by rewrite.

---

## SECTION 5 — TAXONOMY SCOPE

| In scope (this taxonomy fixes/closes) | Out of scope (by reference or excluded) |
|---------------------------------------|------------------------------------------|
| The canonical **classification ranks** (Root → Partition → Family → Class/Leaf → Sub-kind) over the Ontology catalog | The **entity model** itself (attributes, relationships, per-concern semantics) — owned by SECURITY-003, consumed here **by reference**, never redefined |
| The **closure proofs** the Ontology deferred: partition (PR-1/2/3), object-family, Principal-archetype (ST-4), control-kind | Concrete cryptographic algorithms/suites, key stores/KMS, identity providers, scanners, WAFs, secret managers, vendor products, running systems, code |
| The **constitutional coverage matrix** (CAT-1): SECURITY-001 §7 (25) + `Role` + `Vulnerability` + §8 supporting entities → leaves | Execution/state/policy **runtime** (RL-F2); platform security service (PL-F2 `platform/security`); data representation (DF-2); service operation (SF-2); application security (AF-3 / APPLICATION-013); infrastructure security facet (Band-13 U08) — **reused by reference, never redefined** |
| The **total, deterministic classification function** `classify(c) → leaf` and its default-deny discipline | The **meta-model** — leaf meta-classes, well-formedness rules, instantiation semantics — which this taxonomy *feeds* but does not *fix* (SECURITY-005) |
| The **taxonomic invariants** (`TAX-INV-*`) and **closure theorems** (`TAX-CLO-*`) | Any operational/enforcement/ratification/EC-series authority; any secret/credential/key material; any counting of source assets as roadmap completion (STATUS-001 §2) |
| The taxonomy's **downward-only relationship** to Existence…Infrastructure and its **by-reference** mapping to validation/certification/acceptance | Any new entity, class, taxon, primitive, authority, registry system, identifier scheme, or lifecycle (USL-015) |

The taxonomy is a **classification reference**, not a runtime schema: it fixes how security constructs are *categorized* for architecture, not a persisted data model, wire format, or executable type system.

---

## SECTION 6 — TAXONOMY BOUNDARIES

The taxonomy draws explicit, non-overlapping boundaries so that it owns **only** the classification of assurance-domain constructs and re-owns nothing (USL-002; SECURITY-001 §17; SECURITY-003 §6):

| Boundary | This taxonomy (SECURITY-004) | The bounded layer / artifact (by reference) |
|----------|------------------------------|---------------------------------------------|
| **Ontology boundary** | Classifies the entities the Ontology fixed; proves closure over them. | SECURITY-003 owns the entities, attributes, relationships, and invariants. **Consumed by reference; never redefined.** |
| **Existence boundary** | Roots the classification tree at `SecurityConstruct ⊑ ENG-002::Object`. | EL-1 owns objecthood/identity/value/type/reference. **Never redefined.** |
| **Behavior boundary** | Classifies `Authorization`/`Policy`/`Control` as taxa; names what they *are*. | RL-F2 owns runtime behavior/enforcement; delegated **by reference**. |
| **Composition / Representation / Operation / Experience boundaries** | References PL-F2, DF-2, SF-2, AF-3 constructs only as the referents of already-classified entities. | Those layers own composition/representation/operation/experience. **Never re-owned.** |
| **Realization-environment boundary** | Classifies `IsolationDomain`, `Availability`, `Control` whose referents are Band-13 U05/U07/U08. | Band-13 owns isolation/availability/security-facet. **Consumed by reference.** |
| **Meta boundary** | *Feeds* the meta-model with a closed leaf set and classification procedure; does **not** fix well-formedness or instantiation. | SECURITY-005 (Meta-Model) closes leaf meta-classes, well-formedness, and instantiation semantics. |

**Boundary rule.** The taxonomy classifies; it never re-implements, re-owns, or duplicates an entity, mechanism, or lower construct (USL-002). Where a fixation is downstream (meta-model well-formedness/instantiation), the taxonomy **feeds but does not close** it, deferring to SECURITY-005.

---

## SECTION 7 — TAXONOMY DESIGN PRINCIPLES

The taxonomy is constructed under the following design law, which governs *how* taxa, ranks, and classification rules are formed (distinct from the *what-holds* foundational principles of §4):

| # | Design Principle | Statement |
|---|------------------|-----------|
| **TDP-1 Rank discipline** | Every taxon occupies exactly one canonical rank (Root=0, Partition=1, Family=2, Class/Leaf=3, Sub-kind=4); no taxon spans ranks. |
| **TDP-2 Single-criterion split** | Each rank-to-rank split is governed by **one** decidable classificatory criterion (partition: agency vs acted-upon; family: role-of-object; leaf: canonical entity type), so classification at each step is a single decidable test. |
| **TDP-3 Class reuse only** | Every taxon reuses an Ontology class verbatim (its canonical name and `ONT-E-nn` code); no synonym, rename, or new class is introduced (DP-2 of SECURITY-003; USL-015). |
| **TDP-4 Tree over DAG** | Classification uses single-parent inheritance, yielding a tree; multiple inheritance is disallowed for classification decidability (IH-1). |
| **TDP-5 Exhaustive-and-disjoint at every split** | Every split is proven exhaustive (covers the parent) and disjoint (siblings share no non-abstract member) before it is admitted (§18). |
| **TDP-6 Decidable, total classifier** | The classification function is total and decidable from immutable evidenced attributes; every undefined/ambiguous case maps to `indeterminate → reject` (default-deny). |
| **TDP-7 Stable codes** | Leaf codes (`TAX-L-nn`) are stable, append-only, intra-document references bound 1:1 to the Ontology's `ONT-E-nn`; they mint no registry identifier (CAT-3). |
| **TDP-8 Coverage-first** | No taxonomy is admitted until the coverage matrix (§15) shows every constitutional/ontological concept classified with no gap and no orphan taxon. |
| **TDP-9 Reference-only downward binding** | All bindings to lower layers and to sibling pipelines (validation/certification/acceptance) are downward-only / by-reference; the taxonomy redefines, re-owns, or duplicates nothing. |
| **TDP-10 Neutrality** | Every taxon and criterion is implementation-independent, technology-, vendor-, algorithm-, cloud-, and platform-neutral; no concrete technology is named or implied. |

---

## SECTION 8 — THE CANONICAL TAXONOMIC RANKS

The taxonomy fixes **five canonical ranks**. Each rank is a horizontal cut of the single-parent classification tree; each rank-to-rank descent applies exactly one decidable criterion (TDP-2).

| Rank | Name | Members | Splitting criterion (single, decidable) | Instantiable | Fixed / closed in |
|------|------|---------|-----------------------------------------|--------------|-------------------|
| **0** | **Root** | `SecurityConstruct` | — (the root) | No (abstract) | §9 (root) |
| **1** | **Partition** | `SecuritySubject`, `SecurityObject` | **Agency**: can the construct *act / hold authority / be accountable* (Subject) vs is it *acted-upon / decided-over / produced / asserted* (Object)? | No (abstract) | §9 (closed) |
| **2** | **Family** | Subject: `Principal`; Object: the 7 object families | **Role-of-thing**: on the Object side, the object's role (access / relation / authority / protection / risk / assurance / property); on the Subject side, the single agency-bearer family. | Object families No; `Principal` Yes | §10 (subject), §11 (object) |
| **3** | **Class / Leaf** | the 32 catalog entities (`ONT-E-01…32`) | **Canonical entity type** (`type`, ENG-004): which single canonical entity the construct instantiates. | Yes | §12, §14 |
| **4** | **Sub-kind** | `Principal` archetypes (4); `Control` kinds (3) | **Typed refinement** that mints no entity (credential-class/agency-nature; preventive/detective/corrective). | Yes | §10 (archetypes), §13 (control) |

**Rank rules:**

- **RK-1 Exactly-one-rank.** Every taxon occupies exactly one rank (TDP-1); the abstract taxa (Rank 0–2 object families) are never instantiated (IH-4), only Rank-3 leaves and Rank-4 sub-kinds are.
- **RK-2 Single descent criterion.** Each descent (0→1 agency; 1→2 role/family; 2→3 entity-type; 3→4 typed-refinement) applies exactly one decidable criterion (TDP-2), so `classify` is a fixed sequence of single tests (§16).
- **RK-3 Rank-2 asymmetry.** The Subject partition has a single Rank-2 family (`Principal`) that is itself the sole concrete Subject leaf; the Object partition has seven abstract Rank-2 families whose leaves are the 31 object entities. This asymmetry is proven consistent with exhaustiveness/disjointness in §18.
- **RK-4 No skipped ranks.** A leaf's path to the root visits exactly one taxon at each rank above it (Leaf → Family → Partition → Root); no rank is skipped and none is doubled (single-parent tree, TDP-4).
- **RK-5 Sub-kinds are not partitions.** Rank-4 sub-kinds are typed refinements of a single leaf entity; they add no attribute beyond the refinement criterion and mint no entity (SECURITY-003 ST-4; RO of Control §13).

---

## SECTION 9 — RANK-0 / RANK-1 — ROOT & PARTITION TAXONOMY + PARTITION CLOSURE

### 9.1 Root (Rank 0)

```
ENG-002::Object                       «frozen existence primitive — referenced, never redefined»
   ▲ ⊑
SecurityConstruct  «Rank 0 — abstract root; the sole root of the taxonomy»
```

`SecurityConstruct` is the single Rank-0 taxon (SECURITY-003 §8.1). Every taxon and every classified construct descends from it (TXP-1). It is never instantiated (IH-4).

### 9.2 Partition (Rank 1)

```
SecurityConstruct «Rank 0, abstract»
├── SecuritySubject   «Rank 1 — abstract»  — bears agency: acts / holds authority / is accountable
└── SecurityObject    «Rank 1 — abstract»  — acted-upon / decided-over / produced / asserted
```

The Rank-1 split applies the single criterion **agency** (RK-2). A construct is a `SecuritySubject` iff it can act, be authorized, hold trust/authority, or be held accountable; otherwise it is a `SecurityObject` (SECURITY-003 §8.2).

### 9.3 Partition closure (discharging SECURITY-003 PR-1/PR-2/PR-3)

SECURITY-003 §8.2 fixed the partition rules and deferred their closure "*proven in SECURITY-004*". They are closed here:

| Closure | Statement | Proof basis |
|---------|-----------|-------------|
| **PC-1 Exhaustiveness (closes PR-1)** | Every non-abstract `SecurityConstruct` is a `SecuritySubject` **or** a `SecurityObject`. | The agency criterion is **total** over the catalog: of the 32 catalog entities, exactly one (`Principal`, `ONT-E-02`) bears agency (SECURITY-003 CAT-2/§13 ST-1) and is a `SecuritySubject`; the remaining 31 are acted-upon/produced/asserted and are `SecurityObject`s (SECURITY-003 §11 partition column). No catalog entity is unassigned ⇒ coverage complete (see §14 register, §15 matrix). |
| **PC-2 Disjointness (closes PR-2)** | No non-abstract construct is both a `SecuritySubject` and a `SecurityObject`. | Agency-bearing and acted-upon are **mutually exclusive** classificatory roles (SECURITY-003 PR-2, ST-5): where a real-world thing plays both roles, the Ontology models two distinct entities (a `Principal` and a resource `SecurityObject`) related by reference, never one dual-typed entity. Hence no construct occupies both partitions. |
| **PC-3 Rootedness (closes PR-3)** | Both partitions specialize `SecurityConstruct`; neither exists outside the root. | By construction both are direct `isA` children of `SecurityConstruct` (single-parent, TDP-4); no third Rank-1 sibling exists (the agency criterion is binary). |

**Partition-closure theorem (summary; full proof §18 `TAX-CLO-1`).** `{SecuritySubject, SecurityObject}` is an **exhaustive, disjoint, rooted** partition of the non-abstract constructs of `SecurityConstruct`. Therefore Rank 1 is closed: every construct classifies into exactly one partition, and the classifier's first step (§16) is total and deterministic.

---

## SECTION 10 — RANK-2 (SUBJECT SIDE) — SUBJECT FAMILY & PRINCIPAL ARCHETYPE TAXONOMY + ARCHETYPE CLOSURE

### 10.1 Subject family (Rank 2) and leaf (Rank 3)

The `SecuritySubject` partition has a **single Rank-2 family**, which is also its **single Rank-3 concrete leaf**: `Principal` (`ONT-E-02`) — the sole bearer of agency in the Ontology (SECURITY-003 §13 ST-1).

```
SecuritySubject «Rank 1, abstract»
└── Principal (ONT-E-02) «Rank 2 family = Rank 3 leaf; concrete; the sole Subject leaf»
      ├── HumanPrincipal      «Rank 4 sub-kind»
      ├── ServicePrincipal    «Rank 4 sub-kind»
      ├── DevicePrincipal     «Rank 4 sub-kind»
      └── CompositePrincipal  «Rank 4 sub-kind»
```

`Principal` is the only concrete Subject entity; the Subject side therefore has no seven-way family split (RK-3). Its Rank-4 refinement is by **archetype** — the single criterion `{Human, Service, Device, Composite}` differing only by agency-nature and secret-free credential-class (SECURITY-003 §13 ST-4).

### 10.2 Principal archetype closure (discharging SECURITY-003 ST-4)

SECURITY-003 §13 ST-4 fixed the four archetypes as typed refinements of one entity and deferred their closure "*proven in SECURITY-004*". Closed here:

| Closure | Statement | Proof basis |
|---------|-----------|-------------|
| **AC-1 Exhaustiveness** | Every `Principal` is exactly one of `{HumanPrincipal, ServicePrincipal, DevicePrincipal, CompositePrincipal}`. | The archetype criterion partitions agency-nature into the natural-person, autonomous-workload, attested-device, and bounded-aggregate cases; a `CompositePrincipal` (bounded aggregate acting as one) absorbs any composite/aggregate agent, so the four cases are jointly total over agency-bearers (SECURITY-003 §13). |
| **AC-2 Disjointness** | No `Principal` is two archetypes at once. | Agency-nature is single-valued (`archetype` attribute, SECURITY-003 §15 PR attributes: cardinality 1); a composite of principals is a `CompositePrincipal`, not simultaneously its members. |
| **AC-3 No-mintage** | The archetypes add no entity, attribute (beyond agency-nature + credential-class), authority, or lifecycle. | SECURITY-003 ST-4/§15 PR-INV; USL-015. Archetypes are Rank-4 sub-kinds (RK-5), not Rank-1 partitions or Rank-3 leaves. |

**Archetype-closure theorem (summary; full proof §18 `TAX-CLO-4`).** `{HumanPrincipal, ServicePrincipal, DevicePrincipal, CompositePrincipal}` is an exhaustive, disjoint sub-kind refinement of the single leaf `Principal`; it mints no entity. The Subject side of the taxonomy is therefore closed at every rank.

---

## SECTION 11 — RANK-2 (OBJECT SIDE) — THE SEVEN OBJECT FAMILIES + FAMILY CLOSURE

### 11.1 The seven object families (Rank 2)

`SecurityObject` is split at Rank 2 by the single criterion **role-of-object** into seven abstract families (SECURITY-003 §12/§45.1). Each family is an abstract specialization of `SecurityObject`; every object leaf belongs to exactly one family.

```
SecurityObject «Rank 1, abstract»
├── AccessObject      «governs/records who may do what»            — 9 leaves
├── RelationObject    «an evidenced security relation»             — 3 leaves
├── AuthorityObject   «a referenced capacity to decide/permit»     — 1 leaf
├── ProtectionObject  «prevents/contains/restores harm»            — 4 leaves
├── RiskObject        «models potential/actual weakness & exposure»— 3 leaves
├── AssuranceObject   «substantiates that a property holds»        — 5 leaves
└── PropertyObject    «a named, asserted-and-evidenced property»    — 6 leaves
```

| Family | Role-of-object criterion (single, decidable) | Leaf count | Leaves (`ONT-E`) |
|--------|----------------------------------------------|-----------:|------------------|
| `AccessObject` | governs or records **who may do what** | 9 | Identity (01), CredentialModel (03), Authentication (08), Authorization (09), Policy (10), Permission (11), Privilege (12), Role (13), Delegation (14) |
| `RelationObject` | is an **evidenced security relation** between constructs | 3 | Trust (05), TrustAnchor (06), TrustBoundary (07) |
| `AuthorityObject` | is a **referenced capacity to decide/permit** | 1 | Authority (04) |
| `ProtectionObject` | **prevents / contains / restores** harm | 4 | Control (15), IsolationDomain (23), Boundary (24), Recovery (30) |
| `RiskObject` | **models** potential/actual weakness & exposure | 3 | Threat/ThreatModel (16), Risk/RiskAssessment (17), Vulnerability (18) |
| `AssuranceObject` | **substantiates** that a property holds | 5 | Evidence (19), AuditRecord (20), Compliance (21), Attestation (22), AssuranceFacet (31) |
| `PropertyObject` | is a **named, asserted-and-evidenced property** | 6 | Integrity (25), Confidentiality (26), Availability (27), Accountability (28), NonRepudiation (29), SecurityGovernanceFacet (32) |
| **Total** | | **31** | all 31 `SecurityObject` leaves |

### 11.2 Object-family closure (discharging SECURITY-003 §12 family-closure)

SECURITY-003 §12 stated "*every `SecurityObject` leaf belongs to exactly one family (family-closure proven in SECURITY-004)*". Closed here:

| Closure | Statement | Proof basis |
|---------|-----------|-------------|
| **FC-1 Exhaustiveness** | Every `SecurityObject` leaf belongs to ≥1 of the seven families. | The seven role-of-object criteria are jointly total over the 31 object leaves: 9+3+1+4+3+5+6 = **31** = all object leaves (§14 register; SECURITY-003 §45.1 inheritance hierarchy). No object leaf is unassigned. |
| **FC-2 Disjointness** | No `SecurityObject` leaf belongs to two families. | Each leaf's role-of-object is single-valued and each leaf appears under exactly one family in the Ontology inheritance hierarchy (SECURITY-003 §45.1); the family sums (9,3,1,4,3,5,6) partition 31 with no overlap. |
| **FC-3 Abstract families** | The seven families are abstract (never instantiated); only their leaves are instantiable. | SECURITY-003 §12/IH-4. |
| **FC-4 No-mintage** | The families introduce no entity beyond the Ontology's abstract families. | SECURITY-003 §12; USL-015. |

**Note on the seven-family criterion and prior §11 grouping.** SECURITY-003 §11 recorded a looser "concept family" column (e.g., "Governance" for `AssuranceFacet`/`SecurityGovernanceFacet`); the **authoritative** family partition is the formal seven-family inheritance hierarchy of SECURITY-003 §12/§45.1, which this taxonomy adopts verbatim. Accordingly `AssuranceFacet` (31) is an `AssuranceObject` and `SecurityGovernanceFacet` (32) is a `PropertyObject`, exactly as §45.1 fixes. This introduces no reclassification of any entity — it uses the Ontology's own formal hierarchy (TDP-3).

**Family-closure theorem (summary; full proof §18 `TAX-CLO-2`).** The seven object families form an exhaustive, disjoint partition of the 31 `SecurityObject` leaves. Combined with PC-1/PC-2 (§9) and AC-1/AC-2 (§10), the taxonomy is closed at Ranks 1–2 across both partitions.

---

## SECTION 12 — RANK-3 / RANK-4 — PER-FAMILY LEAF TAXONOMY

This section assigns **every** catalog leaf to its family and fixes its full taxonomic path (Leaf → Family → Partition → Root). Every leaf is an Ontology entity reused verbatim (TDP-3); no leaf is invented. Each leaf carries its `ONT-E-nn` code (Ontology) and its `TAX-L-nn` code (this taxonomy, §14), bound 1:1.

### 12.1 Subject partition — `Principal` family (1 leaf)

| Leaf (`ONT-E`) | Rank-4 sub-kinds | Path |
|----------------|------------------|------|
| `Principal` (02) | Human / Service / Device / Composite (§10) | `Principal ⊑ SecuritySubject ⊑ SecurityConstruct` |

### 12.2 Object partition — `AccessObject` family (9 leaves)

| Leaf (`ONT-E`) | Path (Leaf ⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|------------------------------------------------------------------|
| `Identity` (01) | ✔ |
| `CredentialModel` (03) | ✔ (secret-free class) |
| `Authentication` (08) | ✔ (decision) |
| `Authorization` (09) | ✔ (decision) |
| `Policy` / `AuthorizationPolicy` (10) | ✔ |
| `Permission` (11) | ✔ |
| `Privilege` (12) | ✔ |
| `Role` (13) | ✔ (aggregation) |
| `Delegation` (14) | ✔ |

### 12.3 Object partition — `RelationObject` family (3 leaves)

| Leaf (`ONT-E`) | Path (Leaf ⊑ RelationObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|-------------------------------------------------------------------|
| `Trust` (05) | ✔ (relation) |
| `TrustAnchor` (06) | ✔ |
| `TrustBoundary` (07) | ✔ |

### 12.4 Object partition — `AuthorityObject` family (1 leaf)

| Leaf (`ONT-E`) | Path (Leaf ⊑ AuthorityObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|--------------------------------------------------------------------|
| `Authority` (04) | ✔ (referenced capacity; never minted) |

### 12.5 Object partition — `ProtectionObject` family (4 leaves)

| Leaf (`ONT-E`) | Rank-4 sub-kinds | Path (Leaf ⊑ ProtectionObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|------------------|----------------------------------------------------------------------|
| `Control` (15) | Preventive / Detective / Corrective (§13) | ✔ |
| `IsolationDomain` (23) | — | ✔ |
| `Boundary` (24) | — | ✔ |
| `Recovery` (30) | — | ✔ |

### 12.6 Object partition — `RiskObject` family (3 leaves)

| Leaf (`ONT-E`) | Path (Leaf ⊑ RiskObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|----------------------------------------------------------------|
| `Threat` / `ThreatModel` (16) | ✔ (exploiting event/actor; model aggregates threats) |
| `Risk` / `RiskAssessment` (17) | ✔ (evaluated exposure) |
| `Vulnerability` (18) | ✔ (weakness of a construct) |

### 12.7 Object partition — `AssuranceObject` family (5 leaves)

| Leaf (`ONT-E`) | Path (Leaf ⊑ AssuranceObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|---------------------------------------------------------------------|
| `Evidence` / `SecurityEvidence` (19) | ✔ (first-class) |
| `Audit` / `AuditRecord` (20) | ✔ (immutable, hash-chained) |
| `Compliance` (21) | ✔ (aggregated verdict) |
| `Attestation` (22) | ✔ (point-in-time assertion) |
| `AssuranceFacet` (31) | ✔ (non-enforcing evaluative facet) |

### 12.8 Object partition — `PropertyObject` family (6 leaves)

| Leaf (`ONT-E`) | Path (Leaf ⊑ PropertyObject ⊑ SecurityObject ⊑ SecurityConstruct) |
|----------------|--------------------------------------------------------------------|
| `Integrity` (25) | ✔ |
| `Confidentiality` (26) | ✔ |
| `Availability` (27) | ✔ (references Band-13 U07 by reference) |
| `Accountability` (28) | ✔ |
| `NonRepudiation` (29) | ✔ |
| `SecurityGovernanceFacet` (32) | ✔ (non-enforcing governance property) |

**Leaf-assignment rule.** Every leaf appears in **exactly one** of §12.1–§12.8 (single-parent, TDP-4). The union of the eight tables is the 32 catalog entities: 1 (Subject) + 9 + 3 + 1 + 4 + 3 + 5 + 6 = **32** (§14 register; §18 `TAX-CLO-3`).

---

## SECTION 13 — CONTROL SUB-TAXONOMY + SUB-KIND CLOSURES

Two catalog leaves carry Ontology-fixed **typed refinements** that mint no new entity (RK-5). The taxonomy records them as Rank-4 sub-kinds and proves their closure. No other leaf has sub-kinds.

### 13.1 `Control` sub-taxonomy (Preventive / Detective / Corrective)

SECURITY-003 §27 fixed `Control` (`ONT-E-15`) with three canonical sub-kinds via the single-valued `controlKind` attribute.

```
Control (ONT-E-15) «ProtectionObject leaf»
├── PreventiveControl   — bars a threat from acting          «Rank 4 sub-kind»
├── DetectiveControl    — evidences a threat's action        «Rank 4 sub-kind»
└── CorrectiveControl   — restores state after a threat acts «Rank 4 sub-kind»
```

| Closure | Statement | Proof basis |
|---------|-----------|-------------|
| **CC-1 Exhaustiveness** | Every `Control` is exactly one of `{Preventive, Detective, Corrective}`. | The control lifecycle relative to a threat event is total: *before* (prevent), *during/observed* (detect), *after* (correct); SECURITY-003 §27 fixes exactly these three; `controlKind` is mandatory (no unclassified control). |
| **CC-2 Disjointness** | No `Control` is two kinds at once. | `controlKind` is single-valued (SECURITY-003 §27 attribute table); a mechanism that both prevents and detects is modeled as two composed `Control`s (`composesWith`, CT-INV-2), not one dual-kind control. |
| **CC-3 No-mintage** | The three kinds add no entity/attribute beyond `controlKind`. | SECURITY-003 §27; USL-015. Rank-4 sub-kinds (RK-5). |

### 13.2 `Principal` archetype sub-taxonomy

Fixed and closed in §10.2 (`AC-1/AC-2/AC-3`): `{Human, Service, Device, Composite}` — an exhaustive, disjoint, non-minting Rank-4 refinement of `Principal`.

### 13.3 Sub-kind rule

- **SK-1 Refinement-only.** A sub-kind refines exactly one leaf by exactly one single-valued criterion (`controlKind`, `archetype`); it adds no entity, authority, registry, identifier, or lifecycle (USL-015; RK-5).
- **SK-2 No cross-family sub-kinds.** Sub-kinds never move a construct to a different family or leaf; a `PreventiveControl` remains a `Control ⊑ ProtectionObject` (TDP-1).
- **SK-3 Closed set.** Only `Control` and `Principal` bear sub-kinds; all other 30 leaves are terminal at Rank 3 (§14). Any future sub-kind is admitted additively (§24; USL-015).

**Sub-kind-closure theorem (summary; full proof §18 `TAX-CLO-4`).** Both sub-kind sets are exhaustive, disjoint, and non-minting; the taxonomy is therefore closed at Rank 4.

---

## SECTION 14 — THE COMPLETE CANONICAL LEAF REGISTER

The 32 canonical leaves, each bound 1:1 to an Ontology entity (`ONT-E-nn`) and carrying a stable intra-document taxonomy code (`TAX-L-nn`). `TAX-L-nn` codes are **intra-document references only** (they mint no registry identifier — CAT-3/TDP-7); the artifact's registry identity is the REG-AUTO-001 allocation `UCOS-SEC-000005`.

| `TAX-L` | Leaf entity | `ONT-E` | Partition | Family | Rank-4 sub-kinds |
|---------|-------------|---------|-----------|--------|------------------|
| `TAX-L-01` | `Identity` | 01 | Object | AccessObject | — |
| `TAX-L-02` | `Principal` | 02 | **Subject** | Principal | Human/Service/Device/Composite |
| `TAX-L-03` | `CredentialModel` | 03 | Object | AccessObject | — |
| `TAX-L-04` | `Authority` | 04 | Object | AuthorityObject | — |
| `TAX-L-05` | `Trust` | 05 | Object | RelationObject | — |
| `TAX-L-06` | `TrustAnchor` | 06 | Object | RelationObject | — |
| `TAX-L-07` | `TrustBoundary` | 07 | Object | RelationObject | — |
| `TAX-L-08` | `Authentication` | 08 | Object | AccessObject | — |
| `TAX-L-09` | `Authorization` | 09 | Object | AccessObject | — |
| `TAX-L-10` | `Policy` / `AuthorizationPolicy` | 10 | Object | AccessObject | — |
| `TAX-L-11` | `Permission` | 11 | Object | AccessObject | — |
| `TAX-L-12` | `Privilege` | 12 | Object | AccessObject | — |
| `TAX-L-13` | `Role` | 13 | Object | AccessObject | — |
| `TAX-L-14` | `Delegation` | 14 | Object | AccessObject | — |
| `TAX-L-15` | `Control` | 15 | Object | ProtectionObject | Preventive/Detective/Corrective |
| `TAX-L-16` | `Threat` / `ThreatModel` | 16 | Object | RiskObject | — |
| `TAX-L-17` | `Risk` / `RiskAssessment` | 17 | Object | RiskObject | — |
| `TAX-L-18` | `Vulnerability` | 18 | Object | RiskObject | — |
| `TAX-L-19` | `Evidence` / `SecurityEvidence` | 19 | Object | AssuranceObject | — |
| `TAX-L-20` | `Audit` / `AuditRecord` | 20 | Object | AssuranceObject | — |
| `TAX-L-21` | `Compliance` | 21 | Object | AssuranceObject | — |
| `TAX-L-22` | `Attestation` | 22 | Object | AssuranceObject | — |
| `TAX-L-23` | `Isolation` / `IsolationDomain` | 23 | Object | ProtectionObject | — |
| `TAX-L-24` | `Boundary` | 24 | Object | ProtectionObject | — |
| `TAX-L-25` | `Integrity` | 25 | Object | PropertyObject | — |
| `TAX-L-26` | `Confidentiality` | 26 | Object | PropertyObject | — |
| `TAX-L-27` | `Availability` | 27 | Object | PropertyObject | — |
| `TAX-L-28` | `Accountability` | 28 | Object | PropertyObject | — |
| `TAX-L-29` | `NonRepudiation` | 29 | Object | PropertyObject | — |
| `TAX-L-30` | `Recovery` | 30 | Object | ProtectionObject | — |
| `TAX-L-31` | `AssuranceFacet` | 31 | Object | AssuranceObject | — |
| `TAX-L-32` | `SecurityGovernanceFacet` | 32 | Object | PropertyObject | — |

**Register rules:**
- **LR-1 Bijection.** `TAX-L-nn ↔ ONT-E-nn` is a bijection over the 32 catalog entities; the taxonomy classifies every Ontology entity and no more (no invented leaf; TXP-2).
- **LR-2 Partition tally.** Subject = 1 (`TAX-L-02`); Object = 31; total = 32.
- **LR-3 Family tally.** AccessObject 9 · RelationObject 3 · AuthorityObject 1 · ProtectionObject 4 · RiskObject 3 · AssuranceObject 5 · PropertyObject 6 = 31 object leaves (§18 `TAX-CLO-2/3`).
- **LR-4 Append-only.** Future entities admitted by the Ontology are appended as `TAX-L-33…`, never renumbered (§24; USL-015).

---

## SECTION 15 — COVERAGE CLOSURE (CAT-1) — CONSTITUTIONAL & ONTOLOGICAL COVERAGE MATRIX

This section discharges SECURITY-003 **CAT-1** ("*coverage/partition closure proven in SECURITY-004*"). It proves **bidirectional** coverage: (a) every constitutional/ontological concept maps to ≥1 leaf (**completeness — no gap**), and (b) every leaf maps back to a constitutional or ontological source (**rootedness — no invented taxon**).

### 15.1 The 25 SECURITY-001 §7 constitutional concepts → leaves

| # | Constitutional concept (SECURITY-001 §7) | Leaf | Family |
|---|------------------------------------------|------|--------|
| 1 | Identity | `TAX-L-01` | AccessObject |
| 2 | Principal | `TAX-L-02` | Principal (Subject) |
| 3 | Trust | `TAX-L-05` | RelationObject |
| 4 | Authority | `TAX-L-04` | AuthorityObject |
| 5 | Authentication | `TAX-L-08` | AccessObject |
| 6 | Authorization | `TAX-L-09` | AccessObject |
| 7 | Policy | `TAX-L-10` | AccessObject |
| 8 | Permission | `TAX-L-11` | AccessObject |
| 9 | Privilege | `TAX-L-12` | AccessObject |
| 10 | Delegation | `TAX-L-14` | AccessObject |
| 11 | Control | `TAX-L-15` | ProtectionObject |
| 12 | Boundary | `TAX-L-24` | ProtectionObject |
| 13 | Threat | `TAX-L-16` | RiskObject |
| 14 | Risk | `TAX-L-17` | RiskObject |
| 15 | Evidence | `TAX-L-19` | AssuranceObject |
| 16 | Audit | `TAX-L-20` | AssuranceObject |
| 17 | Compliance | `TAX-L-21` | AssuranceObject |
| 18 | Attestation | `TAX-L-22` | AssuranceObject |
| 19 | Isolation | `TAX-L-23` | ProtectionObject |
| 20 | Integrity | `TAX-L-25` | PropertyObject |
| 21 | Confidentiality | `TAX-L-26` | PropertyObject |
| 22 | Availability | `TAX-L-27` | PropertyObject |
| 23 | Accountability | `TAX-L-28` | PropertyObject |
| 24 | Non-repudiation | `TAX-L-29` | PropertyObject |
| 25 | Recovery | `TAX-L-30` | ProtectionObject |

All **25** constitutional concepts map to a distinct leaf ⇒ **no constitutional gap** (TXP-8).

### 15.2 The two ontological refinements → leaves

| Refinement | Source | Leaf | Family |
|------------|--------|------|--------|
| `Role` | SECURITY-001 §5/§9 (RBAC/ABAC), admitted by SECURITY-003 §3 | `TAX-L-13` | AccessObject |
| `Vulnerability` | SECURITY-002 §11–§12 (weakness), admitted by SECURITY-003 §3 | `TAX-L-18` | RiskObject |

### 15.3 The five §8 supporting entities → leaves

| Supporting entity | Source | Leaf | Family |
|-------------------|--------|------|--------|
| `CredentialModel` (secret-free) | SECURITY-001 §8 | `TAX-L-03` | AccessObject |
| `TrustAnchor` | SECURITY-001 §8 | `TAX-L-06` | RelationObject |
| `TrustBoundary` | SECURITY-001 §8 | `TAX-L-07` | RelationObject |
| `AssuranceFacet` | SECURITY-001 §8/§12 | `TAX-L-31` | AssuranceObject |
| `SecurityGovernanceFacet` | SECURITY-001 §8/§12 | `TAX-L-32` | PropertyObject |

### 15.4 Coverage tally & closure

| Source class | Count | Leaves |
|--------------|------:|--------|
| SECURITY-001 §7 constitutional concepts | 25 | 25 distinct leaves (§15.1) |
| Ontological refinements (`Role`, `Vulnerability`) | 2 | `TAX-L-13`, `TAX-L-18` |
| §8 supporting entities | 5 | `TAX-L-03/06/07/31/32` |
| **Total sources** | **32** | **all 32 leaves (`TAX-L-01…32`)** |

- **CAT-1a Completeness (no gap).** Every source concept maps to ≥1 leaf; 25 + 2 + 5 = 32 sources cover 32 leaves (§15.1–§15.3). No constitutional or ontological concept is unclassified.
- **CAT-1b Rootedness (no invented taxon).** Every leaf (`TAX-L-01…32`) appears in exactly one row above with a named constitutional/ontological source ⇒ no leaf lacks a source; the taxonomy mints no entity (TXP-2/LR-1).
- **CAT-1c Bijection.** §15.1–§15.3 establish a bijection {32 sources} ↔ {32 leaves} ↔ {`ONT-E-01…32`} (LR-1); coverage is exact — neither under- nor over-covering.

**Coverage-closure theorem (summary; full proof §18 `TAX-CLO-5`).** The leaf taxonomy is a bijective, gap-free, orphan-free cover of the constitutional and ontological concept space. **CAT-1 is closed.**

---

## SECTION 16 — THE CANONICAL CLASSIFICATION FUNCTION

The taxonomy fixes a single **total, deterministic** classification function `classify : WellFormedConstruct → Leaf ∪ {reject}` that places any well-formed `SecurityConstruct` (as defined by SECURITY-003 §52 existence rules) into exactly one leaf, or rejects it (default-deny). It is a fixed sequence of single decidable tests, one per rank descent (RK-2).

### 16.1 Decision procedure

```
classify(c):
  # Precondition — well-formedness (SECURITY-003 §52 EX-1…EX-9), evidence-decidable (TXP-7)
  if not well_formed(c):                      return reject        # EX-3/EX-5/EX-6 fail ⇒ default-deny (USL-005)

  # Rank 0 → 1 : agency criterion (§9.2)
  if bears_agency(c):                                              # can act / hold authority / be accountable
      partition ← SecuritySubject
      # Rank 1 → 2 → 3 : the sole Subject leaf
      leaf ← Principal (TAX-L-02)
      # Rank 3 → 4 : archetype (single-valued c.archetype)
      subkind ← archetype_of(c) ∈ {Human, Service, Device, Composite}
      return (leaf, subkind)
  else:
      partition ← SecurityObject
      # Rank 1 → 2 : role-of-object criterion (§11.1) — exactly one family matches
      family ← the unique F ∈ {Access, Relation, Authority, Protection, Risk, Assurance, Property}Object
               such that role_of(c) = criterion(F)
      if no such F or more than one:          return reject        # cannot occur for catalog entities (FC-1/FC-2); guard = default-deny
      # Rank 2 → 3 : canonical entity type (c.type = ENG-004)
      leaf ← the unique L ∈ leaves(family) such that c.type = entity(L)
      if no such L:                           return reject        # unknown type ⇒ default-deny (USL-005)
      # Rank 3 → 4 : sub-kind where defined (§13); else terminal
      if leaf = Control:      subkind ← controlKind_of(c) ∈ {Preventive, Detective, Corrective}
      else:                   subkind ← ∅
      return (leaf, subkind)
```

### 16.2 Function properties

| Property | Statement | Basis |
|----------|-----------|-------|
| **CF-1 Totality** | `classify` is defined for every input; undefined/ambiguous cases return `reject`. | TXP-6; USL-005 |
| **CF-2 Determinism** | Identical inputs yield identical outputs (byte-identical), since every test reads immutable evidenced attributes (`type`, `archetype`, `controlKind`, agency role). | TXP-6; SECURITY-003 ONT-INV-8; USL-012 |
| **CF-3 Single-valued** | For any catalog construct exactly one `(leaf[, subkind])` is returned — guaranteed by partition disjointness (PC-2), family disjointness (FC-2), and single-valued sub-kind attributes (CC-2/AC-2). | §18 `TAX-CLO-1/2/4` |
| **CF-4 Completeness** | Every well-formed catalog construct is classified (not rejected) — guaranteed by exhaustiveness (PC-1, FC-1, coverage §15). | §18 `TAX-CLO-1/2/5` |
| **CF-5 Default-deny** | Absence of decidable type/role/evidence ⇒ `reject`; no construct is silently admitted to a leaf. | USL-005; SECURITY-003 ONT-INV-6 |
| **CF-6 Non-enforcing** | `classify` returns a category; it enacts nothing (assurance, not enforcement). | TXP-9; USL-014 |

**Classifier theorem (summary; full proof §18 `TAX-CLO-6`).** `classify` is a total, deterministic, single-valued function whose restriction to well-formed catalog constructs is a surjection onto the 32 leaves. Classification is therefore decidable and unique.

---

## SECTION 17 — TAXONOMIC INVARIANTS

The taxonomy-level invariants every conforming classification SHALL satisfy. They **draw upon and specialize** the Ontology's master register (`ONT-INV-1…16`); they add no invariant to the Ontology, they constrain the classification built over it.

| Invariant | Statement | Basis |
|-----------|-----------|-------|
| **TAX-INV-1 Rooted classification** | Every classified construct's path terminates at `SecurityConstruct ⊑ ENG-002::Object`. | TXP-1; ONT-INV-1 |
| **TAX-INV-2 Single-parent tree** | Every taxon has exactly one direct parent; the classification graph is a rooted tree. | TXP-5; ONT-INV-3 |
| **TAX-INV-3 Exhaustive splits** | At every rank the children cover the parent (no unclassifiable non-abstract construct). | TXP-3; PC-1/FC-1/AC-1/CC-1 |
| **TAX-INV-4 Disjoint splits** | At every rank the children are pairwise disjoint (no dual classification). | TXP-4; PC-2/FC-2/AC-2/CC-2 |
| **TAX-INV-5 Exactly-one-leaf** | Every well-formed construct classifies into exactly one leaf (and ≤1 sub-kind). | CF-3; §18 |
| **TAX-INV-6 Determinism** | Identical inputs yield identical classification. | TXP-6; ONT-INV-8 |
| **TAX-INV-7 Default-deny totality** | Ambiguity/absence/unknown-type ⇒ `reject`; no silent admission. | TXP-6; ONT-INV-6; USL-005 |
| **TAX-INV-8 Evidence-decidability** | Every classification step is decidable from immutable evidenced attributes. | TXP-7; ONT-INV-7 |
| **TAX-INV-9 Constitutional coverage** | Every SECURITY-001 §7 concept (+ admitted refinements + §8 supporting) classifies to a leaf. | TXP-8; §15 CAT-1 |
| **TAX-INV-10 No-mintage** | The taxonomy introduces no entity/class/taxon/primitive/authority/registry/identifier/lifecycle; every taxon is an Ontology class. | TXP-2; USL-015 |
| **TAX-INV-11 Non-enforcement** | Classification is descriptive/evaluative; it enforces nothing (`nonEnforcing = true` inherited). | TXP-9; ONT-INV-15; USL-014 |
| **TAX-INV-12 Bijective leaf register** | `TAX-L-nn ↔ ONT-E-nn` is a bijection over the 32 catalog entities. | LR-1; §14 |

**Invariant rules:** `TAX-INV-*` are **complete** over the taxonomic layer and **non-overlapping**; each specializes ≥1 `ONT-INV-*` without amending it. New invariants are admitted additively (`TAX-INV-13…`), never by rewrite (§24; USL-015).

---

## SECTION 18 — CLOSURE THEOREMS & PROOFS

The taxonomy's closure obligations (deferred by SECURITY-003) are discharged as the following theorems. Each proof is finite, deterministic, and rests only on the frozen Ontology catalog and the tallies of §14 (evidence-decidable, TXP-7).

### `TAX-CLO-1` — Partition closure (Rank 1)

**Theorem.** `{SecuritySubject, SecurityObject}` is an exhaustive, disjoint, rooted partition of the non-abstract constructs of `SecurityConstruct`.

**Proof.** *Exhaustive:* the agency predicate `bears_agency(c)` is total (every construct either can act/hold-authority/be-accountable or cannot). By SECURITY-003 CAT-2, exactly one catalog entity (`Principal`, `ONT-E-02`) satisfies it; the other 31 do not (§14 partition column). Every catalog entity is assigned ⇒ exhaustive. *Disjoint:* `bears_agency` is a predicate, so a construct cannot both satisfy and not satisfy it; dual-role real-world things are modeled as two distinct entities (SECURITY-003 ST-5), so no construct is in both partitions. *Rooted:* both partitions are direct `isA` children of `SecurityConstruct`, and the binary criterion admits no third sibling. ∎

### `TAX-CLO-2` — Object-family closure (Rank 2, Object side)

**Theorem.** The seven object families partition the 31 `SecurityObject` leaves exhaustively and disjointly.

**Proof.** By §14/§11.1 the family membership counts are AccessObject 9, RelationObject 3, AuthorityObject 1, ProtectionObject 4, RiskObject 3, AssuranceObject 5, PropertyObject 6. Their sum is 9+3+1+4+3+5+6 = **31** = |`SecurityObject` leaves|. Each leaf appears under exactly one family in the frozen Ontology inheritance hierarchy (SECURITY-003 §45.1). A partition whose block sizes sum to the whole with each element in exactly one block is exhaustive and disjoint. ∎

### `TAX-CLO-3` — Catalog closure (Rank 3)

**Theorem.** The 32 leaves (`TAX-L-01…32`) are exactly the Ontology catalog (`ONT-E-01…32`), no more and no fewer.

**Proof.** §14 exhibits a bijection `TAX-L-nn ↔ ONT-E-nn` for n = 1…32 (LR-1). Partition tally: Subject 1 + Object 31 = 32 (LR-2). Family tally sums to 31 objects (`TAX-CLO-2`) + 1 subject = 32. Both tallies agree with |catalog| = 32 (SECURITY-003 §11). Hence the leaf set equals the catalog. ∎

### `TAX-CLO-4` — Sub-kind closure (Rank 4)

**Theorem.** The `Principal` archetypes `{Human, Service, Device, Composite}` and the `Control` kinds `{Preventive, Detective, Corrective}` are each exhaustive, disjoint, and non-minting refinements of their single parent leaf.

**Proof.** *Archetypes:* §10.2 AC-1 (exhaustive over agency-nature; `CompositePrincipal` absorbs aggregates), AC-2 (single-valued `archetype`), AC-3 (no-mintage). *Control kinds:* §13.1 CC-1 (exhaustive over the before/during/after threat-event lifecycle), CC-2 (single-valued `controlKind`), CC-3 (no-mintage). Both are Rank-4 sub-kinds (RK-5), adding no entity. ∎

### `TAX-CLO-5` — Coverage closure (CAT-1)

**Theorem.** The leaf taxonomy is a bijective, gap-free, orphan-free cover of the constitutional + ontological concept space.

**Proof.** §15.1 maps the 25 SECURITY-001 §7 concepts to 25 distinct leaves; §15.2 maps `Role`,`Vulnerability` to 2 leaves; §15.3 maps the 5 §8 supporting entities to 5 leaves; 25+2+5 = 32 sources ↔ 32 leaves (§15.4). Completeness (no gap): every source has a leaf. Rootedness (no orphan): every leaf has a source. Hence the cover is a bijection. ∎

### `TAX-CLO-6` — Classifier closure

**Theorem.** `classify` (§16) is total, deterministic, single-valued, and surjective onto the 32 leaves over well-formed catalog constructs.

**Proof.** *Total & default-deny:* every branch returns a leaf or `reject` (CF-1/CF-5). *Deterministic:* every test reads immutable evidenced attributes (CF-2; ONT-INV-8). *Single-valued:* first step unique by `TAX-CLO-1`; family unique by `TAX-CLO-2`; leaf unique by canonical `type` (SECURITY-003 EX-2); sub-kind unique by single-valued attribute (`TAX-CLO-4`). *Surjective:* by `TAX-CLO-3/5` every leaf is the image of its catalog entity. ∎

### Closure summary

| Theorem | Closes (SECURITY-003 deferral) | Result |
|---------|-------------------------------|--------|
| `TAX-CLO-1` | PR-1/PR-2/PR-3 (§8.2) | Rank-1 partition closed |
| `TAX-CLO-2` | §12 family-closure | Rank-2 object families closed |
| `TAX-CLO-3` | catalog completeness (§11) | Rank-3 leaves = catalog |
| `TAX-CLO-4` | ST-4 (§13) + Control kinds (§27) | Rank-4 sub-kinds closed |
| `TAX-CLO-5` | CAT-1 (§11) | Constitutional coverage closed |
| `TAX-CLO-6` | classification decidability | Classifier total/unique |

**All closure obligations SECURITY-003 deferred to SECURITY-004 are discharged.**

---

## SECTION 19 — TAXONOMY ↔ ONTOLOGY CONSISTENCY

The taxonomy is **consistent with, and additive-free over,** the Ontology. This section fixes the exact correspondences and proves no drift.

| Ontology construct (SECURITY-003) | Taxonomy treatment (SECURITY-004) | Consistency rule |
|-----------------------------------|-----------------------------------|------------------|
| Entity catalog `ONT-E-01…32` (§11) | Leaves `TAX-L-01…32` (§14), 1:1 bijection | `TC-1` — no entity added/removed/renamed |
| Root & partitions `SecurityConstruct`/`SecuritySubject`/`SecurityObject` (§8) | Rank-0/Rank-1 taxa (§9), verbatim | `TC-2` — reused, not redefined |
| Seven object families (§12/§45.1) | Rank-2 object families (§11), verbatim | `TC-3` — family assignments match §45.1 exactly |
| `Principal` archetypes (§13 ST-4) | Rank-4 sub-kinds (§10), verbatim | `TC-4` — same four, no addition |
| `Control` kinds (§27) | Rank-4 sub-kinds (§13), verbatim | `TC-5` — same three, no addition |
| Inheritance model `isA`/`R-01` (§45) | Classification edges, single-parent restriction | `TC-6` — tree ⊆ Ontology DAG (no new edge) |
| Master invariants `ONT-INV-1…16` (§50.2) | Specialized by `TAX-INV-1…12` (§17) | `TC-7` — each `TAX-INV` refines ≥1 `ONT-INV`; none amended |
| Existence rules `EX-1…9` (§52) | Well-formedness precondition of `classify` (§16) | `TC-8` — reused as classifier guard |

**Consistency rules:**
- **TC-9 No new semantics.** The taxonomy adds no attribute (`A-*`), relationship (`R-*`), cardinality (`CR-*`), or invariant (`ONT-INV-*`) to the Ontology; it classifies the entities the Ontology fixed (TXP-2).
- **TC-10 Family fidelity.** Where SECURITY-003 §11 (looser concept-family column) and §45.1 (formal seven-family hierarchy) differ in wording, the taxonomy follows **§45.1** (the formal hierarchy), reclassifying no entity (§11.2 note).
- **TC-11 Bidirectional traceability.** Every leaf traces up to its `ONT-E` code and down to its constitutional/ontological source (§15); every Ontology entity traces to exactly one leaf (`TC-1`).
- **TC-12 No conflict.** Where any statement here would conflict with SECURITY-003/002/001, the higher instrument governs and the statement is void to the extent of the conflict (EVR-4 of SECURITY-003).

---

## SECTION 20 — VALIDATION MAPPINGS

The taxonomy is **validatable**: each closure/invariant maps to a decidable check reusing the frozen validation pattern **by reference** (SECURITY-001 §13; SECURITY-003 §33 Compliance; the CERTIFIED EC-1 `ValidationEngine` pattern). The taxonomy defines *what must hold*; it executes no validator (USL-014).

| Validation check (decidable) | Verifies | Maps to |
|------------------------------|----------|---------|
| `VAL-TAX-1` Partition totality | every catalog entity ∈ exactly one partition | `TAX-CLO-1`; `TAX-INV-3/4` |
| `VAL-TAX-2` Family partition | family membership counts sum to 31; each object leaf in one family | `TAX-CLO-2`; `TAX-INV-4` |
| `VAL-TAX-3` Leaf bijection | `TAX-L-nn ↔ ONT-E-nn` bijection over 32 | `TAX-CLO-3`; `TAX-INV-12` |
| `VAL-TAX-4` Sub-kind closure | archetypes (4) and control kinds (3) exhaustive/disjoint/single-valued | `TAX-CLO-4` |
| `VAL-TAX-5` Coverage completeness | 25 §7 + 2 refinements + 5 §8 = 32 sources, no gap/orphan | `TAX-CLO-5`; `TAX-INV-9` |
| `VAL-TAX-6` Classifier totality | `classify` total, deterministic, single-valued, default-deny | `TAX-CLO-6`; `TAX-INV-5/6/7` |
| `VAL-TAX-7` Single-parent tree | every taxon has exactly one parent; acyclic | `TAX-INV-2` |
| `VAL-TAX-8` No-mintage | no entity/identifier/lifecycle introduced | `TAX-INV-10`; USL-015 |

- **VM-1 Decidable.** Each check is total and decidable from the frozen catalog and §14 tallies (evidence-first, USL-012).
- **VM-2 Reference-only.** Validation reuses the EC-1 `ValidationEngine`/`default checks` pattern by reference; the taxonomy adds no validator (USL-002/014).
- **VM-3 Default-deny.** Any failed check ⇒ the classification is treated as invalid (deny), not silently accepted (USL-005).

---

## SECTION 21 — CERTIFICATION MAPPINGS

Certification of the taxonomy **aggregates** the validation evidence deterministically — it does not re-judge (SECURITY-003 §33 CM-INV-1; ER-7) — reusing the CCE ten-gate + INFRASTRUCTURE-001 §12 + the CERTIFIED EC-1 `CertificationEngine` (`certify_validation`) pattern **by reference**.

| Certification gate (by reference) | Aggregates | Basis |
|-----------------------------------|------------|-------|
| `CERT-TAX-1` Closure certification | `VAL-TAX-1…5` PASS ⇒ taxonomy structurally closed | `TAX-CLO-1…5` |
| `CERT-TAX-2` Classifier certification | `VAL-TAX-6` PASS ⇒ classification decidable/unique | `TAX-CLO-6` |
| `CERT-TAX-3` Consistency certification | Ontology consistency (`TC-1…12`) holds; no drift | §19 |
| `CERT-TAX-4` Coverage certification | constitutional coverage complete (CAT-1) | §15 |
| `CERT-TAX-5` Traceability certification | every leaf closes a No-Orphan lineage to SECURITY-001 | `TAX-INV-1`; USL-011 |
| `CERT-TAX-6` Non-mintage certification | no primitive/authority/registry/identifier/lifecycle minted; secret-free | `TAX-INV-10`; USL-013/015 |
| `CERT-TAX-7` Determinism certification | classification/verdicts re-derive byte-identically | `TAX-INV-6`; ONT-INV-8 |

- **CM-1 Aggregation-not-rejudgement.** Certification aggregates the §20 evidence; it re-computes no verdict (ER-7; CM-INV-1).
- **CM-2 Scope-closure, not evolution.** Certification closes the scope of this artifact; it does not close the domain's infinite evolution (CM-INV-2; AUTH-INF-001).
- **CM-3 Traceable & deterministic.** Every certification verdict closes a No-Orphan lineage and re-derives deterministically (CM-INV-3/4; USL-011/012).
- **CM-4 Non-constitutive.** Certification here is **engineering-readiness only** and confers no EC-level constitutional finality or authority (ID-01; AUTH-06).

---

## SECTION 22 — ACCEPTANCE MAPPINGS

Acceptance maps the taxonomy to the universal acceptance-gate suite **by reference** (the CERTIFIED EC-1 `AcceptanceEngine` + universal gate suite; SECURITY-001 §13/§14). Acceptance is the go/no-go over certified evidence; it introduces no new gate.

| Acceptance gate (by reference) | Accepts iff | Basis |
|--------------------------------|-------------|-------|
| `ACC-TAX-1` Completeness gate | all closures (`TAX-CLO-1…6`) certified | §18; `CERT-TAX-1/2` |
| `ACC-TAX-2` Coverage gate | CAT-1 coverage certified (no gap/orphan) | §15; `CERT-TAX-4` |
| `ACC-TAX-3` Consistency gate | Ontology consistency certified (`TC-1…12`) | §19; `CERT-TAX-3` |
| `ACC-TAX-4` Traceability gate | No-Orphan lineage certified for every leaf + the artifact | `CERT-TAX-5`; USL-011 |
| `ACC-TAX-5` Neutrality gate | implementation/technology/vendor/cloud/platform-neutral | TDP-10; §5 |
| `ACC-TAX-6` Non-duplication gate | no lower-layer construct re-owned; no entity minted | `TAX-INV-10`; §6; USL-002/015 |
| `ACC-TAX-7` STATUS-001 gate | R1–R5 conformance (self-check below) | STATUS-001 |

- **AM-1 Evidence-gated.** Each gate accepts only on certified evidence (§21); absent evidence ⇒ no-go (default-deny, USL-005).
- **AM-2 Deterministic go/no-go.** Identical evidence yields identical acceptance verdict (ONT-INV-8).
- **AM-3 Non-constitutive.** Acceptance records engineering readiness only; it confers no constitutional finality (ID-01; AUTH-06).

---

## SECTION 23 — DEPENDENCY MODEL

The taxonomy's dependencies are **strictly downward-only, by reference** (USL-001/002; SECURITY-003 §56). All dependency edges are founding associations forming a DAG (ONT-INV-4).

### 23.1 Canonical dependency stack (downward-only)

```
Existence (EL-1) → Reality/Behavior (RL-F2) → Platform (PL-F2) → Data (DF-2)
   → Service (SF-2) → Application (AF-3) → Infrastructure (Band-13, IF-3)
   → SECURITY foundation:  SECURITY-GOV-000 → SECURITY-001 → SECURITY-002 → SECURITY-003 → **SECURITY-004 (this taxonomy)**
   → [SECURITY-005 (Meta-Model) · concern architectures · Implementation (PHASE-009) : downstream, non-binding forward references]
```

### 23.2 Relationship to each dependency (reference-only; redefines none)

| Dependency | The taxonomy's downward relationship |
|------------|--------------------------------------|
| **SECURITY-003 (Ontology)** | Founds directly: classifies its catalog, proves its deferred closures, specializes its invariants. **Consumed by reference; redefines nothing.** |
| **SECURITY-002 / SECURITY-001** | Instantiates the theory's constructs and the constitution's §7 concepts as classified leaves; adds/amends no law/theorem. |
| **SECURITY-GOV-000** | Authorized by OUTPUT 13 roadmap (SL-3 slot). |
| **Existence (EL-1)** | Roots the tree at `SecurityConstruct ⊑ ENG-002::Object`; references ENG-001/003/004/005. Redefined never. |
| **RL-F2 / PL-F2 / DF-2 / SF-2 / AF-3** | References only as the referents of already-classified entities; owns no runtime/platform/data/service/application construct. |
| **Infrastructure (Band-13, U01–U10)** | References U05 (isolation), U07 (availability), U08 (security facet) as referents of `IsolationDomain`/`Availability`/`Control`; re-owns none. |
| **SECURITY-005 (Meta-Model)** | **Feeds** it the closed leaf set + classification procedure; does not fix well-formedness/instantiation. **Non-binding forward reference.** |
| **Implementation / Operations / Governance** | Downstream; consume the classification by reference. **Non-binding forward references.** |

### 23.3 Dependency rules

- **DEP-1 Downward-only.** References only frozen layers beneath it and intra-domain predecessors (SECURITY-GOV-000…003). No upward/forward founding dependency.
- **DEP-2 Reuse-by-reference.** Every referenced construct is consumed by reference; nothing re-implemented/re-owned/duplicated (USL-002).
- **DEP-3 Acyclic.** The founding/dependency graph is a DAG (ONT-INV-4; DP-4).
- **DEP-4 Frozen-input immutability.** All referenced lower layers (and SECURITY-001…003) are immutable inputs; the taxonomy neither modifies nor reinterprets any of them.
- **DEP-5 Non-binding forward references.** References to SECURITY-005 / Implementation / Operations are non-binding.

---

## SECTION 24 — TAXONOMY EVOLUTION RULES

The taxonomy evolves under strict non-constitutive discipline (USL-015; AUTH-INF-001; UCI-001; SECURITY-003 §57 EVR-1…8; `TAX-INV-10`).

| Rule | Statement |
|------|-----------|
| **TEV-1 Append-only** | New leaves (`TAX-L-33…`), sub-kinds, families, invariants (`TAX-INV-13…`), and checks are **added** as the Ontology admits new entities; existing taxa/codes are never renumbered or rewritten. |
| **TEV-2 Ontology-driven** | The taxonomy classifies **only** entities the Ontology has fixed; a new leaf is admitted **iff** SECURITY-003 (or its append-only successor) first admits the entity (`ONT-E-33…`). The taxonomy never mints a taxon ahead of the Ontology (TXP-2). |
| **TEV-3 Closure-preserving** | Every addition re-proves exhaustiveness/disjointness/coverage for the affected rank before admission (§18); a new leaf must fit exactly one family (or its addition, with its own family-closure). |
| **TEV-4 Backward traceability mandatory** | Every addition/supersession records a backward lineage to what it extends/supersedes, closing to SECURITY-001 (USL-011). |
| **TEV-5 No constitutional/ontological mutation** | Subordinate to SECURITY-001/002/003; may never contradict a USL, theorem, or ontology invariant; conflicts resolve to the higher instrument (TC-12). |
| **TEV-6 Non-constitutive** | Evolution mints no primitive/authority/registry/identifier/lifecycle and embeds no secret (USL-013/015). |
| **TEV-7 Non-terminal & unbounded** | Per AUTH-INF-001 the taxonomy is never TERMINAL; leaf/sub-kind numbering is sequence, not ceiling. |
| **TEV-8 Deterministic re-derivation** | Every superseding version re-derives its closures/classification deterministically from the immutable catalog (ONT-INV-8). |

---

## SECTION 25 — READINESS ASSESSMENT

| Gate | Result |
|------|--------|
| Founded downward-only on frozen substrate (SECURITY-003/002/001 + full stack + Infrastructure Baseline `2dee20b`; HEAD `081ecb0`) | ✅ |
| Purpose · overview · foundational principles (`TXP-1…10`) · scope · boundaries · design principles (`TDP-1…10`) defined | ✅ |
| Canonical ranks (Root → Partition → Family → Class/Leaf → Sub-kind) + rank rules (`RK-1…5`) fixed | ✅ |
| Partition closure (`PC-1/2/3`, closes PR-1/2/3) proven | ✅ |
| Subject-archetype closure (`AC-1/2/3`, closes ST-4) proven | ✅ |
| Object-family closure (`FC-1…4`, closes §12) proven | ✅ |
| Control sub-kind closure (`CC-1/2/3`) proven | ✅ |
| Per-family leaf taxonomy (all 32 leaves assigned; §12) fixed | ✅ |
| Complete canonical leaf register (`TAX-L-01…32`, bijection to `ONT-E-01…32`) fixed | ✅ |
| Coverage closure (CAT-1): 25 §7 + `Role` + `Vulnerability` + 5 §8 supporting = 32 sources ↔ 32 leaves | ✅ |
| Canonical classification function (`classify`, total/deterministic/default-deny) + properties (`CF-1…6`) fixed | ✅ |
| Taxonomic invariants (`TAX-INV-1…12`) + closure theorems (`TAX-CLO-1…6`) fixed & proven | ✅ |
| Taxonomy ↔ Ontology consistency (`TC-1…12`; no new semantics; §45.1 fidelity) fixed | ✅ |
| Validation (`VAL-TAX-1…8`), Certification (`CERT-TAX-1…7`), Acceptance (`ACC-TAX-1…7`) mappings fixed by reference | ✅ |
| Dependency model (downward-only; DAG; reference-only) + rules (`DEP-1…5`) fixed | ✅ |
| Evolution rules (`TEV-1…8`; append-only, ontology-driven, closure-preserving) fixed | ✅ |
| Implementation-independent · technology/vendor/algorithm/cloud/platform-neutral | ✅ |
| No duplication of any lower layer (reuse-by-reference only); mints no entity/primitive/authority/registry/identifier/lifecycle | ✅ |
| Feeds but does not pre-empt SECURITY-005 (Meta-Model) | ✅ |
| REG-AUTO-001 registration (`UCOS-SEC-000005`) allocated & synchronized on creation | ✅ |
| STATUS-001 R1–R5 conformance | ✅ (self-check below) |

---

## SECTION 26 — FINAL DETERMINATION

The Universal Security Taxonomy is complete, coherent, implementation-independent, technology-neutral, founded downward-only by reference on SECURITY-003/SECURITY-002/SECURITY-001 and the frozen substrate, non-duplicating, and STATUS-001-conformant. It fixes the canonical classification of the SECURITY domain: the five taxonomic ranks, the root/partition/family/leaf/sub-kind taxa (reused verbatim from the Ontology catalog), the complete leaf register (`TAX-L-01…32` bijective to `ONT-E-01…32`), the total deterministic classification function, the taxonomic invariants (`TAX-INV-1…12`), and — decisively — the **closure theorems** (`TAX-CLO-1…6`) that **discharge every closure SECURITY-003 deferred**: partition (PR-1/2/3), object-family (§12), subject-archetype (ST-4), control-kind, and constitutional coverage (CAT-1). It instantiates SECURITY-001 §7 and the Ontology without amending either, mints no entity, and defers meta-model well-formedness/instantiation to SECURITY-005.

> ## SECURITY-004 — UNIVERSAL SECURITY TAXONOMY — **RATIFIED**
> (roadmap-governance ratification; authoritative classification scheme + closure for every future `SECURITY-*` artifact; subordinate to SECURITY-003, SECURITY-002, SECURITY-001, the frozen corpus, and AUTH-INF-001; non-constitutive at the EC level.)

**Roadmap progress:** SECURITY 4 (SECURITY-004 of the authorized foundation chain 001…005). **Next artifact:** SECURITY-005 (Universal Security Meta-Model).

---

## SECTION 27 — IMPLEMENTATION NOTES

These notes are **non-normative**; they record the assembly, normalization, and registration provenance of this artifact and bind nothing (ID-01, AUTH-06).

- **Incremental assembly.** This artifact was assembled under the UCOS Large Artifact Protocol in validated passes (skeleton/metadata → foundation §1–§11 → closure/proofs/mappings §12–§27 → consistency review), each verified between steps, to remain resilient to session interruption. It was then sealed as this single canonical artifact with substantive content preserved verbatim (USL-015).
- **REG-AUTO-001 invariant.** Per the repository's canonical automation, *artifact creation causes registration*: the `PostFileCreate` hook (`.kiro/hooks/auto-register-artifact.json`) fired `00-BOOK/tools/register.sh` on first creation, allocating registry identity **`UCOS-SEC-000005`** and synchronizing the Artifact Registry, Page Registry, Volume Registry, Knowledge-Graph, Control Tower, and Digital Twin. The registration transaction completed atomically (re-entrancy lock released). Because the hook fires on creation, the register was re-run after content completion to synchronize the final page count (idempotent, append-only).
- **Metadata-driven registration.** Registration is driven by the artifact's self-declared front-matter (`PROGRAM = SECURITY`, `CATEGORY = SEC`, `VOLUME = VOL-023`, `FAMILY = SECURITY-FOUNDATION`); no generator hard-coding is required (AUTH-INF-001 infinite expansion; REG-AUTO-001 metadata classification).
- **Working-tree provenance.** SECURITY-004 founds solely on the committed/frozen substrate (HEAD `081ecb0`; Infrastructure Baseline `2dee20b`). Unrelated uncommitted work in other domains present at authoring time (engine/platform/intelligence/repository-operations/cert-004) is not a dependency of, and does not affect, this artifact (§1 working-tree note).
- **No runtime behavior.** This artifact introduces no code, no runtime, no enforcement, and selects no technology/algorithm/vendor. Every enforcement reference is delegated by reference to already-frozen, certified lower-layer mechanisms (USL-014).
- **No new taxonomy beyond the catalog.** Every taxon is an Ontology class; the taxonomy proves properties of the Ontology's structure and fixes a classification procedure — it adds no entity (TXP-2; `TAX-INV-10`).

---

## STATUS-001 VALIDATION SELF-CHECK (§5, R1–R5)

| Rule | Result | Evidence |
|------|--------|----------|
| **R1 Declaration** | ✅ | STATUS DOMAIN (ROADMAP EXECUTION — FOUNDATION) + BASIS declared at head. |
| **R2 Domain isolation** | ✅ | Taxonomy-only; no operational/enforcement/technology projection; lower layers and SECURITY-001…003 consumed as immutable inputs by reference. |
| **R3 Claim completeness** | ✅ | Claim (SECURITY-004 exists; RATIFIED; 4 of foundation chain 001…005) supplies domain, unit, evidence source, registry basis (SECURITY-003; `UCOS-SEC-000005`), completion basis. |
| **R4 Evidence physicality** | ✅ | Rests on physical SECURITY-003/002/001 + frozen Infrastructure Baseline (`2dee20b`) + committed HEAD (`081ecb0`) + this file; no claim rests on uncommitted work (§1 note). |
| **R5 Append-only** | ✅ | New file in `14-SECURITY/`; no constitution, frozen artifact, Band-13/Infrastructure artifact, prior SECURITY artifact, or numbering modified; REG-AUTO-001 append-only registration (`UCOS-SEC-000005`); supersession-only evolution (UCI-001; AUTH-INF-001). |

**SECURITY-004 — UNIVERSAL SECURITY TAXONOMY — RATIFIED · ACTIVE; AUTHORITATIVE CLASSIFICATION & CLOSURE FOR SECURITY-*; NEXT ARTIFACT: SECURITY-005 (UNIVERSAL SECURITY META-MODEL).**
