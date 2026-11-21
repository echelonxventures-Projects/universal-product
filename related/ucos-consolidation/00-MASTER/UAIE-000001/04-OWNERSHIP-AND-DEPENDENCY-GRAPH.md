# Ownership Graph and Faculty Dependency Graph

## Ownership graph

> One canonical owner per faculty, and no owner claimed by two faculties. A shared
> canonical owner would mean two faculties are one faculty under two names.

| Faculty | Name | Canonical owner | Homes |
|---|---|---|---|
| `UAIE-FAC-01` | Repository Semantic Graph | `engine/graph` | `engine/graph/model.py`, `engine/graph/engine.py`, `platform/repository_intelligence/graph.py` |
| `UAIE-FAC-02` | Architectural Reasoning Engine | `engine/graph/architecture` | `engine/graph/architecture/engine.py`, `engine/graph/architecture/algorithms.py`, `engine/graph/architecture/layers.py` |
| `UAIE-FAC-03` | Dependency Intelligence | `engine/graph/architecture/dependency_intelligence.py` | `engine/graph/architecture/dependency_intelligence.py`, `platform/repository_intelligence/discovery.py` |
| `UAIE-FAC-04` | Ownership Intelligence | `engine/knowledge/integration/ownership.py` | `engine/knowledge/integration/ownership.py`, `platform/repository_intelligence/discovery.py` |
| `UAIE-FAC-05` | Duplication Intelligence | `engine/knowledge/integration/duplication.py` | `engine/knowledge/integration/duplication.py`, `platform/repository_intelligence/discovery.py`, `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py` |
| `UAIE-FAC-06` | Gap Intelligence | `platform/measurement/gaps.py` | `platform/measurement/gaps.py`, `platform/repository_intelligence/discovery.py`, `00-MASTER/UCOS-RIB-001/rib_engine.py` |
| `UAIE-FAC-07` | Evolution Intelligence | `00-MASTER/UEI-000001/uei_engine.py` | `00-MASTER/UEI-000001/uei_engine.py`, `00-MASTER/UCOS-AEE-001/aee_engine.py`, `00-MASTER/UCEF-000001/ucef_engine.py` |
| `UAIE-FAC-08` | Reuse Intelligence | `engine/knowledge/integration/reuse.py` | `engine/knowledge/integration/reuse.py`, `engine/knowledge/integration/pipeline.py`, `platform/repository_intelligence/recommendation.py` |
| `UAIE-FAC-09` | Constitutional Intelligence | `engine/knowledge/integration/constitution.py` | `engine/knowledge/integration/constitution.py`, `00-CMG/tools/cmg_validate.py`, `00-MASTER/UCOS-UCAF-001/ucaf_engine.py` |
| `UAIE-FAC-10` | Completion Intelligence | `platform/validation_intelligence/analyzers.py` | `platform/validation_intelligence/analyzers.py`, `00-MASTER/URRC-000001/urrc_engine.py`, `00-MASTER/UCOS-UTCE-001/utce_engine.py`, `00-MASTER/UCOS-UFEP-001/ufep_engine.py` |

## Faculty dependency graph

**Edges:** 15 · **layers:** 4 · **acyclic:** true

| Faculty | Depends on |
|---|---|
| `UAIE-FAC-01` | — (foundation) |
| `UAIE-FAC-02` | `UAIE-FAC-01` |
| `UAIE-FAC-03` | `UAIE-FAC-01` |
| `UAIE-FAC-04` | `UAIE-FAC-01` |
| `UAIE-FAC-05` | `UAIE-FAC-01` |
| `UAIE-FAC-06` | `UAIE-FAC-01`, `UAIE-FAC-05` |
| `UAIE-FAC-07` | `UAIE-FAC-02`, `UAIE-FAC-06` |
| `UAIE-FAC-08` | `UAIE-FAC-04`, `UAIE-FAC-05` |
| `UAIE-FAC-09` | `UAIE-FAC-01`, `UAIE-FAC-04` |
| `UAIE-FAC-10` | `UAIE-FAC-03`, `UAIE-FAC-06`, `UAIE-FAC-09` |

### Dependency closure, by layer

> Layer zero depends on nothing. A faculty sits one layer above the deepest thing it
> depends on, so a total order exists exactly when the relation is acyclic.

| Layer | Faculties |
|---|---|
| 0 | `UAIE-FAC-01` |
| 1 | `UAIE-FAC-02`, `UAIE-FAC-03`, `UAIE-FAC-04`, `UAIE-FAC-05` |
| 2 | `UAIE-FAC-06`, `UAIE-FAC-08`, `UAIE-FAC-09` |
| 3 | `UAIE-FAC-07`, `UAIE-FAC-10` |
