# UCOS Ω∞ — ARTIFACT ATTRIBUTION RECONCILIATION DETERMINATION

**BC-6 · Step 5 — The deterministic reconciliation model required to attribute every repository artifact without visibility collapse**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-ARTIFACT-ATTRIBUTION-RECONCILIATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, requirement, ADR, phase, class, owner or certification. Authorizes nothing. Assigns nothing. Ratifies nothing. |
| Mode | ANALYSIS ONLY · **NO IMPLEMENTATION · NO CODE CHANGE · NO CONFIGURATION CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Step | **BC-6 Step 5 only.** Step 6 of the companion plan is not performed |
| Predecessors | Step 1 (mutation discovery, `F-2`,`F-5`) · Step 2 (`OB-1`…`OB-7`) · Step 3 `…ARTIFACT-AUTHORITY-VISIBILITY-RESOLUTION-DETERMINATION.md` (`AV-1`…`AV-9`) · Step 4 `…ARTIFACT-AUTHORITY-ATTRIBUTION-READINESS-DETERMINATION.md` (`AAT-1`…`AAT-5`) — all **OPEN** |
| Population re-measured | `git ls-files`: **6,188** tracked · **311** untracked-and-un-ignored · **7,190** ignored — **13,689** total (Step 4 measured 13,688 one file-write ago; §5.1 treats the delta as expected, not anomalous) |
| Findings raised | **5** (`AAR-1`…`AAR-5`) · 1 CRITICAL · 2 HIGH · 1 MEDIUM · 1 LOW/structural |
| Findings resolved | **ZERO.** Determination is not repair |
| Classes, owners, registries or certifications created | **ZERO** |

---

## 1. Objective, Method and Standing Limitation

### 1.1 Objective

Steps 1–4 built up, in order: the mutation population (Step 1), the visibility boundary and
its seven defects (Step 2), the canonical six-class model and the proof that visibility
determines classification (Step 3, `AV-6`), and the per-class authority table plus a
9-stage migration path (Step 4). None of the four attempted attribution — Step 3 §8.2 and
Step 4 §8.2 both name `A6-1` attribution as explicitly deferred pending `AV-6`'s repair.

Step 5 asks the next question directly: **what deterministic reconciliation model would
attribution actually need to run against**, given everything the first four steps
measured? This is answered in three parts — the current pipeline's defects restated as
pipeline transitions rather than isolated findings (§2), the target pipeline defined node
by node against declared authority (§3), and a fresh population partition that classifies
by class rather than by visibility, as the directive requires (§5) — which surfaces three
new triple-classification contradictions no prior step measured (`AAR-1`).

### 1.2 Method

Every measurement is a **read** or a **pure function evaluated in memory** over files
already on disk at this baseline. Nothing was written, committed, staged, restored,
deleted, ignored, registered, classified of record, owned or certified. New instruments
beyond Steps 3–4:

| Instrument | Purpose |
|---|---|
| `git ls-files` / `--others --exclude-standard` / `--others --ignored --exclude-standard`, captured to files and diffed by prefix | Partition the three visibility populations by directory and extension, independent of the classifier |
| Directory/extension-prefix reclassification against `exclusion-register.json`'s 32 entries, evaluated by hand (`fnmatch` over the bare `*` rule reproduces Step 3 `AV-1`'s own finding that it self-matches every path, confirming rather than contradicting §6.2 of Step 3) | Assign each of the 7,190 ignored paths to a V2 class by directory membership rather than by the unscoped literal rule |
| Cross-read of `evidence-universe.json` `surfaces[].path_pattern` against `exclusion-register.json` `entries[].rule` for the same directory | Detect paths claimed by both registers under different classes (`AAR-1`) |
| `grep` for `.ucos-verification-evidence`, `.ucos/` across all three registers | Detect ignored, populated directories claimed by **none** of the three registers (`AAR-2`) |

### 1.3 Standing limitation, unchanged since Step 3

`classify()` still returns `ERROR` for every subject at this baseline — `R-09` remains
undeclared as a predicate. Every classification below is a manual reading of declared
text or a directory-prefix reconstruction, exactly as Steps 1–4 proceeded, and **none is a
classification of record**.

---

## 2. Current Attribution Pipeline — Six Transitions, Read For Defects

### 2.1 The pipeline as it exists today

```
Artifact Path → Classification → Ownership → Registry → Visibility → Certification
```

Each arrow below is graded on the same four questions the directive asks: is the
transition ambiguous, is a join missing, do authorities conflict, is a dependency
unresolved.

| Transition | Ambiguous? | Missing join? | Conflicting authorities? | Unresolved dependency? |
|---|---|---|---|---|
| **Path → Classification** | **Yes** — `R-01` claims any non-tracked path before any substantive rule runs (`AV-6`); classification is a function of visibility, reversed from the declared order | — | `mutation-governance-boundary.json` (V1, 9 classes) vs. `exclusion-register.json` (V2, 7) vs. `generated-artifact-registry.json` (V3, 9) vs. `evidence-universe.json` (V4, 5) — 4 vocabularies, 3 newly measured direct collisions on the **same path** (`AAR-1`) | `classify()` → `ERROR` for all subjects — `R-09` unimplemented (BC-1) |
| **Classification → Ownership** | — | **Yes** — `AV-4`: 345 GENERATED owners and 1,461 constant AUTHORED owners share no key with `ucos-ownership-declarations.json` | — | `assignments: {}`, re-verified unchanged at this baseline (Step 4 §2.2) |
| **Ownership → Registry** | **Yes** — three registries (`generated-artifact-registry.json`, `id-ledger.json`/`artifacts.json`, `ucos-ownership-declarations.json`) each hold a piece of "who owns this," none cross-referencing the others (`AAT-1`) | **Yes** — same defect, restated as a join | — | — |
| **Registry → Visibility** | — | — | `config.py` declares GENERATED bounded by `.gitignore`; `generated-artifact-registry.json` holds 345 tracked GENERATED entries; PORTAL (1,240 tracked, 228 untracked, same producer) splits across both dispositions with no registry entry explaining why (Step 3 §6.4) | Disposition (Option A ignore / Option B commit) still unresolved, `OB-5` blocks Option B (`--guard` timestamp non-determinism) |
| **Visibility → Certification** | — | — | `R-EV-4` forbids `DEBUG`/`IMPROVEMENT` classes from certification but not by visibility — 3 of 10 evidence surfaces are untracked and `may_affect_certification: true` (`AV-8`) | Live verdict `NOT-CERTIFIED`; cited `CERTIFIED-PROVISIONAL` in prior determinations is a superseded run (Step 3 `AV-5`) |
| **The pipeline as a whole** | **Yes — it is not the declared order.** Step 3 §7.3 measured the implemented order as `VISIBILITY → CLASSIFICATION → (OWNER ⊥) → CERTIFICATION`, with `CERTIFICATION` feeding back into `VISIBILITY` (`AV-8`), closing a loop the framework forbids | `REGISTRY` does not appear in Step 3's seven-position framework at all — it is the directive's own addition, and no single register plays that role uniformly (`AAT-1`, sharpened §3.3 below) | — | — |

### 2.2 What is new here versus Steps 3–4

Steps 3–4 measured the OWNERSHIP axis's disconnection (`AV-4`) and generalized it across all
five attribution columns (`AAT-1`). Re-reading the pipeline transition by transition (§2.1)
surfaces one thing neither step's axis-based framing exposed: **the same physical
directory can be claimed by two registers under two different classes, with no declared
precedence between them.** This is not `AV-6` (visibility deciding classification) — it is
two classification vocabularies disagreeing about a **tracked-visibility-irrelevant**
question. §4 below measures three instances.

---

## 3. Target Deterministic Attribution Pipeline

### 3.1 The seven-node target

```
Artifact Identity → Artifact Class → Canonical Authority Record → Owner → Lifecycle State → Visibility State → Certification State
```

This is Step 3 §7.1's seven-position framework with one substantive change: **`CANONICAL
AUTHORITY RECORD` replaces `AUTHORITY`,** made a first-class node between class and owner
rather than a property Step 3 folded into ownership (Step 4 §2.1 made that folding
explicit). The directive's insertion of `REGISTRY` between ownership and visibility in the
*current* pipeline (§2.1) is, by measurement, this same node arriving too late — todaythe
registry lookup happens after an ownership claim already failed to join to anything (§2.1
row 3), where in the target it must happen **before** OWNER is asked, because the register
is what OWNER is read from.

| Node | Question | What would make it deterministic (per class, §4) | Current standing |
|---|---|---|---|
| **ARTIFACT IDENTITY** | What is this artifact's stable identity, independent of path? | A content-or-origin key that survives a move/rename — none declared today | Not represented; identity is conflated with path everywhere (Step 3 §7.3 `ORIGIN` finding) |
| **ARTIFACT CLASS** | Which of AUTHORED/GENERATED/DERIVED/EVIDENCE/CACHE/TEMPORARY? | `R-01`–`R-09` evaluated **without** `tracked` as a precondition (`AV-6` repair, Stage 1) | `classify()` → `ERROR`; counterfactual evaluation only |
| **CANONICAL AUTHORITY RECORD** | Which single register is authoritative for this class? | One register per class, declared as authoritative and not merely descriptive (§4) | **None** — `AAT-1`/`AAR-3`: no class has one register playing this role across source+owner+registry+visibility+certification |
| **OWNER** | Which authority answers for it? | A join key shared between the class's authority record and `ucos-ownership-declarations.json` | `assignments: {}` (empty); 345+1,461 populated owners share no key (`AV-4`) |
| **LIFECYCLE STATE** | What states may it occupy, what transitions are legal? | A per-class enum with ≥2 observed values | GENERATED's `lifecycle` field has exactly 1 observed value across 345/345 entries (`AV-3`) |
| **VISIBILITY STATE** | Does version control carry these bytes, **as a consequence of class, never a cause** | A declared expected-tracked-ness per class (AUTHORED/GENERATED: yes; CACHE/TEMPORARY: no; EVIDENCE/DERIVED: per-surface) | No register declares *expected* tracked-ness for any path (Step 3 §3.4) |
| **CERTIFICATION STATE** | What has been proven, does it still hold, computed **from** the six upstream nodes only, never feeding back | `CEP-005` Article VI, implemented or formally superseded | Unimplemented; 4 disagreeing vocabularies; live verdict below the cited ceiling (`AV-5`); feeds back into visibility today (`AV-8`) |

### 3.2 The two ordering rules the target must satisfy

Carried forward from Step 3 §7.2, unchanged, because Step 5 measured no reason to revise
them: **(1)** each node is a function of its predecessors only — `VISIBILITY` is decided
*from* `ARTIFACT CLASS`, never the reverse, and `CERTIFICATION` may never feed back into
any upstream node; **(2)** the terminal at every node is fail-closed, never a default — an
artifact with no resolvable class, authority record, or owner is refused, not silently
absorbed into `REPOSITORY_STATE` the way `R-01` absorbs it today.

### 3.3 `AAR-3` — No canonical authority record exists for any class today

**Severity: HIGH — this is the node the whole pipeline pivots on.**

`AAT-1` (Step 4) measured that no class has one register serving as source, owner,
registry, visibility rule and certification law simultaneously. Restated as a pipeline
node: the target pipeline's third node, `CANONICAL AUTHORITY RECORD`, is meant to be
exactly that single register — and by the same measurement, **it does not exist for any of
the six classes.** GENERATED comes closest (`generated-artifact-registry.json` serves
source, owner and certification-role) but its visibility rule lives in a different file
(`config.py`) and contradicts the register on PORTAL. Every other class is worse: AUTHORED
has three candidate registers depending on sub-type and none for the untracked residue;
CACHE and TEMPORARY resolve to non-UCOS owners (`AAT-3`) so "authority record" is a
category error for them by design; EVIDENCE's authority (`evidence-universe.json`) is
itself in conflict with a second register over the same paths (`AAR-1`, next section).

---

## 4. Per-Class Attribution Model

Extends Step 4 §4's five-column table with two columns the directive asks for here:
**owner resolution method** (how, mechanically, an owner would be read) and **migration
requirement** (which Step 4 §5 stage must land before that class's attribution is safe).

| Class | Attribution source | Required registry | Owner resolution method | Visibility rule | Certification rule | Migration requirement |
|---|---|---|---|---|---|---|
| **AUTHORED** | Self-declared Authority/Deciders field in the artifact's own header (`GOVERNED_DECLARATION`/`AUTHORED_DOCUMENT`/`GOVERNED_ANALYSIS`) | None uniform — `id-ledger.json`+`artifacts.json` for the 1,233 corpus-registered subset only | Read the self-declaration; **no independent check exists** (`AAT-2`) | Should be TRACKED (loss is permanent); not enforced — `AV-6` absorbs untracked authored paths | `grants_only_mutation_ownership`: none granted; certification remains with the unimplemented `CEP-005` chain | Stage 1 (`R-01` repair) is the floor; a registry for the untracked residue (measured §5.3: 4,663 candidate paths) does not exist and is not scheduled by any stage |
| **GENERATED** | `generated-artifact-registry.json` (`D-1`) | `generated-artifact-registry.json` itself | Read `owner`/`validation_owner` field, 345/345 populated | Declared "bounded by `.gitignore`" but 1,240+228=1,468 PORTAL pages (tracked+untracked) are GENERATED and mostly tracked, contradicting the declaration | `certification_role` field (5 values) + Phase 8/9 checks | Stage 3 (`AV-3`): register the 1,468 `00-BOOK` GENERATED paths — 0/345 currently under `00-BOOK` |
| **DERIVED** | `generated-artifact-registry.json` `generated_inputs` (10 entries) | Same register, `generated_inputs` section | Inherit the owner of the GENERATED artifact the input feeds — no independent field | `"tracked": false` declared explicitly per entry; untracked by design | Inherits parent's certification posture; no independent rule declared | None named by Step 4; Step 5 adds none — the 10 entries are stable and internally consistent, unlike the other five classes |
| **EVIDENCE** | `evidence-universe.json` (10 declared surfaces, population 139) | `evidence-universe.json` `surfaces` | Read per-surface `owner` field — **free text**, not a joinable key (`AAT-5`) | Per-surface; only `VALIDATION` may be tracked, and only if derived from tracked truth | `may_affect_certification` boolean, per surface; `DEBUG`/`IMPROVEMENT` forbidden outright | Stage 6-adjacent: reconcile `AAR-1`'s triple-classification of `00-MASTER/**/evidence/`, `.runtime/`, `coverage.xml` before any EVIDENCE attribution is safe |
| **CACHE** | `exclusion-register.json`, class `CACHE` | `exclusion-register.json` `entries` | Read per-entry `owner` — resolves to a **non-UCOS** authority (CPython, pytest, ruff, mypy) by design (`AAT-3`) | `IGNORED` always | None — explicitly disclaimed as carrying no information | Stage 2 (`OB-1`/`OB-2`): the bare `*` rule self-matches every path when evaluated without out-of-band directory scoping (re-confirmed §1.2); `.ucos-verification-evidence/` (46 files) and `.ucos/*.json` (2 files) are ignored but registered in **no** class at all (`AAR-2`) |
| **TEMPORARY** | `exclusion-register.json`, class `TEMPORARY` | `exclusion-register.json` `entries` | Read per-entry `owner` — the creating process | `IGNORED`, bounded lifetime | None — no consumer outside the creating operation | None named — the 2 measured entries (`~$*.docx` lock files) are internally consistent |

---

## 5. Population Analysis — 13,689 Paths, Classified By Class, Not Visibility

### 5.1 Method and the population delta from Step 4

Step 4 measured 13,688 paths at this identical HEAD; this determination measures 13,689 —
one more, which is Step 4's own determination file, created after Step 4's measurement and
still untracked at the moment this count was taken. This is the same mechanism Step 2 §9.1
and Step 4 `AAT-4` both already named: **a determination that measures the untracked
population becomes a member of it the instant it is written.** It is not corrected for
below, because doing so would require excluding this determination's own predecessor from
a population count taken *before* this determination existed — the count is reported as
measured, with the mechanism named rather than hidden.

### 5.2 The five-way partition, computed by directory/registry membership — not by visibility

| Bucket | Count | Share of 13,689 | Method |
|---|---|---|---|
| **REPOSITORY ARTIFACTS (AUTHORED)** | **4,663** | 34.1% | Tracked non-GENERATED (6,188 − 1,608* GENERATED-under-00-BOOK-or-registered = 4,580) + untracked root-level `.md` (73) + untracked `.py` (9) + untracked `.json` declaration (1) |
| **GENERATED ARTIFACTS** | **2,198** | 16.1% | 345 registered+tracked + 1,263 tracked-under-`00-BOOK`-unregistered (1,240 PORTAL + 17 DATA + 6 REGISTRIES, `AV-3`) + 228 untracked PORTAL + 362 ignored paths under directories `exclusion-register.json` classes `GENERATED_DETERMINISTIC` |
| **CACHE ARTIFACTS** | **5,164** | 37.7% | Ignored, matched by directory to `__pycache__` (4,913) + `.ruff_cache` (227) + `.pytest_cache` (6) + `.mypy_cache` (18) |
| **ENVIRONMENT ARTIFACTS** | **1,607** | 11.7% | Ignored, matched to `.ec1-venv/` (1,470) + `.runtime/` (128) + `build/`/`dist/`/`*.egg-info` (8) + `.claude/settings.local.json` (1) — `exclusion-register.json` class `TOOL_OPERATIONAL` |
| **EVIDENCE ARTIFACTS** | **49** | 0.4% | `.ucos-verification-evidence/` (46, unregistered — `AAR-2`) + `.ucos/execution-evidence.json` (1, unregistered) + 2 residual `.coverage*`/`coverage.xml` (`TEST_EXECUTION_ARTIFACT` in V2, `EV-COVERAGE-*` in V4 — `AAR-1`) |
| **RESIDUAL / AMBIGUOUS** | **8** | 0.1% | `.ucos/environment-fingerprint.json` (CACHE-shaped, unregistered) + `~$*.docx` (2, TEMPORARY) + `.claude/scheduled_tasks.lock` (1) + 4 miscellaneous `00-MASTER` JSON files matched by no directory heuristic |
| **TOTAL** | **13,689** | 100.0% | |

\* 1,608 = 345 registered + 1,263 tracked-`00-BOOK`-unregistered; both counted once under GENERATED, not twice under REPOSITORY ARTIFACTS.

This partition uses **class membership by directory and registry lookup**, never tracked/
untracked/ignored state, as the directive requires. It disagrees sharply with a
visibility-only partition: a visibility-only count would report "6,188 repository content,
7,501 not" — collapsing GENERATED, CACHE, ENVIRONMENT and EVIDENCE into one undifferentiated
"not tracked" bucket, which is `AV-6` applied to population reporting instead of
per-artifact classification. The two partitions of the *same* 13,689 paths disagree by
construction, and that disagreement is the empirical case for §3's target pipeline.

### 5.3 `AAR-1` — Three directories are classified twice, under disagreeing classes, with no declared precedence

**Severity: CRITICAL.**

Cross-reading `exclusion-register.json` (V2) against `evidence-universe.json` (V4) for the
same path prefix, not sampled but exhaustive over both registers' declared paths:

| Path prefix | V2 class (`exclusion-register.json`) | V4 class (`evidence-universe.json`) | Measured population |
|---|---|---|---|
| `00-MASTER/**/evidence/` | `GENERATED_DETERMINISTIC` | `EVIDENCE` (`EXECUTION` ×2 surfaces, `VALIDATION` ×1) | 139 (surface `population` sum) — the 362-count in §5.2's GENERATED bucket includes these; this row is the same physical files, counted once |
| `.runtime/` | `TOOL_OPERATIONAL` | `EVIDENCE` (`EV-GOVERNANCE-TELEMETRY`) | 128 (§5.2 ENVIRONMENT bucket) |
| `.coverage*`, `coverage.xml` | `TEST_EXECUTION_ARTIFACT` | `EVIDENCE` (`EV-COVERAGE-REPORT`, `EV-COVERAGE-DATA`) | 2 (§5.2 EVIDENCE bucket, residual row) |

Neither register declares the other as superseded, subordinate, or consulted-first for
these three prefixes. `evidence-universe.json`'s own `not_in_this_universe` clause (quoted
in Step 3 §2.2) performs exactly this reconciliation for `data/_evidence/`—stating plainly
that those 123 artifacts are governed elsewhere, not evidence — but **no equivalent
disclaimer exists for `00-MASTER/**/evidence/`, `.runtime/`, or coverage output**, even
though all three are claimed by V2 under a different class with a different disposition
(`TOOL_OPERATIONAL`/`GENERATED_DETERMINISTIC` imply "reconstructible, no information";
`EVIDENCE` implies "historical record, may affect certification"). This is the same
mechanism `AV-1` measured for `data/_evidence/` and `PORTAL`, found here on three
additional, previously unexamined prefixes — the pattern is not confined to the two paths
Step 3 sampled; it recurs wherever V2 and V4 both declare a rule over the same directory.

### 5.4 `AAR-2` — 48 ignored, populated paths are claimed by none of the three registers

**Severity: HIGH.**

`.ucos-verification-evidence/` is listed in `.gitignore` (line 222) and holds 46 tracked
verification-run artifacts at this baseline (`autonomous-evolution/`, `evolution-replay/`,
`governance-pre/`, `meta-constitutional/`, `object-birth/`, `registry-validate/`, `ruff/`
subdirectories — content that is, by every declared definition in `evidence-universe.json`
§2, EVIDENCE: *"what a command emitted when it ran."*) It appears in **zero** of
`exclusion-register.json`'s 32 entries, `evidence-universe.json`'s 10 surfaces, and
`generated-artifact-registry.json`'s 345 entries — confirmed by direct `grep` across all
three files, no matches. `.ucos/execution-evidence.json` (1 file) and
`.ucos/environment-fingerprint.json` (1 file) — the exact two paths Step 3 §4.1 used as
its own representative examples of `AV-6`'s absorption — are likewise absent from all
three registers under any `.ucos/` prefix; `grep '"\.ucos'` against `exclusion-register.json`
returns nothing.

`exclusion-register.json`'s own invariant states: *"Every ignored path resolves to exactly
one entry here (`ignored_unclassified` = 0)."* The register's self-reported metric is 0
(Step 3 §6.2, re-confirmed unchanged). The measurement here is that **at least 48 ignored
paths resolve to no entry**, which the register's own metric does not detect because
nothing computes it against the live `.gitignore`/working-tree population — the metric is
declared, not measured, exactly as Step 3 `OB-1` found for the classifier's coverage claim.

### `AAR-4` — Non-repository ephemeral state is the majority of the measured population

**Severity: MEDIUM, and it is the quantitative form of `AAT-4`.**

CACHE (5,164) + ENVIRONMENT (1,607) = **6,771 of 13,689 paths — 49.5%** — are local machine
state that would not exist in a pristine clone and were not present, in this proportion,
at Step 3's baseline (233 total ignored paths, §Step 3 §3.4) taken at the **identical
commit**. `AAT-4` named the mechanism; this measurement gives it a share: essentially half
of any raw population count taken from this working tree, at any point, is expected to be
tool-generated noise rather than repository content, cache, or evidence of anything. An
attribution readiness gate that reports "N of 13,689 paths attributed" without first
removing this half is reporting against a denominator that is mostly not the repository's
concern.

### `AAR-5` — This determination's own partition is not a classification of record

**Severity: LOW / structural.**

§5.2's five-way partition was computed by hand-written directory-prefix matching, not by
executing `mutation_classification.classify()` (which still returns `ERROR`, §1.3) or any
other first-party classifier. It is subject to the same limitation Steps 1–4 each declared
of their own manual readings: it is a **best-effort reconstruction of declared rules**,
demonstrated in §1.2 to reproduce `exclusion-register.json`'s own known defect (the bare
`*` rule self-matching every path, `AV-1`/§6.2) when evaluated literally rather than with
the register's undeclared out-of-band directory scoping. The 8-path RESIDUAL bucket in
§5.2 is itself evidence of this: those paths are not ambiguous in the repository's own
terms, only in this determination's necessarily incomplete reconstruction of the register's
intent. This finding does not revise §5.2's counts; it bounds the confidence they should
be read with, the same way Step 3 §1.3 bounded its own counterfactual evaluation.

---

## 6. Prerequisites For BC-6 Step 6 — Clean Baseline Certification

Read from the dependency structure established across Steps 3–5, not assigned or scheduled
here:

| # | Prerequisite | Source | Status at this baseline |
|---|---|---|---|
| 1 | `_r01_repository_state` consults the exclusion register before claiming a path (Step 4 Stage 1) | `AV-6` | **NOT MET** — mechanism unchanged, confirmed §1.2 |
| 2 | `ignored_unclassified` is measured against live `.gitignore`/working-tree state, not self-reported | `AAR-2` (new) | **NOT MET** — 48 ignored paths resolve to no register entry, undetected by the register's own metric |
| 3 | `00-MASTER/**/evidence/`, `.runtime/`, `coverage.xml`/`.coverage*` have one declared class each, or an explicit precedence between V2 and V4 | `AAR-1` (new) | **NOT MET** — three unreconciled dual-classifications |
| 4 | 1,468 `00-BOOK` GENERATED paths (1,240 PORTAL + 17 DATA + 6 REGISTRIES tracked, 228 PORTAL untracked) are registered in `generated-artifact-registry.json` | `AV-3` (Step 4 Stage 3) | **NOT MET** — 0/345 entries under `00-BOOK` |
| 5 | `R-09 GOVERNED_ANALYSIS` predicate implemented | BC-1 (Step 4 Stage 4) | **NOT MET** — `classify()` → `ERROR` for all subjects |
| 6 | Ownership catalogue ratified (`assignments` populated from the 345+ read-but-unjoined owners) | `AV-4`/`CEP-OWN-004` (Step 4 Stage 5) | **NOT MET** — `assignments: {}`, re-verified §Step4 §2.2 and again implicitly here |
| 7 | Certification law (`CEP-005` Art VI) implemented or formally superseded; the four disagreeing vocabularies reconciled | `AV-5` (Step 4 Stage 6) | **NOT MET** — live verdict `NOT-CERTIFIED`, `AV-8` regression still live |
| 8 | The `CANONICAL AUTHORITY RECORD` node (§3.3) exists for at least the GENERATED and AUTHORED classes, the two largest populations (2,198 + 4,663 = 6,861 of 13,689, 50.1%) | `AAT-1`/`AAR-3` (new, sharpened) | **NOT MET** — no class has this node today |
| 9 | A stated method for excluding CACHE/ENVIRONMENT paths (49.5% of the measured population, `AAR-4`) from any readiness or coverage denominator | `AAR-4` (new) | **NOT MET** — no register declares this exclusion as a rule; it is reconstructed by hand in §5.2 |

**Zero of nine prerequisites are met at this baseline.** Prerequisites 1, 4, 5, 6, 7 restate
Step 4 §5 Stages 1, 3, 4, 5, 6 verbatim, confirmed still open. Prerequisites 2, 3, 8, 9 are
new, surfaced only by this determination's directory-level population analysis (§5) rather
than the axis-level analysis Steps 3–4 performed. None is closed by this determination,
and none is scheduled — this table names dependency, not a plan.

---

## 7. Findings Register

| ID | Finding | Severity | Owner (read, not assigned) | Status |
|---|---|---|---|---|
| `AAR-1` | `00-MASTER/**/evidence/`, `.runtime/`, and `coverage.xml`/`.coverage*` are each classified under disagreeing classes by `exclusion-register.json` (V2) and `evidence-universe.json` (V4) simultaneously, with no declared precedence | **CRITICAL** | exclusion-register owner · evidence-universe owner | **OPEN** |
| `AAR-2` | 48 ignored paths (`.ucos-verification-evidence/` ×46, `.ucos/*.json` ×2) resolve to no entry in any of the three registers; the exclusion register's own `ignored_unclassified = 0` invariant does not detect this because it is self-reported, not measured | **HIGH** | exclusion-register owner · Repository Intelligence | **OPEN** |
| `AAR-3` | The target pipeline's `CANONICAL AUTHORITY RECORD` node has no implementation for any of the six classes; `AAT-1` restated as a pipeline-node gap rather than an axis gap | **HIGH** | Mutation governance owner | **OPEN** |
| `AAR-4` | CACHE + ENVIRONMENT artifacts are 49.5% of the measured 13,689-path population at an unchanged HEAD — non-repository ephemeral state dominates any raw count | **MEDIUM** | Repository Intelligence | **OPEN** |
| `AAR-5` | This determination's own five-way partition (§5.2) is a hand-reconstructed reading, not a classification of record, and is shown to reproduce a known register defect (the unscoped `*` rule) when evaluated literally | **LOW / structural** | — (self-limitation, not assignable) | **OPEN** |

**5 raised · 0 resolved · 0 repaired.**

### 7.1 Relationship to prior findings

| Prior | Step 5 disposition |
|---|---|
| Step 3 `AV-1` (six vocabularies, no crosswalk; `data/_evidence/`/PORTAL dual-claimed) | **Extended**: the dual-classification pattern recurs on three further prefixes not previously examined (`AAR-1`) |
| Step 3 `AV-6` (visibility determines classification) | **Restated as the target pipeline's ordering constraint** (§3.2); not re-measured as a new finding |
| Step 4 `AAT-1` (no class has one authority across all 5 columns) | **Sharpened** into pipeline-node form as `AAR-3` |
| Step 4 `AAT-3` (CACHE/TEMPORARY resolve to non-UCOS owners) | **Unchanged**, carried into the per-class table (§4) verbatim |
| Step 4 `AAT-4` (population volatility, 2x growth at unchanged HEAD) | **Quantified**: 49.5% of the current population is the CACHE+ENVIRONMENT share driving that growth (`AAR-4`) |
| Step 3 `OB-1` (classification obligation structurally void) | **Re-confirmed a third time**: the register's own coverage metric (`ignored_unclassified = 0`) is self-reported and undetects the 48 paths `AAR-2` measures |

---

## 8. What Step 5 Establishes And What It Does Not

### 8.1 Establishes

- **The current pipeline's six transitions**, each graded for ambiguity, missing joins,
  conflicting authorities and unresolved dependencies (§2.1) — the directive's four
  questions, answered per transition rather than per axis.
- **A seven-node target pipeline** (§3.1) that inserts `CANONICAL AUTHORITY RECORD` between
  class and owner, and shows the current pipeline's `REGISTRY` step is that same node
  arriving too late, after an ownership lookup has already failed to join (§3.1 note).
- **A complete per-class attribution model** (§4) — attribution source, required registry,
  owner resolution method, visibility rule, certification rule, and migration requirement —
  for all six canonical classes, extending Step 4 §4 with the two columns this directive
  asks for.
- **A five-way population partition of 13,689 paths by class, not by visibility** (§5.2),
  the directive's explicit requirement, showing the two kinds of partition disagree by
  construction on the same population.
- **Three newly measured dual-classification contradictions** (`AAR-1`) on prefixes Step 3
  did not sample, and **48 doubly-unregistered ignored paths** (`AAR-2`) the exclusion
  register's own invariant does not detect.
- **A nine-item prerequisite list for Step 6** (§6), of which zero are met, five restating
  Step 4's migration stages and four newly surfaced by this determination's directory-level
  analysis.

### 8.2 Does not establish

| Not established | Why | Requires |
|---|---|---|
| Any classification, ownership or certification of record | `classify()` still returns `ERROR` for all subjects | BC-1 / `R-09` |
| That the target pipeline (§3.1) or per-class model (§4) is adopted | This determination has no authority | Mutation governance owner |
| A resolved precedence between V2 and V4 for the three `AAR-1` prefixes | Neither register declares one; this determination only measures the absence | exclusion-register owner + evidence-universe owner, jointly |
| A repaired `ignored_unclassified` metric | Would require executing a live count against `.gitignore`, not reading a self-reported field | Implementation authority |
| That the 13,689-path partition (§5.2) is stable | Re-measured once already at 13,688 → 13,689 with zero commits between (§5.1) | Partition by class before any downstream use, per `AAR-4` |
| BC-6 Step 6 readiness | Zero of nine prerequisites (§6) are met | All nine, independently |

### 8.3 The recursion, at Step 5

Consistent with Steps 3–4: this determination's own act of measuring the population made it
a member of the population it measured (§5.1). Its own five-way partition is, by its own
admission (`AAR-5`), not a classification of record. The pattern begun at Step 3 —
the instrument that would verify a separation is the instrument subject to the defect it
measures — holds at Step 5 for a third axis: population counting.

---

## 9. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-ARTIFACT-ATTRIBUTION-RECONCILIATION-DETERMINATION.md` |
| Required sections present | ✅ current pipeline analysis (§2) · target pipeline (§3) · per-class model (§4) · population analysis by class, not visibility (§5) · Step 6 prerequisites (§6) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis only — implementation performed | ✅ **0** |
| Code changes | ✅ **0** — every module and registry read, none written |
| Configuration changes | ✅ **0** |
| Registry changes | ✅ **0** — 4 registers read, none written |
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
`generated-artifact-registry.json`, `evidence-universe.json`, or a fresh `git ls-files`
partition at the stated HEAD — none is a classification, ownership or certification of
record, because `classify()` returns `ERROR` for all subjects at this baseline. Five
findings (`AAR-1`…`AAR-5`) are raised and all remain open. Steps 3–4's `AV-1`…`AV-9` and
`AAT-1`…`AAT-5` remain open and unaffected. Zero of nine Step 6 prerequisites are met.
`A6-1` attribution remains confirmed, not attempted. The single repository mutation is the
creation of this file.*

**END DETERMINATION — BC-6 STEP 5 COMPLETE · STEP 6 NOT PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
