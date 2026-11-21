# Missing Execution Surface Report

**Programme** UCI-000001 Universal Certification Integrity
**Authority** NONE — DERIVED TRUTH. Every figure below is a measurement of tracked repository
content, produced by `engine/certification_integrity`, reproducible with `make uci`.
**Measured at** `e3fb3d5e` (before remediation) and `78b62b30` (after), branch
`integration/recovery-001`.

---

## 1. The finding that reframes every other one

The repository reported **97.9% coverage of 83,142 statements**. That figure was arithmetically
correct and answered a question about **49.4% of the executable surface**.

| | before remediation | after remediation |
|---|---|---|
| tracked non-test Python files | 1,524 | 1,334 |
| executable statements | 183,310 | 162,700 |
| statements inside the denominator | 96,070 | **134,595** |
| **denominator share of the surface** | **52.4%** | **82.7%** |
| executable files outside the denominator | 607 | **65** |
| files claimed by no governing authority | 570 | **27** |

The counts fall between the two columns because 188 test modules moved from "non-test
executable" into "test" once their roots were collected — they were previously counted as
unmeasured product code, which is itself a symptom of the same defect.

Nothing was excluded to produce the improvement. The denominator was **widened** by 38,500
statements and the reported whole-suite percentage moved *down* slightly. That direction is the
distinction the mandate's Rule 1 turns on.

---

## 2. `engines_without_a_test`

Two populations are reported because two measurements exist and neither supersedes the other.

**UEC-000001 (`engines_without_a_test` = 18)** over 49 engines, needles = module path and
basename, docstrings excluded.

**UCI-000001 (`engines_without_tests` = 25)** over 49 engines including `engine/*/gate.py`
modules, using invocation *plane types*.

The 18 UEC names, verbatim:

```
00-MASTER/ACEE-000001/acee_engine.py            00-MASTER/UCOS-MXR-001/roadmap_engine.py
00-MASTER/MCOS-000001/mcos_engine.py            00-MASTER/UCOS-RFP-001/rfp_engine.py
00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py
00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py
00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py    00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py
00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py    00-MASTER/UEI-000001/uei_engine.py
00-MASTER/UCCEP-000000/uccep_engine.py          00-MASTER/UER-000001/uer_engine.py
00-MASTER/UCDA-000001/ucda_engine.py            00-MASTER/UIS-001/uis_engine.py
00-MASTER/UCEF-000001/ucef_engine.py            00-MASTER/UMK-000001/umk_engine.py
                                                00-MASTER/UPF-000001/upf_engine.py
                                                00-MASTER/URRC-000001/urrc_engine.py
```

**Status: NOT CLOSED.** Both counters are unchanged by this work.

---

## 3. `engines_with_no_invoker`

**UEC measures 6.** Nothing in the Makefile, any workflow, `verify.sh` or `scripts/ucos-env.sh`
names these, so no plane can run them:

```
00-MASTER/UAKOS-CLOSURE-008/decision_engine.py
00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py
00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py
00-MASTER/UAKOS-PHASE-001B/provenance_engine.py
00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py
00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py
```

**Status: NOT CLOSED.**

---

## 4. `one_invocation_plane`

**UEC measures 15** (distinct invoking *texts*). **UCI measures 14** (invocation *plane types*).
UCI is the stricter question — 33 workflow files are 33 texts and one `ci` plane — and the two
are reported side by side rather than reconciled, because silently overwriting a governed ceiling
with a stricter measurement is an ungoverned adoption event.

The 14 UCI names:

```
00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py
00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py
00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py
00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py
00-MASTER/UAKOS-CLOSURE-008/decision_engine.py
00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py
00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py
00-MASTER/UAKOS-PHASE-001B/provenance_engine.py
00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py
00-MASTER/UCOS-UCAF-001/ucaf_engine.py
00-MASTER/UCOS-UFEP-001/ufep_engine.py
00-MASTER/UCOS-URAT-001/urat_engine.py
00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py
00-MASTER/UCOS-UTCE-001/utce_engine.py
```

**Status: NOT CLOSED.**

---

## 5. `declarations_no_code_consumes` and `declarations_without_certification_identity`

`declarations_no_code_consumes` = **3**, unchanged. No module loads these, so every field in them
is unenforced:

```
00-MASTER/UCOS-CEU-001/ceu-declaration.json
00-MASTER/UCOS-URR-001/urr-declaration.json
00-MASTER/UCXI-000001/ucxi-declaration.json
```

`declarations_without_a_certification_identity` = **0**. Already closed, and held through the
addition of `00-MASTER/UCI-000001/uci-declaration.json` — its owning package mints digests
(`sha256`, `def digest`), so it entered without moving the counter.

---

## 6. Unmeasured governance engines — the sharpest false green

**39 of 39** `00-MASTER/*/*_engine.py` files carry **20,359 statements** and are measured by
nothing. Each is an enforcement artifact UEC-000001 governs *by name*; several are `verify.sh`
certification stages.

A gate whose own executed fraction is unknown can rot into a no-op and keep reporting OPEN. This
is distinct from an untested engine: `unmeasured_governance_engines` (39) asks whether any
measurement covers the file at all, `engines_without_tests` (25) asks whether a test names it.
An engine can be named by a test and still have 95% of its body never execute.

**Status: NOT CLOSED.** These files are executable as scripts but are not importable as modules
(their directories are not packages and contain hyphens), so admitting them to the denominator
requires them to become importable under test — a real change, not a setting.

---

## 7. Closed by this work: 3,995 tests that ran nowhere

`service/tests`, `data/tests`, `application/tests`, `infrastructure/tests` held **188 test
modules and 3,995 tests**, named in no `testpaths`, no Makefile target, no `verify.sh` stage and
no workflow. Every one passes, in **14.7 seconds** for all four.

| layer | tests | statements | missing | coverage |
|---|---|---|---|---|
| service | 1,070 | } | } | } |
| data | 954 | } 29,970 | } 458 | } **98%** |
| application | 1,094 | } | } | } |
| infrastructure | 877 | } | } | } |
| intelligence | 126 | 5,363 | 561 | **87%** |

`intelligence` is the sharpest single case: UCOS-CL-008 admitted `intelligence/tests` to
`testpaths` and recorded that the denominator was "a separate question, answered separately
below". The separate answer was never given.

Tests that exist and never run are worse than absent tests, because absence is visible.

**Why the existing control could not see it:** `platform/tests/test_coverage_scope.py` has
`SOURCE_TREES = ("engine", "platform")` and governs the packages *under* those two. A top-level
package that is neither was not a third possibility it refused — it was a question it never
asked. Two new controls close it, both discovered from the filesystem so a sixth layer is
governed the day it appears, and both directions are enforced: a collected test root must have
its layer in the denominator, **and** a layer shipping test modules must have its root collected.

**Status: CLOSED**, with four non-vacuity proofs each forged against a layer actually in the
refused state.

---

## 8. Also closed: a namespace package worth 2,849 statements

`engine/recursive_knowledge` — 16 modules, URKE-000001, a `verify.sh` stage with a workflow, a
Makefile target and a 135-test suite — was in neither scope list nor the exclusion list, and
every scope test passed. `_packages_present()` asked whether `__init__.py` existed; since PEP 420
an implicit namespace directory imports perfectly well without one, and `verify.sh` line 713 runs
`-m engine.recursive_knowledge.gate` as a certification stage. The guard against unmeasured
packages had an unmeasured-package hole of its own shape.

Measured on admission: 2,849 statements, 381 missing, **83%** — below the floor, admitted anyway.

**Status: CLOSED.**

---

## 9. Summary

| counter | mandate target | before | after | status |
|---|---|---|---|---|
| `executable_outside_denominator` | 0 | 607 | **65** | reduced 89% |
| `ungoverned_executables` | 0 | 570 | **27** | reduced 95% |
| `unmeasured_governance_engines` | 0 | 39 | 39 | not closed |
| `engines_without_tests` (UCI) | 0 | 25 | 25 | not closed |
| `engines_without_a_test` (UEC) | 0 | 18 | 18 | not closed |
| `engines_with_no_invoker` (UEC) | 0 | 6 | 6 | not closed |
| `single_plane_engines` (UCI) | 0 | 14 | 14 | not closed |
| `one_invocation_plane` (UEC) | 0 | 15 | 15 | not closed |
| `declarations_no_code_consumes` | 0 | 3 | 3 | not closed |
| `declarations_without_identity` | 0 | 0 | **0** | closed |
| `files_with_no_execution_path` | disclosure | 6 | 10 | raised, justified |

Every remaining counter is declared as a two-sided ceiling in
`00-MASTER/UCI-000001/uci-declaration.json`, so none can grow without a build failure and none
can be repaid without the ceiling being tightened in the same commit.
