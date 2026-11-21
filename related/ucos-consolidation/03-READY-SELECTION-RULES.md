# 03 — READY SELECTION RULES

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. READY is a **derived predicate**; an object is never marked READY manually.

---

## 1. READY definition

An object is **READY** iff it is executable (`disposition = SPECIFIED`, non-sentinel) **and all seven** predicates below evaluate true against Repository Truth at the current baseline. READY is recomputed after every regeneration; it is never cached across baselines.

```
READY(o) :=
      executable(o)
  AND P1 dependencies_complete(o)
  AND P2 destination_exists(o)
  AND P3 owner_exists(o)
  AND P4 implementation_target_exists(o)
  AND P5 validation_owner_exists(o)
  AND P6 certification_owner_exists(o)
  AND P7 traceability_owner_exists(o)
```

If any predicate is false → object is **BLOCKED** (predicate names the reason). Fail-closed.

---

## 2. The seven READY predicates (deterministic)

| # | Predicate | Derivation from Repository Truth | Blocks with reason |
|---|---|---|---|
| P1 | **dependencies_complete** | all objects in strictly-lower waves (`03`/`04` IMG layer-gate) are IMPLEMENTED (`in_code=true`) | `BLOCKED:PREDECESSOR-WAVE` |
| P2 | **destination_exists** | `closure.json.files[0]` (canonical home) is non-empty and `homed=true` | `BLOCKED:NO-DESTINATION` |
| P3 | **owner_exists** | `family` maps to a defined owner (family→owner map, `02` IMG) | `BLOCKED:NO-OWNER` |
| P4 | **implementation_target_exists** | target package resolvable (family→package, `02` IMG); for GENERATED objects, the factory realizer file exists in `engine/factory/factories/` | `BLOCKED:NO-TARGET` / `BLOCKED:NO-REALIZER` |
| P5 | **validation_owner_exists** | validation harness present (`verify.sh`) + per-type validation owner defined (`02` IMG §5) | `BLOCKED:NO-VALIDATION-OWNER` |
| P6 | **certification_owner_exists** | EC-3 gate defined as certification owner for the type | `BLOCKED:NO-CERT-OWNER` |
| P7 | **traceability_owner_exists** | canonical home register resolvable so `id→artifact` can be bound (`homed=true`, register present) | `BLOCKED:NO-TRACE-OWNER` |

---

## 3. Dependency-order safety

> **No READY object may violate dependency order.**

P1 guarantees this: an object in wave *N* becomes READY only when **every** lower-wave object is IMPLEMENTED. Because the dependency graph is a strict partial order over 5 layers (acyclic, `03` IMG), P1 is well-defined and terminating. Intra-wave objects have no edges, so once P1 holds for one member of a wave it holds for all non-sentinel members simultaneously → the whole wave becomes READY together.

---

## 4. READY evaluation at the current baseline (`ab78f35`)

| Wave | Objects | P1 (deps complete?) | READY now? |
|---|---|---|---|
| Wave-01 (LAW, 20) | roots | ✔ (no predecessor) | **READY — 20** |
| Wave-02 (14 impl) | needs W1 IMPLEMENTED | ✘ (W1 still SPECIFIED) | BLOCKED |
| Wave-03 (25 impl) | needs W2 | ✘ | BLOCKED |
| Wave-04 (10 impl) | needs W3 | ✘ | BLOCKED |
| Wave-05 (8 impl) | needs W4 | ✘ | BLOCKED |

**Current READY set = the 20 Wave-01 LAW roots.** This matches IMG-001 `08` (READY 20). All higher waves are correctly BLOCKED on `P1:PREDECESSOR-WAVE`.

---

## 5. GENERATED-object special case (P4)

For the 12 GENERATED objects, P4 additionally requires the **factory realizer** to exist:

| Generative object(s) | Realizer file | Present @ `ab78f35`? | P4 |
|---|---|---|---|
| ARCH-API-001 | `engine/factory/factories/api.py` | ✔ (scaffold) | satisfiable |
| ARCH-EVENT-001 | `engine/factory/factories/event.py` | ✘ absent | `BLOCKED:NO-REALIZER` |
| ARCH-WORKFLOW-001 | `engine/factory/factories/workflow.py` | ✘ absent | `BLOCKED:NO-REALIZER` |
| ARCH-RUNTIME-001 / RUNTIME-000/020 | `engine/factory/factories/runtime.py` | ✘ absent | `BLOCKED:NO-REALIZER` |
| DATA-027 | `data.py` | ✔ | satisfiable |
| APPLICATION-015/017/019/020 | `application.py` | ✔ | satisfiable |
| INFRASTRUCTURE-004 | (infrastructure realizer) | ✘ absent | `BLOCKED:NO-REALIZER` |

Even after their wave opens (P1), these objects remain BLOCKED under P4 until their realizer exists. This is a derived, Repository-Truth-grounded block (factory directory listing), not a manual hold.

---

## 6. Determinism attestation

READY is a pure boolean function of `closure.json` + fixed predicate definitions + the factory directory listing. No manual override path exists. Recomputed every baseline; never cached.

---
*End of 03-READY-SELECTION-RULES.md*
