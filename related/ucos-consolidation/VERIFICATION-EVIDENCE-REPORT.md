# VERIFICATION EVIDENCE REPORT

| Field | Value |
|---|---|
| **ARTIFACT** | `VERIFICATION-EVIDENCE-REPORT.md` |
| **PHASE** | Phase 6 — Verification Execution |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** Transcript of executed commands and their exit codes. |
| **CLASSIFICATION** | `EVIDENCE` — Priority 1 under `ASSESSMENT-BOUNDARY-DETERMINATION.md` §2 |
| **SNAPSHOT** | `1f869865` + 113 uncommitted entries · branch `integration/recovery-001` |
| **ENVIRONMENT** | macOS 27.0 (26A5406e) arm64 · `.ec1-venv/bin/python` 3.12.13 · pytest 8.3.4 · pytest-cov 6.0.0 · coverage 7.15.2 · ruff 0.8.4 · jsonschema 4.26.0 |
| **COMMAND** | `./verify.sh` (canonical entry point, no arguments) |
| **WALL CLOCK** | **2668 s (44 min 28 s)** |
| **EXIT CODE** | **1 — VERIFICATION FAILED (2 stages)** |
| **TRANSCRIPT** | `/tmp/ucos-verify/verify2.log` (2611 lines), per-gate logs `/tmp/ucos-verify/g_*.log` |

---

## 1. Headline result

```
================ VERIFICATION SUMMARY ================
  PASS  ruff lint + format-check (engine + platform)                          0s
  PASS  prerequisite generation (knowledge · determinism · closure 1-3)      30s
  FAIL  pytest + coverage gate (--cov-fail-under=90)                       2620s
  PASS  coverage report                                                      4s
  PASS  governance enforce --pre                                             0s
  PASS  registry validate (schema + integrity)                               7s
  PASS  meta-constitutional conformance (CMG-INV-01..12)                     0s
  FAIL  universal object governance (UGA-INV-01..10)                         4s
  PASS  autonomous universal evolution (UAUE gate, every declared obligation) 2s
  PASS  evolution surface replay (history + 18 registers)                     1s
  TOTAL (wall clock)                                                      2668s
=====================================================
✗ VERIFICATION FAILED (2 stage(s)).
VERIFY_EXIT=1
```

**8 of 10 stages PASS. 2 FAIL. Both failures share a single root cause.**

---

## 2. Stage-by-stage evidence

### Stage 1 — ruff lint + format-check · **PASS** (0 s)
`ucos_ruff_gate` over `engine platform`. Zero findings. This is the identical gate the pre-commit hook runs, so no lint/format drift exists between the canonical path and the hook.

### Stage 1b — prerequisite generation · **PASS** (30 s)
```
generated prerequisites: knowledge · determinism-evidence · closure phases 1-3 ·
research · publication · provenance · realization
```
All 11 producers of `scripts/generate-prerequisites.sh` ran in declared order before the consuming gates. Every write landed on a `.gitignore`d path, so the stage introduced **no tracked drift** (verified in §5).

### Stage 2 — pytest + coverage gate · **FAIL** (2620 s) — exit 1

```
=========== 2 failed, 11300 passed, 3 skipped in 2586.52s (0:43:06) ============
```

| Metric | Value |
|---|---|
| Tests collected and run | **11 305** |
| Passed | **11 300** |
| **Failed** | **2** |
| Skipped | 3 |
| Duration | 2586.52 s |
| Coverage threshold | 90 % |
| **Coverage achieved** | **97.59 %** — `Required test coverage of 90% reached` |
| Coverage totals | 74 910 statements · 1315 missing · 16 542 branches · 731 partial · **98 %** |

**The coverage gate PASSED. The stage failed purely on 2 test failures.**

```
FAILED platform/tests/test_constitutional_authority_alignment.py::test_the_uga_gate_enforces_every_alignment_invariant
FAILED platform/tests/test_observation_universe.py::test_the_governance_gate_enforces_every_invariant
```

Both are **gate-binding tests**: each shells out to `uga_engine.py gate` and asserts `returncode == 0`. Their docstring states the intent — *"The invariants must run inside the gate verify.sh already invokes. A second gate for the invariants that forbid a second authority would be the joke told with a straight face, so this asserts they are in the existing one."*

Both therefore fail **for the same reason Stage 6b fails**, and are not independent defects. Assertion text captured verbatim in the transcript at lines 777–917 and 849–916.

**Coverage scope caveat (boundary §4(4)).** 97.59 % is measured over the 59 `--cov=` targets only. It is not a statement about `application/`, `service/`, `data/`, `infrastructure/`, `intelligence/`, `realization/`, `00-MASTER/**`, `00-BOOK/tools/`, `engine/constitution/` or `engine/uicm/` — 647 files / 224 647 LOC outside the denominator. And the 11 305 tests run exclude the **3879** authored tests in the non-collected roots.

### Stage 3 — coverage report · **PASS** (4 s)
`coverage report` independently resolved and reproduced `TOTAL … 98 %`, confirming the coverage tool itself is present and the measurement is not an artefact of pytest-cov alone.

### Stage 4 — `ukb.py enforce --pre` · **PASS** (0 s)
```
  eligible on-disk artifacts : 1259
  registered (in registers)  : 1233
  unregistered eligible      : 26
  unclassified (OTHER/MISC)  : 0 (GATED)
  reconciled sets declared   : 1 (CMG)
  reconciled-set drift       : 0 (GATED)
  invalid (unreadable/empty) : 0
  awaiting VCS binding       : 18 (REPORTED — not repository artifacts until `git add`)
ENFORCEMENT PASSED — no unregistered or invalid artifact can silently enter the corpus.
```
**Warning captured:** 26 unregistered eligible artifacts, 18 of them awaiting VCS binding (`CERTIFICATION-ARCHITECTURE-DETERMINATION-DRAFT.md`, `PHASE-0.7-*`, `PHASE-CERTIFICATION-*`, `PHASE-GOVERNANCE-*`, `PHASE-IDENTITY-NAMESPACE-*`, `PHASE-KNOWLEDGE-*`, `PHASE-VERDICT-*`, `POST-STABILIZATION-*`, …). Reported, not blocked.

### Stage 5 — `ukb.py validate` · **PASS** (7 s)
```
jsonschema validation: ran.
VALIDATION PASSED — 1233 artifacts, append-only page ledger intact,
referential integrity OK; 0 execution(s) — forward-only append-only lifecycle intact.
```
`jsonschema validation: ran` is the explicit refutation of the historical silent-pass defect (`ukb.py:1733-1735` swallowing `ImportError`, which once let 539 schema violations through). **`0 execution(s)`** is a measured void, carried forward to Phase 7.

### Stage 6 — meta-constitutional conformance (CMG-INV-01..12) · **PASS** (0 s)
```
  canonical source      : 00-CMG/CMG-000001-…-CONSTITUTION.md v1.2
  articles present      : 86
  mandated sections     : 80
  artifacts recognized  : 44
  concerns allocated    : 61 (50 delegated, 11 retained)
  vacancies recorded    : 1
  gaps recorded         : 9
  open questions        : 7
  findings              : 0
  readiness outcome     : READY-PROVISIONAL
```
Zero findings. **Warnings captured:** 9 gaps, 7 open questions, 1 vacancy, and a declared ceiling of `READY-PROVISIONAL` — the gate passes *and* declares that provisional is the maximum reachable state.

### Stage 6b — universal object governance · **FAIL** (4 s) — exit 1

**29 invariants evaluated: 27 PASS, 2 FAIL.**

| Invariant | Result | Measured |
|---|---|---|
| **UGA-INV-01 `EVERY_OBJECT_HAS_UNIVERSAL_ID`** | **FAIL — 8 violations** | 5844 |
| UGA-INV-02 `EVERY_OBJECT_HAS_OWNER` | PASS | 5844 |
| UGA-INV-03 `EVERY_OBJECT_REGISTERED` | PASS | 5844 |
| UGA-INV-04 `EVERY_CANONICAL_ARTIFACT_HAS_INPUT_CLOSURE` | PASS | 344 |
| UGA-INV-05 `EVERY_GENERATED_INPUT_HAS_PRODUCER` | PASS | 10 |
| UGA-INV-06 `EVERY_GENERATED_INPUT_HAS_BOOTSTRAP_PATH` | PASS | 10 |
| UGA-INV-07 `EVERY_CERTIFICATION_HAS_EVIDENCE_BOUNDARY` | PASS | 11 |
| UGA-INV-08 `NO_CANONICAL_ARTIFACT_DEPENDS_ON_UNCLASSIFIED_OBSERVATION` | PASS | 344 |
| UGA-INV-09 `NO_ARCHITECTURE_DEPENDS_ON_FINITE_INSTANCE` | PASS | 64 |
| **UGA-INV-10 `EVERY_MUTATION_HAS_AUDIT_EVENT`** | **FAIL — 8 violations** | 4611 |
| OBS-INV-01…10, 12, 13 | **PASS** (12) | up to 2466 |
| CAA-INV-01…07 | **PASS** (7) | up to 5874 |

```
  ANONYMOUS OBJECTS: 8 — run `uga_engine.py run`
GATE FAILED — 2 blocking invariant(s).
```

**The 8 anonymous objects:**
1. `engine/uckp/resolution.py`
2. `engine/uckp/uga_projection.py`
3. `engine/tests/uckp/test_category_integrity.py`
4. `engine/tests/uckp/test_category_ownership_resolution.py`
5. `engine/tests/uckp/test_uga_projection.py`
6. `platform/tests/test_commercial_cli.py`
7. `platform/tests/test_repository_intelligence_cli.py`
8. `platform/tests/test_universal_provider_cli.py`

All eight are staged-added (`A `) in the index — new files that entered version control without passing through the identity minting producer. The engine names its own remedy: `uga_engine.py run`.

### Stage 6c — autonomous universal evolution (UAUE gate) · **PASS** (2 s)
```
  UAUE gate OPEN — 10/10 obligations satisfied
  runs conducted:  52     runs certified:  52     history records: 780
```
Notable obligations satisfied: all 44 dependency edges resolve and run forward · 52 runs replay byte-identically, each settling within 3 rounds · the declared unknown subject traversed 11 positions under 33 pre-existing owner homes requiring no new registry, authority, engine or schema · all 10 mandatory invariants measured over 572 evolution objects · all 18 declared registers render through 14 renderers carrying no memory address, wall clock or absolute path · all 15 exit criteria across 15 implementation phases measured.

### Stage 6d — evolution surface replay · **PASS** (1 s)
The 19 files in `00-MASTER/UAUE-000001/` reproduce **byte-identically** from the declaration. No hand edit exists in the evolution surface.

### Stage 7 — registration + drift gate · **NOT RUN**
Opt-in (`--full`) only, because `register.sh --guard` mutates generated DATA/REGISTRIES/CONTROL-TOWER/PORTAL. Deliberately excluded to preserve the read-only boundary. **Registration drift is therefore UNMEASURED on this snapshot** — recorded as a gap, not as a pass.

---

## 3. Gates outside `verify.sh` — executed separately

These are declared validation authorities that the canonical entry point does not invoke. All were run this session.

| Gate | Command | Exit | Result |
|---|---|---|---|
| **Repository integration** | `rib_engine.py --gate` | **1** | `BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP` · units=298 · sources=8 · substrate=13/15 · matrices=6bound/16 · queued=58in5waves · **gates=10/12** · **dirty=166** · seal `7e84f1b215251893`. Failing: **GATE-04** Repository Validation (`validations_failed=1`), **GATE-12** Repository Clean (`dirty_entries_outside_generated=166`) |
| **Continuous constitutional evolution** | `uccep_engine.py --gate` | **1** | `NOT-CERTIFIED` · tier=standard · **gates=17/26** · **programmes=13/21** · blocking=**CK-BASELINE, CK-UCL, CK-UIS** · unproven=none · seal `8d9038f8f65bc4da`. Also: *"emission withheld: tier standard is narrower than the recorded tier full"* |
| **Freeze eligibility** | `ufep_engine.py --gate` | **1** | `FREEZE-ELIGIBILITY=TRUE CONSTITUTIONAL-COMPLETION=FALSE` · subjects=**5/5 eligible** · completion=**9/11** · frozen-baseline=13/13 verified · drifted=0 · **freeze-performed=NO** · gate=CLOSED · seal `e42ab8811f8a0cf5`. Blocking `UFEP-VAL-14`: **`UFEP-CC-01` unsatisfied, `UFEP-CC-02` unsatisfied** |
| **Ratification** | `urat_engine.py --gate` | 0 | `RATIFICATION-REGISTRY-BOUND` · records=5/5 · admitting-freeze=5 · coverage=16/16 · unaccounted=0 · gate=**OPEN** |
| **Traceability closure** | `utce_engine.py --gate` | 0 | `CONSTITUTIONAL-TRACEABILITY-CLOSED` · artifacts=1233 · edges=12899 · dangling=0 · unrooted=0 · orphans=0 · **lanes-with-mechanism=8/13** · **spine=0/1233** · **derivable=0** · gate=**OPEN** |
| **Authority model** | `ucaf_engine.py --gate` | 0 | `AUTHORITY-MODEL-BOUND` · authorities=34 · tiers=**8 (1 vacant)** · delegations=61 · successions=15 · resolved=17/17 · undefined=0 · tokens=21 (0 unclassified, 0 colliding) · **realizations=1/1** · **reconciliation-required=3** · gate=**OPEN** |
| **Import acyclicity** | `platform/repository_intelligence` (Tarjan SCC) | **not executed by any gate** | Not wired into `verify.sh`; `code_roots = ("engine","platform")` excludes 6 of 8 roots; output tree `.runtime/` is gitignored |

---

## 4. Failure and warning register

### 4.1 Blocking failures — 3 distinct root causes

| # | Failure | Gate(s) affected | Root cause | Remedy named by the repository |
|---|---|---|---|---|
| **F-01** | 8 tracked executable objects have no universal identity and no audit event | `verify.sh` Stage 6b (UGA-INV-01, UGA-INV-10) **and** Stage 2 (both test failures) | New files entered version control without minting | `uga_engine.py run` |
| **F-02** | 166 dirty entries outside generated paths; 1 validation failure | `rib_engine.py --gate` GATE-12, GATE-04 | Working tree carries 113 uncommitted entries incl. whole implementation packages | commit or revert; then re-gate |
| **F-03** | 3 blocking constitutional checks fail | `uccep_engine.py --gate` (CK-BASELINE, CK-UCL, CK-UIS) → transitively `ufep_engine.py` (`UFEP-CC-01/02`) | Aggregate certifier reports a failing gate; freeze completion criteria read it | resolve the three programme checks, then re-run UCCEP at tier `full` |

**F-01 is the single cause of all 3 `verify.sh` failure symptoms** (Stage 6b plus both Stage 2 test failures). It is mechanical: one producer invocation.

### 4.2 Warnings and declared voids — passing gates that report incompleteness

| # | Warning | Source | Value |
|---|---|---|---|
| W-01 | 26 unregistered eligible artifacts, 18 awaiting VCS binding | Stage 4 (PASS) | reported, not blocked |
| W-02 | `0 execution(s)` in the lifecycle ledger | Stage 5 (PASS) | the certified `execution` domain certifies an empty set |
| W-03 | 9 gaps, 7 open questions, 1 vacancy; ceiling `READY-PROVISIONAL` | Stage 6 (PASS) | terminal certification unreachable in-corpus |
| W-04 | `spine=0/1233`, `derivable=0`, `lanes-with-mechanism=8/13` | UTCE (OPEN) | traceability closed structurally, unpopulated semantically |
| W-05 | `tiers=8 (1 vacant)`, `reconciliation-required=3`, `realizations=1/1` | UCAF (OPEN) | one constitution→code binding exists in the whole repository |
| W-06 | All 5 ratification records `PROVISIONAL` | URAT (OPEN) | nothing is FINAL |
| W-07 | `matrices=6bound/16`, `substrate=13/15`, `queued=58in5waves` | RIB | 10 of 16 matrices unbound |
| W-08 | Registration drift unmeasured | Stage 7 not run | `--full` deliberately skipped |
| W-09 | Import dependency graph unmeasured | no gate | 1 known cycle (`platform ↔ intelligence`) invisible |
| W-10 | 3879 authored tests never collected | `pyproject.toml:200` | pass/fail status UNKNOWN → fails closed |

### 4.3 Missing dependencies · **NONE**

`ucos_ensure_venv` self-healed the environment with no manual activation. All five pinned dev tools resolved (`pytest`, `pytest-cov`, `coverage`, `ruff`, `jsonschema`). `dependencies = []` is honoured — no undeclared third-party import in any tracked root. Stage 1b satisfied all 10 declared generated inputs (`UGA-INV-05`/`06` PASS, `bootstrap_gaps: []`).

### 4.4 Coverage gaps

| Aspect | Measurement |
|---|---|
| Coverage **within** the denominator | **97.59 %** — exceeds the 90 % gate by 7.59 points |
| Denominator size | 74 910 statements / 16 542 branches ≈ 283 500 LOC |
| **Outside** the denominator | 647 files / **224 647 LOC** ≈ 44 % of repository Python |
| Notable exclusions | `engine/constitution/` (6888 LOC, ships the `ucos-cel` console script) · `engine/uicm/` (5343 LOC, **untracked**) · `00-MASTER/**` (57 629 LOC, 48 governance engines, 0 tests) · `00-BOOK/tools/` (6476 LOC, 0 tests) · four EC-3 bands (128 073 LOC, 3828 authored tests uncollected) |

The measured coverage is genuinely high. The *scope* of the measurement is the gap.

---

## 5. Boundary integrity of this execution

| Check | Result |
|---|---|
| Porcelain before assessment | **113** entries (61 staged / 31 unstaged / 21 untracked) |
| Porcelain after `verify.sh` + all separate gates + 6 RTC artifacts | **119** = 113 + 6 new untracked assessment documents |
| Tracked drift introduced by `verify.sh` | **0** — Stage 1b writes only to `.gitignore`d paths |
| Tracked drift introduced by separate gate runs | **73 files transiently** — `uccep --gate` cascaded into `ACEE-000001` (17), `BASELINE-001` (5), `UCL-000001` (15), `UIS-001` (10); `rib --gate` (16); `ucaf --gate` (7); `ufep/urat/utce --gate` (3+); **all restored via `git checkout --`**, leaving only `ucaf-authority.json` which was already dirty pre-session |
| Read-only gates confirmed write-free | `uga_engine.py gate`, `cmg-gate.sh`, `ukb.py enforce/validate`, `engine.uaue.gate --gate/--replay` |
| Assessment-induced modification of pre-existing state | **NONE** — every unstaged tracked file has an mtime at or before 22:06:58, prior to the 22:36 assessment start |

---

## 6. Verification determination

| Question | Answer | Evidence |
|---|---|---|
| Does `./verify.sh` pass? | **NO — exit 1, 2 of 10 stages FAIL** | summary block, §1 |
| Are there test failures? | **YES — 2 of 11 305** | both are gate-binding tests asserting UGA exit 0 |
| Is the coverage gate met? | **YES — 97.59 % vs 90 % required** | `Required test coverage of 90% reached` |
| Are there missing dependencies? | **NO** | §4.3 |
| Do all declared validation authorities pass? | **NO — 4 of 10 fail** | UGA, RIB, UCCEP, UFEP |
| Is the repository clean? | **NO — `dirty=166` outside generated paths** | RIB GATE-12 |
| Is freeze permitted by the freeze authority? | **NO — gate CLOSED, freeze-performed=NO** | UFEP `UFEP-CC-01/02` unsatisfied |
| Is any failure irrecoverable? | **NO** | F-01 is one producer invocation; F-02 is a commit decision; F-03 is 3 programme checks |

### Determination

**VERIFICATION STATUS: FAILED — RECOVERABLE.**

The engineering substrate is in strong shape: lint clean, 11 300 of 11 305 tests passing, coverage 97.59 % against a 90 % gate, registry schema and referential integrity validated, meta-constitutional conformance at zero findings, and the autonomous evolution surface both gate-open at 10/10 and byte-identically replayable.

Verification fails on **three root causes, none of them a defect in the implementation**:

1. **F-01 — 8 unminted objects.** Causes all three `verify.sh` failure symptoms. Remedy is a single declared producer invocation.
2. **F-02 — 166 dirty entries.** The repository's own integration gate says `REPOSITORY MUST STOP`. Remedy is a commit/revert decision reserved to the human authority.
3. **F-03 — 3 blocking UCCEP checks**, which transitively hold the freeze gate closed through `UFEP-CC-01/02`.

Ten warnings are recorded from *passing* gates, and they matter more than the failures for readiness: `0 executions`, `spine=0/1233`, `realizations=1/1`, all ratifications `PROVISIONAL`, ceiling `READY-PROVISIONAL`, 3879 tests uncollected, 224 647 LOC unmeasured, and the import dependency graph unobserved. A green `verify.sh` would not have changed any of them.
