# USIS-007 — Domain Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-007 (Domain Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Domain / Sub-Domain (USIS-004 tiers 3–4) |
| CANONICAL HOME (on realization) | `15-…/08-DOMAINS/` (+ Domain Registry under `04-REGISTRIES/`) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-005 (Theory/Ontology/Taxonomy foundation) |
| DEPENDS-ON | Science Catalog (USIS-003) · Universe Catalog (USIS-002) · USIS-004 Meta-Model · Domain & Human-Intelligence Catalog · USIS-001 |
| CONSTITUTIONAL ANCHOR | LAW USIS-01 (universality); LAW USIS-09 (recursive extensibility); LAW USIS-05 (canonical ownership); MIP Part 19 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/002/003/004. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Domain / Sub-Domain** — the contextual home that groups capabilities under a discipline of a science universe, including the cross-universe domains and the Human-Intelligence families. This blueprint specifies how domains are homed, related to disciplines/universes, and recursively branched, so any present or future field of science or intelligence acquires a canonical home by registration, never by redesign (LAW USIS-01/09).

---

## 1 — Purpose
The Domain tier sits between Discipline (a member of the Science Catalog) and Capability (USIS-006). It provides the observer-relative grouping under which capabilities are declared, giving every capability exactly one host context and lineage back to a science universe.

## 2 — Responsibilities
- Own the **domain node shape** and its placement under a Discipline of the Science Catalog.
- Own **recursive branching** — a Domain may host Sub-Domains to unbounded depth (LAW USIS-09), each with its own owner and home.
- Host the **Human-Intelligence families** and other cross-universe domains as first-class domain homes (referencing, not duplicating, the Domain & Human-Intelligence Catalog).
- Assert **ownership closure** (USIS-004 tier contract): every domain has exactly one owning artifact and one canonical home under `08-DOMAINS/`.

## 3 — Boundaries
- **Owns:** domain/sub-domain node shape, branching rules, canonical homing under `08-DOMAINS/`.
- **Does not own:** the science/discipline set (Science Catalog, USIS-003 — referenced), the universe set (Universe Catalog, USIS-002 — referenced), the capabilities themselves (USIS-006), or the taxonomy tree structure (USIS-005 — referenced).
- Does not create a competing discipline catalog or taxonomy (LAW USIS-02).

## 4 — Interfaces
Exposes at the domain scope: `register · describe · compose · discover · search · govern · evolve`. A domain declares its parent Discipline and its member/child Sub-Domains and capabilities by contract; it enumerates no concrete algorithm or model.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` the Science Catalog (USIS-003, discipline lineage), the Universe Catalog (USIS-002, universe membership), USIS-004 (tier contract), and the Domain & Human-Intelligence Catalog (member set, referenced). USIS-006 (Capability) `Depends-On` this blueprint — this tier founds the Capability tier.

## 6 — Registry model
Every domain is a row in the **Domain Registry** (program registry under `04-REGISTRIES/`) and resolves in the Capability Registry (target #1), Taxonomy Registry (#3), and Dependency Registry (#9). Append-only, deterministic, metadata-classified. Adding a future domain appends a row + one homed artifact and rewrites nothing (CR-INF-007; Proof Obligation 20).

## 7 — Relationship model
Parent edge → Discipline (Science Catalog). Child edges → Sub-Domains (self-similar) and Capabilities (USIS-006). Reference edges → Universe (USIS-002) for membership; Ontology/Taxonomy (USIS-005) for placement. Cross-universe domains (e.g. Human-Intelligence families) reference their source universe and are never re-homed there (LAW USIS-05).

## 8 — Lifecycle
A domain node follows: **DEFINED → GROUNDED (placed in ontology/taxonomy) → REGISTERED → EVOLVING**, under UCIC-001. A domain is admissible once its parent Discipline exists (no forward reference; Proof Obligation 14). Sub-Domain creation is an append operation at any time.

## 9 — Validation model
Referenced to USIS-014: a domain is valid only with taxonomy closure (every taxon has a parent to a root, Proof Obligation 12) and ontology closure (every concept defined + placed, Proof Obligation 11). Grounding evidence links the domain to its discipline and universe.

## 10 — Certification model
Referenced to USIS-015: domain certification confirms ownership closure (single owner/home) and No-Orphan (Proof Obligation 4) — a structural certification, lighter than capability certification, discharged at registration.

## 11 — Evidence model
Referenced to USIS-016: placement evidence (ontology/taxonomy edges), ownership record, and dependency-satisfaction note (parent discipline certified/registered). Absence ⇒ NOT integrated (C-00.3).

## 12 — Failure model
Per UCIC Output-4. A domain without a parent Discipline is not eligible (return to selection). A domain claiming a concern already owned elsewhere violates Zero-Overlap ⇒ rejected. An orphan (unhomed/unparented) domain fails the No-Orphan gate ⇒ non-registerable.

## 13 — Reuse model
Reuse-First (LAW USIS-02): before creating a domain, search the Domain Registry and the Domain & Human-Intelligence Catalog for a canonical instance and reuse it. Data/Security/Runtime/Simulation concerns are **referenced** to their owning programs (`10-DATA`, `14-SECURITY`, `08-RUNTIME`/RIE, Universe U26) — never forked into a USIS domain.

## 14 — Non-goals
- Not the science/discipline catalog (USIS-003) nor the universe catalog (USIS-002).
- Not a list of concrete Human-Intelligence families (registered content; the catalog owns the set).
- Names no technology (LAW USIS-04); creates no competing taxonomy (LAW USIS-02).

*END — USIS-007 · DOMAIN ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
