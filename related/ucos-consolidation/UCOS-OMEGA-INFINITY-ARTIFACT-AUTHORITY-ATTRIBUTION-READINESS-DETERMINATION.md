# UCOS Ω∞ — ARTIFACT AUTHORITY ATTRIBUTION READINESS DETERMINATION

**BC-6 · Step 4 — Resolving the authority model required before mutation attribution**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-ARTIFACT-AUTHORITY-ATTRIBUTION-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, requirement, ADR, phase, class, owner or certification. Authorizes nothing. Assigns nothing. Ratifies nothing. |
| Mode | ANALYSIS ONLY · **NO IMPLEMENTATION · NO CODE CHANGE · NO CONFIGURATION CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Step | **BC-6 Step 4 only.** Steps 5–6 of the companion plan are not performed |
| Predecessor | Step 3 `UCOS-OMEGA-INFINITY-ARTIFACT-AUTHORITY-VISIBILITY-RESOLUTION-DETERMINATION.md` — `AV-1`…`AV-9`, all **OPEN** |
| Population re-measured | `git ls-files`: **6,188** tracked · **310** untracked-and-un-ignored · **7,190** ignored — **13,688** total (Step 3 measured 6,730; the delta is analyzed in §3.3, `AAT-4`) |
| Findings raised | **5** (`AAT-1`…`AAT-5`) · 1 CRITICAL · 3 HIGH · 1 MEDIUM |
| Findings resolved | **ZERO.** Determination is not repair |
| Classes, owners, registries or certifications created | **ZERO** |

---

## 1. Objective, Method and Standing Limitation

### 1.1 Objective

Step 3 established `AV-6`: **visibility determines classification**, because `R-01
REPOSITORY_STATE` sits at precedence 1 and absorbs every non-tracked path regardless of
what it actually is. Step 3 §8.2 recorded that mutation attribution (`A6-1`) must not be
attempted while that inversion stands, because it would record contamination as the
mutation class of the programme's own authored source.

Step 4 does not attempt attribution. It resolves the **authority model attribution would
need**: for each of the six canonical artifact classes established in Step 3 §2.3, which
register is authoritative, who owns it, where visibility is declared, and what
certification law applies — so that when `AV-6` is repaired, attribution has an authority
to attribute *to*, rather than a second undeclared model built ad hoc at attribution time.

### 1.2 Method

Every measurement below is a **read** of a committed registry or a `git ls-files`
enumeration. Nothing was written, committed, staged, restored, deleted, ignored,
registered, classified of record, owned or certified. Four registers were read directly
with `json.load` and their `owner`, `authority`, `entries`, `surfaces` and
`generated_inputs` fields enumerated: `mutation-governance-boundary.json`,
`exclusion-register.json`, `generated-artifact-registry.json`, `evidence-universe.json`,
plus `ucos-ownership-declarations.json` and `certification.json`. Population counts use
`git ls-files`, `git ls-files --others --exclude-standard` and
`git ls-files --others --ignored --exclude-standard`, run fresh at this baseline.

### 1.3 Standing limitation, carried from Step 3

The classifier (`platform/repository_intelligence/mutation_classification.py`) still
refuses to run: `R-09 GOVERNED_ANALYSIS` is declared in
`mutation-governance-boundary.json` but has no predicate in `RULE_PREDICATES`, so
`classify()` returns `ERROR` for every subject at this baseline, unchanged since Step 3.
Every class assignment below is a **manual reading of declared authority text**, exactly
as Steps 1–3 proceeded, and **none is a classification of record**.

---

## 2. The Canonical Artifact State Model

### 2.1 Six axes, read from declared authority text

The directive names six axes. Step 3 §7.1 already measured seven decision positions
(`ORIGIN`, `CLASSIFICATION`, `OWNER`, `AUTHORITY`, `VISIBILITY`, `LIFECYCLE`,
`CERTIFICATION`); the six requested here map onto that framework with `AUTHORITY` folded
into `OWNERSHIP` — the instrument a decision is taken *under* is, by measurement, always a
property of who holds the decision, never an independent axis with its own register. No
register in the repository declares an `AUTHORITY` axis separate from `OWNER`; Step 3's
own §7.1 diagram lists it only as "the register or constitution granting the mutation
right," which is a description of the owner's standing, not a sixth thing to measure.

| Axis | Question | Authority of record | Current standing |
|---|---|---|---|
| **ORIGIN** | Who or what produced these bytes? | **None.** Not a first-class field in any register (Step 3 §7.3) | Distinguishable only by registry membership — an unregistered PORTAL page and an authored markdown file are indistinguishable to `R-08`/`R-09` |
| **CLASSIFICATION** | Which of the six canonical classes? | `mutation-governance-boundary.json` §2.3 (nine V1 classes, no crosswalk of record to the six canonical classes) | `classify()` → `ERROR` for all subjects (§1.3) |
| **OWNERSHIP** | Which authority answers for it, under what instrument? | `platform/universal_ownership/catalog/ucos-ownership-declarations.json` (precedence 900, CONSTITUTIVE) | `"assignments": {}` — still literally empty at this baseline (re-verified §2.2) |
| **VISIBILITY** | Does version control carry these bytes? | The index itself; no register declares *expected* tracked-ness for any path | 6,188 TRACKED · 310 untracked-and-un-ignored · 7,190 IGNORED (§3.3) |
| **LIFECYCLE** | What states may it occupy, what transitions are legal? | Per-class: `generated-artifact-registry.json` (`lifecycle` field) for GENERATED; `CEP-005` Art VI for CERTIFICATION; none declared for AUTHORED, EVIDENCE, CACHE, TEMPORARY | `lifecycle` = `REGENERATED` for 345/345 GENERATED entries — one value, not yet a lifecycle (Step 3 `AV-3`) |
| **CERTIFICATION** | What has been proven, and does the proof still hold? | `CEP-005` Article VI (declared, unimplemented — Step 3 `AV-5`) | Live verdict `NOT-CERTIFIED`; `00-BOOK/DATA/certification.json` scope is 1,233 artifacts against a corpus of 1,461+ (228 stale at Step 3, re-verified unchanged at §2.2) |

### 2.2 Re-verification at this baseline

Three figures Step 3 measured were re-read directly rather than carried forward
unverified, because they are load-bearing for §4 below:

| Figure | Step 3 value | This baseline | Changed? |
|---|---|---|---|
| `ucos-ownership-declarations.json` `assignments` | `{}` | `{}` | No |
| `generated-artifact-registry.json` entries / distinct owners | 345 / 32 | 345 / 32 | No |
| `00-BOOK/DATA/certification.json` verdict / scope | `CERTIFIED` (stale), 1,233 scope | `CERTIFIED` (still stale), 1,233 scope | No |

The authority state Step 3 measured is stable. What is **not** stable is the visibility
population — see `AAT-4` (§3.3).

---

## 3. Required Separation: Repository Visibility ≠ Artifact Classification

### 3.1 The rule, restated as a rule rather than a finding

Step 3 measured `AV-6` as an empirical fact: 542 of 542 non-tracked paths, at that
baseline, resolved to `R-01 REPOSITORY_STATE`. Step 4 restates it as the constraint any
authority model must satisfy before attribution is safe:

> **A path's presence in, or absence from, the git index SHALL NOT be an input to which
> canonical class (AUTHORED · GENERATED · DERIVED · EVIDENCE · CACHE · TEMPORARY) an
> artifact belongs to. Classification is a function of origin and reproducibility only
> (Step 3 §2.3). Visibility is a separate, downstream decision: given a class, does
> version control need to carry these bytes?**

This restates Step 3 §7.2 Rule 1 for the ORIGIN→CLASSIFICATION→VISIBILITY ordering
specifically, because it is the one arrow `AV-6` measured as reversed.

### 3.2 Why attribution depends on the separation holding

Mutation attribution (`A6-1`) asks, for a changed or added path, *what kind of change is
this and who answers for it*. If classification is derived from visibility, an
untracked-but-authored file (`engine/execution_environment/gate.py`, per Step 3 §4.1) and
genuine working-tree debris are attributed identically — both `R-01 REPOSITORY_STATE`,
both ownerless, both invisible to every downstream gate. Attribution under that model
would not misattribute a mutation; it would report a null result for every non-tracked
mutation regardless of substance, which is a wrong authority silently returned as no
authority.

### 3.3 `AAT-4` — The population attribution would run over has grown 2.0x since Step 3

**Severity: MEDIUM, and it bounds every count in this determination and Step 3's.**

Step 3's population was 6,730 paths (6,188 tracked · 233 ignored · 309
untracked-and-un-ignored), measured at the same HEAD (`bae59755`) and the same branch.
Re-measured now, at the identical commit:

```
tracked:                    6,188   (unchanged)
untracked-and-un-ignored:     310   (+1 — this determination's own predecessor file,
                                      the mechanism Step 2 §9.1 already named)
ignored:                     7,190   (+6,957)
TOTAL:                      13,688   (Step 3: 6,730)
```

The ignored population's growth is not a repository change — HEAD is identical — it is a
**working-tree** change: a re-verified breakdown attributes 691 paths to
`platform/tests/__pycache__`, 217 to `engine/tests/unit/__pycache__`, 225 to
`.ruff_cache/{0.8.4,0.15.10}`, and **~5,800** to `.ec1-venv/` (a locally materialized
Python virtual environment, entirely CACHE/TOOL_OPERATIONAL by the exclusion register's
own classes, §4 below). None of this is committed; all of it is correctly `.gitignore`d;
none of it should ever reach attribution. But it demonstrates concretely what `AV-8`
(Step 3 §6.6) already warned about the CERTIFICATION axis, generalized to attribution: **a
population count taken from the working tree is not a repository property.** It is a
snapshot of one machine's local state at one instant, and it moved 2x between two
determinations at the same commit with zero commits in between. Any attribution readiness
gate that counts "artifacts requiring attribution" from `git ls-files --others` without
first partitioning by the exclusion register will count ephemeral tool state as pending
mutations.

---

## 4. Per-Class Authority Table

For each of the six canonical classes established in Step 3 §2.3, the authoritative
source, owner, registry, visibility rule and certification requirement, read directly from
declared text — never inferred, never filled in where the source is silent.

| Class | Authoritative source | Owner | Registry | Visibility rule (declared) | Certification requirement |
|---|---|---|---|---|---|
| **AUTHORED** | *No single register.* Split across three V1 classes that are each "owner-parameterised, read from the artifact itself": `GOVERNED_DECLARATION`, `AUTHORED_DOCUMENT`, `GOVERNED_ANALYSIS` | Whoever the artifact self-declares (Authority/Deciders field) — **not** independently verified against any registry entry | None uniform. `id-ledger.json` + `artifacts.json` for the 1,233 corpus-registered subset; **no registry at all** for the remainder | Should be TRACKED — "loss is permanent" (Step 3 §2.3) — but not enforced: `R-01` absorbs untracked authored paths as contamination (`AV-6`) | `grants_only_mutation_ownership` explicitly on all three classes: **"no certification, ratification, or freeze authority"** (`CEP-009 I.1`). Certification remains with the CEP-005 chain, which is unimplemented (`AV-5`) |
| **GENERATED** | `00-BOOK/DATA/generated-artifact-registry.json` — self-declared *"upstream of every engine it describes… must never be produced by one of them"* (`D-1`, Step 3 §3.2) | `owner` / `validation_owner` fields, **345/345 populated**, **32 distinct programmes** (re-verified §2.2) | `generated-artifact-registry.json` itself | Declared *"bounded by version control (.gitignore)"* (`config.py`), but PORTAL — 1,240 tracked GENERATED pages — contradicts this by being tracked (`AV-1`, `AV-6` §6.4) | `certification_role` field, 5 values (`PROGRAMME_DELIVERABLE` 273 · `REPLAY_PROVEN` 30 · `BLOCKING_GATE_SOURCE` 16 · `CONVERGENCE_DETERMINATION` 15 · `PHASE9_VARIANCE_DIMENSION` 11) plus Phase 8 (fixed-point) and Phase 9 (pristine-clone) checks |
| **DERIVED** | `generated-artifact-registry.json` `generated_inputs` (10 declared entries) | Same `owner` as the GENERATED artifact it feeds — no independent DERIVED owner field exists | `generated-artifact-registry.json` `generated_inputs` section; `bootstrap_gaps` (currently `[]`) records unmet inputs | Each `generated_inputs` entry declares `"tracked": false` explicitly — e.g. `knowledge/`, producer `engine/knowledge/seed.py`, bootstrapped via `verify.sh` stage 1b. Untracked by design, reproducible only if the `bootstrap_command` runs | Inherits the certification posture of whatever it feeds; no independent certification requirement is declared for the DERIVED class itself |
| **EVIDENCE** | `00-BOOK/DATA/evidence-universe.json` — *"legislates what evidence IS and what it may influence"* | Per-surface `owner` field, in prose (e.g. `EV-PROGRAMME-EXECUTION-LOG`: *"the 00-MASTER programme that owns the containing directory"*) — a description, not an identifier that joins to any owner registry | `evidence-universe.json` `surfaces` (10 declared) | Per-surface: most surfaces (e.g. execution logs, `population: 76`) are explicitly excluded from version control by declaration; the one class that *may* be tracked is `VALIDATION`, *"and only when derived from repository truth and tracked"* | `may_affect_certification` boolean, per surface — **3 of 10 are `true` while untracked** (Step 3 `AV-8`); classes `DEBUG` and `IMPROVEMENT` are certification-forbidden outright (`R-EV-4`) |
| **CACHE** | `00-BOOK/DATA/exclusion-register.json`, class `CACHE` (and the adjacent `TOOL_OPERATIONAL` class for non-cache tool state) | Per-entry `owner`, and it is **never a UCOS authority** — measured values are `CPython`, `pytest`, `ruff`, `mypy` (§4.1 below) | `exclusion-register.json` `entries` (32 total across 7 classes) | `IGNORED`, by definition — *"Reconstructible from source at any time; carries no information"* | None. Disclaimed outright by `evidence-universe.json`: *"caches carry no information not present in their source; they are not evidence of anything"* (Step 3 `AV-1`) |
| **TEMPORARY** | `exclusion-register.json`, class `TEMPORARY` | The creating process, per entry — e.g. `00-BOOK/tools/.register.lock` owned by `00-BOOK/tools/register.sh` | `exclusion-register.json` `entries` | `IGNORED`, bounded lifetime, *"owned by the process that creates it"* | None — no consumer outside the operation that created it, so no certification claim can outlive the operation |

### 4.1 `AAT-3` — Three of six classes have no UCOS-authority owner at all

**Severity: HIGH.**

CACHE and TOOL_OPERATIONAL entries in `exclusion-register.json` declare `owner` as the
*producing tool*, measured directly:

```
__pycache__/        owner: CPython           producer: python interpreter
*.pyc                owner: CPython           producer: python interpreter
.pytest_cache/       owner: pytest            producer: pytest
.ruff_cache/         owner: ruff              producer: ruff
.mypy_cache/         owner: mypy              producer: mypy
.ec1-venv/           owner: verify.sh / ucos-env.sh   producer: ucos_ensure_venv
build/, dist/        owner: setuptools        producer: python -m build
**/.claude/settings.local.json   owner: developer workstation   producer: Claude Code
```

This is not a defect in the exclusion register — attributing a bytecode cache to "CPython"
is the correct answer to "what produced this." It **is** a defect in any attribution model
that expects every artifact to resolve to a UCOS ownership authority: `AAT-3` establishes
that CACHE and TEMPORARY, by construction, resolve to an owner **outside** the
`ucos-ownership-declarations.json` universe of discourse entirely. The 391-unresolved /
542-total figures Step 3 measured for the OWNERSHIP axis (`AV-4`) already exclude these —
but no register states that exclusion as a rule; it is an artifact of the ownership
catalogue's silence on non-repository owners, discoverable only by reading every entry.
An attribution readiness gate that iterates "every mutated path needs an owner" without
first partitioning by class will search for a UCOS owner of `__pycache__/module.pyc` and
find none, correctly, but for the wrong reason if the partition isn't made explicit first.

### 4.2 `AAT-1` — No class has one authority for all five attribution columns

**Severity: CRITICAL.**

Reading the table in §4 across, not down: **not one of the six classes has a single
register that is simultaneously its authoritative source, its owner registry, its
visibility declaration and its certification law.** GENERATED comes closest — one register
for source, owner and (partially) certification — but its visibility rule lives in
`config.py`, a different file, and contradicts the register's own tracked GENERATED
artifacts (PORTAL). AUTHORED has no registry at all for two-thirds of its declared
membership. EVIDENCE's owner field is prose, not a key. CACHE and TEMPORARY resolve to
non-UCOS owners (`AAT-3`).

This is the same disconnection Step 3 measured for the OWNERSHIP axis alone (`AV-4`,
*"declared in one place and enforced in another, and the two do not share a key"*), shown
here to hold **across every axis for every class**, not only OWNERSHIP. Attribution
(`A6-1`) needs to answer "source, owner, registry, visibility, certification" for a
mutated path in one lookup; today that is up to five lookups across five files with no
shared key, and for AUTHORED and DERIVED artifacts at least one of the five lookups has no
register to consult at all.

### 4.3 `AAT-2` — Self-declared authority is unverified against any registry

**Severity: HIGH.**

`GOVERNED_DECLARATION`, `AUTHORED_DOCUMENT` and `GOVERNED_ANALYSIS` are each, by their own
`$why_governed_by_is_owner_parameterised` notes, governed by *"the authority the artifact
declares of itself… read from an Authority or Deciders self-declaration."* This is a
majority of the AUTHORED class's population (2,822 tracked paths reach `R-09`'s intended
territory per Step 3 `AV-7`, plus the untracked residue `AV-6` absorbs). No register
cross-checks the self-declared value against `ucos-ownership-declarations.json`
(`assignments: {}`, §2.2) or against any other independent source. An artifact can declare
any Authority string in its own header, and nothing in the classification or ownership
chain disputes it. This is not evidence of forgery — no forged authority was found or
sought — it is a measured absence of a check: **self-attestation with no adjudicator is
the entire ownership mechanism for the largest artifact class in the repository.**

---

## 5. Migration Path: `R-01 REPOSITORY_STATE` Dominance → Artifact Authority Resolution Model

Read from the dependency structure the findings above impose — an ordering, not an
assignment, and not a schedule:

```
Stage 0   PRECONDITION (this determination)
          Authority-per-class table exists as declared text (§4). No implementation.

Stage 1   REPAIR AV-6's MECHANISM  (Step 3 §4.2a)
          `_r01_repository_state` must consult the exclusion register before claiming
          a path — today it checks two hardcoded instrument paths and nothing else.
          Until this lands, every subsequent stage inherits 542+ wrong authorities.
          Requires: implementation authority (§6).

Stage 2   MAKE EEXCLUSION REACHABLE  (`OB-1`, `OB-2`)
          `ignored_unclassified` must be able to rise above the constant 0; the 23
          `.gitignore` patterns with no register entry (`OB-2`) must be closed.
          Requires: implementation authority + owner authority (exclusion-register owner).

Stage 3   CLOSE THE GENERATED-ARTIFACT COVERAGE GAP  (`AV-3`)
          Register the 1,232 PORTAL pages and 23 DATA/REGISTRIES artifacts under
          `00-BOOK` into `generated-artifact-registry.json`. Step 3 measured this as
          recovering ~1,232 of the 2,822-path `UNRESOLVED` residue with no rule change.
          Requires: owner authority (generated-artifact-registry owner, `00-BOOK`).

Stage 4   IMPLEMENT R-09  (BC-1)
          The missing predicate. Unblocks `classify()` for the first time at this
          baseline — currently `ERROR` for all subjects.
          Requires: implementation authority.

Stage 5   RATIFY OWNERSHIP  (`AV-4`, `CEP-OWN-004`)
          A governing authority ratifies the `ratified: false` draft measured in Step 3
          §3.5 — coverage 27.86% → 66.97% with zero code change, because the blocker is
          ratification, not data.
          Requires: owner authority (whichever authority `CEP-OWN-004` names) +
          constitutional authority (the ratifying act is itself a constitutional act
          per `CEP-009`).

Stage 6   RESOLVE CERTIFICATION  (`AV-5`, `CEP-005` Art VI)
          Either implement the declared 8-state machine, or formally supersede it with
          one of the three code enums actually in use. Leaving four unreconciled
          vocabularies in place is itself a standing defect regardless of which choice
          is made.
          Requires: certification authority (CEP-005's own governing chain) +
          constitutional authority if superseding rather than implementing.

Stage 7   THIS DETERMINATION'S OWN TABLE (§4) BECOMES BINDING
          Nothing above adopts the six-class model, the crosswalk, or the per-class
          table in §4 as authoritative — this determination has no authority (header).
          Adoption is a distinct owner act, not implied by any stage above completing.

Stage 8   A6-1 ATTRIBUTION
          Only after Stage 1 (mechanism repaired) and Stage 7 (model adopted) does
          attributing a mutation to a class, owner and authority mean anything other
          than reporting which of 6,730+ paths git happens to track.
```

Stage 1 is the only stage that must precede every other stage — this is `AV-6`'s ordering
conclusion (Step 3 §8.2), unchanged and re-affirmed here. Stages 2–6 are not
sequence-dependent on each other and could proceed in parallel once Stage 1 lands; Stage 7
depends on Stages 2–4 producing a stable classification to adopt; Stage 8 depends on
Stage 7.

---

## 6. Authority Requirement Matrix

Which of the four authority types (implementation, owner, constitutional, certification)
each migration decision requires — read from the same declared text as §4 and §5, not
assigned here:

| Decision | Implementation authority | Owner authority | Constitutional authority | Certification authority |
|---|---|---|---|---|
| Fix `_r01_repository_state` to consult the exclusion register (Stage 1) | **Yes** — code change to `platform/repository_intelligence/mutation_classification.py` | — | — | — |
| Close the 23 uncovered `.gitignore` patterns (Stage 2, `OB-2`) | Yes, to add entries | **Yes** — exclusion-register owner decides classification of each | — | — |
| Register 1,232 PORTAL pages as GENERATED (Stage 3, `AV-3`) | Yes, to add registry entries | **Yes** — `00-BOOK` owner and generated-artifact-registry owner | — | — |
| Implement `R-09 GOVERNED_ANALYSIS` predicate (Stage 4, BC-1) | **Yes** | — | — | — |
| Adopt the six-class canonical model as authoritative (Stage 7) | — | **Yes** — mutation governance owner, since it supersedes V1's nine-class model | Possibly, if adoption amends a declared mutation class (`UCKP-ART-18` — two classes for one artifact is forbidden, so any reclassification is a constitutional-adjacent act) | — |
| Ratify the ownership catalogue (Stage 5, `CEP-OWN-004`) | — | **Yes** — the named ratifying authority | **Yes** — `CEP-009` frames amendment/ratification as a constitutional act | — |
| Cross-check self-declared AUTHORED authority against a registry (`AAT-2`) | Yes, to build the check | **Yes** — decides what the check verifies against | — | Possibly, if the check becomes a certification precondition |
| Implement `CEP-005` Article VI's 8-state machine, or formally supersede it (Stage 6, `AV-5`) | Yes, if implementing | — | **Yes**, if superseding (changes declared law) | **Yes** — the certification chain itself must accept whichever path is taken |
| Reconcile the four certification vocabularies into one (`AV-5`) | Yes | — | — | **Yes** |
| Resolve `AV-8` — visibility purchasing certification | Yes, to add a visibility constraint to `R-EV-4` | — | — | **Yes** — changes what `may_affect_certification` means |
| Attribute a mutation to a class/owner (Stage 8, `A6-1`) | — | **Yes**, per-artifact | — | Only if the mutation touches a certified artifact |

No decision in this matrix requires all four authority types simultaneously. The two that
require three are the certification-vocabulary decisions (Stage 6, `AV-8`), because
resolving them changes declared law, requires the certification chain's acceptance, and —
if superseding rather than implementing — is itself a constitutional amendment.

---

## 7. Findings Register

| ID | Finding | Severity | Owner (read, not assigned) | Status |
|---|---|---|---|---|
| `AAT-1` | No canonical class has one register serving as source, owner, registry, visibility rule and certification law simultaneously; attribution needs up to five uncorrelated lookups per path | **CRITICAL** | Mutation governance owner · `00-BOOK` | **OPEN** |
| `AAT-2` | AUTHORED class ownership is self-declared prose with no adjudicating registry; the largest artifact class has no independent ownership check | **HIGH** | Mutation governance owner · Universal Ownership | **OPEN** |
| `AAT-3` | CACHE and TEMPORARY classes resolve to non-UCOS owners (CPython, pytest, ruff, mypy, setuptools) by design; attribution must partition these out before searching for a UCOS authority, and no register states that partition as a rule | **HIGH** | exclusion-register owner | **OPEN** |
| `AAT-4` | The visibility population measured at the identical HEAD grew from 6,730 (Step 3) to 13,688 paths, driven entirely by local `.ec1-venv/` and cache growth in the working tree, not by any commit | **MEDIUM** | Repository Intelligence | **OPEN** |
| `AAT-5` | EVIDENCE surface `owner` fields are free-text descriptions ("the 00-MASTER programme that owns the containing directory"), not identifiers joinable to the ownership axis — the same defect `AV-4` measured for GENERATED, now confirmed for EVIDENCE | **HIGH** | evidence-universe owner · Universal Ownership | **OPEN** |

**5 raised · 0 resolved · 0 repaired.**

### 7.1 Relationship to Step 3's findings

| Step 3 finding | Step 4 disposition |
|---|---|
| `AV-4` (ownership disconnected by key) | **Extended** to EVIDENCE (`AAT-5`) and generalized across all five attribution columns, not ownership alone (`AAT-1`) |
| `AV-6` (the axis collapse) | **Restated as the binding rule** attribution must satisfy (§3.1), not re-measured as a new finding; its mechanism (§3.2) is unchanged |
| `AV-9` (no bidirectional gates) | **Consistent with `AAT-2`**: self-declared authority is exactly a position with no gate against wrongly-present values |
| — | `AAT-3` and `AAT-4` are new — neither was visible from Step 3's OWNERSHIP-axis framing; `AAT-3` required reading every exclusion-register entry's `owner` field, `AAT-4` required re-measuring the same population at the same commit |

---

## 8. What Step 4 Establishes And What It Does Not

### 8.1 Establishes

- The six requested axes **map onto Step 3's seven-position framework** with `AUTHORITY`
  folded into `OWNERSHIP` as a property, not an independent axis with its own register
  (§2.1) — re-verified against three of Step 3's figures, all unchanged (§2.2).
- The separation `VISIBILITY ≠ CLASSIFICATION` **restated as a binding rule** for any
  future authority model, with the reason attribution specifically depends on it holding
  (§3.1–3.2).
- **A complete per-class authority table** (§4) for all six canonical classes across five
  attribution-relevant columns, sourced from `mutation-governance-boundary.json`,
  `exclusion-register.json`, `generated-artifact-registry.json` and
  `evidence-universe.json` directly — no column left unfilled by inference; where a source
  is silent, the table says so (AUTHORED's registry, DERIVED's owner).
- **A nine-stage migration path** from `R-01` dominance to a model where attribution means
  something (§5), ordered by the dependency structure Step 3 §8.2 already established and
  extended one stage further to attribution itself.
- **A complete authority-requirement matrix** (§6) naming which of implementation, owner,
  constitutional and certification authority each migration decision needs, with no
  decision assigned an authority type its source text does not support.
- Five new findings (`AAT-1`…`AAT-5`), of which `AAT-1` is the determination Step 4 exists
  to produce: no class has one authority across all five attribution columns.
- **A measured 2.0x population drift** (`AAT-4`) at an unchanged HEAD, which bounds the
  reliability of any snapshot-based readiness count, this determination's own included.

### 8.2 Does not establish

| Not established | Why | Requires |
|---|---|---|
| Any classification of record | `classify()` still returns `ERROR` for all subjects | BC-1 / `R-09` (Stage 4) |
| That the per-class authority table (§4) is adopted | This determination has no authority; it reads and tabulates declared text | Mutation governance owner (Stage 7) |
| Any ownership assignment | `assignments: {}`, re-verified (§2.2) | `CEP-OWN-004` ratification (Stage 5) |
| Any mutation attribution | That is `A6-1`, explicitly out of scope per Step 3 §8.2 and this determination's own ordering (Stage 8) | Stages 1–7 |
| That `AV-6`'s mechanism is repaired | Not attempted — read-only determination | Stage 1, an implementation act |
| A resolved certification vocabulary | Four vocabularies still stand, unreconciled | Stage 6 |
| That the 13,688-path population is accurate for any purpose beyond this reading | It is a working-tree snapshot proven volatile at an unchanged HEAD (`AAT-4`) | Partition by exclusion class before any count is used downstream |

### 8.3 The recursion, at Step 4

Step 3 ended by naming its own circularity: the instrument that would verify the
visibility/classification separation is the instrument that violates it. Step 4's version
is narrower and answerable: **this determination itself is an instance of the AUTHORED
class** (§4, row 1) — self-declared authority (`NONE — DERIVED TRUTH`, header), untracked
at the moment of writing, registered nowhere. By its own §4 table, an untracked AUTHORED
artifact is exactly the population `R-01` absorbs as contamination under the present,
unrepaired mechanism. This determination will itself become `AAT-6`-shaped evidence for
Step 3's `AV-6` the moment `git status` is next measured — which is a demonstration of the
finding, not an exemption from it.

---

## 9. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-ARTIFACT-AUTHORITY-ATTRIBUTION-READINESS-DETERMINATION.md` |
| Required sections present | ✅ canonical artifact state model (§2) · required separation (§3) · per-class authority table (§4) · migration path (§5) · authority requirement matrix (§6) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis only — implementation performed | ✅ **0** |
| Code changes | ✅ **0** — every module read, none written |
| Configuration changes | ✅ **0** |
| Registry changes | ✅ **0** — 6 registers read, none written |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ identical set to session start |
| Only new artifact added | ✅ the single delta is this file |
| Classes / owners / registries / certifications created | ✅ **0** |
| Findings resolved | ✅ **0** — all 5 raised and left open |

---

*This determination modified no file, changed no code or configuration, wrote to no
registry, altered no certification, committed nothing, and created no class, owner,
authority or lifecycle. Every table entry is a direct reading of declared text in
`mutation-governance-boundary.json`, `exclusion-register.json`,
`generated-artifact-registry.json`, `evidence-universe.json`,
`ucos-ownership-declarations.json` or `certification.json`, or a fresh `git ls-files`
measurement at the stated HEAD — none is a classification, ownership or certification of
record, because `classify()` returns `ERROR` for all subjects at this baseline. Five
findings (`AAT-1`…`AAT-5`) are raised and all remain open. Step 3's `AV-1`…`AV-9` remain
open and unaffected. `A6-1` attribution is confirmed, not attempted, to remain blocked on
`AV-6`'s repair (Stage 1) and this determination's own model being adopted (Stage 7). The
single repository mutation is the creation of this file.*

**END DETERMINATION — BC-6 STEP 4 COMPLETE · STEPS 5–6 NOT PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
