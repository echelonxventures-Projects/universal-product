# CONST-08 — Pipeline Constitution

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Freezes the Repository Closure Pipeline. No parallel pipelines permitted.

---

## 1. Purpose

Freeze the single, canonical Repository Closure Pipeline. Future work may not introduce a parallel
or competing pipeline; it may only operate the stages defined here.

## 2. The Frozen Pipeline (8 stages)

| Stage | Name | Owner | Engine / gate | Authority |
|-------|------|-------|---------------|-----------|
| 1 | Discovery | CLOSURE-002 | source scan | derived |
| 2 | Canonical Reconciliation | CLOSURE-002 | `closure_engine.py` → `closure.json` | derived |
| 3 | Implementation Planning | CLOSURE-002 | `phase2_engine.py`/`phase3_engine.py` → phase2/phase3.json | derived |
| 4 | Governance | UKB | governance model | **UKB (authority)** |
| 5 | Repository Enrichment | CLOSURE-003 | enrichment waves | derived |
| 6 | Validation | CLOSURE-004 | `ukb validate` (+ referential integrity) | **UKB (authority)** |
| 7 | Certification | CLOSURE-004 | certification artifacts | CLOSURE-004 |
| 8 | Continuous Knowledge Assimilation | CLOSURE-005 | ingestion/monitoring | derived |

## 3. Pipeline Authority Rule (frozen)

- **No pipeline stage is an authority over Repository Truth.** Stages 1–3, 5, 8 are derived
  analytical/operational stages. Only UKB (stages 4 & 6 gate) owns Repository Truth.
- `closure_engine.py` = derived analytical pipeline (self-declared `AUTHORITY = NONE`).
- `phase2_engine.py` = planning/analysis stage (PHASE-002).
- `phase3_engine.py` = execution planning stage (PHASE-003).

## 4. Prohibitions

- No parallel pipeline may be introduced.
- No stage may mutate the frozen corpus during analysis (net-zero modification).
- No stage may issue closure the evidence does not support (fail-closed).

## 5. Determinism

Every stage MUST be deterministic and re-runnable, reproducing identical determinations at a fixed
baseline commit.

## 6. DETERMINATION

The 8-stage Repository Closure Pipeline is frozen. Stage roles and authority boundaries are
permanent. UKB is the sole authority; all engine stages are derived.
