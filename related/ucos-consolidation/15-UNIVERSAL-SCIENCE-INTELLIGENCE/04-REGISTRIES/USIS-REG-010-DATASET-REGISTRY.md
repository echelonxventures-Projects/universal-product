# USIS-REG-010 — Dataset Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-010 (Dataset Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Dataset Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — row-projection surface for dataset membership (USIS-004 tier 9). Records **no** member row; the canonical data home is `10-DATA/` + Universal Data (`USIS-U-DAT`), referenced never re-homed. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Dataset registry rows under `15-…/04-REGISTRIES/` — projecting into `00-BOOK/DATA`; data platform referenced. |
| DEPENDS-ON | USIS-REG-000 · USIS-009 · USIS-002 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — dataset row projection (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · USIS Registry Integration Manifest `…/09` §2 · `10-DATA/` + U07 (referenced) |
| GOVERNED BY | USIS-REG-000 · USIS-009 (model/dataset linkage) · USIS-001 (LAW USIS-02/03/05/09) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry and **no second data platform** (USIS-002 Part D references `10-DATA/`; LAW USIS-02). DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; dataset is registry #10 of `…/09` §2; data platform referenced (`10-DATA/`). No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. The data platform is owned by `10-DATA/`/U07; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Dataset Registry** as an empty, schema-bearing row-projection surface for per-member dataset rows (with provenance and lineage) in Wave-3, referencing the canonical data platform. It records **0 member rows** at this baseline and duplicates no data platform.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-DS-<NAME>, provenance: <source, immutable>, schema_ref: <reference>,
  lineage: { predecessor?, successors[] }, data_home_ref: 10-DATA/ (reference),
  status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-009** (Model) dataset linkage + `…/07` §5 (Learning universe dataset registry); canonical data home `10-DATA/` + U07.

## PART B — Rows at this baseline

**0 member rows.** Dataset rows are recorded per member in Wave-3 (priority groups 3–4). Append-only; open (LAW USIS-09).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only; per-member closure at each realization.
- No parallel allocator/certifier/registry and **no second data platform**; rows project to `00-BOOK/DATA`. Data platform referenced (owned by `10-DATA/`/U07).

*END — USIS-REG-010 · DATASET REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
