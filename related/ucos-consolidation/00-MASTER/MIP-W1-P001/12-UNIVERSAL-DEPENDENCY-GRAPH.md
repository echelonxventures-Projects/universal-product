# 12 — Universal Dependency Graph

**Anchor** `c6c20fb` · **Canonical owners** `00-BOOK/DATA/relationships.json` (edges),
`engine.graph` (validation), `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` (derived views)

---

## 1 · Graph at the anchor

| Measure | Value |
|---|---|
| Nodes | **1,229** (1,204 artifacts + 25 volumes) |
| Edges | **12,851** |
| Edge types | **16** (8 relations × forward/inverse) |
| `is_valid` | **true** |
| `dependency_cycle` | **[] — empty** |
| `dangling_edge_endpoints` | **[]** |
| `duplicate_node_ids` / `malformed_node_ids` / `malformed_edge_ids` | **[] / [] / []** |
| `unversioned_artifacts` | **[]** |
| `depends_on_acyclic` | **true** |
| Discovered units (RIB) | 236 |
| Unresolved dependency edges | **0** (RIB GATE-06 PASS) |
| Maximum parallelism | **26** |

## 2 · Edge-type distribution

| Edge type | Count | Inverse | Count |
|---|---|---|---|
| `Depends-On` | **4,774** | `Required-By` | 4,697 |
| `Parent` | 1,211 | `Child` | 1,211 |
| `Consumes` | 316 | `Consumed-By` | 316 |
| `Authorized-By` | 99 | `Authorizes` | 99 |
| `Implements` | 48 | `Implemented-By` | 48 |
| `References` | 6 | `Referenced-By` | 6 |
| `Traces-To` | **5** | `Traced-From` | 5 |
| `Evolves-From` | 5 | `Evolves-From-Inverse` | 5 |

Two observations follow directly from this table.

**Asymmetry.** `Depends-On` = 4,774 but `Required-By` = 4,697 — a **77-edge asymmetry**. In a
fully-inverted relation store these must be equal. 77 dependency assertions have no recorded
inverse, so reverse-impact queries are incomplete by 1.6%.

**`Traces-To` = 5.** Out of 12,851 edges, exactly **five** are trace edges — 0.04% of the graph.
This is the structural expression of blocker **B-3**: the graph is dense in *structure*
(dependency, parenthood, consumption) and empty of *traceability*.

## 3 · Layered architecture — the dependency backbone (bottom-up)

```
 1  LAW Ω∞-000
 2  MIP v2 (28 universes · 25 directives) + ARCH-001..004
 3  UCGF + GOV-001..006
 4  Domain constitutions (02-MASTER) + bands 03-13
 5  CIOA spec → CCE spec                          ◄── PLANNED, not implemented
 6  EC-1 engine/                                       CERTIFIED
 7  EC-2 platform/ (composes EC-1)                     CLOSED/FROZEN
 8  UKB/UKBX + control-tower/twin/artifacts             ACTIVE
 9  MCS (00-MASTER)                                     ACTIVE
10  [FUTURE] AEOS execution spine                  ◄── ABSENT
11  [FUTURE] adapters + universal CLI              ◄── ABSENT
```

Dependency direction is strictly upward. No layer depends on a layer above it — verified by
`depends_on_acyclic: true` and RIB GATE-10.

## 4 · Programme-scope dependency edges (16)

| From | To | | From | To |
|---|---|---|---|---|
| ARCH | CAT ⟲ | | IMP | CEP ⟲ |
| ARCH | CONSOLIDATION | | IMP | CONSOLIDATION |
| CAT | ARCH ⟲ | | PLATFORM | RUN |
| CEP | IMP ⟲ | | REF | ARCH |
| DATA | PLATFORM | | RUN | ARCH |
| EES | CONSOLIDATION | | SERVICE | DATA |
| ENG | ARCH | | UMB | ADV |
| GEN | REF | | USIS | SERVICE |

⟲ = participates in a 2-cycle.

**Two programme-scope cycles:** `ARCH ↔ CAT` and `CEP ↔ IMP`. These are **not** `Depends-On` cycles
— the typed dependency plane is acyclic — but at programme granularity each pair cites the other as
an input. `CEP ↔ IMP` is the more consequential: the Constitutional Engineering Programme and the
Implementation programme are mutually dependent, which means neither can be reasoned about (or
frozen) independently of the other.

Recorded as `G-DEP-2` (output 16). Not blocking, because no gate asserts acyclicity at programme
granularity — which is itself the finding.

## 5 · Implementation-plane dependency chains

### Critical path (RIB-derived, 10 nodes)

```
platform.observability → platform.workspace → intelligence → intelligence.rie
  → intelligence.kernel → platform.universal_provider → platform.portal
  → intelligence.research → application → data
```

### Fan-in ranking (dependents)

| Rank | Unit | Dependents | Disposition |
|---|---|---|---|
| 1 | `platform.observability` | **16** | EXTEND |
| 2 | `intelligence` | 7 | EXTEND |
| 3 | `platform.universal_provider` | 2 | EXTEND |
| 4–8 | `service`, `data`, `application`, `infrastructure`, `platform.commercial_intelligence` | 1 each | EXTEND |

`platform.observability` is the highest-leverage and highest-risk node in the repository: 16
dependents, and it sits **outside the declared coverage source** (output 07 §2). A regression there
propagates to 16 units and is not caught by the canonical gate.

### Compositional layering

```
engine/  (EC-1, CERTIFIED, 17 capabilities)
   ▲ composed by
platform/  (EC-2, FROZEN, 28 capabilities)
   ▲ extended by
data/ service/ application/ infrastructure/  (EC-3 Bands 10-13, 8 capabilities)
   ◄ observed by
intelligence/  (ADDITIVE, AUTHORITY=NONE, 7 capabilities)
```

## 6 · Cycles

| Plane | Non-benign cycles | Verdict |
|---|---|---|
| Typed `Depends-On` (12,851 edges) | **0** | PASS |
| Python import, cross-unit (`CYC-ARCHITECTURAL`) | **0** | PASS — RIB GATE-10 |
| Python import, intra-unit `__init__` re-export (`CYC-INIT-REEXPORT`) | present | **declared benign** — the participants import successfully under the canonical suite |
| Programme-scope citation | **2** (`ARCH↔CAT`, `CEP↔IMP`) | ungated |

### Cycle history (closed)

Three architectural cycles existed and were eliminated at commit `6dae436` ("eliminate the three
architectural cycles by homing one contract correctly"). The named root cause was a mutual
`Depends-On` between `UCOS-ENG-000008` (ENG-004 Universal Type System) and `UCOS-ENG-000007`
(ENG-005 Universal Relationship & Reference System) via edge `UEDGE-000003640`, where ENG-005's
metadata contradicted its own `artifacts.json` dependency list. Fixed as **data**, not as a code
workaround — the correct remedy.

The associated fail-open validator defect (`UCCEP-F-003`: cycle reported while `is_valid` returned
true) is also **discharged**: `engine/graph/validation.py` now includes `dependency_cycle` in the
`is_valid` computation, and the CLI exits non-zero when invalid. Verified by reading the source and
by the passing `CK-GRAPH` json assertions.

## 7 · Redundant dependencies

| Class | Finding |
|---|---|
| Duplicate edges between the same node pair | none reported by `engine.graph` |
| Redundant inverse pairs | **the inverse relation is materialised for all 8 relations** — 12,851 edges encode ~6,426 logical relations. This doubles storage and creates a consistency obligation the store does not fully meet (the 77-edge `Depends-On`/`Required-By` asymmetry in §2 is the measured consequence). |
| Transitively implied `Depends-On` edges | not computed by any located owner — **non-derivable at this anchor** |

## 8 · Missing dependencies

| Gap | Count | Detail |
|---|---|---|
| `GAP-DEPENDENCY` — implementation units with no measured dependency in either direction | **1** | **`engine`** — the CERTIFIED root of the entire stack has no measured dependency edge. Its consumers (all of `platform/`) are real but undeclared in the dependency plane. |
| Artifacts with empty `dependencies` field | **1,014 of 1,204 (84.2%)** | dependency knowledge lives in the edge store; the artifact records are largely silent, and the two are not cross-validated |
| `Depends-On` edges lacking an inverse | **77** | reverse-impact analysis incomplete |
| Trace edges | **5 of 12,851** | traceability plane effectively unpopulated (**B-3**) |

## 9 · Invalid dependencies

| Class | Count |
|---|---|
| Unresolved dependency edges (endpoint not a discovered unit) | **0** — RIB GATE-06 PASS |
| Dangling edge endpoints | **0** (external trace markers permitted by design, UMB-007 §5) |
| Malformed edge IDs | **0** |
| Layering violations (dependency pointing down-stack) | **0** |

## 10 · Hidden dependencies

| Hidden dependency | Why it matters |
|---|---|
| **External corpus** `<repo>/../UCOS` (6,332 files, 1,944 eligible) | Closure verdicts depend on an untracked, unversioned, unhashed directory outside the repository. Its presence flips the determination between CLOSED/0-gap and NOT-CLOSED/91-gap. |
| **Connector cursors** (5 external systems) | 6 of 15 progress dimensions depend on GitHub Actions / Kubernetes / Prometheus / Trivy / SonarQube cursors last advanced 2026-07-15. Four dimensions report `BLOCKED` from staleness alone. |
| **`intelligence/` regeneration ↔ `artifacts.json`** | Regenerating any derived intelligence artifact invalidates its registry `content_hash`. Real coupling, unenforced ordering — the direct cause of **B-1**. |
| **Optional `jsonschema`** | Registry validation strength depends on an unpinned optional import (`UCCEP-F-006`). |
| **`pyproject.toml` scope declaration** | 6 code roots depend on being *absent* from `testpaths` to pass the gate; adding them would surface unknown failures (**B-4**). |

## 11 · Dependency graph verdict

| Criterion | Verdict |
|---|---|
| Every dependency mapped | **PASS** — 12,851 edges, 16 types, 0 unresolved |
| Zero cycles in the typed dependency plane | **PASS** |
| Zero cross-unit architectural cycles | **PASS** — RIB GATE-10 |
| Zero invalid / dangling / malformed edges | **PASS** |
| Layering strictly respected | **PASS** — 11 layers, no downward dependency |
| Critical path and parallelism determined | **PASS** — 10-node path, `max_parallel` = 26 |
| Inverse-relation consistency | **FAIL** — 77-edge asymmetry |
| Every implementation unit has a measured dependency | **FAIL** — `engine` isolated |
| Artifact-level dependency declaration | **FAIL** — 84.2% empty |
| Traceability edges present | **FAIL** — 5 of 12,851 (**B-3**) |
| Programme-scope acyclicity | **FAIL / UNGATED** — 2 cycles, no gate asserts this plane |
