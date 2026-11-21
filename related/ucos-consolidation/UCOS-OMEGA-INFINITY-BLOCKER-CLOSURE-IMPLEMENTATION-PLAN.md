# UCOS Ω∞ — BLOCKER CLOSURE IMPLEMENTATION PLAN

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE-IMPLEMENTATION-PLAN.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, requirement, ADR, phase, roadmap or certification. Authorizes no implementation. Assigns no ownership. Resolves no constitutional decision. |
| Mode | READ-ONLY PLANNING ARTIFACT · **NO IMPLEMENTATION PERFORMED** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Baseline working tree | 336 `git status --porcelain` lines · **38 tracked-modified** · 1 untracked artifact (the predecessor determination). Pre-existing; not produced by this plan. |
| Predecessor | `UCOS-OMEGA-INFINITY-UNIVERSAL-FOUNDATION-TRANSFORMATION-EXECUTION-READINESS-DETERMINATION.md` — verdict **NOT READY**, 6 blocking conditions BC-1…BC-6 |
| Scope | Closure plan for BC-1…BC-6, one plan per blocker, each independent |
| Target | `IMPLEMENTATION READINESS: NOT READY` → `READY UNCONDITIONAL`, **evidence-backed closure only** |
| Implementation authorization | **NOT GRANTED.** §10 records the stop condition. |
| Closure claimed | **NONE.** No blocker is closed, partially closed, or in progress. |

---

## 1. Objective and Method

### 1.1 Objective

Produce an executable closure plan for the six blocking conditions that hold `IMPLEMENTATION READINESS` at **NOT READY**, such that each blocker has a root cause, a resolution approach, a dependency set, an identified owner, an evidence requirement, a validation method, and an acceptance criterion — **before any mutation occurs**.

### 1.2 Method actually followed, in the directive's required order

| # | Required pre-mutation step | Performed | Result |
|---|---|---|---|
| 1 | Read current determination artifacts | ✅ | 7 baseline determinations + the readiness determination (§2.1) |
| 2 | Read current closure register | ✅ | `100-PERCENT-CLOSURE-MASTER-REGISTER` — 41/135 closed (30.4%), 2 of 10 final gate conditions met, `verify.sh --full` exits 1 |
| 3 | Read current dependency graph | ✅ | Readiness determination §19; B-5 §28; `CLOSURE-DEPENDENCY-GRAPH-DETERMINATION` |
| 4 | Identify exact blocker ownership | ✅ | §3 per blocker. **Owners are identified from declared sources; none is assigned by this plan** |
| 5 | Create implementation plan before changing anything | ✅ | **This artifact. Zero mutations performed.** |

### 1.3 Measurements taken during planning

All measurements were **pure reads** or **in-memory evaluation**. No file was written, no registry touched, no gate executed, no identifier minted.

| # | Measurement | Method | Result |
|---|---|---|---|
| **P-1** | R-09 predicate absence | Read `RULE_PREDICATES` at `platform/repository_intelligence/mutation_classification.py:403-412` | **Implements R-01…R-08 only. R-09 absent.** Confirms M-C root cause |
| **P-2** | R-09 declaration | Parsed `00-BOOK/DATA/mutation-governance-boundary.json` `classification_rules.rules` | **9 rules declared: R-01…R-09.** R-09 → class `GOVERNED_ANALYSIS`, precedence 9 |
| **P-3** | R-09 membership criteria | Parsed `mutation_classes[8]` | **Six criteria, all mechanically decidable** (§3.1.3) |
| **P-4** | R-09 governance model | Same | `governed_by` is **owner-parameterised — read from the artifact's own `Authority` field** |
| **P-5** | Determinism harness scope | Read `engine/determinism/reproduce.py` (~line 270-300) | **Both builds occur in one process**, sharing `env`, `adapter`, `signer`, inside a single `trace()` block. Confirms CH-2 |
| **P-6** | Ownership catalogue population | Parsed `platform/universal_ownership/catalog/ucos-ownership-declarations.json` | **`assignments` = `{}` — literally empty.** Confirms CH-4 independently |
| **P-7** | `verify.sh` stage count | Counted `run_stage` invocations | **14 declared stages + coverage report = 15 stage slots** (§3.6.3) |
| **P-8** | Working-tree state | `git status --porcelain` | **38 tracked-modified**, enumerated in §3.6.4 |
| **P-9** | `verify.sh` diff magnitude | `git diff --stat verify.sh` | **+46 / −6.** *Variance from the inherited figure (+45/−0) is disclosed in §9.2, not reconciled* |
| **P-10** | In-flight R-09 test coverage | Grep `platform/tests/test_mutation_classification.py` | **No occurrence of `R-09` or `GOVERNED_ANALYSIS`.** The modified test does not cover the missing predicate |

### 1.4 What this plan deliberately does not do

- It does **not** modify code, configuration, registry, schema, certification or any tracked file.
- It does **not** assign ownership. §3.4 produces an unresolved-ownership process and partition; it names no owner for any unowned subject.
- It does **not** resolve any constitutional decision. §3.5 produces decision packages; it selects no option.
- It does **not** claim partial closure. Every blocker is **OPEN**.
- It does **not** create a new capability. §8 records the gap-confirmation test each proposed change must pass, and the finding that **all six blockers resolve to REUSE or EXTEND with CREATE = 0**.

---

## 2. Baseline Evidence

### 2.1 Artifacts read

| # | Artifact | Inherited content used |
|---|---|---|
| R-1 | `…UNIVERSAL-FOUNDATION-TRANSFORMATION-EXECUTION-READINESS-DETERMINATION.md` | **NOT READY**; BC-1…BC-6; 67 transformations (10 EXECUTABLE / 47 CONDITIONAL / 4 BLOCKED / 6 PROHIBITED); 7 invariants with disclosed variance; 8 waves; EP-1…EP-7 |
| R-2 | `…FINITE-TO-INFINITE-TRANSFORMATION-MASTER-DETERMINATION.md` | **NOT READY**; 78 constraints; 20 runtime-authority violations; 63 VR; 23 CR; 65 risks; SQ-1…SQ-12; **CREATE = 0** |
| R-3 | `…UNIVERSAL-INFINITE-EXISTENCE-…-COMPLETENESS-DETERMINATION.md` | **PARTIALLY PROVEN**; M-A/M-B/M-C; 2 of 13 expansions DISPROVEN |
| R-4 | `…UNIVERSAL-TRUTH-AUTHORITY-RUNTIME-INDEPENDENCE-DETERMINATION.md` | **PARTIALLY PROVEN**; two mutable authorities; 13 truth objects 4/2/7; TA-26 path-reproducibility ≠ initialization-independence |
| R-5 | `…UNIVERSAL-IDENTITY-CAPABILITY-EVOLUTION-DETERMINATION.md` | Identity capability **DISPROVED** clause-by-clause; 22 gaps; **zero new engines necessary** |
| R-6 | `…IDENTITY-DETERMINISTIC-VALIDATION-BOUNDARY-DETERMINATION.md` | **DEPENDENT on execution history for 43 of 72 kinds**; root cause DV-11; **one** true missing capability |
| R-7 | `…100-PERCENT-CLOSURE-MASTER-REGISTER.md` | **41/135 = 30.4% closed**; 2 of 10 gate conditions met; `verify.sh --full` exits 1 on 4 of 15 stages; `IMPLEMENTATION-NOT-AUTHORIZED` |
| R-8 | `…IMPLEMENTATION-SEQUENCE-MASTER-PLAN.md` | 11 waves + 1 vest class; **6 actionable roots**; **NO WAVE AUTHORIZED**; ceiling `CERTIFIED-PROVISIONAL`; condition `0.6` failing |
| R-9 | `00-BOOK/DATA/mutation-governance-boundary.json` | 9 classes, 9 rules, R-09 → `GOVERNED_ANALYSIS`, six criteria, owner-parameterised governance |
| R-10 | `platform/repository_intelligence/mutation_classification.py` | `RULE_PREDICATES` R-01…R-08; two-sided `validate_rule_coverage`; `classify()` returns ERROR on coverage failure |

### 2.2 Evidence limits carried into this plan

- Discovery was **not repeated**. Only P-1…P-10 were taken, and each is a read.
- `./verify.sh --full` was **not executed**. Reason: `UGA-001` declares a `run` mode that **mints and emits**, only 4 of 29 gates declare their mutation mode, and `verify.sh` itself is one of the 38 modified files. Executing it during planning could mint identifiers or write registries — precisely the mutation class this plan is forbidden to perform. The inherited failure count (4 of 15 stages) is therefore carried on report and is flagged in §3.6 as **requiring first-party measurement under BC-6 by its owner**.
- The 38 tracked modifications are enumerated but **not attributed**. Attribution is an owner act, not a planning act (§3.6.4).

---

## 3. Blocker Closure Plans

Each blocker is planned independently, as directed. The order below is presentational; §5 states the actual dependency order.

---

### 3.1 BC-1 — CLASSIFICATION OUTAGE

#### 3.1.1 Blocker

`classify()` returns `status='ERROR'` for **every** subject in the repository. No change of any kind can be classified, therefore no change can be governed. Inherited as CH-3 / M-C; independently re-confirmed by P-1 and P-2.

#### 3.1.2 Root cause

**A two-sided coverage contract with one side unimplemented.**

`validate_rule_coverage()` refuses in both directions by design — a declared rule with no predicate, and a predicate no rule declares, are both errors. The register declares **nine** rules (R-01…R-09). The module implements **eight** predicates (R-01…R-08). `classify()` calls `validate_rule_coverage()` before evaluating any rule and returns `ERROR` when it is non-empty (`mutation_classification.py:438-440`).

The failure is therefore **total rather than partial by design**: the classifier refuses to classify *anything* while the register and the module disagree, rather than silently classifying the eight rules it can. That is correct fail-closed behaviour and it is why the outage is repository-wide from a single omission.

**The omitted rule is R-09 → `GOVERNED_ANALYSIS`**, added to the register as the *"Phase 1B Violation 4 resolution"* to give determination, analysis and assessment artifacts a class distinct from `AUTHORED_DOCUMENT`. Its declared precedence is 9, and the register states *"R-09 evaluates before R-08 so analysis artifacts are classified as GOVERNED_ANALYSIS rather than the more general AUTHORED_DOCUMENT."*

**Second-order finding, recorded because it changes the interpretation of the whole programme:** the artifact class that R-09 exists to govern is exactly the class every determination in this programme belongs to. The governance void that `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` identifies for determination artifacts and the R-09 omission are **the same defect seen from two directions**.

#### 3.1.3 Resolution approach

**EXTEND — implement the declared predicate. No new capability.**

Implement `_r09_governed_analysis(subject, repo, boundary) -> bool` and register it in `RULE_PREDICATES`, evaluating the six declared membership criteria. All six are **mechanically decidable from repository state with no inference, no ownership assignment and no authority act**:

| # | Declared criterion | Decidable from | Fabrication risk |
|---|---|---|---|
| 1 | markdown — path ends `.md` | Path string | None |
| 2 | authored — absent from `producer_homes` | Declared register | None |
| 3 | repository-controlled — tracked by version control | VCS state | None |
| 4 | non-generated — absent from `generated-artifact-registry.json` `canonical_path` | Declared register | None |
| 5 | analysis-artifact — filename carries `determination\|analysis\|assessment\|execution\|matrix\|readiness\|admission\|blocker\|gap` | Path string | None |
| 6 | self-declared-authority — carries an `Authority` field in the opening metadata block | The artifact's own content | **None — the authority is *read*, never assigned** |

Criterion 6 is the reason this resolution does **not** violate the prohibition on automatic ownership assignment: `governed_by` is **owner-parameterised**, read from the artifact's self-declared `Authority` field. The predicate **reports** a declared authority; it does not confer one. An artifact with no `Authority` field **fails criterion 6 and falls through to R-08** — the declared fall-through, not an invented default.

**Explicitly out of scope for BC-1:** adding a tenth rule; changing any of R-01…R-08; changing precedence; changing the two-sided coverage contract; making `UNRESOLVED` or `ERROR` permissive.

#### 3.1.4 Dependencies

| Dependency | State | Note |
|---|---|---|
| None on any other blocker | — | **BC-1 is a root.** It is one of the two items the readiness determination classifies EXECUTABLE with no predecessor |
| BC-6 (baseline integrity) | **Advisory, not blocking** | `platform/tests/test_mutation_classification.py` is one of the 38 modified files (+3/−3). Its owner should land or revert that change first, so BC-1 evidence is not confounded |
| SQ-2 | **BC-1 gates everything else** | Every other blocker's remediation is itself a mutation, and until BC-1 closes, that mutation is unclassifiable |

#### 3.1.5 Owner

| Role | Owner | Basis |
|---|---|---|
| Subject owner | **Repository Intelligence** | The register's `governed_by` chain for R-09: *"the authority the analysis declares of itself → **Repository Intelligence** → verify.sh (observation only)"* |
| Change class | `SOURCE` (R-07) for the module; the register itself is **not** modified | The predicate is added to `.py`; the JSON register already declares R-09 |
| Authority required | **Engineering execution only** | A declared rule is made to function. No law, register, precedence or class is created or amended |

**This owner is read from the register, not assigned by this plan.**

#### 3.1.6 Evidence required

| Class | Requirement |
|---|---|
| **Tests** | Positive: a known `GOVERNED_ANALYSIS` subject classifies as `GOVERNED_ANALYSIS`. Coverage: `validate_rule_coverage(boundary)` returns `()`. Totality: a sample spanning **all nine** classes classifies without `ERROR` |
| **Negative tests** | Each of the six criteria independently falsified → subject must **not** classify as `GOVERNED_ANALYSIS`. Missing `Authority` field → falls through to R-08, never to a default. A markdown analysis artifact that is **untracked** → excluded by criterion 3 |
| **Precedence test** | A subject satisfying **both** R-08 and R-09 classifies as `GOVERNED_ANALYSIS`, proving R-09 evaluates first as declared |
| **Purity test** | `classify()` performs **no mutation**: no file written, no identifier minted, no registry touched. Asserted by the mutation-tested-purity pattern already proven at `UEG-000001` (`test_verify_does_not_ensure_the_environment_it_is_verifying:826`) |
| **Unknown-input safety** | An unclassifiable subject returns `UNRESOLVED` fail-closed — **never** a permissive default |
| **Replay evidence** | Two runs over the same corpus produce byte-identical classification output, compared by digest |
| **Regression protection** | A test asserting `set(RULE_PREDICATES) == {declared rule ids}` so a future declared-but-unimplemented rule **fails at test time**, not at classify time. This is the recurrence guard for the defect class itself |

#### 3.1.7 Validation method

Execute the disposition chain end to end over a real subject set:

```
change/event/object → Classification → Evidence → Disposition
                                                   ∈ {REUSE, EXTEND, COMPOSE, HOLD, TRUE MISSING, CREATE}
```

Validated **cross-process** once BC-2 lands (fresh interpreter and bootstrapped interpreter must agree). Until BC-2 exists, BC-1 is validated **in-process only**, and that limitation is declared rather than hidden.

Named requirement: **VR-40** — `validate_rule_coverage` returns empty; `classify()` returns a class for a sample spanning all nine classes. Recurrence guard: **VR-41** in spirit, applied to the coverage contract.

#### 3.1.8 Acceptance criteria

| # | Criterion | Pass condition |
|---|---|---|
| A1-1 | Coverage contract satisfied | `validate_rule_coverage(boundary) == ()` |
| A1-2 | Totality | Zero `ERROR` results across a sample spanning all nine classes |
| A1-3 | Determinism | Identical verdict on repeated execution; digest-compared |
| A1-4 | Purity | Zero mutations during classification, mutation-tested |
| A1-5 | Fail-safe | Unknown input → `UNRESOLVED`, never permissive |
| A1-6 | No fabrication | No `Authority` invented; missing `Authority` falls through to R-08 |
| A1-7 | Regression guard | A declared-but-unimplemented rule fails at test time |
| A1-8 | Disclosure | Any mutation found to have been certified while unclassified is **recorded, not silently absorbed** (R-42) |

**A1-8 is a disclosure obligation, not a pass/fail gate.** Closing BC-1 is expected to reveal history that was certified without classification.

---

### 3.2 BC-2 — INITIALIZATION-INDEPENDENT DETECTION

#### 3.2.1 Blocker

Runtime state can determine truth, and **no instrument can detect it**. Zero of 29 gates vary initialization order. Inherited as CH-2 + M-B; harness scope independently re-confirmed by P-5.

#### 3.2.2 Root cause

**Two distinct defects that the repository currently conflates.**

1. **The condition.** Identity kind space and vocabularies live in process-global mutable module state (`registry/universal/identity.py:156,159` and `uckp/vocabulary.py:542`), populated only by a *call* — import is insufficient. Same commit, zero file changes: `is_well_formed("UCOS-CLSS-8966ca9e8d02")` is `False` before `bootstrap()` and `True` after. 43 of 72 kinds and 195 CEU identities are affected.

2. **The blindness.** `reproduce.py` executes both builds **inside one process**, sharing `env`, `adapter` and `signer` (P-5). It therefore measures **path reproducibility** — which the repository has genuinely proven — and has never measured **initialization independence**. `TA-26` records exactly this distinction, and collapsing the two is the evidential error CH-2 consists of.

**BC-2 is the second defect only.** The condition is closed by T-6.1/T-26.1, which are separate transformations; BC-2 closes the *inability to see it*.

#### 3.2.3 Resolution approach

**EXTEND — add a cross-process comparator alongside the existing harness. Do not replace it.**

Three isolated child processes over the same canonical input:

| Scenario | Environment |
|---|---|
| **Process A** | Fresh interpreter · **no** bootstrap call |
| **Process B** | Fresh interpreter · bootstrap called |
| **Process C** | Fresh interpreter · **different initialization order** (a different admissible call sequence reaching the same declared state) |

Each emits a structured verdict record plus a digest. The comparator asserts **A = B = C** for the same canonical input.

Four detection targets, each with a distinct signature:

| Target | Signature |
|---|---|
| Hidden runtime state | A ≠ B |
| Mutable singleton authority | A ≠ B **and** the divergence localises to a module global |
| Bootstrap dependency | B differs from A **only** after an explicit bootstrap call |
| Import/call-order dependency | B ≠ C — same declared state, different arrival order |

**Preservation constraints.** The existing cross-process path-reproducibility gates must keep passing unchanged; `S-12` byte-identical artifact reconstruction from a bare fresh clone must be preserved; and the new comparator must be a **declared `gate`-mode instrument that mutates nothing**.

#### 3.2.4 Dependencies

| Dependency | State |
|---|---|
| None | **BC-2 is the second root.** No predecessor |
| BC-1 | Advisory — BC-2's own change is unclassifiable until BC-1 closes (SQ-2) |
| **BC-2 gates T-6.1** | SQ-1 / **R-01**: the existing reconstruction test's fixture calls `bootstrap()`, so it cannot detect failure of the durability fix. BC-2 must exist before durability work is verifiable |
| **BC-2 gates T-13.3** | SQ-7 / **R-24 CRITICAL** |

#### 3.2.5 Owner

| Role | Owner | Basis |
|---|---|---|
| Subject owner | **Determinism / verification-intelligence owner** | `engine/determinism/` and `engine/verification_intelligence/` are the affected declared homes |
| Change class | `SOURCE` (R-07), plus a gate declaration | Adds a stage; must declare its mutation mode |
| Authority required | **Engineering execution**, plus the gate-mode field decision if a new stage is registered | The mode field is a declared secondary decision (`H-06`/`CR-09`), noted in §3.5.3 |

#### 3.2.6 Evidence required

| Class | Requirement |
|---|---|
| **Execution logs** | Per-process stdout/stderr with the initialization sequence recorded explicitly |
| **Hashes** | A canonical digest of each process's verdict set — the comparison primitive, not prose |
| **Comparison reports** | A/B, A/C and B/C matrices, listing every divergence with the subject and the localised authority |
| **Positive control** | A subject **known** to be initialization-dependent (`UCOS-CLSS-8966ca9e8d02`) must be **detected**. A comparator that reports clean on a known-dirty subject is worthless |
| **Negative control** | A subject known deterministic (UCKP URN plane, UMK kernel plane, or one of the 29 core kinds) must report clean |
| **Coverage statement** | Which of the 72 admissible kinds were compared. **Partial coverage must be declared, never implied as total** |
| **Isolation proof** | Each process is a genuine child process — no shared interpreter, env, adapter or signer |

#### 3.2.7 Validation method

**VR-01** — the same subject yields the same verdict in a fresh interpreter and a bootstrapped one, for all 72 admissible kinds. Executed by the new comparator, with the positive control required to fail-detect and the negative control required to pass-clean.

#### 3.2.8 Acceptance criteria

| # | Criterion | Pass condition |
|---|---|---|
| A2-1 | Genuine multi-process isolation | Three distinct child processes; no shared state proven |
| A2-2 | Detection works | The known initialization-dependent subject **is detected** |
| A2-3 | No false positives | Known-deterministic planes report clean |
| A2-4 | Order sensitivity covered | B ≠ C is detectable, not only A ≠ B |
| A2-5 | Coverage declared | The compared subset of the 72 kinds is stated explicitly |
| A2-6 | Purity | The comparator mutates nothing; declared `gate` mode; mutation-tested |
| A2-7 | Preservation | Existing path-reproducibility gates and `S-12` reconstruction unaffected |
| A2-8 | Expected regression disclosed | **Green gates will turn red (R-41). This is the intended effect and must be recorded as such before execution, not explained afterwards** |

---

### 3.3 BC-3 — CERTIFICATION EVIDENCE CLOSURE

#### 3.3.1 Blocker

Certification rests on declaration. 16 unboundedness axes are marked CERTIFIED UNBOUNDED on **prose citation alone** — no axis cites executable code, a test, a digest or a reproducible instrument — and Axes 13 and 14 are **directly contradicted by measurement**. ~15 root-level certifications assert completeness without evidence binding. No machine certificate confers constitutional finality by its own declaration.

#### 3.3.2 Root cause

**The repository can assert and cannot instrument.** Certification mechanics are sound — content-addressed, digest-anchored, deterministically ordered, injectable rules and frames (`S-10`). What is absent is the **binding between a certified claim and a reproducible measurement**. A certificate records that a claim was made; nothing records that it was measured.

Compounding this: `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"`, so no machine certificate confers finality; and `UCCEP-F-004` caps the maximum attainable verdict anywhere at `CERTIFIED-PROVISIONAL` with Tier T1 **vacant** (`VAC-01`).

#### 3.3.3 Resolution approach

**EXTEND — apply an existing instrument to surfaces it does not currently cover.**

Convert every certified claim into a five-part record:

```
claim  +  measurement  +  evidence  +  verification  +  certification
```

Mandatory fields per certified item: **evidence source · validation result · timestamp/context · verifier · reproducibility proof.**

The instrument already exists. `check_open_world` (`S-14`) fails closed on bound tokens, closed registries, absent re-entry and claimed terminal states, and is present in four engines. BC-3 points it — and the probe idiom `is_extensible` proves openness with — at the 16 axes.

**Two constraints inherited and preserved:**

- **Timestamp/context must respect the temporal contract.** The baseline authority is temporally unaware and *certifies dates its own contract refuses* (T-02). A `timestamp` field satisfying BC-3 by asserting an unqualified date would **create** the R-18 defect while closing BC-3. Either the coordinate is qualified, or a declared exemption is recorded. **This is flagged as a secondary decision, not resolved here.**
- **No prose-only certification may remain.** Where a claim cannot be instrumented, the correct outcome is **withdrawal of the claim**, not a weaker instrument.

#### 3.3.4 Dependencies

| Dependency | State |
|---|---|
| **BC-2** | Required. Certification evidence must be reproducible **cross-process**; `CR-01` states the new evidence must **replace**, not supplement, the current single-process determinism evidence |
| **BC-1** | Required. A certification act is a mutation and must be classifiable |
| Temporal qualification decision | **Secondary decision, unresolved** (§3.5.3) |
| **BC-3 gates every later success claim** | SQ-9 / EP-7 / **CR-21** |

#### 3.3.5 Owner

| Role | Owner | Basis |
|---|---|---|
| Subject owner | **Certification / assurance owner** (`platform/universal_certification/`, `universal_assurance/`) plus **each axis's declaring owner** | The 16 axes live in `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md`; its owner must accept invalidation |
| Change class | `SOURCE` for probes; `GOVERNED_ANALYSIS` for the certification artifact |
| Authority required | **Engineering execution** to build probes. **The declaring owner** to accept that a standing certification loses its basis |

#### 3.3.6 Evidence required

| Class | Requirement |
|---|---|
| Per axis | An executable probe with a recorded result — **16 of 16, none omitted** |
| Expected failures | **Axes 13 and 14 are expected to FAIL.** A run reporting 16/16 pass would contradict standing measurement and must itself be treated as suspect |
| Reproducibility | Each probe reproducible from a bare fresh clone with **no environment variables set** |
| Verifier identity | Recorded per item |
| Five-field completeness | Every certified item carries all five fields, or the absence is **named with a reason** |
| Withdrawal record | Any claim that cannot be instrumented is **withdrawn**, and the withdrawal is recorded |

#### 3.3.7 Validation method

**VR-56** — each of the 16 axes has a probe; Axes 13–14 currently fail. Plus **VR-25** — reproducible from a bare fresh clone with no environment variables set.

#### 3.3.8 Acceptance criteria

| # | Criterion | Pass condition |
|---|---|---|
| A3-1 | 16/16 instrumented | No axis lacks a probe |
| A3-2 | Contradictions surfaced | Axes 13–14 results recorded, expected failing |
| A3-3 | Five fields present | Every certified item, or a named absence |
| A3-4 | Cross-process reproducibility | `CR-01` replaces single-process evidence |
| A3-5 | Zero prose-only certifications remain | Instrumented or withdrawn |
| A3-6 | Ceiling respected | **No verdict exceeds `CERTIFIED-PROVISIONAL`.** A criterion promising more is unsatisfiable by construction |
| A3-7 | No new temporal defect | Timestamps qualified, or the exemption declared |

**A3-6 is why BC-3 cannot yield `READY UNCONDITIONAL` by itself.** Unconditional certification requires a ratifier, and none is located.

---

### 3.4 BC-4 — OWNERSHIP CLOSURE

#### 3.4.1 Blocker

Ownership is unresolved for the majority of subjects. **0% ratified.** The governed assignment catalogue is **literally empty** — independently confirmed by P-6: `assignments = {}`.

| Figure | Source | Value |
|---|---|---|
| Unowned | `UCOD-001` / R-2 | **391 of 542** (151 owned, 27.86%) |
| Unowned | R-7 | **398 of 549** (151 declared, 27.5046%, **and falling**) |
| Ratified | both | **0%** |
| Assignment catalogue | **P-6, first-party** | **empty (`{}`)** |

The variance between the two figures is **disclosed and carried unresolved**. On either figure the ownership property is unsatisfied for a majority of subjects.

#### 3.4.2 Root cause

**An authority problem in the shape of a data problem.** `UCOD-001:332` separates them: machinery **production-ready**, data 27.86% populated. But the data cannot be produced by the machinery, because the machinery exists specifically to refuse producing it — `require_owner()` raises `OwnershipFabricationError` rather than infer.

Two structural aggravators: authority is partitioned across **three mutually disclaiming planes with no shared key** (declaration and enforcement *"do not share a key"*), and **no competent ratifier is located** (`MP2-C-04`, `VAC-01`).

#### 3.4.3 Resolution approach

**Define and operate a Universal Ownership Resolution Process. Populate nothing automatically.**

```
Entity → Ownership Discovery → Authority Verification → Evidence → Binding → Registry Update
```

| Stage | What it does | What it must never do |
|---|---|---|
| **Entity** | Enumerate the subject population at the declared grain | Invent a subject |
| **Ownership Discovery** | Search **declared** sources only: existing declarations, canonical homes, `producer_homes`, `governed_by` chains, self-declared `Authority` fields | Infer an owner from proximity, authorship, commit history or file location |
| **Authority Verification** | Confirm the discovered owner is a **located, competent** authority for that subject class | Accept a plausible owner; accept an unregistered authority; accept a contested one (**R-55** — F-20 must be resolved first) |
| **Evidence** | Bind the assignment to an evidence record of a declared `EvidenceKind` | Use an evidence kind whose constitutive status is undecided (**R-52 CRITICAL**) |
| **Binding** | Record the assignment as a proposal awaiting ratification | Treat a binding as ratification. **0% ratified is a separate fact from 0% assigned** |
| **Registry Update** | Write the catalogue **only** for a verified, evidenced, owner-accepted assignment | Write a single row that is discovered-but-unverified |

**Three hard rules, non-negotiable:**

1. **Unknown owner remains unknown.** No default, no `UNASSIGNED` fallback, no permissive placeholder.
2. **No automatic approval.** Discovery proposes; only the owner accepts.
3. **No invented authority.** If no competent authority exists, that is the finding — not a gap to fill.

**R-54 (CRITICAL) restated as a prohibition:** automated population of the 391 (or 398) assignments is *exactly* the fabrication the machinery is built to refuse. `UCOD-001:401` — *"will not fabricate them to close it."*

#### 3.4.4 Unresolved ownership partition

The process's **first deliverable is a partition, not a population.** Structure fixed here; contents to be produced by executing Discovery, which has not been run:

| Partition | Definition | Discharged by | Expected disposition |
|---|---|---|---|
| **P-A · Resolvable internally** | A declared source already names a located, competent owner; the row is merely unwritten | Engineering execution transcribing a **declared** owner — never choosing one | Assignable, **still unratified** |
| **P-B · Requires external authority** | No competent authority is located in-repo | An **external constituent act** (`CEP-002` Article 28) | **BLOCKED.** Includes UKAP/UREE |
| **P-C · Constitutional decision required** | Ownership depends on an undecided constitutional question | A **constitutional decision** | Held. Includes multi-dimensional ownership, **constitutionally excluded** by `OWN-REQ-002` (X-12), and evidence-kind constitutive status (R-52) |

**Even a fully populated P-A leaves ratification at 0%,** because ratification requires a ratifier and `MP2-C-04` records that none is located. **BC-4 therefore cannot reach unconditional closure inside the repository, by any engineering sequence.**

#### 3.4.5 Dependencies

| Dependency | State |
|---|---|
| **T-22.2** — machine-readable authority key | **Unresolved authority decision.** SQ-12: ownership rows cannot be joined to enforcement without it |
| **F-20** resolution | **Unresolved contradiction.** Two determinations disagree whether the Article 28 block exists. **R-55** forbids proceeding under *"already operational"* |
| **BC-1** | Required — a registry update is a mutation and must be classifiable |
| **BC-4 gates** | T-14.1 (canonical declaration), T-24.3/T-19.4 (autonomy), T-14.3 (assimilation Ownership stage), T-22.4, T-23.2 |

#### 3.4.6 Owner

| Role | Owner | Basis |
|---|---|---|
| Process owner | **Universal Ownership programme** (`platform/universal_ownership/`) | Owns the machinery and the catalogue |
| Per-assignment owner | **Each subject's own owner** | Cannot be named by this plan without committing R-54 |
| Ratifying authority | **NOT LOCATED** | `MP2-C-04`, `VAC-01` |
| Article 28 authority | **EXTERNAL** | `CEP-002` |

#### 3.4.7 Evidence required

Per proposed assignment: the **declared source** the owner was discovered from · the authority-verification result · an evidence record of a declared kind · the owner's explicit acceptance · a ratification record **or** an explicit statement that ratification is unavailable. Programme-level: the P-A/P-B/P-C partition with counts, the disclosed 391/542 ↔ 398/549 variance, and the **coverage trend**, since R-7 records coverage *falling*.

#### 3.4.8 Validation method

**VR-52** — ownership closure measured; unowned subjects **fail closed** rather than defaulting to `UNASSIGNED`. **VR-51** — every ownership row resolves to a machine-readable key; declaration and enforcement join on it. Expected side effect **R-53**: making rows machine-readable **exposes rows that do not resolve** — intended.

#### 3.4.9 Acceptance criteria

| # | Criterion | Pass condition | Attainable in-repo? |
|---|---|---|---|
| A4-1 | Process defined and fail-closed at every stage | Six stages, three hard rules enforced | **YES** |
| A4-2 | Partition produced | Every unowned subject in exactly one of P-A / P-B / P-C | **YES** |
| A4-3 | Zero fabrication | No assignment lacking a declared source and owner acceptance | **YES** |
| A4-4 | Unknown stays unknown | No default, no `UNASSIGNED` fallback | **YES** |
| A4-5 | Authority key resolves | VR-51 | **NO — decision** |
| A4-6 | Ownership ratified | VR-52 with ratification | **NO — owner act + no ratifier located** |
| A4-7 | **TI-4 holds** | Every admitted subject resolves to exactly one ratified owner | **NO** |

**A4-5, A4-6 and A4-7 are unattainable inside the repository.** This is recorded plainly rather than restated as a smaller target.

---

### 3.5 BC-5 — CONSTITUTIONAL DECISION RESOLUTION

#### 3.5.0 Closure fields

Stated in the same eight-field form as BC-1…BC-4 and BC-6, so BC-5 is not under-specified merely because its content is a decision rather than a change.

| Field | Content |
|---|---|
| **Blocker** | Two foundational constitutional questions are undecided, and both determine what the programme is aiming at |
| **Root cause** | The questions are **choices, not findings.** They are not discoverable by analysis, and the authority competent to make them is **not located in the repository**. `MP2-C-04` records that three located instruments find no competent ratifier; no instrument in the corpus claims amendment competence |
| **Resolution approach** | **DECISION — zero engineering.** Prepare a complete decision package per question (options · consequences · architectural impact · affected laws · affected capabilities · required authority) and **present it for decision without selecting**. §3.5.2 and §3.5.3 are those packages |
| **Dependencies** | **None.** BC-5 runs parallel to all other work and blocks none of BC-1, BC-2, BC-3 or BC-6. It gates only the **final target definition** — and, through D-2, the specific items T-17.2, T-15.4 and T-18.2 |
| **Owner** | **Constitutional / amendment authority — NOT LOCATED.** Not assignable by this plan. Package preparation is owned by the analysis function; **selection is not** |
| **Evidence required** | Per decision: the enumerated options · the consequence of each · the affected laws and capabilities · the named required authority · and, on decision, a **recorded act by that authority**. Evidence of *preparation* is this plan; evidence of *resolution* does not exist and cannot be manufactured |
| **Validation method** | A decision is validated by the **existence of a competent recorded act**, not by a test. There is no `VR-nn` for a choice. The falsifiable check available is negative: **no engineering artifact may be found to have selected either option** — verified for this plan in §3.5.5 A5-2 |
| **Acceptance criteria** | §3.5.5 — A5-1…A5-4. **A5-4 is `UNATTAINABLE-IN-REPO`** |

#### 3.5.1 Blocker

Two foundational questions are undecided, and **both change the target**. Beginning implementation before they are decided means discovering mid-programme that the target was wrong.

**No option is selected below. Selection is not an engineering act.**

---

#### 3.5.2 DECISION PACKAGE D-1 — CH-6 · Facet frame: invariant or limitation?

| Field | Content |
|---|---|
| **Question** | Is the 33-facet frame a **true invariant** or a **limitation to be opened**? |
| **Current state** | `Facet` is a closed 33-member enum (C-02). `engine/uckp/facets.py` states: *"Adding a thirty-fourth facet is a constitutional amendment."* A 33-row `facet_reduction` mapping binds every facet to a root primitive |
| **Option A — INVARIANT** | The frame is fixed. UCOS Ω∞ is infinite in **population** and permanently bounded in **description**. The honest target becomes *"unbounded within a fixed descriptive frame"* |
| **Option B — LIMITATION** | The frame opens. Facets become registered members |
| **Consequence of A** | The programme's stated objective is **narrowed and made truthful**. **TI-3 (kind openness) becomes unreachable by definition** at the facet level. Every "infinite evolution" claim must be requalified corpus-wide |
| **Consequence of B** | The doctrine at `engine/uckp/facets.py` must be **amended**. Every dimension inherits the same question: a 16th evolution stage, a 2nd certification class, a 17th universal context kind, a 7th evidence kind, a 14th reasoning kind |
| **Architectural impact** | CH-6 is the root of the whole schema-layer boundary. Under A, W4 kind openness is bounded and honest. Under B, W4 expands and the 33-row reduction mapping must remain total over a growing set |
| **Affected laws** | `engine/uckp/facets.py` doctrine · `FOUNDATION_ARTICLES` UFC-01…17 (C-37) · `ConstitutionalDomain` (C-38) · `UCPA-L-04` (nothing reduces to the axiom) · the ratified 4 root primitives (C-41) and 7/7/7 grammar (C-40) |
| **Affected capabilities** | Every W4 transformation (21) · T-23.2 certification subject · T-24.2 evolution stages · T-9.1 context kinds · T-22.1 evidence kinds · T-20.2 reasoners |
| **Required authority** | **Constitutional / amendment authority. NOT LOCATED** |
| **Engineering position** | **No transformation below W4 depends on this.** BC-1, BC-2, BC-3 and BC-6 may all be closed while D-1 is undecided. Only the *final answer to the programme's objective* depends on it |
| **Risks if pre-empted** | Opening the frame by engineering action **dissolves the constitution**. Declaring it invariant by engineering action **forecloses the programme's stated purpose**. Both are amendments performed without authority |

---

#### 3.5.3 DECISION PACKAGE D-2 — T-17.1 · Protocol: Option A or Option B?

| Field | Content |
|---|---|
| **Question** | Protocol-neutral core with a representable declared periphery, or protocols representable anywhere? |
| **Current state** | **No protocol is representable anywhere.** `_TECHNOLOGY_MARKERS` (17 tokens) and `_TECH_MARKERS` (20 tokens, incl. bare `http`, `grpc`, `mqtt`, `amqp`, `rest`, `websocket`) scan the canonical identity core; a match becomes hard validation failure at **7 sites** and construction failure at **2 more**. `ApiRegistry` **requires** a `protocol` attribute and has **never held a record**. `pyproject.toml:19-22`: *"stdlib-only by constitutional intent (TP-04 Vendor Neutrality of Core, TP-05 Least Sufficient Technology)"* |
| **Option A — neutral core, representable declared periphery** | Core selects no technology; a declared boundary layer may name protocols. **Preserves `USL-15` intact and closes the representational gap.** Achievable by extension: the `ApiRegistry` slot is built, `S-13` supplies registry semantics, the frame/axis pattern supplies the boundary pattern |
| **Option B — representable anywhere** | Requires **weakening or repealing `USL-15`**. A constitutional amendment |
| **Consequence of A** | The gap closes without touching the constitution. The core **still fails** on a protocol token while the periphery admits one (VR-35). Requires a declared boundary the marker scan does not apply to |
| **Consequence of B** | `USL-15` is narrowed or repealed. TP-04 and TP-05 are reopened. The prohibition ceases to be enforceable as a validation failure |
| **Architectural impact** | Under A, one dimension (technology, currently **DISPROVEN**) becomes partially provable at the periphery. Under B, the core's vendor neutrality — one of the properties that makes the substrate universal — is surrendered |
| **Affected laws** | **`USL-15`** · TP-04 Vendor Neutrality of Core · TP-05 Least Sufficient Technology |
| **Affected capabilities** | T-17.2 (**BLOCKED** on this decision) · T-15.4 API adapters · T-18.2 · `ApiRegistry` · the 9 enforcement sites |
| **Required authority** | **Constitutional authority. `CR-15` is explicitly constitutional and cannot be an engineering act. NOT LOCATED** |
| **Independent of the decision** | **T-17.3** (connector schema/code drift) is a consistency defect, is EXECUTABLE now, and is unaffected by either option |
| **Risks if pre-empted** | **R-36 (HIGH):** the marker check is a **naive lowercased substring scan** — `"lambda"` false-positives on identifiers, `"rest"` on `restore`/`restriction`/`forest`. Any change must fix the matching semantics, or narrowing the taboo silently narrows it in unintended places. **R-37 (HIGH):** populating the registry while `USL-15` stands creates records the validators would reject |

---

#### 3.5.4 Secondary decisions surfaced by this plan

Recorded because they gate specific closure steps above. **None is resolved here.**

| # | Decision | Gates | Authority |
|---|---|---|---|
| S-1 | **Gate mutation-mode field** (`H-06`/`CR-09`) — only 4 of 29 gates declare a mode | BC-2's new stage; BC-6 purity attribution | Mutation governance owner |
| S-2 | **Temporal qualification of certification timestamps** | BC-3 field 3. Asserting an unqualified date would create the R-18 defect | Baseline authority owner |
| S-3 | **Machine-readable authority key** (T-22.2) | BC-4 A4-5 · SQ-12 | An authority spanning three disclaiming planes |
| S-4 | **Evidence-kind constitutive status** (R-52 CRITICAL) | BC-4 Evidence stage | Constitutional authority |
| S-5 | **F-20 resolution** — does the Article 28 block exist? | BC-4 P-B · R-55 | The two disagreeing determinations' owners |
| S-6 | **Lifecycle authority** (T-15.3) — six incompatible models; determination artifacts have none | BC-3 artifact lifecycle · SQ-8 | Lifecycle authority — **not located** |

#### 3.5.5 BC-5 acceptance criteria

| # | Criterion | Pass condition |
|---|---|---|
| A5-1 | Decision packages complete | D-1 and D-2 each carry options, consequences, architectural impact, affected laws, affected capabilities, required authority |
| A5-2 | **No automatic selection** | Neither package selects an option ✅ **satisfied by this artifact** |
| A5-3 | Secondary decisions surfaced | S-1…S-6 recorded, none resolved ✅ **satisfied** |
| A5-4 | Decisions recorded by a competent authority | **NOT SATISFIED — no competent authority located** |

---

### 3.6 BC-6 — BASELINE INTEGRITY

#### 3.6.1 Blocker

The baseline is not measurable. Evidence produced by any closure work could not be distinguished from pre-existing failure.

#### 3.6.2 Root cause

Three independent conditions, conflated into one symptom:

1. **`verify.sh --full` exits 1** — 4 of 15 stages fail (inherited; **not re-measured**, see §2.2).
2. **38 tracked modifications with no recorded owner, purpose, evidence or approval** — including `verify.sh` itself (**+46/−6**, P-9) and `platform/tests/test_mutation_classification.py` (+3/−3, P-10), i.e. **the gate and the test of the blocker being closed are both dirty**.
3. **Baseline ambiguity** — B-7 §3 condition `0.6` (*isolate the dirty tree by owning programme*) is recorded as **currently failing**.

#### 3.6.3 The 15 stage slots

Measured first-party by counting `run_stage` invocations (P-7). 14 declared stages plus the coverage report:

| # | Stage |
|---|---|
| 1 | ruff lint + format-check (engine + platform) |
| 2 | prerequisite generation (knowledge · determinism · closure 1-3) |
| 3 | pytest + coverage gate (`--cov-fail-under=90`) |
| 4 | governance enforce `--pre` |
| 5 | registry validate (schema + integrity) |
| 6 | meta-constitutional conformance (CMG-INV-01..12) |
| 7 | universal object governance (UGA-INV-01..10) |
| 8 | autonomous universal evolution (UAUE gate, every declared obligation) |
| 9 | evolution surface replay (history + 18 registers) |
| 10 | universal object birth contract (UOBC-000001, identity before existence) |
| 11 | universal infinite scope and direction (UISD-000001, unbounded and self-applied) |
| 12 | constitutional primitive alignment (UCPA-000001, root ontology measured and reduced) |
| 13 | universal verification intelligence (UVI-000001, selection derived and assurance preserved) |
| 14 | coverage report |
| — | (`run_stage` definition itself, not a stage) |

**Which 4 fail is inherited and unverified by this plan.** First-party measurement requires executing the gate, which this plan is forbidden to do (§2.2). **Identifying the 4 failing stages is the first step of BC-6 and belongs to its owner.**

#### 3.6.4 The 38 tracked modifications, grouped by owning programme

Grouping is by declared home. **Attribution of purpose and approval is an owner act and is not performed here.**

| Group | n | Paths | Likely owning programme |
|---|---|---|---|
| **G-1 · Book data** | 6 | `00-BOOK/DATA/{artifacts,change-ledger,control-tower,id-ledger,relationships,volumes}.json` | 00-BOOK / registry. **`id-ledger.json` and `artifacts.json` are R-03 `CORPUS_REGISTRATION` subjects — mutation here is identifier allocation** |
| **G-2 · Book portal** | 10 | `00-BOOK/PORTAL/*` (9 pages + `index.md`) | 00-BOOK. Likely generated — must be checked against `generated-artifact-registry.json` (R-04) |
| **G-3 · Book registries** | 5 | `00-BOOK/REGISTRIES/{CHANGE-VERSION-LINEAGE,KNOWLEDGE-GRAPH,UNIVERSAL-ARTIFACT,UNIVERSAL-PAGE,VOLUME}-REGISTRY.md` | 00-BOOK |
| **G-4 · Control tower** | 1 | `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md` | 00-BOOK |
| **G-5 · Verification intelligence** | 4 | `engine/verification_intelligence/{model,registry,selection}.py`, `engine/verification_impact/changes.py` | UVI-000001 owner. **Directly relevant to BC-2 and to T-13.3/R-24** |
| **G-6 · Tests** | 2 | `engine/tests/unit/test_verification_impact.py`, `platform/tests/test_mutation_classification.py` | UVI owner · Repository Intelligence. **The second is BC-1's own test** |
| **G-7 · Gate and build** | 5 | `verify.sh` (**+46/−6**), `Makefile`, `pyproject.toml`, `bootstrap.sh`, `doctor.sh` | Verification / build owner. **R-07 `SOURCE`** |
| **G-8 · Environment** | 2 | `scripts/ucos-env.sh`, `ENVIRONMENT-SETUP.md` | Environment owner |
| **G-9 · Exclusion authority** | 1 | `.gitignore` | **R-02 `EXCLUSION` — an exclusion instrument; mutation here changes what the gate can see** |
| **G-10 · Registry coverage** | 1 | `engine/registry_coverage/declarations.json` | Registry coverage owner |
| **G-11 · Master plan** | 1 | `UCOS-MIP-000003-MASTER-IMPLEMENTATION-PLAN-V3.md` | MIP owner |
| | **38** | | |

**Two observations that materially affect closure order.** G-9 modifies the **exclusion authority**, so the gate's own field of view is currently uncommitted. G-5/G-6 are in-flight work on **verification intelligence and the mutation-classification test** — the exact surfaces BC-1 and BC-2 touch. Closing BC-1 or BC-2 on top of these without first landing or reverting them would produce evidence attributable to neither.

#### 3.6.5 Resolution approach

**Attribution first, repair second. No bulk action.**

| Step | Action | Constraint |
|---|---|---|
| 1 | Each owning programme claims its group and records **owner · purpose · evidence · approval** for every path | **No bulk attribution. No assumed intent** |
| 2 | Land or revert per group, owner by owner | **G-9 first** — the gate's field of view must be settled before anything is measured. **G-5/G-6 before BC-1/BC-2** |
| 3 | Owner of `verify.sh` reconciles **+46/−6** and declares whether it changes stage semantics | If it does, the inherited 4-of-15 figure is stale |
| 4 | Execute `./verify.sh --full` **first-party** and record which stages fail | The first legitimate execution; belongs to the gate owner |
| 5 | Route each failing stage to its declared owner with evidence | Each failure is a separate defect, not one blocker |
| 6 | Re-execute until it exits 0, or every remaining failure has owner · purpose · evidence · approval | The directive's stated acceptable terminal state |

**Forbidden during BC-6:** `git checkout .`, `git reset --hard`, `git clean -fd`, `git stash` across groups, or any bulk discard. The 38 modifications include registry data, an exclusion instrument, and identifier-allocation ledgers; discarding them in bulk could **destroy minted identifiers** and would itself be an unclassified, unowned, unevidenced mutation of exactly the kind this programme exists to prevent.

#### 3.6.6 Dependencies

| Dependency | State |
|---|---|
| None on other blockers | **BC-6 is a precondition, not a peer.** It is outside the 67-transformation population |
| **BC-6 gates BC-1, BC-2, BC-3 measurement** | Without it, closure evidence is not distinguishable from pre-existing failure |
| S-1 (gate mode field) | Advisory — clean attribution of gate purity is easier once modes are declared |

#### 3.6.7 Owner

| Role | Owner | Basis |
|---|---|---|
| Per-group owner | **Each owning programme** (§3.6.4) | Declared homes |
| Gate owner | **`verify.sh` / verification owner** | Owns stages and the exit code |
| Coordination | **Programme-level** | Cross-programme sequencing; **no cross-class transaction authority exists** (B-7) |
| Authority required | **Each owner for its own group.** No new authority | Attribution and repair inside declared law |

#### 3.6.8 Evidence required

Per modification: owner · purpose · evidence · approval, **or** a recorded revert. Per gate execution: full stage-by-stage output with pass/fail and exit code. Per failing stage: the owning programme and a defect record. Terminal: either `git status` clean, **or** a manifest in which every remaining modification carries all four fields.

#### 3.6.9 Validation method

`./verify.sh --full` **exits 0**, executed first-party. Plus a reproducibility check: the same result on re-execution. Plus **VR-25** — the closure verdict reproducible from a bare fresh clone with no environment variables set (this is also T-14.2, a W0 transformation).

#### 3.6.10 Acceptance criteria

| # | Criterion | Pass condition |
|---|---|---|
| A6-1 | Every modification attributed | Owner · purpose · evidence · approval, or reverted |
| A6-2 | Exclusion authority settled | G-9 landed or reverted **first** |
| A6-3 | Gate reconciled | `verify.sh` +46/−6 explained; stage semantics declared unchanged or restated |
| A6-4 | Failing stages identified first-party | The 4 (or actual n) named, owned, and recorded |
| A6-5 | Gate passes | `./verify.sh --full` **exits 0** |
| A6-6 | Terminal state reached | `git status` clean, **or** a fully attributed manifest |
| A6-7 | No destructive shortcut | No bulk discard; no identifier lost |
| A6-8 | Reproducible | Same result on re-execution and from a bare fresh clone |

---

## 4. Root Cause Summary

| Blocker | Root cause in one line | Class | Size |
|---|---|---|---|
| **BC-1** | A two-sided coverage contract with one declared rule (R-09 `GOVERNED_ANALYSIS`) unimplemented; fail-closed makes it total | **EXTEND** | ~1 predicate function |
| **BC-2** | Path reproducibility proven and mistaken for initialization independence; the harness runs both builds in one process | **EXTEND** | 1 comparator + 3 child processes |
| **BC-3** | Certification records that a claim was made and never that it was measured; the instrument exists and is not pointed at the 16 axes | **EXTEND** | 16 probes + 5-field binding |
| **BC-4** | An authority problem in the shape of a data problem; the machinery refuses to produce the data by design | **PROCESS + EXTERNAL ACT** | Process definable; ratification unattainable |
| **BC-5** | Two constitutional questions that determine the target, with no located authority to decide them | **DECISION** | Zero engineering |
| **BC-6** | The gate, the exclusion authority and the blocker's own test are all uncommitted, so no measurement is attributable | **ATTRIBUTION + REPAIR** | 38 paths, 11 groups |

**CREATE = 0 across all six.** Consistent with R-2 §32.2 and R-5: no new engine is required anywhere.

---

## 5. Dependency Order

```
BC-6  baseline integrity            ← PRECONDITION (outside the 67 population)
   │   G-9 exclusion authority first · G-5/G-6 before BC-1/BC-2
   ▼
BC-1  classification   ══╗
BC-2  detection        ══╬══ jointly first, mutually independent (both roots)
   │                     ║
   │  BC-1 → everything (SQ-2: every later mutation must be classifiable)
   │  BC-2 → T-6.1 (SQ-1, R-01) · T-13.3 (SQ-7, R-24 CRITICAL)
   ▼
BC-3  certification evidence         ← requires BC-1 + BC-2 (CR-01 must REPLACE single-process evidence)
   │  BC-3 → every later success claim (SQ-9, EP-7, CR-21)
   ▼
BC-4  ownership closure              ← process definable now; P-A assignable; ratification BLOCKED
   │  gated by S-3 (authority key, SQ-12) and S-5 (F-20)
   ▼
BC-5  constitutional decisions       ← PARALLEL THROUGHOUT; blocks none of BC-1/2/3/6
                                       blocks only the final target definition
```

**Reading of the graph:** BC-6 → BC-1 + BC-2 → BC-3 is a fully in-repo chain of four. BC-4 is partially in-repo and terminally blocked. BC-5 is entirely outside engineering and runs in parallel.

---

## 6. Implementation Safety Gates

Every change under this plan must pass all nine stages in order. A change that cannot complete a stage **stops there** and is recorded, not routed around.

```
Discovery → Classification → Impact Analysis → Security Review → Implementation
          → Testing → Validation → Certification → Evidence Capture
```

| # | Stage | Gate condition | Instrument | Available at baseline? |
|---|---|---|---|---|
| 1 | **Discovery** | The subject and its declared home are identified from declared sources | Canonical homes, `producer_homes`, `governed_by` | YES |
| 2 | **Classification** | `classify()` returns a class, not `ERROR` | `mutation_classification.classify` | **NO — BC-1** |
| 3 | **Impact Analysis** | Impact computed **and its substrate coverage disclosed** | `verification_impact` | **NO — unwired, 10.4% coverage (R-45)** |
| 4 | **Security Review** | No new pre-validation execution path; no code loaded as data | CH-5 pattern check | **PARTIAL — CH-5 open until T-21.1** |
| 5 | **Implementation** | Inside the engineering-execution boundary; no privileged attribute opened | §3 owner column | YES for BC-1/2/3/6 |
| 6 | **Testing** | Positive, negative, purity, and regression-guard tests | pytest, coverage floor 90 | **PARTIAL — gate exits 1** |
| 7 | **Validation** | The named `VR-nn` executed **cross-process** | BC-2 comparator | **NO — BC-2** |
| 8 | **Certification** | Five-field record; ceiling `CERTIFIED-PROVISIONAL` | BC-3 | **NO — BC-3 / CR-21** |
| 9 | **Evidence Capture** | All six evidence classes E-1…E-6, or each absence named | R-1 §22 | **NO — E-1 and E-5 absent** |

**Four of nine safety gates are unavailable at baseline, and stage 2 is unavailable for every change including the change that fixes stage 2.** This is resolved by validating BC-1 directly against VR-40 rather than through the classifier it repairs, and by declaring that limitation rather than concealing it.

---

## 7. Stop Conditions Encountered

The directive specifies five stop conditions. **Three are triggered at baseline.**

| Condition | Triggered | Where | Consequence |
|---|---|---|---|
| **Authority missing** | ✅ **YES** | BC-4 (no ratifier — `MP2-C-04`, `VAC-01`); BC-5 (no amendment authority); S-3, S-4, S-6 | **BC-4 and BC-5 cannot proceed to closure** |
| **Ownership unresolved** | ✅ **YES** | BC-4 — 391/542 (or 398/549) unowned, 0% ratified, catalogue empty (P-6) | **No governed change to an unowned subject may proceed** |
| **Constitutional decision required** | ✅ **YES** | BC-5 — D-1 (CH-6), D-2 (protocol A/B); plus S-4, S-6 | **The final target remains undefined** |
| **Evidence impossible** | ⚠️ **PARTIAL** | BC-3 A3-6: unconditional certification is unattainable — ceiling `CERTIFIED-PROVISIONAL`, Tier T1 vacant. BC-4 A4-6/A4-7: ratification evidence unobtainable in-repo | **`READY UNCONDITIONAL` is not reachable by engineering** |
| **Security boundary unclear** | ❌ NO | CH-5 is precisely located (`universal_provider/discovery.py:404,424`) with a bounded fix (R-49) | Not a stop condition; a scoped W0 transformation |

### 7.1 Consequence for the stated goal

The objective is to move `NOT READY` → **`READY UNCONDITIONAL`** with evidence-backed closure only, and with **no compromise and no partial closure claim**. Applying that standard honestly:

**`READY UNCONDITIONAL` is not attainable by any engineering sequence available inside this repository**, for two independent reasons:

1. **`UCCEP-F-004` caps every verdict at `CERTIFIED-PROVISIONAL`** and Tier T1 is vacant (`VAC-01`). "Unconditional" exceeds the ceiling. A plan promising it would be **unsatisfiable by construction** — and the directive forbids compromise, which includes the compromise of restating an unreachable criterion as though it were reachable.
2. **BC-4 and BC-5 terminate in an owner act, an external constituent act, and two constitutional decisions.** No engineering sequence removes those dependencies, and automated substitutes are explicitly refused (**R-54**, `UCOD-001:401`).

**What is attainable:** BC-6, BC-1, BC-2 and BC-3 can reach evidence-backed closure at the `CERTIFIED-PROVISIONAL` ceiling. That would move the state from **NOT READY** to **READY-CONDITIONAL-ON-{BC-4, BC-5}** — which is a real and substantial advance, and is **not** `READY UNCONDITIONAL`.

This is recorded here rather than discovered later, because concealing it would violate the directive's own instruction to **hide no unresolved condition**.

---

## 8. Gap Confirmation Before Any New Capability

The directive forbids creating new capabilities without gap confirmation. Each proposed change was tested against the inherited reuse analysis:

| Blocker | Proposed change | Existing mechanism reused | New capability? |
|---|---|---|---|
| BC-1 | R-09 predicate | The eight sibling predicates; the two-sided coverage contract; the declared six criteria | **NO — EXTEND** |
| BC-2 | Cross-process comparator | `hermetic_env()`, `_execute_build`, existing digest comparison, the two proven cross-process path gates | **NO — EXTEND** |
| BC-3 | 16 axis probes | `check_open_world` (`S-14`, in 4 engines); `is_extensible` probe idiom; content-addressed certification (`S-10`) | **NO — EXTEND** |
| BC-4 | Resolution process | `require_owner()`, `OwnershipFabricationError`, declared grain, evidence admission — **machinery is production-ready** | **NO — PROCESS over existing machinery** |
| BC-5 | Decision packages | None required | **NO — zero engineering** |
| BC-6 | Attribution + repair | `git`, `verify.sh`, declared homes | **NO** |

**CREATE = 0.** Consistent with R-2 §32.2 (*"there is no missing engine to build"*), R-5 (*"New engines determined necessary: ZERO"*) and R-6 (*"New engines / authorities / registries implied: ZERO"*).

---

## 9. Disclosures

### 9.1 Expected degradation — recorded before execution, not explained after

| Blocker | Expected effect | Risk | Correct reading |
|---|---|---|---|
| BC-1 | Mutations certified while unclassified are revealed | R-42 | Disclosure obligation (CR-17) |
| BC-2 | **Green gates turn red** | R-41 | **Intended.** They were green because they could not see |
| BC-3 | **Axes 13 and 14 fail**; a standing certification loses its basis | R-58 | Expected; the point of the exercise |
| BC-3 | ~230 closures surface if disclosure runs alongside | R-64 | Register worsens before improving |
| BC-4 | Rows that do not resolve become visible; measured ownership worsens | R-53 | Intended effect |
| BC-6 | `gaps=0` may become non-zero once provenance is fixed | R-26 | **Truth-restoring** |

**A closure run that produces none of these is more suspect than one that produces all of them.**

### 9.2 Variances disclosed, not reconciled

| # | Variance | Values | Handling |
|---|---|---|---|
| V-1 | Ownership population | **391/542** (R-2) vs **398/549** (R-7) | Both carried. No execution state depends on the difference |
| V-2 | `verify.sh` diff magnitude | inherited **+45/−0** vs measured **+46/−6** (P-9) | Measured value recorded; reconciliation is BC-6 step 3, owned by the gate owner |
| V-3 | True invariant count | **7 by count**, **6 verified** with the `invariant` marker | Carried as 7 and 6. **The seventh is not invented** |
| V-4 | Which 4 of 15 stages fail | Inherited, unverified | First-party measurement is BC-6 step 4 |

### 9.3 What this plan changed

**Nothing.** No code, configuration, registry, schema, constitution, law, identifier, requirement, ADR, phase, roadmap or certification was modified. No ownership was assigned. No constitutional decision was resolved. No closure was claimed. The single repository mutation is the creation of this file and its companion status register.

---

## 10. Implementation Authorization

| Field | Value |
|---|---|
| Implementation authorization | **NOT GRANTED — not explicitly conferred by the directive** |
| Blockers closed by this plan | **ZERO** |
| Blockers in progress | **ZERO** |
| Mutations performed | **ZERO** (two new untracked planning artifacts) |
| Closure register updated | **NO.** Deliverable 3 is conditioned on *"only after evidence exists."* No closure evidence exists. Updating it would be a registry mutation and a partial closure claim — both forbidden |
| Stop conditions triggered | **3 of 5** — authority missing · ownership unresolved · constitutional decision required. Plus **partial** evidence-impossible on `READY UNCONDITIONAL` |
| Next action requiring authorization | **BC-6 step 1** — per-group attribution by each owning programme. It is the only step with no unmet prerequisite |
| Position | **STOPPED after planning artifacts, per the directive's stop condition** |

### 10.1 Minimum authorization set to begin

| # | Authorization needed | From | For |
|---|---|---|---|
| 1 | Attribute and land/revert group G-9, then G-5/G-6, then the remainder | Each owning programme (§3.6.4) | BC-6 |
| 2 | Execute `./verify.sh --full` first-party and record stage results | Gate owner | BC-6 A6-4 |
| 3 | Implement the R-09 `GOVERNED_ANALYSIS` predicate | **Repository Intelligence** (read from the register) | BC-1 |
| 4 | Add the cross-process comparator as a declared `gate`-mode stage | Determinism / UVI owner + S-1 mode decision | BC-2 |
| 5 | Instrument the 16 axes; accept that a standing certification loses its basis | Certification owner + the axes' declaring owner | BC-3 |
| 6 | Operate Ownership Discovery to produce the P-A/P-B/P-C partition | Universal Ownership programme | BC-4 (partition only) |
| 7 | **Decide D-1 and D-2** | **Constitutional authority — NOT LOCATED** | BC-5 |
| 8 | **Ratify ownership; perform the Article 28 act; resolve F-20** | **Owner act + external constituent act — NOT AVAILABLE IN-REPO** | BC-4 closure |

**Items 1–6 are attainable inside the repository. Items 7 and 8 are not.**

---

*This plan modified no code, configuration, registry, schema, constitution, law, identifier, requirement, ADR, phase, roadmap or certification. It assigned no ownership, invented no authority, resolved no constitutional decision, and claimed no closure — partial or otherwise. Every blocker recorded here remains OPEN. Every unresolved condition is stated rather than hidden, including the finding that `READY UNCONDITIONAL` is unattainable inside this repository and why. The single repository mutation is the creation of this file.*

**END PLAN — STOPPED BEFORE IMPLEMENTATION.**
