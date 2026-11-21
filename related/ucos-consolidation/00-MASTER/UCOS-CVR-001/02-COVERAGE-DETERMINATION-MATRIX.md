# UCOS-CVR-001 · 02 — COVERAGE DETERMINATION MATRIX

> **Satisfies:** Task 3 (coverage determination) and Task 4 (automatic discovery).
> **Anchor:** commit `898ef8d`. All percentages are measured, not projected.

---

## PART A — TASK 3 · THE σ FUNCTION

`σ : C → {CONTRIBUTES, NEVER}` — a total function on the fifteen classes. There is no third value
and no per-artifact exception.

| Class | σ | Why |
|---|---|---|
| 1 Production Runtime | **CONTRIBUTES** | executed product code; unexecuted lines are unverified behaviour |
| 2 Production Library | **CONTRIBUTES** | same |
| 3 Production CLI | **CONTRIBUTES** | an entry point is the most user-visible code in the repository; excluding it inverts risk |
| 4 Production Generator | **CONTRIBUTES** | a generator defect corrupts every artifact it emits — the highest-leverage code class |
| 5 Generated Output | **NEVER** | verified by *regeneration equality*, not execution. Counting it would let a generator inflate its own score by emitting more output |
| 6 Evidence | **NEVER** | evidence is an *observation*; measuring it measures the observer |
| 7 Documentation | **NEVER** | no executable semantics; verified by `REP`/`KNW`/link resolution |
| 8 Configuration | **NEVER** | declarations are verified by schema + declaration-integrity, not by line execution |
| 9 Tooling | **NEVER** | not shipped; verified by the fact that the gates it drives pass |
| 10 Governance | **NEVER** | instruments constrain code, they are not code |
| 11 Certification | **NEVER** | a certificate is an output of verification, never an input to it |
| 12 **Tests** | **NEVER** | *the* cardinal rule. A suite that counts itself can reach 100 % with zero product coverage |
| 13 Examples | **NEVER** | demonstrative; may be executed by tests, but must not dilute the denominator |
| 14 Temporary | **NEVER** | not part of the repository |
| 15 Unknown | **NEVER** | and simultaneously a hard gate failure — unknown artifacts cannot be admitted to a denominator that must be trustworthy |

**Coverage universe** `U3 = { u ∈ U0 : σ(class(u)) = CONTRIBUTES }` = classes 1–4, i.e. **all
production Python, and only production Python**.

### A.1 Additional coverage rules

| Rule | Statement | Rationale |
|---|---|---|
| **CR-1 Aggregate floor** | repository-wide threshold, currently `90` | preserved; the *number* is out of scope for this mission (`Do NOT change coverage thresholds`) |
| **CR-2 Per-unit floor** | every unit in `U3` must independently meet a declared floor | removes D-3. Without it, `engine/graph` at 54.5 % and a 0 %-covered shipped CLI are both *passing* states today |
| **CR-3 Declared = measured** | `|U3 declared| = |U3 in report|`; any element with no coverage data is a **failure**, never an omission | removes D-2 (`platform/validation_intelligence`, 842 stmts) |
| **CR-4 CLI floor** | every `[project.scripts]` target is a unit under CR-2 | `engine/knowledge/ukip/cli.py` = 0.0 % of 255 lines is currently invisible |
| **CR-5 No pragma inflation** | `exclude_lines` may exclude only non-semantic lines; `if __name__ == "__main__":` stays excluded, but the `main()` it calls does not | today the exclusion list is fine; it must not become an escape hatch |
| **CR-6 Threshold single authority** | the floor is declared **once** | today `90` is declared three times (`addopts`, `[tool.coverage.report]`, `repo-operations.json`) — D-9 |
| **CR-7 Ratchet, never regress** | the floor may only rise | the migration in `06` depends on this |

---

## PART B — MEASURED REALITY OF THE UNIVERSE

Measured by executing every existing test suite except `intelligence/tests` (excluded: it writes
into `intelligence/` — D-11), with an isolated `COVERAGE_FILE` in `/tmp`. **8 746 tests passed.**
The committed `.coverage` / `coverage.xml` were not touched; `git status` was empty before and after.

### B.1 Headline

| Universe | Coverage | Statements |
|---|---|---|
| Gate's curated universe (33 measured packages) | **92.00 %** (statement) / **94.11 %** (line-rate, committed `coverage.xml`) | 37 451 |
| Everything else in the production universe | **78.77 %** | 44 229 |
| **True total (`U3` as determined above)** | **84.83 %** statement · **85.85 %** branch-inclusive (pytest-cov) | 81 680 |

The declared threshold is `90`. **`U3` is therefore below the existing threshold by ~4.2 points.**
This is the single most important consequence of the mission and the reason `08` returns
`READY WITH ACTIONS` rather than `READY`.

### B.2 In-universe today, but below any reasonable per-unit floor

| Unit | Coverage | Statements | Missing |
|---|---|---|---|
| `engine/graph` | **54.5 %** | 2 041 | 929 |
| `engine/knowledge` | **80.8 %** | 6 050 | 1 162 |
| `platform/validation_intelligence` | **declared, unmeasured** | 842 | 842 |
| `engine/knowledge/ukip/cli.py` (shipped console script) | **0.0 %** | 255 lines | 255 |
| `platform/runtime_platform` | 98.8 % | 1 058 | 13 |
| `engine/context` | 98.2 % | 2 106 | 38 |

### B.3 Outside the universe today (would join `U3`)

| Unit | Coverage | Statements | Note |
|---|---|---|---|
| `application/*` | **100.00 %** | 7 642 | 0 missing — fully verified by 1 094 orphan tests |
| `service/*` | **100.00 %** | 7 063 | 0 missing — 1 070 orphan tests |
| `data/*` | **97.49 %** | 7 536 | 189 missing — 954 orphan tests |
| `infrastructure/*` | **96.52 %** | 7 729 | 269 missing — 877 orphan tests |
| `platform/workspace` | 100.0 % | 754 | covered incidentally by `platform/tests` |
| `platform/portal` | 100.0 % | 790 | incidental |
| `platform/observability` | 96.6 % | 680 | incidental |
| `platform/universal_provider` | 86.5 % | 2 208 | incidental |
| `platform/commercial_intelligence` | **51.9 %** | 2 335 | 1 122 missing |
| `platform/universal_assurance` | *(no tests, not measured)* | ~1 500 | D-12: bound to no gate |
| `platform/repository_intelligence` | **0.0 %** | 2 073 | |
| `platform/providers` | **0.0 %** | 107 | |
| `intelligence/kernel` | **0.0 %** | 588 | |
| `intelligence/realization` | **0.0 %** | 1 981 | |
| `intelligence/publication` | **0.0 %** | 1 082 | gated by `research-publication-gate.yml`, but by *determinism/validation*, never by tests |
| `intelligence/research` | **0.0 %** | 727 | same |
| `intelligence/rie` | **0.0 %** | 499 | |
| `intelligence/portal.py` | **0.0 %** | 421 | |

**Reading:** the four "band" trees (`application`, `service`, `data`, `infrastructure` — **29 970
statements at 98.45 %**, 458 lines missing, proven by 3 995 passing tests) are *pure gain*:
admitting them **raises** the aggregate. The loss comes from ~10 000 statements at 0 % in
`intelligence/*`, `platform/repository_intelligence`, `platform/providers`, plus
`commercial_intelligence` at 51.9 %. The migration in `06` sequences those two facts deliberately.

---

## PART C — TASK 4 · AUTOMATIC DISCOVERY DESIGN

### C.1 The prohibition

No path, package name, module name, directory, or file glob naming a *specific* artifact may
appear in any executable verification file — `verify.sh`, `pyproject.toml`, any workflow, any
engine. Discovery consumes **only** these six substrates, all of which already exist:

| # | Substrate | Concretely | Already exists? |
|---|---|---|---|
| S1 | Repository Truth | `git ls-files --cached --exclude-standard` via `ukb.py::_repo_artifact_paths()` + `eligibility_universe()` digest | **yes** |
| S2 | Registration | `00-BOOK/DATA/artifacts.json` (1 204 records: `path`, `category`, `program`, `owner`, `content_hash`, `traceability{unit_test, integration_test, …}`) | **yes** (corpus only) |
| S3 | Classification | `ukb.py::classify()` + `config.CLASSIFY_RULES` + path-derived catch-all (total) | **yes** (corpus axis) |
| S4 | Package ownership | `[tool.setuptools.packages.find]`, package `__init__.py`, `ARTIFACT_FAMILIES` sources | **yes** |
| S5 | Capability ownership | `00-BOOK/DATA/{artifacts,relationships,twin,certification}.json`, `platform/coverage` universe→code graph | **yes** |
| S6 | Artifact metadata | `ukb.py::read_metadata()` self-declared classification keys (`config.METADATA_CLASSIFY_KEYS`), completion reports, `[project.scripts]` | **yes** |

### C.2 The derivation

```
U0  := S1                                        # version control is the boundary
for u in U0:
    m   := S6(u)                                 # self-declared metadata wins
    r   := S2(u)                                 # registration record, if any
    o   := S4(u) ⊕ S5(u)                         # package + capability ownership
    c   := first_match(CLASS_RULES, (u, m, r, o)) or UNKNOWN
U1  := { (u, c) }
assert count(c == UNKNOWN) == 0                  # I-1, fail-closed
U2  := { (u, c, t, posture(c, t)) for t in TYPES } # policy from declaration, not code
U3  := { u : σ(c) == CONTRIBUTES }
assert U3 declared == U3 measured                 # CR-3
```

Every step is a pure function of committed bytes. Two environments at the same commit compute
identical universes — the property `eligibility_universe()` already proves by digest, extended to
the classification and coverage universes.

### C.3 Where scope comes from, per gate

| Gate | Today | Derived form |
|---|---|---|
| lint | `ruff check engine platform` | `ruff check $(select U1 where class ∈ {1,2,3,4,9,12,13})` |
| tests | `testpaths = ["engine/tests","platform/tests"]` | `select U1 where class == Tests` → every test root, discovered |
| coverage | 34 hand-written `--cov=` | `select U1 where σ(class) == CONTRIBUTES` → package roots, derived |
| omit | `omit = ["engine/tests/*","platform/tests/*"]` | `select U1 where class == Tests` |
| freeze | `repo-operations.json` `paths: []` (vacuous) | `select U1 where class == Governance ∧ frozen` |
| acceptance facts | hand-authored literals in `repo-operations.json` | measured facts only; a hand-authored fact becomes a gate failure |

### C.4 The declaration (shape only — **not** created by this mission)

One machine-readable declaration, in the pattern every programme in this repository already uses
(`uccep-bindings.json`, `uer-resilience.json`, `uei-evolution.json`, `ucos-assurance-policy.json`):

```jsonc
{
  "declaration": "ucos-verification-universe/1.0.0",
  "authority": "NONE (DERIVED TRUTH)",
  "substrates": { "repository_truth": …, "registration": …, "classification": … },
  "classes":   [ { "id": "production-cli", "precedence": 30,
                   "evidence": ["entry_point_declared", "module_main_symbol"],
                   "coverage": "CONTRIBUTES" } ],
  "types":     [ { "id": "coverage", "authority": "coverage+pytest-cov",
                   "absent": false, "unit_floor": true } ],
  "policy":    [ { "class": "production-cli", "type": "system-test",
                   "posture": "MANDATORY", "reason": "…" } ],
  "thresholds":{ "aggregate": 90, "per_unit": null, "ratchet": true }
}
```

Adding a package, a tree, a capability, a verification type, or an entire new band is **an entry in
this declaration** — never an edit to `verify.sh`, `pyproject.toml`, a workflow, or an engine.

### C.5 Self-guards the discovery engine must carry

Copied deliberately from `URRC-000001` / `UCCEP-000000`, which already implement them:

| Guard | Proves |
|---|---|
| `--check-declaration` | every substrate, class, type and policy reference resolves |
| `--check-no-enumeration` | **no class id, package name or path in the declaration appears hard-coded in the engine source** — the mechanical proof of Task 4 |
| `--check-totality` | `count(Unknown) == 0` over `U0` |
| `--check-universe-digest` | local and CI compute an identical universe digest at one commit |
| `--check-declared-measured` | CR-3 |
| `--check-write-scope` | the engine writes nothing outside its own home |
| `--check-determinism` | byte-identical output across runs |

*End of 02-COVERAGE-DETERMINATION-MATRIX.md*
