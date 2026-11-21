# 02 — RELATIONSHIP MATRIX

> **Mission:** IAC-001C · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Relationship types × direction × establishing field × cardinality, derived from authored CKO headers.

---

## 1. Matrix (type × inverse × source field × count)

| # | Relationship | Inverse | Establishing field | Edge count (raw) | Source-node count |
|---|---|---|---|---|---|
| 1 | Depends-On | Required-By | `DEPENDS-ON` | (in 1,536 resolved dep edges) | 150 |
| 2 | Derives-Authority-From | Confers-Authority-To | `DERIVES AUTHORITY FROM` | ↑ | 10 |
| 3 | Parent | Child | `PARENT` | ↑ | 4 |
| 4 | Governed-By | Governs | `GOVERNED BY` | — | 9 (+ prose `AUTHORITY`) |
| 5 | Realizes | Realized-By | `REALIZES` | — | 7 |
| 6 | Supersedes | Superseded-By | `SUPERSEDES` / `SUPERSEDED BY` | — | 4 |
| 7 | Contains | Contained-By | path + program/band containment | structural | all |
| 8 | References | Referenced-By | `REFERENCES` / prose | pervasive | — |

Total authored edges across all types: **1,976**. The dependency-defining subset (types 1–3) yields **1,536 resolved in-corpus edges** + 36 external/anchor targets (`03` §3).

## 2. Directionality invariant (downward-only)

Every relationship is **downward-only** by constitutional design: a subordinate declares its authority/parent/dependency *upward* toward roots; roots never declare downward into subordinates. This is what guarantees the graph is acyclic (`03`). Observed in headers, e.g. `CEP-005 DERIVES AUTHORITY FROM CEP-000..004`; `USIS-001 DEPENDS-ON USIS-GOV-000`.

## 3. Cardinality

- Each node has **≥1** upward relationship (dependency/parent/authority) **or** is a declared root (176 L0 nodes with no in-corpus dependency).
- No node declares a downward `Contains` edge that conflicts with a child's upward `Parent`/`DependsOn` (no contradiction found).

## 4. Determination

> Relationship matrix is complete and internally directional (downward-only). Feeds `03`–`08`.

---
*End of 02-RELATIONSHIP-MATRIX.md*
