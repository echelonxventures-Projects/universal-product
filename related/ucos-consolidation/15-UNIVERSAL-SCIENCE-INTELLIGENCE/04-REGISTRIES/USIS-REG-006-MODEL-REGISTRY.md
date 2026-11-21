# USIS-REG-006 — Model Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-006 (Model Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Model Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — row-projection surface for agnostic, versioned model membership (USIS-004 tier 9/11). Records **no** member row; the model model is owned by USIS-009. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Model registry rows under `15-…/04-REGISTRIES/` (with `10-MODELS/`) — projecting into `00-BOOK/DATA`. |
| DEPENDS-ON | USIS-REG-000 · USIS-009 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — model row projection resolved by engines at reference time (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · MIP Part 20 (Model Registry) · USIS Registry Integration Manifest `…/09` §2 |
| GOVERNED BY | USIS-REG-000 · USIS-009 (model model) · USIS-011 (engines resolve this registry) · USIS-001 (LAW USIS-02/03/04/05/09) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry; technology-neutral, versioned, append-only (superseded models retained with lineage). DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; enumeration referenced from USIS-009 + `…/07` §4 (agnostic, append-only, versioned). No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. Model **model** owned by USIS-009; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Model Registry** as an empty, schema-bearing row-projection surface so that engine contracts have a reference-time resolution target and per-member model rows (agnostic, versioned) can be recorded in Wave-3. It records **0 member rows** at this baseline.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-MDL-<NAME>, version: <scheme-agnostic>, binding?: <optional>,
  algorithm_ref?: USIS-ALG-<NAME>, dataset_ref?: USIS-DS-<NAME>,
  taxon: USIS-TAXON-MODEL, superseded_by?: <lineage>, status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-009** model architecture / `…/07` §4 (append-only, versioned; superseded models retained with lineage).

## PART B — Rows at this baseline

**0 member rows.** Model rows are recorded per member in Wave-3 (priority group 3). Append-only; open (LAW USIS-09; CR-INF-007).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only; per-member closure at each realization.
- No parallel allocator/certifier/registry; rows project to `00-BOOK/DATA`. Model model not duplicated (owned by USIS-009).

*END — USIS-REG-006 · MODEL REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
