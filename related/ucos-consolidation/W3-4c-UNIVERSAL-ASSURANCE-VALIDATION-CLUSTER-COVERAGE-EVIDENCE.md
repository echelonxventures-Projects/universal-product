# W3-4c — Universal Assurance validation cluster: coverage evidence

**Wave:** W3-4 (coverage campaign)
**Owned capability:** `platform.universal_assurance`
**Claimed cluster:** the dependency-independent validation cluster — `policy.py`, `config.py`, `errors.py`
**Authority:** ENGINEERING-EXECUTION-ONLY. No Repository Truth was modified. No production
code under `platform/universal_assurance/` was modified.

---

## 1. Measurement before modification

The package was measured before a single line was authored.

`platform.universal_assurance` is absent from **both** halves of the coverage gate in
`pyproject.toml`: it appears in neither the `[tool.pytest.ini_options] addopts` `--cov=`
list nor `[tool.coverage.run] source`. The absence was confirmed empirically rather than
read off the config — the full suite was run with coverage scoped to the package:

```
coverage run --branch --source=platform/universal_assurance -m pytest platform/tests engine
→ 7628 passed, 1 skipped
→ CoverageWarning: No data was collected. (no-data-collected)
```

**Baseline: 0.00%.** Not "low" — *zero*. Across 7,628 passing tests, no test in the
repository imports this package at all. All 2,299 measurable statements were unmeasured,
and the 90% gate had never seen one of them.

## 2. Cluster derivation (derived, not assumed)

The internal import graph was extracted from the package's own import statements. A module
was admitted to the claim only if the set is **closed under internal imports** — testing it
requires no in-package module outside the set except modules that are frozen to this claim.

| Module | In-package dependencies | Admitted |
|---|---|---|
| `errors.py` | *(none)* | ✅ |
| `policy.py` | `contracts`, `errors` | ✅ |
| `config.py` | `contracts`, `errors`, `policy` | ✅ |
| `registry.py` | `errors` | ⛔ ceded (§3) |
| `determinism.py` | `errors`, `policy` | ⛔ ceded (§3) |
| `planning.py`, `generation.py`, `certification.py`, `contracts.py` | — | ⛔ peer-owned |
| `execution.py`, `orchestrator.py` | — | ⛔ peer-owned |
| `evidence.py`, `measurement.py`, `intelligence.py` | — | ⛔ out of named scope |

The only inbound dependency of the claimed set is `contracts.py`, which is **imported but
never modified** — satisfying the "do not modify contracts" constraint.

`evidence.py` and `measurement.py` were excluded as *evidence* and *measurement* concerns,
not validation concerns; `intelligence.py` was excluded as dependency-**coupled** (it imports
`validation_intelligence.engine`). `execution.py`/`orchestrator.py` likewise import other
packages' engines and are therefore not dependency-independent.

## 3. Concurrency: four live sessions, two claims de-conflicted

Four peer sessions were operating on this repository during this work. The working tree was
clean at session start and had acquired peer modifications to `planning.py`,
`generation.py`, `certification.py` plus untracked peer test files before any of this work
began.

A peer declared a runtime-facing claim over `execution.py`, `orchestrator.py`, `registry.py`
and `determinism.py` — colliding with two modules of the derived set. The collision was
resolved **in the peer's favour**: `registry.py` and `determinism.py` were ceded before any
test code for them existed, because duplicating them would create parallel authority. The
claim narrowed to the three modules above.

Fixtures were **reused, not recreated**: the tests import
`platform/tests/universal_assurance_helpers.py`, authored by a third session, rather than
standing up a second fixture module for the same vocabulary.

## 4. Result

| Module | Stmts | Miss | Branch | BrPart | Cover |
|---|---:|---:|---:|---:|---:|
| `platform/universal_assurance/config.py` | 77 | 0 | 22 | 0 | **100%** |
| `platform/universal_assurance/errors.py` | 27 | 0 | 0 | 0 | **100%** |
| `platform/universal_assurance/policy.py` | 295 | 0 | 72 | 0 | **100%** |
| **TOTAL** | **399** | **0** | **94** | **0** | **100%** |

**325 tests added.** Statement *and* branch coverage are complete, with **zero partial
branches** — every branch is taken in both directions.

### Per-line determination

Every line of the claimed cluster is classified **reachable behaviour**, and every one is
tested. Consequently:

- **Unreachable behaviour:** none.
- **Dead code:** none.
- **Defensive containment:** none requiring exemption.
- **Constitutional impossibility:** none.
- **`pragma: no cover` added:** **zero.** No unreachability determination was needed, and
  none was manufactured to reach a number.

## 5. Replay determinism

Three consecutive replays were hashed over the executed / missing / excluded line sets of
the three modules, with the volatile coverage meta block stripped:

```
replay 1: 325 passed  digest=33a78bfdd6050c2d5a958e751c85b8af919d5e13d8849358c7031ed66f0f3585
replay 2: 325 passed  digest=33a78bfdd6050c2d5a958e751c85b8af919d5e13d8849358c7031ed66f0f3585
replay 3: 325 passed  digest=33a78bfdd6050c2d5a958e751c85b8af919d5e13d8849358c7031ed66f0f3585
```

**Deterministic fixed point reached.** The tests are hermetic: no wall-clock, no RNG, no
network, no ambient state, no inter-test ordering dependency.

## 6. Determination — coverage registration (SUPERSEDED BY EVENTS, recorded in full)

> **Status: this determination was correct when made and was overtaken during the wave.**
> It is preserved because the reasoning still governs *how* the registration had to be
> made, and a determination that is silently deleted once it stops binding is not
> Repository Truth. The outcome is recorded in §6.1.

`pyproject.toml:207-212` records a prior determination that `platform.universal_assurance`
"stays out until it has [tests]", because "a gate that measures what nothing tests is not a
measurement". **That determination is re-affirmed, not superseded**, and `pyproject.toml`
was left unmodified.

Two findings drive this:

1. **The advisory is keyed on the capability, not the module.**
   `platform/repository_intelligence/discovery.py:759-777` raises
   `capability-unregistered-coverage` when the capability's *path form*
   (`platform/universal_assurance`) is absent from `coverage_sources`, and
   `capability-unregistered-cov-option` when its *dotted package name* is absent from the
   `--cov` targets. Registering individual modules
   (`--cov=platform.universal_assurance.policy`) would therefore **not** clear either
   advisory. Partial registration is the wrong shape under Repository Truth.

2. **Package-level registration would break the gate for every session.** The package is
   2,299 statements; 399 are covered by this claim and 1,900 belong to modules whose tests
   are still uncommitted in peer sessions. Registering the package now moves 1,900
   untested statements into the denominator:

   | corpus | current | after registration | delta |
   |---|---|---|---|
   | 50,000 stmts | 90.0% | 86.81% | **−3.19 pts** |
   | 50,000 stmts | 91.0% | 87.76% | **−3.24 pts** |
   | 45,000 stmts | 92.0% | 88.37% | **−3.63 pts** |

   Every case lands below `--cov-fail-under=90`.

**Determination:** `platform.universal_assurance` is registered in the coverage gate once
the *whole* capability is tested — that is, after the peer claims land. The correct actor
is whichever session closes the last module, in a single package-level edit adding
`platform/universal_assurance` to `[tool.coverage.run] source` and
`--cov=platform.universal_assurance` to `addopts`. Registering it earlier trades a real gate
for a green number.

The 325 tests **do** execute in the gate today — `testpaths` collects `platform/tests` — so
the behaviour is protected now; only the denominator entry is deferred.

### 6.1 Outcome — the condition was met and the capability was registered

The deferral was conditional on 1,900 statements having no tests behind them. That
condition ceased to hold within the wave: peer sessions landed suites for the remaining
eleven modules, taking the whole package to **800 tests / 99%** (2,297 stmts, 6 miss, 372
branch, 5 partial). The registration was then performed **once, at package level**, by the
session that closed the last module — exactly the shape and sequencing this determination
prescribed.

Verified in the current tree:

- `pyproject.toml:213` — `"--cov=platform.universal_assurance"`
- `pyproject.toml:228` — `"platform/universal_assurance"` in `[tool.coverage.run] source`
- the `207-212` determination comment was rewritten in the same edit, so no stale claim
  survives.

**This session added nothing to `pyproject.toml` and touched it at no point.** The
prohibition on per-module `--cov` lines stands: they clear neither advisory and would now
also double-count.

## 6.2 Gate defect — `--cov-fail-under=90` is not a 90% floor

Verified independently at source, not accepted on report. `coverage/results.py`:

```python
def should_fail_under(total: float, fail_under: float, precision: int) -> bool:
    ...
    return round(total, precision) < fail_under
```

`precision` defaults to **0**, so the comparison is `round(total, 0) < 90`. A true total of
**89.5%–89.9999%** rounds to `90` and the gate **exits 0**. The repository's declared 90%
floor is therefore an **89.5% floor**.

Combined with `verify.sh` being non-failfast — a failed Stage 1 still lets Stages 2-6 run
and print — a `VERIFICATION PASSED` line proves neither that lint passed nor that coverage
genuinely reached 90%.

**This is outside this claim and was not modified.** It needs an explicit owner. The
remedy is `precision = 4` under `[tool.coverage.report]`, which makes the comparison
`round(total, 4) < 90`.

### Blast radius — measured, and smaller than first stated

The initial version of this determination cautioned that applying the fix "will turn the
gate red for every session at once if the true total is below 90%". That caution was
written before the true total was known, and it is **overstated at the current tree**. A
peer session measured the headroom; the figure was then re-verified here independently
from the `.coverage` the last full `verify.sh` wrote:

| measurement | value |
|---|---|
| precision 0 — what the gate compares | 94% |
| precision 4 — the honest total | **94.3053%** |
| headroom above the 90% floor | **+4.31 pts** |

The loophole only bites when the true total lands in **[89.5, 90)**. Verified against
`should_fail_under` directly:

| true total | precision 0 | precision 4 |
|---|---|---|
| 94.3053% | pass | pass |
| 89.9999% | pass | **FAIL** |
| 89.5000% | pass | **FAIL** |
| 89.4999% | FAIL | FAIL |

So `precision = 4` is a **no-op at the current total** and can be applied safely today. The
window in which the fix is harmless is exactly the window in which the corpus is
comfortably above the floor — which argues for applying it while that holds rather than
after coverage drifts down. Whoever picks it up should re-measure immediately before
applying rather than trusting this number.

**Not applied here.** Changing gate semantics repository-wide is outside this claim, and a
peer's concurrence is not authorization for it. It is surfaced to the user for decision.

## 6.3 The superseded determination follows, unaltered

## 7. Production defects discovered

**None in the claimed cluster.** All 325 tests passed against unmodified production code;
no test was weakened, skipped, or deleted to achieve a pass.

Two gaps were observed **outside** this claim and are recorded here for an owner, not fixed:

- `data/ucos-assurance-selfcheck.json` documents a `ucos-assure selfcheck` CLI, but the
  package ships no `cli.py` and `pyproject.toml [project.scripts]` publishes no
  `ucos-assure` entry point. This is the `capability-unpublished-cli` shape.
- The same file lists `platform/tests/test_universal_assurance_policy.py` as a changed path.
  That file did not exist; **this claim creates it**, closing that dangling reference.

## 8. Files added

```
platform/tests/test_universal_assurance_policy.py    146 tests
platform/tests/test_universal_assurance_config.py     54 tests
platform/tests/test_universal_assurance_errors.py    125 tests
```

No file under `platform/universal_assurance/` was modified. `pyproject.toml` was not
modified. No Repository Truth document was modified.

All three landed in commit **`845ad51`** ("W3-4c REGISTER: universal assurance gets the
tests that found run() was dead"), staged by the session that closed the last module of the
capability, together with the eleven peer suites and the single package-level registration.

## 9. Gate result

`./verify.sh` — **VERIFICATION PASSED**, all six stages green, on the tree containing this
claim:

| Stage | Result |
|---|---|
| ruff lint + format-check (engine + platform) | ✅ PASS |
| pytest + coverage gate (`--cov-fail-under=90`) | ✅ PASS — 8,775 passed, 1 skipped, 410s |
| coverage report | ✅ PASS — 63,836 stmts, 13,622 branch, **94.31%** |
| governance enforce --pre | ✅ PASS |
| registry validate (schema + integrity) | ✅ PASS — 1,220 artifacts, ledger intact |
| meta-constitutional conformance (CMG-INV-01..12) | ✅ PASS — 0 findings |

An earlier run of the same gate failed at Stage 1. The failure was measured and attributed
before any remediation: **8 findings across 7 peer-authored files, zero in this claim.**
No file belonging to another session was edited to make the gate green — the owners were
notified with the exact remediation and fixed their own files, including a production
source (`planning.py`) that was failing `ruff format --check`.

### 9.1 Commit record correction — `dfadda1` contains work this session did not author

`dfadda1`'s message describes a one-file amendment to this document. **Its actual contents
are 11 files, 2,556 insertions.** Ten of them belong to another session (Terminal T5,
`platform.validation_intelligence`):

```
platform/tests/_validation_intelligence_helpers.py
platform/tests/test_validation_intelligence_{analyzers,cli,compatibility,config,
                contracts,determinism,engine,evidence,service}.py
```

**Cause.** This session staged its own file with an explicit pathspec
(`git add W3-4c-…-EVIDENCE.md`) and then ran a bare `git commit`. An explicit `add` does
not scope a commit: bare `git commit` commits **the whole index**, and the peer session had
its files already staged in the shared index awaiting a green Stage 1. The explicit
pathspec created a false sense of containment. `git commit -- <pathspec>` was required and
was not used.

**Compounding cause — a verification that could not fail.** The post-commit check was
`git status --short | grep -v validation_intelligence`, which filtered out precisely the
signal that would have exposed the contamination, then reported `(empty = clean)`. A check
constructed so it cannot report the failure it is meant to detect is not a check. The
filter was added to reduce noise from another session's files and instead suppressed the
evidence.

**State.** Nothing is lost or altered: the working tree matches the commit, the index is
empty, and the ten files are byte-for-byte the peer's content.

**Not corrected by rewriting history.** An amend or rebase to re-split `dfadda1` on a
branch with three live sessions sharing one working tree and index would be far more
destructive than the misattribution. The record is corrected here instead. Authorship of
those ten files is Terminal T5's; `d55eb63` is clean (one file) and `845ad51` was staged by
another session.

**Practice adopted.** While sessions share this tree: explicit pathspecs on *commit*, not
just on *add* — `git commit -- <files>` — and never `-a` or `add -A`.

Tracking this document was itself measured rather than assumed safe: with it staged,
`governance enforce --pre`, `ukb.py validate`, and the CMG gate all still pass. It joins
five sibling root evidence documents already carried in the same UNREGISTERED-but-passing
state, `R-1-REPOSITORY-REPLAY-SYNCHRONIZATION-EVIDENCE.md` among them.
