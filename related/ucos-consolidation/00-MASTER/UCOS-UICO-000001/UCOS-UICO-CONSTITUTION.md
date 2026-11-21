# UCOS-UICO-000001 — Constitution

> **Artifact:** `UCOS-UICO-CONSTITUTION`
> **Programme:** UCOS-UICO-000001 — Universal Implementation Closure Orchestrator
> **CONSTITUENT AUTHORITY:** NONE
> **GOVERNANCE AUTHORITY:** NONE
> **RATIFICATION AUTHORITY:** NONE
> **EC-1 AUTHORITY:** NONE
> **AUTHORITY = NONE — DERIVED TRUTH**
> **CLASSIFICATION:** SUBSTANTIVE — therefore forbidden a namespace token in
> `00-CMG/CMG-REGISTRY.json` by CMG-000001 Art LXXVI.2(b), and it claims none.
> **Disposition:** COMPOSITION AND REPORTING PROJECTION ONLY.

---

## Article 0 — What this document is not

**This is not a constitution in the constitutive sense, and it is important to say so first.**

The steering that authorized this document also stated: *"This is NOT permission to create a new
authority."* A document that legislated would create one. So this instrument is a **charter and
disclosure** — the same form `uicm.json`'s `programme` block takes, and the same all-NONE authority
posture `SECURITY-001` and `UMB-015` declare.

It therefore:

- **legislates no lifecycle** — the lifecycle it names is a projection of `uckp.evolution-stage`;
- **mints no identifier** — no `UICO-*` identity scheme is created;
- **opens no registry** — none;
- **allocates no ownership** — every owner named here was already the owner;
- **creates no authority** — where this document and a located instrument differ, **the located
  instrument governs** and this document is void to the extent of the conflict.

Every conclusion recorded here is a **technical, non-constitutive** governance record.

## Article 1 — Purpose

To record, once, that **Universal Implementation Closure already exists as a distributed
constitutional capability**, and to name the composition by which its existing owners already
discharge it — so that no future programme mistakes the composition for a missing capability and
builds a fifth orchestrator.

## Article 2 — Disposition

| Question | Determination |
|---|---|
| Is UICO a new capability? | **NO** — all six permitted responsibilities are already owned |
| Is UICO an orchestration protocol? | **NO** — orchestration exists at four levels |
| What is UICO? | a **composition and reporting projection**, plus three EXTEND rows owned by UICM and UAUE |
| Disposition under CMG Art LXXVII.2 | **REUSE** for thirteen concerns, **COMPOSE** for two, **EXTEND** for three, **REJECT** for six, **CREATE** for none |

## Article 3 — What UICO may own

Exactly the six the steering permits, and each is held **as a projection over an existing owner**,
never as an independent faculty:

| # | Permitted | Held as | Existing owner it projects |
|---:|---|---|---|
| 1 | orchestration sequence | a *reading* of an existing order | UAUE AUE-P-01..11; `verify.sh` `run_stage`; `uccep-bindings.json` |
| 2 | closure workflow | a *coarse vocabulary* over declared stages | UICM `ClosureState`; UCIC-001 15 stages |
| 3 | dependency ordering | a *citation* of derived order | `engine/foundation/composition/ordering.derive_order` — the single ordering authority |
| 4 | implementation planning | a *reference* to located plans | UAUE AUE-P-03; UCDA `work_packages[]`; `platform/universal_master_plan` |
| 5 | progress coordination | a *projection* of measurements | UICM measurement report; UAKOS; RIE progress |
| 6 | measurement invocation | an *invocation*, never a measurement | `UicmController.run()` |

**UICO owns no state, no record and no verdict.** It may report; it may not decide.

## Article 4 — What UICO shall not own

Eight concerns, each with its located owner. This table is the operative prohibition.

| Concern | Canonical owner | UICO relationship |
|---|---|---|
| Identity | AIF `A/G-AUTH` (law) · UGA-001 (artifacts) · `id-ledger.json` `by_object` (sole sequence) | **READ** |
| Knowledge | UCKP-LAW-0001 · `engine/uckp/canonical.py` Layer Zero (Art-13) | **READ / DELEGATE** |
| Registry | `engine/registry/universal` (12 typed registries) · REG-AUTO-001 | **REFERENCE** |
| Security | SECURITY-001 (SL-0, USL-001..015) · `platform/security` (record-only) | **REFERENCE** |
| Certification | UCOS-EPIC-006 `engine/universal_certification` (T6), `OP-CERT-001` | **INVOKE** |
| Governance | CEP-002 Art 28 · UCDA-000001 · G-14 · CMG-000001 Art L | **REFERENCE** |
| Evidence | `EvidenceRegistry` · SECURITY-001 §16 | **REFERENCE** |
| Execution mutation | `engine/constitution/gateway.py` `UCOS-CMG-EXEC-000001` — sole clean `StateSeal` producer | **REFERENCE** |

## Article 5 — The closure lifecycle is a projection, not a new lifecycle

The ten states are admitted **only** as a reporting vocabulary over the fifteen canonical stages
declared by `engine/uckp/evolution.py::EvolutionStage` — the stage authority UAUE itself defers to,
*"read from this module rather than restated here, so this register cannot drift from the law it
claims to traverse."*

| UICO state | Meaning | UAUE phase | Canonical stage(s) | Bound gate |
|---|---|---|---|---|
| DISCOVERED | repository truth observed | AUE-P-01 | `observe` | `make rib-gate` |
| ASSIMILATED | context, dependencies, constraints, ownership understood | AUE-P-02 | `learn`, `impact-analysis`, `dependency-analysis` | `make ucl-gate` |
| OWNED | every required change has a canonical owner | AUE-P-03 | `authority-resolution` | `make uaep-gate` |
| PLANNED | execution sequence and dependencies deterministic | AUE-P-03 / P-04 | `reason`, `simulate` | `make uaep-gate` / `make final-closure-gate` |
| EXECUTED | owner performed the approved change | AUE-P-05 | `implementation` | `./verify.sh` |
| MEASURED | measurement observed the result | AUE-P-06 | `replay` | `make aee-gate` |
| VALIDATED | contracts and behaviours satisfied | AUE-P-07 | `validation` | `./verify.sh` |
| VERIFIED | independent verification proves correctness | AUE-P-08 | `verification` | `./verify.sh` |
| CERTIFIED | certification authority accepts closure | AUE-P-09 | `certification` | `make aee-gate` |
| EVOLVED | repository advanced, constitutional integrity preserved | AUE-P-10 / P-11 | `knowledge-assimilation`, `state-transition`, `continuation` | `make assimilate-gate` / `make uaue-gate` |

```
UICO states: 10    mapped onto an existing phase: 10 / 10    already gate-bound: 10 / 10
UAUE phases: 11    canonical stages claimed: 15 / 15         unclaimed: 0
```

**Article 5.1 — No transition table.** UICO declares no `may_transition_to`, no ordinals with
independent meaning, and no persistence. A second transition algebra over these states would be a
second lifecycle, which was **already refused once** (Ω-E04) and which UICM discharges by binding to
UCIC-001 under *"REUSE — BIND, DO NOT FORK."*

**Article 5.2 — Closure state remains UICM's.** The authoritative per-coordinate state is
`ClosureState`, and a coordinate changes state only because a probe re-measured it. UICO cannot
advance a state.

## Article 6 — Gap closure governance

Every gap shall map to the nine-element chain the steering requires. All 158 do, derived from located
registers rather than declared here:

```
Gap  ->  Capability  ->  Canonical Owner  ->  Target Artifact  ->  Dependency
     ->  Validation Instrument  ->  Evidence Producer  ->  Verification Gate
     ->  Closure Observation
```

**Article 6.1 — Rejection.** A gap shall be rejected if it has no owner, an invented owner,
overlapping owners, no evidence path, or no verification path. Measured over the full population:

| Criterion | Rejected |
|---|---:|
| no owner | 0 |
| invented owner | 0 |
| overlapping owner | 0 |
| missing evidence path | 0 |
| missing verification path | 0 |
| **total** | **0** |

**Article 6.2 — Overlap is measured at file granularity.** Subtree scoping yields 38 nesting
conflicts because `engine` and `platform` are themselves depth-0 capabilities. Write scope is the
**target file**, never the subtree (43 scopes, 0 collisions).

## Article 7 — Execution preconditions

No implementation begins until all seven hold. Each is measurable, and each names its evidence:

| # | Precondition | How it is established |
|---:|---|---|
| 1 | context assimilation completed | `UCOS-UICO-CONTEXT-ASSIMILATION-REPORT.md` + UICM Phases 2–5 |
| 2 | existing capability reuse evaluated | Reuse→Compose→Extend→Create→Reject applied: 13/2/3/0/6 |
| 3 | canonical owner identified | 158/158, by a total function of dimension |
| 4 | dependency graph resolved | per-dimension dependencies; 7 closure waves |
| 5 | validation path exists | 158/158 |
| 6 | evidence path exists | 158/158 |
| 7 | verification path exists | 158/158 |

**Article 7.1 — The eighth precondition UICO adds.** Discovery established one further condition the
steering did not name but which follows from principle 8 (*no mutable historical records*):

> **Cross-run observation continuity must exist before any gap is closed.**

UICM's `lineage.max_revision` is 3 for all 1054 coordinates and no loader exists, so a gap that
closes today leaves **no record it was ever open**. Closing gaps before continuity exists would
satisfy preconditions 1–7 and still destroy the evidence of closure. This is UICO-GAP-02.

## Article 8 — Relationship with existing systems

```
                        UICO   (AUTHORITY = NONE; coordinates, never replaces)
                          |
        +-----------------+-----------------+------------------+
        |                 |                 |                  |
      UICM              UAUE               CEP               UGA / UCKP
   measurement      evolution           governance          identity /
   gap detection    lifecycle           decision control    knowledge
   closure state    replay              G-14 gate           id-ledger / Layer Zero
        |                 |                 |                  |
        +--------- engine/universal_certification (T6) --------+
                        the only verdict
```

**Article 8.1** — UICO coordinates. It does not replace. Where UICO and a located owner differ, the
owner governs and UICO records a referred finding.

**Article 8.2** — UICO adds no gate. Cross-programme sequencing remains `verify.sh` plus
`uccep-bindings.json`, with `uccep-gate.yml` as the aggregate backstop.

**Article 8.3** — UICO invokes measurement; it does not measure. `UicmController.run()` is the
invocation, and its result is not UICO's to interpret.

## Article 9 — Prohibited creations

| Kind | Canonical owner | UICO relationship |
|---|---|---|
| registry | `engine/registry/universal`; REG-AUTO-001 | REFERENCE |
| identity scheme | AIF / UGA-001 / `id-ledger.json` | READ |
| authority | CEP-003 Art I/VIII; UCOS-UCAF-001 | REFERENCE |
| lifecycle | `engine/uckp/evolution.py`; UCIC-001 | BIND, DO NOT FORK |
| certification mechanism | UCOS-EPIC-006 | INVOKE |
| execution engine | `engine/constitution/gateway.py`; UAUE AUE-P-05 | REFERENCE |
| closure matrix | UICM `00-UNIVERSAL-IMPLEMENTATION-CLOSURE-MATRIX.md` | PROJECT |
| gap register | UICM `04-CLOSURE-GAP-REGISTER.json` | READ |
| observation history | UICM `ObservationRegistry` | READ |

## Article 10 — Evolution

**Article 10.1** — Append-only. This charter is corrected by appending a superseding determination
with explicit lineage, never by editing it.

**Article 10.2** — Additive. A future responsibility is admitted by an entry, never by rewrite, and
only after Reuse→Compose→Extend→Create→Reject has been applied and recorded.

**Article 10.3** — No admission by default routing. Per CMG-000001 Art LXXVII.4, an unowned concept
shall not be routed to UICO because UICO is the most recently active programme. *"Default routing
manufactures parallel authority."*

**Article 10.4** — Self-limiting. If a future determination finds that UICO owns nothing beyond what
its owners already discharge, the correct outcome is to **retire this programme**, not to grow it.
On the evidence of Phase 1, that outcome is likely.

## Article 11 — Standing

**PROVISIONAL.** UICO carries the EC-1 provisional-state posture: it asserts no constitutional
finality, confers no authority, and records engineering readiness only. Its three EXTEND rows belong
to UICM and UAUE and are **unauthorized** pending explicit approval.
