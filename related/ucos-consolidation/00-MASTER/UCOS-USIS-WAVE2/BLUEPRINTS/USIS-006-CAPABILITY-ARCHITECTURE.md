# USIS-006 — Capability Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-006 (Capability Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Capability (USIS-004 tier 5) |
| CANONICAL HOME (on realization) | `15-…/08-DOMAINS/` (capability specs) + `15-…/05-META-MODEL/` (tier binding) + `04-REGISTRIES/` (Capability Registry) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-005 (Theory/Ontology/Taxonomy foundation) |
| DEPENDS-ON | USIS-007 (Domain) · USIS-004 Meta-Model · USIS-001 Constitution · Science Catalog · UCIC-001 |
| CONSTITUTIONAL ANCHOR | LAW USIS-08 (meta-model conformance); LAW USIS-00 C-00.3 (seven integration facets); UCIC-001 Output-2; LAW Ω∞-000; MIP Parts 19/20/21 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/004 + UCIC-001. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Capability** — the single unit of realization in USIS. A capability is the node at which a science/intelligence concern becomes a governed, testable, evidenced, certified deliverable. This blueprint specifies how any present or future capability is declared, decomposed, owned, edged, and driven through the meta-model chain — uniformly and machine-checkably — so that no capability can exist partially (LAW USIS-08).

---

## 1 — Purpose
The Capability tier is the meta-model's pivot (USIS-004 tier 5): everything above it (Science → Domain) *contextualizes* a capability; everything below it (Model → Evidence) *realizes* one. This blueprint gives the capability its structural contract, independent of any discipline or technology, so a mathematics-reasoning capability and an autonomous-agent capability are described by the same shape.

## 2 — Responsibilities
- Own the **capability declaration contract** — the specialization of UCIC-001 Output-2 for the science-intelligence stream (identifier, objective, dependencies, governing determination, constitutional anchor, additive surfaces, acceptance criteria, evidence, validation, certification, required repo updates, completion definition).
- Own **capability decomposition** — how a coarse capability branches into sub-capabilities without redesign (recursive, LAW USIS-09).
- Own **capability identity** — assignment of a Universal ID and canonical owner to every capability.
- Assert **capability closure** (Proof Obligation 13): a capability is realized only if the full Science→Lifecycle chain is present, owned, edged, and evidenced.

## 3 — Boundaries
- **Owns:** the capability node shape, its declaration contract, decomposition rules, and closure predicate.
- **Does not own:** the discipline/domain context that hosts it (USIS-007 Domain), the models/algorithms/patterns that realize it (USIS-008/009/010), the lifecycle *execution engine* (UCIC-001), or the meta-model chain definition itself (USIS-004 — referenced).
- A capability produces **no code**; the Implementation tier (Software/Infrastructure stream) does, and is referenced, preserving intelligence-stream purity.

## 4 — Interfaces
Exposes the Constitution Part E cross-cutting verbs at the capability scope, at minimum: `register · describe · compose · decompose · govern · prove · certify · evolve · explain`. Each verb is a contract, not an implementation. The capability declaration is the required input to UCIC-001 Stage 3 (Authority Verification) and Stage 4 (Implementation).

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-007 (Domain — the capability's host context), USIS-004 (meta-model tier contract), the Science Catalog (discipline lineage), and UCIC-001 (lifecycle). Referenced, never re-homed: the Capability Registry mechanism (Registry Integration Manifest).

## 6 — Registry model
Every capability is a row in the **Capability Registry** (Registry Integration Manifest, target registry #1), homed under `04-REGISTRIES/` and `08-DOMAINS/`, and a node in the Architecture/Knowledge/Dependency registries. Registration is append-only, deterministic, and metadata-classified (`UCOS-PROGRAM=USIS`). Identity is never reused or renumbered (CR-INF-007).

## 7 — Relationship model
Parent edge → Sub-Domain/Domain (USIS-007). Child edges → Theory/Ontology/Taxonomy context (USIS-005, referenced) and downward to Model/Algorithm/Pattern realizers. Reference edges → Science (USIS-003) for lineage; Governance determination + Lifecycle span the node. No sibling capability may claim the same concern (Zero-Overlap, Proof Obligation 3).

## 8 — Lifecycle
A capability advances through the SCIENCE_INTELLIGENCE lifecycle (Execution-Stream deliverable): **DEFINED → GROUNDED → MODELED → REASONED → VALIDATED → CERTIFIED → EVOLVING**, executed under the UCIC-001 15 stages and 6 gates. No stage is skipped; the sole backward transition is a defect-driven REOPEN. Partial realization is not a valid terminal state (Proof Obligation 13).

## 9 — Validation model
Discharged by USIS-014 (Validation Architecture) referenced here: a capability is VALIDATED only with grounding + explanation-coverage evidence (LAW USIS-07) and UCIC Stages 5–9 PASS. Capability-specific acceptance criteria are declared in the Output-2 contract and are objective and checkable.

## 10 — Certification model
Discharged by USIS-015 (Certification Architecture): CCE 10 fail-closed gates PASS with certifier ≠ executor (SoD). Certification confirms the capability satisfies the seven integration facets (C-00.3) and its declared completion definition (UCIC Output-6).

## 11 — Evidence model
Discharged by USIS-016 (Evidence Architecture) using UCIC Output-5: dependency-verification, declaration diff, validation/certification records, and traceability edges (Vision→Certification). Absence of any required evidence ⇒ capability NOT-DONE (TRACK-001).

## 12 — Failure model
Per UCIC Output-4. Missing governing determination/anchor or SoD violation ⇒ non-recoverable for the attempt (escalate). Multi-capability scope in one realization ⇒ non-recoverable ⇒ rollback. Failed certification ⇒ REOPEN to ACTIVE with evidence preserved. A capability lacking any of the seven integration facets is fail-closed NOT integrated (C-00.3).

## 13 — Reuse model
Reuse-First (LAW USIS-02): before declaring a capability the owner searches the Capability Registry for a canonical instance and reuses it. A new capability is admissible only if no canonical instance exists. Human-Intelligence and cross-universe concerns reuse existing domain/science nodes rather than forking them (Knowledge-Once, C-00.2).

## 14 — Non-goals
- Not a catalog of concrete capabilities (those are registered content, Wave 3+).
- Not the meta-model definition (USIS-004) nor the lifecycle engine (UCIC-001).
- Names no technology, model, or algorithm (LAW USIS-04).
- Creates no competing capability catalog or registry (LAW USIS-02).

*END — USIS-006 · CAPABILITY ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
