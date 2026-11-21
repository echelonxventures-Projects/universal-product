# USIS-012 — Service Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-012 (Service Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000014` (next free after `UCOS-USIS-000013` = USIS-013). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Service Architecture (EVO-USIS-012) — establish the constitutional Service-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Service tier (governed, contract-first surface over runtime-hosted capabilities) owned by the substrate (subordinate to USIS-001…011, USIS-013, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Service tier (USIS-004 tier 16) — the governed contract surface exposing runtime-hosted engine behavior (reason/learn/predict/analyze/simulate/…) |
| DEPENDS-ON | USIS-013 · USIS-011 · USIS-004 · USIS-002 · SERVICE program (referenced) · `14-SECURITY` (referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **16 (Service)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 20 (Intelligence/Analytics) · Part 19 (Knowledge) · Part 21 (Learning); Constitution Part E (cross-cutting capability contract) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/07/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the service-contract mandate conferred by USIS-001 (Part E cross-cutting interfaces / LAW USIS-04 technology neutrality) and the USIS-004 Service tier, exposing the Runtime tier (USIS-013), and referencing the SERVICE program's universal service machinery and Security controls. Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-012-SERVICE-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 8 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/13-SERVICES/` per USIS-005 §2 (area 13 = SERVICES) — no variance; no structure invented. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The SERVICE program's universal service machinery and `14-SECURITY` controls are **referenced**; the canonical home governs and this architecture holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Service tier** — the governed, contract-first surface that exposes runtime-hosted engine behavior (reason, learn, predict, analyze, simulate, …) to consumers. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/13-SERVICES/` home and defines service abstraction, identity, contracts, lifecycle, discovery, composition, orchestration, governance, and dependency realization — remaining technology-agnostic, protocol-agnostic, infrastructure-agnostic, deployment-agnostic, and implementation-independent (LAW USIS-04), and never duplicating the SERVICE program's universal service machinery. **This instrument establishes only the Service-tier architecture.** It authors **no** individual service instance — those are separately-authorized later (Wave-3) realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the service-contract mandate of USIS-001 and the Service tier (16) of the USIS-004 meta-model:

- **USIS-004 Part C tier 16** — Service (parent = Runtime). USIS-012 is the constitutional architecture and rule-set for this tier.
- **USIS-001 Part E** — every USIS universe/discipline/domain exposes the cross-cutting interfaces (`register · describe · compose · govern · secure · monitor · observe · meter · bill · audit · prove · comply · certify · discover · search · remember · know · reason · simulate · compile · evolve · explain`); the Service tier binds these verbs to service operations by contract.
- **USIS-001 LAW USIS-04** — the service is a contract; it names no transport/protocol/framework/infrastructure/deployment; the API/SDK tier (USIS-017) projects it onto surfaces, the SERVICE program provides transport.
- **USIS-013 (Runtime)** hosts the executing capability; the SERVICE program provides universal service machinery; `14-SECURITY` provides controls. USIS-012 `Depends-On` Runtime and **references** SERVICE/Security and the reachable lower tiers — never duplicating their architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-012).** This architecture:
- creates the `15-…/13-SERVICES/` home and this single registered architecture artifact;
- defines the Service **abstraction, ontology/taxonomy, identity, lifecycle, contracts, discovery, composition, orchestration, dependency model, registry model, governance** (Parts B–N);
- founds downward-only on `USIS-013/011/004/002` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** service instance, and begins **no** Wave-3 realization;
- reuses, without duplication, the SERVICE program machinery, `14-SECURITY` controls, the registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/13-SERVICES/` already classifies to USIS/VOL-024).

## PART B — Service architecture & abstraction (the Service node)

A service is a typed node of the canonical form:

```
{ id: USIS-SVC-<NAME>, home: 13-SERVICES/<NAME>/, tier: 16,
  runtime: <USIS-RUN-* host>, operations: [ { verb, pre, post, contract } ],
  governance_bindings, observability_bindings, owner, status }
```

- **Abstraction.** A service is the agnostic contract over a runtime-hosted (USIS-013) capability; it abstracts *what* is offered (operations + pre/post-conditions), not *how/where* it runs.
- The node is the meta-model parent of the API tier (USIS-004): API/SDK (USIS-017) projects the service contract onto surfaces.
- It is **specification only** — names no transport/protocol/framework (LAW USIS-04); produces no code (implementation independence, Part K).

## PART C — Service ontology (reference to USIS-005)

Every service is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares the service concepts (operation, contract, governance binding, observability binding) and their relations to runtime/capability concepts. Ontology Closure (obligation 11) governs. USIS-012 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Service taxonomy (reference to USIS-005)

Every service occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the service taxonomy of kinds (reason / learn / predict / analyze / simulate / …). Taxonomy Closure (obligation 12) governs. USIS-012 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Service identity

Each service has a Universal ID and a native `USIS-SVC-*` identity, exactly one canonical owner, and one canonical home under `13-SERVICES/` (LAW USIS-05, No-Orphan). Identity is append-only and never reused (CR-INF-007).

## PART F — Service lifecycle

A service node follows, under UCIC-001:

```
DEFINED → BOUND (to runtime) → GOVERNED (verbs + observability bound) → REGISTERED → EVOLVING
```

New operations append to the contract; existing operations are never rewritten in place (append-only; obligation 7). No stage skipped; defect-driven REOPEN only.

## PART G — Service contracts

Each service operation is a contract: `verb` (a Constitution Part E cross-cutting verb), `pre`-conditions, `post`-conditions, and an agnostic I/O `contract`. The full verb set is projectable (Part E). Contracts are protocol/transport-neutral; the API/SDK tier (USIS-017) realizes them on concrete surfaces.

## PART H — Service discovery & composition

- **Discovery.** Services are discoverable via the `describe`/`discover`/`search` verbs and the Architecture/Capability registries; discovery is contract-based, not endpoint-based (no infrastructure coupling).
- **Composition.** A service composes other services and its runtime-hosted engine by **reference** (contract-to-contract), never by embedding; composition is acyclic (obligation 5).

## PART I — Service orchestration

The service tier orchestrates *operation-level* invocation over its runtime host (sequencing operations, honoring pre/post-conditions). Execution-mode/hosting orchestration belongs to Runtime (USIS-013) and member resolution to Engine (USIS-011) — no overlap (Zero-Overlap, obligation 3).

## PART J — Service dependency model, Runtime/Engine/Pattern realization

| Realization (by reference) | Model |
|----------------------------|-------|
| **Runtime realization** | a service is bound to a Runtime host (USIS-013) that executes it; runtime owned by USIS-013, referenced |
| **Engine realization** | the runtime hosts the Engine (USIS-011) whose execution the service exposes; referenced |
| **Pattern realization** | the engine executes the Pattern (USIS-010) realizing the capability's method; referenced |
| **Capability / Domain** | the service exposes a Capability (USIS-006) in its Domain (USIS-007) context; referenced |

- **Dependency model.** `Depends-On` runs downward to `USIS-013/011/004/002` (+ references SERVICE/`14-SECURITY`); `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). USIS-017 (API/SDK) `Depends-On` this tier — Service founds API.

## PART K — Registry integration & Runtime/technology independence

- Services are recorded in the **Architecture Registry** (#10) and, for execution, the **Execution Registry** (#5); governance/metering/audit bindings resolve against SERVICE/Security/Data registries by reference. Append-only, deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`); projection by `ukb build`; no parallel registry (LAW USIS-02).
- **Independence.** The Service tier is technology-agnostic, protocol-agnostic, infrastructure-agnostic, deployment-agnostic, and implementation-independent: it defines contracts, not endpoints/transports/deployments. A service is fully defined without any protocol, infrastructure, or deployment present.

## PART L — Validation model

Discharged by USIS-014 (referenced): a service is valid only if its contract is complete (pre/post per operation), its governance/observability verbs are bound, its runtime dependency is certified (Dependency Closure), and no transport/framework is named (agnosticism, obligation 1). Explanation coverage of service-mediated decisions is required (LAW USIS-07).

## PART M — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms contract completeness, cross-cutting-verb coverage, agnosticism, and canonical ownership.

## PART N — Evidence model & Governance model

- **Evidence (→ USIS-016).** UCIC-001 Output-5: service-contract record, verb-binding matrix, dependency-satisfaction note (runtime certified), observability/audit traces. Absence ⇒ NOT-DONE (TRACK-001).
- **Governance model.** Each service binds the `govern · secure · comply · audit · meter · bill` verbs by contract to the SERVICE/Security/governance surfaces (referenced). Governance is a mandatory facet (C-00.3); a service missing a governance/audit binding is fail-closed NOT integrated.

## PART O — Security considerations

Security is **referenced** to `14-SECURITY` (never re-homed, LAW USIS-02/05): every service binds `secure`/`comply` verbs to the universal Security controls (authn/authz, policy, audit). USIS-012 introduces no bespoke security mechanism; it declares the binding contract. Unbound security on an externally-reachable operation is a fail-closed governance defect.

## PART P — Reuse model

Reuse-First (LAW USIS-02): the SERVICE program's universal service machinery, Security controls (`14-SECURITY`), and metering/billing surfaces are **referenced**, never re-homed. USIS services add only the science-intelligence contract specialization. Runtime (USIS-013), Engine (USIS-011), Pattern (USIS-010), Algorithm (USIS-008), Model (USIS-009), Capability (USIS-006), Domain (USIS-007) are referenced.

## PART Q — Constitutional invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations).**
1. Duplicate service catalog/registry or duplication of SERVICE-program machinery by USIS-012: **0** (LAW USIS-02).
2. Hard-coded transport/protocol/framework/infrastructure/deployment in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) service layers: **0** (LAW USIS-05, obligation 4).
4. Service missing a governance/audit/security binding: **0** (C-00.3 seven facets).
5. USIS-012 edits to any frozen instrument: **0** (obligation 19).
6. Service exposing an uncertified runtime: **0** (Dependency Closure; obligation 14).
7. Circular ownership / dependency / composition cycles: **0** (obligation 5).
8. Duplication of Runtime/Engine/Pattern/Algorithm/Model/Capability/Domain Architecture: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- A service exposing an uncertified runtime ⇒ Dependency-Closure failure ⇒ rejected.
- A missing governance/audit/security verb binding ⇒ fail-closed (C-00.3).
- A named transport/framework/deployment in the contract ⇒ agnosticism violation ⇒ rejected.
- Two services claiming one concern ⇒ Zero-Overlap violation. Absence of required evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART R — Non-goals

- Authors **no** individual service instance (Wave-3, per-member).
- Is **not** the SERVICE program's universal service infrastructure, the API/SDK surfaces (USIS-017), the Runtime (USIS-013), or any lower tier — all referenced.
- Defines **no** transport, protocol, deployment, or security mechanism (referenced to SERVICE/`14-SECURITY`).
- Names **no** technology/protocol/infrastructure/deployment (LAW USIS-04); creates **no** competing service registry (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-012 · SERVICE ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
