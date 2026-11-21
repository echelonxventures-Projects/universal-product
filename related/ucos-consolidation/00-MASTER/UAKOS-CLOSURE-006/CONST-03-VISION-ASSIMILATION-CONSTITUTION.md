# CONST-03 — Vision Assimilation Constitution (DOMAIN B)

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Canonical evidence: `00-MASTER/UAKOS-CLOSURE-002/phase2.json` (PHASE-002 analysis) and
> `phase3.json` (PHASE-003 planning). Both derived, AUTHORITY=NONE.
> Fail-Closed · Evidence Before Conclusion

---

## 1. Definition

**Vision Assimilation** is the assimilation of *external* knowledge into Repository Truth. It
answers: "Has all discovered intent — conversations, uploaded documents, vision documents,
historical architecture, future architecture, external constitutional knowledge — been brought
into the governed corpus?"

It is **independent** of Repository Integrity (CONST-02). Domain B being NOT-CLOSED does **not**
diminish Domain A being CLOSED.

## 2. Purpose

Ensure the repository eventually represents the *entire* discovered vision, not merely the
already-governed subset.

## 3. Scope

- IN: the full discovered concept graph (co-occurrence over all sources), including conversation-
  and upload-sourced concepts not yet homed.
- OUT: internal governed-only correctness — that is Domain A.

## 4. Authority

- **Analytical authority:** `phase2_engine.py` → `phase2.json` (PHASE-002). Builds the
  co-occurrence concept graph and enumerates enrichment gaps. Derived; non-authoritative.
- **Planning authority:** `phase3_engine.py` → `phase3.json` (PHASE-003). Plans enrichment
  waves. Derived; non-authoritative.
- **Governing authority:** UKB — sole owner of Repository Truth; `ukb validate` is the gate.

## 5. Must-Verify Invariants

| Invariant | Metric (phase2.json) | Target |
|-----------|----------------------|--------|
| Full-graph closure | `determination` | CLOSED |
| No open enrichment | `gap_total` / `open_enrichment_items` | 0 |
| Conversation assimilation | `gaps.conversation_only` | 0 |
| Graph coverage | `cooccurrence.nodes` = `concept_total` | equal |

## 6. Evidence Requirements

Deterministic `phase2.json` (graph + gaps) and `phase3.json` (planning) present at baseline; the
concept graph derived from `00-BOOK/DATA/relationships.json`.

## 7. Success Criteria

- Domain B `determination = CLOSED`
- `gap_total = 0`, `conversation_only = 0`, `open_enrichment_items = 0`

## 8. Failure Criteria (CURRENTLY MET — Domain B is NOT closed)

Any open enrichment item. Present state is fail-closed NOT-CLOSED.

## 9. Dependencies

Knowledge Assimilation · Conversation Assimilation · Upload Assimilation (CONST-01 §2.6–2.8) ·
Continuous Knowledge Ingestion (UAKOS-CLOSURE-005).

## 10. Lifecycle

Continuous ingestion. Enrichment executes via UAKOS-CLOSURE-003 waves; each item is homed and
validated (`ukb validate`) before it leaves the gap set. Never closed speculatively.

---

## 11. CURRENT EVIDENCE (baseline b67a720)

```
phase2.json (PHASE-002)
  concept_total       : 506
  cooccurrence        : nodes 506 · edges 52276
  determination       : NOT-CLOSED
  gap_total           : 110
  gaps.conversation_only : 108   (+2 further gap items → 110 total)
  open_enrichment_items  : 110
  source              : 00-BOOK/DATA/relationships.json

phase3.json (PHASE-003)
  determination   : "PLANNING-COMPLETE · REPOSITORY NOT-CLOSED (fail-closed)"
  planning_complete : true
  planned_total   : 110   (organized into execution waves; wave1 Critical, wave2 High)
  validation_required : "ukb validate"  (+ referential integrity for Critical items)
  head_commit     : b67a720
```

## 12. DETERMINATION

**Vision Assimilation (Domain B) = NOT-CLOSED.** 110 open enrichment items remain (108
conversation-only + 2). Execution planning is COMPLETE (phase3), but execution/enrichment is NOT
performed by this mission. This determination is reported independently of Domain A's CLOSED state.

**Independence statement (mandatory):** Repository Integrity is CLOSED **and** Vision Assimilation
is NOT-CLOSED. Both are true simultaneously and neither overrides the other.
