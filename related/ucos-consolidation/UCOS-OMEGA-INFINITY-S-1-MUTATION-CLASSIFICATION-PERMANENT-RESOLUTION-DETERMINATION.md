# UCOS Ω∞ — S-1 MUTATION CLASSIFICATION PERMANENT RESOLUTION DETERMINATION

> **Question:** What is the permanent constitutional and engineering resolution for the mutation classification coverage failure?
> **Baseline:** `bae59755d7e2d3566c93b89c722b68847145269a` · **Branch:** `integration/recovery-001` · 515 commits
> **Working tree at capture:** 374 porcelain entries (38 tracked-modified · 336 untracked) — pre-existing, untouched
> **Inputs:** `UCOS-OMEGA-INFINITY-PERMANENT-CLOSURE-EXECUTION-READINESS-DETERMINATION.md` (759 lines) · `00-BOOK/DATA/mutation-governance-boundary.json` (407 lines, v1.1.0) · `platform/repository_intelligence/mutation_classification.py` (507 lines) · `platform/repository_intelligence/mutation_class_extension.py` (206 lines) · `platform/tests/test_violation_4_mutation_extension.py` (381 lines)
> **Mode:** RESOLUTION DETERMINATION ONLY. No implementation, no code change, no registry change, no identity change, no relationship change, no commit.
> **Authority:** **NONE (DERIVED TRUTH).** This determination selects an architecture. It authorizes no execution.
> **Verdict:** **RESOLUTION ARCHITECTURE DETERMINED · NOT RESOLVED**

**Mandatory principles, as applied**

| Principle | Applied meaning in this determination |
|---|---|
| **Zero fixes** | The missing predicate was located, the overlap was measured, the rival declaration was read. Nothing was repaired. `RULE_PREDICATES` still holds 8 entries. |
| **Zero patches** | No file edited. One new markdown artifact; nothing else. |
| **Zero shortcuts** | The predecessor's scoping of S-1 was tested rather than inherited, and is corrected in §1.3. No option is selected on convenience. |
| **Zero temporary solutions** | Three of the four options analysed in §9 would restore a green coverage check while leaving the declared class unreachable. All three are refused for that reason. |
| **Zero duplicate classifiers** | A second declaration source already exists and is measured in §5. The resolution retires it; it does not add a third. |
| **Zero overlapping authorities** | The measured R-08 ∩ R-09 overlap is 98 artifacts across two different authority chains. Any resolution that leaves the overlap in place is refused. |

---

## 1. Executive Determination

# RESOLUTION ARCHITECTURE DETERMINED · NOT RESOLVED

**The correct permanent resolution is determinable and is determined here as Option O-4 (§10). It may not yet be executed, because one of its two required authorities is not established.**

### 1.1 The determination in one movement

The coverage failure is real, is exactly one rule wide, and is **not** exactly one dictionary entry deep. Four defects occupy the same rule, and they are not independent — each is a consequence of the same act:

| # | Defect | Measured state |
|---|---|---|
| **D-1** | R-09 is declared with no predicate | `RULE_PREDICATES` = 8 entries; register declares 9 rules; `validate_rule_coverage()` returns `("rule 'R-09' is declared but no predicate implements it",)` |
| **D-2** | R-09 is **unreachable** as declared, even once implemented | R-09's six membership criteria are R-08's five plus one. R-08 holds precedence 8, R-09 precedence 9. Measured: **98** tracked artifacts satisfy both; **0** would ever reach R-09 |
| **D-3** | A **rival declaration** of the same class and rule exists in Python | `mutation_class_extension.py` holds `GOVERNED_ANALYSIS_CLASS` and `GOVERNED_ANALYSIS_RULE` as module literals, already divergent from the register in two fields |
| **D-4** | R-09's authority chain names an authority the register does not declare | `governed_by` cites "Repository Intelligence"; the register's `authorities` list holds 8 entries and none of them is it |

**D-1 is what fails. D-2, D-3 and D-4 are why supplying the predicate is not the resolution.**

### 1.2 The single cause

All four defects were introduced by one act — commit `fb43383e`, *"EXECUTION: Complete Phase 1B with certification (REQ-28, REQ-43, Violation 4)"* — which added the class and the rule **to the declaration and to a new Python module**, and to no predicate in the classifier. The class was declared twice and implemented zero times.

The certification accompanying that act is measurable: `test_violation_4_mutation_extension.py` passes **9 of 9**. It asserts the Python literals in `mutation_class_extension.py`. It never calls `classify()`. In the same tree, `test_mutation_classification.py` — which does call `classify()` — fails **26 of 49**.

> **9 passing tests certified a class that the classifier cannot evaluate, because the tests were pointed at the duplicate rather than at the classifier.**

### 1.3 Correction to the predecessor's scoping of S-1

The predecessor determination closes with: *"One dictionary entry stands between this repository and the ability to classify anything new at all."*

**That sentence is exact about the `ERROR` and understated about the resolution.** One dictionary entry does stand between the repository and a non-`ERROR` return from `classify()`. It does not stand between the repository and correct classification. Adding `_r09_governed_analysis` alone would:

- return `CLASSIFIED` for every subject, and
- assign **98** analysis artifacts to `AUTHORED_DOCUMENT`'s chain — *"→ verify.sh (observation only) → Phase 8 → Phase 9"* — while the register declares them to be governed by a different chain, and
- leave R-09 as evaluated-but-never-matched code, and
- leave the rival declaration in place.

A green coverage check over a rule that can never match is the same defect class as the one the register itself documents as its origin: *"the invariants quantified over classes rather than over artifacts, so an artifact belonging to no class violated nothing."* **S-1 as scoped in the predecessor is therefore insufficient, and this determination records that as a scope correction, not a disagreement about the measurement.**

### 1.4 Why the verdict is NOT RESOLVED

The resolution spans two mutation classes, and only one has an operative authority:

| Half of the resolution | Class | Authority | Operative? |
|---|---|---|---|
| Predicate, predicate-level disjointness, retirement of the rival module, test re-pointing | **SOURCE** (`R-07` claims `mutation_classification.py`, verified) | pre-commit → `verify.sh`, outside the constitutional gateway under Option B | **YES** |
| Declared token vocabulary as data, R-08 criteria narrowing, R-09 authority-chain correction | **GOVERNED_DECLARATION** (`R-06` claims the register — all seven criteria verified True) | owner-parameterised: *"the owning programme authority declared by the artifact itself"* | **DECLARED, NOT RESOLVABLE** |

The register's own self-declared authority reads *"AUTHORED REPOSITORY TRUTH, HELD SUBORDINATE UNDER UCKP-LAW-0001."* That is a **standing**, not an actor. It names no instrument competent to issue the register-side mutation, and the mechanism that would resolve it — `classify()` — returns `ERROR` for the register too.

**The two halves cannot be split** (§9, O-1 and O-2), and one half has no resolvable authority. Therefore: architecture determined, execution not authorized, **NOT RESOLVED**.

### 1.5 What is and is not claimed

| Claim | Status |
|---|---|
| The resolution architecture is determined | **YES — O-4, §10** |
| O-4 is the only architecture satisfying all six mandatory principles | **YES — §9.6** |
| O-4 is authorized | **NO — §12, two preconditions unmet** |
| The failure is resolved | **NO** |
| Closure of any kind | **NOT CLAIMED** |
| S-1 may proceed as previously scoped | **NO — §1.3** |

---

## 2. Current Mutation Classification Reality

### 2.1 The two artifacts that must agree, and do not

| Artifact | Lines | SHA-256 (baseline) | Declares |
|---|---|---|---|
| `00-BOOK/DATA/mutation-governance-boundary.json` | 407 | `a7c8171518…ca5a89ee` | 9 mutation classes · 9 classification rules · 8 authorities · v1.1.0 |
| `platform/repository_intelligence/mutation_classification.py` | 507 | `54ecc7e2c4…dd6def3c` | 8 rule predicates · `R-01`…`R-08` |
| `platform/repository_intelligence/mutation_class_extension.py` | 206 | `9a742a7629…bb5db572` | **a second copy** of the GOVERNED_ANALYSIS class and the R-09 rule |

### 2.2 The failure, measured at the line

`classify()` validates coverage before it evaluates anything:

```
438:    problems = validate_rule_coverage(doc)
439:    if problems:
440:        return ClassificationResult(subject.identity, "", "", "", ERROR, "; ".join(problems))
```

Measured directly at this baseline:

```
validate_rule_coverage(boundary) -> ("rule 'R-09' is declared but no predicate implements it",)
len(RULE_PREDICATES)             -> 8   ['R-01' … 'R-08']
declared rule ids                -> 9   ['R-01' … 'R-09']
```

Three representative subjects, one per authority chain that ought to differ:

| Subject | Result | Class | Rule |
|---|---|---|---|
| `UCOS-OMEGA-INFINITY-PERMANENT-CLOSURE-EXECUTION-READINESS-DETERMINATION.md` | **ERROR** | — | — |
| `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | **ERROR** | — | — |
| `engine/uckp/law.py` | **ERROR** | — | — |

**Every subject returns `ERROR`, and none reaches a predicate.** The fail-closed construction is behaving exactly as designed; the design is refusing because the declaration and the implementation disagree.

### 2.3 `ERROR` is a FAULT, and is not the terminal

The register declares a terminal — `UNRESOLVED`, *"FAILS CLOSED"*, *"must never be read as a permissive default."* The classifier's docstring separates the two: `ClassificationError` is *"a FAULT, never a verdict."*

At this baseline the repository is not producing the terminal. It is producing a fault. The distinction is load-bearing for §13: a resolution that turns `ERROR` into `UNRESOLVED` for 98 artifacts has moved from *"no verdict is reachable"* to *"a verdict of no authority"*, which is a different and still-failing state.

### 2.4 Test reality

| Test module | Lines | Result at baseline | What it exercises |
|---|---|---|---|
| `platform/tests/test_mutation_classification.py` | 599 | **26 failed · 23 passed** | `classify()` against the real register |
| `platform/tests/test_mutation_governance_boundary.py` | — | **9 passed** | register-level invariants |
| `platform/tests/test_violation_4_mutation_extension.py` | 381 | **9 passed** | the Python literals in `mutation_class_extension.py` |

The 23 passes in the first module are the ones that never reach `classify()` — coverage-refusal assertions, subject construction, `to_dict`. The 26 failures are every test that asks for a class.

**The distribution is the finding: the module that tests the duplicate is green, the module that tests the classifier is red, and the register-level module is green because its invariants quantify over class names rather than over artifacts.**

### 2.5 Downstream reach

Consumers of `mutation_classification` at this baseline: `engine/verification_impact/changes.py` (documentation reference at `:61` only), the two test modules above, and `mutation_class_extension.py`. **No verification gate consumes `classify()` as a verdict.** The consequence cuts both ways and both must be stated:

- The `ERROR` state is not currently failing any gate — so nothing in `verify.sh` is announcing it.
- Nothing in `verify.sh` would announce its return either. `$conformance_is_not_claimed_here` names the conformance gate as **EX-018**, and EX-018 does not exist in the tree.

**Mutation classification is presently unenforced in both directions.** That is context for §13's closure criteria, and it is not a mitigation.

---

## 3. Rule Declaration vs Implementation Alignment

Alignment is tested at three levels, because `validate_rule_coverage()` tests only the first.

| Level | What it compares | Instrument that checks it |
|---|---|---|
| **L1 — identity** | declared rule ids ↔ predicate keys | `validate_rule_coverage()` — exists, two-sided |
| **L2 — semantics** | declared predicate text ↔ what the predicate computes | **none exists** |
| **L3 — disjointness** | predicate ∩ predicate = ∅ over real subjects | **none exists** |

### 3.1 L1 — identity alignment

One failure, both directions checked:

- declared-without-predicate: **R-09**
- predicate-without-declaration: **none**

This is the only misalignment the repository can currently detect.

### 3.2 L2 — semantic alignment, evaluated rule by rule

| Rule | Declared predicate | Implementation | Aligned? |
|---|---|---|---|
| R-01 | under `.git/`, **or** present in working tree and neither tracked nor exclusion-governed | `_r01_repository_state` (`:254`) — matches | **YES** |
| R-02 | `.gitignore` or `exclusion-register.json` | `_r02_exclusion` (`:265`) — `_EXCLUSION_INSTRUMENTS`, 2 entries | **YES** |
| R-03 | `id-ledger.json` or `artifacts.json`, **or is a Universal ID or page-range allocation** | `_r03_corpus_registration` (`:269`) — path membership in `_CORPUS_REGISTERS` only | **NO — a declared disjunct is unimplemented** |
| R-04 | `canonical_path` in the generated-artifact registry | `_r04_generated_artifact` (`:273`) | **YES** |
| R-05 | a `Population` or `ConstitutionalMetadata` object | `_r05_constitutional_truth` (`:277`) — OBJECT-kind predicate | **YES** |
| R-06 | all seven GOVERNED_DECLARATION criteria | `_r06_governed_declaration` (`:282`) + `governed_declaration_checks` (`:292`) — seven, individually | **YES** |
| R-07 | a **tracked** executable or build-configuration path | `_r07_source` (`:323`) — suffix or basename only; **`tracked` is not evaluated** | **NO — a declared criterion is dropped** |
| R-08 | all five AUTHORED_DOCUMENT criteria | `_r08_authored_document` (`:395`) + `authored_document_checks` (`:384`) — five, individually | **YES** |
| R-09 | tracked non-generated markdown carrying an analysis token, all six criteria | **absent** | **NO — unimplemented** |

**Three of nine rules are misaligned, and only one of the three is visible to `validate_rule_coverage()`.**

### 3.3 The two silent misalignments, measured

**R-03.** The declared disjunct *"or is a Universal ID or page-range allocation"* describes a subject that is not a path. The classifier's `Subject` model supports exactly this — `OBJECT` kind with an `object_type`, which R-05 uses. R-03 does not use it. So allocation subjects are not claimed by R-03; they fall through every rule and reach the terminal. The register's own `$conformance_is_not_claimed_here` predicted this population by name: *"the `by_object` index of `00-BOOK/DATA/id-ledger.json`, which allocates permanent identities from the shared `category_seq` counter and is not a declared class."*

**R-07.** Measured, predicate-level, on a path that is neither tracked nor present:

```
R-07 predicate claims 'does/not/exist/untracked_probe.py'  -> True
R-01 predicate claims the same path                        -> False
```

R-01 does not compensate, because R-01 requires the path to **exist**. So a `.py` path that is not in the repository at all is claimed as `SOURCE` and handed the pre-commit → `verify.sh` → RIB → AEE → Phase 8 → Phase 9 chain. This is an authority **over-claim** on a non-member, and it is not an ordering artifact.

### 3.4 L3 — disjointness, and the property it violates

The register declares disjointness as a property of the rule set, and explicitly forbids ordering as a substitute:

> `unique`: *"Exactly one class. The predicates are written to be disjoint; the ordering is a tie-break of last resort and never a substitute for disjointness, because two classes would be two authorities and UCKP-ART-18 refuses that."*

Two violations of that property exist at this baseline:

- **R-07 relies on nothing** for the untracked case — it simply over-claims (§3.3).
- **R-08 and R-09 are not disjoint by construction** — R-09's criteria are a strict superset of R-08's (§4.3), so ordering is the *only* thing separating them, which is precisely what the property refuses.

### 3.5 A note recorded and not acted on

`mutation_classification.py`'s module docstring opens *"declares seven ordered classification rules."* The register declares nine. The docstring is stale by two rules. `_r01_repository_state` at `:255` reads `if subject.kind is not PATH and subject.kind != PATH:` — an identity test conjoined with the equivalent equality test, which is redundant rather than wrong. **Both are recorded as observations. Neither is repaired, and neither is a defect this determination resolves.**

---

## 4. R-01–R-09 Coverage Analysis

### 4.1 Coverage matrix

| Rule | Class | Prec. | Predicate | L1 | L2 | Disjoint | Reachable | Subjects claimed at baseline |
|---|---|---|---|---|---|---|---|---|
| R-01 | REPOSITORY_STATE | 1 | `_r01_repository_state` | ✅ | ✅ | ✅ | yes | 0 — `ERROR` precedes evaluation |
| R-02 | EXCLUSION | 2 | `_r02_exclusion` | ✅ | ✅ | ✅ | yes | 0 — as above |
| R-03 | CORPUS_REGISTRATION | 3 | `_r03_corpus_registration` | ✅ | **⚠ partial** | ✅ | yes | 0 — as above |
| R-04 | GENERATED_ARTIFACT | 4 | `_r04_generated_artifact` | ✅ | ✅ | ✅ | yes | 0 — as above |
| R-05 | CONSTITUTIONAL_TRUTH | 5 | `_r05_constitutional_truth` | ✅ | ✅ | ✅ | yes | 0 — as above |
| R-06 | GOVERNED_DECLARATION | 6 | `_r06_governed_declaration` | ✅ | ✅ | ✅ | yes | 0 — as above |
| R-07 | SOURCE | 7 | `_r07_source` | ✅ | **❌ over-claims** | **❌** | yes | 0 — as above |
| R-08 | AUTHORED_DOCUMENT | 8 | `_r08_authored_document` | ✅ | ✅ | **❌ vs R-09** | yes | 0 — as above |
| R-09 | GOVERNED_ANALYSIS | 9 | **absent** | **❌** | **❌** | **❌ vs R-08** | **no — 0 even if supplied** | 0 |
| terminal | UNRESOLVED | — | fall-through | ✅ | ✅ | n/a | yes | 0 — `ERROR` precedes it |

**Every cell in the final column is 0. Nine implemented-or-declared rules and one terminal, and not one of them classifies anything, because coverage refusal precedes rule evaluation.**

### 4.2 Coverage totals

| Measure | Count |
|---|---|
| Rules declared | 9 |
| Predicates implemented | 8 |
| L1-aligned | 8 of 9 |
| L2-aligned | 6 of 9 |
| Disjoint by predicate | 6 of 9 |
| Reachable if L1 were closed | **8 of 9** |
| Subjects classified at baseline | **0** |

### 4.3 The reachability measurement

R-09's declared membership criteria, against R-08's:

| Criterion | R-08 AUTHORED_DOCUMENT | R-09 GOVERNED_ANALYSIS |
|---|---|---|
| markdown | ✅ | ✅ |
| authored | ✅ | ✅ |
| repository-controlled (tracked) | ✅ | ✅ |
| non-generated | ✅ | ✅ |
| self-declared authority | ✅ | ✅ |
| **analysis-artifact filename token** | — | ✅ |

R-09 ⊂ R-08, strictly. Under `evaluation: "ORDERED PRECEDENCE — rules are evaluated in the order declared, and the first rule whose predicate holds assigns the class"`, and with R-08 at precedence 8 and R-09 at precedence 9:

```
tracked .md paths                                  : 3331
satisfying R-08's five criteria                    :  458
of those, carrying an R-09 analysis filename token :   98   <- R-08 ∩ R-09
reachable by R-09 under declared precedence        :    0
```

**98 artifacts satisfy two rules naming two different authority chains, and the later rule can never be reached. Supplying the predicate would add 0 classifications and 1 permanently-dead branch.**

### 4.4 The register contradicts itself on this point

`$distinction_from_authored_document` states:

> *"R-09 evaluates before R-08 so analysis artifacts are classified as GOVERNED_ANALYSIS rather than the more general AUTHORED_DOCUMENT."*

The declared precedences are R-08 = 8 and R-09 = 9, and `evaluation` is declared-order-first. **The register's stated intent and the register's declared mechanism are opposites.** This is a defect in the declaration, not in the classifier, and it is why the resolution cannot be source-only.

### 4.5 Subjects that would remain unclassified after L1 closure alone

| Population | Disposition after predicate-only repair |
|---|---|
| 98 analysis artifacts | `AUTHORED_DOCUMENT` — **wrong chain per the register's stated intent** |
| 360 remaining R-08 markdown artifacts | `AUTHORED_DOCUMENT` — correct |
| 2,873 tracked `.md` failing an R-08 criterion | `UNRESOLVED` — fails closed, correct-as-declared |
| Universal ID / page-range allocations | `UNRESOLVED` — R-03's declared disjunct unimplemented (§3.3) |
| Untracked `.py` paths | `SOURCE` — **over-claimed** (§3.3) |
| This determination and its predecessor | `UNRESOLVED` — untracked, so the `repository-controlled` criterion fails |

---

## 5. Duplicate / Overlap Analysis

Two distinct duplications exist. They are different in kind and both are disqualifying for any resolution that leaves them.

### 5.1 Duplicate declaration source — `mutation_class_extension.py`

`mutation_classification.py`'s docstring states the governing rule for its own layer:

> *"THE RULES ARE DATA, NOT CODE. This module contains no rule text, no class name ordering and no predicate the register does not declare."*

`mutation_class_extension.py` holds, as Python module-level literals: the full `GOVERNED_ANALYSIS_CLASS` dict — class name, `examples`, `governed_by`, six `membership_criteria`, `grants_only_mutation_ownership`, `does_not_govern`, `$why_this_class_was_added` — and the full `GOVERNED_ANALYSIS_RULE` dict, including `precedence: 9`.

**This is rule text and class ordering held in code, and it is a rival to the register.** `UCKP-ART-18` — *"Before anything is created its canonical object shall be located. If it exists it is reused, extended or referenced. It is never duplicated and never given a rival"* — is the article violated. `UCKP-ART-11` — *"Markdown, JSON, YAML and schemas are not authority"* — bears on the converse and is honoured by the register calling itself a projection; it does not license a Python copy.

### 5.2 The duplicate has already diverged, in three places

| Field | Register (canonical) | `mutation_class_extension.py` (rival) |
|---|---|---|
| `membership_criteria` analysis clause | *"carries determination/analysis/assessment/**execution/matrix/readiness/admission/blocker/gap** in filename"* — 9 tokens | *"carries determination/analysis/assessment in filename **or declares analysis type**"* — 3 tokens + an undeclared disjunct |
| `examples` | 8 entries (adds `BLOCKER-ELIMINATION-DETERMINATION.md`, `100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md`) | 6 entries |
| internal consistency | criteria (9 tokens) and predicate (9 tokens) agree | criteria (3 tokens) and its own `predicate` (9 tokens) **disagree with each other** |

The divergent disjunct *"or declares analysis type"* names no field, and no declaration convention in the repository carries one. It is **undecidable from repository state**, which violates the register's own `repository_evaluable` property: *"Every predicate is decidable from tracked repository state alone."*

**Duplication has already produced drift, in under one commit's distance from its introduction. This is the concrete harm ART-18 exists to prevent, observed rather than predicted.**

### 5.3 The duplicate is also an out-of-band mutator

`extend_mutation_governance_boundary()` opens the register and, with `dry_run` defaulting to **False**, writes it:

```
with boundary_path.open("w", encoding="utf-8") as f:
    json.dump(boundary, f, indent=2, ensure_ascii=False)
```

It also performs a semantic-version minor bump on the register. So a `platform/repository_intelligence` source module can author a `GOVERNED_DECLARATION`-class artifact directly, with no owner act and no gateway. Against the register's own recurrence-prevention text — *"A future mutation class added without an authority fails that test"* — this is the mechanism by which a class was added, and the test it names did not fail.

Its present state is worth stating precisely: because `GOVERNED_ANALYSIS` is now in the register, the function can only raise `ValueError`. **It is a mutator whose sole reachable outcome against the real register is an exception, and whose sole live use is as a literal source for tests.**

### 5.4 Duplicate class membership — the 98-artifact overlap

Measured in §4.3: 98 tracked artifacts satisfy both R-08 and R-09. The two rules name **different** authority chains:

| Rule | `governed_by` |
|---|---|
| R-08 → AUTHORED_DOCUMENT | *"the authority the artifact declares of itself … → verify.sh (observation only) → **Phase 8 → Phase 9**"* |
| R-09 → GOVERNED_ANALYSIS | *"the authority the analysis declares of itself … → **Repository Intelligence** → verify.sh (observation only)"* |

These are not the same chain, and neither is a prefix of the other. The register's own invariants name the failure: *"No artifact resolves to more than one mutation class. **Failure: authority ambiguity.**"*

### 5.5 Why no existing instrument detects either duplication

| Instrument | What it checks | Why the overlap is invisible to it |
|---|---|---|
| `validate_rule_coverage()` | rule ids ↔ predicate keys | identity only; no predicate semantics, no intersection |
| `test_2_no_class_is_claimed_by_two_authorities_as_primary` | `len(classes) == len(set(classes))` | **uniqueness of class *names*, not of artifact membership** |
| `test_3_no_mutation_class_is_ungoverned` | `required <= covered` where `required` is a **hardcoded 5-name set** | GOVERNED_DECLARATION, AUTHORED_DOCUMENT and GOVERNED_ANALYSIS are not in `required`; the invariant does not grow with the register |
| `test_4_every_named_authority_implementation_exists` | iterates the `authorities` list | class `governed_by` chains are never parsed, so D-4 passes unseen |
| `test_violation_4_*` (9 passing) | Python literals in the rival module | never calls `classify()`; asserts the duplicate against itself |

> **The register documented this exact vacuity as the cause of the previous gap — *"its invariants quantified over classes rather than over artifacts, so an artifact belonging to no class violated nothing"* — and the invariants were not changed when the ninth class was added. The vacuity recurred in the same shape.**

---

## 6. Extension Mechanism Assessment

### 6.1 What the mechanism actually is

`add_dynamic_class_extension_mechanism()` returns a dict. It declares itself:

> `"status": "SPECIFIED (implementation deferred to Phase 3-4)"` — *"This is a SPECIFICATION, not an implementation."*

It specifies a registry at `00-BOOK/DATA/mutation-class-extensions.json`, a `load_extensions()` loader in `mutation_classification.py`, a merge strategy, four validation rules, and a `HYPOTHETICAL_CLASS` example.

| Component specified | Exists in tree? |
|---|---|
| `00-BOOK/DATA/mutation-class-extensions.json` | **NO** |
| `load_extensions()` in `mutation_classification.py` | **NO** |
| `merge_classes()` | **NO** |
| extension validation | **NO** |
| tests for extension loading | **NO** |

**The extension mechanism is a returned dictionary describing itself. Nothing loads it, nothing consumes it, and two of the nine passing Violation-4 tests assert properties of that dictionary's own string content.**

### 6.2 Assessment against the constraint it claims to satisfy

The mechanism's stated purpose is *"future classes admissible via data (not code change)"* — the property `UCKP-ART-17` requires: *"an unknown future category is admitted by registration, never by amendment."*

It fails that purpose at its own root, and the failure is self-demonstrating:

| Claim | Reality |
|---|---|
| Classes admissible via data | The one class it admits — GOVERNED_ANALYSIS — is a **Python literal in the same module** |
| Unbounded expansion | The register's rule set is fixed-arity in `RULE_PREDICATES`; each new rule still requires a new predicate function |
| Registration, not amendment | Its own `extend_…()` performs an **amendment** — it rewrites the register file |

### 6.3 Is a second registry the right shape at all?

**No, and this bears directly on §9.** A `mutation-class-extensions.json` would be a second declaration source for the same thing the register already declares. The register is the canonical home of mutation classes and rules; a second file holding more of them is a rival home, refused by ART-18 on the same grounds as §5.1. The register is already extensible **in the only sense that matters**: it is data, and classes and rules are appended to it — which is exactly how R-08 and R-09 were both added.

**The genuine extensibility gap is one level down and is not what the mechanism addresses:** R-09's analysis-token vocabulary is prose inside a criterion string. To evaluate it, the vocabulary must be readable as data. Two dispositions exist:

| Disposition | Consequence |
|---|---|
| Predicate hardcodes the 9 tokens as a Python frozenset | A new analysis kind requires a **code edit**. `UCKP-ART-15` — *"No conclusion rests on a hardcoded assumption; every finding is derived from the declared universe"* — is violated, and the vocabulary is closed |
| Register carries the tokens as a **declared list**, predicate reads them from `boundary` | A new analysis kind is admitted by **declaration**. ART-15 and ART-17 both hold |

The precedent cuts toward the second: `_EXECUTABLE_SUFFIXES` (2 members) and `_EXCLUSION_INSTRUMENTS` (2 members) are enumerated in code because the register enumerates them exhaustively in the rule text and they are closed by nature. An analysis-artifact vocabulary is **open by nature** — it is the vocabulary of the repository's own future work products. The two cases are not analogous, and treating them as analogous is how the closed enumeration would be smuggled in.

Every predicate in `RULE_PREDICATES` already receives `boundary` as its third parameter. **The channel to read declared data exists and is unused by all eight predicates.**

### 6.4 Extension mechanism verdict

| Question | Answer |
|---|---|
| Does an extension mechanism exist? | **NO — a specification of one exists, as a return value** |
| Is it needed for the resolution? | **NO — the register is already the extensible surface** |
| Should it be implemented? | **NO — it would create a second declaration home (ART-18)** |
| Should it be retired? | **YES — §10.4** |
| Is there a real extensibility gap? | **YES — the analysis-token vocabulary must be register data, not code (§6.3)** |

---

## 7. Authority Ownership Analysis

### 7.1 The two mutation classes the resolution touches

| Surface | Verified class | Authority chain | Consults `classify()`? | Operative? |
|---|---|---|---|---|
| `mutation_classification.py` | **SOURCE** — `_r07_source` returns True, verified | pre-commit → `verify.sh` → RIB-001 → AEE-001 → Phase 8 → Phase 9 | **NO** | **YES** |
| `mutation_class_extension.py`, both test modules | **SOURCE** | as above | NO | **YES** |
| `mutation-governance-boundary.json` | **GOVERNED_DECLARATION** — `_r06_governed_declaration` returns True; all seven criteria verified True | owner-parameterised: *"the owning programme authority declared by the artifact itself"* | **the mechanism that resolves it is the one that is broken** | **NO** |

The seven R-06 criteria, measured on the register itself:

```
authored True · repository-controlled True · declaration-bearing True
programme-owned True · engine-consumed True · non-generated True · non-executable True
```

**The register that declares the classification rules is classifiable by them, and cannot presently be classified by them.**

### 7.2 Why the register's authority is declared but not resolvable

`GOVERNED_DECLARATION`'s chain is owner-parameterised by design, and the register explains why: *"UISD-000001 owns its declaration, UCL-000001 owns the stage manifest… The authority is therefore read from the artifact."*

Read from this artifact, the `authority` field returns:

> *"AUTHORED REPOSITORY TRUTH, HELD SUBORDINATE UNDER UCKP-LAW-0001. This artifact declares the boundary; it does not create a new authority and governs nothing itself."*

That is a **standing**, not an owner. `constitutional_superior` names `UCKP-LAW-0001` at `engine/uckp/law.py` with `relation: PROJECTION` and articles `UCKP-ART-10`, `UCKP-ART-16`, and states the effect: *"It owns which mutation classes exist and which authority disposes of each; it may never own knowledge."*

So the register's own text establishes **what the register may own** and does not establish **who may change it**. This is the precise sense in which the predecessor's §1.4 distinction holds: *"mutation authority is declared … and its executable resolution is what fails."* For this artifact the gap is sharper — the declaration itself names no actor, so even a working classifier would return an owner-parameterised chain that resolves to a standing.

### 7.3 D-4 — R-09 names an undeclared authority

`GOVERNED_ANALYSIS.governed_by` cites *"→ Repository Intelligence →"*. The register's `authorities` list holds 8 entries, each with an `implementation` path:

```
UCOS-CMG-EXEC-000001 · pre-commit hook · verify.sh · UCOS-RIB-001
UCOS-AEE-001 · Phase 8 · Phase 9 · REG-AUTO-001
```

**"Repository Intelligence" is not among them.** The register's invariant *"Every named authority resolves to an implementation that exists in the tree"* is not violated as tested, because `test_4` iterates the `authorities` list and never parses a class's `governed_by` chain. So the ninth class was given a chain through an authority that the register does not declare, does not bind to an implementation, and does not test.

**This is a hidden authority in the strict sense — a party named in a governing chain with no declaration and no implementation binding.** It is the fourth defect, and it is the one that cannot be closed by any amount of source work.

### 7.4 Authority findings

**F-1 — The source half of the resolution has a present, operative, declared authority.** Under Option B, source mutations are outside the constitutional gateway and are governed by pre-commit → `verify.sh`. That chain does not consult `classify()`, so it cannot deadlock on the defect it repairs. This is the same structural basis on which the predecessor found S-1 eligible, and it survives the enlarged scope **for the source half only**.

**F-2 — The declaration half has no resolvable authority.** The register-side corrections (token vocabulary as data, R-08 criteria narrowing, R-09 chain correction) are `GOVERNED_DECLARATION` mutations whose authority is owner-parameterised and whose owner is, on the artifact's own text, a standing rather than an actor.

**F-3 — The two halves may not be separated.** §9 establishes this as an evidentiary conclusion rather than a preference: every split produces either a dead rule (source-first) or a rule declared for a predicate that does not exist (declaration-first). Both are the states this determination exists to end.

**F-4 — D-4 requires an authority act that is not a code act and not a declaration edit under the same owner.** Declaring "Repository Intelligence" as an authority with a bound implementation **creates an authority**. Nothing in this determination, and no engineering step, may do that. The alternative — correcting R-09's chain to name only already-declared authorities — is a declaration edit and falls under F-2.

**F-5 — No part of the resolution confers certification.** `GOVERNED_ANALYSIS`'s own text: *"It grants no certification authority, no ratification authority and no freeze authority."* A fully converged R-09 would make these determinations **classifiable**, not certified, and not final.

### 7.5 Overlapping-authority check on the resolution itself

| Test | O-4 result |
|---|---|
| Does it create a mutation class? | **NO — all 9 already declared** |
| Does it create an authority? | **NO — and D-4 is held as a precondition precisely so that it cannot** |
| Does it place any instrument above `CMG-000001` / `UCIC-001` / `UCKP-ART-05`? | **NO** |
| Does it resolve an authority question by implementation? | **NO — D-4 is escalated, not coded** |
| Does it remove an authority? | **NO — it removes an out-of-band mutator (§5.3), which is not an authority** |
| Does it leave any artifact under two chains? | **NO — that is its purpose** |

---

## 8. Existing Architecture Reuse Assessment

Every component the resolution needs, assessed for existence before anything is proposed — `UCKP-ART-18`, applied to this determination's own output.

| Need | Canonical object | Exists? | Disposition |
|---|---|---|---|
| Rule declaration home | `mutation-governance-boundary.json` `classification_rules.rules` | **YES** | **REUSE** — R-09 is already declared in it |
| Class declaration home | same register, `mutation_classes` | **YES** | **REUSE** — GOVERNED_ANALYSIS already declared |
| Classifier | `mutation_classification.py` | **YES** | **EXTEND** — one predicate into the existing `RULE_PREDICATES` |
| Per-criterion evidence shape | `authored_document_checks()` (`:384`), `governed_declaration_checks()` (`:292`) | **YES** | **REUSE** — R-09's checks follow the identical shape |
| Markdown metadata reader | `_markdown_declared_fields()`, `authored_document_owner()` | **YES** | **REUSE** — R-09's `self-declared-authority` criterion is R-08's, unchanged |
| Tracked/generated/producer views | `Repository.tracked`, `.generated`, `.producer_homes` | **YES** | **REUSE** — no new repository view |
| Declared-data channel into predicates | the `boundary: dict` third parameter of every predicate | **YES, unused** | **REUSE** — this is how the token vocabulary is read |
| Two-sided coverage refusal | `validate_rule_coverage()` (`:415`) | **YES** | **REUSE unchanged** — it is correct; it was telling the truth |
| Fail-closed terminal | `classification_rules.terminal` | **YES** | **REUSE unchanged** |
| Extension registry | specified only, `mutation-class-extensions.json` | **NO** | **DO NOT CREATE** — §6.3 |
| Extension loader / merge | specified only | **NO** | **DO NOT CREATE** — §6.3 |
| Second classifier | — | **NO** | **REFUSED** — zero duplicate classifiers |
| Parallel rule system | — | **NO** | **REFUSED** — zero parallel rule systems |
| Rival class declaration | `mutation_class_extension.py` | **YES — and must not persist** | **RETIRE** — §10.4 |
| Artifact-level disjointness check | — | **NO** | **NEW TEST OBLIGATION** — §13.4 |
| Conformance gate | EX-018, named in the register | **NO** | **out of scope; recorded in §13.6** |

### 8.1 Reuse totals

| Disposition | Count |
|---|---|
| REUSE unchanged | 7 |
| EXTEND existing | 2 (one predicate · one register field) |
| CORRECT existing | 3 (R-08 criteria · R-09 chain · overlap-blind invariants) |
| RETIRE existing | 1 (the rival module and its 9 self-referential tests) |
| **CREATE** | **0 mechanisms · 1 test obligation on an existing test module** |

**The resolution creates no mechanism. That is the strongest single indicator that O-4 is convergence rather than construction, and it is consistent with the predecessor architecture's 0-CREATE finding.**

---

## 9. Option Analysis

Four options. Each is tested against the six mandatory principles and against the register's own declared properties (`unique`, `repository_evaluable`, `total`, `deterministic`).

### 9.1 O-1 — Supply the R-09 predicate only

Add `_r09_governed_analysis` to `RULE_PREDICATES`, mirroring `_r08_authored_document`, with the nine tokens as a module frozenset. Touch nothing else. **This is S-1 exactly as the predecessor scoped it.**

| Effect | Measured / determined |
|---|---|
| `validate_rule_coverage()` | returns `()` — coverage closed |
| `classify()` | stops returning `ERROR`; the 26 failing tests would pass |
| R-09 matches | **0 subjects** — unreachable behind R-08 (§4.3) |
| 98 analysis artifacts | assigned `AUTHORED_DOCUMENT` — the chain the register's stated intent excludes |
| Rival declaration | **persists**, with its existing divergence |
| D-4 undeclared authority | **persists** |
| Token vocabulary | **hardcoded in Python** — closed, ART-15 |
| Register self-contradiction (§4.4) | **persists** |

| Principle | Verdict |
|---|---|
| Zero shortcuts | **FAIL** — makes the check green while the declared rule remains inert |
| Zero temporary solutions | **FAIL** — a dead branch awaiting a second act is a staged solution |
| Zero duplicate classifiers | **FAIL** — the rival declaration survives |
| Zero overlapping authorities | **FAIL** — the 98-artifact overlap survives |
| Converges declaration and implementation | **FAIL** — implements a rule the declaration cannot reach |

**REJECTED.** O-1's most dangerous property is not that it is incomplete — it is that it **removes the signal**. Once `classify()` returns `CLASSIFIED` for every subject, nothing in the repository reports that a declared class governs nothing.

### 9.2 O-2 — Supply the predicate and reorder R-09 before R-08

As O-1, plus swap the declared precedences so R-09 evaluates first, matching `$distinction_from_authored_document`'s stated intent.

| Effect | Determined |
|---|---|
| R-09 matches | 98 subjects |
| Disjointness | **still absent** — the sets still intersect; ordering is the only separator |
| Register's `unique` property | **violated by its own terms**: *"the ordering … never a substitute for disjointness"* |
| 98 artifacts | migrated from one authority chain to another **by a precedence integer**, with no owner act naming the migration |
| Rival declaration, D-4, hardcoded tokens | **all persist** |

| Principle | Verdict |
|---|---|
| Zero shortcuts | **FAIL** — ordering used as the disjointness mechanism the register forbids |
| Zero overlapping authorities | **FAIL** — the overlap is masked, not removed |
| Zero duplicate classifiers | **FAIL** |
| Avoids bypassing governance | **FAIL** — an authority migration for 98 artifacts performed as a number change |

**REJECTED.** O-2 is worse than O-1 in one specific way: it produces a *correct-looking* result — 98 artifacts under the intended chain — from a mechanism the register explicitly refuses. The right answer by the wrong instrument is the harder defect to find later.

### 9.3 O-3 — Retract R-09 and GOVERNED_ANALYSIS from the register

Remove the ninth class and rule. Coverage closes at 8 = 8. Delete the rival module and its tests.

| Effect | Determined |
|---|---|
| `validate_rule_coverage()` | returns `()` |
| Overlap | **eliminated** — one rule, no intersection |
| Rival declaration | eliminated |
| D-4 | eliminated — the chain naming the undeclared authority is gone |
| 98 analysis artifacts | `AUTHORED_DOCUMENT` — and the register's stated governance need for a distinct analysis class is **discarded** |
| Append-only evolution | **`UCKP-ART-14` — *"It appends; it never rewrites"*** — a retraction rewrites |
| Authority | **retraction is a larger declaration act than correction**, under the same unresolved owner (§7.2) |

| Principle | Verdict |
|---|---|
| Zero duplicate classifiers | PASS |
| Zero overlapping authorities | PASS |
| Zero shortcuts | **FAIL** — resolves the disagreement by deleting one side of it |
| Converges declaration and implementation | **FAIL** — converges by removal, not by convergence |
| Preserves existing constitutional mechanisms | **FAIL** — discards a declared class and a stated governance need |

**REJECTED.** O-3 is the only option that reaches a coherent state without touching the classifier, and it is refused because the task is convergence and the constitution is append-only. It is recorded rather than dismissed: **if the owner determines that GOVERNED_ANALYSIS was declared in error, O-3 becomes the correct resolution and this determination's selection must be re-opened.** That determination is not available to engineering.

### 9.4 O-4 — Single-source convergence, applied atomically

One classifier, one register, four coupled corrections, applied as a single mutation:

| # | Correction | Surface | Class |
|---|---|---|---|
| **C-1** | The analysis-token vocabulary becomes a **declared list on the GOVERNED_ANALYSIS class**; the predicate reads it from the `boundary` parameter it already receives | register | GOVERNED_DECLARATION |
| **C-2** | `_r09_governed_analysis` + `governed_analysis_checks()` added to the existing classifier, mirroring `authored_document_checks()`; registered in `RULE_PREDICATES`; reuses `authored_document_owner()` unchanged | classifier | SOURCE |
| **C-3** | R-08's declared criteria and predicate gain the **negation** of the analysis-artifact criterion, so R-08 ∩ R-09 = ∅ **by predicate**, independent of precedence; the register's §4.4 self-contradiction resolves because ordering ceases to be load-bearing | register + classifier | both |
| **C-4** | The rival declaration is **retired**: `mutation_class_extension.py` deleted, its 9 tests re-pointed at the register and `classify()`. R-09's `governed_by` chain corrected to name only declared authorities — **or** escalated if "Repository Intelligence" is to become one | classifier + register + escalation | SOURCE + GOVERNED_DECLARATION + **authority** |

| Effect | Determined |
|---|---|
| Coverage | closed, 9 = 9 |
| R-09 reachable | **98 subjects**, by predicate rather than by ordering |
| Overlap | **∅ by construction** |
| Declaration sources | **one** |
| Token vocabulary | **register data** — a new analysis kind is admitted by declaration, no code edit (ART-15, ART-17) |
| Hardcoded exceptions | none — no path, filename or artifact is special-cased anywhere |
| Second classifier | none |
| Parallel rule system | none |
| Mechanisms created | **0** |

| Principle | Verdict |
|---|---|
| Zero fixes / patches | PASS — no repair-in-place of a symptom; the declaration and implementation are made to agree |
| Zero shortcuts | PASS — disjointness is structural, not ordered |
| Zero temporary solutions | PASS — permanent on first application; no follow-up act is presumed |
| Zero duplicate classifiers | PASS — count goes from 2 declaration sources to 1 |
| Zero overlapping authorities | PASS — measured overlap 98 → 0 |
| Preserves constitutional mechanisms | PASS — Option B, the terminal, two-sided coverage refusal, and `verify.sh`'s observational role are all untouched |
| Converges declaration and implementation | **PASS — this is its definition** |

**SELECTED as the architecture. NOT AUTHORIZED for execution — §9.5.**

### 9.5 The atomicity requirement, and why it blocks O-4 today

O-4's four corrections span two mutation classes. Neither ordering is admissible as a staged execution:

| Split | Intermediate state | Why refused |
|---|---|---|
| Source first (C-2 before C-1/C-3) | predicate exists, register unchanged → R-09 reachable by 0 subjects, tokens necessarily hardcoded to be evaluable at all | **This is O-1.** Rejected above |
| Declaration first (C-1/C-3 before C-2) | register declares a token list and a narrowed R-08 → `validate_rule_coverage()` **still returns the R-09 problem**, and R-08's narrowed criteria now disagree with `authored_document_checks()`, adding a **second** L1/L2 misalignment | Increases divergence; `classify()` still `ERROR` for every subject |

**Therefore O-4 is atomic, and an atomic mutation spanning SOURCE and GOVERNED_DECLARATION requires both authorities present at the same moment. F-1 supplies one. F-2 and F-4 leave the other unestablished.**

### 9.6 Option comparison

| | O-1 predicate only | O-2 + reorder | O-3 retract | **O-4 converge** |
|---|---|---|---|---|
| Coverage closes | ✅ | ✅ | ✅ | ✅ |
| R-09 reachable | ❌ 0 | ⚠ 98, by ordering | n/a — removed | ✅ 98, by predicate |
| Disjoint by predicate | ❌ | ❌ | ✅ | ✅ |
| One declaration source | ❌ | ❌ | ✅ | ✅ |
| D-4 closed | ❌ | ❌ | ✅ by removal | ⚠ escalated |
| Vocabulary open to declaration | ❌ | ❌ | n/a | ✅ |
| Append-only respected | ✅ | ✅ | ❌ | ✅ |
| Mechanisms created | 0 | 0 | 0 | **0** |
| Principles failed | **5** | **4** | **3** | **0** |
| Executable at this baseline | eligible, and wrong | eligible, and wrong | needs declaration authority | **needs both authorities** |

**No option is both executable now and correct. O-1 and O-2 are executable now under F-1 and fail the principles. O-4 satisfies every principle and is not executable now.**

---

## 10. Permanent Resolution Selection

### 10.1 Selection

**O-4 — single-source convergence, applied atomically — is the permanent resolution architecture.**

It is selected because it is the only option that (a) leaves one classifier, (b) leaves one declaration source, (c) achieves disjointness by predicate rather than by ordering, (d) opens the analysis vocabulary to declaration rather than closing it in code, (e) creates zero mechanisms, and (f) fails none of the six mandatory principles.

**Selection is architectural. It is not authorization, and §12 records what authorization would require.**

### 10.2 The convergence stated exactly

For each defect, the terminal state the resolution must reach — stated as a property, not as an edit:

| Defect | Terminal property |
|---|---|
| **D-1** | `validate_rule_coverage(boundary) == ()` with 9 declared rules and 9 predicates, the two-sided check **unchanged and unweakened** |
| **D-2** | R-08's and R-09's predicates are **disjoint over every repository subject**, and reordering the declared rules changes no artifact's class |
| **D-3** | Exactly one artifact in the repository declares the GOVERNED_ANALYSIS class and the R-09 rule, and it is the register |
| **D-4** | Every authority named in every class's `governed_by` chain resolves to a declared authority with an implementation present in the tree |

### 10.3 What the resolution must not do, restated as prohibitions

| Prohibited | Basis |
|---|---|
| A second classifier module | zero duplicate classifiers; ART-18 |
| A second rule or class registry, including `mutation-class-extensions.json` | zero parallel rule systems; §6.3 |
| A compatibility shim between the register and the classifier | zero temporary solutions; the disagreement is the defect, not the interface |
| Any per-path, per-filename or per-artifact exception | zero hardcoded exceptions; ART-15 |
| Weakening `validate_rule_coverage()`, or making it one-sided | zero shortcuts; it is correct and was telling the truth |
| Making `UNRESOLVED` permissive, or collapsing it with `ERROR` | the register: *"must never be read as a permissive default"*; FAULT ≠ verdict |
| Ordering as the disjointness mechanism | the register's `unique` property |
| Declaring "Repository Intelligence" an authority as part of an engineering step | F-4; it would create an authority |
| Writing the register from a `platform/` module | §5.3; it is an out-of-band mutation path |
| Retracting a declared class to close coverage | ART-14; and it is O-3, which requires an owner determination |

### 10.4 Retirement of the rival module — scope and caution

`mutation_class_extension.py` (206 lines) and `test_violation_4_mutation_extension.py` (381 lines, 9 passing) are the rival declaration and its self-referential proof. Retirement means: the module is deleted, and the 9 tests are re-pointed at the register and `classify()` so that each assertion is made against the canonical source.

**Two cautions are recorded because they change what retirement costs:**

1. `test_violation_4_governed_analysis_class_structure` asserts the **divergent** 3-token criterion string. Re-pointing it at the register changes its expected value. **A test whose expected value is the rival's text is a lock-in: it will fail when the duplicate is removed, and that failure is correct.** It must not be read as a regression, and it must not be preserved by keeping the literal.
2. The 9 tests currently constitute the stated evidence for *"✅ VIOLATION 4 CERTIFIED (extensibility operational)."* Retiring them **withdraws that evidence**. The certification was measured against literals, and `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` means no machine certificate confers finality in any case — but the withdrawal must be recorded by the owner rather than absorbed silently.

### 10.5 What selection does not settle

| Open | Why it stays open |
|---|---|
| Whether "Repository Intelligence" becomes a declared authority, or R-09's chain is corrected to declared authorities | **An authority determination. Not available to engineering (F-4)** |
| R-03's unimplemented declared disjunct (§3.3) | A separate L2 misalignment, in a different rule and a different class. **Not folded in** — folding unrelated corrections into an atomic mutation is how scope becomes unfalsifiable |
| R-07's `tracked` over-claim (§3.3) | As above. Recorded, not bundled |
| The stale module docstring and the `:255` redundancy | Observations (§3.5). Not defects this resolution closes |
| Whether GOVERNED_ANALYSIS should exist at all | O-3's precondition. **An owner determination** |
| EX-018, the conformance gate | Declared absent by the register itself; out of this determination's scope (§13.6) |

---

## 11. Zero Patch / Zero Shortcut Compliance

### 11.1 Compliance of this determination

| Principle | Evidence |
|---|---|
| **Zero fixes** | `RULE_PREDICATES` still holds 8 entries. The predicate was specified and not written. The 98-artifact overlap was measured and not removed. The rival module was read and not deleted |
| **Zero patches** | No file edited. `git status --porcelain` unchanged at 38 tracked-modified; one new untracked artifact |
| **Zero shortcuts** | The predecessor's S-1 scoping was tested and corrected (§1.3) rather than inherited. The verdict remains **NOT RESOLVED** where authority evidence is absent |
| **Zero temporary solutions** | Three options that would produce a green check today are refused, by name, with their measured consequences (§9.1–9.3) |
| **Zero duplicate classifiers** | This determination adds no classifier, no registry, no rule text and no class declaration. It names the existing duplicate and requires its retirement |
| **Zero overlapping authorities** | This determination confers no authority. §7.5 checks the selected resolution against overlap and D-4 is escalated rather than resolved by design |

### 11.2 Compliance of the selected resolution

| Test | O-4 |
|---|---|
| Is any symptom repaired without its cause? | **NO** — all four defects are addressed as one act, because they were introduced as one act |
| Is any mechanism added? | **NO — 0 CREATE (§8.1)** |
| Is any existing mechanism weakened? | **NO** — the two-sided coverage check, the terminal, and Option B are untouched |
| Is any artifact special-cased? | **NO** |
| Is any check made to pass by lowering it? | **NO** — R-08's narrowing makes it *stricter*, and the 26 failing tests must pass unweakened |
| Does anything remain for a later step? | **Only the authority acts, which engineering may not perform** |
| Is a compatibility layer introduced? | **NO** — the two sides are made to agree, not bridged |
| Does governance get bypassed anywhere? | **NO** — the one existing bypass (§5.3) is removed |

### 11.3 The shortcut most available here, named so it is not taken

The cheapest action at this baseline is O-1: eight lines of Python, coverage closes, 26 tests go green, and the repository reports `CLASSIFIED` for every subject.

**It would also delete the only signal that a declared mutation class governs nothing.** After O-1, `validate_rule_coverage()` returns `()`, `classify()` returns a class for everything, and the fact that R-09 matches zero subjects is visible only to someone who computes the intersection by hand — as this determination did.

> The register already recorded this failure mode once, about itself: *"Six certified mutations to it proved execution validity and could not prove governance validity."* O-1 would reproduce it exactly — a green mechanism over an ungoverned population. **It is refused, and it is refused specifically because it is available.**

---

## 12. Implementation Preconditions

Preconditions, not tasks. None is dischargeable by engineering, and O-4 may not begin until all four hold.

### 12.1 The preconditions

| # | Precondition | Class | Status | Discharged by |
|---|---|---|---|---|
| **P-1** | An owner competent to mutate `mutation-governance-boundary.json` is identified. The artifact's own `authority` field returns a **standing**, not an actor (§7.2), so the owner must be named by an act outside the artifact | GOVERNED_DECLARATION | **NOT SATISFIED** | owner act |
| **P-2** | D-4 is ruled: either "Repository Intelligence" is declared as an authority with a bound implementation, **or** R-09's `governed_by` chain is corrected to name only the 8 declared authorities. **The first creates an authority and is not an engineering act** | authority | **NOT SATISFIED** | authority act (F-4) |
| **P-3** | The withdrawal of *"VIOLATION 4 CERTIFIED"* is recorded, since retirement of the 9 self-referential tests withdraws its stated evidence (§10.4) | declaration | **NOT SATISFIED** | owner record |
| **P-4** | Atomicity is authorized: one mutation spanning SOURCE and GOVERNED_DECLARATION, under both chains at once. §9.5 establishes that neither split is admissible | both | **NOT SATISFIED** | P-1 + P-2 |

### 12.2 What is already satisfied

| # | Condition | Status | Basis |
|---|---|---|---|
| **S-a** | The source half has an operative declared authority | **SATISFIED** | Option B; pre-commit → `verify.sh`; verified not to consult `classify()` (F-1) |
| **S-b** | Every component the resolution reuses exists | **SATISFIED** | §8 — 7 REUSE, 2 EXTEND, 0 CREATE |
| **S-c** | The resolution creates no authority | **SATISFIED** | §7.5 |
| **S-d** | The failure is measured, not inferred | **SATISFIED** | §2.2, §4.3, §5.2 — all from source and register at this baseline |
| **S-e** | The declared class already exists and needs no amendment to exist | **SATISFIED** | GOVERNED_ANALYSIS and R-09 are both in the register at v1.1.0 |
| **S-f** | No rollback is required | **SATISFIED** | the coupled state is either coherent or `validate_rule_coverage()` refuses — which is the current state. A half-applied O-4 lands where the repository already is |

### 12.3 Sequencing, once preconditions hold

Stated for completeness. **This is not a schedule and nothing here is authorized.**

1. P-1…P-4 discharged and recorded.
2. O-4's four corrections composed as **one** mutation.
3. Pre-commit → `verify.sh` examines the source half before it becomes repository state.
4. Verification per §13, all criteria, none waived.
5. The result is evidenced. **No certificate is issued** — F-5.

### 12.4 What no precondition can supply

| Not supplied by any precondition | Why |
|---|---|
| A conformance gate for mutation classification | EX-018 does not exist; the register declares it as future work |
| Enforcement of `classify()` anywhere in `verify.sh` | No gate consumes it (§2.5). O-4 makes classification *correct*, not *enforced* |
| Classification of this determination or its predecessor | Both are untracked, so the `repository-controlled` criterion fails. Tracking requires a commit, which the constraints on both artifacts forbid |
| Certification, ratification or freeze | F-5 |

---

## 13. Closure Criteria

The conditions under which the mutation classification failure would be resolved. **None is satisfied at this baseline, and no closure is claimed.**

### 13.1 Coverage

| # | Criterion | Measurement | State |
|---|---|---|---|
| **CC-1** | `validate_rule_coverage(boundary) == ()` | direct call | **FAIL** — returns 1 problem |
| **CC-2** | 9 declared rules, 9 predicates, two-sided check **unweakened** | `len(RULE_PREDICATES)` vs declared ids, and the check's source unchanged | **FAIL** — 8 vs 9 |
| **CC-3** | `classify()` returns `ERROR` for **no** subject | `classify_all` over all tracked paths | **FAIL** — `ERROR` for every subject |

### 13.2 Reachability

| # | Criterion | Measurement | State |
|---|---|---|---|
| **CC-4** | Every declared rule matches ≥ 1 subject, **or** its emptiness is declared and intended | per-rule match census over tracked paths | **FAIL** — R-09 would match 0 |
| **CC-5** | R-09 claims the 98 measured analysis artifacts | classification census | **FAIL** — 0 |
| **CC-6** | No rule is dead code | as CC-4 | **FAIL** |

### 13.3 Disjointness

| # | Criterion | Measurement | State |
|---|---|---|---|
| **CC-7** | For every pair of rules, the predicate intersection over all subjects is ∅ | pairwise predicate evaluation, precedence ignored | **FAIL** — R-08 ∩ R-09 = 98 |
| **CC-8** | Permuting the declared rule order changes no artifact's class | classify, permute, re-classify, compare | **FAIL** — R-08/R-09 and R-07's over-claim both depend on order |
| **CC-9** | No artifact resolves to two authority chains | as CC-7, over `governed_by` | **FAIL** |

### 13.4 Single-source

| # | Criterion | Measurement | State |
|---|---|---|---|
| **CC-10** | Exactly one artifact declares the GOVERNED_ANALYSIS class and the R-09 rule | repository search for the class name as a declaration | **FAIL** — register and `mutation_class_extension.py` |
| **CC-11** | No `platform/` or `engine/` module holds mutation rule text or class ordering as a literal | source inspection | **FAIL** — 206-line rival |
| **CC-12** | No module can write the register | search for write paths to `BOUNDARY_PATH` | **FAIL** — `extend_mutation_governance_boundary()`, `dry_run=False` default |
| **CC-13** | Every test asserting R-09 or GOVERNED_ANALYSIS asserts it **against the register or `classify()`** | test inspection | **FAIL** — 9 tests assert Python literals |

### 13.5 Authority

| # | Criterion | Measurement | State |
|---|---|---|---|
| **CC-14** | Every authority named in every class's `governed_by` chain is a declared authority with an implementation in the tree | parse all 9 chains against the `authorities` list | **FAIL** — "Repository Intelligence" undeclared |
| **CC-15** | The register's own mutation authority resolves to an actor | read the `authority` field | **FAIL** — resolves to a standing (§7.2) |
| **CC-16** | The register-level invariants quantify over **artifacts**, not over class names, and grow with the register | test inspection | **FAIL** — `test_2` counts names; `test_3` uses a hardcoded 5-name `required` set |

### 13.6 Enforcement — recorded, out of scope

| # | Criterion | State | Note |
|---|---|---|---|
| **CC-17** | A gate consumes `classify()` as a verdict and fails closed on `UNRESOLVED` or `ERROR` | **FAIL** | This is **EX-018**, which the register names and which does not exist. **O-4 does not close it, and must not be presented as closing it** |

### 13.7 Closure state

| Group | Criteria | Satisfied |
|---|---|---|
| Coverage | CC-1…CC-3 | **0 of 3** |
| Reachability | CC-4…CC-6 | **0 of 3** |
| Disjointness | CC-7…CC-9 | **0 of 3** |
| Single-source | CC-10…CC-13 | **0 of 4** |
| Authority | CC-14…CC-16 | **0 of 3** |
| Enforcement | CC-17 | **0 of 1 — out of scope** |
| **Total** | **17** | **0** |

**Zero of seventeen closure criteria are satisfied. O-4 executed in full would satisfy CC-1 through CC-13 and CC-16. CC-14 and CC-15 require authority acts. CC-17 requires an instrument the register itself declares as future work.**

> **Even complete execution of the selected resolution would not close this failure. Three criteria would remain, two of them because no authority exists to close them. CLOSURE IS NOT CLAIMED.**

### 13.8 Final verdict

> **What is the permanent resolution for the mutation classification coverage failure?**

# RESOLUTION ARCHITECTURE DETERMINED · NOT RESOLVED

**The architecture is O-4: single-source convergence of the existing register and the existing classifier, applied atomically, creating no mechanism and retiring one rival.**

**It is not resolved. It is not authorized. It is not closed.**

| Statement | Status |
|---|---|
| The correct permanent resolution is determined | **YES — O-4** |
| It satisfies all six mandatory principles | **YES — §9.4, §11.2** |
| It may be executed | **NO — 4 preconditions unmet (§12.1)** |
| S-1 as previously scoped is sufficient | **NO — §1.3** |
| The failure is resolved | **NO** |
| Closure | **NOT CLAIMED** |
| This determination confers authority | **NO — NONE (DERIVED TRUTH)** |

---

## 14. Verification Record

### 14.1 Baseline captured before writing

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| Commits | 515 |
| Porcelain total | 374 |
| Tracked modified | 38 |
| Untracked | 336 |
| Target artifact | **absent at capture** |
| Predecessor determination | 759 lines · `2985924ab1…c2b5f7f87b` |
| Register | 407 lines · v1.1.0 · `a7c8171518…ca5a89ee` |
| Classifier | 507 lines · `54ecc7e2c4…dd6def3c` |
| Rival module | 206 lines · `9a742a7629…bb5db572` |
| Violation-4 tests | 381 lines · `2a99f4b7ff…4375cd3c72` |

### 14.2 Read-only measurements taken for this determination

| ID | Measurement | Surface | Write? |
|---|---|---|---|
| **N-1** | `validate_rule_coverage(boundary)` → `("rule 'R-09' is declared but no predicate implements it",)`; `RULE_PREDICATES` = 8; declared = 9; `classify()` returns `ERROR` at `:438` before rule evaluation | classifier · register | **NO** |
| **N-2** | 3,331 tracked `.md`; **458** satisfy R-08's five criteria; **98** of those also carry an R-09 analysis token → R-08 ∩ R-09 = 98; R-09 reachable = **0** under declared precedence | classifier predicates · register · `git ls-files` | **NO** |
| **N-3** | R-09 declared at precedence 9, R-08 at 8, `evaluation` = declared-order-first — contradicting `$distinction_from_authored_document`'s *"R-09 evaluates before R-08"* | register | **NO** |
| **N-4** | `mutation_class_extension.py` holds the class and rule as Python literals; diverges from the register in the analysis criterion (3 tokens + undecidable disjunct vs 9) and in `examples` (6 vs 8); internally inconsistent between its own criteria and predicate | rival module · register | **NO** |
| **N-5** | `extend_mutation_governance_boundary()` writes the register with `dry_run=False` default and bumps its version; against the current register it can only raise `ValueError` | rival module | **NO — not invoked against the register** |
| **N-6** | `GOVERNED_ANALYSIS.governed_by` names "Repository Intelligence"; the register declares 8 authorities and none is it | register | **NO** |
| **N-7** | Test census: `test_mutation_classification.py` **26 failed · 23 passed**; `test_mutation_governance_boundary.py` **9 passed**; `test_violation_4_mutation_extension.py` **9 passed** and never calls `classify()` | test modules | **NO — read-only pytest, no `--cov` write, no artifact written** |
| **N-8** | R-06 claims the register: all seven criteria True → the register is `GOVERNED_DECLARATION`. R-07 claims the classifier module → `SOURCE` | classifier predicates | **NO** |
| **N-9** | R-07's predicate returns True for `does/not/exist/untracked_probe.py`; R-01 returns False for the same path — a `SOURCE` over-claim on a non-member | classifier predicates | **NO** |
| **N-10** | R-03's implementation omits the declared disjunct *"or is a Universal ID or page-range allocation"* | classifier · register | **NO** |
| **N-11** | `test_2` asserts uniqueness of class **names**; `test_3`'s `required` is a hardcoded 5-name set excluding all three newest classes; `test_4` never parses class `governed_by` chains | boundary test module | **NO** |
| **N-12** | R-09 and GOVERNED_ANALYSIS introduced at `fb43383e` *"EXECUTION: Complete Phase 1B with certification (REQ-28, REQ-43, Violation 4)"*; rival module last touched at `bae59755` | `git log` | **NO** |

**Every defect this determination had the information to repair — the missing predicate, the 98-artifact overlap, the rival declaration, the undeclared authority, the R-03 and R-07 misalignments — was located, measured, and left exactly as found.**

### 14.3 Artifact identity

| Field | Value |
|---|---|
| Path | `UCOS-OMEGA-INFINITY-S-1-MUTATION-CLASSIFICATION-PERMANENT-RESOLUTION-DETERMINATION.md` |
| Status | Untracked — new artifact |
| Required sections | **14** |
| Verdict | **RESOLUTION ARCHITECTURE DETERMINED · NOT RESOLVED** |
| Resolution selected | **O-4 — single-source convergence** |
| Resolution authorized | **NO** |
| Closure claimed | **NO** |
| Authority | **NONE (DERIVED TRUTH)** |
| Implementation performed | **NONE** |

### 14.4 Mutation boundary

| Surface | State |
|---|---|
| Source code | **UNCHANGED** — no `.py` written |
| Registries | **UNCHANGED** — no `.json` written |
| `mutation-governance-boundary.json` | **READ ONLY** — parsed for measurement; SHA unchanged |
| `mutation_classification.py` | **READ ONLY** — `RULE_PREDICATES` still **8 entries** |
| `mutation_class_extension.py` | **READ ONLY** — not deleted, not invoked against the register |
| Test modules | **READ ONLY** — executed, not modified; no test weakened, added or removed |
| Identity | **UNCHANGED** — no mint, no serial consumed, no `id-ledger.json` write |
| Relationship data | **UNCHANGED** — no edge added, removed or retyped |
| Schemas · declarations · constitutions · law | **UNCHANGED** |
| Workflows · gates | **UNCHANGED** |
| Certifications | **UNCHANGED** — none issued, none withdrawn |
| Predecessor determination | **UNCHANGED** — 759 lines |
| Commits · tags · pushes · stash | **NONE** |

### 14.5 Verification checklist

Executed after this artifact was written. Each check is reproducible against baseline `bae59755d7e2d3566c93b89c722b68847145269a` on branch `integration/recovery-001`.

| Check | Requirement |
|---|---|
| File exists | yes |
| Section count | **14** — headings `## 1.`…`## 14.`, contiguous |
| Line count | recorded in the accompanying verification output |
| Only one new artifact | 1 new untracked entry vs baseline (374 → 375) |
| HEAD unchanged | `bae59755…` |
| Branch unchanged | `integration/recovery-001` |
| Commit count unchanged | 515 |
| Tracked modifications unchanged | 38 |
| Code unchanged | no `.py` delta; classifier and rival module SHAs unchanged |
| Registry unchanged | no `.json` delta; register SHA unchanged |
| Identity unchanged | no `id-ledger.json` write |
| Relationship data unchanged | no relationship artifact write |
| Predecessor unchanged | 759 lines, SHA unchanged |
| No commits | HEAD and count unchanged |

---

**END UCOS Ω∞ — S-1 MUTATION CLASSIFICATION PERMANENT RESOLUTION DETERMINATION**

**Verdict:** **RESOLUTION ARCHITECTURE DETERMINED · NOT RESOLVED**
**Selected architecture:** O-4 — single-source convergence · 0 mechanisms created · 1 rival retired
**Defects:** 4 in one rule (D-1 unimplemented · D-2 unreachable · D-3 duplicated · D-4 undeclared authority)
**Measured overlap:** 98 artifacts under 2 authority chains · R-09 reachable by 0
**Rules:** 9 declared · 8 implemented · 6 semantically aligned · 6 disjoint by predicate
**Options:** 4 analysed · 3 rejected · 1 selected · **0 authorized**
**Preconditions:** 4 · **0 satisfied** — all four are authority acts
**Closure criteria:** 17 · **0 satisfied** · 3 unclosable by O-4
**Predecessor verdict preserved:** NOT READY AS A PROGRAMME · SINGLE-STEP ELIGIBLE — **with S-1's scope corrected (§1.3)**
**READY:** not claimed · **RESOLVED:** not claimed · **CLOSURE:** not claimed
**Authority:** NONE (DERIVED TRUTH) — authorizes nothing, schedules nothing, certifies nothing
**Principles honoured:** Zero fixes · Zero patches · Zero shortcuts · Zero temporary solutions · Zero duplicate classifiers · Zero overlapping authorities

*This determination modified no code, configuration, registry, schema, constitution, law, identifier, relationship, requirement, ADR, phase, roadmap or certification. It implemented no predicate, deleted no module, reordered no rule, declared no authority, weakened no test, and issued no certificate. The eight-entry `RULE_PREDICATES` dictionary it measured against a nine-rule declaration remains, at the moment of writing, exactly eight entries.*
