# UCOS Ω∞ — OBSERVATION BOUNDARY RECONCILIATION DETERMINATION

**BC-6 · Step 2 — The canonical visibility boundary for every repository artifact**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-OBSERVATION-BOUNDARY-RECONCILIATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, requirement, ADR, phase or certification. Authorizes nothing. Assigns no ownership. Approves no commit. Changes no ignore rule. |
| Mode | READ-ONLY RECONCILIATION · **NO FILE MODIFIED · NO COMMIT · NO REGISTRY WRITE · NO CERTIFICATION WRITE · NO IGNORE-RULE CHANGE** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Step | **BC-6 Step 2 only.** Steps 3–6 of the companion plan are not performed |
| Predecessors | `…BASELINE-INTEGRITY-RECONCILIATION-REPORT.md` (BC-6 Step 1, F-2 / F-5) · `…BLOCKER-CLOSURE-STATUS-REGISTER.md` §8 (A6-2, G-9) · `…BLOCKER-CLOSURE-IMPLEMENTATION-PLAN.md` §3.6 |
| Acceptance criterion addressed | **A6-2** — *"Exclusion authority settled — G-9 `.gitignore` landed or reverted first"* |
| Population reconciled | **6,188 tracked · 308 untracked-and-un-ignored · 233 ignored entries** |
| Findings raised | **7** (`OB-1`…`OB-7`) · 1 CRITICAL · 2 HIGH · 3 MEDIUM · 1 LOW |
| Findings resolved by this determination | **ZERO.** Reconciliation is not repair |
| Ignore rules added, removed or amended | **ZERO** |

---

## 1. Objective, Method and Standing Limitation

### 1.1 Objective

Determine **the canonical visibility boundary**: for every class of repository artifact,
which authority decides whether that artifact is visible, and which authority is merely
reporting a consequence of that decision.

Step 1 classified every mutation and left two boundary defects open — `F-2` (PORTAL has
three disagreeing authorities) and `F-5` (the programme's evidence base is untracked).
Both are visibility defects, not attribution defects, and both must be settled before
`A6-1` attribution can be trusted: **an attribution census over a population whose
membership is itself contested is not a census.** That is why the status register orders
`A6-2` **FIRST — the gate's field of view**.

### 1.2 Method

Every measurement is a **read** or an **in-memory comparison**. Nothing was written,
committed, staged, restored, deleted, ignored, un-ignored or registered.

| Instrument | Purpose |
|---|---|
| `git ls-files` / `--others --exclude-standard` | Tracked-set and untracked-and-un-ignored-set membership |
| `git status --porcelain --ignored=matching --untracked-files=all` | The ignored-inclusive filesystem — the observation surface `UCOS-CL-001` mandates |
| `git check-ignore -v` | Which ignore rule, at which `.gitignore` line, claims a path |
| `git check-ignore --no-index` over `git ls-files` | Exclusion-register invariant 2 (tracked-but-shadowed) |
| `git diff .gitignore` / `--numstat` | The G-9 mutation, exactly |
| `git show HEAD:.gitignore` | The committed ignore boundary, without touching the working copy |
| `git log --oneline -- .gitignore` | Provenance of the ignore authority |
| `platform.repository_intelligence.contamination.measure()` | First-party execution of the declared contamination metric |
| `contamination._classify()` over probe rules | **Direct test of whether the classification obligation is real** |
| `json.load` on the four candidate authorities | Structural comparison of declared scope against actual coverage |

The contamination measurement was executed **first-party**, in-process, against the live
tree, using the repository's own canonical implementation. It wrote nothing: `measure()`
is a pure function over `git` reads and two JSON reads.

### 1.3 Standing limitation, declared not hidden

Step 1's limitation carries forward unchanged: `classify()` returns `ERROR` for every
subject at this baseline (BC-1 / M-C), because `R-09` is declared with no predicate.
Every mutation-class reference below is therefore a **manual reading of declared
predicates, not a machine verdict**, and none may be treated as a classification of
record. This determination adds a second, narrower limitation of its own, and it is the
CRITICAL finding: the one metric that *is* machine-computable in this domain —
`ignored_unclassified` — is measured below to be **structurally incapable of returning a
non-zero value**. See `OB-1`.

---

## 2. The `.gitignore` Mutation (G-9)

### 2.1 What changed, exactly

`git diff --numstat .gitignore` → **`9  0  .gitignore`**. Nine lines added, none removed,
one hunk, appended at end of file. One active pattern; eight comment lines.

```
+# UEG-000001 — the execution environment fingerprint cache and the per-run execution
+# evidence. Both describe THIS MACHINE'S environment: an interpreter path, a venv prefix,
+# an installed toolchain. None of it reproduces on another machine, so committing it would
+# publish a claim that is false everywhere except where it was written. The cache may skip
+# exactly one measurement and never a verdict (see the declaration), so deleting the whole
+# directory changes no verdict — only the cost of reaching one. The evidence is emitted
+# fresh by every certified run and is bound into certification from there, not from git.
+.ucos/
```

The single functional delta is the pattern **`.ucos/`**, resolving at `.gitignore:231`.

### 2.2 Why it changed

The stated reason is machine-locality, and it is **substantively correct**. `.ucos/`
holds exactly two files, both declared in `00-MASTER/UEG-000001/ueg-declaration.json`:

| Path | Declared standing | Declared `gitignored` |
|---|---|---|
| `.ucos/environment-fingerprint.json` | *"A CACHE OF A MEASUREMENT, NEVER A SUBSTITUTE FOR ONE."* | `true` |
| `.ucos/execution-evidence.json` | Per-run execution evidence, 8 declared records | `true` |

Both contain an absolute interpreter path, a venv prefix and an installed-toolchain
inventory. Committing either would publish a claim true only on the writing machine.
The declaration says so before the ignore rule did: the rule **records** a declared
property rather than inventing one.

The comment's two load-bearing technical claims were verified against source, not taken
on trust:

**Claim: "The cache may skip exactly one measurement and never a verdict."** Confirmed.
`engine/execution_environment/gate.py::measure()` uses the cache for exactly one purpose
— producing `tool_records`, one argument to `observe()`. `assess()` then runs
unconditionally. `EEG-01`…`EEG-05` are recomputed on every invocation; only `EEG-06`'s
distribution `RECORD` scan is answerable from cache. `fingerprint.load()` maps an
unreadable or malformed cache to `None` → `STATE_MISS` → full scan. `store()` is gated on
`environment.valid`, so an invalid environment is never cached. **A missing `.ucos/`
costs work, never a verdict, and never a pass.**

**Claim: evidence "is bound into certification from there, not from git."** Confirmed,
and this is the claim with a consequence the comment does not draw — see `OB-4`.

### 2.3 Owner

| Question | Answer | Basis |
|---|---|---|
| Owner of the **rule** | **Exclusion owner** (status register G-9) | Read from the register's group table; **not assigned here** |
| Owner of the **subject** | **UEG-000001 / environment owner** | `ueg-declaration.json` is the declaring home |
| Owner of the **classification obligation** | **`00-BOOK` / exclusion-register owner** | `00-BOOK/DATA/exclusion-register.json` is the tracked, authored register |

These are three different owners, and the mutation discharges only the first. That
division is the mechanism of `OB-2`.

### 2.4 Authority — and the obligation the rule did not pay

`00-BOOK/DATA/exclusion-register.json` is the declared authority for what an exclusion
*means*. Its own `why_this_exists` states the constitutional principle verbatim:

> *"The correction is not a better pattern. It is that **EXCLUSION MUST COST A
> DECLARATION**. […] An ignored path with no declared class is `ignored_unclassified` and
> FAILS CLOSED. Adding an ignore rule therefore no longer removes an observation; it adds
> a classification obligation. The metric cannot be shrunk by editing `.gitignore`, which
> is the property that was missing."*

Its invariant 1: *"Every ignored path resolves to exactly one entry here
(`ignored_unclassified` = 0)."*

Measured against that authority:

| Measure | Value |
|---|---|
| Exclusion-register entries | **32** |
| Active `.gitignore` patterns (non-comment, non-blank) | **55** |
| Register entry for `.ucos/` | **ABSENT** — `load_register()` mapping lookup returns nothing |
| Register entry for `.ucos-verification-evidence/` (`.gitignore:222`, already at HEAD) | **ABSENT** |

**The G-9 mutation added an ignore rule and did not add the declaration that rule was
declared to cost.** The predecessor rule at `.gitignore:222` did not either. Under the
register's own stated principle both should be `ignored_unclassified` and both should
fail closed. Neither does — and the reason is `OB-1`.

### 2.5 Impact on verification

| Dimension | Impact | Evidence |
|---|---|---|
| Verdict correctness | **None.** Absence of `.ucos/` is a MISS, never a pass | `fingerprint.py:96-107`; `gate.py:78-84` |
| Tracked-tree cleanliness | **Positive.** Without the rule, every `verify.sh` run dirties the tree via Stage 0, making a clean tree unreachable | `verify.sh:124-126`; `scripts/ucos-env.sh:408-427` |
| `ignored_unclassified` metric | **None measurable — and that is the defect** | `OB-1` |
| Contamination surface | `.ucos/` moves from `??` to `!!`; **2 files** | `find .ucos -type f` → 2 |
| Reproducibility (`A6-8`) | **Negative, indirectly.** Certification evidence exists only on the emitting machine and is not reconstructible from a clean checkout after the fact | `OB-4` |
| Attributability (`A6-1`) | **Positive.** The rule is the smallest, best-documented mutation in the 38-file set: 8 comment lines for 1 pattern, with a verifiable declaration behind it | `git diff .gitignore` |

**On the merits, the rule should land.** It is correct, it is declared, its subject is
genuinely machine-local, and reverting it makes `A6-6` unreachable. It should not land
*alone* — `OB-2` names the one artifact that must accompany it.

---

## 3. `OB-1` — The Classification Obligation Is Structurally Void

**Severity: CRITICAL. This is the finding that governs the entire step.**

### 3.1 The measurement

First-party execution of the canonical metric against the live tree:

```
ignored_unclassified:   0
unclassified_paths:     0
excluded_entries:     233
clean:              False   (from dirty/untracked counts, not from exclusion)
```

`.ucos/` classifies as **`CACHE`**. So does `.ucos-verification-evidence/`. Neither has a
register entry. The classification comes from `contamination._classify()`, whose fallback
is a **bidirectional** `fnmatch`:

```python
def _classify(rule: str, register: Mapping[str, str]) -> str | None:
    if rule in register:
        return register[rule]
    # A nested tool-authored `.gitignore` may hold a bare `*`; the register declares that
    # form once rather than once per cache directory.
    for declared, klass in register.items():
        if fnmatch.fnmatch(rule, declared) or fnmatch.fnmatch(declared, rule):
            return klass
    return None
```

The register contains a bare `*` entry, admitted for nested tool-authored caches:

```json
{ "rule": "*", "class": "CACHE", "owner": "tool-authored nested .gitignore",
  "producer": "mypy and peers",
  "rationale": "Several caches write a nested `.gitignore` holding `*` to self-exclude.
    The rule is scoped to the cache directory that contains it, never to the repository
    root, and is admitted only in that scope." }
```

`fnmatch.fnmatch(anything, "*")` is unconditionally `True`. Therefore **every** ignore
rule resolves to `CACHE`. Probed directly:

| Probe rule | `_classify()` result |
|---|---|
| `.ucos/` | `CACHE` |
| `totally-invented-rule/` | `CACHE` |
| `secrets/` | `CACHE` |
| `src/` | `CACHE` |
| `00-BOOK/PORTAL/` | `CACHE` |

### 3.2 What this means

`ignored_unclassified` **cannot return a non-zero value for any input**. It is not a
measurement; it is the constant `0`. Three consequences:

1. **The `UCOS-CL-001` correction is defeated by its own admission.** The defect closed at
   `be46a300` was that two `.gitignore` lines removed 41 physically-present files from the
   gate's observation surface, flipping `GATE-12` and `GATE-04`, opening `rib.json:gate`,
   satisfying AEE `OBS-BLUEPRINT-GATE` and clearing `CONV-02` — *"A one-line ignore rule
   could buy a convergence certification."* The register's fix was to make an ignore rule
   cost a declaration. **It does not.** Any single ignore line is still self-classifying,
   so the same purchase is still available by the same mechanism.
2. **The register's own scoping instruction is not implemented.** The `*` entry declares
   itself *"scoped to the cache directory that contains it, never to the repository root."*
   `_classify()` receives only a rule string and has no parameter for the `.gitignore`
   that authored it, so the declared scope restriction is unrepresentable in the current
   signature. The register legislates a constraint the classifier cannot express.
3. **Step 1's `A6-2` cannot be discharged by measurement.** `ignored_unclassified = 0` is
   not evidence that the exclusion authority is settled; it is evidence of nothing at all.
   Any closure claim resting on that number is unfounded.

### 3.3 Standing

This finding is raised, measured and **left open**. Repair is implementation and is
outside this step. It is recorded here because it is the reason `OB-2` is a real finding
rather than a satisfied obligation, and because **any BC-6 closure claim citing
`ignored_unclassified = 0` must be refused until it is repaired.**

---

## 4. `OB-2` — Two Ignore Rules Carry No Declaration

**Severity: HIGH. Blocks `A6-2` on the merits, independently of `OB-1`.**

| Rule | `.gitignore` line | Register entry | Standing |
|---|---|---|---|
| `.ucos-verification-evidence/` | 222 (committed at HEAD) | **ABSENT** | Pre-existing debt |
| `.ucos/` | 231 (**G-9, uncommitted**) | **ABSENT** | Introduced by the mutation under review |

Both subjects are genuinely excludable and both are declared elsewhere —
`00-MASTER/UVI-000001/uvi-declaration.json` states `"tracked": false` for the evidence
store and calls it *"A CACHE, NOT A RECORD OF TRUTH"*; `ueg-declaration.json` states
`"gitignored": true` for both `.ucos/` paths. **The subjects are not in doubt. The
declaration is simply in the wrong register.**

Note the asymmetry that makes this precise rather than pedantic: the UVI gate
(`engine/verification_intelligence/gate.py:262-276`, wired at `verify.sh:606`) *does*
measure that `.ucos-verification-evidence/` is excluded by `.gitignore` — it refuses if
the store is **not** ignored. So the repository verifies the ignore rule exists and never
verifies the register entry exists. The obligation is enforced in the direction that was
already satisfied and unenforced in the direction that was not.

`A6-2` asks whether the exclusion authority is *settled*. It is not: the ignore authority
and the exclusion register disagree about 23 patterns (55 active vs 32 entries), and the
two most recent additions are both on the uncovered side.

---

## 5. Visibility Census — Five Artifact Classes Compared

### 5.1 The three visibility states

Every path in the repository occupies exactly one:

| State | Definition | Count |
|---|---|---|
| **TRACKED** | In the index | **6,188** |
| **IGNORED** | Claimed by a non-negated ignore rule | **233** entries |
| **UNDECLARED-INVISIBLE** | Untracked **and** un-ignored | **308** |

The third state is the defect state. It is not a decision — it is the *absence* of a
decision, and nothing in the repository declares it, budgets for it, or gates on it as
such.

### 5.2 The comparison

| # | Class | Representative population | Visibility | Declared by | Gate that would catch a violation |
|---|---|---|---|---|---|
| 1 | **Tracked source** | `engine/`, `platform/`, `scripts/`, `verify.sh` | TRACKED | none — convention | ruff/pytest, indirectly |
| 2 | **Authored corpus** | 69 untracked determinations at root | UNDECLARED-INVISIBLE | `config.py` `REPOSITORY_ARTIFACT_DEFINITION` — *"a CANDIDATE artifact: reported, never registered, until bound by `git add`"* | **advisory report only** (`ukb.py:794`) |
| 3 | **Generated — ignored** | `/knowledge/` 13 · `/realization/` 44 · `determinism-evidence/` 2 | IGNORED | `.gitignore` + exclusion register + `generated-artifact-registry.json` | UGA-INV-06 (bootstrap path exists), regenerated at `verify.sh:344` |
| 4 | **Generated — tracked** | `00-BOOK/PORTAL` 1,240 · `DATA` 17 · `REGISTRIES` 6 · `CONTROL-TOWER` | **TRACKED** | **three authorities, in conflict** | `register.sh --guard` (exit 3) |
| 5 | **Evidence** | `.ucos/` 2 · `.ucos-verification-evidence/` 46 | IGNORED | `ueg-declaration.json` · `uvi-declaration.json` | UVI gate `.gitignore` check |
| 6 | **Registries** | `00-BOOK/DATA/*.json`, `00-BOOK/REGISTRIES/*.md` | TRACKED (11 modified) | self-declaring `authority` fields | schema validation, `register.sh --guard` |
| 7 | **Certification** | `CERTIFICATION-REGISTRY.md`, `certification.json` | TRACKED | `CEP-005` | — |
| 8 | **Certification evidence** | `.ucos/execution-evidence.json` | **IGNORED** | `ueg-declaration.json` | **none** — `OB-4` |
| 9 | **Implementation of a governed capability** | `engine/execution_environment/` (8 modules) | **UNDECLARED-INVISIBLE** | **nothing** | **none** — `OB-3` |
| 10 | **Governed declaration** | `00-MASTER/UEG-000001/ueg-declaration.json` | **UNDECLARED-INVISIBLE** | **nothing** | **none** — `OB-3` |

### 5.3 The pattern

Classes 3, 5 and 6 are coherent: the visibility state is declared, the declaration is
tracked, and something measures it. Classes 4, 8, 9 and 10 are not. Rows 9 and 10 are the
sharpest: **the code and the declaration that together implement the execution-governance
capability on which certification depends are invisible to git for no declared reason at
all.**

---

## 6. `OB-3` — The Verification Gate Depends On Undeclared-Invisible Authored State

**Severity: HIGH. This is Step 1 `F-5`, measured and localized.**

### 6.1 The measurement

Nine authored files are untracked **and** un-ignored (`git check-ignore` exit 1 for every
one):

```
00-MASTER/UEG-000001/ueg-declaration.json
engine/execution_environment/__init__.py
engine/execution_environment/__main__.py
engine/execution_environment/contract.py
engine/execution_environment/discovery.py
engine/execution_environment/evidence.py
engine/execution_environment/fingerprint.py
engine/execution_environment/gate.py
engine/execution_environment/model.py
```

These are **authored source and an authored declaration** — not caches, not evidence, not
generated output. No visibility class in §5.2 admits them.

### 6.2 The dependency is hard and fail-closed

`verify.sh:126` calls `ucos_env_gate` bare — no `||`, no `if` — under `set -euo pipefail`.
`ucos_env_gate` (`scripts/ucos-env.sh:408-427`) invokes
`python -m engine.execution_environment.gate --gate --quiet --evidence`. `gate.measure()`
calls `load_declaration()` (`model.py:416-429`), which raises
`ExecutionEnvironmentError("declaration not found at …")` on `FileNotFoundError`;
`gate.main()` returns `EXIT_FAULT = 2`.

So: **a checkout carrying the current `verify.sh` and `scripts/ucos-env.sh` but not the
nine untracked files aborts the entire verification at Stage 0.** Missing declaration →
exit 2 with a correct message. Missing package → bare `ModuleNotFoundError`, exit 1, same
abort with a much worse one.

The gate is correctly fail-closed. It fails closed on **authored files that are invisible
to git for no declared reason** — which converts a reproducibility property into a
machine-local accident.

### 6.3 Why no gate catches it

| Gate | Universe | Verdict on the nine files |
|---|---|---|
| `UCOS-UGA-001` UGA-INV-01…10 | `git ls-files -z --cached` | **Outside observation entirely.** No universal identity, no owner, no content hash. UGA cannot report them as unidentified because they are not in its universe |
| `UCOS-RIB-001` GATE-12 | `git status --porcelain`, `dirty_entries_outside_generated` | Counted as generic **dirt** (`??`) — a cleanliness failure, not a coverage failure |
| `UCOS-RFP-001` CLO-01/CLO-05 | `untracked_outside_excluded` | Same: untracked = dirt |
| `generated-artifact-registry.json` `EVERY_CANONICAL_ARTIFACT_REGISTERED` | tracked files inside a declared producer home | `engine/execution_environment` is not among the 31 `producer_homes`; invariant not reached |

**Nothing anywhere asserts "authored source implementing a governed capability must be
tracked."** The obligation is unexpressed, so its violation is unmeasurable. There is a
second-order consequence: `evidence.input_digest` refuses a reuse key when a prefix
matches no registered object, so untracked source can never contribute a content hash to
a verification-reuse digest — the untracked state silently degrades caching too.

### 6.4 The declaration does not declare its own visibility

`ueg-declaration.json` declares `gitignored: true` for `.ucos/environment-fingerprint.json`
and `.ucos/execution-evidence.json`, and notes `.ec1-venv` is *"Disposable and
.gitignored."* Its `lifecycle.IMPLEMENTATION` is marked **COMPLETE**, `discharged_by:
"engine/execution_environment/"`. It declares visibility for its outputs and **nothing
about the visibility of its own implementation or of itself** — while marking that
implementation complete. It is scrupulous about the machine-local files and silent about
the nine files that must not be machine-local.

---

## 7. `OB-4` — Certification Evidence Is Not Reconstructible

**Severity: MEDIUM. Bears on `A6-8` (reproducible from a bare fresh clone) and on `S-2`.**

`.ucos/execution-evidence.json` carries the eight records that let a certified run state
*which interpreter produced it* (finding F-5 in the UEG declaration). It is written only
under `--evidence`, and a write failure is `EXIT_FAULT`, not a warning — so the binding is
enforced at emission. `ueg-declaration.json` places the CERTIFICATION lifecycle position
as `discharged_by: ".ucos/execution-evidence.json emitted by every certified run"`, and
the `.gitignore` comment states it *"is bound into certification from there, not from
git."*

Both statements are accurate. The consequence neither draws:

> **A past certification's execution evidence exists only on the machine that produced it.
> It is not reconstructible from a clean checkout. It can only be re-earned by
> re-execution.**

For a *current* run this is correct design — machine-local truth must not be published as
repository truth. For an *audit* of a past certification it means the evidence is gone.
The mitigation the design already provides is that `cache_state` is recorded in the
payload, so a reader can at least tell whether `EEG-06` was scanned or reused.

This is recorded as a **disclosed property of the boundary, not a defect to repair here.**
The correct resolution is a declaration of what certification evidence must survive a
clone and in what form — a `S-2`-adjacent decision belonging to the baseline authority
owner. Deciding it is outside this step.

---

## 8. Resolution Of The Three PORTAL Authorities

This section discharges the third element of the directive and closes Step 1 `F-2` to the
extent an analysis can close it: **the precedence question is resolvable from declared
constitutional text; the disposition question is not, and is named as an owner act.**

### 8.1 The three claims, measured

| # | Authority | Says of `00-BOOK/PORTAL/` | Measured |
|---|---|---|---|
| **A1** | `00-BOOK/tools/config.py:895` `EXCLUDE_DIR_PREFIXES`; `:449-454` `NON_ARTIFACT_SCOPE` | **GENERATED.** Excluded from registration eligibility | `"00-BOOK/PORTAL/"` present at line 895 |
| **A2** | `git` + `00-BOOK/tools/register.sh --guard` | **TRACKED SOURCE**, and must be regenerated *and committed* | 1,240 tracked · 228 untracked · 1,468 on disk · `check-ignore` exit 1 · no `.gitattributes` |
| **A3** | `00-BOOK/DATA/generated-artifact-registry.json` | **NOT A REGISTERED GENERATED PATH** | 345 entries · **0** under `00-BOOK` · substring `PORTAL` appears **0** times in the whole file |

The disagreement is not latent. It is exactly what `A3`'s own `why_this_exists` predicts:

> *"The same fact — 'this path is generated output' — was expressed in three independent
> places: each programme's own declaration `outputs` section,
> `00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES` for registration eligibility, and
> .gitignore prose for the version-control boundary. They drifted… This register is the
> single upstream fact. Derived views consume it; none produces it."*

**The register built to end this drift does not cover the subject.** The observable
consequence: `platform/repository_intelligence/mutation_class_extension.py:38` classifies
each PORTAL page as *"non-generated — absent from generated-artifact-registry.json
canonical_path"*, and the lineage, object-birth and registry-coverage views have no
producer for a tree that has one (`ukbx.py portal`, lines 1288-1331).

### 8.2 Determination on precedence

Precedence follows from declared constitutional text, not from preference. Each authority
speaks to a **different fact**, and two of the three claims are category errors.

**D-1. `A3` is the authority of record for the predicate `is_generated_output`.** Its
`authority` field is explicit: *"AUTHORED REPOSITORY TRUTH, HELD AS A PROJECTION UNDER
UCKP-LAW-0001. This register declares generated-artifact identity and lifecycle. It is
upstream of every engine it describes and must never be produced by one of them."* It
names `A1` by name as a source it supersedes. No competing text grants that predicate to
any other authority.

**D-2. `A1` is a derived view, not an authority.** `EXCLUDE_DIR_PREFIXES` decides
*registration eligibility* only — its sole load-bearing consumer is
`ukb.py::_iter_files()`, and its effect is that PORTAL pages receive no Universal ID and
never enter `artifacts.json`. It drives no hand-edit check, no regeneration, and no drift
gate. Under `D-1` it must be **projected from `A3`, not asserted alongside it.** Its
present content is an *undeclared* assertion of generatedness — correct on the facts,
without standing.

**D-3. `A2` holds no authority over `is_generated_output` whatsoever.** Tracked-ness is
the answer to a different question — `is_visible`. Treating a `git` state as evidence of
generatedness is precisely the inversion `UCOS-CL-001` was written to forbid (§3.2).

**D-4. `A1` and `A2` are in direct contradiction under `A1`'s own definition, and this is
the substance of `F-2`.** `REPOSITORY_ARTIFACT_DEFINITION` states generated outputs *"are
non-artifacts, **bounded by version control (.gitignore)**."* Read against
`NON_ARTIFACT_SCOPE`, which names `PORTAL/` generated, `A1` asserts **generated ⇒
ignored**. PORTAL is generated **and tracked and un-ignored**, and `register.sh --guard`
(exit 3) *requires* it committed — the exact inverse of the treatment given to every other
generated tree (`/knowledge/`, `/realization/`, `determinism-evidence/`,
`intelligence/UCOS-UPI-001/`, the UAKOS-CLOSURE-002 outputs), each ignored *because* it is
generated. **PORTAL is the systematic exception, and `A1` contradicts itself about it.**

**Therefore the canonical boundary for PORTAL is undetermined not because three
authorities disagree, but because the one authority with standing is silent, and the
definition that would settle it is self-contradictory on this subject.**

### 8.3 The disposition decision — an owner act, with consequences measured

Two terminal states are internally coherent. Both require the `00-BOOK` owner. This
determination selects neither.

**Option A — PORTAL is generated and ignored.** Add `00-BOOK/PORTAL/` to `.gitignore`,
add an exclusion-register entry class `GENERATED_DETERMINISTIC`, add entries to `A3` with
producer `ukbx.py portal`, remove PORTAL from `register.sh --guard`, project `A1` from
`A3`. Consequences: consistent with every other generated tree and with
`REPOSITORY_ARTIFACT_DEFINITION`; **removes 1,240 files from the tracked set and 228
mutations from the BC-6 population**; makes the portal unavailable to any consumer reading
the repository without running the generator.

**Option B — PORTAL is a committed projection.** Keep it tracked, register it in `A3`
with `input_classification: GENERATED_DETERMINISTIC` and
`registration_status: EXCLUDED_FROM_CORPUS_REGISTRATION`, keep `--guard`, amend
`REPOSITORY_ARTIFACT_DEFINITION` so generated-and-tracked is an admitted state rather than
a contradiction. Consequences: preserves availability and `--guard`'s drift detection;
requires amending the definition; **and requires fixing `OB-5` first, or `--guard` can
never pass.**

### 8.4 `OB-5` — `--guard` is currently unsatisfiable

**Severity: MEDIUM. Decisive for Option B.**

`00-BOOK/PORTAL/index.md` embeds a wall-clock timestamp at `ukbx.py:1305`:

```python
f"*Generated {_now()} by ukbx portal. {len(arts)} artifacts. …"
```

with `_now()` returning `datetime.now(timezone.utc)` to second precision (`ukbx.py:55-56`).
The current diff confirms it:

```
-*Generated 2026-08-10T15:29:22+00:00 by ukbx portal. 1233 artifacts. …
+*Generated 2026-08-23T13:32:48+00:00 by ukbx portal. 1461 artifacts. …
```

`index.md` therefore changes bytes on **every** run regardless of content change.
`register.sh --guard` requires `git status --porcelain` over `00-BOOK/PORTAL` to be empty
after regeneration. **"Regenerate, then require a clean tree" is unsatisfiable at second
granularity.** Verified: `--guard` would fail right now — 228 `??` plus 22 ` M`.

Per-artifact pages are deterministic (composed purely from `artifacts.json`,
`relationships.json`, `twin.json` in stable order). The non-determinism is confined to
`index.md`. Option B requires removing the timestamp from generated output or excluding
`index.md` from the guard. Option A makes it moot.

### 8.5 `OB-6` — 228 PORTAL pages are in no state at all

**Severity: MEDIUM.** Of 1,468 pages on disk: 1,240 tracked, **228 generated, untracked,
un-ignored and unregistered.** They are simultaneously outside git's tracked truth,
outside the ignore authority, outside `A3`, and outside `A1`'s registration eligibility.
Under Option A they should be ignored; under Option B they should be committed. Under the
current boundary they are nothing. This is the same undeclared-invisible state as `OB-3`,
reached by a different route, and it is the largest single population in it (228 of 308).

---

## 9. The Canonical Visibility Boundary — Determination

### 9.1 The rule

> **Visibility is a declared property of an artifact class, not a residue of tooling.
> Every path in the repository must resolve to exactly one of two declared states —
> TRACKED or IGNORED — and the state must be declared by the authority that owns the
> artifact's *kind*, recorded in a tracked register, and measurable by a gate that fails
> closed in both directions.**

Three corollaries, each derived from a measurement above:

**C-1. There is no third state.** UNDECLARED-INVISIBLE (untracked and un-ignored) is not a
visibility class; it is an unmade decision. **308 paths are in it**, including the nine
authored files `verify.sh` depends on and 228 generated PORTAL pages.

**C-2. Each fact has exactly one authority, and no authority may hold two.**
`is_generated_output` → `generated-artifact-registry.json`. `means_of_exclusion` →
`exclusion-register.json`. `is_visible` → `.gitignore` + the index, as **consequences** of
the first two, never as inputs to them. `config.py::EXCLUDE_DIR_PREFIXES` must be a
projection, not a peer.

**C-3. The obligation must be measurable in both directions.** Today it is measurable in
one: the UVI gate refuses if the evidence store is *not* ignored; nothing refuses if an
authored module *is* untracked, and `ignored_unclassified` refuses nothing at all
(`OB-1`). A boundary enforced in one direction is not a boundary.

### 9.2 `OB-7` — The bidirectional gate does not exist

**Severity: LOW as a finding, structural as a cause.** No gate anywhere expresses
*"authored source implementing a governed capability must be tracked."* `UCOS-UGA-001`
enumerates from `git ls-files --cached`, so untracked authored code is outside its
universe by construction; RIB GATE-12 and RFP CLO-05 see it only as generic dirt.
`OB-3` and `OB-6` are not independent accidents — they are the two populations this
missing gate would have caught.

### 9.3 Application to the ten classes

| Class | Current | Canonical | Gap |
|---|---|---|---|
| Tracked source | TRACKED | TRACKED | none |
| Authored corpus (69 untracked) | UNDECLARED-INVISIBLE | TRACKED | `A6-1` disposition |
| Generated — ignored | IGNORED | IGNORED | register entries only |
| **Generated — tracked (PORTAL et al.)** | **CONTESTED** | **owner decision §8.3** | **`F-2` · `OB-5` · `OB-6`** |
| Evidence (`.ucos/`, `.ucos-verification-evidence/`) | IGNORED | IGNORED | **`OB-2`** — declaration missing |
| Registries | TRACKED | TRACKED | none |
| Certification | TRACKED | TRACKED | none |
| Certification evidence | IGNORED | IGNORED + survivability rule | **`OB-4`** |
| **Implementation of a governed capability** | **UNDECLARED-INVISIBLE** | **TRACKED** | **`OB-3`** |
| **Governed declaration** | **UNDECLARED-INVISIBLE** | **TRACKED** | **`OB-3`** |

---

## 10. Findings Register

| ID | Finding | Severity | Owner (read, not assigned) | Blocks | Status |
|---|---|---|---|---|---|
| `OB-1` | `ignored_unclassified` is structurally always 0; the `*` register entry + bidirectional `fnmatch` self-classify every ignore rule; the `be46a300` purchase is still available | **CRITICAL** | Repository Intelligence · exclusion-register owner | `A6-2` by measurement · any closure claim citing the metric | **OPEN** |
| `OB-2` | `.ucos/` and `.ucos-verification-evidence/` are ignored with no exclusion-register entry (32 entries vs 55 patterns) | **HIGH** | Exclusion owner (G-9) + `00-BOOK` | `A6-2` on the merits | **OPEN** |
| `OB-3` | 9 authored files (`engine/execution_environment/` + `ueg-declaration.json`) are untracked and un-ignored; `verify.sh:126` fail-closes on them; no gate expresses the obligation | **HIGH** | UEG-000001 / environment owner | `A6-1` · `A6-5` · `A6-8` | **OPEN** (Step 1 `F-5`) |
| `OB-4` | Certification execution evidence is machine-local and not reconstructible from a clean checkout | **MEDIUM** | Baseline authority owner (`S-2`-adjacent) | `A6-8` | **OPEN — disclosed** |
| `OB-5` | `register.sh --guard` is unsatisfiable: `index.md` embeds a wall-clock timestamp, so regeneration always dirties the tree | **MEDIUM** | `00-BOOK` owner | Option B in §8.3 · `A6-6` | **OPEN** |
| `OB-6` | 228 PORTAL pages are generated, untracked, un-ignored and unregistered — in no declared state | **MEDIUM** | `00-BOOK` owner | `A6-1` · `F-2` | **OPEN** (Step 1 `F-2`) |
| `OB-7` | No gate expresses "authored source implementing a governed capability must be tracked"; UGA's universe is tracked-only | **LOW / structural** | UGA owner · Repository Intelligence | root cause of `OB-3`, `OB-6` | **OPEN** |

**7 raised · 0 resolved · 0 repaired.**

### 10.1 Effect on `A6-2`

`A6-2` — *"Exclusion authority settled — G-9 `.gitignore` landed or reverted first"* —
**remains OPEN.** The determination on the merits is that **G-9 should land, and must not
land alone**: it is correct, declared, minimal, and reverting it makes `A6-6`
unreachable — but landing it without the `OB-2` register entry propagates the very drift
`A3` and the exclusion register were both created to end, and `OB-1` means nothing would
report the omission.

Landing is a commit. **This determination performs none.**

### 10.2 Ordering implied for Steps 3–6

Read from the dependency structure above, not assigned:

> `OB-1` (make the metric real) → `OB-2` (pay G-9's declaration, land G-9) →
> `OB-3` (make the gate's own dependencies visible) → §8.3 PORTAL disposition, with
> `OB-5` first if Option B → `A6-1` attribution over a population whose membership is
> finally settled → BC-1 closure → machine re-classification → `A6-3`/`A6-4` gate
> measurement.

This refines Step 1 §8.3's sequence rather than replacing it. Step 1 said *attribute and
settle the tree by owner → close BC-1 → re-classify by machine → measure the gate.* Step 2
adds the precondition Step 1 could not see: **the tree cannot be settled by owner until
membership is settled, and membership is a visibility question, not an attribution one.**

---

## 11. What Step 2 Establishes And What It Does Not

### 11.1 Establishes

- The canonical visibility rule and its three corollaries (§9.1) — two states only, one authority per fact, bidirectional measurement.
- **`OB-1` by first-party measurement**: the classification obligation `UCOS-CL-001` declared is void, and the certification-purchase defect it closed is re-openable by the same mechanism.
- A complete three-state census: **6,188 TRACKED · 233 IGNORED · 308 UNDECLARED-INVISIBLE**, with the third state named as a defect class rather than a residual.
- The G-9 mutation fully characterized: `+9/−0`, one pattern, correct subject, verified technical claims, **one unpaid obligation**.
- **Resolution of `F-2`'s precedence question** (§8.2, `D-1`…`D-4`): `A3` holds the predicate; `A1` is an unstanding derived view; `A2` answers a different question; and `A1` contradicts itself on PORTAL.
- Localization of Step 1 `F-5` to nine named files, with the exact fail-closed path (`verify.sh:126` → `EXIT_FAULT`) and the reason no gate catches it.
- Two coherent PORTAL dispositions with consequences measured, and `OB-5` as the blocker on one of them.

### 11.2 Does not establish

| Not established | Why | Requires |
|---|---|---|
| That `A6-2` is satisfied | `OB-1` + `OB-2` open; G-9 uncommitted | Repair, then a commit |
| The PORTAL disposition | Neither option is derivable from declared text; the governing definition is self-contradictory | **`00-BOOK` owner act** |
| Any ownership assignment | Every owner above is *read* from a declared home | Owner acts |
| Any classification of record | `classify()` returns `ERROR` for every subject (BC-1) | BC-1 closure |
| That `ignored_unclassified = 0` means anything | It is the constant 0 (`OB-1`) | `OB-1` repair |
| Whether the 69 untracked determinations should be committed | An `A6-1` disposition question | Owner acts |
| That `verify.sh --full` exits 0 (`A6-5`) | Not executed. Executing it writes `.ucos/` and evidence — outside this step's read-only mode | Steps 3–4 |

### 11.3 The circularity, restated at Step 2

Step 1 recorded that classification is the capability BC-1 exists to restore, so Step 1
could produce no classification of record. Step 2 finds the same shape one level down:

> **Step 2 was to determine the visibility boundary. The metric that would measure a
> visibility boundary — `ignored_unclassified` — is the constant 0, and cannot fail.**

The boundary is therefore determined here **by reading declared authority text and
measuring the filesystem directly**, exactly as Step 1 classified by hand. It does not
invalidate the determination; §9.1 stands on declared constitutional text and on
first-party measurement. But it means **Step 2 cannot produce a boundary of record**, and
`OB-1` must be repaired before any gate can assert that the boundary holds.

---

## 12. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-OBSERVATION-BOUNDARY-RECONCILIATION-DETERMINATION.md` |
| Required sections present | ✅ `.gitignore` why/owner/authority/verification-impact (§2) · five-class comparison (§5) · three PORTAL authorities resolved (§8) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Implementation performed | ✅ **0** — no source file created or modified |
| Git changes | ✅ **0** — no `add`, `commit`, `restore`, `checkout`, `rm`, `mv` |
| `.gitignore` modified by this step | ✅ **0** — still `+9/−0`, byte-identical |
| Registry changes | ✅ **0** — every register read; none written |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** modified tracked files, identical set |
| Only new artifact added | ✅ `git status --porcelain` 339 → 340 lines; the single delta is this file |
| Ownership assigned | ✅ **0** — every owner is *read* from a declared home |
| Findings resolved | ✅ **0** — all 7 raised and left open |

---

*This determination modified no file, committed nothing, staged nothing, restored nothing, deleted nothing, and changed no ignore rule, register or certification. It assigned no ownership and resolved no finding. Every mutation-class reference is a manual reading of declared predicates and is not a classification of record, because the classifier returns `ERROR` for every subject at this baseline. Seven findings (`OB-1`…`OB-7`) are raised and all remain open. Step 1's `F-2` is resolved as to precedence (§8.2) and remains open as to disposition (§8.3, an owner act). Step 1's `F-5` is localized to nine named files (`OB-3`). `A6-2` remains **OPEN**; BC-6 remains **OPEN** at 0 of 8 acceptance criteria. The single repository mutation is the creation of this file.*

**END DETERMINATION — BC-6 STEP 2 COMPLETE · STEPS 3–6 NOT PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
