# WP-002 — Architectural Cycle Elimination

| Field | Value |
|---|---|
| MISSION | `UCOS-IMP-MSN-000002` |
| PROMPT | `UCOS-PRM-IMP-000002` |
| PREDECESSOR | `UCOS-IMP-MSN-000001` / `UCOS-PRM-IMP-000001` — **COMPLETED** |
| PROGRAM / EPIC / WP | `Ω∞-001` / `EPIC-001` / `WP-002` |
| TASK | `UCOS-RIB-001-TASK-000002` |
| AUTHORITY | **NONE (DERIVED TRUTH)** — this record legislates nothing and owns no capability |
| KIND | **REFACTORING** — no redesign, no feature, no behaviour change |
| PREDECESSOR BASELINE SEAL | `71334dbbef3ed2ce0299cc645de0827ff7194790a56b6184dcf8b81b6bbe2ddf` |
| BASELINE ANCHOR | `088a853937f23f56a3dc261f00e70dcbb81e8357` on `integration/recovery-001` |
| VERDICT | **GATE-10 PASS — ZERO ARCHITECTURAL CYCLES** |

> This is a one-time work-package record, not a regenerable derivation. It authors only what
> did not already exist. Every fact that the predecessor's engine already computes is **bound
> by pointer** and is not restated here, because restating it would create the second truth
> that WP-001 exists to prevent.

---

## Output index

The mission names seven outputs. Six are already produced — and regenerated on every run —
by `rib_engine.py`. They are bound, not duplicated.

| # | Output | Mode | Location |
|---|---|---|---|
| 001 | Cycle Elimination Report | **AUTHORED HERE** | §1–§4 of this record |
| 002 | Updated Dependency Graph | **BOUND** | `00-MASTER/UCOS-RIB-001/05-DEPENDENCY-GRAPH.md` |
| 003 | Refactoring Decision Log | **AUTHORED HERE** | §2 of this record |
| 004 | Verification Report | **BOUND** | `00-MASTER/UCOS-RIB-001/11-VERIFICATION-REPORT.md` |
| 005 | Validation Report | **BOUND** | `00-MASTER/UCOS-RIB-001/12-VALIDATION-REPORT.md` |
| 006 | Certification Report | **BOUND** | `00-MASTER/UCOS-RIB-001/13-CERTIFICATION-REPORT.md` |
| 007 | Git Cleanliness Report | **BOUND** | `00-MASTER/UCOS-RIB-001/01-REPOSITORY-INVENTORY.md` § repository reality |

Regeneration route: `make rib`. Standing gate: `make rib-gate` / `.github/workflows/rib-gate.yml`.

---

## 1. The cycles, as reported by the predecessor (STEP-002 / STEP-003)

Loaded from `rib.json` plane `PLN-CODE`. Nothing was rediscovered.

| Cycle | Participants | Import chain | Runtime dep. | Compile-time dep. | Constitutional owner | Risk |
|---|---|---|---|---|---|---|
| `CYC-1` | `engine.runtime` ↔ `engine.acceptance` | `engine/runtime/bridge/bridge.py` → `engine.acceptance.{engine,evidence,contracts}` · `engine/acceptance/{engine,readiness}.py` → `engine.runtime.disclosure` | YES both directions | YES both directions | `engine/` (EPIC-005 runtime · EPIC-VAL-002 acceptance) | **HIGH** — layering violation across two certified capabilities |
| `CYC-2` | `engine.certification` ↔ `engine.runtime` | `engine/runtime/bridge/bridge.py` → `engine.certification.{contracts,engine,evidence}` · `engine/certification/{closure,engine}.py` → `engine.runtime.disclosure` | YES both directions | YES both directions | `engine/` (EPIC-005 · EPIC-008) | **HIGH** |
| `CYC-3` | `engine.runtime` ↔ `engine.validation` | `engine/runtime/bridge/bridge.py` → `engine.validation.{evidence,executor}` · `engine/validation/checks.py` → `engine.runtime.disclosure` | YES both directions | YES both directions | `engine/` (EPIC-005 · EPIC-007) | **HIGH** |

**Direction analysis.** All three cycles share one shape and one cause. The downward edge is
legitimate: `engine/runtime/bridge/bridge.py` orchestrates validation, certification and
acceptance, so the runtime depending on those three is correct layering. The upward edge is
the defect: all five back-edges resolve to a **single module**, `engine/runtime/disclosure.py`,
and to only the pure part of it — `build_disclosure` (four sites) and `disclosure_present`
(one site).

**Not a runtime cycle.** The module plane `PLN-MODULE` reported **zero** non-benign cycles
before the change: no Python import actually fails. The defect is architectural — a
foundation-layer contract homed in a runtime package — which is why the predecessor
classified it `CYC-ARCHITECTURAL` rather than counting it as a broken import.

**Scale of the mis-homing.** `engine.runtime.disclosure` is imported at ~110 sites across
`engine`, `platform`, `service`, `data`, `infrastructure` and `application`. A contract with
that reach is not a runtime mechanism.

---

## 2. Refactoring decision log (STEP-004)

The ladder was walked in order. The first rung that resolves the cycle is the one taken.

| Rung | Option | Determination |
|---|---|---|
| 1 | **Reuse** | **TAKEN.** `engine.foundation` already exists and is already a **leaf** — it imports nothing outside itself — and all four participants already depend on it (`engine.acceptance`, `engine.certification`, `engine.validation` and `engine.runtime` each import `engine.foundation.obs.*`). It already owns a `contracts/` subpackage. The lower layer both sides depend on therefore did not need to be created; it needed to be used. |
| 2 | **Extract interface** | **PARTIALLY TAKEN**, as the mechanism of rung 1: the pure contract — four constants, `build_disclosure`, `disclosure_present` — was extracted into `engine/foundation/contracts/disclosure.py`. This is exactly the remediation the predecessor's own compliance register named for `CMP-ACYCLIC`. |
| 3 | Dependency inversion | **NOT NEEDED.** No protocol, ABC or registration point is required once the contract sits below both sides. |
| 4 | Event | **NOT NEEDED.** The disclosure is synchronous pure data; an event would add a runtime mechanism to remove a compile-time edge. |
| 5 | Contract | **SUBSUMED** by rung 2 — the extracted unit *is* the contract. |
| 6 | Injection | **NOT NEEDED.** No caller signature changes. |
| 7 | Split runtime | **NOT NEEDED.** No runtime is split; `engine.runtime` keeps every runtime behaviour it had. |
| 8 | Last-resort refactor | **NOT REACHED.** |

### What deliberately did NOT move, and why

| Symbol | Stays in `engine.runtime.disclosure` | Reason |
|---|---|---|
| `inject_provisional_state` | yes | Its parameter is a `RuntimeUnit`. Its subject matter is the runtime. |
| `require_disclosure` | yes | It raises `engine.runtime.errors.DisclosureError`, whose MRO is `DisclosureError → RuntimeAssemblyError → FoundationError → Exception`. Moving the error would change that MRO and therefore change which `except` clauses catch it — a behaviour change this mission forbids. Its only callers, `engine/runtime/deploy.py` and one runtime test, are inside `engine.runtime`. |

### Duplication invariants held

| Invariant | Evidence |
|---|---|
| No duplicated code | The constants and the two functions exist **once**, in `engine.foundation.contracts.disclosure`. `engine.runtime.disclosure` imports them; it does not restate them. Verified by object identity: `engine.runtime.disclosure.build_disclosure is engine.foundation.contracts.disclosure.build_disclosure` → `True`, and likewise for all six symbols. |
| No duplicated contracts | One definition of `DISCLOSURE_ID` / `STANDARD` / `GATE` / `STATEMENT`. |
| No duplicated runtime | Nothing was split, forked or re-entered. |
| No duplicated interfaces | `engine/foundation/contracts/__init__.py` was **not** extended: adding the disclosure symbols there would have created a second public import path for one contract. The module path is the single route. |
| No temporary adapters | None introduced. The re-export in `engine.runtime.disclosure` is not an adapter — it is the module's own unchanged public surface, preserved so that ~110 existing call sites remain valid without being touched. |

### Scope restraint

Only the **five** import sites that close a cycle were rewired. The remaining
`engine.runtime.disclosure` consumers — in `engine.governance`, `engine.factory`,
`engine.universal_certification`, and across `platform`, `service`, `data`,
`infrastructure`, `application` — were left untouched: none of them closes a cycle
(`engine.runtime` imports nothing from those packages), so changing them would be scope
creep in a refactoring mission, and their imports remain correct because the module's
surface is unchanged.

---

## 3. The change (STEP-005)

| File | Change |
|---|---|
| `engine/foundation/contracts/disclosure.py` | **new** — the canonical EC-1 disclosure contract: `DISCLOSURE_ID`, `DISCLOSURE_STANDARD`, `DISCLOSURE_GATE`, `DISCLOSURE_STATEMENT`, `build_disclosure`, `disclosure_present`. |
| `engine/runtime/disclosure.py` | re-exports the contract unchanged; retains `inject_provisional_state` and `require_disclosure`; `__all__` byte-identical to before. |
| `engine/acceptance/engine.py` | import source only → `engine.foundation.contracts.disclosure` |
| `engine/acceptance/readiness.py` | import source only |
| `engine/certification/engine.py` | import source only |
| `engine/certification/closure.py` | import source only |
| `engine/validation/checks.py` | import source only |

Six existing files changed by exactly one import line each (plus the relocation of the
contract body). No signature, no return value, no control flow, no error type altered.

---

## 4. Cycle elimination result (STEP-006)

Recomputed by the predecessor's own engine — `make rib` — not by any new tool.

| Plane | Nodes | Edges before → after | Cycles before → after | Non-benign before → after |
|---|---|---|---|---|
| `PLN-CODE` (package import) | 60 | 228 → **225** | 3 → **0** | 3 → **0** |
| `PLN-MODULE` (module import) | 1 560 | 7 566 → 7 567 | 2 → 2 | 0 → **0** |
| `PLN-CORPUS` (typed graph) | 311 | 4 774 → 4 774 | 0 → 0 | 0 → **0** |

Exactly three edges disappeared, and they are exactly the three cycle-closing edges:

| Unit | Dependencies before → after | Edge removed |
|---|---|---|
| `engine.acceptance` | 8 → 7 | `engine.acceptance → engine.runtime` |
| `engine.certification` | 10 → 9 | `engine.certification → engine.runtime` |
| `engine.validation` | 8 → 7 | `engine.validation → engine.runtime` |

The two remaining `PLN-MODULE` cycles are `CYC-INIT-REEXPORT` — package-initializer
re-export, declared benign by the predecessor's own cycle-class declaration and unchanged by
this mission.

---

## 5. Regression verification (STEP-007)

| Check | Result |
|---|---|
| Canonical suite `make test` (declared testpaths: `engine/tests`, `platform/tests`) | **4 751 passed** |
| Coverage gate (floor 90 %) | **93.45 % — PASS** |
| The five roots outside the declared testpaths (`service`, `data`, `infrastructure`, `application`, `intelligence` tests) — run because they consume the relocated contract | **4 117 passed** |
| Total | **8 868 tests pass, 0 failures** |
| `ruff check engine platform` | **All checks passed** |
| `ruff format --check engine platform` | **1 012 files already formatted** |

### Behaviour identity, proven rather than asserted

| Property | Evidence |
|---|---|
| Disclosure payload unchanged | The committed pre-refactor module was loaded in isolation from `git show HEAD:engine/runtime/disclosure.py` and its `build_disclosure()` output hashed: `4461123a11fb99c5bcbdf9603d5aaae9b8b76df36a88f6964cb563e8aaabb3c8`. The post-refactor output hashes **identically**. |
| Constants unchanged | All four compare equal to the pre-refactor values. |
| Single definition | All six relocated symbols satisfy `runtime_symbol is foundation_symbol`. |
| Public surface unchanged | `engine.runtime.disclosure.__all__` equals the pre-refactor list, and every name resolves. `engine.runtime` package-level re-exports all still resolve. |
| Error contract unchanged | `require_disclosure(None)` still raises `DisclosureError`, code `RT-DISC-001`, MRO `DisclosureError → RuntimeAssemblyError → FoundationError → Exception`, still homed in `engine.runtime.errors`. |
| Determinism preserved | Repeated calls and both import paths return equal payloads. |

---

## 6. Repository validation (STEP-008)

Measured by diffing the predecessor's model against its baseline at `HEAD`.

| Obligation | Measured | Verdict |
|---|---|---|
| No capability ownership changes | 236 units before and after; 0 added, 0 removed; **0** changes to `owner`, `program`, `unit_class`, `rie_id` | **PASS** |
| No disposition changes | distribution identical: REUSE 196, EXTEND 21, CONFIGURE 12, DEPRECATE 5, IMPLEMENT 2 | **PASS** |
| No registry corruption | `ukb.py validate`: 1 204 artifacts, append-only page ledger intact, referential integrity OK; `registration_drift` 0 → 0; `00-BOOK/` untouched (Python modules are non-artifacts under `INCLUDE_EXTENSIONS`) | **PASS** |
| No runtime regression | `engine.runtime` retains every behaviour and its full public surface; 8 868 tests pass | **PASS** |
| No API regression | `__all__` and package re-exports byte-identical; ~110 untouched call sites still resolve | **PASS** |
| No contract regression | disclosure payload hash identical; error type and MRO identical | **PASS** |
| No new duplication | `duplicate_findings` 0 → 0 | **PASS** |
| No dependency-closure loss | `unresolved_dependency_edges` 0 → 0 | **PASS** |
| No unintended metric drift | `orphan_units` 9 → 9 · `uncatalogued_units` 23 → 23 · `gap_findings` 669 → 669 · `closure_gaps` 0 → 0 · `certification_domains_failed` 0 → 0 · `matrices_unbound` 0 → 0 | **PASS** |

---

## 7. Certification (STEP-009)

| Gate | Before | After |
|---|---|---|
| **`GATE-10` Zero Circular Dependency** | **FAIL** — `architectural_cycles=3` | **PASS** — `architectural_cycles=0` |
| `VER-08` No circular dependency | FAIL | **PASS** |

**GATE-10 PASS.** The mission gate is satisfied: zero architectural cycles in every measured
plane, behaviour unchanged, verification and validation clear, repository clean.

### Gates still failing, and why they are not this mission's

`rib-gate` remains CLOSED overall. The residue is untouched by WP-002 and out of its scope:

| Gate | Finding | Owner |
|---|---|---|
| `GATE-03` | `VER-09` (orphans) and `VER-11` (dead engines) still fail; `VER-08` now passes | WP-003+ |
| `GATE-07` | 23 implementation units absent from the capability catalogue | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` |
| `GATE-11` | 9 orphan units | respective owners |

### Standing guard against regression

No new test was added, because a stronger guard already exists and is already wired:
`GATE-10` is evaluated by `rib_engine.py --gate`, which runs on every push and pull request
via `.github/workflows/rib-gate.yml`. Any reintroduction of an upward edge from acceptance,
certification or validation into `engine.runtime` closes the gate and fails CI.

---

## 8. Git cleanliness report

| Stage | State |
|---|---|
| Before work | **CLEAN** — 0 entries at `088a853937f23f56a3dc261f00e70dcbb81e8357` |
| Changes made | 1 new module, 1 relocated module body, 5 single-line import rewires, this record, and the predecessor's regenerated artifacts |
| Unrelated modifications | **none** — no corpus file, no registry, no constitutional instrument, no other programme's operational memory was written |
| Temporary files | **none** — the isolated pre-refactor comparison module was created under `/tmp` and removed |
| After work | **CLEAN** |

### One unrelated modification was produced, and reverted

Running the `intelligence/tests` suite (STEP-007, because those tests consume the relocated
contract) regenerated ten `intelligence/UCOS-RIE-*.json` operational outputs as a side effect.
The diff was **not** caused by this refactor — it reported `engine` at 52 589 LOC against a
committed 39 555, and `platform` at 87 400 against 61 944, figures no six-line import change
can move. The committed RIE outputs are simply **stale by a wide margin**.

Those files were reverted with `git checkout -- intelligence/` and are **not** part of this
commit, because they are not mission-owned. The predecessor's model was then regenerated
against committed truth and produced the identical seal `64a4e4cf88607f22`, confirming the
staleness had no bearing on any verdict recorded above.

**Finding for a later work package.** `intelligence/UCOS-RIE-*` — the canonical capability
catalogue, dependency graph, execution frontier and health record — are materially stale
against the repository they describe. This is the same owner that `GATE-07` already names
(23 uncatalogued units), so the two findings share one remediation: regenerate and commit the
RIE outputs through their owner. That act is outside WP-002's scope and requires the owner's
authorization.

---

*This record is DERIVED TRUTH. It creates no authority, ratifies nothing, freezes nothing and
supersedes no governing instrument. It restates none of the six outputs the predecessor's
engine regenerates; those are bound by pointer above. Where this record conflicts with a
higher frozen or governing instrument, the higher instrument governs.*
