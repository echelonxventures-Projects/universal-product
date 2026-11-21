# RA-002 — MISSING CONCEPTS REGISTER (Output 02 of 03)

| Field | Value |
|-------|-------|
| MISSION | RA-002 — Knowledge Gap Determination (READ ONLY) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Records candidate concepts; homes, owners, and priorities are *recommendations*, not enactments. |
| SCOPE | Concepts introduced by `04-REFERENCE/` that exist ONLY there and are absent from Repository Truth's concept ledger (`00-MASTER/UAKOS-CLOSURE-002/20`,`21`,`22`). |
| DEFINITIONS | **Missing** = only in `04-REFERENCE`, no downstream mirror, no concept home. **Partially Canonical** = authoritative definition only in `04-REFERENCE`, but consumed/mirrored by canonical `05-GENERATION`. Both classes are unhomed at the concept layer and are listed here for completeness. |
| PROOF OF ABSENCE | Exclusion-scoped grep of `00-MASTER/UAKOS-CLOSURE-002/2*.md` for `REF-000\|REF-DATA\|Storage Realization\|Reference Architecture\|SRP-\|RRC-\|realization facet` → **No matches**. `REF` is not a family in `21-CONCEPT-NORMALIZATION-REGISTER.md`. |

**Priority scale:** P1 = required to make Repository Truth's concept layer honest about the REF family (root-cause). P2 = required before any GEN framework can be safely implemented. P3 = completeness/traceability hardening.

---

## PART A — MISSING CONCEPTS (only in 04-REFERENCE, no downstream mirror)

### M-01 — Universal Reference Architecture Meta-Model
- **Concept:** The realization meta-chain `Universe → Domain → Capability → Component → Entity → Event → API → Workflow → Service → Application → Reference Architecture`, with the "no orphan reference architectures" invariant.
- **Description:** Defines that every reference-architecture realization must trace back to a registered ARCH+CAT asset; establishes the physical-realization layer over the runtime universe.
- **Reference document:** `04-REFERENCE/UCOS-Ω∞-UNIVERSAL-REFERENCE-ARCHITECTURE-CONSTITUTION.md §1`
- **Repository destination:** `00-MASTER/UAKOS-CLOSURE-002/20-CANONICAL-CONCEPT-REGISTER.md` (new `REF` family rows) + `28-KNOWLEDGE-GRAPH.md` node.
- **Canonical owner:** REF-000 (Universal Reference Architecture Constitution).
- **Implementation priority:** **P1**.
- **Dependencies:** Requires `REF` to be added as a recognized family in `21-CONCEPT-NORMALIZATION-REGISTER.md` (see M-00 below).

### M-00 — `REF` (and `CAT`/`GEN`) Concept-Family Namespace *(root-cause prerequisite)*
- **Concept:** Recognition of `REF`, `CAT`, `GEN` as first-class concept-family namespaces in the normalization register.
- **Description:** `21-CONCEPT-NORMALIZATION-REGISTER.md` enumerates families (UCKO, ARCH, MEP, MCP, MCS, CEP, DATA, SERVICE, …) but omits REF/CAT/GEN, so their concepts can never be homed.
- **Reference document:** absence evidenced by `21-CONCEPT-NORMALIZATION-REGISTER.md`; concepts sourced across all of `04-REFERENCE`.
- **Repository destination:** `00-MASTER/UAKOS-CLOSURE-002/21-CONCEPT-NORMALIZATION-REGISTER.md`.
- **Canonical owner:** UAKOS closure program (concept-ledger owner).
- **Implementation priority:** **P1 (blocks M-01…M-14).**
- **Dependencies:** none — this is the enabling prerequisite.

### M-02 — Reference Architecture 9-Field Identity Model
- **Concept:** Reference ID · Name · Type · Version · Status · Owner · Dependencies · Certification Status · Traceability References.
- **Description:** The mandatory identity schema every reference architecture must carry; an unidentified reference architecture is a failure condition.
- **Reference document:** `REF-000 §3`.
- **Repository destination:** concept register (`20`) + identity schema note alongside `06-IMPLEMENTATION/UCOS-Ω∞-REGISTRY-PLATFORM.md`.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P2**.
- **Dependencies:** M-00, M-01.

### M-03 — Eight Realization Facets
- **Concept:** Logical · Physical · Runtime · Deployment · Operational · Observability · Certification · Recovery realization.
- **Description:** The facet decomposition through which any registered runtime asset is physically realized; consumes ARCH-INFRA/OPS/OBS/CERT/BCDR.
- **Reference document:** `REF-000 §4` (and applied in every REF-DATA…APPLICATION §4/§10).
- **Repository destination:** concept register (`20`) + architecture taxonomy in `02-MASTER` cross-reference.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P2**.
- **Dependencies:** M-00, M-01.

### M-04 — Nine Reference Classification Classes
- **Concept:** Core · Shared · Domain · Platform · Infrastructure · Security · Operational · Application · Agent.
- **Description:** The mandatory single-classification taxonomy for reference architectures (distinct from the 8-level data sensitivity scale).
- **Reference document:** `REF-000 §8`.
- **Repository destination:** canonical taxonomy register (new) + concept register (`20`).
- **Canonical owner:** REF-000.
- **Implementation priority:** **P2**.
- **Dependencies:** M-00.

### M-05 — Reference Architecture Lifecycle Model
- **Concept:** Proposed → Defined → Approved → Active → Deprecated → Retired → Archived → Destroyed, with runtime binding requiring {Approved, Active}.
- **Description:** REF-scoped lifecycle governance (mirrors ARCH lifecycle but scoped to reference artifacts).
- **Reference document:** `REF-000 §9`.
- **Repository destination:** concept register (`20`); lifecycle already generically present for ARCH — record REF specialization.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P3**.
- **Dependencies:** M-00, M-01.

### M-06 — Reference Registry Model (six registries)
- **Concept:** Master Reference · Dependency · Certification · Evidence · Runtime · Implementation registries.
- **Description:** The registry set the Reference Architecture Program must maintain; only the artifact-level registry rows currently exist.
- **Reference document:** `REF-000 §10`.
- **Repository destination:** `00-BOOK/REGISTRIES/` (new REF-scoped registries) or `06-IMPLEMENTATION/UCOS-Ω∞-REGISTRY-PLATFORM.md` (registry substrate).
- **Canonical owner:** REF-000 + Registry Platform.
- **Implementation priority:** **P2**.
- **Dependencies:** M-02, M-14.

### M-07 — Reference Certification Model (six certification types)
- **Concept:** Architecture · Design · Security · Operational · Runtime · Compliance certification.
- **Description:** Bounded-scope certification determining engineering readiness only (no authority); consumes ARCH-CERT-001 + ARCH-TEST-001.
- **Reference document:** `REF-000 §11` (applied per family §12/§13/§14).
- **Repository destination:** concept register (`20`) + certification evidence area under `06-IMPLEMENTATION`.
- **Canonical owner:** REF-000 (consuming ARCH-CERT-001).
- **Implementation priority:** **P2**.
- **Dependencies:** M-03.

### M-08 — Reference Runtime Binding Model
- **Concept:** Reference architectures bind only to registered, certified, Active/Approved catalog assets.
- **Description:** The enforced boundary between "how it is realized" (reference) and "what runs" (execution).
- **Reference document:** `REF-000 §12`.
- **Repository destination:** concept register (`20`); enforced by GEN validation (`05-GENERATION` §6/§10).
- **Canonical owner:** REF-000.
- **Implementation priority:** **P2**.
- **Dependencies:** M-06.

### M-09 — Reference Generation-Readiness Model
- **Concept:** Deterministic realization, bound dependencies, resolved traceability, certification hooks — the criteria that make a reference architecture generation-ready.
- **Description:** The contract GEN frameworks rely on; the semantic bridge REF→GEN.
- **Reference document:** `REF-000 §14`.
- **Repository destination:** concept register (`20`) + explicit REF→GEN linkage in `05-GENERATION/…GENERATION-FRAMEWORK-CONSTITUTION.md`.
- **Canonical owner:** REF-000 (consumed by GEN-000).
- **Implementation priority:** **P2**.
- **Dependencies:** M-03, M-08.

### M-10 — Reference Quality Model (seven dimensions)
- **Concept:** Completeness · Consistency · Traceability · Maintainability · Certifiability · Auditability · Operational Readiness.
- **Reference document:** `REF-000 §15`.
- **Repository destination:** concept register (`20`) + quality-gate note in `54-REPOSITORY-CLOSURE-QUALITY-GATES.md`.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P3**.
- **Dependencies:** M-00.

### M-11 — Reference Architecture Safety/Authority Boundary (REF-scoped)
- **Concept:** Reference architectures MAY define implementation/runtime/deployment/operational models; SHALL NOT create governance/constitutional/constituent/legislative/executive/judicial/EC-series authority.
- **Description:** The operative REF safety boundary + mandatory Authority Boundary repeated in every REF doc.
- **Reference document:** `REF-000 §16` + AUTHORITY BOUNDARY block (all 7 REF docs).
- **Repository destination:** concept register (`20`) + governance-boundary cross-reference in `02-MASTER`.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P1** (safety-relevant — must be captured with the family).
- **Dependencies:** M-00.

### M-12 — Reference Traceability Model (seven types)
- **Concept:** Backward · Forward · Dependency · Runtime · Certification · Evidence · Implementation traceability.
- **Reference document:** `REF-000 §6`.
- **Repository destination:** concept register (`20`) + `26-CONCEPT-TRACEABILITY-MATRIX.md`.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P2**.
- **Dependencies:** M-00, M-06.

### M-13 — Reference Governance Model
- **Concept:** Policies · Standards · Controls · Ownership · Compliance · Evidence · Certification · Quality (records-only, never ratify/enact).
- **Reference document:** `REF-000 §7`.
- **Repository destination:** concept register (`20`) + governance cross-reference in `02-MASTER`.
- **Canonical owner:** REF-000.
- **Implementation priority:** **P3**.
- **Dependencies:** M-00, M-13 is largely satisfied structurally by ARCH-GOV-001 — record the REF specialization only.

### M-14 — Instantiated Per-Family Realization Registries (as data, not prose)
- **Concept:** The Entity Registry (51), Event Registry (612), API+Contract Registry (765+765), Workflow Registry (612), Service Registry (459), Application Registry (459) — currently Markdown tables, not queryable registry instances.
- **Description:** REF-* §15/§14 mandate these registries; they exist only as prose realization tables in `04-REFERENCE` (partially mirrored as GEN blueprints).
- **Reference document:** `REF-DATA-001 §15`, `REF-EVENT-001 §15`, `REF-API-001 §13`, `REF-WORKFLOW-001 §14`, `REF-SERVICE-001 §13`, `REF-APPLICATION-001 §14`.
- **Repository destination:** `06-IMPLEMENTATION/UCOS-Ω∞-REGISTRY-PLATFORM.md` (registry substrate) or `00-BOOK/REGISTRIES/`.
- **Canonical owner:** REF family + Registry Platform.
- **Implementation priority:** **P2**.
- **Dependencies:** M-06, M-02, and the Partially-Canonical realization patterns (Part B).

---

## PART B — PARTIALLY-CANONICAL CONCEPTS (defined only in 04-REFERENCE; mirrored in 05-GENERATION; still unhomed at concept layer)

For each, **Repository destination** = concept register (`20`) with an explicit definition↔consumption link; **Canonical owner** = the cited REF document; **Dependencies** = M-00 (family namespace) + M-01 (meta-model).

| ID | Concept | Reference document | Mirrored in | Priority |
|----|---------|--------------------|-------------|:--------:|
| P-01 | Storage Realization Patterns SRP-A…SRP-G | REF-DATA-001 §2.1 | `05-GENERATION/…DATA-GENERATION-FRAMEWORK.md §2.2` | P2 |
| P-02 | Data Runtime Realization Classes RRC-1…RRC-4 | REF-DATA-001 §2.2 | `…DATA-GENERATION-FRAMEWORK.md` | P2 |
| P-03 | Event Pattern Realization EVP-01…EVP-12 + Runtime Classes ERC-1…ERC-3 | REF-EVENT-001 §2.1–2.2 | `…EVENT-GENERATION-FRAMEWORK.md` | P2 |
| P-04 | API Operation Realization APIP-01…APIP-15 + Runtime Classes ARC-1…ARC-3 | REF-API-001 §2.1–2.2 | `…API-GENERATION-FRAMEWORK.md` | P2 |
| P-05 | Workflow Pattern Realization WFP-01…WFP-12 + Runtime Classes WRC-1…WRC-4 | REF-WORKFLOW-001 §2.1–2.2 | `…WORKFLOW-GENERATION-FRAMEWORK.md` | P2 |
| P-06 | Service Pattern Realization SVCP-01…SVCP-09 + Runtime Classes SRC-1…SRC-4 | REF-SERVICE-001 §2.1–2.2 | `…SERVICE-GENERATION-FRAMEWORK.md` (BP-SERVICE-*) | P2 |
| P-07 | Application Pattern Realization APPP-01…APPP-09 + Runtime Classes AppRC-1…AppRC-4 | REF-APPLICATION-001 §2.1–2.2 | `…APPLICATION-GENERATION-FRAMEWORK.md` | P2 |
| P-08 | Deterministic derivation formulas (EV=(N-1)×12+k; API=×15; SVC/APP=×9) | REF-EVENT/API/SERVICE/APPLICATION §2 | GEN frameworks restate identically | P2 |
| P-09 | Service 7-facet Boundary Model (business/capability/data/API/workflow/ownership/runtime; no hidden coupling) | REF-SERVICE-001 §3 | `…SERVICE-GENERATION-FRAMEWORK.md` | P3 |
| P-10 | Application Experience/Interaction/Presentation models (9 experiences, 8 interaction facets, 6 presentation channels, mandatory a11y+i18n) | REF-APPLICATION-001 §3–5 | `…APPLICATION-GENERATION-FRAMEWORK.md` | P3 |

---

## PART C — COUNT SUMMARY

| Class | Count | Notes |
|-------|:-----:|-------|
| Already Canonical (artifacts) | 7 REF artifacts + 1 program | Registered; no gap |
| Missing (only in 04-REFERENCE) | 14 (M-01…M-14) + 1 prerequisite (M-00) | Governance meta-model concepts; unhomed & unmirrored |
| Partially Canonical | 10 concept-groups (P-01…P-10) | Single-sourced in 04-REFERENCE, mirrored in 05-GENERATION |
| Superseded/Deprecated | 5+ `.docx` source inputs | Reference-only / FROZEN |

**Root-cause single fix (M-00):** admitting `REF`/`CAT`/`GEN` as concept families and running concept extraction over `04-REFERENCE` would convert all Missing + Partially-Canonical items from unhomed to homed.

*END — RA-002 · Output 02 · MISSING CONCEPTS · AUTHORITY = NONE (DERIVED TRUTH). Read-only; no implementation performed.*
