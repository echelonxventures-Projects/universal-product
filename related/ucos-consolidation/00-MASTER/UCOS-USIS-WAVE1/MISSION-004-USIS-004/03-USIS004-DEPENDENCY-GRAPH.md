# 03 — USIS-004 DEPENDENCY GRAPH

All existing edges are downward-only and acyclic (verified this session by
`ukbx twin --check` C-07 PASS). This analysis confirms USIS-004's dependency root
is satisfied.

---

## 1 — Established founding chain (registered, unchanged)

```
… SECURITY → USIS-GOV-000 (…000001) → USIS-001 (…000002) → USIS-002 (…000003)
                 Wave 0                 Wave 1·M1·07e0de4     Wave 1·M2·8db7d52
```

## 2 — Substrate-foundation dependency DAG (from establishment-package blueprints)

```
USIS-001  DEPENDS-ON  USIS-GOV-000
USIS-002  DEPENDS-ON  USIS-001
USIS-004  DEPENDS-ON  USIS-001 · USIS-002 · UCIC-001 · MIP-24-field-contract
USIS-003  DEPENDS-ON  USIS-002 · USIS-004
USIS-005  DEPENDS-ON  USIS-GOV-000 · USIS-002 · USIS-004
```

Topological order:
```
USIS-001 → USIS-002 → USIS-004 → { USIS-003 , USIS-005 }
```

**USIS-004 sits directly below USIS-002 and above USIS-003/USIS-005.** It has **no**
dependency on USIS-003 (no cycle) and its two hard corpus dependencies are already
established.

## 3 — USIS-004 dependency-root check

| Dependency | Class | Registered / satisfied? |
|---|---|:--:|
| USIS-001 (`UCOS-USIS-000002`) | hard corpus | ✅ ACTIVE, `07e0de4` |
| USIS-002 (`UCOS-USIS-000003`) | hard corpus | ✅ ACTIVE, `8db7d52` |
| UCIC-001 | governance/methodology anchor | ✅ external marker (precedented) |
| MIP per-part 24-field contract | frozen upstream anchor | ✅ external reference (precedented) |

**Dependency-root status: SATISFIED.** Both hard corpus prerequisites are
registered, ACTIVE, certified (10/10), and committed. The methodology/frozen
anchors resolve as external spine markers — the identical, precedented handling
used by USIS-001 and USIS-002 (whose only registered `Depends-On` corpus edges were
to their predecessors, with UCIC-001/LAW Ω∞-000/MIP as external markers). **No
remaining upstream blocker.**

## 4 — Parent / authorization chain (for the eventual USIS-004)

- **Parent (structural):** program root `USIS-GOV-000` (`UCOS-USIS-000001`),
  non-chained option (a) — the established USIS precedent.
- **Depends-On (metadata):** USIS-001 **and** USIS-002 (both registered → both
  resolve; 0 unmet).
- **Authorized-By:** USIS-001 / USIS-GOV-000 (NONE-DERIVED authority chain).
- **Realizes:** LAW USIS-08.
- All edges downward-only; adding USIS-004 preserves acyclicity (C-07).

## 5 — Downstream dependents of USIS-004

| Dependent | Relationship | Effect of establishing USIS-004 |
|---|---|---|
| USIS-003 (Science Catalog) | `Depends-On USIS-004` | **unblocks USIS-003** (its NOT-AUTHORIZED blocker B-1 clears) |
| USIS-005 (Structure Spec) | `Depends-On USIS-004` | prerequisite satisfied for a later USIS-005 |
| All Wave-2+ capabilities | conform to USIS-004 (LAW USIS-08) | meta-model spine available for every future capability |

## 6 — Ordering invariants (fail-closed)

- **Strict downward order:** USIS-004 may only `Depends-On` already-registered nodes
  — USIS-001 ✅, USIS-002 ✅ (UCIC-001 Stage 2 / USIS-011 obligation 14 satisfied).
- **No forward reference:** USIS-004 declares no dependency on any unregistered
  artifact (it does **not** depend on USIS-003/005).
- **Acyclicity:** re-proven each build by `ukbx twin --check` C-07.

**Graph verdict:** the dependency graph is **acyclic and downward-only**, and
**USIS-004's dependency root is fully satisfied**. Adding USIS-004 as a
child/dependent of USIS-002 (and USIS-001) introduces no cycle and no forward
reference.
