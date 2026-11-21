# UCOS Ω∞ — UNIVERSAL FOUNDATION TRANSFORMATION EXECUTION READINESS DETERMINATION

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-UNIVERSAL-FOUNDATION-TRANSFORMATION-EXECUTION-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** This determination creates no identifier, requirement, ADR, phase, roadmap or certification. It authorizes no implementation, confers no authority, and closes no scope. |
| Mode | READ-ONLY EXECUTION READINESS DETERMINATION |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Baseline working tree | 335 `git status --porcelain` lines, of which 38 are tracked-modified. **Pre-existing; not produced by this determination.** |
| Predecessor | `UCOS-OMEGA-INFINITY-FINITE-TO-INFINITE-TRANSFORMATION-MASTER-DETERMINATION.md` — verdict **NOT READY** |
| Function | Converts the predecessor's 67-transformation architectural analysis into an execution decision framework: four execution states, eight ordered waves, and the exact boundary of what may proceed |
| Transformation population | **67** |
| Execution state vocabulary | EXECUTABLE · CONDITIONAL · BLOCKED · PROHIBITED |
| Discovery | **Not repeated.** Every finding, count, measurement and classification is inherited from §2. No new discovery was performed, and no settled finding is reopened. |

---

## 1. Objective

Determine the exact boundary between:

- transformations that **may proceed** now
- transformations **requiring authority** before they may proceed
- transformations **blocked by missing foundation** or by an act outside the repository
- transformations **prohibited by constitutional principles** or by the fact that transformation would be regression

The predecessor determination established *what* must transform, *in what order*, and *why*. It returned **NOT READY** for the programme and **READY** for ten specific transformations. That verdict is a statement about architecture. It is not yet a decision framework: it does not state, for an arbitrary proposed change, whether that change may be executed, what must be true first, who must decide, and what evidence closes it.

This determination supplies that framework.

### 1.1 The primary question

> What is the minimum safe execution boundary that allows UCOS Ω∞ transformation to begin without creating **non-durable truth**, **uncontrolled mutation**, **unauthorized ownership**, **runtime authority leakage**, or **unverifiable evolution**?

The answer is stated in §3 as a boundary, in §18 as eight waves, and in §28 as a verdict.

### 1.2 What this determination deliberately does not do

It performs no implementation. It creates no identifier, requirement, ADR, phase or roadmap. It authorizes no wave. It ratifies nothing. It does not convert a gap into a fix, does not decide any of the five open authority questions, and does not open any constitutional restriction. Where the predecessor recorded a constraint as constitutional intent rather than defect, this determination carries that judgment forward unchanged and classifies transformation of it as **PROHIBITED** rather than pending.

### 1.3 The correction carried forward

The predecessor made four corrections to the framing it inherited (§35.5 of that document). All four are load-bearing here and are restated because the execution boundary depends on them:

1. **Not every finite boundary is a limitation.** Seven constraints are true invariants; four transformations are classified READY *as preservation*, meaning the correct action is to change nothing. Transforming them is regression, and this determination classifies them **PROHIBITED** rather than available.
2. **The protocol verdict is not a defect to remediate.** `USL-15` is working as designed. Opening it is an amendment about what UCOS Ω∞ is for.
3. **"Truth authority precedes runtime independence" is inverted.** Detection precedes both. Without initialization-independence measurement, neither fix is verifiable.
4. **Autonomous evolution is not the third step of a gradient.** It is a change of kind, gated on all five target invariants, carrying the highest-severity risk on the register.

---

## 2. Baseline Evidence

### 2.1 Determinations relied upon

Discovery is not repeated. Conclusions are inherited with their verdicts intact.

| # | Determination | Inherited verdict / decisive content |
|---|---|---|
| B-1 | `UCOS-OMEGA-INFINITY-UNIVERSAL-INFINITE-EXISTENCE-REALITY-KNOWLEDGE-CAPABILITY-EVOLUTION-COMPLETENESS-DETERMINATION.md` | **PARTIALLY PROVEN.** 0 ASSIMILATED / 19 PARTIALLY / 7 NOT YET at dimension level; 90 findings (19/35/35/1); 2 of 13 expansions DISPROVEN (technology, governance); 239 closed enums with 230 undisclosed |
| B-2 | `UCOS-OMEGA-INFINITY-UNIVERSAL-TRUTH-AUTHORITY-RUNTIME-INDEPENDENCE-DETERMINATION.md` | **PARTIALLY PROVEN.** 30 findings (3 ASSIMILATED / 14 PARTIALLY / 12 NOT YET / 1 UNKNOWN); 13 truth objects: 4 SUPPORTED / 2 PARTIAL / 7 UNSUPPORTED; **two** process-global mutable authorities (`identity.py:156,159` and `vocabulary.py:542`), both leaking across capabilities; chain B in force on every open surface |
| B-3 | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CAPABILITY-EVOLUTION-DETERMINATION.md` | Identity capability claim **DISPROVED** clause-by-clause: 2 of 6 clauses hold, 2 partially, 2 fail. 22 gaps (`IDF-01…IDF-22`), 12 contradictions. 13 identifier shapes, 58 prefixes, 4 alphabets, no codec, no scheme version, no migration. **Zero new engines determined necessary** |
| B-4 | `UCOS-OMEGA-INFINITY-IDENTITY-DETERMINISTIC-VALIDATION-BOUNDARY-DETERMINATION.md` | **DEPENDENT — on execution history, for 43 of 72 admissible kinds (59.7%).** 17 findings (`DV-01…DV-17`), 12 contradictions. Overall classification **PARTIALLY DETERMINISTIC**. Root cause `DV-11`: a derivable kind space that is not derived. **One** true missing capability: committed-data kind resolution |
| B-5 | `UCOS-OMEGA-INFINITY-FINITE-TO-INFINITE-TRANSFORMATION-MASTER-DETERMINATION.md` | **NOT READY.** 67 transformation analyses across 19 domains; 78 finite constraints four-way classified; 20 runtime-authority violations; 63 validation requirements; 23 certification obligations; 65 risks (8 CRITICAL); 12 hard sequencing constraints; **0 CREATE required** |
| B-6 | `UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-MASTER-REGISTER.md` | **41 / 135 = 30.4% closed** (27 GOVERNED · 53 OPEN · 14 BLOCKED); 2 of 10 final gate conditions met; `verify.sh --full` **exits 1**, 4 of 15 stages failing; dominant constraint ownership; `VERDICT: REGISTER-COMPLETE · CLOSURE-INCOMPLETE · IMPLEMENTATION-NOT-AUTHORIZED` |
| B-7 | `UCOS-OMEGA-INFINITY-IMPLEMENTATION-SEQUENCE-MASTER-PLAN.md` | `SEQUENCE-DERIVED · 11 WAVES + 1 VEST-ONLY CLASS · 6 ACTIONABLE ROOTS · NO WAVE AUTHORIZED`. 94 scheduled items reconciling exactly to 53 OPEN + 27 GOVERNED + 14 BLOCKED. Certification ceiling `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`); Tier T1 vacant (`VAC-01`); no competent ratifier located (`MP2-C-04`) |

### 2.2 The three anchoring measurements

Reproduced independently in B-1 and B-5 at `HEAD = bae59755`, not taken on report. Every execution state in this determination reduces to one of these three:

| # | Measurement | Result |
|---|---|---|
| **M-A** | Closed enumeration census | 239 closed `Enum` subclasses in production trees; **230 undisclosed** |
| **M-B** | Runtime-dependent validity | Same commit, zero file changes: `is_well_formed("UCOS-CLSS-8966ca9e8d02")` → `False` in a fresh interpreter, `True` after `engine.ceu.catalog.bootstrap()`. 43 of 72 kinds and 195 CEU identities affected |
| **M-C** | Mutation classification non-functional | `RULE_PREDICATES` = R-01…R-08; `validate_rule_coverage` → `("rule 'R-09' is declared but no predicate implements it",)`; `classify()` returns `status='ERROR'` for **every** subject in the repository |

### 2.3 The seven defect chains

| Chain | Root | Consequence for execution |
|---|---|---|
| CH-1 | No committed existence document | Anything admitted is non-durable; 43 of 72 kinds; 9 enforcement sites |
| CH-2 | Zero of 29 gates vary initialization order; single-process determinism harness | CH-1 is undetectable by any existing gate — **no fix can be shown to work** |
| CH-3 | One missing mutation predicate (R-09) | **Nothing new can be classified anywhere, in any dimension, right now** |
| CH-4 | 391/542 unowned; 0% ratified; three disclaiming planes; UKAP/UREE blocked on Article 28 | No located authority can admit a change |
| CH-5 | Unrestricted `importlib` from unvalidated JSON, pre-validation | The sole open-kind mechanism is an execution-trust hole |
| CH-6 | 33 facets / 15 stages / 1 certification class / 16 context kinds / 6 evidence kinds / 13 reasoning kinds | A new dimension of description is an amendment in every dimension |
| CH-7 | Frames open, computation absent | Any future reality is addressable and not computable |

### 2.4 The five target invariants

| # | Target invariant | Testable form | Achievability |
|---|---|---|---|
| TI-1 | **Durability** — anything admitted survives process death | Delete runtime memory, reload canonical, reconstruct, compare identical | Existing capability |
| TI-2 | **Initialization independence** — no verdict depends on process history | Same subject, same verdict in a fresh and a bootstrapped interpreter | Existing capability |
| TI-3 | **Kind openness** — a new kind of description enters by registration | A probe kind never seen by the release is admitted, persisted and honoured by a fresh validator | Requires CH-6 decision |
| TI-4 | **Owned admission** — nothing is admitted without a resolvable ratified owner | Every admitted subject resolves to exactly one ratified owner, or admission fails closed | Requires an authority act |
| TI-5 | **Trusted admission** — nothing executes before it is trusted and validated | No code path imports or invokes from an unverified descriptor | Existing capability |

### 2.5 The twelve/fourteen sound foundations that must survive

`S-01` location/frame resolver · `S-02` temporal model · `S-03` measurement registry · `S-04` serialization registry · `S-05` persistence suite · `S-06` capability register · `S-07` pipeline contract · `S-08` non-termination · `S-09` evolution refusals · `S-10` certification integrity · `S-11` ownership fail-closed resolution · `S-12` artifact-layer reconstruction · `S-13` vocabulary mechanism · `S-14` anti-closure gate.

**S-13 and S-14 carry the programme.** Nineteen transformations are vocabulary conversions against S-13; four are applications of S-14 to surfaces it does not currently cover. This is why **zero transformations require a new capability**.

### 2.6 Evidence limits carried forward

- Numeric findings from prior determinations were not re-executed except M-A, M-B, M-C.
- The working tree carries 38 pre-existing tracked modifications, not analysed as intended change. B-7 §3 records that these must be isolated by their owning programmes before any wave can be measured cleanly, and that this condition is **currently failing**.
- No claim is made about surfaces neither read nor executed.
- **Ownership figure variance (disclosed, not resolved).** B-5/`UCOD-001` states **391 of 542** subjects unowned (151 owned, 27.86%). B-6 states **398 of 549** unowned (151 declared, 27.5046%, *and falling*). Both are carried. The variance does not change any execution state: on either figure the ownership property is unsatisfied for a majority of subjects and CH-4 stands.

---

## 3. Transformation Boundary

### 3.1 The boundary stated

```
                         ┌─────────────────────────────────────────────┐
   EXECUTABLE  (10)      │ Dependencies satisfied · authority present   │
                         │ inside existing declared law · evidence      │
                         │ obtainable · validation definable ·          │
                         │ certification attainable at the provisional  │
                         │ ceiling. MAY PROCEED under wave discipline.  │
                         └─────────────────────────────────────────────┘
                                            │
                         ┌─────────────────────────────────────────────┐
   CONDITIONAL (47)      │ Architecturally transformable, held by an    │
                         │ unmet predecessor (SQ-1…SQ-12) or by one of  │
                         │ five undecided authority questions.          │
                         │ MAY NOT PROCEED until the named condition.   │
                         └─────────────────────────────────────────────┘
                                            │
                         ┌─────────────────────────────────────────────┐
   BLOCKED     (4)       │ Terminates in an owner act or an external    │
                         │ act with no competent authority located      │
                         │ inside the repository. NO ENGINEERING PATH.  │
                         └─────────────────────────────────────────────┘
                                            │
                         ┌─────────────────────────────────────────────┐
   PROHIBITED  (6)       │ Transformation is regression, or is refused  │
                         │ by a standing constitutional position.       │
                         │ MUST NOT PROCEED. Not a backlog item.        │
                         └─────────────────────────────────────────────┘

   TRUE INVARIANTS (7)   Not transformations. Constraints that define the
                         constitution. Out of scope for execution entirely.
```

### 3.2 Population reconciliation

| Execution state | Count | Share | Derivation from B-5 classifications |
|---|---|---|---|
| **EXECUTABLE** | **10** | 14.9% | The ten Layer 0/1 transformations of B-5 §34.3, all READY, all REUSE or EXTEND, none requiring an authority decision |
| **CONDITIONAL** | **47** | 70.2% | 33 READY-but-sequenced + 13 REQUIRES AUTHORITY DECISION + 1 REQUIRES FOUNDATION CHANGE (T-14.3) |
| **BLOCKED** | **4** | 6.0% | T-14.1, T-17.2, T-22.3, T-22.4 |
| **PROHIBITED** | **6** | 9.0% | 4 READY-as-preservation (T-10.1, T-23.1, T-24.1, T-24.5) + 2 autonomy items (T-19.4, T-24.3) prohibited in the current state |
| **TOTAL** | **67** | 100% | Matches B-5 §35.3 population exactly |

Cross-check against B-5's own roll-up (47 READY · 15 AUTHORITY · 1 FOUNDATION · 0 NEW CAPABILITY · 4 BLOCKED = 67):

- Of 47 READY: 10 become EXECUTABLE, 33 become CONDITIONAL, 4 become PROHIBITED (preservation).
- Of 15 AUTHORITY: 13 become CONDITIONAL, 2 become PROHIBITED (T-19.4, T-24.3 — autonomy).
- The 1 FOUNDATION CHANGE (T-14.3) becomes CONDITIONAL.
- The 4 BLOCKED remain BLOCKED.

`10 + 33 + 4 = 47` ✔ · `13 + 2 = 15` ✔ · `1` ✔ · `4` ✔ · total `67` ✔

### 3.3 True invariants — reconciliation variance disclosed

B-5 §25.4 classifies **7** constraints as invariant (must not be transformed). Six are explicitly enumerated in the constraint tables:

| # | Invariant constraint | Location | Why it is an invariant |
|---|---|---|---|
| C-40 | Hierarchy grammar (7/7/7) | `UMN-001:22-32,195-206` | Ratified grammar; opening it dissolves the hierarchy |
| C-41 | Root primitives (4, +1 demoted) | `01-WORKING/ONTOLOGY-REGISTER.md` | Ratified; T-7.1 instantiates them, never opens them |
| C-46 | Serialization readers, 3 of 6 | `acee_engine.py:246` | The gate **requires** an unregistered format to remain unregistered; closing the gap would break the openness proof |
| C-50 | `SystemType` including `UNKNOWN` | `temporal/coordinate.py:29-41` | `UNKNOWN` first-class is the architecture working |
| P-07 | Identity namespace/local regexes | `uckp/identity.py:49-50` | Open by pattern with no allow-list — already universal |
| P-08 | Registry namespace/natural-key regexes | `registry/universal/identity.py:43,46` | Same property |

**Reconciliation variance, recorded and not resolved:** the §25.4 aggregate states 7 invariants; the itemised tables of §25.1–§25.2 carry the `**invariant**` marker on exactly 6 rows. The seventh is referenced by the count and is not separately enumerated in the evidence read. This determination **carries the count as 7 and the verified enumeration as 6**, and does not invent the seventh. No execution state depends on the difference: all six verified invariants and any unenumerated seventh are equally outside the transformation population and equally out of scope for execution.

### 3.4 The boundary in one sentence

> **Ten transformations may proceed. Forty-seven are held by a predecessor or a decision. Four terminate outside the repository. Six must not be attempted at all. Seven are not transformations.**

---

## 4. Execution Principles

Five principles govern every execution decision below. Each is forced by measured evidence rather than chosen by preference, and each has an associated failure mode already on record.

### EP-1 — Detection before durability

No fix may be executed before the instrument that can detect its failure exists.

**Basis.** CH-2: zero of 29 gates vary initialization order; the only reproducibility harness builds twice in one interpreter sharing env, adapter and signer. **R-01** records that the existing reconstruction test's own fixture calls `bootstrap()`, so it *cannot* detect failure of the durability fix. Executing T-6.1 before T-19.1 produces a change with no verifiable evidence of success — which is indistinguishable, evidentially, from not doing it.

**Enforced by** SQ-1.

### EP-2 — Classification before mutation

No change may be executed while the mechanism that classifies changes is non-functional.

**Basis.** CH-3 / M-C: `classify()` returns `ERROR` for every subject. `UNRESOLVED` fails closed and is documented as never a permissive default. Every transformation in the programme would itself be an unclassifiable mutation. This is not a gap — it is a **live outage in the mechanism that governs change**, and it is one missing predicate.

**Enforced by** SQ-2, SQ-3.

### EP-3 — Durability before openness

No kind, vocabulary, stage or dimension may be opened before what is admitted survives process death.

**Basis.** CH-1 + CH-6. Opening the schema layer first multiplies kinds that evaporate at process exit. B-5 §31.2 names this precisely: Layer 3 kind openness is *"the most visible and most satisfying work"* and starting there violates SQ-1, SQ-2 and SQ-6 simultaneously.

**Enforced by** SQ-6.

### EP-4 — Authority before admission

No subject may be admitted, and no knowledge declared canonical, without a resolvable ratified owner.

**Basis.** CH-4. `require_owner()` raises `OwnershipFabricationError` rather than infer. 391 of 542 concepts have no owner; the assignment catalogue is empty; 0% is ratified. **R-25**: declaring knowledge canonical without a ratified owner creates canonical truth nobody can amend. **R-54**: automated population of the 391 assignments is *exactly* the fabrication the machinery is built to refuse.

**Enforced by** SQ-12, and by TI-4.

### EP-5 — Trust before execution

Nothing may be imported or invoked from a descriptor that has not been verified.

**Basis.** CH-5 / T-13: unrestricted `importlib.import_module` on an unvalidated JSON field at `universal_provider/discovery.py:404,424`, invoked **before** validation runs, with the trust and certification machinery that would prevent it sitting unwired two modules away. This is the sole CRITICAL security defect and the cheapest fix in the register.

**Enforced by** SQ-4, SQ-5, and by TI-5.

### 4.1 Two subordinate principles

| # | Principle | Basis |
|---|---|---|
| EP-6 | **Disclosure before remediation.** A closure must be disclosed before it is fixed. | R-21, R-64. Fixing an undisclosed closure silently changes a certified property. Expect the disclosure register to get worse before it gets better (~230 closures). |
| EP-7 | **No success claim before instrumentation.** No transformation may be certified successful while success is asserted in prose form. | CR-21 / SQ-9. 16 unboundedness axes are CERTIFIED UNBOUNDED on prose citation alone; Axes 13–14 are contradicted by measurement; `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` confers no constitutional finality. |

### 4.2 The certification ceiling that bounds every principle

`UCCEP-F-004` sets a standing ceiling: **the maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`.** Tier T1 is vacant (`VAC-01`) and `MP2-C-04` records that no located instrument is competent to ratify. Every certification field in this determination is bounded accordingly. **A criterion promising unqualified certification would be unsatisfiable by construction and is therefore never stated.**

### 4.3 Field legend for all readiness tables

| Column | Values | Meaning |
|---|---|---|
| Dependency satisfied | `YES` · `NO — <predecessor>` | Whether every SQ-constrained predecessor is discharged at baseline |
| Authority available | `YES (engineering)` · `NO — decision` · `NO — owner act` · `NO — external` | Whether an authority competent to admit the change is located |
| Evidence available | `YES` · `PARTIAL` · `NO` | Whether the evidence required to justify and close the change exists at baseline |
| Validation available | `VR-nn` · `VR-nn (instrument absent)` | Whether the validation requirement is executable at baseline |
| Certification available | `PROV` · `PROV after CR-21` · `NO — <act>` | Attainability at the `CERTIFIED-PROVISIONAL` ceiling |
| Execution state | `EXECUTABLE` · `CONDITIONAL` · `BLOCKED` · `PROHIBITED` | The decision |

---

## 5. Foundation Readiness

**Question: can foundation transformation begin?**

**Answer: YES — and only foundation transformation may begin.** The foundation layer is the sole domain containing EXECUTABLE transformations, and it contains all ten of them.

### 5.1 Readiness of the five foundation elements

| Element | State at baseline | Evidence | Readiness to transform |
|---|---|---|---|
| **Canonical knowledge** | Mechanism sound, population thin. 549/549 concepts homed; **25.5% canonically declared**; the loader that would make the kind space canonical works and has **no committed document to read** (M-D). Artifact-layer reconstruction proven byte-identical from a bare fresh clone (`S-12`, `RTBD-001`) | B-1 F-13.1/F-13.2; B-5 T-6.1 step 6 | **READY.** One committed document plus one load call. REUSE, not build |
| **Truth authority** | Two chains implemented, neither declared governing. Chain A (canonical → reconstruction → validation → projection) holds at the artifact layer only. Chain B (canonical → bootstrap → mutable runtime state → truth) is in force on **every open surface**. **Two** process-global mutable authorities, both leaking across capabilities | B-2 §15.1; RA-01…RA-13, RA-12 | **PARTIALLY READY.** T-6.1 and T-26.1 are EXECUTABLE; declaring which chain governs (T-8.2) is an authority act |
| **Evidence model** | Fail-closed and anti-fabricating, and closed. `EvidenceKind` is a 6-member fail-closed enum (C-23, defect); 12 truth facets have no declared owner; 4 of 11 assimilation stages have no truth owner | B-2 TA-22, TA-27; C-23 | **NOT READY to open.** T-22.1 is CONDITIONAL behind EP-4: registrable evidence kinds could let a data edit declare weak evidence constitutive (**R-52, CRITICAL**) |
| **Runtime independence** | **Fails on one axis only, and it is the decisive one.** Independence holds on every classical axis (clock, path, storage, locale) and fails on **call history**. 43 of 72 kinds runtime-dependent; 13 truth objects at 4 SUPPORTED / 2 PARTIAL / 7 UNSUPPORTED; 20 runtime-authority violations, **13 of which resolve through a single artifact** | M-B; B-2 TA-25/TA-26; B-5 §26 | **READY.** T-6.1 + T-26.1 + T-19.1. The highest-leverage work in the programme |
| **Deterministic validation** | **PARTIALLY DETERMINISTIC.** Core-kind validation (29 kinds) deterministic; extension-kind validation and minting (43 kinds) runtime dependent; UCKP URN, UMK kernel and the 6-digit repository regex deterministic. Root cause `DV-11`: a derivable kind space that is not derived. **One** true missing capability: committed-data kind resolution | B-4 §15.2; M-B | **READY.** The information required to make validation deterministic is already committed to the repository; it is reached through mutable module state rather than read from source |

### 5.2 The ten EXECUTABLE foundation transformations

Each entry carries the nine required fields. All ten are drawn from B-5 §34.3 and are the complete EXECUTABLE population of this determination.

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-19.1** | Single-process determinism harness; zero of 29 gates vary initialization order (`determinism/reproduce.py:275-330`; RA-14, RA-15; T-14) | Initialization-independence measurement: statefulness is detectable | **YES** — no predecessors | YES (engineering) | YES — CH-2 named, harness located | VR-01 (instrument is the deliverable) | PROV | **EXECUTABLE** |
| **T-19.2** | R-09 declared with no predicate; `classify()` → `ERROR` for every subject (M-C; RA-20; C-39) | Total mutation classification across all nine classes | **YES** — no predecessors | YES (engineering) | YES — M-C reproduced | VR-40 | PROV | **EXECUTABLE** |
| **T-21.1** | Unrestricted `importlib` from unvalidated JSON, invoked **before** validation (`universal_provider/discovery.py:404,424`; CH-5; T-13) | Trust → validation → import: no execution from an unverified descriptor (TI-5) | **YES** — no predecessors | YES (engineering) | YES — CH-5 located; trust machinery exists two modules away | VR-47 | PROV | **EXECUTABLE** |
| **T-6.1** | Identity kind space held in mutable module globals; validity a function of process history (M-B; RA-01…RA-11, RA-13) | Kind space as canonical knowledge; deterministic resolution on load (TI-1 + TI-2) | **YES within wave** — requires T-19.1 first (SQ-1); no external predecessor | YES (engineering) | YES — loader exists at `ceu/existence.py:773`, measures losslessness at `:868` | VR-01, VR-02 | PROV | **EXECUTABLE** |
| **T-26.1** | `DEFAULT_VOCABULARIES` a second process-global mutable authority (`vocabulary.py:542`); 230 of 239 closures undisclosed (RA-12; M-A; CR-23) | Vocabularies persisted and reconstructed; every closed enumeration disclosed | **YES within wave** — parallel to T-6.1, verified by T-19.1 | YES (engineering) | YES — `is_extensible` enumerates vocabularies; `check_open_world` already detects closure | VR-02, VR-62 | PROV | **EXECUTABLE** |
| **T-13.1** | Cyclic relationship registered, then refused (`ceu/existence.py:989-1006`; RA-19) | Refuse before register; no edge survives a refused registration | **YES** — independent, single site | YES (engineering) | YES — site located | VR-21 | PROV | **EXECUTABLE** |
| **T-23.4** | Certification chains unverified on load; `verify()` unconditionally `True`; one registry non-monotonic; a re-mint disguised as replay (RA-17, RA-18) | Verify-on-load; `verify()` returns `False` for an unverifiable record | **YES** — independent, three sites | YES (engineering) | YES — sites located | VR-57 | PROV | **EXECUTABLE** |
| **T-14.2** | Headline closure verdict depends on an out-of-repository corpus and an environment variable (`closure_engine.py:74,176`; RA-16; T-11) | Closure verdict reproducible from a bare fresh clone with no environment variables set | **YES** — independent | YES (engineering) | YES — both sites located | VR-25 | PROV | **EXECUTABLE** |
| **T-17.3** | Connector schema closed and already drifted: runtime `SOURCES` extended twice, neither appears in the schema (C-34, C-35) | One authority for the source vocabulary; schema and code cannot diverge | **YES** — independent of the protocol question | YES (engineering) | YES — drift measured | VR-37 | PROV | **EXECUTABLE** |
| **T-24.4** | Five scale-local closure clauses contradicting the expansion mandate (C-47) | No architectural bound token survives unclassified | **YES** — independent | YES (engineering) | YES — clauses located | VR-61 | PROV | **EXECUTABLE** |

### 5.3 Why these ten and no others

Three properties hold for all ten and for no other transformation in the population:

1. **No unmet predecessor.** Eight have no dependency at all; T-6.1 and T-26.1 depend only on T-19.1, which is itself in the set.
2. **No authority decision.** None of the five open questions (CH-6, T-17.1, T-18.1, autonomy, ownership ratification) gates any of them. **EP-4 does not apply**: B-5 §27.4 establishes that ownership gates neither detection, durability nor trust.
3. **No CREATE.** All ten are REUSE or EXTEND against mechanisms already proven in-repo. Three of them are approximately **one predicate function** (T-19.2), **one committed document plus one load call** (T-6.1), and **three edits** (T-21.1).

### 5.4 The asymmetry that defines the execution boundary

| Transformation | Approximate size | Defect chain closed | Consequence |
|---|---|---|---|
| T-19.2 | ~1 function | CH-3 | Restores classification of every change in every dimension |
| T-6.1 | 1 artifact + wiring | CH-1 | Resolves RA-01…RA-11 and RA-13; 43 of 72 kinds; 9 enforcement sites |
| T-21.1 | ~3 edits | CH-5 | Closes the sole CRITICAL security defect |

Three of the seven defect chains — including the two that gate everything else — are closed by approximately one function, one document and three edits. **This asymmetry is the reason a NOT READY programme has a safe entry point.**

### 5.5 Foundation readiness verdict

> **Foundation transformation MAY BEGIN, bounded to the ten transformations in §5.2, executed under the intra-wave ordering of §18 (W0), and claiming no success until T-23.3 instrumentation exists (EP-7).**

No other domain contains an EXECUTABLE transformation. Every readiness section that follows is a statement about what is *held*, and by what.

---

## 6. Classification Readiness

### 6.1 The current state

```
classify(subject)  →  status = 'ERROR'      for every subject in the repository
```

`RULE_PREDICATES` implements R-01…R-08. `mutation-governance-boundary.json` declares nine classes and nine rules. `validate_rule_coverage()` returns:

```
("rule 'R-09' is declared but no predicate implements it",)
```

One declared rule has no predicate, and the classifier is total-or-nothing: it fails closed for **all** subjects, not only R-09 subjects. `UNRESOLVED` fails closed and is documented as never a permissive default.

### 6.2 The required closure chain, assessed link by link

```
Change  →  Classification  →  Impact  →  Authority  →  Validation
```

| Link | State at baseline | Transformation | Execution state |
|---|---|---|---|
| **Change** | Detectable but not measurable as intent. 38 tracked modifications sit in the working tree unanalysed; B-7 §3 condition `0.6` (isolate the dirty tree by owning programme) is **currently failing** | Out of scope — a programme hygiene precondition, not a transformation | — |
| **Classification** | **NON-FUNCTIONAL** (M-C). One missing predicate | **T-19.2** | **EXECUTABLE** (W0) |
| — extension | Mutation class extension is *"a SPECIFICATION, not an implementation"*; the current defect exists **because a class was registered without a predicate** | **T-19.3** — extension must refuse predicate-less classes at registration (VR-41) | **CONDITIONAL** — SQ-3, after T-19.2 |
| **Impact** | Impact analysis exists and is **unwired**; substrate coverage is **10.4%** (5 substrates; C-43) | **T-19.5** — wire impact, and disclose coverage with every verdict | **CONDITIONAL** — after T-19.1 (EP-1) |
| — coverage | Selection narrowing over unverified coverage converts fail-wide into fail-silent | **T-13.3** — substrate coverage expansion, **strictly after detection** | **CONDITIONAL** — SQ-7; **R-24 CRITICAL** if started early |
| **Authority** | Three mutually disclaiming planes, **no shared key**; declaration and enforcement *"do not share a key"* | **T-22.2** | **CONDITIONAL** — authority decision |
| **Validation** | Real and fail-closed, and **process-dependent** (M-B); 6 of 15 chain stages unvalidated; `verify.sh --full` **exits 1** on 4 of 15 stages | **T-6.1** for determinism; baseline repair is a B-7 Wave 1 precondition | **EXECUTABLE** (T-6.1) / precondition (baseline) |

### 6.3 Classification-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-19.2** | R-09 declared, no predicate; `classify()` ERROR for all subjects | Total classification across nine classes | YES | YES (engineering) | YES — M-C | VR-40 | PROV | **EXECUTABLE** |
| **T-19.3** | Mutation class extension is a specification, not an implementation (C-39) | New mutation classes registrable; predicate-less classes refused **at registration** | **NO — T-19.2** (SQ-3) | YES (engineering) | YES | VR-41 | PROV after CR-21 | **CONDITIONAL** |
| **T-19.5** | Impact analysis exists and is unwired; 10.4% substrate coverage | Impact wired; every verdict discloses its coverage | **NO — T-19.1** | YES (engineering) | YES | VR-43 | PROV after CR-21 | **CONDITIONAL** |
| **T-13.3** | Relationship traversal deliberately partial; substrate coverage one tenth (C-42, C-43) | Coverage measured before and after; fail-wide remains default for uncovered subjects | **NO — T-19.1** (SQ-7) | YES (engineering) | PARTIAL — coverage unmeasured at baseline | VR-23 | PROV after CR-21 | **CONDITIONAL** |
| **T-26.2** | 29 hand-authored gates, 46 Makefile targets, no gate register, `check_open_world` never applied to the gate population (C-48) | Gates are a registered population subject to the openness test they enforce | **NO — T-19.2** (gates classify mutations) | YES (engineering) | YES — C-48 measured | VR-63 | PROV after CR-21 | **CONDITIONAL** |
| **T-23.3** | 16 unboundedness axes CERTIFIED UNBOUNDED on prose citation alone; Axes 13–14 contradicted by measurement | Each axis has an executable probe | **NO — T-19.1** | YES (engineering) | YES — contradiction measured | VR-56 (**Axes 13–14 currently fail**) | PROV — **and is the precondition for all other CR** | **CONDITIONAL** |
| **T-21.3** | Adversarial-input handling is one narrow scanner with an adjacent bypass; `record()` docstring/implementation mismatch (P-12) | Uniform adversarial bounds; identical secret handling across entry points | YES — independent | YES (engineering) | YES — mismatch located | VR-49 | PROV after CR-21 | **CONDITIONAL** |

### 6.4 The measurement problem beneath the classification problem

Classification and measurement fail together and for the same structural reason: **the repository can assert but cannot instrument.**

- 16 unboundedness axes are certified on prose; **no axis cites executable code, a test, a digest, or a reproducible instrument**.
- No machine certificate confers constitutional finality (`UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"`).
- ~15 root-level certifications assert completeness without evidence binding.

**CR-21 must be discharged before any other certification is credible** (EP-7 / SQ-9). Until T-23.3 exists, a claim that a transformation succeeded would be recorded in exactly the evidential form the baseline determinations have shown to be unreliable — *including a claim about this programme*.

### 6.5 Classification readiness verdict

> **Classification restoration is EXECUTABLE (T-19.2, W0). Classification extension, impact wiring, coverage expansion, gate self-application and axis instrumentation are CONDITIONAL on W0 exit.** Until T-19.2 lands, every transformation in this determination is itself an unclassifiable mutation, and EP-2 forbids executing any of them — including, strictly, the other nine EXECUTABLE items. §18 resolves this by ordering T-19.2 and T-19.1 first inside W0.

---

## 7. Ownership Readiness

### 7.1 The measured position

| Figure | Source | Value |
|---|---|---|
| Subjects unowned | `UCOD-001` / B-5 | **391 of 542** (151 owned = 27.86%) |
| Subjects unowned | B-6 | **398 of 549** (151 declared = 27.5046%, **and falling**) |
| Ratified | both | **0%** |
| Governed assignment catalogue | both | **empty** |
| Authority planes | `CANONICAL-AUTHORITY-DETERMINATION.md` | **three**, mutually disclaiming, *"declaration and enforcement do not share a key"* |
| Multi-dimensional ownership | `OWN-REQ-002` (X-12) | **constitutionally excluded** |
| Machinery | `UCOD-001:332` | **production-ready**; data 27.86% populated |

The variance between the two figures is disclosed in §2.6 and carried unresolved. On either figure the ownership property is unsatisfied for a majority of subjects.

### 7.2 What ownership means, in this repository's terms

Ownership is not attribution and not authorship. It is the **located competence to admit a change to a subject**. Four properties are structural, and each constrains execution:

| Property | Mechanism | Execution consequence |
|---|---|---|
| **Fail-closed** | `require_owner()` raises `OwnershipFabricationError` rather than infer | An unowned subject cannot be governed-changed at all; it does not default to permissive |
| **Anti-fabricating** | The machinery refuses to derive an owner from evidence it does not have | Automated population is not a shortcut; it is the specific failure the design prevents |
| **Grain-declared** | Granularity is declared, not hardcoded (`S-11`) | Ownership can be resolved at a declared grain without opening the grain vocabulary |
| **Evidence-bound** | Admission checks registration and canonical-home admissibility **before** accepting evidence | Evidence kinds carry authority; opening that vocabulary is an authority act, not a data edit (**R-52 CRITICAL**) |

### 7.3 The three-way partition the directive asks for

#### 7.3.1 What can be discovered automatically

| Discoverable | Basis | Limit |
|---|---|---|
| **Whether a subject is owned** | Resolution is already implemented and fail-closed | Measurement only; discovers absence, never an owner |
| **Whether an ownership row resolves to a machine-readable key** | T-22.2 makes this measurable | Making rows machine-readable **exposes rows that do not resolve** (R-53) — intended effect |
| **The unowned population and its trend** | B-6 measures 398/549 and records coverage *falling* | Trend is measurable; direction is not correctable by measurement |
| **Canonical-home admissibility** | 549/549 concepts homed; `UAKOS-CLOSURE-002` reports concepts=549, gaps=0 across seven homing checks | Homing is not ownership. A concept can be perfectly homed and entirely unowned — this is precisely the current state |

**Automatic discovery closes the measurement gap and none of the authority gap.**

#### 7.3.2 What requires human or constitutional authority

| Requires authority | Which authority | Why no engineering path exists |
|---|---|---|
| **The 391 (or 398) ownership assignments** | Each subject's owner, plus `CEP-002` | `UCOD-001:401`: the determination *"will not fabricate them to close it."* **R-54 (CRITICAL):** automated population is exactly the fabrication the machinery is built to refuse |
| **Ratification of any assignment (0% today)** | A competent ratifier | `MP2-C-04`: three located instruments record **no authority in the corpus competent to ratify**. `VAC-01`: Tier T1 vacant |
| **The machine-readable authority key** | An authority spanning the three disclaiming planes | T-22.2. Declaration and enforcement do not share a key; inventing one would create a fourth plane |
| **Evidence-kind constitutive status** | Constitutional authority | R-52: a registrable evidence kind could let a data edit declare weak evidence constitutive, **fabricating ownership** |
| **UKAP/UREE registration** | `CEP-002` **Article 28** — external | *"no competent ratifying authority located within the repository"*; and F-20 records two determinations disagreeing on whether the block exists |

#### 7.3.3 What cannot proceed without ownership

| Held transformation | Why ownership precedes it |
|---|---|
| **T-14.1** knowledge declaration 25.5% → 100% | A concept declared canonical without a ratified owner becomes canonical truth nobody can amend (**R-25**) — **BLOCKED** |
| **T-24.3** autonomous evolution | An autonomous mutation of an unowned subject is ungoverned by construction — **PROHIBITED** |
| **T-19.4** source self-modification | Same, applied to source — **PROHIBITED** |
| **T-14.3** assimilation binding | The Ownership stage of the chain resolves against an **empty catalogue** — **CONDITIONAL** |
| **T-22.4** capability admission | The admitting authority is itself unowned (`Owner: UNCLEAR / Authority: UNCLEAR`) — **BLOCKED** |
| **T-23.2** certification subject genericity | A certificate names a target; an unowned target has no accountable subject — **CONDITIONAL** |

#### 7.3.4 What ownership does **not** hold

This is the finding that makes a NOT READY programme executable at all:

> **Ownership gates neither detection, nor durability, nor trust.** T-19.1, T-19.2, T-6.1 and T-21.1 are all independent of CH-4 and all EXECUTABLE. The programme is **not stalled by ownership**, because the four highest-impact transformations sit upstream of it. (B-5 §27.4)

### 7.4 Ownership-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-22.1** | `EvidenceKind` 6-member fail-closed enum; standings, reasons, grains closed (C-23, C-24, C-25) | Evidence kinds registered; a kind without a declared role is refused | YES (engineering path clear) | **NO — decision** on constitutive status (R-52 CRITICAL) | YES | VR-50 | PROV after CR-21 | **CONDITIONAL** |
| **T-22.2** | Authority partitioned across three mutually disclaiming planes with no shared key | Every ownership row resolves to a machine-readable key; declaration joins enforcement | YES | **NO — decision** | YES — measured | VR-51 | **NO** — authority act | **CONDITIONAL** |
| **T-22.3** | 391 of 542 unowned; catalogue empty; 0% ratified | Every admitted subject resolves to exactly one ratified owner, or admission fails closed (TI-4) | **NO — T-22.2** (SQ-12) | **NO — owner act** | YES — measured | VR-52 | **NO** — ratification | **BLOCKED** |
| **T-22.4** | Capability admission authority unregistered and externally blocked; F-20 contested | The admitting authority is registered, or the external dependency is declared | NO | **NO — external** (`CEP-002` Art. 28) | PARTIAL — F-20 live | VR-53 | **NO** — external act | **BLOCKED** |
| **T-8.2** | Two coexisting truth models, neither governing | Every artifact resolves to exactly one governing truth model | YES | **NO — decision** (same missing key as T-22.2) | YES | VR-10 | **NO** — authority act | **CONDITIONAL** |
| **T-15.3** | Six mutually incompatible lifecycle models; determination artifacts have **no lifecycle at all** | Every artifact resolves to exactly one lifecycle authority | YES | **NO — decision** | YES | VR-30 | **NO** — authority act | **CONDITIONAL** |
| **T-14.1** | Canonical declaration 25.5% while homing is 100% | Declaration coverage stated; no concept declared canonical without a ratified owner | **NO — T-22.3** | **NO — owner act** | YES — measured | VR-24 | **NO** — ratification | **BLOCKED** |
| **T-14.4** | `KnowledgeStore` filesystem-bound; storage neutrality **declined** on four criteria; frozen-corpus guard silently succeeds under substitution | Storage boundary declared; the guard **fails**, never silently succeeds | YES for the guard leg | **NO — decision** on the neutrality question | YES | VR-27 | PROV for the guard leg | **CONDITIONAL** |

**Note on T-14.4.** The guard defect (**R-28, HIGH**) is independent of the storage-neutrality decision and must be fixed regardless of how that decision goes. It is held here only because the domain decision is undecided; a decision to fix the guard alone would move that leg to EXECUTABLE without touching the neutrality question.

### 7.5 The ownership chain

```
T-22.2  machine-readable authority key            (CONDITIONAL — decision)
   │
   ├──► T-6.2  identity mint federation           (CONDITIONAL — same missing key)
   ├──► T-8.2  governing truth model              (CONDITIONAL — same missing key)
   │
   ▼
T-22.1  evidence kinds registered                 (CONDITIONAL — R-52 gate)
   │
   ▼
T-22.3  391 assignments populated and ratified    (BLOCKED — owner act)
   │
   ├──► T-14.1  knowledge declaration 25.5% → 100%   (BLOCKED)
   ├──► T-24.3  autonomous evolution                  (PROHIBITED)
   └──► T-22.4  capability admission authority        (BLOCKED — external, Article 28)
```

### 7.6 Ownership readiness verdict

> **NOT READY, and no engineering sequence makes it ready.** Two ownership transformations terminate outside the repository. Full transformation cannot complete without an owner act. **Execution of the foundation layer does not require ownership and may proceed without it** — but nothing may be *declared canonical*, *admitted under governance*, or *autonomously changed* until EP-4 is satisfied.

---

## 8. Identity Readiness

### 8.1 The required transition

```
Finite representation  →  Universal Identity Capability
```

### 8.2 The measured position on each required element

| Element | State | Evidence | Readiness |
|---|---|---|---|
| **Namespace** | **Open and sound.** Namespace/local regexes are open by pattern with **no allow-list** (P-07, P-08 — both invariants). `engine/kernel/identity.py` accepts **any Unicode** non-whitespace segment | B-5 §25.2 | **Already universal — PROHIBITED to change** |
| **Authority** | **NOT READY.** Three independent mint schemes plus a fourth in the assimilation framework whose identity no registry can resolve — *"structurally unreconcilable with any constitutional identity."* Governance model is `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` with *"No universal identity authority created."* Declared and simultaneously un-declared in the same file; enforcement test blind to 9 of 13 shapes; no competent ratifier | B-3 §14.1; B-5 T-6.2 | **CONDITIONAL — authority decision** |
| **Representation** | **NOT YET ASSIMILATED.** 13 shapes, 58 prefixes across 53 files, 4 alphabets, one CI-enforced 6-digit regex (`^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$`), **no codec, no scheme version, no migration**. `alignment.py:307-308` raises on ≠6 digits; `test_alignment.py:97-103` asserts width-3 must raise. **A format that raises is a format** | B-3 §14.2 | **CONDITIONAL — sequenced** |
| **Separation of semantics from representation** | **NOT YET ASSIMILATED.** The rendered string is a stored invariant and the UUID is computed over it — `uuid5` over the rendered string means **representation change is indistinguishable from tampering** and fails `verify()` | B-3 §14.1 | **CONDITIONAL — the hard blocker on representation evolution** |
| **Lineage** | **PARTIALLY.** Supersession is complete and round-trippable **within CEU** (split/merge/transform/deprecate, appending). No per-identity version; migration determined absent (IDF-17); no resolver spans prefixes; no historical resolution (IDF-15) | B-3 §14.2 | **CONDITIONAL** |
| **Evolution** | **PARTIALLY.** Open on the *kind* axis (`register_kind`, `declare_form`, `ContextTaxonomy.extend` — all tested). Closed on the *representation* axis. Population ceiling of **10⁶ per family** from a regex quantifier | B-3 §14.1 | **CONDITIONAL** |
| **Migration** | **ABSENT.** Path-keyed `allocate()` mints a new id on rename **with no back-pointer**; `derive_change_events` **drops** stale subjects rather than redirecting (`ukb.py:347-366`); `data/entity.py:260` embeds a mutable name in the identity | B-3 §14.2 | **CONDITIONAL** |
| **Determinism of validity** | **DEPENDENT on execution history for 43 of 72 kinds.** Minting is pure and clock-free on every plane; validation is pure on three planes and process-dependent on **the one plane that implements openness** | B-4 §15.1–15.4; M-B | **EXECUTABLE via T-6.1** |

### 8.3 The one-line summary the evidence supports

> *UCOS Ω∞ purchased infinite kind extensibility with process state, and the receipt is that identity validity is no longer a property of the identity.* (B-4 §15.3)

The information required to make validation deterministic **is already committed to the repository**; it is reached through mutable module state rather than read from source. That is why the fix is REUSE, not build.

### 8.4 Identity-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-6.1** | Validity decided against mutable module globals populated only by `bootstrap()` (M-B); 43 of 72 kinds; 9 enforcement sites incl. the sole constitutional mutation gateway | Identity kinds are canonical knowledge; a fresh validator honours every registered kind (TI-1 + TI-2) | YES within W0 (after T-19.1, SQ-1) | YES (engineering) | YES — loader exists, journal-verifying, measures losslessness | VR-01, VR-02 | PROV | **EXECUTABLE** |
| **T-6.2** | Three irreconcilable mint pathways plus a fourth in assimilation; no crosswalk; no governing declaration | Identity resolvable across planes: a crosswalk exists, or one plane is declared governing | YES | **NO — decision** (and T-22.2 shares the missing key) | YES — all four planes located | VR-03 | **NO** — authority act | **CONDITIONAL** |
| **T-6.3** | `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` — 10⁶ ceiling per family (ZF-1; P-01, P-13) | Identifier representation carries no cardinality ceiling | **NO — T-6.1** (durability of any new family), **T-15.1** (same schema) | YES (engineering) | YES — `dictionary.py` already emits `"closed_set": False, "upper_limit": None` | VR-04 (**all 1,461 artifact records must remain valid**) | PROV after CR-21 | **CONDITIONAL** |
| **T-6.4** | Extension kind code `[A-Z][A-Z0-9]{1,7}` — ASCII-only (P-09) | Codes are opaque registered tokens, not constrained glyph sequences | **NO — T-6.1** | YES (engineering) | YES — `engine/kernel/identity.py` already accepts any Unicode; the pattern to follow exists in-repo | VR-05 | PROV after CR-21 | **CONDITIONAL** |
| **T-6.5** | `engine/object_birth/` implements identity-before-existence and **zero production callers**; only two tests and one CLI gate subprocess | Every first-class entity is born through the declared contract | **NO — T-6.2** (else wired to one of three irreconcilable planes) | **NO — decision** | YES | VR-06 | **NO** — authority act | **CONDITIONAL** |

### 8.5 The risk that governs identity execution

| Risk | Severity | Constraint |
|---|---|---|
| **R-02** | HIGH | Declaring one mint governing invalidates identifiers already issued by the others; a federation crosswalk **must not itself become a second identity authority** — `CAA-INV-04` forbids one |
| **R-03** | MEDIUM | The identifier pattern is mirrored in **at least three** places; divergence reproduces the C-34/C-35 drift failure already on record. T-17.3 (EXECUTABLE, W0) establishes the drift-prevention pattern this needs |
| **R-05** | HIGH | Wiring birth into hot paths risks minting as a side effect. Precedent: **140 permanent identifiers minted by a drift check**. Birth only on declared intent, never as a side effect |
| **R-01** | HIGH | The existing reconstruction test's fixture calls `bootstrap()` — it **cannot** detect failure of T-6.1. T-19.1 must exist first |

### 8.6 Identity readiness verdict

> **Identity durability is EXECUTABLE and is the highest-leverage transformation in the programme** — T-6.1 alone closes CH-1, resolves 13 of 20 runtime-authority violations, and unblocks every kind-openness transformation. **Identity representation, federation, migration and birth adoption are CONDITIONAL**, and three of the four are held by one undecided question: which mint governs, or how they federate. No identity transformation is BLOCKED, and none is PROHIBITED except changing the namespace patterns (P-07, P-08), which are already universal.

---

## 9. Entity Readiness

### 9.1 The required chain

```
Unknown existence  →  Entity recognition  →  Identity  →  Context  →  Evolution
```

### 9.2 Chain assessment, link by link

| Link | State at baseline | Evidence | Held by |
|---|---|---|---|
| **Unknown existence** | **Sound and first-class.** `SystemType.UNKNOWN` is an invariant (C-50). Unknown inputs are deferred with a reason rather than rejected. `unknown` is a first-class member of the measurement registry. `UAUE` obligation #6 conducts a genuine open-world admission proof on an unowned, unclassed, unregistered subject | C-50; B-1; B-6 | **Nothing — this link works** |
| **Entity recognition** | **Nothing to recognise against.** `EXISTENCE`, `RELATIONSHIP`, `TRANSFORMATION` exist as string ids in a declaration a gate cross-checks against **prose**. No `Primitive` class. GAP A-1: they *"appear in no `.py` and no `.json` file… only as markdown prose."* No UCKO references `ONT-01…ONT-04`. The ontology is **measured, never instantiated** | `P1-A-01` §3; `ucpa-declaration.json` | T-7.1, held by T-6.1 |
| **Identity** | Runtime-dependent for 43 of 72 kinds; entity kinds admitted **only in process memory** | M-B | T-6.1 — **EXECUTABLE** |
| **Context** | Graph-node entity types are a closed 6-tuple (C-07); value types a closed 5-tuple (C-08); context relations closed by construction (C-06) | §25.1 | T-7.2, T-9.x — held by T-6.1 |
| **Evolution** | Non-termination structurally guaranteed (`is_terminal` returns `False` because **no state could return `True`**) — sound and must be preserved | `S-08` | **Nothing — PROHIBITED to change** |

### 9.3 Entity-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-7.1** | Root primitives not instantiable; ontology measured against prose, never instantiated | An unknown existence is recognised by anchoring to a root primitive, then acquires identity, context and an evolution path | **NO — T-6.1** (else anchors evaporate) | YES (engineering) — additive to the existing measurement gate | YES — `engine/root_ontology/{model,contract,gate}.py`; the 33-row `facet_reduction` map already binds every facet to a primitive; `UCKO.ontology: OntologyRef` already exists | VR-07 (`UCPA-L-04` must still hold) | PROV after CR-21 | **CONDITIONAL** |
| **T-7.2** | `ENTITY_TYPES` closed 6-tuple (`context/ontology.py:37-44`; C-07) | A probe node type is admissible; relation rules remain total | **NO — T-6.1** (SQ-6) | YES (engineering) | YES | VR-08 | PROV after CR-21 | **CONDITIONAL** |
| **T-7.3** | Entity kinds admitted only in process memory | Admitted entity kinds survive process death (TI-1) | **NO — T-6.1** — *this is T-6.1 seen from the entity dimension* | YES (engineering) | YES | VR-01, VR-02 | PROV | **CONDITIONAL** |

### 9.4 The two risks that bound entity execution

| Risk | Severity | Constraint |
|---|---|---|
| **R-06** | HIGH | The four primitives are **ratified**. Instantiating them must not become a path to **amending** them. `UCPA-L-04` (nothing reduces to the axiom) must continue to hold |
| **R-07** | HIGH | Opening node types permits **unbounded edges** — the exact condition `ContextOntology.__init__` refuses. Rule totality must hold over the widened set at every instant |

### 9.5 Entity readiness verdict

> **NOT READY, and entirely downstream of identity durability.** All three entity transformations are CONDITIONAL on T-6.1, and T-7.3 *is* T-6.1 viewed from the entity dimension. The `unknown` end of the chain and the non-termination end are both sound; the gap is the middle, and one EXECUTABLE transformation opens it.

---

## 10. Context Readiness

### 10.1 The measured position

Context is the domain with the **most transformations classified READY and the cheapest available proof of openness anywhere in the programme**.

| Constraint | Location | N | Class |
|---|---|---|---|
| `ContextKind` | `context/taxonomy.py:64-79` | 16 | representation |
| `ContextAuthority` | `taxonomy.py:107-140` | 5 | implementation limitation |
| `ContextLifecycle` | `taxonomy.py:152-214` | 8 | implementation limitation |
| `ContextRelation` | `taxonomy.py:240-275` | 11 | implementation limitation |
| `VALUE_TYPES` | `ontology.py:47` | 5 | implementation limitation |
| `REALITY_CONTEXT_AXES` | `location.py:84-90` | 5 | representation |
| `AXIS_DERIVATION` | `location.py:90-116` | ~19 | implementation limitation |

Three of these vocabularies — authority, lifecycle and relation — have **no extension mechanism at all**, which distinguishes them from `ContextKind`.

Separately: **context is populated with the repository's self-description, one instance per kind.** Nothing has ever resolved a second, disjoint context set.

### 10.2 What is already universal in this layer and must survive

| Property | Mechanism | Constraint on execution |
|---|---|---|
| No axis value in code | `engine/context/location.py` — grep it for a calendar name and there is none | `PROHIBITED_TOKENS` and the **zero-axis root frame** must survive (R-15, R-16) |
| No defaults; `UNRESOLVED` with a derivation path | same | The pattern T-8.1 and T-16.1 must copy |
| 14 reference frames already resolving | off-world, orbital, virtual, distributed, interstellar | VR-09: all 14 must resolve **identically** before and after axis migration |
| Identity deliberately outside the context derivation chain | verified **0** occurrences of an `identity` axis across the 19 declared axes | B-3 §14.4 determines this posture **defensible**. The gap is the unwired facet (IDF-13), not the purity |

### 10.3 Context-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-9.1** | `ContextKind` closed 16-member enum (C-03) | A probe kind is admitted, persisted, and honoured by a fresh validator (TI-3) | **NO — T-6.1** (SQ-6) | YES (engineering) — **except** the universal flag, which requires constitutional authority | YES | VR-12 | PROV after CR-21 | **CONDITIONAL** |
| **T-9.2** | Context authority, lifecycle and relation vocabularies have **no extension mechanism at all** (C-04, C-05, C-06) | Vocabularies open with precedence total and every relation retaining a rule | **NO — T-6.1**, and **T-15.3** for lifecycle (SQ-8) | YES (engineering) | YES | VR-13 | PROV after CR-21 | **CONDITIONAL** |
| **T-9.3** | `VALUE_TYPES` closed 5-tuple (C-08) | A probe value type with a registered validator is admissible; an unvalidated type is refused | **NO — T-6.1** | YES (engineering) | YES | VR-14 | PROV after CR-21 | **CONDITIONAL** |
| **T-9.4** | Context populated with the repository's self-description; one instance per kind | Two disjoint context sets resolve **without code change** | **NO — Layer 3** (it is the empirical proof of Layer 3) | YES (engineering) | YES | VR-15 | PROV after CR-21 | **CONDITIONAL** |
| **T-8.1** | The mandatory reality-axis chain is code, not data (C-09, C-10) | Axis derivation as data, with the fail-closed reality gate refusing a shrinking axis set | **NO — T-6.1** | YES (engineering) | YES | VR-09 | PROV after CR-21 | **CONDITIONAL** |
| **T-8.3** | Reality modes are declarable and **inert**; `GOVERNED_CATEGORIES` includes `simulation` with no engine | A simulated-reality assertion **cannot be certified as actual** | **NO — T-23.2** (sequence after, R-10) | YES (engineering) | YES | VR-11 | PROV after CR-21 | **CONDITIONAL** |
| **T-10.1** | *No fixed locations exist to remove* | — the property is already held | n/a | n/a | YES — grep-verified absence | VR-09 (preservation test) | PROV as preservation | **PROHIBITED** |
| **T-10.2** | No coordinate systems, geometry, or spatial-relation algebra (T-08, T-09) | A coordinate in an invented system is representable; an undeclared conversion is **refused, not improvised** | **NO — Layer 3** | YES (engineering) | YES — `engine/temporal/operations.py` supplies the register-never-infer pattern | VR-16 (`primary` **never** normalised) | PROV after CR-21 | **CONDITIONAL** |
| **T-12.1** | Measurement registry already universal; **conversions do not execute** (T-10) | Declared conversions reproduce; undeclared pairs refused; the term evaluator is total, pure and **non-eval** | **NO — Layer 3** | YES (engineering) | YES | VR-19 | PROV after CR-21 | **CONDITIONAL** |
| **T-12.2** | Currency hardcoded to `^[A-Z]{3}$`, contradicting frames already declared (P-03, T-03) — an **undisclosed** closure | Currency as a registered axis; cross-currency arithmetic remains refused | **NO — EP-6**: disclosure precedes remediation | YES (engineering) | YES — discovered by B-6 | VR-20 | PROV after CR-21 | **CONDITIONAL** |
| **T-11.1** | Temporal model built and **unadopted**; 3 importers | Baseline, birth, UCKO and evidence temporal claims carry qualified coordinates | **NO — T-11.2** | **NO — decision** (frame-at-mint policy) | YES | VR-17 | **NO** — authority act | **CONDITIONAL** |
| **T-11.2** | Baseline authority temporally unaware; **certifies dates its own contract refuses** (T-02) | No certification asserts a date its own contract refuses | YES | **NO — decision** (re-qualifying certified dates changes certified content, R-18) | YES | VR-18 | **NO** — authority act | **CONDITIONAL** |
| **T-11.3** | Five evidence emitters assume UTC/ISO-8601 (T-01) | Declared boundary between run timestamps and constitutional temporal claims | **NO — T-11.2** | YES (engineering), once the boundary is declared | YES | VR-17 | PROV after CR-21 | **CONDITIONAL** |
| **T-13.2** | Relationship types open in UCKP and **closed by construction** in context (C-06) | Relation members and rules co-registered atomically; rule totality holds after every registration | **NO — T-6.1** | YES (engineering) | YES — `RELATION_RULES` supplies the co-registration pattern | VR-13, VR-22 | PROV after CR-21 | **CONDITIONAL** |
| **T-15.2** | `DiscoveryKind` closed 8-member enum (ZF-5; C-13) | A ninth discovery dimension is admissible | **NO — T-6.1** | YES (engineering) | YES | VR-29 | PROV after CR-21 | **CONDITIONAL** |
| **T-21.2** | Entire security vocabulary closed; **no threat model as data** anywhere; `14-SECURITY/` is 5 prose files (C-18…C-22, C-49) | A probe threat class is admitted; blocking severities remain total | **NO — T-6.1** | YES (engineering) | PARTIAL — **TRUE MISSING** in part: no threat/attack-surface/trust-boundary/adversary model exists | VR-48 | PROV after CR-21 | **CONDITIONAL** |
| **T-23.2** | Certification subject type fixed by `isinstance`; `CertificationClass` is a **one-member** enum (C-17) | A novel subject type is certifiable without flattening; existing certificate digests unchanged | **NO — T-6.1**, **T-23.1** preservation constraints | YES (engineering) | YES | VR-55 | PROV after CR-21 | **CONDITIONAL** |
| **T-24.2** | `EvolutionStage` closed 15-member enum; the module itself states a **sixteenth is a code edit** (C-15, self-declared INV-14 breach) | A probe stage is admitted and ordered; the cycle still wraps | **NO — T-15.3** (SQ-8) | YES (engineering) | YES | VR-59 | PROV after CR-21 | **CONDITIONAL** |

### 10.4 The three risks that bound context and vocabulary execution

| Risk | Severity | Constraint |
|---|---|---|
| **R-11** | HIGH | If universality becomes registrable, a **data edit could declare an arbitrary kind universal**. The universal flag must require constitutional authority |
| **R-12** | HIGH | Registering an authority level **without a declared position** makes precedence partial and resolution non-deterministic. Position mandatory at registration — the same total-order hazard recurs at R-50 (severities) and R-61 (stages) |
| **R-23** | HIGH | Moving refusal to registration time may create a **window in which an unruled relation exists**. Co-registration must be atomic |

### 10.5 Context readiness verdict

> **NOT READY, and cheaply provable once durability lands.** Every context transformation is CONDITIONAL on T-6.1 alone — none is BLOCKED, none requires an authority decision except the universal flag, and none requires a new capability. **T-9.4 is the cheapest proof-of-openness available anywhere in the programme** (data only, lowest risk on the register at R-14) and should be understood as the empirical test of T-9.1 through T-9.3 rather than as separate work. **T-10.1 is PROHIBITED**: the directive's instruction to remove fixed locations has no target, because there are none.

---


## 11. Assimilation Readiness

### 11.1 The required chain

```
Assimilation  →  Security  →  Ownership  →  Validation  →  Certification  →  Evolution
```

### 11.2 Chain assessment, link by link

| Link | State at baseline | Evidence | Held by |
|---|---|---|---|
| **Assimilation** | **Fourteen admission surfaces exist.** The engines are real. The topology is *"three islands / one bridge / one one-way street"*; 6 of 13 categories are admissible. The decisive inherited finding: *"the obstacle is not a missing engine. It is a missing binding layer between fourteen engines that already exist"* | `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSIMILATION-FABRIC-DETERMINATION.md` — verdict **No** | T-14.3 |
| **Security** | **CH-5 unfixed.** The sole open-kind mechanism is an unrestricted `importlib` on an unvalidated JSON field, invoked **before** validation. Binding the planes while this stands routes untrusted input into arbitrary import | CH-5; T-13; SQ-4 | T-21.1 — **EXECUTABLE (W0)** |
| **Ownership** | **The Ownership stage of the chain resolves against an empty catalogue.** 391/542 unowned; 0% ratified. 4 of 11 assimilation stages have **no truth owner** | CH-4; B-2 TA-27 | T-22.3 — **BLOCKED** |
| **Validation** | Real and fail-closed, and **6 of 15 chain stages are unvalidated**; validity itself is process-dependent (M-B); `verify.sh --full` exits 1 on 4 of 15 stages | B-1 §35.3; M-B; B-6 | T-6.1 — **EXECUTABLE (W0)** |
| **Certification** | Mechanics sound (content-addressed, digest-anchored, deterministic ordering, injectable rules and frames — `S-10`). **One** certification class; no machine certificate confers constitutional finality | `S-10`; C-17; `UCERT_AUTHORITY` | T-23.2, T-23.3 — CONDITIONAL |
| **Evolution** | **The assimilation↔intelligence edge does not exist.** Two complete, mutually unreachable planes; *the feedback loop is prose*. Assimilation terminates in a measurement of itself | B-1 F-13.5; `…ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md` | T-14.3 |

### 11.3 The clause the chain fails on

B-1 §35.3 tested *"become understood"* and returned **No**, with this basis: the assimilation↔intelligence edge does not exist, the feedback loop is prose, and assimilation terminates in a measurement of itself. That is the defining knowledge-evolution gap, and it is the last link that closes, not the first.

### 11.4 Assimilation-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-14.3** | The assimilation↔intelligence edge does not exist; two complete mutually unreachable planes; the feedback loop is prose | An admitted source reaches a reasoner and produces a **recorded consequence** | **NO — five domains**: identity (T-6.1), context (T-9.x), relationship (T-13.2), security (T-21.1), impact (T-19.5) | YES (engineering) once predecessors land — **COMPOSE, not build** | YES — all 14 engines located | VR-26 | PROV after CR-21 | **CONDITIONAL** |
| **T-15.1** | Artifact schema closed in **four independent ways** (ZF-1…ZF-4): `LifecycleStatus` 17, `TRACE_STAGES` 13, `^VOL-[0-9]{3}$`, `additionalProperties: false` (C-11, C-12, P-02, P-11) | A probe artifact form is admitted **without code change**; all existing records remain valid | **NO — T-15.3** (SQ-8), and shares the schema with T-6.3 | **NO — decision** inherited from T-15.3 lifecycle authority | YES — all four closures located and named unfixed | VR-28 | PROV after CR-21 | **CONDITIONAL** |
| **T-15.4** | Serialization and storage already open; **adapters are document-shaped only** (T-12) | A non-document form is admitted; **an unregistered serialization still exists after transformation** (`S-04` must survive) | **NO — partially held by T-17.1/T-18.1 targets** | YES (engineering) for the adapter leg | YES | VR-31 | PROV after CR-21 | **CONDITIONAL** |

### 11.5 The two CRITICAL risks that govern assimilation execution

| Risk | Severity | Constraint |
|---|---|---|
| **R-27** | **CRITICAL** | *Binding the planes early routes unvalidated, unidentified, unowned, unsecured input into reasoning.* T-14.3 **must be last** among its five dependencies (SQ-4). Starting it early is the highest-severity sequencing error available in the entire programme |
| **R-32** | HIGH | A reader registered as data implies **code loaded as data** — T-15.4 must not reproduce CH-5 |
| **R-29** | HIGH | Replacing `additionalProperties: false` may permit unvalidated fields, so the schema **stops being a contract**. T-15.1 requires a declared-extension mechanism, never an open shape |

### 11.6 Assimilation readiness verdict

> **NOT READY.** No assimilation transformation is EXECUTABLE. T-14.3 is the single **REQUIRES FOUNDATION CHANGE** item in the population and is dependent on five domains simultaneously; it is correctly the last convergence step, not an entry point. The engines exist — 14 of them — and what is missing is a binding layer whose safe construction requires trust, durability, classification, ownership and impact all to be on the path first. **Assimilation activation is W5 and cannot advance.**

---

## 12. Security Readiness

### 12.1 The required model, assessed link by link

```
Input  →  Trust  →  Security  →  Impact  →  Validation  →  Execution
```

| Link | State at baseline | Evidence | Held by |
|---|---|---|---|
| **Input** | Open in shape and document-bound in form. Unknown inputs are deferred with a reason rather than rejected — sound. But unknown inputs are **document-shaped only**, and presently **unclassifiable** (M-C) | B-1 §35.3; T-12 | T-19.2 — **EXECUTABLE (W0)** |
| **Trust** | **Machinery exists and is unwired.** HMAC-SHA256 signer, key status model, allowlist concepts all present at `foundation/trust.py`. `KeyStatus` is a closed 3-member enum (C-27). The trust machinery that would prevent CH-5 sits **two modules away** from the hole | T-05; C-27; CH-5 | T-21.1 — **EXECUTABLE (W0)** |
| **Security** | **No threat model as data anywhere.** No threat, attack-surface, trust-boundary or adversary model exists; `14-SECURITY/` is 5 prose files. `FindingKind` (7), `Severity`, `FindingState`, `RollupState`, `ClassificationKind` (6), `SecurityZone`/`SecurityControl` (5/7) + 4 parallel dicts, `Permission` (4), `EXPOSURE_KINDS`/`BLOCKING_SEVERITIES`/`OPEN_FINDING_STATES` — **all closed** | C-18…C-22, C-49; B-1 dimension S = **NOT YET ASSIMILATED** | T-21.2 — CONDITIONAL |
| **Impact** | Exists and is **unwired**; substrate coverage **10.4%** | C-43 | T-19.5 — CONDITIONAL (W1) |
| **Validation** | Fail-closed and **process-dependent** (M-B); pre-validation execution is the defect | M-B; T-13 | T-6.1, T-21.1 — **EXECUTABLE (W0)** |
| **Execution** | **Occurs before trust and before validation.** `importlib.import_module` on an unvalidated JSON field at `universal_provider/discovery.py:404,424`, invoked **before** validation runs. Default execution subject is `"engineering"` (T-15) | CH-5; T-13; T-15 | T-21.1 — **EXECUTABLE (W0)** |

**The model is currently inverted at its most consequential point: execution precedes trust.** That inversion is CH-5, it is the sole CRITICAL security defect, and it is approximately three edits.

### 12.2 All admission paths — the assessment the directive requires

| Admission path | Trust check before execution? | Validation before effect? | Assessment |
|---|---|---|---|
| **Provider discovery** (`universal_provider/discovery.py:404,424`) | **NO** — unrestricted `importlib` on an unvalidated JSON field | **NO** — invoked pre-validation | **CH-5. The sole CRITICAL defect.** Also the **only** mechanism by which a genuinely unforeseen kind enters without a code change (PC-14) |
| **Vocabulary registration** (`uckp/vocabulary.py`) | n/a — data only, append-only, refuses redefinition | YES — register-then-use, openness proved by probe | **Sound** (`S-13`). Process-memory-only persistence is a durability defect (RA-12), not a trust defect |
| **Identity kind registration** (`registry/universal/identity.py:162-199`) | n/a — data only | YES | **Sound in trust; non-durable** (RA-02) |
| **Pipeline handler registry** (`platform/universal_pipeline/`) | YES — an unregistered handler **fails closed** | YES | **Sound** (`S-07`) |
| **Serialization registry** | YES — openness enforced bidirectionally; fails if nothing is left to admit | YES | **Sound** (`S-04`, and C-46 is an invariant) |
| **Ownership evidence admission** | YES — registration and canonical-home admissibility checked **before** accepting evidence | YES — fail-closed, `OwnershipFabricationError` | **Sound** (`S-11`) |
| **Adversarial input scanning** (`security/intelligence.py:74-92`) | Partial — one narrow scanner with an **adjacent bypass**; `record()` docstring and implementation disagree | Partial | **Defect.** Current reliance on `record()` is unfounded (R-51) |
| **Relationship registration** (`ceu/existence.py:989-1006`) | n/a | **NO** — a cyclic relationship is **registered, then refused** | **Validate-after-mutate. Same pattern as CH-5** (RA-19, R-22) |
| **Certification chain load** (RA-17, RA-18) | **NO** — no chain verification on load; `verify()` unconditionally `True` | **NO** | **Defect.** Current reliance is unfounded (R-59) |
| **Reasoner dispatch** (`uckp/intelligence.py`) | n/a — hardcoded dispatch, closed 13-member enum | n/a | Closed, therefore not an admission path today. Opening it **creates** one (R-47) |

### 12.3 Trust boundaries — as they actually stand

| Boundary | Enforced? | Note |
|---|---|---|
| Repository ↔ out-of-repository corpus | **NO** | The frozen-corpus guard **silently succeeds under substitution** (R-28, HIGH). The headline closure verdict depends on this corpus plus an environment variable (RA-16) |
| Data plane ↔ code plane | **NO at one site** | CH-5 crosses it. Everywhere else the boundary holds |
| Declaration ↔ enforcement | **NO** | Three disclaiming planes, *"do not share a key"* |
| Process memory ↔ canonical truth | **NO** | Two process-global mutable authorities decide truth (RA-01, RA-12) |
| Gate ↔ subject | Partial | Only 4 of 29 gates declare their mutation mode |
| Environment ↔ verdict | **NO** | Nine verdict-bearing environment variables; unfiltered subprocess inheritance (B-2 TA-06) |

### 12.4 Security-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-21.1** | Unrestricted import from unvalidated JSON, invoked **before** validation (CH-5; T-13) | Trust → validation → import; nothing executes from an unverified descriptor (TI-5) | **YES** — no predecessors | YES (engineering) | YES — hole and fix both located | VR-47 | PROV | **EXECUTABLE** |
| **T-21.2** | No threat model as data; entire security vocabulary closed (C-18…C-22, C-49) | A probe threat class is admitted; blocking severities remain **total** | **NO — T-6.1** (SQ-6) | YES (engineering) | PARTIAL — **TRUE MISSING** in part: no threat/attack-surface/trust-boundary/adversary model exists to open | VR-48 | PROV after CR-21 | **CONDITIONAL** |
| **T-21.3** | Adversarial handling is one narrow scanner with an adjacent bypass; `record()`/`record_finding()` disagree on secret content; no oversized/deep-input bounds (P-12) | Uniform adversarial bounds; identical secret handling at every entry point | **YES** — independent | YES (engineering) | YES — mismatch located | VR-49 | PROV after CR-21 | **CONDITIONAL** |

### 12.5 The risk that makes CH-5 delicate rather than trivial

| Risk | Severity | Constraint |
|---|---|---|
| **R-49** | **CRITICAL** | *Hardening the provider path narrows the one genuinely open admission mechanism (PC-14).* The fix must **preserve open admission while requiring verification** — it must not close the only door through which an unforeseen kind can arrive |
| **R-50** | HIGH | Opening severities without declared ordering makes blocking non-deterministic — the same total-order hazard as R-12 |
| **R-20** | HIGH | A conversion executor evaluating string terms would become a **second** code-execution surface. T-12.1's evaluator must be total, pure and non-eval, and must not reproduce CH-5 |

### 12.6 Security readiness verdict

> **The single most disproportionate item in the repository is EXECUTABLE now.** CH-5 is a CRITICAL hole whose fix is already built two modules away, requires no authority decision, has no predecessors, and is approximately three edits. **T-21.1 is EXECUTABLE (W0).** Threat-model-as-data (T-21.2) and adversarial bounds (T-21.3) are CONDITIONAL. Security is *fully transformable by extension and wiring — no new capability is required*, which is precisely what makes the present state indefensible rather than merely incomplete.

---

## 13. API Protocol Readiness

### 13.1 The USL-15 finding is respected, not reopened

The absence of protocol representation is **not an oversight**. It is enforced by `USL-15`, implemented as `_TECHNOLOGY_MARKERS` (17 tokens) and the stricter `_TECH_MARKERS` (20 tokens, including bare `http`, `grpc`, `mqtt`, `amqp`, `rest`, `websocket`) scanning the canonical identity core, converted into **hard validation failure at seven sites** and enforced at construction time in two more. `pyproject.toml:19-22` states the intent: *"stdlib-only by constitutional intent (TP-04 Vendor Neutrality of Core, TP-05 Least Sufficient Technology)."*

**This determination does not open it, does not narrow it, and does not treat it as a defect.**

### 13.2 What is intentionally prohibited

| Prohibited | Instrument | Standing |
|---|---|---|
| Naming a protocol anywhere in the canonical identity core | `USL-15`, enforced at 7 validation sites + 2 construction sites | **Constitutional intent.** Working as designed |
| Selecting a transport, technology or vendor in the core | TP-04, TP-05 | **Constitutional intent** |
| Concrete endpoints | `Interface.endpoint_ref` is *"abstract only — no URL/protocol/port"* | **Constitutional intent** |

### 13.3 What capability is genuinely missing

| Missing | Nature | Is it a defect? |
|---|---|---|
| Any representation of a protocol at any layer | The model can say *"request-response"*; it structurally **cannot** say *"over HTTP/2"*. `InterfaceKind` is an interaction **style**, not a protocol | **No** — this is the prohibition working. **Closed by taboo, not open by data** |
| A populated API registry | `ApiRegistry` is wired at `registries.py:299`, exported, and **requires** `contract` and `protocol`. Zero `ucos.api` records; zero `UCOS-API-######`; no `.apis.register` call; `protocol` is untyped `Any`, validated for **presence only**. No `ProtocolKind`, `TransportKind`, adapter, transport abstraction or dispatcher exists | **Yes — the inconsistency is the defect.** A registry that requires a `protocol` attribute and has never held a record is an internal contradiction independent of the prohibition |
| Schema/code agreement on connector sources | Runtime `SOURCES` extended twice (`GIT`, `EXECUTION`); **neither appears in the schema**; the code comment claims *"Sources are pluggable… append-only addition to the open source set"* while being a closed Python set | **Yes.** The exemplar failure mode: a closed enumeration became a limitation and the response was **silent drift rather than amendment** |

### 13.4 Can protocol neutrality coexist with protocol evolution?

**Yes — under Option A, and only as a declared boundary.** The question is not *how do we open the protocol dimension* but **which of two different things is wanted**:

| Option | Content | Nature | Achievability |
|---|---|---|---|
| **Option A** | Protocol-neutral **core**, protocol-representable **declared periphery**. The core continues to select no technology; a declared boundary layer may name protocols | Preserves `USL-15` intact and closes the representational gap | **Achievable by extension.** The frame/axis pattern supplies the boundary pattern; `S-13` supplies the registry semantics; the `ApiRegistry` slot is already built |
| **Option B** | Protocols representable anywhere | Requires **weakening or repealing `USL-15`** | **Constitutional amendment** |

The current state is **neither**, and that is the finding: the registry exists, requires a `protocol` attribute, and has never held a record.

**This determination does not choose.** It records that Option A is achievable by extension, Option B is an amendment, and that no engineering act may make the selection.

### 13.5 API/protocol-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-17.1** | No protocol representable anywhere; `_TECHNOLOGY_MARKERS`/`_TECH_MARKERS` enforced as validation failure at 7 sites + construction failure at 2 (C-36) | Option A: declared periphery admits protocols, core prohibition intact. Option B: representable throughout | YES (no engineering predecessor) | **NO — constitutional decision A or B** | YES — all 9 enforcement sites located | VR-35 (under Option A: core still fails on a protocol token while the periphery admits one) | **NO** — CR-15 is **constitutional** and cannot be an engineering act | **CONDITIONAL** |
| **T-17.2** | `ApiRegistry` requires `contract` + `protocol` and has **never held a record**; `protocol` untyped `Any`, presence-validated only | Populated with typed protocol attributes, **or withdrawn with a stated reason** | **NO — T-17.1** (SQ-11) | **NO — inherits T-17.1** | YES — M-D measured | VR-36 | **NO** — CR-15 | **BLOCKED** |
| **T-17.3** | Connector schema `sources` enum of 11, `mode`/`status` closed, `additionalProperties: false`, **no `protocol` field at all**; runtime `SOURCES` drifted twice (C-34, C-35) | One authority for the source vocabulary; schema and code **cannot** diverge | **YES** — independent of the protocol question; this is a consistency defect | YES (engineering) | YES — drift measured | VR-37 | PROV | **EXECUTABLE** |

### 13.6 The risk that must be respected in any protocol work

| Risk | Severity | Constraint |
|---|---|---|
| **R-36** | HIGH | The marker check is a **naive lowercased substring scan**: `"lambda"` false-positives on identifiers, `"rest"` on `restore`/`restriction`/`forest`. Any change to this mechanism must fix the **matching semantics**, or narrowing the taboo will silently narrow it in unintended places |
| **R-37** | HIGH | Populating the API registry while `USL-15` stands creates records the validators would reject if scanned — an inconsistency between the registry and validation planes |
| **R-38** | LOW | T-17.3 is low risk and **high diagnostic value**: fixing it establishes the drift-prevention pattern that T-15.1 and T-6.3 both require, since both mirror constants across schema and code |

### 13.7 API protocol readiness verdict

> **One EXECUTABLE, one CONDITIONAL on a constitutional decision, one BLOCKED behind it.** T-17.3 (schema/code drift) proceeds now and is independent of the protocol question entirely. T-17.1 is a decision about **what UCOS Ω∞ is for**, not a fix, and no engineering act may substitute for it. T-17.2 cannot proceed in either direction until that decision exists. **Protocol neutrality and protocol evolution can coexist — under Option A — and this determination declines to select it.**

---

## 14. UI UX Readiness

### 14.1 The correction the evidence requires

As with protocol: **the absence of a UI is not obviously a defect.** There is no frontend, no interaction runtime, and `application/interaction.py` *"selects no technology, UI framework, design system, or rendering technology."* Whether UCOS Ω∞ **should** have an experience capability is an authority question about scope.

What *can* be determined without that answer is that the current UI representation is **internally inconsistent**.

### 14.2 The measured position

| Element | State | Evidence |
|---|---|---|
| `ui-artifact.schema.json` | **21 lines, no enums**, nullable `wireframe`/`design`, `components: array[string]` with **no component model**, `derived_status` an unconstrained string — **strictly weaker than its neighbour** `page.schema.json`, which carries a real 17-value enum | schema files |
| `journey.schema.json` | Likewise **no enums** | schema files |
| Instances | **Zero** `UCOS-UI-######`; **zero** `UCOS-UX-######`. No tool references the schemas | M-D, M-F |
| `12-APPLICATION/` | 22 `.md`, **zero source** | M-F |
| Frontend | **Zero files**; one generated `.html`. `intelligence/portal.py` is a **Markdown generator** despite its name | `portal.py:65-81,1028,1070` |
| `InteractionKind` | Closed 4-member vocabulary {Input, Command, Query, Response}; `Interaction` is a frozen typed record with a lifecycle state — not an event loop or widget tree; data presented **by reference** (C-28) | `application/interaction.py:1-45` |
| Identifier patterns | `^UCOS-UI-[0-9]{6}$`, `^UCOS-FLOW-[0-9]{6}$` (P-05) | UI/flow schemas |
| Dimension verdict | **P. UI/UX — NOT YET ASSIMILATED** | B-1 §35.1 |

**Nothing in this dimension can evolve because nothing exists to evolve.**

### 14.3 What foundation is required before future interfaces can evolve

Recorded as a dependency statement, not as a plan, because the scope decision is undecided:

| Prerequisite | Why it precedes any interface |
|---|---|
| **The scope decision itself (T-18.1)** | Everything else in the dimension is conditional on whether experience is in scope. Building speculatively adds a dimension with no consumer; withdrawing forecloses a direction (R-39) |
| **Durability (T-6.1, TI-1)** | An interaction kind admitted into process memory evaporates. Interfaces are exactly the surface where kinds proliferate |
| **Kind openness for interaction (T-18.2)** | A future interaction model outside input/command/query/response — neural, spatial, agentic, non-human observer — is unrepresentable today |
| **The `Observer` anchor** | `Observer` already exists in the context layer and is the natural anchor for a **non-human** interaction model. No new concept is required |
| **Schema parity** | `page.schema.json` (17-value enum) is the in-repo quality bar. The UI schemas must meet it or be withdrawn |
| **Preservation of the rendering-technology refusal** | The refusal to select a rendering technology is **correct and must survive** any expansion (R-40). Only the *kind* set opens |

### 14.4 UI/UX-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-18.1** | UI representation exists with **zero instances and no runtime**; schemas strictly weaker than neighbours; 21-line schema with no enums | Either a populated interaction model, **or** an explicit declaration that experience is out of scope **with the schemas withdrawn** | YES (no engineering predecessor) | **NO — scope decision** (same class as T-17.1) | YES — M-D, M-F measured | VR-38 (either ≥1 UI instance exists, or the schemas are withdrawn) | **NO** — CR-16 requires the scope declaration | **CONDITIONAL** |
| **T-18.2** | `InteractionKind` closed 4-member vocabulary (C-28) | Interaction kinds registered; **no rendering technology selected** | **NO — T-18.1** scope decision | YES (engineering) once scope is declared — cheap if the dimension is retained | YES | VR-39 | PROV after CR-21 | **CONDITIONAL** |

### 14.5 UI UX readiness verdict

> **NOT READY, and not blocked by engineering.** Both transformations are CONDITIONAL on a single scope decision that no engineering act supplies: **is experience in scope for UCOS Ω∞?** Until that is answered, the honest position is that the dimension holds a declared-but-empty surface — schemas weaker than their neighbours, zero instances, no runtime — and that this internal inconsistency is a defect **regardless** of how the scope question is decided. If the answer is yes, T-18.2 is a cheap vocabulary conversion against `S-13`. If the answer is no, the correct action is withdrawal.

---

## 15. Software Evolution Readiness

### 15.1 The required model, assessed link by link

```
Discovery  →  Impact  →  Testing  →  Validation  →  Certification  →  Migration
```

| Link | State at baseline | Evidence | Held by |
|---|---|---|---|
| **Discovery** | Real and **closed in shape**. `DiscoveryKind` is a closed 8-member enum (ZF-5, C-13). Source extensions ~30, injectable (C-33). **Detection is declaration-bound**: `AD-G-01` guarantees undisclosed closures remain invisible | C-13, C-33; B-6 | T-15.2, T-26.1 |
| **Impact** | **Exists and is unwired.** Substrate coverage **10.4%** (5 substrates, C-43); `PATH_BEARING_KINDS`/`SELF_PREFIXES` closed (C-42) | C-42, C-43 | T-19.5, T-13.3 |
| **Testing** | Substantial and **cannot detect the defects that matter**. 52 passing persistence tests; interchangeability measured by digest equality. But **zero of 29 gates vary initialization order**; the reconstruction test's own fixture calls `bootstrap()` (R-01); `verify.sh --full` **exits 1** on 4 of 15 stages | CH-2; R-01; B-6 | T-19.1 — **EXECUTABLE (W0)** |
| **Validation** | Fail-closed and **process-dependent** (M-B); 6 of 15 chain stages unvalidated | M-B; B-1 | T-6.1 — **EXECUTABLE (W0)** |
| **Certification** | Mechanically sound; **evidentially unable to support a success claim**. 16 axes certified on prose; Axes 13–14 contradicted by measurement; ceiling `CERTIFIED-PROVISIONAL`; ~15 root certifications self-asserted | `S-10`; T-23.3; `UCCEP-F-004` | T-23.3 — CONDITIONAL (W1) |
| **Migration** | **Absent across the board.** No identifier migration (IDF-17); no per-identity version; path-keyed `allocate()` mints on rename with no back-pointer; `derive_change_events` **drops** stale subjects; six incompatible lifecycle models with determination artifacts in a **governance void** | B-3 §14.2; C-14; `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` | T-15.3, T-6.3 |

**The model is intact at both ends and broken in the middle: testing cannot detect statefulness, and migration does not exist.**

### 15.2 Safe evolution of languages, dependencies, frameworks, architectures, runtimes

| Target of evolution | Current finite state | Evidence | Execution position |
|---|---|---|---|
| **Human languages** | `language: "en"` hardcoded at `context/catalog.py:178-186`; **no resolver** (T-04) | T-04 | T-16.1 — CONDITIONAL. The axis is **already open in the location layer**; the resolver pattern (`no default, UNRESOLVED with derivation path`) exists at `context/location.py` |
| **Machine languages / execution kinds** | `KNOWN_EXECUTION_KINDS` closed 10-member, including a named placeholder `FUTURE_LANGUAGE` bound to a live adapter class; `KNOWN_PERSISTENCE_KINDS` mirrors the pattern with `FUTURE_STORAGE` (C-31, C-32) | C-31, C-32 | T-16.2 — CONDITIONAL. **Infinity as a named placeholder is not openness**: two distinct unforeseen kinds must be separately registrable and distinguishable (VR-33) |
| **Symbolic systems** | **No symbolic-system axis** exists; verified `UNKNOWN` at finding level (F-15.4 — the single UNKNOWN across 90 findings) | B-1 F-15.4 | T-16.3 — CONDITIONAL on an authority decision. **R-35: adding an axis speculatively is worse than determining first.** Record as unresolved, per the `unknown`-as-valid discipline |
| **Dependencies** | stdlib-only **by constitutional intent** (TP-04, TP-05) | `pyproject.toml:19-22` | Not a transformation. Constitutional position |
| **Frameworks** | None selected anywhere, by design | `S-06`, `application/interaction.py` | Not a transformation |
| **Architectures** | 33-facet frame is amendment-gated (**CH-6**); 4 root primitives and the 7/7/7 hierarchy grammar are **ratified invariants** (C-40, C-41); 17 constitutional articles as code (C-37); `ConstitutionalDomain` 13 (C-38) | CH-6; C-37, C-38, C-40, C-41 | **CH-6 is the single most consequential open question and no engineering work resolves it** |
| **Runtime environments** | **CPython/venv is the only modelled environment** (T-07) | T-07 | Not separately transformed; recorded as a technology assumption |

### 15.3 Software-evolution-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-19.1** | Single-process determinism harness; **zero of 29 gates vary initialization order** (T-14; RA-14, RA-15) | Statefulness is detectable; a fix can be shown to work | **YES** — no predecessors | YES (engineering) | YES — CH-2 measured | VR-01 (the instrument **is** the deliverable) | PROV | **EXECUTABLE** |
| **T-19.2** | `classify()` → ERROR for every subject; R-09 declared with no predicate (M-C; RA-20; C-39) | Total classification across all nine classes | **YES** — no predecessors | YES (engineering) | YES — M-C reproduced | VR-40 | PROV | **EXECUTABLE** |
| **T-19.3** | Mutation class extension is *"a SPECIFICATION, not an implementation"* (C-39) | New classes registrable; **predicate-less classes refused at registration** | **NO — T-19.2** (SQ-3) | YES (engineering) | YES | VR-41 | PROV after CR-21 | **CONDITIONAL** |
| **T-19.5** | Impact analysis exists and is unwired; 10.4% coverage (C-43) | Impact wired; every verdict **discloses its substrate coverage** | **NO — T-19.1** | YES (engineering) | YES | VR-43 | PROV after CR-21 | **CONDITIONAL** |
| **T-16.1** | One hardcoded language, no resolver (T-04) | ≥2 languages resolve; **no `en` default appears in code** | **NO — Layer 3/4** | YES (engineering) | YES — remediation already specified with an acceptance criterion | VR-32 | PROV after CR-21 | **CONDITIONAL** |
| **T-16.2** | Machine languages fixed tuples with **infinity as a named placeholder** (C-31, C-32) | Two distinct unforeseen execution kinds separately registrable and distinguishable | **NO — T-6.1** (SQ-6) | YES (engineering) | YES | VR-33 | PROV after CR-21 | **CONDITIONAL** |
| **T-16.3** | No symbolic-system axis; status verified UNKNOWN | Symbolic systems either have an axis **or a documented subsumption** | YES | **NO — decision** (R-35: determine before adding) | PARTIAL — the single UNKNOWN finding | VR-34 | **NO** — authority act | **CONDITIONAL** |
| **T-15.3** | **Six mutually incompatible lifecycle models**; determination artifacts have **no lifecycle at all** — including this artifact | Every artifact resolves to exactly one lifecycle authority | YES | **NO — decision.** Gates T-15.1, T-24.2, T-9.2 (SQ-8) | YES | VR-30 | **NO** — authority act | **CONDITIONAL** |
| **T-19.4** | Source self-modification prevented by **three independent confinements** | — the confinements are a **safety property, not a gap** | **NO — TI-1…TI-5** (SQ-10) | **NO — authority decision** | YES | VR-42 | **NO** | **PROHIBITED** |

### 15.4 The risks that bound software evolution

| Risk | Severity | Constraint |
|---|---|---|
| **R-41** | MEDIUM | Introducing initialization-independence measurement **turns green gates red**. This is the **intended effect and not a regression** — it is the whole point of T-19.1 |
| **R-42** | HIGH | Restoring classification may reveal **mutations certified while unclassified**. Expect disclosure, not silence |
| **R-43** | HIGH | The current defect exists **because a class was registered without a predicate**. Extension must make that impossible — refuse at registration (VR-41) |
| **R-45** | HIGH | Impact analysis over **10.4% coverage** produces confident reports with wide blind spots. Coverage must be disclosed with every verdict |
| **R-24** | **CRITICAL** | **Narrowing selection without verified coverage converts fail-wide into fail-silent.** T-13.3 must never precede T-19.1 (SQ-7) |
| **R-31** | HIGH | Consolidating six lifecycle models invalidates stage assignments **corpus-wide**. Federation is the lower-risk path |
| **R-34** | MEDIUM | `FUTURE_LANGUAGE` is bound to a **live adapter class**; retiring the placeholder requires re-homing that binding |

### 15.5 Software evolution readiness verdict

> **The two transformations at the root of the entire dependency graph are EXECUTABLE, and they are the smallest work in the programme.** T-19.1 (detection) and T-19.2 (classification) have no dependencies, require no authority, and jointly restore the two faculties the programme cannot proceed without: the ability to **detect that a fix worked** and the ability to **classify what is being changed**. Everything else in this domain — extension, impact wiring, language resolution, execution kinds, lifecycle reconciliation — is CONDITIONAL. **Source self-modification is PROHIBITED.** The migration link of the model does not exist at all, and no transformation in the population creates it: identifier migration (IDF-17) is recorded as absent and remains absent.

---


## 16. Intelligence Evolution Readiness

### 16.1 The required chain, assessed link by link

```
Discovery  →  Understanding  →  Impact Analysis  →  Validation  →  Certification  →  Evolution
```

| Link | State at baseline | Evidence | Held by |
|---|---|---|---|
| **Discovery** | Real and closed in shape. `DiscoveryKind` closed 8-member (C-13). Detection is **declaration-bound**: `AD-G-01` guarantees undisclosed closures remain invisible | C-13; B-6 | T-15.2, T-26.1 |
| **Understanding** | **Does not exist as a link.** The assimilation↔intelligence edge does not exist; the feedback loop is **prose**; assimilation terminates in a measurement of itself. B-1 §35.3 tested *"become understood"* and returned **No** | B-1 F-13.5, §35.3 | T-14.3 — CONDITIONAL on five domains |
| **Impact Analysis** | Exists and is **unwired**; substrate coverage **10.4%** | C-43 | T-19.5, T-13.3 |
| **Validation** | Fail-closed and process-dependent (M-B). **This is the link intelligence is strongest at**: falsifiability is enforced by refusal | M-B; `S-09` | T-6.1 — EXECUTABLE (W0) |
| **Certification** | Sound mechanically; ceiling `CERTIFIED-PROVISIONAL`; one certification class (C-17) | `S-10`; C-17 | T-23.2, T-23.3 |
| **Evolution** | **Achieved by refusing to conclude, not by learning.** Externally triggered, append-only recording. No parameters are updated by any run. The controller *"conducts; it does not decide"* | B-1 F-21.1, F-20.3, F-29.3 | T-20.x, T-24.3 |

### 16.2 Reasoning evolution

| Element | State | Evidence | Position |
|---|---|---|---|
| Reasoner set | **Closed 13-member enum with hardcoded dispatch** and **no plugin interface** (C-16) | `uckp/intelligence.py:39-53` | T-20.2 — CONDITIONAL |
| Dispatch mechanism | Hardcoded; a 14th reasoning kind is a code edit — an amendment in the CH-6 sense | C-16; CH-6 | T-20.2 |
| Threshold discipline | **No corpus-tuned thresholds**, enforced in CI (`intelligence.py:9-13`). This discipline is **retained in the target** | `S-09` | Preservation constraint |
| Non-falsifiable output | Refused. Prediction is **deliberately refused as unfalsifiable** | `uaue/simulation.py:1-25` | **PROHIBITED to add** |
| Strongest scope | Intelligence is the **strongest scope in the closure register — 7 of 12 closed**. Its two absences are *both edges, not engines* | B-6 §19.3 | — |

### 16.3 Knowledge evolution

| Element | State | Evidence | Position |
|---|---|---|---|
| Homing | **549/549 homed, gaps=0** across seven checks (`UAKOS-CLOSURE-002`: conversation_only 0, duplicate_canonical_homes 0, in_repo_unhomed 0, not_homed_concepts 0, orphan_concepts 0, ukda_content_hash_duplicates 0, upload_only 0) | B-1 F-13.1; session baseline | **Sound. Homing is not ownership** |
| Canonical declaration | **25.5%** while homing is 100% | B-1 F-13.2 | T-14.1 — **BLOCKED** on T-22.3 |
| Headline closure verdict | Depends on an **out-of-repository corpus** and an **environment variable**; the frozen-corpus guard **silently succeeds under substitution** | RA-16; T-06, T-11 | T-14.2 — **EXECUTABLE (W0)**; T-14.4 guard leg CONDITIONAL |
| Store neutrality | Filesystem-bound; storage neutrality **declined** on four criteria | REQ-43 §3.2 | T-14.4 — CONDITIONAL |
| Feedback into reasoning | **Prose only** | B-1 F-13.5 | T-14.3 — CONDITIONAL |

**R-26 (MEDIUM):** resolving the closure verdict is expected to change `gaps=0` to non-zero (evidence: 91), making every citing artifact stale. This is **truth-restoring** and the documentary consequence is expected, not a reason to defer.

### 16.4 Model evolution

| Element | State | Evidence | Position |
|---|---|---|---|
| AI adapter layer | A **declared HIGH-severity gap** | B-1 F-21.4 | T-20.1 — CONDITIONAL on an authority decision |
| Internal forecaster for AI-model evolution | **Refused by design with a stated reason**; the assimilation route is scheduled instead | B-7 §2 | **PROHIBITED to add** |
| Provider conclusions | A future intelligence *"may supply data but never a conclusion"*; `Provider` protocol has **no `propose()`** (C-44) | B-1 F-21.3 | T-20.3 — CONDITIONAL |
| Intelligence as re-derivation | Intelligence is re-derivation, not learning | B-1 F-21.1 | T-20.1 |

### 16.5 Intelligence capability evolution

The capability register is the **best openness evidence in the repository**: machine-checked zero-enumeration, governing modules named as data, admission by measurement rather than declaration, and the check itself has **no hardcoded module list** (`S-06`). Against that: **realized coverage = 1**, the admission authority is **unregistered and externally blocked**, and the gate layer *"grows only by hand-written code"* (B-1 F-17.1, F-17.3, F-17.4, F-17.5).

Capability evolution is therefore **mechanism-complete and population-empty**, and its admission authority is one of the four BLOCKED items (T-22.4).

### 16.6 Intelligence-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-20.1** | Intelligence is re-derivation; the AI adapter layer is a **declared HIGH-severity gap** | Any introduced intelligence produces **falsifiable** output; non-falsifiable estimates refused | YES (no engineering predecessor) | **NO — scope decision** on what intelligence is for | YES — gap declared | VR-44 | **NO** — authority act | **CONDITIONAL** |
| **T-20.2** | Reasoner set a closed 13-member enum with hardcoded dispatch and no plugin interface (C-16) | A registered reasoner **never seen by the release** contributes; a corpus-tuned threshold is refused | **NO — T-6.1** (SQ-6) | YES (engineering) | YES | VR-45 | PROV after CR-21 | **CONDITIONAL** |
| **T-20.3** | A future intelligence may supply data but **never a conclusion**; `Provider` protocol has no `propose()` (C-44) | Provider conclusions treated as **claims requiring validation** | **NO — T-21.1** (SQ-5) | **NO — decision** on whether conclusions are admissible at all | YES | VR-46 | **NO** — authority act | **CONDITIONAL** |

### 16.7 The risks that bound intelligence execution

| Risk | Severity | Constraint |
|---|---|---|
| **R-46** | **CRITICAL** | *A model whose output cannot be re-derived reintroduces **belief over evidence**.* Falsifiability is mandatory and non-negotiable |
| **R-47** | HIGH | An open reasoner registry is a **code-loading surface**. Register, never import from data — or T-20.2 reproduces CH-5 in a second location |
| **R-48** | HIGH | Provider conclusions **bypassing validation become belief**. T-20.3 must be sequenced after T-21.1 (SQ-5) |
| **R-35** | MEDIUM | Adding a symbolic axis speculatively is worse than determining first — record as unresolved, per the `unknown`-as-valid discipline |

### 16.8 Intelligence evolution readiness verdict

> **NOT READY, and the chain fails at its second link.** *Understanding* does not exist as a capability — the assimilation↔intelligence edge is absent and the feedback loop is prose. No intelligence transformation is EXECUTABLE. Two of three require an authority decision about **what intelligence is for**, and the third (reasoner openness) is held by durability and carries a code-loading hazard that would reproduce CH-5 if executed carelessly. The domain's greatest strength is what it **refuses**: prediction as unfalsifiable, corpus-tuned thresholds, conclusions from providers. Those three refusals are retained in the target and must survive any expansion.

---

## 17. Autonomous Evolution Readiness

### 17.1 The question

> What must exist before the system changes itself?

### 17.2 The determination

**T-19.4 = PROHIBITED. T-24.3 = PROHIBITED.**

Autonomous evolution requires prior closure of **ownership, trust, evidence, validation, rollback and certification**. Not one of the six is closed at baseline. Executing either transformation in the current state would place autonomy over **undurable, unowned, undetectable, untrusted state** — which is the worst configuration available and is recorded as **R-44, CRITICAL**.

This is a **change of kind, not of degree**. It is not the third step of a gradient, and it is not reachable from the current state by extension.

### 17.3 The six required closures, assessed

| # | Required closure | State at baseline | Evidence | Closed by |
|---|---|---|---|---|
| **1. Ownership** | **NOT CLOSED.** 391/542 unowned (variance: 398/549), catalogue empty, **0% ratified**. An autonomous mutation of an unowned subject is **ungoverned by construction** | CH-4; §7 | T-22.3 — **BLOCKED (owner act)** |
| **2. Trust** | **NOT CLOSED.** CH-5: unrestricted import from unvalidated JSON, pre-validation. Autonomy over an execution-trust hole is arbitrary code execution with a governance label | CH-5 | T-21.1 — EXECUTABLE (W0) |
| **3. Evidence** | **NOT CLOSED.** `EvidenceKind` closed fail-closed; 12 truth facets have no declared owner; 4 of 11 assimilation stages have no truth owner; ~15 root certifications self-asserted in prose | C-23; B-2 TA-22, TA-27 | T-22.1, T-23.3 — CONDITIONAL |
| **4. Validation** | **NOT CLOSED.** Process-dependent for 43 of 72 kinds (M-B); 6 of 15 chain stages unvalidated; `verify.sh --full` **exits 1** on 4 of 15 stages; **zero of 29 gates vary initialization order** | M-B; CH-2; B-6 | T-6.1, T-19.1 — EXECUTABLE (W0) |
| **5. Rollback** | **REFUSED, CORRECTLY, AND THE REFUSAL IS RETAINED.** `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md` §1 refuses a rollback point with reasons; `ORL-15` forbids introducing an engine, scheduler, automation platform or executor | `S-09`; B-7 §2 | **PROHIBITED to add (T-24.5)** |
| **6. Certification** | **NOT CLOSED, AND CANNOT REACH FINALITY.** Ceiling is `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`); Tier T1 vacant (`VAC-01`); `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` confers no constitutional finality; 16 axes certified on prose with Axes 13–14 contradicted | `UCCEP-F-004`; T-23.3 | T-23.3 + CR-21 — CONDITIONAL |

### 17.4 The rollback paradox, stated plainly

Requirement 5 is not satisfiable in the ordinary way, and this determination records the consequence rather than resolving it:

- Autonomous evolution conventionally depends on rollback.
- Rollback is **refused by standing determination**, because a rollback path would let a failed mutation *appear* reverted when the truth it produced has already propagated.
- **R-63 (HIGH):** *"A programme under pressure will be tempted to add rollback. It must not."*

**Therefore the rollback requirement must be discharged by a declared bound, not by a rollback engine.** The consequence is explicit and is the reason autonomy is the highest bar in the programme: **there is no rollback for an evolution that reaches truth incorrectly, which raises the pre-admission bar rather than lowering the post-admission one.**

### 17.5 Provenance, impact analysis and the three confinements

| Element | State | Position |
|---|---|---|
| **Provenance** | Append-only lineage exists and is round-trippable within CEU; the evolution ledger *has* serialization and lacks only a **production writer** (B-6 self-correction to `F-3`) | Partially present; not sufficient alone |
| **Impact analysis** | Exists, **unwired**, **10.4% coverage**. R-45: confident reports with wide blind spots | T-19.5 + T-13.3 — CONDITIONAL |
| **Three confinements against source self-modification** | Present and independent | **A safety property, not a gap.** Removing them is the authority act, not the engineering act |
| **Evolution Registry** | **REFUSED** — it could become a second identity authority (`CAA-INV-04`) | **PROHIBITED to add (T-24.5)** |
| **Predictive engine** | **REFUSED** as unfalsifiable | **PROHIBITED to add** |
| **Non-termination** | Structurally guaranteed: `is_terminal` returns `False` because **no state could return `True`** | **PROHIBITED to change (T-24.1)** |

### 17.6 Autonomous-evolution-layer transformations

| ID | Current finite constraint | Target universal capability | Dependency satisfied | Authority available | Evidence available | Validation available | Certification available | Execution state |
|---|---|---|---|---|---|---|---|---|
| **T-19.4** | Source self-modification prevented by **three independent confinements** | — the confinements are a **safety property**; removal is an authority act | **NO — TI-1…TI-5 all unmet** (SQ-10) | **NO — authority decision, undecided** | YES — confinements located | VR-42 (no source mutation outside the declared governed path) | **NO** — ceiling + CR-21 undischarged | **PROHIBITED** |
| **T-24.3** | Evolution is **externally triggered recording** with no self-modification and no learning; no parameters updated by any run; the controller *"conducts; it does not decide"* | Autonomous evolution occurring **only where TI-1…TI-5 all hold** | **NO — TI-1…TI-5 all unmet** (SQ-10) | **NO — authority decision, undecided** | YES | VR-60 | **NO** — ceiling + CR-21 undischarged | **PROHIBITED** |
| **T-24.1** | Non-termination achieved | Preserve: **no terminal state becomes claimable** | n/a — preservation | n/a | YES | VR-58 | PROV as preservation | **PROHIBITED** |
| **T-24.5** | Evolution Registry and Rollback Point **refused, correctly** | Preserve both refusals | n/a — preservation | n/a | YES | VR-58 | PROV as preservation | **PROHIBITED** |
| **T-23.1** | Certification mechanics sound | Preserve content-addressing, digest-anchoring, deterministic ordering, injectable rules and frames | n/a — preservation | n/a | YES | VR-54 | PROV as preservation | **PROHIBITED** |

### 17.7 Autonomous evolution readiness verdict

> **PROHIBITED in the current state, and convertible to CONDITIONAL only by an authority decision taken after all five target invariants hold.** The two autonomy transformations are the only items in the population classified PROHIBITED for reasons of **state** rather than of **principle** — the other four are PROHIBITED because transformation would be regression. The distinction matters: T-19.4 and T-24.3 are not permanently forbidden, they are **forbidden now**, and the conditions for reconsidering them are the six closures of §17.3, of which one (rollback) must be discharged by a declared bound rather than a mechanism.

---

## 18. Execution Wave Model

### 18.1 Wave allocation and reconciliation

All 67 transformations are allocated to exactly one wave. No transformation appears twice; none is omitted.

| Wave | Theme | n | Execution states present |
|---|---|---|---|
| **W0** | Foundation integrity | **10** | 10 EXECUTABLE |
| **W1** | Classification and measurement | **6** | 6 CONDITIONAL |
| **W2** | Authority and ownership closure | **8** | 5 CONDITIONAL · 3 BLOCKED |
| **W3** | Identity capability evolution | **4** | 4 CONDITIONAL |
| **W4** | Entity/context/vocabulary expansion | **21** | 20 CONDITIONAL · 1 PROHIBITED |
| **W5** | Assimilation activation | **3** | 3 CONDITIONAL |
| **W6** | Technology/software evolution | **10** | 9 CONDITIONAL · 1 BLOCKED |
| **W7** | Autonomous evolution | **5** | 5 PROHIBITED |
| | **TOTAL** | **67** | **10 EXECUTABLE · 47 CONDITIONAL · 4 BLOCKED · 6 PROHIBITED** |

Reconciliation: `10+6+8+4+21+3+10+5 = 67` ✔ · EXECUTABLE `10` ✔ · CONDITIONAL `6+5+4+20+3+9 = 47` ✔ · BLOCKED `3+1 = 4` ✔ · PROHIBITED `1+5 = 6` ✔

**Two wave adjustments carried forward from the derivation and preserved here:** `T-21.2 → W4` (it is a Layer 3 vocabulary conversion, not security engineering) and `T-21.3 → W1` (it is integrity and bounds hardening, independent of the security vocabulary question).

---

### WAVE 0 — FOUNDATION INTEGRITY

**Objective.** Restore the four faculties without which no other transformation can be governed, verified, retained or trusted: **detection**, **classification**, **durability**, **trust** — plus five independent integrity repairs that require nothing and block nothing.

**Prerequisites.** None. This is the only wave with no unmet predecessor. It is independent of ownership (B-5 §27.4), independent of all five open authority questions, and independent of the certification ceiling.

**Allowed transformations (10 — the complete EXECUTABLE population).**

| Order | ID | Why it is in W0 |
|---|---|---|
| 0.1 | **T-19.1** | Restores detection. Must be first: nothing else is verifiable (EP-1, SQ-1) |
| 0.2 | **T-19.2** | Restores classification. Must be first: nothing else is governable (EP-2, SQ-2). T-19.1 and T-19.2 are **jointly first** and mutually independent |
| 0.3 | **T-21.1** | Closes CH-5, the sole CRITICAL security defect (EP-5) |
| 0.4 | **T-6.1** | Closes CH-1. Strictly after T-19.1 (SQ-1), because R-01 means the existing test cannot detect its failure |
| 0.5 | **T-26.1** | The second mutable authority + closure disclosure. Parallel to T-6.1; verified by T-19.1 (EP-6) |
| 0.6 | **T-13.1** | Refuse-before-register. Independent, single site |
| 0.7 | **T-23.4** | Verify-on-load. Independent, three sites |
| 0.8 | **T-14.2** | Closure verdict provenance. Independent, truth-restoring |
| 0.9 | **T-17.3** | Schema/code drift. Independent; establishes the drift-prevention pattern for T-6.3 and T-15.1 |
| 0.10 | **T-24.4** | Scale-clause classification. Independent |

**Forbidden transformations.** Everything else. Specifically and emphatically: **no Layer 3 kind openness** (W4). Opening kinds in W0 violates SQ-1, SQ-2 and SQ-6 simultaneously and produces a larger population of non-durable, unclassifiable kinds than exists today. Also forbidden: any ownership population (R-54), any rollback (R-63), any predictive engine, any second identity authority, any narrowing of the provider path that closes open admission (R-49), any narrowing of substrate selection (R-24, SQ-7).

**Evidence required.** M-A/M-B/M-C carried as the entry baseline · the located sites for each of the ten (RA-01…RA-20 mapping) · the 38 pre-existing tracked modifications isolated by owning programme before measurement (B-7 §3 condition `0.6`, **currently failing**).

**Certification required.** CR-01 (runtime independence — must **replace**, not supplement, the current single-process determinism evidence) · CR-17 (mutation classification total; **must disclose mutations certified while unclassified**) · CR-19 (trust before import — highest urgency) · CR-11, CR-12, CR-13, CR-22, CR-23 partial. All bounded to `CERTIFIED-PROVISIONAL`. **No success claim may be made in this wave** (EP-7): the instrument that would make such a claim credible is T-23.3, in W1.

**Exit criteria.**

| # | Criterion | Instrument |
|---|---|---|
| X0-1 | `validate_rule_coverage()` returns empty; `classify()` returns a class for a sample spanning all nine classes | VR-40 |
| X0-2 | The same subject yields the same verdict in a fresh interpreter and a bootstrapped one, for all 72 admissible kinds | VR-01 |
| X0-3 | Delete runtime memory → reload canonical → reconstruct → compare identical, for all 13 truth objects (from 4/2/7) | VR-02 |
| X0-4 | An unsigned or non-allowlisted descriptor is refused **before** import | VR-47 |
| X0-5 | After a refused cyclic registration the registry contains **no edge** | VR-21 |
| X0-6 | A tampered chain fails on load; `verify()` returns `False` for an unverifiable record | VR-57 |
| X0-7 | The closure verdict is reproducible from a bare fresh clone with **no environment variables set** | VR-25 |
| X0-8 | Schema and runtime source vocabularies provably agree | VR-37 |
| X0-9 | No architectural bound token survives unclassified | VR-61 |
| X0-10 | Every closed enumeration in the codebase appears in the disclosure register | VR-62 |
| X0-11 | **TI-1, TI-2 and TI-5 all hold** | X0-2/3/4 jointly |

**Expected side effects, recorded so they are not mistaken for regressions.** R-41: green gates turn red — intended. R-42: mutations certified while unclassified are revealed — expect disclosure. R-64: ~230 closures surface, several contradicting standing certifications — the register gets worse before better. R-26: `gaps=0` becomes non-zero, making citing artifacts stale — truth-restoring.

---

### WAVE 1 — CLASSIFICATION AND MEASUREMENT

**Objective.** Convert restored faculties into **instrumented** faculties: extend classification safely, wire impact with disclosed coverage, expand substrate coverage, apply the anti-closure gate to the gates themselves, and instrument the 16 unboundedness axes so that any later success claim is credible.

**Prerequisites.** W0 exit criteria X0-1 … X0-11 all satisfied. Specifically T-19.1 (for every item) and T-19.2 (for T-19.3 and T-26.2).

**Allowed transformations (6).** T-19.3 · T-23.3 · T-19.5 · T-13.3 · T-26.2 · **T-21.3**

**Forbidden transformations.** All kind openness (W4). Any substrate narrowing before coverage is measured (**R-24 CRITICAL**, SQ-7). Extending the classifier before it is total (SQ-3). Any success claim about W0 until T-23.3 lands (EP-7, SQ-9).

**Evidence required.** W0 exit evidence · measured substrate coverage before and after (baseline 10.4%) · the 16-axis probe results including the **expected failure of Axes 13 and 14**.

**Certification required.** **CR-21 — the overriding obligation.** It must be discharged in this wave, because until the axes are instrumented, any claim that a transformation succeeded would be recorded in the same evidential form already shown unreliable. Also CR-17 (extension refuses predicate-less classes), CR-11 (coverage disclosed with every impact verdict), CR-19 (adversarial bounds uniform), CR-23 (gate self-application).

**Exit criteria.**

| # | Criterion | Instrument |
|---|---|---|
| X1-1 | A class registered without a predicate is **refused at registration** | VR-41 |
| X1-2 | Each of the 16 unboundedness axes has an executable probe; Axes 13–14 results recorded | VR-56 |
| X1-3 | Impact verdicts **disclose their substrate coverage** | VR-43 |
| X1-4 | Coverage measured before and after; **fail-wide remains default for uncovered subjects** | VR-23 |
| X1-5 | The gate population passes the openness test it applies to others | VR-63 |
| X1-6 | `record()` and `record_finding()` behave identically on secret content; oversized/deep inputs refused | VR-49 |
| X1-7 | **P-3 met** — success can be credibly asserted | X1-2 |

---

### WAVE 2 — AUTHORITY AND OWNERSHIP CLOSURE

**Objective.** Make authority **resolvable** and ownership **satisfiable**. This wave contains the programme's exit from the repository and is the only wave that cannot be completed by any amount of engineering.

**Prerequisites.** W0 and W1 exit. For T-22.3: T-22.2 (SQ-12).

**Allowed transformations (8).** T-22.1 · T-22.2 · **T-22.3 (BLOCKED)** · **T-22.4 (BLOCKED)** · T-8.2 · T-15.3 · **T-14.1 (BLOCKED)** · T-14.4

**Forbidden transformations.** **Automated population of the 391 (or 398) ownership assignments — R-54 CRITICAL.** That is precisely the fabrication the machinery is built to refuse and `UCOD-001:401` explicitly declines. Declaring any concept canonical without a ratified owner (R-25). Making any evidence kind constitutive by data edit (**R-52 CRITICAL**). Consolidating six lifecycle models where federation is the lower-risk path (R-31). Fixing the frozen-corpus guard is **permitted and required** regardless of the neutrality decision (R-28).

**Evidence required.** The ownership figure with its disclosed variance (391/542 and 398/549) · the three disclaiming planes and the absent shared key · F-20 status on UKAP/UREE · `CEP-002` Article 28 standing.

**Certification required.** CR-20 (ownership closure measured **and ratified**; authority key machine-readable) — **not attainable in-repo.** CR-06 (one governing truth model, or federation with crosswalks). CR-12 (declaration coverage stated; **will change the headline number**). CR-13 (lifecycle authority singular).

**Exit criteria.**

| # | Criterion | Instrument | Attainable in-repo? |
|---|---|---|---|
| X2-1 | Every ownership row resolves to a machine-readable key; declaration and enforcement **join on it** | VR-51 | Only after an authority decision |
| X2-2 | A probe evidence kind participates; a kind without a declared role is refused | VR-50 | Yes, with the constitutive gate |
| X2-3 | Every artifact resolves to exactly one governing truth model | VR-10 | Only after a decision |
| X2-4 | Every artifact resolves to exactly one lifecycle authority | VR-30 | Only after a decision |
| X2-5 | The frozen-corpus guard **fails**, never silently succeeds, under any substitution | VR-27 | **Yes — independent of the neutrality decision** |
| X2-6 | Ownership closure measured; unowned subjects **fail closed** rather than defaulting to `UNASSIGNED` | VR-52 | Measurement yes; **ratification NO** |
| X2-7 | **TI-4 holds** | VR-52 | **NO — owner act required** |

**Wave verdict.** W2 **cannot exit** inside the repository. X2-6 and X2-7 terminate in an owner act; X2-5 and X2-2 can be discharged. This wave is therefore permanently partial until an external act occurs, and every downstream wave that depends on TI-4 inherits that.

---

### WAVE 3 — IDENTITY CAPABILITY EVOLUTION

**Objective.** Move identity from a strong **semantics** with 13 representations to a resolvable, migratable, evolvable capability — after durability has already made validity a property of the identity (delivered in W0 by T-6.1).

**Prerequisites.** W0 exit (T-6.1 in particular). T-22.2 for T-6.2 (the same missing authority key). T-6.2 before T-6.5. T-15.1/T-17.3 drift-prevention pattern before T-6.3.

**Allowed transformations (4).** T-6.2 · T-6.3 · T-6.4 · T-6.5

**Forbidden transformations.** Creating a **second identity authority** — `CAA-INV-04` forbids it, and a federation crosswalk must not become one (R-02). Changing P-07/P-08 namespace patterns, which are **invariants and already universal**. Wiring `birth()` into hot paths where it could mint as a side effect — precedent: **140 identifiers minted by a drift check** (R-05). Widening the identifier pattern in one of its three mirrored locations without the others (R-03).

**Evidence required.** The 13 shapes / 58 prefixes / 4 alphabets inventory · the four mint planes including the assimilation `source_id` · all 1,461 existing artifact records · `uuid5`-over-rendered-string coupling.

**Certification required.** CR-02 (mint federation or governing declaration, **lineage preserved for already-issued identifiers**; `CAA-INV-04` must continue to hold) · CR-03 (widened patterns valid across schema and code with **no divergence**; drift check mandatory).

**Exit criteria.** X3-1: an identifier minted by any plane resolves in every other plane, or the crosswalk **names the boundary** (VR-03). X3-2: all 1,461 artifact records remain valid after widening (VR-04). X3-3: a non-ASCII extension kind code is admissible and collision-free (VR-05). X3-4: every first-class entity in a sample resolves to a birth record (VR-06).

---

### WAVE 4 — ENTITY/CONTEXT/VOCABULARY EXPANSION

**Objective.** Open the kind layer. This is the wave the directive's original framing wanted to start with, and it is the wave that is most dangerous to start early: it is **the most visible and most satisfying work**, and beginning here violates SQ-1, SQ-2 and SQ-6 simultaneously.

**Prerequisites.** W0 exit (durability — SQ-6, absolutely non-negotiable) · W1 exit (instrumentation, so openness claims are provable) · T-15.3 decision for T-24.2 and T-9.2 lifecycle leg (SQ-8) · T-23.2 before T-8.3 (R-10).

**Allowed transformations (21).**

| Group | IDs |
|---|---|
| Entity | T-7.1 · T-7.2 · T-7.3 |
| Reality | T-8.1 · T-8.3 |
| Context | T-9.1 · T-9.2 · T-9.3 · T-9.4 |
| Spatial | **T-10.1 (PROHIBITED — preservation only)** · T-10.2 |
| Temporal | T-11.1 · T-11.2 · T-11.3 |
| Measurement | T-12.1 · T-12.2 |
| Relationship | T-13.2 |
| Data | T-15.2 |
| Security vocabulary | **T-21.2** |
| Certification subject | T-23.2 |
| Evolution stages | T-24.2 |

**Forbidden transformations.** Declaring any kind **universal** by data edit — the universal flag requires constitutional authority (**R-11**). Registering an authority level, severity or stage **without a declared position** — precedence and ordering must stay total (**R-12, R-50, R-61**). Non-atomic relation/rule co-registration (**R-23**). Opening node types without rule totality over the widened set (**R-07**). Instantiating root primitives as a path to **amending** them (**R-06**). Adopting a canonical spatial frame or normalising `primary` (**R-15, R-16**). Forcing a default temporal frame (**R-17**). An `eval`-based conversion evaluator (**R-20**). Replacing `additionalProperties: false` with an open shape (**R-29**). Opening the facet frame — **CH-6 is undecided and no transformation in this wave depends on it**.

**Evidence required.** W0 + W1 exit evidence · the closed-enumeration disclosure register from T-26.1 · all 14 reference frames · all 16 context kinds · the 33-row `facet_reduction` mapping · the zero-axis root frame.

**Certification required.** CR-04 (primitives instantiable while remaining ratified; `UCPA-L-04` intact) · CR-05 (axis derivation as data with the gate refusing a shrinking axis set) · CR-07 (context vocabularies open with invariants intact) · CR-08 (coordinates representable, undeclared conversions refused, **no canonical frame adopted**) · CR-09 (no certification asserts an unqualified date) · CR-10 (conversions reproducible; **disclosure precedes remediation**) · CR-11 · CR-13 · CR-19 · CR-21 (already discharged) · CR-22.

**Exit criteria.** X4-1: **TI-3 holds** — a probe kind never seen by the release is admitted, persisted and honoured by a fresh validator (VR-12). X4-2: **T-9.4 resolves two disjoint context sets without code change** — the empirical proof of the whole wave, and the cheapest test available anywhere in the programme (VR-15). X4-3: probe admissibility for node types, value types, relations, discovery kinds, threat classes, certification subjects and evolution stages (VR-08, VR-14, VR-13, VR-29, VR-48, VR-55, VR-59). X4-4: all 14 frames resolve identically before and after; the zero-axis root frame still resolves nothing (VR-09). X4-5: a coordinate in an invented system is representable; undeclared conversions **refused, not improvised** (VR-16). X4-6: declared conversions reproduce; the term evaluator is total, pure and non-eval (VR-19). X4-7: a simulated-reality assertion cannot be certified as actual (VR-11).

---

### WAVE 5 — ASSIMILATION ACTIVATION

**Objective.** Bind fourteen engines that already exist. Not build — **compose**.

**Prerequisites.** All five of T-14.3's dependency domains on the path: identity (T-6.1, W0) · context (T-9.x, W4) · relationship (T-13.2, W4) · security (T-21.1, W0) · impact (T-19.5, W1). Plus T-15.3 for T-15.1 (SQ-8).

**Allowed transformations (3).** **T-14.3** · **T-15.1** · **T-15.4**

**Forbidden transformations.** **Binding the planes before all five dependencies are discharged — R-27, CRITICAL.** *Binding early routes unvalidated, unidentified, unowned, unsecured input into reasoning.* T-14.3 must be **last** among its five dependencies (SQ-4); starting it early is the highest-severity sequencing error available in the entire programme. Also forbidden: registering a reader as data such that code is loaded as data (**R-32** — must not reproduce CH-5); opening the artifact schema shape rather than adding a declared-extension mechanism (**R-29**); admitting a non-document form in a way that leaves **no unregistered serialization** — `S-04` requires that one always remain (VR-31).

**Evidence required.** The 14 admission surfaces · the three-islands/one-bridge/one-one-way-street topology · 6 of 13 categories admissible · the empty Ownership-stage catalogue · 4 of 11 stages with no truth owner.

**Certification required.** CR-12 (knowledge certification — declaration coverage stated; every declared concept owned) · CR-13 (artifact form admissible by registration; existing records valid) · CR-19 (trust before import, already discharged in W0 and re-asserted here).

**Exit criteria.** X5-1: an admitted source **reaches a reasoner and produces a recorded consequence** (VR-26) — this is the single test that converts *"become understood"* from **No** to yes. X5-2: a probe artifact form is admitted **without code change** and all existing records remain valid (VR-28). X5-3: a non-document form is admitted and **an unregistered serialization still exists** afterwards (VR-31).

**Wave constraint.** X5-1 depends on the Ownership stage resolving. While T-22.3 is BLOCKED, assimilation can be **wired and demonstrated** but cannot be **governed**. This is a real ceiling on W5, inherited from W2.

---

### WAVE 6 — TECHNOLOGY/SOFTWARE EVOLUTION

**Objective.** Resolve the two scope questions (protocol, experience) and open language, execution-kind and reasoner dimensions — none of which any earlier wave depends on.

**Prerequisites.** W0–W4 exit. T-17.1 decision before T-17.2 (SQ-11). T-18.1 decision before T-18.2. T-21.1 before T-20.3 (SQ-5).

**Allowed transformations (10).** T-16.1 · T-16.2 · T-16.3 · T-17.1 · **T-17.2 (BLOCKED)** · T-18.1 · T-18.2 · T-20.1 · T-20.2 · T-20.3

**Forbidden transformations.** **Opening `USL-15` by engineering action** — Option B is a constitutional amendment and this determination does not open it. Populating the API registry while `USL-15` stands, creating records the validators would reject (**R-37**). Changing the marker mechanism without fixing its **naive substring semantics** (**R-36**). Selecting a rendering technology (**R-40**). Adding a symbolic axis speculatively (**R-35**). Importing a reasoner from data (**R-47**). Admitting provider conclusions as anything other than claims requiring validation (**R-48**). Introducing any non-falsifiable output (**R-46, CRITICAL**). Adding corpus-tuned thresholds. Building an internal forecaster for AI-model evolution — refused by design.

**Evidence required.** The 7 validation + 2 construction enforcement sites for `USL-15` · the empty `ApiRegistry` requiring `protocol` · the UI schema/instance/runtime measurements (M-D, M-F) · the closed 13-member reasoner enum with hardcoded dispatch · the declared HIGH-severity AI adapter gap.

**Certification required.** **CR-15 — constitutional.** The Option A/B decision recorded and `USL-15` status made explicit. *Cannot be an engineering act.* Also CR-14 (≥2 languages resolve; execution kinds individually identified) · CR-16 (experience scope declared; schemas **populated or withdrawn**) · CR-18 (falsifiability preserved; reasoners **registered, never imported**).

**Exit criteria.** X6-1: under Option A the core **still fails** on a protocol token while the declared periphery admits one (VR-35). X6-2: every API record carries a **typed** protocol attribute, or the registry is withdrawn with a stated reason (VR-36). X6-3: either ≥1 UI instance exists, **or the UI schemas are withdrawn** (VR-38). X6-4: a probe interaction kind is admissible and **no rendering technology is selected** (VR-39). X6-5: two languages resolve and **no `en` default appears in code** (VR-32). X6-6: two distinct unforeseen execution kinds are separately registrable and distinguishable (VR-33). X6-7: symbolic systems have an axis **or a documented subsumption** (VR-34). X6-8: a registered reasoner never seen by the release contributes; a corpus-tuned threshold is refused (VR-45). X6-9: any introduced intelligence produces **falsifiable** output (VR-44). X6-10: provider conclusions are treated as **claims requiring validation** (VR-46).

---

### WAVE 7 — AUTONOMOUS EVOLUTION

**Objective.** None available. This wave exists to record what must be true before the system may change itself, and to state that no part of it may be executed in the current state.

**Prerequisites.** **All five target invariants holding simultaneously** — TI-1 (durability), TI-2 (initialization independence), TI-3 (kind openness), TI-4 (owned admission), TI-5 (trusted admission) — plus the six closures of §17.3 (ownership · trust · evidence · validation · rollback-as-declared-bound · certification), plus an explicit authority decision that autonomy is **wanted**, and under what invariants. **SQ-10.**

At baseline: **TI-4 is unreachable in-repo**, TI-3 depends on the undecided CH-6, and the authority decision does not exist.

**Allowed transformations.** **NONE.**

**Forbidden transformations (all 5 items in this wave).**

| ID | Classification | Reason |
|---|---|---|
| **T-19.4** | **PROHIBITED** | Source self-modification. The three confinements are a **safety property, not a gap**. Requires closure of ownership, trust, evidence, validation, rollback and certification — **none closed** |
| **T-24.3** | **PROHIBITED** | Autonomous evolution. Same six closures. **R-44, CRITICAL: autonomy over undurable, unowned, undetectable, untrusted state** |
| **T-23.1** | **PROHIBITED** | Certification mechanics are sound. Transformation is regression |
| **T-24.1** | **PROHIBITED** | Non-termination is achieved. **No terminal state may become claimable** |
| **T-24.5** | **PROHIBITED** | Evolution Registry and Rollback Point were refused, correctly. **R-63: a programme under pressure will be tempted to add rollback. It must not** |

Additionally forbidden in this wave and every wave: a predictive engine · a second identity authority · corpus-tuned thresholds · a rollback path · an evolution registry.

**Evidence required.** Demonstrated satisfaction of TI-1…TI-5 by executable instrument, not by prose. Provenance with a **production writer** (the ledger has serialization and lacks only that). Impact analysis with **materially better than 10.4%** coverage, disclosed. A ratified ownership population.

**Certification required.** CR-22 (non-termination preserved; stage set open with ordering intact; **refusals preserved**). And a certification of autonomy itself, which **is not attainable**: the ceiling is `CERTIFIED-PROVISIONAL`, Tier T1 is vacant, and no machine certificate confers constitutional finality.

**Exit criteria.** X7-1: autonomous evolution occurs **only where TI-1…TI-5 all hold** (VR-60). X7-2: no source mutation occurs outside the declared governed path (VR-42). X7-3: no terminal state becomes claimable and **no rollback path is introduced** (VR-58).

**Wave verdict.** **W7 is not enterable.** It is recorded for completeness and as the boundary condition on every wave beneath it.

---

### 18.2 What the wave model is, and is not

It is an **ordering**, derived from evidence, of what may be attempted after what. It is **not** an authorization: no wave in this model is authorized, and this artifact carries `authority: NONE`. It contains no calendar, no duration and no velocity — B-7 refuses these on the stated ground that *"the repository carries no velocity evidence"*, and one prior document's 70-week schedule is explicitly not inherited (`C-4`).

**The value of the model is the ordering, not the inventory.** Reading the 47 CONDITIONAL items as a work list — particularly beginning at W4, which is the most visible and most satisfying work — would violate SQ-1, SQ-2 and SQ-6 simultaneously and produce a larger population of non-durable, unclassifiable kinds than exists today.

---

## 19. Dependency Graph

### 19.1 The derived ordering

```
Detection  →  Classification  →  Measurement  →  Ownership  →  Authority  →  Identity  →  Entity  →  Assimilation  →  Evolution
```

Each arrow is forced by measured evidence. The two that invert the directive's original framing are marked.

| Edge | Forced by | Consequence of violating |
|---|---|---|
| **Detection → Classification** | Both are roots; neither depends on the other. They are **jointly first** and mutually independent | Neither is delayed by the other; nothing else may precede either |
| **Detection → Measurement** | CH-2 · SQ-1 · R-01 | A fix cannot be shown to work; the reconstruction test's own fixture calls `bootstrap()` |
| **Classification → Measurement** | CH-3 · SQ-2 · SQ-3 | Every change is unclassifiable; extending a broken classifier extends the breakage |
| **Measurement → Ownership** | SQ-9 · CR-21 | Ownership closure asserted in prose form already shown unreliable |
| **Ownership → Authority** | SQ-12 | Ownership rows cannot be joined to enforcement |
| **Authority → Identity** | T-22.2 and T-6.2 share **one missing key** | Identity federation becomes a second authority (`CAA-INV-04`) |
| **Identity → Entity** | SQ-6 — **and by the same artifact**: T-7.3 *is* T-6.1 seen from the entity dimension | Opening kinds multiplies non-durable kinds |
| **Entity → Assimilation** | SQ-4 · R-27 CRITICAL | The binding layer routes untrusted, unidentified, unowned input into reasoning |
| **Assimilation → Evolution** | SQ-10 · R-44 CRITICAL | Autonomy over undurable, unowned, undetectable, untrusted state |

**Two inversions of the directive's original ordering, both preserved from the predecessor:**

1. **Detection precedes truth authority**, not the reverse. Without T-19.1, neither the durability fix nor the authority fix can be shown to work (CH-2).
2. **Security precedes assimilation.** T-21.1 must precede T-14.3, or the binding layer routes untrusted input into arbitrary import (SQ-4).

### 19.2 The graph with transformations attached

```
═══ ROOTS — no dependencies; nothing else is verifiable or governable without these ═══

  ┌─────────────────────────────┐        ┌─────────────────────────────┐
  │ DETECTION                   │        │ CLASSIFICATION              │
  │ T-19.1  init-independence   │        │ T-19.2  R-09 predicate      │
  │ EXECUTABLE · W0             │        │ EXECUTABLE · W0             │
  └──────────────┬──────────────┘        └──────────────┬──────────────┘
                 │                                      │
                 │        ┌─────────────────────────────┐│
                 │        │ TRUST (independent root)    ││
                 │        │ T-21.1  trust before import ││
                 │        │ EXECUTABLE · W0 · CH-5      ││
                 │        └──────────────┬──────────────┘│
                 │                       │               │
═══ DURABILITY + INTEGRITY ══════════════│═══════════════│════════════════
                 ▼                       │               ▼
  ┌──────────────────────────────┐       │   ┌──────────────────────────┐
  │ T-6.1  committed existence   │       │   │ T-19.3 class extension   │
  │        document + loader     │       │   │ CONDITIONAL · W1         │
  │ ⇒ RA-01…RA-11, RA-13         │       │   └──────────────────────────┘
  │ EXECUTABLE · W0              │       │
  └──────┬───────────────────────┘       │   ┌──────────────────────────┐
         │  ┌──────────────────────────┐ │   │ T-26.2 gate self-appl.   │
         │  │ T-26.1 vocab persistence │ │   │ CONDITIONAL · W1         │
         │  │ + closure disclosure     │ │   └──────────────────────────┘
         │  │ EXECUTABLE · W0 · RA-12  │ │
         │  └──────────────────────────┘ │
         │                               │
         │  INDEPENDENT INTEGRITY (W0, no predecessors)
         │  T-13.1 refuse-before-register   T-23.4 verify-on-load
         │  T-14.2 closure provenance       T-17.3 schema/code sync
         │  T-24.4 scale-clause classification   T-21.3 adversarial bounds (W1)
         │
═══ MEASUREMENT — instrumentation of claims ═════════════════════════════
         │
  ┌──────▼─────────────────────────────────────────────┐
  │ T-23.3  16 unboundedness axes → executable probes  │
  │ CONDITIONAL · W1 · CR-21 · required before ANY      │
  │ success claim (SQ-9 / EP-7)                         │
  └──────┬─────────────────────────────────────────────┘
         │        ┌────────────────────────────────────┐
         │        │ T-19.5 impact wiring (coverage     │
         │        │        disclosed)                  │
         │        │ T-13.3 substrate coverage          │
         │        │        MUST follow detection (SQ-7)│
         │        │ CONDITIONAL · W1 · R-24 CRITICAL   │
         │        └────────────────────────────────────┘
         │
═══ OWNERSHIP → AUTHORITY (parallel track; does not block W0/W1) ════════
         │
  T-22.2 machine-readable authority key ── CONDITIONAL (decision) ── W2
     │
     ├──► T-6.2 identity federation  ── CONDITIONAL ── W3   ┐ same
     ├──► T-8.2 governing truth model ── CONDITIONAL ── W2  ┘ missing key
     │
     ▼
  T-22.1 evidence kinds registered ── CONDITIONAL (R-52) ── W2
     │
     ▼
  T-22.3 391 assignments ratified ── ★ BLOCKED — OWNER ACT ── W2
     │
     ├──► T-14.1 declaration 25.5%→100% ── ★ BLOCKED ── W2
     ├──► T-22.4 capability admission ── ★ BLOCKED — Article 28, EXTERNAL ── W2
     └──► T-24.3 autonomy ── PROHIBITED ── W7

═══ IDENTITY ════════════════════════════════════════════════════════════
  T-6.3 identifier width · T-6.4 code alphabet · T-6.5 birth adoption
  CONDITIONAL · W3  (all downstream of T-6.1; T-6.5 behind T-6.2)

═══ ENTITY / CONTEXT / VOCABULARY — all depend on T-6.1 durability ══════
  T-7.1 T-7.2 T-7.3 · T-8.1 T-8.3 · T-9.1 T-9.2 T-9.3 T-9.4
  T-10.1(preserve) T-10.2 · T-11.1 T-11.2 T-11.3 · T-12.1 T-12.2
  T-13.2 · T-15.2 · T-21.2 · T-23.2 · T-24.2
  CONDITIONAL · W4      ⇐ T-9.4 is the empirical proof of this layer
     │
     │   ┌──────────────────────────────────────────────┐
     │   │ T-15.3 lifecycle reconciliation (DECISION)   │
     │   │ gates ⇒ T-15.1 · T-24.2 · T-9.2  (SQ-8)      │
     │   └──────────────────────────────────────────────┘
     │
═══ ASSIMILATION — convergence ══════════════════════════════════════════
  ┌──▼───────────────────────────────────────────────────┐
  │ T-14.3  assimilation ↔ intelligence binding layer    │
  │ requires: identity · context · relationship ·        │
  │           security · impact  ALL on the path         │
  │ CONDITIONAL · W5 · R-27 CRITICAL · must be LAST      │
  │ T-15.1 artifact form · T-15.4 non-document adapters  │
  └──────────────────────────────────────────────────────┘

═══ TECHNOLOGY / EXPERIENCE / INTELLIGENCE (decision-gated, parallel) ═══
  T-17.1 protocol A-or-B (CONSTITUTIONAL) ──► T-17.2 ★ BLOCKED
  T-18.1 experience scope ──► T-18.2
  T-16.1 T-16.2 T-16.3 · T-20.1 T-20.2 T-20.3
  CONDITIONAL · W6

═══ TERMINAL — requires TI-1…TI-5 all holding ═══════════════════════════
  T-19.4 source self-modification   ── PROHIBITED ── W7
  T-24.3 autonomous evolution       ── PROHIBITED ── W7 · R-44 CRITICAL
  T-23.1 T-24.1 T-24.5 (preservation) ── PROHIBITED ── W7
```

### 19.3 The critical path

```
T-19.1 + T-19.2  →  T-6.1  →  T-23.3  →  W4 kind openness  →  W5 binding  →  (W7 unreachable)
```

**Six ordered steps.** Everything else is parallel or in the authority track. The first two are jointly first and mutually independent.

### 19.4 The twelve hard sequencing constraints

| # | Constraint | Consequence of violating it |
|---|---|---|
| SQ-1 | T-19.1 before T-6.1 | The durability fix cannot be shown to work; CH-2 persists |
| SQ-2 | T-19.2 before anything governed | Every change is unclassifiable and fails closed |
| SQ-3 | T-19.2 before T-19.3 | Extending a broken classifier extends the breakage |
| SQ-4 | T-21.1 before T-14.3 | The binding layer routes untrusted input into arbitrary import |
| SQ-5 | T-21.1 before T-20.3 | Provider conclusions enter through an execution hole |
| SQ-6 | T-6.1 before all kind openness | Opening kinds multiplies non-durable kinds |
| SQ-7 | T-19.1 before T-13.3 | Narrowing selection without verified coverage converts fail-wide into **fail-silent** |
| SQ-8 | T-15.3 before T-15.1 / T-24.2 | A status vocabulary is meaningless while six lifecycle models coexist |
| SQ-9 | T-23.3 before any success claim | Success asserted in prose form already shown unreliable |
| SQ-10 | TI-1…TI-5 before T-19.4 / T-24.3 | Autonomy over undurable, unowned, undetectable, untrusted state |
| SQ-11 | T-17.1 decision before T-17.2 | Records the validators would reject if scanned |
| SQ-12 | T-22.2 before T-22.3 | Ownership rows cannot be joined to enforcement |

### 19.5 What must happen first

**T-19.1 and T-19.2, jointly and before anything else.** Neither depends on anything. Both are small — one cross-process measurement and one predicate function. Together they restore the two faculties the programme cannot proceed without: the ability to **detect that a fix worked**, and the ability to **classify what is being changed**. Every other transformation in this determination is unverifiable or ungovernable until they exist.

### 19.6 Where the graph exits the repository

Four terminals have **no in-repo predecessor that discharges them**:

| Terminal | Terminus | Instrument that refuses to fabricate it |
|---|---|---|
| T-22.3 — 391 ownership ratifications | Owner act | `UCOD-001:401` — *"will not fabricate them to close it"* |
| T-22.4 — UKAP/UREE registration | `CEP-002` **Article 28**, external | *"no competent ratifying authority located within the repository"* |
| T-17.1 — protocol Option A vs B | Constitutional decision on `USL-15` | CR-15 — *cannot be an engineering act* |
| CH-6 — facet frame invariant-or-limitation | Constitutional decision | `engine/uckp/facets.py` — *"a thirty-fourth facet is a constitutional amendment"* |

Plus two scope decisions (T-18.1 experience, T-19.4/T-24.3 autonomy) that no engineering act supplies.

---

## 20. Risk Register

Risks are of **transformation**, not of the current state. All 65 inherited risks are carried; none is retired. Severity reflects consequence if the risk materialises during execution.

### 20.1 The eight CRITICAL risks

| ID | Description | Impact | Dependency | Mitigation | Execution impact | Severity |
|---|---|---|---|---|---|---|
| **R-24** | Narrowing substrate selection without verified coverage **converts fail-wide into fail-silent** | Impact analysis returns confident clean verdicts over blind spots; the failure is silent by construction | T-13.3 | Must never precede T-19.1 (SQ-7); measure coverage before and after; fail-wide remains default for uncovered subjects | **Forces T-13.3 out of W0 into W1.** Any attempt to start it earlier is a stop condition | **CRITICAL** |
| **R-27** | Binding the assimilation planes early routes **unvalidated, unidentified, unowned, unsecured input into reasoning** | The system reasons over untrusted input and records the conclusions as governed truth | T-14.3 | Must be **last** among its five dependencies (SQ-4) | **Forces T-14.3 to W5 and defines W5's prerequisites.** The highest-severity sequencing error available | **CRITICAL** |
| **R-44** | **Autonomy over undurable, unowned, undetectable, untrusted state** | The system changes itself under conditions in which no change can be classified, verified, owned or reverted | T-19.4, T-24.3 | TI-1…TI-5 must all hold (SQ-10); plus the six closures of §17.3 | **Forces both items to PROHIBITED.** W7 is not enterable | **CRITICAL** |
| **R-46** | A model whose output cannot be re-derived **reintroduces belief over evidence** | Defeats the architecture's founding purpose: evidence over assertion | T-20.1 | Falsifiability mandatory; non-falsifiable estimates refused | Holds T-20.1 CONDITIONAL on a scope decision; the refusal of prediction is **retained in the target** | **CRITICAL** |
| **R-49** | **Hardening the provider path narrows the one genuinely open admission mechanism (PC-14)** | The fix for CH-5 could close the only door through which an unforeseen kind arrives without a code change | T-21.1 | Preserve open admission **while** requiring verification — verify, do not restrict | **Constrains the shape of the highest-priority W0 fix.** T-21.1 remains EXECUTABLE; its design is bounded | **CRITICAL** |
| **R-52** | Registrable evidence kinds could let a data edit declare weak evidence constitutive, **fabricating ownership** | Ownership — the binding constraint on the whole programme — becomes forgeable by data | T-22.1 | Constitutive status requires **constitutional authority**, not registration | Holds T-22.1 CONDITIONAL despite being engineering-READY | **CRITICAL** |
| **R-54** | **Automated population of 391 ownership assignments is exactly the fabrication the machinery refuses** | Destroys the anti-fabrication property that makes ownership meaningful; `require_owner()` exists to prevent this | T-22.3 | `UCOD-001:401` — will not fabricate to close. **No automation permitted** | **Forces T-22.3 to BLOCKED.** W2 cannot exit in-repo | **CRITICAL** |
| **R-63** | *A programme under pressure will be tempted to add rollback. It must not* | A rollback path would let a failed mutation **appear** reverted after its truth has propagated | T-24.5 | `ORL-15` — no engine, scheduler, automation platform or executor. Declared bound instead of mechanism | Discharges autonomy requirement 5 **by declared bound**, raising the pre-admission bar. Forces T-24.5 PROHIBITED | **HIGH → treated as CRITICAL in effect** |

*Note on R-63: the inherited register rates it HIGH. It is grouped here because it is the constraint that makes the autonomy requirement set unsatisfiable in the ordinary way, and because §31.1 identifies "fabrication and belief" — R-46 and R-54 — as one of the three CRITICAL clusters that R-63 structurally belongs to. The inherited severity is preserved as **HIGH** in §20.6.*

### 20.2 Sequencing risks

| ID | Description | Impact | Dependency | Mitigation | Execution impact | Severity |
|---|---|---|---|---|---|---|
| **R-01** | The existing reconstruction test's fixture calls `bootstrap()`, so it **cannot detect failure** of the durability fix | T-6.1 could be executed, appear to pass, and have failed | T-6.1, T-7.3 | T-19.1 must exist first (SQ-1) | Sets W0 intra-wave order: 0.1 before 0.4 | **HIGH** |
| **R-10** | Reality-mode-aware certification refuses subjects currently accepted | Previously certified subjects become uncertifiable | T-8.3 | Sequence after T-23.2 | Intra-W4 ordering constraint | MEDIUM |
| **R-31** | Consolidating six lifecycle models invalidates stage assignments **corpus-wide** | Every artifact's stage becomes questionable at once | T-15.3 | **Federation is the lower-risk path** | Shapes the W2 decision; gates W4/W5 via SQ-8 | **HIGH** |
| **R-37** | Populating the API registry while `USL-15` stands creates records the validators would reject if scanned | Registry and validation planes contradict each other | T-17.2 | Blocked on T-17.1 (SQ-11) | Forces T-17.2 to BLOCKED | **HIGH** |
| **R-48** | Provider conclusions bypassing validation **become belief** | Same failure class as R-46, entering through a different door | T-20.3 | Sequence after T-21.1 (SQ-5) | Holds T-20.3 to W6 | **HIGH** |
| **R-23** | Moving refusal to registration time may create a **window in which an unruled relation exists** | A momentary state the ontology is built to make impossible | T-13.2 | Atomic co-registration | Constrains T-13.2's implementation shape in W4 | **HIGH** |
| **R-58** | Instrumenting the axes **will invalidate a standing certification** | `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md` loses its basis | T-23.3 | Expected — **it is the point of the exercise** | Makes X1-2 a disclosure event, not a pass/fail gate | MEDIUM |

### 20.3 Ownership and authority risks

| ID | Description | Impact | Dependency | Mitigation | Execution impact | Severity |
|---|---|---|---|---|---|---|
| **R-25** | Declaring knowledge canonical without a ratified owner creates **canonical truth nobody can amend** | Permanently unamendable truth — worse than an open gap | T-14.1 | Blocked on T-22.3 | Forces T-14.1 to BLOCKED | **HIGH** |
| **R-53** | Making ownership rows machine-readable **exposes rows that do not resolve** | The measured ownership figure will worsen | T-22.2 | **Intended effect** | X2-1 is a disclosure event | MEDIUM |
| **R-55** | Proceeding under *"already operational"* while the blocking determination stands admits capabilities under **contested authority** | Capabilities admitted by an authority two determinations disagree exists | T-22.4 | **Resolve F-20 first** | Forces T-22.4 to BLOCKED; F-20 is a W2 precondition | **HIGH** |
| **R-02** | Declaring one mint governing invalidates identifiers already issued by the others; federation may itself **become a second identity authority** | Either existing identifiers break, or `CAA-INV-04` is violated | T-6.2 | `CAA-INV-04` must hold; lineage preserved for already-issued identifiers | Holds T-6.2 CONDITIONAL; shapes W3 | **HIGH** |
| **R-06** | Instantiating root primitives becomes a path to **amending** them | The ratified ontology becomes editable by the mechanism meant to realise it | T-7.1 | `UCPA-L-04` and ratified standing must hold | Constrains T-7.1 in W4 | **HIGH** |
| **R-11** | If universality becomes registrable, a **data edit could declare an arbitrary kind universal** | Constitutional status conferred by data | T-9.1 | Universal flag requires constitutional authority | Splits T-9.1 into an engineering leg and an authority-gated attribute | **HIGH** |
| **R-12** | Registering an authority level **without a declared position** makes precedence partial and resolution non-deterministic | Authority resolution stops being total | T-9.2 | Position mandatory at registration | Constrains T-9.2; same hazard recurs at R-50, R-61 | **HIGH** |

### 20.4 Runtime authority risks

| ID | Description | Impact | Dependency | Mitigation | Execution impact | Severity |
|---|---|---|---|---|---|---|
| **R-41** | Introducing initialization-independence measurement **turns green gates red** | Multiple gates begin failing on the same commit | T-19.1 | **Intended effect; not a regression** | Must be communicated before W0, or W0 looks like a break | MEDIUM |
| **R-42** | Restoring classification may reveal **mutations certified while unclassified** | Past certifications lose their basis | T-19.2 | **Expect disclosure, not silence** | W0 produces a disclosure obligation (CR-17) | **HIGH** |
| **R-43** | The current defect exists **because a class was registered without a predicate**; extension must make that impossible | The same outage recurs through the extension mechanism | T-19.3 | **Refuse at registration** (VR-41) | Defines X1-1 | **HIGH** |
| **R-64** | Disclosure reveals ~230 closures, several **contradicting standing certifications** | Notably T-23.3 Axes 13–14 | T-26.1 | Disclosure precedes remediation (EP-6). **Register gets worse before better** | W0 lowers the measured position on purpose | MEDIUM |
| **R-59** | An unconditional `True` in `verify()` means **current reliance is unfounded**; fixing may invalidate adopted records | Records believed verified were never verified | T-23.4 | Fix regardless; expect invalidation | W0 item; expect adopted records to fail | **HIGH** |
| **R-28** | The frozen-corpus guard **silently succeeds under substitution** — independent of the neutrality question | The headline closure verdict rests on an unguarded external corpus | T-14.4 | **Fix regardless of the storage decision** | The guard leg is executable independently of the W2 decision | **HIGH** |
| **R-26** | Resolving the closure verdict changes `gaps=0` to non-zero (evidence: 91); **every citing artifact becomes stale** | Wide documentary consequence | T-14.2 | Truth-restoring; expect the consequence | W0 item with corpus-wide documentary fallout | MEDIUM |
| **R-45** | Impact analysis over **10.4%** substrate coverage produces confident reports with wide blind spots | False confidence in change safety | T-19.5 | **Disclose coverage with every verdict** | Defines X1-3 | **HIGH** |
| **R-65** | Gate self-application **will likely fail initially** | The anti-closure mechanism fails its own test | T-26.2 | **Correct outcome; the reason to do it** | X1-5 is expected to fail first | LOW |

### 20.5 Autonomy risks

| ID | Description | Impact | Dependency | Mitigation | Execution impact | Severity |
|---|---|---|---|---|---|---|
| **R-44** | *(carried from §20.1)* Autonomy over undurable, unowned, undetectable, untrusted state | The worst configuration available | T-19.4, T-24.3 | SQ-10 — TI-1…TI-5 all hold | **T-19.4 = PROHIBITED · T-24.3 = PROHIBITED** | **CRITICAL** |
| **R-60** | Opening the stage set may introduce a stage **from which the cycle cannot continue** | Non-termination — a structurally guaranteed property — is lost | T-24.1, T-24.2 | **No terminal state claimable** (VR-58) | Constrains T-24.2 in W4; T-24.1 stays PROHIBITED | **HIGH** |
| **R-61** | A registered stage without a declared position breaks `append`'s fail-closed ordering | Stage ordering becomes non-deterministic | T-24.2 | Position mandatory | Same hazard as R-12/R-50 | **HIGH** |
| **R-63** | A programme under pressure **will be tempted to add rollback. It must not** | A failed mutation could appear reverted after its truth propagated | T-24.5 | Declared bound, never a mechanism | Autonomy requirement 5 discharged by bound; **raises the pre-admission bar** | **HIGH** |
| **R-47** | An open reasoner registry is a **code-loading surface** | CH-5 reproduced in a second location | T-20.2 | **Register, never import from data** | Constrains T-20.2 in W6 | **HIGH** |

### 20.6 Complete inherited register — the remaining risks

All carried at inherited severity; none retired. Execution impact is stated where it changes a wave or a state.

| ID | Description | Transformation | Severity | Execution impact |
|---|---|---|---|---|
| R-03 | Identifier pattern mirrored in ≥3 places; divergence reproduces the C-34/C-35 drift failure | T-6.3 | MEDIUM | T-17.3 (W0) establishes the drift-prevention pattern this needs |
| R-04 | Wider code alphabet changes collision semantics | T-6.4 | LOW | Re-verify collision refusal |
| R-05 | Wiring birth into hot paths may mint as a side effect — precedent: **140 minted by a drift check** | T-6.5 | **HIGH** | Birth only on declared intent, never as a side effect |
| R-07 | Opening node types permits **unbounded edges** — the condition `ContextOntology.__init__` refuses | T-7.2 | **HIGH** | Rule totality over the widened set |
| R-08 | Axis list as data means a **data edit can weaken a constitutional gate** | T-8.1 | **HIGH** | Gate must refuse an empty or shrinking axis set |
| R-09 | Declaring one truth model governing **orphans artifacts authored under the other** | T-8.2 | MEDIUM | Migration or federation |
| R-13 | A registered value type with an unsound validator admits malformed values | T-9.3 | MEDIUM | Validators pure and total |
| R-14 | **Lowest-risk transformation in the register**; failure mode is a failed resolve, not a corrupted verdict | T-9.4 | LOW | Makes T-9.4 the cheapest available proof of openness |
| R-15 | **The risk is transforming what is already correct.** Spatial addressing is universal today | T-10.1 | **HIGH** | Forces T-10.1 to **PROHIBITED** |
| R-16 | A spatial registry that adopts a canonical frame **destroys the property S-01 protects** | T-10.2 | **HIGH** | Replicate *"`primary` is never normalised"* exactly |
| R-17 | A temporal migration that forces a default frame **destroys the property being adopted** | T-11.1 | **HIGH** | This is why non-adoption was deliberate (`P4-F-007`) |
| R-18 | Re-qualifying certified baseline dates **changes certified content** | T-11.2 | **HIGH** | Authority act; an exemption is lower-risk but records a permanent hole |
| R-19 | Scope creep: treating run timestamps as constitutional temporal claims | T-11.3 | LOW | Declare the boundary |
| R-20 | A conversion executor evaluating string terms **becomes a code-execution surface** | T-12.1 | **HIGH** | Total, pure, non-eval evaluator; **must not reproduce CH-5** |
| R-21 | Re-typing `Money` touches priced commitments; the closure must be **disclosed before fixed** | T-12.2 | MEDIUM | EP-6 — disclosure precedes remediation |
| R-22 | Same validate-after-mutate pattern as CH-5 | T-13.1 | MEDIUM | The W0 fix establishes the pattern T-21.1 also needs |
| R-29 | Replacing `additionalProperties: false` may permit unvalidated fields, so **the schema stops being a contract** | T-15.1 | **HIGH** | Declared-extension mechanism, never an open shape |
| R-30 | Low | T-15.2 | LOW | — |
| R-32 | A reader registered as data implies **code loaded as data** | T-15.4 | **HIGH** | Must not reproduce CH-5 |
| R-33 | Low; remediation already specified with an acceptance criterion | T-16.1 | LOW | — |
| R-34 | `FUTURE_LANGUAGE` is bound to a **live adapter class**; retiring it requires re-homing that binding | T-16.2 | MEDIUM | — |
| R-35 | Adding a symbolic axis **speculatively is worse than determining first** | T-16.3 | MEDIUM | Record as unresolved (the `unknown`-as-valid discipline) |
| R-36 | The marker check is a **naive substring scan** — `"lambda"`, `"rest"` false-positive; narrowing it narrows unintended places | T-17.1 | **HIGH** | Fix matching semantics as part of any change |
| R-38 | Low risk, **high diagnostic value** | T-17.3 | LOW | Establishes drift prevention for T-15.1 and T-6.3 |
| R-39 | Building experience speculatively adds a dimension with no consumer; withdrawing **forecloses a direction** | T-18.1 | MEDIUM | Scope decision first |
| R-40 | Low; the **rendering-technology refusal must survive** | T-18.2 | LOW | — |
| R-50 | Opening severities without declared ordering makes blocking non-deterministic | T-21.2 | **HIGH** | Same total-order hazard as R-12 |
| R-51 | The `record()` docstring/implementation mismatch means **current reliance is unfounded**; fixing may reject accepted content | T-21.3 | MEDIUM | — |
| R-56 | Degrading certification integrity while opening the subject type | T-23.1, T-23.2 | **HIGH** | Content-addressing and determinism **must survive** |
| R-57 | A protocol-typed subject whose rules cannot interpret its inputs produces **confident wrong verdicts** | T-23.2 | **HIGH** | Preserve the input guarantee |
| R-62 | Low; an existing gate does not cover documents it should | T-24.4 | LOW | — |

### 20.7 Risk concentration and what it forces

**Eight CRITICAL risks, clustering into three patterns:**

1. **Sequencing violations (R-24, R-27, R-44)** — each is correct work in the wrong order. All three are prevented by SQ-7, SQ-4 and SQ-10 respectively. **These three alone determine the wave boundaries of W1, W5 and W7.**
2. **Openness without authority (R-49, R-52)** — opening a vocabulary whose members carry authority (constitutive evidence, provider execution) converts a data edit into an authority act. Both require an authority gate on the **specific privileged attribute**, not on registration generally.
3. **Fabrication and belief (R-46, R-54)** — introducing non-falsifiable output, or populating ownership automatically, would each defeat the architecture's founding purpose. Both are explicitly refused by standing determinations and **must remain refused**.

### 20.8 The risk this determination itself creates

Recorded for completeness. This determination classifies **10 transformations as EXECUTABLE**. That classification is a statement about **safety and sequence**, not authorization — no wave in §18 is authorized and this artifact carries `authority: NONE`.

The specific misreading to guard against: treating the 47 CONDITIONAL items as a backlog and starting at **W4**, which is the most visible and most satisfying work. Doing so violates SQ-1, SQ-2 and SQ-6 simultaneously and produces a larger population of non-durable, unclassifiable kinds than exists today.

**The value of this determination is the boundary, not the inventory.**

---


## 21. Authority Requirements

### 21.1 Existing authorities — what is actually located

| Authority | Instrument | Competence | Standing |
|---|---|---|---|
| **Engineering execution** | `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` | May perform, verify and record engineering acts within existing declared law | **PRESENT.** This is the authority under which all 10 EXECUTABLE transformations proceed |
| **Ownership resolution machinery** | `require_owner()`, `OwnershipFabricationError`, declared grain (`S-11`) | May *resolve* an owner; **refuses to infer one** | **PRESENT and production-ready.** Data 27.86% populated |
| **Vocabulary registration** | `engine/uckp/vocabulary.py` (`S-13`) | Append-only; refuses redefinition; register-then-use | **PRESENT.** Openness proved by probe |
| **Anti-closure enforcement** | `check_open_world` (`S-14`) | Fails closed on bound tokens, closed registries, claimed terminal states | **PRESENT** in four engines; **not applied to the gate population** |
| **Constitutional mutation gateway** | `engine/constitution/gateway.py:203` | Admits constitutional mutations | **PRESENT and defective** — refuses legitimate mutations in a fresh process (RA-07) |
| **Certification issuance** | `universal_certification/` (`S-10`) | Content-addressed, digest-anchored, deterministic | **PRESENT** — and confers **no constitutional finality** by its own declaration |
| **Programme owners** | Per-programme declarations | May accept changes within their own programme | **PRESENT but partial** — 12 truth facets and 4 of 11 assimilation stages have **no declared owner** |

### 21.2 Missing authorities — what is not located

| Missing authority | What it would decide | Evidence of absence |
|---|---|---|
| **A ratifier of anything** | Whether any closure, ownership assignment or determination is ratified | `MP2-C-04`: three located instruments record **no authority in the corpus competent to ratify**. `VAC-01`: Tier T1 **vacant**. Maximum attainable verdict anywhere: `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`) |
| **A single canonical authority** | Which of three planes governs | `CANONICAL-AUTHORITY-DETERMINATION.md`: no single canonical-authority artifact; three **mutually disclaiming** planes; declaration and enforcement *"do not share a key"* |
| **A universal identity authority** | Which of four mints governs, or how they federate | Governance model is `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` with *"No universal identity authority created."* `CAA-INV-04` **forbids creating a second one** |
| **A capability admission authority** | Whether a new capability may be admitted | Unregistered; `Owner: UNCLEAR / Authority: UNCLEAR`; blocked on `CEP-002` **Article 28** with *"no competent ratifying authority located within the repository"*. F-20 records two determinations **disagreeing on whether the block exists** |
| **A cross-class transaction authority** | Whether a mutation may span programme classes atomically | B-7: the located determination **rejects** creating one and selects a capability holding no authority. *"an authority spanning 7 programmes — **none exists**"* |
| **A lifecycle authority** | Which of six lifecycle models governs | `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md`: six incompatible models; **determination artifacts are in a governance void** — including this artifact |
| **An amendment authority** | Whether `USL-15` may be narrowed; whether the 33-facet frame is invariant | Both are constitutional positions. No instrument in the corpus claims amendment competence |

### 21.3 Authority boundaries — what each may and may not do

```
┌──────────────────────────────────────────────────────────────────────┐
│ ENGINEERING EXECUTION AUTHORITY                                      │
│   MAY:  repair a defect inside existing declared law                 │
│         wire an existing capability to an existing call site          │
│         persist what is already derivable from committed data        │
│         disclose a closure                                           │
│         add an instrument that measures an existing claim             │
│   MAY NOT: ratify · declare canonical · amend a constitutional        │
│            position · create an authority · populate ownership ·      │
│            confer finality · open a privileged attribute              │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│ PROGRAMME OWNER AUTHORITY                                            │
│   MAY:  accept a change to a subject it owns                         │
│   MAY NOT: own what it has not declared · ratify · span programmes   │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│ CONSTITUTIONAL AUTHORITY                    ← NOT LOCATED            │
│   WOULD DECIDE:  USL-15 Option A/B · CH-6 facet frame · universality │
│                  flag · constitutive evidence status · autonomy      │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│ EXTERNAL CONSTITUENT ACT                    ← OUTSIDE REPOSITORY     │
│   WOULD DISCHARGE:  CEP-002 Article 28 · ownership ratification      │
└──────────────────────────────────────────────────────────────────────┘
```

### 21.4 Ownership dependency, restated as an authority requirement

Ownership is not a data-completeness problem wearing an authority costume; it is an authority problem wearing a data costume. `UCOD-001:332` separates the two cleanly — **machinery ready, data 27.86% populated** — so the dependency is on **data and ratification**, not on capability. But the data cannot be produced by the capability, because the capability exists specifically to refuse producing it (**R-54, CRITICAL**).

| Requirement | Discharged by | Available? |
|---|---|---|
| 391 (or 398) ownership assignments | Each subject's owner | **NO** |
| Ratification of any assignment | A competent ratifier | **NO — none located** |
| A machine-readable authority key | An authority spanning three disclaiming planes | **NO — a decision** |
| Constitutive status for an evidence kind | Constitutional authority | **NO — a decision** |
| UKAP/UREE registration | `CEP-002` Article 28, external | **NO — outside the repository** |

### 21.5 What can proceed without new authority

All **10 EXECUTABLE** transformations, on three grounds jointly:

1. Each is a **repair, a wiring, a persistence of already-derivable data, a disclosure, or an instrument** — every one inside the engineering-execution boundary of §21.3.
2. None declares anything canonical, ratifies anything, amends a constitutional position, or opens a privileged attribute.
3. **Ownership gates none of them.** B-5 §27.4: ownership does not gate detection, durability or trust. The four highest-impact transformations sit **upstream** of CH-4.

| ID | Authority basis for proceeding |
|---|---|
| T-19.1 | Adds an instrument that measures an existing claim |
| T-19.2 | Repairs a declared rule that has no predicate — restores declared law to function |
| T-21.1 | Repairs a defect against a stated security property; wires existing trust machinery |
| T-6.1 | Persists what is already derivable from committed data; the loader already exists |
| T-26.1 | Same, for vocabularies; plus disclosure, which is explicitly an engineering act |
| T-13.1 | Single-site defect repair against a stated refusal |
| T-23.4 | Repairs `verify()` to do what its own contract states |
| T-14.2 | Removes an out-of-repository dependency from an in-repository verdict |
| T-17.3 | Reconciles a schema with the code it already drifted from |
| T-24.4 | Applies an existing gate to documents it should already cover |

### 21.6 What requires an authority decision

**Five decisions**, none of which any engineering act supplies. Each is a choice, not a finding — which is why further discovery will keep returning the same answer.

| # | Decision | Question | Gates |
|---|---|---|---|
| **D-1** | **CH-6 — facet frame** | Is the 33-facet frame an **invariant** or a **limitation**? | Whether "infinite evolution" means unbounded population within a fixed descriptive frame, or an open frame. **TI-3.** No transformation below W4 depends on it; the final answer to the programme's objective does |
| **D-2** | **T-17.1 — protocol** | **Option A** (neutral core, representable declared periphery) or **Option B** (representable anywhere, requiring `USL-15` amendment)? | T-17.2 (BLOCKED), T-15.4 partially, T-18.2. CR-15 is **constitutional and cannot be an engineering act** |
| **D-3** | **T-18.1 — experience** | Is experience in scope for UCOS Ω∞ — populate the interaction model, or withdraw the schemas? | T-18.2. Building speculatively adds a dimension with no consumer; withdrawing forecloses a direction |
| **D-4** | **T-19.4 / T-24.3 — autonomy** | Is autonomy wanted, and under what invariants? | W7 entirely. **Gated on TI-1…TI-5 all holding first** |
| **D-5** | **T-22.2 / T-22.3 / T-22.4 — ownership and authority** | Which plane governs; who ratifies; does the Article 28 block exist (F-20)? | T-14.1, T-6.2, T-8.2, T-22.3, T-22.4, and the ownership property of **every** item |

Secondary decisions of the same class, each gating a smaller set: **T-15.3** lifecycle authority (gates T-15.1, T-24.2, T-9.2 via SQ-8) · **T-8.2** governing truth model · **T-11.2** frame-at-mint policy · **T-14.4** storage neutrality · **T-16.3** symbolic axis · **T-20.1** intelligence scope · **T-20.3** whether provider conclusions are admissible at all.

### 21.7 What cannot be assumed

Recorded explicitly, because assuming any of these would convert a determination into an authorization:

| Must not be assumed | Why | Instrument that refuses it |
|---|---|---|
| That an unowned subject may be changed because no owner objects | Ownership is **fail-closed**, not permissive-by-default | `require_owner()` raises rather than infer |
| That 391 assignments may be derived from evidence already present | That is the fabrication the machinery exists to prevent | `UCOD-001:401` — *"will not fabricate them to close it"* |
| That "already operational" discharges a standing block | Two determinations disagree that the block exists (F-20). Proceeding admits capabilities under **contested authority** | R-55 |
| That a machine certificate confers finality | It declares that it does not | `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` |
| That an unqualified certification is attainable | The ceiling is `CERTIFIED-PROVISIONAL`; Tier T1 is vacant | `UCCEP-F-004`, `VAC-01` |
| That `USL-15` may be narrowed to close a representational gap | It is constitutional intent, enforced at 9 sites | TP-04, TP-05, `pyproject.toml:19-22` |
| That a 34th facet, 16th stage, 2nd certification class or 17th context kind is an engineering act | Each is an amendment by the repository's own doctrine | `engine/uckp/facets.py` |
| That a federation crosswalk is not a new authority | It may become one, and one is forbidden | `CAA-INV-04` |
| That this determination authorizes any wave | It carries `authority: NONE` | §1.2, §18.2 |

### 21.8 Authority requirements verdict

> **Sufficient authority exists to execute exactly the ten EXECUTABLE transformations and nothing more.** Beyond them, the programme requires **five decisions and one external act**, and no engineering sequence removes that dependency. The most consequential structural finding is that the missing authorities are not missing *capabilities* — every mechanism they would operate already exists and is production-ready. They are missing **choices and constituent acts**, which is why B-5 concluded that further discovery *"will keep returning the same answer, because the unresolved items are not findable by analysis. They are choices."*

---

## 22. Evidence Requirements

### 22.1 The six evidence classes

Every transformation must produce all six classes, or declare which class is unavailable and why. A transformation that produces effect without evidence is indistinguishable from one that produced nothing.

| Class | Requirement | Instrument that must produce it |
|---|---|---|
| **E-1 Execution evidence** | What was changed, at which site, under which classification | `classify()` returning a class — **currently `ERROR` for every subject** (M-C). **T-19.2 is a precondition for E-1 on every transformation, including itself** |
| **E-2 Validation evidence** | The named `VR-nn` executed with a recorded result | The 63 validation requirements of §23. **VR-01, VR-02, VR-40, VR-47 are prerequisites for the rest** |
| **E-3 Provenance** | Append-only lineage from prior state to new state, attributable | The evolution ledger **has serialization and lacks a production writer** (B-6 self-correction to `F-3`). `save_provenance` exists at `store.py:370` |
| **E-4 Reproducibility** | The same result from a bare fresh clone with no environment variables set | Artifact-layer reconstruction is **proven byte-identical** (`S-12`, `RTBD-001`). The closure verdict is **not** — it depends on an out-of-repo corpus plus an env var (RA-16) |
| **E-5 Deterministic verification** | The same verdict in a fresh interpreter and a bootstrapped one | **Does not exist at baseline.** Zero of 29 gates vary initialization order (CH-2). **T-19.1 is the deliverable that creates E-5** |
| **E-6 Rollback evidence** | Not a rollback path — a **declared bound** on what cannot be undone | Rollback is **refused** (`S-09`, R-63). E-6 is discharged by declaring the bound, never by building a mechanism |

### 22.2 Evidence availability at baseline, per class

| Class | Available? | Blocking condition |
|---|---|---|
| E-1 Execution | **NO** | `classify()` → ERROR for all subjects. One missing predicate |
| E-2 Validation | **PARTIAL** | Real and fail-closed; 6 of 15 chain stages unvalidated; `verify.sh --full` **exits 1** on 4 of 15 stages |
| E-3 Provenance | **PARTIAL** | Serialization present; production writer absent. No identifier migration (IDF-17); `derive_change_events` **drops** stale subjects |
| E-4 Reproducibility | **PARTIAL** | Artifact layer proven; the headline closure verdict is not; the frozen-corpus guard **silently succeeds under substitution** |
| E-5 Deterministic verification | **NO** | CH-2. The instrument does not exist |
| E-6 Rollback bound | **NO** | The bound has not been declared. The mechanism must not be built |

**Four of six evidence classes are unavailable or partial at baseline, and two of them (E-1, E-5) are absolutely unavailable.** This is the evidential form of the NOT READY verdict.

### 22.3 Evidence required per transformation

Applying the six classes across the population. `†` marks a transformation that **creates** the evidence class it is measured by, which is why it must come first.

| Transformation group | E-1 | E-2 | E-3 | E-4 | E-5 | E-6 | Note |
|---|---|---|---|---|---|---|---|
| **T-19.1** | after T-19.2 | VR-01 † | required | required | **† creates E-5** | n/a | The instrument is the deliverable |
| **T-19.2** | **† creates E-1** | VR-40 | required | required | after T-19.1 | n/a | Self-referential: its own execution evidence depends on itself; discharged by VR-40 directly |
| **T-21.1** | after T-19.2 | VR-47 | required | required | after T-19.1 | n/a | R-49: must evidence that open admission **survived** |
| **T-6.1** | after T-19.2 | VR-01, VR-02 | required | required | **required — R-01** | n/a | Existing test cannot detect failure; E-5 is mandatory |
| **T-26.1** | after T-19.2 | VR-02, VR-62 | required | required | required | n/a | Disclosure register is itself E-1 for ~230 closures |
| **W0 integrity set** (T-13.1, T-23.4, T-14.2, T-17.3, T-24.4) | after T-19.2 | VR-21, VR-57, VR-25, VR-37, VR-61 | required | required | required | n/a | T-14.2 **creates** E-4 for the closure verdict |
| **W1 measurement set** | required | VR-41, VR-56, VR-43, VR-23, VR-63, VR-49 | required | required | required | n/a | T-23.3 **creates** the evidence form all later success claims need |
| **W2 authority set** | required | VR-50, VR-51, VR-52, VR-53, VR-10, VR-30, VR-27 | required | required | required | n/a | E-2 for VR-52 requires **ratification** — unavailable in-repo |
| **W3 identity set** | required | VR-03, VR-04, VR-05, VR-06 | **lineage for already-issued identifiers mandatory** (CR-02) | required | required | declared bound on re-mint | R-02: lineage evidence is the safety property |
| **W4 expansion set** | required | VR-07…VR-20, VR-22, VR-29, VR-48, VR-55, VR-59 | required | required | required | declared bound per vocabulary | Probe evidence is the required form (TI-3) |
| **W5 assimilation set** | required | VR-26, VR-28, VR-31 | required | required | required | declared bound | E-2 for VR-26 requires the Ownership stage to resolve |
| **W6 technology set** | required | VR-32…VR-39, VR-44, VR-45, VR-46 | required | required | required | declared bound | CR-15 evidence is a **recorded decision**, not a measurement |
| **W7 autonomy set** | required | VR-42, VR-58, VR-60 | **production writer required** | required | required | **declared bound mandatory** | All six classes must hold **simultaneously** before entry |

### 22.4 The three evidence disciplines that must not be relaxed

| Discipline | Statement | Instrument |
|---|---|---|
| **Absence is named, never blank** | An unavailable evidence class is declared with a reason, not omitted | The `unknown`-as-valid and `UNRESOLVED`-with-derivation-path patterns |
| **Openness is proved by probe, not asserted** | `is_extensible` admits a probe term and **fails an invariant if refused**; `check_open_world` fails if a registry has **nothing left to admit** | `S-13`, `S-14` |
| **Disclosure precedes remediation** | A closure is disclosed before it is fixed | EP-6; R-21, R-64 |

### 22.5 Expected evidence degradation

Recorded so that the correct outcome is not mistaken for failure:

| Wave | Expected degradation | Risk | Correct interpretation |
|---|---|---|---|
| W0 | Green gates turn red | R-41 | **Intended.** The gates were green because they could not see |
| W0 | Mutations certified while unclassified are revealed | R-42 | Disclosure obligation (CR-17), not a new defect |
| W0 | ~230 closures surface, several contradicting standing certifications | R-64 | The register gets worse before better |
| W0 | `gaps=0` becomes non-zero (evidence: 91); citing artifacts go stale | R-26 | **Truth-restoring** |
| W0 | Records believed verified are shown never to have been verified | R-59 | Current reliance was unfounded |
| W1 | Axes 13 and 14 **fail** their probes | R-58, VR-56 | Expected; a standing certification loses its basis |
| W1 | Gate self-application fails initially | R-65 | **The correct outcome and the reason to do it** |
| W2 | Ownership rows that do not resolve become visible | R-53 | Intended effect |

### 22.6 Evidence requirements verdict

> **Two of six evidence classes are absolutely unavailable at baseline (E-1 execution, E-5 deterministic verification), and both are created by W0 transformations that are themselves EXECUTABLE.** This is the precise sense in which the programme is NOT READY but has a safe entry point: the work that produces the missing evidence does not itself require the missing evidence — T-19.2 is validated directly by VR-40, and T-19.1 by being the instrument. Every transformation after W0 requires all six classes, and **E-6 must always be discharged by a declared bound rather than a rollback mechanism.**

---

## 23. Validation Requirements

### 23.1 The required validation chain

```
Discovery  →  Classification  →  Impact Analysis  →  Testing  →  Validation  →  Certification
```

| Link | Baseline state | Blocking finding | Discharged by |
|---|---|---|---|
| **Discovery** | Real; closed in shape; **detection is declaration-bound** — `AD-G-01` guarantees undisclosed closures stay invisible | 230 of 239 closures undisclosed (M-A) | T-26.1 (W0), T-15.2 (W4) |
| **Classification** | **NON-FUNCTIONAL** — `classify()` → ERROR for every subject (M-C) | One missing predicate, R-09 | **T-19.2 (W0)** |
| **Impact Analysis** | Exists, **unwired**, **10.4%** substrate coverage | Confident reports with wide blind spots (R-45) | T-19.5, T-13.3 (W1) |
| **Testing** | Substantial and **structurally unable to detect the defects that matter** — zero of 29 gates vary initialization order; the reconstruction fixture calls `bootstrap()` | CH-2, R-01 | **T-19.1 (W0)** |
| **Validation** | Real, fail-closed, and **process-dependent** for 43 of 72 kinds; 6 of 15 chain stages unvalidated; `verify.sh --full` **exits 1** on 4 of 15 stages | M-B | **T-6.1 (W0)** + baseline repair (B-7 Wave 1 precondition) |
| **Certification** | Mechanically sound; **evidentially unable to support a success claim**; ceiling `CERTIFIED-PROVISIONAL` | 16 axes on prose; Axes 13–14 contradicted | **T-23.3 (W1)** — CR-21 |

**The chain is broken at three of six links, and all three repairs are in W0 or W1.**

### 23.2 The four prerequisite validation requirements

Of the 63 inherited requirements, four are prerequisites for the rest: **without them, satisfaction of any other requirement cannot be established.**

| # | Requirement | Establishes |
|---|---|---|
| **VR-01** | The same subject yields the same verdict in a fresh interpreter and a bootstrapped one, for all 72 admissible kinds | **TI-2** — initialization independence |
| **VR-02** | Delete runtime memory → reload canonical → reconstruct → compare identical, for all 13 truth objects (currently 4 / 2 / 7) | **TI-1** — durability |
| **VR-40** | `validate_rule_coverage()` returns empty; `classify()` returns a class for a sample spanning all nine classes | Classification totality |
| **VR-47** | An unsigned or non-allowlisted descriptor is refused **before** import | **TI-5** — trusted admission |

### 23.3 Gate requirements

| Requirement | Baseline | Required state | Transformation |
|---|---|---|---|
| A gate must declare its **mutation mode** | Only **4 of 29** declare one | Every gate declares one mode (`run` mints and emits · `gate` verifies and mutates nothing · `stats` prints) | B-7 Wave 4 decision (`H-06`/`CR-09`) |
| A gate must not mutate what it verifies | Precedent exists: `UEG-000001`'s mutation-tested purity guard — injecting `ucos_ensure_venv` **fails** `test_verify_does_not_ensure_the_environment_it_is_verifying:826` | Uniform across the population | T-26.2 |
| The gate population must pass the openness test it enforces | **No gate register, no generator, no `check_open_world` applied to gates** | Gates are a registered population subject to `S-14` | **T-26.2** (VR-63) |
| A gate must vary initialization order | **Zero of 29 do** | At least one gate varies it, for all 72 kinds | **T-19.1** (VR-01) |
| The canonical gate must pass | `verify.sh --full` **exits 1** — 4 of 15 stages fail | Exits 0, or each failure is owned and declared | B-7 Wave 1 precondition — **not a transformation in this population** |
| Gate evidence must be distinguishable from pre-existing failure | 38 pre-existing tracked modifications unanalysed; B-7 condition `0.6` **currently failing** | Dirty tree isolated by owning programme | **Precondition to W0 measurement** |

### 23.4 Cross-process validation

The single most important validation requirement in the determination, because **it is the one that does not exist at all**.

| Property | Baseline | Required |
|---|---|---|
| Same verdict across processes | **FAILS** — M-B: `False` before `bootstrap()`, `True` after, same commit, zero file changes | VR-01 across all 72 kinds |
| Reproducibility harness spans processes | **NO** — both builds run in **one interpreter** sharing env, adapter and signer (`determinism/reproduce.py:275-330`) | Two interpreters, varied initialization order |
| Path reproducibility | **PROVEN** — two cross-process gates establish it | Preserved. It is **not** initialization independence (TA-26) |
| Reconstruction test independence | **FAILS** — its own fixture calls `bootstrap()` (R-01) | A fixture that does not bootstrap |
| Artifact-layer reconstruction | **PROVEN byte-identical from a bare fresh clone** (`S-12`) | Preserved |

**Distinction that must not be collapsed:** the repository has proven **path reproducibility** and has never tested **initialization independence**. TA-26 records exactly this. Presenting the former as the latter is the evidential error CH-2 consists of.

### 23.5 Initialization independence

| Requirement | Instrument | Status |
|---|---|---|
| No verdict depends on process history | VR-01 | **Instrument absent — T-19.1 creates it** |
| No truth is held in process-global mutable state | VR-02, VR-62 | **Two such authorities exist** (RA-01, RA-12) |
| No cache hides a bootstrap trigger | — | `@cache roles_holding` calls `bootstrap()` **then hides it** (RA-06) |
| Every truth object declares its reconstruction contract | VR-02 | **No truth object declares one** (TA-12) |
| A loader replays verbatim and refuses re-derivation | — | `from_document()` does; `durable_identity.from_dict` **re-mints instead of replaying** (RA-17, TA-21) |

### 23.6 Mutation safety

| Requirement | Baseline | Transformation | Validation |
|---|---|---|---|
| Every change is classifiable | **NO** — ERROR for all subjects | T-19.2 | VR-40 |
| A class cannot be registered without a predicate | **NO** — this is why the outage exists | T-19.3 | **VR-41** |
| No mutation occurs before validation | **NO** at three sites: CH-5 import, cyclic relationship registration, certification chain load | T-21.1, T-13.1, T-23.4 | VR-47, VR-21, VR-57 |
| No source mutation outside the declared governed path | Held by **three confinements** | T-19.4 — **PROHIBITED** | VR-42 |
| No identifier is minted as a side effect | **VIOLATED historically** — 140 minted by a drift check | T-6.5 constraint (R-05) | VR-06 |
| Impact is known before mutation | **NO** — impact unwired, 10.4% coverage | T-19.5, T-13.3 | VR-43, VR-23 |
| Ownership is resolved before mutation | **NO** — 0% ratified | T-22.3 — **BLOCKED** | VR-52 |
| No terminal state becomes claimable | **HELD** | T-24.1, T-24.2 | VR-58, VR-59 |
| No rollback path is introduced | **HELD** | T-24.5 — **PROHIBITED** | VR-58 |

### 23.7 The 63 validation requirements, mapped to waves

| Wave | Validation requirements | n |
|---|---|---|
| **W0** | VR-01, VR-02, VR-21, VR-25, VR-37, VR-40, VR-47, VR-57, VR-61, VR-62 | 10 |
| **W1** | VR-23, VR-41, VR-43, VR-49, VR-56, VR-63 | 6 |
| **W2** | VR-10, VR-24, VR-27, VR-30, VR-50, VR-51, VR-52, VR-53 | 8 |
| **W3** | VR-03, VR-04, VR-05, VR-06 | 4 |
| **W4** | VR-07, VR-08, VR-09, VR-11, VR-12, VR-13, VR-14, VR-15, VR-16, VR-17, VR-18, VR-19, VR-20, VR-22, VR-29, VR-48, VR-55, VR-59 | 18 |
| **W5** | VR-26, VR-28, VR-31 | 3 |
| **W6** | VR-32, VR-33, VR-34, VR-35, VR-36, VR-38, VR-39, VR-44, VR-45, VR-46 | 10 |
| **W7** | VR-42, VR-54, VR-58, VR-60 | 4 |
| | **TOTAL** | **63** |

`10+6+8+4+18+3+10+4 = 63` ✔

### 23.8 Validation requirements verdict

> **The validation chain is broken at Classification, Testing and Validation — three of six links — and every repair is EXECUTABLE in W0.** The decisive requirement is **cross-process validation, which does not exist in any form**: the repository has proven path reproducibility and has never tested initialization independence, and TA-26 records that these are not the same property. Until VR-01 has an instrument, no transformation in this determination can be shown to have worked, and **the four prerequisite requirements (VR-01, VR-02, VR-40, VR-47) are precisely the exit criteria of W0.**

---

## 24. Certification Requirements

### 24.1 The ceiling that bounds everything in this section

**The maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`** (`UCCEP-F-004`). Tier T1 is **vacant** (`VAC-01`). `MP2-C-04` records that three located instruments find **no authority in the corpus competent to ratify**. `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` — **no machine certificate confers constitutional finality by its own declaration.**

Every requirement below is bounded accordingly. **A criterion promising unqualified certification would be unsatisfiable by construction and is therefore never stated.**

### 24.2 How a transformed capability becomes certified

```
   TRANSFORMATION EXECUTED
            │
            ▼
   ┌────────────────────────────────────────────────────────┐
   │ 1. EVIDENCE ACCEPTANCE                                 │
   │    All six evidence classes (E-1…E-6) produced, or     │
   │    each absence named with a reason. Openness proved    │
   │    by probe, never asserted.                            │
   └────────────────────┬───────────────────────────────────┘
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │ 2. VALIDATION ACCEPTANCE                               │
   │    The named VR-nn executed cross-process with a        │
   │    recorded result. VR-01/02/40/47 must already hold.   │
   └────────────────────┬───────────────────────────────────┘
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │ 3. INSTRUMENTATION GATE  ← CR-21, overriding           │
   │    The claim form must be executable, not prose.        │
   │    Until T-23.3 lands, NO success claim is credible.    │
   └────────────────────┬───────────────────────────────────┘
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │ 4. AUTHORITY ACCEPTANCE                                │
   │    A located authority competent for THIS class of      │
   │    change accepts it. Engineering execution suffices    │
   │    for repair/wiring/persistence/disclosure only.       │
   └────────────────────┬───────────────────────────────────┘
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │ 5. LIFECYCLE CERTIFICATION                             │
   │    The subject resolves to exactly ONE lifecycle        │
   │    authority. Six models coexist today; determination   │
   │    artifacts have none. BLOCKED on T-15.3.              │
   └────────────────────┬───────────────────────────────────┘
                        ▼
   ┌────────────────────────────────────────────────────────┐
   │ 6. EVOLUTION CERTIFICATION                             │
   │    Non-termination preserved · stage ordering intact ·  │
   │    refusals preserved · re-entry, never terminal.       │
   └────────────────────┬───────────────────────────────────┘
                        ▼
        VERDICT: CERTIFIED-PROVISIONAL   ← ceiling, always
```

### 24.3 Evidence acceptance

| Criterion | Requirement | Refusal condition |
|---|---|---|
| Completeness | All six classes of §22.1 produced, or each absence **named with a reason** | A blank is refused; a named absence is admissible |
| Form | Executable instrument, digest, or test — **never prose citation** | ~15 root certifications currently fail this and are the reason CR-21 exists |
| Openness | Proved by probe: a term never seen by the release is admitted, and the invariant **fails if it is refused** | An asserted openness is refused (`S-13` `is_extensible`) |
| Content-addressing | Certificate content-addressed, digest-anchored, deterministic ordering | Must survive subject genericity (CR-21, R-56) |
| Disclosure ordering | The closure was disclosed **before** it was fixed | EP-6 |

### 24.4 Authority acceptance

| Change class | Competent authority | Available? |
|---|---|---|
| Defect repair inside declared law | Engineering execution | **YES** |
| Wiring an existing capability | Engineering execution | **YES** |
| Persisting already-derivable data | Engineering execution | **YES** |
| Closure disclosure | Engineering execution | **YES** |
| Adding a measurement instrument | Engineering execution | **YES** |
| Opening a vocabulary | Programme owner + module owner | **PARTIAL** — 12 truth facets unowned |
| Opening a **privileged attribute** (universality flag, constitutive evidence, provider execution) | Constitutional authority | **NO** (R-11, R-52, R-49) |
| Declaring knowledge canonical | Ratified owner | **NO** (R-25) |
| Amending a constitutional position (`USL-15`, CH-6) | Amendment authority | **NO — not located** |
| Ratifying anything | A ratifier | **NO — `MP2-C-04`, `VAC-01`** |

### 24.5 Validation acceptance

Validation is accepted only when executed **cross-process**. A single-process pass is not acceptance, because CH-2 establishes that a single-process harness cannot distinguish a working fix from a fix whose effect is supplied by import order.

| Requirement | Acceptance condition |
|---|---|
| Cross-process execution | Two interpreters, varied initialization order (**T-19.1 creates this**) |
| Prerequisite requirements hold | VR-01, VR-02, VR-40, VR-47 satisfied first |
| Fail-closed preserved | The transformation did not convert a refusal into a default. Specifically: `UNRESOLVED` never permissive; unowned never `UNASSIGNED`; unregistered handler still fails closed; fail-wide still default for uncovered subjects |
| Invariant survival | Named invariants still hold — `UCPA-L-04`, `CAA-INV-04`, rule totality, precedence totality, `primary` never normalised, no terminal state claimable |
| Existing records valid | Where a pattern or schema widened: all 1,461 artifact records still valid; existing certificate digests unchanged |

### 24.6 Lifecycle certification

| Requirement | Baseline | Blocking |
|---|---|---|
| One lifecycle authority per artifact | **Six mutually incompatible models** | **T-15.3 — authority decision** |
| Determination artifacts have a lifecycle | **They have none** — a governance void that includes **this artifact** | T-15.3 |
| Status vocabulary meaningful | Meaningless while six models coexist (SQ-8) | T-15.3 before T-15.1, T-24.2, T-9.2 |
| Stage assignments stable under consolidation | Consolidation invalidates them **corpus-wide** (R-31) | **Federation is the lower-risk path** |

**Consequence recorded honestly:** this determination is itself an artifact with no lifecycle authority, in the governance void `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` identifies. Its own certification ceiling is therefore the same `CERTIFIED-PROVISIONAL` it applies to everything else, and it claims no more.

### 24.7 Evolution certification

| Requirement | Instrument | Must survive every transformation |
|---|---|---|
| Non-termination preserved | `is_terminal` returns `False` because **no state could return `True`** | **YES — VR-58** |
| Stage set open with ordering intact | Position mandatory at registration; `append` admits only the next stage; the cycle still wraps | **YES — VR-59** |
| Refusals preserved | No predictive engine · no rollback · no evolution registry · no second identity authority · no corpus-tuned thresholds | **YES — VR-58, CR-22** |
| Re-entry, never terminal | The target architecture's final clause | **YES** |
| Autonomy only where all five invariants hold | TI-1…TI-5 simultaneously | **YES — VR-60** |

### 24.8 The 23 certification obligations mapped to waves

| Wave | Obligations | Note |
|---|---|---|
| **W0** | CR-01, CR-11, CR-12, CR-13, CR-17, CR-19, CR-22, CR-23 (partial) | CR-01 must **replace**, not supplement, the current single-process determinism evidence. CR-19 is highest urgency |
| **W1** | **CR-21**, CR-11, CR-17, CR-19, CR-23 | **CR-21 is the overriding obligation and must be discharged here** |
| **W2** | CR-06, CR-12, CR-13, CR-20 | CR-20 requires ownership **ratified** — not attainable in-repo |
| **W3** | CR-02, CR-03 | Lineage preserved; drift check mandatory |
| **W4** | CR-04, CR-05, CR-07, CR-08, CR-09, CR-10, CR-11, CR-13, CR-19, CR-22 | CR-09 touches an **existing certification** |
| **W5** | CR-12, CR-13, CR-19 | CR-12 **will change the headline number** |
| **W6** | **CR-15**, CR-14, CR-16, CR-18 | CR-15 is **constitutional and cannot be an engineering act** |
| **W7** | CR-22 + a certification of autonomy that **is not attainable** | Ceiling + vacant tier |

### 24.9 The overriding certification constraint

**CR-21 must be discharged before any other certification is credible.** The repository's standing unboundedness certification rests on prose citation; no machine certificate confers constitutional finality; ~15 root-level certifications assert completeness without evidence binding; and Axes 13–14 are directly contradicted by measurement. Until the 16 axes are instrumented (T-23.3, W1), any claim that a transformation succeeded would be recorded in **the same evidential form this determination has shown to be unreliable — including a claim about this programme.**

### 24.10 Certification requirements verdict

> **Certification is mechanically sound and evidentially insufficient, and no transformation changes the ceiling.** A transformed capability becomes certified by passing six sequential acceptances — evidence, validation, instrumentation, authority, lifecycle, evolution — of which **instrumentation (CR-21) is not yet possible**, **authority is unavailable for every privileged change**, and **lifecycle has six competing claimants**. W0 may be certified at `CERTIFIED-PROVISIONAL` on completion of CR-01/CR-17/CR-19. Nothing may be certified beyond that ceiling, and any artifact claiming otherwise is unsatisfiable by construction.

---

## 25. Forbidden Transformations

### 25.1 The six PROHIBITED transformations

| ID | Transformation | Reason class | Reason |
|---|---|---|---|
| **T-19.4** | Source self-modification | **State — autonomy** | **PROHIBITED.** Requires prior closure of ownership, trust, evidence, validation, rollback and certification. **None closed.** The three confinements are a **safety property, not a gap** (SQ-10, R-44 CRITICAL) |
| **T-24.3** | Autonomous evolution | **State — autonomy** | **PROHIBITED.** Same six closures. Autonomy over undurable, unowned, undetectable, untrusted state is the worst configuration available (R-44 CRITICAL) |
| **T-10.1** | "Remove fixed locations" | **Regression** | The instruction has **no target**. Spatial addressing is already universal: no axis value in code, no defaults, zero-axis root frame, 14 frames already resolving. `PROHIBITED_TOKENS` and the root frame must survive (R-15) |
| **T-23.1** | Certification mechanics | **Regression** | Content-addressed, digest-anchored, deterministically ordered, injectable rules and frames. Transformation degrades integrity (R-56) |
| **T-24.1** | Non-termination | **Regression** | `is_terminal` returns `False` because **no state could return `True`**. Structurally guaranteed and provable (R-60) |
| **T-24.5** | Evolution Registry / Rollback Point refusals | **Regression** | Both refused, correctly, with reasons. *A programme under pressure will be tempted to add rollback. It must not* (R-63) |

**T-19.4 and T-24.3 are prohibited by state and are convertible to CONDITIONAL by an authority decision taken after TI-1…TI-5 all hold.** The other four are prohibited by principle and are **not convertible**.

### 25.2 Forbidden because they would create accidental authority

| Forbidden act | Would create | Refused by |
|---|---|---|
| A federation crosswalk that governs identity | A **second identity authority** | `CAA-INV-04`; R-02 |
| An evolution registry | A second identity authority | `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md`; T-24.5 |
| Making the universality flag registrable without an authority gate | Constitutional status conferred **by data edit** | R-11 (HIGH) |
| Making evidence-kind constitutive status registrable | **Fabricated ownership** by data edit | **R-52 (CRITICAL)** |
| Axis list as pure data with no gate floor | A **data edit weakening a constitutional gate** | R-08 (HIGH) |
| Registering an authority level, severity or stage without a declared position | **Non-deterministic** precedence, blocking or ordering | R-12, R-50, R-61 (HIGH) |
| Leaving truth in process-global mutable state | Two authorities that decide truth and leak across capabilities | RA-01, RA-12 |
| A cross-class transaction authority | An authority spanning 7 programmes — the located determination **rejects** creating one | B-7 §2 |

### 25.3 Forbidden because they would create unowned evolution

| Forbidden act | Refused by |
|---|---|
| **Automated population of the 391 (or 398) ownership assignments** | **R-54 (CRITICAL).** `UCOD-001:401` — *"will not fabricate them to close it."* This is precisely the fabrication `require_owner()` exists to prevent |
| Declaring any concept canonical without a ratified owner | **R-25 (HIGH).** Creates canonical truth nobody can amend |
| Defaulting an unowned subject to `UNASSIGNED` rather than failing closed | VR-52; `OwnershipFabricationError` |
| Autonomous mutation of an unowned subject | **Ungoverned by construction.** §7.3.3 |
| Admitting capabilities under contested authority while the blocking determination stands | **R-55 (HIGH).** Resolve F-20 first |
| Binding the assimilation planes while the Ownership stage resolves against an **empty catalogue** | **R-27 (CRITICAL)** |

### 25.4 Forbidden because they would create unverifiable mutation

| Forbidden act | Refused by |
|---|---|
| Executing **any** transformation while `classify()` returns ERROR for every subject | EP-2, SQ-2. **This is why W0 begins with T-19.2** |
| Executing T-6.1 before T-19.1 | EP-1, SQ-1, **R-01** — the existing test cannot detect its failure |
| Extending the classifier before it is total | SQ-3, **R-43** |
| **Narrowing substrate selection before coverage is verified** | **R-24 (CRITICAL)** — converts fail-wide into **fail-silent** |
| Claiming any success before the 16 axes are instrumented | EP-7, SQ-9, **CR-21** |
| Certifying with single-process evidence | CR-01 must **replace**, not supplement |
| Registering a mutation class without a predicate | **R-43.** The current outage exists for exactly this reason |
| Introducing a conversion executor that evaluates string terms via `eval` | **R-20 (HIGH)** — a second CH-5 |
| Registering a reader as data such that code is loaded as data | **R-32 (HIGH)** — a second CH-5 |
| Importing a reasoner from data | **R-47 (HIGH)** — a second CH-5 |
| Minting an identifier as a side effect | **R-05 (HIGH).** Precedent: **140 minted by a drift check** |
| Introducing non-falsifiable output or a predictive engine | **R-46 (CRITICAL).** Belief over evidence |
| Corpus-tuned thresholds | `S-09`; CI-enforced |
| An internal forecaster for AI-model evolution | Refused by design with a stated reason (B-7 §2) |

### 25.5 Forbidden because they would regress a constitutional invariant

| Forbidden act | Invariant protected |
|---|---|
| Opening the 7/7/7 hierarchy grammar | **C-40** — ratified |
| Opening the 4 root primitives, or using instantiation as an amendment path | **C-41** — ratified; `UCPA-L-04` (**R-06**) |
| Registering all six serialization readers | **C-46** — the gate **requires** an unregistered format to remain unregistered; `S-04` fails if nothing is left to admit |
| Removing `SystemType.UNKNOWN` | **C-50** — `unknown` first-class is the architecture working |
| Constraining the identity namespace/local patterns | **P-07, P-08** — open by pattern with no allow-list; already universal |
| Narrowing or repealing `USL-15` by engineering action | Constitutional intent; TP-04, TP-05. **Option B is an amendment, and this determination does not open it** |
| Adding a 34th facet, 16th stage, 2nd certification class or 17th universal context kind as an engineering act | **CH-6** — an amendment by the repository's own doctrine |
| Adopting a canonical spatial frame, or normalising `primary` | `S-01`, **R-16** |
| Forcing a default temporal frame | `S-02`, **R-17** — destroys the property being adopted |
| Making SI the default measurement system | `S-03` — *"never the default"* |
| Replacing `additionalProperties: false` with an open shape | **R-29** — the schema stops being a contract |
| Making any terminal state claimable | `S-08`, **R-60**, VR-58 |
| Selecting a rendering technology | **R-40** |
| Hardening the provider path so open admission is lost | **R-49 (CRITICAL)** — PC-14 is the only door an unforeseen kind can enter through |

### 25.6 The reconciliation variance, restated in the forbidden context

**Seven true invariants** are recorded by count in the inherited classification (§25.4 of B-5); **six** are explicitly enumerated with the `invariant` marker (C-40, C-41, C-46, C-50, P-07, P-08). The seventh is referenced by the count and is not separately enumerated in the evidence read.

**This determination carries the count as 7 and the verified enumeration as 6, and does not invent the seventh.** No execution state depends on the difference: all six verified invariants and any unenumerated seventh are equally outside the 67-transformation population, equally out of scope for execution, and equally forbidden to transform.

### 25.7 Forbidden transformations verdict

> **Six transformations are PROHIBITED — two by state, four by principle — and seven constraints are true invariants outside the population entirely.** Beyond those, five classes of act are forbidden regardless of which wave is in progress: creating accidental authority, creating unowned evolution, creating unverifiable mutation, regressing a constitutional invariant, and reproducing CH-5 in a new location. **The last of these deserves emphasis: four separate transformations (T-12.1, T-15.4, T-20.2, T-20.3) each carry a path to re-creating the exact defect W0 exists to close.**

---

## 26. Allowed Transformations

### 26.1 EXECUTABLE — 10 transformations, allowed now

Allowed under engineering-execution authority, in W0, in the stated intra-wave order, subject to EP-1 through EP-7 and to the risk constraints named.

| # | ID | What is allowed | Bounding constraint |
|---|---|---|---|
| 1 | **T-19.1** | Add cross-process initialization-independence measurement | Must be first with T-19.2. Expect green gates to turn red (R-41) — intended |
| 2 | **T-19.2** | Implement the R-09 predicate; restore total classification | Must be first with T-19.1. Expect disclosure of mutations certified while unclassified (R-42) |
| 3 | **T-21.1** | Verify before import; close CH-5 | **Must preserve open admission while requiring verification (R-49 CRITICAL).** Verify, do not restrict |
| 4 | **T-6.1** | Commit the existence document; wire the load path before any validation | **Strictly after T-19.1 (SQ-1, R-01)** |
| 5 | **T-26.1** | Persist vocabularies; disclose every closed enumeration | Disclosure precedes remediation (EP-6). Expect ~230 closures, several contradicting standing certifications (R-64) |
| 6 | **T-13.1** | Refuse before register at the cyclic-relationship site | Establishes the pattern T-21.1 also needs (R-22) |
| 7 | **T-23.4** | Verify chains on load; make `verify()` return `False` for unverifiable records | Expect adopted records to fail (R-59) |
| 8 | **T-14.2** | Remove the out-of-repo corpus and env var from the closure verdict | Expect `gaps=0` → non-zero and corpus-wide staleness (R-26) — truth-restoring |
| 9 | **T-17.3** | Reconcile connector schema with runtime `SOURCES` | Low risk, **high diagnostic value**: establishes drift prevention for T-6.3 and T-15.1 (R-38) |
| 10 | **T-24.4** | Classify the five scale-local closure clauses | Independent, low risk |

### 26.2 CONDITIONAL — 47 transformations, allowed on a stated condition

| ID | Wave | Condition that must be discharged first |
|---|---|---|
| T-19.3 | W1 | T-19.2 (SQ-3); extension must **refuse predicate-less classes at registration** (VR-41, R-43) |
| T-23.3 | W1 | T-19.1; **and this discharges CR-21, the precondition for every later success claim** (SQ-9) |
| T-19.5 | W1 | T-19.1; coverage disclosed with every verdict (R-45) |
| T-13.3 | W1 | T-19.1 (SQ-7). **R-24 CRITICAL** — fail-wide must remain default for uncovered subjects |
| T-26.2 | W1 | T-19.2; expect initial failure (R-65) — the correct outcome |
| T-21.3 | W1 | Independent; fixing may reject currently accepted content (R-51) |
| T-22.1 | W2 | **Authority decision** on constitutive evidence status (**R-52 CRITICAL**) |
| T-22.2 | W2 | **Authority decision** — a key spanning three disclaiming planes; expect non-resolving rows to surface (R-53) |
| T-8.2 | W2 | **Authority decision**; migration or federation for orphaned artifacts (R-9) |
| T-15.3 | W2 | **Authority decision**; **federation is the lower-risk path** (R-31). Gates T-15.1, T-24.2, T-9.2 (SQ-8) |
| T-14.4 | W2 | **Authority decision** on neutrality. **The guard leg (R-28) must be fixed regardless** |
| T-6.2 | W3 | **Authority decision**; `CAA-INV-04` must hold; lineage preserved for issued identifiers (R-02) |
| T-6.3 | W3 | T-6.1 + T-15.1; single source of truth across ≥3 mirrored sites (R-03); all 1,461 records valid |
| T-6.4 | W3 | T-6.1; re-verify collision refusal under a wider alphabet (R-04) |
| T-6.5 | W3 | T-6.2; **birth only on declared intent, never as a side effect** (R-05) |
| T-7.1 | W4 | T-6.1; instantiation **must not become an amendment path** (R-06); `UCPA-L-04` holds |
| T-7.2 | W4 | T-6.1; rule totality over the widened set — **no unbounded edge** (R-07) |
| T-7.3 | W4 | T-6.1 — *this is T-6.1 seen from the entity dimension* |
| T-8.1 | W4 | T-6.1; **gate must refuse an empty or shrinking axis set** (R-08) |
| T-8.3 | W4 | T-23.2 first (R-10); a simulated-reality assertion cannot be certified as actual |
| T-9.1 | W4 | T-6.1; **universal flag requires constitutional authority** (R-11) |
| T-9.2 | W4 | T-6.1 + T-15.3; **position mandatory at registration** (R-12) |
| T-9.3 | W4 | T-6.1; validators pure and total (R-13) |
| T-9.4 | W4 | Layer 3 openness. **Lowest risk in the register (R-14); the cheapest proof of openness available** |
| T-10.2 | W4 | Layer 3; **`primary` never normalised; no canonical frame adopted** (R-16) |
| T-11.1 | W4 | T-11.2 decision; **must not force a default frame** (R-17) |
| T-11.2 | W4 | **Authority decision** — re-qualifying certified dates changes certified content (R-18) |
| T-11.3 | W4 | T-11.2; declare the run-timestamp boundary (R-19) |
| T-12.1 | W4 | Layer 3; **total, pure, non-eval evaluator — must not reproduce CH-5** (R-20) |
| T-12.2 | W4 | **Disclosure before remediation** (EP-6, R-21) |
| T-13.2 | W4 | T-6.1; **atomic co-registration — no window with an unruled relation** (R-23) |
| T-15.2 | W4 | T-6.1; low risk (R-30) |
| T-21.2 | W4 | T-6.1; **blocking severities remain total** (R-50); partly TRUE MISSING — no threat model exists to open |
| T-23.2 | W4 | T-6.1; content-addressing and determinism **must survive** (R-56); preserve the input guarantee (R-57) |
| T-24.2 | W4 | T-15.3 (SQ-8); **position mandatory; no stage from which the cycle cannot continue** (R-60, R-61) |
| T-14.3 | W5 | **All five domains discharged. R-27 CRITICAL — must be LAST** (SQ-4) |
| T-15.1 | W5 | T-15.3; **declared-extension mechanism, never an open shape** (R-29) |
| T-15.4 | W5 | **Must not load code as data** (R-32); an unregistered serialization must still exist afterwards |
| T-16.1 | W6 | Layer 3/4; **no `en` default in code** (R-33) |
| T-16.2 | W6 | T-6.1; re-home the `FUTURE_LANGUAGE` adapter binding (R-34) |
| T-16.3 | W6 | **Authority decision** — determine before adding (R-35) |
| T-17.1 | W6 | **Constitutional decision A or B**; any change must fix the **naive substring semantics** (R-36) |
| T-18.1 | W6 | **Scope decision** — populate or withdraw (R-39) |
| T-18.2 | W6 | T-18.1; **rendering-technology refusal must survive** (R-40) |
| T-20.1 | W6 | **Scope decision**; **falsifiability mandatory** (R-46 CRITICAL) |
| T-20.2 | W6 | T-6.1; **register, never import from data** (R-47) |
| T-20.3 | W6 | T-21.1 (SQ-5); conclusions treated as **claims requiring validation** (R-48) |

**Count: 6 (W1) + 5 (W2) + 4 (W3) + 20 (W4) + 3 (W5) + 9 (W6) = 47** ✔

### 26.3 What is allowed in aggregate

| Category | Count | Availability |
|---|---|---|
| Allowed **now** | **10** | W0, engineering authority, no decision required |
| Allowed **after a predecessor transformation** | **33** | Dependency order only — no authority act needed |
| Allowed **after an authority decision** | **13** | One of the five decisions of §21.6, or a secondary decision |
| Allowed **only after an external act** | **0** of the CONDITIONAL set | The 4 items requiring an external act are BLOCKED, not CONDITIONAL |
| **Total allowed** | **57** | 10 EXECUTABLE + 47 CONDITIONAL |

**Zero of the 57 requires a new capability.** All resolve to REUSE (11), EXTEND (33), COMPOSE (2), or HOLD-pending-decision. This is the strongest available evidence that the substrate is **incomplete rather than mis-designed**.

### 26.4 Allowed transformations verdict

> **Fifty-seven of sixty-seven transformations are allowed — ten now and forty-seven on stated conditions — and not one of them requires building a new engine.** Thirty-three are gated purely by dependency order, meaning they become available through engineering work alone. Thirteen are gated by a decision. **The programme's constraint is not capability. It is sequence for thirty-three items, choice for thirteen, and a constituent act for four.**

---

## 27. Implementation Boundary

### 27.1 The boundary, stated exactly

> **Implementation may begin at Wave 0, with the ten EXECUTABLE transformations of §26.1, ordered T-19.1 and T-19.2 first, and nowhere else.**

### 27.2 Minimum prerequisites before any implementation begins

| # | Prerequisite | State | Discharged by |
|---|---|---|---|
| **MP-1** | The 38 pre-existing tracked modifications isolated by their owning programmes, so that evidence is distinguishable from pre-existing failure | **FAILING** — B-7 §3 condition `0.6`. Includes `verify.sh` +45/−0 and `generated-artifact-registry.json` +864/−0 | Owning programmes. **Not a transformation in this population** |
| **MP-2** | The baseline measurable — `verify.sh --full` failures owned and declared, or repaired | **FAILING** — exits 1, 4 of 15 stages | B-7 Wave 1 preconditions |
| **MP-3** | Acceptance that W0 will **lower** the measured position: green gates turn red, ~230 closures surface, `gaps=0` becomes non-zero, adopted records fail verification | Not yet recorded anywhere | An explicit acknowledgement before W0, or W0 will look like a break |
| **MP-4** | Acknowledgement that no wave is authorized by this determination | — | This artifact carries `authority: NONE` |
| **MP-5** | Agreement that no success will be claimed until CR-21 is discharged in W1 | — | EP-7, SQ-9 |

**MP-1 and MP-2 are outside the 67-transformation population and are genuine preconditions.** Beginning W0 with a dirty, red baseline means W0's evidence cannot be separated from what was already failing — which is the same evidential error CH-2 consists of, committed at the programme level instead of the process level.

### 27.3 The first executable wave

**W0 — Foundation integrity.** Ten transformations. Intra-wave order:

```
STEP 1  (parallel, mutually independent, both first)
        T-19.1  initialization-independence measurement   ← creates E-5, restores DETECTION
        T-19.2  R-09 predicate                            ← creates E-1, restores CLASSIFICATION

STEP 2  (after STEP 1)
        T-21.1  trust before import        ← closes CH-5, the sole CRITICAL security defect
        T-6.1   committed existence document + loader wire ← closes CH-1 (strictly after T-19.1, SQ-1)
        T-26.1  vocabulary persistence + closure disclosure ← closes the second mutable authority

STEP 3  (independent; may run alongside STEP 1 or 2)
        T-13.1  refuse-before-register
        T-23.4  verify-on-load
        T-14.2  closure verdict provenance
        T-17.3  connector schema/code sync
        T-24.4  scale-clause classification
```

**Why these two are first and jointly:** neither depends on anything. Both are small — one cross-process measurement and one predicate function. Together they restore the ability to **detect that a fix worked** and to **classify what is being changed**. Every other transformation in the determination is unverifiable or ungovernable until they exist.

### 27.4 Forbidden starting points

Each of these is a plausible, attractive place to begin, and each is wrong for a stated reason.

| Forbidden start | Why it is attractive | Why it is forbidden |
|---|---|---|
| **W4 kind openness** (T-9.1, T-7.2, T-15.2, T-21.2, T-24.2…) | The most visible and most satisfying work; 21 transformations; obvious progress | **Violates SQ-1, SQ-2 and SQ-6 simultaneously.** Produces a larger population of non-durable, unclassifiable kinds than exists today |
| **T-6.1 alone**, before T-19.1 | It is the single highest-leverage transformation | **R-01:** the existing reconstruction test's fixture calls `bootstrap()`, so it **cannot detect failure**. The work would be unverifiable (SQ-1) |
| **T-13.3 substrate coverage** | Impact analysis at 10.4% coverage is obviously inadequate | **R-24 CRITICAL:** narrowing selection without verified coverage converts fail-wide into **fail-silent** (SQ-7) |
| **T-14.3 assimilation binding** | The engines all exist; it looks like pure wiring | **R-27 CRITICAL:** routes unvalidated, unidentified, unowned, unsecured input into reasoning. Must be **last** among five dependencies (SQ-4) |
| **T-22.3 ownership population** | It is the dominant constraint; 391 rows look like data entry | **R-54 CRITICAL:** exactly the fabrication the machinery refuses. `UCOD-001:401` |
| **T-19.3 classifier extension** | Extending the classifier looks like the fix | **SQ-3:** extending a broken classifier extends the breakage. T-19.2 first |
| **T-17.2 API registry population** | An empty registry requiring `protocol` is an obvious inconsistency | **SQ-11 / R-37:** creates records the validators would reject. Blocked on the A/B decision |
| **W7 autonomy** | It is the programme's stated destination | **R-44 CRITICAL.** PROHIBITED. Requires all five invariants plus six closures, none of which hold |
| **Adding rollback** to de-risk the programme | Rollback makes any programme feel safer | **R-63:** *a programme under pressure will be tempted to add rollback. It must not.* Refused by standing determination |

### 27.5 Evidence required before each wave

| Wave | Entry evidence required | Attainable? |
|---|---|---|
| **W0** | MP-1 (clean, attributable baseline) · MP-2 (measurable gate) · M-A/M-B/M-C as the entry position · located sites for all ten | **YES** — MP-1/MP-2 by owning programmes |
| **W1** | X0-1…X0-11 all satisfied · **TI-1, TI-2, TI-5 holding** · the disclosure register populated | YES, on W0 exit |
| **W2** | X1-1…X1-7 · **CR-21 discharged** · measured substrate coverage · axis probe results incl. the Axes 13–14 failures | YES, on W1 exit |
| **W3** | X2-1…X2-5 · the ownership variance disclosed · **T-22.2 decision recorded** · the 13-shape/58-prefix inventory · all 1,461 records | **PARTIAL** — X2-6/X2-7 require ratification, unavailable in-repo |
| **W4** | X3-1…X3-4 · **T-15.3 decision recorded** · all 14 frames · all 16 context kinds · the 33-row facet_reduction mapping | **PARTIAL** — inherits W2/W3 |
| **W5** | X4-1…X4-7 · **all five T-14.3 dependency domains on the path** · a resolving Ownership stage | **NO** — the Ownership stage cannot resolve while T-22.3 is BLOCKED |
| **W6** | **T-17.1 decision recorded** · **T-18.1 decision recorded** · the 9 `USL-15` enforcement sites · M-D/M-F UI measurements | **NO** — both decisions absent |
| **W7** | **TI-1…TI-5 demonstrated by executable instrument** · provenance production writer · coverage materially above 10.4% · ratified ownership · autonomy decision recorded | **NO** — TI-4 unreachable in-repo; TI-3 depends on undecided CH-6 |

### 27.6 The boundary, drawn

```
        ┌─────────────────────────── MAY BEGIN ────────────────────────────┐
        │                                                                  │
        │   W0 — Foundation integrity — 10 transformations                  │
        │   T-19.1 · T-19.2 · T-21.1 · T-6.1 · T-26.1                       │
        │   T-13.1 · T-23.4 · T-14.2 · T-17.3 · T-24.4                      │
        │                                                                  │
        │   Authority: engineering execution                                │
        │   Certification ceiling: CERTIFIED-PROVISIONAL                     │
        │   Success claim: NOT PERMITTED until CR-21 (W1)                    │
        │                                                                  │
        └──────────────────────────────┬───────────────────────────────────┘
                                       │
  ═══════════════════════════ THE BOUNDARY ══════════════════════════════════
                                       │
        ┌──────────────────────────────▼───────────────────────────────────┐
        │   MAY NOT BEGIN                                                   │
        │                                                                  │
        │   W1  6 CONDITIONAL   — on W0 exit criteria                       │
        │   W2  5 CONDITIONAL + 3 BLOCKED — on decisions and an owner act   │
        │   W3  4 CONDITIONAL   — on T-6.1 and the mint decision            │
        │   W4  20 CONDITIONAL + 1 PROHIBITED — on durability (SQ-6)        │
        │   W5  3 CONDITIONAL   — on five domains (SQ-4, R-27)              │
        │   W6  9 CONDITIONAL + 1 BLOCKED — on two constitutional decisions │
        │   W7  5 PROHIBITED    — on all five invariants + six closures     │
        │                                                                  │
        └──────────────────────────────────────────────────────────────────┘
```

### 27.7 Implementation boundary verdict

> **The boundary is Wave 0 and it is ten transformations wide.** Below it, work is safe, unblocked, requires no authority decision, and restores the four faculties every other transformation depends on. Above it, work is either sequenced behind an unmet predecessor, held by one of five undecided questions, terminated in an external act, or prohibited outright. **Two preconditions sit outside the population and must be discharged first — a clean attributable baseline (MP-1) and a measurable gate (MP-2) — because beginning W0 against a dirty red baseline commits the same evidential error at programme level that CH-2 commits at process level.**

---

## 28. Final Execution Readiness Determination

### 28.1 The question

> **Is UCOS Ω∞ ready to begin controlled transformation execution?**

### 28.2 The answer

# NOT READY

### 28.3 What NOT READY applies to

**NOT READY** is the verdict on the **transformation programme as a whole** — the question the directive asks. It is not a verdict on every part of it.

| Scope | Verdict |
|---|---|
| The transformation programme (67 transformations, W0–W7) | **NOT READY** |
| Wave 0 — the ten EXECUTABLE foundation transformations | **READY**, under the boundary of §27 |
| Waves 1–6 | **NOT READY** — held by predecessors, decisions, or external acts |
| Wave 7 — autonomy | **PROHIBITED**, not merely not-ready |

The distinction is not a hedge. Beginning at W0 is safe and unblocks the rest. Beginning anywhere else is unsafe **regardless of engineering quality**, because the system currently cannot classify what is being changed and cannot detect whether a change worked.

### 28.4 Exact blocking conditions

Six conditions block the programme. Each is stated with what would discharge it and whether that is attainable inside the repository.

| # | Blocking condition | Measured evidence | Discharged by | In-repo? |
|---|---|---|---|---|
| **BC-1** | **The system cannot classify what would be changed.** `classify()` returns `status='ERROR'` for **every** subject. One declared rule (R-09) has no predicate. Every transformation in this determination would itself be an unclassifiable mutation. This is a **live outage in the mechanism that governs change**, not a gap | M-C, reproduced at `HEAD = bae59755` | **T-19.2** — approximately one predicate function | **YES — EXECUTABLE** |
| **BC-2** | **The system cannot detect whether a fix worked.** Zero of 29 gates vary initialization order; the only reproducibility harness builds twice in one interpreter sharing env, adapter and signer; the reconstruction test's own fixture calls `bootstrap()`, so it cannot detect failure of the durability fix | CH-2, RA-14, RA-15, R-01 | **T-19.1** — one cross-process measurement | **YES — EXECUTABLE** |
| **BC-3** | **No success claim would be credible.** 16 unboundedness axes CERTIFIED UNBOUNDED on prose citation alone, with Axes 13–14 contradicted by measurement; no machine certificate confers constitutional finality; ~15 root certifications assert completeness without evidence binding; ceiling is `CERTIFIED-PROVISIONAL` with Tier T1 vacant | T-23.3, `UCERT_AUTHORITY`, `UCCEP-F-004`, `VAC-01` | **T-23.3 / CR-21** — axis instrumentation | **YES — CONDITIONAL on W0 exit** |
| **BC-4** | **Ownership terminates outside the repository.** 391 of 542 unowned (variance: 398/549), assignment catalogue **empty**, **0% ratified**, authority split across three mutually disclaiming planes with no shared key, UKAP/UREE blocked on `CEP-002` Article 28 with *"no competent ratifying authority located within the repository"* — and **27 contradictions remain live**, including F-20 on whether that block exists | CH-4, `UCOD-001`, `MP2-C-04`, F-20 | An **owner act** and an **external constituent act**. Automated population is refused (**R-54 CRITICAL**) | **NO** |
| **BC-5** | **Two foundational questions are undecided, and both change the target.** **CH-6** — whether the 33-facet frame is an invariant or a limitation — determines whether "infinite evolution" means unbounded population within a fixed descriptive frame, or an open frame. **T-17.1** — protocol Option A or B — determines whether an entire dimension is in scope. Beginning implementation before these are decided means discovering mid-programme that the target was wrong | CH-6, C-36, `USL-15`, CR-15 | Two **constitutional decisions**. No engineering act supplies either | **NO** |
| **BC-6** | **The baseline is not measurable.** 38 pre-existing tracked modifications unattributed (including `verify.sh` +45/−0 and `generated-artifact-registry.json` +864/−0); `verify.sh --full` **exits 1** on 4 of 15 stages; B-7 condition `0.6` **currently failing**. W0 evidence could not be distinguished from pre-existing failure | B-7 §3; B-6; working-tree measurement | Owning programmes isolating the dirty tree; baseline repair | **YES — outside this population** |

### 28.5 The minimum conditions to reach READY

| For | Minimum conditions | Count |
|---|---|---|
| **Begin W0 safely** | BC-6 discharged (MP-1, MP-2) + MP-3 acceptance of expected degradation | **1 precondition, in-repo** |
| **Exit W0** | BC-1 (T-19.2) + BC-2 (T-19.1) + T-21.1 + T-6.1 + T-26.1 + 5 integrity repairs → **TI-1, TI-2, TI-5 hold** | **10 transformations, all EXECUTABLE** |
| **Make any success claim** | BC-3 discharged — T-23.3, CR-21 | **1 transformation, CONDITIONAL on W0** |
| **Reach READY for the programme** | BC-4 (owner act + Article 28 external act, F-20 resolved) **and** BC-5 (CH-6 decision + protocol A/B decision) **and** three further decisions: experience scope, autonomy, lifecycle authority | **5 decisions + 1 external act — none attainable by engineering** |

### 28.6 What NOT READY does not mean

**It does not mean the architecture is unsound.** The counter-evidence is decisive: **zero transformations require a new capability.** All 67 resolve to REUSE (11), EXTEND (33), COMPOSE (2), HOLD (19) or acknowledged absence (6). **CREATE = 0.** The three highest-impact fixes are approximately **one predicate function**, **one committed document plus one load call**, and **three edits** — and they close three of the seven defect chains, including the two that gate everything else. The substrate is **incomplete, not mis-designed**.

**It does not mean no work may begin.** Ten transformations are EXECUTABLE, independent of every blocked prerequisite and every undecided question, and they are exactly the work that restores the faculties needed to judge the rest.

**It does not mean further discovery will help.** The remaining foundational gaps are not architectural and are not findable by analysis. They are **five decisions and one external act**:

- **CH-6** — is the 33-facet frame an invariant or a limitation?
- **T-17.1** — Option A or Option B for protocol representation?
- **T-18.1** — is experience in scope?
- **T-19.4 / T-24.3** — is autonomy wanted, and under what invariants?
- **T-15.3** — which of six lifecycle models governs?
- **T-22.3 / T-22.4** — the Article 28 act, which no derived-truth cycle may perform.

Until those are settled, further discovery will keep returning the same answer, **because the unresolved items are not findable by analysis. They are choices.**

### 28.7 The determination stated precisely

UCOS Ω∞ has a **complete and correct architectural understanding of its own finite constraint space** — 78 constraints inventoried and four-way classified, 67 transformations analysed with target, reuse path, dependency, validation, certification and risk, a six-step critical path, twelve hard sequencing constraints, and zero new engines required.

What it lacks is the **operational capacity to change itself under governance**: it cannot classify a change, cannot detect whether a change worked, cannot durably retain what it admits, cannot locate the owner of most of what it contains, cannot credibly certify a success, and has not decided the questions that define the target.

**The execution boundary is therefore exactly ten transformations wide, and the programme beyond it is NOT READY.**

### 28.8 Final answer

| Field | Value |
|---|---|
| Transformation population | **67** |
| EXECUTABLE | **10** |
| CONDITIONAL | **47** |
| BLOCKED | **4** |
| PROHIBITED | **6** |
| True invariants (outside population) | **7 by count · 6 verified · variance disclosed, not invented** |
| Waves | **8** (W0–W7); **1 enterable**; W2 cannot exit in-repo; W7 not enterable |
| Blocking conditions | **6** (BC-1…BC-6); **3 discharged by EXECUTABLE work**; **2 require constitutional decisions**; **1 requires an external act** |
| Minimum conditions to READY | **5 decisions + 1 external constituent act** |
| Certification ceiling | **`CERTIFIED-PROVISIONAL`** (`UCCEP-F-004`, `VAC-01`) |
| New capabilities required | **ZERO** |
| Waves authorized by this determination | **NONE** |
| Programme verdict | **NOT READY** |
| Wave 0 verdict | **READY** — bounded to the ten transformations of §26.1 |

# FINAL DETERMINATION: NOT READY

**Minimum conditions required, restated exactly:**

1. **BC-6** — isolate the 38 pre-existing tracked modifications by owning programme and make `verify.sh --full` measurable, so W0 evidence is distinguishable from pre-existing failure.
2. **BC-1** — implement the R-09 predicate (T-19.2). One function. Restores classification of every change in every dimension.
3. **BC-2** — implement cross-process initialization-independence measurement (T-19.1). One measurement. Restores the ability to detect that a fix worked.
4. **BC-3** — instrument the 16 unboundedness axes (T-23.3, CR-21). Until then, no success claim about anything — including this programme — is credible.
5. **BC-5** — take two constitutional decisions: **CH-6** (is the 33-facet frame an invariant or a limitation?) and **T-17.1** (protocol Option A or B?). Both change the target. Neither is an engineering act.
6. **BC-4** — an **owner act** ratifying ownership, and the **`CEP-002` Article 28 external act**, with **F-20** resolved first. No engineering sequence removes this dependency, and automated population is explicitly refused.

Conditions 1–4 are attainable inside the repository. **Conditions 5 and 6 are not.**

---

*This determination modified no code, configuration, registry, schema, constitution, law, identifier, requirement, ADR, phase, roadmap, or certification. It creates no identity and confers no authority. It authorizes no wave, no transformation and no implementation; it closes no scope and claims no completion. Every gap recorded here remains a gap; no gap has been converted into a fix; and no implementation decision has been made. Where a constraint is constitutional intent rather than defect, this determination records it as such and declines to propose its removal. Where an inherited count and an inherited enumeration disagree — the seventh true invariant — the variance is disclosed and nothing is invented to reconcile it. The single repository mutation is the creation of this file.*

**END DETERMINATION — STOPPED AFTER ARTIFACT CREATION.**
