# UCOS Ω∞ — UNIVERSAL IDENTITY ARBITRATION EXECUTION READINESS DETERMINATION

**May the arbitration model be executed? — converting the UIA model into an execution decision, and measuring every condition it depends on**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-EXECUTION-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Arbitrates no subject, mints no identity, retires none, supersedes none, declares no map, opens no register, and authorizes no act. The sequence in §14 is a proposal; §13's preconditions must be discharged by the authorities named there before a single subject may be arbitrated. |
| Mode | ANALYSIS ONLY · **NO IDENTITY CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Baseline working tree | 349 `git status --porcelain` lines — 38 tracked-modified, 311 untracked. **Pre-existing; not produced by this determination.** |
| Predecessor | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-DETERMINATION.md` — model **SPECIFIED · NOT ADOPTED · ZERO SUBJECTS ARBITRATED** |
| Subject | Execution readiness of the `CIS-0…5` / `MIG-1…7` / `CR-1…6` model over the measured population of **217** dual-identity subjects |
| Law read | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` (`AIF-L01…L24`) · `00-MASTER/UIS-001/uis-declaration.json` (`UIL-01…`) · `00-BOOK/DATA/constitutional-authority-alignment.json` · `00-BOOK/DATA/mutation-governance-boundary.json` · `00-MASTER/UCOS-UGA-001/uga-declaration.json` · `AUTH-INF-001` (`IL-INF-06`, `IL-INF-07`) · `UCKP-INV-14` |
| Method | Re-measurement of the population at this baseline; source reading of every mechanism the model depends on (`uga_engine.py`, `ukb.py`, `mutation_classification.py`, `mutation_class_extension.py`, `uis_engine.py`); **read-only execution** of `uga_engine.py gate`; reference-counting of every affected identifier across the tracked corpus |
| Readiness states | READY · CONDITIONAL · BLOCKED · PROHIBITED |
| Dimensions assessed | **9** — 0 READY · 3 CONDITIONAL · 6 BLOCKED · 0 PROHIBITED |
| Findings raised | **13** (`UIAR-1`…`UIAR-13`) · 4 CRITICAL · 5 HIGH · 3 MEDIUM · 1 LOW |
| **Verdict** | **NOT READY — EXECUTION PROHIBITED AT THIS BASELINE. 0 of 217 subjects may be arbitrated. 12 preconditions outstanding, 5 of them requiring an authority act no located party currently holds.** |

---

## 1. Objective, Method, and Standing Limitation

### 1.1 Objective

The predecessor determination answered *what* arbitration is: the canonical identity is the one
minted by the authority whose admission predicate the subject's currently governing class
satisfies (`CIS-2`), every other identity is retained and marked `SUPERSEDED-BY` it, and nothing
is ever deleted, edited, renumbered or reissued. It answered *by what law* (`AIF-L02`, `L06`,
`L13`, `L15`, `L16`, `L17`, `L20`, `L21`), *by whom* (three coordinating authorities), and it
stated plainly that the model **is not adopted and cannot be executed today**.

It did not measure how far from executable it is. A model that is one declaration away from
execution and a model that is twelve conditions away are both "not executable," and the
difference is the whole content of an execution decision.

This determination asks:

> **Can identity arbitration be executed safely, at this baseline, under AIF law? If not, what
> exactly must be true first, in what order, verified by what gate, reversible under what
> conditions, and accepted on what criteria?**

### 1.2 Method

Three disciplines, each chosen because asserting the answer instead of measuring it is how the
condition being arbitrated was produced in the first place:

1. **Re-measure the population rather than inherit it.** §2.2 recomputes the 217, the group
   split, the id sets, the categories and the page allocations directly from the ledger at this
   baseline. The predecessor's numbers are confirmed, not assumed — and one of them (the
   uncommitted status of Group B's canonical ids) turns out to carry a consequence the
   predecessor did not draw.
2. **Read every mechanism the model calls, in source.** `CIS-0` calls a classifier; `MIG-3`
   calls publishers; `MIG-4` names an engine run; `MIG-7` names measurements. Each was read at
   the line that implements it. Four of the six were found to be in a different state than the
   model presumes.
3. **Execute only what mutates nothing.** `uga_engine.py gate` is declared non-mutating,
   is guarded as such by `platform/tests/test_verification_purity.py`, and was run. Its result
   is §8's decisive measurement. `uga_engine.py run` was **not** executed and must not be —
   §8.3 explains why running it is itself the act the model forbids until `M-2` is done.

### 1.3 Standing limitation

`classify()` still returns `ERROR` for every subject in the repository (§4.3, re-measured).
Nothing below is a classification, an arbitration, an identity, or a certification of record.
**No identity was minted, retired, superseded, renumbered, arbitrated or resolved in producing
this determination**; `by_path` stands at 1,492, `by_object` at 4,914 and `by_observation` at 7,
before and after (§18).

### 1.4 What this determination deliberately does not do

It does not amend the `CIS`/`MIG`/`CR` model — the model is inherited intact and is not
reopened. It declares no `A(C)`. It does not decide the corpus-authority question §12.5 of the
predecessor referred to `UMB-003`. It does not commit, revert, stash or otherwise touch the 228
uncommitted corpus registrations that create Group B, and it does not recommend that anyone
else do so without the owner act §13 names. It resolves none of the ten `UIA` findings; it
adds thirteen readiness findings to them.

---

## 2. Baseline Evidence

### 2.1 Inherited, not re-derived

| # | Source | Inherited content |
|---|---|---|
| B-1 | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-DETERMINATION.md` | The arbitration model (`CIS-0…5`), migration rules (`MIG-1…7`), conflict rules (`CR-1…6`), validation criteria (`VC-1…13`), closure conditions (`CC-1…6`), and findings `UIA-1…UIA-10`, all **OPEN** |
| B-2 | `UCOS-OMEGA-INFINITY-UGA-REALITY-SYNCHRONIZATION-DETERMINATION.md` | `URS-2` (the 217), `URS-3` (stale certification), `URS-5` (`RETIRED` unemittable), `URS-6` (absorbing terminal is the minting mechanism), and synchronization steps `S-1…S-5` |
| B-3 | `00-MASTER/UIS-001/` | `UIS-F-001` (25 nonsource admissions), `UIS-F-003` (ungoverned namespaces), the plane/grammar crosswalk, and the 42-measure ledger measurement register |
| B-4 | `UCOS-OMEGA-INFINITY-UNIVERSAL-FOUNDATION-TRANSFORMATION-EXECUTION-READINESS-DETERMINATION.md` | The four-state execution vocabulary (READY · CONDITIONAL · BLOCKED · PROHIBITED), adopted here rather than re-invented; measurement `M-C` (mutation classification non-functional) |

### 2.2 Re-measured at this baseline

Every figure below was computed from repository state at `HEAD = bae59755` plus the standing
working tree, not taken on report.

```
id-ledger by_path / by_object / by_observation      1,492 / 4,914 / 7        (working tree)
  at HEAD                                           1,264 / 4,914 / 7
by_path ∩ by_object   worktree / HEAD                 217 / 25
by_observation ∩ by_path / ∩ by_object                  0 / 0
Group A (present at HEAD)                              25
  00-MASTER/ 13 · intelligence/ 11 · root pointer 1
  by_object category: EXDOC 12 · DATAOBJ 13
  by_path  category: MASTER 13 · INTELLIGENCE 11 · MCP001MASTER 1
  page ranges held by the corpus ids                   85 pages
  in artifacts.json (registered_docs)                  0 of 25
Group B (working tree only)                           192
  by_object category: EXDOC 189 · DATAOBJ 3
  by_path  category: 75 distinct namespaces
  .md / .json                                         189 / 3
  matching the R-09 GOVERNED_ANALYSIS filename rule    127 of 192
  page ranges held by the corpus ids                  866 pages
  in artifacts.json (registered_docs)                192 of 192
by_path categories across all 217                      78 distinct
uncommitted corpus registration standing in tree
  artifacts.json records         HEAD → tree      1,233 → 1,461   (+228)
  id-ledger by_path              HEAD → tree      1,264 → 1,492   (+228)
  page_cursor                    HEAD → tree      9,826 → 10,840  (+1,014)
  category_seq counters advanced                        88
UGA surfaces referencing the 217 by_object ids
  02-UNIVERSAL-OBJECT-REGISTRY.json                    217 occurrences
  03-AUDIT-UNIVERSE.json                               434 occurrences
  04-RELATIONSHIP-GRAPH.json                           868 occurrences
  total                                              1,519 occurrences
tracked files outside the UGA programme + the ledger
  referencing ANY of the 217 by_object ids                0
tracked files referencing the 217 by_path ids in
  UGA surfaces                                            0
uga_engine.py gate (read-only, executed)             FAILED — 2 blocking invariants
  UGA-INV-01 EVERY_OBJECT_HAS_UNIVERSAL_ID           7 violations
  UGA-INV-10 EVERY_MUTATION_HAS_AUDIT_EVENT          7 violations
  anonymous objects                                    7
UGA 07-CERTIFICATION.json                            verdict CERTIFIED · blocking_deviations []
  scope objects_governed / minted_by_this_programme   6,145 / 4,912
mutation classification
  RULE_PREDICATES implemented                         R-01…R-08  (8)
  rules declared                                      R-01…R-09  (9)
  validate_rule_coverage()                            ("rule 'R-09' is declared but no
                                                       predicate implements it",)
  classify() status for every subject                 ERROR
UIS-001 uis.json
  identities_multiple                                    0   (blocking law UIL-02, expect 0)
  recorded_identities / registered_identities        1,264 / 1,233
  nonsource_identity_admissions                         25
  identity_collisions / renumbered / reused / grammar  0 / 0 / 0 / 0
  gate                                                OPEN
  UIS-001 present in verify.sh                        NO  (Makefile target only)
alignment register REPOSITORY_OBJECT plane maps       ["by_path","by_object","by_observation"]
alignment register mint_markers                       ["category_seq"]
generated-artifact-registry entries                   345
  UGA canonical surfaces declared generated            10
  00-BOOK/DATA/id-ledger.json declared generated       NO — Recorded Truth
```

### 2.3 The three measurements that decide this determination

| # | Measurement | Result | Decides |
|---|---|---|---|
| **R-A** | `validate_rule_coverage(mutation-governance-boundary.json)` | `("rule 'R-09' is declared but no predicate implements it",)` → `classify()` = `ERROR` for **every** subject | `CIS-0` is unevaluable. Arbitration cannot begin for one subject, let alone 217 (§4) |
| **R-B** | `by_path` and `artifacts.json` at HEAD vs working tree | +228 registrations, +1,014 pages, 88 counters advanced, **uncommitted** | Group B's 192 canonical ids are not sealed admissions under `AIF-L14`. Supersession records would name unsealed identities (§5) |
| **R-C** | `python3 00-MASTER/UCOS-UGA-001/uga_engine.py gate` | **FAILED** — `UGA-INV-01` and `UGA-INV-10`, 7 anonymous objects | `M-3` (`uga_engine.py run`) is not a clean refresh: it is currently *required* to clear a failing gate, and it would mint 7 unrelated identities inside the arbitration act (§8) |

Everything below follows from these three, plus the source reading each dimension names.

---

## 3. Readiness Vocabulary

Adopted from `B-4` rather than re-derived, so two determinations do not create two scales.

| State | Meaning | What it licenses |
|---|---|---|
| **READY** | Every condition the dimension depends on is measured true at this baseline | The dimension imposes no precondition |
| **CONDITIONAL** | The mechanism exists and is sound, but its correct use depends on a condition another dimension must supply | Proceed only after the named condition holds |
| **BLOCKED** | A condition the dimension depends on is measured false, absent, or unevaluable | No act in this dimension may execute |
| **PROHIBITED** | Executing the dimension would itself violate a ratified law | Never executes in this form; requires a different act |

A dimension is **BLOCKED**, not CONDITIONAL, when the missing thing is a *fact about the
repository* rather than an *ordering*. "The declaration does not exist" is BLOCKED. "This must
follow that" is CONDITIONAL.

---

## 4. Dimension 1 — Authority Admission Map Readiness

**State: BLOCKED. The map `CIS-2` requires does not exist, both candidate vocabularies are unfit for it, and the classifier that would evaluate it returns `ERROR` for every subject in the repository.**

### 4.1 What `CIS-2` requires

```
CIS-2  ADMISSION.  Let A(C) be the authority whose declared admission predicate C(S)
       satisfies.  If exactly one iₖ ∈ I(S) was minted by A(C), iₖ is CANONICAL …
```

Two objects must exist before this sentence can be evaluated: `C(S)`, a governing class per
subject, and `A(C)`, a total mapping from class to admitting authority. The predecessor recorded
that `A(C)` is "not declared anywhere today" and called it *the single new declaration the model
requires*. Measurement shows the condition is worse than undeclared: **the two vocabularies
`A(C)` could be built over are each unfit, in different ways, and the function that computes
`C(S)` does not run.**

### 4.2 Candidate vocabulary 1 — the mutation classes

`00-BOOK/DATA/mutation-governance-boundary.json` declares nine mutation classes with an ordered,
total, fail-closed resolution (`R-01…R-09`) and a `governed_by` per class. It is the obvious
candidate and it is the one the predecessor's `CIS-0` cites. Measured against `A(C)`'s
requirements:

| Class | `governed_by` | Names a *minting* authority? |
|---|---|---|
| `CONSTITUTIONAL_TRUTH` | `UCOS-CMG-EXEC-000001` | No — a mutation gateway |
| `SOURCE` | `pre-commit → verify.sh → UCOS-RIB-001 → UCOS-AEE-001 → Phase 8 → Phase 9` | No — a chain of gates |
| `GENERATED_ARTIFACT` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9` | No |
| `EXCLUSION` | `UCOS-EXCLUSION-REGISTER-001 → UCOS-RIB-001 GATE-12` | No |
| `REPOSITORY_STATE` | `UCOS-RIB-001 GATE-02 / GATE-12` | No |
| **`CORPUS_REGISTRATION`** | **`REG-AUTO-001 → 00-BOOK/tools/register.sh (ukb.py build --mint)`** | **Yes — the only one** |
| `GOVERNED_DECLARATION` | *the owning programme authority declared by the artifact itself (owner-parameterised)* | No — a parameter, not a value |
| `AUTHORED_DOCUMENT` | *the authority the artifact declares of itself (owner-parameterised)* | No — a parameter |
| `GOVERNED_ANALYSIS` | *the authority the analysis declares of itself (owner-parameterised)* | No — a parameter |

Three properties disqualify it:

1. **`UCOS-UGA-001` appears in none of the nine.** The authority that minted 4,914 of the
   ledger's 6,413 identities — and one of the two identities every one of the 217 holds — has no
   class in the vocabulary `A(C)` would be built over. `A(C)` would be **non-total in its
   codomain**: it could never return the authority that is correct for Group A.
2. **The register says so itself.** `REG-AUTO-001`'s `does_not_govern` block, read verbatim:
   *"the `by_object` index of the same ledger, which `uga_engine.py` allocates and **which is
   not a declared mutation class**."* The one entry that names a minting authority explicitly
   disclaims the map that holds half the ledger.
3. **Three of nine classes return a parameter rather than an authority.** `authority_for()`
   (`platform/repository_intelligence/mutation_classification.py:241-246`) returns the
   `governed_by` string verbatim. For `GOVERNED_DECLARATION`, `AUTHORED_DOCUMENT` and
   `GOVERNED_ANALYSIS` that string is a *rule for finding an authority by reading the artifact*,
   not an authority. `A(C)` built on it would not be a function.

**`UIAR-1` (CRITICAL):** The mutation-class vocabulary cannot carry `A(C)`. `UCOS-UGA-001`
has no class in it; the one class that names a minting authority explicitly disclaims the
`by_object` map; and three of nine classes resolve to an owner-parameterised placeholder rather
than to an authority. `A(C)` over this vocabulary is neither total nor functional.

### 4.3 The classifier does not run

Even setting `A(C)` aside, `CIS-0` — *"Resolve `S`'s governing class `C(S)` by the declared,
ordered classification rules"* — is unevaluable at this baseline.

`00-BOOK/DATA/mutation-governance-boundary.json` declares nine rules. `RULE_PREDICATES`
(`mutation_classification.py:403-413`) implements eight. `validate_rule_coverage` refuses in
both directions, and `classify()` calls it first:

```python
problems = validate_rule_coverage(doc)
if problems:
    return ClassificationResult(subject.identity, "", "", "", ERROR, "; ".join(problems))
```

Measured at this baseline: `("rule 'R-09' is declared but no predicate implements it",)`. Every
subject therefore resolves to `ERROR` — not to `UNRESOLVED`, which `CIS-0` knows how to handle
by refusing, but to a *fault*, which it does not.

The cause is located. `platform/repository_intelligence/mutation_class_extension.py` (206 lines,
added by the Phase-2/Violation-4 work at `bae59755`) appends `GOVERNED_ANALYSIS_CLASS` and
`GOVERNED_ANALYSIS_RULE` to the boundary **JSON** and adds no predicate to `RULE_PREDICATES`. It
extended the declaration and not the implementation, and the two-sided coverage check — written
precisely to catch that — now fails closed over the whole repository.

The consequence for arbitration is sharper than "the classifier is down":

> **127 of the 192 Group B subjects are markdown files whose names match `R-09`'s own predicate
> — `(determination|analysis|assessment|execution|matrix|readiness|admission|blocker|gap)`.**

The class that would govern two-thirds of Group B is exactly the class whose predicate does not
exist. Repairing `classify()` globally is a precondition; and when it is repaired, the rule that
then fires for 127 subjects is one that has never been executed against a subject.

**`UIAR-2` (CRITICAL):** `classify()` returns `ERROR` for every subject because `R-09` is
declared without a predicate, so `CIS-0` cannot resolve `C(S)` for any of the 217. The
declaration-only extension that produced this condition also means that the rule governing
**127 of 192** Group B subjects has never been evaluated once.

### 4.4 Candidate vocabulary 2 — the UGA object classes

`00-MASTER/UCOS-UGA-001/uga-declaration.json` `object_classes` is the vocabulary that actually
determines which authority mints. It is total (`classify_object`'s final branch is
unconditional), it is implemented, and it already routes admission:

| Object class | `id_category` | `governed_by` |
|---|---|---|
| `DOCUMENT_ARTIFACT` | `null` | `UMB-IMP-001` — *"This programme registers NOTHING here"* |
| `EXECUTABLE_OBJECT` | `ENGINE` | `UCOS-UGA-001` |
| `TEST_OBJECT` | `TESTOBJ` | `UCOS-UGA-001` |
| `CONFIGURATION_OBJECT` | `CONFIG` | `UCOS-UGA-001` |
| `TOOLING_OBJECT` | `TOOLING` | `UCOS-UGA-001` |
| `DATA_OBJECT` | `DATAOBJ` | `UCOS-UGA-001` |
| `EXCLUDED_DOCUMENT` | `EXDOC` | `UCOS-UGA-001` |

This is `A(C)`, in substance, for seven classes and two authorities — and `epoch1_identity`
already executes it (`uga_engine.py:272-301`): a `DOCUMENT_ARTIFACT` has its identity **read**
from `by_path` and is never minted here; every other class mints into `by_object`.

Three defects stop it from being the declaration `CIS-2` may depend on:

1. **It is a programme's internal vocabulary, not a cross-authority register.** Adopting it as
   `A(C)` makes `uga_engine.classify_object` the arbiter of which authority owns a subject's
   identity — a single programme's Python function deciding a question that §14.5 of the
   predecessor routes to three authorities. `CIS-2` may not depend on a derivation performed by
   whoever implements it; it equally may not depend on one performed by a party to the dispute.
2. **It does not cover `by_observation`.** The third map's seven identities are minted by
   observing programmes (`UCOS-AEE-001`, `UCOS-RIB-001`, `UCCEP-000005`,
   `intelligence/realization`, `P0-FINAL-CLOSURE-002`) under keys of the form
   `<observer>::<subject>::<KIND>` — a keyspace that is not a path. Measured: `by_observation ∩
   by_path = 0` and `by_observation ∩ by_object = 0`, so it contributes no subject to today's
   217 — but `A(C)` must be total over the *plane*, not over today's overlap, or the first
   observation subject that also acquires a path identity lands in `CIS-3` with no admitting
   authority to emit a request to.
3. **It is keyed on the wrong side of the very dispute.** `classify_object`'s first test is
   `rel in registered_docs` — membership of `artifacts.json`. For Group B that set is exactly
   the 228 uncommitted registrations (§5). The class that determines the canonical identity is
   therefore a function of an unsealed transaction.

**`UIAR-3` (HIGH):** `A(C)` is derivable from `uga-declaration.json` `object_classes` for seven
classes and two authorities and is already implemented in `epoch1_identity`, but adopting it as
declared would make one programme's classifier the cross-authority arbiter, leaves
`by_observation`'s authority unmapped, and keys the decision on an uncommitted registration set.

### 4.5 Dimension verdict

| Requirement | State |
|---|---|
| `A(C)` declared | **ABSENT** |
| A vocabulary fit to carry it | **NONE of the two candidates** (`UIAR-1`, `UIAR-3`) |
| `C(S)` computable | **NO** — `classify()` = `ERROR`, repository-wide (`UIAR-2`) |
| Total over the three declared maps | **NO** — `by_observation` unmapped |
| Owner identified for the declaration | Mutation governance owner (`B-1` §14.5) — **unratified; `CH-4` stands** |

**BLOCKED.** Four independent conditions, of which two (`UIAR-1`, `UIAR-2`) are repository facts
and cannot be sequenced around.

---

## 5. Dimension 2 — 217 Identity Conflict Migration Readiness

**State: BLOCKED. The population is confirmed intact at 217, and 192 of the canonical identities the migration would name do not exist in Recorded Truth.**

### 5.1 The population is stable and re-measured

| | Group A | Group B | Total |
|---|---|---|---|
| Count | **25** | **192** | **217** |
| Present at HEAD | yes | no — working tree only | — |
| Canonical id under `CIS-2` | the `by_object` id | the `by_path` id | — |
| Superseded id under `CIS-2` | the `by_path` corpus id | the `by_object` `EXDOC`/`DATAOBJ` id | — |
| Superseding authority | corpus (`REG-AUTO-001` / `UMB-003`) | `UCOS-UGA-001` | — |
| `by_object` categories | `EXDOC` 12 · `DATAOBJ` 13 | `EXDOC` 189 · `DATAOBJ` 3 | `EXDOC` 201 · `DATAOBJ` 16 |
| `by_path` namespaces | `MASTER` 13 · `INTELLIGENCE` 11 · `MCP001MASTER` 1 | 75 distinct | 78 distinct |
| Page ranges held by the corpus id | 85 | 866 | 951 |
| In `artifacts.json` | 0 of 25 | 192 of 192 | — |

Group A is enumerable in full and was: ten `00-MASTER/` documents (`MCP-001…007`, `MCS-000`,
`README`, one checkpoint), `00-MASTER/UCOS-RECON-001`, two `00-MASTER/STATE/` JSON objects,
eleven `intelligence/UCOS-*.json` objects, and the root pointer
`MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md`. Every one is a `UIS-F-001`
`nonsource_identity_admission`, and `uis.json` still reports that count as exactly **25**.

### 5.2 The finding the predecessor recorded but did not draw

The predecessor recorded that Group B is *"working-tree-only."* Measured in full, that phrase
means:

```
artifacts.json     HEAD 1,233 records   →   tree 1,461 records   (+228, uncommitted)
id-ledger by_path  HEAD 1,264 entries   →   tree 1,492 entries   (+228, uncommitted)
page_cursor        HEAD 9,826           →   tree 10,840          (+1,014, uncommitted)
category_seq       88 counters advanced                          (uncommitted)
```

A complete `REG-AUTO-001` transaction — 228 permanent Universal IDs, 1,014 pages of the corpus
page layout, and 88 advanced sequence counters — **stands executed and uncommitted in the
working tree.** Group B's 192 dual identities are a subset of it.

`AIF-L14` is the law that makes this decisive:

> **`AIF-L14` Atomic Admission (realizes `REG-AUTO-001`).** *"An artifact exists only when its
> admission is sealed AND its derived projection re-verifies AND certification passes."*

None of the three conjuncts holds for the 192. The admission is not sealed (uncommitted). The
derived projection does not re-verify (`uga_engine.py gate` FAILS, §8). Certification does not
pass (the same gate; §11). Under the law the model is enforcing, **the 192 canonical identities
do not yet exist as admissions**.

The consequence for `MIG-2` is exact. A supersession record has the shape

```jsonc
{ "superseded_id": "UCOS-EXDOC-001457", "canonical_id": "UCOS-MASTER-000015", … }
```

and `canonical_id` for each of the 192 would name an identifier that exists only in an unsealed
transaction. If that transaction is ever discarded — and prior determinations record that the
38 tracked modifications *"must be isolated by their owning programmes before any wave can be
measured cleanly"* — the supersession records name 192 identifiers that no longer exist, in an
append-only store that forbids deleting them.

**`UIAR-4` (CRITICAL):** 192 of the 217 canonical identities are held only by an uncommitted
`REG-AUTO-001` transaction (+228 registrations, +1,014 pages, 88 counters). Under `AIF-L14`
their admission is not sealed, so arbitrating Group B now would write append-only supersession
records naming identifiers that Recorded Truth does not carry and that cannot be un-named if the
transaction is discarded.

### 5.3 Sealing is itself an unresolved act

The obvious response — commit the transaction first — is not available to this determination and
is not obviously available to anyone:

- The transaction was produced by `register.sh` / `ukb.py build --mint`, whose class is
  `CORPUS_REGISTRATION`, governed by `REG-AUTO-001`. Committing it is a corpus-authority act.
- Its 228 identities were minted with `first_seen` ISO wall-clock stamps already frozen in the
  working-tree ledger. Re-deriving them from HEAD is not guaranteed to reproduce the same
  identifiers: allocation advances `category_seq` in iteration order over the eligibility
  universe, and the universe today includes 311 untracked files.
- 65 of the 192 do **not** match `R-09`'s filename rule and would fall to `R-08`
  (`AUTHORED_DOCUMENT`) or earlier — a different class, a different owner-parameterised
  authority, and therefore potentially a different `A(C)` answer than the other 127.

**`UIAR-5` (HIGH):** Sealing Group B's admissions is a `CORPUS_REGISTRATION` act that no
determination has authorized, whose identifiers are not demonstrably reproducible if
re-derived, and which splits Group B across at least two mutation classes (127 `R-09` / 65
other) with different authority-resolution paths.

### 5.4 Group A is migration-ready in mechanism and blocked on a decision

Group A is the inverse case. Its 25 subjects are at HEAD, sealed, and stable under any engine
run: they are corpus-excluded by `00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES`, so
`classify_object` will keep returning `EXCLUDED_DOCUMENT`/`DATA_OBJECT` and `epoch1_identity`
will keep publishing the `by_object` id. No refresh changes them; no refresh is needed.

What blocks them is entirely the decision the predecessor referred to `UMB-003` (§12.5 there):
superseding 25 **corpus** identities that hold 85 pages of allocated page range and 25 records
in `artifacts.json`. Measured: those 25 paths hold **0** records in `artifacts.json`
(they are excluded), so the "record removal" concern is void — but the 85 pages are allocated
against `page_cursor` and remain so, since `MIG-1` forbids touching it and §14.3 forbids freeing
a range.

**`UIAR-6` (MEDIUM):** Group A carries no `artifacts.json` records (measured 0 of 25), so the
corpus-authority decision reduces to a narrower question than the predecessor framed: whether 85
pages of allocated page range may remain permanently bound to 25 superseded corpus identities.
That is decidable; it is not decided.

### 5.5 Dimension verdict

| Requirement | Group A | Group B |
|---|---|---|
| Population measured and stable | ✅ 25 | ✅ 192 |
| Canonical id exists in Recorded Truth | ✅ | ❌ (`UIAR-4`) |
| Admission sealed under `AIF-L14` | ✅ | ❌ |
| Superseding authority identified | ✅ corpus / `UMB-003` | ✅ `UCOS-UGA-001` |
| Owner decision recorded | ❌ (`UIAR-6`) | ❌ (`UIAR-5`) |
| `C(S)` computable | ❌ (§4.3) | ❌ (§4.3) |

**BLOCKED**, both groups, for different reasons — which is exactly `MIG-5`'s "one group, one
act" holding at the readiness layer too.

---

## 6. Dimension 3 — Supersession Model Readiness

**State: BLOCKED. `supersede` is a ratified transition with no implementation, no store, no schema and no declared home; two of the three carriers are viable and one requires amending the constitutional alignment register.**

### 6.1 What exists

| Element | State |
|---|---|
| `supersede` as a declared transition | **EXISTS** — `AIF-L15`, ratified, machine-validated in principle |
| An algorithm that decides it | **EXISTS in specification** — `CIS-0…5`, `AIF-L16`; **no implementation** |
| A record shape | **EXISTS in specification** — `B-1` §14.1; **no schema** |
| A store for the record | **DOES NOT EXIST** |
| Code that writes one | **DOES NOT EXIST** — no module in `engine/`, `platform/`, `00-BOOK/tools/` or `00-MASTER/` emits an identity supersession |
| A reader that resolves one | **DOES NOT EXIST** |
| A validator | **DOES NOT EXIST** |

`00-BOOK/SCHEMAS/` holds nineteen schemas (`artifact`, `page`, `relationship`, `signal`,
`finding`, …). None is an identity-transition schema, and the id-ledger itself has no schema in
that directory at all. The string `supersed*` appears across 25 tracked JSON and Python files,
in every case as prose about documents or requirements being superseded — never as an identity
transition record.

**`UIAR-7` (HIGH):** `supersede` is ratified law with zero implementation surface: no store, no
schema, no writer, no reader, no validator. `MIG-2`'s "every identity that ceases to be
published acquires a supersession record in the same act" has nothing to write the record into,
and `VC-5` has nothing to check.

### 6.2 The three candidate carriers, measured

**Carrier 1 — a new top-level key in `00-BOOK/DATA/id-ledger.json`.**

Positive, and it is the strongest single readiness signal in this determination:
`ukb.py:867-871` `load_ledger` loads the whole document and preserves unknown keys, and
`cmd_build` iterates the document eligibility universe rather than the ledger. `uga_engine.py`'s
own header records the same property as the reason `by_object` was safe to add:

> *"`ukb.py cmd_build` iterates the document eligibility universe (never the ledger), and
> `load_ledger` preserves unknown keys, so `by_object` is invisible to the corpus transaction by
> construction rather than by convention."*

A `supersessions` key would survive every corpus registration round-trip **by construction**,
exactly as `by_object` and `by_observation` did. There is precedent for the act (`by_execution`
→ `by_object` → `by_observation`; the plane has grown three times).

Negative, and it is decisive: `00-BOOK/DATA/constitutional-authority-alignment.json` declares
the `REPOSITORY_OBJECT` plane's maps as a **closed list of exactly three**:

```json
"maps": ["by_path", "by_object", "by_observation"]
```

and `uga_engine.py:987-996` recomputes `CAA-INV-04` by iterating `plane["maps"]` and reading
only the fields `universal_id` and `observation_id`. A fourth map is therefore either
(a) undeclared — in which case `CAA-INV-04`'s claim to be *"TOTAL over every id the ledger
holds"* silently becomes false, which is precisely the vacuity mechanism `UIA-2` and
`mutation-governance-boundary.json` have each already been found by; or (b) declared — in which
case the alignment register, a constitutional instrument, is amended as part of an identity
cleanup.

**Carrier 2 — a separate register file.**

Safe against the rival-mint detector: `identity_authority_resolution.mint_markers` is exactly
`["category_seq"]`, and `uga_engine.py:1013-1021` flags any `.json` other than the ledger holding
one. A supersession register carrying `superseded_id` / `canonical_id` / `transition` and **no
counter** holds no marker and is not a second mint. This is measured, not assumed.

But it inherits the same defect from the other side: identifiers recorded in a file outside the
declared plane are outside `CAA-INV-04`'s recomputation, and a supersession register is a
register of identity facts that the one identity invariant does not read.

**Carrier 3 — inside an existing identity's `history`.**

Excluded by the predecessor (§9.1) and confirmed here: `history` records 1,492 append-only
contiguous sequences and `UIL-13` measures `history_not_append_only: 0`. Writing a supersession
into it is editing Recorded Truth to record a correction — the defect being corrected.

### 6.3 Dimension verdict

| Requirement | State |
|---|---|
| Transition vocabulary ratified | ✅ `AIF-L15` |
| Record shape specified | ✅ `B-1` §14.1 |
| Store exists | ❌ |
| Store may be added without amendment | ❌ — Carrier 1 needs the alignment register amended; Carrier 2 leaves the records outside `CAA-INV-04` |
| Writer / reader / validator | ❌ / ❌ / ❌ |
| Free of rival-mint detection | ✅ measured (`mint_markers` = `["category_seq"]` only) |

**BLOCKED.** The carrier question is answerable — Carrier 1 with a declared amendment is the
only option that keeps `CAA-INV-04` total — but the answer is an amendment to a constitutional
instrument, which is an authority act, not an implementation task.

---

## 7. Dimension 4 — Alias Preservation Readiness

**State: CONDITIONAL. The blast radius is bounded and measured; reverse resolution survives; forward resolution from a superseded id to its successor has no mechanism.**

### 7.1 What "alias preservation" must mean here

Under `MIG-1` and `AIF-L17` nothing is deleted, so no identifier is ever unresolvable *in the
ledger*. What changes is which identifier the **publishers** carry (`MIG-3`). "Alias
preservation" is therefore the question: after arbitration, can a party holding a superseded
identifier still (a) find its subject, and (b) find its canonical successor?

### 7.2 (a) Reverse resolution — READY

For all 217, the `by_object` entry is retained verbatim (`MIG-1`), keyed **by path**. A holder
of `UCOS-EXDOC-001457` can recover `00-MASTER/MCP-001-MASTER-CONTEXT.md` by scanning the map,
before and after arbitration, unchanged. The same holds for the 25 `by_path` entries superseded
in Group A. No mechanism is required and none is at risk.

### 7.3 (b) Forward resolution — ABSENT

Nothing anywhere maps a Universal ID to a successor Universal ID. The repository has exactly one
alias mechanism on the identity planes, and it is a different one:

> `00-MASTER/UIS-001/03-IDENTITY-PLANE-AND-GRAMMAR-REGISTER.md`, P3 row: *"an authority-local
> admission ordinal rendered at mint, **preserved as a native-ID crosswalk alias**"* — implemented
> in `00-BOOK/tools/ukb.py` and `config.py`, declared by `UMB-004` §2: *"the Nomenclature Engine
> maintains the crosswalk while renaming a native ID never changes the durable identity."*

That crosswalk aliases a **native ID** (a human filename ordinal) to a **durable ID**. It is
`native → UID`. Arbitration needs `UID → UID`, on the same plane, which `AIF-L03` describes as
crosswalked-never-merged between planes and says nothing about within one. The existing
mechanism is the wrong direction and the wrong plane pair, and cannot be reused.

### 7.4 The blast radius, measured exactly

This is where the dimension earns CONDITIONAL rather than BLOCKED. Every occurrence of every
affected identifier was counted across the entire tracked corpus:

| Surface | Group B (192 ids) | Group A (25 ids) | Total |
|---|---|---|---|
| `00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json` | 192 | 25 | 217 |
| `00-MASTER/UCOS-UGA-001/03-AUDIT-UNIVERSE.json` | 384 | 50 | 434 |
| `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | 768 | 100 | 868 |
| `00-MASTER/UCOS-UGA-001/05-GOVERNANCE-INVARIANTS.json`, `07-CERTIFICATION.json` | 0 | 0 | 0 |
| `00-BOOK/DATA/id-ledger.json` | 192 | 25 | 217 |
| **Every other tracked file in the repository** | **0** | **0** | **0** |

**Not one tracked file outside the UGA programme directory and the ledger references any of the
217 `by_object` identifiers.** And symmetrically, the UGA surfaces reference **0** of the 217
`by_path` corpus identifiers today.

Three consequences:

1. The exposure is **1,519 occurrences in three files**, all three of which are declared
   `canonical_path` entries in `00-BOOK/DATA/generated-artifact-registry.json` and are therefore
   regenerable from the ledger (§10).
2. There is **no external consumer** to break. No determination, register, engine, test or
   config outside UGA holds one of these ids. The dangling-reference risk that would normally
   dominate an id migration is measured at zero.
3. Group B's 192 ids vanish from `01-EXECUTABLE-OBJECT-REGISTRY.json` entirely on the flip:
   `emit()` filters that surface to `identity_authority == "UCOS-UGA-001"`
   (`uga_engine.py:1716`), and after the flip those 192 entries carry `UMB-IMP-001`. The
   identifier ceases to appear in any published surface in one step.

**`UIAR-8` (MEDIUM):** No `UID → UID` alias mechanism exists on the durable plane; the only
located alias is P3's `native-ID → UID` crosswalk, which is the wrong direction. After
arbitration a superseded identifier is resolvable to its subject through the retained ledger
entry but not to its canonical successor through any mechanism, unless the supersession record
of §6 is built and is readable. **Blast radius measured: 1,519 occurrences across 3 regenerable
surfaces; 0 references outside the UGA programme and the ledger.**

### 7.5 Dimension verdict

| Requirement | State |
|---|---|
| Superseded id survives in the ledger | ✅ by `MIG-1` |
| Reverse resolution (id → subject) | ✅ measured, unaffected |
| Forward resolution (id → successor) | ❌ no mechanism (`UIAR-8`) |
| External consumers to migrate | ✅ **zero**, measured |
| Affected surfaces regenerable | ✅ 3 of 3 declared generated artifacts |

**CONDITIONAL** — on §6 producing a readable supersession record. Everything else in this
dimension is measured ready, and the bounded blast radius is the strongest argument that
arbitration, once its preconditions hold, is a small act rather than a large one.

---

## 8. Dimension 5 — UGA Refresh Dependency Readiness

**State: BLOCKED. The refresh `MIG-4` orders is currently a repair for a failing gate, and executing it would mint 7 unrelated identities in the same act that performs 192 supersessions.**

### 8.1 What the refresh does to the 192 — read in source, not inferred

`epoch1_identity` (`uga_engine.py:258-309`):

```python
if o["object_class"] == "DOCUMENT_ARTIFACT":
    # Governed by UMB-IMP-001. Read its identity; never mint one here.
    entry = doc_ids.get(rel)
    o["universal_id"] = entry["universal_id"] if entry else None
    o["identity_authority"] = "UMB-IMP-001"
    …
    continue
```

and `classify_object`'s first test is `rel in registered_docs`. For each of the 192 — all 192 of
which are now in `artifacts.json` — the next run therefore:

1. classifies the path `DOCUMENT_ARTIFACT` instead of `EXCLUDED_DOCUMENT`/`DATA_OBJECT`;
2. publishes the **`by_path` corpus id**, read from the ledger;
3. sets `identity_authority` to `UMB-IMP-001`;
4. **mints nothing** — the `by_object` branch is never reached;
5. **leaves the existing `by_object` entry in the ledger untouched**;
6. does **not** mark it `RETIRED` — `retired` is computed as `sorted(p for p in by_object if p
   not in live)` (line 308) and all 192 paths are live.

Step 6 is the exact orphan condition. The identifier is sealed, retained, referenced by nothing,
and recorded as nothing. `AIF-L13` — *"abort discards (no orphan identity)"* — forbids producing
it, and there is no code path in the engine that could emit a supersession instead. The
predecessor derived this; source reading confirms it line by line.

The reverse is also now established: **the flip mints zero identities for the 192**, so
arbitrating Group B is not a minting act and consumes no counter. That is a positive readiness
property and it matters for rollback (§10).

### 8.2 The refresh cannot currently be a clean act — measured

`python3 00-MASTER/UCOS-UGA-001/uga_engine.py gate` was executed at this baseline. It is
declared non-mutating (`build(mint=False)`, no `emit`), is guarded as such by
`platform/tests/test_verification_purity.py`, and the working tree was byte-identical before and
after (349 porcelain lines, unchanged).

Result:

```
GATE FAILED — 2 blocking invariant(s).
  ANONYMOUS OBJECTS: 7 — run `uga_engine.py run`
  UGA-INV-01  EVERY_OBJECT_HAS_UNIVERSAL_ID          7 violations
  UGA-INV-10  EVERY_MUTATION_HAS_AUDIT_EVENT         7 violations
```

The seven anonymous objects are the source files added by the Phase-1B/Phase-2/Phase-3 commits
at and before `bae59755`:

```
engine/ceu/context_binding.py
engine/tests/ceu/test_context_binding.py
engine/tests/context/test_req_28_extensibility.py
engine/tests/lineage/test_req_43_upeg_certification.py
engine/tests/uckp/test_phase_2_requirement_evolution.py
platform/repository_intelligence/mutation_class_extension.py
platform/tests/test_violation_4_mutation_extension.py
```

`UGA-INV-01` and `UGA-INV-10` are both `fails_closed: true` and both block. The engine's own
remediation string for `UGA-INV-01` is *"Run `uga_engine.py run` to mint identities for unminted
objects."*

This produces a coupling the model does not anticipate:

> **`M-3` is simultaneously (a) the step that publishes Group B's arbitrated canonical ids, and
> (b) the only available repair for two failing UGA invariants, and (c) an act that mints 7 new
> permanent Universal IDs for objects unrelated to arbitration.**

`MIG-5` says *"one group, one act, never as one bulk operation."* A run that arbitrates 192
subjects and mints 7 unrelated identities in one write of the ledger is precisely a bulk
operation, and it makes the arbitration act non-isolable: the 7 mints advance `category_seq`,
which is Recorded Truth, and cannot be separated from the arbitration afterwards.

Note also the ordering inside `cmd_run` (`uga_engine.py:1863-1876`): the ledger is persisted
first, then `build(mint=False)` re-derives, then surfaces are emitted. A failure between those
steps leaves the ledger advanced and the surfaces stale — a partial state `AIF-L13`'s
prepare/commit/abort atomicity does not cover, because the engine has no abort.

**`UIAR-9` (CRITICAL):** `uga_engine.py gate` FAILS at this baseline (`UGA-INV-01`,
`UGA-INV-10`, 7 anonymous objects), so the refresh `MIG-4` orders after `M-2` is also the
outstanding repair for a red gate. Executing it would mint 7 unrelated permanent identities
inside the arbitration act, violating `MIG-5`'s one-group-one-act rule and making the
arbitration write non-isolable in an append-only counter. The engine has no abort path between
its ledger write and its surface emit.

### 8.3 The one thing that is ready: the hold is enforceable

`MIG-4` requires that no producer run change a published identity before arbitration. That hold
is **structurally enforced today**, which is worth recording because so little else is:

- `verify.sh:436` invokes `uga_engine.py gate` and nothing else; the file contains exactly one
  reference to the engine (asserted by
  `platform/tests/test_constitutional_authority_alignment.py:311-312`).
- `platform/tests/test_verification_purity.py:321` names `"uga_engine.py run"` in its forbidden
  set with the reason *"mints UGA object identity (use `gate`)"*, and
  `test_verify_sh_declares_no_mutating_invocation` fails if it ever appears.
- No Makefile target, CI workflow or engine invokes `run`. `00-MASTER/UCOS-AEE-001/aee_engine.py:1618`
  emits it as *advice in a message string*, not as a call.

`uga_engine.py run` is therefore a deliberate manual act with no automated trigger. `MIG-4` can
be held indefinitely without adding a single guard.

### 8.4 Dimension verdict

| Requirement | State |
|---|---|
| Refresh semantics understood and verified in source | ✅ (§8.1) |
| Refresh mints nothing for the 192 | ✅ measured |
| Refresh is isolable to arbitration | ❌ — 7 unrelated mints (`UIAR-9`) |
| Refresh leaves no orphan | ❌ — 192 orphans by construction, no supersession emitter |
| Gate green before the act | ❌ — FAILS, 2 blocking invariants |
| `MIG-4` hold enforceable | ✅ — no automated invocation exists |

**BLOCKED.**

---

## 9. Dimension 6 — Identity Invariant Measurement Readiness

**State: BLOCKED. The blocking law for this exact condition exists and is wired to a vacuous measure over 19.7% of the population, in a programme absent from the verification path — and repairing the measure turns a standing OPEN gate red before arbitration can be executed to close it.**

### 9.1 The law exists and blocks

`00-MASTER/UIS-001/uis-declaration.json` `laws`:

```json
{ "id": "UIL-02", "law": "Singular Identity",
  "invariant": "No object SHALL possess more than one permanent UID.",
  "measurable": true, "measure": "identities_multiple",
  "comparator": "==", "expect": 0, "blocking": true }
```

This is not a gap in legislation. `UIL-02` is a declared, measurable, blocking law naming
precisely the condition the 217 are. `VC-3` of the predecessor asked for an invariant to be
created; measurement shows the invariant already exists and is **already blocking**. What is
missing is a measure that measures it.

### 9.2 Three layers of vacuity, each measured

**Layer 1 — the measure's population.** `uis_engine.py:317-322` builds `path_to_ids` from
`records`, which is `artifacts.json`'s artifact collection. It never reads `by_object`.
`identities_multiple` = **0**, truthfully and uninformatively (`UIA-2`).

**Layer 2 — the programme's population.** `uis.json` reports `recorded_identities: 1264` and
`registered_identities: 1233` — the HEAD corpus. The identity ledger holds **6,413**. The
programme that owns identity conformance measures **19.7%** of the identity population, and the
80.3% it does not measure is exactly the `by_object` map that holds one of the two identities
every one of the 217 subjects carries.

**Layer 3 — the verification path.** `UIS-001` appears in `Makefile` (targets `uis`,
`uis-gate`, `uis-self`, `--check-determinism`, `--check-write-scope`, …) and **nowhere in
`verify.sh`**. `uis.json` records `gate: OPEN`. No blocking verification stage measures identity
conformance at all.

**`UIAR-10` (CRITICAL):** `UIL-02` is a declared blocking law for exactly this condition, wired
to a measure that reads one register (`identities_multiple` = 0), inside a programme whose whole
measured population is 1,264 of 6,413 identities (19.7%), which no stage of `verify.sh` executes.
`MIG-7` ("measure before and after") and `VC-5`/`VC-6`/`VC-7`/`VC-10` have no instrument that
can see the subject of the measurement.

### 9.3 The trap in repairing it

`VC-4` requires `identities_multiple` be re-scoped to quantify over subjects across all maps.
Doing so is a small change — the same `path_to_ids` construction over the union of the three
declared maps. Its consequence is not small:

```
identities_multiple : 0 → 217
UIL-02              : blocking, expect == 0  →  FAILS
uis.json gate       : OPEN → CLOSED
UIS-001 determination : IDENTITY-CONFORMANCE-BOUND → breached
```

So the repair that makes arbitration verifiable is also the act that converts a standing green
identity-conformance gate into a red one, before a single subject can be arbitrated to close it.
That is not a reason to skip it — a gate that is green because it looks in the wrong place is
`UIA-2`'s finding, not an asset — but it is a sequencing fact the migration plan must state
rather than discover: **there is a window, bounded by `X-3` and `X-8` in §14, during which
`UIS-001` is measurably non-conformant by design.**

**`UIAR-11` (HIGH):** Re-scoping `identities_multiple` per `VC-4` moves it from 0 to 217 and
fails the blocking law `UIL-02`, closing `UIS-001`'s currently-OPEN gate. Measurement repair must
therefore precede arbitration and will leave the programme red for the whole migration window;
the alternative — arbitrating first and measuring after — makes `MIG-7`'s before-measurement
impossible and is refused.

### 9.4 What is measurable today

Not everything is missing. These `MIG-7` / `VC-6` / `VC-7` quantities are measurable at this
baseline with existing instruments and are recorded here as the pre-arbitration baseline:

| Quantity | Instrument | Value |
|---|---|---|
| `by_path` / `by_object` / `by_observation` | ledger | 1,492 / 4,914 / 7 |
| `category_seq` counters | ledger | 88 advanced vs HEAD |
| `page_cursor` | ledger | 10,840 |
| identifier collisions | `uis.json`, `CAA-INV-04` | 0 / 0 |
| identities renumbered / reused / altered | `uis.json` | 0 / 0 / 0 |
| grammar failures | `uis.json` | 0 |
| history not append-only | `uis.json` (`UIL-13`) | 0 |
| `CAA-INV-04` population | `uga_engine.py gate` | 6,413, PASS |
| registry identities absent from ledger | `uis.json` | 0 |

**Eight of the nine `MIG-7` quantities are measurable now. The ninth — one canonical identity per
subject — is the one the migration exists to establish.**

### 9.5 Dimension verdict

**BLOCKED.** The law is ready; the measure is vacuous; the programme is out of the verification
path; and the repair is itself a gate-reddening act that must be sequenced explicitly.

---

## 10. Dimension 7 — Rollback Readiness

**State: CONDITIONAL. Rollback is asymmetric — the published surfaces are fully recoverable, the ledger is not recoverable by any lawful means once written, and the only isolation boundary available today is entangled with 228 uncommitted registrations.**

### 10.1 The asymmetry, established from the registries

| Object | Class | Recoverable how |
|---|---|---|
| `00-MASTER/UCOS-UGA-001/00-EXISTENCE-INVENTORY.json`, `01`, `02`, `03`, `04`, `05`, `07`, `08`, `00-UGA-DASHBOARD.md` — **10 canonical surfaces** | `GENERATED_ARTIFACT` (`R-04`), declared `canonical_path` in `generated-artifact-registry.json` | **Regeneration.** Restore the ledger, re-run the producer. Byte-identical by the determinism contract (no wall clock) |
| `00-BOOK/DATA/id-ledger.json` | `CORPUS_REGISTRATION` (`R-03`); **not** a declared generated artifact | **Recorded Truth.** Not regenerable, and not editable |
| `00-BOOK/DATA/artifacts.json` | `CORPUS_REGISTRATION` (`R-03`) | Same |
| A written supersession record | (no class — the structure does not exist) | **Not rollback-able at all** (§10.2) |

The determinism contract is what makes the first row real rather than hopeful:

> *"No output of this engine contains a wall clock. … Re-running the engine with no repository
> change is a no-op on disk."*

So surface rollback is: restore the ledger to its prior bytes, run the producer, compare. Not a
patch — a recomputation.

### 10.2 A recorded supersession has no rollback, by law

`AIF-L17`: *"No deletion or edit of Recorded Truth; correction is a new event."* `CR-5`:
*"A `CIS-2` re-run producing a different canonical id than the recorded one is a CONTESTED case
requiring a new `AIF-L15` transition. It is never applied silently."*

Together these mean the migration has a **point of no return** with a precise location: the
first byte of the first supersession record. Before it, everything is recoverable by
regeneration and `git checkout`. After it, "rollback" does not exist as a concept — only
forward-only compensation: a second, recorded `AIF-L15` transition that supersedes the
supersession, leaving both events permanently in the record.

This is not a defect. It is the law working. But it must be stated as a rollback *condition*
rather than discovered as a surprise, because a migration plan that promises rollback after
`X-6` is promising something `AIF-L17` forbids.

### 10.3 The isolation boundary is entangled

The natural rollback boundary — `git checkout -- <paths>` — is unavailable in the form the
migration would need it. `00-BOOK/DATA/id-ledger.json` and `00-BOOK/DATA/artifacts.json` are
**already modified** in the working tree, carrying the 228 uncommitted registrations (§5.2).
Therefore:

- `git checkout -- 00-BOOK/DATA/id-ledger.json` after a failed arbitration discards the
  supersession records **and** the 228 registrations **and** the 1,014 pages **and** the 88
  advanced counters — including the 192 canonical identities Group B's arbitration was about.
- `git stash` on those paths has the same effect for the duration of the stash, and re-applying
  it after any other write to the same files is a merge, not a restore.
- Committing the 228 first to create a clean boundary is the `CORPUS_REGISTRATION` act
  `UIAR-5` records as unauthorized.

**There is no path-level rollback that isolates arbitration from the standing uncommitted
transaction.** A safe rollback boundary must be *created* before `X-4`, and creating it is
itself the sealing act of `UIAR-4`.

**`UIAR-12` (HIGH):** No rollback boundary isolates arbitration from the 228 uncommitted corpus
registrations, because both write the same two files. Any `git`-level revert of an arbitration
failure also discards the 192 canonical identities the arbitration was performed over. The
boundary must be established by sealing (`P-4`) before any arbitration write, and after the first
supersession record no rollback exists in any form — only forward-only compensation under
`AIF-L17`.

### 10.4 What is genuinely reversible, and it is more than expected

Two properties measured in this determination make the *pre-record* window unusually safe:

1. **The flip mints nothing for the 192** (§8.1). Group B's arbitration consumes no counter and
   creates no new identity. Undoing the *publication* is a pure regeneration.
2. **Zero external consumers hold the affected ids** (§7.4). Rolling back the published surfaces
   restores a state no other artifact ever observed, so no third party carries a stale reference
   to reconcile.

The dangerous step is not the flip. It is the record.

### 10.5 Dimension verdict

| Requirement | State |
|---|---|
| Published surfaces recoverable | ✅ regeneration, 10 of 10 declared generated |
| Ledger recoverable | ⚠️ only by `git`, only while a clean boundary exists |
| Supersession record reversible | ❌ **never** — `AIF-L17`, by design |
| Isolation boundary available today | ❌ (`UIAR-12`) |
| External reconciliation needed on rollback | ✅ none — 0 consumers |
| Point of no return located | ✅ first supersession record (`X-5`) |

**CONDITIONAL** — on the sealing act that creates the boundary.

---

## 11. Dimension 8 — Certification Impact

**State: BLOCKED. The certification the migration must recompute currently asserts a verdict its own live gate contradicts, and cannot be recomputed to that verdict until a defect unrelated to arbitration is repaired.**

### 11.1 What the certification says, and what the gate says

`00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json`, verbatim at this baseline:

```json
{ "verdict": "CERTIFIED",
  "blocking_deviations": [],
  "declared_open": [],
  "proof": { "existence_digest": "ea83747b…", "identity_digest": "14005b62…",
             "registry_digest": "5dda706a…", "graph_digest": "c34482f0…",
             "invariant_digest": "53a2be24…" },
  "scope": { "objects_governed": 6145, "minted_by_this_programme": 4912,
             "corpus_bytes_touched": 0 } }
```

`uga_engine.py gate`, executed at the same baseline: **FAILED**, two blocking invariants, seven
violations each (§8.2). `blocking_deviations: []` is false as of this measurement. `URS-3`
recorded the certification as stale; it is now measurably contradicted, not merely stale.

### 11.2 What arbitration does to it

All five digests are computed over surfaces that carry the published identifier. Arbitration
changes the published identifier for 192 of 6,145 governed objects, so:

| Digest | Computed over | Moves? |
|---|---|---|
| `existence_digest` | `00-EXISTENCE-INVENTORY.json` (object classes) | **Yes** — 192 objects change `object_class` |
| `identity_digest` | identity assignments | **Yes** — 192 change published id and `identity_authority` |
| `registry_digest` | `02-UNIVERSAL-OBJECT-REGISTRY.json` | **Yes** — 192 entries re-key |
| `graph_digest` | `04-RELATIONSHIP-GRAPH.json` | **Yes** — 868 occurrences re-key |
| `invariant_digest` | `05-GOVERNANCE-INVARIANTS.json` | **Yes** — counts change |

Five of five. `UIA-9` established this; measurement confirms the surfaces and quantifies them.

The constitutional-plane consequence is unchanged and remains lawful: `uga_projection.py` mints
`UCKO(namespace=REPOSITORY_NAMESPACE, local_name=entry["universal_id"])`, and the alignment
register's `derivation` carries the identifier through verbatim into
`urn:ucos:ucko:ucos-repository:<UCOS-ID>`. A changed input to a pure, total, injective function
yields a changed output; `AIF-L03` permits it; no recorded identity is mutated. Both
`EXCLUDED_DOCUMENT` and `DOCUMENT_ARTIFACT` are mapped in `_CATEGORY_MAP`, so no
`UnrecognisedUGAValueError` results.

### 11.3 The law is ready; the sequence is not

`AIF-L21` and `AIF-L01` settle *how*: the standing `CERTIFIED` verdict is an immutable
historical attestation over the population it names and is retained unamended; a new current
status is recomputed into a distinct store. `CR-INF-011` agrees — *certification closes scope,
never evolution*. `MIG-6` states it. Nothing here is unresolved in law.

What is unresolved is arithmetic: **`M-5` cannot produce `CERTIFIED`.** The recomputation runs
the same invariant set the gate just failed. Unless the 7 anonymous objects are minted (which is
`UIAR-9`'s coupled act) and `UGA-INV-10`'s audit events exist for them, the post-arbitration
current status is `FAILED`, and the migration terminates with a red certification that a reader
will attribute to arbitration rather than to a pre-existing defect it inherited.

**`UIAR-13` (HIGH):** UGA's certification asserts `CERTIFIED` with `blocking_deviations: []`
while its own gate fails two blocking invariants, so `MIG-6`'s "recompute, never amend" cannot
close: the recomputation returns FAILED for reasons that predate arbitration. The pre-existing
gate failure must be discharged before `X-8`, or arbitration inherits the blame for a defect it
did not cause.

### 11.4 What is not affected — measured

`certification.json` / `CERTIFICATION-REGISTRY.md` scope the corpus identity set, which
arbitration does not change: no `by_path` entry is added, removed or altered by any step. The
corpus certification surface is unaffected, confirming `UIA-9`'s bounding.

### 11.5 Dimension verdict

**BLOCKED** — not by arbitration's own effects, which are lawful and bounded, but by the
standing contradiction it would be executed underneath.

---

## 12. Dimension 9 — Future Identity Expansion Compatibility

**State: CONDITIONAL. The arbitration model is expansion-clean; the mechanisms it would be implemented on are not, and the gap is four edits, two of them to constitutional instruments.**

### 12.1 The binding constraints, restated

> **`UCKP-INV-14`** — *"Every vocabulary, adapter set and relationship class admits an unknown
> future member."*
> **`IL-INF-06`** — *"Every construct SHALL be read as admitting a next member **without
> rewrite, renumber, or migration**."*
> **`AIF-L24`** — pinned parameters *"widen append-only."*

### 12.2 The model passes

`CIS-0…5` reads no authority list, no map order, no `first_seen` and no rank. A fourth minting
authority declares an admission predicate; `A(C)` gains a mapping; the five rules are unchanged.
This is `B-1` §11.2's argument and it survives measurement: nothing in the rule text enumerates
an authority.

### 12.3 The mechanisms do not

Measured, one by one:

| Mechanism | Shape | Cost of a fourth authority / class |
|---|---|---|
| `constitutional-authority-alignment.json` `planes[REPOSITORY_OBJECT].maps` | closed list of **3** | **Amendment** to a constitutional instrument. `CAA-INV-04` iterates only this list (`uga_engine.py:987`), so an undeclared map is silently outside the one identity invariant |
| `uga_engine.py` `ID_CATEGORY` | closed `dict`, **6** keys, keyed by `object_class` | **Code change.** `ID_CATEGORY[o["object_class"]]` raises `KeyError` on an unmapped class — fails closed, but by exception, not by refusal |
| `uga_engine.py` `classify_object` | hard-coded `if`-chain, 7 branches | **Code change.** Total by construction, extensible only by editing |
| `mint_markers` | `["category_seq"]` | Declaration edit if a future mint uses a different counter name |
| `mutation-governance-boundary.json` `classification_rules.rules` | 9 ordered rules + `RULE_PREDICATES` | **Two-sided:** a rule needs a predicate and a predicate needs a rule. The current `ERROR` state (§4.3) is exactly what happens when only one side is extended |
| `uga-declaration.json` `finite_instance_tokens` | 8 tokens; rule: *"No object class, owner rule, id category, relationship kind or invariant … may be predicated on a finite instance"* | Does **not** constrain closed enumerations — it forbids naming `earth`, not forbidding a closed class list |

So the cost of admitting a fourth minting authority today is: **one constitutional amendment
(`planes.maps`), one declaration edit (`object_classes`), and two code edits (`ID_CATEGORY`,
`classify_object`)** — plus, for any new mutation class, the two-sided rule/predicate pair whose
one-sided extension is the live `R-09` defect.

`IL-INF-06` requires *no rewrite*. Renumbering: not required — passes. Migration: not required —
passes. Rewrite: **required, in four places** — fails.

### 12.4 The precedent cuts both ways

`uga-declaration.json` records the precedent honestly: *"`EXEC-REG-001` established
`by_execution` as an append-only map sharing the one identity authority. `by_object` is the same
construction for a second object class."* The plane has grown three times, so growth is
demonstrably possible. But each growth was a rewrite, and the third growth
(`by_observation`) is the one whose authority `A(C)` still cannot name (§4.4). **Expansion has
happened repeatedly and has left an unmapped authority behind each time** — which is the
condition arbitration exists to repair, recurring.

`VC-13` requires this be *exercised, not asserted*: a synthetic fourth authority admitted with a
declared predicate, `CIS-0…5` unamended. That exercise is not performed here and cannot be —
`CIS-0…5` has no implementation to exercise (§6.1).

### 12.5 Dimension verdict

| Requirement | State |
|---|---|
| Model admits an unknown authority without amendment | ✅ by construction |
| Ledger plane admits a fourth map without amendment | ❌ — closed list of 3 |
| Category assignment admits a new class without code change | ❌ — closed dict |
| Classifier admits a new class without code change | ❌ — hard-coded chain |
| Two-sided rule extension enforced | ✅ — and currently **failing** (`R-09`) |
| `VC-13` exercised | ❌ — nothing to exercise |

**CONDITIONAL.** The model is expansion-safe; the substrate costs four edits per expansion. This
does not block arbitration — it determines that `CC-6` cannot be claimed on arbitration's
completion.

---

## 13. Execution Readiness Verdict

### 13.1 The verdict

> # NOT READY — EXECUTION PROHIBITED AT THIS BASELINE
>
> **0 of 217 subjects may be arbitrated. 0 of 9 readiness dimensions are READY. 12 preconditions
> are outstanding, of which 5 require an authority act by a party that is not currently
> ratified. The migration has a located point of no return after which no rollback exists in
> any form.**

### 13.2 Dimension summary

| # | Dimension | State | Decisive measurement |
|---|---|---|---|
| 1 | Authority admission map | **BLOCKED** | `A(C)` absent; `UCOS-UGA-001` in 0 of 9 mutation classes; `classify()` = `ERROR` repository-wide |
| 2 | 217 conflict migration | **BLOCKED** | 192 canonical ids uncommitted; `AIF-L14` admission unsealed |
| 3 | Supersession model | **BLOCKED** | No store, schema, writer, reader or validator; the viable carrier needs a constitutional amendment |
| 4 | Alias preservation | **CONDITIONAL** | 1,519 occurrences in 3 regenerable surfaces; **0** external consumers; no `UID → UID` mechanism |
| 5 | UGA refresh dependency | **BLOCKED** | Gate FAILS; refresh couples 7 unrelated mints into the arbitration act |
| 6 | Identity invariant measurement | **BLOCKED** | `UIL-02` blocking, measure vacuous, programme covers 19.7%, absent from `verify.sh` |
| 7 | Rollback | **CONDITIONAL** | Surfaces regenerable; ledger entangled with 228 uncommitted registrations; record irreversible by law |
| 8 | Certification impact | **BLOCKED** | `CERTIFIED` + `blocking_deviations: []` contradicted by a failing live gate |
| 9 | Future expansion | **CONDITIONAL** | Model clean; substrate costs 1 amendment + 1 declaration + 2 code edits per authority |

**0 READY · 3 CONDITIONAL · 6 BLOCKED · 0 PROHIBITED.**

### 13.3 What may proceed now, and it is not nothing

Six acts are **EXECUTABLE** at this baseline because each is analysis, declaration or repair that
touches no identity:

| # | Act | Why it may proceed |
|---|---|---|
| `E-1` | Implement `R-09`'s predicate in `RULE_PREDICATES` | Repairs a defect that predates and is independent of arbitration; restores `classify()` for the whole repository |
| `E-2` | Re-scope `identities_multiple` per `VC-4` | Measurement only; changes no identity. Reddens `UIL-02` — intended (§9.3) |
| `E-3` | Add `UIS-001` to `verify.sh` as an observing stage | Read-only; the programme already guards its own write scope |
| `E-4` | Draft `A(C)` as a declaration for the mutation-governance owner to ratify | A proposal is not an authority act |
| `E-5` | Mint identities for the 7 anonymous objects and record their audit events | `UGA-INV-01`/`UGA-INV-10` repair; independent of the 217; **but see `P-6` — it must precede, not accompany, arbitration** |
| `E-6` | Specify the supersession record schema and its carrier | Specification only |

None of the six arbitrates a subject. All six are preconditions.

### 13.4 What is PROHIBITED

| Act | Prohibited by |
|---|---|
| Arbitrating any subject before `A(C)` is declared and `classify()` runs | `AIF-L16` — ambiguity fails closed; `CIS-0` cannot even refuse, it faults |
| Writing a supersession record naming an uncommitted canonical id | `AIF-L14`, `AIF-L17` — an unsealed admission recorded irreversibly |
| Running `uga_engine.py run` before Group B is arbitrated | `MIG-4`, `AIF-L13` — 192 orphan identities as a refresh side effect |
| Writing a supersession into an existing identity's `history` | `AIF-L17`, `UIL-13` |
| Recording a supersession as a `RETIRED` lifecycle transition | `URS-5`, `B-1` §14.3 — the subject has not left version control |
| Amending the standing `CERTIFIED` attestation | `AIF-L21`, `AIF-L01` — recompute into a distinct store, never edit |
| Resolving a `CIS-0`/`CIS-3`/`CIS-4` refusal by choosing the older, newer or more-referenced id | `CR-1`…`CR-3`, `AIF-L20` |

---

## 14. Preconditions

Twelve, each with an owner, a discharge test and a dependency. **P-1 … P-12 are the complete set;
no subject may be arbitrated while any one is open.**

| # | Precondition | Owner | Discharge test | Depends on |
|---|---|---|---|---|
| **P-1** | `R-09` has a predicate; `validate_rule_coverage()` returns `()` | Mutation governance owner + platform | `classify()` returns `CLASSIFIED` or `UNRESOLVED`, never `ERROR`, for a sample spanning all nine classes | — |
| **P-2** | `C(S)` is resolved and recorded for all 217 subjects | Mutation governance owner | 217 classifications recorded; count by class published; `UNRESOLVED` count stated, not zero-assumed | `P-1` |
| **P-3** | `A(C)` is declared: total over the class vocabulary **and** over the three ledger maps, functional (no owner-parameterised value), fail-closed on `UNRESOLVED`, and naming `UCOS-UGA-001` and the observation authorities explicitly | Mutation governance owner, ratified | Every class resolves to exactly one *minting* authority; `by_observation`'s authority is named; the declaration is a register, not a programme's code | `P-1`, `P-2` |
| **P-4** | The 228 uncommitted corpus registrations are **sealed** — committed under `REG-AUTO-001` — or formally discarded | Corpus authority (`REG-AUTO-001` / `UMB-003`) | `git status` shows `id-ledger.json` and `artifacts.json` clean; `by_path` = 1,492 at HEAD; a clean rollback boundary exists | — |
| **P-5** | Group A's disposition is decided: whether 85 pages of allocated range may remain bound to 25 superseded corpus identities | Corpus authority via `UMB-003` | A recorded decision citing `UIS-F-001`; `MIG-1`'s "`page_cursor` byte-unchanged" restated as accepted | — |
| **P-6** | `uga_engine.py gate` **PASSES** — the 7 anonymous objects are minted and audited in an act that carries **no** arbitration | `UCOS-UGA-001` | Gate exits 0; `UGA-INV-01`/`UGA-INV-10` violations = 0; the run is committed separately and named as unrelated to arbitration | — |
| **P-7** | The supersession store exists: a declared carrier, a schema, and — if inside the ledger — an amendment to `planes[REPOSITORY_OBJECT].maps` so `CAA-INV-04` remains total | Identity authority + constitutional alignment owner | The store is readable; `CAA-INV-04` measures the same or a larger population and still PASSES | — |
| **P-8** | `CIS-0…5` is implemented as a pure function and proven so | Platform, under the identity authority | Same subject, same commit, same answer across a fresh and a bootstrapped interpreter; no clock, no map order, no `first_seen` read | `P-3`, `P-7` |
| **P-9** | `identities_multiple` (or a successor invariant) quantifies over subjects across all three maps | `UIS-001` | The measure returns **217** at the pre-arbitration baseline; `UIL-02` fails; the failure is recorded as expected and time-boxed to the migration window | — |
| **P-10** | `UIS-001` executes in the verification path as an observing stage | Verification owner | `verify.sh` names `uis_engine.py --gate`; `test_verification_purity` still passes | `P-9` |
| **P-11** | The `MIG-7` pre-arbitration measurement set is recorded and committed | `UIS-001` + `UCOS-UGA-001` | Nine quantities recorded at a named commit (§9.4 supplies eight; `P-9` supplies the ninth) | `P-9`, `P-4` |
| **P-12** | The three coordinating authorities named in `B-1` §14.5 are ratified and have each accepted their act | Constitutional authority | A recorded acceptance per authority; `CH-4`'s "no located competent ratifier" is discharged for these three | — |

### 14.1 Precondition dependency structure

```
P-1 ──▶ P-2 ──▶ P-3 ─────────────┐
                                 ├──▶ P-8 ──┐
P-7 ─────────────────────────────┘          │
                                            ├──▶ ARBITRATION MAY BEGIN
P-4 ──▶ P-11 ◀── P-9 ──▶ P-10               │
  │                                         │
  └──▶ (rollback boundary)                  │
P-5 ────────────────────────────────────────┤   (Group A only)
P-6 ────────────────────────────────────────┤
P-12 ───────────────────────────────────────┘
```

Five preconditions have no dependency and may be discharged in parallel today: `P-1`, `P-4`,
`P-6`, `P-9`, `P-12`. Five require an authority act that `CH-4` records as currently
unavailable: `P-3`, `P-4`, `P-5`, `P-7`, `P-12`.

---

## 15. Migration Sequence

The predecessor's `M-0…M-6` is refined into an executable sequence with a gate between every
step. Each step names what it writes, what must be true to enter, and what must be true to
leave. **Steps are numbered `X-` to distinguish them from `B-1`'s `M-` steps, which they
supersede as the execution form.**

```
X-0  PREPARE — no identity is touched
     enter:  —
     act:    P-1 (R-09 predicate), P-6 (mint the 7 anonymous, commit separately),
             P-9 (re-scope identities_multiple), P-10 (UIS in verify.sh)
     writes: platform/repository_intelligence/mutation_classification.py
             00-BOOK/DATA/id-ledger.json  (7 mints — UGA authority, NOT arbitration)
             00-MASTER/UIS-001/uis_engine.py, verify.sh
     leave:  G-1, G-2

X-1  SEAL — the rollback boundary is created
     enter:  G-1
     act:    P-4 — the corpus authority commits or discards the 228 registrations
     writes: 00-BOOK/DATA/id-ledger.json, 00-BOOK/DATA/artifacts.json  (commit only)
     leave:  G-3

X-2  DECLARE — A(C) enters the register
     enter:  G-3
     act:    P-2, P-3 — classify all 217; declare and ratify A(C)
     writes: a new or amended authority register (NOT the ledger)
     leave:  G-4

X-3  BUILD — the supersession store and the selection function
     enter:  G-4
     act:    P-7, P-8 — carrier + schema + CIS-0…5 implementation
     writes: the declared carrier (empty), constitutional-authority-alignment.json if
             the carrier is a ledger map
     leave:  G-5

X-4  MEASURE — the before-set
     enter:  G-5
     act:    P-11 — record the nine MIG-7 quantities at a named commit
     writes: a measurement record
     leave:  G-6                              ◀── LAST FULLY REVERSIBLE POINT

X-5  ARBITRATE GROUP B — 192 supersessions recorded
     enter:  G-6, and P-12 accepted by UCOS-UGA-001
     act:    CIS-2 over 192; write 192 supersession records naming the by_path id
             canonical and the by_object EXDOC/DATAOBJ id superseded
     writes: the supersession store ONLY.  by_path, by_object, by_observation,
             category_seq, page_cursor: byte-unchanged
     leave:  G-7                              ◀── POINT OF NO RETURN (§10.2)

X-6  REFRESH — publication follows the record
     enter:  G-7
     act:    uga_engine.py run.  192 flip to DOCUMENT_ARTIFACT and publish the corpus
             id — now the recorded consequence of X-5, not a side effect
     writes: 10 UGA canonical surfaces.  Ledger: 0 mints (measured, §8.1)
     leave:  G-8

X-7  ARBITRATE GROUP A — 25 supersessions recorded
     enter:  G-6 and P-5 and P-12 accepted by the corpus authority
             (independent of X-5/X-6; may run in parallel once P-5 exists)
     act:    CIS-2 over 25; canonical = the by_object id; superseded = the corpus id
     writes: the supersession store ONLY
     leave:  G-9

X-8  RECERTIFY — recompute, never amend
     enter:  G-8, G-9
     act:    MIG-6 — retain the standing attestation; compute a new current status
             into a distinct store
     writes: a new certification record.  07-CERTIFICATION.json's prior content is
             retained as historical attestation
     leave:  G-10

X-9  RE-MEASURE AND CLOSE
     enter:  G-10
     act:    MIG-7 after-set; assert §17's acceptance criteria; run a second
             arbitration pass and compare bytes (CR-5 idempotence)
     writes: a measurement record
     leave:  ACCEPTANCE
```

### 15.1 Ordering constraints that are measured, not preferred

| Constraint | Source |
|---|---|
| `X-0` before everything | `classify()` = `ERROR` makes every later step unevaluable (§4.3) |
| `P-6` inside `X-0`, **committed separately** | The 7 mints must not share a ledger write with arbitration (`UIAR-9`, `MIG-5`) |
| `X-1` before `X-4` | No rollback boundary exists until the 228 are sealed (`UIAR-12`) |
| `X-1` before `X-5` | `AIF-L14` — a supersession may not name an unsealed canonical id (`UIAR-4`) |
| `X-4` before `X-5` | `MIG-7` before-measurement is impossible after the first record |
| `X-5` before `X-6` | `MIG-4` — otherwise 192 unrecorded supersessions occur as a refresh side effect |
| `X-7` independent of `X-5`/`X-6` | Group A is stable under any engine run (§5.4) |
| `X-8` after both `X-6` and `X-9`'s inputs | Digests must be computed over the settled state (`AIF-L21`) |
| `P-9` before `X-4` | The before-measurement must use the repaired measure or it measures nothing (`UIAR-11`) |

### 15.2 The window of declared non-conformance

Between `X-0` (`P-9` lands) and `X-9`, `UIL-02` measures `217 → 0` and is **failing by design**.
This window must be declared, time-boxed and visible, not discovered. `UIS-001`'s `gate` is
`OPEN` today and will be `CLOSED` for the whole migration. A migration plan that does not state
this will be read, correctly, as having broken the identity gate.

---

## 16. Validation Gates

Ten gates, one between each pair of steps. Each is a measurement with a stated pass condition,
and each **fails closed**: an unmeasurable input is a failure, never a pass.

| Gate | After | Pass condition | Instrument |
|---|---|---|---|
| **G-1** | `X-0` (`P-1`) | `validate_rule_coverage()` returns `()`; `classify()` returns non-`ERROR` for ≥1 subject in each of the 9 classes | `platform/tests/test_mutation_classification.py` |
| **G-2** | `X-0` (`P-6`) | `uga_engine.py gate` exits **0**; `UGA-INV-01` and `UGA-INV-10` violations = 0; the mint commit contains no supersession | `uga_engine.py gate` |
| **G-3** | `X-1` | `git status --porcelain 00-BOOK/DATA/` is empty; `by_path` = 1,492 at HEAD; `page_cursor` = 10,840 at HEAD; `category_seq` identical to the working tree it sealed | `git`, ledger read |
| **G-4** | `X-2` | `A(C)` is total over the class vocabulary and over `["by_path","by_object","by_observation"]`; returns a single named authority per class; no owner-parameterised value; `UNRESOLVED` maps to refusal | declaration read + a totality test |
| **G-5** | `X-3` | The supersession store is readable and empty; `CAA-INV-04` PASSES with a population **≥ 6,413**; `rival_mints` = `[]`; `unshaped_identities` = `[]` | `uga_engine.py gate` |
| **G-6** | `X-4` | Nine `MIG-7` quantities recorded at a named commit; `identities_multiple` = **217**; collisions / renumbered / reused / grammar / history-discontinuity all **0** | `uis_engine.py --gate`, ledger read |
| **G-7** | `X-5` | Exactly **192** supersession records; each names a `canonical_id` present in `by_path` **at HEAD**; each names a `superseded_id` present in `by_object`; `by_path`/`by_object`/`by_observation`/`category_seq`/`page_cursor` **byte-identical** to `G-6`; **0** records use `RETIRED` | store read + `git diff` on the ledger |
| **G-8** | `X-6` | `uga_engine.py gate` exits 0; **0** identities minted by the run; the 192 publish their `by_path` id; **0** published identifiers changed without a matching supersession record; `retired` list unchanged | `uga_engine.py gate`, ledger diff |
| **G-9** | `X-7` | Exactly **25** supersession records; `page_cursor` byte-unchanged; the 25 `by_path` entries and their `history` sequences byte-unchanged; `artifacts.json` unchanged (measured: the 25 hold 0 records) | store read + `git diff` |
| **G-10** | `X-8` | A new current-status record exists in a store distinct from the retained attestation; the prior `07-CERTIFICATION.json` content is preserved verbatim somewhere; the new status is computed, not asserted; five digests recomputed | certification store read |

### 16.1 The gate that does not exist yet

`G-6` and `G-7` both depend on an instrument that measures *one canonical identity per subject
across all maps*. That instrument is `P-9`. Until it exists, six of the ten gates cannot be
evaluated — which is the operational form of `UIAR-10` and the reason dimension 6 is BLOCKED
rather than CONDITIONAL.

---

## 17. Rollback Conditions

### 17.1 The three regions

```
X-0 … X-4     FULLY REVERSIBLE.  Every write is a generated surface, a code change, a
              declaration, or a commit that can be reverted.  No identity semantics change.

X-5 (first record)  ────── POINT OF NO RETURN ──────

X-5 … X-9     NOT REVERSIBLE.  AIF-L17 forbids deleting or editing a recorded
              supersession.  Correction is forward-only: a new AIF-L15 transition,
              with both events permanently in the record.
```

### 17.2 Rollback conditions, by trigger

| # | Trigger | Available action | Region |
|---|---|---|---|
| `RB-1` | `G-1` fails — `classify()` still errors | Revert the predicate change; no identity was touched | Reversible |
| `RB-2` | `G-2` fails — the gate stays red after minting the 7 | `git revert` the mint commit. **Note:** the 7 identities remain in `category_seq` history; the counter does not roll back. Re-minting after a revert would issue *different* identifiers | Reversible with a permanent counter trace |
| `RB-3` | `G-3` fails — sealing produced a dirty tree | `git reset` the seal commit; the working tree returns to its present state, 228 registrations uncommitted | Reversible |
| `RB-4` | `G-4` fails — `A(C)` is not total or not functional | Withdraw the declaration; nothing downstream has run | Reversible |
| `RB-5` | `G-5` fails — `CAA-INV-04` population shrinks or `rival_mints` is non-empty | Remove the carrier; revert the alignment amendment. **Condition:** only while the store is empty | Reversible |
| `RB-6` | `G-6` fails — the before-set cannot be measured | Stop. Do not proceed to `X-5`. There is no lawful arbitration without a before-measurement (`MIG-7`) | Reversible |
| `RB-7` | `G-7` fails — a supersession names a canonical id absent from HEAD, or a ledger byte moved | **No rollback.** The records are written. Compensate forward: a new `AIF-L15` transition per defective record, each recorded, referred to the authority that wrote it | **Irreversible** |
| `RB-8` | `G-8` fails — the refresh minted, orphaned, or changed a published id without a record | Regenerate the 10 surfaces from the sealed ledger (all 10 are declared generated artifacts). If the ledger moved, `git revert` the run commit — **the supersession records stay** | Surfaces reversible; records not |
| `RB-9` | `G-10` fails — recomputed certification is not `CERTIFIED` | **Do not amend.** Record the failing current status as the current status. `AIF-L21` requires exactly this; a red current status beside a retained green attestation is the lawful outcome, not a rollback trigger | Not a rollback |

### 17.3 The abort condition

`AIF-L13` requires that an abort discard provisionally-minted identities and leave no orphan.
The migration has **one** point where a genuine abort is available and one where it is not:

- **Before `X-5`:** abort discards nothing, because nothing was minted — the flip mints zero
  (§8.1) and arbitration mints zero by construction (`MIG-1`).
- **After `X-5`:** abort is not defined. `uga_engine.py`'s `cmd_run` writes the ledger, then
  re-derives, then emits; a failure between the write and the emit leaves an advanced ledger and
  stale surfaces, and the engine has no abort path. This is a pre-existing property of the
  engine, not of arbitration, and it is the reason `P-6` requires the 7 mints be committed in a
  separate act: an abort during `X-6` must not be able to strand a mint.

### 17.4 The rollback boundary must be created, not assumed

Restated from §10.3 because it is the single most consequential operational fact in this
determination: **today there is no `git` operation that reverts an arbitration failure without
also discarding the 192 canonical identities the arbitration was performed over.** `X-1` exists
solely to create that boundary, and no step after it is safe without it.

---

## 18. Acceptance Criteria

Arbitration is **accepted** when all sixteen hold. Each is measurable; none is an assertion.
**None holds at this baseline.**

**Specification accepted:**

- [ ] `AC-1` · `validate_rule_coverage()` returns `()`; `classify()` returns `ERROR` for zero subjects in the repository
- [ ] `AC-2` · `A(C)` is declared, ratified, total over the class vocabulary **and** over the three declared ledger maps, functional, and fail-closed on `UNRESOLVED`
- [ ] `AC-3` · `CIS-0…5` is implemented as a pure function: same subject, same commit, same answer in a fresh and a bootstrapped interpreter; reads no clock, no map order, no `first_seen`
- [ ] `AC-4` · The supersession store is declared, schema'd, readable, and inside `CAA-INV-04`'s recomputed population

**Population closed:**

- [ ] `AC-5` · `by_path ∩ by_object` = 217 subjects, of which **217** carry a supersession record naming the surviving id; **0** unarbitrated
- [ ] `AC-6` · Exactly one identity per subject is `CANONICAL`; **0** orphans — no identity ceased to be published without a record written in the same act (`MIG-2`, `VC-9`)
- [ ] `AC-7` · Group A's 25 arbitrated under the recorded corpus-authority decision of `P-5`, not implicitly
- [ ] `AC-8` · Group B's 192 arbitrated against canonical identifiers that are present in `by_path` **at a commit**, not in a working tree (`AIF-L14`)

**Nothing destroyed:**

- [ ] `AC-9` · `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · every `category_seq` counter — **byte-identical** before and after arbitration (`MIG-1`, `MIG-7`)
- [ ] `AC-10` · Identifier collisions **0** · renumbered **0** · reused **0** · altered **0** · grammar failures **0** · history discontinuities **0**, after (`CAA-INV-04`, `VC-7`)
- [ ] `AC-11` · **0** supersessions recorded as `RETIRED`; the `retired` list emitted by `uga_engine.py` is unchanged in length (`URS-5`, `VC-8`)
- [ ] `AC-12` · Every one of the 1,519 prior references to a superseded identifier resolves — to its subject through the retained ledger entry, and to its successor through the supersession store (`UIAR-8`)

**Measurable and stable:**

- [ ] `AC-13` · `identities_multiple` (or its successor) quantifies over subjects across all three maps and reads **0**; `UIL-02` PASSES for a non-vacuous reason; `UIS-001` `gate` returns to `OPEN`
- [ ] `AC-14` · `uga_engine.py gate` exits **0**; UGA's recomputed **current status** is `CERTIFIED` on its own recomputation, and the prior attestation is retained verbatim and unamended (`AIF-L21`, `MIG-6`)
- [ ] `AC-15` · A second arbitration pass over the same commit produces **byte-identical** output; no `CIS-2` re-run silently re-selects (`CR-5`, `VC-12`)
- [ ] `AC-16` · A synthetic fourth minting authority is admitted with a declared predicate and `CIS-0…5` requires **no amendment** — exercised, not asserted (`VC-13`, `UCKP-INV-14`, `IL-INF-06`)

### 18.1 What acceptance does *not* close

`AC-16` closes the model's extensibility. It does **not** close the substrate's: §12.3 measures
that a fourth authority still costs one constitutional amendment, one declaration edit and two
code edits. `CC-6` of the predecessor — *"it grows: a fourth authority costs a predicate
declaration, not a rule amendment"* — is therefore **not** claimable on this migration's
completion, and that limitation is recorded here rather than discovered at the next expansion.

Likewise `CC-5` — *"it cannot silently recur"* — depends on `URS-6`'s absorbing terminal, which
is outside this migration's scope. Arbitration closes the standing 217. It does not stop the
218th. The predecessor said so; measurement adds the rate: Group B grew from 0 to 192 in one
uncommitted registration wave, so the next wave of comparable size produces a comparable
population.

---

## 19. Findings Register

| ID | Finding | Severity | Status |
|---|---|---|---|
| `UIAR-1` | The mutation-class vocabulary cannot carry `A(C)`: `UCOS-UGA-001` appears in 0 of 9 classes, `REG-AUTO-001`'s own `does_not_govern` states `by_object` "is not a declared mutation class", and 3 of 9 classes resolve to an owner-parameterised placeholder rather than an authority | **CRITICAL** | **OPEN** |
| `UIAR-2` | `classify()` returns `ERROR` for every subject in the repository because `R-09` was declared without a predicate, so `CIS-0` cannot resolve `C(S)` for any of the 217 — and the unimplemented rule is the one governing **127 of 192** Group B subjects | **CRITICAL** | **OPEN** |
| `UIAR-3` | `A(C)` is derivable from `uga-declaration.json` `object_classes` and is already executed by `epoch1_identity`, but adopting it would make one programme's classifier the cross-authority arbiter, leaves `by_observation`'s authority unmapped, and keys the decision on an uncommitted registration set | **HIGH** | **OPEN** |
| `UIAR-4` | 192 of 217 canonical identities exist only in an uncommitted `REG-AUTO-001` transaction (+228 registrations, +1,014 pages, 88 counters). Under `AIF-L14` the admission is unsealed, so arbitrating Group B now writes irreversible records naming identifiers Recorded Truth does not carry | **CRITICAL** | **OPEN** |
| `UIAR-5` | Sealing Group B is an unauthorized `CORPUS_REGISTRATION` act whose identifiers are not demonstrably reproducible if re-derived, and which splits Group B across at least two mutation classes (127 `R-09` / 65 other) with different authority-resolution paths | **HIGH** | **OPEN** |
| `UIAR-6` | Group A holds **0** `artifacts.json` records (measured), narrowing the `UMB-003` referral to a single decidable question: whether 85 pages of allocated range may remain permanently bound to 25 superseded corpus identities | **MEDIUM** | **OPEN** |
| `UIAR-7` | `supersede` is ratified law with zero implementation surface — no store, schema, writer, reader or validator. `MIG-2` has nothing to write into and `VC-5` has nothing to check | **HIGH** | **OPEN** |
| `UIAR-8` | No `UID → UID` alias exists on the durable plane; the only located alias (P3 native-ID crosswalk) is the wrong direction. Blast radius measured at **1,519** occurrences across 3 regenerable surfaces, with **0** references outside the UGA programme and the ledger | **MEDIUM** | **OPEN** |
| `UIAR-9` | `uga_engine.py gate` FAILS at this baseline (`UGA-INV-01`, `UGA-INV-10`, 7 anonymous objects), so the `MIG-4` refresh is also the outstanding repair for a red gate; executing it mints 7 unrelated permanent identities inside the arbitration act, breaking `MIG-5` and making the write non-isolable in an append-only counter | **CRITICAL** | **OPEN** |
| `UIAR-10` | `UIL-02` is a declared **blocking** law for this exact condition, wired to a measure that reads one register (reads 0), in a programme covering 1,264 of 6,413 identities (19.7%), which no stage of `verify.sh` executes. Six of ten validation gates are unevaluable as a result | **CRITICAL** | **OPEN** |
| `UIAR-11` | Re-scoping `identities_multiple` per `VC-4` moves it 0 → 217, fails `UIL-02`, and closes `UIS-001`'s currently-OPEN gate for the whole migration window. Measurement repair must precede arbitration; the window must be declared, not discovered | **HIGH** | **OPEN** |
| `UIAR-12` | No rollback boundary isolates arbitration from the 228 uncommitted registrations, because both write the same two files; any `git`-level revert also discards the 192 canonical identities. After the first supersession record no rollback exists in any form — only forward-only compensation | **HIGH** | **OPEN** |
| `UIAR-13` | UGA's certification asserts `CERTIFIED` with `blocking_deviations: []` while its own gate fails two blocking invariants, so `MIG-6`'s recomputation cannot close: it returns FAILED for pre-existing reasons that arbitration would be blamed for | **HIGH** | **OPEN** |

**13 raised · 0 resolved.**

### 19.1 Disposition of prior findings

| Prior | This determination |
|---|---|
| `UIA-1` (217 hold two ids) | **CONFIRMED at this baseline** — re-measured 217 (25 / 192), unchanged |
| `UIA-2` (`identities_multiple` vacuous) | **EXTENDED** — the vacuity is three-layered (measure, programme population 19.7%, absent from `verify.sh`) and repairing it reddens a blocking law (`UIAR-10`, `UIAR-11`) |
| `UIA-3` (two groups, opposite orders) | **CONFIRMED**; the class-determined model remains the only correct one, and is now measured **unevaluable** because `classify()` errors (`UIAR-2`) |
| `UIA-4` (Group A = `UIS-F-001`) | **NARROWED** — Group A holds 0 `artifacts.json` records, so the open question reduces to 85 pages (`UIAR-6`) |
| `UIA-5` (UGA absent from the plane crosswalk) | **REINFORCED** — the same absence is why `A(C)` cannot be built over the mutation vocabulary (`UIAR-1`) |
| `UIA-6` (incomparable `first_seen` grammars) | **NOT ON THE CRITICAL PATH** — `CIS-0…5` reads no `first_seen`; confirmed by rule text |
| `UIA-7` (two declared grammars) | **CARRIED** — `unshaped_identities` = 0 under the looser pattern; latent |
| `UIA-8` (`UIS-F-003` load-bearing) | **QUANTIFIED** — Group B's canonical ids span **75** distinct namespaces; 78 across all 217 |
| `UIA-9` (5 digests invalidated) | **EXTENDED** — the recomputation cannot return `CERTIFIED` for reasons predating arbitration (`UIAR-13`) |
| `UIA-10` (`second_authority_test` unapplied) | **CARRIED** — unchanged |
| `URS-2` | **SPECIFIED, NOT RESOLVED, NOT EXECUTABLE.** 12 preconditions located |
| `URS-3` (stale certification) | **UPGRADED from stale to contradicted** — measured by executing the gate (`UIAR-13`) |
| `URS-6` (absorbing terminal) | **RATE-QUANTIFIED** — Group B grew 0 → 192 in one uncommitted wave |
| `M-C` / `CH-3` (mutation classification non-functional) | **CONFIRMED and made load-bearing** — it is now the first precondition of an identity migration, not only a governance gap (`UIAR-2`) |
| `CH-4` (no located competent ratifier) | **BINDING** — 5 of 12 preconditions require an authority act it says is unavailable |

---

## 20. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-ARBITRATION-EXECUTION-READINESS-DETERMINATION.md` |
| Line count | ✅ **1605** |
| Required section — execution readiness verdict | ✅ §13 (`NOT READY — EXECUTION PROHIBITED`, dimension table, executable set, prohibited set) |
| Required section — preconditions | ✅ §14 (`P-1`…`P-12`, owners, discharge tests, dependency graph) |
| Required section — migration sequence | ✅ §15 (`X-0`…`X-9`, ordering constraints, non-conformance window) |
| Required section — validation gates | ✅ §16 (`G-1`…`G-10`, instruments, the gate that does not exist) |
| Required section — rollback conditions | ✅ §17 (`RB-1`…`RB-9`, the three regions, the abort condition, the boundary) |
| Required section — acceptance criteria | ✅ §18 (`AC-1`…`AC-16`, and what acceptance does not close) |
| Required analysis 1 — authority admission map readiness | ✅ §4 |
| Required analysis 2 — 217 identity conflict migration readiness | ✅ §5 |
| Required analysis 3 — supersession model readiness | ✅ §6 |
| Required analysis 4 — alias preservation readiness | ✅ §7 |
| Required analysis 5 — UGA refresh dependency readiness | ✅ §8 |
| Required analysis 6 — identity invariant measurement readiness | ✅ §9 |
| Required analysis 7 — rollback readiness | ✅ §10 |
| Required analysis 8 — certification impact | ✅ §11 |
| Required analysis 9 — future identity expansion compatibility | ✅ §12 |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis only — subjects arbitrated | ✅ **0** |
| Identity changes | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7, before and after; `category_seq` and `page_cursor` untouched |
| Identities minted / retired / superseded / renumbered | ✅ **0 / 0 / 0 / 0** |
| Registry changes | ✅ **0** — ledger, `artifacts.json`, all 10 UGA surfaces, `uis.json`, the alignment register and the mutation boundary were read, none written |
| Certification changes | ✅ **0** — `07-CERTIFICATION.json` read, unmodified |
| Code changes | ✅ **0** — `uga_engine.py`, `ukb.py`, `uis_engine.py`, `mutation_classification.py`, `mutation_class_extension.py`, `uga_projection.py`, `config.py` read, none written |
| Commands executed | ✅ **read-only only** — `uga_engine.py gate` (declared non-mutating, guarded by `test_verification_purity.py`), `git show`, `git ls-files`, JSON reads. `uga_engine.py run` **not executed** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to session start |
| Working tree total | ✅ **349 → 350** porcelain lines; the single delta is this file |
| Only one new artifact | ✅ the single repository delta is this file |
| Findings resolved | ✅ **0** — 13 raised |

### 20.1 Measurement provenance

```
HEAD                                              bae59755d7e2d3566c93b89c722b68847145269a
branch                                            integration/recovery-001
git status  modified / untracked / total          38 / 311 / 349   (before)
                                                  38 / 312 / 350   (after — this file only)

ledger by_path / by_object / by_observation       1,492 / 4,914 / 7
  at HEAD                                         1,264 / 4,914 / 7
by_path ∩ by_object   worktree / HEAD               217 / 25
by_observation ∩ by_path / ∩ by_object                0 / 0
Group A / Group B                                    25 / 192
  A by_object cats: EXDOC 12 · DATAOBJ 13
  B by_object cats: EXDOC 189 · DATAOBJ 3
  A by_path cats:   MASTER 13 · INTELLIGENCE 11 · MCP001MASTER 1
  B by_path cats:   75 distinct        all 217: 78 distinct
  A / B pages held by the corpus id                    85 / 866
  A / B in artifacts.json                          0 of 25 / 192 of 192
  B matching R-09 filename rule                    127 of 192
  B .md / .json                                       189 / 3
uncommitted corpus transaction
  artifacts.json HEAD → tree                      1,233 → 1,461   (+228)
  by_path        HEAD → tree                      1,264 → 1,492   (+228)
  page_cursor    HEAD → tree                      9,826 → 10,840  (+1,014)
  category_seq counters advanced                       88
reference counts over the 217 by_object ids
  02-UNIVERSAL-OBJECT-REGISTRY.json                   217
  03-AUDIT-UNIVERSE.json                              434
  04-RELATIONSHIP-GRAPH.json                          868
  05-GOVERNANCE-INVARIANTS.json / 07-CERTIFICATION      0 / 0
  00-BOOK/DATA/id-ledger.json                         217
  every other tracked file                              0
  UGA surfaces referencing the 217 by_path ids          0
uga_engine.py gate (executed, read-only)          FAILED
  UGA-INV-01 / UGA-INV-10 violations                    7 / 7
  anonymous objects                                     7
  CAA-INV-04 population / result                    6,413 / PASS
mutation classification
  rules declared / predicates implemented               9 / 8
  validate_rule_coverage()                          ("rule 'R-09' is declared but no
                                                     predicate implements it",)
  classify() status, every subject                  ERROR
UIS-001
  identities_multiple                                   0
  recorded / registered identities                  1,264 / 1,233
  nonsource_identity_admissions                        25
  collisions / renumbered / reused / grammar        0 / 0 / 0 / 0
  gate / in verify.sh                                OPEN / NO
alignment register REPOSITORY_OBJECT maps         3  ["by_path","by_object","by_observation"]
alignment register mint_markers                   1  ["category_seq"]
generated-artifact-registry entries                 345
  UGA canonical surfaces declared                      10
  id-ledger.json declared generated                    NO
AIF laws read / bearing on readiness               24 / 11
dimensions assessed                                   9   (0 READY · 3 CONDITIONAL ·
                                                           6 BLOCKED · 0 PROHIBITED)
preconditions / gates / rollback conditions / criteria   12 / 10 / 9 / 16
findings raised / resolved                          13 / 0
subjects arbitrated                                    0
this artifact, lines                               1605
```

---

*This determination arbitrated no subject, minted no identity, retired none, superseded none and
renumbered none — `by_path` stands at 1,492, `by_object` at 4,914 and `by_observation` at 7,
before and after, and the working tree carries the same 38 tracked modifications it carried at
session start. It converts the predecessor's arbitration model into an execution decision and
returns **NOT READY**: zero of nine dimensions are ready, six are blocked on measured repository
facts rather than on ordering, and zero of the 217 subjects may be arbitrated. Three
measurements decide it. `classify()` returns `ERROR` for every subject in the repository because
`R-09` was declared without a predicate — so `CIS-0` cannot resolve a governing class for any
subject, and the unimplemented rule is precisely the one governing 127 of the 192 Group B
subjects. One hundred and ninety-two of the canonical identities the migration would name exist
only in an uncommitted 228-registration transaction, so under `AIF-L14` their admission is not
sealed and a supersession record naming them would be an irreversible reference to something
Recorded Truth does not hold. And `uga_engine.py gate` fails at this baseline on two blocking
invariants, which makes the refresh the model orders after arbitration simultaneously the
outstanding repair for a red gate and an act that would mint seven unrelated identities inside
the arbitration write. Against those, three dimensions are conditional rather than blocked, and
the measurements behind them are the encouraging half of this determination: the blast radius is
1,519 occurrences across three regenerable surfaces with zero references anywhere else in the
tracked corpus; the refresh mints nothing for the 192; and the ledger's loader preserves unknown
keys, so a supersession store is addable by the same construction that added `by_object`. Twelve
preconditions, ten validation gates, nine rollback conditions and sixteen acceptance criteria
are stated, and one operational fact governs all of them: no rollback boundary exists today that
separates arbitration from the uncommitted transaction it depends on, and after the first
supersession record no rollback exists at all. Thirteen findings (`UIAR-1`…`UIAR-13`) are
raised; none is resolved. The single repository mutation is the creation of this file.*

**END DETERMINATION — EXECUTION READINESS: NOT READY · 0 OF 217 ARBITRABLE · 12 PRECONDITIONS OPEN · ZERO SUBJECTS ARBITRATED · STOPPED AFTER ARTIFACT CREATION.**
