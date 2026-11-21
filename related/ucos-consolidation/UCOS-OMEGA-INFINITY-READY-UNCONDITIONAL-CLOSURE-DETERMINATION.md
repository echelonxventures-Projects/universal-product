# UCOS Ω∞ — READY UNCONDITIONAL CLOSURE DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-READY-UNCONDITIONAL-CLOSURE-DETERMINATION.md` |
| KIND | `CMG-K-17` — Determination (derived truth) |
| STANDING | **DECLARATIVE** (`CMG-000001` XII.6) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Determines conditions; asserts no readiness. Creates no requirement, ADR, identifier, authority, form, law or gate. Mutates no code, configuration, registry, status field or certification. Not registered in `CMG-REGISTRY.json`; **SHALL NOT be cited as constitutional authority** (`CMG-L-01`). |
| MODE | **OBSERVE.** |
| VERDICT ISSUED | **NONE.** This determination issues no readiness verdict, upgrades no verdict, and modifies no status field. See §0.1. |
| BASELINE | HEAD `bae59755` · `integration/recovery-001` · **78 dirty paths at time of measurement** · 6,188 tracked files |
| ⚠ BASELINE EVENT | **An ungoverned mutation occurred during this determination's own evidence gathering, at 19:02.** `register.sh --guard` executed its full registration transaction: 238 pages emitted, 6 ledgers and 6 registry documents rewritten, ~36 identifiers minted. Working tree moved **78 → 329** dirty paths. Every measurement in §4 was taken **before** the event and is marked accordingly. **The event is not treated as closure** — see §10.3, which records it as the live realization of condition `RU-07` |
| SUBJECT | The conditions standing between `READY WITH CONDITIONS` and `READY UNCONDITIONAL` |
| PREMISE | **Located, and narrower than the question assumes.** `READY WITH CONDITIONS` exists as a verdict in exactly **one** artifact, at a **superseded-in-fact baseline**, over a **different scope**. §1 establishes this before anything is derived from it |
| METHOD | Conditions are admitted only where a located instrument states them or a command measures them. The test for "unconditional" is taken from the corpus, not invented — §2 |
| CONDITIONS DETERMINED | **20** · 18 closable in-corpus · **2 not closable by any repository work** |
| VERDICT | `CONDITIONS-DETERMINED · NO READINESS ASSERTED · NO STATUS MODIFIED · NOTHING IMPLEMENTED` |

---

## SECTION 0 — DETERMINATION BOUNDARY

### 0.1 What this determination refuses to do

Three refusals, stated first because the directive requires them and because each is a live temptation in this corpus:

1. **No readiness is claimed.** No verdict is issued, no verdict is upgraded, and no verdict is retired. Where this document concludes something about reachability, it states it as a derivation from located tests and marks it falsifiable.
2. **No status is modified.** No status field, no registry, no declaration and no certification is written. The single mutation is the creation of this file, whose measured consequences are disclosed in §10.
3. **No implementation.** No condition below is closed, begun, or scheduled by this document. Sequencing lives in `UCOS-OMEGA-INFINITY-IMPLEMENTATION-SEQUENCE-MASTER-PLAN.md`; this document determines *what must be true*, not *when*.

### 0.2 One methodological commitment

The corpus contains a recurring failure this determination is built to avoid, and it is documented in the corpus's own words. `100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md` §8.2 contrasts *"Before analysis: … 54.3% … NOT READY"* with *"After analysis: … 100% … READY FOR IMPLEMENTATION"*, listing as the basis *"8 determination documents produced"* and *"3 admission analysis documents produced."* **No blocker was discharged between those two states.** The improvement was documentary.

Accordingly: **no condition below is marked closed on the strength of a document.** Each carries either a command output taken this session or a located instrument's verbatim text. Where I could not measure, the field reads `UNMEASURED` rather than being inferred.

---

## SECTION 1 — LOCATING THE PREMISE

The question presupposes a current state of `READY WITH CONDITIONS`. Before determining what closes it, the premise must be located, because a condition set derived against the wrong scope would be precise and useless.

### 1.1 The premise is real, committed, and in the ancestry of HEAD

`READY WITH CONDITIONS` appears as a **verdict** in exactly one artifact in the repository:

**`02-MASTER/UCOS-EXEC-001-EXECUTION-FRONTIER-AND-PROGRAM-TRANSITION-DETERMINATION.md`**
- `:188` — `> ## **READY WITH CONDITIONS**`
- `:222` — `> ## **TRANSITION DECISION: READY WITH CONDITIONS (TC-1 … TC-4; no blocking condition)**`
- `:224` — trailer `… ENGINEERING-EXECUTION-ONLY · READY WITH CONDITIONS`
- **Scope:** whether UCOS Ω∞ may transition **from FOUNDATION to SYSTEMATIC IMPLEMENTATION**. Held authority: `ENGINEERING-EXECUTION-ONLY`.
- **Baseline:** `HEAD 5874ede`, branch `governance-reconciliation`, working tree DIRTY, dated 2026-07-18.
- **Verified:** the file is **TRACKED** in git, and `git merge-base --is-ancestor 5874ede HEAD` returns true — `5874edea Add data domain models and validation framework`. So the premise is committed Repository Truth and its baseline is genuinely in this branch's history.

Its four conditions, verbatim:

| ID | Condition | Owner named |
|---|---|---|
| `TC-1` | *"Commit the pending working-tree hygiene to restore a clean, reproducible baseline: **MEP-10** (MCS subsystem) then **MEP-07** (REG-AUTO-001 regeneration)."* | MCS Architect / UKB tooling |
| `TC-2` | *"Re-derive the ISR + CIOA Global Implementation Graph at HEAD `5874ede` so the baseline reflects EC-2 closure (OBS-2)."* | CIOA orchestration process |
| `TC-3` | *"Refresh CI signals on current HEAD (**MEP-08**) to reconcile with the 2,677-pass local evidence."* | CI |
| `TC-4` | *"Constitutional finality (**MEP-09** / DR-RAT-11) remains external and **non-blocking**."* | external |

And `:182` — `**Blocking conditions to systematic implementation:** **NONE.**`

The only other corpus occurrence of the phrase is **vocabulary, not verdict**: `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-READINESS-001-…:18` enumerates *"NOT READY, READY WITH CONDITIONS, or READY FOR EXECUTION"*. That document's actual verdict was `READY FOR EXECUTION` (`:208`) with zero conditions, over the five-artifact governance stack only.

### 1.2 The premise's own justification names exactly why it was conditional

This is the most useful sentence in the premise, because it defines the gap the question asks about — `:197`:

> *"…the execution lane is OPEN with **a single deterministic RUNNABLE root** (Band 10, ADMITTED). CIOA and CCE are active. The only reasons this is *conditional* rather than unqualified are **baseline-hygiene and living-registry-staleness** items, none of which block the frontier. The verdict is therefore **READY WITH CONDITIONS**, not NOT READY (no blocker exists) and **not unqualified READY (a dirty tree + stale ISR/CI are outstanding)**."*

Reinforced at `:111` — *"There is **exactly one** RUNNABLE root on the realization critical path: **MEP-01 (Band 10)**. Frontier is singular and deterministic."* — and at `:210` — *"Execution order deterministic | **YES** | §4 single RUNNABLE root."*

So per the premise itself, `READY UNCONDITIONAL` was **two items away**: a clean tree, and a current ISR/CI. Both were classified hygiene. Neither was a blocker.

**That is no longer the state, and §3 shows the load-bearing property has inverted rather than merely lagged.**

### 1.3 A contradicting verdict exists at HEAD, and nothing is formally superseded

| Artifact | Scope | Verdict | Baseline | Git |
|---|---|---|---|---|
| `UCOS-EXEC-001-…-PROGRAM-TRANSITION-DETERMINATION.md:188` | FOUNDATION → SYSTEMATIC IMPLEMENTATION | **READY WITH CONDITIONS** (TC-1…TC-4) | `5874ede` 2026-07-18 | TRACKED |
| `UCOS-OMEGA-INFINITY-IMPLEMENTATION-ADMISSION-READINESS-DETERMINATION.md:504` | pre-implementation admission, programme-wide | **`# NOT READY`** — 6 blockers `B-1`…`B-6`, *"each independently sufficient"* | `bae59755` = **live HEAD** | **UNTRACKED** |
| `02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md:40` | the registry's nomination | **CONDITIONALLY READY FOR IMPLEMENTATION** (EC-2 lane authorized) | — | TRACKED |
| `IAC-001E/07-IMPLEMENTATION-READINESS.md:11` | mission IAC-001E | **CONDITIONALLY READY** | `836475c` | TRACKED |
| `00-MASTER/MIP-W1-P001/README.md:13` | Wave-1 → Wave-2 | **CONDITIONALLY READY FOR WAVE-2** — 4 blockers + 1 vacancy | `c6c20fb5` | TRACKED |
| `PHASE-POST-FREEZE-EVOLUTION-READINESS-DETERMINATION.md:73` | evolution lifecycle | **(B) Ready with documented implementation prerequisites**; explicitly *"(A) … unconditionally — **No**"* | `ec8b8d5b` | TRACKED |
| `UCOS-Ω∞-FINAL-REPOSITORY-READINESS-DETERMINATION.md:138` | repository health | **B. FOUNDATION COMPLETE — REQUIRES LIMITED REMEDIATION** | `1f869865` | TRACKED |
| `100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md:433` | phases 2–6 | **100% ✅ READY FOR IMPLEMENTATION**, *"Blocking risks: **ZERO**"* | `03179308` | **UNTRACKED** |

**None of these declares itself superseded or superseding.** That is not an artifact of reading — it is a registered defect. `UCOS-Ω∞-FINAL-REPOSITORY-READINESS-DETERMINATION.md:237` records gap `G-11`: *"Supersession vocabulary legislated but unused | 1 supersession header in ~145 root docs; 0 SUPERSEDED statuses in 1233 artifacts; 49 docs with no status marker."*

Two consequences that bear directly on the question:

- **The premise stands, unretired, alongside a verdict that contradicts it at the current baseline.** Closing `READY WITH CONDITIONS` therefore includes reconciling the verdict landscape — recorded as `RU-18`, a condition the question did not anticipate but which the evidence forces.
- **The contradicting verdict is untracked**, and the corpus's own rule is `TRACK-001` fail-closed: *"absence of evidence = NOT-DONE"* (`02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md:25`). Under that rule the HEAD determination is not yet committed Repository Truth — which does not make it wrong, and does make its status a condition in itself.

### 1.4 Determination on the premise

The question as posed assumes one transition. The evidence shows **two**, over **two scopes**:

> **`T-A`** — from the committed `READY WITH CONDITIONS` (FOUNDATION → SYSTEMATIC IMPLEMENTATION, at `5874ede`) to unconditional at that same scope. Requires `TC-1`…`TC-3` and the restoration of the single-root property (§3).
>
> **`T-B`** — from the HEAD-baseline `NOT READY` (pre-implementation admission, programme-wide) to `READY WITH CONDITIONS` at that scope, and only then to unconditional. Requires the six blockers plus everything in §4.

**Applying the premise's verdict to today's state would be a scope error**, and the premise itself forbids it: `CEP-000:473` `30.2 CM-2 — Stage completion SHALL be distinct from readiness; completion of a stage SHALL NOT implicitly authorize its successor`, restated as law at `CEP-001:353` `XXII.1 Stage completion SHALL require satisfaction of that stage's exit criteria and SHALL be distinct from readiness.`

Every condition in §4 is tagged with the transition it belongs to.

---

## SECTION 2 — WHAT "UNCONDITIONAL" MEANS, TAKEN FROM THE CORPUS

The conditions below are worthless unless the target is defined by a located instrument. Three findings, one of them negative and important.

### 2.1 There is no canonical readiness predicate — measured, not assumed

`00-CEP/STAGE-02-S2-01-…-CROSSWALK.md:151` cites a *"CEP readiness predicate (exit ∧ next-entry ∧ single-next-action)"* attributed to `CEP-001 / CEP-000 §31`. **That predicate does not exist verbatim in either.** Across `00-CEP/CEP-000…CEP-010` the word `readiness` appears five times and never as a defined predicate. `CEP-001` mentions readiness exactly once — at `XXII.1`, and only to say what it is *not*.

The crosswalk formula is a faithful *synthesis*, not a quotation. Its three conjuncts are individually legislated and individually quotable:

| Conjunct | Located at | Verbatim |
|---|---|---|
| **exit** | `CEP-001:41` (LAW-3) | *"No stage SHALL be entered before its entry criteria hold, and no stage SHALL be exited before its exit criteria hold."* |
| **next-entry** | `CEP-000:549` §34.5; enforced `CEP-003:140` | *"Authorization SHALL be denied when the active stage's entry criteria do not hold; a denied authorization SHALL place the Program in HALTED."* |
| **single-next-action** | `CEP-001:157` INV-6 + six more | *"Exactly one next authorized action is defined at every checkpoint."* |

**This determination does not claim to quote a readiness predicate**, because doing so would be falsifiable against `00-CEP/`.

### 2.2 The vocabulary has an owner but no membership criteria

`Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }` is owned by the Implementation State Registry — `02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md:25`, registry slot `R-13`. The ISR *records state only*; it enumerates the three values and supplies **no criteria for membership**. `00-CEP/STAGE-02-S2-11-…:24` explicitly disclaims authorship: *"Readiness vocabulary (inherited, not redefined)."*

**So no instrument states necessary-and-sufficient conditions for READY.** Any determination that asserts one is legislating, and this one does not.

### 2.3 The one quotable unconditionality test

`07-ENGINEERING/UCOS-Ω∞-ENGINEERING-FOUNDATION-COMPLETION-ENG-005-READINESS-DETERMINATION.md:208-210`, which reached an unqualified READY and stated its own criterion:

> *"**No conditions outstanding:** no gap, no unresolved dependency, and no destabilizing factor requires a CONDITIONALLY READY qualifier."*
>
> *"Accordingly, the determination is **READY** — unqualified."*

Read as a predicate: **unqualified READY ⟺ (no gap) ∧ (no unresolved dependency) ∧ (no destabilizing factor).** Any one of the three forces the qualifier.

The complementary boundary, from `02-MASTER/UCOS-GOV-003-IMPLEMENTATION-READINESS-DETERMINATION.md:298`:

> *"No closure dimension is failed outright; therefore the repository is neither fully READY nor NOT READY, but **CONDITIONALLY READY FOR IMPLEMENTATION**."*

And the worked example of what earns unqualified READY — `S2-11:215`: *"dependencies closed; substrate certified; determinism preserved; **next lawful action defined**"* — note the singular, which §3 turns on.

### 2.4 There is no upgrade rule, so each condition discharges independently

Searches for `unconditional`, `condition discharged`, `upgraded to READY`, `becomes READY`, `lift the condition` and `promote.*READY` return **no readiness-promotion rule anywhere in the corpus**. What exists is per-determination condition enumeration, of which `GOV-003:298` is the fullest example.

Two hard constraints bound any upgrade attempt:

- `CEP-000:477` `30.4 CM-4 — No completion SHALL be declared while any blocking finding, orphan, drift, or unresolved deferral remains.`
- `CEP-000:479` `30.5 CM-5 — Every declaration of completion SHALL be provable by reference to evidence and traceability.`

**Consequence for the condition register:** there is no partial credit, no discretionary upgrade, and no time-based expiry. Twenty conditions means twenty independent discharges, each with evidence.

### 2.5 The corpus has already adjudicated one unconditionality claim — and proved it unreachable

`00-MASTER/P0-FINAL-CLOSURE-002/UCOS-P0-FINAL-CLOSURE-DETERMINATION.md`:
- `:8` — `| **VERDICT** | **UNCONDITIONAL CERTIFICATION — PROVEN IMPOSSIBLE IN-CORPUS** |`
- `:21` — *"Tier **T1 (Constitutional Authority)** is **VACANT** — `VAC-01` in `00-CMG/CMG-REGISTRY.json`."*
- `:148` — `| 6 Unconditional certification | **POSSIBLE AFTER VACANCY RESOLUTION**; from inside — **PROHIBITED** |`
- `:158` — `### Can P0 achieve UNCONDITIONAL CERTIFICATION inside Repository Truth?` → resolved at `:160` to `# PROVEN — NO`

This is precedent, not analogy: the repository has already run this exact question for the certification analogue, and registered the answer. §5 states what it implies for readiness without extending it beyond its scope.

---

## SECTION 3 — THE DECISIVE STRUCTURAL CONDITION

Set out separately because it is the one condition the question could not have anticipated, it is the one the premise itself rested on, and it has moved in the wrong direction.

### 3.1 The requirement is "exactly one", legislated seven times

| Location | Verbatim |
|---|---|
| `CEP-001:157` | `VII.6 INV-6 — Exactly one next authorized action is defined at every checkpoint.` |
| `CEP-001:71` | `II.5 Every operational act SHALL conclude by advancing program state and emitting exactly one next authorized action.` |
| `CEP-000:317` | `19.3 AP-3 — Every checkpoint SHALL yield exactly one next authorized action so that resumption is deterministic.` |
| `CEP-003:65` | `III.4 Every execution unit SHALL conclude at exactly one terminal state and SHALL emit exactly one next authorized action **or a halt**.` |
| `CEP-003:138` | `VIII.2 Authorization SHALL grant exactly one next authorized action and SHALL bind it to one stage and one write area.` |
| `CEP-003:164` | `X.3 Handoff … through a checkpoint that emits exactly one next authorized action.` |
| `CEP-003:190` | `XII.4 A checkpoint SHALL emit exactly one next authorized action.` |

The wording is `exactly one` in all seven, and `CEP-003:65` gives the only permitted alternative: **one action, or a halt.** The stated rationale is determinism of resumption (`AP-3`), which is independently mandated by `CEP-000` `31.9 SD-8`.

The failure mode is specified rather than left open: `CEP-001:185` `VIII.6 HALTED SHALL be entered on any failed criterion or contradiction and SHALL be exited only upon remediation.`

### 3.2 The premise satisfied it. The current state does not.

| Baseline | Root count | Source |
|---|---|---|
| `5874ede` (the premise) | **1** — *"There is **exactly one** RUNNABLE root on the realization critical path: MEP-01 (Band 10). Frontier is singular and deterministic."* | `UCOS-EXEC-001:111` |
| `bae59755` (HEAD) | **6 actionable + 2 decision-only** | `UCOS-OMEGA-INFINITY-CLOSURE-DEPENDENCY-GRAPH-DETERMINATION.md` §7, derived this session from cited edges |

### 3.3 Determination `RU-17`

Under `INV-6` read with `CEP-003:65`, a state offering six or eight lawful next actions offers neither `exactly one` nor `a halt`. It is therefore a failed criterion, and `CEP-001:185` routes a failed criterion to HALTED, exitable only upon remediation.

Two further obstructions make this structural rather than presentational:

- `CEP-003:138` requires an authorization to bind its single action to **one stage and one write area**. Six independent roots cannot bind to one write area without either merging them — destroying the independence that measurement established — or issuing six authorizations, which `CEP-003:63` forbids: `III.3 No second execution unit SHALL enter RUNNING before the current unit reaches a terminal state.`
- The plurality may not be resolved by assertion. `02-MASTER/UCOS-COMP-000000-CONSTITUTIONAL-IMPLEMENTATION-ORCHESTRATION-AUTHORITY.md:59` forbids CIOA to *"declare any critical path, next artifact, or sequence **manually** — every such determination SHALL be dependency-derived from repository evidence."*

**The lawful route to one action exists and is located.** `S2-11:120` records the machinery: *"canonical DAG + lexicographic tie-break; topological antichains."* The tie-break exists precisely because an antichain can hold more than one element while `INV-6` demands one. The corpus's own worked precedent is `EC-1`…`EC-6`, six ordered prerequisites reduced to one nameable action by the rule *"**EC-1 gates all others**"* (`02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-CONSOLIDATION-CLOSURE-REPORT.md` §11) — and note that even with the collapse achieved, that verdict is `CONDITIONALLY READY`, never READY.

So `RU-17` is: either a dependency-derived ordering collapses the root set to one, or the lexicographic tie-break is invoked and declared. **Six independent roots is the single largest structural distance between the current state and any unqualified verdict**, and it is a distance the premise did not have.

---

## SECTION 4 — CONDITION REGISTER

Twenty conditions. Each carries the five fields the directive requires. `T-A`/`T-B` marks the transition (§1.4). Certification fields are bounded by `UCCEP-F-004` — *"Maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`"* — so none promises more.

### CLASS A — BASELINE AND EVIDENCE ADMISSIBILITY

---

#### `RU-01` — Clean, reproducible baseline · `T-A` `TC-1` · also `B-6`, MIP `B-1`

| Field | Content |
|---|---|
| **Current evidence** | `git status --porcelain \| wc -l` → **78**. `bash 00-BOOK/tools/register.sh --guard` → **exit 2**: `VALIDATION FAILED — 3 problem(s)`; `UCOS-F1LINE-000001 projected Parent UCOS-USIS-000001 is not the declared parent UCOS-BOOK-000000`; same for `UCOS-USIS-000017`; `UCOS-F1LINE-000001 has 3 conflicting projected parents: ['UCOS-BOOK-000000','UCOS-USIS-000001','UCOS-USIS-000017']`; then `TRANSACTION INCOMPLETE — ukb validate failed` / `Artifacts remain UNREGISTERED; completion claims INVALID.` Among the 78 are `verify.sh` +45/−0 and `generated-artifact-registry.json` +864/−0. `TC-1` was raised 2026-07-18 and is **undischarged five weeks later**; the tree has not been clean at any measured point since |
| **Missing evidence** | A `git status --porcelain` of zero. `register.sh --guard` exit 0 **from a clean tree** — the discharge condition MIP `B-1` states verbatim: *"`register.sh --guard` exits 0 from a clean tree; all 1,204 `content_hash` values match committed bytes."* Whether the 10 stale `content_hash` entries recorded in `wave1-baseline.json` persist is **UNMEASURED** — the guard aborts at parent-conflict validation before reaching that check |
| **Closure action** | The owning programmes commit their own work (`H-06` Phase-0 condition `0.6`, currently failing). Resolve the three-way parent conflict on `UCOS-F1LINE-000001`, which is a declared-versus-projected parent disagreement, not a hash staleness |
| **Validation requirement** | `git status --porcelain` empty **and** `register.sh --guard` exit 0 **and** the 1,204 content hashes matching committed bytes, in one measurement from one tree state |
| **Certification requirement** | Two consecutive clean measurements from independent invocations, at `CERTIFIED-PROVISIONAL`. A single pass is insufficient: `ADR-0020` records a teardown fixture that reverted two governed mutations *"silently, with no test failure to signal it"* |

---

#### `RU-02` — Canonical validation green · `T-B` `B-6`

| Field | Content |
|---|---|
| **Current evidence** | Measured this session, gate by gate. **Red:** `uga_engine.py gate` → **1** (`UGA-INV-01` violations=43 measured=6188; `UGA-INV-10` violations=43 measured=4955; all other invariants 0) · `engine.uaue.gate --replay` → **1** (`REPLAY DRIFT … 1316175 bytes committed, 1316175 bytes projected` — identical counts, so content drift at equal length) · `engine.infinite_scope.gate` → **1** (`laws measured / refused : 11 / 1`; `ISD-L-07` refused on 2 undeclared sites carrying 3 occurrences) · `register.sh --guard` → **2** · `platform.measurement.cli health --strict` → **1** (`unhealthy traceability-gaps`). **Green:** `uaue --gate` 0 · `object_birth` 0 · `verification_intelligence` 0 · `root_ontology` 0 · `cmg-gate.sh` 0 (`readiness outcome : READY-PROVISIONAL`, `vacancies recorded : 1`) · `ukb.py enforce --pre` 0. Tests: `.pytest_cache` holds **23 failing node ids across 20 modules** |
| **Missing evidence** | `./verify.sh --full` exit 0. **Correction to the standing account:** the pytest stage does not fail on coverage — coverage over the committed `.coverage` is **97%** against a `--cov-fail-under=90` floor. The failure is 23 tests. Any closure plan citing a coverage breach is aiming at the wrong defect |
| **Closure action** | Four independent sub-actions, cost-ordered per the located `B-6` sequence: disclose the 2 `ISD-L-07` sites in `freeze_scan.preserved_sites` with class and count; mint the 43 anonymous objects under a new `CEP-002` Article 28 decision; capture the replay delta **before** running `make uaue-render`; resolve the 23 failing tests with their owners |
| **Validation requirement** | `./verify.sh --full` exit 0 with all 15 stages PASS. Note `decide()` refuses evidence reuse for `integration` and `full` modes by construction, so certification always re-executes |
| **Certification requirement** | Exit 0 on two consecutive `--full` runs from a clean tree — the bar `ADR-0017` met. `CERTIFIED-PROVISIONAL` |

---

#### `RU-03` — Gate/test agreement · **newly derived; in no prior register**

| Field | Content |
|---|---|
| **Current evidence** | Three gates exit **0** while their corresponding unit tests are cached as **failing**: `root_ontology` gate 0 vs `engine/tests/unit/test_root_ontology.py`; `uaue --gate` 0 vs `test_uaue_controller.py` and `test_uaue_evolution_engine.py`; `verification_intelligence` gate 0 vs `test_verification_intelligence.py`. Exactly one of two things is true, and the corpus cannot currently say which: the `lastfailed` cache is stale, or the gates do not cover what their tests cover |
| **Missing evidence** | A single fresh run establishing which. Not measured here — the directive excludes running the full suite, and a partial run would not settle it |
| **Closure action** | Re-run the four named modules against the current tree and reconcile with each gate's own verdict. If the gates genuinely pass while the tests fail, the gate's coverage is the defect and `RU-02`'s green is not evidence of health |
| **Validation requirement** | For each of the four modules: test result and gate exit agree, from one tree state |
| **Certification requirement** | Recorded agreement per module. **This condition gates the *meaning* of every other green in this register** — an unreconciled gate/test disagreement makes exit 0 uninterpretable, so it must certify before `RU-02` can be read as evidence rather than as output |

---

#### `RU-04` — Living-registry currency · `T-A` `TC-2`

| Field | Content |
|---|---|
| **Current evidence** | `TC-2` required re-deriving the ISR + CIOA Global Implementation Graph at `5874ede`. `02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md:40` still reads `| Governing readiness decision | CONDITIONALLY READY FOR IMPLEMENTATION (EC-2 lane authorized) | GOV-003 §15; GOV-004 §14 |`. Anchor drift is measurable: `wave1-baseline.json` anchors at `c6c20fb5`, **4,895 tracked files**, working tree `CLEAN (0 entries)`; today `bae59755`, **6,188 tracked files**, 78 dirty. Every Wave-1 figure — 1,204 artifacts, 91 concepts, 969 evidence artefacts, 56.9% — describes the old anchor |
| **Missing evidence** | An ISR re-derivation at `bae59755`, not at `5874ede`. `TC-2` as written is now under-specified: re-deriving at a baseline 5 weeks and ~1,300 tracked files stale would satisfy the letter and not the purpose |
| **Closure action** | Re-derive the ISR and the CIOA graph at current HEAD. `CIOA:59` forbids declaring the next artifact manually, so the derivation must be dependency-derived from repository evidence |
| **Validation requirement** | ISR re-derives byte-identically from located sources at HEAD, and its `Governing readiness decision` row reflects the derivation rather than a 2026-07 nomination |
| **Certification requirement** | Two consecutive identical derivations. `CERTIFIED-PROVISIONAL` |

---

#### `RU-05` — CI signal currency · `T-A` `TC-3`

| Field | Content |
|---|---|
| **Current evidence** | `TC-3` required refreshing CI on HEAD to reconcile with *"the 2,677-pass local evidence."* That figure is from 2026-07-18. Local evidence today is 23 failures across 20 modules and 97% coverage. `.ucos-verification-evidence/` holds 8 stage directories, 44 PASS and 2 FAIL entries, and is **gitignored** (`.gitignore:222`) — so CI and local evidence do not share a store |
| **Missing evidence** | A CI run on `bae59755` and its reconciliation against local evidence. **UNMEASURED** — I did not query CI |
| **Closure action** | Run the CI workflows on current HEAD; reconcile signal-by-signal with local stage results; record divergences rather than averaging them |
| **Validation requirement** | Every CI gate's verdict matches the local verdict for the same stage on the same commit |
| **Certification requirement** | A reconciliation record naming each divergence and its cause. `CERTIFIED-PROVISIONAL` |

---

### CLASS B — ADMISSION BLOCKERS AT HEAD

---

#### `RU-06` — Canonical ownership threshold · `T-B` `B-1`

| Field | Content |
|---|---|
| **Current evidence** | `python -m platform.universal_ownership.cli homing` → exit 0: `subjects 549 · declared 151 · contested 0 · unresolved 398 · remediable 195 · coverage 27.5046%`, residue `186 EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE · 212 NO-OWNERSHIP-EVIDENCE · 45 LOCATOR-NOT-REGISTERED · 2 LOCATOR-FORM-NOT-ADMITTED · 195 ZONE-NOT-CANONICAL-HOME-ELIGIBLE`. **The trend is adverse:** subjects rose 542 → 549 while declared owners stayed at 151, so coverage fell from 27.86% to 27.5046% |
| **Missing evidence** | 398 owner declarations, of which only 195 are diagnosed remediable — **the other 203 need something other than remediation, and what that is has not been determined.** No threshold has been declared, though the located closure criterion admits one: *"ownership closed **or at a declared threshold**."* Also missing: an entry-condition mechanism binding a new subject to a declaration at admission time |
| **Closure action** | Each subject's own owner declares — no central authority may declare on their behalf without creating the parallel-authority defect `GV-02` currently prevents, and `OWN-REQ-002` `EXACTLY-ONE-OWNER` forbids provisional co-ownership since *"multiple survivors are a contest, never a merge."* Separately, declare the threshold |
| **Validation requirement** | `homing --gate` exit 0, or the declared threshold met with residue enumerated per diagnosis; `contested: 0` preserved; **and coverage measured non-decreasing across two consecutive subject-population changes** — the only validation that tests the trend rather than the level |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` at the declared threshold with residue disclosed. **Note the trap:** `homing` exits **0** today at 27.5% coverage — it is a report, not an enforcing gate. Exit 0 here must not be read as satisfaction |

---

#### `RU-07` — Declared gate mode · `T-B` `B-2`

| Field | Content |
|---|---|
| **Current evidence** | ≥24 gate paths mutate tracked Repository Truth with no declared mode; **4 of 46** `*-gate` targets declare one. `uccep-bindings.json` binds 26 gates and 48 checks and carries **no `mode` field on any of them** — the discriminator present is `tier` (`boot` 25 · `standard` 19 · `full` 4). Recorded harm: `uccep --gate` wrote 47 tracked files across 4 programme homes; a drift check minted 140 identifiers; one `--gate` probe wrote 11 tracked files with two operators' uncommitted bytes unrecoverable. **And one new incident, caused by this determination at 19:02: `register.sh --guard`, invoked to measure `RU-01`, emitted 238 documents, rewrote 6 ledgers and 6 registries, minted ~36 identifiers, and moved the tree 78 → 329 dirty. See §10.3.** `H-06-R3` settled the field name (`gate_mode` ACCEPTABLE, `R-3 RESOLVED`) |
| **Missing evidence** | The owner decision. `H-06` IADR §8 is signed for its §4 scope, but Phase 0 stands at **2 of 6**: `0.2` `P-3` unselected and *"blocked until R-4 is corrected per §3.2"*; `0.5` `verify.sh` baseline never captured; `0.6` unrelated deltas not isolated; `0.4` unmeasured owner act. *"No phase begins until all six pass."* `R-4` remains the only OPEN item of `R-1`…`R-4` |
| **Closure action** | Mutation Governance Owner acts under `H-06`/`CR-09` on four points: the Option A/B mode policy, the `R-4` grandfathering window (`P-3`), confirmation of `gate_mode`, and the standing of an `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` sub-class. Correct `R-4` first — `P-3` cannot be validly selected in `R-4`'s present state |
| **Validation requirement** | Every `*-gate` target declares exactly one mode and honours it, **proven by an injected violation** at each target — the technique is already proven at one (`test_verify_does_not_ensure_the_environment_it_is_verifying:826`; `test_no_bare_tool_is_ever_in_command_position:887`). Guard: no mode may be declared on a surface whose owning engine carries no `--check-declaration` |
| **Certification requirement** | Per-target injected-violation evidence at `CERTIFIED-PROVISIONAL`. **The criterion is *mode declared and honoured*, never *gate purity closed*** — `H-06-IADR:363` states *"Executing the full authorized scope does not close gate purity"*, and `GP-1`/`GP-3`/`GP-11` terminate OPEN as disclosed residuals |

---

#### `RU-08` — Safety composition · `T-B` `B-3`

| Field | Content |
|---|---|
| **Current evidence** | `platform/security` is 13 modules / 6,512 LOC, **architecturally non-enforcing**, referenced by **zero** CI workflows. Adjacent absences measured: no dependency scan, no CI secret scan, no SAST, no Dependabot, no renovate, no SBOM, no lockfile — `.github/` contains only `workflows/`. The only security lint is ruff `S`. `14-SECURITY/` is 5 markdown files and 0 code |
| **Missing evidence** | The enforce-versus-record decision, and **the authority to make it.** The register names `ARCH-SECURITY-001`; that authority appears in derived architecture data and in prose, and is **registered nowhere** in `00-CMG/CMG-REGISTRY.json` |
| **Closure action** | Locate `ARCH-SECURITY-001` or route the decision to `CEP-002` via `CMG-DLG-02`. Then compose — but only after `RU-07`, on a structural argument rather than a preference: *"While ≥24 gate paths mutate undeclared, adding machinery to admission adds mutation to admission"* |
| **Validation requirement** | Security analysis **reachable from the admission path with reachability measured** — import-graph or call-graph proof, since the current defect is precisely that existence was mistaken for reachability. A refused admission attributed to a named computed finding |
| **Certification requirement** | Reachability evidence at `CERTIFIED-PROVISIONAL`, with the chosen enforce-or-record semantics declared. Any condition requiring an external vulnerability feed additionally depends on `SC-05`, since an external feed is untrusted input entering a substrate that *"trusts its declaration substrate absolutely"* |

---

#### `RU-09` — Cross-class atomic transaction · `T-B` `B-4`

| Field | Content |
|---|---|
| **Current evidence** | *"A cross-class transaction is not a constitutionally existing category"*, and `UCKP-ART-02` holds *"nothing exists constitutionally until it has become one."* Zero `atomic`/`transaction` tokens in `law.py` or the mutation-governance boundary artifact. `GOVERNED_CATEGORIES` measured at **35 members**, none of them `transaction`. Today's atomicity is `AIF-L14`, **single-class only**. The disposition is settled: **C — a transaction orchestration capability under an existing framework**, with a new authority (**option B**) **rejected on measured grounds**, and the maxim *"There is no transaction authority. Transaction orchestration holds no authority at all"* — role `EXECUTION`, `may_hold_authority: false` |
| **Missing evidence** | Eight owner decisions `D-1`…`D-8`, **all OPEN, none opened as a record.** `D-5` is load-bearing: prospective-only binding, absent which there is a bootstrap deadlock — *"the capability cannot lawfully be created by the act that creates it."* Note this corrects the standing framing: `B-4` is described as needing *"an authority that does not presently exist"*, but the terminal determination **rejects creating one**. It is a decision-then-capability condition, not a vesting condition |
| **Closure action** | Record `D-1`…`D-8` with their named authorities: Mutation Governance Owner (`D-1`, `D-5`, `D-7`), UCKP owner (`D-2`, `D-4`, `D-6`), `ukb.py` alone for repository serials (`D-3`, per `CAA-INV-04`), `AT-2`'s owner (`D-8`). **Do not create a cross-class authority** |
| **Validation requirement** | The proposed invariant holds: *"Every mutation spanning more than one class belongs to exactly one declared transaction, and no transaction claims a class as primary."* A multi-class mutation commits atomically or aborts leaving no orphan identity |
| **Certification requirement** | `CERTIFIED-PROVISIONAL`, certifying a capability that **holds no authority**. A certification asserting transaction authority contradicts the located determination and must be refused |

---

#### `RU-10` — Machine-readable plan state · `T-B` `B-5`

| Field | Content |
|---|---|
| **Current evidence** | `mip.json` re-verified **absent**, so `LAW P50-002` has **no operand**. `MP2-C-01`, CONFIRMED: *"with prose-only success criteria there is nothing to measure over… **Every arrow in the target chain presumes a measurable predecessor, so this blocks the whole model**."* The MIP is **not among the sequencing engine's 8 `SRC` inputs**, although that engine already computes Kahn topological sort, cycle detection and an effort-weighted critical path twice |
| **Missing evidence** | The derived operand. The disposition constrains the method: **derive and register, never amend** |
| **Closure action** | Derive `mip.json` from located sources and wire it into the existing sequencing engine. **Ratification is out of scope and belongs to `RU-19`** — `MP2-C-04` records that a correct `mip.json` would still be unratifiable, so conflating the two makes the condition unclosable |
| **Validation requirement** | `LAW P50-002` returns a **measured** value; `mip.json` re-derives byte-identically, since a derived operand that cannot be re-derived is an amendment in disguise; `roadmap-gate` drift and derivability pass with the MIP included |
| **Certification requirement** | Two identical derivations at `CERTIFIED-PROVISIONAL`. **Measurability only — not ratification** |

---

### CLASS C — WAVE-1 CLOSURE BLOCKERS

---

#### `RU-11` — Knowledge closure measures its own claim · MIP `B-2`

| Field | Content |
|---|---|
| **Current evidence** | The escape hatch is still live: `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py:177` reads `os.environ.get("CLOSURE_SKIP_CORPUS") == "1"`, with supporting text at `:39`, `:214`, `:769`, and `Makefile:247` documents it as *"skips the external corpus scan for a fast repo-only pass."* This session's start hook reported `UAKOS-CLOSURE-002: CLOSED \| concepts=549 \| gaps=0` |
| **Missing evidence** | Whether that `gaps=0` was measured with the corpus scan enabled. **The hook's own report is uninterpretable while the skip variable exists in the standing hook** — a gate that can be told not to look cannot evidence what it did not look at. The current count of unhomed `UCOS-COMP-001001…009009` concepts (91 at the anchor) is **UNMEASURED** |
| **Closure action** | Home the concepts with destination, owner and disposition; **remove `CLOSURE_SKIP_CORPUS=1` from the standing hook** so the gate measures its own claim, per the verbatim discharge condition |
| **Validation requirement** | `closure_engine.py --gate` exit 0 with the corpus scan enabled and no skip variable available to the standing hook |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` on a run whose configuration is recorded alongside its verdict. **A gaps count without its scan configuration is not evidence** |

---

#### `RU-12` — Traceability spine · MIP `B-3`

| Field | Content |
|---|---|
| **Current evidence** | `python -m platform.measurement.cli health --strict` → **exit 1**, `status: unhealthy`; four sub-checks healthy (`measurement-determinism`, `measurement-registry-consistency`, `ownership-gaps`, `structural-truth-gaps`), one **`unhealthy traceability-gaps`** |
| **Missing evidence** | Whether `CK-HEALTH` was promoted from advisory to blocking, and whether any of the 969 evidence artefacts are now bound into the spine — both **UNMEASURED**. The 969 figure is itself from the stale anchor |
| **Closure action** | Bind the evidence artefacts into the spine; promote `CK-HEALTH` to blocking. Owners: `CEP-008` · `platform/measurement` · `engine/graph` |
| **Validation requirement** | `health --strict` exit 0 with `traceability-gaps` healthy, and `CK-HEALTH` blocking rather than advisory |
| **Certification requirement** | `CERTIFIED-PROVISIONAL`. Note the sequencing trap: promoting a check to blocking while it fails converts an advisory signal into a hard stop, so promotion must follow binding, not precede it |

---

#### `RU-13` — Verification scope · MIP `B-4`

| Field | Content |
|---|---|
| **Current evidence** | `pyproject.toml:200` still reads `testpaths = ["engine/tests", "platform/tests", "intelligence/tests"]` — **3 roots, not the 8 code roots** the discharge condition names. `[tool.coverage.run] source` at `:343` is an explicit ~70-subpackage list confined to `engine/` and `platform/`; `fail_under = 90` at `:348` |
| **Missing evidence** | Whether the 12 named uncovered subpackages are now in `source` — **UNMEASURED**, not diffed against the blocker's list. Current coverage against the 56.9% / 52.5% anchor figures is unmeasured; measuring it requires the full suite. **And the material unknown: what fails once the scope widens.** The blocker's own effort estimate says *"days (config) + unknown (resulting failures)"* |
| **Closure action** | Extend `testpaths`, coverage `source`, `packages.find` and the `lint` target to all 8 code roots and the 12 subpackages; then resolve what the widened scope surfaces |
| **Validation requirement** | Gate green **at the new scope** — a green gate at the old scope is not evidence, and this is the condition most easily mistaken for closed |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` with the scope recorded alongside the percentage. A coverage figure without its scope is not comparable to any other coverage figure |

---

#### `RU-14` — Artifact registration completeness

| Field | Content |
|---|---|
| **Current evidence** | `ukb.py enforce --pre` → **exit 0**, `ENFORCEMENT PASSED`, on audit run #601: `eligible on-disk artifacts: 1461 · registered: 1233 · unregistered eligible: 228 · unclassified: 0 (GATED) · reconciled-set drift: 0 (GATED) · invalid: 0 · awaiting VCS binding: 59 (REPORTED)`. Note the gate passes **while 228 eligible artifacts are unregistered** — the gate's contract is that nothing unregistered *silently enters*, not that nothing is unregistered |
| **Missing evidence** | Registration of the 228, or their exclusion with a reason; and disposition of the 59 awaiting VCS binding. `MIP-W1-P001` records that its own twenty outputs are unregistered and self-exempt *"because performing it here would compound the very drift condition recorded as blocker B-1"* — so the population is partly self-inflicted and grows with each determination committed |
| **Closure action** | A dedicated `CEP-002` Article 28 decision enumerating the population, under `REG-AUTO-001`/`CMG-DLG-13`. At roughly 7–8× `ADR-0017`'s scale, and the corpus flags it highest-risk because `register.sh --guard`'s full transaction is implicated, not identity minting alone |
| **Validation requirement** | `ukb.py enforce --pre` reports **0 unregistered eligible**; `UGA-INV`/`CAA-INV` unaffected; the full suite survives per `DEC-ADR-0020`'s fixed fixture |
| **Certification requirement** | Decision registered → minted → survives two consecutive full-suite runs, the bar `ADR-0017` met. `CERTIFIED-PROVISIONAL`. **Depends on `RU-01`** — the guard must pass before a transaction of this size is attempted |

---

### CLASS D — PENDING DECISIONS WITH NO RECORDED OWNER

---

#### `RU-15` — `ConstitutionalPipeline` mandatory-path decision

| Field | Content |
|---|---|
| **Current evidence** | The capability exists and is reachable: `engine/knowledge/integration/pipeline.py:117` `class ConstitutionalPipeline`, *"Runs the fail-closed constitutional execution path over an intent"*, with `execute()` at `:156` and `assimilate()` at `:372`, registered as console script `ucos-knowledge-integration` (`pyproject.toml:54`). **Its complete invocation set is its own CLI, `RepositoryAssimilator`, and tests.** Grepping `Makefile`, `verify.sh` and `.github/workflows/*.yml` for it returns **zero hits** — independently reproduced this session. The located finding: *"the one concrete mechanism that would keep evolution-phase creation disciplined … is not yet the mandatory path for anything"* |
| **Missing evidence** | **The decision, and its owner.** No owner, assignee, ADR or decision record for this exists anywhere searched. §6 of the source determination classifies it as *"an implementation/adoption decision, not a design or discovery gap"* and **names no party.** Owner is missing evidence, not merely pending |
| **Closure action** | Name the deciding owner, then decide: adopt it as the mandatory entry point *"matching its own stated purpose"*, or explicitly record that it remains optional tooling **and accept the risk that describes**. Either is a closure; silence is not |
| **Validation requirement** | If mandatory: a gate requires it and an injected bypass fails. If optional: the decision is recorded with its accepted risk named, and no gate claims otherwise |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` on the recorded decision. **This condition cannot be closed by measurement** — it is a choice, and measuring the current state (unwired) does not discharge it |

---

#### `RU-16` — "Universal Evolution Law" scoping

| Field | Content |
|---|---|
| **Current evidence** | **NOT DRAFTED**, recorded twice. `UCOS-POST-STABILIZATION-READINESS-DETERMINATION.md:51` gives home *"Not yet homed"*, status `NOT DRAFTED`. `PHASE-POST-FREEZE…:54` — *"has never been scoped or drafted… Whether evolution work needs only that, or genuinely new supreme law text, has still not been determined."* The cheap path is measured available: `GOVERNED_CATEGORIES` at `engine/uckp/law.py:424` holds **35 members** and is an open set — *"Article 17 requires that an unknown future category be admitted by registration, never by editing this tuple"*, admitted via `VocabularyRegistry.extend` |
| **Missing evidence** | The scoping determination itself: does evolution work need only a category extension, or genuinely new supreme law? **The answer determines whether this condition is in-corpus or out.** A registration extension *"does not touch Tier T1 at all"*; new supreme law requires the vacant Tier T1 ratifying authority and therefore becomes `RU-19` |
| **Closure action** | Scope the content against the open `GOVERNED_CATEGORIES` path and record which of the two it needs. This is the highest-leverage cheap determination in the register, because it decides its own tractability |
| **Validation requirement** | A recorded scoping determination; if a category extension suffices, the extension registers through `VocabularyRegistry.extend` and `INV-14` measures it |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` if in-corpus. **If the answer is "new supreme law", this condition transfers to Class F and becomes unclosable by work** — which is why scoping it is a prerequisite to knowing the size of the whole register |

---

### CLASS E — STRUCTURAL UNCONDITIONALITY

---

#### `RU-17` — Exactly one next authorized action · derived in §3

| Field | Content |
|---|---|
| **Current evidence** | `INV-6` requires `exactly one`, legislated seven times; `CEP-003:65` permits *"exactly one next authorized action **or a halt**."* The premise satisfied it — *"There is **exactly one** RUNNABLE root … Frontier is singular and deterministic"* (`UCOS-EXEC-001:111`). At HEAD the measured root count is **6 actionable + 2 decision-only** (`UCOS-OMEGA-INFINITY-CLOSURE-DEPENDENCY-GRAPH-DETERMINATION.md` §7). **The property that made the verdict conditional-rather-than-NOT-READY has been lost, not merely deferred** |
| **Missing evidence** | Either a dependency-derived ordering collapsing the roots to one, or an invoked and declared tie-break. Neither exists |
| **Closure action** | Apply the located machinery — *"canonical DAG + lexicographic tie-break; topological antichains"* (`S2-11:120`) — to establish a single NOW item, following the `EC-1`…`EC-6` precedent where *"EC-1 gates all others."* `CIOA:59` forbids declaring it manually; it must be dependency-derived. If the six survive as a true antichain, the tie-break is the only lawful way to name one, and that must be stated rather than left implicit |
| **Validation requirement** | Exactly one next authorized action nameable, bound to **one stage and one write area** (`CEP-003:138`), with the derivation reproducible from repository evidence |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` on the derived ordering. **This condition gates the availability of any unqualified verdict**, independent of whether the other nineteen close: `INV-6` failing is a failed criterion, and `CEP-001:185` routes a failed criterion to HALTED, exitable only upon remediation |

---

#### `RU-18` — Verdict-landscape reconciliation

| Field | Content |
|---|---|
| **Current evidence** | Eight coexisting readiness verdicts over eight scopes (§1.3), ranging from `100% READY … Blocking risks: ZERO` to `# NOT READY` with six blockers. **None declares itself superseded or superseding.** Registered as `G-11`: *"Supersession vocabulary legislated but unused \| 1 supersession header in ~145 root docs; 0 SUPERSEDED statuses in 1233 artifacts; 49 docs with no status marker."* Five of the readiness documents, including the HEAD-baseline one, are **untracked** |
| **Missing evidence** | A reconciliation naming, per scope, which verdict is operative and which are historical. Absent that, *"READY WITH CONDITIONS"* and *"NOT READY"* are both citable for the same programme at the same moment, and a reader may select either |
| **Closure action** | Apply the legislated supersession vocabulary: for each scope, record the operative verdict and mark the rest historical. Commit the untracked determinations or accept, under `TRACK-001` fail-closed, that they are not Repository Truth |
| **Validation requirement** | For any given scope, exactly one verdict is citable as operative, and every other carries a supersession or historical marker |
| **Certification requirement** | `CERTIFIED-PROVISIONAL` on the reconciliation record. **This condition is a precondition to answering the question the register exists to answer** — the transition cannot be evidenced as complete while its own start state is ambiguous |

---

### CLASS F — NOT CLOSABLE BY REPOSITORY WORK

---

#### `RU-19` — Constitutional ratifying authority

| Field | Content |
|---|---|
| **Current evidence** | `00-CMG/CMG-REGISTRY.json:255` — Tier `T1 Constitutional Authority`, `"occupancy": "VACANT"`, `"vacancy": "VAC-01"`, whose declared superior *"exists in the repository only as frozen non-normative source material under `00-SOURCE/CONSTITUTIONS/` (.docx). No ratified normative artifact occupies the tier."* Its `provisional_consequence`: every determination depending on T1 is provisional, *"including the standing of `CMG-000001` itself."* Measured this session: `cmg-gate.sh` exit 0, `readiness outcome : READY-PROVISIONAL`, `vacancies recorded : 1`, `gaps recorded : 9`, `open questions : 7`. `MP2-C-04` rests on three located instruments — `UCAF-RC-01`, `UCAF-RC-02`, `UCAF-RC-03` — classified `UCAF-F-002 STANDING-CONSTITUTIONAL-CONFLICT`. `EC-1`…`EC-6` are recorded OPEN, with `EC-1` an *"exogenous constituent act … not performable by this program"* and *"EC-1 gates all others."* `TC-4` already classified this as external |
| **Missing evidence** | An external constituent act. `UCAF-F-003`: competence to ratify and the ratifying act are distinct, and *"only the first is closable by measurement."* `OA-6`: *"Constitute a Tier T1 authority competent to ratify \| external constituent act \| **NOT ACTIONABLE IN-REPOSITORY**."* `CMG-OQ-01` remains OPEN |
| **Closure action** | **None available in-repository.** Promotion of a lower instrument is forbidden: `CMG-000001` XVII.4 forbids it and LXXXI.5 voids any reading that permits it. The discharge event is described and awaited, not performed |
| **Validation requirement** | Not applicable. There is no executable check for competence to ratify, and constructing one would assert the answer it purports to measure |
| **Certification requirement** | **None available.** `UCCEP-F-004` sets the ceiling: *"Maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`"* |

---

#### `RU-20` — The unconditionality claim itself

| Field | Content |
|---|---|
| **Current evidence** | The corpus has already adjudicated the analogous claim and recorded the proof. `00-MASTER/P0-FINAL-CLOSURE-002/UCOS-P0-FINAL-CLOSURE-DETERMINATION.md:8` — `**UNCONDITIONAL CERTIFICATION — PROVEN IMPOSSIBLE IN-CORPUS**`; §19 *"Why unconditional certification is prohibited"*, resting on `VAC-01`; `:148` *"from inside — **PROHIBITED**"*; `:158-160` *"Can P0 achieve UNCONDITIONAL CERTIFICATION inside Repository Truth?"* → `# PROVEN — NO` |
| **Missing evidence** | Nothing is missing. **This condition is not open; it is answered, and the answer is negative for its scope.** What is missing is only the corresponding determination for *readiness*, which no instrument has made — the precedent is for certification |
| **Closure action** | None. The condition is discharged by resolving `RU-19`, or it stands |
| **Validation requirement** | Not applicable |
| **Certification requirement** | Not applicable. **Recorded so that no future determination re-derives it as though it were open** — which is the failure mode `G-11` makes likely |

---

## SECTION 5 — DETERMINATION

Stated as a derivation from the located tests in §2, not as a verdict.

### 5.1 The condition count and its split

| Class | Conditions | Closable by work or decision in-corpus |
|---|---|---|
| A — baseline and evidence | `RU-01`…`RU-05` | Yes (5) |
| B — admission blockers | `RU-06`…`RU-10` | Yes (5) |
| C — Wave-1 closure | `RU-11`…`RU-14` | Yes (4) |
| D — pending decisions | `RU-15`, `RU-16` | Yes (2) — but `RU-16` may transfer to F on scoping |
| E — structural | `RU-17`, `RU-18` | Yes (2) |
| F — external | `RU-19`, `RU-20` | **No (2)** |

**18 closable · 2 not closable by any repository work.**

### 5.2 What this implies, under the located tests

Applying `ENG-005 D10` — *unqualified READY ⟺ no gap ∧ no unresolved dependency ∧ no destabilizing factor* — to the measured state:

- **no gap** fails on `RU-06` (398 unresolved subjects), `RU-14` (228 unregistered), `RU-11` (unmeasured concept homing), `RU-12` (`traceability-gaps` unhealthy).
- **no unresolved dependency** fails on `RU-09` (eight OPEN owner decisions), `RU-10` (no plan operand), `RU-19` (vacant tier).
- **no destabilizing factor** fails on `RU-01` (78 dirty, guard exit 2), `RU-02` (5 red gates, 23 failing tests), `RU-03` (gates and tests disagree), `RU-07` (≥24 undeclared mutating gate paths).

All three conjuncts fail, each on multiple independent grounds. And `RU-17` fails `INV-6` on its face.

**The determination that follows, and it is narrower than a verdict:**

> `READY UNCONDITIONAL` in the sense of `ENG-005 D10` — *no conditions outstanding* — is **not reachable by repository work alone**, because `RU-19` requires an act the corpus records as *"NOT ACTIONABLE IN-REPOSITORY"* and `RU-20` records the analogous claim as already `PROVEN — NO` from inside.
>
> The state reachable by closing all 18 in-corpus conditions is `READY WITH CONDITIONS` **where every remaining condition is external, enumerated, and declared** — the shape `TC-4` already used for this exact dependency, and the shape `EC-1`…`EC-6` uses at constitutional scale.

This is not a counsel of despair and it is not a hedge. It is the difference between eighteen conditions that can be worked and two that must be awaited — and the corpus's own instruction is that conflating them misrepresents both: *"Reserved decisions are … owner decisions awaiting a person, not repository work awaiting a process. Sequencing them as backlog would misrepresent them."*

### 5.3 Two corrections to the premise as posed

1. **Scope.** The committed `READY WITH CONDITIONS` covers the FOUNDATION → SYSTEMATIC IMPLEMENTATION transition at `5874ede`. It is not a verdict on pre-implementation admission at `bae59755`. `CM-2` and `XXII.1` both forbid reading the one as the other.
2. **Decay.** The premise's conditionality rested on two hygiene items and *"a single deterministic RUNNABLE root."* Five weeks later `TC-1` is undischarged (78 dirty), `TC-2`'s registry still carries a 2026-07 nomination, and the root count has gone from **1** to **6**. **The distance to unconditional has grown since the premise was issued.** Any plan that treats the premise's two items as the remaining gap is aiming at a state the repository has left.

---

## SECTION 6 — NON-CONDITIONS

Recorded so they are not mistaken for closure evidence.

| Apparent evidence | Why it is not closure |
|---|---|
| `homing` exits **0** | It is a report, not an enforcing gate. Exit 0 coexists with 27.5046% coverage and 398 unresolved subjects. The enforcing form is `homing --gate` |
| `ukb.py enforce --pre` exits **0** | Its contract is that nothing unregistered *silently enters* — not that nothing is unregistered. 228 remain |
| `cmg-gate.sh` exits **0** | Its own output is `READY-PROVISIONAL` with `vacancies recorded : 1`. The green is conditional by construction |
| `uaue --gate` exits **0** | Its replay counterpart exits 1. A gate passing while its replay drifts means the declaration and its projection disagree |
| Coverage is 97% | Above the 90 floor. **The pytest stage fails on 23 tests, not on coverage.** Citing a coverage breach aims at the wrong defect |
| `100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md` — *"100% READY, Blocking risks: ZERO"* | Its own §8.2 shows the 54.3% → 100% movement was *"8 determination documents produced"*, with no blocker discharged. It is untracked, and the HEAD-baseline determination post-dates it with `# NOT READY` |
| `UAKOS-CLOSURE-002: CLOSED \| gaps=0` (session hook) | Uninterpretable while `CLOSURE_SKIP_CORPUS` exists in the standing hook (`RU-11`). A gate that can be told not to look cannot evidence what it did not look at |
| `MIP-W1-P001` figures — 1,204 artifacts, 91 concepts, 969 evidence artefacts, 56.9% | Anchored at `c6c20fb5`, 4,895 tracked files, clean tree. Today: `bae59755`, **6,188** tracked files, 78 dirty. All four are stale as current measurements |

---

## SECTION 7 — INFINITE SCOPE VALIDATION

| Prohibition | This register |
|---|---|
| Fixed condition categories | Classes A–F are disclosed with an admission path: a 21st condition enters by citing a located instrument or a command output, with no structural change. The class set is closed and its closure is declared here |
| Fixed calendars | **No date, duration, velocity or effort appears in any condition.** Where the corpus supplies effort estimates (*hours · days · weeks*) they are quoted as located text, never adopted as this register's unit |
| Fixed units | The only quantities are measured counts, each with the command that produced it |
| Fixed technologies, languages, APIs | Mechanisms are cited by located path as **current manifestations**. Substituting one changes a citation, not a condition |
| Fixed intelligence models | No condition presumes one |
| Fixed realities, locations | None named |
| Examples are not boundaries | Every count — 35 governed categories, 46 gate targets, 26 gates, 48 checks, 549 subjects, 1,461 eligible artifacts, 16 preserved sites — is a measurement at a moment, with an admission path, not a definition |

**Self-application.** This register is subject to its own discipline. It issues no verdict (§0.1); its two structural conditions `RU-17` and `RU-18` apply to it as much as to anything else, since it is now one more determination in an unreconciled verdict landscape; and every measurement in it is reproducible by the command given, which makes it falsifiable rather than authoritative.

---

## SECTION 8 — FALSIFIABILITY

- Exhibit a located instrument defining necessary-and-sufficient conditions for `READY` → §2.2 is wrong and the target must be re-derived.
- Exhibit a readiness-promotion rule → §2.4 is wrong and conditions may discharge collectively rather than independently.
- Name exactly one next authorized action, dependency-derived, binding to one stage and one write area → `RU-17` is discharged and §3 falls.
- Exhibit an in-repository act that occupies Tier T1 without promoting a lower instrument → `RU-19` moves from Class F to Class A and §5.2's determination is void.
- Show that `5874ede`'s verdict remains operative at `bae59755` for the admission scope → §1.4's two-transition finding collapses to one.

---

## SECTION 9 — STATUS

| Field | Value |
|---|---|
| CONDITIONS DETERMINED | **20** — `RU-01`…`RU-20` |
| CLOSABLE IN-CORPUS | **18** (one of which, `RU-16`, may transfer out on scoping) |
| NOT CLOSABLE BY WORK | **2** — `RU-19` ratifying authority · `RU-20` the unconditionality claim, already `PROVEN — NO` for its analogue |
| NEWLY DERIVED HERE | `RU-03` gate/test disagreement · `RU-17` single-next-action loss · `RU-18` verdict-landscape reconciliation. None appears in any prior register |
| PREMISE | Located at `UCOS-EXEC-001:188`, TRACKED, baseline `5874ede` (ancestor of HEAD), scope FOUNDATION → SYSTEMATIC IMPLEMENTATION, conditions `TC-1`…`TC-4` |
| PREMISE DECAY | `TC-1` undischarged (78 dirty) · `TC-2` registry unrefreshed · root count **1 → 6** |
| TRANSITIONS REQUIRED | **2**, not 1 — `T-A` at the premise's scope, `T-B` at the admission scope |
| CERTIFICATION CEILING | `CERTIFIED-PROVISIONAL` on every condition (`UCCEP-F-004`) |
| READINESS ASSERTED | **NONE** |
| STATUS MODIFIED | **NONE** |
| VERDICT ISSUED | **NONE** |
| VERDICT OF THIS ARTIFACT | `CONDITIONS-DETERMINED · NO READINESS ASSERTED · NO STATUS MODIFIED · NOTHING IMPLEMENTED` |

---

## SECTION 10 — SELF-DISCLOSURE

Three measured consequences of this determination, disclosed rather than omitted. The third is an ungoverned mutation caused by this determination's own evidence gathering, and it is the most consequential finding in the document.

### 10.1 `ISD-L-07`

This file is a root-depth-zero `.md` inside the scanned roots. It carries none of the nine permanence phrases and no line matching the status-field pattern, verified by re-running the gate after writing. The gate's refusal remains the two pre-existing sites. Note the standing hazard, learned earlier in this session: **citing that law by title reintroduces the phrase it detects.** It is cited here by identifier only.

### 10.2 `UGA-INV-01` / `UGA-INV-10`

This file is a root-level determination carrying no minted identifier. UGA's population is `git ls-files --cached`, so the anonymous-object count is unaffected while the file is untracked and **rises on commit**.

### 10.3 ⚠ Ungoverned mutation event — `RU-07` realized live

**What happened.** While gathering evidence for `RU-01` (the `register.sh --guard` state), the guard was invoked as a read-only measurement. It is not read-only. At 19:02 it executed its **full registration transaction**:

| Effect | Measured |
|---|---|
| New page documents emitted to `00-BOOK/PORTAL/` | **238** files |
| Identifiers minted | ~36 (`EXDOC` class), inferred from the anonymous-object drop |
| Ledgers rewritten | `id-ledger.json` (+12,290/−8,058) · `change-ledger.json` (+22,898/−13,068) · `relationships.json` (+21,366/−17,670) · `artifacts.json` (+9,368/−3) · `volumes.json` · `control-tower.json` |
| Registry documents rewritten | 5 under `00-BOOK/REGISTRIES/` + `PROGRAM-CONTROL-TOWER.md` + 12 existing PORTAL pages |
| Working tree | **78 → 329** dirty paths |
| Anonymous objects | **43 → 7** (the 7 residual are all `.py`, matching the recorded `ENGINE +2 / TESTOBJ +5` split) |

**This is the recorded harm class, not a new one.** `GATE-PURITY-DETERMINATION` documents the precedent in the same mechanism: *"A `register.sh --guard` run over a corpus with 140 unregistered artifacts **minted all 140 permanent identities inside a verification path**"* — the reason `verify.sh` now calls `register.sh --observe` and `CORPUS_REGISTRATION` became a governed class. `RU-07` exists to prevent exactly this, and the event is its live realization: **a command with no declared mode, invoked to measure, mutated instead.**

**One possible irreversible effect, stated with its uncertainty.** `00-BOOK/DATA/generated-artifact-registry.json` is now **clean**. The `H-06` Phase-0 record describes that file as carrying an uncommitted `+864/−0` delta and cites it as one of the two deltas failing condition `0.6`. I did not capture a per-file dirty list at session start — only a count — so **I cannot establish whether that uncommitted work was present today and has been lost, or was already absent at a different baseline.** `git stash show --name-only stash@{0}` does not contain the file. This is the `F-A` signature and it may be a false alarm; it is recorded because an unverified loss must not be resolved by assumption in either direction.

**Why the improved numbers are not closure.** The event moved two conditions' measurements favourably — anonymous objects 43 → 7, and the 228 unregistered eligible artifacts are now registered. **Neither `RU-02` nor `RU-14` is discharged by it**, on the corpus's own terms:

- `RU-14`'s closure action requires *"a dedicated `CEP-002` Article 28 decision enumerating the population"*, with an explicit irreversibility disclosure. `ADR-0017` declined a standing blanket mint: *"A future anonymous object requires its own decision under this same Article, not a standing blanket authorization."* **No such decision exists for these ~36 mints or the 228 registrations.** The identifiers are minted; the authority for minting them is not.
- `RU-01`'s condition requires a clean tree. The event moved the tree **further from clean**, by 251 paths.
- `CM-4` bars declaring completion *"while any blocking finding, orphan, drift, or unresolved deferral remains"*, and `CM-5` requires completion be *"provable by reference to evidence and traceability."* A mutation whose authorizing decision does not exist cannot supply that proof.

**Determination on the event.** It is disclosed, not remediated. Remediation would mean reverting tracked ledger files and deleting 238 emitted documents — destructive operations on uncommitted work, in a tree that already carried 78 dirty paths of other people's uncommitted state. **No remediation is performed and none is authorized by this document.** The event is registered as evidence under `RU-07` and as a new measurement baseline that supersedes §4's counts.

**What this adds to the determination.** `RU-07` was, before 19:02, supported by historical incidents. It is now supported by one that occurred inside a read-only determination that was explicitly trying not to cause it, using a command the corpus had already documented as dangerous. That is stronger evidence for the condition than any prior citation, and it is the clearest available answer to why `READY UNCONDITIONAL` cannot be asserted while `RU-07` stands: **in this repository, measuring can still mutate.**

---

## STOP

Conditions determined. No implementation performed. No status modified. No readiness claimed. No verdict issued, upgraded or retired. No code, configuration, registry, declaration, status field or certification modified. No requirement, ADR, identifier, authority, form or law created. The single mutation is the creation of this file, whose two measured consequences are disclosed in §10.

**Awaiting explicit authorization.**
