# ADR-0002 — UCOS Ω∞ AEOS-001 · PHASE-1 ARCHITECTURAL DETERMINATION PACKAGE

| Field | Value |
|-------|-------|
| ARTIFACT | AEOS-001 Phase-1 — Repository Discovery, Composition & Architectural Determination |
| CLASSIFICATION | Architectural Determination (analysis only) — NOT implementation, NOT corpus, NOT governance |
| STATUS | DETERMINED · ADVISORY · AUTHORITY = NONE (derived truth) |
| MISSION | Determine the canonical architecture to transform UCOS into an Autonomous Engineering Operating System (AEOS) through **maximum reuse via composition**, never duplication |
| BASELINE | branch `governance-reconciliation` · HEAD `5874ede` · 2026-07-18 |
| METHOD | Read-only discovery of `engine/**`, `platform/**`, `00-BOOK/**`, `02-MASTER/**`, bands `03–13`, `00-MASTER/**`, `.kiro/**`, `scripts/**` |
| SUBORDINATE TO | Frozen corpus (`00-SOURCE/`,`99-FREEZE/`,`00-BOOK/`), UCGF, MIP v2 (`UCOS-MIP-000002`), CIOA (`UCOS-COMP-000000`), CCE (`UCOS-COMP-000001`), MCS (`00-MASTER/`) |
| PROHIBITION HONORED | No production code · no new engines · no stubs · no duplication · no modification of runtime/governance/constitutional/frozen artifacts |
| CONFLICT RULE | Where this conflicts with any higher frozen or governing instrument, the higher instrument governs and the conflicting statement is void to the extent of the conflict |

> **Determination in one sentence.** UCOS already contains the entire *certified capability substrate* (EC-1 `engine/`), the entire *governed surface substrate* (EC-2 `platform/`), the *constitutional specification* of orchestration and completeness (CIOA + CCE), a *repository digital twin* + *append-only ledgers* + *execution register*, and a *state-driven operational memory* (MCS). What AEOS requires that does **not yet exist as executable code** is a single **Execution Spine** that *composes* these into a running, resumable, multi-executor orchestration runtime — realizing CIOA/CCE (which today are constitutions on paper) and adding only the genuinely-missing coordination primitives (scheduler, lease, transaction, git orchestrator, recovery/resume, adapter layer, universal CLI). AEOS is **≈90% composition + orchestration** of what exists; the new work is the spine, not the organs.

---

## DELIVERABLE 1 — REPOSITORY CAPABILITY INVENTORY

Two capability planes exist: the **specified** plane (constitutional catalogs) and the **realized** plane (code).

### 1.1 Specified capability catalog (authority-neutral, `02-MASTER/`)
| Catalog | ID | Scheme | Count | Purpose |
|---------|----|--------|------:|---------|
| Universe Catalog | ARCH-001 | `UNI-001…112` | 112 | Fundamental concerns (11 classes CL-FND…INF) |
| Domain Catalog | ARCH-002 | `DOM-0001…0499` | 499 | Each ∈ exactly one universe (6 classes) |
| Capability Catalog | ARCH-003 | `CAP-0001…2027` | 2,027 | Each ∈ exactly one domain (7 classes) |
| Component Catalog | ARCH-004 | `CMP-0001…2709` | 2,709 | Each capability → ≥1 component (7 types) |

Compositional chain: **Universe → Domain → Capability → Component**. Plus the constitutional frame in MIP v2 (`UCOS-MIP-000002`, 50 parts): **28 constitutional universes** (U01–U28), **25 directives** (D1–D25), **LAW Ω∞-000** (7 properties: representable, governable, traceable, explainable, simulatable, evolvable, compilable).

### 1.2 Realized executable capabilities (`engine/` EC-1, `platform/` EC-2, `00-BOOK/tools/`)
| # | Realized capability | Location | Status |
|---|---------------------|----------|--------|
| RC-01 | Blueprint compile pipeline (parse→IR→resolve→compile→optimize→package→sign→publish) | `engine/compiler/` | CERTIFIED |
| RC-02 | Dependency resolution + cycle detection + topological order | `engine/compiler/{resolver,cycles}.py` | CERTIFIED |
| RC-03 | Deterministic/hermetic double-build reproducibility | `engine/determinism/` | CERTIFIED |
| RC-04 | Factory generation orchestration (classify→route→execute) | `engine/factory/` | CERTIFIED |
| RC-05 | Runtime assembly + deploy + rollback + disclosure | `engine/runtime/` | CERTIFIED |
| RC-06 | Validation engine (checks, gates, acceptance, evidence) | `engine/validation/` | CERTIFIED |
| RC-07 | Certification engine + hash-chained append-only ledger + closure | `engine/certification/` | CERTIFIED |
| RC-08 | Registry adapter (artifacts, relationship graph, volumes, integrity) | `engine/registry/` | CERTIFIED |
| RC-09 | Foundation (config/secrets, contracts+versioning, frozen-path guard, structured logging/telemetry/correlation) | `engine/foundation/` | CERTIFIED |
| RC-10 | Certification console (surface, ledger view, lineage, readiness, governance) | `platform/certification/` | FROZEN (EC-2) |
| RC-11 | Coverage engine (Universe→Code spine, gaps, health, certification) | `platform/coverage/` | FROZEN |
| RC-12 | Generation request lifecycle + dispatch ledger + provenance ledger | `platform/generation/` | FROZEN |
| RC-13 | Runtime operations planner (admit→plan deploy/rollback→record) + ledger + reversibility proof | `platform/runtime_operations/` | FROZEN |
| RC-14 | Security (classification, intelligence/findings, zones, registries, observability signals) | `platform/security/` | FROZEN |
| RC-15 | Artifact explorer (references, lineage, provenance trace, search) | `platform/artifact_explorer/` | FROZEN |
| RC-16 | Projects + associations + workspaces + administration (RBAC, audit, membership) | `platform/{projects,administration,workspace}/` | FROZEN |
| RC-17 | Execution dashboard (service, views) | `platform/execution_dashboard/` | FROZEN (EC2-EPIC-008) |
| RC-18 | Observability + portal surfaces | `platform/{observability,portal}/` | FROZEN |
| RC-19 | Blueprint catalog + validation + versioning + identity | `platform/{blueprints,identity}/` | FROZEN |
| RC-20 | Knowledge-graph build, append-only ID/page ledger, registries, control-tower emission, classification, enforce gates | `00-BOOK/tools/ukb.py` | ACTIVE (automation) |
| RC-21 | Execution register EXEC-REG-001 (append-only, forward-only; realizes RUNTIME-006) | `00-BOOK/tools/ukb.py exec` | ACTIVE |
| RC-22 | Synchronization runtime (schedule·execute·verify·audit·recover) + connectors + digital-twin overlay | `00-BOOK/tools/ukbx.py` | ACTIVE |
| RC-23 | Atomic registration transaction (REG-AUTO-001) + drift guard | `00-BOOK/tools/register.sh` | ACTIVE |
| RC-24 | Verification/env gates (lint→test→coverage≥90→enforce→drift) + self-healing env | `verify.sh`,`doctor.sh`,`bootstrap.sh`,`Makefile`,`scripts/ucos-env.sh` | ACTIVE |

---

## DELIVERABLE 2 — REPOSITORY ARCHITECTURE INVENTORY

**Nature.** UCOS is a *constitution-first operating-system-of-engineering*: the numbered bands and `02-MASTER/` are markdown constitutions/catalogs; `00-BOOK/` is a **generated** knowledge book; realized behavior lives only in `engine/` + `platform/` + `00-BOOK/tools/`.

**Layered stack (authority descends, subordination ascends):**
```
FROZEN CORPUS        00-SOURCE/ · 99-FREEZE/ · 00-BOOK/ (read-only, DP-03)
UNIVERSAL GOVERNANCE UCGF + Governance Operating Model + GOV-001…006 spine
LAYER POLICIES       Engineering Intelligence + per-layer quality/traceability constitutions
DOMAIN CONSTITUTIONS 02-MASTER/ (universal constitutions + ARCH-001…004 + bands 03–13)
ORCHESTRATION SPEC   CIOA (UCOS-COMP-000000) "what next"  +  CCE (UCOS-COMP-000001) "is it complete"
IMPLEMENTATION       MIP v2 → EC-1 (engine/) → EC-2 (platform/) → EC-3 (bands 10–13, in progress)
OPERATIONAL MEMORY   00-MASTER/ MCS (MCP-001…007 + MCS-000) — state-driven boot, AUTHORITY=NONE
AUTOMATION           00-BOOK/tools/{ukb,ukbx}.py + register.sh + verify/doctor/bootstrap + CI
```

**Constitutional band map (docs only unless noted):**
| Band | Concern | Realized code |
|------|---------|---------------|
| 03-CATALOGS | Canonical API/App/Data/Event/Service/Workflow/Runtime catalogs | No |
| 04-REFERENCE | Universal reference architectures | No |
| 05-GENERATION | Generation frameworks | No |
| 06-IMPLEMENTATION | Implementation *definitions* (incl. CIOA/CCE `-IMPLEMENTATION.md`) | No — defines what `engine/`+`platform/` realize |
| 07-ENGINEERING | Type/Object/Identity/Value/Relationship systems | No |
| 08-RUNTIME | Runtime doctrine (RUNTIME-001…014) | No (RUNTIME-006 partially realized by EXEC-REG-001) |
| 09-PLATFORM | Platform doctrine (PLATFORM-001…018) | Partially by `platform/` |
| 10-DATA | Data doctrine (DATA-001…018) — **EC-3 RUNNABLE root** | Class-C spec COMPLETE; Class-I realization NOT_STARTED |
| 11-SERVICE | Service doctrine | No |
| 12-APPLICATION | Application doctrine | No |
| 13-INFRASTRUCTURE | Infrastructure doctrine | No |

---

## DELIVERABLE 3 — CANONICAL CAPABILITY CATALOG

The catalog already exists and is canonical: **ARCH-003 (2,027 capabilities)** anchored to **ARCH-002 (499 domains)** anchored to **ARCH-001 (112 universes)** and MIP v2's 28 constitutional universes. AEOS **SHALL NOT** mint a parallel capability identifier system (GOV-001-N1, MCS I-G2). AEOS capabilities are **executable capability nodes** that reference existing `CAP-*`/`CMP-*`/`Uxx` IDs; the AEOS-new capability class is exclusively the **orchestration/execution** capability (the spine), which composes RC-01…RC-24. Every AEOS capability MUST resolve to a purpose-trace edge (MIP Part 1) and satisfy LAW Ω∞-000.

---

## DELIVERABLE 4 — CANONICAL ENGINE CATALOG

"Engine" = an authoritative, reusable behavioral unit. Replacement of any is **prohibited** (RULE-002).

| Engine | Canonical location | Authority | Reuse posture |
|--------|--------------------|-----------|---------------|
| Compiler Engine | `engine/compiler/` | CERTIFIED (EC-1) | REUSE / COMPOSE — never replace |
| Determinism Engine | `engine/determinism/` | CERTIFIED | REUSE |
| Factory/Generation Engine | `engine/factory/` | CERTIFIED | REUSE |
| Runtime Assembly/Deploy Engine | `engine/runtime/` | CERTIFIED | REUSE |
| Validation Engine | `engine/validation/` | CERTIFIED | REUSE (CCE Gate 4) |
| Certification Engine + Ledger | `engine/certification/` | CERTIFIED | REUSE (CCE Gate 7/10; ledger = event-store pattern) |
| Registry Engine | `engine/registry/` | CERTIFIED | REUSE |
| Foundation (config/contracts/guards/obs) | `engine/foundation/` | CERTIFIED | REUSE (spine base layer) |
| Coverage Engine | `platform/coverage/` | FROZEN (EC-2) | REUSE (CCE Gate 1/3/9) |
| Certification Console | `platform/certification/` | FROZEN | REUSE (readiness Gate 8, governance Gate 10) |
| Generation Request/Dispatch Engine | `platform/generation/` | FROZEN | REUSE (request lifecycle = capability lifecycle seam) |
| Runtime Operations Engine | `platform/runtime_operations/` | FROZEN | REUSE (deploy/rollback orchestration seam) |
| Security Engine | `platform/security/` | FROZEN | REUSE |
| Execution Dashboard | `platform/execution_dashboard/` | FROZEN | REUSE / EXTEND (mission-control view) |
| Knowledge/Registration Engine (UKB) | `00-BOOK/tools/ukb.py` | ACTIVE | REUSE (event/exec register, graph, control tower) |
| Synchronization Runtime (UKBX) | `00-BOOK/tools/ukbx.py` | ACTIVE | REUSE / EXTEND (schedule/verify/recover pattern) |
| **CIOA (orchestration)** | `02-MASTER/UCOS-COMP-000000` + `06-IMPLEMENTATION/…` | SPEC ONLY | **REALIZE (compose) — this is the spine's brain** |
| **CCE (completeness)** | `02-MASTER/UCOS-COMP-000001` + `06-IMPLEMENTATION/…` | SPEC ONLY | **REALIZE (compose the 10 gates over existing engines)** |
| MCS (operational memory) | `00-MASTER/` | ACTIVE (docs+state) | REUSE / EXTEND (state model, boot contract, recovery) |

---

## DELIVERABLE 5 — REUSE MATRIX

For every AEOS responsibility: existing implementation · strategy · replacement prohibition · new work · justification.

| AEOS responsibility | Existing implementation | Strategy | Replace? | New impl required | Justification |
|---------------------|-------------------------|----------|:--------:|:-----------------:|---------------|
| Compile intent→artifact | `engine/compiler/` | COMPOSE | Prohibited | No | Certified pipeline; spine calls it |
| Dependency graph + topo order + cycle check | `engine/compiler/{resolver,cycles}.py` + Depends-On DAG (ukb.py) | COMPOSE | Prohibited | No | Scheduler consumes these |
| Determinism/reproducibility | `engine/determinism/` | COMPOSE | Prohibited | No | Idempotent orchestration determinations |
| Generation execution | `engine/factory/` + `platform/generation/` | COMPOSE | Prohibited | No | Capability execution routes here |
| Deploy / rollback | `engine/runtime/` + `platform/runtime_operations/` | COMPOSE | Prohibited | No | Recovery/rollback reuse reversibility proof |
| Validation | `engine/validation/` | COMPOSE | Prohibited | No | CCE Gate 4 |
| Certification + audit ledger | `engine/certification/` | COMPOSE | Prohibited | No | Event-store + Gate 7/10 |
| Coverage / gaps | `platform/coverage/` | COMPOSE | Prohibited | No | CCE Gate 1/3/9 |
| Readiness / governance | `platform/certification/status.py` | COMPOSE | Prohibited | No | CCE Gate 8/10 |
| Completeness determination ("is it complete") | CCE **spec** (no code) | REALIZE by composition | N/A | **Yes (thin unifier)** | ~95% orchestration of engines above; 0 new judgment |
| Sequencing / "what next" / critical path / parallel / next-artifact / forecast | CIOA **spec** (no code) | REALIZE by composition | N/A | **Yes (derivation engine)** | Derives from Depends-On DAG + CCE + control-tower; the 4 CIOA "derive" domains are genuinely new |
| Repository state / registry | `00-BOOK/tools/ukb.py` + `artifacts.json`/`control-tower.json` | COMPOSE | Prohibited | No | STATUS-001 non-projection preserved |
| Event ledger / event store | certification ledger + `twin.json`/`signals.json` + EXEC-REG-001 + generation/runtime-ops ledgers | COMPOSE / UNIFY | Prohibited | Thin unifying reader | Multiple append-only ledgers already exist |
| Execution state engine | CIOA state models + STATUS-001 + MCP-002 | REALIZE | N/A | Yes | State machine specified; needs runtime |
| Execution scheduler | CIOA execution-queue spec + topo antichains | REALIZE | N/A | Yes | Derivation defined; no runtime scheduler |
| Transaction manager | `register.sh` atomic txn + ledgers | EXTEND | No | Yes (execution-txn scope) | Registration txn exists; execution txn does not |
| Lease manager (concurrency) | — | NEW | N/A | Yes | No concurrency/lease control anywhere |
| Recovery / resume manager | MCP-007 + `CHECKPOINTS/` + `ukbx recover` | REALIZE/EXTEND | No | Yes | Doc + partial sync-recover; no coded execution resume |
| Git orchestrator | manual git + session-load hook (read-only) | NEW (thin) | N/A | Yes | Git is manual; commit-per-capability unenforced in code |
| Mission control runtime | `platform/execution_dashboard/` + control tower + MCS | COMPOSE / EXTEND | No | Thin runtime | Views + state exist; runtime binding is new |
| Mission control dashboard | `platform/execution_dashboard/views.py` | REUSE / EXTEND | Prohibited | No | Add spine data source |
| AI adapter layer | `.kiro/steering` + hooks (Kiro-only) | GENERALIZE | No | Yes | Lifecycle contract exists; multi-AI abstraction missing |
| Human adapter | operator model MIP Part 3 (spec) | REALIZE | N/A | Yes | Spec only |
| Automation runtime | `ukb.py`/`ukbx.py`/`register.sh`/CI | EXTEND | No | Thin | Schedule/verify/recover pattern reusable |
| Universal CLI | `ukb.py` (corpus CLI) | EXTEND | No | Yes | No unified AEOS execution CLI |

---

## DELIVERABLE 6 — DUPLICATION ANALYSIS

The repository is **deliberately low-duplication** (one-canonical-instance-per-concern, GOV-001). Findings:

| # | Capability | Authoritative | Secondary | Intentional? | Recommendation |
|---|------------|---------------|-----------|:------------:|----------------|
| D-1 | Certification | `engine/certification/` (engine + ledger) | `platform/certification/` (console/facade/ledger *view*) | Yes (layered: L1 engine vs L4 read-only surface) | KEEP — compose; not duplication |
| D-2 | Validation | `engine/validation/` | `platform/validation/facade.py` | Yes (façade) | KEEP — compose |
| D-3 | Append-only ledgers | `engine/certification/ledger.py` (canonical hash-chain pattern) | generation dispatch ledger, runtime-ops ledger, `twin.json`/`signals.json`, EXEC-REG-001 | Yes (per-domain projections) | **UNIFY at read-time** via a single Event Ledger reader in the spine; do NOT merge stores (each is a legitimate domain projection) |
| D-4 | State / "what next" | CIOA spec + `control-tower.json` | MCP-002 "Next Authorized Capability" | Yes (MCS reflects CIOA) | KEEP — MCS is derived truth; spine must make MCP-002 a projection of the realized CIOA, not a hand-authored twin |
| D-5 | Orchestration wording | `engine/factory` "orchestration", `platform/runtime_operations` "orchestration" | CIOA "orchestration" | Coincidental naming | No action — different scopes (generation vs runtime-op vs repository-sequence) |
| D-6 | Digital twin | `twin.json` (repository twin, VOL-021) | proposed AEOS "execution digital twin" | N/A | **EXTEND the existing twin**, do not create a second twin store |
| D-7 | CIOA/CCE constitution vs implementation-def | `02-MASTER/UCOS-COMP-0000{00,01}` (rules) | `06-IMPLEMENTATION/…-IMPLEMENTATION.md` (definition) | Yes (spec/impl split) | KEEP — the implementation docs are the build spec for realization; no code duplication exists to remove |

**Net:** zero *obsolete* duplication requiring removal. The single actionable item is **read-time unification** of the several append-only ledgers behind one spine-level Event Ledger interface (D-3), and making MCP-002 a *projection* of realized CIOA (D-4).

---

## DELIVERABLE 7 — GAP ANALYSIS

Genuinely missing (not classifying any existing certified system as missing). All gaps are in the **execution/orchestration runtime**, none in the capability substrate.

| Gap ID | Missing capability | Nearest existing basis | Severity |
|--------|--------------------|------------------------|:--------:|
| G-01 | **Executable CCE** (completeness runtime) | CCE spec + all 10 gate engines exist | HIGH |
| G-02 | **Executable CIOA** (state + critical-path + parallel + next + forecast runtime) | CIOA spec + DAG + control tower | HIGH |
| G-03 | **Execution scheduler** (drive the RUNNABLE frontier) | CIOA execution-queue spec | HIGH |
| G-04 | **Lease manager** (concurrency / single-active-capability enforcement in code) | MCS "one active" contract (doc) | MEDIUM |
| G-05 | **Execution transaction manager** (begin/commit/abort a capability execution) | `register.sh` atomic txn (registration only) | MEDIUM |
| G-06 | **Recovery + resume managers** (crash/interrupt → resume from ledger) | MCP-007 + CHECKPOINTS + `ukbx recover` | MEDIUM |
| G-07 | **Git orchestrator** (one-commit-per-capability, branch/HEAD verify, provenance) | session-load hook (read-only) | MEDIUM |
| G-08 | **Unified Event Ledger reader** over the existing per-domain ledgers | 5 append-only ledgers exist | MEDIUM |
| G-09 | **AI adapter layer** (Claude/Gemini/GPT/Codex/Cursor/Copilot/Windsurf/Kiro/CI/human/future) | `.kiro` steering + hooks (Kiro-only) | HIGH |
| G-10 | **Human adapter** (operator plane binding) | MIP Part 3 operator model (spec) | LOW |
| G-11 | **Mission Control runtime** (bind dashboard/control-tower/MCS to live spine) | dashboard + control tower + MCS | MEDIUM |
| G-12 | **Universal AEOS CLI** (single entrypoint: status/next/run/validate/certify/resume) | `ukb.py` corpus CLI | MEDIUM |
| G-13 | **Automation runtime binding** (event-driven execution beyond registration hook) | hooks + CI + `ukbx` scheduler | LOW |

---

## DELIVERABLE 8 — MISSING CAPABILITY DETERMINATION

The missing capabilities collapse to **one composite subsystem: the AEOS Execution Spine**, plus **two adapters** (AI, Human) and **one surface** (Mission Control runtime binding). Everything else is reuse. The spine is defined by *composition contracts* over existing engines, adding only: (a) realization of CIOA/CCE, (b) scheduler, (c) lease, (d) execution transaction, (e) recovery/resume, (f) git orchestrator, (g) unified event-ledger reader, (h) universal CLI. No new *capability* engine (compiler/validation/certification/etc.) is missing.

---

## DELIVERABLE 9 — EXECUTION SPINE ARCHITECTURE

Layered, composition-only. Each component cites what it composes; none replaces an engine.

```
                       ┌───────────────────────── UNIVERSAL AEOS CLI (G-12) ─────────────────────────┐
                       │  status · next · run · validate · certify · resume · plan · dashboard        │
                       └───────────────┬─────────────────────────────────────────────────┬───────────┘
        ADAPTER PLANE                  │                                                   │
  ┌────────────────────┐   ┌───────────▼───────────┐                         ┌────────────▼───────────┐
  │ AI Adapter (G-09)  │   │  Human Adapter (G-10)  │                         │ Automation Runtime(G-13)│
  │ Claude/Gemini/GPT/ │   │  operator plane        │                         │ hooks · CI · scheduler  │
  │ Codex/Cursor/CoPilot│  │  (MIP Part 3)          │                         │ (ukbx pattern)          │
  │ Windsurf/Kiro/CI    │  └───────────┬───────────┘                         └────────────┬───────────┘
  └─────────┬──────────┘               │  uniform Executor contract (LOAD→EXECUTE→VALIDATE→COMMIT)     │
            └──────────────────────────┴───────────────────────┬───────────────────────────┘
                                                                │
   ORCHESTRATION PLANE (the spine's brain)                      ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Execution Coordinator  ──drives──▶  Execution Scheduler  ──reads──▶  Dependency Coordinator        │
  │        │  (realize CIOA G-02)              (G-03, topo antichains)        (engine/compiler/cycles)   │
  │        ▼                                                                                            │
  │  Execution State Engine (CIOA state machine) ── projects ──▶ MCP-002 / control-tower.json           │
  │        │                                                                                            │
  │        ├── Transaction Mgr (G-05) ── Lease Mgr (G-04) ── Recovery Mgr + Resume Mgr (G-06)            │
  │        └── Git Orchestrator (G-07: 1 commit = 1 capability, verify branch/HEAD, provenance)         │
  └──────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                   │  every gate/verdict deferred to existing engines
   COMPLETENESS + EVENT PLANE                      ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  CCE runtime (realize G-01) ── composes ──▶ engine/validation · engine/certification ·              │
  │      platform/coverage · platform/certification.status (10 gates, 24 dimensions, fail-closed)       │
  │  Unified Event Ledger reader (G-08) ── over ──▶ certification ledger · twin.json/signals.json ·     │
  │      EXEC-REG-001 · generation dispatch ledger · runtime_operations ledger  (append-only, read)     │
  └──────────────────────────────────────────────────────────────────────────────────────────────────┘
   CAPABILITY SUBSTRATE (reuse-only, replacement prohibited)
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  EC-1 engine/{compiler,factory,runtime,determinism,validation,certification,registry,foundation}    │
  │  EC-2 platform/{coverage,certification,generation,runtime_operations,security,execution_dashboard,…} │
  │  UKB/UKBX (00-BOOK/tools) · MCS (00-MASTER) · control-tower.json/artifacts.json/twin.json           │
  └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Spine component determinations (all composition; all AUTHORITY=NONE, ENGINEERING-EXECUTION-ONLY, additive over frozen EC-1/EC-2):**

| Component | Determination | Composes |
|-----------|---------------|----------|
| Execution Event Ledger | UNIFY read-time; append via existing stores only | certification ledger + `twin.json`/`signals.json` + EXEC-REG-001 + platform ledgers |
| Execution Event Store | REUSE existing append-only stores (no new store — CIOA/CCE law) | same |
| Execution Coordinator | REALIZE CIOA determination model | CIOA spec + CCE + DAG |
| Execution State Engine | REALIZE CIOA 12 artifact / 9 completion states | STATUS-001 + `artifacts.json` + MCP-002 |
| Execution Digital Twin | EXTEND existing `twin.json` (no second twin) | `ukbx` twin overlay |
| Execution Scheduler | NEW derivation runtime (topological antichains) | `engine/compiler/cycles.py` + CIOA parallelization |
| Dependency Coordinator | REUSE | `engine/compiler/{resolver,cycles}` + Depends-On DAG |
| Transaction Manager | EXTEND registration-txn pattern to execution scope | `register.sh` + ledgers |
| Lease Manager | NEW (thin) — enforce MCS "one active capability" | MCS contract |
| Recovery Manager | REALIZE MCP-007 + reuse reversibility proof | MCP-007 + `runtime_operations.reversibility` + `ukbx recover` |
| Resume Manager | REALIZE from ledger + last checkpoint | `CHECKPOINTS/` + Event Ledger |
| Git Orchestrator | NEW (thin) — commit-per-capability + verify | git + `foundation/guards/frozen_paths` |
| Mission Control Runtime | EXTEND | `platform/execution_dashboard` + control tower + MCS |
| Execution Dashboard | REUSE / add data source | `platform/execution_dashboard/views.py` |
| AI Adapter Layer | GENERALIZE lifecycle contract | `.kiro` steering/hooks + MCS §06 AI Operating Model |
| Human Adapter | REALIZE operator plane | MIP Part 3 |
| Automation Runtime | EXTEND | `ukbx` scheduler + CI + hooks |
| Universal CLI | EXTEND | `ukb.py` CLI pattern |

---

## DELIVERABLE 10 — REPOSITORY DIGITAL TWIN ARCHITECTURE

**Determination: EXTEND, do not recreate.** The repository already has a living digital twin: `00-BOOK/DATA/twin.json` + `signals.json` (VOL-021 Digital Twin, maintained by `ukbx.py`, append-only overlay over foundation DATA). The AEOS "execution digital twin" is a **projection view** of this twin filtered to execution state (artifact states, RUNNABLE frontier, critical path, blockers, forecast) — produced by the realized CIOA, written through the existing overlay, never as a new store (CIOA-LAW-001, MCS I-I1). Twin = derived output; regenerated, never hand-edited.

---

## DELIVERABLE 11 — TRANSACTION ARCHITECTURE

Two transaction scopes; both fail-closed, both append-only.
1. **Registration transaction** (exists): `register.sh` = enforce --pre → build → sync/twin/portal/validate/certify → enforce --post, with `--guard` drift gate. Atomic over the corpus registration.
2. **Execution transaction** (new, thin): `BEGIN(capability)` → acquire lease → append `STARTED` event → execute via adapter → `VALIDATE` (CCE) → on pass `COMMIT` (git commit + append `COMPLETE`/`CERTIFIED` events + release lease); on fail `ABORT` (append `FAILED`, invoke Recovery, release lease). No partial state persists (CCE-LAW-003 / CIOA-LAW-005 fail-closed). Every transaction references its governing determination (MCS I-I2).

---

## DELIVERABLE 12 — EVENT ARCHITECTURE

**Append-only, content-addressed, hash-chained** — pattern already canonical in `engine/certification/ledger.py`. AEOS event taxonomy (all recorded into existing stores, unified at read-time):
`CAPABILITY_PROPOSED · REGISTERED · READY · ACTIVE · IN_PROGRESS · VALIDATED · CERTIFIED · FROZEN · BLOCKED · SUPERSEDED · DEPRECATED · RETIRED` (CIOA 12 states) and lifecycle events `SESSION_START · LEASE_ACQUIRED · TXN_BEGIN · GATE_EVAL · TXN_COMMIT/ABORT · CHECKPOINT · SESSION_STOP`. Every event carries: id, UTC timestamp, HEAD, capability id, governing determination id, evidence refs, content hash, prev-hash. Determinism law: identical evidence ⇒ byte-identical event id (CIOA-LAW-008, CCE-LAW-006).

---

## DELIVERABLE 13 — CAPABILITY LIFECYCLE

Adopt CIOA's 12 artifact states projected to 9 completion states verbatim (no new lifecycle):
```
PROPOSED → REGISTERED → READY → ACTIVE → IN_PROGRESS → COMPLETE → CERTIFIED → FROZEN → ARCHIVED
                                   ↘ BLOCKED (→READY on clear)      ↘ SUPERSEDED/DEPRECATED/RETIRED
```
Transitions are legal-edge-only (MCS §05); the only backward edge is a defect-driven REOPEN citing evidence. Separation of duties invariant: **Executor ≠ CIOA ≠ CCE**.

---

## DELIVERABLE 14 — EXECUTION LIFECYCLE

The MCS AI Operating Model (`MCS-000 §06`) is the canonical execution lifecycle; AEOS realizes it in code:
```
LOAD MCP-001 (identity) → LOAD MCP-002 (state → Next Authorized Capability)
 → VERIFY repo (branch·HEAD·tree·sync)   [mismatch → Recovery]
 → SCHEDULER picks RUNNABLE capability (CIOA)  → LEASE acquire  → TXN begin
 → adapter EXECUTE (one logical capability, additive-only)
 → CCE VALIDATE (10 gates, fail-closed)
 → UPDATE state (MCP-002/003/005/006) → CHECKPOINT (MCP-007)
 → GIT commit (1 commit = 1 capability, references governing determination) → TXN commit → LEASE release
 → STOP (MCP-002 left accurate)
```
Idempotent at boundaries; infinitely repeatable; O(1) boot (two files).

---

## DELIVERABLE 15 — RECOVERY LIFECYCLE

```
INTERRUPT (crash / session end / mismatch)
 → BOOT reads MCP-001 + MCP-002
 → VERIFY git vs recorded state
     • match      → resume Next Authorized Capability
     • mismatch   → MCP-007 recovery:
          - read latest CHECKPOINTS/CKPT-<ts>-<HEAD>.md
          - replay Event Ledger to last consistent COMMIT
          - if capability was mid-TXN → ABORT (fail-closed), release stale lease, re-derive RUNNABLE via CIOA
          - if rollback needed → reuse platform/runtime_operations reversibility proof
 → RESUME
```
No speculative state; absence of evidence = NOT-DONE. Recovery composes MCP-007 + checkpoints + reversibility proof + `ukbx recover` isolation pattern.

---

## DELIVERABLE 16 — AI ADAPTER ARCHITECTURE

**Determination: one uniform Executor contract, N thin adapters.** The AI Operating Model (`MCS-000 §06`) is already vendor-neutral (a lifecycle, not an API). AEOS defines an **Executor Port**:
```
Executor.load(context) · execute(capability_ticket) → change_set · report(evidence)
```
Adapters implement the port without modifying the OS (RULE: integrate without modifying the operating system):
| Executor | Adapter binding |
|----------|-----------------|
| Kiro | `.kiro/steering` + hooks (exists) — reference implementation |
| Claude / Gemini / ChatGPT / Codex | prompt+context injection of MCP-001/002 + capability ticket; change-set back via CLI/patch |
| Cursor / Copilot / Windsurf | editor-agent binding to the same ticket + verify gate |
| CI/CD | non-interactive adapter: `aeos run --next --headless` in `ec1-ci.yml` |
| Human | Human Adapter (operator plane, MIP Part 3) |
| Future AI | any executor honoring LOAD→EXECUTE→VALIDATE→UPDATE→CHECKPOINT→COMMIT→STOP is compliant (MCS §10 AI-agnostic) |
The OS never depends on a vendor API; adapters are append-only additions.

---

## DELIVERABLE 17 — GIT ORCHESTRATION ARCHITECTURE

Today git is manual (session-load hook only *reads* branch/HEAD/tree/sync). AEOS Git Orchestrator (thin, new):
- **Verify** at boot: branch·HEAD·tree·sync equal recorded MCP-002 (I-R1); mismatch → Recovery.
- **Guard**: refuse any staged write under frozen paths (reuse `engine/foundation/guards/frozen_paths.py`) or under `engine/**`/`platform/**` (additive-only, I-R3).
- **Commit**: one commit = one logical capability, message references governing determination id (I-I2), after CCE PASS only.
- **Never**: push to main, force-push, reset --hard, amend post-hook, or `--no-verify` (git-safety) unless explicitly authorized.
- **Provenance**: commit hash appended to Event Ledger + checkpoint.

---

## DELIVERABLE 18 — MISSION CONTROL ARCHITECTURE

Compose, don't rebuild. Three existing surfaces bind into one runtime:
- **State/metrics:** `control-tower.json` + `platform/execution_dashboard` (views/service, EC2-EPIC-008) + MCP-005 dashboard.
- **What-next:** realized CIOA (RUNNABLE frontier, critical path, next-artifact, forecast).
- **Memory/boot:** MCS (MCP-001/002/007).
Mission Control Runtime = a read-model that joins these and exposes them via the Universal CLI (`aeos status`, `aeos dashboard`, `aeos next`) and the existing dashboard views. Adds a data source; replaces no surface.

---

## DELIVERABLE 19 — DEPENDENCY GRAPH

Canonical layered dependency (acyclic; ascending = "depends on / subordinate to"):
```
LAW Ω∞-000 (7 properties)
   ▲
MIP v2 (28 universes · 25 directives) ── ARCH-001..004 catalogs
   ▲
UCGF / Governance Operating Model ── GOV-001..006
   ▲
Domain constitutions (02-MASTER) ── bands 03–13
   ▲
CIOA spec  ── depends-on ──▶ CCE spec
   ▲                              ▲
EC-1 engine/  ◀── composed by ── CCE gates (validation, certification, coverage*, readiness*)   (*platform)
   ▲
EC-2 platform/ (composes EC-1)
   ▲
UKB/UKBX + control-tower/twin/artifacts (read EC layers + corpus)
   ▲
MCS (00-MASTER) — reads all, writes only itself
   ▲
AEOS EXECUTION SPINE (new) — composes CIOA+CCE+engines+UKB+MCS; depends on all below; owns none
   ▲
Adapters (AI/Human/Automation) + Universal CLI — depend on the spine
```
Cross-cutting dependency classes all resolve downward into existing evidence: **execution** → CIOA/scheduler; **certification/validation** → CCE→engines; **repository** → ukb/artifacts.json; **knowledge** → knowledge-graph registry; **runtime** → engine/runtime + platform/runtime_operations; **infrastructure** → band 13 (spec); **governance** → GOV-001..006 + UCGF. No cycle (CIOA-LAW-004; MCS I-A1).

---

## DELIVERABLE 20 — IMPLEMENTATION ROADMAP

Deterministic, dependency-ordered. Each wave is CCE-gated, additive-only, one-commit-per-capability. **This roadmap authorizes nothing** (CIOA-LAW-010) — it is the sequence for a future authorized program.

| Wave | Deliverable | Depends on | New vs compose |
|------|-------------|------------|----------------|
| W0 | Unified Event Ledger reader (G-08) | existing ledgers | Thin new (read-only) |
| W1 | CCE runtime (G-01) — 10 gates over existing engines | W0, engine/validation+certification, platform/coverage+certification | Compose (≈95%) |
| W2 | CIOA runtime (G-02) — state engine + dependency coordinator | W1, engine/compiler/cycles, DAG, control-tower | Compose + new derivations (critical path/parallel/next/forecast) |
| W3 | Execution Scheduler (G-03) + Lease Manager (G-04) | W2 | New (thin) |
| W4 | Execution Transaction Mgr (G-05) + Git Orchestrator (G-07) | W3, register.sh pattern, frozen_paths guard | Extend + new (thin) |
| W5 | Recovery + Resume Managers (G-06) | W4, MCP-007, reversibility proof | Realize |
| W6 | Executor Port + AI Adapter (G-09) + Human Adapter (G-10) | W5, MCS §06 | Generalize |
| W7 | Mission Control Runtime (G-11) + dashboard extension | W2/W6, execution_dashboard | Compose/extend |
| W8 | Universal AEOS CLI (G-12) + Automation Runtime binding (G-13) | W1–W7, ukb.py CLI | Extend |

Critical path: **W0 → W1 → W2 → W3 → W4 → W5** (the spine core). W6/W7/W8 parallelize after W2/W5.

---

## DELIVERABLE 21 — MIGRATION STRATEGY

- **Additive-only:** the spine is new code in a new module (e.g. a top-level `aeos/` package or `engine/orchestration/` seam) that *imports* EC-1/EC-2 and *reads* corpus/DATA; it never mutates `engine/**`, `platform/**`, or frozen corpus (MCS I-R2/I-R3).
- **MCP-002 becomes a projection:** once CIOA is realized, "Next Authorized Capability" is *generated* from CIOA output, not hand-authored (removes D-4 duplication).
- **Twin extension, not replacement:** execution twin written through the existing `ukbx` overlay (D-6).
- **Adapter-first rollout:** Kiro adapter (already present) is the reference; other executors added append-only.
- **Reversible:** each wave is an isolated commit; `git revert` restores. No frozen artifact is touched, so rollback is loss-free.
- **EC-3 coexistence:** AEOS spine work runs in its own lane; it does not block or alter the in-flight EC-3 Band 10 realization (they compose, since AEOS would *drive* EC-3 capabilities once available).

---

## DELIVERABLE 22 — RISK ANALYSIS

| ID | Risk | Impact | Mitigation |
|----|------|--------|-----------|
| RK-1 | Realizing CIOA/CCE re-implements (duplicates) engine judgment | Violates RULE-001/004 | Enforce "defer/aggregate only" (CCE-LAW-005): gates call engines by reference; add zero new checks |
| RK-2 | New store created for events/twin | Violates CIOA-LAW-001 | Read-time unification only; append via existing stores |
| RK-3 | Spine acquires authority | Violates authority-neutrality | AUTHORITY=NONE, ENGINEERING-EXECUTION-ONLY; sequences, never authorizes |
| RK-4 | Frozen/engine/platform mutation | Breaks certification | frozen_paths guard + git orchestrator refuse; additive module only |
| RK-5 | MCP-002 divergence (hand-edit vs realized CIOA) | State drift | Make MCP-002 §05 a generated projection |
| RK-6 | Non-deterministic orchestration determination | Breaks reproducibility | Pure function of evidence; byte-stable ids (CIOA-LAW-008) |
| RK-7 | Auto-register hook treats spine/analysis docs as corpus | Unintended registration | Place code in non-corpus module; keep determination in `adr/` |
| RK-8 | Constitutional finality still BLOCKED (DR-RAT-11) | No formal ratification | Engineering realization is decoupled (finality-only); disclose provisional state |
| RK-9 | Lease/concurrency added where none existed | New failure mode | Keep single-active-capability default (MCS contract); leases optional/opt-in |

---

## DELIVERABLE 23 — CONSTITUTIONAL COMPLIANCE REPORT

| Rule | Compliance |
|------|:----------:|
| RULE-001 Never recreate certified capability | ✓ — all engines REUSE/COMPOSE; zero recreation |
| RULE-002 Never replace constitutional engine | ✓ — replacement prohibited for every RC-* |
| RULE-003 Never fork a subsystem | ✓ — no fork; adapters/spine are additive |
| RULE-004 Prefer composition | ✓ — AEOS ≈90% composition |
| RULE-005 Prefer orchestration over duplication | ✓ — only read-time unification (D-3), no store duplication |
| RULE-006 Repo knowledge precedes prompt | ✓ — determination derived from repo, not assumptions |
| RULE-007 Repository determines architecture | ✓ — spine shape dictated by existing CIOA/CCE/engines |
| RULE-008 Determine, don't ask | ✓ — proceeded autonomously |
| PROHIBITED: code/engines/stubs/duplication/replace/runtime/governance/constitutional/frozen edits | ✓ — none performed; this package is analysis only |
| MCS invariants I-R2/I-R3/I-G1/I-G2/I-A1/I-I1 | ✓ — no frozen/engine/platform writes; no new authority; no new ID system; one canonical instance per concern; twin as output |

**Determination is constitutionally clean.**

---

## DELIVERABLE 24 — RECOMMENDATION REPORT

1. **Adopt the Execution Spine as the single AEOS-new subsystem.** Everything else is reuse. Do not create new capability engines.
2. **Realize CIOA and CCE as composition runtimes** (Waves W1–W2) — they are the highest-value gap because their specs are complete and their dependencies are all certified/present.
3. **Unify events at read-time; never create a new store.** Extend the existing `twin.json` for the execution twin.
4. **Make MCP-002 "Next Authorized Capability" a generated projection of realized CIOA** to eliminate the only state duplication.
5. **Define one Executor Port; add thin adapters** (Kiro exists as reference) so any AI/human/CI executor plugs in without modifying the OS.
6. **Keep AUTHORITY=NONE end-to-end**: the spine sequences and validates; it authorizes nothing; constitutional finality (DR-RAT-11) remains exogenous.
7. **Sequence exactly per Deliverable 20**, CCE-gated and additive-only, in a new non-corpus module (`aeos/`), one commit per capability.
8. **Do not begin implementation** — this is a Phase-1 determination. Implementation requires a separate authorized program (CIOA/lane authority + GOV-004).

---

## SUCCESS-CRITERIA VERIFICATION

- Every existing capability discovered ✓ (Deliverables 1–4)
- Every certified subsystem cataloged ✓ (Deliverable 4)
- Every reusable engine identified ✓ (Deliverables 4–5)
- Every duplication resolved ✓ (Deliverable 6 — one read-time unification; no obsolete duplication)
- Every missing orchestration component identified ✓ (Deliverables 7–9)
- Complete AEOS architecture determined ✓ (Deliverables 9–19)
- Deterministic implementation roadmap exists ✓ (Deliverable 20)
- Future implementation can proceed without architectural ambiguity ✓

**STOP — architectural determination complete. Implementation NOT begun (per mission).**

*END OF ARTIFACT — AEOS-001 PHASE-1 DETERMINATION · ADVISORY · AUTHORITY = NONE (DERIVED TRUTH)*
