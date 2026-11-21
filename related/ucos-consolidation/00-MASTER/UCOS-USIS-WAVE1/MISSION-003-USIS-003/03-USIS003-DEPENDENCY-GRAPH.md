# 03 — USIS-003 DEPENDENCY GRAPH

All existing edges are downward-only and acyclic (verified this session by
`ukbx twin --check` C-07 PASS). This analysis determines whether USIS-003's
dependency root is satisfied.

---

## 1 — Established founding chain (registered, unchanged)

```
… SECURITY → USIS-GOV-000 (…000001) → USIS-001 (…000002) → USIS-002 (…000003)
                 Wave 0                 Wave 1·M1·07e0de4     Wave 1·M2·8db7d52
```

## 2 — Substrate-foundation dependency DAG (from establishment-package blueprints)

Machine-checkable `DEPENDS-ON` declarations:

```
USIS-001  DEPENDS-ON  USIS-GOV-000
USIS-002  DEPENDS-ON  USIS-001
USIS-004  DEPENDS-ON  USIS-001 · USIS-002 · UCIC-001            # NOT USIS-003
USIS-003  DEPENDS-ON  USIS-002 · USIS-004 · LAW USIS-00
USIS-005  DEPENDS-ON  USIS-GOV-000 · USIS-002 · USIS-004        # NOT USIS-003
```

Topological order implied by these edges:

```
USIS-001 → USIS-002 → USIS-004 → { USIS-003 , USIS-005 }
```

**USIS-004 (Universal Capability Meta-Model) precedes USIS-003.** The set is
acyclic; USIS-004 has no dependency on USIS-003 (so no cycle), and both USIS-003
and USIS-005 depend on USIS-004.

## 3 — USIS-003 placement and root-satisfaction check

| Node | Depends-On (downward) | Registered / satisfied? |
|---|---|:--:|
| USIS-002 | USIS-001 | ✅ established `8db7d52` |
| **USIS-004** | USIS-001, USIS-002 | ❌ **not implemented** (no artifact, no `05-META-MODEL/`) |
| **USIS-003** | USIS-002 ✅ , **USIS-004 ❌** , LAW USIS-00 ✅ | ❌ **root NOT satisfied** |

**Dependency-root status:** USIS-003 has **two** hard dependencies. One (USIS-002)
is satisfied; the other (**USIS-004**) is **unsatisfied**. Therefore the USIS-003
dependency root is **NOT satisfied**.

## 4 — Parent / authorization chain (for the eventual USIS-003)

- **Parent (structural):** program root `USIS-GOV-000` (`UCOS-USIS-000001`), non-chained
  option (a) — the established USIS precedent (USIS-001, USIS-002 both parent to root).
- **Depends-On (metadata):** USIS-002 **and** USIS-004 (once USIS-004 exists).
- **Authorized-By:** USIS-001 / USIS-GOV-000 (NONE-DERIVED authority chain).
- All edges downward-only; adding USIS-003 *after* USIS-004 preserves acyclicity.

## 5 — Downstream dependents of USIS-003

From the blueprints, no registered artifact currently declares a dependency on
USIS-003. Future dependents (per USIS-005 §3 / roadmap): per-science homes
(`USIS-SCI-*`), the Domain & Human-Intelligence catalog (USIS-006-class),
Wave-3 science realizations. None are authored; none block or are blocked now.

## 6 — Ordering invariants (fail-closed)

- **Strict downward order:** a capability may only `Depends-On` already-registered
  nodes (UCIC-001 Stage 2; USIS-011 obligation 14). USIS-003 → USIS-004 would be a
  **forward reference** today (USIS-004 unregistered).
- **Acyclicity:** re-proven each build by `ukbx twin --check` C-07.

## 7 — Roadmap-vs-dependency reconciliation (Repository Truth governs)

The USIS-012 roadmap Wave-1 narrative lists "…Universe Catalog → **Science Catalog
→ Meta-Model** → Theory/Ontology/Taxonomy" (003 before 004). This single narrative
ordering is **contradicted** by three explicit, machine-checkable `DEPENDS-ON`
declarations (USIS-003→USIS-004, USIS-005→USIS-004, USIS-004↛USIS-003) plus LAW
USIS-08 and the USIS-004 §2 Science-tier contract. Per the Absolute Rule
"Everything SHALL be derived from repository evidence," the **dependency
declarations govern** over the narrative grouping. The correct realization order
is **USIS-002 → USIS-004 → USIS-003**.

**Graph verdict:** the dependency graph is acyclic, but **USIS-003's root is
unsatisfied** because USIS-004 is not implemented.
