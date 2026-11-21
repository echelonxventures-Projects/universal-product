# USIS-017 — API & SDK Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-017 (API & SDK Architecture) — Wave-2 area-tree architecture blueprint |
| NAMESPACE | AREA-TREE (Wave-2 architecture spine). Distinct from UCOS-USIS-001 foundation-deliverable doc numbering. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| UCOS-PROGRAM / CATEGORY | USIS / USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| META-MODEL TIER | API (tier 17) + SDK (tier 18) |
| CANONICAL HOME (on realization) | `15-…/18-APIS-SDK/` |
| STATUS | AUTHORED · AWAITING UCIC AUTHORISATION · Wave 2 |
| PARENT | USIS-012 (Service) |
| DEPENDS-ON | USIS-012 (Service) · USIS-001 · SERVICE/PLATFORM API machinery (referenced) |
| CONSTITUTIONAL ANCHOR | LAW USIS-04 (protocol/language neutrality); Constitution Part E; MIP Part 20 |
| AUTHORITY | NONE — DERIVED. Composes USIS-001/012 + SERVICE/PLATFORM. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; void to extent of conflict. |

> **Purpose.** Define the architecture of the **API** and **SDK** surfaces — the outermost projection of service contracts onto consumable interfaces. This blueprint specifies the surface node shapes and their neutrality contract, so services are consumable by any present or future protocol, language, or client without changing any upper tier (LAW USIS-04). API and SDK are co-authored here because SDK is defined as the client projection of the API (USIS-004 tiers 17→18).

---

## 1 — Purpose
The API tier projects a Service contract (USIS-012) onto an invocable interface; the SDK tier projects the API onto a client surface. Both are agnostic: the specification names no protocol, serialization, or language — those are registered bindings of the realizing capability.

## 2 — Responsibilities
- Own the **API surface node shape**: the mapping from service operations to an interface contract (operations, shapes, error contract), protocol-neutral.
- Own the **SDK surface node shape**: the client projection of an API, language-neutral.
- Enforce **surface neutrality**: no protocol/serialization/language is named in the architecture; bindings are registered content.
- Guarantee **full-verb projection**: every Constitution Part E verb a service exposes is projectable onto the API/SDK surface.

## 3 — Boundaries
- **Owns:** API and SDK surface node shapes and their neutrality contract.
- **Does not own:** the service contract (USIS-012 — referenced), the runtime (USIS-013), the transport/serialization machinery (SERVICE/PLATFORM — referenced), or generated client code (Implementation/Software stream — referenced).
- Terminal tier of the Wave-2 spine before Implementation; produces no code.

## 4 — Interfaces
Projects the service's Constitution Part E verbs onto interface operations. Exposes meta-operations: `describe · discover · register · version · deprecate`. The SDK surface additionally exposes composition helpers as contracts (no concrete language binding).

## 5 — Dependencies
Downward-only (acyclic): `Depends-On` USIS-012 (Service — API projects the service contract) and, by reference, the SERVICE/PLATFORM API machinery. SDK `Depends-On` API (both authored here). The Validation tier (USIS-014) depends transitively on this tier via Implementation (see Dependency Report).

## 6 — Registry model
API and SDK surfaces are recorded in the **Architecture Registry** (target #10); versioned surfaces are append-only (a new version never rewrites a prior; Proof Obligation 7). Deprecation is a state, not a deletion (identity append-only; CR-INF-007).

## 7 — Relationship model
Parent edge → Service (API), API (SDK). Reference edges → SERVICE/PLATFORM API machinery (transport), Implementation (generated clients), Evidence (USIS-016). One service may project to multiple API/SDK surfaces; each surface is canonically owned.

## 8 — Lifecycle
Surface nodes follow **DEFINED → PROJECTED (from service/API) → REGISTERED → VERSIONED → (DEPRECATED) → EVOLVING**, under UCIC-001. New surfaces/versions append; consumers migrate by version, never by rewrite.

## 9 — Validation model
Referenced to USIS-014: a surface is valid only if it projects a certified service contract completely (every exposed verb mapped), is protocol/language-neutral (Proof Obligation 1), and its versioning is append-only.

## 10 — Certification model
Referenced to USIS-015: certification confirms complete verb projection, neutrality, append-only versioning, and canonical ownership.

## 11 — Evidence model
Referenced to USIS-016: verb-projection matrix (service→API→SDK), version lineage, neutrality audit, and dependency-satisfaction note (service certified).

## 12 — Failure model
Per UCIC Output-4. A surface projecting an uncertified service ⇒ Dependency-Closure failure. A named protocol/language in the architecture ⇒ neutrality violation. A breaking rewrite of a published surface ⇒ append-only violation ⇒ rejected (must version).

## 13 — Reuse model
Reuse-First (LAW USIS-02): the SERVICE/PLATFORM API and transport machinery are **referenced**, never re-homed. USIS API/SDK surfaces add only the science-intelligence projection; common client concerns reuse platform surfaces.

## 14 — Non-goals
- Not the transport/serialization infrastructure (SERVICE/PLATFORM).
- Not generated client code (Implementation/Software stream).
- Names no protocol/serialization/language (LAW USIS-04).

*END — USIS-017 · API & SDK ARCHITECTURE · Wave-2 operational-memory blueprint · AUTHORITY = NONE (DERIVED).*
