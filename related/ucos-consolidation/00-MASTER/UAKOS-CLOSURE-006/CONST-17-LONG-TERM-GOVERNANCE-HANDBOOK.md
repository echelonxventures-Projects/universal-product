# CONST-17 — Long-Term Governance Handbook

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Operating manual for governing the frozen closure model over the long term.

---

## 1. Purpose

Provide the durable operating guidance a future maintainer needs to run the closure model without
redesign. It references the frozen constitutions; it does not restate them.

## 2. How to Read the Repository's State

1. Read `00-MASTER/UAKOS-CLOSURE-002/closure.json` → Domain A (Repository Integrity).
   - CLOSED iff `determination==CLOSED` and `gap_total==0`.
2. Read `phase2.json` → Domain B (Vision Assimilation) totals and gaps.
3. Read `phase3.json` → Domain B enrichment plan/waves.
4. Apply the Decision Matrix (CONST-13) and State Transition Matrix (CONST-14).
5. Never infer one domain's state from the other's (CONST-01 §3).

## 3. Routine Operations

| Task | How | Owner |
|------|-----|-------|
| Re-verify Domain A | `make closure` (deterministic re-run) | CL-002 tooling |
| Advance Domain B | Execute next enrichment wave, then `ukb validate` | CL-003 |
| Validate/Certify | Run validation, then certification artifacts | CL-004 |
| Ingest new knowledge | Conversation → ingestion funnel (CONST-10) | CL-005 |
| Confirm governance singularity | Re-check CONST-16 facts F1–F7 | UKB/governance |

## 4. Golden Rules (operator)

- **Fail-Closed:** if evidence is missing, the domain is NOT-CLOSED. Never assume.
- **Determinism:** any determination must reproduce on re-run at a fixed baseline.
- **Knowledge Once:** never create a second canonical home; dedupe at Canonical Review.
- **No bypass:** all new knowledge enters via the single funnel (CONST-10).
- **No redesign:** conform ideas to the pipeline; do not fork the pipeline (CONST-08).
- **Report independently:** always report A, B, Architectural Completeness, and D3 separately.

## 5. Escalation & Amendment

- Suspected competing authority/registry → treat as violation; halt; re-verify CONST-16.
- Constitutional amendment → only through the evolution path (Conversation → … → Repository Truth).

## 6. Health Signals (current, baseline b67a720)

| Signal | Value | Healthy? |
|--------|-------|----------|
| Domain A gaps | 0 | ✓ |
| Domain A dispositions cover | 398/398 | ✓ |
| Domain B open enrichment | 110 | in-progress (expected NOT-CLOSED) |
| Domain B planning complete | true | ✓ |
| Governance singularity | intact | ✓ |
| Determinism | reproducible | ✓ |

## 7. DETERMINATION

The closure model is operable long-term with no redesign. Steady-state for Domain A; wave-driven
progression for Domain B; single-funnel ingestion for all future knowledge.
