# 10 — Universal Registry Catalog

**Anchor** `c6c20fb` · 205 instruments carry `REGISTRY` or `REGISTER` in their canonical name

---

## 1 · Machine-readable registries (the operative data plane)

These are the registries that gates read and engines write. They are the ones that matter.

| # | Registry | Path | Records | Owner | Validation | Health |
|---|---|---|---|---|---|---|
| R-01 | **Universal Artifact Registry** | `00-BOOK/DATA/artifacts.json` | 1,204 artifacts × 19 fields | REG-AUTO-001 / `ukb.py` | `CK-REG-VALIDATE` PASS · schema `artifact.schema.json` | **DEGRADED — 10 stale `content_hash` (B-1)** |
| R-02 | **Typed Relationship Registry** | `00-BOOK/DATA/relationships.json` | 12,851 edges × 16 types | `engine.graph` | `CK-GRAPH` PASS — 0 dangling, 0 malformed, 0 duplicate | HEALTHY |
| R-03 | **Universal ID Ledger** | `00-BOOK/DATA/id-ledger.json` | 1,224 paths · 95 category sequences · page cursor 9,618 · 1,224 history chains | REG-AUTO-001 | append-only integrity PASS | HEALTHY |
| R-04 | **Change / Version / Lineage Ledger** | `00-BOOK/DATA/change-ledger.json` | 1,363 change events · 1,204 version records · 1,204 lineage chains · 3-bucket histogram | REG-AUTO-001 | append-only PASS | HEALTHY |
| R-05 | **Certification Store** | `00-BOOK/DATA/certification.json` | 10 domains, verdict `CERTIFIED`, 10/10 passed | UMB-017 | `CK-…`/GATE-05 PASS | HEALTHY (non-terminal) |
| R-06 | **Digital Twin Store** | `00-BOOK/DATA/twin.json` | 8 subjects · 8 dimensions · 15 signals | UMB-017 | twin certified | **STALE — generated 2026-07-16** |
| R-07 | **Control Tower Store** | `00-BOOK/DATA/control-tower.json` | 88 programmes · 15 dimensions · 6 portfolio fields | UMB | — | HEALTHY |
| R-08 | **Volume Register** | `00-BOOK/DATA/volumes.json` | 25 declared | UMB | — | **DEGRADED — `VOL-013`/`VOL-014` empty; 62% of artifacts default to `VOL-000`** |
| R-09 | **Signal Store** | `00-BOOK/DATA/signals.json` | 15 signals · run seq 267 | UMB | — | **STALE — generated 2026-07-17** |
| R-10 | **Connector Cursors** | `00-BOOK/DATA/connector-cursors.json` | 5 connectors (github-actions, kubernetes, prometheus, trivy, sonarqube) | UMB | — | **STALE — all cursors 2026-07-15** |
| R-11 | **CMG Registry** | `00-CMG/CMG-REGISTRY.json` | meta-constitutional instruments | CMG (T1 **VACANT**) | `cmg-gate` 0 findings | PROVISIONAL |
| R-12 | **RIB Unit Register** | `00-MASTER/UCOS-RIB-001/rib.json` | 236 units · 12 gates · 16 matrices · 75 metrics · 9 duplicate classes · 10 gap classes | UCIC-001 | 12/12 gates PASS | **STALE — anchored at `bde5ffa`, 2 commits behind** |
| R-13 | **RIB Blueprint** | `00-MASTER/UCOS-RIB-001/rib-blueprint.json` | integration blueprint | UCIC-001 | — | stale with R-12 |
| R-14 | **Capability Intelligence Catalog** | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | 66 capabilities | RIE (AUTHORITY=NONE) | `CK-RIE-DETERMINISM` PASS | HEALTHY (hash stale in R-01) |
| R-15 | **Dependency Intelligence Graph** | `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | 16 program edges · 11 layers · 12,851 corpus edges · `depends_on_acyclic: true` | RIE | PASS | HEALTHY |
| R-16 | **Repository Intelligence Model** | `intelligence/UCOS-RIE-MODEL.json` | composite of 9 sub-reports | RIE | PASS | HEALTHY |
| R-17 | **Concept Closure Register** | `00-MASTER/UAKOS-CLOSURE-002/closure.json` | 437 (repo) / **528 (corpus)** concepts · 26 families · 4 dispositions | FROZEN spec | `CK-CLOSURE-P1` PASS at repo scope | **NOT-CLOSED at true scope (B-2)** |
| R-18 | **Concept Graph Register** | `.../phase2.json` | 437 homed · 92,717 co-occurrence edges · seal `5f60ff67` | FROZEN spec | `CK-CLOSURE-P2` PASS | HEALTHY at repo scope |
| R-19 | **Implementation Planning Register** | `.../phase3.json` | 0 plans · 0 waves · 0 classes · verdict constant | FROZEN spec | `CK-CLOSURE-P3` **advisory FAIL** | **DEFECTIVE — `UCCEP-F-001`** |
| R-20 | **Constitutional Gate Register** | `00-MASTER/UCCEP-000000/uccep.json` + `uccep-bindings.json` | 14 gates · 16 programmes · 18 checks · 8 findings · 4 ceiling entries | CEP-009 | `CK-SELF-DECLARATION` PASS | **NOT-CERTIFIED (B-1)** |
| R-21 | **Decision Assimilation Register** | `00-MASTER/UCDA-000001/ucda.json` | decision disposition overlay | CEP-002 Art 28 | `CK-DECISION-EVIDENCE` PASS (G-14) | HEALTHY |
| R-22 | **Evolution Register** | `00-MASTER/UEI-000001/uei-evolution.json` | evolution intelligence | UEI | `uei-gate` | HEALTHY |
| R-23 | **Provider Catalog** | `platform/providers/catalog/declared-providers.json`, `repository.json` | declared providers | RC-46 | — | HEALTHY |
| R-24 | **Integration Registry** | `infrastructure/_evidence/EC3-B13-U10/integration-registry.json` | Band 13 U10 integration evidence | EC-3 B13 | band tests | **outside canonical gate** |
| R-25 | **URI Manifest** | `realization/UCOS-URI-MANIFEST.json` | realization surface | URI | — | **outside canonical gate** |
| R-26 | **Canonical Knowledge / Decisions** | `knowledge/canonical-knowledge.json`, `decisions.json` | knowledge + decision stores | CEP-002 Art 28 | via R-21 | HEALTHY |
| R-27 | **Repository Operations Declaration** | `repo-operations.json` | operations declaration | EPIC-PLAT-003 | `repo-ops.sh` | HEALTHY |

## 2 · Narrative registries (`00-BOOK/REGISTRIES/`) — 6

| Registry | Projection of |
|---|---|
| `UNIVERSAL-ARTIFACT-REGISTRY.md` | R-01 |
| `UNIVERSAL-PAGE-REGISTRY.md` | page allocation (9,618) |
| `VOLUME-REGISTRY.md` | R-08 |
| `CERTIFICATION-REGISTRY.md` | R-05 |
| `CHANGE-VERSION-LINEAGE-REGISTRY.md` | R-04 |
| `KNOWLEDGE-GRAPH-REGISTRY.md` | R-02 |

All six are **derived projections**, regenerated by `register.sh`. Two of them (`CERTIFICATION-`,
`CHANGE-VERSION-LINEAGE-`) are among the files that change when the drift in B-1 is corrected.

## 3 · Programme master registries — 20

| Registry | Programme |
|---|---|
| `08-RUNTIME/RUNTIME-REG-001-RL-F2-RUNTIME-PROGRAM-MASTER-REGISTRY.md` | Runtime |
| `09-PLATFORM/PLATFORM-018-PLATFORM-MASTER-REGISTRY.md` | Platform |
| `10-DATA/DATA-018-DATA-MASTER-REGISTRY.md` | Data |
| `11-SERVICE/SERVICE-018-SERVICE-MASTER-REGISTRY.md` | Service |
| `12-APPLICATION/APPLICATION-018-APPLICATION-MASTER-REGISTRY.md` | Application |
| `13-INFRASTRUCTURE/INFRASTRUCTURE-018-INFRASTRUCTURE-MASTER-REGISTRY.md` | Infrastructure |
| **`14-SECURITY/…-018-…`** | **ABSENT — Security has no master registry** |
| `15-…/04-REGISTRIES/USIS-021-…MASTER-REGISTRY.md` | USIS |
| `15-…/04-REGISTRIES/USIS-REG-001…012` (12) | Universe, Science, Domain, Capability, Algorithm, Model, Pattern, Insight, Reasoning-Trace, Dataset, Learned-Change, Self-Evolution |
| `02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md` | Implementation state |
| `00-BOOK/CONTROL-TOWER/UCOS-MASTER-EXECUTION-STATUS-REGISTRY.md` · `…ROADMAP-RECONCILIATION-REGISTRY.md` | Execution status · roadmap |

Total narrative registers/registries across the corpus: **205**.

## 4 · Registry governance state

| Check | Owner | Verdict |
|---|---|---|
| `CK-REG-ENFORCE` — registration & classification enforcement (pre-registration) | `ukb.py` (REG-AUTO-001 / UMB-IMP-001) | **PASS** — 1,204 eligible, 1,204 registered, 0 unregistered, 0 unclassified, 0 invalid, 1 reconciled set (CMG), 0 reconciled-set drift |
| `CK-REG-VALIDATE` — structural validation + append-only ledger integrity | `ukb.py` | **PASS** — but **degrades silently** to structural-only when `jsonschema` is absent (`UCCEP-F-006`) |
| `CK-REG-DRIFT` — atomic registration transaction + drift gate | `register.sh` (REG-AUTO-001 §16.3) | **FAIL, exit 3** — `uncommitted-registration drift — source split from projections` |

Gate consequence: **G-07 Registry Gate = FAIL** → `PROGRAM-000004` Universal Registry Evolution FAIL,
`PROGRAM-000005` Universal Repository Governance FAIL → `UCCEP-000000` **NOT-CERTIFIED**.

## 5 · Registry duplication check

| Class | Count | Determination |
|---|---|---|
| `DUP-REGISTRY` — two registered artifacts sharing one content hash outside the freeze boundary | **0** | clean |
| `GAP-REGISTRY` — units homing no artifact and publishing no interface | **0** | clean |
| Freeze-boundary copies | 2 | `SOURCE-FILES.txt` / `SOURCE-HASHES.txt` duplicated between `00-SOURCE-MANIFEST/` and `99-FREEZE/` — declared, non-blocking |
| **Second registry created by any programme** | **0** | Every derived programme (RIB, RIE, UCCEP, UCDA, closure) binds the canonical owner by pointer. This discipline holds without exception. |

## 6 · Registry catalog verdict

| Criterion | Verdict |
|---|---|
| Every registry inventoried | **PASS** — 27 machine-readable + 6 narrative projections + 20 programme registries (205 instruments total) |
| Single canonical owner per registry; no parallel registries | **PASS** — `DUP-REGISTRY` = 0 |
| Registration enforcement gated and passing | **PASS** — `CK-REG-ENFORCE` |
| Append-only ledger integrity | **PASS** |
| **Registry drift gate passing** | **FAIL** — `CK-REG-DRIFT` exit 3 at a pristine anchor (**B-1**) |
| Registry validation full-strength | **FAIL** — silent schema-check degradation (`UCCEP-F-006`) |
| Every programme has a master registry | **FAIL** — `14-SECURITY` has none |
| Registry freshness | **FAIL** — R-06/R-09/R-10 stale since 2026-07-15/16/17; R-12/R-13 two commits stale |
| Registry classification meaningful | **FAIL** — 62% of artifacts default to `VOL-000`; 2 volumes empty |
