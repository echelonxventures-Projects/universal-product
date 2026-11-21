# IMPLEMENT-001B · DELIVERABLE 01 — C-2 EVIDENCE & DISPOSITION

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| FINDING | **C-2** — *"`repo-ops.sh` is now permanently red"* (`IMPLEMENT-001A` D00 §5.2), classified **BLOCKING** |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### C-2's **mechanism is VALID**. Its **"BLOCKING" classification is DISPROVED**.
> ### Its framing as a **defect** is **INVERTED** — the change set replaced two gates that
> ### could not fail with one that fails honestly.

---

## 2. PHASE 1 — EVIDENCE RECONSTRUCTION

### 2.1 The failure is real and deterministic — reproduced

```
./repo-ops.sh
  PASSED   environment-doctor            canonical command 'doctor' exited 0
  PASSED   canonical-verification        canonical command 'verify' exited 0
  PASSED   coverage-report               line coverage 94.28% (minimum 90.0%)
  FAILED   architecture-freeze           14 frozen-corpus write(s) detected
  FAILED   repository-acceptance         repository acceptance rejected (readiness NOT-READY)
  VERDICT: FAIL
```

Engine log: `{"acceptance_id": "UCOS-ACCEPT-EPIC-PLAT-003-19400ab42980a486",
"blocking_failed": 1, "status": "rejected"}` · `{"gates_passed": 19, "gates_total": 20,
"verdict": "NOT-READY"}`.

### 2.2 The causal chain — verified line by line

| Step | Location | Fact |
|---|---|---|
| 1 | `repo-operations.json:29` | `"coverage_from_measurement": true` |
| 2 | `repo-operations.json` facts | `"coverage": []` |
| 3 | `stages.py:131-139` | when the flag is set, `facts["coverage"] = _measured_coverage_facts(...)`; measurement **replaces** declaration; absence of a measured report raises `StageExecutionError` (fail-closed) |
| 4 | `stages.py:99-118` | `_measured_coverage_facts` emits exactly **2** dimensions: `statements`, `branches` |
| 5 | `engine/acceptance/contracts.py:136-143` | `CoverageProfile.REQUIRED` = **6**: `statements, branches, functions, public_api, exception_paths, repository` |
| 6 | `contracts.py:148-157` | `missing_dimensions()` → 4 missing → `complete` = `False` |
| 7 | `engine/acceptance/gates.py` | `CoverageGate.severity = GateSeverity.BLOCKING` |

**Reproduced. The stage cannot pass while only 2 of 6 dimensions are measurable.** C-2's
mechanism is correct in every particular.

### 2.3 ⛔ The decisive evidence C-2 did not examine — the state at HEAD

```
git show HEAD:repo-operations.json
  :21-23   "stage_id": "architecture-freeze", "kind": "freeze",
           "params": { "paths": [] }                    ← guard over an EMPTY subject
  :64-71   "coverage": [
             { "name": "statements",       "covered": 1, "total": 1 },
             { "name": "branches",         "covered": 1, "total": 1 },
             { "name": "functions",        "covered": 1, "total": 1 },
             { "name": "public_api",       "covered": 1, "total": 1 },
             { "name": "exception_paths",  "covered": 1, "total": 1 },
             { "name": "repository",       "covered": 1, "total": 1 }
           ]                                            ← 100% BY FIAT
```

At HEAD:
- `architecture-freeze` called `find_frozen_writes([])` — which returns `[]` for an empty
  input. **A guard that examined nothing and therefore always passed.**
- `repository-acceptance` declared its own coverage as 6/6 complete with `covered=1, total=1`
  per dimension. **`CoverageProfile.complete` was `True` by assertion, never by measurement.**

> **Both failing stages were, at HEAD, guaranteed passes over nothing.**
>
> The change set (`stages.py:99-118, 121-168, 210-283`) replaced them with a real measurement
> and a real git-derived subject. The stated intent is in the code:
>
> *"Dimensions it cannot measure are deliberately NOT synthesised: acceptance treats a missing
> required dimension as incomplete, which is the correct reading — **an unmeasured dimension is
> unproven, never 100%**."* (`stages.py:103-106`)
>
> *"the acceptance subject used to declare its own coverage as covered=1/total=1 across all six
> required dimensions — 100% by fiat, not by measurement — **so this stage could not fail no
> matter what the repository actually measured**."* (`stages.py:124-131`)

`IMPLEMENT-001A` recorded this change as a defect creating a "permanently red" gate. The
measured truth is the opposite: **a false green was replaced by an honest red.**

---

## 3. PHASE 2 — CONSTITUTIONAL REVIEW

### 3.1 ⛔ `repo-ops.sh` is **not a gate**. C-2's blocking classification has no basis.

Exhaustive search for any binding of `repo-ops.sh` / `platform.repository_operations` /
`repo-operations.json` to a gate:

| Authority | Result |
|---|---|
| `verify.sh` (121 lines, read in full — Stages 0–6) | **0 references** |
| `RELEASE-001` §4 — the 7 release-required gates | **ABSENT.** The list is: lint+format · tests+coverage · coverage report · governance enforce · registry validate · `make uccep-gate` · `make closure-gate`. `grep -rn "repo-ops" 00-MASTER/RELEASE-001/` → **0** |
| `00-MASTER/UCCEP-000000/16-CONSTITUTIONAL-GATE-REGISTER.md` — `G-01`…`G-15` + all `CK-*` | **0 references** |
| `uccep.json` + `uccep-bindings.json` | **0 matches** for `repo-ops\|repository_operations\|repository-operations` |
| `.github/workflows/*.yml` (12 workflows) | **2 prose comments only** — `uccep-gate.yml:91` (mentions it shares `scripts/ucos-env.sh`), `uei-gate.yml:15` (lists it as a consumed capability). **No workflow executes it.** |
| Only actual wiring | `Makefile:91-92` (`repo-ops: @./repo-ops.sh`, a convenience target) and console script `ucos-repo-ops` (`pyproject.toml:52`) |

> `./repo-ops.sh` is a **standalone operational convenience entry point**. It gates no release,
> no CI job, no constitutional gate, and no `verify.sh` stage. Its failure blocks nothing.
>
> **C-2's classification as a BLOCKING certification finding is unsupported by any authority.**

### 3.2 Ownership — a genuine, pre-existing gap

| Record | Content |
|---|---|
| `00-MASTER/UAKOS-PHASE-003/03-GAP-EVIDENCE-REGISTER.md:55` | `EPIC-PLAT-003 \| repo-ops.sh \| REPOSITORY_CANONICAL_HOME \| SPECIFICATION_GAP \| code=Y,cert=N,spec=N \| HIGH \| BLOCKING \| HIGH` |
| `00-MASTER/UAKOS-PHASE-002/03-…-REGISTER.md:195` | canonical home is `repo-ops.sh` **itself**; `PARTIALLY_IMPLEMENTED` |
| `00-MASTER/MIP-W1-P001/10-UNIVERSAL-REGISTRY-CATALOG.md:39` | `R-27 \| Repository Operations Declaration \| repo-operations.json \| EPIC-PLAT-003 \| HEALTHY` |
| `platform/blueprints/` · `adr/` | **No EPIC-PLAT-003 specification or ADR exists** |

`EPIC-PLAT-003` is registered as a `SPECIFICATION_GAP` with `code=Y, cert=N, spec=N`. It
**self-owns through its own code**. This pre-dates the change set and is already recorded.

### 3.3 Disclosure — confirmed absent

`grep -rn "coverage_from_measurement"` → only `repo-operations.json:29`, `stages.py`, and
`platform/tests/test_repository_operations_stages.py`. No ADR, determination, or register
discloses the expected-fail state. The sole in-repository statement of intent is the code
comment at `stages.py:100-106, 124-131`.

**C-2's disclosure sub-claim is VALID.**

---

## 4. PHASE 3 — CLASSIFICATION

> ## **INTENTIONAL BEHAVIOUR** (correctly implemented) + **TOOLING LIMITATION** (4 dimensions unmeasurable) + **INCOMPLETE IMPLEMENTATION** (no disclosure, no owner)

Explicitly **not**: a constitutional defect (no authority binds `repo-ops.sh`), an
implementation defect (the code does exactly what its docstring declares and its tests assert),
or a regression (the prior green was vacuous).

The 4 unmeasurable dimensions are a **tooling limitation**, not a defect:
`coverage.py` measures statements and branches. `functions`, `public_api`, `exception_paths`
and `repository` are not produced by any tool in the repository. Synthesising them was the
defect that was removed.

---

## 5. PHASE 4 — DISPOSITION

> # **WAIVE** — with a mandatory disclosure record
> ### (mechanism ACCEPTED · BLOCKING classification REJECTED · downgraded to ADVISORY)

| Dimension | Determination |
|---|---|
| **Evidence** | `repo-ops.sh` VERDICT: FAIL reproduced live · `contracts.py:136-143` (6 required) vs `stages.py:99-118` (2 emitted) · `git show HEAD:repo-operations.json:23` `"paths": []` and `:64-71` six × `covered:1,total:1` · 0 bindings in `verify.sh`, `RELEASE-001` §4, `G-01…G-15`, `uccep.json`, any workflow |
| **Constitutional justification** | No located instrument binds `repo-ops.sh` to certification. `RELEASE-001` §4 enumerates the 7 required gates exhaustively and omits it. The observed FAIL is the correct output of a gate that was made honest: `CEP-008`-style evidence discipline treats an unmeasured dimension as unproven, and the change set implements exactly that. **Waiving is the only disposition consistent with the evidence** — the behaviour is right, the classification was wrong, and no fix to the code is warranted. |
| **Implementation impact** | **NONE. No code change.** Reverting would restore a gate that cannot fail — a regression. `_measured_coverage_facts`, `_run_acceptance` and `_run_freeze` stay exactly as written. |
| **Repository impact** | One disclosure record required: that `repository-acceptance` is **expected-FAIL** until 4 dimensions become measurable, with the owner named. Recorded in Deliverable 06 as `RB-04`. |
| **Dependency impact** | None. `repo-ops.sh` has no downstream consumer. Its `architecture-freeze` half is unblocked by **C-1c**. |
| **Certification impact** | **NONE — this is the decisive correction.** C-2 was one of four findings on which `IMPLEMENT-001A` withheld certification. It is **not a certification blocker**. Removing it changes the certification arithmetic. |

### 5.1 Two residual sub-items (both non-blocking, both deferred)

| # | Item | Disposition | Owner |
|---|---|---|---|
| **C-2.1** | Record the expected-FAIL disclosure for `repository-acceptance` | **FIX** (record only, no code) | `EPIC-PLAT-003` |
| **C-2.2** | Measure the 4 remaining coverage dimensions, or amend `CoverageProfile.REQUIRED` through the owning route | **DEFER** to Wave-002 | `engine/acceptance` owner |

`C-2.2` is a genuine enhancement, not a defect: the acceptance contract asks for six dimensions
the repository's tooling cannot currently produce. Either the tooling grows or the contract is
amended — both are governed acts, neither is urgent, and the current fail-closed posture is the
safe one meanwhile.

---

## 6. SUMMARY

| Claim in `IMPLEMENT-001A` C-2 | Verdict |
|---|---|
| `repo-ops.sh` fails; `architecture-freeze` + `repository-acceptance` FAILED | ✓ **REPRODUCED** |
| `repository-acceptance` is structurally unsatisfiable (2 of 6 dimensions) | ✓ **REPRODUCED** |
| No disclosure or owner exists | ✓ **CONFIRMED** |
| **BLOCKING** — a certification blocker | ⛔ **DISPROVED** — bound to no gate in `verify.sh`, `RELEASE-001` §4, `G-01…G-15`, `uccep.json`, or any workflow |
| *"A permanently-red gate … is not a stabilized state"* | ⛔ **INVERTED** — at HEAD both stages were guaranteed passes over nothing (`paths: []`; coverage 6 × `covered:1/total:1`). The change set removed two false greens. |
| Requires a fix | ⛔ **NO** — the code is correct as written; only a disclosure record is owed |

> **What survives C-2:** one disclosure record and one deferred enhancement. **Zero lines of
> code.** C-2 is removed from the blocking set.

---

*END — `IMPLEMENT-001B` Deliverable 01 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
