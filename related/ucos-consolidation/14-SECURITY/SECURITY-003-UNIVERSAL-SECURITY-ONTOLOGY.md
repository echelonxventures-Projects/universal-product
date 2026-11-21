# UCOS Ω∞ — UNIVERSAL SECURITY ONTOLOGY

> **STATUS DOMAIN:** ROADMAP EXECUTION (FOUNDATION)
> **STATUS BASIS:** SECURITY-002 (Universal Security Theory — RATIFIED) + SECURITY-001 (Universal Security Constitution — RATIFIED; USL-001…015) + SECURITY-GOV-000 (PHASE-008 ESTABLISHED · ACTIVE) + EC3 Band-13 CLOSED (Infrastructure Baseline frozen `2dee20b`) + AUTH-INF-001 + STATUS-001 + REG-AUTO-001 + UCI-001
> **DOCUMENT PROVENANCE:** Assembled incrementally (append-only) under the UCOS Large Artifact Protocol, then normalized into this single canonical artifact — substantive content preserved verbatim, transient inter-part scaffolding removed (USL-015). See §60 Implementation Notes. Sections §10, §18, §26, §34, §42, §51 are retained as historical assembly checkpoints; the authoritative status is §59 Final Determination.

| Field | Value |
|-------|-------|
| ARTIFACT ID | SECURITY-003 |
| ARTIFACT | Universal Security Ontology |
| PROGRAM | SECURITY |
| CATEGORY | SEC |
| VOLUME | VOL-023 |
| FAMILY | SECURITY-FOUNDATION |
| PACKAGE | Security Foundation Package |
| CLASSIFICATION | Foundational Security Artifact — Implementation-Independent Ontology (fixes the canonical semantic universe of the SECURITY domain; no implementation, no technology, no runtime, no enforcement) |
| STATUS | RATIFIED · ACTIVE |
| PROGRAM POSITION | Third security roadmap artifact (SECURITY-003, SL-2); continues the SECURITY foundation chain 001…005 |
| PREDECESSOR | SECURITY-002 (Universal Security Theory) |
| DEPENDS ON | SECURITY-002; SECURITY-001; SECURITY-GOV-000; Infrastructure Baseline (INFRASTRUCTURE-001…018; EC3-B13-U01…U10) frozen; ENG-000; ENG-001…005 (EL-1); RUNTIME-GOV-003 (RL-F2); PLATFORM-017 (PL-F2, incl. platform/security); DATA-017 (DF-2); SERVICE-017 (SF-2); APPLICATION-018 (AF-3, incl. APPLICATION-013 Security); STATUS-001; AUTH-INF-001; REG-AUTO-001; UCI-001 |
| SECURITY LAYER | SL-2 (Security Ontology) |
| AUTHORIZATION BASIS | SECURITY-GOV-000 (OUTPUT 13 roadmap authorization) + SECURITY-001 §20 (evolution) + SECURITY-002 §26 |
| CONSTITUENT AUTHORITY | NONE |
| GOVERNANCE AUTHORITY | NONE |
| RATIFICATION AUTHORITY | NONE |
| EC-1 AUTHORITY | NONE |
| BRANCH | governance-reconciliation |
| IMPLEMENTATION ANCHOR | `1951c72` (SECURITY-002 committed; Infrastructure Baseline frozen) |
| BASELINE DATE | 2026-07-21 |

*This artifact fixes the **canonical semantic universe** of the UCOS Ω∞ Universal Security Domain: the authoritative vocabulary, entity model, relationship model, attribute model, and semantic constraints that every future `SECURITY-*` artifact SHALL instantiate and conform to. It **operationalizes SECURITY-001 §7 (Ontology) and SECURITY-002 (Theory)** into a normatively-fixed ontology. It contains **no implementation, no runtime, no enforcement logic, and no technology/algorithm/vendor/cloud/platform selection**. It **consumes all lower architectural layers strictly by reference** (EL-1→AF-3 + the frozen Infrastructure Baseline) and **duplicates nothing** — it re-owns, re-implements, and redefines no lower construct, and it mints no new primitive, authority, registry system, identifier scheme, or lifecycle (USL-015). Subordinate to SECURITY-002, SECURITY-001, the frozen corpus, and AUTH-INF-001; where any statement herein would conflict with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict. Every conclusion recorded here is a **technical, non-constitutive** governance record (ID-01, AUTH-06).*

---

## SECTION 1 — REPOSITORY VERIFICATION

This ontology is founded on a verified, physically-present substrate. The following state was confirmed prior to authoring, and no prerequisite is assumed:

| Check | Requirement | Result |
|-------|-------------|--------|
| Branch | `governance-reconciliation` | ✅ confirmed |
| HEAD | `1951c72` (SECURITY-002 committed) | ✅ confirmed |
| Working tree | CLEAN (no uncommitted changes) | ✅ confirmed |
| `verify.sh` | PASS (ruff lint · pytest + coverage `--cov-fail-under=90` · coverage report · governance enforce --pre) | ✅ PASS |
| `register.sh --guard` | PASS (registration transaction 10/10 phases; drift gate clean) | ✅ PASS |
| Registry / Portal / Control Tower / Digital Twin | synchronized (969 artifacts; certification 10/10 integrity domains) | ✅ synchronized |
| SECURITY-001 (Universal Security Constitution) | RATIFIED · ACTIVE | ✅ RATIFIED |
| SECURITY-002 (Universal Security Theory) | RATIFIED · ACTIVE | ✅ RATIFIED |
| Infrastructure Baseline (EC3 Band-13, U01–U10; IF-3) | PROVISIONALLY RATIFIED & FROZEN (`2dee20b`) | ✅ frozen |

**Verification verdict:** every prerequisite for authoring SECURITY-003 is satisfied on physical evidence (STATUS-001 R4). The predecessor chain SECURITY-GOV-000 → SECURITY-001 → SECURITY-002 is complete and RATIFIED, and SECURITY-002 §28 names SECURITY-003 (Universal Security Ontology) as the next authorized artifact.

---

## SECTION 2 — PURPOSE

The Universal Security Ontology fixes, **once and canonically**, the semantic universe of the UCOS Security Domain: *what security things exist, what they are, what attributes they bear, how they relate, and what must always hold of them*. Where SECURITY-001 fixed the constitutional laws (USL-001…015) and SECURITY-002 furnished the theoretical model, SECURITY-003 supplies the **authoritative vocabulary and formal entity model** upon which SECURITY-004 (Taxonomy), SECURITY-005 (Meta-Model), and every downstream concern architecture are built.

Its purposes are:

1. **Authoritative vocabulary.** To name — exactly once, unambiguously, and technology-neutrally — every canonical security concept, so that all `SECURITY-*` artifacts share a single, decidable semantic reference.
2. **Entity model.** To define each canonical security **entity** as a typed (ENG-004), identified (ENG-001) specialization of the frozen `ENG-002::Object` (USL-003), with its canonical attributes and constraints.
3. **Relationship model.** To define the canonical **relationships** among security entities as ENG-005 references (USL-002), with cardinality, direction, and acyclicity fixed.
4. **Semantic constraints.** To fix the invariants, cardinalities, existence rules, authority rules, trust rules, and evidence rules that every conforming security construct SHALL satisfy.
5. **Downward binding.** To define the ontology's relationship to every lower architectural layer strictly by **downward-only reference**, redefining none.

The ontology remains **implementation-independent**, **technology-neutral**, and **assurance-not-enforcement** (USL-014): it *describes and constrains* the meaning of security constructs; it never executes, selects technology, or enforces.

---

## SECTION 3 — ONTOLOGY OVERVIEW

The Universal Security Ontology is a **single, connected, acyclic semantic graph** whose nodes are canonical security **entities** and whose edges are canonical **relationships**, all rooted in the frozen existence layer (EL-1) and closing a No-Orphan lineage to SECURITY-001 (USL-011).

**Structural summary (fixed in full across the assembled parts):**

- **One root abstract entity** — `SecurityConstruct` — a specialization of the frozen `ENG-002::Object`. Every security entity ⊑ `SecurityConstruct`; no security entity exists outside this root (existence rule).
- **Two top partitions of things** — every `SecurityConstruct` is either a **Security Subject** (an actor/bearer capable of acting or being held accountable) or a **Security Object** (a resource, artifact, relation, or assurance record acted upon or produced). These partitions are elaborated in SECTIONS 8, and (in later parts) in the Object-Types and Subject-Types ontologies.
- **The canonical concept families** (elaborated one-ontology-per-section in later parts): Identity · Principal · Authority · Trust · Authentication · Authorization · Policy · Permission · Privilege · Role · Delegation · Control · Threat · Risk · Vulnerability · Evidence · Audit · Compliance · Attestation · Isolation · Boundary · Integrity · Confidentiality · Availability · Recovery.
- **All relationships are ENG-005 references** (USL-002); no new connection primitive is introduced. Founding relationships (`dependsOn`, isolation containment, `derivesFrom`) are **downward-only and acyclic**; evaluative relationships (`authorizes`, `authenticates`, `trusts`, `mitigates`, `attests`, `evaluates`) are **non-mutating**.
- **Every entity is evidence-bearing** (USL-010/012) and **traceable** (USL-011); every verdict-producing entity is **deterministic** and **default-deny** (USL-005/012).

**Relationship to the constitutional ontology.** SECURITY-001 §7 enumerated 25 canonical concepts as constitutional meanings; SECURITY-003 **fixes them normatively** as entities with attributes, relationships, and constraints, and admits the two additional ontological refinements the constitution deferred to this layer — **Role** (an aggregation of permissions, framed in SECURITY-001 §5/§9 under RBAC/ABAC) and **Vulnerability** (a weakness concept within the Threat/Risk sub-theory, SECURITY-002 §11–§12). Neither is a new primitive, authority, registry, identifier, or lifecycle (USL-015); each is a typed specialization of an existing construct.

**Structural note.** This document fixes the **foundation** (repository verification, purpose, overview, foundational principles, scope, boundaries, design principles, the root entity model, and the root relationships) before elaborating the per-concern ontologies and the consolidated attribute/constraint/invariant/dependency/evolution models, closing with the final determination.

---

## SECTION 4 — FOUNDATIONAL PRINCIPLES

The ontology inherits and instantiates — it does not restate or amend — the foundational principles of SECURITY-001 §5 and the theoretical pillars of SECURITY-002 §2. The following principles govern the **ontological layer specifically** and bind every entity, attribute, relationship, and constraint defined in this document and its later parts:

| # | Ontological Principle | Basis |
|---|-----------------------|-------|
| **FP-1 Objecthood** | Every security entity IS a typed (ENG-004), identified (ENG-001) `ENG-002::Object` with deterministic value fidelity (ENG-003). The ontology introduces no parallel thing-model. | USL-003; USA-1; SECURITY-002 T-Id-1 |
| **FP-2 Single Root** | Every security entity is a specialization of the single abstract root `SecurityConstruct ⊑ ENG-002::Object`. Nothing security-relevant exists outside the root. | SECURITY-001 §9 |
| **FP-3 Reference-Only Relations** | Every relationship is an ENG-005 reference; the ontology mints no connection construct. | USL-002/USL-015 |
| **FP-4 Downward-Only Founding** | Founding relations (`dependsOn`, containment, `derivesFrom`) are downward-only and acyclic; no upward, forward, or cyclic founding relation may exist. | USL-001/USL-011; SECURITY-002 INV-6 |
| **FP-5 Evidence-Bearing** | Every entity that participates in a security decision or property carries immutable, attributable, deterministic evidence; absence of evidence is absence of the property (default-deny). | USL-010/012/005; SECURITY-002 T-Ev-1/T-Ev-4 |
| **FP-6 Authority Non-Mintage** | No entity mints authority; authority is a referenced capacity resolved from frozen lower layers and explicit policy, and never embeds secret/credential/key material. | USL-013; SECURITY-002 T-Auth-1 |
| **FP-7 Assurance, Not Enforcement** | Every entity is descriptive/evaluative/attesting at this layer; the ontology names what enforcement *means* and delegates all enforcement by reference to frozen lower mechanisms. | USL-014; SECURITY-002 INV-7 |
| **FP-8 Determinism** | Every classification, membership, and constraint decision over the ontology is total and deterministic — identical inputs yield identical verdicts. | USL-012; SECURITY-002 INV-5 |
| **FP-9 Traceability Closure** | Every entity closes a backward No-Orphan lineage to SECURITY-001 and to the frozen anchors; no orphan entity may exist. | USL-011; SECURITY-002 INV-9 |
| **FP-10 Non-Constitutive Evolution** | The ontology grows append-only / supersession-only with mandatory backward traceability; it mints no new primitive/authority/registry/identifier/lifecycle and mutates no constitution. | USL-015; AUTH-INF-001 |

These ten ontological principles are **complete over the concerns of this layer** (objecthood, rooting, relations, founding, evidence, authority, enforcement-boundary, determinism, traceability, evolution) and non-overlapping in obligation. Any future ontological principle is admitted **additively** (FP-11…), never by rewrite.

---

## SECTION 5 — ONTOLOGY SCOPE

| In scope (this ontology fixes) | Out of scope (by reference or excluded) |
|--------------------------------|------------------------------------------|
| The canonical **vocabulary** of the SECURITY domain — the authoritative name and definition of every security concept | Concrete cryptographic algorithms/suites, key stores/KMS, identity providers, scanners, WAFs, secret managers, vendor products, running systems, code |
| The canonical **entity model** — each security entity as a typed, identified `ENG-002::Object` specialization, with its canonical attributes | Execution/state/policy **runtime** (RL-F2); platform security service (PL-F2 `platform/security`); data representation (DF-2); service operation (SF-2); application security (AF-3 / APPLICATION-013); infrastructure security facet (Band-13 U08 SecurityFacet) — **reused by reference, never redefined** |
| The canonical **relationship model** — inheritance, composition, aggregation, association, and reference relationships, with cardinality, direction, and acyclicity | Any operational/enforcement/ratification/EC-series authority; any secret/credential/key material; any counting of source assets as roadmap completion (STATUS-001 §2) |
| The **semantic constraint model** — cardinality, invariants, existence rules, authority rules, trust rules, evidence rules | The **taxonomy closure** (partition/coverage proof — SECURITY-004) and the **meta-model** (leaf meta-classes, well-formedness rules, instantiation semantics — SECURITY-005), which this ontology *frames* but does not *close* |
| The ontology's **downward-only relationship** to Existence, Reality, Platform, Application, Infrastructure, Implementation, Operations, Governance | Any new primitive, authority, registry system, identifier scheme, or lifecycle (USL-015) |
| The ontology **evolution rules** (append-only, supersession-only, backward traceability) | In-place mutation of any constitution, frozen artifact, or prior part of this document |

The ontology is a **semantic reference**, not a runtime schema: it defines meaning and constraint for architecture, not a persisted data model, wire format, or executable type system.

---

## SECTION 6 — ONTOLOGY BOUNDARIES

The ontology draws explicit, non-overlapping boundaries so that it owns **only** the assurance-domain semantics and re-owns nothing (USL-002; SECURITY-001 §17):

| Boundary | This ontology (SECURITY-003) | The bounded layer / artifact (by reference) |
|----------|------------------------------|---------------------------------------------|
| **Existence boundary** | Names security entities as specializations of `ENG-002::Object`; references identity (ENG-001), value (ENG-003), type (ENG-004), reference (ENG-005). | EL-1 owns objecthood, identity, value, type, reference. **Never redefined.** |
| **Behavior boundary** | Names what authorization/policy/control **mean** and what enforcement **is**. | RL-F2 owns runtime behavior/state/execution; all enforcement is delegated to it **by reference**. |
| **Composition boundary** | References the platform security service and composition constructs as evaluated targets. | PL-F2 (`platform/security`) owns platform composition and the platform security service. **Never re-owned.** |
| **Representation boundary** | Names evidence/audit/attestation **semantics** (immutability, attribution, determinism). | DF-2 owns data representation/serialization. **Never redefined.** |
| **Operation boundary** | Names the assurance concepts operations consume. | SF-2 owns service operation. **Never re-owned.** |
| **Experience boundary** | References the Application Security architecture as an upstream-secured domain. | AF-3 / APPLICATION-013 owns application security architecture. **Referenced, not redefined.** |
| **Realization-environment boundary** | References isolation boundaries, resilience/availability topology, and the infrastructure security facet as evaluated/consumed constructs. | Band-13 U05 (isolation), U07 (availability), U08 (SecurityFacet). **Consumed by reference; never re-owned.** |
| **Meta boundary** | *Frames* leaf meta-classes and instantiation; does **not** fix well-formedness or partition closure. | SECURITY-004 (Taxonomy) closes partition/coverage; SECURITY-005 (Meta-Model) closes well-formedness and instantiation. |

**Boundary rule.** Where a concept already exists in a lower layer, the ontology **names its security-relevant meaning and references the lower construct** — it does not re-implement, re-own, or duplicate it (USL-002). Where a concept is a downstream fixation (taxonomy closure, meta-model well-formedness), the ontology **frames but does not close** it, deferring to SECURITY-004/005.

---

## SECTION 7 — ONTOLOGY DESIGN PRINCIPLES

The ontology is constructed under the following design law, which governs *how* entities, relationships, attributes, and constraints are formed (distinct from the *what-holds* foundational principles of SECTION 4):

| # | Design Principle | Statement |
|---|------------------|-----------|
| **DP-1 Single-Root Specialization** | Every entity is introduced as a specialization (`⊑`) of `SecurityConstruct` (itself `⊑ ENG-002::Object`); no free-floating entity is admitted. |
| **DP-2 Exactly-One-Definition** | Each canonical concept is named and defined **exactly once**; synonyms are recorded as non-canonical aliases pointing to the single canonical entity (no semantic duplication). |
| **DP-3 Typed Reference Relations** | Every relationship is a typed ENG-005 reference with a fixed name, direction, and cardinality; no untyped or implicit relation is admitted (USL-002). |
| **DP-4 Acyclic Founding** | The founding sub-graph (`dependsOn`, containment/composition, `derivesFrom`) is a DAG; any relation that would introduce a cycle or an upward/forward founding edge is prohibited (USL-011; INV-6). |
| **DP-5 Mandatory Core Attributes** | Every entity bears the mandatory core attributes (`id`, `type`, `value`, `scope`, `evidenceRef`, `trustBasis`, `assuranceVerdict`, `nonEnforcing`) unless a later part explicitly and traceably narrows them for a specific entity; attribute sets are additive. |
| **DP-6 Decidable Constraints** | Every constraint (cardinality, invariant, existence, authority, trust, evidence) is decidable from immutable evidence and total (default-deny on ambiguity) (USL-005/012). |
| **DP-7 Reference-Only Downward Binding** | All bindings to lower layers are downward-only references; the ontology redefines, re-owns, or duplicates nothing beneath it (USL-001/002). |
| **DP-8 Assurance Framing** | Every entity is framed as descriptive/evaluative/attesting; where an entity denotes an enforcing mechanism, the ontology names it as a **reference to a frozen lower mechanism**, never as an enforcement primitive owned here (USL-014). |
| **DP-9 Append-Only Assembly** | The ontology is assembled and evolved append-only; new entities/relationships/attributes/constraints are added (never rewritten), and every addition records backward traceability (USL-015). |
| **DP-10 Neutrality** | Every definition is implementation-independent, technology-neutral, vendor-neutral, algorithm-neutral, cloud-neutral, and platform-neutral; no concrete technology is named or implied. |

---

## SECTION 8 — ROOT SECURITY ENTITY MODEL

The ontology is rooted in a single abstract entity and two exhaustive, disjoint partitions.

### 8.1 The root entity

```
ENG-002::Object                       «frozen existence primitive — referenced, never redefined»
   ▲ ⊑
SecurityConstruct  «abstract, root of the SECURITY ontology»
```

**`SecurityConstruct`** — *abstract.* The single root of the Universal Security Ontology. Every security entity, without exception, is a specialization of `SecurityConstruct` (FP-2, DP-1; existence rule). It is itself a specialization of the frozen `ENG-002::Object` (USL-003), and therefore bears — by reference, not by redefinition — an identity (ENG-001), a type (ENG-004), a value with deterministic fidelity (ENG-003), and the capacity to be referenced (ENG-005). `SecurityConstruct` is **never instantiated directly**; only its concrete leaf specializations (fixed across later parts and closed by SECURITY-005) are instantiable.

**Root-level mandatory attributes** (borne by every `SecurityConstruct`, hence by every security entity; detailed in the Attribute Model, later part):

| Attribute | Meaning | Basis |
|-----------|---------|-------|
| `id` | ENG-001 identity of the construct (canonical, stable, distinguishable). | USL-003 |
| `type` | ENG-004 type designation (the leaf entity class). | USL-003 |
| `value` | ENG-003 value with deterministic fidelity. | USL-003 |
| `scope` | The bounded extent within which the construct is meaningful/valid. | USL-007; SECURITY-002 T-Trust-3 |
| `evidenceRef` | Immutable, attributable reference to the evidence substantiating the construct. | USL-010/012 |
| `trustBasis` | The evidenced basis on which the construct may be relied upon (may be ∅ ⇒ distrust). | USL-004; SECURITY-002 T-Trust-2 |
| `assuranceVerdict` | The decidable verdict `{holds, denied, indeterminate→denied}` over the construct's asserted property. | USL-005/012 |
| `nonEnforcing` | Invariant marker: `true` at the architecture layer; enforcement is delegated by reference (USL-014). | USL-014 |
| `lineageRef` | Backward No-Orphan lineage reference closing to SECURITY-001 and the frozen anchors. | USL-011 |

### 8.2 The two root partitions

Every non-abstract `SecurityConstruct` is **exactly one** of the following (exhaustive, disjoint — closure proven in SECURITY-004):

```
SecurityConstruct «abstract»
├── SecuritySubject   «abstract»  — an actor/bearer that can act, hold authority, or be held accountable
└── SecurityObject    «abstract»  — a resource, relation, artifact, or assurance record acted upon or produced
```

**`SecuritySubject`** — *abstract.* A `SecurityConstruct` that can **act, be authorized, hold trust/authority, or be held accountable**. It is the bearer-of-agency side of the ontology. Its canonical leaf families (fixed in the Subject-Types ontology, later part) include `Principal` and its refinements. Every `SecuritySubject` is identifiable and accountable (USA-1; SECURITY-002 T-Id-3).

**`SecurityObject`** — *abstract.* A `SecurityConstruct` that is **acted upon, decided over, produced, or asserted**. It is the acted-upon / produced side of the ontology. Its canonical leaf families (fixed in the Object-Types ontology, later part) include the resources, relations (trust, delegation), decisions (authentication, authorization), governing artifacts (policy, permission, privilege, role, control), risk constructs (threat, risk, vulnerability), assurance records (evidence, audit, attestation, compliance), and protection constructs (isolation, boundary, and the integrity/confidentiality/availability/recovery property constructs).

**Partition rules (fixed here; closure proven in SECURITY-004):**
- **PR-1 Exhaustive.** Every non-abstract security entity is a `SecuritySubject` **or** a `SecurityObject`.
- **PR-2 Disjoint.** No entity is both (a construct is either an agent-bearer or an acted-upon/produced thing; where a real-world thing plays both roles, the ontology models the two roles as two typed references to distinct entities, never one dual-typed entity).
- **PR-3 Rooted.** Both partitions specialize `SecurityConstruct`; neither exists outside the root.

### 8.3 Root entity catalog

| Entity | Kind | Specializes | Instantiable | Fixed in |
|--------|------|-------------|--------------|----------|
| `SecurityConstruct` | abstract root | `ENG-002::Object` (by reference) | No | root (this ontology) |
| `SecuritySubject` | abstract partition | `SecurityConstruct` | No | root (this ontology); leaves in §13 |
| `SecurityObject` | abstract partition | `SecurityConstruct` | No | root (this ontology); leaves in §12 |

*The concrete leaf entities of each partition (Identity, Principal, Authority, Trust, Authentication, Authorization, Policy, Permission, Privilege, Role, Delegation, Control, Threat, Risk, Vulnerability, Evidence, Audit, Compliance, Attestation, Isolation, Boundary, Integrity, Confidentiality, Availability, Recovery) are defined one-ontology-per-section in later parts and their partition-closure is proven in SECURITY-004.*

---

## SECTION 9 — ROOT SECURITY RELATIONSHIPS

All relationships in the ontology are **typed ENG-005 references** (FP-3, DP-3; USL-002); the ontology mints no connection construct. This section fixes the **root relationship kinds** — the abstract relationship categories under which every concrete per-concern relationship (fixed in later parts) is classified. Each kind fixes a direction discipline and a mutation discipline.

### 9.1 The four root relationship kinds

| Kind | Semantics | Direction discipline | Mutation discipline |
|------|-----------|----------------------|---------------------|
| **Inheritance** (`⊑`, *isA*) | Specialization: a sub-entity is a kind of its super-entity, inheriting attributes and constraints. | Directed, **acyclic**, rooted at `SecurityConstruct`. | Non-mutating (structural). |
| **Composition** (*partOf* / *contains*, strong) | A whole is composed of parts whose existence is bounded by the whole (e.g., an `IsolationDomain` contains what it confines). | Directed, **downward-only, acyclic**. | Non-mutating; lifecycle-coupled to the whole. |
| **Aggregation** (*groups* / *collects*, weak) | A collector groups independently-existing members (e.g., a `Role` aggregates `Permission`s; a `ThreatModel` aggregates `Threat`s). | Directed, **acyclic**. | Non-mutating; members exist independently. |
| **Association** (typed reference, evaluative) | A named, non-structural reference expressing a security relation or decision (e.g., `authorizes`, `authenticates`, `trusts`, `mitigates`, `attests`, `evaluates`, `dependsOn`, `delegatesTo`). | Directed; **founding associations** (`dependsOn`, `derivesFrom`, isolation containment) are downward-only & acyclic; **evaluative associations** may reference any layer downward. | **Non-mutating** — an association references its target, never alters it (assurance-not-enforcement, USL-014). |

### 9.2 Root relationship catalog

The following root-level relationships are fixed now; every concrete per-concern relationship in later parts is a specialization of exactly one of these:

| Relationship | Kind | Domain → Range | Cardinality (framed; fixed in Constraint Model) | Discipline |
|--------------|------|----------------|-------------------------------------------------|------------|
| `isA` (`⊑`) | Inheritance | `SecurityConstruct` → `SecurityConstruct` | each entity `⊑` exactly one direct super-entity | acyclic, rooted |
| `dependsOn` | Association (founding) | `SecurityConstruct` → `SecurityConstruct` \| lower-layer construct (by ref) | 0..* | **downward-only, acyclic** |
| `derivesFrom` | Association (founding) | `SecurityObject` → `SecurityObject` | 0..* | downward-only, acyclic |
| `contains` | Composition | `SecurityObject` → `SecurityConstruct` | 0..* (parts bounded by whole) | downward-only, acyclic |
| `groups` | Aggregation | `SecurityObject` → `SecurityConstruct` | 0..* (independent members) | acyclic |
| `evaluates` | Association (evaluative) | `SecurityObject` (assurance) → `SecurityConstruct` | 0..* | **non-mutating** |
| `evidences` | Association (evaluative) | `SecurityConstruct` → `Evidence` | each verdict-bearing construct → 1..* evidence | non-mutating, immutable target |
| `tracesTo` | Association (founding) | `SecurityConstruct` → SECURITY-001 / frozen anchor | each entity → 1 closed lineage | **downward-only, acyclic (No-Orphan)** |

### 9.3 Root relationship rules

- **RR-1 Reference-only.** Every relationship is an ENG-005 reference; no new connection primitive (USL-002/015).
- **RR-2 Typed & named.** Every relationship instance bears a fixed type and name; no untyped/implicit edges (DP-3).
- **RR-3 Acyclic founding.** The union of all founding relationships (`isA`, `dependsOn`, `derivesFrom`, `contains`, `tracesTo`) is a DAG; no cycle, no upward, no forward founding edge (USL-011; INV-6; DP-4).
- **RR-4 Non-mutating evaluation.** Every evaluative association (`evaluates`, `authorizes`, `authenticates`, `trusts`, `mitigates`, `attests`, and their later-part specializations) references its target without altering it (USL-014; INV-7).
- **RR-5 Evidence-linked.** Every relationship expressing a security decision or property links to immutable evidence (`evidences`); absence of evidence ⇒ the relation does not hold (default-deny, USL-005/012).
- **RR-6 Traceability closure.** Every entity bears exactly one `tracesTo` lineage closing to SECURITY-001 and the frozen anchors (No-Orphan, USL-011).
- **RR-7 Downward binding.** Any relationship whose range is a lower-layer construct is a downward-only reference to a frozen construct; it redefines nothing (USL-001/002; DP-7).

*The concrete per-concern relationships (`authenticates`, `authorizes`, `trusts`, `delegatesTo`, `controls`/`mitigates`, `isolates`, `attests`, `assures`, and the property relations for integrity/confidentiality/availability/recovery) are defined with full domain/range/cardinality in later parts and consolidated in the Relationship Model, then constrained in the Constraint Model.*

---

## SECTION 10 — DOCUMENT STATUS (ASSEMBLY CHECKPOINT — historical)

*This section recorded an intermediate assembly checkpoint during incremental authoring. It is retained for provenance only and is superseded by §58 Readiness Assessment and §59 Final Determination. The artifact is RATIFIED (see §59).*



---

## SECTION 11 — FOUNDATIONAL SECURITY ENTITIES

This section fixes the **complete canonical entity catalog** of the SECURITY domain: every concept named in SECURITY-001 §7 (25 constitutional concepts) plus the two ontological refinements the constitution deferred to this layer — `Role` and `Vulnerability` (SECURITY-003 §3). Each is a typed (ENG-004), identified (ENG-001) specialization of `SecurityConstruct` (§8.1), placed in exactly one root partition (§8.2), and assigned a stable **ontology entity code** (`ONT-E-nn`) used for intra-document cross-reference only (not a registry identifier — USL-015).

| Code | Canonical Entity | Partition | Concept family | Constitutional source |
|------|------------------|-----------|----------------|-----------------------|
| `ONT-E-01` | `Identity` | Object | Identity & Access | SECURITY-001 §7 |
| `ONT-E-02` | `Principal` | **Subject** | Identity & Access | SECURITY-001 §7 |
| `ONT-E-03` | `CredentialModel` (secret-free) | Object | Identity & Access | SECURITY-001 §8 |
| `ONT-E-04` | `Authority` | Object | Authority | SECURITY-001 §7 |
| `ONT-E-05` | `Trust` (relation) | Object | Trust | SECURITY-001 §7 |
| `ONT-E-06` | `TrustAnchor` | Object | Trust | SECURITY-001 §8 |
| `ONT-E-07` | `TrustBoundary` | Object | Trust | SECURITY-001 §8 |
| `ONT-E-08` | `Authentication` (decision) | Object | Identity & Access | SECURITY-001 §7 |
| `ONT-E-09` | `Authorization` (decision) | Object | Identity & Access | SECURITY-001 §7 |
| `ONT-E-10` | `Policy` / `AuthorizationPolicy` | Object | Identity & Access | SECURITY-001 §7/§8 |
| `ONT-E-11` | `Permission` | Object | Identity & Access | SECURITY-001 §7 |
| `ONT-E-12` | `Privilege` | Object | Identity & Access | SECURITY-001 §7 |
| `ONT-E-13` | `Role` | Object | Identity & Access | SECURITY-001 §5/§9 (RBAC/ABAC) |
| `ONT-E-14` | `Delegation` | Object | Identity & Access | SECURITY-001 §7 |
| `ONT-E-15` | `Control` (Preventive/Detective/Corrective) | Object | Protection & Control | SECURITY-001 §7/§9 |
| `ONT-E-16` | `Threat` / `ThreatModel` | Object | Threat & Risk | SECURITY-001 §7/§8 |
| `ONT-E-17` | `Risk` / `RiskAssessment` | Object | Threat & Risk | SECURITY-001 §7/§8 |
| `ONT-E-18` | `Vulnerability` | Object | Threat & Risk | SECURITY-002 §11–§12 (weakness) |
| `ONT-E-19` | `Evidence` / `SecurityEvidence` | Object | Assurance & Evidence | SECURITY-001 §7/§8 |
| `ONT-E-20` | `Audit` / `AuditRecord` | Object | Assurance & Evidence | SECURITY-001 §7/§8 |
| `ONT-E-21` | `Compliance` | Object | Assurance & Evidence | SECURITY-001 §7 |
| `ONT-E-22` | `Attestation` | Object | Assurance & Evidence | SECURITY-001 §7/§8 |
| `ONT-E-23` | `Isolation` / `IsolationDomain` | Object | Protection & Control | SECURITY-001 §7/§8 |
| `ONT-E-24` | `Boundary` | Object | Protection & Control | SECURITY-001 §7 |
| `ONT-E-25` | `Integrity` (property) | Object | Security Property | SECURITY-001 §7 |
| `ONT-E-26` | `Confidentiality` (property) | Object | Security Property | SECURITY-001 §7 |
| `ONT-E-27` | `Availability` (property) | Object | Security Property | SECURITY-001 §7 |
| `ONT-E-28` | `Accountability` (property) | Object | Security Property | SECURITY-001 §7 |
| `ONT-E-29` | `NonRepudiation` (property) | Object | Security Property | SECURITY-001 §7 |
| `ONT-E-30` | `Recovery` | Object | Protection & Control | SECURITY-001 §7 |
| `ONT-E-31` | `AssuranceFacet` | Object | Governance | SECURITY-001 §8 |
| `ONT-E-32` | `SecurityGovernanceFacet` | Object | Governance | SECURITY-001 §8 |

**Catalog rules:**
- **CAT-1 Completeness.** The catalog covers every constitutional concept (SECURITY-001 §7) plus the two deferred refinements; coverage/partition **closure** is proven in SECURITY-004 (Taxonomy).
- **CAT-2 Single partition.** Exactly one entity — `Principal` (`ONT-E-02`) — is a `SecuritySubject`; all others are `SecurityObject`s (PR-1/PR-2). Subjecthood is elaborated in §13; the property entities (`ONT-E-25…29`) are Objects denoting asserted-and-evidenced properties, not agents.
- **CAT-3 Codes are non-registry.** `ONT-E-nn` codes are intra-document references only; they mint no identifier scheme (USL-015). Registry identity is the REG-AUTO-001 allocation (`UCOS-SEC-000004`) for the artifact as a whole.
- **CAT-4 Aliases.** Non-canonical synonyms (e.g., "actor" → `Principal`; "entitlement" → `Permission`; "trust relationship" → `Trust`) are recorded as aliases resolving to the single canonical entity (DP-2); they introduce no new entity.

---

## SECTION 12 — SECURITY OBJECT TYPES

`SecurityObject` (§8.2) is partitioned into **seven canonical object families**, each an abstract specialization of `SecurityObject`. Every `SecurityObject` leaf (from §11) belongs to exactly one family (family-closure proven in SECURITY-004).

```
SecurityObject «abstract»
├── AccessObject      «abstract»  — governs/records who may do what
│     Identity · CredentialModel · Authentication · Authorization · Policy · Permission · Privilege · Role · Delegation
├── RelationObject    «abstract»  — an evidenced security relation between constructs
│     Trust · TrustAnchor · TrustBoundary
├── AuthorityObject   «abstract»  — a referenced capacity to decide/permit
│     Authority
├── ProtectionObject  «abstract»  — prevents/contains/restores harm
│     Control · Isolation/IsolationDomain · Boundary · Recovery
├── RiskObject        «abstract»  — models potential/actual weakness & exposure
│     Threat/ThreatModel · Vulnerability · Risk/RiskAssessment
├── AssuranceObject   «abstract»  — substantiates that a property holds
│     Evidence · Audit/AuditRecord · Attestation · Compliance · AssuranceFacet
└── PropertyObject    «abstract»  — a named, asserted-and-evidenced security property
      Integrity · Confidentiality · Availability · Accountability · NonRepudiation · SecurityGovernanceFacet
```

**Object-type semantics:**
- **OT-1** Every `SecurityObject` is **acted upon, decided over, produced, or asserted** — never itself an agent (agency is `SecuritySubject`, §13).
- **OT-2** Every `AccessObject`, `RelationObject`, and `AuthorityObject` is **evidence-bearing** and **default-deny** (absent evidence ⇒ the access/relation/authority does not hold — USL-005/012; §8.1 `assuranceVerdict`).
- **OT-3** Every `AssuranceObject` is **immutable and attributable** (append-only, tamper-evident — USL-010; SECURITY-002 T-Aud-1) and **secret-free** (USL-013; SECURITY-002 T-Ev-3).
- **OT-4** Every `ProtectionObject` that denotes an enforcing mechanism is a **downward reference to a frozen lower mechanism** (`nonEnforcing = true` at this layer — USL-014; DP-8), e.g., `Isolation` references Band-13 U05, `Recovery` references U07 resilience.
- **OT-5** Every `PropertyObject` denotes a property that **holds only insofar as decidable from evidence** (USL-012); it is an assertion-with-evidence, never a runtime guarantee owned here.
- **OT-6** Every `RiskObject` maps to mitigation or accepted residual risk (SECURITY-002 T-Thr-3/T-Rsk-2); no silent unmitigated exposure (default-deny — T-Rsk-3).

---

## SECTION 13 — SECURITY SUBJECT TYPES

`SecuritySubject` (§8.2) is the bearer-of-agency partition. Its single canonical concrete entity is `Principal` (`ONT-E-02`); the ontology refines `Principal` into **subject archetypes** that are *architecture roles of one entity*, not new primitives (USL-015). Each archetype remains a typed `ENG-002::Object` (USL-003) and differs only by the nature of the agency it bears and the credential class (secret-free, `ONT-E-03`) by which it authenticates.

```
SecuritySubject «abstract»
└── Principal  «concrete; ONT-E-02»
      ├── HumanPrincipal        — a natural person acting under an identity
      ├── ServicePrincipal      — a software service/workload acting autonomously
      ├── DevicePrincipal       — a device/node acting under an attested identity
      └── CompositePrincipal    — a bounded aggregate acting as one (e.g., a delegated group)
```

**Subject-type semantics:**
- **ST-1 Agency.** A `SecuritySubject` is the only construct that may **act, hold `Authority`, be the domain of `authorizes`/`authenticates`/`trusts`/`delegatesTo`, and be held accountable** (`Accountability`, `NonRepudiation`).
- **ST-2 Identity-borne.** Every `Principal` **has** exactly one primary `Identity` (`ONT-E-01`) and MAY bear additional scoped identities; identity is asserted-and-evidenced, never inferred (SECURITY-002 T-Id-2).
- **ST-3 Accountability binding.** Every action of a `Principal` binds to its `Identity` via an immutable `AuditRecord` (`ONT-E-20`; USA-4; SECURITY-002 T-Id-3).
- **ST-4 Archetypes are not partitions.** The four archetypes are typed refinements of the single `Principal` entity; they add no attribute beyond credential-class and agency-nature, mint no new entity, and their closure is proven in SECURITY-004.
- **ST-5 No dual-role entity.** Where a real-world thing is both actor and acted-upon (e.g., a `Principal` that is also the *target* of an authorization), the ontology models two typed references to two distinct entities (a `Principal` and a `SecurityObject` resource), never one dual-typed entity (PR-2).
- **ST-6 Zero-trust default.** No `Principal` is trusted implicitly; every trust relation (`Trust`, `ONT-E-05`) originating from or targeting a `Principal` is constructed, scoped, evidenced, and continuously re-verified (USL-004; SECURITY-002 T-Trust-1/T-Trust-4).

---

## SECTION 14 — IDENTITY ONTOLOGY

**Canonical entity:** `Identity` (`ONT-E-01`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A distinguishable, ENG-001-borne designation of a securable subject or object (SECURITY-001 §7). An `Identity` **designates exactly one** `ENG-002::Object` (SECURITY-002 T-Id-1); it is the stable name by which a construct is recognized, authenticated, authorized, and held accountable.

**Canonical attributes** (in addition to root mandatory attributes, §8.1):

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `subjectRef` | ENG-005 reference to the single designated `ENG-002::Object`. | mandatory; cardinality 1 |
| `identityClass` | The archetype of the designated thing (subject vs object; and, for subjects, the `Principal` archetype). | mandatory |
| `assuranceLevel` | The evidenced strength with which the identity is established (set by `Authentication`, §17). | ∅ until authenticated ⇒ unauthenticated |
| `credentialModelRef` | ENG-005 reference to the secret-free `CredentialModel` (`ONT-E-03`) class used to establish the identity. | secret-free (USL-013) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `designates` | Association (founding) | `Identity` → `ENG-002::Object` | 1 (exactly one) |
| `establishedBy` | Association (evaluative) | `Identity` → `Authentication` | 0..* (each yields evidence + assurance level) |
| `boundTo` | Association | `Principal` → `Identity` | Principal 1..* Identity; Identity → 1 Principal-or-Object |
| `evidences` | Association (evaluative) | `Identity` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **ID-INV-1 Single designation.** An `Identity` designates exactly one object; no identity designates two things (non-conflation, T-Id-2).
- **ID-INV-2 Distinctness.** Distinct principals bear distinct identities; identity equality implies object equality.
- **ID-INV-3 Assert-not-infer.** An `Identity` is asserted and evidenced (via `Authentication`), never inferred from behavior.
- **ID-INV-4 Secret-free.** The `credentialModelRef` names a credential *class*, never secret/credential/key material (USL-013).

**Downward references:** ENG-001 (identity primitive), ENG-002 (object), ENG-004 (type) — consumed by reference; redefined never (USL-002).

**Lifecycle participation:** an `Identity` participates in the forward-only lifecycle (SECURITY-001 §11) as a defined→specified construct; its `assuranceLevel` is (re)established continuously (SECURITY-002 T-Cont-1) and decays absent re-authentication (default to unauthenticated).

**Traceability:** every `Identity` closes a `tracesTo` lineage to SECURITY-001 §7 (No-Orphan, USL-011).

---

## SECTION 15 — PRINCIPAL ONTOLOGY

**Canonical entity:** `Principal` (`ONT-E-02`) `⊑ SecuritySubject ⊑ SecurityConstruct`.

**Definition.** An `Identity` that can act or be acted upon — the subject of trust, authorization, and accountability (SECURITY-001 §7); the sole bearer of agency in the ontology (§13). A `Principal` **has** one primary `Identity` and is the domain of every actor-side security relation.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `primaryIdentityRef` | ENG-005 reference to the `Principal`'s single primary `Identity`. | mandatory; cardinality 1 |
| `archetype` | `{Human, Service, Device, Composite}` (§13). | mandatory |
| `heldPrivilegeRefs` | ENG-005 references to `Privilege`s (`ONT-E-12`) currently held. | 0..*; least-privilege (USL-007) |
| `accountabilityRef` | ENG-005 reference to the `Accountability` property (`ONT-E-28`) binding the principal's actions. | mandatory |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `has` | Association (founding) | `Principal` → `Identity` | 1 primary, 0..* scoped |
| `holds` | Aggregation | `Principal` → `Privilege` | 0..* |
| `subjectOf` | Association (evaluative) | `Principal` → `Trust` \| `Authorization` \| `Authentication` | 0..* |
| `accountableFor` | Association (evaluative) | `Principal` → `AuditRecord` | 0..* |
| `delegatesTo` | Association (evaluative) | `Principal` → `Principal` (via `Delegation`) | 0..* (attenuating, §21 later part) |

**Semantic constraints & invariants:**
- **PR-INV-1 Identity-borne.** Every `Principal` has exactly one primary `Identity` (ST-2).
- **PR-INV-2 Least privilege.** The union of a `Principal`'s held privileges is the minimum sufficient for its purpose (USL-007; SECURITY-002 T-AuthZ-3); no standing/ambient over-privilege.
- **PR-INV-3 Accountable.** Every action binds to the `Principal`'s identity via immutable audit (ST-3; USA-4).
- **PR-INV-4 Zero-trust.** No `Principal` is implicitly trusted (ST-6; USL-004).

**Downward references:** ENG-001/002/004 (by reference); references the frozen lower-layer actor/identity constructs (RL-F2/PL-F2/AF-3) without redefinition (USL-002).

**Lifecycle participation:** a `Principal` is a long-lived subject whose trust and authorization are **continuously re-verified** (SECURITY-002 §20 T-Cont-1/T-Cont-2); expiry of established trust defaults to deny.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 16 — AUTHORITY ONTOLOGY

**Canonical entity:** `Authority` (`ONT-E-04`) `⊑ AuthorityObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A **referenced** capacity to decide or permit — declared, never minted (SECURITY-001 §7; USL-013; AUTH-06). Security holds no authority of its own (SECURITY-002 T-Auth-1); an `Authority` entity denotes a capacity resolved from frozen lower layers and explicit `Policy`, bounded by scope.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `sourceRef` | ENG-005 reference to the frozen lower-layer construct and/or `Policy` from which the authority is resolved. | mandatory; **never a mint** (USL-013) |
| `boundedScope` | The scope within which the authority is valid (extent, action-class, duration). | mandatory; bounded (T-Auth-2) |
| `conferredByRef` | ENG-005 reference to the `Policy` (`ONT-E-10`) that confers the authority. | mandatory |
| `secretFree` | Invariant marker: carries no credential/key material. | `true` (USL-013) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `resolvedFrom` | Association (founding, downward) | `Authority` → frozen lower construct \| `Policy` | 1..* |
| `conferredBy` | Association (founding) | `Authority` → `Policy` | 1 |
| `referencedBy` | Association (evaluative) | `Authorization` → `Authority` | 0..* |
| `separatedFrom` | Association | `Authority` ↔ `Authority` (duty separation) | 0..* |

**Semantic constraints & invariants:**
- **AU-INV-1 Non-mintage.** No `Authority` is created by the SECURITY domain; each is resolved-from a referenced source (USL-013; T-Auth-1).
- **AU-INV-2 Bounded.** Every `Authority` is bounded by `boundedScope` and by the `Policy` conferring it (T-Auth-2).
- **AU-INV-3 Separation of duties.** No single `Authority` both grants and exercises a critical action, nor both acts and audits it (USL-008; T-Auth-3) — modeled by mandatory `separatedFrom` for critical-action authorities.
- **AU-INV-4 Secret-free.** An `Authority` embeds no secret/credential/key material (USL-013).

**Downward references:** frozen RL-F2/PL-F2/AF-3 authority-bearing constructs and Band-13 facets, consumed by reference (USL-002); AUTH-06 (authority is declared, never minted).

**Lifecycle participation:** an `Authority` is valid only while its `sourceRef`/`conferredBy` `Policy` is valid; revocation or policy expiry defaults the authority to absent (deny).

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 17 — TRUST ONTOLOGY

**Canonical entity:** `Trust` (`ONT-E-05`) `⊑ RelationObject ⊑ SecurityObject ⊑ SecurityConstruct`, with supporting entities `TrustAnchor` (`ONT-E-06`) and `TrustBoundary` (`ONT-E-07`).

**Definition.** A constructed, directional, scoped, time-bounded relation `trust(subject, object, basis, scope, t)` asserting the subject may rely on the object for a stated purpose during a validity window (SECURITY-001 §7; SECURITY-002 §3). Trust is **never intrinsic** (T-Trust-1): absence of an established relation is distrust (default-deny).

**Supporting entities:**
- **`TrustAnchor`** — an explicitly declared, evidenced root of trust from which trust relations are derived (`derivesFrom`). Anchors are declared, not assumed (SECURITY-002 A-Trust-2).
- **`TrustBoundary`** — a trust/isolation demarcation delimiting what is owned, exposed, and protected (relates to `Boundary`/`IsolationDomain`, later part).

**Canonical attributes of `Trust`:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `subjectRef` | ENG-005 reference to the relying `Principal`/construct. | mandatory; cardinality 1 |
| `objectRef` | ENG-005 reference to the relied-upon construct. | mandatory; cardinality 1 |
| `basisRef` | ENG-005 reference to the decidable `Evidence` (`ONT-E-19`) grounding the trust. | mandatory (T-Trust-2) |
| `trustScope` | The single purpose/scope for which trust is conferred. | mandatory; non-transferable (T-Trust-3) |
| `validityWindow` | The time bound within which the trust holds; decays on expiry. | mandatory (T-Trust-4) |
| `anchorRef` | ENG-005 reference to the originating `TrustAnchor`. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `relies` | Association (evaluative) | `Trust` → (`subject` × `object`) | subject 1, object 1 |
| `basedOn` | Association (founding) | `Trust` → `Evidence` | 1..* |
| `derivesFrom` | Association (founding, downward) | `Trust` → `TrustAnchor` | 1..* |
| `scopedBy` | Composition | `Trust` → `trustScope` | 1 |
| `reVerifiedBy` | Association (evaluative) | `Trust` → `Authentication` \| `Attestation` | 0..* (continuous) |

**Semantic constraints & invariants:**
- **TR-INV-1 No intrinsic trust.** No `Trust` holds by default; every relation is constructed and evidenced (T-Trust-1; USL-004/005).
- **TR-INV-2 Evidence basis.** Every `Trust` has a decidable `basisRef` (T-Trust-2; USL-012); absent evidence ⇒ distrust.
- **TR-INV-3 Scope confinement.** Trust for one scope does not transfer to another; no scope creep (T-Trust-3).
- **TR-INV-4 Continuous re-verification.** Trust decays over time/context and is continuously re-verified; expiry defaults to distrust (T-Trust-4; SECURITY-002 T-Cont-1).
- **TR-INV-5 Anchored.** Every `Trust` derives from ≥1 explicitly declared, evidenced `TrustAnchor` (A-Trust-2).

**Downward references:** references Band-13 U05 isolation/`IsolationBoundary` and U08 SecurityFacet for boundary/anchor substrate by reference (USL-002); redefines none.

**Lifecycle participation:** a `Trust` relation is created on establishment, re-verified continuously, and terminated on expiry/revocation (forward-only; no in-place reversal — SECURITY-001 §11).

**Traceability:** every `Trust`, `TrustAnchor`, and `TrustBoundary` closes a `tracesTo` lineage to SECURITY-001 §7 (USL-011).

---

## SECTION 18 — DOCUMENT STATUS (ASSEMBLY CHECKPOINT — historical)

*This section recorded an intermediate assembly checkpoint during incremental authoring. It is retained for provenance only and is superseded by §58 Readiness Assessment and §59 Final Determination. The artifact is RATIFIED (see §59).*



---

## SECTION 19 — AUTHENTICATION ONTOLOGY

**Canonical entity:** `Authentication` (`ONT-E-08`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The evidenced establishment that a principal is who/what it claims, yielding an **assurance level** (SECURITY-001 §7; SECURITY-002 §6). Authentication is a decision-producing `SecurityObject`: it consumes a claimed `Identity` and a secret-free `CredentialModel` class, and produces immutable `Evidence` and an `assuranceLevel` bound to the `Identity`.

**Canonical attributes** (beyond root mandatory, §8.1):

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `claimedIdentityRef` | ENG-005 reference to the `Identity` being established. | mandatory; cardinality 1 |
| `credentialModelRef` | ENG-005 reference to the secret-free `CredentialModel` class used. | mandatory; secret-free (USL-013) |
| `producedAssuranceLevel` | The evidenced strength of the establishment. | mandatory; graded (T-AuthN-2) |
| `evidenceRef` | Immutable evidence of the authentication event. | mandatory (T-AuthN-1) |
| `validityWindow` | Time bound after which the establishment decays. | mandatory (T-Cont-1) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `establishes` | Association (evaluative) | `Authentication` → `Identity` | 1 |
| `consumes` | Association | `Authentication` → `CredentialModel` | 1..* (secret-free) |
| `emits` | Association (founding) | `Authentication` → `Evidence` | 1..* |
| `grades` | Association | `Authentication` → `assuranceLevel` | 1 |
| `reVerifies` | Association (evaluative) | `Authentication` → `Trust` | 0..* (continuous) |

**Semantic constraints & invariants:**
- **AN-INV-1 Evidence-yielding.** Every `Authentication` emits immutable evidence and an assurance level (T-AuthN-1; USL-010/012).
- **AN-INV-2 Assurance-graded.** Higher-consequence decisions require higher `producedAssuranceLevel` (T-AuthN-2).
- **AN-INV-3 Secret-free.** Models credential *classes* and assurance, never secret material (T-AuthN-3; USL-013).
- **AN-INV-4 Decay.** Establishment decays on `validityWindow` expiry; expiry defaults to unauthenticated (default-deny, USL-005; T-Cont-1).

**Downward references:** ENG-001/002 (identity/object); references frozen RL-F2/PL-F2/AF-3 authentication mechanisms as the enforcement substrate by reference (USL-014); redefines none.

**Lifecycle participation:** an `Authentication` event is created, emits evidence, sets `assuranceLevel`, and is superseded by re-authentication; forward-only (SECURITY-001 §11).

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 20 — AUTHORIZATION ONTOLOGY

**Canonical entity:** `Authorization` (`ONT-E-09`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The decidable determination that a principal may perform an action on a resource under a policy — the total function `authorize(principal, resource, action, context, policy) → {permit, deny, indeterminate}` with default **deny** (SECURITY-001 §7; SECURITY-002 §7; USL-005/006).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `principalRef` | ENG-005 reference to the requesting `Principal`. | mandatory; cardinality 1 |
| `resourceRef` | ENG-005 reference to the target resource object. | mandatory; cardinality 1 |
| `action` | The requested action class. | mandatory |
| `context` | The evaluated decision context (time, posture, boundary). | mandatory |
| `policyRef` | ENG-005 reference to the governing `Policy`. | mandatory; cardinality 1..* |
| `verdict` | `{permit, deny, indeterminate→deny}`. | mandatory; total (T-AuthZ-1) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `decides` | Association (evaluative) | `Authorization` → (`Principal`×`resource`×`action`×`context`×`Policy`) | 1 tuple |
| `references` | Association | `Authorization` → `Authority` | 0..* |
| `governedBy` | Association (founding) | `Authorization` → `Policy` | 1..* |
| `emits` | Association (founding) | `Authorization` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **AZ-INV-1 Totality via default-deny.** The function is total; `indeterminate` and any error resolve to `deny` (T-AuthZ-1; USL-005).
- **AZ-INV-2 Explicitness.** A `permit` exists only when an explicit `Policy` grants it (T-AuthZ-2; USL-006).
- **AZ-INV-3 Least privilege.** The permitted set is minimum sufficient for the action (T-AuthZ-3; USL-007).
- **AZ-INV-4 Determinism.** Identical inputs yield identical verdicts and byte-identical evidence (T-AuthZ-4; USL-012).
- **AZ-INV-5 Non-enforcing.** `Authorization` *decides*; enforcement of the verdict is delegated by reference to frozen lower mechanisms (USL-014; `nonEnforcing = true`).

**Downward references:** references RL-F2 runtime enforcement, PL-F2/AF-3 policy-decision constructs by reference; redefines none (USL-002).

**Lifecycle participation:** each `Authorization` is re-decidable at every access, not cached beyond its evidenced validity (T-Cont-2); expiry defaults to deny.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 21 — POLICY ONTOLOGY

**Canonical entity:** `Policy` / `AuthorizationPolicy` (`ONT-E-10`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A declarative, evaluable rule set governing authorization, control, and conformance (SECURITY-001 §7; SECURITY-002 §9). Policy defines *meaning*; enforcement is delegated by reference (T-Pol-3; USL-014).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `ruleSet` | The declarative, evaluable rules. | mandatory; deterministic (T-Pol-1) |
| `defaultDecision` | The decision absent a matching permit rule. | fixed = `deny` (T-Pol-2; USL-005) |
| `composesWith` | References to policies this composes with. | 0..* |
| `scope` | The bounded extent the policy governs. | mandatory |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `grants` | Association | `Policy` → `Permission` | 0..* |
| `governs` | Association (evaluative) | `Policy` → `Authorization` | 0..* |
| `confers` | Association (founding) | `Policy` → `Authority` | 0..* |
| `composesWith` | Aggregation | `Policy` → `Policy` | 0..* (acyclic) |
| `evaluatedBy` | Association (evaluative) | `Policy` → `Compliance` | 0..* |

**Semantic constraints & invariants:**
- **PO-INV-1 Decidability.** Every `Policy` evaluates deterministically to a decision over its inputs (T-Pol-1; USL-012).
- **PO-INV-2 Deny-closure.** A `Policy` with no matching permit rule denies (T-Pol-2; USL-005).
- **PO-INV-3 Reference-only enforcement.** Policy meaning is defined here; enforcement delegated by reference (T-Pol-3; USL-014).
- **PO-INV-4 Composability.** A composite policy is at least as restrictive as its most restrictive member (T-Pol-4; USL-009 defense-in-depth).
- **PO-INV-5 Acyclic composition.** `composesWith` is acyclic (DP-4).

**Downward references:** references RL-F2 policy-runtime and PL-F2/AF-3 policy constructs by reference; redefines none.

**Lifecycle participation:** a `Policy` is versioned append-only; supersession creates a new versioned `Policy`, the prior retained (USL-015; SECURITY-001 §11).

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 22 — PERMISSION ONTOLOGY

**Canonical entity:** `Permission` (`ONT-E-11`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A discrete, scoped grant derived from policy (SECURITY-001 §7). A `Permission` is the atomic unit of authorized capability: an (action, resource-class, scope) triple `derivesFrom` a `Policy`.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `action` | The permitted action class. | mandatory |
| `resourceClassRef` | ENG-005 reference to the resource class. | mandatory |
| `grantScope` | The bounded scope of the grant. | mandatory; minimal (USL-007) |
| `derivedFromRef` | ENG-005 reference to the granting `Policy`. | mandatory; cardinality 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `derivesFrom` | Association (founding) | `Permission` → `Policy` | 1..* |
| `aggregatedInto` | Aggregation (inverse) | `Permission` → `Role` \| `Privilege` | 0..* |
| `evidences` | Association (evaluative) | `Permission` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **PM-INV-1 Policy-derived.** Every `Permission` derives from ≥1 explicit `Policy`; no free-standing permission (USL-006).
- **PM-INV-2 Discrete & scoped.** A `Permission` is atomic and bounded in scope (USL-007).
- **PM-INV-3 Default-absent.** Absent an explicit granting policy, the permission does not exist (default-deny, USL-005).

**Downward references:** references PL-F2/AF-3 entitlement constructs by reference; redefines none.

**Lifecycle participation:** created on policy grant, revoked on policy change/expiry (forward-only); revocation defaults the capability to absent.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 23 — PRIVILEGE ONTOLOGY

**Canonical entity:** `Privilege` (`ONT-E-12`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** An accumulated authorization capacity held by a principal, subject to least-privilege (SECURITY-001 §7). A `Privilege` is the aggregate of the `Permission`s effectively held by a `Principal` within a scope.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `holderRef` | ENG-005 reference to the holding `Principal`. | mandatory; cardinality 1 |
| `permissionRefs` | ENG-005 references to aggregated `Permission`s. | 1..* |
| `privilegeScope` | The bounded scope/duration of the capacity. | mandatory; minimal (USL-007) |
| `standingProhibited` | Invariant marker: no ambient/standing over-privilege. | `true` |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `heldBy` | Association | `Privilege` → `Principal` | 1 |
| `aggregates` | Aggregation | `Privilege` → `Permission` | 1..* |
| `boundedBy` | Composition | `Privilege` → `privilegeScope` | 1 |

**Semantic constraints & invariants:**
- **PV-INV-1 Least privilege.** The held capacity is the minimum sufficient; bounded in scope, extent, and duration (USL-007; T-AuthZ-3).
- **PV-INV-2 No standing over-privilege.** No ambient or standing over-privilege (USL-007).
- **PV-INV-3 Permission-composed.** Every `Privilege` aggregates ≥1 `Permission`, each policy-derived (PM-INV-1).
- **PV-INV-4 Separation of duties.** Conflicting privileges are partitioned (USL-008; AU-INV-3).

**Downward references:** references PL-F2/AF-3 privilege/entitlement constructs by reference; redefines none.

**Lifecycle participation:** continuously re-evaluated against least-privilege; excess capacity is revoked (forward-only).

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 24 — ROLE ONTOLOGY

**Canonical entity:** `Role` (`ONT-E-13`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A named aggregation of `Permission`s assignable to `Principal`s — the RBAC/ABAC architecture construct framed in SECURITY-001 §5/§9. A `Role` is an **aggregation** entity (weak composition: permissions exist independently), not a new primitive (USL-015): it is a typed specialization of `SecurityObject` that groups policy-derived permissions under a name and scope.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `roleName` | The canonical name of the role. | mandatory; unique in scope |
| `permissionRefs` | ENG-005 references to aggregated `Permission`s. | 1..* |
| `assignmentScope` | The bounded scope within which the role may be assigned. | mandatory |
| `assignableTo` | The `Principal` archetype(s) eligible for assignment. | mandatory |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `groups` | Aggregation | `Role` → `Permission` | 1..* |
| `assignedTo` | Association | `Role` → `Principal` | 0..* |
| `derivesFrom` | Association (founding) | `Role` → `Policy` | 1..* |
| `separatedFrom` | Association | `Role` ↔ `Role` (SoD) | 0..* |

**Semantic constraints & invariants:**
- **RO-INV-1 Aggregation-only.** A `Role` aggregates independently-existing `Permission`s; it mints no permission and no authority (USL-013/015).
- **RO-INV-2 Policy-rooted.** Every aggregated `Permission` is policy-derived (PM-INV-1); a role confers nothing beyond referenced policy.
- **RO-INV-3 Least privilege.** Role assignment respects least-privilege; role scope is minimal (USL-007).
- **RO-INV-4 Separation of duties.** Conflicting roles are partitioned via `separatedFrom` (USL-008).
- **RO-INV-5 Non-primitive.** `Role` is a typed specialization, not a new primitive/identifier/lifecycle (USL-015).

**Downward references:** references PL-F2/AF-3 RBAC/ABAC constructs by reference; redefines none.

**Lifecycle participation:** versioned append-only; role changes create superseding versions (USL-015).

**Traceability:** closes `tracesTo` to SECURITY-001 §5/§9 (USL-011).

---

## SECTION 25 — DELEGATION ONTOLOGY

**Canonical entity:** `Delegation` (`ONT-E-14`) `⊑ AccessObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The scoped, evidenced transfer of a subset of authority from one principal (delegator) to another (delegate) (SECURITY-001 §7; SECURITY-002 §8). Delegation only **attenuates** — a delegate never receives more authority than the delegator holds (monotonic non-amplification, T-Del-1/T-Del-2).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `delegatorRef` | ENG-005 reference to the delegating `Principal`. | mandatory; cardinality 1 |
| `delegateRef` | ENG-005 reference to the receiving `Principal`. | mandatory; cardinality 1 |
| `transferredSubsetRef` | ENG-005 reference to the subset of `Authority`/`Permission` transferred. | mandatory; ⊆ delegator's (T-Del-1) |
| `delegationScope` | The bounded, revocable scope/duration. | mandatory; revocable (T-Del-4) |
| `originChainRef` | ENG-005 reference to the lineage back to origin authority. | mandatory (T-Del-3) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `transfers` | Association | `Delegation` → subset of `Authority`/`Permission` | 1 subset |
| `from`/`to` | Association | `Delegation` → `Principal` (delegator/delegate) | 1 / 1 |
| `derivesFrom` | Association (founding) | `Delegation` → origin `Authority` | 1..* (traceable chain) |
| `evidences` | Association (evaluative) | `Delegation` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **DL-INV-1 Subset (non-amplification).** A delegate receives ≤ the delegator's authority; never more (T-Del-1).
- **DL-INV-2 Attenuation-only.** Delegation may only narrow scope, never widen it (T-Del-2).
- **DL-INV-3 Traceable chain.** Every `Delegation` records lineage to its origin authority (T-Del-3; USL-011).
- **DL-INV-4 Revocable & bounded.** Delegated authority is bounded and revocable; expiry defaults to deny (T-Del-4; USL-005).
- **DL-INV-5 Evidenced.** Every delegation emits immutable evidence (USL-010).

**Downward references:** references PL-F2/AF-3 delegation constructs by reference; redefines none.

**Lifecycle participation:** created on transfer, continuously re-verified, revoked/expired forward-only; expiry defaults to deny (T-Cont-2).

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 26 — DOCUMENT STATUS (ASSEMBLY CHECKPOINT — historical)

*This section recorded an intermediate assembly checkpoint during incremental authoring. It is retained for provenance only and is superseded by §58 Readiness Assessment and §59 Final Determination. The artifact is RATIFIED (see §59).*



---

## SECTION 27 — CONTROL ONTOLOGY

**Canonical entity:** `Control` (`ONT-E-15`) `⊑ ProtectionObject ⊑ SecurityObject ⊑ SecurityConstruct`, with the three canonical sub-kinds `PreventiveControl`, `DetectiveControl`, `CorrectiveControl`.

**Definition.** A preventive, detective, or corrective mechanism (architecture concept) mitigating a threat (SECURITY-001 §7/§9; SECURITY-002 §10). At this layer a `Control` is descriptive/evaluative; where it denotes an enforcing mechanism it is a **downward reference** to a frozen lower mechanism (`nonEnforcing = true`; USL-014; DP-8).

**Canonical attributes** (beyond root mandatory, §8.1):

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `controlKind` | `{Preventive, Detective, Corrective}`. | mandatory |
| `mitigatesRefs` | ENG-005 references to the `Threat`s mitigated. | 1..* (T-Ctl-1) |
| `mechanismRef` | ENG-005 reference to the frozen lower-layer enforcing mechanism. | mandatory; `nonEnforcing = true` here |
| `evidenceRef` | Immutable evidence of the control's evaluation. | mandatory (T-Ctl-4) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `mitigates` | Association (evaluative) | `Control` → `Threat` | 1..* |
| `composesWith` | Aggregation | `Control` → `Control` | 0..* (layered; acyclic) |
| `references` | Association (founding, downward) | `Control` → frozen lower mechanism | 1 |
| `emits` | Association (founding) | `Control` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **CT-INV-1 Threat-linked.** Every `Control` mitigates ≥1 `Threat` (T-Ctl-1); no orphan control.
- **CT-INV-2 Layering.** No single control is assumed sufficient; controls compose across boundaries (T-Ctl-2; USL-009).
- **CT-INV-3 Independence.** Failure of one control does not defeat the composite (T-Ctl-3).
- **CT-INV-4 Evidenced.** Every control emits evidence of its evaluation (T-Ctl-4; USL-010).
- **CT-INV-5 Non-enforcing.** A `Control` references a frozen mechanism for enforcement; it enacts nothing here (USL-014).

**Downward references:** references Band-13 U08 SecurityFacet, U05 isolation, and RL-F2/PL-F2/AF-3 control mechanisms by reference; redefines none (USL-002).

**Lifecycle participation:** defined→specified→validated; continuously evaluated; superseded forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 28 — THREAT ONTOLOGY

**Canonical entity:** `Threat` / `ThreatModel` (`ONT-E-16`) `⊑ RiskObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A potential event or actor capable of harming a security property — confidentiality, integrity, availability, accountability, non-repudiation (SECURITY-001 §7; SECURITY-002 §11). A `ThreatModel` enumerates threats over a bounded scope/boundary.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `targetsRefs` | ENG-005 references to the `PropertyObject`(s) threatened. | 1..* (T-Thr-1) |
| `scopeBoundaryRef` | ENG-005 reference to the `Boundary` the model covers. | mandatory (T-Thr-2) |
| `mitigatedByRefs` | ENG-005 references to mitigating `Control`s or accepted residual `Risk`. | 1..* (T-Thr-3) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `targets` | Association (evaluative) | `Threat` → `PropertyObject` | 1..* |
| `enumeratedBy` | Aggregation | `ThreatModel` → `Threat` | 1..* (bounded scope) |
| `mitigatedBy` | Association (evaluative) | `Threat` → `Control` \| accepted `Risk` | 1..* |
| `exploits` | Association (evaluative) | `Threat` → `Vulnerability` | 0..* |

**Semantic constraints & invariants:**
- **TH-INV-1 Property-targeted.** Every `Threat` targets ≥1 named security property (T-Thr-1).
- **TH-INV-2 Model-completeness.** A `ThreatModel` enumerates threats over a bounded scope/boundary (T-Thr-2).
- **TH-INV-3 Control-mapping.** Every admitted threat maps to ≥1 mitigating control or an accepted residual risk (T-Thr-3); no silent threat.

**Downward references:** references Band-13 U08 SecurityFacet threat surface and AF-3 threat constructs by reference; redefines none.

**Lifecycle participation:** enumerated, mapped to controls/risk, re-evaluated on drift (T-Cont-3); forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 29 — RISK ONTOLOGY

**Canonical entity:** `Risk` / `RiskAssessment` (`ONT-E-17`) `⊑ RiskObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The evaluated exposure combining threat likelihood and impact over an asset (SECURITY-001 §7; SECURITY-002 §12). Risk is classified deterministically from evidence (likelihood × impact).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `threatRef` | ENG-005 reference to the source `Threat`. | mandatory; cardinality 1..* |
| `assetRef` | ENG-005 reference to the exposed asset object. | mandatory |
| `likelihood` / `impact` | The evaluated dimensions. | mandatory; deterministic (T-Rsk-1) |
| `classification` | The decidable risk class. | mandatory; from evidence |
| `residualAcceptanceRef` | ENG-005 reference to the accountable `Principal` + evidence for any accepted residual risk. | required if residual (T-Rsk-2) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `assesses` | Association (evaluative) | `Risk` → (`Threat` × asset) | 1 |
| `classifies` | Association | `Risk` → `classification` | 1 (deterministic) |
| `acceptedBy` | Association (evaluative) | residual `Risk` → `Principal` | 0..1 (accountable) |
| `evidences` | Association (evaluative) | `Risk` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **RK-INV-1 Decidable classification.** Risk is classified deterministically from evidence (T-Rsk-1; USL-012).
- **RK-INV-2 Residual accountability.** Every accepted residual risk binds to an accountable `Principal` and recorded evidence (T-Rsk-2).
- **RK-INV-3 No silent acceptance.** Unmitigated risk defaults to deny of the risky action until explicitly, traceably accepted (T-Rsk-3; USL-005).

**Downward references:** references AF-3/Band-13 risk constructs by reference; redefines none.

**Lifecycle participation:** assessed, classified, mitigated or accepted with accountability; re-assessed on drift; forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 30 — VULNERABILITY ONTOLOGY

**Canonical entity:** `Vulnerability` (`ONT-E-18`) `⊑ RiskObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A weakness in a construct that a `Threat` may exploit to harm a security property (the weakness concept within the Threat/Risk sub-theory, SECURITY-002 §11–§12). `Vulnerability` is a typed specialization of `RiskObject`, not a new primitive (USL-015): it names the *exploitable weakness* distinct from the `Threat` (the exploiting event/actor) and the `Risk` (the evaluated exposure).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `affectedConstructRef` | ENG-005 reference to the construct bearing the weakness. | mandatory; cardinality 1 |
| `weaknessClass` | The class of weakness (architecture concept, technology-neutral). | mandatory |
| `exploitableByRefs` | ENG-005 references to `Threat`s that may exploit it. | 0..* |
| `remediationRef` | ENG-005 reference to the mitigating `Control` or accepted residual `Risk`. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `weakens` | Association (evaluative) | `Vulnerability` → affected construct | 1 |
| `exploitedBy` | Association (evaluative) | `Vulnerability` → `Threat` | 0..* |
| `remediatedBy` | Association (evaluative) | `Vulnerability` → `Control` \| accepted `Risk` | 1..* |
| `evidences` | Association (evaluative) | `Vulnerability` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **VU-INV-1 Weakness-of-construct.** Every `Vulnerability` weakens exactly one identified construct (existence rule).
- **VU-INV-2 Threat-distinct.** A `Vulnerability` (weakness) is distinct from a `Threat` (exploiting event/actor) and a `Risk` (exposure); the three are separate entities related by reference (DP-2).
- **VU-INV-3 Remediation-mapped.** Every admitted `Vulnerability` maps to ≥1 mitigating `Control` or an accepted residual `Risk`; no silent weakness (default-deny of the exposed action until remediated/accepted, USL-005; RK-INV-3).
- **VU-INV-4 Non-primitive.** `Vulnerability` is a typed specialization, not a new primitive/identifier/lifecycle (USL-015).

**Downward references:** references Band-13 U08 SecurityFacet weakness surface and AF-3 constructs by reference; redefines none.

**Lifecycle participation:** identified, mapped to threats/remediation, closed on remediation or accepted as residual risk; forward-only.

**Traceability:** closes `tracesTo` to SECURITY-002 §11–§12 (USL-011).

---

## SECTION 31 — EVIDENCE ONTOLOGY

**Canonical entity:** `Evidence` / `SecurityEvidence` (`ONT-E-19`) `⊑ AssuranceObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** Immutable, attributable, deterministic, content-addressed data substantiating a security decision or property (SECURITY-001 §7/§16; SECURITY-002 §15). Evidence is **first-class**: a property is exactly as strong as its evidence (T-Ev-1; USL-012).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `substantiatesRef` | ENG-005 reference to the decision/property substantiated. | mandatory; cardinality 1..* |
| `contentHash` | Deterministic content address (reused from the CERTIFIED EC-1 ledger by reference). | mandatory; byte-identical for identical inputs (T-Ev-2) |
| `attributionRef` | ENG-005 reference to the responsible `Principal`/evaluator. | mandatory |
| `secretFree` | Invariant marker: embeds no secret/credential/key material. | `true` (T-Ev-3; USL-013) |
| `immutable` | Invariant marker: append-only, tamper-evident. | `true` (USL-010) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `substantiates` | Association (founding) | `Evidence` → decision \| property | 1..* |
| `attributedTo` | Association | `Evidence` → `Principal` | 1 |
| `chainedInto` | Composition | `Evidence` → `AuditRecord` (hash-chained) | 0..* |

**Semantic constraints & invariants:**
- **EV-INV-1 First-class.** A property is exactly as strong as its evidence (T-Ev-1; Evidence-First, USL-012).
- **EV-INV-2 Determinism.** Identical inputs produce byte-identical evidence and hash (T-Ev-2; USL-012).
- **EV-INV-3 Secret-free.** Evidence embeds no secret/credential/key material (T-Ev-3; USL-013).
- **EV-INV-4 Absence-is-deny.** Absent evidence, the property is treated as not holding (T-Ev-4; USL-005).
- **EV-INV-5 Immutable.** Evidence is append-only and tamper-evident (USL-010).

**Downward references:** reuses the CERTIFIED EC-1 `content_hash` ledger and DF-2 representation by reference; redefines none (USL-002).

**Lifecycle participation:** produced by any verdict-bearing construct; append-only; never mutated (only superseded by new evidence).

**Traceability:** closes `tracesTo` to SECURITY-001 §16 (USL-011).

---

## SECTION 32 — AUDIT ONTOLOGY

**Canonical entity:** `Audit` / `AuditRecord` (`ONT-E-20`) `⊑ AssuranceObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The immutable, ordered, attributable record of security-relevant decisions and state changes (SECURITY-001 §7; SECURITY-002 §14). The audit trail suffices to reconstruct and attribute any recorded decision (non-repudiation).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `recordsRef` | ENG-005 reference to the recorded decision/state change. | mandatory; cardinality 1 |
| `attributionRef` | ENG-005 reference to the responsible `Principal`. | mandatory (T-Aud-2) |
| `order` | The total order position in the append-only, hash-chained trail. | mandatory (T-Aud-1) |
| `evidenceRefs` | ENG-005 references to the chained `Evidence`. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `records` | Association (founding) | `AuditRecord` → decision \| state change | 1 |
| `attributes` | Association | `AuditRecord` → `Principal` | 1 |
| `chains` | Composition | `AuditRecord` → `Evidence` (hash-chained) | 1..* |

**Semantic constraints & invariants:**
- **AD-INV-1 Immutability.** Audit records are append-only and tamper-evident (hash-chained) (T-Aud-1; USL-010).
- **AD-INV-2 Attribution.** Every record binds to a responsible `Principal` (T-Aud-2; accountability).
- **AD-INV-3 Reconstructability.** The trail suffices to reconstruct and attribute any recorded decision (T-Aud-3; non-repudiation).

**Downward references:** reuses the CERTIFIED EC-1 hash-chained ledger and DF-2 representation by reference; redefines none.

**Lifecycle participation:** append-only; ordered; never mutated.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 33 — COMPLIANCE ONTOLOGY

**Canonical entity:** `Compliance` (`ONT-E-21`) `⊑ AssuranceObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The decidable conformance of a construct to USL-001…015 and referenced policy, decided from evidence (SECURITY-001 §7/§13; SECURITY-002 §16). Compliance is aggregated from evidence, not re-judged (T-Cmp-1).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `subjectRef` | ENG-005 reference to the assessed construct. | mandatory; cardinality 1 |
| `againstRef` | ENG-005 reference to the USL set / referenced `Policy` assessed against. | mandatory |
| `verdict` | The decidable conformance verdict (aggregated). | mandatory; deterministic |
| `evidenceRefs` | ENG-005 references to the aggregated `Evidence`. | 1..* (T-Cmp-1) |
| `lineageRef` | No-Orphan lineage of the verdict. | mandatory (T-Cmp-3) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `assesses` | Association (evaluative) | `Compliance` → assessed construct | 1 |
| `against` | Association | `Compliance` → USL set \| `Policy` | 1..* |
| `aggregates` | Aggregation | `Compliance` → `Evidence` | 1..* |
| `tracesTo` | Association (founding) | `Compliance` → SECURITY-001 | 1 (No-Orphan) |

**Semantic constraints & invariants:**
- **CM-INV-1 Aggregation.** Compliance is aggregated from evidence, not re-judged (T-Cmp-1; SECURITY-001 §13).
- **CM-INV-2 Scope-closure.** Compliance closes scope, never evolution (T-Cmp-2; AUTH-INF-001 CR-INF-011).
- **CM-INV-3 Traceable verdict.** Every compliance verdict closes a No-Orphan lineage (T-Cmp-3; USL-011).
- **CM-INV-4 Deterministic.** Identical evidence yields identical verdict (USL-012).

**Downward references:** reuses the CCE ten-gate + INFRASTRUCTURE-001 §12 certification pattern by reference; redefines none.

**Lifecycle participation:** assessed on evidence, re-assessed on change; scope-closing, not evolution-closing.

**Traceability:** closes `tracesTo` to SECURITY-001 §7/§13 (USL-011).

---

## SECTION 34 — DOCUMENT STATUS (ASSEMBLY CHECKPOINT — historical)

*This section recorded an intermediate assembly checkpoint during incremental authoring. It is retained for provenance only and is superseded by §58 Readiness Assessment and §59 Final Determination. The artifact is RATIFIED (see §59).*



---

## SECTION 35 — ATTESTATION ONTOLOGY

**Canonical entity:** `Attestation` (`ONT-E-22`) `⊑ AssuranceObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A signed/evidenced assertion that a property or state holds at a point in time (SECURITY-001 §7; SECURITY-002 §19 T-Rec-3). An `Attestation` binds a claimed property, the evidence, the attesting `Principal`, and a timestamp; it asserts, it does not enforce.

**Canonical attributes** (beyond root mandatory, §8.1):

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `assertsRef` | ENG-005 reference to the `PropertyObject`/state asserted. | mandatory; cardinality 1 |
| `atTime` | The point in time at which the assertion holds. | mandatory |
| `attesterRef` | ENG-005 reference to the attesting `Principal`. | mandatory |
| `evidenceRefs` | ENG-005 references to the substantiating `Evidence`. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `asserts` | Association (evaluative) | `Attestation` → `PropertyObject` \| state | 1 (at `atTime`) |
| `attestedBy` | Association | `Attestation` → `Principal` | 1 |
| `evidences` | Association (founding) | `Attestation` → `Evidence` | 1..* |
| `reEstablishes` | Association (evaluative) | `Attestation` → `Trust` | 0..* (post-recovery) |

**Semantic constraints & invariants:**
- **AT-INV-1 Evidenced assertion.** Every `Attestation` is backed by immutable evidence (USL-010; T-Rec-3).
- **AT-INV-2 Point-in-time.** An `Attestation` asserts a property at `atTime`; it decays and is re-attested continuously (T-Cont-1).
- **AT-INV-3 Attributable.** Every `Attestation` binds to an attesting `Principal` (non-repudiation, USL-010).
- **AT-INV-4 Non-enforcing.** An `Attestation` asserts; it enacts nothing (USL-014).

**Downward references:** reuses the CERTIFIED EC-1 content-hash ledger and DF-2 representation by reference; redefines none (USL-002).

**Lifecycle participation:** produced at a point in time, decays, re-attested; append-only; forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 36 — ISOLATION ONTOLOGY

**Canonical entity:** `Isolation` / `IsolationDomain` (`ONT-E-23`) `⊑ ProtectionObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The architectural confinement separating constructs to bound blast radius (SECURITY-001 §7; SECURITY-002 §17), referencing the frozen Infrastructure `IsolationBoundary` (Band-13 U05) **by reference**. An `IsolationDomain` declares exactly one `Boundary` delimiting what is owned, exposed, and protected.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `boundaryRef` | ENG-005 reference to the single declared `Boundary`. | mandatory; cardinality 1 (T-Iso-1) |
| `confinesRefs` | ENG-005 references to the constructs confined within. | 0..* |
| `infraBoundaryRef` | ENG-005 reference to the frozen Band-13 U05 `IsolationBoundary`. | mandatory; by reference (T-Iso-3) |
| `blastRadius` | The bounded extent a compromise may reach. | mandatory; bounded (T-Iso-2) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `contains` | Composition | `IsolationDomain` → confined construct | 0..* (downward, acyclic) |
| `isolates` | Association (evaluative) | `IsolationDomain` → construct | 0..* |
| `bounds` | Composition | `IsolationDomain` → `Boundary` | 1 |
| `references` | Association (founding, downward) | `IsolationDomain` → Band-13 U05 | 1 |

**Semantic constraints & invariants:**
- **IS-INV-1 Boundary-declared.** Every `IsolationDomain` declares exactly one `Boundary` (T-Iso-1).
- **IS-INV-2 Blast-radius bound.** Compromise within a domain does not, by default, cross its boundary (default-deny across boundaries, T-Iso-2; USL-005).
- **IS-INV-3 Reference-only.** Isolation reuses Infrastructure boundaries by reference; re-owns none (T-Iso-3; USL-002).
- **IS-INV-4 Acyclic containment.** The `contains` graph is downward-only and acyclic (DP-4).

**Downward references:** references Band-13 U05 `IsolationBoundary` and U08 SecurityFacet by reference; redefines none.

**Lifecycle participation:** declared with a boundary, evaluated continuously, superseded forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 37 — BOUNDARY ONTOLOGY

**Canonical entity:** `Boundary` (`ONT-E-24`) `⊑ ProtectionObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** A trust/isolation demarcation delimiting what is owned, exposed, and protected (SECURITY-001 §7; SECURITY-002 §24 A-Bnd-1/A-Bnd-2). A `Boundary` is the demarcation entity referenced by `IsolationDomain` (`bounds`) and `TrustBoundary`.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `demarcates` | What is owned/exposed/protected on each side. | mandatory |
| `crossingPolicyRef` | ENG-005 reference to the `Policy` governing cross-boundary interaction. | mandatory (A-Bnd-2) |
| `defaultCrossing` | The decision for un-permitted crossing. | fixed = `deny` (A-Bnd-2; USL-005) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `delimits` | Association | `Boundary` → owned/exposed/protected sets | 1 |
| `governedBy` | Association (founding) | `Boundary` → `Policy` | 1..* |
| `crossedVia` | Association (evaluative) | `Boundary` → typed evidenced reference | 0..* (default-deny) |

**Semantic constraints & invariants:**
- **BD-INV-1 Single demarcation.** A `Boundary` delimits exactly one owned/exposed/protected partition (A-Bnd-1).
- **BD-INV-2 Explicit crossing.** Cross-boundary interaction requires an explicit, typed, evidenced reference; default-deny otherwise (A-Bnd-2; USL-005).
- **BD-INV-3 Policy-governed.** Every crossing is governed by an explicit `Policy` (USL-006).

**Downward references:** references Band-13 U05 isolation boundaries by reference; redefines none.

**Lifecycle participation:** declared, governed by crossing policy, superseded forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 38 — INTEGRITY ONTOLOGY

**Canonical entity:** `Integrity` (`ONT-E-25`) `⊑ PropertyObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The property that a construct/datum is unaltered except by authorized action (SECURITY-001 §7). As a `PropertyObject`, `Integrity` is an asserted-and-evidenced property, not a runtime guarantee owned here (OT-5).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `subjectRef` | ENG-005 reference to the construct/datum whose integrity is asserted. | mandatory; cardinality 1 |
| `authorizedChangeRef` | ENG-005 reference to the `Authorization`/`Policy` defining permitted alteration. | mandatory |
| `evidenceRefs` | ENG-005 references to evidence the property holds. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `heldBy` | Association | `Integrity` → subject construct | 1 |
| `assuredBy` | Association (evaluative) | `Integrity` → `Control` \| `Attestation` | 1..* |
| `threatenedBy` | Association (evaluative) | `Integrity` → `Threat` | 0..* |
| `evidences` | Association (evaluative) | `Integrity` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **IN-INV-1 Evidence-decidable.** `Integrity` holds only insofar as decidable from evidence (OT-5; USL-012).
- **IN-INV-2 Authorized-change-only.** Alteration outside an explicit `Authorization` violates integrity (USL-006).
- **IN-INV-3 Assurance-not-enforcement.** Integrity is asserted/evaluated here; enforcement delegated by reference (USL-014).

**Downward references:** references DF-2 representation integrity and Band-13/AF-3 mechanisms by reference; redefines none.

**Lifecycle participation:** continuously assured/attested; violation triggers `Recovery` (§41).

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 39 — CONFIDENTIALITY ONTOLOGY

**Canonical entity:** `Confidentiality` (`ONT-E-26`) `⊑ PropertyObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The property that information is disclosed only to authorized principals (SECURITY-001 §7). An asserted-and-evidenced property (OT-5), enforced by reference to frozen lower mechanisms (USL-014).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `subjectRef` | ENG-005 reference to the information whose confidentiality is asserted. | mandatory; cardinality 1 |
| `authorizedDisclosureRef` | ENG-005 reference to the `Authorization`/`Policy` defining permitted disclosure. | mandatory |
| `evidenceRefs` | ENG-005 references to evidence the property holds. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `heldBy` | Association | `Confidentiality` → subject information | 1 |
| `assuredBy` | Association (evaluative) | `Confidentiality` → `Control` \| `Attestation` | 1..* |
| `threatenedBy` | Association (evaluative) | `Confidentiality` → `Threat` | 0..* |
| `evidences` | Association (evaluative) | `Confidentiality` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **CF-INV-1 Evidence-decidable.** Holds only insofar as decidable from evidence (OT-5; USL-012).
- **CF-INV-2 Authorized-disclosure-only.** Disclosure outside an explicit `Authorization` violates confidentiality; default-deny disclosure (USL-005/006).
- **CF-INV-3 Secret-free modeling.** The ontology models the *property*, never embedding secret material (USL-013).

**Downward references:** references DF-2 representation and Band-13/AF-3 protection mechanisms by reference; redefines none.

**Lifecycle participation:** continuously assured/attested; violation triggers `Recovery`.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 40 — AVAILABILITY ONTOLOGY

**Canonical entity:** `Availability` (`ONT-E-27`) `⊑ PropertyObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The property that a construct is accessible to authorized principals when required (SECURITY-001 §7), referencing frozen Infrastructure resilience (Band-13 U07 AvailabilityTopology) **by reference** (SECURITY-002 §18).

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `subjectRef` | ENG-005 reference to the construct whose availability is asserted. | mandatory; cardinality 1 |
| `resilienceRef` | ENG-005 reference to the frozen Band-13 U07 resilience topology. | mandatory; by reference (T-Res-2) |
| `evidenceRefs` | ENG-005 references to evidence the property holds. | 1..* |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `heldBy` | Association | `Availability` → subject construct | 1 |
| `sustainedBy` | Association (founding, downward) | `Availability` → Band-13 U07 resilience | 1..* |
| `threatenedBy` | Association (evaluative) | `Availability` → `Threat` | 0..* |
| `evidences` | Association (evaluative) | `Availability` → `Evidence` | 1..* |

**Semantic constraints & invariants:**
- **AV-INV-1 Property-continuity.** Availability preserves accessibility under partial failure alongside confidentiality/integrity/accountability (T-Res-1).
- **AV-INV-2 Reference-only.** Continuity mechanisms are consumed by reference; none re-owned (T-Res-2; USL-002).
- **AV-INV-3 Graceful denial.** Under degradation, the system fails to a safe, default-deny state (T-Res-3; USL-005).

**Downward references:** references Band-13 U07 AvailabilityTopology and RL-F2 by reference; redefines none.

**Lifecycle participation:** continuously assured; degradation triggers graceful denial then `Recovery`.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

---

## SECTION 41 — RECOVERY ONTOLOGY

**Canonical entity:** `Recovery` (`ONT-E-30`) `⊑ ProtectionObject ⊑ SecurityObject ⊑ SecurityConstruct`.

**Definition.** The architected restoration of a secured state after compromise or failure (SECURITY-001 §7; SECURITY-002 §19). Recovery is evidence-driven (detection → response → restoration) and restores integrity and accountability before resuming availability.

**Canonical attributes:**

| Attribute | Meaning | Constraint |
|-----------|---------|------------|
| `restoresRef` | ENG-005 reference to the secured state to restore. | mandatory; cardinality 1 |
| `triggerEvidenceRef` | ENG-005 reference to the detection `Evidence` that triggers recovery. | mandatory (T-Rec-1) |
| `restorationOrder` | Integrity & accountability restored before availability. | fixed order (T-Rec-2) |
| `attestationRef` | ENG-005 reference to the `Attestation` of the restored state. | mandatory (T-Rec-3) |

**Canonical relationships:**

| Relationship | Kind | Domain → Range | Cardinality |
|--------------|------|----------------|-------------|
| `restores` | Association (evaluative) | `Recovery` → secured state | 1 |
| `triggeredBy` | Association (founding) | `Recovery` → detection `Evidence` | 1..* |
| `attestedBy` | Association (evaluative) | `Recovery` → `Attestation` | 1..* |
| `reEstablishes` | Association (evaluative) | `Recovery` → `Trust` | 0..* (post-restoration) |

**Semantic constraints & invariants:**
- **RC-INV-1 Evidence-driven.** Recovery is triggered and validated by evidence (T-Rec-1; USL-012).
- **RC-INV-2 Integrity-first.** Recovery restores integrity and accountability before resuming availability (T-Rec-2).
- **RC-INV-3 Attested restoration.** A restored state is attested before trust is re-established (T-Rec-3; T-Trust-4).

**Downward references:** references Band-13 U07 resilience and RL-F2/AF-3 recovery mechanisms by reference; redefines none.

**Lifecycle participation:** triggered by detection evidence, ordered restoration, attested, trust re-established; forward-only.

**Traceability:** closes `tracesTo` to SECURITY-001 §7 (USL-011).

> **Note on remaining property entities.** `Accountability` (`ONT-E-28`) and `NonRepudiation` (`ONT-E-29`) are `PropertyObject`s already fully constrained by the audit/evidence ontologies (§31–§32; USA-4, AD-INV-2/3): `Accountability` = every action binds to a responsible `Principal` (ST-3; PR-INV-3); `NonRepudiation` = a recorded action cannot be plausibly denied (T-Aud-3). `AssuranceFacet` (`ONT-E-31`) and `SecurityGovernanceFacet` (`ONT-E-32`) are the non-enforcing evaluative facets (`nonEnforcing = true`; USL-014; SECURITY-001 §12) whose relationships (`evaluates`, `attests`) are fixed in the consolidated Relationship Model (§43). No further per-concept section is required; all 32 catalog entities (`ONT-E-01…32`) are now defined.

---

## SECTION 42 — DOCUMENT STATUS (ASSEMBLY CHECKPOINT — historical)

*This section recorded an intermediate assembly checkpoint during incremental authoring. It is retained for provenance only and is superseded by §58 Readiness Assessment and §59 Final Determination. The artifact is RATIFIED (see §59).*



---

## SECTION 43 — CANONICAL RELATIONSHIP MODEL

This section **consolidates** every relationship introduced per-concern (§14–§41) into the single canonical relationship model, classifying each under exactly one of the four root relationship kinds (§9.1). Every relationship is a typed ENG-005 reference (USL-002); the ontology mints no connection construct (USL-015).

### 43.1 Canonical relationship catalog

| Code | Relationship | Kind | Domain → Range | Direction |
|------|--------------|------|----------------|-----------|
| `R-01` | `isA` (`⊑`) | Inheritance | `SecurityConstruct` → `SecurityConstruct` | acyclic, rooted |
| `R-02` | `designates` | Association (founding) | `Identity` → `ENG-002::Object` | downward |
| `R-03` | `has` / `boundTo` | Association (founding) | `Principal` → `Identity` | intra-domain |
| `R-04` | `holds` / `heldBy` | Aggregation | `Principal` ↔ `Privilege` | intra-domain |
| `R-05` | `authenticates` / `establishes` | Association (evaluative) | `Authentication` → `Identity` | non-mutating |
| `R-06` | `authorizes` / `decides` | Association (evaluative) | `Authorization` → (Principal×Resource×Action×Context×Policy) | non-mutating |
| `R-07` | `trusts` / `relies` | Association (evaluative) | `Trust` → (subject×object) | non-mutating |
| `R-08` | `basedOn` | Association (founding) | `Trust` → `Evidence` | downward |
| `R-09` | `derivesFrom` | Association (founding) | `SecurityObject` → `SecurityObject` (Permission→Policy, Delegation→Authority, Trust→TrustAnchor, Role→Policy) | downward, acyclic |
| `R-10` | `grants` | Association | `Policy` → `Permission` | intra-domain |
| `R-11` | `confers` / `conferredBy` / `resolvedFrom` | Association (founding) | `Policy`/lower ↔ `Authority` | downward |
| `R-12` | `governs` / `governedBy` | Association (evaluative) | `Policy` → `Authorization`/`Boundary` | non-mutating |
| `R-13` | `groups` | Aggregation | `Role`/`ThreatModel` → `Permission`/`Threat` | acyclic |
| `R-14` | `delegatesTo` / `transfers` | Association (evaluative) | `Delegation` → `Principal` (subset of Authority) | attenuating, traceable |
| `R-15` | `controls` / `mitigates` | Association (evaluative) | `Control` → `Threat` | non-mutating |
| `R-16` | `targets` | Association (evaluative) | `Threat` → `PropertyObject` | non-mutating |
| `R-17` | `assesses` / `classifies` | Association (evaluative) | `Risk` → (Threat×asset) | non-mutating |
| `R-18` | `exploits` / `exploitedBy` | Association (evaluative) | `Threat` ↔ `Vulnerability` | non-mutating |
| `R-19` | `weakens` | Association (evaluative) | `Vulnerability` → affected construct | non-mutating |
| `R-20` | `evidences` / `substantiates` | Association (founding) | `SecurityConstruct` → `Evidence` | downward |
| `R-21` | `records` / `attributes` | Association (founding) | `AuditRecord` → decision / `Principal` | downward |
| `R-22` | `attests` / `asserts` | Association (evaluative) | `Attestation` → `PropertyObject`/state | non-mutating |
| `R-23` | `assessesCompliance` / `against` | Association (evaluative) | `Compliance` → construct / USL set | non-mutating |
| `R-24` | `contains` | Composition | `IsolationDomain` → confined construct | downward, acyclic |
| `R-25` | `isolates` | Association (evaluative) | `IsolationDomain` → construct | non-mutating |
| `R-26` | `bounds` / `delimits` | Composition / Association | `IsolationDomain`/`Boundary` → `Boundary`/partition | downward |
| `R-27` | `assuredBy` / `sustainedBy` | Association (evaluative/founding) | `PropertyObject` → `Control`/`Attestation`/resilience | non-mutating / downward |
| `R-28` | `restores` / `triggeredBy` / `reEstablishes` | Association (evaluative/founding) | `Recovery` → state/`Evidence`/`Trust` | non-mutating / downward |
| `R-29` | `evaluates` | Association (evaluative) | `AssuranceFacet`/`SecurityGovernanceFacet` → `SecurityConstruct` | **non-mutating** (`nonEnforcing=true`) |
| `R-30` | `dependsOn` | Association (founding) | `SecurityConstruct` → `SecurityConstruct`/lower construct | **downward-only, acyclic** |
| `R-31` | `references` | Association (founding, downward) | `SecurityObject` → frozen lower mechanism | downward |
| `R-32` | `tracesTo` | Association (founding) | `SecurityConstruct` → SECURITY-001/anchor | downward, acyclic (No-Orphan) |
| `R-33` | `separatedFrom` | Association | `Authority`/`Role` ↔ `Authority`/`Role` (SoD) | symmetric, non-mutating |
| `R-34` | `composesWith` | Aggregation | `Policy`/`Control` → `Policy`/`Control` | acyclic |
| `R-35` | `reVerifiedBy` / `reVerifies` | Association (evaluative) | `Trust` ↔ `Authentication`/`Attestation` | non-mutating, continuous |

### 43.2 Relationship model rules

- **RM-1** Every relationship above is a specialization of exactly one root kind (Inheritance / Composition / Aggregation / Association) — §9.1.
- **RM-2** The union of founding relationships (`isA`, `dependsOn`, `derivesFrom`, `contains`, `bounds`, `references`, `tracesTo`, `basedOn`, `evidences`, `records`, `triggeredBy`) is a **DAG** — no cycle, no upward/forward edge (USL-011; INV-6; DP-4).
- **RM-3** Every evaluative association (`authenticates`, `authorizes`, `trusts`, `mitigates`, `attests`, `evaluates`, `isolates`, `assesses`, …) is **non-mutating**: it references its target without altering it (USL-014; INV-7).
- **RM-4** Every relationship expressing a security decision or property is **evidence-linked** (`evidences`); absence of evidence ⇒ the relation does not hold (default-deny — USL-005/012).
- **RM-5** No relationship crosses a `Boundary` without an explicit, typed, evidenced crossing reference governed by `Policy` (A-Bnd-2; §37).

---

## SECTION 44 — CANONICAL ATTRIBUTE MODEL

This section **consolidates** the attribute model: the mandatory core attributes borne by every entity, plus the attribute-formation rules governing per-entity attributes (§14–§41).

### 44.1 Mandatory core attributes (every `SecurityConstruct`)

Restated canonically from §8.1 (borne by every entity via `SecurityConstruct ⊑ ENG-002::Object`):

| Code | Attribute | Type / Source | Mandatory | Meaning |
|------|-----------|---------------|-----------|---------|
| `A-01` | `id` | ENG-001 identity | ✅ | Canonical, stable, distinguishable identity. |
| `A-02` | `type` | ENG-004 type | ✅ | The leaf entity class. |
| `A-03` | `value` | ENG-003 value | ✅ | Value with deterministic fidelity. |
| `A-04` | `scope` | bounded extent | ✅ | Where the construct is meaningful/valid. |
| `A-05` | `evidenceRef` | immutable ref → `Evidence` | ✅ | Evidence substantiating the construct. |
| `A-06` | `trustBasis` | evidenced basis (may be ∅) | ✅ | Basis for reliance; ∅ ⇒ distrust. |
| `A-07` | `assuranceVerdict` | `{holds, denied, indeterminate→denied}` | ✅ | Decidable verdict over the asserted property. |
| `A-08` | `nonEnforcing` | boolean invariant | ✅ | `true` at architecture layer (USL-014). |
| `A-09` | `lineageRef` | ref → SECURITY-001/anchor | ✅ | Backward No-Orphan lineage (USL-011). |

### 44.2 Attribute-formation rules

- **AM-1 Additive.** Per-entity attributes (§14–§41) are **added** to the mandatory core; the core is never removed or weakened (DP-5; append-only).
- **AM-2 Typed & referenced.** Every attribute whose value is another construct is an ENG-005 reference, never an embedded copy (USL-002).
- **AM-3 Secret-free.** No attribute embeds secret/credential/key material; credential attributes name *classes* only (USL-013; EV-INV-3; AN-INV-3).
- **AM-4 Evidence-bearing.** Every attribute asserting a security fact carries or references immutable evidence (USL-010/012).
- **AM-5 Deterministic.** Every attribute derivation is deterministic — identical inputs yield identical values (USL-012; INV-5).
- **AM-6 Scoped.** Every grant/capacity attribute (`grantScope`, `privilegeScope`, `delegationScope`, `trustScope`) is bounded (least-privilege / scope-confinement — USL-007; T-Trust-3).

### 44.3 Attribute inheritance

Attributes are inherited along the `isA` hierarchy (§45): a leaf entity bears the union of (mandatory core) ∪ (all attributes of its super-entities) ∪ (its own declared attributes). No leaf may drop an inherited mandatory attribute (AM-1).

---

## SECTION 45 — INHERITANCE MODEL

**Kind:** Inheritance (`isA`, `⊑`) — specialization (§9.1). Directed, acyclic, rooted at `SecurityConstruct`.

### 45.1 The canonical inheritance hierarchy

```
ENG-002::Object                                   «frozen; referenced, never redefined»
└── SecurityConstruct «abstract, root»
    ├── SecuritySubject «abstract»
    │   └── Principal (ONT-E-02)                  «concrete»
    │       ├── HumanPrincipal · ServicePrincipal · DevicePrincipal · CompositePrincipal
    └── SecurityObject «abstract»
        ├── AccessObject «abstract»
        │     Identity · CredentialModel · Authentication · Authorization
        │     Policy · Permission · Privilege · Role · Delegation
        ├── RelationObject «abstract»
        │     Trust · TrustAnchor · TrustBoundary
        ├── AuthorityObject «abstract»
        │     Authority
        ├── ProtectionObject «abstract»
        │     Control · IsolationDomain · Boundary · Recovery
        ├── RiskObject «abstract»
        │     Threat/ThreatModel · Vulnerability · Risk/RiskAssessment
        ├── AssuranceObject «abstract»
        │     Evidence · AuditRecord · Attestation · Compliance · AssuranceFacet
        └── PropertyObject «abstract»
              Integrity · Confidentiality · Availability · Accountability
              NonRepudiation · SecurityGovernanceFacet
```

### 45.2 Inheritance rules

- **IH-1 Single super.** Every entity `⊑` exactly one direct super-entity (single inheritance); no multiple inheritance (decidability, USL-012).
- **IH-2 Rooted.** Every path terminates upward at `SecurityConstruct ⊑ ENG-002::Object` (FP-2; existence rule).
- **IH-3 Acyclic.** The `isA` graph is a DAG (DP-4).
- **IH-4 Abstract vs concrete.** Abstract entities (`SecurityConstruct`, `SecuritySubject`, `SecurityObject`, the 7 object families) are never instantiated; only concrete leaves are instantiable (§8.1; closure by SECURITY-005).
- **IH-5 Attribute inheritance.** A sub-entity inherits all attributes and constraints of its supers (§44.3); it may add, never remove, mandatory ones.
- **IH-6 Substitutability.** Any constraint holding of a super-entity holds of every sub-entity (Liskov-style substitutability for decidable constraints).

---

## SECTION 46 — COMPOSITION MODEL

**Kind:** Composition (`contains` / `partOf`, strong) — a whole whose parts are existence-bounded by the whole (§9.1). Directed, downward-only, acyclic.

### 46.1 Canonical compositions

| Whole | Part | Relationship | Semantics |
|-------|------|--------------|-----------|
| `IsolationDomain` | confined constructs | `contains` (R-24) | parts confined within the domain; blast-radius bounded (IS-INV-2). |
| `IsolationDomain` | `Boundary` | `bounds` (R-26) | the domain has exactly one delimiting boundary (IS-INV-1). |
| `Privilege` | `privilegeScope` | `boundedBy` | the capacity is existence-bounded by its scope (PV-INV-1). |
| `Trust` | `trustScope` | `scopedBy` | the relation is bounded to a single purpose/scope (TR-INV-3). |
| `AuditRecord` | chained `Evidence` | `chains` | the record composes its hash-chained evidence (AD-INV-1). |

### 46.2 Composition rules

- **CO-1 Existence coupling.** A part in a composition is bounded by its whole: the part's validity does not exceed the whole's (lifecycle-coupled).
- **CO-2 Downward & acyclic.** Every composition edge is downward-only and acyclic (RM-2; DP-4).
- **CO-3 Non-mutating.** Composition expresses structure by reference (ENG-005); the whole does not mutate the part (USL-002/014).
- **CO-4 Single-whole for strong parts.** A strong part (`Boundary` of an `IsolationDomain`, `trustScope` of a `Trust`) belongs to exactly one whole (cardinality 1 — §49).

---

## SECTION 47 — AGGREGATION MODEL

**Kind:** Aggregation (`groups` / `collects`, weak) — a collector of independently-existing members (§9.1). Directed, acyclic.

### 47.1 Canonical aggregations

| Collector | Member | Relationship | Semantics |
|-----------|--------|--------------|-----------|
| `Role` | `Permission` | `groups` (R-13) | permissions exist independently; a role names a set of them (RO-INV-1). |
| `Privilege` | `Permission` | `aggregates` (R-04) | the held capacity is the aggregate of policy-derived permissions (PV-INV-3). |
| `Principal` | `Privilege` | `holds` (R-04) | a principal holds independently-existing privileges (PR-INV-2). |
| `ThreatModel` | `Threat` | `groups` (R-13) | a model enumerates independently-defined threats over a bounded scope (TH-INV-2). |
| `Policy` | `Policy` | `composesWith` (R-34) | policies compose into a composite at least as restrictive as its members (PO-INV-4). |
| `Control` | `Control` | `composesWith` (R-34) | controls layer independently (CT-INV-2). |
| `Compliance` | `Evidence` | `aggregates` (R-23) | a verdict aggregates independent evidence, not re-judged (CM-INV-1). |

### 47.2 Aggregation rules

- **AG-1 Independent members.** Aggregated members exist independently of the collector (weak ownership); deleting the collector does not delete members.
- **AG-2 Acyclic.** Every aggregation graph is acyclic (`composesWith`, `groups`, `holds`) (DP-4).
- **AG-3 Reference-only.** Membership is expressed by ENG-005 reference (USL-002).
- **AG-4 Restrictive composition.** Where aggregation composes decisions/controls/policies, the composite is **at least as restrictive** as its most restrictive member (defense-in-depth — USL-009; PO-INV-4; CT-INV-2).
- **AG-5 No minting.** An aggregation confers nothing beyond the union of its members' referenced grants (RO-INV-2; USL-013).

---

## SECTION 48 — ASSOCIATION MODEL

**Kind:** Association (typed reference) — named, non-structural relations, partitioned into **founding** (downward-only, acyclic) and **evaluative** (non-mutating) (§9.1).

### 48.1 Founding associations (downward-only, acyclic)

`designates` (R-02), `has`/`boundTo` (R-03), `basedOn` (R-08), `derivesFrom` (R-09), `confers`/`resolvedFrom` (R-11), `evidences`/`substantiates` (R-20), `records`/`attributes` (R-21), `references` (R-31), `tracesTo` (R-32), `dependsOn` (R-30), `sustainedBy` (R-27), `triggeredBy` (R-28). These form the founding sub-graph and are constrained to a DAG (RM-2).

### 48.2 Evaluative associations (non-mutating)

`authenticates`/`establishes` (R-05), `authorizes`/`decides` (R-06), `trusts`/`relies` (R-07), `governs` (R-12), `delegatesTo`/`transfers` (R-14), `controls`/`mitigates` (R-15), `targets` (R-16), `assesses`/`classifies` (R-17), `exploits` (R-18), `weakens` (R-19), `attests`/`asserts` (R-22), `assessesCompliance` (R-23), `isolates` (R-25), `assuredBy` (R-27), `restores`/`reEstablishes` (R-28), `evaluates` (R-29), `separatedFrom` (R-33), `reVerifiedBy` (R-35). Each references its target without altering it (USL-014; INV-7).

### 48.3 Association rules

- **AS-1 Typed & named.** Every association bears a fixed type and name (DP-3); no untyped/implicit edges.
- **AS-2 Direction discipline.** Founding associations are downward-only & acyclic; evaluative associations may reference downward but never create a founding cycle (RM-2).
- **AS-3 Non-mutating evaluation.** Evaluative associations never mutate their targets (RM-3; USL-014).
- **AS-4 Evidence-linked.** Every decision/property association links to immutable evidence (RM-4; USL-010/012).
- **AS-5 Boundary-respecting.** No association crosses a `Boundary` except via an explicit, typed, evidenced, policy-governed crossing (RM-5; A-Bnd-2).

---

## SECTION 49 — CARDINALITY RULES

Cardinality is fixed for every canonical relationship; ambiguity resolves to the most restrictive (default-deny — USL-005).

| # | Relationship | Cardinality | Rule |
|---|--------------|-------------|------|
| `CR-01` | `Identity` `designates` `ENG-002::Object` | **1 : 1** | An identity designates exactly one object (ID-INV-1). |
| `CR-02` | `Principal` `has` primary `Identity` | **1 : 1** (0..* scoped) | Exactly one primary identity; ≥0 scoped (PR-INV-1). |
| `CR-03` | `Principal` `holds` `Privilege` | **1 : 0..*** | Minimal set (least-privilege, PV-INV-1). |
| `CR-04` | `Privilege` `aggregates` `Permission` | **1 : 1..*** | ≥1 policy-derived permission (PV-INV-3). |
| `CR-05` | `Permission` `derivesFrom` `Policy` | **1..* : 1..*** | Every permission from ≥1 policy (PM-INV-1). |
| `CR-06` | `Role` `groups` `Permission` | **1 : 1..*** | A role names ≥1 permission (RO-INV-1). |
| `CR-07` | `Authorization` `governedBy` `Policy` | **1 : 1..*** | Every decision under ≥1 policy (AZ-INV-2). |
| `CR-08` | `Authentication` `establishes` `Identity` | **1 : 1** | Establishes exactly one identity (AN-INV-1). |
| `CR-09` | `Trust` (`subject`,`object`) | **1 : 1** each | Directional single subject/object (TR-INV-1). |
| `CR-10` | `Trust` `basedOn` `Evidence` | **1 : 1..*** | ≥1 evidence basis (TR-INV-2). |
| `CR-11` | `Trust` `derivesFrom` `TrustAnchor` | **1 : 1..*** | ≥1 declared anchor (TR-INV-5). |
| `CR-12` | `Delegation` (`delegator`,`delegate`) | **1 : 1** each | Single delegator/delegate; subset only (DL-INV-1). |
| `CR-13` | `Control` `mitigates` `Threat` | **1 : 1..*** | Every control mitigates ≥1 threat (CT-INV-1). |
| `CR-14` | `Threat` `targets` `PropertyObject` | **1 : 1..*** | Every threat targets ≥1 property (TH-INV-1). |
| `CR-15` | `Vulnerability` `weakens` construct | **1 : 1** | Weakens exactly one construct (VU-INV-1). |
| `CR-16` | `Risk` `acceptedBy` `Principal` (residual) | **1 : 0..1** | Accountable acceptor for residual (RK-INV-2). |
| `CR-17` | `IsolationDomain` `bounds` `Boundary` | **1 : 1** | Exactly one boundary (IS-INV-1). |
| `CR-18` | any `SecurityConstruct` `evidences` `Evidence` | **1 : 1..*** (verdict-bearing) | Every verdict-bearing construct ≥1 evidence (RR-5). |
| `CR-19` | any `SecurityConstruct` `tracesTo` anchor | **1 : 1** | Exactly one closed No-Orphan lineage (RR-6; USL-011). |
| `CR-20` | entity `isA` super-entity | **1 : 1** | Single inheritance (IH-1). |

**Cardinality rules:**
- **CD-1 Totality.** Every relationship has a fixed cardinality; none is left unbounded where an invariant requires bounding.
- **CD-2 Minimal-on-ambiguity.** Where a cardinality could be read two ways, the most restrictive (default-deny) reading governs (USL-005).
- **CD-3 Mandatory presence.** Cardinalities with lower bound ≥1 (`1`, `1..*`) are existence-mandatory: absence violates the entity's well-formedness (existence rules — §52).

---

## SECTION 50 — SEMANTIC CONSTRAINT MODEL

This section **consolidates** the semantic constraints distributed across the per-concern ontologies into a single decidable constraint model. Each constraint is decidable from immutable evidence and total (default-deny on ambiguity) (DP-6; USL-005/012). The rule families **Existence · Authority · Trust · Evidence · Dependency · Evolution** are stated in full in §52–§55 and §56–§57; this section fixes the **structural** constraint model and the master invariant register that those rule families draw upon.

### 50.1 Constraint families (overview)

| Family | Governs | Fixed in |
|--------|---------|----------|
| **Cardinality constraints** | how many of each relationship (`CR-01…20`) | §49 |
| **Inheritance constraints** | single-root, single-super, acyclic (`IH-1…6`) | §45 |
| **Composition constraints** | existence-coupling, downward-acyclic (`CO-1…4`) | §46 |
| **Aggregation constraints** | independent members, restrictive composition (`AG-1…5`) | §47 |
| **Association constraints** | typed, direction, non-mutating (`AS-1…5`) | §48 |
| **Existence constraints** | what must exist for an entity to be well-formed | §52 |
| **Authority constraints** | non-mintage, boundedness, SoD | §53 |
| **Trust constraints** | non-intrinsic, evidenced, scoped, re-verified | §54 |
| **Evidence constraints** | immutable, attributable, deterministic, secret-free, absence-is-deny | §55 |

### 50.2 Master semantic invariant register (`ONT-INV-*`)

The ontology-level invariants every conforming construct SHALL satisfy (aggregating the per-concern invariants and the theory invariants SECURITY-002 INV-1…9):

| Invariant | Statement | Basis |
|-----------|-----------|-------|
| **ONT-INV-1 Single-Root Existence** | Every security entity `⊑ SecurityConstruct ⊑ ENG-002::Object`; nothing exists outside the root. | FP-2; IH-2 |
| **ONT-INV-2 Typed & Identified** | Every entity is typed (ENG-004) and identified (ENG-001) with deterministic value (ENG-003). | USL-003; FP-1 |
| **ONT-INV-3 Single Inheritance, Acyclic** | Each entity `isA` exactly one direct super; the `isA` graph is a DAG. | IH-1/IH-3 |
| **ONT-INV-4 Acyclic Founding** | The union of founding relations is a DAG — no cycle/upward/forward edge. | RM-2; SECURITY-002 INV-6 |
| **ONT-INV-5 Non-Mutating Evaluation** | Every evaluative association references without mutating. | RM-3; SECURITY-002 INV-7 |
| **ONT-INV-6 Default-Deny Totality** | Every decision/verdict is total; ambiguity/error/absence ⇒ deny. | USL-005; SECURITY-002 INV-1 |
| **ONT-INV-7 Evidence Sufficiency** | No property/relation holds without sufficient immutable evidence. | USL-012; SECURITY-002 INV-2 |
| **ONT-INV-8 Determinism** | Identical inputs yield identical verdicts and byte-identical evidence. | USL-012; SECURITY-002 INV-5 |
| **ONT-INV-9 Authority Non-Mintage** | No entity mints authority; authority is referenced, bounded, secret-free. | USL-013; SECURITY-002 INV-8 |
| **ONT-INV-10 Least Privilege & SoD** | Grants are minimal; conflicting duties/roles/authorities are partitioned. | USL-007/008 |
| **ONT-INV-11 Trust Non-Intrinsic** | No trust holds by default; every trust is constructed, scoped, evidenced, re-verified. | USL-004; SECURITY-002 INV-4 |
| **ONT-INV-12 Monotone Delegation** | Delegated authority never exceeds and only attenuates the delegator's. | SECURITY-002 INV-3; DL-INV-1/2 |
| **ONT-INV-13 Immutable Attributable Audit** | Every decision/change emits immutable, attributable, tamper-evident record. | USL-010 |
| **ONT-INV-14 Traceability Closure** | Every entity closes exactly one No-Orphan lineage to SECURITY-001. | USL-011; SECURITY-002 INV-9 |
| **ONT-INV-15 Non-Enforcement (arch layer)** | Every entity is `nonEnforcing=true`; enforcement delegated by reference. | USL-014; SECURITY-002 INV-7 |
| **ONT-INV-16 Non-Constitutive** | The ontology mints no primitive/authority/registry/identifier/lifecycle; embeds no secret. | USL-015; SECURITY-002 INV-8 |

### 50.3 Constraint model rules

- **SC-1 Decidable & total.** Every constraint is decidable from immutable evidence and total; ambiguity ⇒ deny (DP-6; USL-005/012).
- **SC-2 Complete.** The families (§50.1) cover every constraint kind the ontology admits; §52–§55 close the Existence/Authority/Trust/Evidence families.
- **SC-3 Non-overlapping.** Each constraint belongs to exactly one family; the master register (`ONT-INV-1…16`) is the single source of ontology-level invariants.
- **SC-4 Additive.** New constraints/invariants are admitted additively (`ONT-INV-17…`), never by rewrite (USL-015).

---

## SECTION 51 — DOCUMENT STATUS (ASSEMBLY CHECKPOINT — historical)

*This section recorded an intermediate assembly checkpoint during incremental authoring. It is retained for provenance only and is superseded by §58 Readiness Assessment and §59 Final Determination. The artifact is RATIFIED (see §59).*



---

## SECTION 52 — EXISTENCE RULES

The existence rules fix **what must exist** for a security entity to be well-formed. Each is decidable from immutable evidence and total; failure to satisfy any existence rule renders the construct **ill-formed** and its asserted property **denied** (default-deny — USL-005; ONT-INV-6).

| Rule | Statement | Basis |
|------|-----------|-------|
| **EX-1 Rooted existence** | An entity exists as a security construct only if it `isA` (transitively) `SecurityConstruct ⊑ ENG-002::Object`; nothing exists outside the root. | ONT-INV-1; FP-2 |
| **EX-2 Identified & typed** | An entity exists only if it bears an ENG-001 `id` and an ENG-004 `type`; an unidentified or untyped construct does not exist in the ontology. | ONT-INV-2; A-01/A-02 |
| **EX-3 Mandatory-attribute presence** | An entity is well-formed only if it bears all mandatory core attributes (`A-01…A-09`); a missing mandatory attribute renders it ill-formed. | §44.1; DP-5 |
| **EX-4 Single-super existence** | An entity exists in the hierarchy only via exactly one direct super-entity (`isA`, cardinality 1); a construct with zero or multiple direct supers does not exist. | IH-1; CR-20 |
| **EX-5 Lineage existence** | An entity exists only if it closes exactly one `tracesTo` No-Orphan lineage to SECURITY-001 and the frozen anchors; an orphan construct does not exist. | ONT-INV-14; RR-6; CR-19 |
| **EX-6 Evidence existence** | A verdict-bearing or property-asserting entity holds its property only if ≥1 immutable `Evidence` exists (`evidences`, cardinality 1..*); absent evidence, the property does not exist (is denied). | ONT-INV-7; RR-5; CR-18 |
| **EX-7 Scope existence** | A grant/relation/capacity entity exists only within a declared bounded `scope`; an unscoped grant does not exist (it is denied). | USL-007; A-04 |
| **EX-8 Partition existence** | A non-abstract entity exists only as exactly one of `SecuritySubject` or `SecurityObject` (exhaustive, disjoint). | PR-1/PR-2/PR-3 |
| **EX-9 Non-mintage existence** | No entity brings into existence a new primitive, authority, registry, identifier scheme, or lifecycle; such a construct is void. | ONT-INV-16; USL-015 |

**Existence closure.** EX-1…EX-9 are complete over the existence conditions of the ontology and non-overlapping; a construct satisfying all nine is well-formed with respect to existence. Any future existence rule is admitted additively (EX-10…), never by rewrite (USL-015).

---

## SECTION 53 — AUTHORITY RULES

The authority rules fix how **capacity to decide or permit** is admitted. Authority is always referenced, never minted (USL-013; AUTH-06; ONT-INV-9).

| Rule | Statement | Basis |
|------|-----------|-------|
| **AR-1 Non-mintage** | No security entity mints authority; every `Authority` is `resolvedFrom` a referenced frozen lower construct and/or explicit `Policy`. | ONT-INV-9; AU-INV-1; T-Auth-1 |
| **AR-2 Bounded capacity** | Every authority is bounded by an explicit `boundedScope` (extent, action-class, duration); unbounded authority is void. | AU-INV-2; T-Auth-2 |
| **AR-3 Policy-conferred** | Every authority is `conferredBy` exactly one explicit `Policy`; authority absent a conferring policy does not exist. | AU-INV-2; CR-07 basis |
| **AR-4 Separation of duties** | No single authority both grants and exercises a critical action, nor both acts and audits it; conflicting authorities/roles are partitioned (`separatedFrom`). | ONT-INV-10; AU-INV-3; USL-008 |
| **AR-5 Least privilege** | Every grant (permission/privilege/role) is the minimum sufficient, bounded in scope, extent, and duration; no standing/ambient over-privilege. | ONT-INV-10; PV-INV-1/PV-INV-2; USL-007 |
| **AR-6 Monotone delegation** | Delegated authority never exceeds and only attenuates the delegator's authority; every delegation records a traceable chain to origin authority and is revocable. | ONT-INV-12; DL-INV-1/2/3/4 |
| **AR-7 Explicit authorization** | Every access derives from an explicit, decidable `Authorization` referencing (principal, resource, action, context, policy); default is deny. | AZ-INV-1/AZ-INV-2; USL-005/006 |
| **AR-8 Secret-free authority** | No authority, permission, privilege, role, or delegation embeds secret/credential/key material. | USL-013; AU-INV-4; AM-3 |

**Authority closure.** AR-1…AR-8 are complete over the authority conditions and non-overlapping; additive-only (AR-9…) (USL-015).

---

## SECTION 54 — TRUST RULES

The trust rules fix how **reliance** is admitted. Trust is never intrinsic (USL-004; ONT-INV-11).

| Rule | Statement | Basis |
|------|-----------|-------|
| **TRR-1 Non-intrinsic** | No `Trust` holds by default; every trust relation is explicitly constructed. Absence of an established, evidenced trust relation is distrust (default-deny). | ONT-INV-11; TR-INV-1; USL-004/005 |
| **TRR-2 Evidence basis** | Every `Trust` has a decidable `basisRef` to immutable `Evidence`; trust without evidence does not hold. | TR-INV-2; T-Trust-2; USL-012 |
| **TRR-3 Scope confinement** | Trust conferred for one scope does not transfer to another; no scope creep. | TR-INV-3; T-Trust-3 |
| **TRR-4 Continuous re-verification** | Trust decays over time/context and is continuously re-verified (`reVerifiedBy`); expiry defaults to distrust. | TR-INV-4; T-Cont-1; USL-004 |
| **TRR-5 Explicit anchoring** | Every `Trust` `derivesFrom` ≥1 explicitly declared, evidenced `TrustAnchor`; unanchored trust does not hold. | TR-INV-5; A-Trust-2 |
| **TRR-6 Boundary default-deny** | Cross-`Boundary` interaction requires an explicit, typed, evidenced, policy-governed crossing; otherwise the crossing is denied. | BD-INV-2; A-Bnd-2; USL-005 |
| **TRR-7 Directional & bounded** | Every `Trust` is directional (single subject, single object) and time-bounded by a `validityWindow`. | TR-INV-1; CR-09 |

**Trust closure.** TRR-1…TRR-7 are complete over the trust conditions and non-overlapping; additive-only (TRR-8…) (USL-015).

---

## SECTION 55 — EVIDENCE RULES

The evidence rules fix how **assurance** is grounded. A property holds only insofar as decidable from immutable evidence (USL-012; ONT-INV-7).

| Rule | Statement | Basis |
|------|-----------|-------|
| **ER-1 Evidence-first** | A security property/relation holds exactly to the strength of its evidence; no evidence ⇒ no property (denied). | ONT-INV-7; EV-INV-1/EV-INV-4; T-Ev-1/T-Ev-4 |
| **ER-2 Immutability** | Evidence and audit records are append-only and tamper-evident (hash-chained); no in-place mutation. | ONT-INV-13; EV-INV-5; AD-INV-1; USL-010 |
| **ER-3 Attribution** | Every `Evidence`/`AuditRecord` binds to a responsible `Principal` (accountability, non-repudiation). | AD-INV-2/AD-INV-3; USA-4 |
| **ER-4 Determinism** | Identical inputs produce byte-identical evidence and content hash; every verdict is reproducible. | ONT-INV-8; EV-INV-2; USL-012 |
| **ER-5 Secret-free** | Evidence embeds no secret/credential/key material; it records classes, hashes, and references only. | EV-INV-3; USL-013; AM-3 |
| **ER-6 Reconstructability** | The audit trail suffices to reconstruct and attribute any recorded decision or state change. | AD-INV-3; T-Aud-3 |
| **ER-7 Aggregation-not-rejudgement** | Compliance/certification verdicts aggregate evidence deterministically; they do not re-judge, and they close scope, not evolution. | CM-INV-1/CM-INV-2; T-Cmp-1/T-Cmp-2 |
| **ER-8 Absence-is-deny** | Absence of required evidence is treated as absence of the property; the dependent decision defaults to deny. | ONT-INV-6; EV-INV-4; USL-005 |

**Evidence closure.** ER-1…ER-8 are complete over the evidence conditions and non-overlapping; additive-only (ER-9…) (USL-015).

---

## SECTION 56 — DEPENDENCY MODEL

The dependency model fixes the ontology's relationship to every architectural layer, **strictly by downward-only reference** (USL-001/002; SECURITY-001 §17/§18; SECURITY-002 §23/§25). All dependency edges are founding associations (`dependsOn`/`references`) and form a DAG (ONT-INV-4; RR-3).

### 56.1 Canonical layer stack (downward-only)

```
Existence (EL-1)  →  Reality/Behavior (RL-F2)  →  Platform (PL-F2)  →  Data (DF-2)
   →  Service (SF-2)  →  Application (AF-3)  →  Infrastructure (Band-13, IF-3)  →  SECURITY (PHASE-008, this ontology)
   →  [Implementation (PHASE-009) · Operations · Governance : downstream/orthogonal, non-binding forward references]
```

### 56.2 Relationship to each layer (reference-only)

| Layer | Ontology's downward relationship (reference-only; redefines none) |
|-------|-------------------------------------------------------------------|
| **Existence (EL-1)** | Every entity IS an `ENG-002::Object`, identified (ENG-001), typed (ENG-004), valued (ENG-003), referenced (ENG-005). The ontology's root `SecurityConstruct ⊑ ENG-002::Object`. Redefined never. |
| **Reality / Behavior (RL-F2)** | The ontology names what authorization/policy/control **mean** and delegates all enforcement to RL-F2 runtime mechanisms **by reference** (`nonEnforcing = true`; USL-014; ONT-INV-15). |
| **Platform (PL-F2)** | References the platform security service (`platform/security`) and composition constructs as evaluated targets; re-owns neither. |
| **Data (DF-2)** | References data representation for evidence/audit/attestation **semantics** (immutability, attribution, determinism); re-owns no representation. |
| **Service (SF-2)** | References service operation as a secured/evaluated target; performs no operation. |
| **Application (AF-3 / APPLICATION-013)** | References the Application Security architecture as an upstream-secured domain; the cross-cutting assurance ontology reasons above it, redefining none. |
| **Infrastructure (Band-13, U01–U10; IF-3)** | Founds directly on the frozen Infrastructure Baseline; references isolation boundaries (U05), availability/resilience topology (U07), and the infrastructure security facet (U08) **by reference**; re-owns none. |
| **Implementation (PHASE-009)** | Downstream. Realizations may instantiate this ontology by reference. **Non-binding forward reference.** |
| **Operations** | Downstream/operational. Consumes the ontology's assurance/evidence model; the ontology performs no operation. **Non-binding forward reference.** |
| **Governance** | Security governance evaluates conformance to this ontology (record-only under ENG-000), reusing the Infrastructure governance facet by reference; enforces nothing (USL-014). |

### 56.3 Dependency rules

- **DEP-1 Downward-only.** The ontology references only frozen layers beneath it and intra-domain predecessors (SECURITY-GOV-000, SECURITY-001, SECURITY-002). No upward or forward founding dependency.
- **DEP-2 Reuse-by-reference.** Every lower-layer construct is consumed strictly by reference; nothing re-implemented, re-owned, or duplicated (USL-002).
- **DEP-3 Acyclic.** The founding/dependency graph is a DAG (ONT-INV-4; RR-3; DP-4).
- **DEP-4 No duplicated ownership.** The ontology owns only the assurance-domain semantics; it re-owns no lower capability/registry/engine/lifecycle (SECURITY-001 §17).
- **DEP-5 Non-binding forward references.** References to Implementation/Operations (PHASE-009+) are non-binding; those layers do not yet constrain this ontology.
- **DEP-6 Frozen-input immutability.** All referenced lower layers are consumed as immutable inputs; the ontology neither modifies nor reinterprets any of them.

---

## SECTION 57 — ONTOLOGY EVOLUTION RULES

The ontology evolves under strict non-constitutive discipline (USL-015; AUTH-INF-001; UCI-001; ONT-INV-16).

| Rule | Statement |
|------|-----------|
| **EVR-1 Append-only** | New entities, relationships, attributes, constraints, invariants, and rules are **added** (`ONT-E-33…`, `R-36…`, `A-10…`, `ONT-INV-17…`, `EX-10…`, `AR-9…`, `TRR-8…`, `ER-9…`), never by rewriting existing definitions. |
| **EVR-2 Supersession-only** | A changed entity/relationship is superseded by a new versioned artifact or additive definition; the prior definition is retained (never deleted in place). |
| **EVR-3 Backward traceability mandatory** | Every addition or supersession records a backward `tracesTo` lineage to what it extends or supersedes, closing to SECURITY-001 (USL-011). |
| **EVR-4 No constitutional mutation** | This ontology is subordinate to SECURITY-001/002 and may never contradict a USL, axiom, or theorem; conflicts resolve in favor of the higher instrument, and the conflicting statement is void to the extent of the conflict. |
| **EVR-5 Non-constitutive** | Evolution mints no new primitive, authority, registry system, identifier scheme, or lifecycle, and embeds no secret (ONT-INV-16; USL-013/015). |
| **EVR-6 Non-terminal & unbounded** | Per AUTH-INF-001, the ontology is never TERMINAL; entity/relationship numbering is sequence, not ceiling; scope is current-authorized, not maximum. |
| **EVR-7 Deterministic re-derivation** | Every superseding version re-derives its verdicts deterministically from immutable evidence; identical inputs yield identical results (ONT-INV-8). |
| **EVR-8 Downstream fixation deference** | Partition/coverage closure (SECURITY-004) and meta-model well-formedness/instantiation (SECURITY-005) are fixed downstream; this ontology frames but does not pre-empt them, and evolves consistently with them. |

---

## SECTION 58 — READINESS ASSESSMENT

| Gate | Result |
|------|--------|
| Founded downward-only on frozen substrate (SECURITY-002/001 + full stack + Infrastructure Baseline) | ✅ |
| Purpose · overview · foundational principles (`FP-1…10`) · scope · boundaries · design principles (`DP-1…10`) defined | ✅ |
| Root entity model (`SecurityConstruct` + Subject/Object partitions) + root relationships (4 kinds) fixed | ✅ |
| Complete entity catalog (`ONT-E-01…32`) covering all 25 constitutional concepts + Role + Vulnerability | ✅ |
| All 25 mission-listed per-concern ontologies defined (Identity → Recovery) | ✅ |
| Object-type families (7) + Subject-type archetypes fixed | ✅ |
| Consolidated Relationship (`R-01…35`), Attribute (`A-01…09`), Inheritance, Composition, Aggregation, Association models fixed | ✅ |
| Cardinality rules (`CR-01…20`) + Semantic Constraint model + master invariant register (`ONT-INV-1…16`) fixed | ✅ |
| Existence (`EX-1…9`), Authority (`AR-1…8`), Trust (`TRR-1…7`), Evidence (`ER-1…8`) rules fixed | ✅ |
| Dependency model (downward-only to Existence/Reality/Platform/Data/Service/Application/Infrastructure/Implementation/Operations/Governance) fixed | ✅ |
| Ontology evolution rules (`EVR-1…8`; append-only, supersession-only, backward traceability) fixed | ✅ |
| Implementation-independent · technology/vendor/algorithm/cloud/platform-neutral | ✅ |
| No duplication of Infrastructure or any lower layer (reuse-by-reference only); mints no primitive/authority/registry/identifier/lifecycle | ✅ |
| Frames but does not pre-empt SECURITY-004 (Taxonomy closure) / SECURITY-005 (Meta-Model) | ✅ |
| STATUS-001 R1–R5 conformance | ✅ (self-check below) |

---

## SECTION 59 — FINAL DETERMINATION

The Universal Security Ontology is complete, coherent, implementation-independent, technology-neutral, founded downward-only by reference on SECURITY-002/SECURITY-001 and the frozen substrate, non-duplicating, and STATUS-001-conformant. It fixes the canonical semantic universe of the SECURITY domain: the authoritative vocabulary, the complete entity catalog (`ONT-E-01…32`), the entity/subject/object type models, all 25 per-concern ontologies, the consolidated relationship/attribute/inheritance/composition/aggregation/association models, the cardinality rules, the master semantic invariant register (`ONT-INV-1…16`), the existence/authority/trust/evidence rule families, the downward-only dependency model, and the append-only evolution rules — instantiating SECURITY-001 §7 and SECURITY-002 without amending either, and deferring taxonomy/meta-model closure to SECURITY-004/005.

> ## SECURITY-003 — UNIVERSAL SECURITY ONTOLOGY — **RATIFIED**
> (roadmap-governance ratification; authoritative semantic universe for every future `SECURITY-*` artifact; subordinate to SECURITY-002, SECURITY-001, the frozen corpus, and AUTH-INF-001; non-constitutive at the EC level.)

**Roadmap progress:** SECURITY 3 (SECURITY-003 of the authorized foundation chain 001…005). **Next artifact:** SECURITY-004 (Universal Security Taxonomy).

---

## SECTION 60 — IMPLEMENTATION NOTES

These notes are **non-normative**; they record the assembly, normalization, and registration provenance of this artifact and bind nothing (ID-01, AUTH-06).

- **Incremental assembly.** This artifact was assembled under the UCOS Large Artifact Protocol as seven append-only parts (foundation → per-concern ontologies → consolidated models → rules/dependency/evolution/determination), each verified for append-only integrity between steps, to remain resilient to session interruption. On completion the document was **normalized** into this single canonical artifact and the transient inter-part scaffolding (PART dividers and per-part completion markers) was removed; the substantive section content was preserved verbatim.
- **REG-AUTO-001 invariant.** Per the repository's canonical automation, *artifact creation causes registration*: the `PostFileCreate` hook (`.kiro/hooks/auto-register-artifact.json`) fired `register.sh` on first creation, allocating registry identity **`UCOS-SEC-000004`** and synchronizing the Artifact Registry, Page Registry, Volume Registry, Knowledge-Graph, Control Tower, and Digital Twin. This registration was preserved across all subsequent parts.
- **Metadata-driven registration.** Registration is driven by the artifact's self-declared front-matter (`PROGRAM = SECURITY`, `CATEGORY = SEC`, `VOLUME = VOL-023`, `FAMILY = SECURITY-FOUNDATION`); no generator hard-coding is required (AUTH-INF-001 infinite expansion; REG-AUTO-001 metadata classification).
- **No runtime behavior.** This artifact introduces no code, no runtime, no enforcement, and selects no technology/algorithm/vendor. Every enforcement reference is delegated by reference to already-frozen, certified lower-layer mechanisms (USL-014).
- **Verification.** Final ratification is accompanied by `register.sh --guard` PASS and `verify.sh` PASS with the repository CLEAN and Registry/Portal/Control-Tower/Digital-Twin synchronized (recorded in the commit that seals this artifact).

---

## STATUS-001 VALIDATION SELF-CHECK (§5, R1–R5)

| Rule | Result | Evidence |
|------|--------|----------|
| **R1 Declaration** | ✅ | STATUS DOMAIN (ROADMAP EXECUTION — FOUNDATION) + BASIS declared at head. |
| **R2 Domain isolation** | ✅ | Ontology-only; no operational/enforcement/technology projection; lower layers consumed as immutable inputs by reference. |
| **R3 Claim completeness** | ✅ | Claim (SECURITY-003 exists; RATIFIED; 3 of foundation chain 001…005) supplies domain, unit, evidence source, registry basis (SECURITY-002; `UCOS-SEC-000004`), completion basis. |
| **R4 Evidence physicality** | ✅ | Rests on physical SECURITY-002/SECURITY-001 + frozen Infrastructure Baseline (`1951c72`) + frozen stack + this file. |
| **R5 Append-only** | ✅ | New file in `14-SECURITY/`; no constitution, frozen artifact, Band-13/Infrastructure artifact, or numbering modified; REG-AUTO-001 append-only registration; supersession-only evolution (UCI-001; AUTH-INF-001). |

**SECURITY-003 — UNIVERSAL SECURITY ONTOLOGY — RATIFIED · ACTIVE; AUTHORITATIVE SEMANTIC UNIVERSE FOR SECURITY-*; NEXT ARTIFACT: SECURITY-004 (UNIVERSAL SECURITY TAXONOMY).**
