# 02 — USIS-005 DEPENDENCY DETERMINATION

All existing edges downward-only and acyclic (`ukbx twin --check` C-07 PASS).

---

## 1 — Committed founding chain

```
… SECURITY → USIS-GOV-000 (…001) → USIS-001 (…002) → USIS-002 (…003) → USIS-004 (…004) → USIS-003 (…005)
```

## 2 — USIS-005 declared dependency set (blueprint `05` header)

`DEPENDS-ON: USIS-GOV-000 · USIS-002 · USIS-004 · config.py (VOLUMES/CLASSIFY_RULES/CHAINS)`

| Dependency | Class | Registered / committed? | Evidence |
|---|---|:--:|---|
| USIS-GOV-000 | hard corpus (program root) | ✅ | `UCOS-USIS-000001`, ACTIVE (Wave 0) |
| USIS-002 (Universe Catalog) | hard corpus | ✅ | `UCOS-USIS-000003`, ACTIVE, committed `8db7d52` |
| USIS-004 (Meta-Model) | hard corpus | ✅ | `UCOS-USIS-000004`, ACTIVE, committed `e33c05b` |
| `config.py` (routing/volumes) | governed source | ✅ | present; routes `^15-…/ → USIS/USIS/VOL-024` |
| USIS-001 (Constitution) | transitive (via USIS-002/004) | ✅ | `UCOS-USIS-000002`, ACTIVE, committed `07e0de4` |

> USIS-005 **does not** depend on USIS-003 (already established anyway). The
> content-derivation reuses USIS-004 meta-model tiers 6/7/8 and USIS-011 obl 11/12
> (both committed operational instruments referenced by the meta-model).

## 3 — Dependency closure

**ACHIEVED.** All hard corpus dependencies (USIS-GOV-000, USIS-002, USIS-004) are
registered, ACTIVE, certified, and **committed**; the governed `config.py`
dependency is present and already carries USIS routing. Transitive USIS-001 is
committed. **0 unmet dependencies** (USIS-011 obl 14; UCIC-001 Stage 2 satisfied).

## 4 — Topological placement & acyclicity

```
USIS-001 → USIS-002 → USIS-004 → { USIS-003 , USIS-005 }
```

USIS-005 is a sibling of USIS-003 under USIS-004 (both depend on USIS-002 +
USIS-004; neither on the other). Adding USIS-005 as a dependent of
USIS-GOV-000/USIS-002/USIS-004 introduces **no cycle** and **no forward reference**
(all targets pre-registered/committed). Acyclicity re-proven by `ukbx twin --check`
C-07 (PASS this session).

## 5 — Parent / authorization chain (for the eventual USIS-005)

- **Parent (structural):** program root `USIS-GOV-000` (non-chained option (a) —
  the USIS precedent).
- **Depends-On (metadata):** `USIS-002` **and** `USIS-004` (both resolve; 0 unmet);
  optionally `USIS-GOV-000`.
- **Authorized-By:** USIS-001 / USIS-GOV-000 (NONE-DERIVED).
- **Conformance:** `Implements → USIS-004` (Theory/Ontology/Taxonomy meta-model
  tiers 6/7/8), mirroring the USIS-003 conformance edge.

## 6 — Downstream dependents

USIS-005 (Theory/Ontology/Taxonomy foundation) is depended upon by later Wave-2/3
per-universe & per-science ontology/taxonomy realizations (USIS-011 obl 11/12
discharge per member) and by the eventual Master Registry (USIS-021). None are
authored; none block or are blocked now.

## 7 — Ordering invariants (fail-closed) — all satisfied

| Invariant | Result |
|---|:--:|
| Every Depends-On target exists + registered/committed | **PASS** |
| No forward reference | **PASS** |
| Downward-only | **PASS** |
| Acyclic (CIOA) | **PASS** (C-07) |

**Verdict:** the dependency graph is **acyclic and downward-only**, and
**USIS-005's dependency closure is achieved** from committed repository evidence.
