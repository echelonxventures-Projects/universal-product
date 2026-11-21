# 11 — Runtime Compliance Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define runtime-compliance rules an implementation SHALL satisfy (Runtime Review R-7; part of CG-07/CG-11). Consumes RL-F2 / RUNTIME-* and EC-1 runtime descriptors; adds no new runtime model.

## 1. Runtime Rules (RC)

| # | Rule | Basis | Evidence |
|---|---|---|---|
| RC-1 | Runtime behavior binds the frozen **RL-F2 RUNTIME concern by reference** (execution/state/workflow/event/policy) | AB-001 FD-06/07 | runtime-binding record |
| RC-2 | The implementation **re-founds no runtime** (no new lifecycle/scheduler/execution engine) | AB-001 FD-06 | non-refounding check |
| RC-3 | Lifecycle is **forward-only**; recorded transitions only | AB-001 FD-10 (CONST-05/09) | lifecycle record |
| RC-4 | Execution is **deterministic** (no clock/RNG/network in the determined path) | CG-14 | determinism evidence |
| RC-5 | Runtime concerns (timeout/retry/rollback/compensation/cancellation) expressed as **references**, never re-implemented | band precedent (SEX/SOO laws) | reference map |
| RC-6 | Runtime operations govern/record via EC-1 descriptors / EPIC-012 runtime ops | AB-001 B-16 | ops binding |
| RC-7 | Runtime posture is **evaluative where required** (e.g., resilience/availability non-enforcing) | band precedent (IRES laws) | evaluative record |

## 2. Runtime Reuse-by-Reference

An implementation invokes runtime capability strictly by ENG-005 reference to RL-F2; it MUST NOT embed a private runtime. This preserves the single runtime substrate (AB-001 B-16) and Knowledge Once. Violation ⇒ CG-07 FAIL.

## 3. Determinism at Runtime

- The determined execution path is a pure function of inputs + referenced runtime state; re-execution reproduces byte-identical results (CG-14).
- Non-determinism sources (wall-clock, RNG, network ordering) are excluded from the determined path or explicitly isolated and declared.

## 4. Fail-Closed Conditions

| Condition | Result |
|---|---|
| Re-founds a runtime / embeds private scheduler | CG-07 FAIL → DENY |
| Non-deterministic determined path | CG-14 FAIL → DENY |
| Illegal/backward lifecycle transition | CG-07 FAIL → DENY |
| Runtime concern re-implemented (not referenced) | RC-5 FAIL → DENY |

## 5. Determination

**RUNTIME COMPLIANCE RULES ARE DEFINED (RC-1…RC-7, fail-closed).** They require reference-only RL-F2 binding, no re-founding, forward-only deterministic lifecycle, and evaluative posture where mandated — consuming the frozen runtime substrate without redefining it.

*END — 11 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
