# CONST-14 — Repository State Transition Matrix

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Companion to CONST-05 (Repository State Machine). Enumerates legal (L) and prohibited (P) transitions.

## 1. Transition Matrix (from → to)

States: S1 DISCOVERED, S2 REGISTERED, S3 REPRESENTED, S4 SPECIFIED, S5 GOVERNED, S6 PLANNED,
S7 IMPLEMENTED, S8 VALIDATED, S9 CERTIFIED, S10 ASSIMILATED, REJ REJECTED, SUP SUPERSEDED,
D1 REPOSITORY COMPLETE, D2 VISION COMPLETE, D3 FULLY CLOSED.

| from \ to | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | REJ | SUP | D1 | D2 | D3 |
|-----------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---:|:---:|:---:|:--:|:--:|:--:|
| S1 | L | P | P | P | P | P | P | P | P | L | L | P | P | P |
| S2 | — | L | P | P | P | P | P | P | P | L | L | P | P | P |
| S3 | — | — | L | L | P | P | P | P | P | L | L | P | P | P |
| S4 | — | — | — | L | P | P | P | P | P | L | L | P | P | P |
| S5 | — | — | — | — | L | P | P | P | P | L | L | L* | P | P |
| S6 | — | — | — | — | — | L | P | P | P | L | L | P | P | P |
| S7 | — | — | — | — | — | — | L | P | P | L | L | P | P | P |
| S8 | — | — | — | — | — | — | — | L | P | L | L | P | P | P |
| S9 | — | — | — | — | — | — | — | — | L | L | L | P | P | P |
| S10 | — | — | — | — | — | — | — | — | — | P | L | P | L** | P |
| D1 | — | — | — | — | — | — | — | — | — | — | — | — | — | P*** |
| D2 | — | — | — | — | — | — | — | — | — | — | — | — | — | P*** |

Notes:
- `*` S5→D1: roll-up only when ALL Domain-A concepts satisfy criteria and `gap_total==0`.
- `**` S10→D2: roll-up only when ALL Domain-B concepts assimilated and `gap_total==0`.
- `***` D1→D3 or D2→D3: legal ONLY when the *other* domain is also complete (D1 ∧ D2). A single
  domain never transitions to D3.

## 2. Absolute Prohibitions (P)

- Any jump skipping the S1→S2→S3 homing spine.
- Any advance to S10/D1/D2/D3 without corresponding engine evidence (fail-closed).
- S9/S10 regression except via SUP (with successor).
- D3 from a single domain.

## 3. CURRENT POSITIONS (baseline b67a720)

| Subject | State |
|---------|-------|
| Domain A (aggregate) | D1 REPOSITORY COMPLETE |
| Domain B (aggregate) | S6 PLANNED (planning complete); 110 items pre-S10 |
| System | NOT D3 |

## 4. DETERMINATION

Transitions are frozen. Current legal next transition for the system is D2 (upon Domain-B
assimilation), then D1 ∧ D2 ⇒ D3. No prohibited transition has occurred.
