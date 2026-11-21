# `EPIC-PLAT-003` — REPOSITORY-ACCEPTANCE EXPECTED-FAIL DISCLOSURE

| Field | Value |
|---|---|
| SUBJECT | `./repo-ops.sh` stage `repository-acceptance` |
| MISSION | `IMPLEMENT-001C` — Approved Remediation Execution |
| BACKLOG ITEM | `RB-04` (`IMPLEMENT-001B` Deliverable 06) |
| DISCHARGES | finding `C-2` sub-item `C-2.1` (the one item surviving the `C-2` **WAIVE**) |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| OWNER OF RECORD | `EPIC-PLAT-003` |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DECLARATION

> ### `repo-ops.sh` stage `repository-acceptance` is **EXPECTED-FAIL**.
>
> This is **deliberate, correct, and must not be "fixed"** by restoring the prior behaviour.

```
./repo-ops.sh
  PASSED   environment-doctor          canonical command 'doctor' exited 0
  PASSED   canonical-verification      canonical command 'verify' exited 0
  PASSED   coverage-report             line coverage 94.28% (minimum 90.0%)
  FAILED   architecture-freeze         → see §4
  FAILED   repository-acceptance       repository acceptance rejected (readiness NOT-READY)
  VERDICT: FAIL
```

---

## 2. WHY IT FAILS — and why that is right

| Step | Fact |
|---|---|
| `engine/acceptance/contracts.py:136-143` | `CoverageProfile.REQUIRED` demands **six** dimensions: `statements`, `branches`, `functions`, `public_api`, `exception_paths`, `repository` |
| `platform/repository_operations/stages.py:99-118` | `_measured_coverage_facts()` emits **two**: `statements`, `branches` — all `coverage.py` measures |
| `stages.py:103-106` | *"Dimensions it cannot measure are **deliberately NOT synthesised**: acceptance treats a missing required dimension as incomplete, which is the correct reading — **an unmeasured dimension is unproven, never 100%**."* |
| `engine/acceptance/gates.py` | `CoverageGate.severity = BLOCKING` → 4 missing dimensions → `NOT-READY` |

**What it replaced.** At committed `HEAD` (`df763bf9`), `repo-operations.json:64-71` declared:

```json
"coverage": [
  { "name": "statements",      "covered": 1, "total": 1 },
  { "name": "branches",        "covered": 1, "total": 1 },
  { "name": "functions",       "covered": 1, "total": 1 },
  { "name": "public_api",      "covered": 1, "total": 1 },
  { "name": "exception_paths", "covered": 1, "total": 1 },
  { "name": "repository",      "covered": 1, "total": 1 }
]
```

100% across all six, **by assertion, never by measurement**. The stage could not fail no matter
what the repository actually measured.

> The prior PASS was **vacuous**. The current FAIL is **honest**. Restoring the former would
> reinstate certification by fiat — the defect registered as `RO-F-01`.

---

## 3. `repo-ops.sh` GATES NOTHING — verified exhaustively

| Authority | Bound to `repo-ops.sh`? |
|---|---|
| `verify.sh` (Stages 0–6, read in full) | **NO** — 0 references |
| `RELEASE-001` §4 — the 7 release-required gates | **ABSENT.** `grep -rn "repo-ops" 00-MASTER/RELEASE-001/` → 0 |
| `00-MASTER/UCCEP-000000/16-CONSTITUTIONAL-GATE-REGISTER.md` — `G-01`…`G-15`, all `CK-*` | **NO** — 0 references |
| `uccep.json` · `uccep-bindings.json` | **NO** — 0 matches |
| `.github/workflows/*.yml` (12 workflows) | **NO** — 2 prose comments only; none executes it |
| Actual wiring | `Makefile:91-92` convenience target · console script `ucos-repo-ops` (`pyproject.toml`) |

**Consequence:** this FAIL blocks no release, no CI job, no constitutional gate, and no
`verify.sh` stage. It is an operational signal, not a gate verdict.

---

## 4. THE `architecture-freeze` HALF — resolved by `RB-01`

At the time `C-2` was raised, `architecture-freeze` reported *"14 frozen-corpus write(s)
detected"* over `00-BOOK/SCHEMAS/` ×13 + `00-BOOK/tools/config.py`.

`IMPLEMENT-001B` established that **no located instrument freezes those two subtrees**: `X-1` is
`00-SOURCE/` + `00-SOURCE-MANIFEST/` + `99-FREEZE/`; `00-BOOK` appears in the protected-area
register only at `X-4`/`X-5`, both confined to `00-BOOK/DATA/`; `REG-AUTO-001` §2 names
`00-BOOK/tools/` *"the generator's own machinery"*; and four Control-Tower standards authorize
additive schema change.

`RB-01` corrected the **CI review boundary** accordingly. It deliberately did **not** narrow the
shared `FROZEN_PREFIXES` constant, because that constant has **21 call sites**, of which **18
are write-time guards** (evidence writers, knowledge store, publishing, realization) for which
whole-tree `00-BOOK/` breadth is correct — narrowing it would weaken 18 legitimate guards to fix
one review gate.

**Therefore `repo-ops.sh`'s `architecture-freeze` stage — which calls `find_frozen_writes`
directly against the unnarrowed constant — continues to report the same 14 paths.** This is
disclosed, not fixed: extending the exemption into the shared library is a change to a
security-relevant guard's semantics, is not in the approved backlog, and would exceed this
mission's scope. It is carried forward in §6.

---

## 5. OWNERSHIP — the pre-existing gap, recorded

| Record | Content |
|---|---|
| `00-MASTER/UAKOS-PHASE-003/03-GAP-EVIDENCE-REGISTER.md:55` | `EPIC-PLAT-003 \| repo-ops.sh \| REPOSITORY_CANONICAL_HOME \| SPECIFICATION_GAP \| code=Y, cert=N, spec=N \| HIGH` |
| `00-MASTER/UAKOS-PHASE-002/03-…-REGISTER.md:195` | canonical home is `repo-ops.sh` **itself**; `PARTIALLY_IMPLEMENTED` |
| `00-MASTER/MIP-W1-P001/10-UNIVERSAL-REGISTRY-CATALOG.md:39` | `R-27 \| Repository Operations Declaration \| repo-operations.json \| EPIC-PLAT-003 \| HEALTHY` |
| `platform/blueprints/` · `adr/` | **no `EPIC-PLAT-003` specification or ADR exists** |

`EPIC-PLAT-003` self-owns through its own code. This pre-dates the change set and is unchanged
by it.

---

## 6. NAMED OWNERS FOR CLOSURE

| # | Item | Owner | Priority |
|---|---|---|---|
| 1 | Measure `functions`, `public_api`, `exception_paths`, `repository` — **or** amend `CoverageProfile.REQUIRED` through its owning route | `engine/acceptance` owner | Wave-002, P2 (`C-2.2`) |
| 2 | Extend the DP-03 review-scope exemption to the `architecture-freeze` stage without weakening the 18 write-time guards | `engine/foundation` + `platform/repository_operations` | Wave-002, P2 (§4) |
| 3 | Author an `EPIC-PLAT-003` specification so `repo-ops.sh` ceases to self-own | `EPIC-PLAT-003` | Wave-002, P3 |

Until item 1 closes, `repo-ops.sh` returns `VERDICT: FAIL` and **that is the expected result.**
A green `repo-ops.sh` before item 1 closes would mean the vacuous declaration was restored, and
should be treated as a regression.

---

## 7. DETERMINATION

> **DISCLOSED.** `repository-acceptance` is expected-FAIL; the cause is a tooling limitation
> (4 of 6 dimensions unmeasurable), not a defect; the prior PASS was vacuous; the stage gates
> nothing; owners are named for closure.
>
> `RB-04` **DISCHARGED.** `C-2.1` closed.

---

*END — `EPIC-PLAT-003` Repository-Acceptance Disclosure · `IMPLEMENT-001C` `RB-04` · AUTHORITY = NONE*
