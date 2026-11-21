# Output 4 — Dependency Validation Report

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000005` · PHASE 6 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| LOCATED OWNERS | `engine/graph` (UCOS-EPIC-002) · `engine/graph/architecture` (UCOS-EPIC-010) |
| EVIDENCE | `evidence/post/dependency-derivation.json` |

---

## 1. Verdicts

| # | Required verification | Measured | Verdict |
|---|---|---|---|
| V-01 | No dependency cycles | `dependency_cycle = []` · `acyclic = true` | **PASS** |
| V-02 | SCC count >1 = 0 | components 1199, with >1 member = **0** | **PASS** |
| V-03 | No hidden dependencies | `declared_not_projected = []` — every dependency declared in `artifacts.json` is present in the graph | **PASS** |
| V-04 | No duplicate dependencies | `duplicate_dependency_edges = []` · `duplicate_edge_ids = []` | **PASS** |
| V-05 | No malformed dependencies | `malformed_dependency_edges = []` · `dependency_endpoints_unknown = []` · `self_loops = []` | **PASS** |
| V-06 | Deterministic ordering | 1199/1199 ordered · `ordering_complete = true` · identical sha256 across repeated derivations | **PASS** |
| V-07 | Critical Path | length 164 · `cyclic = false` · derivable and well-defined | **PASS** |
| V-08 | Parallel Groups | 164 groups · 1199 members · every member independent of its group peers | **PASS** |
| V-09 | Repository Integrity | `ukbx certify` 10/10 integrity domains CERTIFIED | **PASS** |

## 2. Graph measurements

| Metric | Baseline | Post |
|---|---|---|
| Artifact nodes | 1199 | 1199 |
| Total nodes | 1224 | 1224 |
| Total edges | 12843 | 12841 |
| `Depends-On` artifact edges | 4776 | 4774 |
| Strongly-connected components | 1197 | **1199** |
| Components with >1 member | 1 | **0** |
| Self-loops | 0 | 0 |
| Dangling edge endpoints | 0 | 0 |
| Duplicate node ids | 0 | 0 |
| Malformed node/edge ids | 0 / 0 | 0 / 0 |
| Unversioned artifacts | 0 | 0 |

**Edge-count delta explained (−2).** With the corrected ordering, two `metadata:DEPENDS ON`
edges (`ENG-005→ENG-004`, `ENG-004→ENG-003`) now coincide with the `structural:chain`
edges the generator emits for the same pairs, so the generator de-duplicates them
instead of emitting a second edge in the opposite direction. Two contradictory edges
became one agreeing edge, twice. No dependency relation was lost: `V-03` proves every
declared dependency is still projected.

## 3. Declared vs projected parity

| Measure | Value |
|---|---|
| Declared dependency pairs (`artifacts.json`) | 190 |
| Projected `Depends-On` pairs (`relationships.json`) | 4774 |
| Declared but **not** projected | **0** |
| Projected but not declared | 4584 |
| Parent pairs | 1198 |
| Endpoints not resolving to a registered artifact | **0** |
| Duplicate edge ids | **0** |

`Declared but not projected = 0` is the hidden-dependency test: nothing an artifact
declares is missing from the graph. The 4584 additional projected pairs are the
front-matter `DEPENDS ON` edges the generator derives from each instrument's own
metadata — by design, not hidden dependencies: `artifacts.json.dependencies` carries the
chain predecessor, while the metadata edges carry the artifact's full self-declaration.

## 4. ENG family — every edge verified downward-only

The 27 metadata-derived ENG `Depends-On` pairs were individually checked against
`ENG-GOV-001` Option B. All point from a later position to an earlier one:

| Source | Depends on | Direction |
|---|---|---|
| `UCOS-ENG-000007` (ENG-005 Rel) | `000008` (ENG-004 Type), `000009` (ENG-003 Value), `000006` (ENG-002), `000005` (ENG-001), `000003` (ENG-000) | downward |
| `UCOS-ENG-000008` (ENG-004 Type) | `000009` (ENG-003 Value), `000006`, `000005`, `000003` | downward |
| `UCOS-ENG-000009` (ENG-003 Value) | `000006` (ENG-002), `000005` (ENG-001), `000003` (ENG-000) | downward |
| `UCOS-ENG-000006` (ENG-002 Object) | `000005` (ENG-001) | downward |
| `UCOS-ENG-000005` (ENG-001 Identity) | `000003` (ENG-000) | downward |
| `UCOS-ENG-000001/000002/000004` (ENG-GOV-003/002/001) | the architecture artifacts they govern | downward |

No edge points upward or forward. `ENG-000 ENG-L-05/06` (downward-only, acyclic) holds
by construction.

## 5. Determinism

| Determinism claim | Method | Result |
|---|---|---|
| Dependency derivation | 3 consecutive runs of `derive.py --stage post` | identical sha256 (`4fb76830…`) |
| Gate verdict (negative path) | 3 consecutive `engine.graph.cli validate` runs | identical sha256 (`2542099a…`) |
| Gate verdict (positive path) | 2 consecutive runs | identical sha256 (`00ca3363…`) |
| Repository regeneration | second `ukb build`, hashes compared | **byte-identical** on `artifacts.json`, `relationships.json`, `volumes.json`, `id-ledger.json` |
| Repository intelligence | `intelligence.rie verify` | `deterministic: true`, `mismatches: []`, 10 outputs |
| Compiler double-build | `engine.determinism.reproduce` | `[PASS] double_build byte_identical=True` |

Evidence: `evidence/post/T-3-regeneration-determinism.txt`,
`evidence/post/T-3-rie-determinism.json`, `evidence/post/T-3-determinism-build.log`,
`evidence/post/T-2-gate-paths.txt`.

## 6. Repository integrity — `ukbx certify` (UMB-IMP-006 / UMB-017)

| Domain | Verdict |
|---|---|
| 1 Identity · 2 Registry · 3 Traceability · 4 Knowledge Graph · 5 Change Intelligence | PASS |
| 6 Version · 7 Lineage · 8 Synchronization · 9 Twin Intelligence · 10 Execution | PASS |

**CERTIFIED — 10/10.** Scope: 1199 artifacts, 15 signals, 1353 change events.

---

**DEPENDENCY VALIDATION: 9/9 PASS · GRAPH ACYCLIC · SCC>1 = 0 · ORDERING DETERMINISTIC AND COMPLETE**
