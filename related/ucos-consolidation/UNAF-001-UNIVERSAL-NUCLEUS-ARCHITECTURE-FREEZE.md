# UNAF-001 — Universal Nucleus Architecture Freeze

**Checkpoint commit:** `00bd45f` (integration/recovery-001)
**Determination date:** 2026-08-06
**Authority:** Repository Truth is absolute. Every conclusion herein is grounded in a cited Repository Truth artifact. No claim is asserted without evidence.
**Constitutional posture:** No redesign. No parallel authority. No duplication. Every determination is REUSE, EXTEND, or CREATE (CREATE only where Repository Truth proves no canonical owner exists).

---

## Preamble

Production Foundation is frozen at checkpoint `873ef19` / `00bd45f`. Seven Ω Nuclei are implemented, verified, constitutionally complete, and maturity-100% on all axes. This document freezes the Universal Nucleus Architecture upon which every future Platform, Product, Application, Enterprise, and Ecosystem will be generated.

This programme does NOT redesign the Foundation. It constitutionally determines what a Nucleus is, what contract it must satisfy, what taxonomy of Nuclei exists, and in what order the remaining Foundation phases and subsequent domain Nuclei must be implemented.

---

## DELIVERABLE 1 — Universal Nucleus Architecture

### 1.1 Definition (Repository Truth: `00-MASTER/UCOS-NUCLEUS-001/02-NUCLEUS-CONSTITUTIONAL-MODEL.md`)

A **Universal Nucleus** is the **complete constitutional universe of exactly one canonical concept**. It is the atomic unit of canonical ownership.

```
Nucleus(concept) ≡ Universe/concern-unit(concept)
```

This is a **REFINEMENT**, not a new concept. `MCP-001-MASTER-CONTEXT.md` already defines:
*"28 Constitutional Universes (U01–U28) — exactly one canonical instance per fundamental concern; no universe owns another."* That rule IS the Nucleus definition. The term "Nucleus" attaches a formal completeness contract (NF-01..NF-36) and a Zero-Finite contract to each existing concern-unit; it renames nothing on disk.

**A Nucleus SHALL be:**

- Constitutionally complete · independently governable · independently evolvable
- Independently certifiable · independently discoverable · independently composable
- Independently configurable · independently reusable
- Implemented once · reusable infinitely · Zero-Finite

**A Nucleus SHALL NOT be:**

- A module, microservice, bounded context, or implementation artifact
- A Universe (a Universe is a GOVERNED COMPOSITION of Nuclei — see §1.4)
- A Platform (a Platform is CONFIGURATION of Nuclei/Universes — see §1.4)

### 1.2 Nucleus Meta-Model (Repository Truth: `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §2)

Realized as a **profile over the existing registry substrate** (`engine/registry`, `artifact.schema.json`). Not a new store.

```
NUC-META
 ├─ nucleus_id            (= canonical concept owner id, e.g. UCOS-UFC-001, UNI-006)
 ├─ concept               (the single canonical concept)
 ├─ completeness_profile  (the NF-01..NF-36 facets — present/not-applicable with evidence)
 ├─ zero_finite_profile   (the no-assumption axes — see §1.3)
 ├─ composition_role      (standalone | composed-into-universe)
 ├─ configuration_schema  (declarative config surface — Configuration-First invariant CFG-1)
 └─ evidence_refs         (registry + certification + closure refs)
```

Meta-relationships (REUSE of existing `engine/registry/models.py` `Relationship.type`):
`composes`, `depends-on`, `references`, `governed-by`, `certified-by`, `discovered-by`, `configured-by`, `evolves-via`. No new edge primitives.

### 1.3 Nucleus Contract (Repository Truth: `platform/universal_foundation/catalog/foundation-nucleus.json`)

The permanent Universal Ω Nucleus Contract is frozen as 36 facets (NF-01..NF-36):

| # | Facet | Resolution Kind | Evidence Field |
|---|-------|-----------------|----------------|
| NF-01 | identity | DECLARATION | `identity` |
| NF-02 | universal-identifier | DECLARATION | `capability_id` |
| NF-03 | canonical-ownership | PROFILE | `ownership` |
| NF-04 | repository-truth-binding | PROFILE | `truth_binding` |
| NF-05 | constitutional-registration | GATE | FG-09-EVOLUTION-ADDITIVE |
| NF-06 | discovery | DECLARATION | `service_descriptor` |
| NF-07 | dependency-declaration | GATE | FG-12-COMPOSABLE |
| NF-08 | capability-declaration | DECLARATION | `contracts` |
| NF-09 | context-declaration | PROFILE | `context` |
| NF-10 | configuration | GATE | FG-04-POLICY-DECLARED |
| NF-11 | composition | PROFILE | `composition` |
| NF-12 | runtime-integration | GATE | FG-02-SERVICE-REGISTERED |
| NF-13 | api-generation | PROFILE | `generation.api` |
| NF-14 | cli-generation | GATE | FG-06-RUNTIME-INVOCABLE |
| NF-15 | documentation-generation | PROFILE | `generation.documentation` |
| NF-16 | test-generation | PROFILE | `generation.tests` |
| NF-17 | validation | GATE | FG-05-REGISTRY-DETERMINISTIC |
| NF-18 | verification | GATE | FG-07-LIFECYCLE-BOOTSTRAPPED |
| NF-19 | certification | GATE | FG-11-CERTIFIABLE |
| NF-20 | monitoring | PROFILE | `observability.monitoring` |
| NF-21 | measurement | PROFILE | `measurement` |
| NF-22 | observability | PROFILE | `observability.signals` |
| NF-23 | traceability | PROFILE | `traceability` |
| NF-24 | evidence | PROFILE | `evidence` |
| NF-25 | versioning | GATE | FG-08-COMPATIBILITY-DECLARED |
| NF-26 | evolution | PROFILE | `evolution` |
| NF-27 | governance | GATE | FG-10-FAIL-CLOSED |
| NF-28 | security | PROFILE | `security` |
| NF-29 | compliance | PROFILE | `compliance` |
| NF-30 | commercialization | PROFILE | `commercial.commercialization` |
| NF-31 | billing | PROFILE | `commercial.billing` |
| NF-32 | licensing | PROFILE | `commercial.licensing` |
| NF-33 | marketplace | PROFILE | `commercial.marketplace` |
| NF-34 | extensibility | GATE | FG-03-PROVIDER-PLUGGABLE |
| NF-35 | specialization | GATE | FG-13-SPECIALIZED-BY-DECLARATION |
| NF-36 | contract-surface | GATE | FG-01-CONTRACT-PUBLISHED |

**Certification rule:** a Nucleus is NUC-COMPLETE only when NF-01..NF-36 each resolve to an owner AND are CERTIFIED for that concept. Absent facets are recorded as realization scope, never silently assumed.

**Resolution kinds:** DECLARATION (named field non-empty), GATE (constitutional gate PASSED), PROFILE (dotted path in nucleus profile block with `present`+evidence or `not-applicable`+rationale). No fourth kind. An unstated facet is MISSING and blocks freeze.

### 1.4 Universe vs Nucleus vs Platform (Repository Truth: `05-PLATFORM-CONFIG-AND-UNIVERSE-COMPOSITION.md`)

These three terms are constitutionally distinct and must not be confused:

| Term | Definition | Evidence |
|------|------------|----------|
| **Nucleus** | Complete constitutional universe of exactly ONE canonical concept | `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §1 |
| **Universe** | Governed COMPOSITION of Nuclei plus configuration — not a canonical concept itself | `05-…` §1; `BUC-002` reference composition |
| **Platform** | Realizable entirely by CONFIGURING complete Nuclei/Universes — no bespoke code | `05-…` §2; `PLATFORM-010`; `EC2-EPIC-006` |

**Composition exemplar (from Repository Truth, `BUC-002`, no new content):**
```
Commerce Universe := compose(
    Product(UNI-064), Catalog(frontier), Pricing(UNI-065), Offer(frontier),
    Inventory, Order, Payment(→Currency UNI-067), Tax,
    Customer/Party(UNI-010/075/039), Supplier, Logistics, Contract,
    Workflow, Policy(CEP)
) + configuration
```

**Anti-duplication guard (Repository Truth: `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §6):**
The following are **Universes, not Nuclei:** Commerce · Retail · Marketplace · ERP · CRM · Healthcare · Government · Finance (as sector) · Education · Manufacturing.
The following are **Platform facets, not new Nuclei:** Meta-Platform · Platform Builder.

### 1.5 Zero-Finite Contract (NUC-ZF) — Conditional

A Nucleus asserts no assumption on: technology · database · language · country · planet · calendar · currency · business model · deployment · runtime · organization · any future concept.

**NUC-ZF is currently CONDITIONAL** (Repository Truth: `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §4) due to five tracked substrate constraints:

| ID | Constraint | Fix target |
|----|-----------|-----------|
| ZF-1 | `universal_id` pattern → 10⁶ ID ceiling | `artifact.schema.json` |
| ZF-2 | `volume` pattern → 1000-volume ceiling | `artifact.schema.json` |
| ZF-3 | Closed `LifecycleStatus` enum (17) | `engine/registry/models.py` + `status.schema.json` |
| ZF-4 | Closed `TRACE_STAGES` + `additionalProperties:false` | schema + `models.py` |
| ZF-5 | Closed `DiscoveryKind` enum | `engine/discovery/contracts.py` |

ZF-1..ZF-5 are the ONLY items requiring code change. All Nucleus content is registration/configuration.

---

## DELIVERABLE 2 — Universal Nucleus Taxonomy

### 2.1 Constitutional Classification Rules

Every entry in this taxonomy is classified as:
- **REUSE** — canonical owner exists and is sufficient; reference only
- **EXTEND** — canonical owner exists; attach Nucleus completeness/ZF profile + realization scope
- **CREATE** — no owner found after exhaustive Repository Truth search (Repository Truth: `01-REPOSITORY-IMPACT-AND-GAP-ANALYSIS.md` §1)
- **UNIVERSE** — a governed composition of Nuclei, NOT a Nucleus; creation of a "Nucleus" here would violate `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §6

CREATE is constitutionally forbidden unless Repository Truth proves no owner exists.

### 2.2 Layer 0 — Foundation Ω Nuclei (IMPLEMENTED, production-ready)

Source: `OMEGA-NUCLEUS-IMPLEMENTATION-INVENTORY.md`, `PRODUCTION-FOUNDATION.md` §4

| Nucleus ID | Name | Package | Class | State |
|-----------|------|---------|-------|-------|
| UCOS-URTF-001 | Universal Repository Truth Framework | `platform.universal_truth` | REUSE | IMPLEMENTED · CONFORMANT · COMPLETE |
| UCOS-UOF-001 | Universal Ownership Framework | `platform.universal_ownership` | REUSE | IMPLEMENTED · CONFORMANT · COMPLETE |
| UCOS-USAF-001 | Universal Source Assimilation Framework | `platform.universal_assimilation` | REUSE | IMPLEMENTED · CONFORMANT · COMPLETE |
| UCOS-UMPF-001 | Universal Measurement Policy Framework | `platform.universal_measurement` | REUSE | IMPLEMENTED · CONFORMANT · COMPLETE |
| UCOS-UFC-001 | Universal Foundation Constitution | `platform.universal_foundation` | REUSE | IMPLEMENTED · CONFORMANT · sole constitutional authority |
| UCOS-UFP-001 | Universal Foundation Platform | `platform.universal_foundation` | REUSE | IMPLEMENTED · CONFORMANT · COMPLETE |
| UCOS-UNG-001 | Universal Ω Nucleus Generator | `platform.universal_generator` | REUSE | IMPLEMENTED (plan/readiness; write phase pending) |

### 2.3 Layer 1 — Foundation Infrastructure Nuclei (to implement, roadmap phases 1–6)

Source: `PRODUCTION-ROADMAP.md`

| Nucleus | Name | Class | Owner |
|---------|------|-------|-------|
| UCKP-REG | Ω Nucleus Registry | EXTEND | `platform.universal_foundation` capability register; `load_capability_register` |
| UCKP-DIS | Ω Nucleus Discovery | EXTEND | `platform.repository_intelligence.discovery`; `engine.discovery` |
| UCKP-CMP | Ω Nucleus Composition | EXTEND | composition engine; `bootstrap.*`; `service_register`; FZ-10 total order |
| UCOS-UNG-001 (write) | Universal Generator — execution phase | EXTEND | `platform.universal_generator` (plan already implemented) |
| UCKP-RUN | Universal Runtime | EXTEND | per-nucleus CLIs; `engine/` runtime primitives |
| UCKP-PLT | Universal Platform Composition | EXTEND | platform packages + verification pipeline |

### 2.4 Layer 2 — Foundational / Cross-Cutting Nuclei

Source: `03-CANONICAL-NUCLEI-CATALOG-AND-OWNERSHIP.md` §2. All EXTEND — owners exist.

| Nucleus | Canonical Owner | Class |
|---------|----------------|-------|
| Identity Nucleus | `UNI-010` + `ENG-001` + `id-ledger.json` | EXTEND |
| Space / Geography / Location Nucleus | `UNI-005`; `UNI-053/054/055/056` | EXTEND |
| Time Nucleus | `UNI-006` (`DOM-0020`, `CAP-0083..0087`) | EXTEND |
| Calendar Nucleus | `DOM-0021` (dep `DOM-0020`) | EXTEND |
| Scale Nucleus | `UNI-007` | EXTEND |
| Observer / Perspective Nucleus | `UNI-008` / `UNI-009` | EXTEND |
| Reality Nucleus | `UNI-011` | EXTEND |
| Meaning / Values Nucleus | `UNI-012` / `UNI-013` | EXTEND |
| Language / Communication Nucleus | `UNI-037/038/039` (`DOM-0170..0173`) | EXTEND |
| Value / Currency Nucleus | `UNI-067` + `ENG-003` | EXTEND |
| Knowledge / Memory / Intelligence Nucleus | `UNI-027/028/029` + `engine/knowledge` + `intelligence/` | EXTEND |
| Organization Nucleus | `UNI-075` | EXTEND |
| Policy / Rules / Governance Nucleus | `CEP` policy layer + `engine/governance` | EXTEND |
| Workflow Nucleus | `RUNTIME` workflow + reference-universe Workflow layer | EXTEND |
| Event Nucleus | reference-universe Event layer + `RUNTIME-008` | EXTEND |

### 2.5 Layer 3 — Commerce-Domain Nuclei

Source: `03-CANONICAL-NUCLEI-CATALOG-AND-OWNERSHIP.md` §3; `BUC-002`. All EXTEND — owners exist.

| Nucleus | Canonical Owner | Class |
|---------|----------------|-------|
| Product Nucleus | `UNI-064` (Product, Variant, Attribute-set, LifecycleState) | EXTEND |
| Catalog Nucleus | `UNI-064` + Taxonomy `UNI-036` + SearchIndex | EXTEND |
| Pricing Nucleus | `UNI-065` (PriceModel, PriceBook, DiscountRule, DynamicPricingPolicy) | EXTEND |
| Offer / Promotion Nucleus | `DOM-0283` Discounts + Product + Pricing frontier | EXTEND |
| Inventory Nucleus | Product + Location reference | EXTEND |
| Order Nucleus | order concern reference composition | EXTEND |
| Cart Nucleus | Order frontier (pre-submission state) | EXTEND |
| Checkout Nucleus | Order + Payment frontier | EXTEND |
| Payment Nucleus | `UNI-067` Currency + order concern | EXTEND |
| Billing Nucleus | `commercial.billing` facet; Payment + Order | EXTEND |
| Tax Nucleus | Value/Currency over Order/Payment | EXTEND |
| Invoice Nucleus | Billing + Order frontier | EXTEND |
| Shipment Nucleus | Logistics/Fulfilment over Order + Location | EXTEND |
| Logistics / Fulfilment / Return / Refund Nucleus | Logistics concern over Order + Location + Workflow | EXTEND |
| Warehouse Nucleus | Location + Inventory frontier | EXTEND |
| Contract Nucleus | Party + Policy concern | EXTEND |
| Customer / Party Nucleus | `UNI-010/105` + `UNI-075` + `UNI-039` | EXTEND |
| Supplier Nucleus | Party specialization (`DOM-0275/0276` roles) | EXTEND |

### 2.6 Layer 4 — Sector / Vertical Nuclei (Universes — governed compositions)

These are **Universes** (governed compositions of Nuclei), not Nuclei themselves. Authoring them as "Nuclei" would create a parallel canonical instance, violating `CMG-INV-02` (no parallel authority).

| Name | Constitutional Classification | Owner |
|------|------------------------------|-------|
| Marketplace | UNIVERSE | `PLATFORM-010` + `BUC-002` composition |
| Commerce | UNIVERSE | `BUC-002` reference composition |
| CRM | UNIVERSE | Party + Workflow + Communication composition |
| ERP | UNIVERSE | Organization + Finance + Inventory + Order + Workflow composition |
| HR | UNIVERSE | Organization + Identity + Policy composition |
| Finance (sector) | UNIVERSE | Value/Currency + Order/Payment/Billing composition |
| Banking | UNIVERSE | Finance Universe + Identity + Contract |
| Insurance | UNIVERSE | Finance Universe + Policy + Risk |
| Healthcare | UNIVERSE | Organization + Identity + Policy + Compliance composition |
| Education | UNIVERSE | Organization + Knowledge + Identity composition |
| Government | UNIVERSE | Organization + Identity + Policy + Compliance composition |
| Manufacturing | UNIVERSE | Organization + Inventory + Workflow + Logistics composition |

### 2.7 Layer 5 — Platform-Capability Nuclei

| Nucleus | Canonical Owner | Class |
|---------|----------------|-------|
| AI / Intelligence Nucleus | `UNI-029 Intelligence` + `intelligence/` | EXTEND |
| Agent Nucleus | AI + Workflow frontier | EXTEND |
| Runtime Nucleus | `engine/runtime`; `RUNTIME-*`; `UCOS-UFP-001` | REUSE |
| Infrastructure Nucleus | `platform/` infrastructure packages | EXTEND |
| Security Nucleus | `platform/security` + `14-SECURITY` | EXTEND |
| Governance / Constitutional Nucleus | `CEP-002` + `engine/governance` + `UFC-001` | REUSE |
| Notification Nucleus | Communication + Event frontier | EXTEND |
| Communication Nucleus | `UNI-037/038/039` | EXTEND |
| Search Nucleus | Catalog + Knowledge frontier | EXTEND |
| Analytics Nucleus | Measurement + Knowledge + Intelligence | EXTEND |
| Reporting Nucleus | Analytics + Document frontier | EXTEND |
| Monitoring Nucleus | `platform/observability` | EXTEND |
| Observability Nucleus | `platform/observability` | EXTEND |
| Document / Content Nucleus | Content concern + Registry | EXTEND |
| Localization Nucleus | Language/Communication + Calendar + Identity | EXTEND |
| Accessibility Nucleus | Identity + UX frontier | EXTEND |
| Branding / Theme / UI / UX Nucleus | `PLATFORM-005` meta-model facets | EXTEND |
| API Nucleus | `UCOS-URTF-001` + `engine/foundation/contracts` | REUSE |
| Integration Nucleus | `UCOS-USAF-001` assimilation framework | REUSE |
| Configuration Nucleus | `PLATFORM-010` + `EC2-EPIC-006` blueprint catalog | EXTEND |
| Commercialization Nucleus | `commercial.*` facets (NF-30..NF-33) of existing nuclei | EXTEND |

### 2.8 Candidate CREATE

| Nucleus | Reason | Adjudication |
|---------|--------|-------------|
| Commission Nucleus | No owner found via `grep 02-MASTER/** commission` | **CREATE\*** only if Reuse-First vs `UNI-065`/`DOM-0283`/`DOM-0284` confirms distinctness. If Commission is a value-distribution model distinct from price formation → NEW domain under Value/Commerce universe. Otherwise EXTEND Pricing. |
| Nucleus Primitive (formal) | `GAP-1` — formalization gap | **EXTEND** `S2-03-UNIVERSE-FOUNDATION-BINDING` + CEP-009 amendment. Not standalone CREATE. |

---

## DELIVERABLE 3 — Canonical Owner Matrix (Compressed)

Full matrix at: `02-CANONICAL-OWNERSHIP-MATRIX.md` (71 rows). Key entries below.

| Concept Domain | Canonical Owner | Repository Location | Status |
|----------------|-----------------|---------------------|--------|
| Platform (constitution/theory) | PLATFORM-001 / PLATFORM-002 | `09-PLATFORM/` | OWNED |
| Platform meta-model | PLATFORM-005 | `09-PLATFORM/` | OWNED |
| Platform composition | PLATFORM-010 | `09-PLATFORM/` | OWNED |
| Foundation architecture | IMP-001 | `06-IMPLEMENTATION/` | OWNED |
| Repository architecture | IMP-002 | `06-IMPLEMENTATION/` | OWNED |
| Blueprint / Platform Blueprint | EC2-EPIC-006 | `06-IMPLEMENTATION/` | OWNED |
| Universal compiler | UCOS-Ω∞-UNIVERSAL-COMPILER | `06-IMPLEMENTATION/` | OWNED |
| Universe model | S2-03 + ARCH-001 (112 capabilities) | `00-CEP/` | OWNED |
| Registry federation | S2-02 + REGISTRY-PLATFORM | `00-CEP/`; `06-IMPLEMENTATION/` | OWNED |
| Canonical registries | `00-BOOK/REGISTRIES/*` | `00-BOOK/REGISTRIES/` | OWNED |
| Context Assimilation Gate | USIS-WAVE1 framework | `00-MASTER/UCOS-USIS-WAVE1/` | OWNED |
| Canonical Ownership / Knowledge Once | RA-003 + closure engine + CEP-001 | `00-MASTER/RA-003/`; `00-CEP/` | OWNED |
| Ontology / taxonomy | per-family `*-003`/`*-004` + ONTOLOGY-REGISTER | family zones; `01-WORKING/` | OWNED |
| Freeze | CEP-007 + Freeze Registry | `00-CEP/` | OWNED |
| Evolution / amendment | CEP-009 + ADDENDUM B | `00-CEP/` | OWNED |
| **Nucleus model** | `NUCLEUS-001-02` | `00-MASTER/UCOS-NUCLEUS-001/` | OWNED (canonicalized 2026-07-26) |
| **Nucleus↔Universe binding** | `NUCLEUS-001-03` + `05-…` | `00-MASTER/UCOS-NUCLEUS-001/` | OWNED |
| Identity (law + architecture + realization) | AIF + ENG-001 + UMB-003/004 | `02-MASTER/`; `07-ENGINEERING/`; `00-BOOK/MASTER-BOOK/` | OWNED |
| Baseline model | CEP-007 Art VIII + BASELINE-001 | `00-CEP/`; `00-MASTER/BASELINE-001/` | OWNED |
| Constitutional tier lattice | CMG-000001 Art XVI | `00-CMG/` | OWNED |
| Execution authority | CEP-003 + UCOS-UCAF-001 | `00-CEP/`; `00-MASTER/UCOS-UCAF-001/` | OWNED |
| Lifecycle | UCIC-001 + UCL-000001 | `00-MASTER/UCIC-001`; `00-MASTER/UCL-000001/` | OWNED |
| Capability discovery | `intelligence/rie` | `intelligence/rie/` | OWNED (EXTENDED 2026-08-05) |
| Reuse determination | `engine/knowledge/integration/reuse.py` | `engine/knowledge/integration/` | OWNED (EXTENDED 2026-08-05) |

**105 capabilities** discovered. Ownership coverage: **100%**. All 431 concepts from `closure.json` are owned (`orphan_concepts = 0`, `duplicate_canonical_homes = 0`).

---

## DELIVERABLE 4 — Dependency Graph

### 4.1 Foundation Ω Nuclei Dependencies (from implementation state)

Source: `OMEGA-NUCLEUS-IMPLEMENTATION-INVENTORY.md`, convergence bindings.

```
UCOS-UFC-001 (Universal Foundation Constitution)
    ├─ depends-on → UCOS-URTF-001 (Repository Truth)
    ├─ depends-on → UCOS-UOF-001 (Ownership)
    ├─ depends-on → UCOS-UMPF-001 (Measurement Policy)
    └─ depends-on → UCOS-USAF-001 (Source Assimilation)

UCOS-UFP-001 (Universal Foundation Platform)
    └─ depends-on → UCOS-UFC-001

UCOS-UNG-001 (Universal Ω Nucleus Generator)
    ├─ depends-on → UCOS-UFC-001
    └─ depends-on → all seven Foundation Nuclei (reads capability register)
```

Convergence bindings (all CONVERGED):
- MODEL-IMPLEMENTATION → `platform.universal_foundation`
- MODEL-MEASUREMENT → `platform.universal_measurement`
- MODEL-OWNERSHIP → `platform.universal_ownership`
- MODEL-TRUTH → `platform.universal_truth`

Gates: FG-14 EXACTLY-ONCE, FG-15 NO-PARALLEL-AUTHORITY, FG-16 ONE-MEASUREMENT, FG-17 NUCLEUS-COMPLETE — all PASS.

### 4.2 Production Roadmap Dependencies (from `PRODUCTION-ROADMAP.md`)

```
Foundation (DONE at 873ef19)
    ↓
Registry (EXTEND capability register)
    ↓
Discovery (EXTEND engine.discovery + platform.repository_intelligence.discovery)
    ↓
Composition (EXTEND composition engine + FZ-10 total order)
    ↓
Generator execution (EXTEND UNG-001 write phase + replay evidence)
    ↓
Runtime (EXTEND per-nucleus CLIs + engine runtime)
    ↓
Platform Composition (COMPOSE full platform + platform-level freeze)
```

**Ordering constraint (measured, not assumed):** each phase's gate follows the existing pattern: implement under constitution → register through transaction → measure with `ucos-constitution` → freeze only when gates pass.

### 4.3 Nucleus Implementation Wave Dependencies (from `06-IMPLEMENTATION-ROADMAP-AND-SEQUENCING.md`)

```
Wave 0:  Governance authorization (CEP-009 amendment + Reuse-First adjudication)
    ↓
Wave 1:  Nucleus primitive + Constitution (EXTEND S2-03 + CEP-009)
    ↓
Wave 2:  Completeness contract + NUC-META profile over registry
    ↓
Wave 3:  Zero-Finite substrate (ZF-1..ZF-5 schema de-hard-coding)
    ↓
Wave 4:  Configuration-First invariant CFG-1 + config schemas (PLATFORM-010)
    ↓
Wave 5:  Foundational Nuclei (Identity, Space, Time, Scale, Observer, Value, Language)
    ↓
Wave 6:  Time/Calendar deep scope (TRS, sync, precision, non-Earth frames/calendars)
    ↓
Wave 7:  Commerce-domain Nuclei (Product, Catalog, Pricing, Offer, Inventory, Order, Payment, Tax, Party, Supplier, Logistics, Contract)
    ↓
Wave 8:  Commission Nucleus (NEW if Reuse-First confirms distinctness)
    ↓
Wave 9:  Universe-as-composition catalog + Platform blueprints/config profiles
    ↓
Wave 10: Registry regeneration + closure re-run (after each wave, invariants=0)
```

**Dependency rationale:**
- Time depends on Existence/Transformation (`UNI-006` deps `UNI-002, UNI-004`)
- Calendar depends on Time (`DOM-0021` dep `DOM-0020`)
- Pricing depends on Currency + Product + Time (`UNI-065` deps `UNI-067, UNI-064, UNI-006`)
- Commission depends on Pricing + Party + Currency
- Universe compositions depend on their member Nuclei

### 4.4 Critical Path

```
Foundation (DONE) → ZF substrate + Nucleus constitution (W0-W4)
                  → Foundational Nuclei (W5) → Time/Calendar (W6)
                  → Commerce Nuclei (W7) → Commission (W8)
                  → Universe catalogs (W9) → Registry regeneration (W10)
                  → [Production Roadmap Phase 1: Registry]
                  → Phase 2: Discovery
                  → Phase 3: Composition
                  → Phase 4: Generator execution
                  → Phase 5: Runtime
                  → Phase 6: Platform Composition
```

Longest in-corpus chain: Foundation → W0-W10 → Registry → Discovery → Composition → Generator → Runtime → Platform Composition.

---

## DELIVERABLE 5 — Lifecycle

### 5.1 Constitutional Lifecycle (Repository Truth: `00-MASTER/UCIC-001` + `UCL-000001`)

The single deterministic lifecycle every capability follows (15 mandatory stages from UCIC-001, extended to 45 constitutional stages by UCL-000001):

**Core 15 stages (UCIC-001):**
1. Discovery
2. Scope Determination
3. Constitutional Alignment
4. Specification
5. Architectural Design
6. Implementation
7. Validation
8. Verification
9. Certification
10. Registration
11. Composition
12. Deployment / Runtime Activation
13. Monitoring / Measurement
14. Evolution / Amendment
15. Retirement / Supersession

**Extended lifecycle (UCL-000001 discovered 45 stages across 13 graph types):**
3,063 Canonical Knowledge Objects and 342 relationships discovered across 10 metadata adapters over 8 providers. Lifecycle is **graph-driven, not enumeration-driven**. Discovery is **implementation-independent** and **serialization-independent**.

### 5.2 Nucleus-Specific Lifecycle Properties

From NF-18 (verification), NF-19 (certification), NF-25 (versioning), NF-26 (evolution):
- Nucleus comes into existence through **declared bootstrap** (no import-time side effects)
- Two independent builds are **byte-identical and content-addressed**
- Nucleus carries **one declared semantic version** governing whole surface
- Evolution is **additive only** (CEP-009; backward-compatibility mandatory)
- Certification pins a **fingerprint, never a claim**

---

## DELIVERABLE 6 — Universal Asset Relationship

### 6.1 Nucleus ⊃ Assets (Operational Level)

A Universal Nucleus **owns, governs, and produces** the Universal Assets (artifacts) within its concept domain.

Evidence: NF-04 (repository-truth-binding) — "Which class of Repository Truth the nucleus's own artifacts occupy." A Nucleus declares which artifacts it owns.

```
Universal Nucleus ─┬─→ owns artifacts
                   ├─→ governs artifacts via constitution
                   ├─→ certifies artifacts via NF-19
                   ├─→ traces artifacts via NF-23
                   └─→ evolves artifacts via NF-26
```

### 6.2 Nucleus ⊆ Asset (Registry Level)

The Nucleus itself is **registered as an artifact** in the Universal Artifact Registry.

Evidence: `platform/universal_foundation/catalog/foundation-capabilities.json` — each of the 7 Foundation Nuclei is registered as a capability with `capability_id`, `identity`, `contracts`, `service_descriptor`, etc.

Registration flow: Nucleus implementation → `register.sh` → Universal Artifact Registry → `artifact.schema.json` conformance → `UNIVERSAL-ARTIFACT-REGISTRY.md` append-only ledger.

### 6.3 Relationship Summary

**Bidirectional relationship:**
- **Operational:** Universal Nucleus ⊃ Universal Assets (a Nucleus owns/produces/governs its domain's assets)
- **Registry:** Universal Nucleus ⊆ Universal Assets (the Nucleus itself is registered as an artifact)

This dual relationship is constitutional by design: registration is universal (everything is an artifact), while ownership is domain-specific (each Nucleus owns its concept's artifacts).

---

## DELIVERABLE 7 — Repository Truth Evidence

All conclusions in this architecture freeze are grounded in the following Repository Truth artifacts:

| Artifact | Path | Role |
|----------|------|------|
| Production Foundation | `PRODUCTION-FOUNDATION.md` | 7 implemented Ω Nuclei; all gates green; freeze state |
| Production Roadmap | `PRODUCTION-ROADMAP.md` | 6 remaining phases; ordering constraint |
| Ω Nucleus Implementation Inventory | `OMEGA-NUCLEUS-IMPLEMENTATION-INVENTORY.md` | Per-nucleus state; convergence bindings |
| Repository Discovery Report | `01-REPOSITORY-DISCOVERY-REPORT.md` | Zone inventory; canonical presence scan |
| Canonical Ownership Matrix | `02-CANONICAL-OWNERSHIP-MATRIX.md` | 71 ownership rows; 105 capabilities; addenda Ω-A02 |
| Dependency Graph | `03-DEPENDENCY-GRAPH.md` | L1..L8 ladder; critical path; acyclicity proof |
| Nucleus Constitutional Model | `00-MASTER/UCOS-NUCLEUS-001/02-NUCLEUS-CONSTITUTIONAL-MODEL.md` | Nucleus ≡ concern-unit; NUC-META; NUC-ZF |
| Canonical Nuclei Catalog | `00-MASTER/UCOS-NUCLEUS-001/03-CANONICAL-NUCLEI-CATALOG-AND-OWNERSHIP.md` | Full ownership mapping; candidate-NEW list |
| Repository Impact Analysis | `00-MASTER/UCOS-NUCLEUS-001/01-REPOSITORY-IMPACT-AND-GAP-ANALYSIS.md` | Reuse-First adjudication; gaps G-N1..G-CFG |
| Implementation Roadmap | `00-MASTER/UCOS-NUCLEUS-001/06-IMPLEMENTATION-ROADMAP-AND-SEQUENCING.md` | Wave 0..10; ZF-1..ZF-5 |
| Platform Config & Universe Composition | `00-MASTER/UCOS-NUCLEUS-001/05-PLATFORM-CONFIG-AND-UNIVERSE-COMPOSITION.md` | Universe=composition; Platform=config; CFG-1 |
| Foundation Nucleus Contract | `platform/universal_foundation/catalog/foundation-nucleus.json` | NF-01..NF-36; three resolution kinds |
| Foundation Capabilities Register | `platform/universal_foundation/catalog/foundation-capabilities.json` | 7 Foundation Nuclei registered |
| Constitutional Meta-Governance | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | Art XVI lattice; Art LXXVI-LXXVII admission |
| MIP v2 | `UCOS-OMEGA-INFINITY-MASTER-IMPLEMENTATION-PLAN-V2.md` | LAW Ω∞-000; 25 Constitutional Directives; 7 properties |
| Closure machine truth | `00-MASTER/UAKOS-CLOSURE-002/closure.json` | 431 concepts; 0 orphans; 0 duplicates; CLOSED |

Measurement anchor: `UCOS-UMAR-2825dd04da4ab25e` — 1203 artifacts, 12,839 relationships, 25 volumes, 184 metric series.

---

## DELIVERABLE 8 — REUSE / EXTEND / CREATE Matrix

| Category | Count | REUSE | EXTEND | CREATE | UNIVERSE |
|----------|-------|-------|--------|--------|----------|
| Foundation Ω Nuclei (Layer 0) | 7 | 7 | 0 | 0 | 0 |
| Foundation Infrastructure (Layer 1) | 6 | 0 | 6 | 0 | 0 |
| Foundational / Cross-Cutting (Layer 2) | 15 | 0 | 15 | 0 | 0 |
| Commerce-Domain Nuclei (Layer 3) | 17 | 0 | 17 | 0 | 0 |
| Sector / Vertical Compositions (Layer 4) | 12 | 0 | 0 | 0 | 12 |
| Platform-Capability Nuclei (Layer 5) | 21 | 4 | 17 | 0 | 0 |
| Candidate CREATE | 1 | — | — | 1* | — |
| **TOTAL** | **79** | **11** | **55** | **1*** | **12** |

*Commission Nucleus: CREATE only if Reuse-First adjudication vs `UNI-065`/`DOM-0283`/`DOM-0284` confirms it is architecturally distinct from price/discount formation. If not distinct: EXTEND Pricing. CREATE count may collapse to 0.

**Key principle confirmed:** Of 79 taxonomy entries, only 1 is a candidate-CREATE and that CREATE is conditional. CREATE is the rarest classification, as required by Repository Truth and `CMG-000001` Art LXXVII.2(a).

---

## DELIVERABLE 9 — Updated Production Roadmap

### Phase 0: Production Foundation — COMPLETE

**Checkpoint:** `873ef19` / `00bd45f`  
**State:** All gates green. 7/7 Ω Nuclei conformant. Freeze READY 13/13. Replay byte-identical. 6403 tests, 93% coverage. 1203/1203 artifacts registered.

**Before any implementation phase begins:**

| Pre-Phase | Action | Constitutional Authority | Blocks |
|-----------|--------|-------------------------|--------|
| PP-1 | Commission Reuse-First adjudication | `CMG-000001` Art LXXVII.2(a) | Wave 8 |
| PP-2 | CEP-009 amendment authorization for Nucleus Constitution | `CEP-009` | Wave 1 |
| PP-3 | ZF-1..ZF-5 substrate fixes | `02-NUCLEUS-CONSTITUTIONAL-MODEL.md` §4 | NUC-ZF claim |
| PP-4 | CFG-1 Configuration-First invariant (EXTEND PLATFORM-010) | `05-PLATFORM-CONFIG-AND-UNIVERSE-COMPOSITION.md` §3 | all domain Nuclei |

### Phase 1: Ω Nucleus Registry

**Implements:** first-class registry nucleus — registration contracts, append-only registration lifecycle for nuclei beyond Foundation seven, registry CLI.
**Extends:** existing `load_capability_register` / `default_capability_register` (single authority — no parallel register).
**Owner:** `platform.universal_foundation` capability register.
**Gate:** implements under constitution → registered through transaction → `ucos-constitution` conformant → freeze.

### Phase 2: Ω Nucleus Discovery

**Implements:** nucleus-specific discovery — measuring the repository for packages satisfying the nucleus contract; reconciling discovered nuclei against the registry.
**Extends:** `platform.repository_intelligence.discovery` + `engine.discovery` (registry-driven discovery over Registry Truth).
**Key rule:** discovery emits measured declarations; it never registers on its own authority.
**Gate:** same as Phase 1.

### Phase 3: Ω Nucleus Composition

**Implements:** composition engine assembling registered nuclei into a running composition using declared service descriptors and the FZ-10-measured total order.
**Extends:** `bootstrap.*`, `service_register`, existing composition engine; FZ-10 total order already measured.
**Key rule:** fail-closed refusal on unresolvable compositions.
**Gate:** same as Phase 1.

### Phase 4: Universal Generator — Execution Phase

**Implements:** write phase — materializing a plan's rendered artifacts into the repository under the registration transaction.
**Extends:** `platform.universal_generator` (plan/readiness already implemented; 10 targets, 10 templates).
**Key rule:** generated artifacts must enter through `register.sh` like every other artifact; replay evidence proving byte-determinism required.
**Constitutional decision:** resolve or formally record UCOS-USAF-001 GT-07 declared-absence (either USAF declares a catalogue, or targets document gains declared-absence mechanism).
**Gate:** same as Phase 1 + replay evidence.

### Phase 5: Universal Runtime

**Implements:** runtime hosting composed nuclei as one operable system — service resolution, health/status surfaces, runtime conformance measurement.
**Extends:** per-nucleus CLIs (`ucos-foundation`, `ucos-constitution`, etc.) + `engine/` runtime primitives.
**Key rule:** running system re-measured against the same constitution that froze it.
**Gate:** same as Phase 1 + runtime conformance measurement.

### Phase 6: Universal Platform Composition

**Implements:** terminal phase — composing the full platform (Foundation + Registry + Discovery + Composition + Generator + Runtime) into a single certified deliverable.
**Gate:** platform-level freeze determination equivalent to FZ-01..FZ-13 measured over the whole composition.

### Domain Nucleus Phases (Wave 5..9 — parallel to Phases 1–6)

These waves can proceed in parallel with production roadmap phases, but each domain Nucleus must pass the nucleus gate (NF-01..NF-36) before it is declared NUC-COMPLETE:

- **Wave 5:** Foundational Nuclei (Identity, Space, Time, Scale, Observer, Value, Language)
- **Wave 6:** Time/Calendar deep scope
- **Wave 7:** Commerce-domain Nuclei (12)
- **Wave 8:** Commission (conditional CREATE)
- **Wave 9:** Universe composition catalog + platform blueprints

---

## DELIVERABLE 10 — Production Implementation Order

Topological order derived from dependency graph (§4) and constitutional ordering constraints.

### Tier 0 — Pre-implementation gates (before any code is written)

1. `PP-2` CEP-009 amendment authorization for Nucleus Constitution
2. `PP-1` Commission Reuse-First adjudication
3. `PP-3` ZF-1..ZF-5 substrate fixes — ONLY code changes required; all else is registration/config
4. `PP-4` CFG-1 Configuration-First invariant (EXTEND PLATFORM-010)

### Tier 1 — Foundation Nucleus formalization (Wave 0–2)

5. EXTEND `00-CEP/STAGE-02-S2-03` — Nucleus ≡ concern-unit binding + SHALL-CONTAIN contract (resolves G-N1, G-N2)
6. EXTEND `00-CEP/` — Nucleus Constitution amendment under CEP-009 governance
7. EXTEND `02-MASTER/UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md` — Nucleus completeness profile per `UNI-*`
8. NEW `02-MASTER/UCOS-Ω∞-NUCLEUS-REGISTER.md` — index mapping every UNI-*/ENG-*/DOM-* → Nucleus profile
9. REGENERATE registries + closure re-run (invariants = 0)

### Tier 2 — Production Roadmap Phase 1 (Ω Nucleus Registry)

10. Implement Ω Nucleus Registry nucleus (registration contracts + CLI)
11. Register → validate → certify → freeze

### Tier 3 — Production Roadmap Phase 2 (Ω Nucleus Discovery)

12. Implement Ω Nucleus Discovery
13. Register → validate → certify → freeze

### Tier 4 — Production Roadmap Phase 3 (Ω Nucleus Composition) + Wave 5

14. Implement Ω Nucleus Composition engine
15. [Parallel] Wave 5: Foundational Nuclei realization (Identity, Space, Time, Scale, Observer, Value, Language)
16. Register → validate → certify → freeze

### Tier 5 — Production Roadmap Phase 4 + Wave 6–7

17. Implement Universal Generator execution phase (write + replay evidence)
18. Resolve GT-07 declared-absence (constitutional decision)
19. [Parallel] Wave 6: Time/Calendar deep scope
20. [Parallel] Wave 7: Commerce-domain Nuclei (12)
21. Register → validate → certify → freeze

### Tier 6 — Production Roadmap Phase 5 + Wave 8–9

22. Implement Universal Runtime
23. [Parallel] Wave 8: Commission Nucleus (if CREATE confirmed)
24. [Parallel] Wave 9: Universe composition catalog + Platform blueprints
25. Register → validate → certify → freeze

### Tier 7 — Production Roadmap Phase 6 (Terminal)

26. Universal Platform Composition — compose full platform into single certified deliverable
27. Platform-level freeze determination (FZ-01..FZ-13 over the whole composition)

**Per-unit definition of done (every tier):**
Owner EXTENDED/authored → `register.sh` → `engine/validation` → `engine/certification` + CERTIFICATION-REGISTRY → closure regenerated (`gap_total=0`, invariants=0) → traceability edge recorded.

---

## Exit Criteria Verification

| Exit Criterion | State |
|----------------|-------|
| Universal Nucleus Architecture constitutionally frozen | ✅ This document — grounded in Repository Truth |
| Repository Truth supports every conclusion | ✅ Every section cites a Repository Truth artifact |
| No parallel authority created | ✅ Every nucleus maps to an existing owner (REUSE/EXTEND); only 1 conditional CREATE |
| Every future implementation phase has a deterministic architectural foundation | ✅ Deliverable 10 provides a complete topological implementation order |

**This architecture is frozen at commit `00bd45f`.**

No production implementation shall begin until this architecture has been ratified.

---

*End of UNAF-001-UNIVERSAL-NUCLEUS-ARCHITECTURE-FREEZE.md*
