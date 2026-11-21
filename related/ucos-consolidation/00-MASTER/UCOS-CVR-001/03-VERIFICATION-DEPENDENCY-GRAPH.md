# UCOS-CVR-001 · 03 — VERIFICATION DEPENDENCY GRAPH

> **Satisfies:** Task 6. **Anchor:** commit `898ef8d`.
> Four properties are asserted **and checked** below: no cycles · no duplicate authority ·
> no orphan verification · no conflicting ownership. Two of the four **currently fail**.

---

## PART A — THE GRAPH

Nine layers. Every edge is `produces → consumes`. No layer may read from a layer above it.

```
 L0  REPOSITORY TRUTH          git ls-files --cached  ──────────────┐  authority: version control
       │  paths + content hashes + universe digest                  │
       ▼                                                            │
 L1  CLASSIFICATION            class(u) ∈ 15, total, fail-closed    │  authority: classification decl.
       │  (u, class)                                                │
       ▼                                                            │
 L2  REGISTRATION              identity · ownership · traceability   │  authority: ukb.py + register.sh
       │  registry records                                          │
       ▼                                                            │
 L3  VERIFICATION              22 types × posture per class          │  authority: verification policy
       │  per-type results + raw evidence                           │
       ▼                                                            │
 L4  COVERAGE                  U3 measurement (aggregate + per unit) │  authority: coverage+pytest-cov
       │  coverage data + report                                    │
       ▼                                                            │
 L5  CERTIFICATION             verdicts over L3 ∪ L4                 │  authority: *_certification
       │  hash-chained certificates                                 │
       ▼                                                            │
 L6  DIGITAL TWIN              machine-readable mirror of L0..L5     │  authority: DATA/twin.json
       │  twin state                                                │
       ▼                                                            │
 L7  RELEASE READINESS         one verdict: READY / NOT READY        │  authority: aggregate gate
       │                                                            │
       └────────────── feedback is FORBIDDEN ───────────────────────┘
 L8  TEMPORAL PROVENANCE       cross-cutting sidecar: stamps L3..L6 artifacts, is read by none of them
```

### Layer contracts

| Layer | Consumes | Produces | Fail-closed condition |
|---|---|---|---|
| L0 | — | path set + digest | boundary query fails ⇒ abort (`EligibilityBoundaryError`, already implemented) |
| L1 | L0 | `(path, class)` | `count(Unknown) > 0` ⇒ fail |
| L2 | L0, L1 | registry records | eligible ∧ unregistered `> 0` ⇒ fail (already enforced: 0 today) |
| L3 | L1, L2 | per-type results | any Mandatory posture unsatisfied ⇒ fail |
| L4 | L1 (σ), L3 (test execution) | coverage report | aggregate `<` floor, per-unit `<` floor, or declared≠measured ⇒ fail |
| L5 | L3, L4 | certificates | a certificate without resolving evidence ⇒ fail |
| L6 | L0–L5 | twin | twin diverges from derivation ⇒ fail |
| L7 | L6 | verdict | any blocking gate failed ⇒ NOT READY |
| L8 | L0 (commit anchor) + external clock | temporal record | see `04`; must never be an input to L1–L7 |

---

## PART B — PROPERTY CHECKS

### B.1 No cycles — **PASS (by construction)**

The relation is a strict total order `L0 < L1 < … < L7`, and L8 has in-degree from L0 only and
out-degree to artifact *sidecars*, never to a layer's inputs. A cycle would require an edge
`Li → Lj, j ≤ i`. Three such edges are *plausible* and are explicitly prohibited:

| Prohibited edge | Why it is tempting | Why it is forbidden |
|---|---|---|
| L4 → L1 (coverage result changes the universe) | "exclude this package, it drags the number down" | makes the universe a function of the score — the exact defect D-1/D-3 |
| L5 → L3 (certification asserts a verification result) | `repo-operations.json` already does this with hand-authored `coverage: [{covered:1,total:1}]` facts | certification would then certify itself — **this edge exists today (D-6) and must be cut** |
| L6 → L0 (twin declares what exists) | twin is convenient and machine-readable | version control is the only boundary authority |

**Determination:** the graph is acyclic *as designed*; one prohibited edge (L5 → L3) **exists in
the current implementation** via `repo-operations.json`'s hand-authored acceptance facts and must
be removed by W1 of the roadmap.

### B.2 No duplicate authority — **FAIL (3 violations)**

| # | Subject | Authorities found | Resolution |
|---|---|---|---|
| V-1 | coverage threshold `90` | (a) `[tool.pytest.ini_options].addopts --cov-fail-under=90` (b) `[tool.coverage.report].fail_under=90` (c) `repo-operations.json.stages[coverage-report].min_percent=90` | one declaration; the other two derive from it |
| V-2 | coverage *ontology* | (a) line/branch coverage — `pyproject`/`coverage` (b) architectural coverage, 8 node kinds — `platform/coverage` (Universe→…→RuntimeAsset) | not duplicates but **unbound siblings**: declare them as two distinct coverage *dimensions* of one ontology, each with its own authority, and bind both to L4 |
| V-3 | test universe | (a) `pyproject.testpaths` (2 roots) (b) `determinism.yml` naming 3 test modules directly (c) `research-publication-gate.yml` running `intelligence.*` self-guards instead of tests | one derived test universe; gates select *subsets by marker*, never by path |

### B.3 No orphan verification — **FAIL (4 violations)**

An *orphan* is verification capability that no gate consumes, or verification value that no
authority claims.

| # | Orphan | Magnitude | Disposition required |
|---|---|---|---|
| O-1 | `service/tests`, `data/tests`, `infrastructure/tests`, `application/tests` | **4 117 collected, 3 995 passing, executed by no gate** | admit to the derived test universe (W2) |
| O-2 | `intelligence/tests` | 122 tests | admit **after** sandboxing its repository writes (D-11) |
| O-3 | `platform/universal_assurance` — 14 modules, policy-driven, `data/ucos-assurance-policy.json` (27 KB) + `ucos-assurance-selfcheck.json` | ~1 500 stmts, **no tests, no gate, no coverage** | either bind as the L3 policy engine (it is the closest existing fit) or record as unrealized |
| O-4 | `platform/repository_intelligence` (2 073 stmts, 0 %), `platform/providers` (107, 0 %), `intelligence/{kernel,realization,publication,research,rie}` + `intelligence/portal.py` (5 298, 0 %) | ~7 500 stmts with no test relationship at all | classification will force a disposition: production ⇒ owes tests; otherwise reclassify honestly |

### B.4 No conflicting ownership — **PASS with one unowned subject**

| Subject | Owner | Conflict? |
|---|---|---|
| eligibility boundary | `ukb.py::_repo_artifact_paths()` | no |
| corpus classification | `ukb.py::classify()` | no |
| registration | `register.sh` / `ukb.py` / `00-BOOK/DATA` | no |
| registration validation | `engine/registry/universal` | no — distinct from registration itself |
| lint | `ucos_ruff_gate` | no — single function shared by verify.sh, CI, pre-commit (already deliberately de-duplicated) |
| determinism | `engine/determinism` + per-programme `--check-determinism` | no — different subjects (blueprints vs programme rendering) |
| aggregate verdict | `00-MASTER/UCCEP-000000/uccep_engine.py` | no |
| **temporal** | **NONE in code**; declared owners `UNI-006` (Time) / `DOM-0021` (Calendar), status `SPEC/PLANNED` | **unowned in implementation** — see `04` |

### B.5 Summary verdict on Task 6

| Property | Result |
|---|---|
| No cycles | **PASS as designed**; 1 prohibited edge present today (`repo-operations.json` acceptance facts) |
| No duplicate authority | **FAIL** — V-1, V-2, V-3 |
| No orphan verification | **FAIL** — O-1..O-4 (~11 700 statements and 4 239 tests unclaimed) |
| No conflicting ownership | **PASS**, with temporal unowned |

None of these is a defect in any individual engine. All four are consequences of the missing
binding layer (L1 + L3 declaration) that this package proposes.

*End of 03-VERIFICATION-DEPENDENCY-GRAPH.md*
