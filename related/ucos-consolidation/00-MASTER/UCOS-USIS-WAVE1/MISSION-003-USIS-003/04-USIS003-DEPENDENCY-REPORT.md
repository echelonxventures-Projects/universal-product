# 04 — USIS-003 DEPENDENCY & DETERMINISM REPORT

---

## 1 — Realized edges (from `00-BOOK/DATA/relationships.json`, verified this session)

```
UCOS-USIS-000005 (USIS-003 — Universal Science Catalog)
   -Parent->        UCOS-USIS-000001   (structural:program-root)      # USIS-GOV-000
   -Depends-On->    UCOS-USIS-000003   (metadata:DEPENDS-ON)          # USIS-002
   -Depends-On->    UCOS-USIS-000004   (metadata:DEPENDS-ON)          # USIS-004
   -Implements->    UCOS-USIS-000004   (metadata:REALIZES)            # meta-model conformance
   -Authorized-By-> UCOS-USIS-000002 / 000003 / 000004

   inbound:  <-Child-       UCOS-USIS-000001
             <-Required-By- UCOS-USIS-000003 , UCOS-USIS-000004
             <-Implemented-By- UCOS-USIS-000004
```

All outbound edges point **downward** to already-registered/committed nodes:
USIS-002 (`…000003`), USIS-004 (`…000004`), USIS-GOV-000 (`…000001`). No
forward/downstream edge. **Acyclic** — `ukbx twin --check` C-07 PASS.

## 2 — Founding chain (extended, downward-only)

```
… USIS-GOV-000 (…001) → USIS-001 (…002) → USIS-002 (…003) → USIS-004 (…004) → USIS-003 (…005)
```

USIS-003 is **non-chained** (option (a)): parents to the program root; carries its
ordering to USIS-002/USIS-004 via `Depends-On` metadata. `config.py` **unchanged**.

## 3 — Dependency correctness checks

| Check | Result |
|---|:--:|
| Every Depends-On target exists + registered/committed | **PASS** (USIS-002 ✅, USIS-004 ✅) |
| No forward reference (targets pre-registered) | **PASS** |
| Downward-only (no upward/cross edge) | **PASS** |
| Acyclic (CIOA) | **PASS** (C-07) |
| Meta-model conformance edge present (LAW USIS-08) | **PASS** (`Implements → USIS-004`) |
| Cross-links are reference-only (LAW USIS-02) | **PASS** (catalog Part D) |
| No `config.py` chain edit required | **PASS** |

## 4 — Deterministic regeneration

Method: `find 00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL} -type f | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256`.

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| USIS-004 baseline (`e33c05b`) | `14ce16f86f5fedd28e401f00ec486eae9e8486d929bc31d30ec9b77b58195970` |
| After USIS-003 `register.sh` run #1 | `4d97626235722c2bdbc61ca431b813c462a5af3f00425d620470651c3d86504d` |
| After USIS-003 `register.sh` run #2 | `4d97626235722c2bdbc61ca431b813c462a5af3f00425d620470651c3d86504d` |

**DETERMINISM: PASS** — byte-identical across independent transactions. Evidence:
`evidence/08-determinism.txt`, `evidence/09-register-run2.log`.

## 5 — Drift attribution (guard drift is SOLELY USIS-003)

`register.sh --guard` → **exit 3** (uncommitted; commit forbidden by STOP). Complete
tracked drift vs `e33c05b`:

- **New files:** `15-…/07-SCIENCES/USIS-003-UNIVERSAL-SCIENCE-CATALOG.md`,
  `00-BOOK/PORTAL/UCOS-USIS-000005.md`.
- **Regenerated projections:** `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`.
- **Only new Universal ID:** `UCOS-USIS-000005`.
- **VOL-024 reused:** artifact_count 4 → 5 (no new volume).
- **Frozen paths / `config.py`:** empty diff (untouched).

The guard drift is **wholly and solely attributable to the intentionally
uncommitted USIS-003 registration**. No unrelated or collateral drift.

## 6 — Guard status

Exit 3 is the correct pending-commit signal (transaction sealed COMPLETE; STOP
forbids commit). It clears to exit 0 when a commit is explicitly authorized (a
separate mission), mirroring USIS-001/002/004.
