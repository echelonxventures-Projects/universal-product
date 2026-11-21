# UCOS Ω∞ — ARTIFACT AUTHORITY & VISIBILITY RESOLUTION DETERMINATION

**BC-6 · Step 3 — The canonical authority model for artifact lifecycle visibility**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-ARTIFACT-AUTHORITY-VISIBILITY-RESOLUTION-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, requirement, ADR, phase, class, owner or certification. Authorizes nothing. Assigns nothing. Ratifies nothing. |
| Mode | ANALYSIS ONLY · **NO IMPLEMENTATION · NO CODE CHANGE · NO CONFIGURATION CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Step | **BC-6 Step 3 only.** Steps 4–6 of the companion plan are not performed |
| Predecessors | Step 1 `…BASELINE-INTEGRITY-RECONCILIATION-REPORT.md` (F-2, F-5) · Step 2 `…OBSERVATION-BOUNDARY-RECONCILIATION-DETERMINATION.md` (`OB-1`…`OB-7`) |
| Population classified | **6,730 paths** — 6,188 tracked · 233 ignored · 309 untracked-and-un-ignored |
| Classification vocabularies found | **6 competing · 39 class names · 0 crosswalks** |
| Findings raised | **9** (`AV-1`…`AV-9`) · 2 CRITICAL · 3 HIGH · 3 MEDIUM · 1 LOW |
| Findings resolved | **ZERO.** Determination is not repair |
| Classes, owners or certifications created | **ZERO** |

---

## 1. Objective, Method and Standing Limitation

### 1.1 Objective

Resolve the **canonical authority model for artifact lifecycle visibility**: which authority
decides each independent property of an artifact, and in which order those decisions must
be taken.

Step 1 classified mutations by hand. Step 2 determined the visibility boundary and found
seven defects, of which `OB-1` (the classification obligation is structurally void) and
`OB-3` (authored code is undeclared-invisible) are load-bearing here. Step 3 asks the
question both steps deferred: **is "what kind of artifact is this" even a separable
question from "can git see it"?**

It is measured below that, in this repository, **it is not** — and that this single
collapse explains `F-2`, `F-5`, `OB-3`, `OB-6` and the PORTAL conflict as one defect rather
than five.

### 1.2 Method

Every measurement is a **read** or a **pure function evaluated in memory**. Nothing was
written, committed, staged, restored, deleted, ignored, registered, classified of record,
owned or certified.

| Instrument | Purpose |
|---|---|
| `json.load` on 6 registers | Enumerate every declared classification vocabulary and its class names |
| `platform.repository_intelligence.mutation_classification.validate_rule_coverage()` | First-party test of declared-vs-implemented rule parity |
| `mutation_classification.classify()` | First-party actual classification outcome |
| **Counterfactual precedence evaluation** | `RULE_PREDICATES` applied in declared order, bypassing the coverage refusal, to measure what each subject *would* resolve to once `R-09` exists |
| `git ls-files -z` · `--others --exclude-standard` · `--ignored=matching` | The three visibility populations, exactly |
| `inspect.getsource` on `Repository` and `_r01_repository_state` | Compare implemented predicate against declared predicate |
| `generated-artifact-registry.json` field census | Generation-state values actually in use across 345 entries |
| `evidence-universe.json` surface census | Evidence-class and certification-eligibility values across 10 surfaces |

The counterfactual evaluation is the central instrument and requires justification. `classify()`
returns `ERROR` for every subject (§1.3), so the live classifier yields no distribution at
all. To measure the *model* rather than the *outage*, each declared predicate was applied
in declared precedence order and the first match recorded. This is a read-only evaluation
of already-written predicates over already-committed state. It changes nothing, and it
answers the question the outage hides: **is the model correct, independently of whether it
runs?**

### 1.3 Standing limitation — the classifier is inoperative, measured first-party

```
RULE_PREDICATES:      ['R-01','R-02','R-03','R-04','R-05','R-06','R-07','R-08']
validate_rule_coverage: ("rule 'R-09' is declared but no predicate implements it",)
classify(<any subject>): status=ERROR  reason="rule 'R-09' is declared but no predicate
                                               implements it"
```

`classify()` calls `validate_rule_coverage()` before evaluating any rule and returns `ERROR`
if it reports a problem. Eight of nine predicates exist; `R-09 GOVERNED_ANALYSIS` does not.
**One missing predicate therefore disables classification for all 6,730 subjects, not for
the subset `R-09` would have claimed.** This is Step 1's limitation, now localized to its
exact mechanism, and it is BC-1.

The refusal is correct design — a classifier that silently skipped an unimplemented rule
would assign wrong authorities. It means every class assignment below is either a manual
reading of declared predicates or a counterfactual evaluation, and **none is a
classification of record.**

---

## 2. The Artifact Classification Model

### 2.1 Six vocabularies, thirty-nine class names, no crosswalk

The directive names six artifact kinds — authored · generated · derived · evidence · cache ·
temporary. **No register in the repository declares that model, and six registers declare
six different ones:**

| # | Register / module | Classes | Vocabulary |
|---|---|---|---|
| V1 | `00-BOOK/DATA/mutation-governance-boundary.json` | **9** | `REPOSITORY_STATE` `EXCLUSION` `CORPUS_REGISTRATION` `GENERATED_ARTIFACT` `CONSTITUTIONAL_TRUTH` `GOVERNED_DECLARATION` `SOURCE` `AUTHORED_DOCUMENT` `GOVERNED_ANALYSIS` |
| V2 | `00-BOOK/DATA/exclusion-register.json` | **7** | `GENERATED_DETERMINISTIC` `GENERATED_ENVIRONMENTAL` `TEST_EXECUTION_ARTIFACT` `CACHE` `TOOL_OPERATIONAL` `TEMPORARY` `EXPLICITLY_AUTHORIZED_EXTERNAL` |
| V3 | `00-BOOK/DATA/generated-artifact-registry.json` `input_classifications` | **9** | `TRACKED_DETERMINISTIC` `ENVIRONMENTAL` `OPERATIONAL` `EXTERNAL` `UNKNOWN` `EXECUTION_TRANSCRIPT` `LOCAL_RUNTIME` `ENVIRONMENTAL_OBSERVATION` `GENERATED_DETERMINISTIC` |
| V4 | `00-BOOK/DATA/evidence-universe.json` `evidence_classes` | **5** | `AUDIT` `DEBUG` `IMPROVEMENT` `EXECUTION` `VALIDATION` |
| V5 | `00-BOOK/tools/config.py` `NON_ARTIFACT_SCOPE` | **3** | `environment` `generated` `transient` |
| V6 | Step 1 report §5 (this programme's own working vocabulary) | **6** | generated · canonical · implementation · governed declaration · temporary · unknown |
| | **Total** | **39** | **and not one declared crosswalk between any pair** |

`GENERATED_DETERMINISTIC` is the only name appearing in two registers (V2, V3) — and it
carries **different meanings**: in V2 it is a class of *excluded filesystem state*; in V3 it
is a class of *input to a canonical artifact*, admissible *"ONLY when `generated_inputs`
names its producer and a bootstrap path."* The one shared token is a homonym, not a join.

### 2.2 `AV-1` — The six vocabularies are unjoined and partly contradictory

**Severity: HIGH.**

Three measured contradictions, not stylistic differences:

1. **`data/_evidence/` is and is not evidence.** V4's `not_in_this_universe` states:
   *"`data/_evidence/<unit>/` excluding URI-000001 — 123 TRACKED canonical certification
   artifacts (UCOS-DATA-*). They are named 'evidence' but are authored/derived repository
   truth committed with the corpus, not an evidence surface. Their governance belongs to the
   generated-artifact registry, not here."* They are not in V3's 345 entries either. **123
   artifacts are disclaimed by both registers that could own them.**
2. **PORTAL is generated in V5, absent from V3.** V5's `generated` names *"the emitted
   registries, DATA/, CONTROL-TOWER/, PORTAL/"*; V3 holds **0 entries under `00-BOOK`**.
   V3 declares itself the register that ends exactly this drift and names V5 as a source it
   supersedes. This is Step 1 `F-2`, and §6.4 resolves its precedence.
3. **Caches are excluded state in V2 and disclaimed as evidence in V4.** V4:
   *"caches carry no information not present in their source; they are not evidence of
   anything."* V2 classes them `CACHE`. These are compatible *only* because neither register
   asserts the other's domain — which is exactly the absence of a crosswalk, not its
   presence.

### 2.3 The canonical six-class model, and its crosswalk

The directive's six kinds are adopted here as the **canonical artifact model**, because they
are the only proposed vocabulary that is *complete over the measured population* and
*orthogonal to visibility*. Each is defined by **origin and reproducibility**, never by
tracked-ness:

| Class | Definition — origin and reproducibility only | Reproducible from a pristine clone? | Measured population |
|---|---|---|---|
| **AUTHORED** | A human wrote the bytes. No producer can re-derive them. Loss is permanent | No — must be carried | 458 `R-08` + 394 `R-09`-eligible + 2,189 residual `.md` |
| **GENERATED** | A declared producer re-derives the bytes deterministically from tracked inputs | **Yes** | 345 registered + 1,240 PORTAL + 23 `00-BOOK/DATA`+`REGISTRIES` |
| **DERIVED** | Re-derived deterministically, but from inputs that are themselves not all tracked | Only if every input is obtainable | V3 `generated_inputs` (10) |
| **EVIDENCE** | A record of something that happened. Historical, not re-derivable — re-running produces *new* evidence, not the same evidence | **No, and re-running is not reproduction** | 10 declared surfaces + `.ucos/execution-evidence.json` |
| **CACHE** | A stored answer to a computation whose inputs are still present. Deleting it costs time only | Yes, by recomputation | `.ucos/environment-fingerprint.json`, `__pycache__/`, `.ruff_cache/`, `.ucos-verification-evidence/` (46) |
| **TEMPORARY** | Exists only during an operation. No consumer outside that operation | N/A | `~$*`, `.register.lock`, `mktemp` plan/stage files |

**Crosswalk to the six existing vocabularies** — offered as analysis, binding nothing:

| Canonical | V1 (mutation) | V2 (exclusion) | V3 (input) | V4 (evidence) | V5 (scope) |
|---|---|---|---|---|---|
| AUTHORED | `SOURCE` · `AUTHORED_DOCUMENT` · `GOVERNED_ANALYSIS` · `GOVERNED_DECLARATION` | — | `TRACKED_DETERMINISTIC` | — | — |
| GENERATED | `GENERATED_ARTIFACT` | `GENERATED_DETERMINISTIC` | `GENERATED_DETERMINISTIC` | — | `generated` |
| DERIVED | `GENERATED_ARTIFACT` | `GENERATED_ENVIRONMENTAL` | `ENVIRONMENTAL` · `ENVIRONMENTAL_OBSERVATION` | `VALIDATION` | `generated` |
| EVIDENCE | *(no class)* | `TEST_EXECUTION_ARTIFACT` | `EXECUTION_TRANSCRIPT` · `LOCAL_RUNTIME` | `AUDIT` `DEBUG` `IMPROVEMENT` `EXECUTION` | *(no class)* |
| CACHE | *(no class)* | `CACHE` · `TOOL_OPERATIONAL` | `OPERATIONAL` | *(disclaimed)* | `environment` |
| TEMPORARY | *(no class)* | `TEMPORARY` | — | — | `transient` |

### 2.4 `AV-2` — V1, the only executable vocabulary, has no class for three canonical kinds

**Severity: HIGH.**

The crosswalk's `*(no class)*` cells are the finding. `mutation-governance-boundary.json` is
the **only** vocabulary with an implemented classifier, a declared authority per class, and
a fail-closed terminal. It has **no class for EVIDENCE, CACHE or TEMPORARY.**

Its `R-01 REPOSITORY_STATE` is the nearest fit, and its declared predicate is:

> *"subject is a path under `.git/`, or is working-tree contamination — present in the
> working tree and neither tracked nor governed by an exclusion register"*

So the only executable vocabulary models evidence, cache and temporary artifacts as
**contamination**, and the register that would rescue them (`exclusion-register.json`, V2)
is named in the predicate but **not consulted by the implementation** — see `AV-4`. Three
of six canonical artifact kinds have no lawful class in the only classifier that runs.

---

## 3. The Four States — Defined, Separated and Measured

### 3.1 The separation claim

The directive asks for the distinction between four states. The determination is that they
are **four logically independent axes**, and that the independence is not a modelling
preference but a consequence of what each axis can be wrong about:

| Axis | Question | Wrong answer costs |
|---|---|---|
| **GENERATION** | Can a declared producer re-derive these bytes from declared inputs? | A pristine clone cannot rebuild the repository |
| **VISIBILITY** | Does version control carry these bytes? | Truth is lost, or a false machine-local claim is published |
| **OWNERSHIP** | Which authority answers for this artifact? | A change lands with no one accountable |
| **CERTIFICATION** | What has been proven about it, and does that proof still hold? | A claim outlives its evidence |

No axis determines another. A GENERATED artifact may be tracked (PORTAL) or ignored
(`/knowledge/`). An AUTHORED artifact may be tracked (`verify.sh`) or untracked
(`engine/execution_environment/gate.py`). An untracked artifact may affect certification
(measured, §3.5) or be forbidden from it. **Every combination is occupied in this
repository.** That is the empirical proof of independence.

### 3.2 Axis 1 — GENERATION STATE

| Property | Measured |
|---|---|
| Authority of record | `00-BOOK/DATA/generated-artifact-registry.json` (§6.4 `D-1`) |
| Declared standing | *"upstream of every engine it describes and must never be produced by one of them"* |
| Entries | **345** |
| `deterministic` | `true` — **345 / 345**, one distinct value |
| `lifecycle` | `REGENERATED` — **345 / 345**, one distinct value |
| `canonical_identity_role` | `CANONICAL` — **345 / 345**, one distinct value |
| `registration_status` | `EXCLUDED_FROM_CORPUS_REGISTRATION` — **345 / 345**, one distinct value |
| `owner` / `validation_owner` | **345 / 345** populated · **32** distinct programmes |
| `certification_role` | 5 values: `PROGRAMME_DELIVERABLE` 273 · `REPLAY_PROVEN` 30 · `BLOCKING_GATE_SOURCE` 16 · `CONVERGENCE_DETERMINATION` 15 · `PHASE9_VARIANCE_DIMENSION` 11 |
| `producer_homes` | 31 · `invariants` 13 |

### 3.3 `AV-3` — The generation axis has one lifecycle value, so it is not yet a lifecycle

**Severity: MEDIUM.**

`lifecycle` is `REGENERATED` for all 345 entries; `deterministic` is `true` for all 345;
`canonical_identity_role` is `CANONICAL` for all 345; `registration_status` is
`EXCLUDED_FROM_CORPUS_REGISTRATION` for all 345. **Four of the eighteen per-entry fields are
constants.** A field with one observed value carries no information and cannot discriminate
— it is a declaration of intent awaiting a second value.

Concretely, the register cannot currently express: a generated artifact that has been
superseded, one whose producer was removed, one that is non-deterministic and known to be,
or one admitted *into* corpus registration. Coverage is also bounded: **0 of 345 entries lie
under `00-BOOK`**, so the 1,240 PORTAL pages and 23 `DATA`/`REGISTRIES` artifacts have no
generation state at all, and `mutation_class_extension.py:38` reports each as
*"non-generated — absent from generated-artifact-registry.json canonical_path"*.

### 3.4 Axis 2 — VISIBILITY STATE

Carried forward from Step 2 §9.1, re-measured at this baseline:

| State | Count | Declared by |
|---|---|---|
| **TRACKED** | **6,188** | the index — no register declares expected tracked-ness |
| **IGNORED** | **233** | `.gitignore` (55 active patterns), bounded by `exclusion-register.json` (32 entries) |
| **UNDECLARED-INVISIBLE** | **309** | **nothing** |
| **Total** | **6,730** | |

The 309 is 308 as measured in Step 2 plus the Step 2 determination itself — an artifact that
entered the defect state by being created, which is the mechanism in miniature.

### 3.5 Axis 3 — OWNERSHIP STATE

| Property | Measured |
|---|---|
| Authority of record | `platform/universal_ownership/catalog/ucos-ownership-declarations.json` (precedence 900, CONSTITUTIVE) |
| Assignments in it | **`"assignments": {}`** — literally empty |
| Standing vocabulary | `DECLARED` · `CONTESTED` · `UNRESOLVED` (closed enum, `contracts.py:87-93`) |
| Recorded run (commit `00bd45f`) | 542 subjects · 151 declared · 0 contested · **391 unresolved** · coverage 27.8598% · `closed: False` |
| Current population | `closure.json` holds **549** concepts; the repository's own newer figure is **398 of 549** |
| Ratified | **0%** — definitional, since the only ratification surface is empty |
| Fabrication | A typed error: `OwnershipFabricationError` — *"SHALL NEVER be implied, inferred, or filled in to close a metric"* |
| Ratifying act | `CEP-OWN-004` — a governing authority ratifies the `ratified: false` draft; coverage 27.86% → 66.97% with **zero** code change |

**Three authority planes, each disclaiming the others**, per
`CANONICAL-AUTHORITY-DETERMINATION.md:15-26` — with a defect in the source worth recording:
the heading reads *"tripartite"* and the prose *"three planes"*, but **the table has four
rows** (ownership declaration · concept truth · identity+artifact registration ·
constitutional recognition). The concept-truth plane disclaims authority outright
(`AUTHORITY = NONE (DERIVED TRUTH)`); the ownership matrix is self-declared
machine-unreadable and admitted at Priority 5 (documentation) because no executing check
binds its rows.

Determination `D-2.1`, verbatim:

> *"the Canonical Ownership Principle is **declared** in one place and **enforced** in
> another, and the two do not share a key."*

### 3.6 `AV-4` — Populated owner fields are invisible to the ownership axis

**Severity: HIGH.**

Owner fields *are* populated, in quantity:

| Register | `owner` populated | Distinct owners | Grain |
|---|---|---|---|
| `generated-artifact-registry.json` | **345 / 345** (+ `validation_owner`) | **32** | programme |
| `00-BOOK/DATA/artifacts.json` | **1,461 / 1,461** | **1** — every row `UCOS-PROGRAM-CUSTODIAN` | degenerate |
| `ucos-ownership-declarations.json` | **0** | 0 | concept |

**None of the 345 programme owners feeds the 391-unresolved measurement.** UOF-001's four
evidence providers read only the (empty) catalogue, artifact `ARTIFACT ID` headers, and
`closure.json` home fields. The concept plane is keyed on concept id, the registration plane
on artifact path — and no join exists. That is `D-2.1` made concrete and countable.

`artifacts.json`'s owner field deserves separate note: it is 100% populated and carries
**zero information**, because all 1,461 rows hold the same constant. A field that cannot
vary is not an assignment; it is the *appearance* of one, which is worse than a null,
because a coverage metric computed over it would report 100%.

### 3.7 Axis 4 — CERTIFICATION STATE

| Property | Measured |
|---|---|
| Declared law | `CEP-005` Article VI — **8 states**, **12 legal transitions**, initial `NOT_ELIGIBLE`, terminal `REVOKED`, `VI.4` any other transition ⇒ `HALTED` |
| Implementation of that law | **NONE LOCATED** anywhere in `engine/` or `platform/` |
| `engine/certification/contracts.py:73-77` | `CertificationStatus` — **2** members (`certified`, `not-certified`) |
| `platform/certification/status.py:34-39` | `CertificationPosture` — **3** members |
| `uccep_engine.py:896-903` | 3 bare strings: `NOT-CERTIFIED` / `CERTIFIED-PROVISIONAL` / `CERTIFIED` |
| `00-BOOK/DATA/certification.json` | **1** record · `verdict: CERTIFIED` · domains 10/10 · **scope 1,233 artifacts** |
| Current corpus size | **1,461** artifacts — the certification is **228 artifacts stale** |
| Live `uccep.json` | `certification: NOT-CERTIFIED` · `gate_exit: 1` · `gate_blocking: ["CK-ACEE"]` |
| Ceiling | `UCCEP-F-004`, `blocking: true`, class `STANDING-CONSTITUTIONAL-CEILING` |
| Tier 1 | `occupancy: VACANT`, `vacancy: VAC-01`, `located: false` |

### 3.8 `AV-5` — Four certification vocabularies, none of which is the declared law

**Severity: CRITICAL.**

`CEP-005` Article VI legislates an 8-state machine with 12 enumerated transitions and
declares that any unenumerated transition places the Program in `HALTED`. **No
implementation of it exists.** In its place run three code enums with 2, 3 and 3 members,
sharing no vocabulary with each other or with Article VI, plus a fourth pass/fail domain
verdict in `certification.json`.

`CERTIFIED-PROVISIONAL` — the ceiling every readiness determination cites — appears in **none**
of the three code enums. It is a string literal produced by one `elif` branch in one engine.

Two further measured facts:

- **The live verdict is not the cited verdict.** `uccep.json` currently reads
  `NOT-CERTIFIED` with `gate_blocking: ["CK-ACEE"]`. Documents citing `CERTIFIED-PROVISIONAL`
  with `gate_exit: 0` are quoting a superseded run. Decision `R-01` governs: *"Where a
  committed determination and a current gate measurement disagree, the measurement
  governs."* The current measurement is one rung **below** the provisional ceiling.
- **`CEP-005 X.3`** — *"A subject SHALL NOT be certified until every subject it depends upon
  is CERTIFIED"* — is unsatisfiable by construction while Tier 1 is `VACANT` under `VAC-01`
  and every CEP instrument is `PROVISIONAL`. `UCCEP-F-004` records exactly this standing.

Certification is therefore not a *state* of an artifact in this repository. It is an
assertion made by whichever of four vocabularies was consulted, over a population that has
grown 228 artifacts since the assertion was computed.

---

## 4. `AV-6` — The Axis Collapse

**Severity: CRITICAL. This is the finding Step 3 exists to produce.**

### 4.1 The measurement

Counterfactual precedence evaluation over the entire repository — every declared predicate
applied in declared order, `R-09` treated as reached-but-unimplemented:

```
=== UNTRACKED-AND-UN-IGNORED POPULATION ===
    309   R-01 REPOSITORY_STATE
    TOTAL 309                                    ← 100%

=== IGNORED POPULATION ===
    233   R-01 REPOSITORY_STATE
    TOTAL 233                                    ← 100%

=== TRACKED POPULATION ===
   3216   reaches R-09 (UNIMPLEMENTED) → UNRESOLVED
   2118   R-07 SOURCE
    458   R-08 AUTHORED_DOCUMENT
    345   R-04 GENERATED_ARTIFACT
     47   R-06 GOVERNED_DECLARATION
      2   R-02 EXCLUSION
      2   R-03 CORPUS_REGISTRATION
   TOTAL 6188
```

**Every one of the 542 non-tracked paths in the repository resolves to `R-01
REPOSITORY_STATE` — working-tree contamination — regardless of what it actually is.**

Representative subjects, measured individually:

| Subject | True canonical class | Visibility | Resolves to |
|---|---|---|---|
| `verify.sh` | AUTHORED | TRACKED | `R-07 SOURCE` ✅ |
| `engine/execution_environment/gate.py` | AUTHORED | untracked | **`R-01 REPOSITORY_STATE`** ❌ |
| `00-MASTER/UVI-000001/uvi-declaration.json` | AUTHORED | TRACKED | `R-06 GOVERNED_DECLARATION` ✅ |
| `00-MASTER/UEG-000001/ueg-declaration.json` | AUTHORED | untracked | **`R-01 REPOSITORY_STATE`** ❌ |
| `intelligence/UCOS-RIE-MODEL.json` | GENERATED | TRACKED | `R-04 GENERATED_ARTIFACT` ✅ |
| `00-BOOK/PORTAL/UCOS-BOOK-000000.md` | GENERATED | TRACKED | reaches `R-09` → **UNRESOLVED** ❌ |
| `00-BOOK/PORTAL/UCOS-ADR-000004.md` | GENERATED | untracked | **`R-01 REPOSITORY_STATE`** ❌ |
| `.ucos/execution-evidence.json` | EVIDENCE | IGNORED | **`R-01 REPOSITORY_STATE`** ❌ |
| `.ucos/environment-fingerprint.json` | CACHE | IGNORED | **`R-01 REPOSITORY_STATE`** ❌ |
| `.ruff_cache/.gitignore` | CACHE | IGNORED | **`R-01 REPOSITORY_STATE`** ❌ |
| `00-BOOK/DATA/certification.json` | GENERATED | TRACKED | reaches `R-09` → **UNRESOLVED** ❌ |
| `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md` | GENERATED | TRACKED | reaches `R-09` → **UNRESOLVED** ❌ |

The same artifact kind resolves differently based **only** on its visibility. `gate.py` and
`verify.sh` are both authored shell/python source in the governed roots; one is `SOURCE`, one
is contamination. `ueg-declaration.json` and `uvi-declaration.json` are both governed
declarations of a verification capability; one is `GOVERNED_DECLARATION`, one is
contamination. Two PORTAL pages produced by the same generator in the same run resolve to
two different outcomes.

### 4.2 The mechanism

Two properties of the rule set, together:

**(a) `R-01` sits at precedence 1 and claims any existing untracked path.** The
implementation:

```python
def _r01_repository_state(subject, repo, boundary) -> bool:
    path = subject.identity
    if path.startswith(".git/"):
        return True
    if path in _EXCLUSION_INSTRUMENTS or path in repo.tracked:
        return False
    return (repo.root / path).exists()
```

`_EXCLUSION_INSTRUMENTS` is `{".gitignore", "00-BOOK/DATA/exclusion-register.json"}` — the two
*instrument* paths. The declared predicate's clause **"nor governed by an exclusion
register" is not implemented at all.** No ignore rule and no register entry is consulted.
That is why all 233 ignored paths — every cache and every evidence file the repository
correctly excluded and correctly declared — are claimed as contamination by the first rule
evaluated.

**(b) Every rule that could rescue them requires `tracked`.** `R-06` membership includes
`"repository-controlled": path in repo.tracked`; `R-07` is *"a **tracked** executable or
build-configuration path"*; `R-08` *"a **tracked**, non-generated markdown path"*; `R-09`
*"a **tracked**, non-generated markdown path…"*. Only `R-02`, `R-03`, `R-04` are
visibility-neutral, and each is a small fixed membership test.

So visibility is evaluated **first**, and it is a **precondition of every substantive
class**. The consequence is exact:

> **Classification does not determine visibility. Visibility determines classification.**

### 4.3 The repository has already recorded the mechanism — as a narrower bug

`Repository.tracked`'s docstring documents the absorption hazard in its own words:

> *"because `_r01_repository_state` claims any existing path absent from this set, the
> artifact is silently absorbed into REPOSITORY_STATE before the rule that actually owns it
> is ever evaluated — **a wrong authority, which is strictly worse than the fail-closed
> terminal**."*

That paragraph exists to justify `git ls-files -z` for non-ASCII paths — a **one-artifact**
quoting defect. The identical absorption over **542 paths** for the ordinary reason that
they are simply untracked is not framed as a hazard anywhere. The repository diagnosed the
mechanism correctly and scoped the finding to 1/542nd of its actual population.

### 4.4 Why this is one defect and not five

`AV-6` subsumes four previously separate findings:

| Prior finding | Restated as an instance of the collapse |
|---|---|
| Step 1 `F-2` — PORTAL has three disagreeing authorities | PORTAL is GENERATED; two of its three "authorities" are answering visibility questions |
| Step 1 `F-5` / Step 2 `OB-3` — the evidence base is untracked | AUTHORED artifacts absorbed into `REPOSITORY_STATE` by `R-01` |
| Step 2 `OB-6` — 228 PORTAL pages are in no state | GENERATED artifacts absorbed by `R-01` |
| Step 2 `OB-1` — the classification obligation is void | The exclusion register is unreachable from the classifier (§4.2a), so its declarations cannot rescue anything |

They are four symptoms of one inversion. **Repairing them independently would not repair
the model** — it would move 542 paths across a boundary whose semantics remain wrong.

---

## 5. `AV-7` — Even With BC-1 Closed, 41.9% Of The Repository Fails Closed

**Severity: MEDIUM, and it bounds the value of BC-1.**

`R-09` is the missing predicate. Assume it is implemented **exactly as declared** — tracked,
non-generated markdown whose filename matches
`(determination|analysis|assessment|execution|matrix|readiness|admission|blocker|gap)`:

| Measure | Count | Share of 6,730 |
|---|---|---|
| Tracked paths reaching `R-09` | **3,216** | 47.8% |
| Of those, satisfying `R-09`'s declared predicate | **394** | 5.9% |
| **True `UNRESOLVED` residue** | **2,822** | **41.9%** |

Residue composition: **2,189 `.md` · 575 `.json` · 29 `.yml` · 24 `.docx` · 4 `.txt` · 1
extensionless.** By location: **1,320 `00-BOOK`** (of which **1,232 PORTAL pages**, 6
`REGISTRIES`, 8 `DATA`), 506 `00-MASTER`, 149 `service`, 134 `data`, 131 `infrastructure`,
121 `application`, 32 `platform`, 29 `.github`.

`UNRESOLVED` is declared **`FAILS CLOSED`** and *"names the absence of one [authority]…
it must never be read as a permissive default."* So on the declared semantics, **41.9% of
the repository has no authority even after BC-1 closes.**

The register anticipated failure but not its shape. `$conformance_is_not_claimed_here`
predicts *"root-level `*.md` including the Master Implementation Plan artifacts; the majority
of `00-MASTER/**/*.json`… and the `by_object` index"* — it names neither the 1,232 PORTAL
pages nor the 6 registries, which are the two largest coherent blocks and both consist of
**generated** artifacts that `R-04` misses only because `A3` has no `00-BOOK` entries
(`AV-3`). **Closing `AV-3` would move 1,232+ paths from `UNRESOLVED` to `R-04` with no rule
change at all** — which makes registry coverage, not `R-09`, the larger lever.

---

## 6. Conflict Analysis

### 6.1 `.gitignore`

**Standing:** 55 active patterns, `+9/−0` uncommitted (the `.ucos/` rule). **Conflicts:**
(i) against `exclusion-register.json` — 23 patterns carry no entry, including both `.ucos`
rules (`OB-2`); (ii) against `mutation_classification` — `R-01`'s implementation never reads
it, so ignoring a path does not exempt it from contamination (§4.2a); (iii) against
`config.py` `REPOSITORY_ARTIFACT_DEFINITION`, which asserts generated outputs are *"bounded
by version control (.gitignore)"* while `.gitignore` never mentions `PORTAL`, `00-BOOK/DATA`
or `00-BOOK/REGISTRIES`. **Determination:** `.gitignore` is an *instrument* of the visibility
axis, never an authority on any other. Step 2's conclusion stands: G-9 should land, and not
alone.

### 6.2 `exclusion-register.json`

**Standing:** 32 entries, 7 classes, 4 invariants, authority *"legislates the classification
of excluded filesystem state."* **Conflicts:** (i) `ignored_unclassified` is the constant `0`
— the bare `*` entry plus bidirectional `fnmatch` self-classifies every rule as `CACHE`
(`OB-1`, re-confirmed: `.ucos/`, `secrets/`, `src/`, `00-BOOK/PORTAL/` all → `CACHE`);
(ii) its declared scoping of `*` (*"never to the repository root"*) is unrepresentable in
`_classify()`'s signature; (iii) **the classifier that would enforce it never calls it**
(§4.2a). **Determination:** the correct authority for the EVIDENCE / CACHE / TEMPORARY
classes `V1` lacks (`AV-2`) — currently unreachable from the one classifier that runs. Its
`constitutional_superior.effect` states the axis separation better than any other text in
the repository: *"exclusion from it is a statement about STORAGE and never about whether a
thing exists… it may never own existence."*

### 6.3 `generated-artifact-registry.json`

**Standing:** 345 entries, 31 producer homes, 13 invariants. **Conflicts:** (i) 0 entries
under `00-BOOK` despite `V5` naming `DATA/`, `REGISTRIES/`, `CONTROL-TOWER/`, `PORTAL/`
generated (`AV-3`); (ii) four fields are constants (`AV-3`); (iii) its 345 populated owners
are invisible to the ownership axis (`AV-4`); (iv) it and `evidence-universe.json` **each
disclaim** the 123 tracked `data/_evidence/` artifacts (`AV-1`). **Determination:** authority
of record for the GENERATION axis (`D-1`). Its defect is coverage, not standing — and its
coverage gap is the single largest driver of `AV-7`.

### 6.4 PORTAL generation model

**Standing:** producer `ukbx.py portal` (`PORTAL_DIR:39`, writer `1288-1331`), entry point
`register.sh` Phase 4/10, drift gate `--guard` (exit 3). 1,240 tracked · 228 untracked ·
1,468 on disk. **Determination on precedence, carried forward from Step 2 §8.2 unchanged:**

- **`D-1`** — `generated-artifact-registry.json` holds the predicate `is_generated_output`.
- **`D-2`** — `config.py::EXCLUDE_DIR_PREFIXES` is a derived view without standing; it must be projected from `D-1`.
- **`D-3`** — git tracked-ness answers `is_visible` and holds no authority over generation.
- **`D-4`** — `config.py` contradicts *itself*: `NON_ARTIFACT_SCOPE` calls PORTAL generated while `REPOSITORY_ARTIFACT_DEFINITION` implies generated ⇒ ignored, and PORTAL is tracked and required-committed.

**Step 3 adds:** under the canonical model PORTAL is unambiguously **GENERATED** (a declared
producer re-derives it deterministically from tracked inputs), and *that classification is
independent of the disposition decision.* The disposition — Option A ignored, Option B
committed projection — remains an owner act, and `OB-5` still blocks Option B: `index.md`
embeds a wall-clock timestamp, so `--guard` is unsatisfiable at second granularity.

### 6.5 Git tracked state

**Standing:** 6,188 tracked, no register declaring expected tracked-ness for any path.
**Conflicts:** (i) it is a *precondition* of `R-06`/`R-07`/`R-08`/`R-09` and therefore an
input to classification (`AV-6`); (ii) UGA enumerates from `git ls-files --cached`, so
untracked authored code is outside its universe by construction (`OB-7`); (iii) RIB GATE-12
and RFP CLO-05 see the 309 only as generic dirt. **Determination:** tracked-ness is the
*consequence* of a visibility decision and must never be an input to classification,
generation or ownership. Today it is an input to all three.

### 6.6 `AV-8` — Visibility can still purchase certification

**Severity: MEDIUM, and it is a live regression of a closed defect.**

`evidence-universe.json` `R-EV-4` forbids two *classes* from affecting certification
(`DEBUG`, `IMPROVEMENT`), enforced by `CERTIFICATION_FORBIDDEN_CLASSES`. It does **not**
constrain by visibility, and measurement shows why that matters: of 10 declared surfaces,
**3 carry `may_affect_certification: true` while being untracked.**
`EV-PROGRAMME-VALIDATION-STATE` states the permission and its own caveat:

> *"Derived from tracked declarations and therefore deterministic in CONTENT — but excluded
> from version control, so it is absent from a pristine clone… **determinism of derivation
> does not make an untracked file repository truth.**"*

So an untracked surface may affect certification, by explicit declaration. Combined with
`OB-1` — where any single `.gitignore` line self-classifies and `ignored_unclassified`
cannot rise — the `be46a300` mechanism (*"A one-line ignore rule could buy a convergence
certification"*) **remains available**. The exclusion register was written to close it; §6.2
measures that it does not.

---

## 7. The Canonical Decision Framework

### 7.1 The declared order

For every artifact, exactly one decision at each position, each taken by the authority that
owns that position, and **each taken only after its predecessor**:

```
ORIGIN         Who or what produced these bytes?
   ↓             AUTHORED (a human)  |  PRODUCED (a declared producer)  |  OBSERVED (a run)
CLASSIFICATION Which of the six canonical classes?            §2.3
   ↓             AUTHORED · GENERATED · DERIVED · EVIDENCE · CACHE · TEMPORARY
OWNER          Which authority answers for it?                §3.5
   ↓             DECLARED | CONTESTED | UNRESOLVED — never inferred to close a metric
AUTHORITY      Under what instrument does that owner act?
   ↓             the register or constitution granting the mutation right
VISIBILITY     Must version control carry these bytes?        §3.4
   ↓             TRACKED | IGNORED — and never a third state
LIFECYCLE      What states may it occupy, and what transitions are legal?
   ↓             per class; GENERATED needs ≥2 (AV-3)
CERTIFICATION  What must be proven, and does the proof still hold?   §3.7
                 per CEP-005 Art VI, over a population stated at assertion time
```

### 7.2 The two rules that make the order load-bearing

**Rule 1 — each arrow is a function of its predecessors only.** `VISIBILITY` is decided from
`CLASSIFICATION` (a CACHE is ignored *because* it is a cache), never the reverse.
`CERTIFICATION` is decided from everything upstream, and can never feed back — otherwise a
visibility edit changes a certification, which is `AV-8`.

**Rule 2 — the terminal is fail-closed at every position, and never a default.** An artifact
with no class, no owner, or no declared visibility is refused, not defaulted. `V1`'s
`UNRESOLVED` and `V3`'s `UNKNOWN` already say this; `OwnershipFabricationError` already
enforces it on the OWNER position.

### 7.3 The framework as currently implemented

The measured order is **not** the declared order. It is:

```
VISIBILITY  →  CLASSIFICATION  →  (OWNER ⊥ unjoined)  →  CERTIFICATION (4 vocabularies)
   ↑                                                              │
   └──────────────────────  AV-8: still purchasable  ─────────────┘
```

- **The first arrow is reversed** (`AV-6`): `R-01` at precedence 1 plus `tracked` in four rule predicates makes visibility a precondition of classification. 542 paths misclassified.
- **`ORIGIN` is not represented at all.** No register records who or what produced an artifact as a *first-class field* independent of the generated registry's `producer`, so an AUTHORED artifact and a GENERATED one are distinguished only by registry membership — which is why the 1,232 unregistered PORTAL pages are indistinguishable from authored markdown to `R-08`/`R-09`.
- **`OWNER` is disconnected** (`AV-4`): 345 populated owners share no key with the axis that measures ownership; 1,461 more are a constant.
- **`LIFECYCLE` is a single value** on the generation axis (`AV-3`) and an unimplemented 8-state machine on the certification axis (`AV-5`).
- **`CERTIFICATION` feeds back into `VISIBILITY`** (`AV-8`), closing a loop the framework forbids.

### 7.4 `AV-9` — No position in the framework has a bidirectional gate

**Severity: LOW as a finding, structural as a cause.**

Extending Step 2 `OB-7` across all seven positions:

| Position | Gate that fails if the property is absent | Gate that fails if the property is *wrongly present* |
|---|---|---|
| ORIGIN | none | none |
| CLASSIFICATION | `UNRESOLVED` fails closed — but `classify()` returns `ERROR` for all subjects, so it never runs | none |
| OWNER | `OwnershipFabricationError` ✅ | none |
| AUTHORITY | none | none |
| VISIBILITY | UVI gate: refuses if the evidence store is **not** ignored ✅ | **none** — nothing refuses an untracked authored module |
| LIFECYCLE | none | none |
| CERTIFICATION | `CEP-005 V.4` (unverifiable precondition ⇒ unsatisfied) ✅ *declared* | `R-EV-4` by class ✅ · **by visibility, none** (`AV-8`) |

Three of fourteen cells are enforced. **The framework is declared at seven positions and
measured at three half-positions** — which is why `AV-1`…`AV-8` could all arise without any
gate reporting a failure.

---

## 8. Findings Register

| ID | Finding | Severity | Owner (read, not assigned) | Status |
|---|---|---|---|---|
| `AV-1` | Six classification vocabularies · 39 class names · 0 crosswalks; 123 `data/_evidence/` artifacts disclaimed by both registers that could own them | **HIGH** | `00-BOOK` · Repository Intelligence | **OPEN** |
| `AV-2` | `V1`, the only executable vocabulary, has no class for EVIDENCE, CACHE or TEMPORARY; `R-01` models all three as contamination | **HIGH** | Mutation governance owner | **OPEN** |
| `AV-3` | Generation axis: 4 of 18 fields are constants (`lifecycle`=`REGENERATED` 345/345); 0 of 345 entries under `00-BOOK` | **MEDIUM** | Generated-artifact registry owner · `00-BOOK` | **OPEN** |
| `AV-4` | 345 programme owners + 1,461 constant owners share no key with the ownership axis; catalogue empty; 0% ratified | **HIGH** | Universal Ownership · `00-BOOK` | **OPEN** |
| `AV-5` | `CEP-005` Art VI 8-state machine unimplemented; 3 code enums (2/3/3 members) + a 4th verdict vocabulary; `CERTIFIED-PROVISIONAL` in no enum; live verdict `NOT-CERTIFIED`, cited verdict provisional; corpus certification 228 artifacts stale | **CRITICAL** | Certification owner (CEP-005) | **OPEN** |
| `AV-6` | **The axis collapse.** All 542 non-tracked paths → `R-01 REPOSITORY_STATE`. Visibility determines classification. Subsumes `F-2`, `F-5`, `OB-3`, `OB-6` | **CRITICAL** | Mutation governance owner · Repository Intelligence | **OPEN** |
| `AV-7` | 2,822 tracked paths (41.9%) reach `UNRESOLVED` even with `R-09` implemented as declared; 1,232 are PORTAL pages recoverable by registry coverage alone | **MEDIUM** | `00-BOOK` · mutation governance owner | **OPEN** |
| `AV-8` | Visibility can still purchase certification: 3 untracked surfaces carry `may_affect_certification: true`, and `ignored_unclassified` cannot rise (`OB-1`) | **MEDIUM** | Certification owner · exclusion-register owner | **OPEN** |
| `AV-9` | No framework position has a bidirectional gate; 3 of 14 cells enforced | **LOW / structural** | Repository Intelligence · UGA owner | **OPEN** |

**9 raised · 0 resolved · 0 repaired.**

### 8.1 Relationship to prior findings

| Prior | Step 3 disposition |
|---|---|
| Step 1 `F-2` (PORTAL, three authorities) | **Precedence resolved** §6.4. Classification resolved: GENERATED. Disposition still an owner act |
| Step 1 `F-5` / Step 2 `OB-3` | **Root-caused** as `AV-6`: `R-01` absorption, not an isolated tracking oversight |
| Step 2 `OB-1` | **Re-confirmed and extended**: also unreachable from the classifier (§6.2), and the enabler of `AV-8` |
| Step 2 `OB-2` | Unchanged — 23 patterns uncovered |
| Step 2 `OB-5` | Unchanged — `--guard` unsatisfiable; blocks PORTAL Option B |
| Step 2 `OB-6` | **Root-caused** as `AV-6` |
| Step 2 `OB-7` | **Generalized** to `AV-9` across all seven positions |

### 8.2 Ordering implied for Steps 4–6

Read from the dependency structure, not assigned:

> `AV-6` **first** — `R-01` must stop claiming declared-excluded and declared-authored paths, or every later measurement inherits 542 wrong authorities → `OB-1`/`OB-2` (make the exclusion register reachable and its metric real) → `AV-3` (register `00-BOOK` generated artifacts; recovers ~1,232 of `AV-7`'s residue at once) → BC-1 / `R-09` → machine re-classification → `AV-4` (`CEP-OWN-004` ratification: 27.86% → 66.97%, zero code change) → `AV-5` (implement or formally supersede `CEP-005` Art VI) → `A6-3`/`A6-4` gate measurement.

Note the ordering consequence for BC-6 as a whole: **`A6-1` attribution should not be
attempted before `AV-6`.** Attributing 38 modified and 309 untracked paths under a
classifier that assigns 542 of them to `REPOSITORY_STATE` would record contamination as the
mutation class of the programme's own authored source and declarations.

---

## 9. What Step 3 Establishes And What It Does Not

### 9.1 Establishes

- A **canonical six-class artifact model** defined purely by origin and reproducibility, with a full crosswalk to all six existing vocabularies (§2.3) and the three cells `V1` cannot express (`AV-2`).
- The **four states are logically independent**, proven empirically: every combination of generation × visibility is occupied in this repository (§3.1).
- **`AV-6` by first-party counterfactual measurement**: 542 of 542 non-tracked paths resolve to `R-01 REPOSITORY_STATE`, with the two-part mechanism identified in source (`R-01` at precedence 1; `tracked` as a precondition in four predicates) and the repository's own docstring quoted as independent corroboration.
- That **`F-2`, `F-5`, `OB-3` and `OB-6` are one defect**, not four (§4.4).
- A **quantified bound on BC-1's value**: closing `R-09` exactly as declared still leaves 2,822 paths (41.9%) failing closed, and registry coverage (`AV-3`) is the larger lever, worth ~1,232 paths with no rule change (`AV-7`).
- The **certification axis has four vocabularies and no implementation of its declared law**, and the live verdict (`NOT-CERTIFIED`) is below the ceiling every readiness determination cites (`AV-5`).
- The **ownership axis is disconnected by key, not by absence of data**: 345 populated owners are invisible to the metric that reports 391/398 unowned (`AV-4`).
- The **canonical decision framework** (§7.1), the two rules that make its order load-bearing (§7.2), and a measured account of how the implemented order differs (§7.3).
- That **`AV-8` is a live regression**: the `be46a300` purchase remains available.

### 9.2 Does not establish

| Not established | Why | Requires |
|---|---|---|
| Any classification of record | `classify()` returns `ERROR` for all 6,730 subjects | BC-1 / `R-09` |
| That the canonical six-class model is adopted | This determination has **no authority**; it proposes and crosswalks | Mutation governance owner |
| The PORTAL disposition | Classification is resolved (GENERATED); disposition is not derivable from declared text | **`00-BOOK` owner act** |
| Any ownership assignment | Every owner named is *read* from a declared home | `CEP-OWN-004` — a governing authority |
| Any certification state | Four vocabularies disagree; the declared law is unimplemented | Certification owner (CEP-005) |
| That `A6-2` is satisfied | `OB-1`, `OB-2` open; G-9 uncommitted | Repair, then a commit |
| That the 2,822 residue is correctly sized | It assumes `R-09` implemented *exactly* as declared; a broader predicate would reduce it | `R-09` implementation |
| That `verify.sh --full` exits 0 (`A6-5`) | Not executed — execution writes `.ucos/`, outside analysis-only mode | Steps 4–5 |
| Whether the 309 untracked paths should be committed | An `A6-1` disposition question per owning programme | Owner acts |

### 9.3 The circularity, at Step 3

Step 1: classification is the capability BC-1 exists to restore, so Step 1 produced no
classification of record. Step 2: the metric that would measure a visibility boundary is the
constant `0`, so Step 2 produced no boundary of record. Step 3 completes the pattern:

> **Step 3 was to separate classification from visibility. The classifier resolves
> classification *from* visibility — so the instrument that would verify the separation is
> the instrument that violates it.**

The separation is therefore established here by **reading declared authority text and
evaluating the declared predicates directly**, exactly as Steps 1 and 2 proceeded. §2.3,
§3.1 and §7.1 stand on declared text and first-party measurement. But **Step 3 cannot
produce an authority model of record**, and `AV-6` must be repaired before any gate can
assert that the four axes are independent in fact rather than in intent.

---

## 10. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-ARTIFACT-AUTHORITY-VISIBILITY-RESOLUTION-DETERMINATION.md` |
| Required sections present | ✅ six-class model (§2) · four-state distinction (§3) · all five conflicts (§6) · Origin→Certification framework (§7) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis only — implementation performed | ✅ **0** |
| Code changes | ✅ **0** — every module read, none written |
| Configuration changes | ✅ **0** — `.gitignore` untouched, still `+9/−0` |
| Registry changes | ✅ **0** — 6 registers read, none written |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ **38**, identical set |
| Only new artifact added | ✅ `git status --porcelain` 340 → 341; the single delta is this file |
| Classes / owners / certifications created | ✅ **0** |
| Findings resolved | ✅ **0** — all 9 raised and left open |

---

*This determination modified no file, changed no code or configuration, wrote to no registry, altered no certification, committed nothing, and created no class, owner, authority or lifecycle. Every class assignment is a manual reading of declared predicates or a read-only counterfactual evaluation, and none is a classification of record, because `classify()` returns `ERROR` for all 6,730 subjects at this baseline. Nine findings (`AV-1`…`AV-9`) are raised and all remain open. Step 1 `F-2` is resolved as to classification (GENERATED) and precedence, and remains open as to disposition. Step 1 `F-5` and Step 2 `OB-3`/`OB-6` are root-caused into `AV-6`. `A6-2` remains **OPEN**; BC-6 remains **OPEN** at 0 of 8 acceptance criteria. The single repository mutation is the creation of this file.*

**END DETERMINATION — BC-6 STEP 3 COMPLETE · STEPS 4–6 NOT PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
