# UCOS-CVR-001 · 07 — REPOSITORY IMPACT ASSESSMENT

> **Anchor:** commit `898ef8d`, working tree clean. **Anticipated, not executed.**

---

## PART A — WHAT THIS MISSION ALREADY CHANGED

| Category | Detail |
|---|---|
| Files created | 9, all under `00-MASTER/UCOS-CVR-001/` (untracked, uncommitted) |
| Files modified | **0** |
| Ratified files touched | **0** — `verify.sh`, `pyproject.toml`, `.github/workflows/*`, `Makefile`, `repo-operations.json`, every test: unmodified |
| Registration impact | **none** — `00-MASTER/` is a `config.EXCLUDE_DIR_PREFIXES` entry, so this package consumes no permanent corpus identity and cannot cause registration drift |
| Coverage artifacts | `.coverage` and `coverage.xml` untouched; all probes used `COVERAGE_FILE=/tmp/…` and were deleted |
| Working tree | `git status --porcelain` verified empty before every probe and after every probe; the only entry now is `?? 00-MASTER/UCOS-CVR-001/` |
| Gate impact | zero. `verify.sh`, `make uccep-gate` and every CI workflow behave exactly as before this session |

Probes executed (all read-only): `git ls-files`, `pytest --collect-only`, four suite executions
with an isolated coverage file, `coverage report/json` against `/tmp`, and reads of
`pyproject.toml`, `verify.sh`, `Makefile`, `repo-operations.json`, `00-BOOK/tools/{ukb,config}.py`,
`platform/coverage/*`, `platform/universal_assurance/*`, `00-BOOK/DATA/artifacts.json`,
`.github/workflows/*`.

---

## PART B — ANTICIPATED IMPACT OF IMPLEMENTATION (per wave)

Blast radius: **L** local/additive · **M** touches a ratified file · **H** changes gate outcomes.

| Wave | Radius | Files changed | Gate outcome change | Reversible |
|---|---|---|---|---|
| W0 ratification | L | 1 (status block) | none | yes |
| W1 truth + classification | L | new engine home + declaration; **no existing file** | none (non-enforcing) | yes, by deletion |
| W2 test universe | **H** | `pyproject.toml` (`testpaths`), `scripts/ucos-env.sh` (lint scope) | **+4 117 tests execute; 585 files newly linted — outcome currently unknown** | yes, 2-line revert |
| W3 coverage universe | **H** | `pyproject.toml` (`addopts`, `[tool.coverage.run]`), `repo-operations.json` | **reported coverage 94.11 % → 85.85 % against a floor of 90 ⇒ the gate FAILS unless XII.3 is decided first** | yes, restore the block |
| W4 obligations | M | declaration + new gate wiring; `Makefile` target | new blocking checks appear | per-obligation |
| W5 temporal split | M | 12 emission sites across `engine/`, `00-MASTER/` | **evidence document shapes change** ⇒ any consumer keyed on `generated_at` breaks | yes, but consumers must be found first |
| W6 certification + twin | M | `repo-operations.json`, twin assertions | acceptance stage becomes real, so it can now fail | yes |
| W7 binding | M | `uccep-bindings.json`, `.kiro/hooks/*` | the architecture becomes standing | yes |

---

## PART C — THE FOUR MATERIAL RISKS

### R-1 · The coverage cliff (W3) — **certain, quantified**

Widening `U3` to the full production universe moves the measured number from **94.11 %** to
**85.85 %** against a floor of **90**. This is arithmetic, not estimation. Contributions:

| Source | Statements | Coverage | Effect |
|---|---|---|---|
| `application` + `service` + `data` + `infrastructure` | 29 970 | 98.45 % | **raises** the aggregate |
| `intelligence/*` + `intelligence/portal.py` | 5 298 | 0 % | lowers |
| `platform/repository_intelligence` | 2 073 | 0 % | lowers |
| `platform/commercial_intelligence` | 2 335 | 51.9 % | lowers |
| `platform/validation_intelligence` (declared, unmeasured) | 842 | 0 % | lowers |
| `platform/providers` | 107 | 0 % | lowers |
| `platform/universal_assurance` | ~1 500 | untested | lowers |

**Mitigation:** the mission forbids changing thresholds, and VP-11 forbids lowering them, so the
only admissible paths are XII.3 (a), (b) or (c) — a decision reserved to the ratifying authority.
Roughly **11 000 statements at or near 0 %** are the whole problem; the four band trees are not.

### R-2 · Unknown lint debt (W2) — **unmeasured, deliberately**

585 `.py` files have never been subject to `ruff check` or `ruff format --check`. Their violation
count was **not measured** in this mission, because measuring it would have required either running
ruff over them (safe, but out of the determination's remit) or guessing. `ruff format --check` in
particular tends to flag a large fraction of never-formatted code. W2 must begin with that
measurement, and the formatting pass must be its own commit, separate from the scope change.

### R-3 · Evidence-shape change (W5) — **latent consumer breakage**

Removing `generated_at` from evidence documents changes bytes that other engines already read.
`ukb.py::_stamp_eq_json` is explicitly built around `stamp_keys=("generated_at",)`, and
`00-BOOK/DATA/*.json` all carry it (`artifacts.json` top-level keys: `generated_at`,
`generator_version`, `count`, `artifacts`). Every consumer must be located before the split, or the
drift gate will interpret a plane split as content drift.

### R-4 · Repository-writing tests (W2) — **known, bounded**

`intelligence/tests` contains `test_engine_writes_only_under_intelligence_dir`, and
`intelligence/UCOS-RIE-*.json` are tracked outputs. Admitting this suite without sandboxing would
make the canonical suite mutate tracked files, breaking lifecycle step 8 (Repository Clean). This
is why the suite was excluded from every measurement in this package, and why W2 lists it as a
prerequisite rather than a deliverable.

---

## PART D — WHAT DOES **NOT** CHANGE

| Preserved | Why it matters |
|---|---|
| Registration integrity | 1 204/1 204 registered, zero drift, zero eligible-unregistered. The architecture widens *classification*, not *registration eligibility* (Article VII.2) |
| Determinism guards | `--check-determinism` on URRC/UER/UEI/UCCEP keeps passing **unmodified**, because the deterministic plane is where the timestamps already aren't |
| `SOURCE_DATE_EPOCH = 0` | `engine/determinism/hermetic.py` is untouched |
| Stdlib-only runtime | no wave introduces a runtime dependency; W1's engine is stdlib, like every existing programme engine |
| Frozen corpus | `00-BOOK`, `00-SOURCE`, `99-FREEZE` remain read-only (DP-03); the frozen-path guard is unchanged |
| The one-command contract | `./verify.sh` remains the single canonical entry point; W2/W3 change its *scope*, never its interface |
| Existing engines | no engine is rewritten. Eleven verification authorities are **bound**, not replaced (VP-06) |

---

## PART E — EFFORT AND SEQUENCING SHAPE

Relative sizing only; no dates are given, because no temporal authority exists to express them
(Article VIII.3).

| Wave | Relative size | Dominant cost |
|---|---|---|
| W0 | XS | decision, not work |
| W1 | L | the declaration schema and the zero-enumeration guard |
| W2 | M | the lint debt in R-2, plus sandboxing `intelligence/tests` |
| W3 | S mechanically, **XL politically** | the XII.3 decision and whatever coverage work it implies |
| W4 | L | binding 22 types × 15 classes to located authorities |
| W5 | M | finding every `generated_at` consumer (R-3) |
| W6 | S | deleting hand-authored facts is small; making the real gate pass may not be |
| W7 | S | one bindings entry plus the inheritance proof |

*End of 07-REPOSITORY-IMPACT-ASSESSMENT.md*
