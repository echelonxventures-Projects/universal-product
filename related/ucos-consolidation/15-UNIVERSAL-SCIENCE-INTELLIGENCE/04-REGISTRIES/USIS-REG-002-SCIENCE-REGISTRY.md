# USIS-REG-002 — Science Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-002 (Science Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Science Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — the row-projection surface for scientific-discipline membership (USIS-004 tier 9). Records **no** member row; the constitutional enumeration is owned by USIS-003. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Science registry rows under `15-…/04-REGISTRIES/` — projecting into `00-BOOK/DATA`. |
| DEPENDS-ON | USIS-REG-000 · USIS-003 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — science row projection (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · USIS Registry Integration Manifest `…/09` §2 (registry #2) |
| GOVERNED BY | USIS-REG-000 · USIS-001 (LAW USIS-02/03/05/09) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry; identity via `id-ledger.json`; projection via `ukb build` (LAW USIS-02). DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; enumeration referenced from USIS-003 (30 seed disciplines + open receptors). No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. The science **enumeration** is owned by USIS-003; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Science Registry** as an empty, schema-bearing row-projection surface for per-member scientific-discipline realizations (tier-9) in Wave-3. It records **0 member rows** at this baseline.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-SCI-<NAME>, home: 07-SCIENCES/<NAME>/, discipline: <name>,
  parent_science?: USIS-SCI-<PARENT>, cross_links: [<reference edges>],
  taxon: USIS-TAXON-SCIENCE, status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-003** — the 30 seed disciplines (28 realizable + `FUTURE-*`/`UNKNOWN-*` permanent receptors).

## PART B — Rows at this baseline

**0 member rows.** Science rows are recorded per member by `EVO-USIS-W3-M-<member>` missions (priority group 1). Append-only; open (LAW USIS-09).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only (schema + home + projection); per-member closure at each realization.
- No parallel allocator/certifier/registry; rows project to `00-BOOK/DATA`. Science enumeration not duplicated (owned by USIS-003).

*END — USIS-REG-002 · SCIENCE REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
