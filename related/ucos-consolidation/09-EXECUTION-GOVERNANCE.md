# 09 — EXECUTION GOVERNANCE MODEL

> **Mission:** IEC-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** DESIGN ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Governance guarantees that execution remains derived, auditable, and constitutionally bounded.

---

## 1. Governance principle

The controller governs *itself*: every selection, transition, gate verdict, and regeneration is a **derived, logged, reproducible** act. Governance does not add a human decision-maker into the execution path; it adds **accountability and bounds** so that the derived process cannot drift, cannot be manually steered, and can always be replayed.

**Prime directive:** *Implementation is never manually selected. Implementation is always repository-derived.* Governance enforces this directive structurally.

---

## 2. Separation of authorities

| Authority | Holds power over | Explicitly excluded from |
|---|---|---|
| **Repository Truth** (`closure.json`) | what exists, what is realized, what is certified | — (supreme for implementation) |
| **IMG-001 manifest** | the canonical unrealized inventory + waves + graph | cannot override truth |
| **UIEC controller** | *selection & sequencing* of work (derived) | cannot author knowledge/architecture; cannot pick work manually |
| **Quality Gate Engine** | permit/reject transitions | cannot invent state |
| **External constituent authority** (DR-RAT-11) | constitutional *finality* only (out-of-corpus) | cannot alter in-corpus implementation selection |
| **Human operator** | start/stop the tick; set fixed parameters (`MAX_BATCH`, `MAX_RETRY`) | **cannot select which object executes** |

The human operator advances or halts the loop and sets bounded parameters, but has **no work-selection input** — selection is a pure function of truth.

---

## 3. Governance ledger (C12)

Every controller event is appended to an immutable governance ledger:

| Logged event | Payload |
|---|---|
| Truth load | baseline hash, invariants snapshot |
| READY evaluation | object id, predicate vector (P1–P7), verdict |
| Batch cut | batch id, members, wave, baseline hash |
| State transition | id, from→to, trigger, gate verdicts |
| Gate verdict | gate id, id, PASS/REJECT, reason |
| Regeneration | pre-hash, post-hash, SPECIFIED delta, invariant post-conditions |
| Escalation | id, terminal-failure reason |

**Replayability:** given the ledger + the sequence of baselines, any third party can re-derive every selection and verify the controller never acted outside Repository Truth.

---

## 4. Governance controls

| Control | Rule |
|---|---|
| **No manual selection** | controller exposes no "implement object X" API; only `advance_tick()` |
| **Determinism** | same baseline ⇒ same READY set ⇒ same batch (verifiable via ledger replay) |
| **Fail-closed** | any unresolved predicate/gate halts the object; nothing advances speculatively |
| **Bounded autonomy** | `MAX_BATCH`, `MAX_RETRY` are fixed parameters, not per-run manual choices |
| **Escalation** | terminal failures (retry exhausted, RG-3 violation, illegal transition) escalate to governance for human *review*, never human *selection* |
| **Immutability** | ledger and published baselines are append-only / hash-anchored |
| **Constitutional boundary** | controller governs implementation only; finality (DR-RAT-11) remains external (IAC-001 `09`) |

---

## 5. Escalation model

```
recoverable reject  → retry loop (05 R1–R3)              [no human]
retry exhausted     → FAILED-terminal → ESCALATE         [human review]
RG-3 post-condition → regeneration rejected → ESCALATE   [human review]
illegal transition  → hard reject (Q8) → ESCALATE        [human review]
```

Human review may fix the underlying artifact/realizer and **re-admit** the object to the derived pipeline; it may never inject a hand-picked implementation or bypass a gate.

---

## 6. Roles & responsibilities

| Role | May | May not |
|---|---|---|
| Repository Truth | define reality | — |
| Controller (UIEC) | derive selection, drive lifecycle, trigger regeneration | author work, pick work |
| Gate Engine | allow/reject transitions | create state |
| Operator | start/stop tick, set fixed params, review escalations | select objects, bypass gates, edit truth |
| Constituent authority (external) | grant constitutional finality | alter implementation selection |

---

## 7. Governance conformance checklist

| Requirement | Mechanism | Status (design) |
|---|---|---|
| Execution dependency-derived | P1 + single-wave batches | ✔ designed |
| Never manually scheduled | no selection API; tick-only | ✔ designed |
| No architecture redesign | controller reads, never authors | ✔ designed |
| Auditable | governance ledger C12 | ✔ designed |
| Reproducible | pure-function selection | ✔ designed |
| Constitutionally bounded | truth-supreme; finality external | ✔ designed |

---

## 8. Determinism attestation

The governance model adds accountability without adding discretion to the execution path. Selection remains a pure function of Repository Truth; governance guarantees that property is observable, bounded, and replayable.

---
*End of 09-EXECUTION-GOVERNANCE.md*
