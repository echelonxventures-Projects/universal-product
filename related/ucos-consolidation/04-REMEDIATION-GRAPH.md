# 04 — REMEDIATION GRAPH

> **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY planning only. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Assumptions flagged explicitly.

---

## 1. Deterministic remediation waves

The remediation graph is derived from the dependency graph (`03`). It is deterministic: wave order is fixed by the constitutional ladder; within a wave, work parallelizes across independent families.

```
WAVE A (parallel, in-corpus)
   ├─ R1  Realize the 90 SPECIFIED span
   │      · generative realizers: add event.py, workflow.py; realize API + RUNTIME architecture
   │      · realize remaining SPECIFIED families (LAW 20, PLATFORM 10, ARCH 15, PHASE 6, …)
   └─ R2  Certify the 74 realized-but-uncertified IMPLEMENTED concepts
             (independent of R1 — may run fully in parallel)
                         │
WAVE B (after R1)
   └─ D1  Validate the newly-realized span                → completes L6
                         │
WAVE C (after R1 + D1)
   ├─ D2  Certify the newly-realized span
   └─ D3  Close traceability CKO → implementation artifact → completes L7 (PROVISIONAL)
                         │
WAVE D (external, terminal — out-of-corpus)
   └─ R3  DR-RAT-11 External Constituent Act              → elevates L7 → L8 (ABSOLUTE)
```

---

## 2. Per-root remediation specification

### R1 — Realization incompleteness (ROOT, in-corpus)

| Attribute | Value |
|---|---|
| Prerequisites | None in-corpus. L4 Implementation Ready already achieved; dependency graph acyclic; architecture SPECIFIED. |
| Dependents | D1, D2, D3, L5 |
| Execution order | Wave A (may start immediately) |
| Parallelization | High. Independent SPECIFIED families parallelize (LAW, PLATFORM, ARCH, PHASE, APPLICATION, GOV, …). Generative realizers `event.py`/`workflow.py`/API/RUNTIME are mutually independent. |
| Estimated impact | Unlocks L5; removes 90 SPECIFIED; enables D1/D2/D3. **(Effort not estimated from Repository Truth — ASSUMPTION territory; not asserted.)** |
| Completion criteria | `closure.json` dispositions show SPECIFIED = 0 (all → IMPLEMENTED, `in_code=true`). |
| Success evidence | Regenerated `closure.json` at new baseline: SPECIFIED count 0; `engine/factory/factories/event.py` and `workflow.py` present; generative catalogs realized. |

### R2 — Certification incompleteness of realized concepts (ROOT, in-corpus)

| Attribute | Value |
|---|---|
| Prerequisites | None (74 concepts already `in_code=true`). Runs in parallel with R1. |
| Dependents | L7 |
| Execution order | Wave A |
| Parallelization | High — 74 concepts independently certifiable via verify pipeline. |
| Estimated impact | Moves 74 IMPLEMENTED from `certified=false` to `certified=true`; contributes to L7. |
| Completion criteria | Every IMPLEMENTED concept has `certified=true`. |
| Success evidence | `closure.json`: IMPLEMENTED-certified count == IMPLEMENTED total; verify pipeline (`verify.sh`) green for the 74. |

### R3 — DR-RAT-11 constitutional finality (ROOT, EXTERNAL)

| Attribute | Value |
|---|---|
| Prerequisites | External Constituent Act (F-05); constituent-authority capabilities CAC-01..07 (all currently ABSENT); closure of GAP-01..08. |
| Dependents | L8 (absolute finality) only. Does **not** gate R1/R2/D1–D3 or L4–L7 provisional. |
| Execution order | Wave D — terminal. Out-of-corpus; cannot be completed by any repository action. |
| Parallelization | Fully independent of in-corpus waves (may be pursued externally in parallel, but cannot *complete* in-corpus). |
| Estimated impact | Elevates PROVISIONAL (L7) → FINAL (L8); retires residual risk RR-08 (permanent-freeze). |
| Completion criteria | External ratification act executed and bound read-only into the corpus (per R-12). |
| Success evidence | Ratification determination recorded out-of-corpus; `UCOS-RAT-001-REPOSITORY-RATIFICATION-DETERMINATION` transitions from SPECIFIED to ratified/final. |

---

## 3. Derived-blocker remediation (collapse into R1)

| Derived | Remediation | Completes |
|---|---|---|
| D1 Validation | Validate realized span post-R1 (verify pipeline) | L6 |
| D2 Certification-of-span | Certify realized span post-R1 | contributes L7 |
| D3 Traceability | Bind each realized CKO to its implementation artifact | contributes L7 |

No derived blocker requires independent planning beyond its parent root R1.

---

## 4. Parallelization summary

| Wave | Parallel tracks |
|---|---|
| A | R1 (multi-family, multi-realizer) ∥ R2 (74 certifications) |
| B | D1 validation (fan-out per realized family) |
| C | D2 ∥ D3 |
| D | R3 (external, single terminal act) |

**Maximum concurrency** is in Wave A. The terminal gate R3 is serial and external.

---

## 5. Determinism statement

Given Repository Truth at `ab78f35`, the wave order (A→B→C→D) is uniquely determined by the constitutional ladder and the root/derived edges. There is no discretionary ordering among waves; only intra-wave scheduling is free. This satisfies the mission requirement for a **single canonical, deterministic remediation order**.

---
*End of 04-REMEDIATION-GRAPH.md*
