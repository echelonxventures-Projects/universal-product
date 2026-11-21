# USIS-REG-001 — Universe Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-001 (Universe Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Universe Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — the row-projection surface for universe membership (USIS-004 tier 9). Records **no** member row; the constitutional enumeration is owned by USIS-002. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Universe registry rows under `15-…/04-REGISTRIES/` — projecting into `00-BOOK/DATA` via the reused mechanism. |
| DEPENDS-ON | USIS-REG-000 · USIS-002 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — universe row projection (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 (04-REGISTRIES) · USIS Registry Integration Manifest `…/09` §2 (registry #1) |
| GOVERNED BY | USIS-REG-000 (shared registry model) · USIS-001 (LAW USIS-02/03/05/09) · REG-AUTO-001 (single allocator) · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** Creates no allocator/certifier/competing registry; identity remains `id-ledger.json`; projection remains `ukb build` → `00-BOOK/DATA` (LAW USIS-02). DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; home per structure spec §2 / `…/09` §2. No new knowledge; enumeration referenced from USIS-002. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. The universe **enumeration** is owned by USIS-002; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Universe Registry** as an empty, schema-bearing row-projection surface so that per-member universe realizations can record their tier-9 registry rows in Wave-3. It records **0 member rows** at this baseline and creates no allocator or competing catalog.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-U-<UNIV>, home: 06-UNIVERSES/<UNIV>/, realizes: <MIP anchor, reference>,
  owner: USIS, concern: <single canonical concern>, parent_universe?: USIS-U-<PARENT>,
  status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-002** — the 21 constitutional universes (seed; open, append-only per LAW USIS-09; reserved receptors `USIS-U-FUT`/`USIS-U-UNK`).

## PART B — Rows at this baseline

**0 member rows.** Universe rows are recorded per member by the separately-authorized `EVO-USIS-W3-M-<member>` missions (gaps G-07/G-09). Population is append-only; adding a universe is a registration, never a redesign.

## PART C — Closure & non-duplication

- Tier-9 registry closure is discharged **at foundation level** here (schema + home + projection target); the per-member half is discharged at each realization.
- No parallel allocator, no second certifier, no competing artifact registry; rows project to `00-BOOK/DATA` via `ukb build`. The universe enumeration is not duplicated (owned by USIS-002).

*END — USIS-REG-001 · UNIVERSE REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
