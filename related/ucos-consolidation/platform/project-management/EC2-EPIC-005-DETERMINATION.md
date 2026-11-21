# EC2-EPIC-005 — Project Management Runtime — Determination

| Field | Value |
|-------|-------|
| ARTIFACT ID | EC2-EPIC-005-DETERMINATION |
| ARTIFACT | Project Management Runtime — Implementation Specification Determination |
| ARTIFACT TYPE | Determination artifact only (no implementation, no code, no service, no runtime, no API, no schema, no infrastructure, no registry, no directory beyond this file's own) |
| PROGRAM | UCOS EC-2 Platform Realization Program |
| EPIC | EC2-EPIC-005 — Project Management |
| CLASSIFICATION | Platform determination — implementation specification derived from repository evidence |
| STATUS | ACTIVE — determination only |
| BRANCH | `governance-reconciliation` |
| REPOSITORY STATE | HEAD `f1db627`; origin synchronized; working tree clean |
| BASELINE DATE | 2026-07-17 |
| VOLUME (per GOV-006) | VOL-006 (PLATFORM / `PLT`) — `^platform/` category mapping |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |
| INDICATIVE TASK RANGE | EC2-TASK-000089 … EC2-TASK-000096 (contract §5) |

*This artifact **determines and defines only** the implementation specification for the Project Management Runtime authorized by `platform/EC2-IMPLEMENTATION-STATUS-DETERMINATION.md` (`NEXT IMPLEMENTATION TARGET DETERMINED → EC2-EPIC-005`). It creates no runtime code, no service, no API, no schema, no infrastructure, no database, no registry, and no directory beyond this file's own. It invents no architecture, no roadmap, no governance, no capability group, and no lifecycle model: every construct it names traces to an existing physical repository artifact — the EC-2 governing contract, the certified Foundation/Identity/Observability layers, the completed Workspace and Administration runtimes, and the Security Runtime. It is subordinate to the frozen corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` — read-only, DP-03), the EC-2 Platform Realization Program, and every prior governance/execution determination; where any statement conflicts with a higher instrument, the higher instrument governs. It carries the EC-1 provisional-state disclosure verbatim, asserts no constitutional finality, and the external gates EC-1…EC-6 remain open.*

---

## 1. EXECUTIVE SUMMARY

`EC2-EPIC-005 — Project Management` is the sixth EC-2 platform runtime and the single unblocking node on the program critical path (`… → 002 → 005 → 006 → 007 → 010 → 011 → 012 → 014 → GO-LIVE`). Its authoritative basis is the EC-2 contract `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`: §2.1 Surface #4 **Project Management** ("Create/organize projects; associate blueprints, requests, artifacts; lifecycle & status"), **PC-03** (Workspace & project lifecycle), §3.2 RBAC row **Workspace/project lifecycle**, §4 architecture layer **L3 Application**, §5 EC2-EPIC-005 acceptance ("Project lifecycle states defined & enforced; associations to blueprints/requests/artifacts intact; status derivable deterministically"), and acceptance criterion **P3** (Workspace & Project Integrity).

The central architectural finding, drawn directly from repository evidence:

> **PC-03 is a single "workspace & project lifecycle" capability, and the §3.2 RBAC matrix binds it to a single capability group `workspace-project-lifecycle` (`CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE`, matrix index 3). EC2-EPIC-004 realized the *workspace* half of PC-03 against that group. EC2-EPIC-005 realizes the *project* half against the SAME group — it introduces no new capability group, no new authority, and no new authorization logic.**

A second decisive finding governs scope: the entities a project "associates" — **blueprints (EPIC-006), generation requests (EPIC-007), and artifacts (EPIC-009)** — **do not yet exist** in the repository (§4/§5 of the status determination). Therefore the Project Management Runtime models associations **by reference only**: append-only, content-addressed *association records* binding a project to an opaque, typed external reference (`kind ∈ {blueprint, request, artifact}` + `ref_id`). "Associations intact" means the **referential integrity of the association records themselves** (no dangling project, no duplicate binding, associations bound to a valid project, deterministic removal on archival) — **not** resolution of a not-yet-implemented downstream runtime. This mirrors the certified "by reference" seam pattern of `EC2-CAP-SEC-001` (classification bound to the L7 seam by reference) and resolves the apparent paradox that EPIC-005 precedes the epics whose entities it references.

The runtime is a strictly **additive L3 composition point** that: authorizes **only** through the certified Identity Layer (`AuthorizationService`) on the existing `workspace-project-lifecycle` group; is scoped **within** a workspace and isolated by the reused `platform.workspace.isolation.tenants_isolated` rule; observes **only** through the certified Observability Layer (governed events on the L8 bus + L8 `AuditTrail`); persists/discovers **only** through the Foundation registries/events with content-addressed IDs; and reuses the completed Administration and Security runtimes where they already own a concern. It creates no new authority, no second audit-of-record, no second isolation rule, and no new identity scheme.

**All twelve determination readiness conditions (§11) are met; all upstream dependencies are COMPLETE/CERTIFIED; no architectural invention is required; no gap blocks execution.**

**Verdict: `IMPLEMENTATION AUTHORIZED`** — see §15.

---

## 2. CONSTITUTIONAL BASIS

All inputs are physically present and `ACTIVE`/COMPLETE. "Constitutional" here means the governing execution contract and the standing governance/execution determinations that authorize the EC-2 lane; the Project Management Runtime asserts no constitutional authority of its own.

### 2.1 Governing authority chain

| # | Source | Path | Governing role |
|---|--------|------|----------------|
| A-1 | EC-2 Platform Realization Program | `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md` | **Primary authority.** §2.1 Surface #4 Project Management; §2.2 PC-03; §3.2 RBAC row `workspace-project-lifecycle`; §4 L3 Application; §5 EC2-EPIC-005 epic definition + acceptance; §6.2/§6.4 dependency graph + critical path; §9 P3 acceptance; §10 certification classes; §Authority-Boundary (additive-only, per-epic admission). |
| A-2 | EC2 Implementation Status Determination | `platform/EC2-IMPLEMENTATION-STATUS-DETERMINATION.md` | The authorization that names EC2-EPIC-005 the next authorized target (READY). |
| A-3 | GOV-004 — Implementation Execution Authorization | `02-MASTER/UCOS-GOV-004-...md` | IMPLEMENTATION CONDITIONALLY AUTHORIZED; single authorized lane = EC-2. |
| A-4 | UCOS-EXEC-001 — EC-2 Execution Activation | `02-MASTER/UCOS-EXEC-001-...md` | EC-2 EXECUTION CONDITIONALLY ACTIVATED, subject to per-epic admission (EN-5) + standing conditions. |
| A-5 | UCOS-EXEC-002 — Next-Epic Sequencing | `02-MASTER/UCOS-EXEC-002-...md` | Records EPIC-005 dependency = EPIC-004, and EPIC-005 as prerequisite for the generation spine. |
| A-6 | GOV-006 — Repository Governance Correction | `02-MASTER/UCOS-GOV-006-...md` | Category→volume mapping: `^platform/` ⇒ PLATFORM / `PLT` / VOL-006 (governs registration). |
| A-7 | REG-AUTO-001 — Automatic Artifact Registration Standard | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-...md` | The registration discipline applied after each implementation commit (git evidence: every prior EC2 unit followed by a `REG-AUTO-001: register …` commit). |
| A-8 | STATUS-001 — Status Determination Standard | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-STATUS-001-...md` | Evidence→status discipline; certification never inferred from source-asset coverage. |

### 2.2 Governing principles (from A-1 §Authority-Boundary and epic invariants)

- **Additive-only over EC-1 and prior layers.** 0 `engine/**` modifications; 0 modifications to Foundation/Identity/Observability/Workspace/Administration/Security.
- **Frozen corpus read-only (DP-03).** No writes to `00-BOOK/`, `00-SOURCE/`, `99-FREEZE/`.
- **Least-privilege, fail-closed (PL-04).** All access authorization-derived; deny by default.
- **Determinism & reproducibility (P5).** Identical inputs ⇒ identical content-addressed IDs and evidence fingerprints; no wall-clock in identities or ordering (caller-supplied logical `tick`/`now`).
- **Append-only audit (PC-16 / OP-C3).** Every governed action emitted onto the Foundation `EventBus` and captured by the L8 `AuditTrail`.
- **Contract-first, versioned (AR-03 / PL-05).** Published `ContractRef`s consumers bind to by reference.
- **No duplication.** Reuse the single certified seam for each concern (identity, isolation, audit).
- **Provisional-state disclosure** carried on every artifact and record.

### 2.3 Mandatory constraints / applicable runtime laws

- **No new capability group.** EPIC-005 authorizes against the existing `CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE` (matrix index 3), verbatim from `platform/identity/roles.py`.
- **No new authorization logic / no new authority.** Sole decision point = `platform.identity.AuthorizationService` (as Workspace and Administration already do).
- **No second isolation rule.** Reuse `platform.workspace.isolation.tenants_isolated`.
- **No second audit-of-record.** Reuse `platform.observability.AuditTrail`.
- **No downstream-runtime dependency.** Associations are record-only references; the runtime does not import or require blueprint/request/artifact runtimes (they are not yet implemented).
- **No filesystem writes; no server; no socket.** Deterministic in-memory/metadata runtime model (Workspace/Administration precedent).

### 2.4 Authority boundary

The Project Management Runtime holds **ENGINEERING-EXECUTION-ONLY** authority. It creates no constitutional/governance/ratification/EC-series authority; it neither closes nor asserts any external gate (EC-1…EC-6 remain open); it is subordinate to every instrument in §2.1 and to the frozen corpus.

---

## 3. MISSION DEFINITION

### 3.1 Purpose

Realize the **project** half of PC-03 as a governed, additive, deterministic **Project Management Runtime (L3 Application)**: a scoped organizational container, subordinate to a workspace, that lets authorized principals create and organize **projects**, associate work references (blueprints, requests, artifacts) to them **by reference**, drive each project through a deterministic lifecycle, and expose a deterministically-derivable project status — with authorization-scoped discovery/search, cross-runtime health, append-only audit, and reproducible evidence.

### 3.2 Responsibilities (summary; detailed in §4)

1. Create/organize **projects** within a workspace (authorization-gated; creator recorded as project owner).
2. Maintain a deterministic **project lifecycle** state machine and enforce legal transitions.
3. Maintain **association records** binding a project to typed external references (blueprint/request/artifact) with referential integrity.
4. Derive a deterministic **project status** from lifecycle state + association posture.
5. Provide authorization- and isolation-scoped **project discovery/search** (PC-13).
6. Emit governed-action **telemetry/audit** through L8 (PC-16).
7. Expose **cross-runtime health** and reproducible **project evidence** (OP-C1 / P5).

### 3.3 Outcomes (acceptance-aligned, A-1 §5)

- Project lifecycle states are **defined & enforced** (illegal transitions refused, fail-closed).
- Associations to blueprints/requests/artifacts are **referentially intact** (no dangling/duplicate/cross-project bindings).
- Project status is **derivable deterministically** (pure function of stored state + associations).
- Cross-workspace/tenant isolation holds in **100%** of isolation tests (P3).

### 3.4 Runtime role

L3 Application composition point directly downstream of the Workspace Runtime (a project is always scoped to a workspace) and upstream of the generation spine: EPIC-006 (Blueprint Catalog), EPIC-007 (Generation Requests), and EPIC-009 (Artifact Explorer) will bind their entities to projects through the association-by-reference surface this runtime publishes. It is the container that "organizes blueprints, requests, artifacts" (A-1 §2.1 #4).

---

## 4. RUNTIME RESPONSIBILITY DETERMINATION

For each responsibility: source authority · purpose · runtime obligation · dependency requirements.

| # | Responsibility | Source authority | Purpose | Runtime obligation | Dependency requirement |
|---|----------------|------------------|---------|--------------------|------------------------|
| RR-1 | **Project creation & organization** | A-1 §2.1 #4; PC-03; §3.2 `workspace-project-lifecycle` | Create/organize projects within a workspace | Authorization-gated create (CREATE grant); creator recorded as project owner; content-addressed `project_id` keyed by `{workspace_id, slug}`; idempotent | Identity `AuthorizationService`; Workspace registry (parent workspace must exist/active); Foundation `content_hash` |
| RR-2 | **Project lifecycle state machine** | A-1 §2.1 #4 "lifecycle & status"; §5 "lifecycle states defined & enforced" | Deterministic, enforced project lifecycle | Pure fail-closed transition function; illegal/terminal-exit/no-op transitions refused; each transition an ordered append-only event (caller `tick`) | Workspace `lifecycle.py` pattern (precedent); Foundation events |
| RR-3 | **Association-by-reference** | A-1 §2.1 #4 "associate blueprints, requests, artifacts"; §5 "associations … intact" | Bind projects to typed external work references | Append-only association records `{project_id, kind, ref_id}`; referential integrity (valid project, no duplicate binding, no cross-project leakage); deterministic removal on archival | Foundation `content_hash`; **no** dependency on EPIC-006/007/009 runtimes (record-only) |
| RR-4 | **Deterministic status derivation** | A-1 §5 "status derivable deterministically" | Reproducible project status | Pure function: lifecycle state + association posture ⇒ derived status summary; no wall-clock; identical inputs ⇒ identical output | Foundation `content_hash` (fingerprint) |
| RR-5 | **Project membership / ownership scoping** | A-1 §3.2 `workspace-project-lifecycle`; P3 | Scope project mutation to owner/authorized principals | Owner recorded at creation; mutations require CREATE/ADMINISTER grant; workspace membership respected | Identity; Workspace membership (by reference) |
| RR-6 | **Authorization- & isolation-scoped discovery/search** | A-1 §2.2 PC-13; §3.2; P3 | Discover projects without leaking across tenant/workspace | READ-gated; results filtered by tenant isolation + workspace scope; never surface a cross-tenant/cross-workspace project | Identity; `platform.workspace.isolation.tenants_isolated` |
| RR-7 | **Governed-action telemetry & audit** | A-1 §2.2 PC-16; §9 P9/OP-C3 | Auditable project actions | Emit `project.created` / `project.lifecycle.transitioned` / `project.association.{added,removed}` / `project.access.evaluated` onto L8 bus; captured by L8 `AuditTrail` | `platform.observability.ObservabilityService` / `AuditTrail` |
| RR-8 | **Cross-runtime health** | A-1 §9 OP-C1/G1 | Health under fault | Register project health checks into L8 `HealthRegistry`; an integrity fault (e.g., orphaned association) drives `UNHEALTHY` | `platform.observability.HealthRegistry` / `HealthCheck` / `HealthStatus` |
| RR-9 | **Reproducible project evidence** | A-1 §9 P5; §10 | Deterministic certification evidence | Emit a `ProjectEvidence` fingerprint; identical across independent processes | Foundation `content_hash` |
| RR-10 | **Contract publication** | A-1 §4 L2/L3; AR-03/PL-05 | Consumers bind by reference | Publish versioned `ContractRef`s into the Foundation `ServiceRegistry` | Foundation `platform_contract` / `ContractRef` / `ServiceRegistry` |

---

## 5. CAPABILITY DECOMPOSITION

The decomposition is driven by **what requires net-new record-only realization** versus **what is reused by reference**, mirroring the Workspace and Administration module topology (12–13 modules) exactly. Proposed importable runtime package: **`platform/projects/`** (Python identifiers cannot contain hyphens; `platform.projects` is the hyphen-free analogue of `platform.workspace`/`platform.administration`; this determination FILE resides at the mission-specified `platform/project-management/` path — see §12 naming reconciliation).

### 5.1 Sub-capabilities (net-new, record-only)

| Sub-capability | Module | Constitutional basis | Responsibility |
|----------------|--------|----------------------|----------------|
| **PROJ-CONTRACT** | `contracts.py` | A-1 §4; PL-05 | Vocabulary (`ProjectStatus`, `AssociationKind`, `Project`, `ProjectAssociation`) + published `ContractRef`s + verb→permission map; binds to `CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE` |
| **PROJ-LIFECYCLE** | `lifecycle.py` | A-1 §2.1 #4; §5 | Deterministic project state machine + append-only transition event (workspace `lifecycle.py` pattern) |
| **PROJ-REGISTRY** | `registry.py` | A-1 §2.1 #4; PC-03 | Append-only, content-addressed project registry: create/register/resolve/discover; parent-workspace binding |
| **PROJ-ASSOC** | `associations.py` | A-1 §2.1 #4; §5 | Association-by-reference registry: bind/unbind typed references; referential integrity guards |
| **PROJ-STATUS** | `status.py` | A-1 §5 | Deterministic derived-status computation (lifecycle + associations) |
| **PROJ-SEARCH** | `search.py` | A-1 §2.2 PC-13 | Authorization- + isolation-scoped project discovery/search |
| **PROJ-CONTEXT** | `context.py` | A-1 §4 L3 | Immutable resolved project runtime context (selected project + granted actions) |
| **PROJ-METADATA** | `metadata.py` | A-1 §2.1 #4 | Immutable project metadata value type (workspace `metadata.py` pattern) |
| **PROJ-HEALTH** | `health.py` | A-1 §9 OP-C1 | Project health checks over the reused L8 health model |
| **PROJ-ERRORS** | `errors.py` | A-1 §Authority-Boundary | `EC2-PROJ-*` error taxonomy over `platform.foundation.errors.PlatformError` |
| **PROJ-SERVICE** | `service.py` | A-1 §4 L3 | `ProjectService` composition root + `ProjectAccess` + `ProjectEvidence` (two-gate access decision) |
| **PROJ-BOOTSTRAP** | `bootstrap.py` | A-1 §4; §8 | `bootstrap_projects(context)` — composes identity + observability + workspace + projects; publishes contracts; registers health |
| **PROJ-INIT** | `__init__.py` | — | Package surface re-exports |

This 13-module topology is identical in shape to `platform/workspace/` and `platform/administration/` (proven templates), preventing both under- and over-decomposition.

### 5.2 Reused-by-reference (declared non-goals — NOT sub-capabilities)

| Concern | Reused from | Why not re-realized |
|---------|-------------|---------------------|
| Identity / authorization | `platform.identity` (`AuthorizationService`, `PermissionEngine`, `RoleRegistry`, `AccessDecision`) | Sole certified decision point; no new authority |
| Tenant/workspace isolation | `platform.workspace.isolation.tenants_isolated` | Certified isolation rule (P3) |
| Parent workspace binding | `platform.workspace` registry/context | Projects are scoped to workspaces; workspace already owns workspace identity |
| Audit-of-record / telemetry | `platform.observability` (`AuditTrail`, `ObservabilityService`, `MetricRegistry`, `LogBuffer`, `TraceRecorder`, `HealthRegistry`) | Certified L8; no second audit/telemetry stack |
| Policy administration / audit export | `platform.administration` | Administrative surface already realized |
| Security classification / findings | `platform.security` (EC2-CAP-SEC-001) | Security posture recorded there; project runtime raises no new security model |
| Contracts / events / IDs / hashing | `platform.foundation` (`content_hash`, `EventBus`, `ServiceRegistry`, `platform_contract`) | Certified primitives |

### 5.3 Capability boundaries / implementation partitions

- **Records, never enacts** downstream work: the runtime stores project↔reference bindings; it does not create, validate, generate, or resolve blueprints/requests/artifacts.
- **Organizes, never authors**: it is a container/lifecycle/association surface, not a blueprint author (EPIC-006) or a generation orchestrator (EPIC-007).
- **Scoped within a workspace**: no project exists outside a resolvable workspace; cross-workspace association is refused.

---

## 6. DEPENDENCY ANALYSIS

### 6.1 Upstream dependencies

| Dependency | Type | Component consumed | Status | Contract |
|------------|------|--------------------|--------|----------|
| EC2-EPIC-004 Workspace | **Required** | `Workspace`, workspace registry/context, `isolation.tenants_isolated`, membership | COMPLETE | Parent-scope binding + isolation rule |
| EC2-EPIC-002 Identity | **Required** | `AuthorizationService`, `CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE`, `AccessDecision`, `PermissionEngine`, `RoleRegistry` | COMPLETE / CERTIFIED | Sole authorization seam |
| EC2-EPIC-001 Foundation | **Required** | `content_hash`, `EventBus`, `ServiceRegistry`/`ServiceDescriptor`, `PlatformContext`, `Permission`, `Principal`, `PlatformError`, `platform_contract`, `ContractRef` | COMPLETE | Primitives, contract publication, governed events |
| EC2-EPIC-013 Observability | **Required** | `ObservabilityService`, `AuditTrail`, `HealthRegistry`, `HealthCheck`, `HealthStatus`, metric/log/trace | COMPLETE | Telemetry/audit/health |
| EC2-CAP-ADMIN-001 Administration | **Reused (optional)** | policy/audit-export surface | COMPLETE | Consumed if a project-policy view is later surfaced; not required for core |
| EC2-CAP-SEC-001 Security | **Reused (optional)** | security classification/finding recording | COMPLETE | Project security posture recorded there, by reference |
| EXEC-REG-001 | **Reused (optional)** | `security`/DOMAIN-D signal spine | COMPLETE | Signal emission by reference |
| EC-1 Realization Engine | **Required (integrity)** | none consumed directly | CERTIFIED | 0 modifications (P10) |

### 6.2 Downstream dependencies

| Downstream | Effect of EPIC-005 | Relationship |
|------------|--------------------|--------------|
| EC2-EPIC-006 Blueprint Catalog | **Enabled/unblocked** | Blueprints associate to projects via the PROJ-ASSOC surface (`kind = blueprint`) |
| EC2-EPIC-007 Generation Requests | **Enabled (transitive)** | Requests associate to projects (`kind = request`); requires EPIC-006 first |
| EC2-EPIC-008 Execution Dashboard | Enabled (transitive) | Surfaces request state within project scope |
| EC2-EPIC-009 Artifact Explorer | Enabled (transitive) | Artifacts associate to projects (`kind = artifact`) |
| EC2-EPIC-010/011/012 | Enabled (transitive) | Downstream of 007 along the spine |

**Currently blocked-by-EPIC-005:** EPIC-006 (direct), and transitively 007→{008,009,010}→011→012. Completing EPIC-005 closes the sole open dependency root (per A-2 §3.3).

### 6.3 Dependency graph

```
        EC-1 (certified)
          │
   EC2-EPIC-001 Foundation ──┬── EC2-EPIC-002 Identity ──┬── EC2-EPIC-004 Workspace
          │                  └── EC2-EPIC-013 Observability │        │
          │                                                 │        ▼
          └─────────────────(primitives, telemetry)─────────┴──▶  EC2-EPIC-005  ◀── (reuse) ADMIN-001, CAP-SEC-001
                                                                    Project Mgmt
                                                                        │  (association-by-reference surface)
                                     ┌──────────────────┬──────────────┴───────────────┐
                                     ▼                  ▼                               ▼
                          EC2-EPIC-006 Blueprint   EC2-EPIC-007 Generation      EC2-EPIC-009 Artifacts
                          (kind=blueprint)          (kind=request)               (kind=artifact)
```

All required upstream dependencies are **COMPLETE/CERTIFIED**; all dependency direction is inward/downward (AR-01); no cyclic or upward dependency exists; **nothing depends on EPIC-005 yet** (its dependents are unimplemented). Dependency closure: **CLOSED**.

---

## 7. TRACEABILITY DETERMINATION (requirements only)

| Obligation | Requirement |
|------------|-------------|
| **Authoritative-basis citation** | The completion report and every module docstring SHALL cite `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md` (§2.1 #4, PC-03, §3.2, §4 L3, §5, P3) as authoritative basis (GOV-001 Part 8; precedent: workspace/administration reports). |
| **Task traceability** | Every module/test SHALL map to a task in the indicative range EC2-TASK-000089…000096 (contract §5). |
| **Backward traceability** | Every project construct SHALL trace to its authority (project→PC-03→§2.1 #4; association→§2.1 #4/§5; status→§5). |
| **Forward traceability** | The PROJ-ASSOC surface SHALL be documented as the binding point for EPIC-006/007/009 (`kind` vocabulary published for downstream consumption). |
| **Evidence obligation** | A deterministic `ProjectEvidence` fingerprint SHALL be reproducible across independent processes (P5). |
| **Audit obligation** | Every governed project action SHALL be emitted onto the Foundation `EventBus` and captured by the L8 `AuditTrail` (append-only; PC-16/OP-C3). |
| **Reporting obligation** | A completion report `platform/projects/EC2-EPIC-005-COMPLETION-REPORT.md` SHALL record acceptance status, coverage, determinism evidence, and certification impact; the artifact SHALL be registered per REG-AUTO-001 (A-7). |
| **Identity preservation** | No existing Universal/Artifact/Registry/Relationship/Certification ID SHALL be changed; new IDs SHALL be content-addressed under new non-colliding prefixes (e.g. `UCOS-PROJ`, `UCOS-PASC`, `UCOS-PCTX`, `UCOS-PACC`, `UCOS-PEVT`). |

No implementation is specified here — obligations only.

---

## 8. OBSERVABILITY DETERMINATION

**Reuse the existing L8 Observability Runtime (EC2-EPIC-013). No duplicate telemetry system.**

| Requirement | Determination |
|-------------|---------------|
| Telemetry transport | All metrics/logs/traces flow through `platform.observability.ObservabilityService`; the runtime adds no second stack. |
| Governed events | `project.created`, `project.lifecycle.transitioned`, `project.association.added`, `project.association.removed`, `project.access.evaluated` emitted onto the Foundation `EventBus`, captured by the L8 `AuditTrail` (audit of record). |
| Coverage | Telemetry on **100% of governed project actions** (P9 analogue); an action lacking required telemetry fails readiness (PL-02 discipline; workspace/administration precedent). |
| Monitoring / health | Project health checks (e.g., referential-integrity probe) registered into the L8 `HealthRegistry`; an integrity fault drives `UNHEALTHY` (OP-C1/G1). |
| Reporting / evidence | `to_dict()` summaries report observability binding; `ProjectEvidence` provides the deterministic fingerprint. |
| Determinism | No wall-clock in telemetry ordering; caller-supplied logical `tick`. |

---

## 9. SECURITY DETERMINATION

**Reuse EC2-CAP-SEC-001 and the certified Identity Layer. No new security architecture.**

| Requirement | Determination |
|-------------|---------------|
| Authorization | Every project action authorized **only** by `platform.identity.AuthorizationService` on `CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE`; no new authority (P2). The verb→permission map: `CREATE_PROJECT→CREATE`; `INSPECT/DISCOVER/SEARCH→READ`; `TRANSITION_LIFECYCLE/ADD_ASSOCIATION/REMOVE_ASSOCIATION→CREATE` for the owning C/R roles and `ADMINISTER` for Platform Administrator; owner-scoping enforced. |
| Tenant/workspace isolation | Reuse `platform.workspace.isolation.tenants_isolated`; cross-tenant/cross-workspace project access refused (P3). |
| Security posture | Any project-scoped security finding recorded through `platform.security` (EC2-CAP-SEC-001) **by reference**; the project runtime raises no new security model, no new finding schema, no new zone/control. |
| Secrets (SEC-04) | The runtime stores no secret value; project metadata holds no credential material. |
| Least-privilege / fail-closed | Deny by default; malformed requests raise; denials returned as data. |
| Security dependencies | Identity (required), Security Runtime (reused, optional), Workspace isolation (required). |

---

## 10. REGISTRY DETERMINATION

**Reuse the Foundation registry/event infrastructure and the content-addressed identity discipline. Introduce no new identity scheme or allocator.**

| Registry / record | Determination | Lifecycle requirement |
|-------------------|---------------|-----------------------|
| **Project Registry** (`registry.py`) | Append-only, content-addressed store of `Project` records keyed by `{workspace_id, slug}` (id `UCOS-PROJ-…`); create/register/resolve/discover; fail-closed on duplicates | Create → (lifecycle) ACTIVE; transitions recorded as ordered append-only events; ARCHIVED terminal |
| **Association Registry** (`associations.py`) | Append-only store of `ProjectAssociation` records `{association_id, project_id, kind, ref_id}` (id `UCOS-PASC-…`); referential-integrity guards (valid project; no duplicate `{project_id, kind, ref_id}`; no cross-project rebinding) | Add (project must be non-terminal) → active; remove → append-only removal event; associations of an ARCHIVED project become immutable |
| **Lifecycle event log** (`lifecycle.py`) | Ordered, append-only `ProjectEvent` records (caller `tick`), reproducible | Append-only; no mutation |
| **Access/audit records** | Reuse L8 `AuditTrail`; project access recorded as `ProjectAccess` + governed event | Append-only (OP-C3) |
| **Records required** | `Project`, `ProjectAssociation`, `ProjectEvent`, `ProjectAccess`, `ProjectEvidence` | All immutable, content-addressed, serializable |
| **Evidence required** | Deterministic `ProjectEvidence` fingerprint (P5) | Reproducible across processes |

No registry writes to `00-BOOK/` (DP-03); registries are platform-owned and additive. RG discipline (record-only, timestamped by logical tick, attributed by principal reference, queryable) mirrors the Security Runtime §17 registries and the workspace/administration registries.

---

## 11. READINESS DETERMINATION

| # | Condition | Status | Evidence |
|---|-----------|--------|----------|
| R-1 | Authoritative basis complete & ACTIVE | ✅ | EC-2 contract §2.1 #4, PC-03, §3.2, §4, §5, P3 all present |
| R-2 | No invention required | ✅ | §3.2 capability group, workspace lifecycle pattern, association-by-reference seam all pre-exist |
| R-3 | Required upstream dependencies COMPLETE/CERTIFIED | ✅ | Foundation, Identity (CERTIFIED), Observability, Workspace all COMPLETE (A-2 §2) |
| R-4 | Authorization seam exists & certified | ✅ | `AuthorizationService` + `WORKSPACE_PROJECT_LIFECYCLE` group (`platform/identity/roles.py`) |
| R-5 | Isolation rule exists | ✅ | `platform.workspace.isolation.tenants_isolated` (EC2-EPIC-004) |
| R-6 | Audit-of-record / telemetry / health exist | ✅ | `platform.observability` (EC2-EPIC-013) |
| R-7 | Lifecycle state-machine precedent exists | ✅ | `platform/workspace/lifecycle.py` (deterministic, append-only) |
| R-8 | Association model realizable without downstream runtimes | ✅ | Record-only by-reference seam (SEC precedent); EPIC-006/007/009 not required |
| R-9 | Realization template proven | ✅ | Workspace (13 modules, 100% cov) + Administration (13 modules, 100% cov) |
| R-10 | Governance/volume mapping resolved | ✅ | GOV-006: `^platform/` ⇒ VOL-006 |
| R-11 | Determinism + coverage discipline available | ✅ | EC-2 CI (`--cov-fail-under=90`, ruff, determinism gate); current platform suite 915 passed / 96.29% |
| R-12 | Boundary (additive, record-only, non-enacting) definable | ✅ | §12; DP-03/P10/least-privilege encodable |

**No readiness condition is unmet. Dependency closure: CLOSED. Constitutional readiness: SATISFIED. Implementation readiness: SATISFIED.**

### VERDICT: **READY**

---

## 12. IMPLEMENTATION BOUNDARY DETERMINATION

### 12.1 EPIC-005 SHALL implement

1. A `platform/projects/` runtime package of ~13 additive modules (§5.1) — importable Python package (`platform.projects`).
2. A deterministic, content-addressed **project registry** scoped to a parent workspace.
3. A deterministic, enforced **project lifecycle** state machine with append-only transition events.
4. An append-only **association-by-reference** registry (`kind ∈ {blueprint, request, artifact}`) with referential-integrity guards.
5. A pure **derived-status** computation.
6. Authorization- and isolation-scoped **project discovery/search**.
7. A composed, fail-closed `ProjectService` with two-gate access (identity ∧ workspace/tenant isolation), reproducible `ProjectEvidence`, cross-runtime health, and a `bootstrap_projects` composition root publishing versioned contracts.
8. A full test suite (§13) at ≥90% gate / 100% module target, ruff-clean, determinism-verified.
9. A completion report + REG-AUTO-001 registration.

### 12.2 EPIC-005 SHALL NOT implement

- **No new capability group / role / authority** — reuse `WORKSPACE_PROJECT_LIFECYCLE` + `AuthorizationService`.
- **No blueprint authoring/validation** (EPIC-006), **no generation orchestration** (EPIC-007), **no artifact inspection** (EPIC-009) — associations are opaque references only; the runtime resolves/validates no referenced entity.
- **No second isolation rule, no second audit-of-record, no second telemetry stack** — reuse workspace/observability.
- **No new security model / finding schema / zone** — reuse EC2-CAP-SEC-001.
- **No new identity scheme or allocator** — content-addressed IDs via `content_hash`.
- **No EC-1 or prior-layer modification** (P10); **no frozen-corpus write** (DP-03); **no filesystem write, no server, no socket**.
- **No API/infrastructure/database** — deterministic in-memory/metadata runtime model (workspace/administration precedent).
- **No modification of the mission-specified determination path**: this file resides at `platform/project-management/EC2-EPIC-005-DETERMINATION.md`.

### 12.3 Naming reconciliation (evidence-based)

The mission specifies the determination artifact at `platform/project-management/`. Python package identifiers cannot contain hyphens, and the established runtime naming is single-word, hyphen-free (`platform.workspace`, `platform.administration`, `platform.security`). Therefore the **importable runtime package SHALL be `platform/projects/`**, while this determination document remains at the mission-specified `platform/project-management/` path. The completion report SHALL be co-located with the runtime at `platform/projects/EC2-EPIC-005-COMPLETION-REPORT.md` (workspace/administration precedent). This is a naming reconciliation, not an architectural change.

---

## 13. IMPLEMENTATION SEQUENCING

Derived from the workspace/administration realization order (contracts → value types → registries → composition → service/health/bootstrap → tests), mapped to EC2-TASK-000089…000096.

| Phase | Task(s) | Deliverable | Validation |
|-------|---------|-------------|------------|
| **P1 — Contracts & errors** | TASK-000089 | `errors.py`, `metadata.py`, `contracts.py` (vocabulary, verb→permission map, `WORKSPACE_PROJECT_LIFECYCLE` binding, `ContractRef`s) | contract/vocabulary tests; verb→permission map tests |
| **P2 — Lifecycle** | TASK-000090 | `lifecycle.py` (state machine + `ProjectEvent`) | legal/illegal/terminal transition tests; determinism |
| **P3 — Registry** | TASK-000091 | `registry.py` (project create/register/resolve/discover; parent-workspace binding) | idempotent id; duplicate fail-closed; workspace-scope tests |
| **P4 — Associations** | TASK-000092 | `associations.py` (by-reference bind/unbind; integrity guards) | no-dangling / no-duplicate / no-cross-project tests |
| **P5 — Status & context** | TASK-000093 | `status.py` (derived status), `context.py` (resolved runtime context) | deterministic status derivation; context validation |
| **P6 — Search** | TASK-000094 | `search.py` (authz + isolation scoped) | no cross-tenant/cross-workspace leak; ranking; fail-closed |
| **P7 — Service & health** | TASK-000095 | `service.py` (`ProjectService`, `ProjectAccess`, `ProjectEvidence`), `health.py` | two-gate access (every reason); CRUD; lifecycle; associations; integrity-fault → UNHEALTHY |
| **P8 — Bootstrap & integration** | TASK-000096 | `bootstrap.py`, `__init__.py`, `pyproject.toml` coverage line | contract publication; cross-runtime health; L8 audit; idempotency; cross-process determinism |

**Validation order:** per-phase unit tests → full platform suite green (EC-1 integrity preserved) → coverage gate (≥90%, target 100% module) → ruff clean → determinism (cross-process fingerprint) → acceptance (§14) → certification impact (§14.2).

**Certification order:** acceptance criteria (A-1 §5) → P3/P2/P5/P9/OP-C1/P10 impact → completion report → REG-AUTO-001 registration → (aggregate program roll-up toward M2 completion).

---

## 14. SUCCESS CRITERIA

### 14.1 Acceptance criteria (A-1 §5 EC2-EPIC-005)

| Criterion | PASS condition |
|-----------|----------------|
| Project lifecycle states defined & enforced | State machine implemented; every illegal/terminal-exit/no-op transition refused (fail-closed); accepted transitions recorded append-only |
| Associations to blueprints/requests/artifacts intact | Association records referentially intact: valid project, no duplicate binding, no cross-project leakage, deterministic removal; `kind` vocabulary published |
| Status derivable deterministically | Derived status is a pure function of lifecycle + associations; identical inputs ⇒ identical output/fingerprint |

### 14.2 Certification criteria (A-1 §9/§10)

| ID | Criterion | PASS condition |
|----|-----------|----------------|
| **P3** — Workspace & Project Integrity | Cross-tenant/workspace isolation holds in 100% of isolation tests; **project associations referentially intact** |
| P2 — Identity & Access | Adds no authority; all access via certified L7 seam on `workspace-project-lifecycle` |
| P5 — Determinism | Reproducible `ProjectEvidence` fingerprint across independent processes |
| P9 / OP-C3 — Observability & Audit | Telemetry on 100% of governed project actions; append-only L8 audit |
| OP-C1 — Health under fault | Integrity fault → `UNHEALTHY`; checks registered into L8 |
| P10 — EC-1 Integrity Preservation | 0 `engine/**`/prior-layer edits; 0 corpus writes; full suite green |
| PLAT-C1 — Platform composition | Additive, contract-first; versioned `ContractRef`s published; registry-driven bootstrap; idempotent |

### 14.3 Readiness / completion criteria

- Implementation complete (all §13 phases) · full suite green · coverage gate PASS (target 100% module) · ruff clean · determinism verified · identity preservation verified · completion report + REG-AUTO-001 registration.

### 14.4 Acceptance criteria (readiness for THIS determination)

All twelve §11 conditions met; verdict READY; dependency closure CLOSED.

---

## 15. AUTHORIZATION DETERMINATION

- **Rationale.** EC2-EPIC-005 is the authorized next target (A-2: `NEXT IMPLEMENTATION TARGET DETERMINED`), the first uncompleted node on the program critical path, the only remaining Wave-2 epic, and the sole root that unblocks the generation spine. Its complete implementation specification is derivable **entirely from repository evidence** with **no architectural, roadmap, or governance invention**: the capability group, authorization seam, isolation rule, audit/telemetry/health model, lifecycle state-machine pattern, and association-by-reference seam all physically pre-exist and are COMPLETE/CERTIFIED.
- **Dependency evidence.** Required upstream dependencies — Foundation (COMPLETE), Identity (COMPLETE/CERTIFIED), Observability (COMPLETE), Workspace (COMPLETE) — are all satisfied; dependency closure CLOSED (§6); no downstream runtime is required because associations are record-only references.
- **Readiness evidence.** All twelve readiness conditions met (§11); platform suite green (915 passed / 96.29% coverage); repository committed, synchronized, clean; EC-1 integrity preserved.
- **Boundary evidence.** Scope is fully bounded (§12): additive `platform/projects/`, record-only, non-enacting, reusing every certified seam; no protected-domain excursion; unaffected by the Generation→Implementation traceability break (RSK-01), which bounds EPIC-006/007, not EPIC-005.
- **Standing conditions (A-4).** Implementation SHALL proceed additive-only over EC-1 (P10), with 0 frozen-corpus writes (DP-03), determinism/reproducibility preserved (P5), TRACK-001 evidence→status (fail-closed), trace citations preserved (GOV-001 Part 8), and per-epic admission honored.

*This determination performs no implementation; it authorizes and fully specifies it. Implementation of EC2-EPIC-005 proceeds only under the standing conditions above.*

---

## IMPLEMENTATION AUTHORIZED

- **Epic:** `EC2-EPIC-005 — Project Management Runtime`
- **Runtime package (importable):** `platform/projects/` · **Determination path:** `platform/project-management/EC2-EPIC-005-DETERMINATION.md`
- **Capability group (reused, no new authority):** `CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE`
- **Dependency basis:** Foundation, Identity (CERTIFIED), Observability, Workspace — all COMPLETE; closure CLOSED
- **Readiness:** READY — all twelve conditions met (§11)
- **Task range:** EC2-TASK-000089 … EC2-TASK-000096
- **Repository state:** branch `governance-reconciliation`, HEAD `f1db627`, origin synchronized, working tree clean, platform suite 915 passed / 96.29% coverage

*Determination only. No code, service, runtime, API, infrastructure, database, or registry created; no existing implementation modified; no architecture, roadmap, or governance invented. Carries the EC-1 provisional-state disclosure verbatim; asserts no constitutional finality; external gates EC-1…EC-6 remain open.*

**END OF ARTIFACT — EC2-EPIC-005-DETERMINATION · ACTIVE · EVIDENCE-DERIVED · APPEND-ONLY · AUTHORITY-NEUTRAL · IMPLEMENTATION AUTHORIZED**
