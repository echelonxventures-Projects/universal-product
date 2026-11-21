# USIS-011 — Engine Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-011 (Engine Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Engine (USIS-004 tier 14) |
| CANONICAL HOME (on realization) | `15-…/12-ENGINES/` (+ resolves against `04-REGISTRIES/`) |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-010 (Pattern) |
| DEPENDS-ON | USIS-010 (Pattern) · USIS-008/009 (Algorithm/Model, referenced) · USIS-004 · USIS-001 |
| CONSTITUTIONAL ANCHOR | LAW USIS-04 (zero hard coding; engines reference registries); MIP Part 20; Constitution Part C (Zero Hard Coding) |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/004/008/009/010. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Engine** — the tier that *executes* patterns by resolving algorithm/model registry contracts at reference time, enumerating no member. This blueprint specifies the engine node shape and its zero-hard-coding contract, so a single engine shape serves all present and future methods by registration.

---

## 1 — Purpose
The Engine tier turns agnostic Patterns (USIS-010) into executable behavior by resolving registry contracts. It is the first tier oriented toward execution, yet it remains architecture: it references registries and enumerates nothing (LAW USIS-04, the constitutional Zero-Hard-Coding surface).

## 2 — Responsibilities
- Own the **engine node shape**: a resolver contract that binds pattern roles to registry members at reference time.
- Enforce **zero hard coding** (USIS-004 tier closure): no engine contains an enumerated list of algorithms/models/domains; all are resolved from registries.
- Provide the **execution contract** consumed by Runtime (USIS-013) and Service (USIS-012).

## 3 — Boundaries
- **Owns:** engine node shape, registry-resolution contract, zero-hard-coding closure.
- **Does not own:** patterns/algorithms/models (referenced), the runtime that hosts the engine (USIS-013), the service that exposes it (USIS-012), or governed-autonomy policy (LAW USIS-06, owned by Runtime).
- Contains no member enumeration (Proof Obligation 1; the meta-model's "zero-hard-coding" closure for this tier).

## 4 — Interfaces
Exposes: `register · describe · compose · reason · analyze · simulate · compile · observe · evolve`. An engine declares which pattern(s) it executes and resolves members from the Algorithm/Model/Pattern registries; it exposes an execution contract but binds no concrete member statically.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-010 (Pattern) and, by reference, USIS-008/009 (Algorithm/Model registries). USIS-013 (Runtime) `Depends-On` this tier — Engine founds Runtime (meta-model).

## 6 — Registry model
Engines are recorded in the **Architecture Registry** (target #10) and resolve, at reference time, against the Algorithm/Model/Pattern registries (`04-REGISTRIES/`). The engine holds registry *contracts*, not rows; resolution is deterministic and open (adding a member changes no engine; Proof Obligation 20).

## 7 — Relationship model
Parent edge → Pattern (USIS-010). Child edge → Runtime (USIS-013). Reference edges → Algorithm/Model registries (resolution), Evidence (USIS-016, execution traces). One engine shape serves unbounded registered methods.

## 8 — Lifecycle
An engine node follows **DEFINED → BOUND-BY-CONTRACT (to pattern/registries) → REGISTERED → EVOLVING**, under UCIC-001. New members become executable purely by registry append — the engine is never edited to admit one (LAW USIS-03; Proof Obligation 20).

## 9 — Validation model
Referenced to USIS-014: an engine is valid only if it contains zero member enumeration (grep audit, Proof Obligation 1) and every referenced registry contract resolves (Dependency Closure, Proof Obligation 14). Explanation coverage of executed reasoning is required (LAW USIS-07).

## 10 — Certification model
Referenced to USIS-015: certification confirms zero hard coding, registry-contract resolution, and canonical ownership. An engine that enumerates members cannot be certified (fail-closed).

## 11 — Evidence model
Referenced to USIS-016: zero-hard-coding audit record, registry-resolution log, and execution/reasoning traces with provenance (LAW USIS-07).

## 12 — Failure model
Per UCIC Output-4. Any enumerated member in an engine ⇒ hard-coding violation ⇒ non-certifiable. An unresolved registry contract ⇒ Dependency-Closure failure. Two engines claiming the same execution concern ⇒ Zero-Overlap violation.

## 13 — Reuse model
Reuse-First (LAW USIS-02): search the Architecture Registry for an engine shape before creating one; extend behavior by registering new patterns/members, not by adding engines. Runtime/simulation execution owned by `08-RUNTIME`/U26 is **referenced**, never duplicated.

## 14 — Non-goals
- Not a runtime or scheduler (USIS-013).
- Not a service surface (USIS-012) or API/SDK (USIS-017).
- Enumerates no algorithm/model/domain; names no technology (LAW USIS-04).

*END — USIS-011 · ENGINE ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
