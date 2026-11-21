# 05 — Dependency Graph

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Record the architectural dependency graph at baseline v1.0 — how strata and programs depend on one another — so implementation consumes them in a proven, acyclic order. This graph is *derived from evidence*, not designed here (mission: no redesign).

## 1. Realization Dependency Spine (frozen, acyclic, downward-only)

```
  00-SOURCE (VISION + CONSTITUTIONS)                [FROZEN]
        │ founds
        ▼
  CEP-000…010 (Constitutional Engineering)          [ACTIVE/governing]
        │ founds
        ▼
  Repository Truth / UKB / Knowledge Once           [ACTIVE — sole truth]
        │ measured-by (derived)
        ▼
  EL-1 (ontology/engine, ENG-000+001…005)           [EC-1 CERTIFIED]
        ▼
  RL-F2 (runtime)                                   [FROZEN]
        ▼
  PL-F2 (platform, EC-2)                            [CLOSED+FROZEN]
        ▼
  DF-2 (data, Band 10)                              [CERTIFIED-COMPLETE]
        ▼
  SF-2 (service, Band 11)                           [FROZEN]
        ▼
  AF-1 (application, Band 12)                        [FROZEN]
        ▼
  Band 13 (infrastructure)                          [REALIZATION CERT COMPLETE · U12 freeze pending]
        ▼
  Products                                          [FUTURE — implementation era]
```

Each layer **reuses** its predecessors *by reference* (ENG-005), redefining none — the invariant proven across every band unit (evidence: MCP-002 unit rows, "reused by reference, redefines none; UIL-02/UAL-02/USL-02"). The spine is a **DAG** (no cycles); this is a frozen architectural decision (doc 13).

## 2. Governance / Measurement Dependency Overlay

```
   UKB (truth) ──read──▶ Measurement (closure engines, derived / UMA design)
        ▲                      │ metrics
        │ governs              ▼
   Governance (CEP-002/GOV-*) ──consumes──▶ Validation ─▶ Certification
        ▲                                                     │
        └───────────────── ratification (DR-RAT-11 BLOCKED) ◀─┘
```

- Measurement **depends on** UKB (read-only); Governance/Validation/Certification **consume** measurement.
- Post-UMA-instantiation, the measurement dependency edge moves from `closure_engine.py` (derived) to UMA (doc 04; UMA doc 10). This is a **planned dependency migration**, not yet effected.

## 3. Program Dependency Chain (evidence)

```
00-SOURCE ─▶ CEP ─▶ CLOSURE-002 ─▶ 003/004/005 ─▶ CLOSURE-006 (CONST freeze) ─▶ CLOSURE-007 ─▶ UCOS-UMA-001 (design)
                                                              │
                                                              ▼
                                   EC-1 ─▶ EC-2 ─▶ EC-3 (Band10 ─▶ Band11 ─▶ Band12 ─▶ Band13) ─▶ MEP-05 closure
                                                                                            │
                                                          UCOS-AB-001 (this baseline) ◀──────┘ consumes all
```

## 4. Implementation Dependency Rules (consumed, not created)

| Rule | Statement | Evidence |
|---|---|---|
| DR-1 | A layer may realize only after its predecessor is CERTIFIED (or FROZEN) | AP-2…AP-5 band admissions |
| DR-2 | Reuse is by reference; no redefinition of a lower layer | per-unit UIL/UAL/USL-02 |
| DR-3 | Founding graphs within a band are acyclic (three-colour DFS proof) | Band unit rows (C5) |
| DR-4 | Freeze of a layer precedes go-live consumption of that layer | Band 11/12 freeze pattern |
| DR-5 | Measurement never founds truth; it depends on it | UMA doc 01; CONST-01 |

## 5. Cycle & Completeness Check (fail-closed)

- **Acyclicity:** the realization spine and program chain are DAGs (evidence: every band certified "founding graph acyclic"). No cycle exists at v1.0.
- **Completeness:** every baseline stratum B-01…B-20 (doc 01) appears as a node with resolved predecessors; the only open successor edge is Band 13 → freeze/MEP-05 and the planned UMA dependency migration — both recorded, none UNKNOWN.

## 6. Determination

**DEPENDENCY GRAPH IS COMPLETE AND ACYCLIC AT v1.0.** The realization spine, governance/measurement overlay, and program chain are evidenced DAGs. The two open edges (Band-13 freeze; planned UMA measurement-dependency migration) are explicitly recorded as future/planned, not hidden.

*END — 05 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
