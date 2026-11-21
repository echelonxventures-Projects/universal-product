# UCOS EC-2 — PLATFORM REALIZATION PROGRAM

| Field | Value |
|-------|-------|
| PROGRAM ID | EC-2 |
| PROGRAM NAME | UCOS Platform Realization Program |
| ARTIFACT | EC-2 Platform Realization Program — Governing Determination |
| ARTIFACT TYPE | Determination & Architecture Artifact (governing) |
| CLASSIFICATION | Authoritative Program-Governing Artifact — Execution Contract for all EC-2 work |
| STATUS | ESTABLISHED — ACTIVE (determination only) |
| PROGRAM POSITION | Second execution-engine program increment; successor to EC-1 (Realization Engine) |
| PREDECESSOR | EC-1 — UCOS Realization Engine (COMPLETE · 54/54 tasks · A1–A10 PASS · Program Closure Certification PASS) |
| SUCCESSOR | NONE (to be authorized on EC-2 closure) |
| BASELINE DATE | 2026-07-16 |
| CONSTITUENT AUTHORITY | NONE |
| GOVERNANCE AUTHORITY | NONE |
| RATIFICATION AUTHORITY | NONE |
| CONSTITUTIONAL EC-SERIES AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |

*This artifact defines the complete, authoritative execution contract for the **UCOS Platform Realization Program (EC-2)** — the program that transforms the certified EC-1 Realization Engine into an operational UCOS Platform. It is a **determination and architecture artifact only**: it contains no implementation, no code, no services, no infrastructure, and no UI. It establishes the program mission, scope, boundaries, platform definition, user model, platform architecture, epic structure, roadmap, go-live definition, tracking model, acceptance framework, and certification criteria. It holds **engineering-execution authority only**, invents no constitutional authority, authorizes no constitutional EC-series step, and neither modifies nor reinterprets the frozen certified corpus, EC-1, or any determination of any prior program. Where any realization derived from this artifact would conflict with a higher instrument (the frozen constitutional corpus, the Technology Constitution, the Implementation Governance Baseline, the Implementation Master Plan, or EC-1), the higher instrument governs and the derived realization is void to the extent of the conflict.*

---

## AUTHORITY BOUNDARY (MANDATORY)

1. **Naming disambiguation.** "**EC-2**" in this artifact denotes the **second Execution-engine program increment** (the successor to the EC-1 Realization Engine). It is **NOT** a constitutional EC-series external gate. The constitutional external gates **EC-1…EC-6 remain open**; this program neither closes, opens, satisfies, nor asserts any of them.
2. **Provisional-state disclosure (DE-05 / C-05 / IP-01).** Every artifact, decision, record, and system produced under EC-2 asserts **no constitutional finality, authority, or ratification** and carries the EC-1 provisional-state disclosure (`EC-1-PROVISIONAL-STATE`, `ENGINEERING-EXECUTION-ONLY`) verbatim. The UCOS Platform is a governed **engineering-execution substrate**, not a constitutional instrument.
3. **Subordination.** EC-2 is fully subordinate to, and must not contradict: the frozen certified corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` — read-only, DP-03), the Technology Constitution (58 principles), the Implementation Governance Baseline, the Implementation Master Plan, and the **complete, certified EC-1 Realization Engine**. EC-2 consumes these as **immutable inputs**.
4. **Additive-only over EC-1.** EC-2 **wraps and orchestrates** the EC-1 engine through its published, versioned contracts. EC-2 **SHALL NOT** modify, fork, re-derive, or re-certify any EC-1 module, and **SHALL NOT** weaken any EC-1 invariant (determinism, immutability, registry-only access, no frozen-corpus writes, fail-closed certification).
5. **Determination scope.** This artifact **determines and defines only**. It creates no code, no service, no schema binding, no infrastructure, and no UI. All such work is EC-2 *implementation*, authorized only after this governing artifact is established and each dependent epic is separately admitted per the roadmap (§6).

---

## SECTION 1 — PROGRAM CHARTER

### 1.1 Program Name
**UCOS Platform Realization Program.**

### 1.2 Program ID
**EC-2** (successor to EC-1). Epics are numbered `EC2-EPIC-0NN`; tasks continue the engine task sequence from `TASK-000055` onward (EC-1 terminated at `TASK-000054`).

### 1.3 Mission
> **Transform the certified EC-1 Realization Engine into an operational, multi-user UCOS Platform** — a governed, observable, access-controlled environment in which authorized users submit blueprints, request generation, and drive artifacts through compilation, deterministic build, signing, SBOM, runtime assembly, deployment/rollback descriptor production, validation, and certification, with full traceability and an append-only certification ledger — **without modifying, forking, or weakening any EC-1 capability or invariant.**

### 1.4 Vision
A single operational platform where the EC-1 engine's certified capabilities (Registry Resolution · Blueprint Classification · Compilation · Deterministic Build · Signing · SBOM · Runtime Assembly · Deployment Descriptor · Rollback Descriptor · Factory Generation · Validation · Certification · Certification Ledger) are exposed as **governed, self-service platform services** to defined user categories, each acting strictly within their permissions, over an auditable, deterministic, reproducible execution surface.

### 1.5 Objectives
- **O1 — Expose:** surface every certified EC-1 capability through a governed API and presentation layer, with **zero modification** to EC-1.
- **O2 — Control:** enforce authenticated, role-based, least-privilege access to every capability and artifact (PL-04).
- **O3 — Orchestrate:** provide end-to-end generation workflows (blueprint → compile → build → assemble → validate → certify) as tracked, resumable, auditable requests.
- **O4 — Observe:** provide real-time execution, validation, certification, and runtime dashboards backed by structured telemetry.
- **O5 — Operate:** provide governed runtime operations (deploy/rollback via EC-1 descriptors) with monitoring and reversibility (IP-08).
- **O6 — Preserve:** preserve determinism, immutability, registry-only access, frozen-corpus read-only guarantees, and fail-closed certification end to end.
- **O7 — Certify:** certify the platform itself against an objective acceptance framework (P1–P10) and a defined go-live gate (UCOS-GO-LIVE-001).

### 1.6 Success Criteria (program-level, objective)
| ID | Success criterion | Objective measure |
|----|-------------------|-------------------|
| SC-1 | All EC-2 epics delivered | 100% of determined epics (§5) at status COMPLETE with acceptance criteria met |
| SC-2 | Acceptance framework satisfied | P1–P10 (§9) all PASS |
| SC-3 | Go-live gate satisfied | UCOS-GO-LIVE-001 (§7) all 8 conditions PASS |
| SC-4 | EC-1 integrity preserved | EC-1 test suite + coverage gate re-run green; 0 modifications to `engine/**` EC-1 modules; 0 frozen-corpus writes |
| SC-5 | Determinism preserved | identical generation request ⇒ identical artifact hashes end to end (reproducibility gate green) |
| SC-6 | Program closure certified | EC-2 Program Closure Certification (§10) issued with verdict PASS and an intact certification ledger |

---

## SECTION 2 — PLATFORM DEFINITION

### 2.1 What constitutes the UCOS Platform
The **UCOS Platform** is the operational, multi-user system that exposes the certified EC-1 Realization Engine as governed self-service. It is composed of twelve capability surfaces. Each surface is a **consumer** of EC-1 (or of platform-native services); none re-implements an EC-1 capability.

| # | Surface | Definition | EC-1 capability consumed |
|---|---------|------------|--------------------------|
| 1 | **Portal** | Authenticated entry point, navigation, global search, notifications, context switching | (platform-native) |
| 2 | **Workspace** | A scoped, collaborative container binding a user/team to projects, blueprints, and requests | (platform-native) |
| 3 | **Identity** | Authentication, authorization, roles, sessions, API credentials (by reference; SEC-04) | (platform-native; aligns with Identity Platform architecture) |
| 4 | **Project Management** | Create/organize projects; associate blueprints, requests, artifacts; lifecycle & status | (platform-native) |
| 5 | **Execution Dashboard** | Real-time state of generation requests across the pipeline; queues, progress, outcomes | Compilation · Build · Assembly · Validation · Certification (status) |
| 6 | **Artifact Explorer** | Browse/inspect generated artifacts: manifests, SBOM, signatures, provenance chains, descriptors | Compilation · Build · Signing · SBOM · Descriptors |
| 7 | **Blueprint Management** | Author, import, version, classify, and validate blueprint documents prior to generation | Registry Resolution · Blueprint Classification |
| 8 | **Generation Requests** | Submit and track end-to-end generation (blueprint → certified runtime unit) | Factory Generation · Compilation · Build · Assembly |
| 9 | **Validation Explorer** | Inspect validation reports, findings, evidence, and acceptance decisions | Validation |
| 10 | **Certification Explorer** | Inspect certification decisions, immutable records, evidence, and the append-only ledger | Certification · Certification Ledger |
| 11 | **Runtime Operations** | Govern deployment and rollback of certified runtime units via EC-1 descriptors; monitor | Runtime Assembly · Deployment Descriptor · Rollback Descriptor |
| 12 | **Administration** | Manage users, roles, workspaces, quotas, policies, audit, and platform configuration | (platform-native) |

### 2.2 Platform capabilities (complete)
- **PC-01 Authentication & session management** — establish and maintain authenticated identity.
- **PC-02 Authorization & RBAC** — enforce least-privilege access to every capability and artifact.
- **PC-03 Workspace & project lifecycle** — create, scope, archive workspaces/projects.
- **PC-04 Blueprint authoring & validation** — author/import, structurally validate, version, classify blueprints.
- **PC-05 Blueprint catalog** — discover, search, and reuse registered blueprints.
- **PC-06 Generation request orchestration** — submit, queue, execute, resume, and cancel end-to-end generation.
- **PC-07 Pipeline execution & status** — drive the EC-1 pipeline stages and expose deterministic status.
- **PC-08 Artifact inspection** — view manifests, SBOM, signatures, provenance, descriptors, and hashes.
- **PC-09 Validation inspection** — view validation reports/evidence and acceptance decisions.
- **PC-10 Certification inspection & ledger** — view certification records/evidence; browse the append-only ledger; verify chain integrity.
- **PC-11 Runtime deploy/rollback operations** — apply EC-1 deployment/rollback descriptors under governance; monitor state.
- **PC-12 Monitoring & observability** — real-time metrics, logs, traces, and health across the platform and pipeline.
- **PC-13 Search & discovery** — cross-entity search over projects, blueprints, requests, artifacts, certifications.
- **PC-14 Notifications & events** — surface state transitions (request completed, certification issued, deploy applied).
- **PC-15 Administration & policy** — user/role/quota/policy management, audit export.
- **PC-16 Audit & traceability** — end-to-end, append-only audit of every governed action.
- **PC-17 API access** — programmatic access to all of the above for integrators/partners (by credential reference).
- **PC-18 Determinism & reproducibility preservation** — guarantee identical inputs yield identical outputs across the platform.

### 2.3 Platform boundaries (Program Scope & Boundaries)
**In scope (EC-2):** presentation, API, application/orchestration, identity, persistence of platform metadata (requests, projects, workspaces, users, audit), observability, and governed runtime operations — all as **consumers** of EC-1.

**Out of scope (EC-2):** any modification to EC-1 engine modules; any change to the frozen corpus; invention of new compilation/validation/certification semantics; constitutional authority of any kind; live production hosting decisions (delegated to the runtime/production architecture as immutable inputs); and any capability that would make an artifact non-deterministic or a certification non-reproducible.

---

## SECTION 3 — USER MODEL

### 3.1 User categories
Nine platform user categories are defined. Access is **least-privilege by default (PL-04)**; every action is authenticated (PC-01), authorized (PC-02), and audited (PC-16).

| ID | User | Primary responsibility |
|----|------|------------------------|
| U1 | **Platform Administrator** | Operate and govern the platform: users, roles, workspaces, quotas, policies, configuration, audit. |
| U2 | **Architect** | Author/curate blueprints and catalog; define generation standards; review validation/certification outcomes. |
| U3 | **Developer** | Author blueprints; submit generation requests; inspect artifacts, validation, and certification. |
| U4 | **Operator** | Execute governed runtime deploy/rollback operations; monitor runtime and pipeline health. |
| U5 | **Auditor** | Read-only access to all records, evidence, ledger, and audit trail; export reports. No mutation. |
| U6 | **Certification Authority** | Review certification decisions and ledger; confirm/attest platform certification (record-only; confers no constitutional authority). |
| U7 | **Business User** | Initiate generation requests from approved blueprints; track outcomes; consume certified deliverables. |
| U8 | **Partner** | Scoped, tenant-isolated access to designated workspaces/projects and APIs. |
| U9 | **Integrator** | Programmatic (API) access to submit/track requests and read artifacts, under credential reference (SEC-04). |

### 3.2 Permission model (RBAC matrix)
Permissions: **C** create · **R** read · **X** execute · **A** administer · **—** none. Rows = capability groups; columns = users.

| Capability group | U1 Admin | U2 Arch | U3 Dev | U4 Ops | U5 Aud | U6 CertAuth | U7 Biz | U8 Partner | U9 Integ |
|------------------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Portal / navigation | R | R | R | R | R | R | R | R | — |
| Identity & sessions (self) | A | R | R | R | R | R | R | R | R |
| User/role/quota admin | A | — | — | — | — | — | — | — | — |
| Workspace/project lifecycle | A | C/R | C/R | R | R | R | C/R | R (scoped) | R (scoped) |
| Blueprint authoring | R | C/R | C/R | — | R | R | — | C/R (scoped) | C/R (scoped) |
| Blueprint catalog | R | C/R | R | — | R | R | R | R (scoped) | R (scoped) |
| Generation requests | R | C/R/X | C/R/X | — | R | R | C/R/X | C/R/X (scoped) | C/R/X (scoped) |
| Execution dashboard | R | R | R | R | R | R | R | R (scoped) | R (scoped) |
| Artifact explorer | R | R | R | R | R | R | R (scoped) | R (scoped) | R (scoped) |
| Validation explorer | R | R | R | R | R | R | R | R (scoped) | R (scoped) |
| Certification explorer / ledger | R | R | R | R | R | R/attest | R | R (scoped) | R (scoped) |
| Runtime operations (deploy/rollback) | A | — | — | X | R | R | — | — | — |
| Monitoring & observability | A | R | R | R | R | R | R | R (scoped) | R (scoped) |
| Administration & policy | A | — | — | — | R | — | — | — | — |
| Audit & traceability | A | R | R | R | R | R | R | R (scoped) | R (scoped) |
| API access | A | X | X | X | R | R | X | X (scoped) | X (scoped) |

**Invariants:** (i) no role may write to the frozen corpus; (ii) no role may modify an issued certification record or a ledger entry (append-only); (iii) Auditor and Certification Authority hold **no** mutation rights over pipeline artifacts; (iv) Partner/Integrator access is always tenant/workspace-scoped and isolated.

---

## SECTION 4 — PLATFORM ARCHITECTURE

### 4.1 Layered architecture (eight layers)
```
┌─────────────────────────────────────────────────────────────────────┐
│ L1 PRESENTATION LAYER   Portal · Workspace · Dashboards · Explorers   │  (UI — EC-2 impl, later)
├─────────────────────────────────────────────────────────────────────┤
│ L2 API LAYER            Governed API gateway · authN/authZ edge · API │  (contract-first, versioned)
│                         versioning · rate/quota · request validation   │
├─────────────────────────────────────────────────────────────────────┤
│ L3 APPLICATION LAYER    Orchestration · request lifecycle · workspace │  (platform business logic)
│                         /project services · notifications · search     │
├─────────────────────────────────────────────────────────────────────┤
│ L4 EXECUTION LAYER      EC-1 ENGINE FAÇADE (read-only consumer)        │  (wraps EC-1; no modification)
│                         registry→classify→compile→build→sign→SBOM→     │
│                         assemble→descriptors→validate→certify→ledger    │
├─────────────────────────────────────────────────────────────────────┤
│ L5 REGISTRY LAYER       EC-1 Registry Adapter (read-only, DP-03)       │  (immutable corpus access)
├─────────────────────────────────────────────────────────────────────┤
│ L6 KNOWLEDGE LAYER      Blueprint/artifact metadata index · search ·   │  (platform metadata store)
│                         provenance graph views (read models)           │
├─────────────────────────────────────────────────────────────────────┤
│ L7 IDENTITY LAYER       Authentication · RBAC · sessions · credential  │  (by reference; SEC-04)
│                         references · tenant isolation                   │
├─────────────────────────────────────────────────────────────────────┤
│ L8 OPERATIONS LAYER     Observability · monitoring · audit · runtime   │  (deploy/rollback governance)
│                         operations governance · health · alerting       │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Layer responsibilities
- **L1 Presentation** — renders platform state; issues no engine calls directly (always via L2). Accessibility-compliant.
- **L2 API** — the single governed boundary; enforces authN/authZ, request contracts (AR-03/PL-05 versioned), quotas, and input validation; forwards to L3.
- **L3 Application** — owns platform business logic: request lifecycle state machine, workspace/project services, notifications, search orchestration; never bypasses L4 for engine work.
- **L4 Execution (EC-1 façade)** — the **only** component that invokes EC-1. It calls EC-1's published APIs (`engine.registry`, `engine.compiler`, `engine.determinism`, `engine.runtime`, `engine.factory`, `engine.validation`, `engine.certification`) as an embedded, versioned dependency. It is **read-only over EC-1** and preserves every EC-1 invariant.
- **L5 Registry** — EC-1 Registry Adapter (read-only over `00-BOOK`, DP-03). No platform component writes the corpus.
- **L6 Knowledge** — platform-owned read models and indexes over blueprints, requests, artifacts, provenance; source of truth remains EC-1 outputs + platform metadata.
- **L7 Identity** — authenticates users, resolves roles/permissions, isolates tenants; holds secrets by reference only (SEC-04).
- **L8 Operations** — telemetry (reusing EC-1 foundation observability discipline), monitoring, alerting, audit, and governed runtime operations via EC-1 descriptors (IP-08 reversibility).

### 4.3 EC-1 interaction map
| Platform action | L4 façade call (EC-1) | EC-1 output consumed |
|-----------------|-----------------------|----------------------|
| Validate a blueprint pre-submit | `registry` resolution + `compiler` classification/front-end | classification, gap report |
| Execute generation request | `factory` / `compiler.pipeline` + `determinism` | published package (manifest, SBOM, signature, record) |
| Assemble runtime unit | `runtime.assemble` | `RuntimeUnit` + descriptor + disclosure |
| Produce deploy/rollback | `runtime.deploy` | deployment & rollback descriptors |
| Validate artifact | `validation.ValidationEngine` | `ValidationReport` + `ValidationEvidence` + `AcceptanceDecision` |
| Certify artifact | `certification.CertificationEngine` | `CertificationDecision` + immutable `CertificationRecord` + `CertificationEvidence` |
| Record certification | `certification.CertificationLedger.append` | append-only, hash-chained `CertificationLedgerEntry` |
| Prove reproducibility | `determinism.double_build` | byte-identical reproducibility result |

**Rule:** EC-2 consumes EC-1 strictly through these contracts. Any EC-1 input that cannot be resolved triggers **STOP → GAP REPORT → REQUEST AUTHORITY** (no invention, TP-01).

---

## SECTION 5 — EPIC DETERMINATION

Fourteen EC-2 epics are determined. Each carries an ID, mission, dependencies, and objective acceptance criteria. Indicative task ranges continue the engine sequence from `TASK-000055`.

| Epic | Name | Mission | Depends on | Acceptance criteria (objective) | Task range (indicative) |
|------|------|---------|------------|---------------------------------|--------------------------|
| **EC2-EPIC-001** | Platform Foundation & API Gateway | Establish the governed API boundary, contracts, request validation, versioning, quotas, and the EC-1 execution façade skeleton. | EC-1 (complete) | Versioned API contract published; authN/authZ edge enforced on 100% of routes; EC-1 façade invokes engine with 0 EC-1 modifications; contract tests green. | 55–62 |
| **EC2-EPIC-002** | Identity & Access | Authentication, RBAC, sessions, tenant isolation, credential-by-reference. | EPIC-001 | 9 roles enforced per §3.2 matrix; least-privilege default; secrets by reference only (0 inline); unauthorized access blocked in 100% of negative tests. | 63–72 |
| **EC2-EPIC-003** | Portal & Navigation | Authenticated entry point, navigation, global search, notifications. | EPIC-001, EPIC-002 | Authenticated portal reachable; navigation to all authorized surfaces; global search returns results across ≥4 entity types; accessibility checks pass. | 73–80 |
| **EC2-EPIC-004** | Workspace & Collaboration | Scoped collaborative containers binding users/teams to work. | EPIC-002 | Workspace CRUD + scoping enforced; membership & isolation verified; cross-tenant access denied in 100% of tests. | 81–88 |
| **EC2-EPIC-005** | Project Management | Projects organizing blueprints, requests, artifacts; lifecycle & status. | EPIC-004 | Project lifecycle states defined & enforced; associations to blueprints/requests/artifacts intact; status derivable deterministically. | 89–96 |
| **EC2-EPIC-006** | Blueprint Catalog & Management | Author/import, version, classify, structurally validate, and discover blueprints. | EPIC-005, EC-1 registry/classification | Blueprint authoring + structural validation via EC-1 classification; versioning + catalog search; invalid blueprints rejected with gap report. | 97–108 |
| **EC2-EPIC-007** | Generation Requests | End-to-end generation orchestration (blueprint → certified runtime unit) as tracked, resumable requests. | EPIC-006, EC-1 factory/compiler/determinism | Request lifecycle state machine; end-to-end run produces published package; resumable/cancellable; identical request ⇒ identical hashes. | 109–124 |
| **EC2-EPIC-008** | Execution Dashboard | Real-time pipeline state across requests: queues, progress, outcomes. | EPIC-007, EPIC-013 | Live status for every stage; queue/progress accurate to state machine; 100% of terminal outcomes surfaced. | 125–134 |
| **EC2-EPIC-009** | Artifact Explorer | Inspect manifests, SBOM, signatures, provenance, descriptors, hashes. | EPIC-007 | All artifact facets viewable; hashes match EC-1 output byte-for-byte; provenance chain rendered and rooted. | 135–144 |
| **EC2-EPIC-010** | Validation Console | Inspect validation reports, findings, evidence, and acceptance decisions. | EPIC-007, EC-1 validation | Reports/evidence rendered faithfully; verdict & blocking failures displayed; matches EC-1 `ValidationReport` exactly. | 145–152 |
| **EC2-EPIC-011** | Certification Console & Ledger | Inspect certification decisions, immutable records, evidence, and the append-only ledger; verify chain. | EPIC-010, EC-1 certification | Records/evidence rendered; ledger browsable; chain-integrity verification exposed; 0 mutation paths to records/ledger. | 153–162 |
| **EC2-EPIC-012** | Runtime Operations | Govern deploy/rollback of certified units via EC-1 descriptors; monitor. | EPIC-011, EC-1 runtime | Deploy/rollback applied only from EC-1 descriptors; reversibility (IP-08) proven; only CERTIFIED units deployable. | 163–176 |
| **EC2-EPIC-013** | Observability & Monitoring | Real-time metrics, logs, traces, health, alerting across platform & pipeline. | EPIC-001 | Structured telemetry on 100% of governed actions; health endpoints live; alerts fire on defined conditions. | 177–186 |
| **EC2-EPIC-014** | Administration & Governance | Users, roles, quotas, policies, audit export, platform configuration. | EPIC-002, EPIC-013 | Admin controls enforce §3 model; append-only audit for 100% of governed actions; policy changes audited. | 187–196 |

**Epic invariants (all epics):** additive over EC-1; deterministic outputs preserved; no frozen-corpus writes; least-privilege access; append-only audit; provisional-state disclosure carried.

---

## SECTION 6 — PROGRAM ROADMAP

### 6.1 Execution sequence (five waves)
- **Wave 1 — Platform Core:** EC2-EPIC-001 (Foundation & API), EC2-EPIC-002 (Identity), EC2-EPIC-013 (Observability). *Foundational; unblock everything.*
- **Wave 2 — Work Surfaces:** EC2-EPIC-003 (Portal), EC2-EPIC-004 (Workspace), EC2-EPIC-005 (Projects).
- **Wave 3 — Blueprint & Generation:** EC2-EPIC-006 (Blueprint Catalog), EC2-EPIC-007 (Generation Requests).
- **Wave 4 — Insight Consoles:** EC2-EPIC-008 (Execution Dashboard), EC2-EPIC-009 (Artifact Explorer), EC2-EPIC-010 (Validation Console), EC2-EPIC-011 (Certification Console & Ledger).
- **Wave 5 — Operate & Govern:** EC2-EPIC-012 (Runtime Operations), EC2-EPIC-014 (Administration & Governance).

### 6.2 Dependency graph
```
EC-1 (complete)
  │
  ▼
EC2-EPIC-001 Foundation/API ──┬──▶ EC2-EPIC-002 Identity ──┬──▶ EC2-EPIC-003 Portal
                              │                            ├──▶ EC2-EPIC-004 Workspace ──▶ EC2-EPIC-005 Projects
                              └──▶ EC2-EPIC-013 Observability                                   │
                                                                                                ▼
                                                              EC2-EPIC-006 Blueprint Catalog ──▶ EC2-EPIC-007 Generation Requests
                                                                                                │
                        ┌───────────────────────────────────────────────┬───────────────┬─────┴───────────┐
                        ▼                                                 ▼               ▼                 ▼
              EC2-EPIC-008 Exec Dashboard                    EC2-EPIC-009 Artifacts  EC2-EPIC-010 Validation
              (also depends EPIC-013)                                                        │
                                                                                             ▼
                                                                                 EC2-EPIC-011 Certification & Ledger
                                                                                             │
                                                                                             ▼
                                                                                 EC2-EPIC-012 Runtime Operations
                                                                                             │
                                                                                             ▼
                                                                    EC2-EPIC-014 Administration & Governance
```

### 6.3 Milestones
| Milestone | Definition | Exit condition |
|-----------|------------|----------------|
| **M1 — Platform Core Ready** | Wave 1 complete | API gateway + identity + observability live; contract & negative-access tests green |
| **M2 — Work Surfaces Ready** | Wave 2 complete | Portal reachable; workspaces/projects operational and isolated |
| **M3 — Generation Operational** | Wave 3 complete | A blueprint submitted via the platform produces a published package deterministically |
| **M4 — Full Insight** | Wave 4 complete | Execution/artifact/validation/certification consoles reflect EC-1 output faithfully; ledger verifiable |
| **M5 — Operate & Govern** | Wave 5 complete | Governed deploy/rollback of a CERTIFIED unit; administration & audit complete |
| **M6 — Go-Live Certified** | UCOS-GO-LIVE-001 PASS | All 8 go-live conditions PASS; EC-2 Program Closure Certification issued |

### 6.4 Critical path
`EC-1 → EC2-EPIC-001 → EC2-EPIC-002 → EC2-EPIC-005 → EC2-EPIC-006 → EC2-EPIC-007 → EC2-EPIC-010 → EC2-EPIC-011 → EC2-EPIC-012 → EC2-EPIC-014 → UCOS-GO-LIVE-001`.
The generation-to-certification-to-runtime spine (007→010→011→012) is the longest dependent chain and governs program duration; EPIC-013 (observability) must precede EPIC-008 and is scheduled in Wave 1 to remove it from the critical path.

---

## SECTION 7 — GO-LIVE DEFINITION

### 7.1 UCOS-GO-LIVE-001
The single, authoritative gate that authorizes the UCOS Platform to be declared operational. **Fail-closed:** every condition must PASS; a single unmet condition blocks go-live.

| # | Condition | Objective acceptance criterion (measurable) |
|---|-----------|---------------------------------------------|
| G1 | **Platform Running** | All in-scope services report healthy on health endpoints; API gateway returns success for a versioned health contract; uptime observed over the acceptance window. |
| G2 | **Authentication Working** | A user authenticates successfully; an unauthenticated request is rejected on 100% of protected routes; sessions expire per policy. |
| G3 | **Blueprint Submission Working** | An authorized user submits a blueprint; a valid blueprint is accepted and a structurally invalid blueprint is rejected with an EC-1 gap report. |
| G4 | **Generation Working** | A submitted blueprint executes end to end and produces a published package (manifest + SBOM + signature + record); repeat run yields byte-identical hashes. |
| G5 | **Validation Working** | The generated runtime unit is validated; the platform surfaces the EC-1 `ValidationReport` + evidence + acceptance decision that match the engine exactly. |
| G6 | **Certification Working** | The validated unit is certified; an immutable `CertificationRecord` is issued, its integrity verifies, and an append-only ledger entry is created with a verifiable chain. |
| G7 | **Runtime Deployment Working** | A CERTIFIED unit is deployed via its EC-1 deployment descriptor and rolled back via its rollback descriptor; a non-certified unit is refused deployment. |
| G8 | **Monitoring Active** | Metrics, logs, and traces are emitted for the full G3→G7 flow; defined alerts fire under induced fault; audit records exist for every governed action. |

### 7.2 Go-live acceptance criteria (aggregate)
- **GLA-1:** G1–G8 all PASS (fail-closed).
- **GLA-2:** P1–P10 (§9) all PASS.
- **GLA-3:** EC-1 integrity re-verified (SC-4) and reproducibility re-verified (SC-5).
- **GLA-4:** Go-live certification (§10) issued and recorded in the certification ledger; provisional-state disclosure attached.

---

## SECTION 8 — TRACKING MODEL

### 8.1 TRACK-001 integration
EC-2 progress is tracked by **TRACK-001**, an integration that derives program status **automatically and deterministically** from objective evidence — never from manual assertion. It reuses the EC-1 discipline: evidence → status, append-only, fail-closed.

### 8.2 Tracked dimensions
| Dimension | Unit tracked | Status source (objective) |
|-----------|--------------|---------------------------|
| **Execution tracking** | Task (`TASK-0NNNNN`) | task acceptance tests + coverage gate green |
| **Epic tracking** | Epic (`EC2-EPIC-0NN`) | all epic tasks COMPLETE ∧ epic acceptance criteria (§5) met |
| **Milestone tracking** | Milestone (`M1…M6`) | all epics in the milestone's wave COMPLETE ∧ exit condition met |
| **Go-live tracking** | `UCOS-GO-LIVE-001` | G1–G8 ∧ GLA-1…GLA-4 all PASS |

### 8.3 Automatic status update model
```
Evidence (tests, coverage, acceptance gates, ledger entries, reproducibility results)
     │  produced by CI + platform acceptance runs
     ▼
Status Deriver (TRACK-001)   — pure function of evidence; no manual override
     │  Task PASS/FAIL → Epic → Milestone → Go-Live
     ▼
Status Registry (append-only)   — records each transition with evidence reference
     │
     ▼
Program Status View   — Execution / Epic / Milestone / Go-Live, always reproducible from evidence
```
**Rules:** (i) status is a **pure function of evidence** (deterministic, reproducible); (ii) transitions are **append-only** and reference their evidence; (iii) **fail-closed** — absence of evidence is NOT-DONE, never assumed-done; (iv) no manual status override is admissible.

---

## SECTION 9 — ACCEPTANCE FRAMEWORK

Ten platform acceptance criteria (**P1–P10**). Every criterion is **objectively measurable** and **fail-closed**. These are the platform analogue of EC-1's A1–A10.

| ID | Platform acceptance criterion | Objective measure (PASS condition) |
|----|-------------------------------|-------------------------------------|
| **P1** | **Platform Foundation & API** | 100% of API routes contract-conformant and behind the governed gateway; contract tests green. |
| **P2** | **Identity & Access Control** | 9 roles enforce the §3.2 matrix; 100% of unauthorized-access negative tests denied; secrets 100% by reference. |
| **P3** | **Workspace & Project Integrity** | Cross-tenant/workspace isolation holds in 100% of isolation tests; project associations referentially intact. |
| **P4** | **Blueprint Management** | Valid blueprints accepted; invalid blueprints rejected with EC-1 gap report; versioning + catalog search functional. |
| **P5** | **Generation Correctness & Determinism** | End-to-end generation produces a published package; identical request ⇒ byte-identical hashes (reproducibility gate green). |
| **P6** | **Validation Fidelity** | Platform-surfaced validation report/evidence/decision equal EC-1 output byte-for-byte. |
| **P7** | **Certification Integrity** | Issued certification records are immutable (integrity verifies); ledger chain verifies; 0 mutation paths. |
| **P8** | **Runtime Operations & Reversibility** | Only CERTIFIED units deployable; deploy + rollback proven reversible (IP-08); non-certified deploy refused. |
| **P9** | **Observability & Auditability** | Telemetry on 100% of governed actions; append-only audit complete; defined alerts fire under fault. |
| **P10** | **EC-1 Integrity Preservation** | 0 modifications to EC-1 modules; 0 frozen-corpus writes; EC-1 suite + coverage gate re-run green. |

---

## SECTION 10 — PROGRAM CERTIFICATION

EC-2 certification reuses the EC-1 certification discipline (evidence-backed, record-only, immutable, append-only, fail-closed, non-constitutive) and is recorded in the certification ledger. Four certification classes are defined.

### 10.1 EC-2 Completion Criteria
- **EC2-C1:** All fourteen epics (EC2-EPIC-001…014) at status COMPLETE (via TRACK-001).
- **EC2-C2:** All tasks in scope COMPLETE with acceptance tests + coverage gate green.
- **EC2-C3:** P1–P10 all PASS.
- **EC2-C4:** Milestones M1–M6 reached.
- **EC2-C5:** EC-1 integrity preserved (P10) and reproducibility preserved (P5).

### 10.2 Platform Certification Criteria
- **PLAT-C1:** Every platform capability (PC-01…PC-18) demonstrably operational and access-controlled.
- **PLAT-C2:** Every EC-1 capability exposed through the L4 façade with 0 EC-1 modification (P10).
- **PLAT-C3:** Determinism, immutability, registry-only access, frozen-corpus read-only, and fail-closed certification preserved end to end.
- **PLAT-C4:** RBAC (§3.2) enforced; audit (PC-16) complete and append-only.

### 10.3 Go-Live Certification Criteria
- **GL-C1:** UCOS-GO-LIVE-001 conditions G1–G8 all PASS.
- **GL-C2:** Go-live aggregate GLA-1…GLA-4 all PASS.
- **GL-C3:** A go-live certification record issued, integrity-verified, and appended to the ledger with provisional-state disclosure.

### 10.4 Operational Certification Criteria
- **OP-C1:** Health, monitoring, and alerting active and validated under induced fault (G8/P9).
- **OP-C2:** Governed runtime deploy/rollback validated for reversibility (P8).
- **OP-C3:** Sustained healthy operation observed across the defined acceptance window with 0 unaudited governed actions.
- **OP-C4:** Operational runbook conditions satisfied within the runtime/production architectural boundaries (consumed as immutable inputs).

### 10.5 EC-2 Program Closure Certification
EC-2 is **closed** when EC2-C1…C5 ∧ PLAT-C1…C4 ∧ GL-C1…C3 ∧ OP-C1…C4 all hold. Closure yields an **EC-2 Program Closure Certification** (record-only, ledger-recorded, verdict PASS) that records **engineering-execution readiness only**, carries the EC-1 provisional-state disclosure, and asserts **no constitutional finality** — the external gates (EC-1…EC-6) remain open.

---

## PROGRAM CLOSURE STATEMENT (of this determination)

This artifact establishes the complete EC-2 execution contract: charter, platform definition, user model, platform architecture, epic determination, roadmap, go-live definition, tracking model, acceptance framework, and certification criteria. It is a **determination and architecture artifact only** — it contains no implementation, code, services, infrastructure, or UI, and creates none. It becomes the **authoritative governing artifact for all EC-2 work**; all subsequent EC-2 implementation is subordinate to it and to every higher instrument named in the Authority Boundary.

**STOP — EC-2 Platform Realization Program determination COMPLETE. No implementation begun. No code, infrastructure, or UI created.**
