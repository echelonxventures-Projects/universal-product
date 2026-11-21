# UCOS Ω∞ — R-09 PREDICATE IMPLEMENTATION READINESS DETERMINATION

**Option A converted into a controlled implementation assessment. The population arithmetic closes exactly — 92 + 347 = 439 — provided one implementation detail is symmetric. If it is not, 91 artifacts fall out of every class.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-R09-PREDICATE-IMPLEMENTATION-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Writes no predicate, changes no precedence, amends no declaration, executes no implementation. |
| Mode | ANALYSIS ONLY · **NO `mutation_classification.py` · NO `mutation-governance-boundary.json` · NO `RULE_PREDICATES` · NO PRECEDENCE VALUES · NO `classify()` EXECUTION · NO `register.sh` · NO REGISTRY · NO CERTIFICATION · NO IDENTITY · NO OWNERSHIP · NO COMMIT** |
| Resolution source | `UCOS-OMEGA-INFINITY-R09-PREDICATE-ARCHITECTURE-RESOLUTION-DETERMINATION.md` (654 lines) — Option A canonical, verdict `CONDITIONALLY READY` |
| Method | Read-only measurement at HEAD `bae59755`: population arithmetic over 6,188 tracked paths via `git ls-files` and pure string evaluation; blast-radius survey of every module referencing the classifier; audit of all five markdown fixtures in the existing test module. **`classify()` was not executed and the engine was not imported.** |
| New findings | **3** — the symmetric implementation conserves population exactly with **zero** new `UNRESOLVED` (§5.3); an asymmetric one orphans **91** named artifacts (§5.4); and the blast radius is **four files with no gate, engine or workflow consumer**, so certification, identity and ownership have zero coupling to mutation class (§9.3–§9.5) |
| Disclosure | The directive characterises Option A as *approved*. **No `AG-2b` decision record exists in the repository.** See §2.1. |

---

## 1. Current Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **356** lines |
| Tracked modifications | **38** |
| Untracked | **318** porcelain entries · **325** files by `git ls-files --others --exclude-standard` |
| Staged | **0** |

### 1.1 Current R-09 state

```
declared   boundary JSON  mutation_classes[8] GOVERNED_ANALYSIS · rule R-09 · precedence 9
                          six membership_criteria
implemented                NONE — RULE_PREDICATES = R-01…R-08  (:403-412)

validate_rule_coverage()   ("rule 'R-09' is declared but no predicate implements it",)
classify(any_subject)      status=ERROR      ← repository-wide, every subject
relation to R-08           R-09 ⊂ R-08, strictly, by the form of the declaration
measured                   | R-09 \ R-08 | = 0 over 6,188 tracked paths
population                 92 case-insensitive · 1 case-sensitive  (undeclared — Q-1)
```

### 1.2 `AG-2b` state

| Field | Value |
|---|---|
| Authority | **Mutation governance owner** — same party as `AG-2` and `AG-4` |
| Availability | **LOCATED, OPEN** |
| Constitutional dependency | **NONE** for Option A |
| Open sub-decisions | **5** — option confirmation · `Q-1` case sensitivity · `Q-2` filename vs path · `Q-3` extension-module registration path · `Q-4` Class 8's false ordering note |
| Referred separately | `Q-5` — the 92-subject `EX-017` migration; may reach `AG-4` |
| Decision record in repository | **NONE LOCATED** |

### 1.3 Wave 0 / Wave 1 state

| | Status |
|---|---|
| Wave 0 | **6 of 7 READY** — `W0-1a`, `W0-2`…`W0-6`. `W0-1` IMPLEMENTABLE, NOT ACCEPTABLE |
| Wave 1 | **0 of 5 unconditionally acceptable · `W1-1` CONDITIONALLY READY** |
| `W1-2`, `W1-4` | NOT READY — `W0-6`/`AG-2` and `W0-5`/read-only mode |
| `W1-3` | READY at specification scope |
| `W1-5` | Degraded via edge `E-04`; exposure re-sized to 92 tracked artifacts |
| Readiness verdict | **`NOT READY`** · ceiling `CERTIFIED-PROVISIONAL` · `PROVISIONAL` under `VAC-01` |

---

## 2. Approved Resolution

### 2.1 Standing of the approval — disclosed, not assumed

The directive instructs this determination to convert *"the approved Option A architectural resolution."* The measured position is narrower:

| What exists | What does not |
|---|---|
| Option A **recommended** as canonical by the architecture determination §5.2, on four grounds | **No `AG-2b` decision record.** The architecture determination recorded `AG-2b` as `LOCATED, OPEN` and stated *"this determination decides none of them"* |
| Five sub-questions `Q-1`…`Q-5` enumerated | **None of the five answered** |
| The deciding authority identified and available | **No recorded exercise of that authority** |

**Disposition:** this determination plans against Option A as directed, and records that the authorising decision is **condition 1** of §10's verdict. Treating a recommendation as a discharged approval is the `RC-9` pattern — *certification records that a claim was made, never that it was measured* — and this artifact does not repeat it.

### 2.2 The Option A decision

> **R-08 is narrowed by an explicit `not-analysis-artifact` criterion, making R-08 and R-09 disjoint at the predicate level. R-09's declaration is unchanged. Precedence is unchanged.**

### 2.3 Why Option C is prohibited

`classification_rules.properties.unique`, verbatim:

> *"Exactly one class. The predicates are written to be disjoint; **the ordering is a tie-break of last resort and never a substitute for disjointness**, because two classes would be two authorities and `UCKP-ART-18` refuses that."*

Reordering R-09 ahead of R-08 uses ordering to resolve an overlap. That is the substitution the sentence names and refuses. Three further consequences:

| # | Consequence of C |
|---|---|
| 1 | `invariants[7]` — *"No artifact resolves to more than one mutation class. Failure: authority ambiguity"* — remains violated. 92 subjects still satisfy two predicates; only the `return` statement hides it |
| 2 | Every future specific class depends on **position** rather than **definition**, and `unique` becomes decorative |
| 3 | `CA-1` declares precedence change out of scope, so C is no more in-scope than A |

**C is smaller and wrong. It is refused on the register's own words, not on preference.**

### 2.4 Why D and E introduce unnecessary architectural complexity

| Option | Complexity introduced | Why unnecessary here |
|---|---|---|
| **D** — explicit `excludes`/`overrides` field | A **second resolution mechanism** beside precedence. Requires changing `classify()`'s loop, which the code comment at `:248` states *"never branches on rule identity"* — an override table forces exactly that branch | It **declares** the overlap rather than removing it. `invariants[7]` stays violated at the predicate level. Two mechanisms deciding one subject's class is the shape `UCKP-ART-18` refuses — the concern `unique` already articulates. A solves the same problem with one conjunct |
| **E** — facet / sub-class layer | A new architectural surface across all nine classes; every declared property must be restated over two layers (does `unique` mean one class, one facet, or one leaf?); every consumer of `ClassificationResult.mutation_class` changes | Class 8's `governed_by` differs from Class 7's, so **nesting the classes nests two authority chains** — `invariants[1]`'s *"No mutation class is claimed by two authorities as primary"* becomes ambiguous. It requires amending the declared properties themselves, which plausibly engages `UCOS-CAA-001` and through it the **vacant `T1`**. It solves a general problem the register does not have — **one** overlapping pair in nine rules |

**The decisive asymmetry: A keeps the decision with a located owner. D and E risk routing a nine-rule predicate defect into `AG-9`, which is `VACANT` and unreachable.**

### 2.5 Constitutional alignment

| Requirement | Source | Option A |
|---|---|---|
| `unique` — disjoint predicates, ordering never the mechanism | `properties.unique` | ✅ **SATISFIED** — overlap eliminated; ordering becomes irrelevant to the outcome |
| `total` — every subject resolves, never to nothing or a default | `properties.total` | ✅ **SATISFIED** — §5.3 measures zero new `UNRESOLVED` under symmetric implementation |
| `deterministic` — pure function, no clock, environment or caller ordering | `properties.deterministic` | ✅ **SATISFIED** — a filename test reads neither |
| `repository_evaluable` — decidable from tracked state alone | `properties.repository_evaluable` | ✅ **SATISFIED** — all six criteria are path, registry membership, or declared field |
| `invariants[6]` — every tracked artifact resolves to exactly one class | `invariants` | ✅ **SATISFIED** |
| `invariants[7]` — no artifact resolves to more than one class | `invariants` | ✅ **SATISFIED at the predicate level** — the only option that does |
| `invariants[1]` — no class doubly claimed by two authorities | `invariants` | ✅ **SATISFIED** — each subject reaches exactly one `governed_by` chain |
| `UCKP-ART-10` — execution never owns knowledge | `constitutional_superior.effect` | ✅ Amends which class exists over which subject, not knowledge |
| Extension pattern | `R-04`/`R-08`, `R-06`/`R-07` precedent | ✅ **Completes the register's own pattern** — see §4.5 |

**No constitutional authority act is required.** The change amends a criterion list inside an `EXECUTION`-role register held subordinate under `UCKP-LAW-0001`. It creates no authority, changes no tier, ratifies nothing.

### 2.6 The two required statements

> **R-09 remains a separate governed class.** `GOVERNED_ANALYSIS` keeps its own identity, its own `governed_by` chain, its own six declared `membership_criteria`, its own rule `R-09` at precedence 9, and its own declaration in `mutation_classes[8]`. Option A neither merges it into Class 7 nor subordinates it as a facet. Nothing in R-09's declaration changes.

> **R-08 becomes mutually exclusive.** `AUTHORED_DOCUMENT` gains a sixth criterion, `not-analysis-artifact`, so that `R-08 ∩ R-09 = ∅` holds by construction rather than by evaluation order. R-08's intent is preserved and narrowed to its complement: general authored governance prose that is not an analysis work product.

---

## 3. Implementation Scope Definition

### 3.1 The exact allowed change

```
R-08 PREDICATE REFINEMENT — the whole of the permitted change

1. mutation_classification.py
   a. NEW  _analysis_artifact(path: str) -> bool
             one shared helper; the single source of the token test        ← MANDATORY, §5.4
   b. EDIT authored_document_checks()  5 keys → 6
             + "not-analysis-artifact": not _analysis_artifact(path)
   c. NEW  governed_analysis_checks(path, repo) -> dict[str, bool]
             the six declared criteria, individually, mirroring Classes 6 and 7
             "analysis-artifact": _analysis_artifact(path)                 ← same helper
   d. NEW  _r09_governed_analysis(subject, repo, boundary) -> bool
             if subject.kind != PATH: return False
             return all(governed_analysis_checks(...).values())
   e. EDIT RULE_PREDICATES  += {"R-09": _r09_governed_analysis}
             ▓ addition of the declared R-09 entry only — no other entry altered ▓

2. mutation-governance-boundary.json
   f. EDIT mutation_classes[7].membership_criteria  5 → 6
             + "not-analysis-artifact — filename carries none of the nine analysis tokens"
             ▓ required so the register and the code remain two-sided ▓
             ▓ mutation_classes[8] and classification_rules ARE NOT TOUCHED ▓

3. platform/tests/test_mutation_classification.py
   g. ADD  R-09 positive, negative, and pairwise-exclusivity tests
   h. ADD  the coverage regression guard
```

### 3.2 Preservation requirements

| Must be preserved | How verified |
|---|---|
| **Existing R-08 intent** | R-08 remains *"general governance prose (ADRs, constitutions, policy documents)"*. Only analysis work products leave. Measured: **347** of 439 stay — §5.3 |
| **`R-01…R-07` behaviour** | Not one line of those seven predicates is touched. Verified by diff: the change touches `authored_document_checks`, `RULE_PREDICATES`, and two new functions |
| **R-09's declaration** | `mutation_classes[8]` byte-identical. All six criteria as declared. Rule `R-09` unchanged |
| **Precedence values** | `R-01…R-09` remain `1…9`. The rule list order is unchanged |
| **Two-sidedness** | `validate_rule_coverage()` returns `()` in both directions |
| **Per-criterion attributability** | Both checks dicts keep the individual-key shape so a refusal names which criterion failed |

### 3.3 IN SCOPE

| # | Item |
|---|---|
| 1 | Predicate refinement — the shared helper, R-08's sixth criterion, R-09's checks dict and predicate, the `RULE_PREDICATES` entry |
| 2 | The `mutation_classes[7].membership_criteria` declaration amendment — 5 → 6, required for two-sidedness |
| 3 | Test updates — R-09 positive, R-09 negative, pairwise exclusivity, coverage guard, permutation invariance |
| 4 | Validation updates — `test_mutation_governance_boundary.py` disjointness assertion |
| 5 | `Q-3` disposition of `mutation_class_extension.py` — invoked, or declared vestigial |

### 3.4 OUT OF SCOPE

| # | Item | Why |
|---|---|---|
| 1 | **Precedence changes** | Option C refused; `CA-1` forbids; `unique` forbids ordering as the mechanism |
| 2 | **New classes** | Nine classes remain nine. A tenth rule is explicitly out of `CA-1`'s scope |
| 3 | **New authorities** | Neither class's `governed_by` chain changes. No authority is created, vested or reassigned |
| 4 | **Identity changes** | No ledger, no `by_path`/`by_object`/`by_observation`, no `category_seq`, no `page_cursor` |
| 5 | **Registry migration** | The 92-subject reclassification is `EX-017`, a distinct act. `EX-016` evaluation is what this scope reaches |
| 6 | Changes to `R-01…R-07` | Untouched |
| 7 | `classify()` loop changes | Options D and E only |
| 8 | Ownership, certification | Zero coupling — §9.3–§9.5 |
| 9 | The `EX-018` conformance gate | Required, and separately scoped |

---

## 4. Predicate Design

### 4.1 Before and after

```
BEFORE          R-08 = markdown ∧ authored ∧ tracked ∧ ¬generated ∧ authority
                R-09 = markdown ∧ authored ∧ tracked ∧ ¬generated ∧ authority ∧ analysis

                R-09 ⊂ R-08          strictly, and R-08 evaluates first
                | R-08 | = 439   | R-09 | = 92   | R-08 ∩ R-09 | = 92

AFTER           R-08 = markdown ∧ authored ∧ tracked ∧ ¬generated ∧ authority ∧ ¬analysis
                R-09 = markdown ∧ authored ∧ tracked ∧ ¬generated ∧ authority ∧  analysis

                R-08 ∩ R-09 = ∅       the two differ on exactly one literal, negated
                | R-08 | = 347   | R-09 | = 92   | R-08 ∩ R-09 | = 0
                347 + 92 = 439        population conserved exactly
```

The two predicates become a **partition of the same five-criterion base set, split on one boolean.** That is the strongest available form of disjointness: not merely empty intersection at this commit, but empty by propositional form at every commit.

### 4.2 R-08 membership rule — after

| Criterion | Test |
|---|---|
| markdown | `path.endswith(".md")` |
| authored | `path not in repo.producer_homes` |
| repository-controlled | `path in repo.tracked` |
| non-generated | `path not in repo.generated` |
| self-declared-authority | `bool(authored_document_owner(path, repo))` |
| **not-analysis-artifact** | **`not _analysis_artifact(path)`** ← the only addition |

### 4.3 R-09 membership rule — unchanged from its declaration

| Criterion | Test |
|---|---|
| markdown | `path.endswith(".md")` |
| authored | `path not in repo.producer_homes` |
| repository-controlled | `path in repo.tracked` |
| non-generated | `path not in repo.generated` |
| self-declared-authority | `bool(authored_document_owner(path, repo))` |
| **analysis-artifact** | **`_analysis_artifact(path)`** ← same helper, un-negated |

### 4.4 The exclusion condition

```
_analysis_artifact(path) — ONE definition, TWO call sites, negated in exactly one

  tokens = (determination, analysis, assessment, execution,
            matrix, readiness, admission, blocker, gap)

  ▓ Q-1 UNDECIDED — case sensitivity                  92 subjects vs 1 ▓
  ▓ Q-2 UNDECIDED — filename vs full path                              ▓

  MANDATORY INVARIANT, independent of Q-1 and Q-2:
      R-08's exclusion and R-09's inclusion MUST call the same helper.
      Any divergence creates an UNRESOLVED population — measured at 91. §5.4
```

### 4.5 Why this is the register's own pattern, not a new one

| Pair | Disjointness mechanism | Form |
|---|---|---|
| `R-04` / `R-08` | R-08 carries **`non-generated`** | negative criterion naming the other class's set |
| `R-06` / `R-07` | R-06 carries **`non-executable`** | negative criterion naming the other class's set |
| `R-06` / `R-08` | R-08's `markdown` vs R-06's `declaration-bearing` | structural |
| `R-01` / all tracked rules | R-01 returns `False` when `path in repo.tracked` | negative criterion |
| **`R-08` / `R-09`** | **none today** | ← **the sole exception in nine rules** |

The existing test suite already encodes this discipline. `test_class_7_a_json_declaration_is_never_also_an_authored_document` carries the docstring: *"**Structural exclusivity:** R-06 (JSON declaration) precedes R-08, and a JSON path never satisfies the markdown criterion — **the two classes cannot both claim one subject.**"*

**That test is the template. Option A adds its R-08/R-09 counterpart, which is the only pair currently missing one.**

### 4.6 Edge cases

| # | Case | Before | After | Assessment |
|---|---|---|---|---|
| E-1 | Analysis-named `.md`, **no** Authority field | `UNRESOLVED` (fails R-08 on authority) | `UNRESOLVED` (fails R-08 on two criteria, R-09 on authority) | ✅ **Unchanged.** **448** tracked `.md` carry a token and already fail R-08. Option A does not worsen a pre-existing population |
| E-2 | Analysis-named `.md`, **untracked** | `UNRESOLVED` | `UNRESOLVED` | ✅ Unchanged. All **325** untracked files fail `repository-controlled` — including the 228 Group B pages |
| E-3 | Analysis-named `.md`, **generated** | `GENERATED_ARTIFACT` (R-04, precedence 4) | `GENERATED_ARTIFACT` | ✅ Unchanged — R-04 fires first |
| E-4 | Non-analysis `.md` with authority | `AUTHORED_DOCUMENT` | `AUTHORED_DOCUMENT` | ✅ **347** subjects unchanged |
| E-5 | Analysis `.md` with authority, tracked, non-generated | `AUTHORED_DOCUMENT` ← wrong class | `GOVERNED_ANALYSIS` | ✅ **The 92 subjects. The defect corrected** |
| E-6 | `.json` declaration | `GOVERNED_DECLARATION` (R-06) | unchanged | ✅ R-06 precedes; `.json` fails `markdown` |
| E-7 | `.py` / `.sh` | `SOURCE` (R-07) | unchanged | ✅ Fails `markdown` |
| E-8 | `OBJECT` subject | `CONSTITUTIONAL_TRUTH` (R-05) | unchanged | ✅ Both predicates return `False` on non-`PATH` |
| E-9 | `.gitignore`, `exclusion-register.json` | `EXCLUSION` (R-02) | unchanged | ✅ |
| E-10 | `id-ledger.json`, `artifacts.json` | `CORPUS_REGISTRATION` (R-03) | unchanged | ✅ |
| **E-11** | **Token match asymmetric between the two predicates** | — | **91 subjects → `UNRESOLVED`** | ❌ **THE ONE FAILURE MODE.** Mitigated only by the shared helper — §5.4 |
| E-12 | Path with a token in a **directory** name, not the filename | R-08 | depends on `Q-2` | ⚠️ Undecided. `Q-2` must settle filename-vs-path before either predicate is written |
| E-13 | `adr/0002-aeos-phase-1-architectural-determination.md` — the existing fixture that carries a token | `UNRESOLVED` (asserted by an existing test) | `UNRESOLVED` | ✅ **The existing assertion survives.** `checks["self-declared-authority"] is False` still holds with six keys |

---

## 5. Validation Model

### 5.1 What must be proven before acceptance

| # | Proposition | Threshold |
|---|---|---|
| P-1 | All existing classes still classify correctly | `R-01`…`R-07` outcomes byte-identical for every tracked path |
| P-2 | `\| R-08 ∩ R-09 \| = 0` | Exactly zero, over all 6,188 tracked paths |
| P-3 | R-09 is reachable | `≥ 1` subject returns `GOVERNED_ANALYSIS` / `R-09`; the count matches `Q-1`'s implication exactly |
| P-4 | No new `UNRESOLVED` population | The `UNRESOLVED` set after ⊆ the `UNRESOLVED` set before. **Set containment, not count comparison** |
| P-5 | No authority ambiguity | At most one of nine predicates returns `True` for every tracked path |

### 5.2 Measurement method

```
M-1  BASELINE, before any edit
       classify all 3,228 tracked .md and all 6,188 tracked paths
       record (path → mutation_class, rule_id, status) → digest
       ▓ blocked today: classify() returns ERROR for every subject ▓
       ▓ so the baseline is computed from PREDICATE EVALUATION, not classify() ▓

M-2  PREDICATE-LEVEL EVALUATION, the method used in this determination
       enumerate paths via `git ls-files`
       evaluate each of the nine criteria sets in isolation
       build nine sets; compute all 36 pairwise intersections
       → this is how §5.3's figures were obtained WITHOUT invoking the engine

M-3  AFTER, same computation
       digest-compare against M-1 for R-01…R-07
       assert | R-08 ∩ R-09 | == 0
       assert UNRESOLVED_after ⊆ UNRESOLVED_before
       assert | R-08_after | + | R-09_after | == | R-08_before |     ← conservation

M-4  PERMUTATION INVARIANCE
       shuffle the nine declared rules; reclassify all 6,188 paths
       assert results identical under every permutation
       → the operational proof that ordering is no longer the mechanism

M-5  DETERMINISM
       two runs, digest-identical

M-6  PURITY
       porcelain byte-identical across a classification run, mutation-tested
```

### 5.3 The symmetric case — measured, and it closes exactly

Computed at HEAD by method `M-2`:

```
tracked files                                       6,188
tracked .md                                         3,228
generated-artifact-registry canonical_path             347
tracked .md carrying a token (case-insensitive)        540

                          BEFORE          AFTER (symmetric, case-insensitive)
R-08                         439                347
R-09                           0 (no predicate)  92
R-08 ∩ R-09                   92                  0
                             ───                ───
conservation check     439  ==  347 + 92  =  439        ✅ EXACT

NEW UNRESOLVED               —                    0     ✅
```

**The arithmetic closes with no remainder.** Every subject leaving R-08 enters R-09; none falls through. `P-4` holds by conservation, not by inspection.

Under a case-sensitive reading the same conservation holds at different magnitudes: `R-08` 439 → **438**, `R-09` → **1**, `438 + 1 = 439`. **Either `Q-1` answer is internally consistent. Only a mixture is not.**

*Note:* `producer_homes` could not be resolved without instantiating `Repository`, so `authored` was treated as satisfied. 439 is an **upper bound** and the true figure is ≤ 439. The same treatment applied to both sets, so conservation and disjointness are unaffected.

### 5.4 The asymmetric case — the one failure mode, quantified

If R-08 excludes case-insensitively while R-09 matches case-sensitively:

```
R-08_after  =  439 − 92  =  347        (excluded all 92 token-bearing)
R-09_after  =                  1        (matched only the case-sensitive one)
                            ─────
accounted   =  347 + 1  =  348
missing     =  439 − 348  =  91        ──▶ NEWLY UNRESOLVED

named samples:
  UCOS-MASTER-EXECUTION-STATUS-REGISTRY.md
  61-ADMISSION-BLOCKER-REGISTER.md
  CMG-000012-IDENTITY-AND-OWNERSHIP-DETERMINATION.md
```

**91 artifacts would hold no mutation class at all** — a `total`-property violation, and an *"unclassified artifact"* failure under `invariants[6]`. Each would become an artifact nobody has assigned an authority to.

**This is the entire risk of Option A, and it is fully mitigated by one structural constraint: R-08's exclusion and R-09's inclusion must call the same helper function.** With a shared helper the failure is unreachable, because the negation of a predicate and the predicate itself cannot disagree. Requirement `1a` in §3.1 is therefore not a style preference — it is the mitigation.

---

## 6. Test Strategy

**Tests are specified here and not executed. No test run occurred.**

### 6.1 Predicate unit tests

| ID | Test |
|---|---|
| T-1 | `governed_analysis_checks` returns six keys, each individually asserted |
| T-2 | R-09 **positive**: a tracked, non-generated, authority-declaring analysis `.md` → `all(...) is True` |
| T-3 | R-09 **negative**: a non-analysis `.md` → `False`, with `checks["analysis-artifact"] is False` |
| T-4 | R-09 rejects a non-`PATH` subject |
| T-5 | Each of the six criteria fails **in isolation** — six cases, one criterion falsified each |
| T-6 | `authored_document_checks` returns six keys including `not-analysis-artifact` |
| T-7 | The existing five R-08 assertions still hold. **Audited: of five markdown fixtures, only `DETERMINATION_NO_AUTHORITY` carries a token, and its assertion is `status == UNRESOLVED`, which is unchanged. `ADR_DECIDERS`, `CONSTITUTION_AUTHORITY`, `OMEGA_AUTHORED`, `OMEGA_NO_AUTHORITY` carry none.** No existing assertion changes class |

### 6.2 Overlap tests

| ID | Test |
|---|---|
| T-8 | `test_class_7_and_class_8_never_both_claim_one_subject` — the counterpart of the existing `test_class_7_a_json_declaration_is_never_also_an_authored_document` |
| T-9 | **Exhaustive pairwise disjointness**: for every tracked path, at most one of nine predicates returns `True`. All 36 pairs. **The test that would have caught this defect and does not exist** |
| T-10 | `_analysis_artifact` is the sole definition of the token test — asserted by call-site inspection or by a shared-constant identity check |
| T-11 | Property test: for any path, `authored_document_checks[...]["not-analysis-artifact"] != governed_analysis_checks[...]["analysis-artifact"]` — **the anti-asymmetry guard for §5.4** |

### 6.3 Regression tests

| ID | Test |
|---|---|
| T-12 | `set(RULE_PREDICATES) == {declared rule ids}` — a future declared-but-unimplemented rule fails at test time |
| T-13 | `validate_rule_coverage(boundary) == ()` |
| T-14 | **Permutation invariance** (`M-4`) — classification identical under every ordering of the nine rules |
| T-15 | Determinism — two runs digest-identical |
| T-16 | Purity — zero mutations during classification, mutation-tested |
| T-17 | `test_mutation_governance_boundary.py` still asserts every class governed, none doubly claimed, every named implementation present |

### 6.4 Classification coverage tests

| ID | Test |
|---|---|
| T-18 | A sample spanning **all nine** classes returns `CLASSIFIED` with the expected `rule_id` |
| T-19 | `classify()` never returns `ERROR` for any tracked path |
| T-20 | Unknown input → `UNRESOLVED`, never a permissive default |
| T-21 | Missing `Authority` falls through — no fabrication |

### 6.5 Repository-wide validation

| ID | Test |
|---|---|
| T-22 | All 6,188 tracked paths classified; before/after diff enumerated |
| T-23 | `\| R-08 \| == 347` and `\| R-09 \| == 92` under case-insensitive `Q-1`; **or** `438` / `1` under case-sensitive. The figure must match `Q-1`'s answer exactly, not approximately |
| T-24 | Conservation: `\| R-08_after \| + \| R-09_after \| == \| R-08_before \|` |
| T-25 | `UNRESOLVED_after ⊆ UNRESOLVED_before` — **set containment** |
| T-26 | All 325 untracked paths still `UNRESOLVED` |

---

## 7. Authority Analysis

### 7.1 Decision authority — mutation governance owner

| Decision | Status |
|---|---|
| Confirm Option A | **LOCATED, OPEN** — `AG-2b`; no record exists |
| `Q-1` case sensitivity | **LOCATED, OPEN** — decides 92 vs 1 |
| `Q-2` filename vs path | **LOCATED, OPEN** — edge case `E-12` |
| `Q-3` extension-module registration path | **LOCATED, OPEN** — decides *where* the code lands |
| `Q-4` correct Class 8's false ordering note | **LOCATED, OPEN** |
| Amend `mutation_classes[7].membership_criteria` 5 → 6 | **LOCATED** — boundary register owner under `UCKP-LAW-0001` |
| Amend `CA-1`'s out-of-scope list to admit narrowing R-08 | **LOCATED** — via `AG-2b` |

### 7.2 Implementation authority — engineering owner

| Item | Status |
|---|---|
| Write the shared helper, both checks dicts, the predicate, the `RULE_PREDICATES` entry | **`AG-1` AVAILABLE** — Repository Intelligence, read from the register's `governed_by` chain, **not assigned** |
| Constraint | May implement **only** criteria the register declares. May not decide `Q-1` or `Q-2` — those define what the criterion *is* |
| Caveat | `P0-DECLARATION-001`: `platform/repository_intelligence` *"is not a governed package… falls outside the scope of UFC-14, UFC-15 and UFC-16 entirely."* The code plane has no standing to originate a declaration change |

### 7.3 Validation authority — verification owner

| Item | Status |
|---|---|
| Accept `T-1`…`T-26` as sufficient | **AVAILABLE** |
| Register an `EX-018`-style gate running `classify_all` on changed paths | **AVAILABLE, but gated on `AG-2`** — a new gate must declare `OBSERVE`/`TRANSACT`, which is the open `S-1` decision. **`RC-4` reaches into this scope** |
| Purity constraint | Any validation run must be demonstrably read-only. Porcelain byte-compared, not asserted |

### 7.4 Certification impact — certification owner

| Item | Status |
|---|---|
| Does Option A invalidate a standing certification? | **NO — measured.** No certification artifact references mutation class. §9.5 |
| Does it affect the 16-axis instrumentation (`CA-9`-E / `W1-5`)? | **Indirectly.** Edge `E-04` requires a certification act to be classifiable. Option A makes 92 analysis artifacts classifiable as `GOVERNED_ANALYSIS` — which **improves** `W1-5`'s basis |
| `AG-7` exposure | **None from this change.** `AG-7` is acceptance that a standing certification loses its basis; Option A removes no basis |

### 7.5 Is constitutional authority required?

> **NO — for Option A.**

| Ground | Evidence |
|---|---|
| The register is `EXECUTION` role, `PROJECTION` relation, subordinate under `UCKP-LAW-0001` | `constitutional_superior` |
| It *"declares the boundary; it does not create a new authority and governs nothing itself"* | `authority` field |
| `UCKP-ART-10` — execution *"owns which mutation classes exist and which authority disposes of each"* | `constitutional_superior.effect` |
| Option A amends a criterion list. It creates no authority, changes no tier, ratifies nothing, freezes nothing | §3.1 |
| No declared **property** or **invariant** is amended — all nine are satisfied, several for the first time | §2.5 |

**Contrast, and it is the reason Option A was recommended:** Option E would amend the declared properties and make `invariants[1]` ambiguous under layered authority chains, plausibly engaging `UCOS-CAA-001` and through it **`T1`, which is `VACANT`**. Option D might too. **A is the resolution that does not touch the vacant tier.**

---

## 8. Wave Impact Analysis

### 8.1 Wave 0

| Action | Before | After | Note |
|---|---|---|---|
| `W0-1a` `S-1` package | READY | **READY** | §7.3 adds a reason: the `EX-018` gate needs `S-1` |
| `W0-2`…`W0-5` | READY | **READY** | Untouched |
| `W0-6` denominator | READY | **READY** | Untouched |
| `W0-1` R-09 predicate | IMPLEMENTABLE, NOT ACCEPTABLE | **IMPLEMENTABLE, NOT ACCEPTABLE — design complete, one mitigation identified, five decisions outstanding** | Status unchanged; **cost reduced again** |
| **Wave 0 total** | 6 of 7 READY | **6 of 7 READY** | **Unchanged** |

`W0-1` retains its status because `AG-2b` remains unrecorded. What changed is the residual work: the predicate is designed, the population arithmetic is closed, the single failure mode is quantified at 91 subjects and mitigated by one structural constraint, and the test set is enumerated at 26 tests.

### 8.2 Wave 1 — `W1-1`

| Field | Before | After |
|---|---|---|
| Status | CONDITIONALLY READY | **CONDITIONALLY READY** |
| Conditions | 7, one partial | **7, one partial — unchanged in count, fully specified in content** |
| Design | recommended option | **complete**: shared helper, six-criterion R-08, unchanged R-09, 26 tests, 6 measurement methods |
| Population risk | unquantified | **quantified: 0 new `UNRESOLVED` symmetric; 91 asymmetric** |
| Blast radius | unknown | **measured: 4 files, no gate/engine/workflow consumer** |
| Existing-test risk | unknown | **measured: 0 of 5 fixtures change class** |

**`W1-1` cannot advance past `CONDITIONALLY READY` by further analysis. Every remaining condition is a decision.**

### 8.3 Wave 2 — downstream dependency impact

| Edge | Dependency | Impact |
|---|---|---|
| `E-02` `RC-1 → RC-2` | `CA-4` `A(C)` requires class resolution | ✅ Option A makes all nine classes resolvable, so `A(C)` can be drafted **total over nine classes**. `W0-4` benefits |
| `E-03` `RC-1 → RC-8` | A governed assignment must be classifiable | ✅ 92 analysis artifacts become classifiable. `CA-8`-E's partition gains a resolvable class for its analysis subjects |
| `E-04` `RC-1 → RC-9` | A certification act must be classifiable | ✅ Improves `W1-5`'s basis |
| `E-05` `RC-4 → RC-9` | Cross-process evidence must replace single-process | ⬜ Unaffected — `AG-2` |
| `CA-3`, `CA-4` | `AG-3`, `AG-4` | ⬜ **Unaffected. Wave 2 remains BLOCKED.** Option A discharges neither |

**Wave 2's blockers are untouched.** Option A improves the *quality* of three Wave 1 outputs feeding Wave 2 and moves nothing across the Wave 1 → Wave 2 boundary.

### 8.4 Critical path — updated

```
RC-4 ──▶ RC-3 ──▶ {RC-5, RC-7} ──▶ ARB ──▶ READY
          ▲
          └── AG-3 NOT LOCATED — still binding at node 2 of 5

RC-1 ──▶ {RC-2, RC-8, RC-9} ──▶ …        ← parallel branch; AG-2b sits here
```

**Unchanged.** `RC-1` and `AG-2b` are not on the critical path. Resolving `AG-2b` does not shorten the path to `READY`; leaving it open does not lengthen it.

**What `AG-2b` does gate:** `RC-1` has the highest transitive fan-out in the graph, reaching 5 of 12 nodes. `AG-2b` therefore gates three downstream actions (`CA-4`, `CA-8`, `CA-9`) while gating nothing on the critical path — **high-leverage and non-urgent**, a combination that should be neither escalated as a crisis nor deferred as trivial.

---

## 9. Risk Analysis

### 9.1 Risk — changing R-08's scope

| Field | Assessment |
|---|---|
| Impact | R-08's population falls **439 → 347** (case-insensitive) or **439 → 438** (case-sensitive) |
| Likelihood of harm | **LOW.** Conservation is exact — every departing subject enters R-09 |
| Worst case | **The §5.4 asymmetry: 91 artifacts with no class.** A `total` violation and an `invariants[6]` *"unclassified artifact"* failure |
| Mitigation | **One shared `_analysis_artifact` helper** (§3.1 `1a`), plus test `T-11` asserting the two criteria are exact negations, plus `T-25` set containment |
| Residual | **NONE if the helper is shared.** The negation of a predicate cannot disagree with the predicate |
| Owner | Mutation governance owner (`Q-1`, `Q-2`) · engineering owner (helper structure) |

### 9.2 Risk — existing artifacts changing class

| Field | Assessment |
|---|---|
| Impact | **92 tracked artifacts** move Class 7 → Class 8, changing which authority may mutate them |
| Blast radius | **Four files reference the classifier**: `mutation_classification.py`, `mutation_class_extension.py`, `test_mutation_classification.py`, `test_violation_4_mutation_extension.py`. **No gate, no workflow, no engine, no `verify.sh` stage, no `Makefile` target consumes mutation class.** *(`test_universal_measurement.py`'s `classify_all` is the truth-policy method, a different function — not a consumer.)* |
| Existing-test exposure | **Zero.** Of five markdown fixtures, only `DETERMINATION_NO_AUTHORITY` carries a token, and its assertion is `UNRESOLVED`, unchanged under A |
| Mitigation | The reclassification is `EX-017`, a **distinct act** from `EX-016` evaluation, by the register's own statement. Enumerate the 92 and record their authorisation, or defer explicitly |
| Residual | **The `Q-5` authorisation.** Owner-parameterised `governed_by` values are the `RC-2` defect; `Q-5` may reach `AG-4` |
| Owner | Class 7 and Class 8 authority chains |

### 9.3 Risk — certification impact

| Field | Assessment |
|---|---|
| Impact | **NONE MEASURED.** No certification artifact references mutation class. `07-CERTIFICATION.json`, `00-BOOK/DATA/certification.json` and the `UNAF-001` freeze record are untouched by any class change |
| Indirect effect | **Positive.** Edge `E-04` requires a certification act to be classifiable; Option A makes 92 analysis artifacts classifiable, improving `W1-5`'s basis |
| `AG-7` exposure | **None.** `AG-7` is acceptance that a standing certification loses its basis. Option A removes no basis |
| Residual | Zero |

### 9.4 Risk — identity impact

| Field | Assessment |
|---|---|
| Impact | **NONE. Structurally impossible.** Mutation classification reads `repo.tracked`, `repo.generated`, `repo.producer_homes` and file text. It writes nothing and touches no ledger |
| Verified | `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys — unchanged, and unreachable from this change |
| Coupling to `RC-3` | **None.** No `00-BOOK/DATA/` file is read or written |
| Residual | Zero, **provided** the validation runs are demonstrably read-only — `RC-4`'s hazard applies to the *measurement*, not the change |

### 9.5 Risk — ownership impact

| Field | Assessment |
|---|---|
| Impact | **NONE.** `ucos-ownership-declarations.json` `assignments` stays `{}`. Mutation class is *who may mutate*; ownership is *who owns*. Class 8 states this explicitly: *"Class 8 defines WHO MAY MUTATE a governed analysis artifact and nothing else. It grants no certification authority, no ratification authority and no freeze authority"* |
| Indirect effect | Edge `E-03` — `CA-8`-E's partition gains a resolvable class for analysis subjects. **Classification is not assignment** |
| Fabrication risk | **Zero.** No assignment is written; `OwnershipFabricationError` remains the correct behaviour |
| Residual | Zero |

### 9.6 Rollback boundary

```
SCOPE OF ROLLBACK — three files, none governed

  platform/repository_intelligence/mutation_classification.py    tracked, CLEAN at HEAD
  platform/tests/test_mutation_classification.py                 tracked, MODIFIED +3/−3
  00-BOOK/DATA/mutation-governance-boundary.json                 tracked, MODIFIED

METHOD — pre-save and restore, NOT git checkout
  1  Before the change, copy all three working-tree files out of tree; record sha256
  2  Rollback = restore the saved copies byte-for-byte
  3  Verify sha256 equality
  4  ▓ NEVER `git checkout --` on these paths ▓
       two of the three carry PRE-EXISTING uncommitted diffs this scope does not own
  5  ▓ NEVER git stash · git clean · git reset · git restore --staged ▓
       git clean would delete the 228 untracked registrations irreversibly, and
       category_seq does not roll back, so re-minting issues DIFFERENT identifiers

BOUNDARY PROPERTIES
  ✅ total and reversible — three source files, no governed surface
  ✅ crosses no prohibited surface — no ledger, no certification, no ownership, no identity
  ✅ independent of AG-3 — no 00-BOOK/DATA/ ledger file is involved
  ✅ needs no transaction boundary — no shared JSON counter object is written
  ⚠️ mutation-governance-boundary.json is registry-ADJACENT: it lives in 00-BOOK/DATA/
      but is NOT one of the seven ledgers and is NOT a corpus register under R-03
      (R-03 covers id-ledger.json and artifacts.json only). Rollback is a file restore

PRESERVED THROUGH ROLLBACK — AIF-L17: a correction is a new event, never a deletion
  the pre-action baseline record · the full diff of the reverted change ·
  every gate result including the failures that triggered rollback ·
  the trigger and detecting gate, timestamped · the post-rollback sha256 set

PROHIBITED — there is NO rollback for an identity mutation. RC-7: no git operation
  reverts an arbitration failure without discarding the 192 identities it was performed
  over. This is why no action in this scope may write identity.
```

**The rollback boundary is clean, and this is the strongest practical argument for `W0-1` proceeding ahead of everything else in the programme once `AG-2b` closes: it is the only substantive change available whose reversal crosses no authority boundary at all.**

---

## 10. Final Determination

> # CONDITIONALLY READY
>
> **The Option A implementation is fully specified and fully measured. R-08 gains one criterion, `not-analysis-artifact`; R-09's declaration is untouched; precedence is untouched; the two predicates become a partition of one base set split on a single negated literal. The population arithmetic closes exactly — 439 = 347 + 92 — with zero new `UNRESOLVED`, provided R-08's exclusion and R-09's inclusion call one shared helper. If they do not, 91 named artifacts fall out of every class, and that is the entire risk of the option. Certification, identity and ownership impact is zero, measured: four files reference the classifier and no gate, engine or workflow consumes it. No constitutional authority is required. Seven conditions remain, six of them held by one located owner, and none is analysis — all are decisions. Implementation is not authorised and no execution is claimed.**

### 10.1 Why `CONDITIONALLY READY`

| Verdict | Assessment |
|---|---|
| `READY FOR IMPLEMENTATION` | **Rejected.** No `AG-2b` decision record exists. `Q-1` leaves R-09's population undetermined between 1 and 92, and `Q-2` leaves edge case `E-12` open. `CA-1`'s out-of-scope list still forbids the change. Implementing now would be engineering deciding declaration questions — the defect's own cause repeating |
| **`CONDITIONALLY READY`** | **Adopted.** Design complete · arithmetic closed and conserved · the single failure mode quantified at 91 subjects and structurally mitigated · 26 tests and 6 measurement methods enumerated · blast radius measured at four files · zero certification, identity and ownership coupling · rollback total and crossing no authority boundary · no constitutional dependency · every residual condition a decision held by a located owner |
| `NOT READY` | **Rejected as overstated.** It would imply an unlocated authority or an unmeasured input. Neither holds |

### 10.2 The seven conditions

| # | Condition | Authority | Available |
|---|---|---|---|
| 1 | **`AG-2b` decision recorded**, confirming Option A | Mutation governance owner | **YES** |
| 2 | `Q-1` case sensitivity settled — 92 or 1 | Mutation governance owner | **YES** |
| 3 | `Q-2` filename vs path settled — edge case `E-12` | Mutation governance owner | **YES** |
| 4 | `Q-3` `mutation_class_extension.py` dispositioned | Mutation governance owner | **YES** |
| 5 | `Q-4` Class 8's false ordering note corrected | Declaration owner | **YES** |
| 6 | `CA-1`'s out-of-scope list amended to admit narrowing R-08 | `CA-1` owner via `AG-2b` | **YES** |
| 7 | `Q-5` 92-subject `EX-017` migration authorised **or explicitly deferred** | Class 7 / Class 8 chains; may reach `AG-4` | **PARTIAL** |

**Condition 7 is separable.** `EX-016` evaluation and `EX-017` migration are distinct acts by the register's own statement, so the predicate may be corrected — clearing the repository-wide `ERROR` outage — with the reclassification explicitly deferred.

### 10.3 Mandatory implementation constraint

> **R-08's `not-analysis-artifact` and R-09's `analysis-artifact` MUST be the negation and the assertion of ONE shared helper function. This is the sole mitigation for the only material risk in Option A, and it is measured at 91 orphaned artifacts if violated.**

### 10.4 What is claimed, and what is not

| Claimed | Not claimed |
|---|---|
| The design is complete and internally consistent | That it is authorised |
| Conservation holds exactly: 439 = 347 + 92 | That `Q-1` should be answered either way |
| Zero new `UNRESOLVED` under symmetric implementation | That an asymmetric one is unlikely — it is quantified, not dismissed |
| 91 orphans under asymmetry, with named samples | That the mitigation has been implemented |
| Blast radius is four files, no gate/engine/workflow consumer | That an `EX-018` gate exists — it does not, and it needs `AG-2` |
| Zero certification, identity, ownership coupling | That the 92-subject migration is authorised |
| No constitutional authority required for Option A | That D or E would not reach `T1` — assessed as likely, not measured |
| Rollback is total and crosses no authority boundary | That any rollback has been rehearsed |

**No execution is claimed.** No predicate written, no precedence changed, no declaration amended, no test run, no artifact reclassified, no root cause closed, no blocker discharged. `RC-1` remains OPEN. `AG-2b` remains OPEN. `UCCEP-F-004` caps this determination at `CERTIFIED-PROVISIONAL` and `VAC-01` renders it `PROVISIONAL`.

---

## 11. Verification Record

| Check | Result |
|---|---|
| File exists | ✅ `UCOS-OMEGA-INFINITY-R09-PREDICATE-IMPLEMENTATION-READINESS-DETERMINATION.md` |
| Line count | ✅ **730** — measured post-write against the final file; recorded in the session transcript |
| Section count | ✅ **11** `## ` headings — §1 Current Baseline · §2 Approved Resolution · §3 Implementation Scope Definition · §4 Predicate Design · §5 Validation Model · §6 Test Strategy · §7 Authority Analysis · §8 Wave Impact Analysis · §9 Risk Analysis · §10 Final Determination · §11 Verification Record |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Staged changes | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to plan start |
| Exactly one new artifact | ✅ porcelain 356 → 357; the single delta is this file |
| Code mutations | ✅ **0** — `mutation_classification.py` read only, byte-identical to HEAD |
| `RULE_PREDICATES` | ✅ **UNCHANGED** — `R-01…R-08`, eight entries |
| Precedence values | ✅ **UNCHANGED** — `R-01…R-09` at `1…9` |
| `classify()` executed | ✅ **NO** — populations computed by predicate-level evaluation (`M-2`); the engine was not imported |
| Configuration mutations | ✅ **0** |
| Registry mutations | ✅ **0** — `mutation-governance-boundary.json` parsed read-only, 27,127 bytes, byte-identical |
| Certification mutations | ✅ **0** |
| Identity mutations | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys |
| Ownership mutations | ✅ **0** — `assignments` remains `{}` |
| `register.sh` invocations | ✅ **0** |
| Tests executed | ✅ **0** — 26 tests specified, none run |
| Commits | ✅ **0** |
| Root causes closed | ✅ **0** — `RC-1` OPEN |
| Blockers discharged | ✅ **0** — `AG-2b` OPEN |
| Authorities vested | ✅ **0** |
| Execution claimed | ✅ **NONE** |

---

*This determination wrote no predicate, changed no precedence, amended no declaration and executed no test. It converts Option A into a specified implementation: one shared `_analysis_artifact` helper, a sixth `not-analysis-artifact` criterion on R-08, an unchanged R-09 declaration, and two predicates that become a partition of one five-criterion base set split on a single negated literal. The population arithmetic closes without remainder — 439 = 347 + 92 — so every subject leaving `AUTHORED_DOCUMENT` enters `GOVERNED_ANALYSIS` and none falls through, which is why zero new `UNRESOLVED` is a conservation result rather than an inspection. The one material risk is asymmetry: if R-08 excludes case-insensitively while R-09 matches case-sensitively, 91 named artifacts hold no class at all, and the sole mitigation is that both criteria call one helper, since the negation of a predicate cannot disagree with the predicate. Certification, identity and ownership impact is zero and measured, not assumed: four files reference the classifier, none of them a gate, engine or workflow, and of five markdown fixtures in the existing test module only one carries an analysis token and its assertion is unchanged. No constitutional authority is required, which is the property that distinguishes A from D and E — those risk routing a nine-rule predicate defect into the vacant T1. Seven conditions remain, six with one located owner, and not one of them is further analysis. The directive described Option A as approved; no `AG-2b` decision record exists, and that is recorded as condition 1 rather than assumed away. The single repository mutation is the creation of this file.*

**END DETERMINATION — OPTION A SPECIFIED · 439 = 347 + 92 CONSERVED · 0 NEW UNRESOLVED SYMMETRIC · 91 ORPHANED IF ASYMMETRIC · SHARED HELPER MANDATORY · BLAST RADIUS 4 FILES · ZERO CERTIFICATION / IDENTITY / OWNERSHIP COUPLING · NO CONSTITUTIONAL AUTHORITY REQUIRED · 7 CONDITIONS · VERDICT CONDITIONALLY READY · ZERO MUTATIONS PERFORMED · NO EXECUTION CLAIMED · STOPPED AFTER ARTIFACT CREATION.**
