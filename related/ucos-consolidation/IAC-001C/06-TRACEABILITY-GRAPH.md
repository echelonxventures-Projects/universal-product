# 06 — TRACEABILITY GRAPH

> **Mission:** IAC-001C · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Every CKO must be traceable through the complete constitutional graph.

---

## 1. Traceability construction

Traceability composes the dependency (`03`), composition (`04`), and realization (`05`) graphs into one directed graph rooted at the constitutional apex (CEP-000) and the program roots (`USIS-GOV-000`, band `*-GOV-000`, EC-3 admissions). Governed by `GOV-002` (Constitution→Implementation Traceability) + `CEP-008` (Evidence & Traceability).

## 2. Reachability result

- All **335** CKO nodes participate in the graph (each has ≥1 authored relationship or is a declared L0 root).
- From every node, an upward traversal (dependency ∪ authority ∪ parent) reaches an L0 root in ≤59 hops (topological depth), with **0 cycles** — every node is root-reachable.
- Downward, roots reach their subordinates via inverse edges; no node is unreachable/detached.

## 3. Four-link chain (per IAC-001B, now graph-verified)

`Knowledge Object → Repository Home → Canonical Owner → Constitutional Authority` — every CKO satisfies this chain, and the authority link now extends transitively to the apex via the acyclic dependency/authority graph.

## 4. Worked spine

`USIS-003 → USIS-002/USIS-004 → USIS-GOV-000 → LAW Ω∞-000` (apex law). `CEP-005 → CEP-004 → … → CEP-000` (apex charter). Band CKOs → band `*-GOV-000` → EC-3 admission → CEP stack. All terminate at roots.

## 5. Determination

> **VERIFY 5 (Traceability Graph): PASS.**
> Every Canonical Knowledge Object is traceable through the complete graph to a constitutional root; no detached or unreachable node.

---
*End of 06-TRACEABILITY-GRAPH.md*
