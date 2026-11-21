# 01 — Canonical Ownership Map

> MISSION RA-003 · KNOWLEDGE ONCE · CANONICAL OWNERSHIP AUDIT · **READ ONLY**
> Scope: every concept appearing inside `04-REFERENCE/`
> Authority: NONE (derived audit truth). This artifact records and determines nothing constitutional; it creates no authority and alters no determination.
> Method: full read of all seven `04-REFERENCE/*.md` artifacts + `04-REFERENCE/ARCHITECTURAL-SOURCES/` + the `.docx` source set, cross-checked against the repository canonical registries (`00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md`, `00-MASTER/UAKOS-CLOSURE-002/22-CANONICAL-HOME-REGISTER.md`, `31-CONCEPT-OWNERSHIP-REGISTER.md`) and the source zones (`02-MASTER/`, `03-CATALOGS/`, `05-GENERATION/`). No re-extraction, no fabrication, fail-closed.

---

## 0. WHAT `04-REFERENCE/` CONTAINS

`04-REFERENCE/` holds the **Universal Reference Architecture Program (REF family)** — the "how the registered runtime universe is physically realized" layer — plus its raw source documents.

| Kind | Files |
|------|-------|
| Reference-architecture artifacts (governed `.md`) | 7 — REF-000, REF-DATA-001, REF-EVENT-001, REF-API-001, REF-WORKFLOW-001, REF-SERVICE-001, REF-APPLICATION-001 |
| Raw source documents (`.docx`) | 6 top-level + 3 under `ARCHITECTURAL-SOURCES/` + 1 `README.md` |
| Word lock/temp artifacts (`~$…`) | 2 (orphan junk — see 02-DUPLICATION-REPORT §5) |

The concepts "appearing inside" `04-REFERENCE/` fall into **four ownership classes**. The repository operates a deliberate **3-layer facet model**, which is the key to reading this map correctly:

```
CAT family (03-CATALOGS)   →  owns IDENTITY   ("what exists": entities, events, APIs, workflows, services, applications, and the canonical pattern spaces)
REF family (04-REFERENCE)  →  owns REALIZATION ("how it is physically realized": storage/runtime/transport/orchestration/experience realization + realization taxonomies)
GEN family (05-GENERATION) →  owns GENERATION  ("how it is generated": blueprints)
```

A single identifier (e.g. `DE-0001`, `EVP-01`) legitimately appears in all three layers because **each layer owns a different facet of it**, and each REF/GEN mention carries an explicit backward-derivation link to the identity owner. This is **layered facet ownership**, not duplicated ownership. Canonical-owner determinations below name the **identity owner** and the **realization owner** separately where they differ.

---

## 1. CLASS A — REFERENCE-ARCHITECTURE ARTIFACTS (owned by `04-REFERENCE/`)

Each REF artifact has exactly one source file (canonical home) and exactly one registry entry in `00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md` (the derived universal-artifact index — a mirror, not a competing owner).

| Concept | Canonical home (single) | Universal ID | Status | Owner determination |
|---------|-------------------------|--------------|--------|---------------------|
| REF-000 (Reference Architecture Constitution) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-ARCHITECTURE-CONSTITUTION.md` | `UCOS-ARCH-000024` ⚠ | ACTIVE | **ONE OWNER** ✓ (namespace note ⚠ — see 02 §3.1) |
| REF-DATA-001 (Reference Data Architecture) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-DATA-ARCHITECTURE.md` | `UCOS-REF-000003` | ACTIVE | **ONE OWNER** ✓ |
| REF-EVENT-001 (Reference Event Architecture) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-EVENT-ARCHITECTURE.md` | `UCOS-REF-000004` | ACTIVE | **ONE OWNER** ✓ |
| REF-API-001 (Reference API Architecture) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-API-ARCHITECTURE.md` | `UCOS-REF-000001` | ACTIVE | **ONE OWNER** ✓ |
| REF-WORKFLOW-001 (Reference Workflow Architecture) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-WORKFLOW-ARCHITECTURE.md` | `UCOS-REF-000006` | ACTIVE | **ONE OWNER** ✓ |
| REF-SERVICE-001 (Reference Service Architecture) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-SERVICE-ARCHITECTURE.md` | `UCOS-REF-000005` | ACTIVE | **ONE OWNER** ✓ |
| REF-APPLICATION-001 (Reference Application Architecture) | `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-APPLICATION-ARCHITECTURE.md` | `UCOS-REF-000002` | ACTIVE | **ONE OWNER** ✓ |

**No duplicated constitution.** REF-000 is the single reference-architecture constitution; it is distinct from — and subordinate to — the constitutional corpus, the Technology Constitution (IMP-000 family), the ARCH constitution family, and the CAT-000 catalog constitution. No second copy of any REF artifact exists in the repository (verified by ID search — only `04-REFERENCE/` sources + `00-BOOK` portal mirrors + one `02-MASTER` cross-program navigation pointer).

---

## 2. CLASS B — REALIZATION TAXONOMIES (newly owned by the REF family)

These concept spaces are **invented by, and canonically owned by, exactly one REF file each.** They are the realization facet and exist nowhere else as a definition. Downstream `05-GENERATION` frameworks cite them with attribution (see 02 §4).

| Concept space | Definition | Sole canonical owner |
|---------------|------------|----------------------|
| SRP-A … SRP-G (Storage Realization Patterns, 7) | Physical/storage realization mapping | REF-DATA-001 §2.1 |
| RRC-1 … RRC-4 (Runtime Realization Classes, 4) | Runtime realization classes | REF-DATA-001 §2.2 |
| ERC-1 … ERC-3 (Event Runtime Realization Classes, 3) | Event stream runtime classes | REF-EVENT-001 §2.2 |
| ARC-1 … ARC-3 (API Runtime Realization Classes, 3) | API runtime classes | REF-API-001 §2.2 |
| WRC-1 … WRC-4 (Workflow Runtime Realization Classes, 4) | Workflow runtime classes | REF-WORKFLOW-001 §2.2 |
| SRC-1 … SRC-4 (Service Runtime Realization Classes, 4) | Service runtime classes | REF-SERVICE-001 §2.2 |
| AppRC-1 … AppRC-4 (Application Runtime Realization Classes, 4) | Application runtime classes | REF-APPLICATION-001 §2.2 |
| Realization facet of EVP-01…12 / APIP-01…15 / WFP-01…12 / SVCP-01…09 / APPP-01…09 | Realization layer over the CAT-owned pattern spaces | Respective REF file §2.1 (identity owner = CAT — see Class C) |

**Determination: each realization taxonomy has exactly ONE canonical owner.** ✓

---

## 3. CLASS C — RUNTIME IDENTITY SPACES (referenced by REF; owned by the CAT family)

Every REF file explicitly disclaims creation of these ("SHALL realize … SHALL NOT create/rename/modify identity"). The **identity owner is the CAT catalog**; REF owns only the realization facet. The identity spaces therefore have a single identity owner, cited (not re-owned) by REF.

| Identity space | Identity owner (single) | Realization owner(s) |
|----------------|-------------------------|----------------------|
| DE-0001 … DE-0051 (51 entities) | CAT-DATA-001 — `03-CATALOGS/UCOS-Ω∞-UNIVERSAL-CANONICAL-DATA-CATALOG.md` | REF-DATA-001 (realizes); REF-EVENT/API/WORKFLOW/SERVICE/APPLICATION **inherit** owner+classification for traceability |
| EV-000001 … EV-000612 (612 events) | CAT-EVENT-001 — `03-CATALOGS/…-CANONICAL-EVENT-CATALOG.md` | REF-EVENT-001 |
| API-000001 … API-000765 + APIC-000001 … APIC-000765 | CAT-API-001 — `03-CATALOGS/…-CANONICAL-API-CATALOG.md` | REF-API-001 |
| WF-000001 … WF-000612 (612 workflows) | CAT-WORKFLOW-001 — `03-CATALOGS/…-CANONICAL-WORKFLOW-CATALOG.md` | REF-WORKFLOW-001 |
| SVC-000001 … SVC-000459 (459 services) | CAT-SERVICE-001 — `03-CATALOGS/…-CANONICAL-SERVICE-CATALOG.md` | REF-SERVICE-001 |
| APP-000001 … APP-000459 (459 applications) | CAT-APPLICATION-001 — `03-CATALOGS/…-CANONICAL-APPLICATION-CATALOG.md` | REF-APPLICATION-001 |
| Canonical pattern spaces EVP / APIP / WFP / SVCP / APPP + taxonomies (TAX/EVT/APT/…/SVT/WFT/APPT) | Respective CAT catalog (semantic definition) | Respective REF file (realization facet) |

**Determination: each identity space has exactly ONE identity owner (CAT family).** REF citations are traceability inheritances, not competing definitions. ✓

### 3.1 Inherited-attribute consistency (Knowledge Once at the value level)
The 51-entity inheritance table (entity name · inherited owner · base classification) is repeated across all six REF realization files for traceability. Spot-checks confirm the inherited values are **identical** across files, e.g.:

| Entity | Owner (consistent across DATA/EVENT/API/WORKFLOW/SERVICE/APPLICATION) | Classification |
|--------|----------------------------------------------------------------------|----------------|
| DE-0001 Identity | Security Owner | Restricted |
| DE-0011 Currency | Compliance Owner | Public |
| DE-0029 Invoice | Compliance Owner | Regulated |
| DE-0048 Agent | Security Owner | Restricted |

No divergent inherited value was found. This controlled redundancy is a **citation of the CAT-owned truth**, not a second owner (classified as controlled redundancy in 02 §2).

---

## 4. CLASS D — UPSTREAM CONSTITUTION / GOVERNANCE REFERENCES (owned outside `04-REFERENCE/`)

REF derives from, and cites, these read-only upstream instruments. Each resolves to exactly one canonical home (verified in registries/portal).

| Referenced concept(s) | Canonical owner (single home) |
|-----------------------|-------------------------------|
| ARCH family (17): ARCH-GOV-001 · ARCH-RUNTIME-001 · ARCH-DATA-001 · ARCH-EVENT-001 · ARCH-API-001 · ARCH-WORKFLOW-001 · ARCH-SERVICE-001 · ARCH-APPLICATION-001 · ARCH-INTEGRATION-001 · ARCH-SECURITY-001 · ARCH-INFRA-001 · ARCH-OBS-001 · ARCH-OPS-001 · ARCH-BCDR-001 · ARCH-TEST-001 · ARCH-CERT-001 · ARCH-AI-001 | `02-MASTER/UCOS-Ω∞-UNIVERSAL-*-ARCHITECTURE-CONSTITUTION.md` (source) + `00-BOOK` portal mirror; each homed once (reg. 22/31) |
| CAT family (7): CAT-000 · CAT-DATA-001 · CAT-EVENT-001 · CAT-API-001 · CAT-WORKFLOW-001 · CAT-SERVICE-001 · CAT-APPLICATION-001 | `03-CATALOGS/` (one file each) |
| Governance rule tokens: AR-01, AR-03, AR-04, RG-02, RG-05, DP-01, DP-02, DP-03, DE-04, SEC-04, SEC-05, ID-04, IP-05, AUTH-06, AI-01, C-01, TP-02 | ARCH-GOV-001 / Technology Constitution (single instrument each) |
| Cross-program anchors: IMP-000 (Implementation Governance Baseline / Technology Constitution), EES-001, EES-002, RAT-01…RAT-11 | `02-MASTER/` sources + `00-BOOK` portal (`UCOS-IMP-000001/000004`, `UCOS-EES-000001/000002`); constitutional corpus for RAT |

**Determination: every upstream reference resolves to exactly ONE canonical owner. No dead reference among the artifacts REF depends on.** ✓

---

## 5. CLASS E — RAW SOURCE DOCUMENTS (`.docx`) IN `04-REFERENCE/`

These are raw knowledge inputs whose **realized canonical owners are the Class-A REF `.md` artifacts**. They are registered once each (`UCOS-REF-000007 … UCOS-REF-000015`, per `00-MASTER/UCOS-PROJ-SYNC-001/02-REGISTRY-RECONCILIATION.md`).

| Source document | Registry ID | Role |
|-----------------|-------------|------|
| `ARCHITECTURAL-SOURCES/README.md` | UCOS-REF-000007 | Source index |
| `ARCHITECTURAL-SOURCES/UCOS Ω∞ MASTER END-TO-END PROGRAM.docx` | UCOS-REF-000008 (FROZEN) | Source |
| `ARCHITECTURAL-SOURCES/UCOS Ω∞ MASTER EVOLUTION PATH - Plan.docx` | UCOS-REF-000009 (FROZEN) | Source |
| `ARCHITECTURAL-SOURCES/UCOS-Consolidation Plan.docx` | UCOS-REF-000010 (FROZEN) | Source |
| `ChatGPT Chat.docx` | UCOS-REF-000011 | Source |
| `PHASE.docx` | UCOS-REF-000012 | Source |
| `UCOS Ω - references.docx` | UCOS-REF-000013 | Source |
| `UCOS Ω∞ MASTER IMPLEMENTATION PLAN v2.docx` | UCOS-REF-000014 | Source |
| `UNIVERSAL REALITY COMPILER CONSTITUTION.docx` | UCOS-REF-000015 | Source (distinct-named input; **not** a duplicate of REF-000) |

Two `~$…docx` files are Microsoft Word lock/owner temp artifacts with no canonical owner — flagged as orphan junk in 02 §5.

---

## 6. OWNERSHIP SUMMARY

| Ownership class | Concept count (spaces/artifacts) | Canonical owner | Duplicate owners |
|-----------------|----------------------------------|-----------------|------------------|
| A — REF artifacts | 7 | `04-REFERENCE/` (1 file each) | 0 |
| B — Realization taxonomies | 7 taxonomy families (+ realization facets) | 1 REF file each | 0 |
| C — Runtime identity spaces | 6 asset spaces + pattern/taxonomy spaces | CAT family (1 each) | 0 |
| D — Upstream refs (ARCH/CAT/gov/cross-program) | 17 ARCH + 7 CAT + rule tokens + anchors | 1 home each | 0 |
| E — Raw source docs | 9 registered | REF `.md` realizations | 0 |

**Overall: every concept appearing inside `04-REFERENCE/` maps to exactly ONE canonical owner** under the 3-layer facet model (identity=CAT, realization=REF, generation=GEN). No concept is co-owned by two competing definitions. Detailed duplication/overlap/orphan/dead-reference analysis follows in `02-DUPLICATION-REPORT.md`; the closure determination is in `03-KNOWLEDGE-ONCE-CERTIFICATION.md`.
