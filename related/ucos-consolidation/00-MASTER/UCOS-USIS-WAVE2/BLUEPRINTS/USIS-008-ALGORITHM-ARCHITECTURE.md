# USIS-008 — Algorithm Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-008 (Algorithm Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Algorithm (USIS-004 tier 12) |
| CANONICAL HOME (on realization) | `15-…/09-ALGORITHMS/` (+ Algorithm Registry under `04-REGISTRIES/`) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-006 (Capability) |
| DEPENDS-ON | USIS-009 (Model) · USIS-006 (Capability) · USIS-004 Meta-Model · USIS-001 (LAW USIS-04) |
| CONSTITUTIONAL ANCHOR | LAW USIS-04 (technology neutrality via `binding`); LAW USIS-02 (reuse-first); MIP Part 20 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/004/006/009. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Algorithm** node — the agnostic, registry-backed unit describing *how* a capability computes, reasons, learns, or analyzes. This blueprint specifies the algorithm node shape and the technology-`binding` boundary so any present or future algorithm is registered content, swappable without changing any upper tier (LAW USIS-04).

---

## 1 — Purpose
The Algorithm tier realizes a Capability's method under a Model. It is one of the two tiers (with Model) permitted an optional `binding` field carrying present-day technology; the specification of the algorithm remains technology-free.

## 2 — Responsibilities
- Own the **algorithm node shape**: agnostic method description, inputs/outputs contract, and an optional `binding` field for a concrete present-day realization (registered content, not architecture).
- Own the **Algorithm Registry** membership contract: every algorithm is an appended, versioned row.
- Enforce the **agnosticism boundary**: no upper tier (Pattern → SDK) may name a concrete algorithm; they reference the registry by contract.

## 3 — Boundaries
- **Owns:** the algorithm node, its `binding` boundary, and registry-row semantics.
- **Does not own:** the Model it attaches to (USIS-009), the Pattern that composes it (USIS-010), the Engine that references it (USIS-011), or the code that implements a binding (Implementation tier — referenced).
- The `binding` field is the **only** place a present-day algorithm name may appear; the surrounding architecture stays neutral (LAW USIS-04; Proof Obligation 1).

## 4 — Interfaces
Exposes: `register · describe · compose · reason · analyze · prove · evolve`. An algorithm declares the Model/Capability it serves and its I/O contract; engines invoke it only through the registry contract.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-009 (Model — the algorithm's parent per meta-model) and USIS-006 (Capability). Note: the catalog number (008) precedes Model (009); the *dependency* runs upward to Model — this is a numbering-index artifact, not a cycle (see Dependency Report).

## 6 — Registry model
Every algorithm is a row in the **Algorithm Registry** (program registry under `04-REGISTRIES/`), append-only and versioned; the `binding` sub-field records a swappable concrete realization. The registry is open (no compiled ceiling; Proof Obligation 21). Deterministic regeneration; identity never reused (CR-INF-007).

## 7 — Relationship model
Parent edge → Model/Capability (USIS-009/006). Child edge → Pattern (USIS-010) composes algorithms. Reference edges → Knowledge Object (provenance of inputs) and Evidence (reasoning traces, USIS-016). Multiple bindings may attach to one agnostic algorithm node; the node is canonical, the bindings are content.

## 8 — Lifecycle
An algorithm node follows **DEFINED → MODELED (bound to a Model) → REGISTERED → (bound) → EVOLVING**, under UCIC-001. Adding or swapping a `binding` is an append that leaves the node and all upper tiers unchanged (Proof Obligation 20).

## 9 — Validation model
Referenced to USIS-014: the agnostic node is validated for I/O-contract completeness and reuse-first admissibility; a `binding`, when present, is validated in the Software stream (referenced) — never in this architecture artifact.

## 10 — Certification model
Referenced to USIS-015: certification confirms the node is agnostic (no tech outside `binding`; Proof Obligation 1) and registered with canonical ownership. Binding certification is deferred to the realizing capability's UCIC run.

## 11 — Evidence model
Referenced to USIS-016: registry-row provenance, reuse-first search record (proving no duplicate), and reasoning/analytics traces (LAW USIS-07) for any executed binding.

## 12 — Failure model
Per UCIC Output-4. A named concrete algorithm outside a `binding` field ⇒ agnosticism violation ⇒ rejected. A duplicate of an existing registry algorithm ⇒ Zero-Duplication violation ⇒ reuse the canonical row. An algorithm with no parent Model/Capability ⇒ orphan ⇒ non-registerable.

## 13 — Reuse model
Reuse-First (LAW USIS-02): search the Algorithm Registry before creating a node; attach a new `binding` to an existing agnostic node rather than creating a parallel node. Analytics/learning algorithms already owned by MIP Part 20/21 universes are **referenced**, not re-homed.

## 14 — Non-goals
- Not a library of concrete algorithms (those are `binding` content / registry rows).
- Not the Model tier (USIS-009) nor the Engine that runs algorithms (USIS-011).
- Names no vendor/framework in the architecture (LAW USIS-04).

*END — USIS-008 · ALGORITHM ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
