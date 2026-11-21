# VERIFICATION CLOSURE REMEDIATION DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `VERIFICATION-CLOSURE-REMEDIATION-DETERMINATION.md` |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** Remediation plan only. **No new architecture. No new owner. No new registry. No new terminology.** Every action below is an edit to an existing artifact or an invocation of an existing producer. |
| **CLASSIFICATION** | `EVIDENCE` |
| **BOUNDARY** | `ASSESSMENT-BOUNDARY-DETERMINATION.md` §4.1 — no item may be marked COMPLETE until Specification → Implementation → Test → Validation → Evidence → Certification all exist |
| **SNAPSHOT** | `1f869865` + 113 uncommitted entries |
| **BASIS** | `VERIFICATION-EVIDENCE-REPORT.md` (measured gate results) · `IMPLEMENTATION-REALITY-ASSESSMENT.md` (coverage/test census) · `CAPABILITY-COVERAGE-CLOSURE-DETERMINATION.md` (chain gaps) |

---

## 0. Reuse declaration

No item in this plan creates an artifact type that does not already exist. Every change lands in one of these existing owners:

| Change surface | Existing owner | Precedent for this kind of edit |
|---|---|---|
| Coverage denominator, `testpaths` | `pyproject.toml` | 59 `--cov=` targets already added incrementally |
| Gate wiring | `verify.sh` | Stages 1b, 6b, 6c, 6d were each added the same way |
| Gate targets | `Makefile` | 51 gate targets already exist |
| Identity minting | `00-MASTER/UCOS-UGA-001/uga_engine.py run` | the engine names this remedy itself |
| Generated-artifact declaration | `00-BOOK/DATA/generated-artifact-registry.json` | 344 entries, 30 producer homes |
| Prerequisite ordering | `scripts/generate-prerequisites.sh` | 11 producers already declared |
| Certification classes | `00-BOOK/DATA/certification.json` + `00-BOOK/tools/ukbx.py certify` | `certification_class` field already in use in band evidence (`"engineering-readiness"`) |
| Capability fields | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` schema | already carries 12 fields incl. `unique_id`, `evidence_present` |

---

## 1. P0 — Verification coverage for authority-bearing code

**Problem, measured.** The code that *enforces* the corpus is the least verified code in it.

| Subject | py | LOC | Tests | In `--cov`? | Gates depending on it |
|---|---|---|---|---|---|
| `engine/constitution/` | 17 | **6 888** | in `engine/tests` (collected) | **NO** | ships the `ucos-cel` console script (published entry point) |
| `engine/uicm/` | 10 | **5 343** | unknown | **NO** | **untracked** — outside the version-controlled boundary |
| `00-MASTER/**` engines | 48 | **57 629** | **0** | **NO** | **20 of 28 CI workflows** invoke one of these |
| `00-BOOK/tools/` | 13 | **6 476** | **0** | **NO** | `verify.sh` Stages 4, 5, and `--full` Stage 7 |
| **Total** | **88** | **76 336** | — | — | — |

Historical proof this gap is not theoretical: `pyproject.toml` records that `ukb.py:1733-1735` swallowed `ImportError` and exited 0, so `verify.sh` Stage 5 reported PASS having validated **nothing**, letting **539 schema violations** pass undetected through every gate.

### P0-1 — Actions

| ID | Action | File to edit | Acceptance criterion (measurable) |
|---|---|---|---|
| **P0-1.1** | Add `--cov=engine.constitution` to the addopts list and to `[tool.coverage.run] source` | `pyproject.toml` | `coverage report` lists `engine/constitution/*`; aggregate stays ≥ 90 % |
| **P0-1.2** | `git add engine/uicm/` and `00-MASTER/UCOS-UICM-000001/`, then run `uga_engine.py run` to mint identity, then add `--cov=engine.uicm` | `pyproject.toml`, index | `uga gate` UGA-INV-01 measures `engine/uicm/*`; `coverage report` lists it |
| **P0-1.3** | Create `00-MASTER/tests/` **or** `engine/tests/master_engines/` — whichever the human authority selects — holding one test module per gate engine that asserts (a) `--gate` exit code is deterministic across two runs, (b) `--gate` writes **zero** files, (c) each `--check-*` flag is reachable | new test files under an **existing** test root | ≥ 1 test module per engine invoked by a CI workflow (**20 engines minimum**); all collected |
| **P0-1.4** | Add tests for `00-BOOK/tools/ukb.py`, `ukbx.py`, `config.py` and the 9 connectors, starting with a regression test that `validate` **fails** when `jsonschema` is absent (the 539-violation failure mode) | `platform/tests/` or a new `00-BOOK/tests/` | the historical silent-pass is covered by a failing-on-absence test |
| **P0-1.5** | Add `--cov=` entries for the `00-MASTER` engine package and `00-BOOK/tools` once P0-1.3/1.4 land | `pyproject.toml` | 76 336 LOC enters the denominator; threshold held |

**Ordering constraint:** P0-1.2 must run `uga_engine.py run` **before** `git add` is gated, otherwise minting an already-tracked anonymous file is what UGA-INV-01 is currently failing on.

**P0-1 completion test (boundary §4.1):** every one of the 88 modules has Specification (its programme determination), Implementation (present), Test (≥ 1 collected), Validation (in the coverage denominator and in a gate), Evidence (gate transcript), Certification (named `certification_class`). Until all six exist for all 88, P0-1 is `PARTIAL`.

---

## 2. P0 — Connect existing tests into canonical verification gates

**Problem, measured.** 3879 authored tests are collected by nothing.

| Root | Test files | Tests | Collected today |
|---|---|---|---|
| `application/tests` | 44 | **1 082** | NO |
| `service/tests` | 52 | **1 038** | NO |
| `data/tests` | 48 | **887** | NO |
| `infrastructure/tests` | 44 | **821** | NO |
| `realization/tests` | 3 | **51** | NO |
| **Total** | **191** | **3 879** | — |

Verified absence: grepping `Makefile`, `verify.sh`, all 28 workflows and `pyproject.toml` for `application/tests|service/tests|data/tests|infrastructure/tests|--cov=application|--cov=service|--cov=data|--cov=infrastructure` returns **zero matches**. `make test` is bare `pytest`, so it inherits `testpaths` and skips them too.

### P0-2 — Actions

| ID | Action | File to edit | Acceptance criterion |
|---|---|---|---|
| **P0-2.1** | Extend `testpaths` to `["engine/tests","platform/tests","intelligence/tests","application/tests","service/tests","data/tests","infrastructure/tests"]` | `pyproject.toml:200` | `pytest --collect-only` reports ≥ 15 133 tests (11 305 + 3 828) |
| **P0-2.2** | Run the four band suites **once, in isolation, before wiring**, to establish their true pass rate. Their status today is UNKNOWN and UNKNOWN fails closed | — | a recorded pass/fail count per root; **this is a measurement step, not a fix** |
| **P0-2.3** | Add `--cov=application --cov=service --cov=data --cov=infrastructure` after P0-2.2 confirms green | `pyproject.toml` | 128 073 LOC enters the denominator; aggregate re-baselined |
| **P0-2.4** | Decide `realization/tests` disposition: the tree is **generated** and `.gitignore`d, so its tests can only run after Stage 1b step 11. Either add it to `testpaths` (relying on Stage 1b ordering) or leave it as producer-local | `pyproject.toml` or `generate-prerequisites.sh` | **human decision** — recorded, not assumed |
| **P0-2.5** | Add the band roots to `[tool.setuptools.packages.find] include` **or** record explicitly why four implemented bands are not packaged | `pyproject.toml` | either packaged, or a declared exclusion with a reason |

**Risk, stated plainly.** P0-2.1 may drop the aggregate coverage percentage or surface failures in 3828 never-executed tests. That is the point: the current 97.59 % is high partly because 44 % of the code is not in the denominator. **Re-baselining the threshold downward temporarily is acceptable; leaving the tests uncollected is not.** Sequence P0-2.2 before P0-2.1 so the blast radius is known before the gate is armed.

---

## 3. P0 — Separate documentation / implementation / executable certification

**Problem, measured.** One certification record does all the work and covers none of the code.

| Fact | Value | Source |
|---|---|---|
| Certification records repository-wide | **1** | `00-BOOK/DATA/certification.json` |
| Standard | `UMB-017 Digital Twin Certification (non-terminal)` | ibid. |
| Verdict | CERTIFIED, 10/10 domains, 25/25 checks | ibid. |
| Scope | 1233 artifacts · 12 899 edges · **0 executions** | ibid. |
| `.py` files in the certified population | **0** | `artifacts.json` census |
| Implementation actually present | 328 628 LOC / 1795 files / 13 542 test functions | `UCOS-RIE-HEALTH.json` |
| The `execution` domain passes on | *"0 executions ledgered"* — an empty set | `certification.json` |

### P0-3 — Actions

Three certification classes, using the **existing** `certification_class` field already present in band evidence (`"certification_class": "engineering-readiness"` in `application/_evidence/EC3-B12-U07/cce-certification.json`). No new vocabulary is introduced.

| ID | Class | Subject | Authority (existing) | Evidence surface (existing) | Acceptance criterion |
|---|---|---|---|---|---|
| **P0-3.1** | `documentation` | the 1233 registered corpus artifacts | `UMB-017` via `ukbx.py certify` | `certification.json` | current record re-labelled with `certification_class: documentation`; **scope statement made explicit that it excludes code** |
| **P0-3.2** | `implementation` | the 2027 tracked `.py` modules | to be vested — candidate `engine/universal_certification/` (10 modules, already in `--cov`) | per-package coverage + gate transcripts | a record whose scope counts `.py` files > 0 |
| **P0-3.3** | `executable` | gate runs and their exit codes | `UCOS-UGA-001` for identity, per-programme engines for verdicts | the append-only execution ledger that `ukb.py validate` already reports on (`0 execution(s)` today) | `ukb.py validate` reports `> 0 execution(s)`; the `execution` domain stops certifying an empty set |

| ID | Supporting action | File | Criterion |
|---|---|---|---|
| **P0-3.4** | Record in `certification.json` that the three classes are disjoint and that no class may inherit another's verdict | `00-BOOK/DATA/certification.json` | an explicit non-inheritance statement, mirroring the pattern already used in `mutation-governance-boundary.json` (`governs` / `does_not_govern`) |
| **P0-3.5** | Ledger executions so the `execution` domain has a non-empty population | existing forward-only ledger via `ukb.py` | `executions: 0` → `> 0` |

**Why this is P0 and not P1.** Until the classes are separated, every reading of "the repository is CERTIFIED" is true of the documentation and false of the code, and the artifact does not say so. That is the single most misleading fact in the repository.

---

## 4. P1 — Expand the coverage measurement boundary

**Current denominator:** 59 `--cov=` targets ≈ 74 910 statements / 16 542 branches ≈ 283 500 LOC, at **97.59 %**.
**Outside it:** 647 files / **224 647 LOC** ≈ 44 % of repository Python.

| ID | Action | Adds to denominator | Depends on |
|---|---|---|---|
| **P1-4.1** | `engine.constitution`, `engine.uicm` | 12 231 LOC | P0-1.1, P0-1.2 |
| **P1-4.2** | `application`, `service`, `data`, `infrastructure` | 128 073 LOC | P0-2.2, P0-2.3 |
| **P1-4.3** | `intelligence` | 17 856 LOC | tests already collected; needs `--cov=intelligence` only |
| **P1-4.4** | `00-MASTER` engines | 57 629 LOC | P0-1.3 |
| **P1-4.5** | `00-BOOK/tools` | 6 476 LOC | P0-1.4 |
| **P1-4.6** | `realization` | 2 382 LOC | P0-2.4 (generated-tree decision) |
| | **Target denominator** | **~508 000 LOC (100 % of non-test Python)** | |

| ID | Guard | Criterion |
|---|---|---|
| **P1-4.7** | Add a gate asserting the denominator is complete — that every non-test `.py` under a declared code root appears in `[tool.coverage.run] source` | a new check inside the **existing** `verify.sh` coverage stage; a package added without a `--cov` entry fails the build |
| **P1-4.8** | Re-baseline `--cov-fail-under` honestly: set it to the measured post-expansion floor, then ratchet upward. Do **not** hold 90 % by shrinking the denominator | the threshold is a floor over 100 % of the code, not over a chosen subset |

**P1-4.7 is the item that prevents recurrence.** Every other action in this plan is a one-time expansion; without a completeness gate on the denominator itself, the next new package silently repeats the pattern.

---

## 5. P1 — Package-level chain closure

For each package, all six links must exist. Current state, measured:

| Package | Spec | Impl | Test | Validation | Evidence | Certification | Verdict |
|---|---|---|---|---|---|---|---|
| `engine/` | ✓ | ✓ | ✓ | ◐ (2 subpkgs unmeasured) | ✓ | ◐ (via gates only) | **PARTIAL** |
| `platform/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ (no authority names it) | **PARTIAL** |
| `application/` | ✓ | ✓ | ✓ | ✗ | ✓ (110 JSON) | ✗ | **REQUIRES REMEDIATION** |
| `service/` | ✓ | ✓ | ✓ | ✗ | ✓ (136 JSON) | ✗ | **REQUIRES REMEDIATION** |
| `data/` | ✓ | ✓ | ✓ | ✗ | ✓ (132 JSON) | ✗ | **REQUIRES REMEDIATION** |
| `infrastructure/` | ✓ | ✓ | ✓ | ✗ | ✓ (121 JSON) | ✗ | **REQUIRES REMEDIATION** |
| `intelligence/` | ✓ | ✓ | ✓ | ◐ (code unmeasured) | ✓ | ✗ | **PARTIAL** |
| `realization/` | ✓ | ✓ (generated) | ✓ | ✗ | ✓ | ✗ | **GENERATED** |
| `00-MASTER/**` | ✓ | ✓ | **✗** | ✗ | ✓ (self-issued) | ◐ (self-issued) | **REQUIRES REMEDIATION** |
| `00-BOOK/tools/` | ✓ | ✓ | **✗** | ✗ | ✗ | ✗ | **REQUIRES REMEDIATION** |

### P1-5 — Actions

| ID | Action | Where | Criterion |
|---|---|---|---|
| **P1-5.1** | Store the five `UCIC-001` Output-2 fields per capability — `CAPABILITY IDENTIFIER`, `GOVERNING DETERMINATION`, `CONSTITUTIONAL ANCHOR`, `EVIDENCE REQUIREMENTS`, `CERTIFICATION REQUIREMENT` | extend the **existing** `UCOS-RIE-CAPABILITY-CATALOG.json` schema (already has `unique_id`, `evidence_present`) | all 122 capabilities carry all five; a capability missing one fails a gate |
| **P1-5.2** | Join the three disjoint key spaces (`RC-nn` / `UCAF-CAP-nn` / `CMG-DLG-nn`) by adding the constitution anchor to each catalog entry | same file | ≥ 1 resolvable constitution per capability; today **1 of 122** has a verified chain (`UCAF-RB-01`) |
| **P1-5.3** | Declare the 46 undeclared python directories as capabilities — chiefly the 40 `00-MASTER/**` engine homes now collapsed into one entry pointing at a directory with no `.py` in it | same file | 0 undeclared python directories |
| **P1-5.4** | Add a chain-completeness gate: every capability resolves owner → constitution → implementation → test → coverage → evidence → certification, or the build fails | new check in **existing** `verify.sh` | the gate reports N/122 complete; today it would report 1/122 |
| **P1-5.5** | Resolve the two `PLANNED` authorities blocking `UCIC-001` execution: `SPEC-CIOA` (Stage 1) and `SPEC-CCE` (Stage 10) | `02-MASTER/UCOS-COMP-000000/000001` | `UCIC-001` becomes executable, or the contract is amended to name implemented authorities |
| **P1-5.6** | Bind `14-SECURITY` (5 docs, no `security/` root) and `08-RUNTIME` (18 docs, no `runtime/` root) — either create the root or declare the dispersed realization as the binding | band constitutions + catalog | both bands resolve to an implementation |
| **P1-5.7** | Wire the import-acyclicity detector into `verify.sh` and widen `code_roots` from `("engine","platform")` to all 8 roots | `platform/repository_intelligence/config.py:78`, `verify.sh` | the `platform ↔ intelligence` cycle becomes visible; then fix or declare it |
| **P1-5.8** | Give the `.runtime/` RPI dependency graph a bootstrap stage, so 30 producer homes are matched by 30 bootstrapped producers (11 today) | `scripts/generate-prerequisites.sh`, `generated-artifact-registry.json` | the dependency graph is reproducible on a clean clone |

---

## 6. Execution sequence

Dependency-ordered. Each step is verifiable before the next begins.

| Step | Action | Gate that turns green | Effort |
|---|---|---|---|
| **1** | `uga_engine.py run` — mint the 8 anonymous objects | `verify.sh` Stage 6b **and** both Stage 2 test failures → **`./verify.sh` exits 0** | one command |
| **2** | Decide freeze scope; commit or revert the 113 working-tree entries | `rib gate` GATE-12 (`dirty=166` → 0) | human decision |
| **3** | Resolve CK-BASELINE, CK-UCL, CK-UIS; re-run UCCEP at tier `full` | `uccep gate`, and transitively `ufep` `UFEP-CC-01/02` → freeze gate opens | 3 programme checks |
| **4** | P0-2.2 — run the four band suites in isolation and record the result | nothing yet; converts UNKNOWN into a number | measurement |
| **5** | P0-2.1, P0-2.3 — wire band tests into `testpaths` and `--cov` | +3828 tests, +128 073 LOC measured | config + fixes |
| **6** | P0-1.1, P0-1.2 — cover `engine/constitution`, track and cover `engine/uicm` | +12 231 LOC measured | config + `git add` |
| **7** | P0-3.1…P0-3.5 — separate the three certification classes; ledger executions | `executions: 0` → `> 0`; "CERTIFIED" stops meaning documentation-only | registry edits |
| **8** | P0-1.3, P0-1.4 — test the governance engines and registration tools | +64 105 LOC testable | new test modules |
| **9** | P1-4.1…P1-4.6, then P1-4.7 denominator-completeness gate | 100 % of non-test Python measured, recurrence prevented | config + gate |
| **10** | P1-5.1…P1-5.4 — capability chain fields and the chain-completeness gate | N/122 chains complete, measured rather than asserted | schema + gate |
| **11** | P1-5.5…P1-5.8 — CIOA/CCE, band binding, cycle detector, RPI bootstrap | `UCIC-001` executable; import graph observed | implementation |

**Steps 1–3 are the freeze path. Steps 4–11 are the closure path.** They are independent: step 1 alone produces a green `verify.sh`, and steps 1–3 alone open the freeze gate — but neither makes the repository COMPLETE.

---

## 7. Determination

| Item | Status | Blocking closure? |
|---|---|---|
| P0-1 Authority-bearing code coverage | **REQUIRES REMEDIATION** — 88 modules / 76 336 LOC, 61 of them with zero tests | YES |
| P0-2 Test-gate connection | **REQUIRES REMEDIATION** — 3879 tests collected by nothing | YES |
| P0-3 Certification separation | **REQUIRES REMEDIATION** — 1 record, 0 `.py`, 0 executions | YES |
| P1-4 Coverage boundary expansion | **PARTIAL** — 97.59 % over 56 % of the code | NO (P0 precedes) |
| P1-5 Package chain closure | **PARTIAL** — 1 of 122 capability chains complete; 0 of 10 packages have all six links | NO (P0 precedes) |

### Determination

**VERIFICATION CLOSURE: NOT ACHIEVED — REMEDIATION PLAN ESTABLISHED, NO NEW ARCHITECTURE REQUIRED.**

Every one of the 24 actions is an edit to an existing artifact or an invocation of an existing producer. No new architecture, no new owner, no new registry, no new terminology.

The plan's own honesty condition: **P0-2.2 must precede P0-2.1.** 3828 tests have never been executed by any gate on this snapshot, so their pass rate is UNKNOWN and UNKNOWN fails closed. Wiring them into the gate before measuring them in isolation would convert an unknown into a build failure with an unbounded blast radius. Measure first, then arm the gate.

**No item is marked COMPLETE.** Not one of the ten packages has all six links, and not one of the five remediation groups is discharged.
