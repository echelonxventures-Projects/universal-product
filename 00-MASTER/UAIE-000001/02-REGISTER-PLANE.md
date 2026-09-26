# Register Plane — the semantic graph this programme reasons over

> Each row is a subject the mission requires the repository to understand, bound to
> the register that already holds it and to the faculties that reason over it. A
> subject with no register, or a register no faculty claims, closes the gate.

| ID | Subject | Register | Form | Status | Refs | Broken | Claimed by |
|---|---|---|---|---|---|---|---|
| `UAIE-REG-01` | every repository artifact | `00-BOOK/DATA/artifacts.json` | json | **RESOLVES** | 1691 | 0 | UAIE-FAC-01, UAIE-FAC-06 |
| `UAIE-REG-02` | every relationship between artifacts | `00-BOOK/DATA/relationships.json` | json | **RESOLVES** | 0 | 0 | UAIE-FAC-01, UAIE-FAC-02 |
| `UAIE-REG-03` | every constitution | `00-CMG/CMG-REGISTRY.json` | json | **RESOLVES** | 45 | 0 | UAIE-FAC-04, UAIE-FAC-09 |
| `UAIE-REG-04` | every registry | `00-MASTER/MIP-W1-P001/10-UNIVERSAL-REGISTRY-CATALOG.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-01, UAIE-FAC-07 |
| `UAIE-REG-05` | every ontology | `01-WORKING/ONTOLOGY-REGISTER.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-01 |
| `UAIE-REG-06` | every taxonomy | `10-DATA/DATA-004-UNIVERSAL-DATA-TAXONOMY.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-02 |
| `UAIE-REG-07` | every dependency | `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | json | **RESOLVES** | 0 | 0 | UAIE-FAC-03 |
| `UAIE-REG-08` | every ownership relationship | `02-CANONICAL-OWNERSHIP-MATRIX.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-04 |
| `UAIE-REG-09` | every capability | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | json | **RESOLVES** | 148 | 0 | UAIE-FAC-05, UAIE-FAC-08 |
| `UAIE-REG-10` | every analysis | `00-MASTER/UCOS-UAR-001/uar-analyses.json` | json | **RESOLVES** | 45 | 0 | UAIE-FAC-10 |
| `UAIE-REG-11` | every platform capability binding | `00-MASTER/UAEP-000001/uaep-platform.json` | json | **RESOLVES** | 25 | 0 | UAIE-FAC-08 |
| `UAIE-REG-12` | every validation | `00-MASTER/UCCEP-000000/uccep-bindings.json` | json | **RESOLVES** | 0 | 0 | UAIE-FAC-09 |
| `UAIE-REG-13` | every certification | `00-BOOK/DATA/certification.json` | json | **RESOLVES** | 0 | 0 | UAIE-FAC-10 |
| `UAIE-REG-14` | every canonical knowledge object | `knowledge/canonical-knowledge.json` | json | **RESOLVES** | 0 | 0 | UAIE-FAC-05 |
| `UAIE-REG-15` | every decision | `knowledge/decisions.json` | json | **RESOLVES** | 0 | 0 | UAIE-FAC-07 |
| `UAIE-REG-16` | every universe | `15-UNIVERSAL-SCIENCE-INTELLIGENCE/04-REGISTRIES/USIS-REG-001-UNIVERSE-REGISTRY.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-01 |
| `UAIE-REG-17` | every implementation | `02-IMPLEMENTATION-MANIFEST.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-06 |
| `UAIE-REG-18` | every evolution baseline and change classification | `00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-07 |
| `UAIE-REG-19` | every release lifecycle state | `00-MASTER/RELEASE-001/RELEASE-LIFECYCLE.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-10 |
| `UAIE-REG-20` | every baseline | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` | markdown | **RESOLVES** | 0 | 0 | UAIE-FAC-07 |

## Ontology integration

> Ontology integration here is a *binding*, not an addition: each anchor is an
> element the ontology register already declares, so no ontology element is created
> and no declared cardinality is altered.

| Anchor | Ontology element | Register | Status |
|---|---|---|---|
| `ONT-27` | UNIVERSAL CAPABILITY UNIVERSE | `UAIE-REG-05` | **PRESENT** |
| `ONT-29` | MEMORY -> KNOWLEDGE -> INTELLIGENCE -> WISDOM | `UAIE-REG-05` | **PRESENT** |
| `ONT-25` | UNIVERSAL MODEL (10-tuple) | `UAIE-REG-05` | **PRESENT** |
