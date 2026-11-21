# UCOS Ω∞ — WAVE 0 EXECUTION IMPLEMENTATION DETERMINATION

**The Wave 0 readiness assessment converted into a controlled implementation package — and one measured defect that makes the headline action unable to satisfy its own acceptance criteria as currently scoped.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-WAVE-0-EXECUTION-IMPLEMENTATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED IMPLEMENTATION PACKAGE.** Executes nothing, closes no root cause, discharges no blocker, vests no authority, arbitrates no subject, mints no identity, assigns no ownership, authorizes no act. |
| Mode | IMPLEMENTATION PREPARATION ONLY · **NO CODE · NO CONFIGURATION · NO REGISTRY · NO CERTIFICATION · NO IDENTITY · NO OWNERSHIP · NO `register.sh` · NO MUTATION-PRODUCING COMMAND · NO COMMIT** |
| Scope source | `UCOS-OMEGA-INFINITY-WAVE-0-1-EXECUTION-READINESS-DETERMINATION.md` (564 lines, 10 sections) — Wave 0 READY 6/6; Wave 1 PARTIALLY READY 1/5 |
| Upstream | `…ROOT-CAUSE-CLOSURE-EXECUTION-PLAN-DETERMINATION.md` (281 lines) · `…ROOT-CAUSE-CLOSURE-AND-READINESS-DETERMINATION.md` (864 lines) |
| Method | Read-only inspection at HEAD `bae59755`: parsed `mutation-governance-boundary.json` and read `mutation_classification.py:384-424`. **Two blocking findings were produced that no prior determination in this chain carries** — §3.2 and §3.3. Neither is resolved here. |
| Preserved invariants | No identity mutation without arbitration · no registry mutation without authority · no certification mutation without evidence · no invented authority · no fabricated ownership · no value chosen by preference · no `READY` claim without measurable evidence |

---

## 1. Current Baseline

| Field | Value |
|---|---|
| HEAD commit | `bae59755d7e2d3566c93b89c722b68847145269a` — *"POST-CERTIFICATION: Code formatting cleanup (Phase 1B and Phase 2)"* |
| Branch | `integration/recovery-001` |
| `git status --porcelain` baseline | **354** lines |
| Tracked modifications | **38** |
| Untracked artifacts | **316** porcelain entries · **323** files by `git ls-files --others --exclude-standard` (porcelain collapses untracked directories; both are correct under different counting) |
| Staged | **0** |
| Current readiness verdict | **`NOT READY`** — `Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }`, registry slot `R-13` |
| Verdict ceiling | **`CERTIFIED-PROVISIONAL`** — `UCCEP-F-004`; `PROVISIONAL` under `VAC-01` |

### 1.1 The baseline fact that governs every protocol below

**The working tree is not clean and cannot be made clean within this scope.** 354 porcelain lines, of which 316 are untracked — including the 228 unratified corpus registrations that constitute `RC-3`. Discarding them requires `AG-3`, which is not located.

Consequence, stated once and applied throughout: **every "clean tree" requirement in this package is replaced by a byte-identity comparison against a recorded pre-action baseline.** A literal clean-tree gate would fail for reasons that predate every Wave 0 action and would therefore be uninformative. This is a correction to the directive's §6 requirement, made explicit rather than silently substituted — see §6.4.

### 1.2 Tracked modifications intersecting Wave 0 target surfaces

| File | State at baseline | Relevance |
|---|---|---|
| `platform/tests/test_mutation_classification.py` | tracked-modified `+3/−3`, adds no `R-09` coverage | `W0-1` test target — Wave 0 edits would land on an unreviewed diff |
| `Makefile` | tracked-modified | gate-mode target; `W0-6` denominator source |
| `engine/verification_intelligence/{model,registry,selection}.py` | tracked-modified | adjacent to classification consumers |
| `platform/tests/test_mutation_classification.py`, `platform/tests/test_mutation_classification.py` | — | see `R-2` in the readiness determination §8 |
| `00-BOOK/DATA/*.json` (7 files) | tracked-modified | **PROHIBITED SURFACE** — `AG-3` |

---

## 2. Wave 0 Scope

### 2.1 A disclosed identifier collision, resolved by neither renumbering nor preference

**The directive's §3 heading names `W0-1` as the R-09 predicate implementation. The readiness determination assigns those identifiers differently:**

| Identifier | Readiness determination §3–§4 | Directive for this artifact |
|---|---|---|
| `W0-1` | `S-1` gate mutation-mode **decision package** (document only) | "`W0-1` R-09 Predicate Implementation" |
| `W1-1` | `CA-1` — the R-09 predicate implementation (**Wave 1**, engineering) | — |

Two readings are available and this determination adopts neither as fact:

- **Reading A — renumbering.** Wave 0 is being redefined to lead with the R-09 predicate, promoting `CA-1` from Wave 1 into Wave 0.
- **Reading B — conflation.** `W1-1` was referred to as `W0-1`.

**Why this cannot be silently absorbed:** under Reading A, Wave 0 changes mutation class. The readiness determination established Wave 0 as **six document-only acts with zero governed-surface writes and zero authority required**. Adding the R-09 predicate makes Wave 0 contain a **source-code change to `platform/repository_intelligence/mutation_classification.py`** — which changes the Change Safety Protocol (§6), the Rollback Model (§8), and the required authority from *none* to `AG-1`.

**Disposition adopted here:** this package documents the R-09 predicate boundary in §3 as the directive requires, labels it **`W0-1` (= `CA-1` = `W1-1`)** so both numbering schemes resolve, and treats it as **a code-changing act requiring `AG-1`** rather than as a document-only act. The `S-1` decision package is retained under its readiness-determination identity as **`W0-1a`** in §4 so that nothing is dropped. **Whether Wave 0 formally includes a code change is a programme sequencing decision, not an engineering one, and is referred — not decided.**

### 2.2 Wave 0 action register

| Field | `W0-1` (= `CA-1` = `W1-1`) |
|---|---|
| **Objective** | Implement `_r09_governed_analysis` and register it in `RULE_PREDICATES`, plus a two-sided regression guard |
| **Root cause addressed** | **`RC-1`** — classification outage; `classify()` → `ERROR` for **every** subject |
| **Dependencies** | None as a graph root. **But see §3.2 — a measured blocker was found that CA-1's declared scope forbids fixing** |
| **Allowed changes** | `platform/repository_intelligence/mutation_classification.py` — **add** one predicate function and one `RULE_PREDICATES` entry · `platform/tests/test_mutation_classification.py` — add positive, negative and coverage-guard tests · a disposition record for `mutation_class_extension.py` |
| **Forbidden changes** | Any change to `R-01…R-08` predicates · **any precedence change** · any weakening of the two-sided coverage contract · a tenth rule · any write to `mutation-governance-boundary.json` · any registry, identity, certification or ownership surface |
| **Required authority** | **`AG-1` — AVAILABLE.** Repository Intelligence, read from the register's `governed_by` chain, **not assigned** |
| **Expected evidence** | `validate_rule_coverage()` `("rule 'R-09' …",)` → `()` · per-class `classify()` output with `rule_id` for all nine classes · a negative test proving rejection of a non-analysis subject · digest equality across two runs · `VG-1`…`VG-6` all PASS |

| Field | `W0-1a` — `S-1` gate mutation-mode decision package |
|---|---|
| **Objective** | Assemble the package the mutation governance owner needs to define what `OBSERVE` and `TRANSACT` bind |
| **Root cause addressed** | `RC-4` (prepares only; closes nothing) |
| **Dependencies** | `W0-6` for the denominator |
| **Allowed changes** | One new untracked proposal document |
| **Forbidden changes** | Any `Makefile` or workflow edit · any semantics asserted as decided |
| **Required authority** | **NONE to prepare.** The decision is `AG-2` — **LOCATED, OPEN** |
| **Expected evidence** | Every target and workflow enumerated with current mode state; deciding owner named; semantics proposed, not asserted |

| Field | `W0-2` — supersession carrier decision package |
|---|---|
| **Objective** | Present carrier options with each one's `CAA-INV-04` totality consequence |
| **Root cause addressed** | `RC-6` (prepares only) |
| **Dependencies** | None |
| **Allowed changes** | One new untracked proposal document |
| **Forbidden changes** | **No store built** · no file in `00-BOOK/DATA/` · no `planes[REPOSITORY_OBJECT].maps` amendment · no `id-ledger.json` key added |
| **Required authority** | **NONE to prepare.** The carrier decision is `AG-5` — **NOT LOCATED** |
| **Expected evidence** | Options each carrying the ≥ 6,413 identity constraint; `AIF-L15`/`AIF-L17`/`UIL-13`/`URS-5` compliance stated per option; none recommended as decided |

| Field | `W0-3` — `CEP-002` Article 28 enumeration package |
|---|---|
| **Objective** | Enumerate exactly what a corpus authority would ratify or revert |
| **Root cause addressed** | `RC-3` (prepares only — **the Wave 2 gate**) |
| **Dependencies** | None |
| **Allowed changes** | One new untracked proposal document, assembled **exclusively from already-recorded measurements** |
| **Forbidden changes** | **`register.sh` in any mode, including `--guard`** · any `00-BOOK/DATA/` write · any fresh tool run that could transact · any statement that reads as authorization |
| **Required authority** | **NONE to enumerate. Enumerating is not deciding.** The decision is `AG-3` — **NOT LOCATED**; ratification is unrecordable (0 `ratif` matches) |
| **Expected evidence** | 228 registrations / 238 pages / 1,014 consumed pages / 83 namespaces / 88 counters enumerated exactly, none estimated · both dispositions costed, including that `category_seq` does not roll back so re-minting issues **different** identifiers · `AG-6`'s open 85-page Group A question carried · a face statement that the package authorizes nothing |

| Field | `W0-4` — `A(C)` admission map draft |
|---|---|
| **Objective** | Draft the class → authority map as a proposal, total over 9 classes × 3 ledger maps |
| **Root cause addressed** | `RC-2` (prepares only) |
| **Dependencies** | Benefits from `W0-1`, not blocked by it |
| **Allowed changes** | One new untracked proposal document; every entry marked `PROPOSED` |
| **Forbidden changes** | **No write to `mutation-governance-boundary.json`** · no write to any programme declaration · no adoption of `uga-declaration.json`'s `object_classes` as the map |
| **Required authority** | **NONE to draft.** Ratification is `AG-4` — **NOT LOCATED**; `UCKP-ART-18` refuses the in-repo substitute |
| **Expected evidence** | Total, functional, fail-closed on `UNRESOLVED`; `UCOS-UGA-001` and the observation authority named; zero entries marked `DECLARED` |

| Field | `W0-5` — ownership run-mode canonicality declaration |
|---|---|
| **Objective** | Declare which run mode is canonical, resolving the 398 / 506 / 549 population conflict |
| **Root cause addressed** | `RC-8` (prepares the partition only) |
| **Dependencies** | None |
| **Allowed changes** | One new untracked declaration document |
| **Forbidden changes** | **Any assignment** — `platform/universal_ownership/catalog/ucos-ownership-declarations.json` `assignments` stays `{}` · no `UNASSIGNED` fallback · no suppression of `OwnershipFabricationError` |
| **Required authority** | **NONE** — a measurement-scope declaration is not an ownership assignment. Assignment is `AG-8` → `AG-9`, **NOT AVAILABLE** |
| **Expected evidence** | Exactly one mode canonical with rationale; the other two recorded as non-canonical, not deleted; catalogue byte-identical; the untracked register's path-not-authority defect stated |

| Field | `W0-6` — gate-target denominator reconciliation |
|---|---|
| **Objective** | Reconcile 45 vs 46 vs 49 before any completeness claim is made against it |
| **Root cause addressed** | `RC-4` (removes a false-completeness risk from `CA-2`) |
| **Dependencies** | None — **and it is a prerequisite of `W0-1a` and of `CA-2`-E** |
| **Allowed changes** | One new untracked reconciliation document |
| **Forbidden changes** | **No value chosen by preference** · no `Makefile` edit · no mode field populated |
| **Required authority** | **NONE. Counting is not deciding.** Declaring one canonical is a scope act; if it proves to require an owner, it escalates to `AG-2` |
| **Expected evidence** | All three inventories reproduced with the command or citation that produced each; aliases, phony and non-gate targets dispositioned; one declared canonical with rationale **or** the disagreement escalated |

### 2.3 Scope aggregate

| Measure | Value |
|---|---|
| Actions | **7** — `W0-1`, `W0-1a`, `W0-2`…`W0-6` |
| Actions writing to existing files | **1** — `W0-1` only (two files: one module, one test) |
| Actions producing documents only | **6** |
| Governed surfaces written | **0** — no registry, identity, certification or ownership surface is touched by any action |
| Root causes closed if all seven complete | **1** — `RC-1`, **and only if §3.2 resolves** |

---

## 3. W0-1 R-09 Predicate Implementation Boundary

### 3.1 Current classification failure

```
00-BOOK/DATA/mutation-governance-boundary.json
  mutation_classes            9   CONSTITUTIONAL_TRUTH · SOURCE · GENERATED_ARTIFACT ·
                                  EXCLUSION · REPOSITORY_STATE · CORPUS_REGISTRATION ·
                                  GOVERNED_DECLARATION · AUTHORED_DOCUMENT · GOVERNED_ANALYSIS
  classification_rules.rules  9   R-01 … R-09   (precedence 1 … 9, in declared order)

platform/repository_intelligence/mutation_classification.py:403
  RULE_PREDICATES             8   R-01 … R-08

validate_rule_coverage(boundary)  ──▶ ("rule 'R-09' is declared but no predicate
                                        implements it",)
classify(any_subject)             ──▶ status=ERROR      ← for EVERY subject, not a subset
```

The cause is located and unambiguous: `platform/repository_intelligence/mutation_class_extension.py` (8,752 bytes, added at `bae59755`) appended the `GOVERNED_ANALYSIS` class and the `R-09` rule to the boundary **JSON** and added **no** predicate to `RULE_PREDICATES`. It extended the declaration and not the implementation. `validate_rule_coverage` is two-sided and `classify()` evaluates it **before** the precedence loop (`:427`), so one missing predicate fails closed over the entire repository. **The fail-closed design worked correctly; the defect is a half-landed change.**

### 3.2 BLOCKING FINDING — R-09's membership set is a strict subset of R-08's, and R-08 evaluates first

This was measured at HEAD and is carried by no prior determination in this chain.

**The two declared criteria sets, verbatim:**

```
R-08 AUTHORED_DOCUMENT   authored_document_checks()  mutation_classification.py:384-392
   markdown                   path ends .md
   authored                   path not in repo.producer_homes
   repository-controlled      path in repo.tracked
   non-generated              path not in repo.generated
   self-declared-authority    bool(authored_document_owner(path, repo))

R-09 GOVERNED_ANALYSIS   membership_criteria         boundary JSON, mutation_classes[8]
   markdown                   the path ends .md                              ← same
   authored                   absent from producer_homes                     ← same
   repository-controlled      tracked by version control                     ← same
   non-generated              absent from generated-artifact-registry.json    ← same
   self-declared-authority    carries Authority field in opening metadata     ← same
   analysis-artifact          filename carries determination|analysis|assessment|
                              execution|matrix|readiness|admission|blocker|gap  ← ADDITIONAL
```

**R-09 = R-08 ∧ analysis-artifact. Therefore R-09 ⊂ R-08, strictly.**

**And the evaluation order makes R-08 win:**

```
boundary JSON  classification_rules.evaluation:
  "ORDERED PRECEDENCE — rules are evaluated in the order declared, and the first rule
   whose predicate holds assigns the class."

declared order / precedence:   … R-08 (8) , R-09 (9)
classify() loop, :441:         for rule in doc["classification_rules"]["rules"]:
                               → R-08 is tested BEFORE R-09
```

**Consequence:** implementing `_r09_governed_analysis` exactly as declared repairs `validate_rule_coverage()` to `()` and stops the `ERROR` outage — but **`R-09` never fires for any subject.** Every artifact satisfying R-09's six criteria satisfies R-08's five first and classifies as `AUTHORED_DOCUMENT`. `R-09` becomes reachable-in-code and dead-in-effect.

**Two declared properties are violated at the same time:**

| Declared property | Verbatim | State after `W0-1` as scoped |
|---|---|---|
| `unique` | *"Exactly one class. **The predicates are written to be disjoint**"* | **VIOLATED** — R-08 and R-09 are not disjoint; R-09 ⊂ R-08 |
| Class 8's own note | *"**R-09 evaluates before R-08** so analysis artifacts are classified as GOVERNED_ANALYSIS rather than the more general AUTHORED_DOCUMENT"* | **FALSE AT THIS BASELINE** — R-09 is declared last and evaluates last |

**And `CA-1`'s acceptance criteria become unsatisfiable as scoped.** `CA-1` requires *"`classify()` returns `CLASSIFIED` … for a sample spanning all nine classes"* while declaring **out of scope**: *"any change to `R-01…R-08`, any change to precedence."* The only two repairs available are:

| Repair | Effect | `CA-1` scope |
|---|---|---|
| Move `R-09` before `R-08` in declared order | R-09 fires for analysis artifacts, as Class 8 intends | **OUT OF SCOPE** — *"any change to precedence"* |
| Add `¬analysis-artifact` to R-08's checks | Makes the two disjoint | **OUT OF SCOPE** — *"any change to `R-01…R-08`"* |
| Implement R-09 and accept it never fires | Coverage repaired, `ERROR` cleared, R-09 dead | Within scope, **fails `CA-1`'s all-nine-classes criterion** |

**This determination does not choose.** The choice alters the declared precedence or a declared predicate of the mutation-governance register, whose owner is the mutation governance owner — the same authority holding `AG-2` and `AG-4`. **It is referred as `AG-2b`, a newly identified decision, LOCATED and OPEN.**

### 3.3 Second finding — `mutation_class_extension.py` has no invocation path

`RULE_PREDICATES` is a module-level dict populated at import (`:403`). `mutation_class_extension.py` mutates the boundary **JSON**. No caller invoking `extend_mutation_governance_boundary` was located. Its disposition — intended registration path, or vestigial — is a required output of `W0-1` and is **not** an engineering free choice, because if it is the intended path then `W0-1`'s implementation belongs there rather than in `RULE_PREDICATES`. Referred with §3.2 to `AG-2b`.

### 3.4 Required predicate behaviour

```python
def _r09_governed_analysis(subject: Subject, repo: Repository, boundary: dict) -> bool:
    if subject.kind != PATH:            # mirrors R-06/R-07/R-08 shape exactly
        return False
    return all(governed_analysis_checks(subject.identity, repo).values())

def governed_analysis_checks(path: str, repo: Repository) -> dict[str, bool]:
    """Class 8's six membership criteria, individually, mirroring Class 7's shape."""
    return {
        "markdown":                path.endswith(_MARKDOWN_SUFFIX),
        "authored":                path not in repo.producer_homes,
        "repository-controlled":   path in repo.tracked,
        "non-generated":           path not in repo.generated,
        "self-declared-authority": bool(authored_document_owner(path, repo)),
        "analysis-artifact":       <filename carries one of the nine declared tokens>,
    }
```

All six criteria are **mechanically decidable from repository state at one commit, with no inference, no ownership assignment and no authority act.** The per-criterion dict mirrors `authored_document_checks` so a failing criterion is individually attributable.

### 3.5 Inputs and outputs

| | Detail |
|---|---|
| **Inputs** | `subject: Subject` (kind `PATH`) · `repo: Repository` — `tracked`, `generated`, `producer_homes` · `boundary: dict` — `mutation_classes[8].membership_criteria`, `classification_rules.rules[8]`. **Reads no clock, no environment, no caller ordering** (declared `deterministic` property) |
| **Outputs** | `bool` from the predicate · `ClassificationResult(artifact, mutation_class, rule_id, authority, status, reason)` from `classify()` · `validate_rule_coverage()` → `()` |
| **Side effects** | **NONE.** Zero writes during classification, mutation-tested |

### 3.6 Validation rules

| # | Rule |
|---|---|
| V-1 | `validate_rule_coverage(boundary)` returns `()` — both directions satisfied |
| V-2 | `classify()` returns `CLASSIFIED` or `UNRESOLVED`, **never `ERROR`**, for a heterogeneous sample |
| V-3 | **A subject classifies as `GOVERNED_ANALYSIS` with `rule_id == "R-09"`** — the criterion §3.2 shows is unsatisfiable without an `AG-2b` decision |
| V-4 | Negative test: the predicate **rejects** a non-analysis subject. A predicate returning `True` for everything satisfies V-1 and V-2 vacuously |
| V-5 | Determinism: two runs over the same corpus produce byte-identical output, digest-compared |
| V-6 | Purity: zero mutations during classification, mutation-tested not asserted |
| V-7 | Unknown input → `UNRESOLVED` fail-closed, **never** a permissive default |
| V-8 | Missing `Authority` falls through to `R-08`, no fabrication |
| V-9 | Regression guard: `set(RULE_PREDICATES) == {declared rule ids}` fails **at test time** on a future declared-but-unimplemented rule |
| V-10 | `mutation_class_extension.py` dispositioned — invoked or declared vestigial |

### 3.7 Acceptance criteria

`W0-1` is accepted only when **V-1 through V-10 all pass and `VG-1`…`VG-6` all pass.** V-3 cannot pass without an `AG-2b` decision. Therefore:

> **`W0-1` is implementable to V-1, V-2, V-4…V-10 today, and NOT acceptable today.** The gap is a single declared decision, not work.

**Constraint honoured — no artifact classification changes until validation succeeds.** No consumer may gate on mutation class, no artifact may be reclassified, no migration may run, and no classification output may be recorded as authoritative until V-1…V-10 pass. `classify()` returning `CLASSIFIED` is a computation, not a reclassification; the register's own note is explicit that evaluation is `EX-016` and **migration of existing artifacts is `EX-017`** — a separate act, not in this scope.

---

## 4. W0-2 Through W0-5 Execution Boundaries

*(`W0-1a`, the `S-1` decision package displaced by §2.1, is included here so nothing is dropped.)*

### `W0-1a` — `S-1` gate mutation-mode decision package

| | Detail |
|---|---|
| **Can be implemented** | Enumerate every gate target and workflow with its current mode state · reproduce the 4 declaring targets as precedent · state candidate `OBSERVE`/`TRANSACT` semantics as **proposals** · name `AG-2` as the deciding owner |
| **Cannot be executed** | Populating any mode field · editing `Makefile` or any workflow · asserting semantics as decided · reporting a completeness percentage before `W0-6` closes |
| **Required verification** | `VG-1`, `VG-2`, `VG-4`, `VG-5` · target inventory reconciles to `W0-6`'s canonical denominator · zero existing files modified |
| **Stop conditions** | `SC-1` if semantics are declared by any party other than `AG-2` · `SC-10` if a percentage is reported against an unreconciled denominator |

### `W0-2` — supersession carrier decision package

| | Detail |
|---|---|
| **Can be implemented** | A written schema for the supersession record (subject · prior identity · successor identity · authority · timestamp · evidence) · per-option `CAA-INV-04` totality consequence · a `MIG-2`-field → schema-field mapping · confirmation each option permits **zero** `RETIRED` records and **zero** writes into an existing identity's `history` |
| **Cannot be executed** | Building the store · creating any file in `00-BOOK/DATA/` · adding a tenth `id-ledger.json` key · amending `planes[REPOSITORY_OBJECT].maps` · choosing the carrier |
| **Required verification** | `VG-1`…`VG-5` · `id-ledger.json` byte-identical, 9 top-level keys unchanged · `constitutional-authority-alignment.json` byte-identical |
| **Stop conditions** | `SC-1` if a carrier is chosen without `AG-5` · `VG-4` FAIL on any `id-ledger.json` byte change · `SC-1` if a `planes` amendment is drafted as adopted rather than proposed |

### `W0-3` — `CEP-002` Article 28 enumeration package

| | Detail |
|---|---|
| **Can be implemented** | Enumerate the 228 registrations, 238 emitted pages, 1,014 consumed pages, 83 new namespaces, 88 advanced counters · reproduce the six confirming numstat measurements **from the record** · cost both dispositions · carry `ADR-0017`'s refusal of a blanket mint and `AG-6`'s open 85-page question · state on its face that it authorizes nothing |
| **Cannot be executed** | **`register.sh` in any mode, including `--guard`** · any `00-BOOK/DATA/` write · any fresh tool run capable of transacting · ratifying · reverting · discarding · staging · committing |
| **Required verification** | `VG-1`…`VG-6`, with `VG-4` **critical** · `by_path == 1,492` · `page_cursor == 10,840` · `category_seq == 200` keys · `by_object == 4,914` · `by_observation == 7` · all seven `00-BOOK/DATA/` files byte-identical · **a recorded confirmation that `register.sh` was not invoked** |
| **Stop conditions** | `SC-3` on any identity count movement · `SC-4` on porcelain non-identity · `SC-1` if the package is read or presented as authorization · **immediate stop and disclose if any ledger byte changes** — that is `RC-3` recurring |

### `W0-4` — `A(C)` admission map draft

| | Detail |
|---|---|
| **Can be implemented** | A proposal document containing a map total over the nine classes **and** the three ledger maps `["by_path","by_object","by_observation"]` · functional, no owner-parameterised value · fail-closed on `UNRESOLVED` · naming `UCOS-UGA-001` and the observation authority · every entry marked `PROPOSED` |
| **Cannot be executed** | Writing into `mutation-governance-boundary.json` or any programme declaration · adopting `uga-declaration.json`'s `object_classes` as the map · marking any entry `DECLARED` or `RATIFIED` · using the draft to evaluate `CIS-2` |
| **Required verification** | `VG-1`…`VG-5` · `mutation-governance-boundary.json` byte-identical (27,127 bytes) · totality checked over 9 × 3 · zero `DECLARED` entries |
| **Stop conditions** | `SC-1` — a drafted map placed in a live declaration surface makes the drafter the cross-authority arbiter, which `UCKP-ART-18` refuses · stop if any consumer reads the draft as the map |

### `W0-5` — ownership run-mode canonicality declaration

| | Detail |
|---|---|
| **Can be implemented** | Declare exactly one run mode canonical, with rationale · record the other two as non-canonical, **not deleted** · reproduce `subjects 549 · declared 151 · unresolved 398 · contested 0 · coverage 27.5046%` and the five diagnosis codes (186 / 212 / 2 / 45 / 195) · state that `00-MASTER/UAKOS-CLOSURE-002/31-CONCEPT-OWNERSHIP-REGISTER.md` is untracked, `.gitignore:58`-ignored, and defines ownership as a **directory path, not an authority** |
| **Cannot be executed** | **Any assignment** · any `UNASSIGNED` fallback · suppressing or catching-and-continuing `OwnershipFabricationError` · running Ownership Discovery in a mode not demonstrated read-only · producing the `P-A`/`P-B`/`P-C` partition (that is `CA-8`-E, Wave 1) |
| **Required verification** | `VG-1`…`VG-5` · `ucos-ownership-declarations.json` byte-identical (1,142 bytes) · `assignments == {}` before and after · zero assignments written |
| **Stop conditions** | `SC-2` on any assignment without a declared source **and** owner acceptance · stop if Ownership Discovery's read-only mode cannot be demonstrated — the `RC-4` hazard applies to the measurement itself |

---

## 5. W0-6 Gate Denominator Reconciliation

### 5.1 The disagreement

| Value | Source | How it was produced | Standing |
|---|---|---|---|
| **46** | `…ROOT-CAUSE-CLOSURE-AND-READINESS-DETERMINATION.md` `RC-4` / `CA-2` / `AG-2`; carried into the closure plan and the readiness determination | *"**4 of 46** Makefile gate targets declare one (`B-2`)"* — a curated inventory attributed to register `B-2` | Cited by three determinations in this chain; **provenance is a register, not a command** |
| **49** | Re-measured at HEAD `bae59755` for the readiness determination | `grep -cE "^[a-zA-Z0-9_.-]+-gate:" Makefile` → **49**; total `^name:` targets → 232 | **Reproducible now**; a raw pattern count, which is not authoritative over a curated inventory |
| **45** | `H-06-OWNERSHIP-DISPOSITION-DECISION-PACKAGE.md` GP-11a | *"mode declared for **2 of 45**. Extension applicable to **22**; not applicable to **23**"* — `22 + 23 = 45`, an internally consistent disposition inventory | A **third** figure, with its own two-way partition and a **different** declared-mode count (2, not 4) |

### 5.2 What the disagreement actually is

**Two independent axes disagree, not one:**

| Axis | Values | Note |
|---|---|---|
| Denominator | **45 · 46 · 49** | Three populations for "gate targets" |
| Already-declaring numerator | **2** (GP-11a) · **4** (`B-2`) | The numerator disagrees too, and no determination in this chain had noticed |

A raw `^*-gate:` count will include aliases, `.PHONY` entries, meta-targets and non-gate targets that happen to end `-gate`; a curated inventory will exclude some and may include gate paths not expressed as Makefile targets at all. **Both can be correct about different questions.** The 2-vs-4 numerator split suggests the two curated inventories also disagree about what "declares a mode" means — declaration in the target itself, versus declaration in a canonical owning surface.

### 5.3 Required authority

| Act | Authority | Status |
|---|---|---|
| Reproduce all three inventories | **NONE** — counting is not deciding | Available |
| Disposition each target as gate / alias / phony / non-gate | **NONE** — mechanical against a declared rule | Available |
| Define what "gate target" and "declares a mode" **mean** | **`AG-2`** — mutation governance owner | **LOCATED, OPEN** |
| Declare one denominator canonical | `AG-2` **if** the definitions differ; none if the three reconcile mechanically to one population | **CONDITIONAL** |

### 5.4 Resolution method

```
1  Reproduce each figure with its exact command or citation. Record all three verbatim.
2  Emit the full 232-target Makefile inventory, one row per target.
3  Disposition every row against a WRITTEN rule: gate | alias | phony | meta | non-gate.
4  Reconcile: show precisely which targets the 49-count includes that 46 and 45 exclude,
   and which the curated inventories include that the pattern misses.
5  Reconcile the numerator separately: which targets B-2's "4" counts and GP-11a's "2"
   does not, and under which definition of "declares a mode".
6  IF steps 3–5 reduce the three populations to one under a single written rule
     → declare it canonical, showing the derivation. No authority needed.
   ELSE the figures differ because the DEFINITIONS differ
     → escalate to AG-2. Do not choose.
```

### 5.5 Acceptance criteria

| # | Criterion |
|---|---|
| A-1 | All three values (45, 46, 49) reproduced with the command or citation that produced each — **none paraphrased** |
| A-2 | The 232-target inventory emitted in full, every row dispositioned against a written rule |
| A-3 | The set difference between every pair of populations exhibited **by name**, not by count |
| A-4 | The 2-vs-4 numerator disagreement reconciled or escalated **separately** from the denominator |
| A-5 | Either one denominator declared canonical **with its derivation shown**, or the disagreement escalated to `AG-2` with the three definitions stated |
| A-6 | **No value chosen by preference, recency, majority, or convenience.** A count with three sources and no reconciliation is not resolved by picking one |
| A-7 | `Makefile` byte-identical — zero edits, zero mode fields populated |
| A-8 | No completeness percentage computed anywhere until A-5 closes |

**This determination does not choose 45, 46 or 49.** Doing so would be the fabrication the ownership machinery refuses in its own domain, applied to a different denominator.

---

## 6. Change Safety Protocol

Mandatory. Applies to every action; `W0-1` is the only action that reaches the "During" phase against an existing file.

### 6.1 Before change

```
B-1  git rev-parse HEAD                      → record; MUST equal bae59755d7e2d…269a
B-2  git rev-parse --abbrev-ref HEAD         → record; MUST equal integration/recovery-001
B-3  git status --porcelain > <baseline>     → record verbatim, 354 lines
B-4  git diff --cached --name-only | wc -l   → MUST be 0
B-5  git diff --name-only > <tracked>        → record; 38 entries
B-6  Per-file baseline evidence for every file the action may touch:
       sha256 of each target file
       sha256 of all 7 00-BOOK/DATA/*.json
       sha256 of ucos-ownership-declarations.json, uis.json,
              07-CERTIFICATION.json, certification.json,
              mutation-governance-boundary.json
B-7  Action-specific pre-state:
       W0-1  validate_rule_coverage() return value; classify() status on a sample
       W0-3  by_path · by_object · by_observation · page_cursor · category_seq key count
       W0-5  assignments == {} confirmed
B-8  VG-1 and VG-2 executed and PASSING before any edit
```

### 6.2 During change

```
D-1  ONE ATOMIC CHANGE per action. W0-1's atom is: one predicate function +
     one checks helper + one RULE_PREDICATES entry + its tests. Nothing else.
D-2  NO UNRELATED EDITS. No formatting, no import reordering, no type-hint
     tidying, no docstring rewrites, no lint-driven changes to untouched lines.
D-3  NO HIDDEN MUTATIONS:
       no command that writes outside the declared target files
       register.sh NOT invoked, in any mode, for any reason
       no gate, engine or make target run that has not been shown to be OBSERVE
       no test run that writes to a governed surface
D-4  The 38 pre-existing tracked modifications are NOT touched, reverted,
     amended, staged or absorbed. The action's diff MUST be separable from them.
D-5  No staging. No commit. No stash. No checkout. No clean.
```

### 6.3 After change

```
A-1  Execute verification: V-1…V-10 for W0-1; the action's acceptance criteria otherwise
A-2  git diff review — read EVERY changed line. Confirm each line is within D-1's atom
     and that no line belongs to the pre-existing 38
A-3  git status --porcelain → byte-compare against B-3
       PERMITTED delta:  only the declared target files, and only in their
                         already-modified or newly-untracked status
       ANY other delta  ──▶ STOP, do not proceed, disclose
A-4  Re-verify every sha256 from B-6 that the action was not permitted to touch
A-5  VG-1…VG-6 all executed; all MUST PASS
A-6  If any gate FAILS ──▶ rollback per §8. Do not "fix forward"
```

### 6.4 The directive's "git status clean requirement", corrected

The directive requires a clean `git status` after change. **That requirement cannot be satisfied at this baseline and is not a meaningful gate here.** The tree carries 354 porcelain lines before any action, 316 of them untracked, including the 228 unratified registrations. Making the tree clean would require discarding them, which requires `AG-3`, which is not located — and doing so would destroy 228 permanent identifiers and 1,014 page allocations irreversibly.

**Substituted requirement, `A-3` above:** `git status --porcelain` **byte-identical to the recorded pre-action baseline except the declared target files**. This is strictly stronger than a clean-tree check in the only way that matters — it detects an unintended change to *any* of the 354 existing entries, which a clean-tree assertion on a dirty tree cannot do at all. The substitution is disclosed rather than silent, and it does not weaken the protocol.

---

## 7. Validation Gates

Six. **All six PASS before any action begins; `VG-1`, `VG-2`, `VG-4`, `VG-5`, `VG-6` re-run after each action.**

### `VG-1` — Baseline Integrity

```
ASSERT  HEAD    == bae59755d7e2d3566c93b89c722b68847145269a
        branch  == integration/recovery-001
        staged  == 0
        porcelain byte-identical to B-3 except declared target files
        tracked-modified set byte-identical to B-5  (38 entries, same paths)
FAIL    any unintended path appears, disappears or changes status  ──▶ STOP
NOTE    clean-tree assertion is INVALID here; byte-comparison only  (§6.4)
```

### `VG-2` — Mutation Boundary

```
ASSERT  no write occurred outside the action's declared allowed-changes list
        register.sh not invoked, in any mode                    ← recorded, not assumed
        no command executed that has not been shown to be OBSERVE
        no staging, no commit, no stash, no checkout, no clean
        the 38 pre-existing modifications untouched and unabsorbed
FAIL    any prohibited surface shows a byte change  ──▶ STOP AND DISCLOSE
```

### `VG-3` — Classification Correctness  *(`W0-1` only)*

```
PRE     validate_rule_coverage() == ("rule 'R-09' is declared but no predicate ...",)
        classify() == ERROR for a heterogeneous sample        ← RC-1 confirmed present
POST    V-1   validate_rule_coverage() == ()
        V-2   classify() ∈ {CLASSIFIED, UNRESOLVED}; never ERROR
        V-3   at least one subject → GOVERNED_ANALYSIS with rule_id == "R-09"
                ▓▓▓ CANNOT PASS without an AG-2b decision — §3.2 ▓▓▓
        V-4   negative test: predicate REJECTS a non-analysis subject
        V-5   two runs digest-identical
        V-6   zero mutations during classification, mutation-tested
        V-7   unknown input → UNRESOLVED, never permissive
        V-8   missing Authority falls through to R-08, no fabrication
        V-9   set(RULE_PREDICATES) == {declared ids} guard fails at test time
        V-10  mutation_class_extension.py dispositioned
FAIL    any of V-1…V-10  ──▶ W0-1 NOT ACCEPTED. V-3 fails today, by measurement
```

### `VG-4` — Registry Safety

```
BYTE-COMPARE before and after EVERY action:
  00-BOOK/DATA/  id-ledger.json · change-ledger.json · relationships.json
                 artifacts.json · volumes.json · control-tower.json
                 generated-artifact-registry.json
  00-BOOK/DATA/mutation-governance-boundary.json      (27,127 bytes)
  constitutional-authority-alignment.json
ASSERT  by_path == 1,492 · by_object == 4,914 · by_observation == 7
        page_cursor == 10,840 · category_seq == 200 keys
        id-ledger.json top-level keys == 9  (no supersession map added)
        anonymous objects == 7
        00-MASTER/UIS-001/uis.json byte-identical
        platform/universal_ownership/catalog/ucos-ownership-declarations.json
              byte-identical, assignments == {}
FAIL    any byte differs  ──▶ STOP AND DISCLOSE. A registry or identity mutation
        without AG-3 / AG-5 / AG-8 has occurred. This is RC-3 recurring
```

### `VG-5` — Evidence Completeness

```
ASSERT  every acceptance criterion has a recorded artifact of evidence — a command
        and its output, or a cited measurement. No criterion marked satisfied by
        assertion alone
        every measured figure carries the command that produced it
        every disagreement is DISCLOSED, not reconciled by preference   (45/46/49; 2/4)
        certification artifacts byte-identical:
          00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json
          00-BOOK/DATA/certification.json
          the UNAF-001 freeze record
        no verdict emitted at any level; none above CERTIFIED-PROVISIONAL
        absence of evidence recorded as NOT-DONE, never as pass   (TRACK-001 fail-closed)
FAIL    any criterion asserted without evidence  ──▶ NOT ACCEPTED
```

### `VG-6` — Rollback Validation

```
ASSERT  a rollback path exists and has been REHEARSED before the change:
          the exact revert command recorded
          the post-rollback expected sha256 of every target file recorded
          rollback demonstrated to restore byte-identity to B-6
        the rollback does NOT require touching the 38 pre-existing modifications
        the rollback does NOT require touching any 00-BOOK/DATA/ file
        no action proceeds whose rollback would cross a prohibited surface
FAIL    rollback unrehearsed, or crosses a prohibited surface  ──▶ ACTION NOT AUTHORIZED
```

---

## 8. Rollback Model

### 8.1 Rollback triggers

| Trigger | Detected by |
|---|---|
| Any prohibited surface shows a byte change | `VG-2`, `VG-4` |
| Porcelain delta beyond the declared target files | `VG-1` `A-3` |
| Any identity count moves | `VG-4` |
| Any certification artifact changes | `VG-5` |
| `assignments` no longer `{}` | `VG-4` |
| `register.sh` invoked | `VG-2` |
| `V-1`…`V-10` failure after implementation | `VG-3` |
| A change outside the declared atom appears in `git diff` | `A-2` |
| Any stop condition `SC-1`…`SC-10` trips | continuous |

### 8.2 Rollback method

```
DOCUMENT-ONLY ACTIONS  (W0-1a, W0-2 … W0-6)
  rm <the new untracked file>
  Trivial and total. No tracked file was touched; no governed surface exists to restore.

CODE-CHANGING ACTION  (W0-1)
  git checkout -- platform/repository_intelligence/mutation_classification.py   ← ONLY IF
  git checkout -- platform/tests/test_mutation_classification.py               ← the file's
                                                                                 pre-action
                                                                                 state was
                                                                                 committed
  ▓ test_mutation_classification.py is TRACKED-MODIFIED (+3/−3) at baseline. A
    plain checkout would DISCARD that pre-existing diff, which this scope does
    not own and may not destroy.
  REQUIRED METHOD INSTEAD:
    1. Before the change, save the working-tree copy of both files verbatim
       (copy to an out-of-tree location; sha256 recorded per B-6)
    2. Rollback = restore those saved copies byte-for-byte
    3. Verify sha256 equality against B-6
    4. NEVER `git checkout --` on a file carrying a pre-existing uncommitted diff
    5. NEVER git stash, git clean, git reset, or git restore --staged
```

### 8.3 Preserved evidence

Rollback restores files; it does **not** delete evidence. Retained in all cases:

| Retained | Why |
|---|---|
| The `B-1`…`B-8` baseline record | The pre-action state must remain provable after rollback |
| The full `git diff` of the reverted change | What was attempted is a finding, not a mistake to erase |
| Every gate result, including the failures that triggered rollback | `VG-3` `V-3` failing is the §3.2 evidence |
| The trigger, timestamped, with the gate that detected it | Recurrence prevention |
| The post-rollback sha256 set | Proof the rollback was total |

**Under `AIF-L17`, a correction is a new event, never a deletion.** A rolled-back action is recorded as attempted-and-reverted, not as never-attempted.

### 8.4 Prohibited rollback scenarios

| Scenario | Why prohibited |
|---|---|
| `git checkout --` on a file with a pre-existing uncommitted diff | Destroys work this scope does not own — `test_mutation_classification.py` |
| `git stash` | Removes the 38 pre-existing modifications from the tree; the baseline is no longer provable |
| `git clean -fd` | Would delete the 228 untracked registrations, destroying 228 identifiers and 1,014 page allocations **irreversibly** — and `category_seq` does not roll back, so re-minting issues **different** identifiers |
| `git reset --hard` | Same destruction, plus loss of the tracked diffs |
| `git reset --soft` / `--mixed` | HEAD or index movement; HEAD must remain `bae59755` |
| Any rollback touching `00-BOOK/DATA/` | Requires `AG-3`. A rollback is not an authorization |
| Rolling back an identity mutation | **There is no rollback for one.** `RC-7`: no `git` operation reverts an arbitration failure without also discarding the 192 identities it was performed over. After the first supersession record, `AIF-L17` forbids deletion or edit — only forward-only compensation under `AIF-L15`. **This is why no action in Wave 0 may write identity** |
| Rolling back a certification artifact by amendment | `AIF-L21` — corrections are new events in a distinct store, never amendments |
| "Fix forward" instead of rolling back | A failed gate means the pre-state was not understood. Forward fixes compound |

---

## 9. Execution Readiness Decision

> # WAVE 0 IMPLEMENTATION: READY FOR SIX OF SEVEN ACTIONS · `W0-1` IMPLEMENTABLE BUT NOT ACCEPTABLE
>
> **The six document-only actions (`W0-1a`, `W0-2`…`W0-6`) are ready to execute: zero governed-surface writes, no authority required to perform any of them, trivial and total rollback. `W0-1` — the R-09 predicate — is implementable to nine of its ten validation rules and cannot satisfy the tenth, because R-09's membership set is a strict subset of R-08's and R-08 evaluates first, making R-09 unreachable by construction. Repairing that requires changing either a declared precedence or a declared predicate, both explicitly out of `CA-1`'s scope, and both owned by the mutation governance owner. Referred as `AG-2b`. No `READY` verdict is claimed: nothing was executed and no closure was measured.**

### 9.1 W0 implementation readiness

| Action | Readiness | Basis |
|---|---|---|
| `W0-1a` `S-1` package | **READY** | Document only; `W0-6` improves it but does not block preparation |
| `W0-2` carrier package | **READY** | Document only; the decision it serves is `AG-5`, not located |
| `W0-3` Article 28 package | **READY, `SC-3` ACTIVE** | Must be assembled from recorded measurements only; `register.sh` prohibited |
| `W0-4` `A(C)` draft | **READY** | Proposal only; every entry `PROPOSED`; `UCKP-ART-18` boundary explicit |
| `W0-5` ownership run-mode | **READY, `SC-2` ACTIVE** | Scope declaration, not assignment; catalogue byte-compared |
| `W0-6` denominator | **READY — and highest priority** | Removes a false-completeness risk from `RC-4`, the antecedent of `RC-3` |
| `W0-1` R-09 predicate | **IMPLEMENTABLE, NOT ACCEPTABLE** | V-1, V-2, V-4…V-10 achievable today. **V-3 unsatisfiable** — §3.2 |

### 9.2 W0 blocked items

| Item | Blocker | Class | Reducible by work? |
|---|---|---|---|
| `W0-1` acceptance (`V-3`) | **`AG-2b`** — precedence-vs-predicate decision for R-08/R-09 disjointness | **NEW — LOCATED, OPEN** | **No.** Both available repairs are out of `CA-1`'s declared scope |
| `W0-1` `V-10` | `mutation_class_extension.py` disposition — if it is the intended registration path, the implementation belongs there | `AG-2b` | No |
| `W0-6` `A-5` | Possibly `AG-2`, if the three figures differ by definition rather than by counting | Conditional | Partly — steps 1–5 are mechanical |
| `W0-1a` completeness reporting | `W0-6` | Internal | **Yes** — `W0-6` first |
| Every decision the six packages serve | `AG-2`, `AG-3`, `AG-4`, `AG-5` | 1 located, 3 not | No |

### 9.3 W1 dependency impact

| Wave 1 action | Impact of this determination |
|---|---|
| `W1-1` = `CA-1` | **Status degrades from READY to IMPLEMENTABLE-NOT-ACCEPTABLE.** The readiness determination assessed it READY on the basis that `AG-1` was available and no input was unresolved. §3.2 identifies an unresolved input that measurement, not assessment, revealed |
| `W1-2` = `CA-2`-E | Unchanged: NOT READY on `W0-6` and `AG-2` |
| `W1-3` = `CA-6`-E | Unchanged: READY at specification scope. `W0-2` supplies its input |
| `W1-4` = `CA-8`-E | Unchanged: NOT READY on `W0-5` and the unconfirmed read-only mode |
| `W1-5` = `CA-9`-E | **Degrades.** Depends on `W1-1` via `E-04` (*a certification act must be classifiable*). If `R-09` never fires, analysis artifacts classify as `AUTHORED_DOCUMENT`, and 127 of the 192 Group B subjects plus the modified MIP plan are governed by the wrong class — `G-11`'s exact population |
| **Wave 1 net** | **0 of 5 unconditionally acceptable**, down from 1 of 5. `W1-1` was the one, and its acceptance now depends on `AG-2b` |

### 9.4 Overall verdict

**`NOT READY` — unchanged, and now for one more reason than before.**

| # | Finding |
|---|---|
| 1 | **Six of seven Wave 0 actions are ready to execute now.** Zero governed-surface writes, no authority required, total rollback. This is the only fully unblocked scope in the programme |
| 2 | **`W0-1` cannot be accepted as scoped.** R-09 ⊂ R-08 and R-08 evaluates first. Adding the predicate clears the `ERROR` outage — a real gain, restoring classification for eight of nine classes — while leaving R-09 dead in effect and the declared `unique` disjointness property violated |
| 3 | **One new authority blocker was found by measurement: `AG-2b`.** It is LOCATED and OPEN, held by the same owner as `AG-2` and `AG-4`, and it is a small decision — which precedence or which predicate — not a constitutional act. It brings the authority-blocker count from 9 to 10 |
| 4 | **A second unnoticed disagreement was found:** the already-declaring numerator reads **2** in GP-11a and **4** in `B-2`. `W0-6` must reconcile the numerator separately from the denominator |
| 5 | **Wave 1's unconditional readiness falls from 1 of 5 to 0 of 5**, because the one ready action's acceptance now depends on `AG-2b` |
| 6 | **`READY` is not claimed and cannot be.** Nothing was executed, no root cause closed, no blocker discharged. `UCCEP-F-004` caps every verdict at `CERTIFIED-PROVISIONAL` and `VAC-01` renders this determination `PROVISIONAL` |

**Recommended sequence:** `W0-6` first (mechanical, removes a false-completeness risk from the antecedent of the largest blocker), then `W0-1a`, then refer `AG-2b` with §3.2 attached, then `W0-2`…`W0-5` in any order. `W0-1` may be **implemented** to V-1/V-2/V-4…V-10 to clear the repository-wide `ERROR` outage, provided it is **recorded as partially accepted with `V-3` open** and provided no consumer gates on mutation class until `AG-2b` closes.

---

## 10. Verification Record

| Check | Result |
|---|---|
| File exists | ✅ `UCOS-OMEGA-INFINITY-WAVE-0-EXECUTION-IMPLEMENTATION-DETERMINATION.md` |
| Line count | ✅ **726** — measured post-write against the final file; recorded in the session transcript |
| Section count | ✅ **10** `## ` headings — §1 Current Baseline · §2 Wave 0 Scope · §3 W0-1 R-09 Predicate Implementation Boundary · §4 W0-2 Through W0-5 Execution Boundaries · §5 W0-6 Gate Denominator Reconciliation · §6 Change Safety Protocol · §7 Validation Gates · §8 Rollback Model · §9 Execution Readiness Decision · §10 Verification Record |
| Required Wave 0 fields | ✅ all eight present for each of `W0-1`, `W0-1a`, `W0-2`…`W0-6` — Action ID · Objective · Root cause addressed · Dependencies · Allowed changes · Forbidden changes · Required authority · Expected evidence |
| Required `VG` set | ✅ `VG-1` Baseline Integrity · `VG-2` Mutation Boundary · `VG-3` Classification Correctness · `VG-4` Registry Safety · `VG-5` Evidence Completeness · `VG-6` Rollback Validation |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Staged changes | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to plan start |
| Exactly one new artifact | ✅ porcelain 354 → 355; the single delta is this file |
| Code mutations | ✅ **0** — `mutation_classification.py` read only, byte-identical |
| Configuration mutations | ✅ **0** |
| Registry mutations | ✅ **0** — `mutation-governance-boundary.json` parsed read-only, 27,127 bytes unchanged |
| Certification mutations | ✅ **0** |
| Identity mutations | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys |
| Ownership mutations | ✅ **0** — `assignments` remains `{}` |
| Commits | ✅ **0** |
| `register.sh` invocations | ✅ **0** — in any mode |
| Mutation-producing commands | ✅ **0** — read-only: `git rev-parse`, `git status`, `git diff --name-only`, `grep`, `ls`, `find`, and `json.load` |
| Wave 0 actions executed | ✅ **0** |
| Root causes closed | ✅ **0** |
| Blockers discharged | ✅ **0** — and **1 new blocker identified**, `AG-2b` |
| Authorities vested | ✅ **0** |
| Values chosen by preference | ✅ **0** — 45/46/49 and 2/4 both left unresolved and escalated |

---

*This determination executed nothing, closed no root cause, discharged no blocker, vested no authority, arbitrated no subject, minted no identity and assigned no ownership. It converts the Wave 0 readiness assessment into a controlled implementation package for seven actions, six of which are ready to execute today with zero governed-surface writes and total rollback. Its two substantive findings come from reading the code and the register rather than the determinations: R-09's six membership criteria are R-08's five plus one, so R-09 is a strict subset of R-08, and because R-08 is declared first and `classify()` evaluates in declared order, implementing the R-09 predicate exactly as specified leaves R-09 unreachable for every subject it was written for — which makes `CA-1`'s all-nine-classes acceptance criterion unsatisfiable within `CA-1`'s own declared scope, since both available repairs are things `CA-1` forbids. That is referred as `AG-2b`, a new authority blocker, located and open, and small. Separately, the gate-target disagreement is worse than a denominator: the already-declaring numerator reads 2 in one source and 4 in another. Neither the 45/46/49 split nor the 2/4 split is resolved here, by preference or otherwise. Wave 1's unconditional readiness falls from 1 of 5 to 0 of 5. The working tree carries the same 38 tracked modifications it carried at the start, `by_path` stands at 1,492 before and after, the ownership catalogue holds zero assignments before and after, and the single repository mutation is the creation of this file.*

**END DETERMINATION — 7 WAVE 0 ACTIONS · 6 READY · W0-1 IMPLEMENTABLE-NOT-ACCEPTABLE · 1 NEW AUTHORITY BLOCKER (AG-2b) · 2 MEASUREMENT DISAGREEMENTS DISCLOSED · 6 VALIDATION GATES · VERDICT NOT READY · ZERO ACTIONS EXECUTED · ZERO MUTATIONS PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
