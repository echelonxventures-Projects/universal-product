# USIS-010 — Pattern Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-010 (Pattern Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Pattern (USIS-004 tier 13) |
| CANONICAL HOME (on realization) | `15-…/11-PATTERNS/` (+ Pattern Registry under `04-REGISTRIES/`) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-008 (Algorithm) |
| DEPENDS-ON | USIS-008 (Algorithm) · USIS-009 (Model) · USIS-004 Meta-Model · USIS-001 |
| CONSTITUTIONAL ANCHOR | LAW USIS-04 (agnostic composition); LAW USIS-02 (reuse-first); MIP Part 20/21 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/004/008/009. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Pattern** node — a technology-free composition of algorithms/models that captures a reusable reasoning, learning, analytics, or scientific method (e.g. an inference schema, a learning loop shape, an analytic pipeline shape). This blueprint specifies the pattern node shape so recurring methods are named once and composed by engines without hard-coding.

---

## 1 — Purpose
The Pattern tier composes Algorithm (USIS-008) and Model (USIS-009) nodes into named, reusable method shapes. Patterns are pure specification — the last agnostic tier before Engine — enabling engines to assemble behavior from registered parts rather than embedding logic.

## 2 — Responsibilities
- Own the **pattern node shape**: a named composition contract over algorithm/model references, with a role/edge structure but no concrete member.
- Own the **Pattern Registry** membership contract.
- Provide the **reuse surface** for engines: an engine references a pattern; it does not restate the composition (Zero Hard Coding).

## 3 — Boundaries
- **Owns:** pattern node shape and composition semantics.
- **Does not own:** the algorithms/models it composes (USIS-008/009 — referenced), the engine that executes it (USIS-011), or any runtime binding (USIS-013).
- Enumerates no concrete algorithm/model member — references by registry contract only (LAW USIS-04).

## 4 — Interfaces
Exposes: `register · describe · compose · reason · analyze · evolve`. A pattern declares the algorithm/model roles it composes and the edges among them; engines bind concrete registry members to those roles at reference time.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-008 (Algorithm) and USIS-009 (Model). USIS-011 (Engine) `Depends-On` this tier — Pattern founds Engine (meta-model).

## 6 — Registry model
Every pattern is a row in the **Pattern Registry** (program registry under `04-REGISTRIES/`), append-only and open (Proof Obligation 21). Composition is expressed as role references to the Algorithm/Model registries, resolved deterministically. Adding a pattern appends a row + homed artifact (Proof Obligation 20).

## 7 — Relationship model
Parent edge → Algorithm (USIS-008). Child edge → Engine (USIS-011). Reference edges → Model (USIS-009), Knowledge Object (context), Evidence (USIS-016). A pattern references members by role; the members remain canonically owned by their own tiers.

## 8 — Lifecycle
A pattern node follows **DEFINED → COMPOSED (roles bound to registry contracts) → REGISTERED → EVOLVING**, under UCIC-001. Patterns admit new algorithm/model members by reference without redefinition (Proof Obligation 20).

## 9 — Validation model
Referenced to USIS-014: a pattern is valid only if every composed role resolves to a registered algorithm/model contract (Dependency Closure, Proof Obligation 14) and the composition is acyclic. Explanation coverage of the method is required (LAW USIS-07).

## 10 — Certification model
Referenced to USIS-015: certification confirms agnostic composition (no hard-coded member; Proof Obligation 1), reuse-first admissibility, and canonical ownership.

## 11 — Evidence model
Referenced to USIS-016: role-resolution record (which registry contracts fill each role), reuse-first search record, and method-explanation trace.

## 12 — Failure model
Per UCIC Output-4. An unresolved composed role ⇒ Dependency-Closure failure ⇒ rejected. An enumerated concrete member inside the pattern ⇒ hard-coding violation. A duplicate of an existing method shape ⇒ reuse the canonical pattern.

## 13 — Reuse model
Reuse-First (LAW USIS-02): search the Pattern Registry before creating a shape; extend an existing pattern by adding member roles rather than forking. Reasoning/learning/analytics method shapes already owned by MIP Part 20/21 universes are **referenced**.

## 14 — Non-goals
- Not a catalog of concrete pipelines (those are registered content).
- Not the Engine that executes patterns (USIS-011).
- Names no technology or concrete member (LAW USIS-04).

*END — USIS-010 · PATTERN ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
