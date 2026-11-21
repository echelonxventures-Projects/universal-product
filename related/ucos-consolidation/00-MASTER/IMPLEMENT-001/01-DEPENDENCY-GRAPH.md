# IMPLEMENT-001 · DELIVERABLE 01 — DEPENDENCY GRAPH

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001` |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| INPUT | Deliverable 00 — Complete Executable Backlog (EB-01 … EB-09) |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DEPENDENCY CLASSES

Three distinct edge kinds are present. Conflating them is the usual cause of a false blocker.

| Edge | Meaning | Consequence if unsatisfied |
|---|---|---|
| `⇒ SATISFIED-PREREQ` | A located, verified artifact the item consumes | none — already met |
| `⇒ GATE-PREREQ` | Repository-state condition that must hold before *any* item executes | blocks the whole wave set |
| `⇒ GOVERNANCE-PREREQ` | A constitutional act outside the executable corpus | blocks only its dependent item |

---

## 2. THE GRAPH

```
                        ┌──────────────────────────────────────────────┐
                        │  GATE-PREREQ (applies to EVERY item)         │
                        │                                              │
                        │   B-1  Authority Witness                     │
                        │        9 untracked authority artifacts,      │
                        │        incl. OAA-001 (the authorization      │
                        │        itself) → must be committed +         │
                        │        registered                            │
                        │                                              │
                        │   B-2  Registration Fixed Point              │
                        │        CK-REG-DRIFT FAIL at tier=full        │
                        │        (745 generated files drift)           │
                        └───────────────────┬──────────────────────────┘
                                            │  discharged by ONE operator commit
                                            ▼
   ┌───────────────────────────── DEPENDENCY-SATISFIED FRONTIER ─────────────────────────────┐
   │                                                                                          │
   │  EB-01 ◀── uar-analyses.json + uar_engine.py        [present]  ⇒ SATISFIED-PREREQ        │
   │        ◀── UEI declaration+engine+gate pattern      [present]                            │
   │        ◀── uccep-bindings.json programs[]/checks[]  [present, data-declared]              │
   │                                                                                          │
   │  EB-07 ◀── (none)                                                                        │
   │                                                                                          │
   │  EB-02 ◀── Part 8  Observer/Identity  → platform/identity/, engine/identity/  [present]  │
   │        ◀── Part 12 Monitoring         → platform/observability/*             [present]   │
   │        ◀── Part 14 Audit/Evidence     → platform/observability/audit.py      [present]   │
   │        ◀── platform/foundation contracts+errors+bootstrap                    [present]   │
   │        ┄┄▶ SOFT: a `metering` twin dimension (EB-05 territory) for full certification    │
   │        ⚠  DISJOINTNESS CONSTRAINT with platform/measurement (UCOS-UMA-001)               │
   │                                                                                          │
   │  EB-03 ◀── id-ledger identity authority (ukb.py:52,856)                      [present]   │
   │        ◀── SignalLedger append-only pattern (connectors/base.py:151)         [present]   │
   │        ◀── 00-BOOK/SCHEMAS admission path                                    [present]   │
   │        ⚠  MUST NOT become a second capability-state authority (AEOS-001 #3)              │
   │                                                                                          │
   │  EB-04 ◀── id-ledger (UCHG/UCKA/UREG/URBK minting)                           [present]   │
   │        ◀── change-ledger.json as reuse basis (NOT a discharge)                [present]   │
   │        ◀── 4 new schemas                                                     [in scope]  │
   │                                                                                          │
   │  EB-05 ◀── rollup_dimensions() pure function (base.py:326)                    [present]   │
   │        ◀── connector auto-discovery (ukbx.py discover())                     [present]   │
   │        ◀── DIMENSIONS allowlist (base.py:38) — append-only code edit         [in scope]  │
   │                                                                                          │
   │  EB-06 ◀── Part 38/41 generation seam: platform/generation/{registry,        [present]   │
   │             dispatch,provenance,contracts}.py                                            │
   │        ◀── Part 19 Knowledge → 00-BOOK UKB                                   [present]   │
   │        ⚠  R-7: registry content only — no new numbered family                            │
   │                                                                                          │
   │  EB-08 ◀── registered corpus artifacts.json[*].traceability (13 fields)      [present]   │
   │                                                                                          │
   └──────────────────────────────────────────────────────────────────────────────────────────┘

   ┌───────────────────────────── GOVERNANCE-BLOCKED ─────────────────────────────┐
   │  EB-09 ◀══ CEP-009 amendment to UCIC-001 (FROZEN v1.0)   ⇒ GOVERNANCE-PREREQ │
   │        ◀══ CEP-008 VI.1 two-valued calculus (ACFV AG-03) ⇒ GOVERNANCE-PREREQ │
   │            UNSATISFIED — ineligible for any wave                             │
   └──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. INTER-ITEM EDGES

The decisive finding: **there is not one hard dependency between any two executable backlog items.**

| From | To | Kind | Determination |
|---|---|---|---|
| EB-05 | EB-02 | **SOFT** | A `metering` twin dimension would let metering report through the twin. EB-02 does not require it to function or to pass its own gate. Not a wave-ordering constraint. |
| EB-04 | EB-03 | **SOFT** | `rollback.json` would give the Idea Box register-backed rollback. `RELEASE-001` §2.1 already designates **git revert** as the rollback strategy, so this is an enhancement, not a prerequisite. |
| EB-01 | EB-02 … EB-06 | **ADVISORY, ORDERING** | Any new programme's own gate will be modelled on the binding EB-01 establishes. Doing EB-01 first prevents each later item re-deriving the pattern. |
| EB-07 | all certification claims | **ADVISORY, ORDERING** | While the phase-3 verdict is a constant, `CK-CLOSURE-P3` fails advisorily in every UCCEP run and the programme contradicts itself. Certifying a *new* capability behind a verdict that cannot vary produces evidence of unknown value. |
| EB-08 | `CK-HEALTH` | **CAUSAL** | Traceability completeness is the sole cause of repository health RED. Any new artifact adds 13 more empty slots, so EB-08's cost grows with every later wave. |

**Consequence:** wave ordering is driven by *evidence integrity and scope*, not by technical dependency. Eight items could in principle execute in parallel. They should not, because three of them determine whether the other five can be honestly certified.

---

## 4. CRITICAL PATH

```
[B-1 + B-2 discharge]  ──▶  EB-07  ──▶  EB-01  ──▶  EB-02  ──▶  EB-04 ──▶ EB-03 ──▶ EB-05 ──▶ EB-08 ──▶ EB-06
   one operator commit      make the   bind the   discharge   close     green-    widen     fill       largest
                            gate able  registry   D22/D23     GG-3      field     twin      spine      item
                            to fail    to a gate
                            └────────── WAVE-001 ──────────┘
```

The critical path begins with a **single operator commit**, not with code. Nothing else in this graph can legitimately start before it.

---

## 5. TOPOLOGICAL ORDER

| Order | Item | Admitted because |
|---|---|---|
| 0 | `B-1` + `B-2` discharge | Precondition of every item |
| 1 | EB-07 | Zero dependencies; makes a gate capable of failing |
| 2 | EB-01 | All prereqs present; establishes the enforcement-binding pattern |
| 3 | EB-02 | All three MIP part-dependencies present; discharges D22/D23 |
| 4 | EB-04 | id-ledger present; schemas in scope |
| 5 | EB-03 | Ledger + identity patterns present |
| 6 | EB-05 | Roll-up + discovery present |
| 7 | EB-08 | Corpus present; cheapest after new artifact creation settles |
| 8 | EB-06 | Generation seam present; largest scope, so last |
| — | EB-09 | **Not orderable.** Awaits `CEP-009`. |

---

## 6. DETERMINATION

> **All dependency relationships are RESOLVED.**

- 8 of 9 items are dependency-satisfied.
- 1 item (EB-09) has an identified, named, unsatisfied governance prerequisite and is therefore excluded from all waves rather than left ambiguous.
- 0 items have an unresolved or unknown dependency.
- 0 cyclic dependencies. Verified independently: `engine.graph.cli validate` → `dependency_cycle: []` over 12,829 edges / 1,218 nodes.
- 2 gate-prerequisites (`B-1`, `B-2`) apply uniformly and are discharged by one act.

---

*END — `IMPLEMENT-001` Deliverable 01 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
