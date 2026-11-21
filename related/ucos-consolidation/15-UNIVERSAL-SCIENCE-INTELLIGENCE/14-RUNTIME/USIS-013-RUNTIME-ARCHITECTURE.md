# USIS-013 — Runtime Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-013 (Runtime Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000013` (next free after `UCOS-USIS-000012` = USIS-011). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Runtime Architecture (EVO-USIS-013) — establish the constitutional Runtime-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Runtime tier (governed execution host) owned by the substrate (subordinate to USIS-001, USIS-002, USIS-003, USIS-004, USIS-005, USIS-006, USIS-007, USIS-008, USIS-009, USIS-010, USIS-011, and to LAW Ω∞-000 / MIP Parts 19/20/21/22/32) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Runtime tier (USIS-004 tier 15) — hosts engine execution (on-demand + continuous) under governed autonomy; self-* gating |
| DEPENDS-ON | USIS-011 · USIS-004 · USIS-002 · `08-RUNTIME`/RIE (referenced) · Universe U26 / U28 (referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **15 (Runtime)** (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · MIP Part 21 (Learning) · Part 22/32 (Evolution) · Part 25 (Simulation, referenced); LAW USIS-06 (governed autonomy & self-evolution); LAW P21-001/002/003 |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/06/07/08/09) · USIS-004 (24-tier meta-model) · UCIC-001 · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the runtime-hosting mandate conferred by USIS-001 (LAW USIS-06 governed autonomy) and the USIS-004 Runtime tier, hosting the Engine tier (USIS-011) and referencing the platform runtime (`08-RUNTIME`/RIE) and simulation/evolution universes (U26/U28). Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Registered instantiation of the authorized operational-memory blueprint `00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-013-RUNTIME-ARCHITECTURE.md`, authorized by `00-MASTER/UCOS-USIS-WAVE2-AUTH/` (EVO-USIS-W2-AUTH-001 · Catalogue Entry 7 · AUTHORIZED). No new constitutional knowledge is introduced. Corrections vs the blueprint: (a) STATUS raised to "RATIFIED (PROVISIONAL) · registered"; (b) PARENT resolved to the program root (non-chained), dependency order carried by DEPENDS-ON; (c) VOL-024 canonical (`config.py`). Canonical home `15-…/14-RUNTIME/` per USIS-005 §2 (area 14 = RUNTIME) — no variance; no structure invented. |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The platform runtime (`08-RUNTIME`/RIE) and Simulation universe (U26) are **referenced**; the canonical home governs and this architecture holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Runtime tier** — the tier that hosts engine execution, on-demand and continuous, under governed autonomy. This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/14-RUNTIME/` home and defines the Runtime node shape, its execution semantics, lifecycle coordination, orchestration, state evolution, context propagation, and execution governance (the governed-autonomy and self-* bounds of LAW USIS-06) — while remaining independent of any technology, framework, infrastructure, or vendor and never duplicating the platform runtime. **This instrument establishes only the Runtime-tier architecture.** It authors **no** individual runtime binding or self-evolution instance — those are separately-authorized later (Wave-3/4) realizations.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the runtime-hosting mandate of USIS-001 and the Runtime tier (15) of the USIS-004 meta-model:

- **USIS-004 Part C tier 15** — Runtime (parent = Engine). USIS-013 is the constitutional architecture and rule-set for this tier.
- **USIS-001 LAW USIS-06 (governed autonomy & self-evolution)** — self-* capabilities and autonomous agents operate within governed bounds; self-modification is simulate-then-adopt and reversible-or-justified (Part 21).
- **USIS-001 LAW USIS-04** — the runtime is architecture, not technology: it names no scheduler/orchestrator/infrastructure; the platform runtime is referenced.
- **USIS-011 (Engine)** is hosted; **USIS-010/008/009/006/007** are reached through the engine, by reference. USIS-013 `Depends-On` Engine and **references** the platform runtime (`08-RUNTIME`/RIE), simulation (U26), and evolution (U28) — never duplicating their architecture (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-013).** This architecture:
- creates the `15-…/14-RUNTIME/` home and this single registered architecture artifact;
- defines the Runtime **node shape, ontology/taxonomy placement, execution lifecycle, context propagation, orchestration, state evolution, event coordination, execution governance, engine/pattern integration, registry model** (Parts B–L);
- founds downward-only on `USIS-011/004/002` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** runtime binding, self-evolution action, or agent instance, and begins **no** Wave-3/4 realization;
- reuses, without duplication, the platform runtime (`08-RUNTIME`/RIE), the Simulation universe (U26), the registration/validation/certification engines (`ukb`, `ukbx`, `register.sh`), UCIC-001, and the governance instruments — and performs **no** `config.py` edit (`^15-…/14-RUNTIME/` already classifies to USIS/VOL-024).

## PART B — Runtime architecture (the Runtime node)

A runtime is a typed node of the canonical form:

```
{ id: USIS-RUN-<NAME>, home: 14-RUNTIME/<NAME>/, tier: 15,
  hosts: <USIS-ENG-* engine>, mode: on-demand|continuous,
  governance_gate: <simulation+governance pre-effect gate>, self_star_policy,
  context_contract, state_contract, owner, status }
```

- The node is the meta-model parent of the Service tier (USIS-004): a service exposes a runtime-hosted capability.
- It is a **hosting + governance contract** — it binds an engine to an execution mode and fronts every self-* effect with a governance + simulation gate (LAW USIS-06). It embeds no scheduler and names no infrastructure (LAW USIS-04).
- Produces **no** code; the platform runtime executes, referenced (runtime independence, Part L).

## PART C — Runtime ontology (reference to USIS-005)

Every runtime is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares execution/autonomy concepts (execution mode, gate, self-* action, context, state) and their relations. Ontology Closure (obligation 11) governs. USIS-013 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Runtime taxonomy (reference to USIS-005)

Every runtime occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the runtime taxonomy of execution modes (on-demand / continuous) and autonomy classes (governed / simulate-then-adopt). Taxonomy Closure (obligation 12) governs. USIS-013 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Execution lifecycle & lifecycle coordination

A runtime node follows, under UCIC-001:

```
DEFINED → BOUND (engine + execution mode) → GOVERNED (autonomy envelope + gate set) → REGISTERED → EVOLVING
```

Runtime **coordinates the capability execution lifecycle** (the SCIENCE_INTELLIGENCE lifecycle DEFINED→GROUNDED→MODELED→REASONED→VALIDATED→CERTIFIED→EVOLVING) by hosting the engine that drives it — it does not redefine the lifecycle (UCIC-001 / USIS-006 own it; referenced). No stage skipped; defect-driven REOPEN only.

## PART F — Context propagation

The runtime defines a **context contract**: the provenance, authority, governing determination, and explanation context (LAW USIS-07) propagated into every engine invocation and emitted on every output. Context is carried by reference to the capability/evidence tiers; the runtime propagates, it does not own the context's canonical source.

## PART G — Runtime orchestration

The runtime **orchestrates hosting** of one or more engines under its execution mode, sequencing engine invocations and coordinating their resolved-registry execution. Orchestration of *pattern internals* is the engine's concern (USIS-011); the runtime orchestrates *engine hosting and mode*, not member resolution — no overlap (Zero-Overlap, obligation 3).

## PART H — State evolution & event coordination

- **State evolution.** The runtime defines a **state contract** for execution state; state transitions are governed and, for self-* effects, pass the simulation+governance gate before effect and are reversible-or-justified (LAW USIS-06 / P21-003). Self-evolution actions register in the Self-Evolution Registry, append-only.
- **Event coordination.** The runtime coordinates execution events (invocation, completion, gate outcome, drift signal) by reference to the observability/evidence surfaces; it emits, it does not own the event store.

## PART I — Execution governance (governed autonomy)

Every self-* pathway and autonomous action is **gated**: a governance + simulation gate fronts any effect (LAW USIS-06); no unbounded self-modification. Bounded autonomy is declared in the autonomy envelope; drift/hallucination/contradiction monitoring is declared by reference to Part 20 models. An ungated self-* pathway is non-certifiable (fail-closed).

## PART J — Pattern-execution & Engine integration

| Integration | Model (by reference) |
|-------------|----------------------|
| **Engine integration** | the runtime hosts an Engine (USIS-011) and binds it to an execution mode; the engine remains canonically owned by USIS-011 |
| **Pattern execution integration** | patterns (USIS-010) execute only when the runtime-hosted engine resolves and runs them; the runtime provides the execution context/mode, not the pattern semantics |

All integration is by **reference**; the runtime re-homes nothing (LAW USIS-02).

## PART K — Registry integration

- Runtime bindings are recorded in the **Execution Registry** (target #5, under the Universal Science & Intelligence stream) and the Architecture Registry (#10); self-evolution actions register in the program **Self-Evolution Registry** (`04-REGISTRIES/`), append-only, each carrying its governance + simulation gate outcome.
- Projection produced by the **reused** universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`); no parallel allocator/registry created (LAW USIS-02). Deterministic, metadata-classified (`UCOS-PROGRAM=USIS`, `VOL-024`); append-only (CR-INF-007; obligations 7/20).

## PART L — Dependency model & Runtime independence

- **Dependency model.** `Depends-On` runs downward to `USIS-011/004/002` and references `08-RUNTIME`/RIE, U26, U28; `Parent` is the program root (non-chained). No forward reference (obligation 14). Acyclic, downward-only (obligation 5). USIS-012 (Service) `Depends-On` this tier — Runtime founds Service; the higher catalog number of Service (012 vs 013) is a numbering-index artifact, not a cycle.
- **Runtime independence.** The Runtime tier is architecture: it defines execution *semantics and governance*, not a concrete scheduler/orchestrator/infrastructure. Execution occurs on the platform runtime (`08-RUNTIME`/RIE), referenced never embedded. The runtime architecture is fully defined independent of technology, framework, infrastructure, or vendor.

## PART M — Validation model

Discharged by USIS-014 (referenced): a runtime is valid only if **every self-* pathway is gated** (no ungoverned autonomy), the **governed-autonomy envelope** is declared, and **explanation coverage** of runtime decisions is present (LAW USIS-07). Drift/hallucination/contradiction monitoring is declared (Part 20, referenced).

## PART N — Certification model

Discharged by USIS-015 (referenced): CCE 10 fail-closed gates PASS, certifier ≠ executor (SoD). Certification confirms **bounded autonomy** (no unbounded self-modification), **reversibility-or-justification** of self-* effects, and **canonical ownership**. An ungated self-* pathway is non-certifiable.

## PART O — Evidence model

Discharged by USIS-016 (referenced) using UCIC-001 Output-5: execution traces, self-evolution gate outcomes (simulation result + governance decision), provenance/explanation traces (LAW USIS-07), and monitoring signals. Absence ⇒ NOT-DONE (TRACK-001).

## PART P — Reuse model

Reuse-First (LAW USIS-02): the platform runtime (`08-RUNTIME`), RIE twin, and Simulation universe (U26) are **referenced**, never re-homed. USIS runtime adds only the science-intelligence execution-mode and governed-autonomy specialization. Engine (USIS-011) and the tiers it reaches are referenced.

## PART Q — Runtime (constitutional) invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations).**
1. Duplicate runtime/scheduler created by USIS-013: **0** (LAW USIS-02).
2. Hard-coded present-day technology/infrastructure in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) runtime layers: **0** (LAW USIS-05, obligation 4).
4. Ungoverned self-* pathway (no simulation+governance gate): **0** (LAW USIS-06).
5. USIS-013 edits to any frozen instrument: **0** (obligation 19).
6. Runtime lacking a hosted engine or execution-mode binding: **0** (C-00.3).
7. Circular ownership / dependency cycles: **0** (obligation 5).
8. Duplication of Engine/Pattern/Model/Algorithm/Capability/Domain Architecture or platform runtime: **0** — referenced only (LAW USIS-02).

**Failure model (per UCIC-001 Output-4).**
- An ungoverned self-* effect ⇒ LAW USIS-06 violation ⇒ non-certifiable / blocked before effect.
- A duplicated runtime/scheduler ⇒ Zero-Duplication violation ⇒ reference the platform runtime.
- A self-* effect without a simulation gate ⇒ blocked before effect; rollback is reversal-or-justification.
- Absence of required evidence ⇒ NOT-DONE (TRACK-001). Authoritative history and frozen artifacts are never mutated on rollback.

## PART R — Non-goals

- Authors **no** runtime binding, scheduler, self-evolution action, or agent instance (Wave-3/4, per-member).
- Is **not** the platform runtime/scheduler (`08-RUNTIME`), the Simulation universe (U26), the Engine (USIS-011), or any upper tier — all referenced.
- Defines **no** service or API/SDK (owned by USIS-012/017).
- Permits **no** unbounded self-modification; names **no** technology/infrastructure/vendor (LAW USIS-04/06); creates **no** competing runtime (LAW USIS-02); produces **no** code (implementation independence).

---

*END — USIS-013 · RUNTIME ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
