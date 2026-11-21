# CONST-05 — Repository State Machine

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Fail-Closed · Deterministic · Evidence Before Conclusion

---

## 1. Purpose

Define the official, frozen state machine every concept and every closure domain traverses.
States are ordered; transitions are constrained; prohibited transitions are enumerated.

## 2. Official States

| # | State | Meaning |
|---|-------|---------|
| S1 | DISCOVERED | Concept detected in some source (conversation/upload/vision/repo). |
| S2 | REGISTERED | Concept recorded in the canonical registry (UKB). |
| S3 | REPRESENTED | Concept has a canonical home (Knowledge Once satisfied). |
| S4 | SPECIFIED | Concept constitutionally specified. |
| S5 | GOVERNED | Concept under governance authority. |
| S6 | PLANNED | Concept scheduled in a plan/wave. |
| S7 | IMPLEMENTED | Concept realized in code with evidence. |
| S8 | VALIDATED | Concept passes structural + referential validation. |
| S9 | CERTIFIED | Concept independently certified. |
| S10 | ASSIMILATED | Concept fully in Repository Truth (no external-only residue). |
| D1 | REPOSITORY COMPLETE | Domain A success criteria met (integrity CLOSED). |
| D2 | VISION COMPLETE | Domain B success criteria met (assimilation CLOSED). |
| D3 | FULLY CLOSED | D1 **and** D2 both satisfied. |

Note: S4/S5/S6/S7 are not strictly linear — a concept may be SPECIFIED without being IMPLEMENTED
(disposition SPECIFIED) or IMPLEMENTED then retro-GOVERNED. Ordering expresses maturity, not a
mandatory single path. Terminal exclusions: REJECTED and SUPERSEDED are absorbing side-states.

## 3. Legal Transitions

- S1 → S2 → S3 (mandatory homing spine; enforced by Knowledge Once).
- S3 → S4 → S5 (specification then governance).
- S5 → S6 → S7 (planning then implementation) — OR S5 → (DEFERRED) side-state.
- S7 → S8 → S9 (validate then certify).
- S9 → S10 (assimilation once no external-only residue remains).
- Domain roll-ups: all Domain-A concepts ≥ S5 with 0 gaps ⇒ D1. All Domain-B concepts ≥ S10 ⇒ D2.
- D1 ∧ D2 ⇒ D3.
- Any state → REJECTED (with recorded rationale) or → SUPERSEDED (with canonical successor).

## 4. Prohibited Transitions

- S1 → S7+ (DISCOVERED cannot jump to IMPLEMENTED/VALIDATED/CERTIFIED — no bypass of homing).
- Any → S10 (ASSIMILATED) while an external-only gap for that concept exists (fail-closed).
- Any → D1/D2/D3 without the corresponding engine evidence (no inferred closure).
- Any → CERTIFIED without VALIDATED evidence.
- D1 → D3 without D2 (closure of one domain never implies the other).
- Direct insertion into REPRESENTED/GOVERNED bypassing DISCOVERED→REGISTERED (no direct insertion;
  see CONST-10).
- Regression from CERTIFIED/ASSIMILATED except via explicit SUPERSEDED with successor.

## 5. Fail-Closed Rule

A domain remains in its pre-completion state until evidence proves every success criterion. Absence
of evidence never advances a state.

## 6. CURRENT STATE (baseline b67a720)

- **Domain A:** D1 = REPOSITORY COMPLETE (integrity CLOSED, 398/0 gaps).
- **Domain B:** below S10 — 110 concepts not yet ASSIMILATED; planning (S6-equivalent) COMPLETE.
  Therefore **NOT** D2.
- **System:** NOT D3 (FULLY CLOSED) because D2 is unmet.

## 7. DETERMINATION

The repository is **REPOSITORY COMPLETE (D1)** but **NOT VISION COMPLETE (D2)**, hence **NOT FULLY
CLOSED (D3)**. Reported per the transition matrix in CONST-14.
