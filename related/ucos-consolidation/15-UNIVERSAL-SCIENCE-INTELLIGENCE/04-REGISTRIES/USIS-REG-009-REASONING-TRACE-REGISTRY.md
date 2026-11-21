# USIS-REG-009 — Reasoning-Trace Registry

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-REG-009 (Reasoning-Trace Registry — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger. Repository Truth is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 3 · EVO-USIS-W3-STRUCTURE-001 (step S-01) — home the **Reasoning-Trace Registry** projection surface (0 member rows; tier-9). |
| CLASSIFICATION | Programme Registry Catalog — row-projection surface for reasoning-trace membership (USIS-004 tier 9). Records **no** member row; traces are evidence and are owned by the Evidence architecture (USIS-016) under LAW USIS-07. |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 3 · registered |
| OWNING SCOPE | Reasoning-trace registry rows under `15-…/04-REGISTRIES/` — projecting into `00-BOOK/DATA` / `data/_evidence/<CAP-ID>/`. |
| DEPENDS-ON | USIS-REG-000 · USIS-016 · USIS-005 · USIS-004 |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 tier **9 (Registry)** — reasoning-trace row projection (LAW USIS-08). |
| REALIZES | LAW Ω∞-000 · structure spec §2 · USIS Registry Integration Manifest `…/09` §2 · LAW USIS-07 (explainable provenance) · TRACK-001 |
| GOVERNED BY | USIS-REG-000 · USIS-016 (evidence architecture) · USIS-001 (LAW USIS-02/03/05/07/09) · CEP-008 (referenced) · REG-AUTO-001 · GOV-001-T3 · GOV-002 |
| AUTHORITY | **NONE — DERIVED.** No allocator/certifier/competing registry and no second evidence store (LAW USIS-02). Traces are recorded by the referenced evidence substrate at the time of the reasoning action they substantiate. DR-RAT-11 external, non-blocking. |
| PROVENANCE | Authored under EVO-USIS-W3-STRUCTURE-001 to close gap **G-02**; reasoning-trace is registry #9 of `…/09` §2; evidence/traceability law inherited from USIS-016/CEP-008. No new knowledge. No `config.py` edit. |
| CONFLICT RULE | Higher frozen/governing instruments prevail. Trace/evidence owned by USIS-016/CEP-008; this catalog holds only the registry-row projection (LAW USIS-02). |

> **Purpose.** Home the **Reasoning-Trace Registry** as an empty, schema-bearing row-projection surface for per-member reasoning traces (each grounding a verdict, LAW USIS-07) in Wave-3. It records **0 member rows** at this baseline and duplicates no evidence store.

---

## PART A — Row schema (recorded per member at Wave-3 realization)

```
{ id: USIS-RT-<NAME>, subject: <inference | decision | analysis>,
  grounding_ref: <evidence, USIS-016>, explanation: <trace>, evidence_ref: data/_evidence/<CAP-ID>/,
  status: <lifecycle state> }
```

Enumeration source (reference, LAW USIS-02): **USIS-016** (Evidence) + CEP-008; produced by reasoning members at their realization.

## PART B — Rows at this baseline

**0 member rows.** Reasoning-trace rows are recorded per member in Wave-3 as reasoning/decision members are realized (priority group 4). Append-only; open (LAW USIS-09).

## PART C — Closure & non-duplication

- Foundation-level tier-9 closure only; per-member closure at each realization.
- No parallel allocator/certifier/registry and **no second evidence store**; rows project to `00-BOOK/DATA` / `data/_evidence/`. Evidence law not duplicated (owned by USIS-016/CEP-008).

*END — USIS-REG-009 · REASONING-TRACE REGISTRY · RATIFIED (PROVISIONAL) · AUTHORITY = NONE (DERIVED).*
