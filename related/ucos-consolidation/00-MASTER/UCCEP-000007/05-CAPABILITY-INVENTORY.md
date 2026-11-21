# Output 5 — Capability Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` (content hash `2c740651608f8e7e…`, producer `UCOS-RIE-001 v1.0.0`, evidence timestamp 2026-07-26T02:49:04Z) parsed at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 5 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | The capability catalogue **as the located intelligence engine declares it**. Realized code volume and test evidence → Output 6. |
| EVIDENCE | `evidence/capabilities.txt` · `evidence/rie-metrics.txt` |

---

## 1. Provenance and its limit

The catalogue is not authored by this programme. It is the output of `intelligence/rie` (`UCOS-RIE-001`), which declares its own `authority` as `NONE (derived truth)` and its classification as *ADDITIVE INTELLIGENCE (machine-readable) — derived, non-authoritative*.

**Measured staleness.** The catalogue's sibling `UCOS-RIE-HEALTH.json` records `corpus.artifacts = 1197`, `edges = 12817`, `pages = 9574`. The registers at this HEAD hold **1,199 / 12,841 / 9,587** (Output 4). The RIE snapshot therefore predates the OA-1 commit by 2 artifacts, 24 edges and 13 pages. Every count below is reported as the engine recorded it, not as re-derived truth. Recorded in `12-DISCOVERY-OBSERVATIONS.md` OBS-5.

## 2. Population

| Dimension | Measured | Method |
|---|---|---|
| Capabilities catalogued | **42** | M-3 |
| Carrying evidence (`evidence_present`) | **42 of 42** | M-3 |
| `replacement_prohibited = true` | **36 of 42** | M-3 |

## 3. By declared authority band

| Authority band | Count | Reuse disposition declared |
|---|---|---|
| **EC-1 CERTIFIED** | 14 | `REUSE_AS_IS/COMPOSE` |
| **EC-2 CLOSED/FROZEN** | 22 | `REUSE/COMPOSE` |
| ACTIVE (repository automation) | 3 | `REUSE/EXTEND` |
| ACTIVE (AUTHORITY=NONE) — operational memory | 1 | `REUSE/EXTEND` |
| SPEC (AUTHORITY=NONE) — specification only | 2 | `REALIZE_BY_COMPOSITION` |

## 4. By implementation status

| Status | Count | Members |
|---|---|---|
| **CERTIFIED** | 14 | the `engine/*` layers of §5 |
| **IMPLEMENTED** | 26 | the 22 `platform/*` runtimes + `ukb.py`, `ukbx.py`, `register.sh`, `00-MASTER` |
| **PLANNED** | 2 | `CIOA` and `CCE` — orchestration specifications with no executable code |

## 5. EC-1 certified engine capabilities (14)

`engine.acceptance` · `engine.certification` · `engine.compiler` · `engine.determinism` · `engine.discovery` · `engine.factory` · `engine.foundation` · `engine.governance` · `engine.graph` · `engine.knowledge` · `engine.registry` · `engine.runtime` · `engine.universal_certification` · `engine.validation`

All 14 are `CERTIFIED`, `replacement_prohibited = true`, reuse `REUSE_AS_IS/COMPOSE`.

## 6. EC-2 platform capabilities (22)

`platform.administration` · `artifact_explorer` · `blueprints` · `certification` · `coverage` · `execution_dashboard` · `foundation` · `generation` · `identity` · `measurement` · `observability` · `portal` · `projects` · `repository_operations` · `runtime_operations` · `runtime_platform` · `security` · `universal_portal` · `universal_validation` · `validation` · `validation_intelligence` · `workspace`

All 22 are `IMPLEMENTED`, declared `CLOSED/FROZEN`, `replacement_prohibited = true`, reuse `REUSE/COMPOSE`.

## 7. Automation and operational-memory capabilities (4)

| Capability | Canonical location | Status | `replacement_prohibited` |
|---|---|---|---|
| `automation/ukb.py` | `00-BOOK/tools/ukb.py` | IMPLEMENTED | false |
| `automation/ukbx.py` | `00-BOOK/tools/ukbx.py` | IMPLEMENTED | false |
| `automation/register.sh` | `00-BOOK/tools/register.sh` | IMPLEMENTED | false |
| `master-context-system` | `00-MASTER` | IMPLEMENTED | false |

## 8. Specification-only capabilities (2)

| Capability | Canonical location | Status |
|---|---|---|
| `CIOA` | `02-MASTER/UCOS-COMP-000000-CONSTITUTIONAL-IMPLEMENTATION-ORCHESTRATION-AUTHORITY.md` | **PLANNED** — specification only, no executable code |
| `CCE` | `02-MASTER/UCOS-COMP-000001-CONSTITUTIONAL-COMPLETENESS-ENGINE-CONSTITUTION.md` | **PLANNED** — specification only, no executable code |

## 9. Related intelligence outputs

Measured list sizes only; contents belong to their producing engine.

| Output | Content hash (prefix) | Declared lists |
|---|---|---|
| `UCOS-RIE-MODEL.json` | `04731baa37af8dfe` | `capabilities` 42 |
| `UCOS-RIE-AEOS-READINESS.json` | `4dd953aaae864479` | `known_spine_gaps` 12 · `not_ready_because` 14 · `ready_because` 4 |
| `UCOS-RIE-DEPENDENCY-GRAPH.json` | `ad2a9f189b6f7eac` | `layered_architecture_bottom_up` 11 · `program_edges` 16 |
| `UCOS-RIE-EXECUTION-FRONTIER.json` | `74b9e8850fdf453b` | `critical_path` 5 · `blocked` 2 · `ready` 1 · `evidence` 2 |
| `UCOS-IMP-BASELINE-001.rib.json` | `b790a867f501c7b6` | `capability_inventory` 42 · `known_spine_gaps` 12 |
| `UCOS-RIE-HEALTH.json` | `27a102deda5e7e4a` | overall **HEALTHY**; `coverage_full = false` |
| `UCOS-RIE-DIGITAL-TWIN.json` · `PROGRESS` · `SNAPSHOT` | `b3b3cd81…` · `3e472ffa…` · `2bdfe02d…` | scalar reports |

The 12 `known_spine_gaps` are carried in `13-KNOWN-GAPS.md` DG-4 by reference, not restated here.

---

*`UCCEP-000007` Output 5. AUTHORITY = NONE (DERIVED TRUTH). Reports a located engine's catalogue; declares no capability. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
