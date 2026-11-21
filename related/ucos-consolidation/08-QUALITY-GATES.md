# 08 — QUALITY GATES

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Gates are **automatic, derived, fail-closed**. A transition proceeds only if its gate passes.

---

## 1. Gate engine placement

The Quality Gate Engine (C11) sits on **every** lifecycle transition (`02`, `06`). No object changes state without passing the gate(s) attached to that transition. Failing any gate → transition rejected, object held, event logged (C12), governance notified if terminal (`09`).

```
transition request ─▶ [C11 gate set] ─▶ allow → commit transition
                                     └─ reject → hold + log + (escalate)
```

---

## 2. Gate catalogue (mission-mandated preventions)

| Gate | Prevents | Derived check | Attached to |
|---|---|---|---|
| **Q1 Duplicate-implementation** | duplicate implementation | object not already `in_code=true`; no other object shares its canonical id | READY→EXECUTING, EXECUTING→IMPLEMENTED |
| **Q2 Duplicate-ownership** | duplicate ownership | `duplicate_canonical_homes=0`; object's `files[0]` is its unique home | READY→EXECUTING; regeneration RG-3 |
| **Q3 Dependency-violation** | dependency-order violation | P1 holds (all lower waves IMPLEMENTED); batch is single-wave (B1) | SPECIFIED→READY, READY→EXECUTING, batch cut |
| **Q4 Orphan-implementation** | orphan implementation | `homed=true`, `orphan=false`, `files[0]` non-empty | READY→EXECUTING; RG-3 |
| **Q5 Invalid-validation** | invalid validation | validation owner present (`verify.sh`); `trace.implementation=true` before VALIDATED | IMPLEMENTED→VALIDATED |
| **Q6 Invalid-certification** | invalid certification | EC-3 gate owner present; object VALIDATED before CERTIFIED; `certified=true` only after gate pass | VALIDATED→CERTIFIED |
| **Q7 Invalid-traceability** | invalid traceability | `id→artifact` binding resolvable at canonical home; `homed=true` | IMPLEMENTED→VALIDATED; RG-3 |
| **Q8 Illegal-transition** | invalid lifecycle transition | transition ∈ legal table (`06` §2); else reject | every transition |

---

## 3. Gate composition per transition

| Transition | Gates applied |
|---|---|
| SPECIFIED → READY | Q3, Q8 |
| READY → EXECUTING | Q1, Q2, Q3, Q4, Q8 |
| EXECUTING → IMPLEMENTED | Q1, Q4, Q8 |
| IMPLEMENTED → VALIDATED | Q5, Q7, Q8 |
| VALIDATED → CERTIFIED | Q6, Q8 |
| batch cut (`05`) | Q1, Q2, Q3, Q4 (per member) |
| regeneration RG-3 (`07`) | Q2, Q4, Q7 + invariant post-conditions |
| any → SUPERSEDED / ARCHIVED | Q8 |

---

## 4. Fail-closed semantics

| Property | Behavior |
|---|---|
| Default | **deny** — a transition is allowed only on explicit gate pass |
| Missing evidence | treated as failure (e.g., missing validation owner → Q5 fails) |
| Ambiguity | treated as failure (e.g., duplicate home → Q2 fails) |
| Illegal transition | hard reject (Q8), never queued for retry as-is |
| Terminal failure | escalate to governance (`09`); never silently drop |

---

## 5. Repository-Truth anchors (current baseline)

The gates are satisfiable at `ab78f35` because the reconciled truth already guarantees the global preconditions:

| Global precondition | Value @ `ab78f35` | Supports gate |
|---|---|---|
| `gap_total` | 0 | Q3, Q4 |
| `duplicate_canonical_homes` | 0 | Q2 |
| `orphan_concepts` | 0 | Q4 |
| `in_repo_unhomed` / `not_homed_concepts` | 0 | Q4, Q7 |
| validation harness `verify.sh` | present | Q5 |
| EC-3 gate | defined | Q6 |

Thus, per-object gate evaluation reduces to local checks; the global invariants are already zero.

---

## 6. Gate outcomes & logging

| Outcome | Action | Log (C12) |
|---|---|---|
| PASS | commit transition | `GATE:PASS <gate> <id> <baseline>` |
| REJECT (recoverable) | hold; route to retry (`05` R1–R3) | `GATE:REJECT <gate> <id> <reason>` |
| REJECT (illegal/terminal) | hard stop; escalate | `GATE:ILLEGAL <id>` / `GATE:TERMINAL <id>` |

---

## 7. Determinism attestation

Every gate is a pure predicate over Repository-Truth fields + the legal-transition table. Gates carry no manual override. Identical truth + identical transition ⇒ identical gate verdict. All verdicts are logged.

---
*End of 08-QUALITY-GATES.md*
