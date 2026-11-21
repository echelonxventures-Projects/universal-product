# 02 — EXECUTION LIFECYCLE

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Every lifecycle transition is **derived**; none is manual.

---

## 1. Canonical lifecycle pipeline

```
Repository Truth
      ↓  (C1 load + verify)
Implementation Manifest        (IMG-001 bound: 90 CKOs, waves, graph)
      ↓  (C3 state resolve)
Execution Queue                (all executable objects, topological order)
      ↓  (C4 ready predicates)
Ready Queue                    (subset whose 7 predicates all hold)
      ↓  (C6 batch former + C11 gates)
Execution Batch                (dependency-safe parallel cut)
      ↓  (C7 dispatch → external implementation)
Validation                     (C8: verify.sh + per-type validation owner)
      ↓
Certification                  (C9: EC-3 gate)
      ↓
Repository Regeneration        (C10: regenerate closure.json → new baseline)
      ↓
Readiness Update               (C3/C4 recompute on new baseline)
      ↓
Next Batch                     (loop)
```

**Rule:** each ↓ is a pure derivation from Repository Truth. There are **no manual transitions**.

---

## 2. Stage definitions & derived trigger conditions

| Stage | Enter when (derived) | Exit when (derived) | Controller component |
|---|---|---|---|
| Repository Truth | baseline present; `closure.json` valid; `gap_total=0` | truth loaded & hashed | C1 |
| Implementation Manifest | truth loaded | 90 CKOs bound with wave/graph/readiness | C2 |
| Execution Queue | manifest bound | states resolved; executable set = 77 (non-sentinel) | C3 |
| Ready Queue | states resolved | READY predicates hold for object (`03`) | C4 |
| Execution Batch | Ready Queue non-empty | batch cut passes all gates (`08`) | C6 + C11 |
| Validation | batch objects reach IMPLEMENTED (`in_code=true`) | `verify.sh` + type validation pass/fail | C8 |
| Certification | objects VALIDATED | EC-3 gate pass/fail | C9 |
| Repository Regeneration | regeneration trigger fires (`07`) | new `closure.json` written; new baseline | C10 |
| Readiness Update | new baseline loaded | READY set recomputed | C3/C4 |
| Next Batch | READY Queue non-empty on new baseline | — (loop) | C5/C6 |

---

## 3. Loop termination (derived)

The lifecycle loop terminates when Repository Truth reports the realization blocker resolved:

| Termination condition | Repository-Truth signal |
|---|---|
| Wave complete | 0 SPECIFIED remaining in that wave's families |
| Full implementation complete (R1 resolved) | `dispositions.SPECIFIED = 0` |
| Repository at LEVEL-5 | SPECIFIED=0 and all newly-implemented `in_code=true` |

At `SPECIFIED = 0` the controller stops selecting realization work; downstream validation/certification proceed per the IAC-001 remediation graph (in-corpus ceiling LEVEL-7 PROVISIONAL; LEVEL-8 external DR-RAT-11).

---

## 4. Trigger taxonomy

| Trigger | Fires | Consumes | Produces |
|---|---|---|---|
| **Validation trigger** | object enters IMPLEMENTED | `in_code=true` | VALIDATED / FAILED |
| **Certification trigger** | object enters VALIDATED | validation pass | CERTIFIED / FAILED |
| **Regeneration trigger** | batch/wave/full completion (`07`) | completion signal | new baseline |
| **Readiness trigger** | new baseline loaded | truth delta | updated READY set |
| **Next-batch trigger** | READY Queue non-empty | ordered queue | next batch |

---

## 5. Lifecycle invariants

1. An object cannot enter Validation without being IMPLEMENTED (`in_code=true`).
2. An object cannot enter Certification without being VALIDATED.
3. Readiness is never recomputed from stale truth — it always follows a regeneration.
4. No stage is entered by manual action; every entry has a derived trigger (§2).
5. The loop is **fail-closed**: absence of a trigger keeps the object in place; it never advances speculatively.

---

## 6. One full cycle, worked (illustrative, Wave-01)

```
baseline ab78f35
  → manifest binds 20 READY LAW roots (Ω∞-001..020)
  → Execution Queue head = Wave-01
  → Ready predicates hold for all 20 (no predecessor) → Ready Queue = 20
  → Batch former cuts Wave-01 batch (gates pass)
  → dispatch EXECUTING (external)
  → objects reach IMPLEMENTED → Validation (verify.sh) → VALIDATED
  → Certification (EC-3) → CERTIFIED
  → Regeneration trigger (wave completion) → regenerate closure.json → baseline'
  → Readiness update on baseline': Wave-02 predicates now satisfiable → next batch
```

No step above is manually selected; each is derived from the truth state.

---
*End of 02-EXECUTION-LIFECYCLE.md*
