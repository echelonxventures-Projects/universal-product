# UCOS Ω∞ — CONSTITUTIONAL IMPLEMENTATION ORCHESTRATION AUTHORITY

| Field | Value |
|-------|-------|
| ARTIFACT ID | UCOS-COMP-000000 |
| ARTIFACT | Constitutional Implementation Orchestration Authority (CIOA) — Constitution |
| PROGRAM | UCOS Ω∞ Architecture Knowledge Program |
| PACKAGE | Completeness Governance Package |
| CLASSIFICATION | Foundational Architecture-Governance Artifact — Permanent Implementation-Orchestration Rules |
| STATUS | ACTIVE |
| CONSTITUENT AUTHORITY | NONE |
| GOVERNANCE AUTHORITY | NONE |
| RATIFICATION AUTHORITY | NONE |
| EC-1 AUTHORITY | NONE |
| HELD AUTHORITY | ENGINEERING-EXECUTION-ONLY |
| DEPENDS-ON (immutable) | UCOS-COMP-000001 (Constitutional Completeness Engine) |
| BASELINE DATE | 2026-07-17 |

*This artifact establishes the permanent implementation-orchestration rules that bind every repository-wide "what happens next" determination across the UCOS Ω∞ ecosystem. It is an **engineering-governance and orchestration instrument only**. The word "Constitution" here denotes a binding orchestration rule-set — it is **not** the constitutional corpus, creates no constituent/governance/ratification authority, and authorizes no EC-series step. CIOA **invents no new engine, no new state store, and no new corpus**: it consumes the Constitutional Completeness Engine (UCOS-COMP-000001) and the existing state/execution/dependency ecosystem **by reference only** and derives the repository-wide implementation sequence from repository evidence. It **SHALL NOT** modify UCOS-COMP-000001, which is treated as an immutable dependency. All rules herein are subordinate to, and must not contradict, the frozen constitutional corpus, its adjudicated determinations, the Technology Constitution (58 principles), the Implementation Governance Baseline, ARCH-GOV-001, STATUS-001, REG-AUTO-001, and UCOS-COMP-000001. Where a rule herein conflicts with any higher instrument, the higher instrument governs and this rule is void to the extent of the conflict.*

---

## MISSION

The Constitutional Completeness Engine (UCOS-COMP-000001 / CCE) answers **"Is it complete?"**. It does not answer **"What should happen next?"**. That is the remaining architectural gap.

The Constitutional Implementation Orchestration Authority (CIOA) is the **single authoritative repository-wide implementation determination authority**. It continuously determines — from repository evidence only, deterministically, fail-closed:

> **Where are we, what is next, why, what can run in parallel, what must never run yet, and how far are we from completion.**

CIOA performs **no completeness, coverage, validation, certification, readiness, dependency, gap, or traceability computation itself**. Those exist and are unified by CCE. CIOA **orchestrates** their outputs plus the existing state, registration, dependency-graph, and control-tower evidence into one repository-wide **implementation sequence and forecast**.

---

## PURPOSE

CIOA provides a single, evidence-derived answer to the core question set:

WHERE ARE WE? · WHAT IS COMPLETE? · WHAT IS INCOMPLETE? · WHAT IS BLOCKED? · WHAT IS FROZEN? · WHAT IS ACTIVE? · WHAT IS NEXT? · WHY IS IT NEXT? · WHAT IS THE CRITICAL PATH? · WHAT CAN RUN IN PARALLEL? · WHAT MUST NEVER RUN YET? · HOW FAR ARE WE FROM COMPLETION?

Every answer is **derived, never invented**, by aggregating existing certified engines and existing evidence registries. CIOA adds no new judgment about state, completeness, or readiness; it sequences the judgments the existing systems already make.

---

## AUTHORITY

| Authority type | Held by CIOA |
|----------------|-------------|
| Constituent / Governance / Ratification / EC-series | NONE |
| Engineering-execution authority | **Implementation-orchestration determination only** |

CIOA holds exactly one power: to issue a fail-closed **implementation-orchestration determination** (current state → next state → sequence → forecast) over the repository by aggregating existing evidence. It records **engineering readiness and sequence only** (`ENGINEERING-EXECUTION-ONLY`). It authorizes no work, ratifies nothing, and confers no constitutional finality (DE-05 / IP-01). The constitutional external gates EC-1…EC-6 remain open.

CIOA **SHALL NOT**:

- modify UCOS-COMP-000001 (immutable dependency) or any existing engine, standard, registry, or determination;
- duplicate Coverage, Validation, Certification, Readiness, Dependency-Closure, Governance-Compliance, Gap-Detection, Traceability, or Completeness — all already exist and are unified by CCE;
- create a new state store, status generator, registration mechanism, or dependency graph — STATUS-001, REG-AUTO-001, `control-tower.json`, and the Depends-On DAG already provide these;
- declare any critical path, next artifact, or sequence **manually** — every such determination SHALL be dependency-derived from repository evidence;
- write to the frozen corpus (`00-SOURCE/`, `99-FREEZE/`, `00-BOOK/*` canon — read-only, DP-03) or hand-edit any generated register.

---

## SCOPE

### In scope
- Repository-wide unification of existing state, completeness, dependency, and registration evidence into one implementation-orchestration determination.
- Dependency-derived critical path, parallelization groups, execution sequence, next-artifact identification, and evidence-based forecast.
- Fail-closed determination of BLOCKED / FROZEN / ACTIVE / NEXT / NEVER-YET across artifacts, programs, universes, capabilities, and components.

### Out of scope
- Any net-new completeness, coverage, validation, certification, readiness, dependency, gap, or traceability computation.
- Any change to STATUS-001 domains, REG-AUTO-001 lifecycle, control-tower dimensions, the dependency DAG, or CCE.
- Any authorization, ratification, or enactment of work. CIOA determines sequence; it does not start work.

---

## ORCHESTRATION AUTHORITY CHAIN

CIOA is the terminal orchestration node. It **consumes, by reference only**:

```
Frozen Corpus / Technology Constitution / IMP-000 / ARCH-GOV-001
        │
        ├── STATUS-001            status domains A–E · non-projection law   → State Model
        ├── REG-AUTO-001          registration binding · 7 registers · lifecycle → Artifact State Model
        ├── STATUS-REG-001        Master Execution Status Registry (evidence-derived) → Repository State
        ├── control-tower.json    program rollups · 14 dimensions           → Program State / Forecast
        ├── twin.json/signals.json  append-only signal ledger               → Implementation State
        ├── artifacts.json        append-only artifact registry (per-artifact status) → Artifact registry
        ├── Depends-On DAG        UKB-ADV-017 + ukb.py edges (acyclic, C-07) → Critical Path / Parallelization
        ├── GOV-INT-001           sequence + next-artifact method (governance scope) → Next-Artifact method
        ├── Readiness / Completion / Freeze determinations                  → Readiness / Frozen State
        └── UCOS-COMP-000001 (CCE)  completeness determination (unifies coverage/validation/
              certification/readiness/dependency/gap/traceability)          → Completeness State
        │
        ▼
  UCOS-COMP-000000 — CONSTITUTIONAL IMPLEMENTATION ORCHESTRATION AUTHORITY
        (unify state · derive critical path · derive parallel groups ·
         determine next · forecast completion · sequence the repository)
```

CIOA reads these; it replaces none of them.

---

## CONSTITUTIONAL ORCHESTRATION LAWS

| Law | Rule |
|-----|------|
| **CIOA-LAW-001 — Orchestrate, Never Reinvent** | Every determination SHALL be derived by consuming an existing engine, standard, registry, or determination by reference. CIOA creates no duplicate engine or state store. |
| **CIOA-LAW-002 — Evidence-Derived Only** | Every state, path, group, next-artifact, and forecast SHALL be a pure function of repository evidence (`artifacts.json`, `control-tower.json`, `twin.json`, the Depends-On DAG, CCE determinations). No arbitrary estimate, no manual declaration. |
| **CIOA-LAW-003 — Completeness Deferral** | Any "is it complete / ready / certified / covered / validated" question SHALL be answered by CCE (UCOS-COMP-000001). CIOA never re-derives completeness. |
| **CIOA-LAW-004 — Dependency-Derived Sequence** | The critical path, parallel groups, and execution sequence SHALL be derived from the acyclic Depends-On graph. Manual sequencing is void. |
| **CIOA-LAW-005 — Fail-Closed** | Missing evidence, an unresolved dependency, a broken DAG, a non-deterministic recompute, or an open CCE gate yields **BLOCKED / NOT-READY / NOT-NEXT**. CIOA never defaults an artifact to runnable. |
| **CIOA-LAW-006 — Freeze Supremacy** | Any artifact under a valid freeze (`99-FREEZE/`, program freeze determination) is **FROZEN** and SHALL NOT be sequenced, forecast as remaining work, or placed on any active path. |
| **CIOA-LAW-007 — Non-Projection Preserved** | CIOA SHALL preserve the STATUS-001 non-projection law: a status in one domain never implies another. Orchestration state is an explicit tuple across domains, never a single merged percentage across domains. |
| **CIOA-LAW-008 — Determinism & Reproducibility** | Identical evidence yields a byte-identical orchestration determination and a stable determination id (idempotent, per REG-AUTO-001 P3 / IMP-007 §5). |
| **CIOA-LAW-009 — Append-Only, Read-Only Corpus** | CIOA registries are append-only, evidence-derived projections. CIOA writes nothing to the frozen corpus and hand-edits no generated register (REG-AUTO-001 P2). |
| **CIOA-LAW-010 — Sequence, Not Authorization** | CIOA determines what *should* happen next; it authorizes, ratifies, and starts nothing. It fabricates no authority (AUTH-06, AI-01). |

---

## MANDATORY DETERMINATION DOMAINS

CIOA produces authoritative determinations for fifteen domains. Each resolves to an existing source; only the sequencing/derivation is CIOA's.

| # | Determination domain | Authoritative source (existing) | CIOA role |
|---|----------------------|--------------------------------|-----------|
| 1 | Repository State | STATUS-REG-001 + `artifacts.json` | aggregate |
| 2 | Program State | `control-tower.json` rollups | aggregate |
| 3 | Artifact State | REG-AUTO-001 lifecycle + `artifacts.json` | aggregate |
| 4 | Implementation State | `twin.json` / `signals.json` (STATUS-001 DOMAIN-C) | aggregate |
| 5 | Dependency State | Depends-On DAG (UKB-ADV-017 / ukb.py) | aggregate |
| 6 | Readiness State | Readiness determinations + `evaluate_readiness` (via CCE) | defer |
| 7 | Certification State | Certification Engine + ledger (via CCE) | defer |
| 8 | Completeness State | **UCOS-COMP-000001 (CCE)** | defer |
| 9 | Gap State | Coverage gaps + ARCH-GOV-001 LAW 003 (via CCE) | defer |
| 10 | Blocker State | Unresolved Depends-On edges + CCE open gates | **derive** |
| 11 | Critical Path State | Longest path over the Depends-On DAG | **derive** |
| 12 | Parallelization State | Topological antichains over the DAG | **derive** |
| 13 | Execution State | Topological order over ready/unblocked/unfrozen nodes | **derive** |
| 14 | Forecast State | `control-tower.json` rollups + remaining critical-path length | **derive** |
| 15 | Completion State | Completion determinations + CCE COMPLETE verdict | aggregate |

"defer" = answered wholly by an existing engine; "aggregate" = read + unify existing evidence; "derive" = the genuinely new dependency-derived orchestration.

---

## MANDATORY STATE MODELS

Each model defines Purpose · Inputs · Outputs · State Definitions · Transitions · Evidence · Failure Conditions. All inputs are existing evidence; no model introduces a new store.

### 1. Repository State Model
- **Purpose:** one repository-wide execution-state snapshot.
- **Inputs:** STATUS-REG-001, `artifacts.json`, `control-tower.json`.
- **Outputs:** counts by state; per-program rollup; repository completion tuple (per STATUS-001 domain).
- **States:** derived aggregate of artifact states (below).
- **Transitions:** re-derived on any evidence change (idempotent).
- **Evidence:** the generated registers (never hand-authored).
- **Failure:** stale/missing evidence → repository state = INDETERMINATE (fail-closed), Gap Report emitted.

### 2. Program State Model
- **Purpose:** state of each program (Engineering, Runtime, Platform, Data, Service, Application, Infrastructure, ADV, etc.).
- **Inputs:** `control-tower.json` program rollups; program readiness/completion/freeze determinations.
- **Outputs:** `{program, domain-tuple, blocked?, frozen?, active?, completion%}`.
- **States:** PLANNED · ACTIVE · READY · COMPLETE · CERTIFIED · FROZEN · BLOCKED.
- **Transitions:** governed by the underlying determinations; CIOA reflects, never sets.
- **Evidence:** rollup + determination citations.
- **Failure:** program with no resolvable rollup → BLOCKED (indeterminate).

### 3. Artifact State Model
See **Mandatory Artifact States** below. Purpose: per-artifact orchestration state. Inputs: filesystem existence (REG-AUTO-001 P2), `artifacts.json`, STATUS-001 domain, CCE completeness, certification ledger, freeze set, Depends-On edges. Outputs: one state + evidence per artifact. Failure: any missing mandatory evidence → BLOCKED.

### 4. Execution State Model
- **Purpose:** determine what may execute now.
- **Inputs:** Artifact states + Depends-On DAG + freeze set.
- **Outputs:** Execution Queue (topologically ordered ready set); Deferred set; Never-Yet set.
- **States:** RUNNABLE · DEFERRED · NEVER-YET · FROZEN.
- **Transitions:** an artifact becomes RUNNABLE iff all Depends-On predecessors are COMPLETE/CERTIFIED, it is not FROZEN, and no CCE gate blocks it.
- **Evidence:** predecessor states + DAG edges.
- **Failure:** any unresolved predecessor → DEFERRED (never RUNNABLE).

### 5. Dependency State Model
- **Purpose:** resolved vs unresolved dependencies per node.
- **Inputs:** Depends-On DAG (acyclic, C-07); CCE dependency-closure result.
- **Outputs:** `{node, unresolved_predecessors[], resolved?}`.
- **States:** RESOLVED · UNRESOLVED · CYCLIC(defect).
- **Transitions:** resolved when every predecessor is COMPLETE/CERTIFIED.
- **Evidence:** edge list + predecessor states.
- **Failure:** any cycle → CYCLIC defect → fail-closed halt (contradicts C-07).

### 6. Critical Path Model
- **Purpose:** the dependency-derived longest path to repository completion.
- **Inputs:** Depends-On DAG; per-node remaining-work weight from `control-tower.json`.
- **Outputs:** ordered critical path; slack per node; non-critical/parallel/optional/frozen/blocked/completed paths.
- **States:** CRITICAL · NON-CRITICAL · PARALLEL · OPTIONAL · FROZEN · BLOCKED · COMPLETED.
- **Transitions:** recomputed on any state/edge change.
- **Evidence:** DAG + weights. **No manual declaration** (CIOA-LAW-004).
- **Failure:** broken/cyclic DAG → no path emitted; fail-closed.

### 7. Parallelization Model
- **Purpose:** dependency-safe simultaneous-execution groups.
- **Inputs:** Depends-On DAG; Execution Queue.
- **Outputs:** ordered antichain groups (each group = mutually independent RUNNABLE nodes).
- **States:** per group PARALLEL-SAFE.
- **Transitions:** a node joins the current group iff it shares no ancestor/descendant edge with any group member and is RUNNABLE.
- **Evidence:** transitive-closure independence proof over the DAG.
- **Failure:** any shared dependency → nodes placed in different groups (never co-scheduled).

### 8. Forecast Model
- **Purpose:** evidence-derived completion forecast.
- **Inputs:** `control-tower.json` completion rollups; remaining critical-path length; remaining-work counts from `artifacts.json`.
- **Outputs:** current completion %, program completion %, repository completion %, remaining work, execution forecast (in critical-path units), risk forecast (blocker count × critical-path impact).
- **States:** ON-PATH · AT-RISK · BLOCKED.
- **Transitions:** re-derived on evidence change.
- **Evidence:** rollup values + path length. **No arbitrary estimate** (CIOA-LAW-002).
- **Failure:** missing rollup → forecast = INDETERMINATE.

### 9. Blocker Model
See **Mandatory Blocker Authority** below.

### 10. Completion Model
- **Purpose:** whether a program/repository is complete.
- **Inputs:** Completion determinations; CCE COMPLETE verdict; freeze determinations.
- **Outputs:** `{scope, complete?, certified?, frozen?, evidence}`.
- **States:** INCOMPLETE · COMPLETE · CERTIFIED · FROZEN.
- **Transitions:** COMPLETE only when CCE returns COMPLETE and a completion determination exists.
- **Evidence:** CCE determination id + completion determination citation.
- **Failure:** absent CCE COMPLETE → INCOMPLETE (fail-closed).

---

## MANDATORY ARTIFACT STATES

Each state is derived from existing evidence; CIOA sets no state by hand. `REG-AUTO-001` governs registration; STATUS-001 governs status validity; CCE governs completeness/certification; the freeze set governs FROZEN; the DAG governs BLOCKED.

| State | Entry Criteria | Exit Criteria | Evidence | Transition Rule |
|-------|----------------|---------------|----------|-----------------|
| PROPOSED | Named in a determination/roadmap; not yet on disk | File created on disk | roadmap/determination citation | → REGISTERED on creation (REG-AUTO-001 P1) |
| REGISTERED | Exists on disk AND all 7 registers reflect it | Predecessors resolved | `artifacts.json` entry | → READY when Depends-On predecessors COMPLETE |
| READY | Registered + all predecessors COMPLETE/CERTIFIED + not frozen | Work begins (signal) | DAG predecessor states | → ACTIVE / IN_PROGRESS on first work signal |
| ACTIVE | On an active path; work authorized elsewhere | — | control-tower/twin signals | → IN_PROGRESS |
| IN_PROGRESS | Build/test signals present, not yet complete (DOMAIN-C) | Completeness proven | `twin.json` build/test signals | → COMPLETE when CCE COMPLETE |
| COMPLETE | CCE returns COMPLETE for the artifact | Certification | CCE determination id | → CERTIFIED when certification recorded |
| CERTIFIED | Certification Engine record CERTIFIED + ledgered | — | certification ledger entry | → FROZEN if a freeze determination is issued |
| FROZEN | Under a valid freeze (`99-FREEZE`/program freeze) | Freeze lifted (never, absent new determination) | freeze determination + SOURCE-HASHES | terminal for sequencing (CIOA-LAW-006) |
| BLOCKED | ≥1 unresolved predecessor OR ≥1 open CCE gate | Blocker resolved | unresolved edge / open-gate evidence | → READY when all blockers clear |
| SUPERSEDED | A successor determination replaces it | — | successor citation | excluded from remaining work |
| DEPRECATED | Marked deprecated by a determination | — | deprecation citation | excluded from active paths |
| RETIRED | Removed from active scope by determination | — | retirement citation | terminal; excluded from forecast |

State is an **explicit tuple** across STATUS-001 domains (non-projection, CIOA-LAW-007); the single label above is the orchestration roll-up for sequencing only.

---

## MANDATORY COMPLETION STATES (COMPLETION ROLL-UP)

The twelve artifact states above are the fine-grained lifecycle. For repository-, program-, and completion-forecast roll-ups, CIOA projects them onto the **nine mandatory completion states** below. Each is a derived roll-up over the artifact-state model + CCE verdict + freeze set; CIOA computes none by hand. Every state defines Entry Criteria, Exit Criteria, Evidence, and Certification Impact.

| Completion state | Projects from (artifact states) | Entry criteria | Exit criteria | Evidence | Certification impact |
|------------------|--------------------------------|----------------|---------------|----------|----------------------|
| **NOT_STARTED** | PROPOSED, REGISTERED | Defined/registered but no build/test signal and no realized package | First IN_PROGRESS signal | roadmap/determination citation; `artifacts.json` entry with no DOMAIN-C signal | None; ineligible for certification |
| **IN_PROGRESS** | ACTIVE, IN_PROGRESS | Build/test signals present (STATUS-001 DOMAIN-C); not yet complete | CCE returns COMPLETE | `twin.json`/`signals.json` build/test signals | None until COMPLETE |
| **PARTIALLY_COMPLETE** | (composite roll-up: program/wave/band/universe) | Some members COMPLETE and some not | All members COMPLETE | member completion reports (subset) + open members | Partial; composite not certifiable until all members complete |
| **COMPLETE** | COMPLETE | CCE returns COMPLETE for the unit | Certification recorded | CCE determination id + realized package + completion report | Eligible for certification; feeds CCE gate inputs |
| **CERTIFIED** | CERTIFIED | Certification Engine record CERTIFIED + ledgered; CCE gates closed | Regression (revoked) or supersession | certification ledger entry / tag; CCE record | Certified; may satisfy downstream certification gates |
| **FROZEN** | FROZEN | Under a valid freeze (`99-FREEZE/`, program freeze) | Formal unfreeze (governed; outside CIOA) | freeze determination + SOURCE-HASHES | Certification fixed; no re-derivation (DP-03); excluded from remaining-work forecast |
| **BLOCKED** | BLOCKED | ≥1 unresolved Depends-On predecessor OR ≥1 open CCE gate | All blockers clear | unresolved edge / open-gate evidence | Ineligible until unblocked |
| **SUPERSEDED** | SUPERSEDED | A newer authoritative determination reconciles it forward (evidence-derived) | — (terminal; retained, not deleted) | successor "SUPERSEDES (informationally)" citation | Certification transfers to the superseding artifact |
| **DEPRECATED** | DEPRECATED, RETIRED | Retired from the active path by a determination | — (terminal) | deprecation/retirement citation | Certification withdrawn from the active roll-up |

**Roll-up rule (fail-closed).** A composite (program/wave/band/universe/repository) is COMPLETE only when every member is COMPLETE (or FROZEN/SUPERSEDED with a COMPLETE successor); CERTIFIED only when every certification-required member is CERTIFIED. A single BLOCKED or NOT_STARTED member holds the composite at PARTIALLY_COMPLETE / IN_PROGRESS. These nine states are the mandatory minimum; the twelve artifact states remain the underlying lifecycle they project from.

---

## MANDATORY BLOCKER AUTHORITY

CIOA determines blocked Artifacts · Programs · Universes · Capabilities · Components. For every blocker it records:

| Field | Source |
|-------|--------|
| Cause | unresolved Depends-On edge OR open CCE gate OR missing evidence |
| Dependency | the specific unresolved predecessor node/edge |
| Evidence | DAG edge citation + predecessor state + CCE gate id |
| Resolution Path | the predecessor(s) that must reach COMPLETE/CERTIFIED |
| Priority | critical-path impact (blockers on the critical path rank highest) |
| Critical Path Impact | whether the blocked node lies on the derived critical path |

A blocker is **evidence-derived**; CIOA declares none manually. Fail-closed: if a dependency cannot be resolved to evidence, the node is BLOCKED.

---

## MANDATORY CRITICAL PATH AUTHORITY

CIOA derives, from the acyclic Depends-On graph only (CIOA-LAW-004):

Critical Path · Non-Critical Path · Parallel Path · Optional Path · Frozen Path · Blocked Path · Completed Path.

The **critical path** is the longest dependency-weighted path from the current frontier to repository completion. Node weight = remaining work from `control-tower.json`. Completed and frozen nodes carry zero remaining weight. **No manual declaration is permitted**; a broken or cyclic graph yields no path (fail-closed).

---

## MANDATORY PARALLELIZATION AUTHORITY

CIOA derives dependency-safe execution groups — artifacts, programs, universes, capabilities, and components that may execute simultaneously. A group is a **topological antichain**: a maximal set of RUNNABLE nodes that are pairwise independent in the Depends-On transitive closure. Evidence required per group: the independence proof (no shared ancestor/descendant edge) and the RUNNABLE state of every member. Any shared dependency forces members into different groups (never co-scheduled).

---

## MANDATORY NEXT-ARTIFACT AUTHORITY

CIOA determines the Next Required Artifact · Program · Universe · Capability · Component, generalizing the GOV-INT-001 next-artifact method from governance scope to the whole repository. For each determination it provides:

| Field | Basis |
|-------|-------|
| Why | position on the critical path + unblocks the most downstream work |
| Dependencies | Depends-On predecessors (all must be COMPLETE/CERTIFIED) |
| Evidence | DAG edges + predecessor states + CCE readiness |
| Priority | critical-path rank |
| Critical Path Status | on / off the derived critical path |
| Readiness Status | CCE readiness (Gate 8) for the candidate |
| Certification Impact | which downstream certification the artifact unblocks |

The next artifact is the highest-priority RUNNABLE node on the critical path. If none is RUNNABLE, CIOA returns the highest-priority blocker's resolution path instead (fail-closed: it never invents a runnable artifact).

---

## MANDATORY FORECAST AUTHORITY

CIOA determines Current / Program / Repository / Forecast Completion %, Remaining Work, Execution Forecast, and Risk Forecast — all evidence-derived from `control-tower.json` rollups and remaining critical-path length. **No arbitrary estimate** is permitted (CIOA-LAW-002). Forecasts preserve STATUS-001 non-projection: completion is reported per domain, never as a single cross-domain merged figure (CIOA-LAW-007).

---

## MANDATORY REGISTRIES (REGISTRY MODEL)

CIOA defines seven registries as **append-only, evidence-derived projections** — not new persistent stores (honoring STATUS-REG-001 §0 anti-duplication and REG-AUTO-001 P2). Each is re-derived deterministically from repository evidence and reuses the append-only, content-addressed record + ledger pattern of `engine/certification/ledger.py`.

| Registry | Derived from | Nature |
|----------|--------------|--------|
| Implementation State Registry | `artifacts.json` + STATUS-001 domains + CCE | projection |
| Blocker Registry | Depends-On DAG + open CCE gates | projection |
| Critical Path Registry | Depends-On DAG + rollup weights | projection |
| Execution Queue Registry | RUNNABLE set (topological order) | projection |
| Next Artifact Registry | critical-path RUNNABLE frontier | projection |
| Forecast Registry | control-tower rollups + path length | projection |
| Repository State Registry | STATUS-REG-001 aggregate | projection |

All are append-only and evidence-backed; none is hand-authored; none duplicates the machine source of truth (`artifacts.json`/`control-tower.json`/`twin.json`).

---

## DETERMINATION MODEL

1. CIOA reads repository evidence (registers, DAG, CCE determinations) — no new computation.
2. It computes each artifact's orchestration state tuple (aggregate/defer).
3. It derives the critical path, parallel groups, execution queue, next artifact, and forecast (the four NEW derivation authorities) over the acyclic DAG.
4. It aggregates these into a single fail-closed **Implementation-Orchestration Determination Record** — content-addressed, append-only, deterministic, reproducible — carrying the EC-1 provisional-state disclosure and `ENGINEERING-EXECUTION-ONLY` authority.
5. Any missing evidence, cyclic graph, or open CCE gate yields BLOCKED/INDETERMINATE and a Gap Report (ARCH-GOV-001 LAW 003); CIOA emits no speculative sequence.

---

## FAILURE CONDITIONS

A CIOA determination FAILS (INDETERMINATE / fail-closed) when: evidence is missing or stale; the Depends-On graph is broken or cyclic (contradicts C-07); a recompute is non-deterministic; a CCE gate required for a state is open; a freeze is disregarded; or any state/path/forecast would require a manual declaration or arbitrary estimate. A failed determination emits a Gap Report and halts the affected sequence; it emits no partial or speculative orchestration.

---

## SUCCESS CRITERIA

After establishment, CIOA can answer — from existing repository evidence and existing engines — every core question: what exists · what is complete/incomplete/blocked/frozen/active · what is next and why · what can run in parallel · what is the critical path · how much work remains · the completion forecast · and the authoritative implementation sequence. It does so with **zero new engines**, **zero new state stores**, and **zero duplication** of CCE or any unified capability.

---

## AUTHORITY BOUNDARY (MANDATORY)

Notwithstanding any rule above, this constitution and every actor under it:

- hold **no** constituent, governance, ratification, or EC-series authority and cannot authorize EC-1;
- treat `00-SOURCE/`, `99-FREEZE/`, `00-BOOK/*` canon, and all constitutional/EES determinations as **read-only** (DP-03, C-01);
- treat **UCOS-COMP-000001 as an immutable dependency** and consume it and every existing engine/standard/registry **by reference only** — modifying, forking, or weakening none;
- derive every determination from evidence, never by manual declaration or arbitrary estimate;
- never fabricate, assume, or simulate authority (AUTH-06, AI-01).

Any orchestration action that would breach this boundary is void and must be escalated as a boundary breach.

---

## REGISTRY UPDATE

| Attribute | Value |
|-----------|-------|
| Register | UCOS-COMP-000000 — Constitutional Implementation Orchestration Authority (Constitution) |
| Program | UCOS Ω∞ Architecture Knowledge Program |
| Status | ACTIVE |
| Immutable dependency | UCOS-COMP-000001 (Constitutional Completeness Engine) |
| Companion artifact | `06-IMPLEMENTATION/UCOS-COMP-000000-CONSTITUTIONAL-IMPLEMENTATION-ORCHESTRATION-AUTHORITY-IMPLEMENTATION.md` |

---

## CERTIFICATION

| Attribute | Value |
|-----------|-------|
| Artifact Status | ACTIVE — permanent implementation-orchestration rules established |
| Orchestration Laws | 10 (CIOA-LAW-001…010) |
| Determination Domains | 15 |
| State Models | 10 |
| Artifact States | 12 |
| Completion States (roll-up, mission-mandated) | 9 (NOT_STARTED…DEPRECATED) |
| New engines created | 0 |
| New state stores created | 0 |
| CCE modified | NO (immutable dependency) |
| Authority | NONE (subordinate to the constitutional corpus, IMP-000, ARCH-GOV-001, STATUS-001, REG-AUTO-001, UCOS-COMP-000001) |
| Held Authority | ENGINEERING-EXECUTION-ONLY |
| Scope | IMPLEMENTATION-ORCHESTRATION DETERMINATION ONLY |

This artifact creates no authority, alters no determination, authorizes no EC-series step, invents no engine or state store, and duplicates no capability. It constitutionalizes the repository-wide implementation-orchestration determination as the single authority answering "what happens next," built entirely by orchestration of existing evidence and engines — CCE foremost among them, consumed by reference and never modified.
