# 13 — Frozen Decision Register

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Register the architectural decisions that are **FROZEN** at baseline v1.0 — the invariants implementation must not revisit. Each is stated with evidence and the authority that froze it. Changing any requires a proven constitutional defect + Change Control (doc 07/14).

## 1. Frozen Decision Register (FD)

| FD | Frozen decision | Evidence | Frozen by |
|---|---|---|---|
| FD-01 | UKB is the single Repository Truth; derived tools never become truth | CONST-01 §1 | CLOSURE-006 |
| FD-02 | Knowledge Once — one canonical home per concept; no duplicate canonical stores | CONST-01; `duplicate_canonical_homes=0` | CLOSURE-006 |
| FD-03 | Single Authority / Single Canonical Registry (UKB) | CONST-01/16 | CLOSURE-006 |
| FD-04 | Fail-Closed governance — absence of evidence never yields a positive claim | CONST-01 | CLOSURE-006 |
| FD-05 | Analysis ≠ Authority (Prohibition of Conflation) | CONST-01 §3 | CLOSURE-006 |
| FD-06 | The realization spine EL-1→RL-F2→PL-F2→DF-2→SF-2→AF-1→Band-13→Products (downward-only DAG) | doc 05; EA/UAM-001 | EC-1/EC-2/EC-3 |
| FD-07 | Reuse by reference (ENG-005); no lower-layer redefinition | per-unit UIL/UAL/USL-02 | EC-3 UCIC-001 |
| FD-08 | Founding graphs are acyclic (three-colour DFS proof) | band unit C5 rows | EC-3 |
| FD-09 | 8-stage closure pipeline | CONST-08 | CLOSURE-006 |
| FD-10 | Repository lifecycle / state machine | CONST-05/09 | CLOSURE-006 |
| FD-11 | EL-1 ontology (`ENG-000`+`ENG-001…005`) as canonical ontology | EC-1 certification; `07-ENGINEERING` | EC-1 |
| FD-12 | PL-F2 platform closed baseline (EC-2) | EC2-PROGRAM-CLOSURE-CERTIFICATION | EC-2 |
| FD-13 | Band 11 (Service) immutable baseline `deb2694f…` | EC3-B11-U13 | EC-3 |
| FD-14 | Band 12 (Application) immutable baseline `beff9ed3…` | EC3-B12-U13 | EC-3 |
| FD-15 | Foundational corpus (13 + 2 FINAL) frozen | `99-FREEZE/FREEZE-NOTICE.md` | 99-FREEZE |
| FD-16 | CCE ten-gate + UCIC-001 15-stage realization discipline | every band unit | EC-3 |
| FD-17 | Measurement is separated from decision; permanent measurement authority = UMA (design) | UMA doc 01; CLOSURE-007 §05 | UMA design |
| FD-18 | Determinism / replayability / byte-identical regeneration | determinism CI; band rows | EC-1/EC-3 |

## 2. Non-Frozen (explicitly still open — not in this register)

To avoid overstatement, these are **not** frozen at v1.0 (recorded in doc 03):
- Band-13 freeze (EC3-B13-U12) — realization certified, freeze pending.
- UMA runtime instantiation — design frozen (doc), runtime not built.
- Constitutional finality — DR-RAT-11 BLOCKED.
- Products — implementation era.

## 3. Immutability Rule

Each FD is immutable at v1.0. A change requires: (a) proof of a constitutional defect (doc 07 §4), (b) full Change Control, (c) CEP-009 amendment + CEP-006 ratification where the decision is constitutional. No FD may be altered by implementation (doc 11 T-1/T-5).

## 4. Determination

**FROZEN DECISION REGISTER IS ESTABLISHED (FD-01…FD-18).** The architectural invariants are registered with evidence and freezing authority; the still-open decisions are explicitly excluded to avoid overstatement (fail-closed). Implementation consumes these decisions and may not revisit them absent a proven defect.

*END — 13 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
