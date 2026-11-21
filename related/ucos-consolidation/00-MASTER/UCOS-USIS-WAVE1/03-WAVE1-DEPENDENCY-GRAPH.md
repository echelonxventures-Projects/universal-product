# 03 — WAVE 1 DEPENDENCY GRAPH

All edges are **downward-only and acyclic** (CIOA-enforced). Nothing upstream of
USIS is modified. Every node roots (transitively) at `USIS-GOV-000`, which founds
downward on the prior program.

---

## 1 — Program founding position (established, unchanged)

```
… RUN → PLATFORM → DATA → SERVICE → APPLICATION → INFRASTRUCTURE → SECURITY → USIS
```

`USIS-GOV-000` (`UCOS-USIS-000001`) edges (from `config.py` + artifact metadata):

```
USIS-GOV-000  --Depends-On-->  SVC-000018   (SERVICE terminal; CROSS_PROGRAM ("USIS","SERVICE"))
USIS-GOV-000  --Depends-On-->  SEC-000001   (SECURITY terminal; metadata founding edge)
```

Inverses materialized; graph acyclic (verified `ukbx twin --check` C-07 at `2bf5312`).

## 2 — Wave 1 internal dependency chain (USIS-001…005)

Each artifact's `Parent` is the chain predecessor; `Depends-On` runs downward to
already-realized nodes. Authoring order == dependency order (strict).

```
USIS-GOV-000  (root, established Wave 0)
   └── USIS-001  Program Constitution              [00-CONSTITUTION/]
          └── USIS-002  Universe Catalog (21)        [06-UNIVERSES/]
                 └── USIS-003  Universal Science Catalog (30 seed)  [07-SCIENCES/]
                        └── USIS-004  Universal Capability Meta-Model (24-tier)  [05-META-MODEL/]
                               └── USIS-005  Theory / Ontology / Taxonomy  [01-THEORY/ 02-ONTOLOGY/ 03-TAXONOMY/]
```

| Node | Depends-On (downward) | Constitutional anchor | Realizes / references (no duplication) |
|---|---|---|---|
| USIS-001 | USIS-GOV-000 | LAW Ω∞-000; MIP Parts 19/20/21 | LAW USIS-00 laws + invariants |
| USIS-002 | USIS-001 | USIS-001 (LAW USIS-01/02/09) | **REFERENCES** universes U16 Analytics · U24 Knowledge · U25 Intelligence · U26 Simulation · U28 Evolution |
| USIS-003 | USIS-002 | USIS-001; MIP Part 19 | 30 seed disciplines (open registry) |
| USIS-004 | USIS-002, USIS-003 | LAW USIS-08 | 24-tier Science→…→Lifecycle meta-model |
| USIS-005 | USIS-004 | USIS-001; Ontology/Taxonomy closure | substrate hypergraph theory + ontology + taxonomy |

## 3 — Cross-cutting reference edges (REFERENCE, never re-home)

```
USIS Data Universe (USIS-002 member)     --References-->  10-DATA/
USIS Security integration                --References-->  14-SECURITY/
USIS Runtime / twin                      --References-->  08-RUNTIME/  , intelligence/ (RIE)
USIS Simulation Universe                 --Realizes-->    Universe U26
USIS Knowledge/Analytics/Intelligence/Evolution universes --Realizes--> U24 / U16 / U25 / U28
```

These are `Depends-On`/reference edges only. Re-homing any target violates LAW
USIS-02 (see `02` §6).

## 4 — Capability → area → registry mapping (Wave 1 surface)

| Capability | Corpus area created | Registry touched |
|---|---|---|
| USIS-001 Constitution | `15-…/00-CONSTITUTION/` | UNIVERSAL-ARTIFACT/PAGE/GRAPH (EXTEND) |
| USIS-002 Universe Catalog | `15-…/06-UNIVERSES/` + `15-…/04-REGISTRIES/` (Universe Registry) | + USIS Universe Registry (CREATE, universal mechanism) |
| USIS-003 Science Catalog | `15-…/07-SCIENCES/` + Science Registry | + USIS Science Registry |
| USIS-004 Meta-Model | `15-…/05-META-MODEL/` + Capability Registry | + USIS Capability Registry |
| USIS-005 Theory/Ontology/Taxonomy | `15-…/01-THEORY/ 02-ONTOLOGY/ 03-TAXONOMY/` | UNIVERSAL-ARTIFACT/GRAPH (EXTEND); ontology/taxonomy closure |

## 5 — Config classification dependency (decision point)

- `config.py` already routes `^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ → USIS/USIS/VOL-024` and sets `PROGRAM_ROOTS["USIS"] = USIS-GOV-000…`. So any new USIS artifact **auto-classifies** and, if not chained, **auto-parents to the program root**.
- `CHAINS["USIS"]` currently contains only the head. Two admissible, acyclic options for USIS-001…005 ordering:
  - **(a) Non-chained (default):** each parents directly to `USIS-GOV-000`; internal ordering carried by artifact `Depends-On` metadata. **No `config.py` edit.**
  - **(b) Chained:** append `USIS-001…005` to `CHAINS["USIS"]` (append-only, governed) to materialize the linear spine as Parent/Child edges.
- **Recommendation:** option (b) for a first-class linear substrate spine, executed as a single append-only `config.py` edit at the start of Wave 1 (`04` Phase W1-0). Either option is acyclic and satisfies No-Orphan; the choice is a governance decision (Risk R-2).

## 6 — Ordering invariants

- **Strict topological order:** USIS-001 → 002 → 003 → 004 → 005. USIS-004 depends on both 002 and 003 (needs the universe + science sets to define the meta-model).
- **No forward references:** an artifact may only `Depends-On` an already-registered node — enforced by UCIC-001 Stage 2 (dependency satisfaction) and USIS-011 obligation 14.
- **Downward-only:** no USIS node may be depended on by any upstream program (would create an upward edge / cycle) — USIS-011 obligation 5.
