# DEPENDENCY CLOSURE DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `DEPENDENCY-CLOSURE-DETERMINATION.md` |
| **PHASE** | Phase 4 — Dependency Closure Analysis |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** No new dependency graph is created. The canonical graph owner is `engine/uckp/graph.py`; this document measures against it. |
| **CLASSIFICATION** | `EVIDENCE` |
| **BOUNDARY** | `ASSESSMENT-BOUNDARY-DETERMINATION.md` §2, §5.3 |
| **SNAPSHOT** | `1f869865` + 113 uncommitted entries |

---

## 1. Canonical dependency authority

Determined by `00-BOOK/DATA/constitutional-authority-alignment.json` → `relationship_graph_resolution.projections` and enforced by `CAA-INV-05`.

| Role | Artifact | Enforcement | Verdict this session |
|---|---|---|---|
| **CANONICAL — model owner** | `engine/uckp/graph.py` (`UCKP-ART-07`) | `CAA-INV-05 EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER` | **PASS** (violations 0, measured 6) |
| **CANONICAL — population** | `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | `verify.sh` Stage 6b | present; regenerated 2026-08-15 11:10 |
| PROJECTION | `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` (`intelligence/rie/engine.py::_dependency_graph()`) | `authority: NONE (derived truth)` | in prerequisite chain |
| PROJECTION | `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.{json,dot,mmd}` | `authority: ENGINEERING-EXECUTION-ONLY` | **not gate-wired**; output gitignored |
| EVIDENCE (barred from authority) | ~20 static snapshots incl. `03-DEPENDENCY-GRAPH.md`, `03-IMPLEMENTATION-DEPENDENCY-GRAPH.md` | `dependency_evidence_index`: *"No historical snapshot listed here may serve as a dependency authority."* | HISTORICAL |
| **UNCLASSIFIED** | `05-DEPENDENCY-CLOSURE.md` (determination: COMPLETE) | not name-matched by the `*DEPENDENCY-GRAPH*` inventory, therefore not classified by the binding | **an unclassified determination still asserting COMPLETE** |

**D-4.1:** dependency authority is resolved for the *object* graph and unresolved for the *import* graph. The two are never reconciled — `PHASE-0.7-DEPENDENCY-GRAPH-CONSOLIDATION-READINESS-DETERMINATION.md` §4 states it directly: *"nothing currently checks for divergence at all."*

---

## 2. Declared dependency artifacts — agreement analysis

| Artifact | Claim | Baseline | Class | Agrees with measurement? |
|---|---|---|---|---|
| `03-DEPENDENCY-GRAPH.md` | L1→L8 monotone ladder, 10 edges, acyclic | `ab78f35` | HISTORICAL | Acyclicity is asserted on ladder monotonicity plus `38-DEPENDENCY-REGISTER.md`; the document itself flags the second ground as an **ASSUMPTION** |
| `03-IMPLEMENTATION-DEPENDENCY-GRAPH.md` | 5-wave layer gate, "acyclic by construction", **no intra-layer edges** | `ab78f35` | HISTORICAL | Explicitly records that `closure.json` **carries no concept→concept edges**, so acyclicity is vacuous over a 5-node chain |
| `05-DEPENDENCY-CLOSURE.md` | **COMPLETE** — 0 unknown, 0 missing, 0 circular, 0 orphan, 0 broken; chain `Data → Event → API → Workflow → Service → Application` | mission IAC-001, evidence at `b67a720` | UNCLASSIFIED | **NO.** The asserted reference chain has **no counterpart in Python imports**: `data`, `service`, `application` do not import one another at all (measured, §3) |
| `knowledge/handbooks/DEPENDENCY-REPORT.md` | `depends-on: 4`, `references: 1`, `related-to: 129`; all ~125 `UCKO-CAP-*` nodes have `—` for both dependency columns | regenerated this session (Stage 1b step 3) | GENERATED | Internally consistent, but measures a **different graph** (121-CKO knowledge store) than the ~9550-edge object graph |
| `PHASE-0.7-…CONSOLIDATION-READINESS…md` | Option C (governance recognition, not consolidation); gaps B borderline, C yes, D primary, F yes | `ed74d2d9` | HISTORICAL | Consistent with measurement; its findings remain open |
| `PHASE-0.7-…GOVERNANCE-BINDING…md` | appended 2 PROJECTION entries + `dependency_evidence_index`; 1 file changed, 0 `.py` | `ed74d2d9` | HISTORICAL | Verified — the binding is present in `constitutional-authority-alignment.json` |

**D-4.2 (evidence base is untracked).** Both `03-DEPENDENCY-GRAPH.md` §3 and `05-DEPENDENCY-CLOSURE.md` cite `38-DEPENDENCY-REGISTER.md` and `40-EXECUTION-WAVE-REGISTER.md` as their sole evidence. Both match the `.gitignore` rule `00-MASTER/UAKOS-CLOSURE-002/[0-9][0-9]-*.md`, are **not** among the 24 `!`-re-admitted names, were generated at superseded baseline `b67a720` with `AUTHORITY=NONE`, and exist on disk only because `phase3_engine.py` ran. **The dependency-closure determination rests on untracked output from a superseded baseline.**

---

## 3. Measured import dependency graph

Derived this session by grepping `^\s*(from|import) <pkg>\.` across `*.py` in each root. This is fact, not projection.

### 3.1 Edge set — 9 inter-package edges

```
platform       → engine        (234)
platform       → intelligence  (3)     ← function-local, guarded
application    → engine        (177)
service        → engine        (182)
data           → engine        (193)
infrastructure → engine        (195)
intelligence   → engine        (38)
intelligence   → platform      (2)     ← module-level, unguarded
realization    → engine        (27)
```

| Property | Measurement |
|---|---|
| `engine` outbound inter-package imports | **0** — a clean foundation sink |
| `application` / `service` / `data` / `infrastructure` mutual edges | **0** — fully disjoint leaves |
| Edges into `application`/`service`/`data`/`infrastructure` | **0** — nothing imports them, including the wheel (`packages.find include = ["engine*","platform*"]`) |
| Invalid ordering (a lower band imported by a higher one) | **none found** |
| Unresolved third-party imports | **none** — `dependencies = []` is honoured; only `pytest` (declared under `[dev]`) and `jsonschema` (`ukb.py`, declared under `[dev]`) appear |

### 3.2 Circular dependency — ONE, confirmed by direct read

**`platform ↔ intelligence`.** Exact sites verified this session:

```
platform/repository_intelligence/substrate.py:602  from intelligence.rie.config import RepoConfig
platform/repository_intelligence/substrate.py:603  from intelligence.rie.discovery import discover
platform/repository_intelligence/substrate.py:604  from intelligence.rie.evidence import EvidenceReader
        ↑ function-local (inside _catalog_from_producer), try/except ImportError, # pragma: no cover

intelligence/rie/evidence.py:25  from platform.repository_operations.coverage import load_coverage_summary
intelligence/rie/evidence.py:26  from platform.repository_operations.errors import CoverageReportError
        ↑ module-level, unguarded
```

The cycle is real at package granularity. It cannot deadlock at import time because platform's half is deferred into a function body — but that is a *runtime* mitigation, not an absence of the edge.

**Why no gate sees it — three independent reasons, all verified:**
1. `platform/repository_intelligence/config.py:78` — `code_roots: tuple[str, ...] = ("engine", "platform")`. `intelligence` contributes **no edges** to the acyclicity determination.
2. `discovery.py:516-525` reads `module.import_time_imports`, not `module.imports`, deliberately excluding `TYPE_CHECKING` and function-body imports. Platform's half is function-local, so it is excluded **by design** even if roots were widened.
3. At RPI's *unit* grain (`substrate.py::_unit_of` = root + first sub-package) the pair is `platform.repository_intelligence → intelligence.rie` and `intelligence.rie → platform.repository_operations` — different units, so no SCC forms even under a widened root set.

### 3.3 Cycle detectors present — four implementations, two wired, none over imports

| Detector | Location | Graph checked | Wired into `verify.sh`? |
|---|---|---|---|
| Tarjan SCC (iterative, deterministic) | `platform/repository_intelligence/graph.py::strongly_connected_components` (line 36) → `discovery.py::_cycles` (659) → rule `dependency-graph-acyclic` (78) | **Python imports** | **NO** — `make rpi-gate` only; output tree gitignored |
| Kahn topological order | `00-CMG/tools/cmg_validate.py::topological_order` (357) → `check_acyclicity` (378) → `CMG-INV-05` | CMG artifact `depends_on` metadata | **YES** (Stage 6) — **PASS** this session |
| Three-colour DFS | `00-BOOK/tools/ukb.py::_exec_cycle` (2101) → `EXL-17` | execution-ledger dependency graph | **YES** (Stage 5) — **PASS** this session |
| Second SCC implementation | `engine/graph/architecture/algorithms.py::strongly_connected_components` (50) | internal | **NO** — unit-tested only, no gate invokes it |

**D-4.3:** the two acyclicity checks that execute in `verify.sh` validate *declared metadata registers*. **No gate in the canonical verification path observes the Python import graph.** The one detector that does is unwired, scoped to 2 of 8 roots, and writes to a gitignored tree — the `Makefile` records this itself: *"HONEST LIMIT: … The artefacts are therefore OUTSIDE Repository Truth… Staleness returns the moment this is not run."*

---

## 4. Prerequisite ordering closure

`scripts/generate-prerequisites.sh`, invoked as `verify.sh` Stage 1b **before** the pytest stage — *"a prerequisite generated after the gate that consumes it is not a prerequisite"* (`verify.sh:104-105`). Stdlib-only and venv-free by design.

| # | Producer | Ordering constraint | Named consumers |
|---|---|---|---|
| 1 | `engine.knowledge.cli init --force` | must precede 2; `--force` required for idempotence (plain `init` exits 1 on an existing store) | — |
| 2 | `engine.knowledge.cli capabilities --write` | after 1 (11 seed CKOs → +110 projected) | — |
| 3 | `engine.knowledge.cli docs` | after 2 → 121 CKOs, 10 handbooks | `UCL-000001` REC-KNOWLEDGE, `ACEE-000001` CAP-08, `knowledge/handbooks/DEPENDENCY-REPORT.md` |
| 4 | `engine.determinism.reproduce` | independent | determinism gate; `UFEP-PRE-05` |
| 5 | `closure_engine.py` | must precede 6, 7, 10 | `UCCEP-000000` PROGRAM-000008, `UCOS-AEE-001`, `UCOS-RIB-001 MTX-PRIORITY` |
| 6 | `phase2_engine.py` | after 5 | concept/home/ownership registers |
| 7 | `phase3_engine.py` | after 5 | `38-DEPENDENCY-REGISTER.md`, `40-EXECUTION-WAVE-REGISTER.md` |
| 8 | `intelligence.research build` | independent | `UCDA-000001` DEC-CAEM-04 EQ-4 |
| 9 | `intelligence.publication build` | independent | `UCDA-000001` DEC-CAEM-04 EQ-5 |
| 10 | `provenance_engine.py` | **after 5** (reads `closure.json`) | `UAKOS-PHASE-001A-R1` — reads `provenance.json` **at module import**; all 12 of its registers stand on it |
| 11 | `intelligence.realization realize` | independent | `UGA-INV-06 EVERY_GENERATED_INPUT_HAS_BOOTSTRAP_PATH`; realization tests |

**Verified this session:** Stage 1b **PASSED** — `generated prerequisites: knowledge · determinism-evidence · closure phases 1-3 · research · publication · provenance · realization`. `UGA-INV-06` measured **PASS** (0 violations / 10 generated inputs), and `generated-artifact-registry.json` `bootstrap_gaps` is **empty**.

**D-4.4 (missing prerequisite — one remains).** `generated-artifact-registry.json` declares **30 producer homes**; Stage 1b runs **11** producers. `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.*` has **no bootstrap stage at all** — it is produced only by a manual `make rpi`. `PHASE-0.7` §10 risk 3 records that it could not determine whether this is *"intentional-but-undocumented or accidental drift."* It remains undetermined on this snapshot.

---

## 5. Hidden dependencies

Generated paths that gates consume, cross-referenced against `.gitignore` (214 lines, every rule classified in `exclusion-register.json`).

| Ignored path | Producer | Consumer that would fail on a clean clone | Bootstrap? |
|---|---|---|---|
| `/knowledge/` | steps 1–3 | `UCL-000001`, `ACEE-000001` CAP-08, `DEPENDENCY-REPORT.md` | YES (1b) |
| `00-MASTER/UAKOS-CLOSURE-002/{[0-9][0-9]-*.md,closure.json,phase2.json,phase3.json}` | steps 5–7 | `UCCEP-000000`, `UCOS-AEE-001`, `UCOS-RIB-001 MTX-PRIORITY`; **`38-`/`40-` — the evidence base of `05-DEPENDENCY-CLOSURE.md`** | YES (1b) |
| `determinism-evidence/` | step 4 | determinism gate, `UFEP-PRE-05` | YES (1b) |
| `intelligence/UCOS-URI-001/`, `UCOS-UPI-001/` | steps 8–9 | `UCDA-000001` EQ-4/EQ-5 (measured on a pristine clone: both resolved `[]`, dropping `dimensions_covered` 278 → 276) | YES (1b) |
| `00-MASTER/UAKOS-PHASE-001B/provenance.json` | step 10 | `UAKOS-PHASE-001A-R1` **at module import** | YES (1b) |
| `/realization/` | step 11 | `UGA-INV-06`, realization tests | YES (1b) |
| `.coverage*`, `coverage.xml` | pytest-cov | `platform.repository_operations.coverage::load_coverage_summary` ← imported by `intelligence/rie/evidence.py:25` — **simultaneously the module-level half of the import cycle** | implicit (Stage 2) |
| `.runtime/` | `governance_telemetry.py`, **RPI** | the import-dependency graph itself | **NO** |
| `00-MASTER/**/evidence/` | programme engines | `EV-PROGRAMME-EXECUTION-LOG` (population 76, `may_affect_certification: false`) | NO |
| `00-MASTER/UAKOS-PHASE-004/10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.json` | phase engine | phase consumers | NO |

`.gitignore` records two prior failures of exactly this class, in its own words: the P0-FINAL-CONVERGENCE-001 block (*"the ignore rule hid AUTHORED Repository Truth that TRACKED declarations depend on. A fresh clone could never resolve them"*) and the UCOS-CL-002/CL-017 withdrawal (*"it manufactured cleanliness… An exclusion rule must never be an input to the gate that polices the excluded state"*).

**Verified closed:** `exclusion-register.json` invariant `ignored_unclassified = 0`, and `uga_engine.py` UGA-INV-05/06 both PASS. The hidden-dependency class is **closed for the 10 declared generated inputs** and **open for `.runtime/`**.

---

## 6. Dependency closure determination

| Question | Answer | Evidence |
|---|---|---|
| Circular dependencies (object graph)? | **NO** | `CAA-INV-05` PASS; `CMG-INV-05` PASS; `EXL-17` PASS |
| Circular dependencies (import graph)? | **YES — 1** (`platform ↔ intelligence`) | `substrate.py:602-604` ↔ `evidence.py:25-26`, read directly |
| Is that cycle detected by any gate? | **NO** | 3 independent scope reasons, §3.2 |
| Unresolved dependencies? | **NO third-party**; **1 unbootstrapped generated input** (`.runtime/` RPI graph) | import census; `bootstrap_gaps: []` vs 30 producer homes |
| Hidden dependencies? | **10 declared and bootstrapped**; **1 undeclared-bootstrap** (`.runtime/`) | §5 |
| Missing prerequisites? | **NO** for the 11 wired producers | Stage 1b PASS, UGA-INV-06 PASS |
| Invalid ordering? | **NO** | band→engine direction is uniform; `engine` has 0 outbound edges |
| Is the declared closure evidence current? | **NO** | `05-DEPENDENCY-CLOSURE.md` rests on `38-`/`40-` at baseline `b67a720`, `AUTHORITY=NONE`, untracked |
| Does the declared reference chain match reality? | **NO** | `Data → Event → API → Workflow → Service → Application` has 0 corresponding import edges |

### Determination

**DEPENDENCY CLOSURE: PARTIAL.**

Closed and machine-enforced for the object/metadata plane: one relationship-graph model owner (`CAA-INV-05` PASS), acyclic constitutional dependencies (`CMG-INV-05` PASS), acyclic execution ledger (`EXL-17` PASS), 0 dangling / 0 unrooted / 0 orphan edges over 1233 artifacts and 12 899 edges (`utce_engine.py --gate` OPEN), and every declared generated input bootstrapped (`UGA-INV-06` PASS, `bootstrap_gaps: []`).

**Not closed** for the code plane, on three measured grounds:

1. **One genuine import cycle exists** (`platform ↔ intelligence`) and is invisible to every configured gate — by root scope, by import-kind selection, and by unit granularity.
2. **No gate in `verify.sh` observes the Python import graph.** The only detector that does is unwired, covers 2 of 8 roots, and writes to a gitignored tree.
3. **The authored closure determination is stale and unclassified.** `05-DEPENDENCY-CLOSURE.md` asserts COMPLETE from evidence generated at a superseded baseline, marked `AUTHORITY=NONE`, that a clean clone does not contain — and its asserted reference chain contradicts the measured import graph.

Per boundary §4.1, dependency closure is **not** marked COMPLETE.
