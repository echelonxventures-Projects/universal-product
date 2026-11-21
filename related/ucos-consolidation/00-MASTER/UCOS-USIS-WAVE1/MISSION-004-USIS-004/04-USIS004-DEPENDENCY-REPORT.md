# 04 — USIS-004 DEPENDENCY & DETERMINISM REPORT

---

## 1 — Realized edges (from `00-BOOK/DATA/relationships.json`, verified this session)

```
UCOS-USIS-000004 (USIS-004 — Universal Capability Meta-Model)
   -Parent->        UCOS-USIS-000001   (structural:program-root)      # USIS-GOV-000
   -Depends-On->    UCOS-USIS-000002   (metadata:DEPENDS-ON)          # USIS-001
   -Depends-On->    UCOS-USIS-000003   (metadata:DEPENDS-ON)          # USIS-002
   -Authorized-By-> UCOS-USIS-000002   (metadata:AUTHORITY)           # USIS-001

   inbound:  <-Child-        UCOS-USIS-000001
             <-Required-By-  UCOS-USIS-000002 , UCOS-USIS-000003
             <-Authorizes-   UCOS-USIS-000002
```

All outbound edges point **downward** to already-registered nodes: its two hard
dependencies USIS-001 (`…000002`) and USIS-002 (`…000003`), and the program root
USIS-GOV-000 (`…000001`). No forward/downstream edge. **Acyclic** — `ukbx twin
--check` C-07 PASS.

## 2 — Founding chain (extended, downward-only)

```
… SECURITY → USIS-GOV-000 (…000001) → USIS-001 (…000002) → USIS-002 (…000003) → USIS-004 (…000004)
```

USIS-004 is **non-chained** (option (a)): parents to the program root; carries its
ordering to USIS-001/USIS-002 via `Depends-On` metadata. `config.py` **unchanged** —
no `CHAINS["USIS"]` edit required.

## 3 — Dependency correctness checks

| Check | Result |
|---|:--:|
| Every Depends-On target exists + registered | **PASS** (USIS-001 ✅, USIS-002 ✅) |
| No forward reference (targets pre-registered) | **PASS** |
| Downward-only (no upward/cross edge added) | **PASS** |
| Acyclic (CIOA) | **PASS** (C-07) |
| Governance/methodology anchors (UCIC-001, MIP 24-field) | external spine markers (precedented) — not dangling edges |
| No `config.py` chain edit required | **PASS** (structural program-root parenting) |

## 4 — Deterministic regeneration

Method: `find 00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL} -type f | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256`.

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| USIS-002 baseline (`8db7d52`) | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |
| After USIS-004 `register.sh` run #1 | `14ce16f86f5fedd28e401f00ec486eae9e8486d929bc31d30ec9b77b58195970` |
| After USIS-004 `register.sh` run #2 | `14ce16f86f5fedd28e401f00ec486eae9e8486d929bc31d30ec9b77b58195970` |

**DETERMINISM: PASS** — the digest evolved deterministically from the baseline once
USIS-004 registered (expected), and is **byte-identical across independent
transactions**. Evidence: `evidence/08-determinism.txt`, `evidence/09-register-run2.log`.

## 5 — Drift attribution (guard drift is SOLELY USIS-004)

`register.sh --guard` → **exit 3** (uncommitted registration; commit forbidden by
STOP). Complete tracked drift vs `8db7d52`:

- **New files:** `15-…/05-META-MODEL/USIS-004-UNIVERSAL-CAPABILITY-META-MODEL.md`,
  `00-BOOK/PORTAL/UCOS-USIS-000004.md`.
- **Regenerated projections:** `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`.
- **Only new Universal ID:** `UCOS-USIS-000004`.
- **VOL-024 reused:** artifact_count 3 → 4; page_range_end 9139 → 9142 (append-only).
- **Frozen paths / `config.py`:** empty diff (untouched).

The guard drift is **wholly and solely attributable to the intentionally
uncommitted USIS-004 registration**. No unrelated or collateral drift.

## 6 — Guard status (expected — no commit authorized)

Exit 3 is the correct pending-commit signal (transaction sealed COMPLETE; STOP
forbids commit). It clears to exit 0 when a commit is explicitly authorized (a
separate mission), mirroring the USIS-001/USIS-002 pattern.
