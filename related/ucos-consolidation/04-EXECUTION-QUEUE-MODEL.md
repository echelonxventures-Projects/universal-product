# 04 — EXECUTION QUEUE MODEL

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Queue contents and ordering are **derived**; nothing is enqueued manually.

---

## 1. Queue topology

The controller maintains three derived queues plus terminal sinks:

```
Execution Queue   (all executable objects, topological order)
      │  filter: READY predicates (03)
      ▼
Ready Queue       (READY subset, dependency-safe, order-preserved)
      │  cut: batch former (05)
      ▼
Execution Batch   (current dependency-safe parallel cut)
      │  → EXECUTING → IMPLEMENTED → VALIDATED → CERTIFIED
      ▼
Completed sink    (CERTIFIED / ARCHIVED)     Failed sink (FAILED → retry)
```

Sidecar: **Blocked Set** (executable objects failing ≥1 READY predicate) and **Excluded Set** (13 NOT REQUIRED sentinels).

---

## 2. Queue definitions

| Queue | Membership rule (derived) | Order | Size @ `ab78f35` |
|---|---|---|---|
| **Execution Queue** | `disposition=SPECIFIED` ∧ not sentinel | topological (`05` IMG: wave, family, id) | 77 |
| **Ready Queue** | Execution-Queue objects where `READY(o)` (all 7 predicates, `03`) | inherits topological order | 20 (Wave-01) |
| **Execution Batch** | deterministic cut of Ready-Queue head (`05`) | preserves order | ≤ batch cap |
| **Blocked Set** | executable ∧ ¬READY | keyed by block reason | 45 |
| **Excluded Set** | NOT REQUIRED sentinels | n/a | 13 |

Sum: 77 executable (20 ready + 45 blocked + 12 generated-of-which-blocked-by-P4) + 13 excluded = 90. *(Note: the 12 GENERATED are within the 77 executable; at `ab78f35` all are wave-blocked by P1, some additionally by P4.)*

---

## 3. Ordering rule (single source)

Queue order = IMG-001 `05` topological order: **wave ascending → family ascending → id ascending**. Because there are no intra-wave dependency edges, this order is dependency-valid and fully reproducible. The Queue Manager (C5) never reorders by any non-derived criterion.

---

## 4. Enqueue / dequeue semantics

| Operation | Trigger (derived) | Effect |
|---|---|---|
| Enqueue → Execution Queue | object is SPECIFIED non-sentinel at load | placed at topological position |
| Promote → Ready Queue | all 7 READY predicates hold | moved preserving order |
| Demote → Blocked Set | any predicate fails (e.g., baseline regressed) | removed from Ready Queue with reason |
| Cut → Execution Batch | batch former selects head under safety cap | reserved for dispatch |
| Retire → Completed sink | object CERTIFIED (or ARCHIVED) | leaves all active queues |
| Return → Ready Queue | FAILED object retried after fix | re-promoted if predicates hold |

All operations are idempotent per baseline and logged (C12).

---

## 5. Queue invariants

1. **No manual enqueue.** Membership is a function of `closure.json` only.
2. **Order stability.** Order is derived and identical across runs on the same baseline.
3. **Dependency safety.** An object reaches the Ready Queue only if P1 holds → the Ready Queue never contains a dependency-order violation.
4. **Disjointness.** Execution Batch ⊆ Ready Queue ⊆ Execution Queue; Excluded Set is disjoint from all.
5. **Monotone drain.** Across baselines, the Execution Queue shrinks monotonically as SPECIFIED→IMPLEMENTED (barring SUPERSEDED re-entry).

---

## 6. Queue state at the current baseline

| Set | Count | Contents |
|---|---|---|
| Execution Queue | 77 | all non-sentinel SPECIFIED (Wave-01…05) |
| Ready Queue | 20 | Ω∞-001 … Ω∞-020 |
| Blocked Set | 45 | Wave-02..05 hand-authored objects (reason `PREDECESSOR-WAVE`); GENERATED also `NO-REALIZER` where applicable |
| Excluded Set | 13 | family sentinels (NOT REQUIRED) |

The **only dispatchable content now** is the 20-object Wave-01 Ready Queue.

---
*End of 04-EXECUTION-QUEUE-MODEL.md*
