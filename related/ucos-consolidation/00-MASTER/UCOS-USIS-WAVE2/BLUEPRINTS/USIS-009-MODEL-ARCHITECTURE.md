# USIS-009 — Model Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-009 (Model Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Model (USIS-004 tier 11) |
| CANONICAL HOME (on realization) | `15-…/10-MODELS/` (+ Model Registry under `04-REGISTRIES/`) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-006 (Capability) |
| DEPENDS-ON | Knowledge Object registry (U24, referenced) · USIS-006 (Capability) · USIS-004 Meta-Model · USIS-001 (LAW USIS-04) |
| CONSTITUTIONAL ANCHOR | LAW USIS-04 (agnostic model, `binding`); LAW USIS-02 (reuse-first); MIP Part 20 (models/analytics) |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/004/006 + U24. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Model** node — the agnostic, versioned representation a capability reasons or learns over, grounded on a Knowledge Object. This blueprint specifies the model node shape and its `binding` boundary so any present or future model is registered, versioned content, swappable without changing upper tiers (LAW USIS-04).

---

## 1 — Purpose
The Model tier is the parent of the Algorithm tier (USIS-004): an algorithm operates over/against a model. A model is the agnostic representation (structure, parameters-contract, semantics), with concrete realizations carried as `binding` content.

## 2 — Responsibilities
- Own the **model node shape**: agnostic representation, version identity, grounding edge to a Knowledge Object, and optional `binding`.
- Own the **Model Registry** membership contract: append-only, versioned rows.
- Enforce the **agnosticism boundary** shared with Algorithm: architecture names no concrete model; upper tiers reference by contract.

## 3 — Boundaries
- **Owns:** the model node, versioning, grounding edge, `binding` boundary.
- **Does not own:** the Knowledge Object it grounds on (U24/Knowledge Registry — referenced), the algorithms operating over it (USIS-008), or datasets (Dataset Registry — referenced).
- Concrete models appear only in `binding` (LAW USIS-04; Proof Obligation 1).

## 4 — Interfaces
Exposes: `register · describe · compose · know · reason · version · evolve`. A model declares its Knowledge-Object grounding and its representation contract; algorithms and engines reference it by registry contract.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` the Knowledge-Object registry (U24, referenced) and USIS-006 (Capability). USIS-008 (Algorithm) `Depends-On` this tier — Model founds Algorithm (meta-model), though its catalog number is higher (numbering-index artifact; see Dependency Report).

## 6 — Registry model
Every model is a versioned row in the **Model Registry** (program registry under `04-REGISTRIES/`); a new version appends and never overwrites (append-only; CR-INF-007). Open registry, no compiled ceiling (Proof Obligation 21). Deterministic regeneration.

## 7 — Relationship model
Parent edge → Knowledge Object (Registry tier / U24). Child edges → Algorithm (USIS-008), Pattern (USIS-010). Reference edges → Dataset (training/eval provenance) and Evidence (USIS-016). One agnostic model node may carry many bindings/versions; the node is canonical.

## 8 — Lifecycle
A model node follows **DEFINED → GROUNDED (to a Knowledge Object) → MODELED → REGISTERED → (versioned/bound) → EVOLVING**, under UCIC-001. New versions and bindings append; upper tiers are untouched (Proof Obligation 20).

## 9 — Validation model
Referenced to USIS-014: the agnostic node is validated for grounding presence (Knowledge-Object edge) and representation-contract completeness. A `binding`/version is validated in the Software stream (referenced), with grounding + explanation coverage per LAW USIS-07.

## 10 — Certification model
Referenced to USIS-015: certification confirms agnosticism (Proof Obligation 1), grounding closure, and canonical ownership. Reproducibility of a bound model is certified in the realizing capability's UCIC run.

## 11 — Evidence model
Referenced to USIS-016: grounding edge, version lineage, reuse-first search record, and — for executed bindings — provenance/explanation traces (LAW USIS-07).

## 12 — Failure model
Per UCIC Output-4. A model without a Knowledge-Object grounding edge ⇒ grounding-closure failure ⇒ rejected. A concrete model named outside `binding` ⇒ agnosticism violation. A duplicate representation ⇒ reuse the canonical node.

## 13 — Reuse model
Reuse-First (LAW USIS-02): search the Model Registry and U24 Knowledge universe before creating a node; add a version/binding to an existing node rather than forking. Analytics/knowledge models owned by MIP Part 20 / U24 are **referenced**, never re-homed.

## 14 — Non-goals
- Not a repository of concrete models (those are `binding`/version content).
- Not the Knowledge Object / dataset owner (U24 — referenced), nor the Algorithm tier (USIS-008).
- Names no vendor/framework in the architecture (LAW USIS-04).

*END — USIS-009 · MODEL ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
