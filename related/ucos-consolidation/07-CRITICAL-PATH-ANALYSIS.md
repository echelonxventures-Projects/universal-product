# 07 — CRITICAL PATH ANALYSIS

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Path metrics are **derived** from the dependency graph (`03`). "Length" is measured in **constitutional layers (waves)**, not time — no time/effort estimate is asserted (that would be an ASSUMPTION with no Repository-Truth basis).

---

## 1. Critical path

The dependency graph is a 5-layer strict partial order (`03`). The **critical path** is the longest chain of dependency-gated layers that must complete in sequence:

```
Wave-01 Constitution  →  Wave-02 Architecture  →  Wave-03 Governance/Registry/Roadmap
        →  Wave-04 Capability/Platform  →  Wave-05 Realization
```

**Critical path length = 5 layers.** No implementation can compress this: each layer is gated on the completion of the one below it.

A representative object-level critical chain (one witness per layer):

```
Ω∞-001 (W1)  →  ARCH-MASTER-001 (W2)  →  UCOS-RECON-0000 (W3)  →  PLATFORM-017 (W4)  →  APPLICATION-015 (W5)
```

Any selection of one non-sentinel object per wave yields a chain of the same length (5), because the gating is layer-to-layer, not object-to-object.

---

## 2. Longest dependency chain

| Metric | Value |
|---|---|
| Longest dependency chain (populated layers) | **5** (W1→W2→W3→W4→W5) |
| Shortest path to first value | 1 layer (Wave-01 READY roots are immediately executable) |
| Graph depth | 5 |
| Graph is acyclic | Yes (`03` §5) |

---

## 3. Maximum parallelism

| Metric | Value |
|---|---|
| Widest raw wave (incl. sentinels) | **32** (Wave-03) |
| Widest executable wave (excl. 13 NOT REQUIRED sentinels) | **25** (Wave-03) |
| Narrowest executable wave | 8 (Wave-05) |

**Maximum parallelism = 25** executable objects (Wave-03). This is the peak concurrency the plan can exploit.

---

## 4. Span / throughput characterization

Using layers as the unit of sequencing (Repository-Truth-derived; time is not estimated):

| Quantity | Value | Meaning |
|---|---|---|
| Sequential span | 5 layers | minimum number of gated stages end-to-end |
| Total executable work | 77 objects | 90 − 13 sentinels |
| Ideal parallel stages | 5 | one per wave |
| Work per stage (executable) | W1 20 · W2 14 · W3 25 · W4 10 · W5 8 | |

The plan is **breadth-heavy, depth-shallow**: only 5 serial stages, but up to 25 objects concurrent in the widest stage. The binding constraint is the 5-layer constitutional gate chain, not object count.

---

## 5. Critical-path bottleneck notes (Repository-Truth-grounded)

1. **Wave-01 (Constitution) is the universal gate.** All 70 higher objects are transitively blocked on the 20 LAW roots. Constitution realization is the single highest-leverage action — completing it unblocks Wave-02.
2. **Generative realizers gate the GENERATED objects.** Wave-02 (ARCH-EVENT/WORKFLOW/RUNTIME) and Wave-05 realization depend on factory realizers `event.py`, `workflow.py`, `runtime.py`, which are **absent** from `engine/factory/factories/` (Repository Truth). Their absence is on the critical path for the GENERATED objects specifically.
3. **No object-level long pole beyond the 5 layers.** Because there are no intra-wave edges, no single object extends the critical path beyond the layer count.

---

## 6. Determinism attestation

Critical path (5), longest chain (5), and maximum parallelism (25 executable / 32 raw) are pure functions of the wave partition and are reproducible from `closure.json`.

---
*End of 07-CRITICAL-PATH-ANALYSIS.md*
