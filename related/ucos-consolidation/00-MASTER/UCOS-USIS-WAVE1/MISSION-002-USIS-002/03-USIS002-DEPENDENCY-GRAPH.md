# 03 — USIS-002 DEPENDENCY GRAPH

All edges are **downward-only and acyclic** (CIOA-enforced; verified this session
by `ukbx twin --check` C-07 PASS). Nothing upstream of USIS is modified. Every
USIS-002 node roots (transitively) at `USIS-GOV-000`, which founds downward on the
prior program.

---

## 1 — Program founding position (established, unchanged)

```
… RUN → PLATFORM → DATA → SERVICE → APPLICATION → INFRASTRUCTURE → SECURITY → USIS
```

`config.py` edges (verified this session):
```
CROSS_PROGRAM: ("USIS", "SERVICE")                       # line 714
USIS-GOV-000  --Depends-On-->  SERVICE terminal          # chain-head founding edge
USIS-GOV-000  --Depends-On-->  SECURITY terminal         # artifact metadata founding edge
PROGRAM_ROOTS["USIS"] = USIS-GOV-000-…DETERMINATION       # line 671 (non-chained parent-to-root)
CHAINS["USIS"] = [ USIS-GOV-000-…DETERMINATION ]          # line 635 — head only (no USIS-001..N yet)
```

## 2 — USIS-002 dependency placement (topological)

```
USIS-GOV-000            (UCOS-USIS-000001 — program root, Wave 0)
   └── USIS-001         (UCOS-USIS-000002 — Constitution, committed 07e0de4, ACTIVE)
          └── USIS-002  (Universe Catalog — THIS capability, not yet authored)
                 └── (USIS-003 Science Catalog — later; Depends-On USIS-002)
```

| Node | Depends-On (downward) | Constitutional anchor | Realizes / references (no duplication) |
|---|---|---|---|
| USIS-001 | USIS-GOV-000 (`UCOS-USIS-000001`) | LAW Ω∞-000; MIP 19/20/21 | LAW USIS-00 laws + invariants — **registered, ACTIVE** |
| **USIS-002** | **USIS-001 (`UCOS-USIS-000002`) — SATISFIED** | USIS-001 (LAW USIS-01/02/09) | **REFERENCES** U16 Analytics · U24 Knowledge · U25 Intelligence · U26 Simulation · U28 Evolution |

**Dependency-root status:** USIS-002's sole hard prerequisite (USIS-001) is
registered as `UCOS-USIS-000002`, ACTIVE, committed at `07e0de4`, and terminal-
success (certified 10/10). **The dependency root is satisfied.**

## 3 — USIS-002 internal + cross-cutting reference edges (REFERENCE, never re-home)

Each seed universe carries a `Realizes`/reference edge to its canonical MIP home:
```
USIS-U-ANL  --Realizes-->  U16 Analytics
USIS-U-KNW  --Realizes-->  U24 Knowledge / MIP Part 19
USIS-U-INT/HUM/COG/BEH/PSY/DEC/RSN/AUT/MAS  --Realizes-->  U25 / MIP Part 20
USIS-U-SIM  --Realizes-->  U26 / MIP Part 25
USIS-U-EVO  --Realizes-->  U28 / MIP Part 22/32
USIS-U-LRN  --Realizes-->  MIP Part 21
USIS-U-DAT  --References--> 10-DATA/ + U07
USIS-U-PRD  --Realizes-->  U16
USIS-U-FUT / USIS-U-UNK    (permanent reserved slots — LAW USIS-09; no external edge)
```
All are `Realizes`/`References`/`Depends-On` edges only. Re-homing any target
violates LAW USIS-02 (`02` §6).

## 4 — Capability → area → registry mapping (USIS-002 surface)

| Capability | Corpus area created | Registry touched |
|---|---|---|
| USIS-002 Universe Catalog (21) | `15-…/06-UNIVERSES/` (see D-1) + `15-…/04-REGISTRIES/` (Universe Registry) | UNIVERSAL-ARTIFACT/PAGE/GRAPH/CHANGE-VERSION-LINEAGE/CERTIFICATION (**EXTEND**) + USIS Universe Registry (**CREATE**, universal mechanism) |

## 5 — Config classification / chain decision (decision point, not a blocker)

- `config.py` already routes `^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ → USIS/USIS/VOL-024`
  (line 275) and sets `PROGRAM_ROOTS["USIS"] = USIS-GOV-000`. A new USIS-002
  artifact under `15-…/` therefore **auto-classifies** and, if not chained,
  **auto-parents to the program root** `USIS-GOV-000`.
- `CHAINS["USIS"]` currently holds only the head (line 635). Two admissible,
  acyclic options for USIS-002:
  - **(a) Non-chained (default):** USIS-002 parents to `USIS-GOV-000`; the
    USIS-001→USIS-002 ordering is carried by USIS-002's `Depends-On` metadata.
    **No `config.py` edit.**
  - **(b) Chained:** append `USIS-001, USIS-002` to `CHAINS["USIS"]` (append-only,
    governed) to materialize the linear substrate spine as Parent/Child edges.
- **Recommendation:** option (b) for a first-class linear substrate spine,
  executed as a single append-only `config.py` edit at USIS-002 pre-flight. Either
  option is acyclic and satisfies No-Orphan; the choice is a governance decision
  (Risk R-2 in `04`).

## 6 — Ordering invariants (fail-closed)

- **Strict downward order:** USIS-001 (done) → USIS-002 → USIS-003. USIS-002 may
  only `Depends-On` already-registered nodes (USIS-001 ✓, USIS-GOV-000 ✓) —
  UCIC-001 Stage 2 + USIS-011 obligation 14 (no forward references).
- **Downward-only:** no USIS node may be depended on by an upstream program (would
  create an upward edge / cycle) — USIS-011 obligation 5.
- **Acyclicity re-proven each build:** `ukbx twin --check` C-07 (PASS this session)
  gates every registration.

**Graph verdict:** the dependency graph is **acyclic and downward-only**; adding
USIS-002 as a child/dependent of USIS-001 preserves both invariants.
