# 05 — BATCH GENERATION RULES

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Batches are **derived** deterministically from the Ready Queue; no batch is hand-assembled.

---

## 1. Batch definition

A **batch** is a deterministic, dependency-safe cut of the Ready Queue that the controller dispatches for concurrent execution. Batching is a pure function:

```
batch(Ready Queue, baseline) → ordered subset
```

Same Ready Queue + same rules ⇒ identical batch. No manual assembly.

---

## 2. Batch formation rules (deterministic)

| # | Rule | Definition |
|---|---|---|
| B1 | **Single-wave constraint** | Every batch is drawn from **one wave only**. A batch never mixes waves (prevents cross-layer dependency risk). |
| B2 | **Ready-only** | Every batch member satisfies all 7 READY predicates (`03`). |
| B3 | **Order preservation** | Members are taken from the Ready-Queue head in topological order (`04`). |
| B4 | **Batch-size cap** | `size ≤ min(WAVE_WIDTH, MAX_BATCH)`. Default `MAX_BATCH = full wave` (all intra-wave objects are independent, so max-safe parallelism = the wave). A smaller cap may be set as an operational throttle **without** changing determinism (cap is a fixed parameter, not a manual pick). |
| B5 | **Write-contention sub-serialization** | Members sharing one writable canonical home (`02`/`06` advisory) are placed in the same batch but flagged for serialized/transactional write. |
| B6 | **Sentinel exclusion** | NOT REQUIRED sentinels are never batched. |
| B7 | **Realizer precondition** | GENERATED members are batched only if their factory realizer exists (P4); otherwise they stay BLOCKED. |

---

## 3. Batch size & parallelism

| Wave | Max-safe batch (executable) | Parallelism basis |
|---|---|---|
| Wave-01 | 20 | no intra-wave edges |
| Wave-02 | 14 (4 GENERATED gated by realizer) | independent |
| Wave-03 | 25 | independent (peak parallelism) |
| Wave-04 | 10 | independent |
| Wave-05 | 8 (GENERATED, realizer-gated) | independent |

Default policy: **one batch per wave** at max-safe width, subject to `MAX_BATCH` throttle and B5 write-contention grouping.

---

## 4. Dependency safety

- **Cross-wave:** guaranteed by B1 + P1 — a wave batch is cut only after all lower waves are IMPLEMENTED.
- **Intra-wave:** guaranteed by the graph (`03` IMG: no intra-wave edges). Therefore every member of a single-wave batch is mutually independent and safe to run in parallel.
- **Result:** a batch can never contain a dependency-order violation.

---

## 5. Rollback boundary

| Aspect | Rule |
|---|---|
| Boundary unit | **The batch is the atomic rollback unit.** A partially-failed batch rolls back to the pre-batch baseline. |
| No partial promotion | The controller does **not** regenerate Repository Truth from a partially-successful batch; regeneration requires a defined completion (`07`). |
| Isolation | Because batch members are independent (§4), individual failures do not corrupt siblings; the boundary bounds blast radius to the batch. |
| Baseline anchor | Rollback target = the immutable `closure.json` baseline hash recorded at batch cut (logged by C12). |

---

## 6. Batch outcomes

| Outcome | Condition (derived) | Controller action |
|---|---|---|
| **Batch completion** | all members reach CERTIFIED (or terminal-valid) | trigger regeneration (`07`) |
| **Batch failure** | ≥1 member FAILED at execution/validation/certification | hold batch; do not regenerate; route failures to retry |
| **Batch retry** | failed member re-satisfies READY after fix | re-admit failed members to a new batch (same wave), preserving order |
| **Batch regeneration** | after completion | regenerate `closure.json`; recompute READY on new baseline |

**Failure isolation:** successful members of a failed batch remain IMPLEMENTED/VALIDATED in the controller's working state but are **not certified into a new baseline** until the batch's regeneration criterion is met (`07`); alternatively, per policy, the batch may be re-cut to exclude the failed member and re-run. Both paths are deterministic; the chosen policy is a fixed parameter, not a manual decision.

---

## 7. Retry rules

| # | Rule |
|---|---|
| R1 | Retry is bounded by a fixed `MAX_RETRY` parameter; on exhaustion the member enters FAILED-terminal and is escalated to governance (`09`), never silently dropped. |
| R2 | A retried member must **re-pass all 7 READY predicates** at the current baseline before re-batching (no stale readiness). |
| R3 | Retry never reorders the queue non-deterministically; re-admission preserves topological order. |

---

## 8. Worked batch (Wave-01, current baseline)

```
Ready Queue = [Ω∞-001 … Ω∞-020]   (20, topological)
B1 single-wave: Wave-01 ✔
B4 size = min(20, MAX_BATCH)      → default 20
B5 write-contention: LAW targets constitution corpus; advisory none blocking
B6/B7: no sentinels, no realizer-gated members in Wave-01
⇒ Batch-01 = {Ω∞-001 … Ω∞-020}   (atomic rollback unit, anchored to ab78f35)
```

---

## 9. Determinism attestation

Batch contents, size, and order are pure functions of the Ready Queue and fixed parameters (`MAX_BATCH`, `MAX_RETRY`). No manual batch assembly path exists. Every batch cut is logged with its baseline hash (C12).

---
*End of 05-BATCH-GENERATION-RULES.md*
