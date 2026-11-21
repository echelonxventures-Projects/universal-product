# USIS-REG-003 — Domain Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-003 (Domain Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Domain Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — row-projection surface for domain / sub-domain / Human-Intelligence-family membership (USIS-004 tier 9). Records **no** member row; enumeration owned by USIS-007 + the domain/HI catalog. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Domain registry rows under `15-…/04-REGISTRIES/` — projecting into `00-BOOK/DATA`. |
| DEPENDS-ON | USIS-REG-000 · USIS-007 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — domain row projection (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · USIS Registry Integration Manifest `…/09` §2 (registry #3) |
| GOVERNED BY | USIS-REG-000 · USIS-001 (LAW USIS-02/03/05/09) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry (LAW USIS-02). Security/Governance/Runtime/Validation/Certification domains **reference** their canonical homes and are not re-implemented. DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; enumeration referenced from USIS-007 + `…/06` (42 domains + 38 HI families). No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. Domain **enumeration** owned by USIS-007; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Domain Registry** as an empty, schema-bearing row-projection surface for per-member domain / sub-domain / HI-family realizations (tier-9) in Wave-3. It records **0 member rows** at this baseline.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-DOM-<NAME> | USIS-CAP-HUM-<NAME>, home: 08-DOMAINS/<NAME>/,
  parent_domain?: USIS-DOM-<PARENT>, references?: [<canonical home, reference-only>],
  taxon: USIS-TAXON-DOMAIN, status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-007** + `00-MASTER/UCOS-USIS-001/06` §1 (42 intelligence domains) / §2 (38 HI families). Cross-cutting domains (Security/Governance/Runtime/Validation/Certification) reference `14-SECURITY`/U03/`08-RUNTIME`/U15 — never re-homed.

## PART B — Rows at this baseline

**0 member rows.** Domain/HI-family rows are recorded per member by `EVO-USIS-W3-M-<member>` missions (priority group 2+). Append-only; open (LAW USIS-09).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only; per-member closure at each realization.
- No parallel allocator/certifier/registry; rows project to `00-BOOK/DATA`. Cross-cutting domains referenced, never re-implemented.

*END — USIS-REG-003 · DOMAIN REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
