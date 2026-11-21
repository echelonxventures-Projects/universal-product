# 05 — IMPLEMENTATION GRAPH

> **Mission:** IAC-001E · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Derive the deterministic implementation graph; verify sequential/parallel/independent/blocked nodes + critical path. (Inherits the certified graph from IAC-001C.)

---

## 1. Deterministic graph (from IAC-001C, canonical-only)

| Property | Value |
|---|---|
| Nodes | 335 CKOs |
| Resolved dependency edges | 1,536 |
| Cycles | **0** (acyclic ⇒ topological order exists) |
| Topological levels | **L0 … L59** |
| Independent nodes (L0) | **176** |
| Dependent nodes | 159 |

## 2. Node classes for execution

| Class | Definition | Result |
|---|---|---|
| **Independent nodes** | no in-corpus dependency (L0) | 176 — implementable first, in parallel |
| **Parallel nodes** | share a topological level, no mutual dependency | every level is a parallel stratum |
| **Sequential nodes** | on a dependency chain (level k depends on <k) | 159 across L1–L59 |
| **Blocked nodes** (by cycle) | in an unresolved cycle | **0** |
| **Externally-gated nodes** | behind `DR-RAT-11` (finality) | orderable; gated by design, not defect |

## 3. Critical path

The critical path is the longest dependency chain, terminating at **L59** (depth 60). It is deterministically identifiable as the maximal-level spine; all other chains are shorter and can be scheduled in parallel around it.

## 4. Determinism guarantee

- Inputs are authored edges (deterministic).
- Acyclicity ⇒ a valid topological order exists.
- Intra-level order is fixable by canonical-ID sort ⇒ the schedule is **fully deterministic and reproducible**.
- USIS-004 Capability Meta-Model makes per-node realization "uniform, deterministic, machine-checkable."

## 5. Determination

> **VERIFY 5 (Implementation Graph): PASS.**
> A deterministic implementation graph with sequential/parallel/independent node sets, zero cycle-blocked nodes, and an identifiable critical path is derivable.

---
*End of 05-IMPLEMENTATION-GRAPH.md*
