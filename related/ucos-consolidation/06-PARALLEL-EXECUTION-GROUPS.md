# 06 — PARALLEL EXECUTION GROUPS

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Parallel groups are **derived** from the dependency graph (`03`): objects with no dependency edge between them may execute concurrently. Since there are no intra-wave edges, each wave is a maximal parallel group.

---

## 1. Parallelization principle

Two objects may run in parallel iff neither depends on the other. Under the constitutional layer-gate model (`03`), dependency exists **only across waves**, never within a wave. Therefore:

> **Each wave is a maximal safe parallel-execution group.** Within a wave, all implementable (non-sentinel) objects run concurrently.

A finer intra-wave sub-grouping is available by **canonical destination (home file)**: objects sharing a single writable home may need write-serialization. This is surfaced below as an advisory sub-partition (does not change dependency-parallelism).

---

## 2. Primary parallel groups (one per wave)

| Group | Wave | Parallel-eligible objects (implementable) | Width |
|---|---|---|---|
| **PG-1** | Wave-01 Constitution | all 20 LAW (Ω∞-001…020) | **20** |
| **PG-2** | Wave-02 Architecture | 14 (4 GENERATED + 10 BLOCKED) | **14** |
| **PG-3** | Wave-03 Governance/Registry/Roadmap/Knowledge | 25 BLOCKED | **25** |
| **PG-4** | Wave-04 Capability/Platform/Gate | 10 BLOCKED | **10** |
| **PG-5** | Wave-05 Realization | 8 GENERATED | **8** |

Sentinels (13 NOT REQUIRED) are excluded — they carry no execution.

**Maximum parallelism = 25** (PG-3, effective/implementable). If sentinels are counted as graph nodes, the widest raw wave is Wave-03 at 32; the **executable** maximum is **25**.

---

## 3. Advisory intra-wave sub-groups (write-contention on shared home)

Several objects share `00-BOOK/DATA/artifacts.json` as canonical home. Dependency-wise they are parallel, but if realization writes to that shared ledger, those writes should be serialized (or transactionally merged). This is an **advisory** execution note, not a dependency constraint.

| Wave | Shared-home cluster (`00-BOOK/DATA/artifacts.json`) | Members |
|---|---|---|
| W2 | ARCH generative roots | ARCH-API-001, ARCH-EVENT-001, ARCH-WORKFLOW-001 |
| W3 | UCOS-GOV / UCOS-RAT / PHASE | UCOS-GOV-001/003/005, UCOS-RAT-001, Phase-024 |
| W4 | PLATFORM span | PLATFORM-003/004/007/013/014/015/016/017/018 |
| W5 | APPLICATION / INFRASTRUCTURE | APPLICATION-015/017, INFRASTRUCTURE-004 |

Other homes (e.g., `00-SOURCE/VISION/Missing 2.docx` for 16 LAW objects) are read-sources; the LAW codification target is the constitution corpus, so the 20 LAW objects remain fully parallel with no write-contention concern flagged by Repository Truth.

---

## 4. Concurrency profile across the run

```
parallel width
   25 |                     ████ PG-3
   20 | ████ PG-1                                    
   14 |          ████ PG-2                             
   10 |                              ████ PG-4         
    8 |                                       ████ PG-5
      +----------------------------------------------
        W1        W2        W3        W4        W5   (time →, waves serial)
```

- Waves execute **serially** (each gated on the prior); **within** a wave execution is **fully parallel**.
- Peak concurrency occurs in Wave-03 (25 concurrent governance/registry objects).

---

## 5. Parallel-eligibility per object (rule)

| Readiness | Parallel-eligible? | Note |
|---|---|---|
| READY (20) | Yes — immediately, within PG-1 | no predecessor |
| BLOCKED (45) | Yes — within its wave, once wave opens | gated on lower wave only |
| GENERATED (12) | Yes — within its wave, via factory pipeline | requires realizer present |
| NOT REQUIRED (13) | N/A | no execution |

---

## 6. Determinism attestation

Parallel groups are a pure function of the wave assignment (`04`), which is a pure function of `family`. The grouping is reproducible and introduces no manual scheduling.

---
*End of 06-PARALLEL-EXECUTION-GROUPS.md*
