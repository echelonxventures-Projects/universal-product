# 01 — Regenerated Gap Register

> PROGRAM **UAKOS PHASE-003A-R2** — Universal Realization-Aware Implementation Gap Regeneration · baseline `57d91b7` (branch `governance-reconciliation`) · regenerates the Constitutional Gap Baseline **exclusively** from the certified Realization Model **FREEZE C2** (`f966c8e0…4668f`) · AUTHORITY = **NONE (DERIVED)** · **READ-ONLY** · derived `2026-07-23`.
>
> The complete regenerated gap classification for all 431 certified knowledge objects. Every gap is recomputed under the FREEZE C2 realization model — **not** carried over from the superseded FREEZE C single-lifecycle model.
>
> Authoritative per-object source: FREEZE C2 / PHASE-003R Register 04 (Knowledge Object Reclassification). Superseded prior: FREEZE C (`1ab21078…0676`), which SHALL remain immutable.

## Regeneration rule (deterministic)

For every object the gap is the FIRST unmet step of its assigned lifecycle, using only FREEZE C2's per-object classification:

```
family → realization type (Reg-01) → lifecycle (Reg-02) → current stage (evidence) → gap (Reg-03 vocabulary for that lifecycle) → completion
```

`IMPLEMENTATION_GAP` is admissible **only** on the SOFTWARE lifecycle. No object receives a gap outside its lifecycle's valid vocabulary. Regeneration is a pure function of FREEZE C2; re-derivation yields identical output.

## Regenerated gap distribution (all 431 objects)

| Gap category | Objects | Lifecycle scope |
|---|---|---|
| NO_GAP | 313 | (terminal / complete) |
| IMPLEMENTATION_GAP | 47 | SOFTWARE only |
| RATIFICATION_GAP | 43 | CONSTITUTIONAL, GOVERNANCE |
| CERTIFICATION_GAP | 21 | SOFTWARE, REGISTRY |
| POPULATION_GAP | 7 | KNOWLEDGE |
| **Total** | **431** | |

- Open gaps (INCOMPLETE): **118**. Complete: **313** (of which **4** are TERMINAL(REJECTED)).
- Zero objects classified UNKNOWN. Zero invalid (out-of-lifecycle) gap categories. Zero objects with more than one gap.

## Gap by family (regenerated, FREEZE C2 model)

| Family | Realization type | Lifecycle | Objects | Regenerated gap breakdown |
|---|---|---|---|---|
| APPLICATION | APPLICATION | SOFTWARE | 21 | NO_GAP:13; IMPLEMENTATION_GAP:6; CERTIFICATION_GAP:2 |
| ARCH | ARCHITECTURE_SPECIFICATION | SPECIFICATION | 22 | NO_GAP:22 |
| BAND-UNIT | EXECUTION_BAND_UNIT | REGISTRY | 53 | NO_GAP:53 |
| CEP | CONSTITUTIONAL_EVIDENCE_PRINCIPLE | CONSTITUTIONAL | 11 | NO_GAP:8 (incl 4 TERMINAL); RATIFICATION_GAP:3 |
| DATA | DATA_MODEL | SOFTWARE | 20 | NO_GAP:13; IMPLEMENTATION_GAP:3; CERTIFICATION_GAP:4 |
| EC3-GATE | ADMISSION_GATE | GOVERNANCE | 5 | NO_GAP:4; RATIFICATION_GAP:1 |
| EPIC | PROGRAM_EPIC | SPECIFICATION | 10 | NO_GAP:10 |
| FOUNDATION | CONSTITUTIONAL_FOUNDATION | CONSTITUTIONAL | 6 | NO_GAP:6 |
| GOV | GOVERNANCE_DETERMINATION | GOVERNANCE | 11 | NO_GAP:7; RATIFICATION_GAP:4 |
| INFRASTRUCTURE | INFRASTRUCTURE_COMPONENT | SOFTWARE | 19 | NO_GAP:13; IMPLEMENTATION_GAP:3; CERTIFICATION_GAP:3 |
| LAW | CONSTITUTIONAL_LAW | CONSTITUTIONAL | 21 | NO_GAP:1; RATIFICATION_GAP:20 |
| MCP | MASTER_CONTEXT_PROTOCOL | KNOWLEDGE | 8 | NO_GAP:3; POPULATION_GAP:5 |
| MCS | MASTER_CONTEXT_PROTOCOL | KNOWLEDGE | 1 | POPULATION_GAP:1 |
| MEP | CONSTITUTIONAL_EVOLUTION_PROPOSAL | GOVERNANCE | 12 | NO_GAP:8; RATIFICATION_GAP:4 |
| METACLASS | META_MODEL | KNOWLEDGE | 91 | NO_GAP:91 |
| PHASE | LIFECYCLE_PHASE | SPECIFICATION | 9 | NO_GAP:9 |
| PLATFORM | PLATFORM_COMPONENT | SOFTWARE | 19 | NO_GAP:4; IMPLEMENTATION_GAP:12; CERTIFICATION_GAP:3 |
| RUNTIME | RUNTIME_COMPONENT | SOFTWARE | 16 | NO_GAP:5; IMPLEMENTATION_GAP:9; CERTIFICATION_GAP:2 |
| SERVICE | SERVICE | SOFTWARE | 19 | NO_GAP:14; IMPLEMENTATION_GAP:2; CERTIFICATION_GAP:3 |
| UCKO | ONTOLOGY | KNOWLEDGE | 24 | NO_GAP:23; POPULATION_GAP:1 |
| UCOS-COMP | SOFTWARE_ENGINE | SOFTWARE | 5 | IMPLEMENTATION_GAP:3; CERTIFICATION_GAP:2 |
| UCOS-EXEC | SOFTWARE_ENGINE | SOFTWARE | 12 | NO_GAP:1; IMPLEMENTATION_GAP:9; CERTIFICATION_GAP:2 |
| UCOS-GOV | GOVERNANCE_DETERMINATION | GOVERNANCE | 7 | NO_GAP:3; RATIFICATION_GAP:4 |
| UCOS-RAT | RATIFICATION_DETERMINATION | GOVERNANCE | 2 | RATIFICATION_GAP:2 |
| UCOS-RECON | RECONCILIATION_DETERMINATION | GOVERNANCE | 4 | RATIFICATION_GAP:4 |
| UKDA-DEC | GOVERNANCE_DECISION | GOVERNANCE | 3 | NO_GAP:2; RATIFICATION_GAP:1 |
| **Total** | | | **431** | |

## Open-gap object roster (118 INCOMPLETE)

### IMPLEMENTATION_GAP — 47 (SOFTWARE, stage = SPECIFIED)

APPLICATION-000, -002, -015, -017, -019, -020; DATA-000, -002, -027; INFRASTRUCTURE-000, -002, -004; PLATFORM-000, -002, -003, -004, -005, -007, -013, -014, -015, -016, -017, -018; RUNTIME-000, -001, -002, -003, -004, -005, -011, -014, -020; SERVICE-000, -017; UCOS-COMP-001000, -001010, -009010; UCOS-EXEC-000, -004, -005, -006, -007, -008, -009, -010, -011.

### CERTIFICATION_GAP — 21 (SOFTWARE, stage = IMPLEMENTED)

APPLICATION-016, -018; DATA-003, -004, -015, -018; INFRASTRUCTURE-015, -017, -018; PLATFORM-001, -008, -011; RUNTIME-012, -013; SERVICE-002, -016, -018; UCOS-COMP-000000, -000001; UCOS-EXEC-001, -002.

### RATIFICATION_GAP — 43 (CONSTITUTIONAL SPECIFIED / GOVERNANCE DETERMINED)

CEP-003, -009, -010; Ω∞-001…020 (20 laws); EC-3-AP-1; GOV-007, -008, -009, -010; MEP-00, -06, -08, -09; UCOS-GOV-000, -001, -003, -005; UCOS-RAT-000, -001; UCOS-RECON-0000, -0001, -001, -C1; UKDA-DEC-000.

### POPULATION_GAP — 7 (KNOWLEDGE, stage = REGISTERED)

MCP-000, -001, -004, -005, -006; MCS-000; UCKO-XXX-000.

_READ-ONLY: derived from FREEZE C2 only. No repository code, constitution, prior freeze, or knowledge object was modified or created._
