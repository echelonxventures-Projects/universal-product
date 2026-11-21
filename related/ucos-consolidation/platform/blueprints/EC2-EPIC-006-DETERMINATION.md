# EC2-EPIC-006 — Blueprint Catalog & Management — Determination

| Field | Value |
|-------|-------|
| ARTIFACT ID | EC2-EPIC-006-DETERMINATION |
| ARTIFACT | Blueprint Catalog & Management — Implementation Specification Determination |
| ARTIFACT TYPE | Determination artifact only (no implementation, no code, no service, no runtime, no API, no schema, no infrastructure, no registry, no catalog, no governance, no directory beyond this file's own) |
| PROGRAM | UCOS EC-2 Platform Realization Program |
| EPIC | EC2-EPIC-006 — Blueprint Catalog & Management |
| CLASSIFICATION | Platform determination — implementation specification derived from repository evidence |
| STATUS | ACTIVE — determination only |
| BRANCH | `governance-reconciliation` |
| REPOSITORY STATE | HEAD `2fdbc6b`; origin synchronized; working tree clean |
| BASELINE DATE | 2026-07-17 |
| VOLUME (per GOV-006) | VOL-006 (PLATFORM / `PLT`) — `^platform/` category mapping |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |
| INDICATIVE TASK RANGE | EC2-TASK-000097 … EC2-TASK-000108 (contract §5) |
| MISSION TYPE | DETERMINATION ONLY |

*This artifact **determines and defines only** the implementation specification and admission state for the Blueprint Catalog & Management runtime authorized as the next target by `platform/POST-EPIC-005-IMPLEMENTATION-STATUS-DETERMINATION.md` (verdict **READY — CONDITIONAL**). It creates no runtime code, no service, no API, no schema, no infrastructure, no database, no registry, no catalog, and no directory beyond this file's own. It invents no architecture, no roadmap, no governance, no capability group, no classification, and no lifecycle: every construct it names traces to an existing physical repository artifact — the EC-2 governing contract, the frozen generation-framework corpus (`05-GENERATION/`), the certified EC-1 Registry/Classification/Factory capabilities, the certified Foundation/Identity/Observability layers, and the completed Workspace, Project, Administration, and Security runtimes. It is subordinate to the frozen corpus (`00-BOOK/`, `00-SOURCE/`, `99-FREEZE/` — read-only, DP-03), the EC-2 Platform Realization Program, and every prior governance/execution determination; where any statement conflicts with a higher instrument, the higher instrument governs. It carries the EC-1 provisional-state disclosure verbatim, asserts no constitutional finality, and the external gates EC-1…EC-6 remain open.*

---

## 1. EXECUTIVE SUMMARY

`EC2-EPIC-006 — Blueprint Catalog & Management` is the seventh EC-2 platform runtime, the first node of **Wave 3 (Blueprint & Generation)**, and the first uncompleted node on the program critical path (`… → 002 → 005 → 006 → 007 → 010 → 011 → 012 → 014 → GO-LIVE`, contract §6.4). Its authoritative basis is the EC-2 contract `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`: §2.1 **Surface #7 Blueprint Management** ("Author, import, version, classify, and validate blueprint documents prior to generation" → EC-1 **Registry Resolution · Blueprint Classification**); §2.2 **PC-04** (Blueprint authoring & validation) and **PC-05** (Blueprint catalog); §3.2 RBAC rows **Blueprint authoring** and **Blueprint catalog**; §4 layers **L3 Application / L4 Execution façade / L5 Registry / L6 Knowledge**; §4.3 EC-1 interaction row "**Validate a blueprint pre-submit** → `registry` resolution + `compiler` classification/front-end → **classification, gap report**"; §5 EPIC-006 acceptance ("Blueprint authoring + structural validation via EC-1 classification; versioning + catalog search; invalid blueprints rejected with gap report"); §9 acceptance criterion **P4** (Blueprint Management); §7 go-live condition **G3**.

Three decisive findings, drawn directly from repository evidence, govern this determination:

> **Finding 1 — No new authority.** The §3.2 RBAC matrix binds Blueprint work to **two capability groups that already physically exist** in the certified Identity Layer: `CapabilityGroup.BLUEPRINT_AUTHORING` (`"blueprint-authoring"`, matrix index 4) and `CapabilityGroup.BLUEPRINT_CATALOG` (`"blueprint-catalog"`, matrix index 5) — both enumerated verbatim in `platform/identity/contracts.py` and seeded across all nine roles in `platform/identity/roles.py`. EPIC-006 authorizes **only** through the certified `AuthorizationService` on these pre-existing groups. It introduces no new capability group, no new role, and no new authorization logic.

> **Finding 2 — Classification is reused, never invented.** "Structural validation via EC-1 classification" is realized by the **already-published** L4 façade seam: `platform/foundation/capabilities.py` models `ENG-CAP-01 Registry Resolution → engine.registry.read` and `ENG-CAP-02 Blueprint Classification → engine.compiler.compile`, and `platform/foundation/contracts.py` publishes the corresponding `ContractRef`s (`engine.registry.read` v1.0.0, `engine.compiler.compile` v1.0.0) as `ENGINE_CONTRACTS`. EPIC-006 consumes EC-1 **read-only** through these references (P10); it invents no classification semantics and modifies no `engine/**` module.

> **Finding 3 — EPIC-006 is the trace-closure epic.** The single open governance condition — the **Generation→Implementation traceability break** (GOV-002 §6 **link-4**; GOV-004 **BLK-AUTH-GOV-01/BLK-AUTH-TRC-01**; EXEC-001 **RSK-01**; MEDIUM) — is scoped **into** EPIC-006, not upstream of it. The break is precisely located: a `git grep` over `05-GENERATION` for `engine/`, `compiler`, `04-REFERENCE`, `REFERENCE-ARCH` returned **no matches** — no generation-framework artifact cites a downstream implementation. EPIC-006 closes this by making each catalog record carry **provenance-by-reference** from its `05-GENERATION` blueprint origin (BP-DATA/BP-EVENT/BP-API/…) down to its EC-1 classification and its EPIC-005 project association, and by citing the generation framework as authoritative basis in the completion report — rendering the previously-absent `05-GENERATION → 06-IMPLEMENTATION` trace **present**.

A fourth finding governs scope, mirroring the EPIC-005 "by reference" precedent: EPIC-006 **catalogs and classifies blueprint documents by reference** — it does **not** author generation-framework content, mint new BP-* identities, execute generation (EPIC-007), or resolve/validate downstream artifacts. A blueprint in the catalog is an authored/imported document that is structurally validated + classified against the certified EC-1 engine, versioned immutably, and made discoverable; the catalog is a **platform-owned L6 read model/index**, not a second source of generation truth.

The runtime is a strictly **additive L3/L6 composition point** that authorizes **only** through the certified Identity Layer on the two existing blueprint groups; classifies/validates **only** through the read-only L4 EC-1 façade; is scoped **within** a workspace/project and isolated by the reused `platform.workspace.isolation.tenants_isolated` rule; associates to projects **only** through the EPIC-005 `AssociationKind.BLUEPRINT` surface; observes **only** through the certified L8 Observability Runtime; and persists/discovers **only** through the Foundation registries/events with content-addressed IDs. It creates no new authority, no second audit-of-record, no second isolation rule, no new identity scheme, and no new classification model.

**All readiness conditions material to admission are met; all required upstream dependencies are COMPLETE/CERTIFIED; the one standing condition (link-4 trace closure) is in-scope and dischargeable within the epic; no architectural invention is required.**

**Verdict: `IMPLEMENTATION AUTHORIZED`** — see §15/§16.

---

## 2. CONSTITUTIONAL AUTHORITY ANALYSIS

"Constitutional" here means the governing execution contract and the standing governance/execution determinations that authorize the EC-2 lane; the Blueprint runtime asserts no constitutional authority of its own. All inputs are physically present and `ACTIVE`/COMPLETE/CERTIFIED.

### 2.1 Governing authority chain

| # | Source | Path | Governing role |
|---|--------|------|----------------|
| A-1 | EC-2 Platform Realization Program | `06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md` | **Primary authority.** §2.1 Surface #7 Blueprint Management; §2.2 PC-04 + PC-05; §3.2 RBAC rows `blueprint-authoring` + `blueprint-catalog`; §4.1 L3/L4/L5/L6/L7/L8; §4.3 EC-1 interaction "Validate a blueprint pre-submit"; §5 EC2-EPIC-006 definition + acceptance + dependencies + task range 97–108; §6.1 Wave 3; §6.2/§6.4 dependency graph + critical path; §7 G3; §9 P4/P5/P10; §10 PLAT-C1…C4; §Authority-Boundary (additive-only, per-epic admission). |
| A-2 | POST-EPIC-005 Implementation Status Determination | `platform/POST-EPIC-005-IMPLEMENTATION-STATUS-DETERMINATION.md` | The authorization naming EC2-EPIC-006 the next authorized target (verdict READY — CONDITIONAL; §8/§9/§12/§13). |
| A-3 | GOV-004 — Implementation Execution Authorization | `02-MASTER/UCOS-GOV-004-IMPLEMENTATION-EXECUTION-AUTHORIZATION-DETERMINATION.md` | IMPLEMENTATION CONDITIONALLY AUTHORIZED; single authorized lane = EC-2; §10 records BLK-AUTH-GOV-01 / BLK-AUTH-TRC-01 (link-4, MEDIUM). |
| A-4 | UCOS-EXEC-001 — EC-2 Execution Activation | `02-MASTER/UCOS-EXEC-001-EC2-EXECUTION-ACTIVATION-DETERMINATION.md` | EC-2 EXECUTION CONDITIONALLY ACTIVATED subject to per-epic admission (EN-5) + standing conditions; §RSK-01 traceability break bounds EPIC-006/007. |
| A-5 | UCOS-EXEC-002 — Next-Epic Sequencing | `02-MASTER/UCOS-EXEC-002-...md` | Records generation-spine sequencing (EPIC-006 prerequisite to 007). |
| A-6 | GOV-002 — Constitution→Implementation Traceability | `02-MASTER/UCOS-GOV-002-CONSTITUTION-TO-IMPLEMENTATION-TRACEABILITY-DETERMINATION.md` | §6 traceability matrix; **link-4 (Generation Framework → Implementation Program) = BREAK**; the authoritative location of the trace obligation EPIC-006 discharges. |
| A-7 | GOV-006 — Repository Governance Correction | `02-MASTER/UCOS-GOV-006-...md` | Category→volume mapping: `^platform/` ⇒ PLATFORM / `PLT` / VOL-006 (governs registration). |
| A-8 | REG-AUTO-001 — Automatic Artifact Registration Standard | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-...md` | Registration discipline applied after each implementation commit (every prior EC-2 unit followed by a `REG-AUTO-001: register …` commit; HEAD `2fdbc6b` is itself such a commit). |
| A-9 | STATUS-001 / TRACK-001 | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-STATUS-001-...md`; contract §8 | Evidence→status discipline; append-only; fail-closed (absence of evidence = NOT-DONE). |
| A-10 | Universal Generation Framework corpus | `05-GENERATION/UCOS-Ω∞-UNIVERSAL-GENERATION-FRAMEWORK-CONSTITUTION.md` + six family frameworks | The authoritative definition of what a blueprint **is** and where blueprints **originate** (§3 below). Frozen corpus — read-only (DP-03). |

### 2.2 Governing contracts

- **EC-1 façade contracts (read-only consumers):** `engine.registry.read` v1.0.0, `engine.compiler.compile` v1.0.0 (published as `ENGINE_CONTRACTS` in `platform/foundation/contracts.py`; bound to `ENG-CAP-01`/`ENG-CAP-02` in `platform/foundation/capabilities.py`). These are the sole seams for "structural validation via EC-1 classification".
- **Platform contract surface:** `platform.foundation.platform_contract` / `ContractRef` / `ServiceRegistry` (AR-03/PL-05 versioned contracts consumers bind to by reference).
- **Identity contract:** `platform.identity.AuthorizationService` + `AccessDecision` over `CapabilityGroup.BLUEPRINT_AUTHORING` / `BLUEPRINT_CATALOG`.
- **Project association contract:** `platform.projects.AssociationKind.BLUEPRINT` (published by EPIC-005 for downstream binding).

### 2.3 Governing architecture

Contract §4.1 layers: **L3 Application** (blueprint service, orchestration, search), **L4 Execution** (the only EC-1-invoking component — read-only façade for classification), **L5 Registry** (EC-1 Registry Adapter, read-only over `00-BOOK`, DP-03), **L6 Knowledge** ("Blueprint/artifact metadata index · search · provenance graph views (read models)" — the catalog's home layer), **L7 Identity** (authorization/isolation), **L8 Operations** (telemetry/audit/health). The Blueprint runtime is the first EC-2 runtime to exercise the **L4/L5/L6** triad materially.

### 2.4 Governing classifications

The blueprint **classification model is EC-1's**, not the platform's: EC-1 `Blueprint Classification` (`ENG-CAP-02` → `engine.compiler.compile`). Blueprints belong to the six frozen **generation families** in the non-reversible chain **Data → Event → API → Workflow → Service → Application** (`05-GENERATION` corpus, A-10). EPIC-006 records and reuses these classifications; it defines none.

### 2.5 Governing registries

- Foundation `ServiceRegistry` / `ServiceDescriptor` (contract publication, discovery).
- EC-1 Registry Adapter (L5, read-only) for corpus resolution.
- The **platform-owned blueprint catalog registry** to be realized (L6, additive, content-addressed) — append-only, mirroring the certified `platform/projects/registry.py` and `platform/workspace/` registry discipline.
- The EPIC-005 project **association registry** (`AssociationKind.BLUEPRINT`) — reused, not re-realized.

### 2.6 Governing traceability obligations

- **GOV-001 Part 8** — traceability mandatory: every construct cites its authoritative basis.
- **GOV-002 §6 link-4** — the specific open obligation: establish the `05-GENERATION → 06-IMPLEMENTATION` trace (see §5).
- **Contract §8 / TRACK-001** — evidence→status, append-only, fail-closed.

### 2.7 Authority boundary

The Blueprint runtime holds **ENGINEERING-EXECUTION-ONLY** authority. It creates no constitutional/governance/ratification/EC-series authority; it neither closes nor asserts any external gate (EC-1…EC-6 remain open); it is subordinate to every instrument in §2.1 and to the frozen corpus.

**Every authoritative source is identified above (A-1 … A-10). No authority is invented.**

---

## 3. BLUEPRINT DEFINITION DETERMINATION

Repository-derived definitions only (source: `05-GENERATION/` corpus, A-10; contract §2.1 #7 / PC-04 / PC-05).

### 3.1 What a blueprint is

Per the Universal Generation Framework Constitution (GEN-000), a blueprint is an **executable implementation blueprint** — a deterministic, reproducible, certifiable artifact transformed from an **approved reference architecture** (REF-DATA-001 … REF-APPLICATION-001), never invented and never derived from a catalog asset or an unregistered source. In EC-2 platform terms (contract §2.1 #7, PC-04), a blueprint is a **blueprint document that is authored or imported, structurally validated and classified against the certified EC-1 engine, and versioned prior to generation**. It is the input the generation spine (EPIC-007) consumes to produce a published package.

### 3.2 Blueprint lifecycle (contract §5 acceptance + §2.1 #7 + PC-04/PC-05)

```
authored / imported  →  structurally validated + classified (EC-1: registry.read + compiler.compile)
        │                           │
        │                   valid ──┴──▶ versioned (immutable, content-addressed)  →  cataloged / registered (L6)
        │                                                                                    │
        └── invalid ──▶ REJECTED with EC-1 gap report (no catalog entry; §4.3, P4)            ▼
                                                                                    discoverable / searchable (PC-05, PC-13)
                                                                                                │
                                                                                                ▼
                                                                        consumed by EPIC-007 generation (by reference)
```

Terminal/immutable states are content-addressed; superseded versions remain in lineage (append-only). Invalid blueprints never enter the catalog — they are refused with the EC-1 classification gap report (fail-closed, TP-01 "STOP → GAP REPORT → REQUEST AUTHORITY").

### 3.3 Blueprint ownership model

- **Authoring** governed by `blueprint-authoring` (§3.2): Architect (U2, C/R), Developer (U3, C/R), Partner/Integrator (C/R scoped); Admin/Auditor/CertAuth = R; Business User/Operator = —.
- **Catalog** governed by `blueprint-catalog` (§3.2): Architect (C/R), Developer/Business/Admin/Auditor/CertAuth = R, Partner/Integrator = R scoped.
- Blueprints are **scoped within a workspace and associated to a project** by reference (`AssociationKind.BLUEPRINT`, EPIC-005); the authoring principal is recorded as owner (workspace/project isolation applies).

### 3.4 Blueprint classification model

EC-1 `Blueprint Classification` (`ENG-CAP-02`) via the L4 façade. The classification result and gap report are EC-1 outputs consumed read-only (§4.3). Blueprints carry one of the six frozen generation-family classifications (DATA/EVENT/API/WORKFLOW/SERVICE/APPLICATION). The platform records the classification; it computes none.

### 3.5 Blueprint validation model

**Structural validation via EC-1 classification/front-end** (contract §4.3, §5, P4): `registry` resolution + `compiler` classification produce `{classification, gap report}`. A blueprint is *valid* iff EC-1 resolves it and returns a non-defective classification; otherwise it is *rejected with a gap report*. The platform adds no second validation semantics (P10; out-of-scope §2.3 of contract).

### 3.6 Blueprint versioning model

Content-addressed immutable versions (`content_hash`, P5/P18), append-only, with lineage (parent-version reference) and supersession (a later version supersedes an earlier one without mutating it). Determined in detail in §8.

**All definitions above are repository-derived (GEN-000 constitution + contract §2.1 #7 / PC-04 / PC-05 / §4.3 / §5). None invented.**

---

## 4. GENERATION-LANE RECONCILIATION

Source: `05-GENERATION/` (frozen corpus, read-only, DP-03).

### 4.1 Blueprint origins inside 05-GENERATION

| Framework | Family | Blueprint identity range | Count | Source of realization |
|-----------|--------|--------------------------|-------|-----------------------|
| GEN-000 (Constitution) | — | — | — | Establishes the Universal Generation Framework Program; authorizes six frameworks. |
| GEN-DATA-001 | DATA (base) | `BP-DATA-0001 … BP-DATA-0051` | 51 | REF-DATA-001 (51/51 entities); CAT-DATA-001 (DE-0001…DE-0051) |
| GEN-EVENT-001 | EVENT | `BP-EVENT-000001 … BP-EVENT-000612` | 612 | REF-EVENT-001 (612/612 events); CAT-EVENT-001 |
| GEN-API-001 | API | API + contract blueprints | 765 + 765 | REF-API-001 (765/765 APIs + 765/765 contracts); CAT-API-001 |
| GEN-WORKFLOW-001 | WORKFLOW | workflow blueprints | — | REF-WORKFLOW-001 |
| GEN-SERVICE-001 | SERVICE | service blueprints | — | REF-SERVICE-001 |
| GEN-APPLICATION-001 | APPLICATION (terminal) | `APP-000001 … APP-000459` blueprints | 459 | REF-APPLICATION-001 |

The families are bound by the **non-reversible sequence Data → Event → API → Workflow → Service → Application** (A-10).

### 4.2 BP-DATA artifacts

`BP-DATA-0001…BP-DATA-0051` (51 data blueprints) — schemas, storage, migrations, validation, security, runtime, deployment packages generated from REF-DATA-001 realizations. Base of the chain.

### 4.3 BP-EVENT artifacts

`BP-EVENT-000001…BP-EVENT-000612` (612 event blueprints) — schemas, production/outbox, transport/routing, processing, reliability, security packages generated from REF-EVENT-001 realizations of the 612 canonical events (CAT-EVENT-001).

### 4.4 Generation-framework outputs (contract of the lane)

Generation MAY produce: **Blueprints · Specifications · Schemas · Contracts · Configurations · Infrastructure Definitions · Deployment Definitions · Validation Packages · Certification Packages · Runtime Packages** (GEN-000 §2). Generation SHALL NOT directly produce production systems; SHALL originate only from **registered reference architectures**.

### 4.5 Classification requirements

Each blueprint family is a classification the EC-2 catalog records via EC-1 `Blueprint Classification`. A cataloged blueprint SHALL carry: its generation family, its EC-1 classification result, and its provenance to the originating framework (BP-* identity). These are the fields that make link-4 closure machine-checkable (§5).

### 4.6 Implementation consumption model

EPIC-006 **catalogs blueprints by reference** (opaque `ref_id` + provenance metadata), classifies/validates them via EC-1 read-only, versions them, and publishes them for discovery. It does **not** import or mutate `05-GENERATION` content (DP-03) and does **not** execute generation (EPIC-007). Downstream consumption: EPIC-007 references catalog blueprints to submit generation requests.

**Required blueprint sources identified: the six `05-GENERATION` family frameworks (BP-DATA / BP-EVENT / BP-API / BP-WORKFLOW / BP-SERVICE / BP-APPLICATION), rooted in registered reference architectures.**

---

## 5. TRACEABILITY RECONCILIATION

### 5.1 Exact location of the link-4 break

**GOV-002 §6, row 4 — "Generation Framework → Implementation Program" = BREAK.** Repository evidence quoted verbatim from A-6: *"`git grep` over `05-GENERATION` for `engine/`, `compiler`, `04-REFERENCE`, `REFERENCE-ARCH` returned no matches. No generation-framework artifact cites a downstream implementation or engine. Missing link: generation→implementation trace."* Carried forward as GOV-004 **BLK-AUTH-GOV-01 / BLK-AUTH-TRC-01** (MEDIUM) and EXEC-001 **RSK-01** (MEDIUM, "bounds EPIC-006/007 traceability"). No repository artifact records the break RESOLVED as of HEAD `2fdbc6b`.

Note (evidence discipline): GOV-002 §6 also labels the break "GOV-003 BLK-GOV-01"/"BLK-AUTH-GOV-01" in GOV-004; these are the same link-4 break under the governance and traceability control classes respectively. This determination treats them as one obligation.

### 5.2 Required trace-closure mechanism

Link-4 closes when a repository artifact establishes an explicit, evidence-backed citation from a `05-GENERATION` blueprint origin **down to** its EC-2 implementation consumption. The certified pattern already exists on the *implementation→definition* side (GOV-002 §6 records `platform/identity/EC2-EPIC-002-COMPLETION-REPORT.md` citing the EC-2 contract as authoritative basis, satisfying GOV-001 Part 8). EPIC-006 supplies the missing *generation→implementation* direction.

### 5.3 Blueprint responsibilities in trace closure

Each catalog record SHALL carry **provenance-by-reference** to its `05-GENERATION` origin: the generation family, the framework identity (GEN-DATA-001 … GEN-APPLICATION-001), and the BP-* blueprint identity — plus the EC-1 classification result and the downstream `AssociationKind.BLUEPRINT` project binding. This makes each cataloged blueprint a materialized `05-GENERATION → 06-IMPLEMENTATION` trace edge.

### 5.4 Implementation responsibilities in trace closure

The EPIC-006 completion report and module docstrings SHALL cite (a) the EC-2 contract (§2.1 #7, PC-04/PC-05, §5) and (b) the originating `05-GENERATION` framework(s), discharging GOV-001 Part 8 in the generation→implementation direction. The catalog provenance metadata (§5.3) provides the machine-checkable evidence a subsequent traceability determination can verify to reclassify link-4 from BREAK to PRESENT.

### 5.5 How EPIC-006 closes Generation → Implementation traceability

By implementing the catalog as a **provenance-carrying L6 read model** (§5.3) and citing the generation lane in its completion evidence (§5.4), EPIC-006 makes the previously-absent `05-GENERATION`→implementation citation physically present in the repository. This is an in-scope EPIC-006 deliverable (per A-2 §8/§10 and the mission authority), **not** an upstream prerequisite; it bounds the epic and is dischargeable within it. Formal reclassification of link-4 remains an act of a future traceability determination reading EPIC-006's evidence — EPIC-006 furnishes that evidence.

---

## 6. PROJECT INTEGRATION ANALYSIS (EPIC-005)

### 6.1 Relationship to EPIC-005 Projects

EPIC-005 (COMPLETE) published the **association-by-reference** surface `platform.projects.AssociationKind.BLUEPRINT`, explicitly documented in `platform/projects/contracts.py` as *"EPIC-006 (Blueprint Catalog) binds via `BLUEPRINT`"*. A blueprint is associated to a project through an opaque `ref_id` on that surface.

### 6.2 Ownership boundaries

| Concern | Owner | Not owned by |
|---------|-------|--------------|
| Project record, lifecycle, association record (`{project_id, kind=blueprint, ref_id}`) | **EPIC-005** `platform/projects/` | EPIC-006 |
| Blueprint document, classification, version, lineage, catalog index, provenance | **EPIC-006** `platform/blueprints/` (to be realized) | EPIC-005 |

### 6.3 Reference model

Direction is **project → blueprint by reference** (a project associates a blueprint `ref_id`). EPIC-006 owns the blueprint identity that `ref_id` denotes. EPIC-006 does **not** write to the project association registry; it exposes the catalog record that a project's association resolves to (by reference).

### 6.4 Association model

The EPIC-005 registry treats each `ref_id` as opaque and resolves/validates no referenced entity (`platform/projects/contracts.py`, §5.3 of EPIC-005 determination). EPIC-006 supplies the resolvable blueprint identity; the two runtimes meet **only** at the opaque `ref_id` seam.

### 6.5 Inheritance model

No class/type inheritance across the boundary. Blueprints inherit workspace/tenant scoping transitively (a blueprint's project is scoped to a workspace; the workspace isolation rule governs). No re-declaration of scope.

### 6.6 Duplication check

**No duplication.** EPIC-005 owns the association record; EPIC-006 owns the blueprint record; they share only the `AssociationKind.BLUEPRINT` `ref_id`. The catalog does not re-implement project association, lifecycle, or isolation.

---

## 7. REQUEST INTEGRATION ANALYSIS (EPIC-007)

### 7.1 Relationship to EPIC-007

EPIC-007 (Generation Requests) orchestrates **blueprint → certified runtime unit** (contract §2.1 #8, §5 row 228). Requests consume catalog blueprints.

### 7.2 Upstream/downstream interactions

EPIC-006 is **upstream**; EPIC-007 is **downstream**. Contract §5 row 228 declares EPIC-007 `Depends on: EPIC-006, EC-1 factory/compiler/determinism`. Contract §6.2/§6.4 place `006 → 007` on the critical path.

### 7.3 Dependency direction

`006 → 007` (one-directional). EPIC-006 has **no** dependency on EPIC-007 (contract §5 row 227: EPIC-006 depends on `EPIC-005, EC-1 registry/classification`). Realizing EPIC-006 requires nothing from EPIC-007.

### 7.4 Association-by-reference model

Requests will reference catalog blueprints by opaque identity (mirroring `AssociationKind.REQUEST` on projects). EPIC-006 publishes the blueprint identity/contract that EPIC-007 binds to by reference.

### 7.5 Determination

**YES — EPIC-007 depends on EPIC-006** (directly, per contract §5/§6.2). EPIC-006 does not depend on EPIC-007. This confirms EPIC-006 as the correct next node and the sole unblocker of the generation spine (A-2 §4.2).

---

## 8. CATALOG ARCHITECTURE DETERMINATION

Reusing existing platform patterns (contract §4.1 L6; certified `platform/projects/` + `platform/workspace/` topologies).

| Concern | Determination | Reused pattern |
|---------|---------------|----------------|
| **Catalog structure** | Platform-owned **L6 Knowledge-Layer read model/index** over registered blueprints; append-only, content-addressed; never a source of generation truth | Contract §4.1 L6; `platform/projects/registry.py` |
| **Blueprint registry structure** | Append-only, content-addressed store of immutable `Blueprint` records keyed by `{workspace_id/project scope, blueprint slug, version}`; create/register/resolve/discover; fail-closed on duplicates | `platform/projects/registry.py`; `platform/workspace/` registry |
| **Metadata model** | Immutable blueprint metadata value type: family, EC-1 classification, provenance (framework + BP-* identity), version, lineage, owner, workspace/project scope | `platform/projects/metadata.py` (`ProjectMetadata` precedent) |
| **Discovery model** | Authorization- (`blueprint-catalog` READ) and isolation-scoped discovery; never surfaces a cross-tenant/cross-workspace blueprint | `platform/projects/search.py`; `platform.workspace.isolation.tenants_isolated` |
| **Indexing model** | Deterministic content-addressed index over the metadata model; reproducible fingerprint (P5/P18) | Foundation `content_hash` |
| **Search model** | READ-gated cross-entity search aligned to **PC-13** (projects, blueprints, requests, artifacts, certifications); results filtered by scope; fail-closed | `platform/projects/search.py` |

The catalog raises no new query engine and no new persistence — it is a deterministic in-memory/metadata read model over Foundation registries (Workspace/Project/Administration precedent; no server, no socket, no filesystem writes).

---

## 9. VERSIONING DETERMINATION

Authoritative approach: **content-addressed immutability + append-only lineage** (contract P5/P18; Foundation `content_hash`; ledger-style precedent in `platform/security/classification.py::ClassificationLedger` and `platform/projects/` append-only events).

| Model | Determination |
|-------|---------------|
| **Version model** | Each blueprint version is an immutable, content-addressed record; a version identity is a pure function of its content + metadata (identical content ⇒ identical version id). |
| **Revision model** | A new revision is a new immutable version bound to the same blueprint lineage root; prior revisions are never mutated. |
| **Immutability model** | No in-place edit; all changes append a new version (DP-03/P5). A cataloged version's classification/gap-report result is frozen with it. |
| **Lineage model** | Each version references its parent version (append-only chain from the lineage root), yielding a verifiable, reproducible history. |
| **Supersession model** | A later version MAY supersede an earlier one (marking it superseded by reference) without deleting or mutating it; superseded versions remain discoverable for audit/provenance. |

Immutability + lineage are the same discipline the certified Certification Ledger (EC-1) and `ClassificationLedger` (EC2-CAP-SEC-001) already apply; EPIC-006 reuses it, inventing no new versioning semantics.

---

## 10. VALIDATION DETERMINATION

Required validation categories (contract §5, §4.3, P4, GOV-001 Part 8, P5/P18):

| Category | Determination | Authority |
|----------|---------------|-----------|
| **Structural validation** | Blueprint resolved + classified via EC-1 (`engine.registry.read` + `engine.compiler.compile`); invalid ⇒ **rejected with EC-1 gap report**; fail-closed | §5, §4.3, P4 |
| **Classification validation** | Result maps to exactly one of the six frozen generation families; unclassifiable ⇒ rejected | §2.4; A-10 |
| **Contract validation** | Published blueprint contract conforms to the AR-03/PL-05 versioned `ContractRef` surface | §4.1 L2; PL-05 |
| **Traceability validation** | Each catalog record carries required provenance (framework + BP-* identity) and authoritative-basis citation; missing provenance ⇒ not admissible (discharges link-4, §5) | GOV-001 Part 8; GOV-002 §6 |
| **Determinism validation** | Blueprint version id + catalog fingerprint reproducible byte-identically across independent processes | P5/P18 |

The platform performs **no** validation beyond surfacing EC-1's structural/classification result and enforcing platform-side contract/traceability/determinism integrity (P10 — no invented validation semantics).

---

## 11. DEPENDENCY CLOSURE ANALYSIS

### 11.1 Upstream dependencies

| Dependency | Type | Component consumed | Status | Evidence |
|------------|------|--------------------|--------|----------|
| EC2-EPIC-005 Project Management | **Required** | `AssociationKind.BLUEPRINT`, project association surface | COMPLETE | `platform/projects/EC2-EPIC-005-COMPLETION-REPORT.md`; registered `95d6796` |
| EC2-EPIC-002 Identity | **Required** | `AuthorizationService`, `CapabilityGroup.BLUEPRINT_AUTHORING` + `BLUEPRINT_CATALOG`, `AccessDecision` | COMPLETE / CERTIFIED | `platform/identity/contracts.py`, `roles.py` |
| EC2-EPIC-001 Foundation | **Required** | `content_hash`, `EventBus`, `ServiceRegistry`, `ContractRef`, `ENGINE_CONTRACTS`, `ENG-CAP-01/02`, `PlatformError` | COMPLETE | `platform/foundation/contracts.py`, `capabilities.py` |
| EC2-EPIC-013 Observability | **Required** | `ObservabilityService`, `AuditTrail`, `HealthRegistry`, `HealthCheck`, `HealthStatus` | COMPLETE | `platform/observability/` |
| EC2-EPIC-004 Workspace | **Required** | `isolation.tenants_isolated`, workspace registry/context | COMPLETE | `platform/workspace/` |
| EC-1 Registry Resolution | **Required (read-only)** | `engine.registry.read` (L5 adapter / L4 façade) | CERTIFIED | `ENG-CAP-01`; contract §4.3 |
| EC-1 Blueprint Classification | **Required (read-only)** | `engine.compiler.compile` (L4 façade) | CERTIFIED | `ENG-CAP-02`; contract §4.3 |
| EC-1 Factory Layer (engine EPIC-006) | **Available (consumed downstream by 007)** | `engine/factory/` | COMPLETE | `engine/factory/EPIC-006-COMPLETION-REPORT.md` (distinct EC-1 artifact, per A-2 §4.2) |
| EC2-CAP-SEC-001 / EC2-CAP-ADMIN-001 | **Reused (optional)** | classification-by-reference / policy surface | COMPLETE | `platform/security/`, `platform/administration/` |

### 11.2 Downstream dependencies

| Downstream | Effect of EPIC-006 | Relationship |
|------------|--------------------|--------------|
| EC2-EPIC-007 Generation Requests | **Unblocked (direct)** | requests reference catalog blueprints (§7) |
| EC2-EPIC-008/009/010 | Enabled (transitive, via 007) | downstream of the generation spine |
| EC2-EPIC-011/012 | Enabled (transitive) | downstream of 010/011 |

### 11.3 Unresolved dependencies

**One standing, in-scope condition:** the link-4 Generation→Implementation traceability break (RSK-01 / BLK-AUTH-TRC-01, MEDIUM). It is **not** an upstream prerequisite — it is an EPIC-006 deliverable (§5). No upstream code/contract dependency is unresolved.

### 11.4 Dependency closure status

**CLOSED** for all required upstream dependencies (all COMPLETE/CERTIFIED); dependency direction is inward/downward (AR-01), acyclic. The sole open item (link-4) is discharged **within** EPIC-006, not before it. **Closure: CLOSED with one in-scope trace obligation.**

---

## 12. REUSE ANALYSIS

Mandatory reuse of certified seams (no re-realization; P10 / "no duplication"):

| # | Certified seam | Reused from | Reuse in EPIC-006 |
|---|----------------|-------------|-------------------|
| 1 | **AuthorizationService** | `platform.identity` | Sole authorization decision point for every blueprint action |
| 2 | **CapabilityGroup definitions** | `platform.identity.contracts` | `BLUEPRINT_AUTHORING` (PC-04) + `BLUEPRINT_CATALOG` (PC-05) — both already exist; no new group |
| 3 | **Workspace isolation** | `platform.workspace.isolation.tenants_isolated` | Scope + cross-tenant/workspace denial for authoring & discovery |
| 4 | **Project runtime** | `platform.projects` (`AssociationKind.BLUEPRINT`) | Blueprint↔project binding by reference (§6) |
| 5 | **Observability** | `platform.observability.ObservabilityService` | Governed-action telemetry (100% of blueprint actions, P9) |
| 6 | **AuditTrail** | `platform.observability.AuditTrail` | Single append-only audit-of-record (PC-16/OP-C3) |
| 7 | **HealthRegistry** | `platform.observability.HealthRegistry` / `HealthCheck` / `HealthStatus` | Blueprint health (e.g., provenance-integrity probe) → `UNHEALTHY` on fault (OP-C1) |
| 8 | **EventBus** | `platform.foundation` | Governed blueprint events (`blueprint.authored`, `blueprint.classified`, `blueprint.versioned`, `blueprint.catalogued`, `blueprint.access.evaluated`) |
| 9 | **ServiceRegistry** | `platform.foundation` | Contract publication + discovery |
| 10 | **content_hash** | `platform.foundation.contracts` | Content-addressed blueprint/version IDs + fingerprints (P5/P18) |
| 11 | **ContractRef** | `platform.foundation.contracts` | Versioned published contracts + `ENGINE_CONTRACTS` (`engine.registry.read`, `engine.compiler.compile`) binding for classification |

**All eleven reusable certified seams are present and reused. No seam is re-implemented.**

---

## 13. CAPABILITY DECOMPOSITION

Proposed importable runtime package: **`platform/blueprints/`** (hyphen-free analogue of `platform.projects` / `platform.workspace`). The task range (97–108, twelve tasks — larger than EPIC-005's eight) reflects the added L4 classification façade, versioning/lineage, and the provenance/trace-closure deliverable. Decomposition mirrors the certified 13-module `platform/projects/` and `platform/workspace/` topology, extended with the blueprint-specific classification, versioning, and provenance modules.

### 13.1 Sub-capabilities (net-new, record-only / read-model)

| Sub-capability | Module | Constitutional basis | Responsibility |
|----------------|--------|----------------------|----------------|
| **BP-CONTRACT** | `contracts.py` | §4.1 L2; PL-05 | Vocabulary (`BlueprintFamily`, `BlueprintStatus`, `Blueprint`, `BlueprintVersion`, `BlueprintProvenance`) + published `ContractRef`s + verb→permission map; binds to `BLUEPRINT_AUTHORING` + `BLUEPRINT_CATALOG` |
| **BP-ERRORS** | `errors.py` | §Authority-Boundary | `EC2-BP-*` error taxonomy over `platform.foundation.errors.PlatformError` |
| **BP-METADATA** | `metadata.py` | §2.1 #7; PC-04 | Immutable blueprint metadata value type (family, classification, owner, scope) |
| **BP-CLASSIFY** | `classification.py` | §4.3; ENG-CAP-02 | Read-only L4 façade binding to `engine.compiler.compile` / `engine.registry.read`; records EC-1 classification result (no invented semantics) |
| **BP-VALIDATE** | `validation.py` | §5; §4.3; P4 | Structural validation orchestration; invalid ⇒ EC-1 gap report; fail-closed rejection |
| **BP-VERSION** | `versioning.py` | P5/P18 | Immutable content-addressed versions + lineage + supersession (§9) |
| **BP-REGISTRY** | `registry.py` | §2.1 #7; PC-05 | Append-only, content-addressed blueprint registry; create/register/resolve/discover |
| **BP-CATALOG** | `catalog.py` | §2.2 PC-05; §4.1 L6 | L6 catalog read model/index over registered blueprints |
| **BP-PROVENANCE** | `provenance.py` | GOV-002 §6 link-4; §5 | Provenance-by-reference to `05-GENERATION` origin (framework + BP-* id) — the trace-closure record |
| **BP-SEARCH** | `search.py` | §2.2 PC-13; PC-05 | Authorization- + isolation-scoped discovery/search |
| **BP-CONTEXT** | `context.py` | §4.1 L3 | Immutable resolved blueprint runtime context (blueprint + workspace/project scope + granted actions) |
| **BP-HEALTH** | `health.py` | §9 OP-C1 | Blueprint health checks (provenance/referential-integrity) over the reused L8 health model |
| **BP-SERVICE** | `service.py` | §4.1 L3 | `BlueprintService` composition root + `BlueprintAccess` + `BlueprintEvidence` (two-gate access: identity ∧ isolation) |
| **BP-BOOTSTRAP** | `bootstrap.py` | §4; §8 | `bootstrap_blueprints(context)` — composes identity + observability + workspace + projects + EC-1 façade; publishes contracts; registers health |
| **BP-INIT** | `__init__.py` | — | Package surface re-exports |

### 13.2 Reused-by-reference (declared non-goals — NOT sub-capabilities)

Identity/authorization; workspace/tenant isolation; project association; audit/telemetry/health (L8); EC-1 classification/registry engine internals; contracts/events/IDs/hashing (Foundation) — all consumed by reference per §12.

### 13.3 Capability boundaries / partitions

- **Catalogs & classifies, never generates**: no generation orchestration (EPIC-007), no artifact production (EPIC-009).
- **Records classification, never computes it**: EC-1 owns classification; the platform records the result read-only.
- **Provenance by reference**: does not import or mutate `05-GENERATION` content (DP-03).
- **Scoped within a workspace/project**: no blueprint outside a resolvable workspace scope.

**Runtime modules, contracts, registries, and services determined above. Implementation decomposition complete — no code produced.**

---

## 14. READINESS ASSESSMENT

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Governance readiness** | ⚠️ CONDITIONAL | GOV-004 authorizes EC-2 lane; EXEC-001 conditionally activates. Link-4 break (RSK-01/BLK-AUTH-TRC-01, MEDIUM) bounds — and is discharged within — EPIC-006 (§5, §11.3). |
| **Architecture readiness** | ✅ READY | Contract §2.1 #7, PC-04/PC-05, §3.2 rows, §4.1 L3/L4/L5/L6, §4.3 EC-1 interaction, §5 acceptance all present; L4 classification seam published (`ENGINE_CONTRACTS`, `ENG-CAP-01/02`); EPIC-005 `AssociationKind.BLUEPRINT` published |
| **Dependency readiness** | ✅ READY | EPIC-005 COMPLETE; Identity CERTIFIED (blueprint groups exist); Foundation/Observability/Workspace COMPLETE; EC-1 registry/classification CERTIFIED; closure CLOSED (§11) |
| **Observability readiness** | ✅ READY | EC2-EPIC-013 COMPLETE; L8 audit/telemetry/health reusable |
| **Security readiness** | ✅ READY | Certified Identity + EC2-CAP-SEC-001 reusable by reference; two blueprint capability groups pre-exist; no new authority |
| **Implementation readiness** | ⚠️ CONDITIONAL | Realization template proven (8 additive `platform/**` runtimes; projects=13 modules @100% cov); controls operative (CI, determinism gate, TRACK-001, coverage gate); conditioned on discharging link-4 within the epic |

Two dimensions are CONDITIONAL for the single, instrument-derived reason that EPIC-006 is the first generation-lane epic and carries the link-4 trace obligation — a **bounding, in-scope** condition, not a blocker (A-2 §9/§10/§13). All other dimensions are unconditionally READY.

**Evidence: platform+engine suite green at last determination (1,575 passed / 0 failed / 99.86% coverage, A-2 §7); repository committed, synchronized, clean (HEAD `2fdbc6b`); EC-1 integrity preserved (0 `engine/**` edits).**

---

## 15. IMPLEMENTATION AUTHORIZATION DETERMINATION

- **Rationale.** EC2-EPIC-006 is the authorized next target (A-2: `NEXT IMPLEMENTATION TARGET DETERMINED`), the first uncompleted node on the critical path, the first epic of Wave 3, and the sole root that unblocks the generation spine (007→…→012). Its complete implementation specification is derivable **entirely from repository evidence** with **no architectural, classification, or governance invention**: the two capability groups, the authorization seam, the isolation rule, the L4 EC-1 classification façade contracts, the audit/telemetry/health model, the registry/versioning discipline, and the project association surface all physically pre-exist and are COMPLETE/CERTIFIED.
- **Dependency evidence.** Declared dependencies `EPIC-005` (COMPLETE, registered `95d6796`) and `EC-1 registry/classification` (CERTIFIED) are both satisfied; closure CLOSED (§11); no downstream runtime is required (associations/provenance are record-only references).
- **Readiness evidence.** Architecture/dependency/security/observability readiness satisfied (§14); governance/implementation readiness CONDITIONAL solely on the in-scope link-4 obligation; suite green; repository clean; EC-1 integrity preserved.
- **Boundary evidence.** Scope is fully bounded (§13): additive `platform/blueprints/`, catalog + classification-by-reference + versioning + provenance, reusing every certified seam; no protected-domain excursion; no `engine/**` or frozen-corpus write.
- **Standing conditions (A-3/A-4).** Implementation SHALL proceed additive-only over EC-1 (P10), 0 frozen-corpus writes (DP-03), determinism/reproducibility preserved (P5/P18), TRACK-001 evidence→status (fail-closed), trace citations preserved (GOV-001 Part 8), per-epic admission honored, **and SHALL discharge the link-4 Generation→Implementation trace obligation within the epic** (§5).

The single standing condition is not an external prerequisite but an EPIC-006 deliverable; it therefore **bounds** the work without blocking authorization. All admission criteria are met.

### CONCLUSION: **AUTHORIZED**

---

## 16. IMPLEMENTATION TASK DETERMINATION

Implementation sequence, phases, and task breakdown (derived from the certified workspace/projects realization order, mapped to indicative EC2-TASK-000097…000108). **Determination only — no implementation performed.**

### 16.1 Implementation sequence (dependency-ordered)

`contracts/errors/metadata → EC-1 classification façade → validation → versioning → registry → catalog/provenance → search → service/health → bootstrap/integration → trace-closure evidence`.

### 16.2 Implementation phases & task breakdown

| Phase | Task(s) | Deliverable | Validation |
|-------|---------|-------------|------------|
| **P1 — Contracts, errors, metadata** | TASK-000097–000098 | `errors.py`, `metadata.py`, `contracts.py` (vocabulary, verb→permission map, `BLUEPRINT_AUTHORING`+`BLUEPRINT_CATALOG` binding, `ContractRef`s) | vocabulary/contract tests; verb→permission map tests |
| **P2 — EC-1 classification façade** | TASK-000099 | `classification.py` (read-only L4 binding to `engine.registry.read` + `engine.compiler.compile`; records result) | façade tests; 0 `engine/**` edits (P10); classification result recorded |
| **P3 — Structural validation** | TASK-000100 | `validation.py` (valid/invalid decision; EC-1 gap report on rejection; fail-closed) | valid-accept / invalid-reject-with-gap-report tests (P4) |
| **P4 — Versioning & lineage** | TASK-000101 | `versioning.py` (immutable content-addressed versions, lineage, supersession) | immutability, lineage-chain, supersession, determinism tests (§9) |
| **P5 — Registry** | TASK-000102 | `registry.py` (append-only content-addressed blueprint registry; parent workspace/project scope) | idempotent id; duplicate fail-closed; scope tests |
| **P6 — Catalog & provenance (trace closure)** | TASK-000103–000104 | `catalog.py` (L6 read model/index), `provenance.py` (05-GENERATION origin by reference) | catalog discovery tests; **provenance-present / link-4 evidence** tests (§5) |
| **P7 — Search** | TASK-000105 | `search.py` (authz + isolation scoped; PC-13) | no cross-tenant/workspace leak; ranking; fail-closed |
| **P8 — Service & health** | TASK-000106 | `service.py` (`BlueprintService`, `BlueprintAccess`, `BlueprintEvidence`), `health.py` | two-gate access (every reason); authoring/classify/version/catalog; provenance-integrity fault → UNHEALTHY |
| **P9 — Bootstrap & integration** | TASK-000107 | `bootstrap.py`, `__init__.py`, `pyproject.toml` coverage line | contract publication; cross-runtime health; L8 audit; idempotency; cross-process determinism |
| **P10 — Trace-closure evidence & completion** | TASK-000108 | `platform/blueprints/EC2-EPIC-006-COMPLETION-REPORT.md` (cites EC-2 contract + `05-GENERATION` frameworks); REG-AUTO-001 registration | acceptance (P4/P5/P10/PLAT-C1..C4); **link-4 discharge evidence recorded**; suite green; determinism verified |

### 16.3 Validation & certification order

Per-phase unit tests → full platform+engine suite green (EC-1 integrity preserved) → coverage gate (≥90%, target 100% module) → ruff clean → determinism (cross-process fingerprint) → acceptance (§5 / P4) → certification impact (P2/P5/P9/P10/PLAT-C1…C4) → completion report → REG-AUTO-001 registration → milestone roll-up toward **M3 (Generation Operational)**.

---

## 17. FINAL RECOMMENDATION

`EC2-EPIC-006 — Blueprint Catalog & Management` is the correct and sole next authorized target: the first uncompleted node on the contract critical path, the opening epic of Wave 3, and the unique currently-executable unimplemented epic. Its complete specification is repository-derived with **no invention** — the two blueprint capability groups, the EC-1 classification façade contracts, the isolation rule, the L8 observability/audit/health model, the content-addressed registry/versioning discipline, and the EPIC-005 `AssociationKind.BLUEPRINT` seam all physically pre-exist and are COMPLETE/CERTIFIED. The one standing condition — the link-4 Generation→Implementation traceability break — is an **in-scope EPIC-006 deliverable** (discharged by provenance-carrying catalog records and generation-lane citation in the completion evidence), not an upstream prerequisite; it bounds but does not block admission.

**Recommendation:** admit and implement `EC2-EPIC-006` additively under `platform/blueprints/`, read-only over the certified EC-1 engine (consuming `engine.registry.read` + `engine.compiler.compile` via the L4 façade) and over the completed EC-2 layers, subject to the standing EXEC-001 conditions and per-epic admission, **discharging the link-4 trace obligation within the epic**. Subsequent order: `007 → {008, 009, 010} → 011 → 012 → UCOS-GO-LIVE-001`.

---

## IMPLEMENTATION AUTHORIZED

- **Epic:** `EC2-EPIC-006 — Blueprint Catalog & Management`
- **Runtime package (importable):** `platform/blueprints/` · **Determination path:** `platform/blueprints/EC2-EPIC-006-DETERMINATION.md`
- **Capability groups (reused, no new authority):** `CapabilityGroup.BLUEPRINT_AUTHORING` + `CapabilityGroup.BLUEPRINT_CATALOG`
- **Classification seam (reused, read-only):** `engine.registry.read` + `engine.compiler.compile` (L4 façade; `ENG-CAP-01/02`)
- **Dependency basis:** EPIC-005 (COMPLETE, registered `95d6796`), Identity (CERTIFIED), Foundation, Observability, Workspace — all COMPLETE; EC-1 registry/classification CERTIFIED; closure CLOSED
- **Standing condition (in-scope, bounding):** discharge link-4 Generation→Implementation trace (RSK-01 / BLK-AUTH-TRC-01) within the epic
- **Task range:** EC2-TASK-000097 … EC2-TASK-000108
- **Repository state:** branch `governance-reconciliation`, HEAD `2fdbc6b`, origin synchronized, working tree clean

*Determination only. No code, service, runtime, API, infrastructure, database, registry, or catalog created; no existing implementation modified; no architecture, classification, roadmap, or governance invented. Carries the EC-1 provisional-state disclosure verbatim; asserts no constitutional finality; external gates EC-1…EC-6 remain open.*

**END OF ARTIFACT — EC2-EPIC-006-DETERMINATION · ACTIVE · EVIDENCE-DERIVED · APPEND-ONLY · AUTHORITY-NEUTRAL · IMPLEMENTATION AUTHORIZED**
