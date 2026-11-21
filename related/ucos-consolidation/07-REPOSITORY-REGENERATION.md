# 07 — REPOSITORY REGENERATION RULES

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Regeneration is **derived** and produces a new authoritative baseline; it is never triggered manually.

---

## 1. What "regeneration" means

Regeneration = re-running the closure engine to produce a fresh `closure.json` (and a new baseline commit **outside this design mission**) that reflects newly IMPLEMENTED/CERTIFIED objects. After regeneration, the controller reloads truth (C1) and recomputes the READY set (C3/C4). Regeneration is the **only** mechanism by which the controller advances between baselines.

**Invariant:** the controller never mutates `closure.json` in place; it triggers a full regeneration so Repository Truth remains the single derived authority.

---

## 2. Regeneration triggers (deterministic)

| # | Trigger | Fires when | Scope of truth update |
|---|---|---|---|
| G1 | **Implementation completion** (object) | an object reaches IMPLEMENTED (`in_code=true`) | *staged* — not an immediate regeneration (see §3 cadence) |
| G2 | **Validation completion** (object) | object VALIDATED | staged |
| G3 | **Certification completion** (object) | object CERTIFIED (`certified=true`) | staged |
| G4 | **Batch completion** | all members of a batch CERTIFIED | **REGENERATE** (primary cadence) |
| G5 | **Wave completion** | all non-sentinel objects of a wave IMPLEMENTED | **REGENERATE + readiness re-eval opens next wave** |
| G6 | **Full implementation completion** | `dispositions.SPECIFIED = 0` | **REGENERATE + terminal**: R1 resolved, LEVEL-5 reached |

---

## 3. Regeneration cadence (which trigger actually regenerates)

To keep regeneration deterministic and bounded, the **primary regeneration unit is the batch (G4)**; wave (G5) and full (G6) completions are natural super-cases that also regenerate. Per-object completions (G1–G3) are **staged** into the batch and do **not** each spawn a regeneration (prevents nondeterministic mid-batch truth drift).

```
object IMPLEMENTED/VALIDATED/CERTIFIED  → staged (no regen)
        │  (all batch members CERTIFIED)
        ▼
BATCH COMPLETE (G4) ─▶ REGENERATE closure.json ─▶ new baseline ─▶ reload + READY re-eval
        │  (all wave members done)
        ▼
WAVE COMPLETE (G5) ─▶ REGENERATE ─▶ next wave opens
        │  (SPECIFIED = 0)
        ▼
FULL COMPLETE (G6) ─▶ REGENERATE ─▶ terminal (LEVEL-5)
```

---

## 4. Regeneration procedure (controller-triggered)

| Step | Action | Guard |
|---|---|---|
| RG-1 | Freeze the completed batch; record pre-regeneration baseline hash | batch CERTIFIED |
| RG-2 | Invoke closure engine to recompute `closure.json` | integrity preconditions (`08`) |
| RG-3 | Assert post-conditions: `gap_total=0`, invariants zero, SPECIFIED count decreased by exactly the batch size | fail-closed if violated |
| RG-4 | Publish new baseline as current Repository Truth | post-conditions hold |
| RG-5 | Reload (C1) + recompute states (C3) + READY (C4) | always |

If RG-3 fails (e.g., invariant regressed, SPECIFIED count wrong), regeneration is **rejected**, the batch is held, and governance is notified (`09`). No corrupt baseline is ever published.

---

## 5. Post-regeneration invariants

1. `gap_total = 0` and all 7 gap invariants remain 0 (Knowledge Once preserved).
2. `SPECIFIED_new = SPECIFIED_old − (objects certified in the completing unit)`.
3. `IMPLEMENTED_new ≥ IMPLEMENTED_old` (monotone realization).
4. No object regresses from a terminal-forward state except via explicit SUPERSEDED mapping.
5. The new baseline is immutable and hash-anchored; the prior baseline is retained for rollback (`05` §5).

---

## 6. Regeneration ↔ readiness coupling

Regeneration is the sole event that can change the READY set. Because READY is recomputed only after RG-5, the controller can never act on stale truth:

```
Wave-01 batch CERTIFIED → G4/G5 REGENERATE → SPECIFIED(LAW)=0
   → P1 for Wave-02 now holds → Wave-02 becomes READY → next batch
```

---

## 7. Determinism attestation

Regeneration triggers (G1–G6), cadence (batch-primary), and post-conditions are fixed rules. Given identical batch outcomes, regeneration produces an identical new baseline. No manual regeneration path exists; every regeneration is logged with pre/post baseline hashes (C12).

---
*End of 07-REPOSITORY-REGENERATION.md*
