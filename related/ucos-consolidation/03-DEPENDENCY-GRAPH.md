# 03 — DEPENDENCY GRAPH

> **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Assumptions flagged explicitly.

---

## 1. Scope

This graph expresses the constitutional dependency relationships among the three verified root causes (R1, R2, R3), their derivatives (D1–D3), and the terminal verdict (I1). It answers: *what must be true before what.*

---

## 2. Constitutional dependency graph

```
LEVEL LADDER (monotone)          BLOCKER DEPENDENCY EDGES
─────────────────────           ───────────────────────────────

 L1 Knowledge Complete   ✔
        │
 L2 Architecture Cmpl.   ✔
        │
 L3 Repo Truth Certified ✔  ← closure.json determination=CLOSED @ ab78f35
        │
 L4 Implementation Ready ✔  ← every CKO has a terminating, acyclic impl path
        │
 ══════ current ceiling of achieved contiguous level = L4 ══════
        │
 L5 Implementation Cmpl. X   ← BLOCKED BY  R1  (90 SPECIFIED unrealized)
        │
 L6 Validation Complete  ✗  ← BLOCKED BY  D1 (→R1)
        │
 L7 Certification Cmpl.  ✗  ← BLOCKED BY  R2 (74) + D2 (→R1) + D3 (→R1)
        │
 L8 Impl. Authority Cert ✗  ← BLOCKED BY  R3 (DR-RAT-11, EXTERNAL)
```

### Edge list (predecessor ⇒ dependent)

| Predecessor | Dependent | Type | Evidence |
|---|---|---|---|
| R1 (realize span) | L5 Implementation Complete | hard, in-corpus | SPECIFIED→IMPLEMENTED required |
| R1 | D1 Validation | hard | cannot validate unrealized |
| R1 | D2 Certification-of-span | hard | cannot certify unrealized |
| R1 | D3 Traceability | hard | impl artifact must exist to trace |
| D1 | L6 Validation Complete | hard | validation completion |
| R2 (certify 74) | L7 Certification Complete | hard, in-corpus, **parallel to R1** | 74 uncertified must certify |
| D2 | L7 | hard | span-certification |
| D3 | L7 | hard | traceability closure |
| L7 (provisional) | L8 | governance | absolute finality gate |
| R3 (DR-RAT-11) | L8 Impl. Authority Certified | hard, **EXTERNAL** | out-of-corpus constituent act |

---

## 3. Acyclicity

The in-corpus dependency structure is **acyclic**, confirmed on two independent grounds:

1. **Ladder monotonicity.** L1→L8 is a strict total order; no blocker depends on a higher level.
2. **Register construction.** `38-DEPENDENCY-REGISTER.md` (though from superseded baseline `b67a720`, `AUTHORITY=NONE`) expresses dependencies as constitutional-layer gates (predecessor class + its wave) forming a strict partial order over classes → acyclic by construction. No concept depends on a later-or-equal wave. **Assumption:** the current-baseline realization retains this same layered ordering; label as ASSUMPTION since the `38`/`40` registers have not been regenerated at `ab78f35`.

**No cycles exist.** Every in-corpus implementation path terminates.

---

## 4. R3 externality in the graph

R3 (DR-RAT-11) is drawn as an edge into **L8 only**. It has **no inbound in-corpus edge** (nothing in the repository can satisfy it) and **no edge into R1/R2/D1–D3** (it does not gate engineering realization or certification). This is the graph-level statement of "external, non-blocking for engineering; blocking only for absolute finality," corroborated by `PHASE-0.1-GOVERNANCE-ACTIVATION.md` (Bands 10–13 realized/certified under DR-RAT-11 BLOCKED).

---

## 5. Critical path

```
R1  →  D1  →  (L6)  →  D2/D3 + R2  →  (L7 provisional)  →  R3  →  (L8 absolute)
└── longest in-corpus chain ──────────────────────────┘   └ external ┘
```

- **Longest in-corpus chain:** R1 → D1 → D2/D3 → L7. R2 runs in parallel and is not on the critical path unless it out-sizes R1 (it does not — 74 certification actions vs 90 realizations plus validation).
- **Terminal external gate:** R3 sits after the entire in-corpus chain and cannot be shortened by any repository action.

---
*End of 03-DEPENDENCY-GRAPH.md*
