# USIS-REG-005 — Algorithm Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-005 (Algorithm Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Algorithm Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — row-projection surface for agnostic algorithm membership (USIS-004 tier 9/12). Records **no** member row; the algorithm model is owned by USIS-008. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Algorithm registry rows under `15-…/04-REGISTRIES/` (with `09-ALGORITHMS/`) — projecting into `00-BOOK/DATA`. |
| DEPENDS-ON | USIS-REG-000 · USIS-008 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — algorithm row projection resolved by engines at reference time (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · USIS Registry Integration Manifest `…/09` §2 |
| GOVERNED BY | USIS-REG-000 · USIS-008 (algorithm model) · USIS-011 (engines resolve this registry) · USIS-001 (LAW USIS-02/03/04/05/09) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry; technology-neutral (LAW USIS-04 — concrete algorithms are registered content behind an agnostic registry). DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; USIS-011 resolves algorithm members from `04-REGISTRIES/` at reference time. No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. Algorithm **model** owned by USIS-008; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Algorithm Registry** as an empty, schema-bearing row-projection surface so that engine contracts (USIS-011) have a reference-time resolution target and per-member algorithm rows can be recorded in Wave-3. It records **0 member rows** at this baseline; adding an algorithm changes no engine (zero hard coding).

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-ALG-<NAME>, class: <algorithm class>, binding?: <optional, technology-neutral>,
  taxon: USIS-TAXON-ALGORITHM, status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-008** algorithm architecture; operational seed set in `00-MASTER/UCOS-USIS-001/07` §3 (open, uncapped).

## PART B — Rows at this baseline

**0 member rows.** Algorithm rows are recorded per member in Wave-3 (priority group 3). Append-only; open (LAW USIS-09).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only; per-member closure at each realization.
- No parallel allocator/certifier/registry; rows project to `00-BOOK/DATA`. Engines hold registry *contracts*, not enumerated members (obligation 1/20).

*END — USIS-REG-005 · ALGORITHM REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
