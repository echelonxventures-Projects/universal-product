# UCOS Ω∞ — R-09 PREDICATE ARCHITECTURE RESOLUTION DETERMINATION

**The R-08 / R-09 conflict, measured rather than argued. The register already forbids the resolution that looks easiest, and already demonstrates the one that is correct — twice.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-R09-PREDICATE-ARCHITECTURE-RESOLUTION-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Changes no predicate, no precedence, no declaration. Closes no root cause, discharges no blocker, vests no authority. The recommendation in §5 is a proposal addressed to the authority named in §6. |
| Mode | ANALYSIS ONLY · **NO CODE · NO `mutation_classification.py` · NO `mutation-governance-boundary.json` · NO REGISTRY · NO CERTIFICATION · NO IDENTITY · NO OWNERSHIP · NO PRECEDENCE CHANGE · NO IMPLEMENTATION · NO COMMIT** |
| Conflict source | `UCOS-OMEGA-INFINITY-WAVE-0-EXECUTION-IMPLEMENTATION-DETERMINATION.md` §3.2 (726 lines) |
| Method | Read-only measurement at HEAD `bae59755`: parsed the boundary register, read all nine predicates at `mutation_classification.py:250-424`, and computed the R-08 / R-09 populations over 6,188 tracked and 324 untracked paths using `git ls-files` and pure string evaluation. **The classification engine was not invoked.** |
| New findings | **4** — the subset relation is now quantified (§2.4); the declared token list is lowercase against uppercase filenames, a 1-vs-92 swing (§2.6); eight of nine predicate pairs already achieve disjointness by an explicit criterion and R-08/R-09 is the sole exception (§2.5); and an upstream impact claim about Group B is **not supported at this baseline** (§2.7) |
| Preserved invariants | No invented authority · no fabricated ownership · no value chosen by convenience · no closure claimed |

---

## 1. Current Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **355** lines |
| Tracked modifications | **38** |
| Untracked | **317** porcelain entries · **324** files by `git ls-files --others --exclude-standard` |
| Staged | **0** |
| Current Wave 0 readiness | **6 of 7 actions READY** (`W0-1a`, `W0-2`…`W0-6`) · **`W0-1` IMPLEMENTABLE, NOT ACCEPTABLE** |
| Current Wave 1 readiness | **0 of 5 unconditionally acceptable** — degraded from 1 of 5 when `W0-1`'s `V-3` was found unsatisfiable |
| Readiness verdict | **`NOT READY`** · ceiling `CERTIFIED-PROVISIONAL` (`UCCEP-F-004`) · `PROVISIONAL` under `VAC-01` |

### 1.1 `AG-2b` status

| Field | Value |
|---|---|
| Identifier | **`AG-2b`** — raised by the Wave 0 implementation determination §3.2 |
| Act required | Decide how R-08 and R-09 are made disjoint, and settle the implementation questions the declaration leaves open |
| Authority | **Mutation governance owner** — the same party holding `AG-2` (`S-1` semantics) and `AG-4` (`A(C)`) |
| Availability | **LOCATED, OPEN** |
| Class | **Programme authority** — a declaration decision, not a constitutional act. Not `T1`-dependent |
| Blocks | `W0-1` / `CA-1` acceptance (criterion `V-3`) · transitively `W1-5` via edge `E-04` |
| Size | **Small.** One criterion, or one ordering, or one mechanism. It is a decision awaiting a person, not work awaiting a process |

---

## 2. Problem Statement

### 2.1 R-08 as declared

```
boundary JSON  mutation_classes[7]  AUTHORED_DOCUMENT      rule R-08, precedence 8
code           mutation_classification.py:384-398

authored_document_checks(path, repo) — five criteria, all required:
  markdown                 path.endswith(".md")
  authored                 path not in repo.producer_homes
  repository-controlled    path in repo.tracked
  non-generated            path not in repo.generated
  self-declared-authority  bool(authored_document_owner(path, repo))
                             ← reads "Authority" then "Deciders" from the first 40 lines

_r08_authored_document = subject.kind == PATH and all(checks.values())
```

### 2.2 R-09 as declared

```
boundary JSON  mutation_classes[8]  GOVERNED_ANALYSIS      rule R-09, precedence 9
code           NO PREDICATE — RULE_PREDICATES holds R-01…R-08 only (:403-412)

membership_criteria — six, verbatim:
  "markdown — the path ends .md"
  "authored — absent from producer_homes"
  "repository-controlled — tracked by version control"
  "non-generated — absent from generated-artifact-registry.json canonical_path"
  "analysis-artifact — carries determination/analysis/assessment/execution/matrix/
                       readiness/admission/blocker/gap in filename"
  "self-declared-authority — carries Authority field in opening metadata block"

rule R-09 predicate text:
  "subject is a tracked, non-generated markdown path with (determination|analysis|
   assessment|execution|matrix|readiness|admission|blocker|gap) in the filename,
   satisfying the six membership_criteria declared on GOVERNED_ANALYSIS"
```

### 2.3 Predicate overlap — the structural proof

Criterion-by-criterion, the two declared sets:

| Criterion | R-08 | R-09 | Relation |
|---|---|---|---|
| markdown | ✅ | ✅ | identical |
| authored (¬`producer_homes`) | ✅ | ✅ | identical |
| repository-controlled (tracked) | ✅ | ✅ | identical |
| non-generated | ✅ | ✅ | identical |
| self-declared-authority | ✅ | ✅ | identical |
| **analysis-artifact** | ✗ | ✅ | **R-09 only** |

**R-09 ≡ R-08 ∧ analysis-artifact.** A conjunction with an extra conjunct defines a subset. Therefore **R-09 ⊂ R-08, strictly** — not by coincidence of the current corpus, but by the form of the declaration. No repository state can make an R-09 subject fail R-08.

### 2.4 The subset relationship, measured

Computed over `git ls-files` at HEAD, evaluating the five shared criteria and the token test in pure Python without invoking the engine:

```
tracked files                                   6,188
tracked .md                                     3,228
generated-artifact-registry canonical_path set     347

R-08 population  (5 criteria)                     439        ← upper bound, see note
R-09 population  (6 criteria, case-insensitive)    92
R-09 ⊆ R-08                                      True
| R-09 \ R-08 |                                     0        ← the subset claim, measured
| R-08 \ R-09 |                                   347
```

**`R-09 \ R-08` is empty and `R-09 ⊆ R-08` is `True`.** The structural proof and the measurement agree.

*Note on 439:* `producer_homes` could not be resolved without instantiating `Repository`, so the `authored` criterion was treated as satisfied. 439 is therefore an **upper bound** on R-08 and the true figure is ≤ 439. The direction of the error cannot affect the subset conclusion, because the same treatment was applied to both sets.

**Operational consequence:** implementing R-09 exactly as declared leaves **92 subjects** that the register intends as `GOVERNED_ANALYSIS` classifying as `AUTHORED_DOCUMENT`, because R-08 is evaluated first. R-09 becomes reachable in code and dead in effect.

### 2.5 Whether the predicates are actually disjoint — all nine pairs

The register's `unique` property claims *"The predicates are written to be disjoint."* Tested against the implementations at `:250-398`:

| Rule | Disjointness mechanism | Disjoint from R-08/R-09? |
|---|---|---|
| `R-01` REPOSITORY_STATE | `path in repo.tracked` → **returns False**; requires untracked-and-existing, or `.git/` | ✅ by an explicit negative on `tracked` |
| `R-02` EXCLUSION | membership in `{.gitignore, exclusion-register.json}` | ✅ neither is `.md` |
| `R-03` CORPUS_REGISTRATION | membership in `{id-ledger.json, artifacts.json}` | ✅ neither is `.md` |
| `R-04` GENERATED_ARTIFACT | `path in repo.generated` | ✅ **R-08 and R-09 both carry `non-generated` — an explicit negative criterion naming R-04's set** |
| `R-05` CONSTITUTIONAL_TRUTH | `subject.kind == OBJECT`; every path rule returns False on non-PATH | ✅ by subject kind |
| `R-06` GOVERNED_DECLARATION | requires `declaration-bearing` (JSON declaration keys) **and `non-executable`** | ✅ a `.md` carries no declaration document |
| `R-07` SOURCE | suffix in `{.py, .sh}` or filename in `{pyproject.toml}` | ✅ `.md` is in neither — **and R-06 carries `non-executable` to exclude R-07 explicitly** |
| `R-08` AUTHORED_DOCUMENT | — | ❌ **R-09 ⊂ R-08** |
| `R-09` GOVERNED_ANALYSIS | — | ❌ **R-09 ⊂ R-08** |

**Eight of nine rules achieve disjointness by an explicit criterion — a subject-kind test, a suffix test, a registry-membership test, or a *negative criterion naming the class it must not overlap*. R-08 / R-09 is the only pair in the entire rule set with no such mechanism.**

And the register uses the negative-criterion pattern **twice already**: R-08's `non-generated` exists to keep R-08 out of R-04's territory, and R-06's `non-executable` exists to keep R-06 out of R-07's. This is decisive for §4 and §5: the correct resolution is not a new mechanism. It is the register's own established mechanism applied to the one pair that lacks it.

### 2.6 Precedence ordering and `classify()` evaluation behaviour

```
boundary JSON  classification_rules.evaluation, verbatim:
  "ORDERED PRECEDENCE — rules are evaluated in the order declared, and the first rule
   whose predicate holds assigns the class."

declared order / precedence:   R-01 (1) … R-07 (7) , R-08 (8) , R-09 (9)

mutation_classification.py:441
  for rule in doc["classification_rules"]["rules"]:
      matched = RULE_PREDICATES[rule_id](subject, repo, doc)
      if matched: return ClassificationResult(..., mutation_class, rule_id, ...)
  → R-08 is tested BEFORE R-09; the first match wins and returns immediately
```

**R-08 is declared eighth, R-09 ninth. R-08 wins every contested subject.**

### 2.7 Whether the current declarations are internally consistent — they are not, in four ways

| # | Inconsistency | Evidence |
|---|---|---|
| **I-1** | The `unique` property claims the predicates are written to be disjoint. R-09 ⊂ R-08. | §2.3, §2.4 |
| **I-2** | Invariant 8 states *"No artifact resolves to more than one mutation class. Failure: authority ambiguity."* Every one of the 92 R-09 subjects satisfies two predicates. Only the ordering hides it. | §2.4 + `invariants[7]` |
| **I-3** | Class 8's own note states *"**R-09 evaluates before R-08** so analysis artifacts are classified as GOVERNED_ANALYSIS rather than the more general AUTHORED_DOCUMENT."* **This is false at this baseline** — R-09 is declared last. The class documents an ordering the register does not implement. | §2.6 vs `$distinction_from_authored_document` |
| **I-4** | The declared token list is **lowercase** (`determination/analysis/assessment/…`) while repository filenames are **uppercase**. Case handling is declared nowhere. | measured below |

**I-4, measured — a 92× swing on an undeclared detail:**

```
tracked .md whose filename carries a token, case-INSENSITIVE      540
tracked .md whose filename carries a token, case-SENSITIVE          2

R-09 population, case-insensitive (6 criteria)                     92
R-09 population, case-sensitive   (6 criteria)                      1
```

A case-sensitive implementation against the declared lowercase tokens yields **one** subject. A case-insensitive one yields **92**. The declaration does not say which, so **the predicate's population is undetermined by its own specification.** This is not an engineering preference; it decides which artifacts a class governs.

### 2.8 A correction to an upstream determination

`…ROOT-CAUSE-CLOSURE-AND-READINESS-DETERMINATION.md` `RC-1` states that `R-09 GOVERNED_ANALYSIS` *"is precisely the class governing **127 of the 192** Group B subjects and the modified MIP plan (`G-11`)."*

**Not supported at this baseline.** Measured:

```
untracked .md total                                    314
untracked 00-BOOK/PORTAL/*.md  (the Group B population) 228
  of those, filename carries an analysis token            1
all 314 untracked .md fail R-09's "repository-controlled — tracked by version control"
```

The 192 Group B subjects are `00-BOOK/PORTAL/` page documents. Only **1 of 228** carries an analysis token, and **all 228 are untracked**, so every one fails R-09's third criterion. Under the declaration as written, Group B classifies **`UNRESOLVED`**, not `GOVERNED_ANALYSIS`.

This does not weaken `RC-1` — the `ERROR` outage is repository-wide and real. It relocates R-09's actual population: **92 tracked analysis artifacts, not 127 Group B pages.** Stated because an impact figure carried by three determinations in this chain does not survive measurement, and the resolution below should be sized against the real population.

---

## 3. Constitutional Requirements

### 3.1 The governing chain, as the register declares it of itself

```
UCKP-LAW-0001  (engine/uckp/law.py)  articles UCKP-ART-10, UCKP-ART-16
     │  role EXECUTION · relation PROJECTION
     │  binding: 00-BOOK/DATA/constitutional-authority-alignment.json
     ▼
mutation-governance-boundary.json
  authority: "AUTHORED REPOSITORY TRUTH, HELD SUBORDINATE UNDER UCKP-LAW-0001.
              This artifact declares the boundary; it does not create a new authority
              and governs nothing itself."
  constitutional_basis: UCKP-LAW-0001 · UCOS-CAA-001 ·
                        UCOS-CMG-EXEC-000001 Requirement 004 · GOV-005 · UCOS-CL-016
  UCKP-ART-10 effect: "execution never owns knowledge — It owns which mutation classes
              exist and which authority disposes of each; it may never own knowledge."
     ▼
RULE_PREDICATES  (platform/repository_intelligence/mutation_classification.py)
  ⚠ P0-DECLARATION-001: platform/repository_intelligence "is not a governed package…
    falls outside the scope of UFC-14, UFC-15 and UFC-16 entirely"
```

### 3.2 The four declared properties, and which bind this decision

| Property | Verbatim | Binds? |
|---|---|---|
| `deterministic` | *"a pure function of the subject and the repository at one commit. It reads no clock, no environment and no caller ordering."* | **YES** — forbids any resolution depending on caller order or invocation context |
| `total` | *"Every mutation subject resolves… never to nothing, and never to a default."* | **YES** — forbids a resolution that leaves analysis artifacts unresolved |
| `unique` | *"Exactly one class. The predicates are written to be disjoint; **the ordering is a tie-break of last resort and never a substitute for disjointness, because two classes would be two authorities and UCKP-ART-18 refuses that.**"* | **YES — and it is decisive.** See §3.3 |
| `repository_evaluable` | *"Every predicate is decidable from tracked repository state alone — a path, a registry membership, or a declared field."* | **YES** — all six R-09 criteria satisfy it |

### 3.3 The authoritative constraint

**The `unique` property does not merely require one class per subject. It states, in the register's own words, that ordering may never substitute for disjointness — and it grounds that in `UCKP-ART-18`'s refusal of two authorities over one subject.**

This is the single most consequential sentence for this determination, because it **pre-refuses the resolution that appears cheapest.** Reordering R-09 before R-08 would make the correct class win — while leaving the predicates overlapping and relying on the ordering to hide it. That is precisely "ordering as a substitute for disjointness."

**The authoritative requirement is therefore: R-08 and R-09 must be made genuinely disjoint at the predicate level. Ordering may remain as a tie-break of last resort, but may not be the mechanism.**

### 3.4 Class uniqueness

| Source | Requirement |
|---|---|
| `invariants[6]` | *"Every tracked artifact resolves to exactly one mutation class. Failure: unclassified artifact."* |
| `invariants[7]` | *"No artifact resolves to more than one mutation class. Failure: **authority ambiguity**."* |
| `invariants[1]` | *"No mutation class is claimed by two authorities as primary."* |
| `unique` property | ordering is never a substitute for disjointness |

**`invariants[7]` is violated at the predicate level today for 92 subjects.** The named failure mode — authority ambiguity — is exactly what two overlapping predicates produce: R-08 resolves to Class 7's authority chain, R-09 to Class 8's, and the artifact satisfies both.

### 3.5 Precedence requirements

`evaluation` declares ordered precedence with first-match-wins. Precedence is a declared, ordered property of the rule list and **it is legitimate architecture** — it is how R-04 precedes R-08, for instance. What the `unique` property forbids is *relying* on it where disjointness is absent. Precedence resolves ties that should not exist; it does not license their existence.

### 3.6 Extension rules

| Source | Rule |
|---|---|
| `recurrence_prevention` | *"test_mutation_governance_boundary.py asserts that every class is governed, that no class is doubly claimed, and that every named implementation exists. A future mutation class added without an authority fails that test."* |
| `validate_rule_coverage` | Two-sided: a declared rule needs a predicate; a predicate needs a declared rule |
| Class 8 `grants_only_mutation_ownership` | *"Class 8 defines WHO MAY MUTATE… and nothing else. It grants no certification authority, no ratification authority and no freeze authority."* |
| `$conformance_is_not_claimed_here` | Evaluation is `EX-016`; **migration of existing artifacts is `EX-017`**; the conformance gate is `EX-018`. Three separate acts |

**The extension pattern the register actually uses:** a new, more specific class is added *after* a more general one, and the more general one is narrowed by a negative criterion so the two do not overlap. R-04/R-08 and R-06/R-07 both follow it. **The R-09 extension performed the first half and not the second.**

### 3.7 Backward compatibility requirements

| Concern | Requirement | Consequence |
|---|---|---|
| Artifacts currently `AUTHORED_DOCUMENT` | Reclassifying 92 subjects from Class 7 to Class 8 **changes which authority may mutate them** | This is `EX-017` migration, a distinct act — not part of implementing the predicate |
| Existing R-08 consumers | Any consumer gating on `AUTHORED_DOCUMENT` sees its population fall by 92 | Must be inventoried before migration |
| `EX-018` conformance gate | Does not yet exist — no CI step runs `classify_all` and fails on `UNRESOLVED`/`ERROR` | The outage is currently invisible to every gate |
| The `ERROR` outage | Repository-wide today; **any** resolution that clears coverage improves on it | Argues for implementing the predicate even while `V-3` stays open |

**No backward-compatibility constraint forbids the change. One reframes it:** because 92 subjects move authority, the predicate change and the migration are two acts, and only the first is in scope here.

---

## 4. Resolution Options

### Option A — Narrow R-08 with an explicit negative criterion

*Add `not-analysis-artifact` to `authored_document_checks`, making R-08 = its five criteria ∧ ¬analysis-artifact.*

| | |
|---|---|
| **Advantages** | Establishes **genuine disjointness** — R-08 ∩ R-09 = ∅ by construction, satisfying `unique` as written rather than as tie-broken · **the register's own established pattern**, used twice already (`non-generated` excludes R-04; `non-executable` excludes R-07) · makes ordering irrelevant to the outcome, which is what the `unique` property asks for · one criterion in one dict; the per-criterion shape is preserved so a refusal still names which criterion failed · zero new mechanism, zero new layer, zero precedence change |
| **Disadvantages** | Touches `R-01…R-08`, which `CA-1` declares out of scope · the token definition is now load-bearing in **two** predicates, so `I-4`'s case question must be settled before either can be written · 92 subjects change class, triggering `EX-017` |
| **Constitutional impact** | **Satisfies** `unique`, `invariants[6]`, `invariants[7]`, `deterministic`, `total`, `repository_evaluable`. Requires a declaration amendment to `mutation_classes[7].membership_criteria` (5 → 6 criteria) so the register and the code stay two-sided. `UCKP-ART-10` is respected: this changes which class exists over which subject, not knowledge |
| **Migration impact** | 92 tracked artifacts move Class 7 → Class 8 under `EX-017`. R-08 falls to ≤ 347 |
| **Affected artifacts** | `mutation_classification.py` (`authored_document_checks`, new `governed_analysis_checks`, `RULE_PREDICATES`) · `mutation-governance-boundary.json` (`mutation_classes[7].membership_criteria`) · `platform/tests/test_mutation_classification.py` · `test_mutation_governance_boundary.py` |
| **Risks** | Narrowing R-08 could push a subject to `UNRESOLVED` if the token test is asymmetric between the two predicates — mitigated by deriving both from one shared helper · the boundary JSON edit is a registry-adjacent write requiring the declaration owner |

### Option B — Change the R-09 predicate

*Redefine R-09's criteria so it stops overlapping R-08.*

| | |
|---|---|
| **Advantages** | Leaves `R-01…R-08` untouched, staying inside `CA-1`'s declared scope · no existing class loses population, so no `EX-017` migration |
| **Disadvantages** | **Cannot work.** R-09's overlap is caused by sharing five criteria with R-08. Removing a shared criterion makes R-09 *broader*, and it would then overlap R-08 *and* possibly R-04/R-06/R-07 — strictly worse. Adding a criterion keeps it a subset. **No modification of R-09 alone produces disjointness**, because disjointness is a property of the pair and R-08 is the superset |
| **Constitutional impact** | Cannot satisfy `unique`. If R-09 is narrowed to near-emptiness it satisfies `unique` vacuously while Class 8 governs nothing — the vacuous-measure failure `RC-5` documents in a different register |
| **Migration impact** | None, because nothing is achieved |
| **Affected artifacts** | `mutation_classification.py`, boundary `mutation_classes[8]` |
| **Risks** | Produces the appearance of resolution with none of the substance. **Assessed and rejected on measurement, not preference** |

### Option C — Change the precedence ordering

*Declare R-09 before R-08 so the more specific class is tested first.*

| | |
|---|---|
| **Advantages** | Smallest possible edit — reorder two entries in a JSON list · matches Class 8's own stated intent (*"R-09 evaluates before R-08"*), resolving `I-3` · immediately yields the intended classification for all 92 subjects · precedence is declared architecture and reordering is a legitimate operation in general |
| **Disadvantages** | **Forbidden by the property it would be used to satisfy.** `unique` states: *"the ordering is a tie-break of last resort and **never a substitute for disjointness**, because two classes would be two authorities and `UCKP-ART-18` refuses that."* Using ordering to resolve an overlap is the substitution named · leaves `invariants[7]` violated at the predicate level — 92 subjects still satisfy two predicates; only the return statement hides it · `CA-1` declares precedence change out of scope · leaves the overlap as a latent trap for the next class added after R-09 |
| **Constitutional impact** | **VIOLATES the `unique` property as declared** and leaves `invariants[7]` unsatisfied. The register pre-refused this resolution |
| **Migration impact** | 92 subjects move Class 7 → Class 8, same as A, but with the ambiguity retained |
| **Affected artifacts** | `mutation-governance-boundary.json` `classification_rules.rules` order and `precedence` fields |
| **Risks** | Ratifies ordering-as-disjointness as programme practice. Every future specific class then relies on position rather than definition, and `unique` becomes decorative. **This is the technical-debt option** |

### Option D — Explicit exclusion / override mechanism

*Add a declared `excludes` or `overrides` field to rules, e.g. R-09 `overrides: [R-08]`, evaluated by `classify()`.*

| | |
|---|---|
| **Advantages** | Makes the relationship between rules **declarative and inspectable**, rather than implicit in criteria · one mechanism serves every future specific-over-general pair · a test can assert every overlap is covered by a declared override |
| **Disadvantages** | **Introduces a second resolution mechanism alongside precedence.** Two mechanisms deciding one subject's class is the shape `UCKP-ART-18` refuses — the concern `unique` already articulates · requires changing `classify()`'s loop, which currently *"never branches on rule identity"* (`:248` comment). An override table forces exactly that branch · does not remove the overlap; it declares it and then resolves it — `invariants[7]` remains violated at the predicate level · substantially more change than A, for a problem A solves with one conjunct |
| **Constitutional impact** | Ambiguous, and the ambiguity is the objection. It could be read as satisfying `unique` by declaring the tie-break, or as violating it by institutionalising the substitute. **Not resolvable without the mutation governance owner** |
| **Migration impact** | 92 subjects move, plus every existing rule must be audited for undeclared overrides |
| **Affected artifacts** | `mutation_classification.py` `classify()` · boundary `classification_rules` schema and all nine rules · both test modules |
| **Risks** | Highest architectural risk of the five. It is the only option that changes the resolution *algorithm*, and it makes overlapping predicates a supported configuration rather than a defect |

### Option E — New classification layer

*Introduce a facet or sub-class layer so `GOVERNED_ANALYSIS` becomes a refinement of `AUTHORED_DOCUMENT` rather than a sibling.*

| | |
|---|---|
| **Advantages** | Models the actual relationship honestly — R-09 **is** a specialisation of R-08, and a subset relation is what a subtype expresses · would generalise to future refinements without repeated negative criteria · resolves `I-1` by admitting the sets nest instead of asserting they are disjoint |
| **Disadvantages** | **A new architectural surface for a nine-rule register with one overlapping pair** · every declared property would need restating over two layers: does `unique` mean one class, one facet, or one leaf? · `invariants[1]`'s *"No mutation class is claimed by two authorities as primary"* becomes ambiguous when a subject holds a parent and a child class with different `governed_by` chains · Class 8's `governed_by` differs from Class 7's, so nesting them nests two authority chains — the thing `UCKP-ART-18` refuses · touches every consumer of `ClassificationResult.mutation_class` |
| **Constitutional impact** | Requires amending the declared properties themselves. That is a larger act than the defect warrants and plausibly escalates beyond `AG-2b` |
| **Migration impact** | Largest. Every classified artifact acquires a layer; every consumer must be updated |
| **Affected artifacts** | Boundary schema and all nine classes · `mutation_classification.py` result type and loop · every consumer · both test modules |
| **Risks** | Solves a general problem the register does not have at the cost of the specific one it does. **Reconsider only if the overlapping pairs multiply** |

---

## 5. Canonical Resolution Recommendation

### 5.1 The four tests, applied

| Test | A (narrow R-08) | B (change R-09) | C (reorder) | D (override) | E (layer) |
|---|---|---|---|---|---|
| **Preserves existing architecture** | ✅ **Uses the register's own pattern**, twice-demonstrated | ✅ but achieves nothing | ⚠️ preserves code, **violates a declared property** | ❌ changes the resolution algorithm | ❌ new architectural surface |
| **Minimum change** | ✅ one conjunct + one declaration criterion | ✅ but ineffective | ✅ smallest edit — **and the wrong one** | ❌ schema + loop + 9 rules | ❌ largest |
| **Avoids technical debt** | ✅ overlap **eliminated**, ordering made irrelevant | ❌ vacuous class | ❌ **institutionalises ordering-as-disjointness** | ❌ makes overlap a supported configuration | ⚠️ trades one debt for a broader one |
| **Maintains infinite extensibility** | ✅ each new specific class narrows its general predecessor — **the pattern already scaling across 8 of 9 pairs** | ❌ | ❌ every future class depends on position | ⚠️ generalises, at the cost of two mechanisms | ⚠️ generalises, at the cost of layered authority |

### 5.2 Recommendation

> **Option A — narrow R-08 with an explicit `not-analysis-artifact` criterion — is the canonical resolution.**

Four grounds, none of them convenience:

1. **The register forbids Option C in its own words.** `unique` states ordering is *"never a substitute for disjointness."* C is that substitution. This is not an interpretation; it is the sentence that governs the question, and it was written before the conflict existed.
2. **A is not a new mechanism — it is the register's established one.** Eight of nine pairs are disjoint by an explicit criterion, and the negative-criterion form appears twice: R-08 already carries `non-generated` to stay out of R-04, and R-06 carries `non-executable` to stay out of R-07. R-08/R-09 is the **only** pair lacking one. A completes a pattern; it does not introduce one.
3. **A is the only option that satisfies `invariants[7]` at the predicate level.** C, D and E all leave 92 subjects satisfying two predicates and resolve the conflict downstream of the overlap. A removes the overlap. *"No artifact resolves to more than one mutation class"* is a statement about predicates, not about return values.
4. **A is minimum change among the options that work.** B does not work. C is smaller but forbidden. D and E are larger and change the algorithm or the schema. A is one conjunct, one declaration criterion, and a shared helper.

### 5.3 What Option A does not resolve, and must be decided with it

| # | Question | Why it cannot be deferred |
|---|---|---|
| Q-1 | **Case sensitivity of the token test.** Case-insensitive → 92 subjects; case-sensitive → 1. Undeclared. | It decides R-09's population, and under A the **same** test narrows R-08. An asymmetry between them would push subjects to `UNRESOLVED` |
| Q-2 | **Filename or full path?** The criterion says *"in filename"*; the rule text says *"in the filename"*. Consistent — but a path-based reading would sweep in every file under a directory carrying a token | Same reason as Q-1 — the test is load-bearing in two predicates |
| Q-3 | **Is `mutation_class_extension.py` the intended registration path?** 8,752 bytes, no located caller. If it is, the implementation belongs there, not in `RULE_PREDICATES` | Determines *where* the change lands |
| Q-4 | **Does Class 8's `$distinction_from_authored_document` note get corrected?** It asserts *"R-09 evaluates before R-08"*, false today and **still false under A** — under A, ordering stops mattering | A declaration that documents a false mechanism is `I-3` left open |
| Q-5 | **Is the 92-subject reclassification authorised, and when?** `EX-017` migration is a distinct act from `EX-016` evaluation | 92 artifacts change governing authority |

**All five are declaration questions for the mutation governance owner. None is an engineering choice, and this determination decides none of them.**

---

## 6. Authority Requirement Analysis

### 6.1 Can engineering decide?

**No — for the resolution. Partly — for its implementation.**

Engineering may write a predicate that evaluates declared criteria. It may not decide **which criteria a declared class has**, because that is the register's content, and the register's authority statement is explicit: it *"owns which mutation classes exist and which authority disposes of each"* under `UCKP-ART-10`. Option A adds a sixth criterion to `mutation_classes[7]` — a change to what Class 7 *is*.

Three further reasons engineering cannot self-authorise:

- `CA-1` declares *"any change to `R-01…R-08`"* and *"any change to precedence"* out of scope. A, C, D and E all cross one of those lines. **Every working option is out of scope for the action that would carry it.**
- The change moves 92 artifacts from Class 7's authority chain to Class 8's. Reassigning which authority may mutate 92 artifacts is not an engineering act under any reading.
- `P0-DECLARATION-001` records that `platform/repository_intelligence` *"is not a governed package… falls outside the scope of UFC-14, UFC-15 and UFC-16 entirely."* The code plane has no authority standing from which to originate a declaration change.

### 6.2 Does the mutation governance owner need to approve?

**Yes. This is the deciding authority, and the decision is entirely within its competence.**

The boundary register is `AUTHORED REPOSITORY TRUTH, HELD SUBORDINATE UNDER UCKP-LAW-0001`, role `EXECUTION`, relation `PROJECTION`. Amending which criteria a class declares, and which of two overlapping rules is narrowed, is exactly what that owner owns. `Q-1`…`Q-5` are all its questions.

### 6.3 Does constitutional authority need to approve?

**No — not for Options A, B or C.**

| Option | Escalates to `T1`? | Why |
|---|---|---|
| A | **No** | Amends a criterion list inside an EXECUTION-role register. Creates no authority, changes no tier, ratifies nothing |
| B | No | Same surface |
| C | No | Reorders a declared list — though it is refused on other grounds |
| D | **Possibly** | Changing `classify()`'s resolution algorithm and adding an override field alters *how* authority is resolved, not merely which class applies. Whether that reaches `UCOS-CAA-001` is itself a question for the alignment owner |
| E | **Probably** | Requires amending the declared properties (`unique`, `total`) and makes `invariants[1]` ambiguous under layered authority chains. Amending the invariants of a constitutionally-bound register plausibly engages `UCOS-CAA-001` and, through it, the `T1` vacancy |

**A significant consequence: the recommended option is the one that does *not* touch the vacant tier.** Options D and E risk routing a nine-rule predicate defect into `AG-9`, which is `VACANT` and unreachable. Option A keeps the decision with a located owner.

### 6.4 Decision → Required Authority → Current Availability

| Decision | Required authority | Availability |
|---|---|---|
| Which option resolves R-08/R-09 | **Mutation governance owner** (`AG-2b`) | **LOCATED, OPEN** |
| `Q-1` case sensitivity | Mutation governance owner (`AG-2b`) | **LOCATED, OPEN** |
| `Q-2` filename vs path | Mutation governance owner (`AG-2b`) | **LOCATED, OPEN** |
| `Q-3` extension-module registration path | Mutation governance owner (`AG-2b`) | **LOCATED, OPEN** |
| `Q-4` correct Class 8's ordering note | Declaration owner = mutation governance owner | **LOCATED, OPEN** |
| `Q-5` authorise the 92-subject `EX-017` migration | Class 7 and Class 8 authority chains — *"the authority the analysis declares of itself"*, owner-parameterised | **PARTIAL** — owner-parameterised values are the `RC-2` defect; may require `AG-4` |
| Amend `mutation_classes[7].membership_criteria` | Boundary register owner under `UCKP-LAW-0001` | **LOCATED** |
| Write the predicate once criteria are settled | Repository Intelligence (`AG-1`) | **AVAILABLE** |
| Option D's algorithm change | Mutation governance owner **+ possibly** constitutional alignment owner | **PARTIAL** |
| Option E's property amendment | Constitutional alignment owner **+ possibly `T1`** | **NOT AVAILABLE — `T1` VACANT** |

**`AG-2b` covers `Q-1` through `Q-4` and the option choice: five decisions, one located owner, no constitutional dependency. `Q-5` is the one item that may reach `AG-4`.**

---

## 7. Impact on Wave Execution

### 7.1 Wave 0 readiness — recalculated

| Action | Before | After | Change |
|---|---|---|---|
| `W0-1a` `S-1` package | READY | **READY** | — |
| `W0-2` carrier package | READY | **READY** | — |
| `W0-3` Article 28 package | READY, `SC-3` active | **READY** | — |
| `W0-4` `A(C)` draft | READY | **READY** | — |
| `W0-5` ownership run-mode | READY, `SC-2` active | **READY** | — |
| `W0-6` denominator | READY | **READY** | — |
| `W0-1` R-09 predicate | IMPLEMENTABLE, NOT ACCEPTABLE | **IMPLEMENTABLE, NOT ACCEPTABLE — with the resolution now identified and its authority located** | Blocker unchanged; **path to closure established** |
| **Wave 0 total** | 6 of 7 READY | **6 of 7 READY** | **Unchanged** |

**One material improvement that is not a readiness change:** `AG-2b` moves from *"a decision must be made"* to *"a specific decision, with five enumerated sub-questions, one recommended option grounded in the register's own declared property and its own twice-used pattern, and a located owner with no constitutional dependency."* The blocker is unchanged in status and materially reduced in cost.

### 7.2 Wave 1 readiness — recalculated

| Action | Before | After | Basis |
|---|---|---|---|
| `W1-1` = `CA-1` | IMPLEMENTABLE, NOT ACCEPTABLE | **CONDITIONALLY READY** | Every technical input is now measured. `V-3` remains open pending `AG-2b`, but the resolution and its authority are identified, and **`CA-1`'s scope is now known to be the obstruction** |
| `W1-2` = `CA-2`-E | NOT READY | **NOT READY** | `W0-6`, `AG-2` — untouched |
| `W1-3` = `CA-6`-E | READY (spec scope) | **READY** | untouched |
| `W1-4` = `CA-8`-E | NOT READY | **NOT READY** | `W0-5`, read-only mode — untouched |
| `W1-5` = `CA-9`-E | DEGRADED via `E-04` | **DEGRADED, and re-sized** | Depends on `W1-1`. §2.8 corrects the affected population from *127 Group B pages* to **92 tracked analysis artifacts** — a smaller and better-characterised exposure |
| **Wave 1 total** | 0 of 5 unconditional | **0 of 5 unconditional · 1 CONDITIONALLY READY** | `W1-1` |

### 7.3 `CA-1` status

**`CA-1` is now determined to be mis-scoped, not merely blocked.**

`CA-1` requires *"`classify()` returns `CLASSIFIED` … for a sample spanning all nine classes"* while declaring out of scope *"any change to `R-01…R-08`, any change to precedence."* Measurement establishes that **every resolution producing a firing R-09 crosses one of those two lines**:

| Option | Crosses | Verdict |
|---|---|---|
| A | `R-01…R-08` | **RECOMMENDED — and out of `CA-1`'s scope** |
| B | neither | ineffective |
| C | precedence | forbidden by `unique` |
| D | both, plus `classify()` | larger, algorithmic |
| E | both, plus the properties | largest, possibly `T1` |

**`CA-1` as written cannot reach its own acceptance criteria.** The remedy is a scope amendment by `CA-1`'s owner, admitting the narrowing of R-08 — which is `AG-2b`'s decision to authorise. **`CA-1` is not defective in intent; its out-of-scope list was drawn before the subset relation was measured.**

### 7.4 `AG-2b` status — updated

| Field | Before | After |
|---|---|---|
| Definition | "precedence-vs-predicate decision for R-08/R-09 disjointness" | **Five enumerated decisions: option choice + `Q-1`…`Q-4`; `Q-5` referred separately** |
| Recommended resolution | none | **Option A**, on four measured grounds |
| Authority | mutation governance owner | **Unchanged — LOCATED, OPEN** |
| Constitutional dependency | unknown | **NONE for Option A.** D and E would risk routing to the vacant `T1` |
| Population at stake | unknown | **92 tracked artifacts** (case-insensitive) or **1** (case-sensitive) — `Q-1` decides |
| Class | Programme authority | **Unchanged.** A decision awaiting a person, not work awaiting a process |

### 7.5 Critical path impact

**None. The critical path is unchanged.**

```
RC-4 ──▶ RC-3 ──▶ {RC-5, RC-7} ──▶ ARB ──▶ READY
          ▲
          └── AG-3, NOT LOCATED — still the binding constraint at node 2 of 5
```

`RC-1` and `AG-2b` sit on a **parallel branch** (`RC-1 → RC-2/RC-8/RC-9`), not on the critical path. Resolving `AG-2b` does not shorten the path to `READY`, and failing to resolve it does not lengthen it.

**What it does change:** `RC-1` is the highest transitive-fan-out root in the graph, reaching 5 of 12 nodes. Its closure is a prerequisite of `CA-4`, `CA-8` and `CA-9`. So `AG-2b` gates three downstream actions while gating nothing on the critical path — which makes it **high-leverage and non-urgent**, a combination worth stating explicitly so it is neither escalated as a crisis nor deferred as trivial.

---

## 8. Acceptance Criteria

Measurable closure criteria for the resolution, once `AG-2b` has decided. **None is satisfied today.**

### 8.1 Predicate correctness

| # | Criterion | Measurement |
|---|---|---|
| P-1 | `validate_rule_coverage(boundary)` returns `()` | Two-sided check, both directions |
| P-2 | `governed_analysis_checks` evaluates all six declared criteria individually | Per-criterion dict, mirroring Classes 6 and 7 |
| P-3 | The R-09 predicate **rejects** a non-analysis subject | Non-vacuous negative test. A predicate returning `True` for everything satisfies P-1 vacuously |
| P-4 | Under Option A, `authored_document_checks` evaluates six criteria including `not-analysis-artifact` | Per-criterion dict; count 5 → 6 |
| P-5 | Both predicates derive the token test from **one shared helper** | No asymmetry can arise between the narrowing and the matching |
| P-6 | `Q-1` and `Q-2` settled and implemented as decided | Case handling and filename-vs-path both explicit in code and declaration |

### 8.2 Classification coverage

| # | Criterion | Measurement |
|---|---|---|
| C-1 | `classify()` returns `CLASSIFIED` or `UNRESOLVED` — **never `ERROR`** | Heterogeneous sample |
| C-2 | At least one subject returns `GOVERNED_ANALYSIS` with `rule_id == "R-09"` | **The criterion unsatisfiable today** |
| C-3 | R-09's population equals the figure `Q-1` implies — **92** case-insensitive, **1** case-sensitive | Recomputed over `git ls-files`; must match, not approximate |
| C-4 | R-08's population equals its pre-change value minus R-09's | Under A: ≤ 439 − 92 = ≤ 347 |
| C-5 | No subject moves to `UNRESOLVED` as a side effect of narrowing R-08 | Full before/after classification diff over all 3,228 tracked `.md` |
| C-6 | Untracked subjects still resolve `UNRESOLVED`, not `GOVERNED_ANALYSIS` | 314 untracked `.md` fail `repository-controlled` — §2.8 |

### 8.3 Uniqueness

| # | Criterion | Measurement |
|---|---|---|
| U-1 | **For every tracked path, at most one of the nine predicates returns `True`** | Exhaustive pairwise evaluation over all 6,188 tracked paths. **This is the test that would have caught the defect and does not exist** |
| U-2 | `\| R-08 ∩ R-09 \| == 0` | Direct set intersection |
| U-3 | `invariants[7]` holds at the **predicate** level, not merely at the return-value level | U-1 is the measurement of exactly this |
| U-4 | `invariants[1]` holds — no class doubly claimed | `test_mutation_governance_boundary.py` |

### 8.4 Precedence correctness

| # | Criterion | Measurement |
|---|---|---|
| O-1 | **Classification is invariant under permutation of the rule list** | Shuffle the nine rules, reclassify all 6,188 tracked paths, assert identical results. **This is the operational definition of "ordering is never a substitute for disjointness"** and it is the strongest available proof that Option A worked |
| O-2 | Declared `precedence` values remain `1…9` unchanged | No precedence change — the constraint this determination is bound by |
| O-3 | `Q-4` settled: Class 8's `$distinction_from_authored_document` note corrected or withdrawn | Under A, ordering stops mattering, so the note is false either way |

### 8.5 Regression protection

| # | Criterion | Measurement |
|---|---|---|
| G-1 | `set(RULE_PREDICATES) == {declared rule ids}` asserted in a test | A future declared-but-unimplemented rule fails **at test time**, not at classify time |
| G-2 | **U-1's pairwise disjointness test added permanently** | The recurrence guard for *this* defect class. Without it, the next specific class repeats the failure |
| G-3 | O-1's permutation invariance test added permanently | Guards the `unique` property operationally |
| G-4 | `Q-3` settled: `mutation_class_extension.py` invoked or declared vestigial | An extension module with no caller is the mechanism that produced this defect |
| G-5 | An `EX-018`-style gate runs `classify_all` over changed paths and fails on `UNRESOLVED`/`ERROR` | The outage was invisible to every gate; **noted as required, out of this scope** |

### 8.6 Verification evidence

| # | Criterion |
|---|---|
| E-1 | `validate_rule_coverage()` return value recorded before and after |
| E-2 | Full before/after classification of all 3,228 tracked `.md`, digest-compared |
| E-3 | Two runs digest-identical — `deterministic` property |
| E-4 | Zero mutations during classification, **mutation-tested not asserted** |
| E-5 | `mutation-governance-boundary.json` diff shown explicitly if Option A amends `mutation_classes[7]` |
| E-6 | The `AG-2b` decision recorded, naming the deciding party, before any code lands |
| E-7 | The 92-subject `EX-017` migration list enumerated and its authorisation recorded, or explicitly deferred |
| E-8 | Absence of evidence recorded as **NOT-DONE**, never as pass — `TRACK-001` fail-closed |

---

## 9. Final Determination

> # CONDITIONALLY READY
>
> **The R-08 / R-09 conflict is fully characterised and its resolution is identified. R-09 ⊂ R-08 strictly, proven structurally and measured empirically (`R-09 \ R-08` = 0 over 6,188 tracked paths). Option A — narrowing R-08 with an explicit `not-analysis-artifact` criterion — is the canonical resolution, because the register's `unique` property forbids Option C in its own words, because eight of nine predicate pairs already achieve disjointness by exactly this mechanism and R-08/R-09 is the sole exception, and because A is the only option that satisfies `invariants[7]` at the predicate level rather than downstream of the overlap. The deciding authority is the mutation governance owner under `AG-2b` — LOCATED and OPEN, with no constitutional dependency. Five sub-questions must be settled with the option choice, one of which swings R-09's population between 1 and 92 subjects. Implementation is not authorised and no closure is claimed.**

### 9.1 Why `CONDITIONALLY READY` and not the alternatives

| Verdict | Assessment |
|---|---|
| `READY FOR IMPLEMENTATION` | **Rejected.** Every working resolution crosses `CA-1`'s declared out-of-scope boundary. `Q-1` alone leaves R-09's population undetermined between 1 and 92. Implementing before `AG-2b` would be engineering deciding a declaration question |
| **`CONDITIONALLY READY`** | **Adopted.** Every technical input is measured; the option analysis is complete; the recommendation is grounded in the register's own declared property and its own established pattern; the authority is located and carries no constitutional dependency. The conditions are enumerated, finite and all held by one located owner |
| `NOT READY` | **Rejected as overstated.** It would imply an unlocated authority or an unmeasured input. Neither holds: the owner exists and every figure carries the command that produced it |

### 9.2 The conditions, in full

| # | Condition | Authority | Available |
|---|---|---|---|
| 1 | Option A confirmed, or another chosen with reasons | `AG-2b` | **YES** |
| 2 | `Q-1` case sensitivity settled | `AG-2b` | **YES** |
| 3 | `Q-2` filename vs path settled | `AG-2b` | **YES** |
| 4 | `Q-3` extension-module registration path settled | `AG-2b` | **YES** |
| 5 | `Q-4` Class 8's false ordering note corrected | `AG-2b` | **YES** |
| 6 | `CA-1`'s out-of-scope list amended to admit narrowing R-08 | `CA-1` owner via `AG-2b` | **YES** |
| 7 | `Q-5` 92-subject `EX-017` migration authorised or deferred | Class 7 / Class 8 chains; may reach `AG-4` | **PARTIAL** |

**Six of seven conditions rest with one located owner and none requires a constitutional act.** Condition 7 is the only one that may reach an unlocated authority, and it is separable: the predicate may be corrected without performing the migration, since `EX-016` evaluation and `EX-017` migration are distinct acts by the register's own statement.

### 9.3 What this determination establishes, and what it does not

| Established | Not established |
|---|---|
| R-09 ⊂ R-08, structurally and empirically | That any option is authorised |
| The population at stake: 92 or 1, per `Q-1` | Which `Q-1` answer is correct |
| Eight of nine pairs are disjoint by explicit criterion; R-08/R-09 is the exception | That the pattern must be followed — that is `AG-2b`'s call |
| `unique` forbids ordering as the mechanism | That Option C is unavailable if `AG-2b` amends `unique` |
| `AG-2b` needs no constitutional authority for A, B or C | Whether D or E would reach `T1` — assessed as likely, not measured |
| The upstream *127 of 192 Group B* impact figure fails at this baseline | A replacement impact figure for `G-11`'s MIP-plan claim |
| Four internal inconsistencies `I-1`…`I-4` | Their disposition |

**No closure is claimed.** No root cause is closed, no blocker discharged, no authority vested, no predicate written, no precedence changed, no artifact reclassified. `RC-1` remains open. `UCCEP-F-004` caps this determination at `CERTIFIED-PROVISIONAL` and `VAC-01` renders it `PROVISIONAL`, as it does every determination in this corpus.

---

## 10. Verification Record

| Check | Result |
|---|---|
| File exists | ✅ `UCOS-OMEGA-INFINITY-R09-PREDICATE-ARCHITECTURE-RESOLUTION-DETERMINATION.md` |
| Line count | ✅ **654** — measured post-write against the final file; recorded in the session transcript |
| Section count | ✅ **10** `## ` headings — §1 Current Baseline · §2 Problem Statement · §3 Constitutional Requirements · §4 Resolution Options · §5 Canonical Resolution Recommendation · §6 Authority Requirement Analysis · §7 Impact on Wave Execution · §8 Acceptance Criteria · §9 Final Determination · §10 Verification Record |
| Options analysed | ✅ **5** — A, B, C, D, E, each with advantages · disadvantages · constitutional impact · migration impact · affected artifacts · risks |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Staged changes | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to plan start |
| Exactly one new artifact | ✅ porcelain 355 → 356; the single delta is this file |
| Code mutations | ✅ **0** — `mutation_classification.py` read only, byte-identical to HEAD |
| Configuration mutations | ✅ **0** |
| Registry mutations | ✅ **0** — `mutation-governance-boundary.json` parsed read-only, 27,127 bytes, byte-identical |
| Certification mutations | ✅ **0** |
| Identity mutations | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys |
| Ownership mutations | ✅ **0** — `assignments` remains `{}` |
| Precedence changes | ✅ **0** — `R-01…R-09` remain at precedence 1…9 |
| Predicate changes | ✅ **0** — `RULE_PREDICATES` remains `R-01…R-08` |
| Implementation executed | ✅ **0** |
| Classification engine invoked | ✅ **0** — populations computed by `git ls-files` plus pure string evaluation; the engine was not imported |
| `register.sh` invocations | ✅ **0** |
| Commits | ✅ **0** |
| Root causes closed | ✅ **0** — `RC-1` remains OPEN |
| Blockers discharged | ✅ **0** — `AG-2b` remains OPEN |
| Authorities vested | ✅ **0** |
| Closure claimed | ✅ **NONE** |

---

*This determination changed no predicate, no precedence and no declaration. It characterises the R-08 / R-09 conflict by measurement: R-09's six declared criteria are R-08's five plus one, so R-09 is a strict subset by the form of the declaration, and over 6,188 tracked paths the intersection difference `R-09 \ R-08` is zero while 92 subjects sit inside both. The register pre-refused the cheapest fix — `unique` states that ordering is "never a substitute for disjointness" — and it demonstrates the correct one twice, since R-08 already carries `non-generated` to stay clear of R-04 and R-06 carries `non-executable` to stay clear of R-07. Eight of nine predicate pairs are disjoint by an explicit criterion; R-08 / R-09 is the only exception, so Option A completes an established pattern rather than introducing one. Three further findings: the declared token list is lowercase against uppercase filenames, which swings R-09's population between 1 and 92 on a detail the declaration never states; Class 8 documents an evaluation order the register does not implement; and the upstream claim that R-09 governs 127 of the 192 Group B subjects does not survive measurement, since only 1 of those 228 pages carries an analysis token and all 228 are untracked and so fail R-09's third criterion. The deciding authority is located, the decision needs no constitutional act, and six of its seven conditions rest with one owner. Nothing was implemented, no root cause closed and no closure claimed. The single repository mutation is the creation of this file.*

**END DETERMINATION — R-09 ⊂ R-08 PROVEN AND MEASURED · 5 OPTIONS ANALYSED · OPTION A CANONICAL · 4 INTERNAL INCONSISTENCIES · 1 UPSTREAM FIGURE CORRECTED · AG-2b LOCATED AND OPEN, NO CONSTITUTIONAL DEPENDENCY · VERDICT CONDITIONALLY READY · ZERO MUTATIONS PERFORMED · NO CLOSURE CLAIMED · STOPPED AFTER ARTIFACT CREATION.**
