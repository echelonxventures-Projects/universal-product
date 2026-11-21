# 06 — IMPLEMENTATION STATE MACHINE

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Every transition is **derived** from truth signals; illegal transitions are rejected by the Quality Gate Engine (`08`).

---

## 1. States

| State | Meaning | Repository-Truth signal |
|---|---|---|
| **SPECIFIED** | design-complete, unrealized | `disposition=SPECIFIED`, `in_code=false` |
| **READY** | all 7 READY predicates hold (`03`) | derived (predicates) |
| **EXECUTING** | dispatched to implementation | controller-held (transient; no truth field yet) |
| **IMPLEMENTED** | realized in code | `in_code=true`, `certified=false` |
| **VALIDATED** | validation passed | `trace.implementation=true` + `verify.sh` pass |
| **CERTIFIED** | certification passed | `certified=true` |
| **FAILED** | execution/validation/certification failed | controller-held + failure evidence |
| **BLOCKED** | executable but ≥1 predicate false | derived (predicate reason) |
| **SUPERSEDED** | replaced by a newer canonical object/baseline | `disposition=REJECTED` or replacement mapping |
| **ARCHIVED** | terminal, retained (frozen/not-required/deferred-park) | sentinel, or CERTIFIED+frozen, or DEFERRED park |

---

## 2. Legal transition table

| From → To | Trigger (derived) | Guard |
|---|---|---|
| SPECIFIED → READY | all 7 predicates hold | P1–P7 true |
| SPECIFIED → BLOCKED | ≥1 predicate false | any Pi false |
| SPECIFIED → ARCHIVED | object is NOT-REQUIRED sentinel or DEFERRED park | sentinel/deferred |
| BLOCKED → READY | previously-failing predicates now hold | P1–P7 true |
| BLOCKED → SUPERSEDED | object replaced/rejected at new baseline | REJECTED/replacement |
| READY → EXECUTING | batch former dispatches (`05`) | in current batch, gates pass (`08`) |
| READY → BLOCKED | predicate regressed (e.g., baseline delta) | any Pi false |
| EXECUTING → IMPLEMENTED | realization succeeded | `in_code=true` |
| EXECUTING → FAILED | realization error | execution failure |
| IMPLEMENTED → VALIDATED | validation trigger pass (`02`) | `verify.sh` + type validation pass |
| IMPLEMENTED → FAILED | validation trigger fail | validation fail |
| VALIDATED → CERTIFIED | certification trigger pass | EC-3 gate pass |
| VALIDATED → FAILED | certification trigger fail | EC-3 gate fail |
| FAILED → READY | fixed & re-passes predicates (retry, `05` R2) | P1–P7 true, retries < MAX_RETRY |
| FAILED → BLOCKED | prerequisite regressed during failure | any Pi false |
| FAILED → ARCHIVED | retries exhausted → terminal-failed, escalated (`09`) | retries ≥ MAX_RETRY |
| CERTIFIED → ARCHIVED | frozen after regeneration | baseline froze object |
| CERTIFIED → SUPERSEDED | later baseline replaces it | replacement mapping |
| any active → SUPERSEDED | canonical replacement / baseline supersession | replacement mapping |
| SUPERSEDED → ARCHIVED | retired | terminal |

---

## 3. State diagram

```
                 ┌─────────────┐
                 │  SPECIFIED  │
                 └──┬───────┬──┘
        predicates✔ │       │ predicate✘
                    ▼       ▼
                 ┌──────┐  ┌─────────┐
                 │READY │◀▶│ BLOCKED │
                 └──┬───┘  └────┬────┘
          dispatch │           │ replaced
                    ▼          ▼
               ┌──────────┐  ┌────────────┐
               │EXECUTING │  │ SUPERSEDED │
               └──┬────┬──┘  └─────┬──────┘
       in_code=T │    │ fail       │
                 ▼    ▼            ▼
        ┌────────────┐ ┌────────┐  │
        │IMPLEMENTED │ │ FAILED │──┤ (retry → READY / exhaust → ARCHIVED)
        └─────┬──────┘ └────────┘  │
      validate│                     │
              ▼                      │
        ┌───────────┐               │
        │ VALIDATED │               │
        └─────┬─────┘               │
      certify │                     │
              ▼                      ▼
        ┌───────────┐        ┌────────────┐
        │ CERTIFIED │───────▶│  ARCHIVED  │  (terminal)
        └───────────┘        └────────────┘
```

---

## 4. Illegal transitions (rejected by Gate Engine `08`)

| Illegal transition | Why rejected |
|---|---|
| SPECIFIED → EXECUTING | must pass READY first |
| SPECIFIED → IMPLEMENTED | skips READY/EXECUTING |
| READY → IMPLEMENTED | skips EXECUTING |
| READY → CERTIFIED | skips execution/validation |
| IMPLEMENTED → CERTIFIED | skips VALIDATED |
| EXECUTING → CERTIFIED | skips IMPLEMENTED/VALIDATED |
| VALIDATED → IMPLEMENTED | no backward realization |
| CERTIFIED → EXECUTING/READY | terminal-forward only (except SUPERSEDED) |
| BLOCKED → EXECUTING | must reach READY first |
| ARCHIVED → any | terminal, immutable |
| any → IMPLEMENTED without `in_code=true` | not supported by Repository Truth |
| any → CERTIFIED without `certified=true` | not supported by Repository Truth |

Any transition not in the §2 legal table is rejected and logged (C12) as `GATE:ILLEGAL-TRANSITION`.

---

## 5. State ↔ readiness/disposition mapping (current baseline)

| Truth condition @ `ab78f35` | State |
|---|---|
| Ω∞-001…020 (SPECIFIED, predicates hold) | READY (20) |
| Wave-02..05 hand-authored SPECIFIED, P1 false | BLOCKED (45) |
| GENERATED objects (SPECIFIED, P1/P4 false) | BLOCKED (within 45/12) |
| 13 family sentinels | ARCHIVED-eligible (NOT REQUIRED) |
| the 314 IMPLEMENTED (context) | IMPLEMENTED/CERTIFIED (out of manifest scope) |

---

## 6. Determinism & safety

1. Every state is a function of Repository-Truth fields (except transient EXECUTING/FAILED, which are controller-held and logged).
2. Every transition has a derived trigger and a guard; no manual state edits.
3. Illegal transitions are impossible to commit — the Gate Engine rejects them pre-transition.
4. ARCHIVED and SUPERSEDED are terminal; the machine is acyclic except for the bounded FAILED↔READY retry loop (capped by MAX_RETRY).

---
*End of 06-IMPLEMENTATION-STATE-MACHINE.md*
