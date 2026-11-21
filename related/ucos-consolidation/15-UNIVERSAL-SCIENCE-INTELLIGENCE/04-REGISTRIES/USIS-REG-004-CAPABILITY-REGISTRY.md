# USIS-REG-004 — Capability Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-004 (Capability Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Capability Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — row-projection surface for capability membership (USIS-004 tier 9). Records **no** member row; the capability model is owned by USIS-006. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Capability registry rows under `15-…/04-REGISTRIES/` (with `08-DOMAINS/`) — projecting into `00-BOOK/DATA`. |
| DEPENDS-ON | USIS-REG-000 · USIS-006 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — capability row projection (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · USIS Registry Integration Manifest `…/09` §2 (registry #1 target — Capability) |
| GOVERNED BY | USIS-REG-000 · USIS-006 (capability model; Reuse-First — search Capability Registry first) · USIS-001 (LAW USIS-02/03/05/09) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry (LAW USIS-02). DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; USIS-006 declares `04-REGISTRIES/` as its registry home. No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. Capability **model** owned by USIS-006; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Capability Registry** as an empty, schema-bearing row-projection surface for per-member capability realizations (tier-9) in Wave-3, and the Reuse-First search target (USIS-006 Part O). It records **0 member rows** at this baseline.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-CAP-<NAME>, owner_domain: USIS-DOM-<NAME>, spec_ref: <UCIC Output-2, 12 mandatory fields>,
  verbs: <inherited 22-verb contract unless deviated>, properties: <7 prime, inherited>,
  status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-006** capability architecture / registration model.

## PART B — Rows at this baseline

**0 member rows.** Capability rows are recorded per member by `EVO-USIS-W3-M-<member>` missions, one logical capability per mission (UCIC-001 Stage 4). Append-only; Reuse-First (no capability may exist partially — USIS-004 Part D).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only; per-member closure at each realization.
- No parallel allocator/certifier/registry; rows project to `00-BOOK/DATA`. Capability model not duplicated (owned by USIS-006).

*END — USIS-REG-004 · CAPABILITY REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
