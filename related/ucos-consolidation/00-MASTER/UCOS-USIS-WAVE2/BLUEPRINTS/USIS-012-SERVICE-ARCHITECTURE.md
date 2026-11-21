# USIS-012 — Service Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-012 (Service Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | Service (USIS-004 tier 16) |
| CANONICAL HOME (on realization) | `15-…/13-SERVICES/` |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-013 (Runtime) |
| DEPENDS-ON | USIS-013 (Runtime) · USIS-011 (Engine, referenced) · USIS-001 · SERVICE program (referenced) |
| CONSTITUTIONAL ANCHOR | LAW USIS-04 (agnostic contracts); Constitution Part E (cross-cutting verbs); MIP Part 20 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/011/013 + SERVICE program. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **Service** — the governed, contract-first surface that exposes runtime-hosted engine behavior (reason, learn, predict, analyze, simulate, …) to consumers. This blueprint specifies the service node shape and its contract semantics, without duplicating the SERVICE program's universal service machinery.

---

## 1 — Purpose
The Service tier exposes a Runtime-hosted (USIS-013) capability as a consumable, governed contract. Services are the interface between the science-intelligence substrate and its consumers; they carry the cross-cutting verbs and the governance/observability obligations of the substrate.

## 2 — Responsibilities
- Own the **service node shape**: the agnostic service contract (operations, pre/post-conditions, governance/observability bindings) over a runtime-hosted engine.
- Own the **service catalog membership** contract and canonical ownership of each service concern.
- Bind the Constitution Part E cross-cutting verbs to concrete service operations by contract.

## 3 — Boundaries
- **Owns:** service node shape and contract semantics for science-intelligence.
- **Does not own:** the runtime that executes behavior (USIS-013), the engine logic (USIS-011), the API/SDK transport surfaces (USIS-017), or the universal service infrastructure of the SERVICE program (referenced).
- Defines contracts, names no transport/protocol/framework (LAW USIS-04).

## 4 — Interfaces
Exposes the full Constitution Part E verb set at the service scope: `register · describe · compose · govern · secure · monitor · observe · meter · bill · audit · prove · comply · certify · discover · search · remember · know · reason · simulate · compile · evolve · explain`. Each is a service-contract operation; the API/SDK tier (USIS-017) projects them onto concrete surfaces.

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-013 (Runtime — the service's execution host) and, by reference, USIS-011 (Engine) and the SERVICE program. USIS-017 (API/SDK) `Depends-On` this tier — Service founds API (meta-model).

## 6 — Registry model
Every service is recorded in the **Architecture Registry** (target #10) and, for execution, the **Execution Registry** (#5). Governance, metering, and audit bindings resolve against the SERVICE/Security/Data registries by reference. Append-only; canonical ownership per service (Proof Obligation 9).

## 7 — Relationship model
Parent edge → Runtime (USIS-013). Child edge → API (USIS-017). Reference edges → SERVICE program (universal service machinery), Security (`14-SECURITY`), Evidence (USIS-016). Governance/Lifecycle span the node.

## 8 — Lifecycle
A service node follows **DEFINED → BOUND (to runtime) → GOVERNED (verbs + observability bound) → REGISTERED → EVOLVING**, under UCIC-001. New operations append to the contract; existing operations are never rewritten (append-only; Proof Obligation 7).

## 9 — Validation model
Referenced to USIS-014: a service is valid only if its contract is complete (pre/post-conditions), its governance/observability verbs are bound, and its runtime dependency is certified (Dependency Closure). Explanation coverage of service-mediated decisions is required (LAW USIS-07).

## 10 — Certification model
Referenced to USIS-015: certification confirms contract completeness, cross-cutting-verb coverage, canonical ownership, and agnosticism (no named transport/framework; Proof Obligation 1).

## 11 — Evidence model
Referenced to USIS-016: service-contract record, verb-binding matrix, dependency-satisfaction note (runtime certified), and observability/audit traces.

## 12 — Failure model
Per UCIC Output-4. A service exposing an uncertified runtime ⇒ Dependency-Closure failure. A missing governance/audit verb binding ⇒ fail-closed (C-00.3, seven facets). A named transport/framework in the contract ⇒ agnosticism violation. Two services claiming one concern ⇒ Zero-Overlap violation.

## 13 — Reuse model
Reuse-First (LAW USIS-02): the SERVICE program's universal service machinery, Security controls (`14-SECURITY`), and metering/billing surfaces are **referenced**, never re-homed. USIS services add only the science-intelligence contract specialization.

## 14 — Non-goals
- Not the SERVICE program's universal service infrastructure.
- Not the API/SDK transport surfaces (USIS-017) nor the runtime (USIS-013).
- Names no protocol/transport/framework (LAW USIS-04).

*END — USIS-012 · SERVICE ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
