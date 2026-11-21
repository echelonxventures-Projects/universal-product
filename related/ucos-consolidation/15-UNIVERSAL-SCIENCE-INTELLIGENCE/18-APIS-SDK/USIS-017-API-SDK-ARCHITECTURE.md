# USIS-017 — API & SDK Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-017 (API & SDK Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000015` (next free after `UCOS-USIS-000014` = USIS-012). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · API / SDK Architecture (EVO-USIS-017) — establish the constitutional API + SDK interaction boundary of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the API (tier 17) and SDK (tier 18) surfaces owned by the substrate (subordinate to USIS-001…013, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate API + SDK tiers (USIS-004 tiers 17–18) — the outermost projection of service contracts onto consumable interfaces and client surfaces |
| DEPENDS-ON | USIS-012 · USIS-004 · USIS-002 · SERVICE / PLATFORM API machinery (referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tiers **17 (API)** and **18 (SDK)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 20 (Intelligence/Analytics); Constitution Part E (cross-cutting verb projection) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/07/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the surface-projection mandate conferred by USIS-001 (LAW USIS-04 protocol/language neutrality / Part E) and the USIS-004 API/SDK tiers, projecting the Service tier (USIS-012), and referencing the SERVICE/PLATFORM API machinery. Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-017-API-SDK-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 9 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/18-APIS-SDK/` per USIS-005 §2 (area 18 = APIS-SDK) — no variance; no structure invented. API and SDK are co-authored here (tiers 17→18) per the authorized blueprint. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The SERVICE/PLATFORM API and transport machinery are **referenced**; the canonical home governs and this architecture holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the API and SDK surfaces** — the constitutional interaction boundary between canonical capabilities and all external consumers. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/18-APIS-SDK/` home and defines the API/SDK surface node shapes, contract/consumer/provider models, versioning/compatibility/discovery/registration models, and their neutrality contract — remaining technology-agnostic, protocol-agnostic, language-agnostic, runtime-agnostic, and implementation-independent (LAW USIS-04), and never duplicating the SERVICE/PLATFORM transport machinery. **This instrument establishes only the API/SDK-tier architecture.** It authors **no** individual API/SDK surface instance and **no** generated client — those are separately-authorized later (Wave-3 / Software stream) realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the surface-projection mandate of USIS-001 and the API (17) + SDK (18) tiers of the USIS-004 meta-model:

- **USIS-004 Part C tiers 17/18** — API (parent = Service) and SDK (parent = API). USIS-017 is the constitutional architecture and rule-set for these two adjacent tiers; SDK is the client projection of the API.
- **USIS-001 LAW USIS-04** — the surfaces are agnostic: the specification names no protocol, serialization, language, or runtime; those are registered bindings of the realizing capability; the SERVICE/PLATFORM machinery provides transport.
- **USIS-001 Part E** — every cross-cutting verb a service exposes is projectable onto the API/SDK surface (full-verb projection).
- **USIS-012 (Service)** is projected; the SERVICE/PLATFORM programs provide universal API/transport machinery. USIS-017 `Depends-On` Service and **references** SERVICE/PLATFORM and the reachable lower tiers — never duplicating their architecture (LAW USIS-02). This is the **terminal Wave-2 spine tier** before Implementation.

**Scope of this instrument (Wave 2 · EVO-USIS-017).** This architecture:
- creates the `15-…/18-APIS-SDK/` home and this single registered architecture artifact;
- defines the **API architecture, SDK architecture, interface ontology/taxonomy, contract/consumer/provider models, versioning/compatibility/discovery/registration models, service/runtime/engine/pattern integration, registry model, governance** (Parts B–P);
- founds downward-only on `USIS-012/004/002` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** API/SDK surface instance or generated client, and begins **no** Wave-3 realization;
- reuses, without duplication, the SERVICE/PLATFORM API + transport machinery, the registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/18-APIS-SDK/` already classifies to USIS/VOL-024).

## PART B — API Architecture

An API surface is a typed node of the canonical form:

```
{ id: USIS-API-<NAME>, home: 18-APIS-SDK/<NAME>/, tier: 17, projects: <USIS-SVC-*>,
  operations: [ { service_verb → interface_op, shapes, error_contract } ],
  version, compatibility_class, owner, status }
```

- The API tier projects a Service contract (USIS-012) onto an invocable interface contract (operations, shapes, error contract), **protocol-neutral**.
- It names no protocol/serialization; the concrete transport is a registered binding of the realizing capability (SERVICE/PLATFORM, referenced).

## PART C — SDK Architecture

An SDK surface is a typed node of the canonical form:

```
{ id: USIS-SDK-<NAME>, home: 18-APIS-SDK/<NAME>/, tier: 18, projects: <USIS-API-*>,
  client_contract, composition_helpers (as contracts), version, owner, status }
```

- The SDK tier projects an API (USIS-API-*) onto a client surface, **language-neutral**; it exposes composition helpers as contracts, binding no concrete language.
- Generated client code is Implementation/Software-stream content (referenced), never authored here.

## PART D — Interface ontology (reference to USIS-005)

Every API/SDK surface is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares interface concepts (operation, shape, error, version, compatibility, consumer, provider) and their relations to service concepts. Ontology Closure (obligation 11) governs. USIS-017 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART E — Interface taxonomy (reference to USIS-005)

Every surface occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the interface taxonomy (API vs SDK; version classes; compatibility classes). Taxonomy Closure (obligation 12) governs. USIS-017 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART F — Contract model

Each surface operation is a contract projecting a Service operation's verb (Constitution Part E) onto an interface operation, with input/output shapes and an error contract. Contracts are protocol/language-neutral; **full-verb projection** guarantees every service verb is projectable onto the surface.

## PART G — Consumer model & Provider model

- **Consumer model.** External consumers interact only through the API/SDK contract boundary — the constitutional interaction boundary. Consumers bind to contracts and versions, never to endpoints/transports (no infrastructure coupling); authn/authz is referenced to Security via the Service governance bindings (USIS-012 Part O).
- **Provider model.** The provider is the Service (USIS-012) whose runtime-hosted capability the surface projects; the provider is referenced, never re-homed. The surface is the provider's outward projection, not its owner.

## PART H — Versioning model & Compatibility model

- **Versioning.** Surfaces are versioned; a new version **appends** and never rewrites a published surface (append-only; obligation 7; CR-INF-007). Identity never reused.
- **Compatibility.** Each version declares a compatibility class; consumers migrate by version. A breaking rewrite of a published surface is rejected (must version). Deprecation is a state, not a deletion.

## PART I — Discovery model

Surfaces are discoverable via `describe`/`discover` and the Architecture Registry; discovery is contract/version-based, not endpoint-based (no infrastructure coupling).

## PART J — Registration model & Registry integration

- API and SDK surfaces are recorded in the **Architecture Registry** (#10); versioned surfaces are append-only. Projection produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator/registry created (LAW USIS-02). Deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`).

## PART K — Service / Runtime / Engine / Pattern integration

| Integration (by reference) | Model |
|----------------------------|-------|
| **Service integration** | API projects a Service contract (USIS-012); SDK projects the API; service owned by USIS-012, referenced |
| **Runtime integration** | the projected service is runtime-hosted (USIS-013); referenced |
| **Engine integration** | the runtime hosts the engine (USIS-011) whose behavior the service exposes; referenced |
| **Pattern integration** | the engine executes the pattern (USIS-010) realizing the capability's method; referenced |

All integration is by **reference**; the surfaces re-home nothing (LAW USIS-02).

## PART L — Dependency model & independence

- **Dependency model.** `Depends-On` runs downward to `USIS-012/004/002` (+ references SERVICE/PLATFORM); SDK depends on API (both authored here); `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). The Validation tier (USIS-014) depends transitively on this tier via Implementation (Dependency Report basis).
- **Independence.** The API/SDK tiers are technology-, protocol-, language-, runtime-, and implementation-agnostic: they define contracts and projections, not transports/clients. A surface is fully defined without any protocol/language/runtime present.

## PART M — Validation model

Discharged by USIS-014 (referenced): a surface is valid only if it **projects a certified service contract completely** (every exposed verb mapped), is protocol/language-neutral (obligation 1), and its versioning is append-only. Explanation coverage of surface-mediated decisions is referenced (LAW USIS-07).

## PART N — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms complete verb projection, neutrality, append-only versioning, and canonical ownership.

## PART O — Evidence model & Governance model

- **Evidence (→ USIS-016).** UCIC-001 Output-5: verb-projection matrix (service→API→SDK), version lineage, neutrality audit, dependency-satisfaction note (service certified). Absence ⇒ NOT-DONE (TRACK-001).
- **Governance model.** Surfaces inherit the Service governance/security bindings (USIS-012 Parts N/O) by reference — authn/authz, policy, audit, metering apply at the boundary via the Service, not re-implemented. Versioning/deprecation is governed (append-only). A surface exposing an operation without an inherited governance/security binding is fail-closed.

## PART P — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations).**
1. Duplicate API/SDK catalog/registry or duplication of SERVICE/PLATFORM transport machinery by USIS-017: **0** (LAW USIS-02).
2. Hard-coded protocol/serialization/language/runtime in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) surface layers: **0** (LAW USIS-05, obligation 4).
4. Surface projecting an uncertified service: **0** (Dependency Closure; obligation 14).
5. USIS-017 edits to any frozen instrument: **0** (obligation 19).
6. Breaking rewrite of a published surface (non-versioned): **0** (append-only; obligation 7).
7. Circular ownership / dependency cycles: **0** (obligation 5).
8. Duplication of Service/Runtime/Engine/Pattern/…/Domain Architecture: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- A surface projecting an uncertified service ⇒ Dependency-Closure failure ⇒ rejected.
- A named protocol/language/runtime in the architecture ⇒ neutrality violation ⇒ rejected.
- A breaking rewrite of a published surface ⇒ append-only violation ⇒ rejected (must version).
- Absence of required evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART Q — Non-goals

- Authors **no** individual API/SDK surface instance and **no** generated client code (Wave-3 / Software stream).
- Is **not** the SERVICE/PLATFORM transport/serialization infrastructure, the Service tier (USIS-012), or any lower tier — all referenced.
- Defines **no** transport, serialization, language binding, or runtime.
- Names **no** protocol/serialization/language/runtime (LAW USIS-04); creates **no** competing surface registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-017 · API & SDK ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
