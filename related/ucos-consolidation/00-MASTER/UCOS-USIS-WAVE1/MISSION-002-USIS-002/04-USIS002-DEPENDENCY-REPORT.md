# 04 — USIS-002 DEPENDENCY & DETERMINISM REPORT

---

## 1 — Realized edges (from `00-BOOK/DATA/relationships.json`, verified this session)

```
UCOS-USIS-000003 (USIS-002 — Universe Catalog)
   -Parent->        UCOS-USIS-000001   (structural:program-root)      # USIS-GOV-000
   -Depends-On->    UCOS-USIS-000002   (metadata:DEPENDS-ON)          # USIS-001
   -Authorized-By-> UCOS-USIS-000002   (metadata:AUTHORITY)           # USIS-001
   -Authorized-By-> UCOS-USIS-000001   (metadata:AUTHORITY)           # USIS-GOV-000

   inbound:  <-Child-      UCOS-USIS-000001
             <-Required-By- UCOS-USIS-000002
             <-Authorizes-  UCOS-USIS-000002 / UCOS-USIS-000001
```

All outbound edges point **downward** to already-registered nodes: its direct
dependency `USIS-001` (`UCOS-USIS-000002`) and the program root `USIS-GOV-000`
(`UCOS-USIS-000001`). No forward/downstream edge exists (USIS-003…005 are not
authorized and not present). **Acyclic** — confirmed by `ukbx twin --check` C-07.

> Note: the `artifacts.json` `dependencies[]` array tracks only *structural chain*
> edges; USIS-002's dependency on USIS-001 is a *metadata* edge and is recorded in
> the knowledge graph (`relationships.json`) — the same mechanism USIS-001 used
> for its own downward edge. Referential integrity holds (twin C-05 PASS).

## 2 — Founding chain (unchanged, context)

```
… SERVICE → APPLICATION → INFRASTRUCTURE → SECURITY → USIS-GOV-000 → USIS-001 → USIS-002
                                                        (…000001)      (…000002)   (…000003)
```

`USIS-GOV-000` parents to the SERVICE terminal via `CROSS_PROGRAM` (unchanged).
USIS-002 is **non-chained** (option (a)): it parents to the program root and
carries its ordering to USIS-001 via `Depends-On` metadata. `config.py` is
**unchanged** — no `CHAINS["USIS"]` edit was required.

## 3 — Universe reference edges (REFERENCE, never re-home — catalog Part D)

The catalog records, per LAW USIS-02, that each realizing universe **references**
its canonical MIP home (these are catalog-row mappings, materialized as real edges
only when each universe is separately authored):

```
USIS-U-ANL/PRD  → U16 Analytics
USIS-U-KNW      → U24 Knowledge / MIP Part 19
USIS-U-INT/HUM/COG/BEH/PSY/DEC/RSN/AUT/MAS → U25 / MIP Part 20
USIS-U-SIM      → U26 / MIP Part 25
USIS-U-EVO      → U28 / MIP Part 22/32
USIS-U-LRN      → MIP Part 21
USIS-U-DAT      → 10-DATA/ + U07
USIS-U-SCI      → MIP Part 19 + LAW USIS-00
USIS-U-FUT / USIS-U-UNK  (permanent reserved — no external edge)
```

No target is re-homed or forked (Reuse-First; USIS-011 obl. 2/3).

## 4 — Dependency correctness checks

| Check | Result |
|---|:--:|
| Every Depends-On target exists + registered | **PASS** (USIS-001, USIS-GOV-000 present) |
| No forward reference (targets pre-registered) | **PASS** |
| Downward-only (no upward/cross edge added) | **PASS** |
| Acyclic (CIOA) | **PASS** (C-07) |
| Recursion (`parent-universe`) forms a strict forest, no cycle | **PASS** (catalog Part C) |
| No `config.py` chain edit required | **PASS** (structural program-root parenting) |

## 5 — Deterministic regeneration

Method: `find 00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL} -type f | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256`.

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| USIS-001 baseline (`07e0de4`) | `b53f7fcb61ba125a7b61f79f291f8157ead7442c1c855a9481bdd4b042bc6f24` |
| After USIS-002 `register.sh` run #1 | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |
| After USIS-002 `register.sh` run #2 | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |
| After recovery-session re-run | `b406563c21af1316fe34ab6414a0e2c45822093ec7e312187e3e59680a113dbd` |

**DETERMINISM: PASS** — the digest deterministically evolved from the baseline
once USIS-002 registered (expected), and is **byte-identical across every
subsequent full transaction**. The invariant (byte-stability across re-runs, not a
fixed digest) holds. Evidence: `evidence/08-determinism.txt`,
`evidence/09-register-run2.log`.

## 6 — Guard status (expected drift — no commit authorized)

`register.sh --guard` returns **exit 3** (uncommitted registration drift),
listing the new `15-…/06-UNIVERSES/USIS-002-UNIVERSE-CATALOG.md`, the new
`00-BOOK/PORTAL/UCOS-USIS-000003.md`, and the regenerated
`00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`. This is the **correct and
expected** signal: the registration transaction sealed **COMPLETE**, but the
mission STOP condition forbids committing. It is identical in kind to the USIS-001
pattern — **not** a defect and **not** a blocker; it clears when a commit is
explicitly authorized (a separate mission). Evidence: `evidence/10-guard.log`.
