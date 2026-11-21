# 04 — USIS-001 DEPENDENCY & DETERMINISM REPORT

---

## 1 — Realized edges (from `relationships.json`, verified via `ukb trace UCOS-USIS-000002`)

```
UCOS-USIS-000002 (USIS-001)
   -Parent->        UCOS-USIS-000001   (structural:program-root)
   -Depends-On->    UCOS-USIS-000001   (metadata:DEPENDS-ON)
   -Authorized-By-> UCOS-USIS-000001   (metadata:AUTHORITY)

   inbound:  <-Child- / <-Required-By- / <-Authorizes-  UCOS-USIS-000001
   spine:    requirement → UCOS-USIS-000001, DR-RAT-11 ; architecture → UCOS-USIS-000001
```

All outbound edges point **upward** to the established program root
`UCOS-USIS-000001` (USIS-GOV-000). No downstream/forward edges exist (USIS-002…005
are not authorized and not present). **Acyclic** — confirmed by `ukbx twin --check`
C-07.

## 2 — Founding chain (unchanged, context)

```
… SERVICE → APPLICATION → INFRASTRUCTURE → SECURITY → USIS-GOV-000 → USIS-001
                                                        (UCOS-USIS-000001)  (UCOS-USIS-000002)
```

`USIS-GOV-000` itself parents to `UCOS-SVC-000018` (SERVICE terminal, CROSS_PROGRAM)
— unchanged by this mission.

## 3 — Dependency correctness checks

| Check | Result |
|---|:--:|
| Every Depends-On target exists + registered | **PASS** (USIS-GOV-000 present) |
| No forward reference (target pre-registered) | **PASS** (Wave-0 root) |
| Downward-only (no upward/cross edge added) | **PASS** |
| Acyclic (CIOA) | **PASS** (C-07) |
| No `config.py` chain edit required | **PASS** (structural program-root parenting) |

## 4 — Deterministic regeneration

| Observation | Guard-scope aggregate SHA-256 |
|---|---|
| After `register.sh` run #1 | `b53f7fcb61ba125a7b61f79f291f8157ead7442c1c855a9481bdd4b042bc6f24` |
| After `register.sh` run #2 | `b53f7fcb61ba125a7b61f79f291f8157ead7442c1c855a9481bdd4b042bc6f24` |

**DETERMINISM: PASS** — two independent full transactions produce byte-identical
projections (`_stamp_eq_json` neutralizes `generated_at`; append-only allocation
adds no new IDs on re-run).

## 5 — Guard status (expected drift — no commit authorized)

`register.sh --guard` returns **exit 3** (uncommitted registration drift),
listing the regenerated `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}` and the
new `PORTAL/UCOS-USIS-000002.md`. This is the **correct and expected** signal:
the registration transaction sealed **COMPLETE**, but the mission STOP condition
forbids committing. The drift is the deferred, authorized-commit-pending state —
identical in kind to the Wave-0 pattern. It is **not** a defect and **not** a
blocker to the implementation determination; it will clear when a commit is
explicitly authorized (a separate mission).
