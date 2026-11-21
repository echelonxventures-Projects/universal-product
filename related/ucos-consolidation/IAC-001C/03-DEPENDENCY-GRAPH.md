# 03 — DEPENDENCY GRAPH

> **Mission:** IAC-001C · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Dependency graph over authored `DEPENDS-ON` + `DERIVES AUTHORITY FROM` + `PARENT` edges.

---

## 1. Graph metrics (read-only computation)

| Metric | Value |
|---|---|
| Nodes (CKOs) | 335 |
| Resolved in-corpus dependency edges | **1,536** |
| Unresolved targets (external anchors / enumerators) | 36 |
| **Circular dependencies (cycles)** | **0** |
| Topological depth | L0 … L59 |
| Independent nodes (no in-corpus dependency, L0) | **176** |
| Dependent nodes (≥1 dependency) | 159 |

## 2. Every dependency (closure)

Every inter-CKO `DEPENDS-ON`/`DERIVES-FROM`/`PARENT` edge resolves to an in-corpus node **or** to a recognized anchor (§4). Dependency closure holds: following dependencies from any node terminates at an L0 root (constitutions, program roots) within a finite number of hops — 0 cycles guarantees termination.

## 3. Missing / broken dependencies

**None.** No CKO declares a dependency on a canonical object that should exist but is absent from the corpus. Every unresolved target (§4) is an external anchor, an intra-document enumerator, a governance authority, or a naming-form variant that resolves — not a missing canonical node.

## 4. Unresolved targets (36) — classified (no unknown canonical dependency)

| Class | Count | Members | Disposition |
|---|---|---|---|
| Intra-document freeze-stream / sub-clause enumerators | ~18 | `AF-1/2/3`, `DF-1/2/3`, `SF-1/2/3`, `PL-F1/F2`, `RL-F2`, `IF-1`, `EL-1`, `ID-01`, `AUTH-06`, `CR-INF-003` | Internal enumerated requirement/freeze IDs inside band docs — not standalone CKOs |
| External / apex-law anchors | ~5 | `DR-RAT-11` (external finality act), `LAW USIS-00/08`, `S2-08`, `PHASE-003/003R`, `USIS-000` | Recognized out-of-corpus / higher-law anchors (per IAC-001A + prior missions) |
| Governance-authority instruments (referenced by name) | ~5 | `REG-AUTO-001`, `STATUS-001`, `UCI-001`, `GOV-READINESS-001`, `NEXT-PROGRAM-001` | Canonical governance processes referenced as authorities |
| Naming-form variants that DO resolve | ~3 | long-form `SECURITY-GOV-000-…`, `USIS-000`→`USIS-GOV-000`, `EC3-B13-U01` | Resolve to existing nodes under normalization |

## 5. Circular dependency

**Zero cycles.** DFS three-colour cycle detection over all 335 nodes and 1,536 edges found no back-edge. The downward-only constitutional dependency model (`02` §2) is upheld — no CKO depends (transitively) on itself.

## 6. Determination

> **VERIFY 2 (Dependency Graph): PASS.**
> Every dependency identified; closure holds; zero circular dependencies; zero missing/broken canonical dependencies. The 36 unresolved targets are documented anchors/enumerators, not unknown canonical dependencies.

---
*End of 03-DEPENDENCY-GRAPH.md*
