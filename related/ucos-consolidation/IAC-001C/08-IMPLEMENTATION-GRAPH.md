# 08 — IMPLEMENTATION GRAPH

> **Mission:** IAC-001C · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Determine ONLY whether a **deterministic implementation order** can be mathematically derived from the certified relationship graph. **Readiness is NOT evaluated.**

---

## 1. Derivability result

The dependency graph (`03`) is a **DAG** (335 nodes, 1,536 edges, **0 cycles**). A deterministic topological order therefore **exists** and is computable by longest-path level assignment (dependencies-first).

## 2. Implementation levels (topological)

Level = 0 for nodes with no in-corpus dependency; otherwise 1 + max(level of dependencies). Distribution:

| Band | Levels | Nodes |
|---|---|---|
| Roots | **L0** | **176** (independent) |
| Early | L1–L10 | 41 |
| Mid | L11–L45 | ~55 |
| Deep | L46–L59 | ~63 |
| **Max depth** | **L59** | terminal nodes |

(Full per-level counts computed read-only; each level is a valid parallel execution stratum.)

## 3. Node classes for ordering

| Class | Definition | Count |
|---|---|---|
| **Independent nodes** | no in-corpus dependency (L0) | **176** |
| **Parallel nodes** | share a topological level (no mutual dependency) | all within each level |
| **Dependent nodes** | ≥1 dependency | 159 |
| **Blocked nodes** (by cycle) | in an unresolved circular dependency | **0** |
| **Externally-gated nodes** | depend on a recognized external anchor (e.g. `DR-RAT-11`) | small set (documented in `03` §4) — gated by design, not by a graph defect |

## 4. Determinism

Because the graph is acyclic and every edge is authored (deterministic input), the level assignment is **unique up to intra-level ordering**, and intra-level order is itself deterministically fixable by canonical ID sort. Therefore a **deterministic implementation order is mathematically derivable** from the certified relationship graph.

## 5. Scope discipline

This confirms *derivability of order only*. It makes **no** claim that any node is ready, built, validated, or authorized to execute. Externally-gated nodes (e.g. behind `DR-RAT-11`) remain orderable; their gating is an external-authority matter, not a graph defect.

## 6. Determination

> **VERIFY 8 (Implementation Order Derivation): PASS.**
> A deterministic implementation graph, levels (L0–L59), independent/parallel/dependent node sets, and zero cycle-blocked nodes are all derivable from the certified relationship graph.

---
*End of 08-IMPLEMENTATION-GRAPH.md*
