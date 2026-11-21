# UICM — Resolution Gap Register

> **Artifact:** `UICM-RESOLUTION-GAP-REGISTER`
> **Programme:** UCOS-UICM-000001 — Phase 2 (discovery)
> **AUTHORITY = NONE — DERIVED TRUTH.** This register defines no gap and closes no gap.
> `04-CLOSURE-GAP-REGISTER.json` remains the sole definition of what a gap is.
> **Disposition:** DISCOVERY ONLY. This is a *markdown projection of a resolution
> requirement*, not a registry. It has no identity, no chain and no state.
> **Gap population:** 158 gaps · 158 blocking · 0 non-blocking

---

## 1. What this document is, and what it deliberately is not

It records, per gap, **what would have to be true for the probe to read CLOSED**. It is
not a remediation registry: it mints no identifier, holds no state, and tracks no
progress. Creating a register that tracked resolution progress was considered and
**refused** — see `UICM-RESOLUTION-CAPABILITY-MATRIX.md` §4, which finds that
`engine/uicm/observation.py` already owns append-only resolution history and that the
only genuine absence is *cross-run continuity* within it.

## 2. The observation transition every resolution produces

Resolution is not an edit. It is a later observation of the same coordinate, and the
declared algebra already permits it — no state machine change is required:

```
  revision r    OPEN        <- current reading, carries the gap
       |          (probe re-runs against changed repository state)
       v
  revision r+1  CLOSED      <- appended; supersedes revision r
                            <- revision r becomes SUPERSEDED by derivation, never by edit
       |          (verdict from engine/universal_certification only)
       v
  revision r+2  CERTIFIED   <- reachable only from CLOSED
```

`OPEN -> CLOSED` and `CLOSED -> CERTIFIED` are both declared transitions
(`uicm.json` `closure_states`). `SUPERSEDED` is terminal and is *derived* by the
registry — "an observation cannot carry 'I was superseded', because writing that would
be the in-place mutation the design forbids". Consequently:

- no gap is ever deleted; the OPEN observation stays readable forever;
- no closure is manual — a coordinate closes only because a probe re-measured it;
- no `CLOSED` exists without evidence (`requires_evidence: true` on every state above `DISCOVERED`);
- no `CERTIFIED` exists without a decision from the located certifier.

## 3. Resolution specification per dimension

Nine dimensions carry gaps. Each specification below is a *requirement statement*, not
an instruction to act; execution requires the explicit approval reserved in
`UICM-PHASE-2-DETERMINATION.md`.

### Priority 1 · `identity` — Identity Closure

| Field | Value |
|---|---|
| Gaps | 1 |
| Gap class(es) | REGISTRY-DRIFT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 4 of 17 |
| UCIC-001 stage(s) | 13 |
| Declared `discharging_owner` | `SRC-ARTIFACT-IDENTITY` |
| Resolution owner | UCOS-UGA-001 |
| Instrument that must change | `00-MASTER/UCOS-UGA-001/uga_engine.py run` |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** Re-run the UGA identity minter so the two tracked artifacts are admitted as `EXECUTABLE_OBJECT`, owner `engine/uckp` (ownership rule 3), `id_category ENGINE`, minted from `00-BOOK/DATA/id-ledger.json` `by_object`. UICM mints nothing; it re-reads the register.

**Evidence required to prove closure.** `universal_id` present for `engine/uckp/resolution.py` and `engine/uckp/uga_projection.py` in `01-EXECUTABLE-OBJECT-REGISTRY.json`. Probe emits `identified:<n>` + `identity_sample:<UCOS-ENGINE-NNNNNN>`.

**Validation required.** `verify.sh` stage 6b — `uga_engine.py gate`, UGA-INV-01/02/03 (all blocking). Then UICM re-measure: `probe_identity` returns CLOSED.

**Verification required.** Byte replay of the UICM record set; observation chain intact; UGA registry `count` increases by exactly 2 and no existing row changes.

**Expected observation transition.** `OPEN` -> `CLOSED` for 1 coordinate(s);
1 new observation(s) appended, 1 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
1; no gap record is edited or removed.

### Priority 2 · `registry` — Registry Closure

| Field | Value |
|---|---|
| Gaps | 3 |
| Gap class(es) | REGISTRY-DRIFT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 5 of 17 |
| UCIC-001 stage(s) | 13 |
| Declared `discharging_owner` | `SRC-REGISTRATION` |
| Resolution owner | UCOS-REPOSITORY-ROOT |
| Instrument that must change | `pyproject.toml` |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** Admit `engine`, `engine.constitution` and `platform` to the branch-coverage denominator: add the location to `[tool.coverage.run] source` and a `--cov=<name>` entry to `[tool.pytest.ini_options] addopts`. **High blast radius** — `engine` and `platform` are namespace roots, so admitting them enlarges the denominator over every subpackage and interacts with `--cov-fail-under=90`.

**Evidence required to prove closure.** Probe emits `capability_register:<UCKO-CAP-…>`, `coverage_source:<location>`, `coverage_addopts:<name>`.

**Validation required.** `verify.sh` stage 2 (`pytest --cov-fail-under=90`) and stage 3 (`coverage report`) must still pass at the enlarged denominator. Then UICM re-measure: `probe_registry` returns CLOSED.

**Verification required.** Byte replay; `source_digests.registration` changes and is recorded as the reason the matrix digest moved.

**Expected observation transition.** `OPEN` -> `CLOSED` for 3 coordinate(s);
3 new observation(s) appended, 3 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
3; no gap record is edited or removed.

### Priority 3 · `governance` — Governance Closure

| Field | Value |
|---|---|
| Gaps | 1 |
| Gap class(es) | REGISTRY-DRIFT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 14 of 17 |
| UCIC-001 stage(s) | 3, 13 |
| Declared `discharging_owner` | `SRC-ARTIFACT-IDENTITY` |
| Resolution owner | UCOS-UGA-001 |
| Instrument that must change | `00-MASTER/UCOS-UGA-001/uga_engine.py run` |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** **No independent action.** `probe_governance` returns OPEN solely because `capability.unidentified_artifacts` is non-empty. The identity resolution closes this dimension as a side effect, at which point the probe reads `certification_status` and `validation_contract` for all artifacts.

**Evidence required to prove closure.** `certification_status` (`GOVERNED`) and `validation_contract` (`UCOS-UGA-001 §UGA-INV-01..10`) present for every identified artifact. Probe emits `governance_status:…` + `validation_contract:…`.

**Validation required.** Same stage 6b gate as identity. Then UICM re-measure: `probe_governance` returns CLOSED.

**Verification required.** Byte replay. Closing identity without closing governance would indicate a probe defect and must be investigated rather than worked around.

**Expected observation transition.** `OPEN` -> `CLOSED` for 1 coordinate(s);
1 new observation(s) appended, 1 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
1; no gap record is edited or removed.

### Priority 4 · `contract` — Contract Closure

| Field | Value |
|---|---|
| Gaps | 4 |
| Gap class(es) | UNSATISFIED-REQUIREMENT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 8 of 17 |
| UCIC-001 stage(s) | 4, 5 |
| Declared `discharging_owner` | `SRC-CAPABILITY-IDENTITY` |
| Resolution owner | the capability's own package (UGA path owner) |
| Instrument that must change | `<location>/__init__.py` |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** Publish an explicit `__all__` interface surface from the package root. `_publishes_interface` accepts either an `ast.Assign` or an `ast.AnnAssign` binding the name `__all__` at module level. Two of the four are namespace roots (`engine`, `platform`), where the surface must be a deliberate architectural decision rather than a mechanical re-export.

**Evidence required to prove closure.** Probe emits `interface_surface:<location>` + `module_count:<n>`.

**Validation required.** `verify.sh` stage 1 (ruff, which enforces `__all__` correctness) and stage 2. Then UICM re-measure: `probe_contract` returns CLOSED.

**Verification required.** Byte replay; `source_digests.boundary` changes.

**Expected observation transition.** `OPEN` -> `CLOSED` for 4 coordinate(s);
4 new observation(s) appended, 4 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
4; no gap record is edited or removed.

### Priority 5 · `coverage` — Coverage Closure

| Field | Value |
|---|---|
| Gaps | 3 |
| Gap class(es) | REGISTRY-DRIFT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 12 of 17 |
| UCIC-001 stage(s) | 8 |
| Declared `discharging_owner` | `SRC-REGISTRATION` |
| Resolution owner | UCOS-REPOSITORY-ROOT |
| Instrument that must change | `pyproject.toml` |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** **No independent action.** `probe_coverage` reads the same two `pyproject.toml` keys as `probe_registry`. The registry resolution closes this dimension for the same three capabilities in the same edit.

**Evidence required to prove closure.** Probe emits `coverage_source:<location>` + `coverage_addopts:<name>`.

**Validation required.** Stages 2 and 3 as above. Then UICM re-measure: `probe_coverage` returns CLOSED.

**Verification required.** Byte replay. Coverage is measured as *denominator membership*, never as a percentage — a percentage is an observation of an execution and would leave the register with no fixed point.

**Expected observation transition.** `OPEN` -> `CLOSED` for 3 coordinate(s);
3 new observation(s) appended, 3 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
3; no gap record is edited or removed.

### Priority 6 · `evidence` — Evidence Closure

| Field | Value |
|---|---|
| Gaps | 39 |
| Gap class(es) | UNSATISFIED-REQUIREMENT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 15 of 17 |
| UCIC-001 stage(s) | 9 |
| Declared `discharging_owner` | `SRC-CAPABILITY-IDENTITY` |
| Resolution owner | the capability's own package (UGA path owner) |
| Instrument that must change | `<location>/evidence.py` or a declared evidence format |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** The capability must *produce* evidence. Two declared routes: an `evidence` module in the package, or a declared evidence format emitted by its own code (`_EVIDENCE_FORMAT` over the concatenated package body). The declaration is explicit that `catalogue evidence_present` and `artifact evidence_class` are **classifications of an artifact, not producers of evidence**, and accepting either "would close this dimension for every capability in the repository, which is how a measurement stops measuring anything". Evidence *storage* remains `engine/registry/universal` `EvidenceRegistry` — a `prohibited_creation` for UICM.

**Evidence required to prove closure.** Probe emits `evidence_producer:<location>/evidence.py` or `evidence_producer:emits <format>`.

**Validation required.** Stage 2 plus the capability's own suite. Then UICM re-measure: `probe_evidence` returns CLOSED.

**Verification required.** Byte replay. 39 gaps — the largest genuinely per-capability body of work, and the one least amenable to a single central edit.

**Expected observation transition.** `OPEN` -> `CLOSED` for 39 coordinate(s);
39 new observation(s) appended, 39 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
39; no gap record is edited or removed.

### Priority 7 · `certification` — Certification Closure

| Field | Value |
|---|---|
| Gaps | 35 |
| Gap class(es) | UNSATISFIED-REQUIREMENT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 16 of 17 |
| UCIC-001 stage(s) | 10 |
| Declared `discharging_owner` | `SRC-GATE-BINDING` |
| Resolution owner | CMG-DLG-40 enforcement machinery / UCCEP-000000 |
| Instrument that must change | `.github/workflows/*.yml` + `00-MASTER/UCCEP-000000/uccep-bindings.json` |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** Bind the capability to a gate that can reach a verdict. `probe_certification` also accepts a `certification` module inside the capability, **but that route is refused as the canonical resolution**: letting each capability mint its own certification instrument would create 35 parallel certification authorities and violate `certification_binding` ("UICM is not a certification authority") and CMG-INV-02. So the single canonical route is a CI gate binding declared as a `CK-<PROG>` check under an aggregate gate, with the verdict remaining with `engine/universal_certification`.

**Evidence required to prove closure.** Probe emits `certification_instrument:gate <workflow>`.

**Validation required.** The bound workflow must execute and pass; `uccep-gate.yml` is the aggregate backstop. Then UICM re-measure: `probe_certification` returns CLOSED.

**Verification required.** Byte replay. A gate that names a capability but evaluates nothing about it satisfies the probe while proving nothing — the binding must be a real check, not a string match.

**Expected observation transition.** `OPEN` -> `CLOSED` for 35 coordinate(s);
35 new observation(s) appended, 35 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
35; no gap record is edited or removed.

### Priority 8 · `determinism` — Determinism Closure

| Field | Value |
|---|---|
| Gaps | 42 |
| Gap class(es) | ABSENT-OBLIGATION |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 13 of 17 |
| UCIC-001 stage(s) | 6 |
| Declared `discharging_owner` | `SRC-VERIFICATION-BINDING` |
| Resolution owner | UCOS-REPOSITORY-ROOT (verify.sh) under CMG-DLG-40 |
| Instrument that must change | `verify.sh` `run_stage` or a workflow replay marker |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** Make a located instrument *ask* the replay question. Two declared routes: a `run_stage` line in `verify.sh` naming the capability, or a bound workflow carrying a declared replay marker (`--replay` / `determinism`). 42 gaps is the largest dimension precisely because the declaration refuses to treat an unasked question as passing: "An unasked question has no passing answer." Reuse `engine/determinism` (`hermetic_env`, `double_build`, `compare_builds`) rather than writing a second replay harness.

**Evidence required to prove closure.** Probe emits `replay_binding:verification entry point` or `replay_binding:gate <workflow>`.

**Validation required.** The added stage must actually re-run and compare. Then UICM re-measure: `probe_determinism` returns CLOSED.

**Verification required.** Byte replay. Note the failure mode: because the probe is a substring test over `verify.sh` and workflow text, a mention without a real replay comparison would close the dimension falsely. Tightening the test is a declaration edit (`replay_markers`), which is the declared remedy.

**Expected observation transition.** `OPEN` -> `CLOSED` for 42 coordinate(s);
42 new observation(s) appended, 42 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
42; no gap record is edited or removed.

### Priority 9 · `evolution` — Evolution Closure

| Field | Value |
|---|---|
| Gaps | 30 |
| Gap class(es) | UNSATISFIED-REQUIREMENT |
| Current state | OPEN (all blocking) |
| Dimension ordinal | 17 of 17 |
| UCIC-001 stage(s) | 11, 14, 15 |
| Declared `discharging_owner` | `SRC-GATE-BINDING` |
| Resolution owner | CMG-DLG-40 enforcement machinery / UCCEP-000000 |
| Instrument that must change | gate binding + `pyproject.toml` + the capability's suite |
| Required capability | already exists — see resolution capability matrix |

**Resolution approach.** All three safety-net members must hold at once (`required_net_size: 3`): coverage-denominator membership, at least one regression case attributed by import, and a bound gate or published entrypoint. This is the only composite dimension, so it is genuinely last: it cannot close before `registry`/`coverage` and the capability's tests exist.

**Evidence required to prove closure.** Probe emits three `safety_net:…` references simultaneously.

**Validation required.** Stages 1, 2, 3 and the bound gate. Then UICM re-measure: `probe_evolution` returns CLOSED.

**Verification required.** Byte replay. 30 gaps, every one blocked on at least one lower-layer dimension.

**Expected observation transition.** `OPEN` -> `CLOSED` for 30 coordinate(s);
30 new observation(s) appended, 30 prior observation(s) become
`SUPERSEDED` by derivation. Gap count falls by
30; no gap record is edited or removed.

## 4. Dependency-ordered closure waves

The declared priority (identity -> registry -> governance -> contract -> coverage ->
evidence -> certification -> determinism -> evolution) is consistent with measured
dependencies, with two corrections discovery established:

- **`governance` is a free rider on `identity`** — one action closes both, so ranking it
  third is harmless but it is not independently actionable.
- **`coverage` is a free rider on `registry`** — the same `pyproject.toml` edit closes
  both for the same three capabilities, so ranking coverage fifth separates two gaps
  that resolve in one action.

| Wave | Dimensions | Gaps | Distinct actions | Blocked by |
|---:|---|---:|---:|---|
| 1 | identity + governance | 2 | 1 (`uga_engine.py run`) | nothing |
| 2 | registry + coverage | 6 | 1 (`pyproject.toml`) | **Task-5 freeze on `pyproject.toml`** |
| 3 | contract | 4 | 4 (`__init__.py` each) | nothing |
| 4 | evidence | 39 | 39 (per capability) | nothing |
| 5 | certification | 35 | 35 gate bindings | nothing |
| 6 | determinism | 42 | ≤42 | **Task-5 freeze on `verify.sh`** |
| 7 | evolution | 30 | 30 | wave 2 + per-capability tests |
| | **total** | **158** | | |

**Wave 1 is the only wave executable today.** Waves 2 and 6 touch `pyproject.toml` and
`verify.sh`, both frozen until the closure architecture is proven; wave 7 depends on
wave 2. That is not an obstacle to route around — it is the freeze doing its job, and it
is why this phase stops at discovery.

## 5. Determination

**158/158 GAPS ARE SPECIFIED, OWNED AND CLOSABLE.** Every gap has exactly
one resolution owner, a located instrument, a required-evidence statement, a validation
route and a declared observation transition. No gap requires a capability that does not
already exist. Nothing here has been executed.
