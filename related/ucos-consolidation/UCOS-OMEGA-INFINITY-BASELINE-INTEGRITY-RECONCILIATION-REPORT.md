# UCOS Ω∞ — BASELINE INTEGRITY RECONCILIATION REPORT

**BC-6 · Step 1 — Classification of every current repository mutation**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-BASELINE-INTEGRITY-RECONCILIATION-REPORT.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, requirement, ADR, phase or certification. Authorizes nothing. Assigns no ownership. Approves no commit. |
| Mode | READ-ONLY CLASSIFICATION · **NO FILE MODIFIED · NO COMMIT · NO RESTORE · NO DELETE** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Step | **BC-6 Step 1 only.** Steps 2–6 of the companion plan are not performed |
| Predecessors | `…UNIVERSAL-FOUNDATION-TRANSFORMATION-EXECUTION-READINESS-DETERMINATION.md` (BC-6) · `…BLOCKER-CLOSURE-IMPLEMENTATION-PLAN.md` §3.6 · `…BLOCKER-CLOSURE-STATUS-REGISTER.md` §8 |
| Population classified | **338 mutations** — 38 modified tracked · 300 untracked |
| Mutations approved for commit by this report | **ZERO.** Classification is not approval |
| Mutations rolled back | **ZERO** |

---

## 1. Objective and Method

### 1.1 Objective

Classify **every** current repository mutation before any implementation, so that evidence produced by later closure work is distinguishable from pre-existing change. This is the precondition B-7 §3 records as condition `0.6`, and which the readiness determination records as **BC-6**.

### 1.2 Method

Every measurement below is a **read** or an **in-memory comparison against `HEAD`**. Nothing was written, committed, restored, deleted, or registered.

| Instrument | Purpose |
|---|---|
| `git diff --numstat` / `--shortstat` | Per-file and aggregate diff magnitude |
| `git status --porcelain` | Modified and untracked enumeration |
| `git show HEAD:<path>` | Compare current ledger state against committed state **without touching the working copy** |
| `git ls-files` | Tracked-set membership |
| Python `json.load` on register files | Structural comparison of declarations and ledgers |
| `00-BOOK/DATA/generated-artifact-registry.json` | Generated-path authority (345 entries · 31 producer homes · 10 generated inputs) |
| `00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES` | Registration-eligibility authority |
| `00-BOOK/DATA/mutation-governance-boundary.json` | The nine declared mutation classes R-01…R-09 |

### 1.3 Classification vocabulary

Mutation class is taken from the **declared** boundary register, never invented:

| Rule | Class | Precedence |
|---|---|---|
| R-01 | `REPOSITORY_STATE` | 1 |
| R-02 | `EXCLUSION` | 2 |
| R-03 | `CORPUS_REGISTRATION` | 3 |
| R-04 | `GENERATED_ARTIFACT` | 4 |
| R-05 | `CONSTITUTIONAL_TRUTH` | 5 |
| R-06 | `GOVERNED_DECLARATION` | 6 |
| R-07 | `SOURCE` | 7 |
| R-08 | `AUTHORED_DOCUMENT` | 8 |
| R-09 | `GOVERNED_ANALYSIS` | 9 |

**Standing limitation, declared not hidden.** `classify()` returns `ERROR` for every subject at this baseline (BC-1 / M-C), because R-09 is declared with no predicate. **Every class assignment in this report is therefore a manual reading of the declared predicates, not a machine verdict.** It is offered as analysis, and it is exactly the work that BC-1 would automate. No class assignment here may be treated as a classification of record.

---

## 2. Baseline Measurement

| Measure | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| `git status --porcelain` lines | **338** |
| Modified tracked files | **38** |
| Untracked paths | **300** |
| Staged files | **0** |
| Aggregate diff | **38 files · +81,631 insertions · −51,350 deletions** |
| Largest single diff | `00-BOOK/DATA/change-ledger.json` — +22,898 / −13,068 |
| Corpus identities newly allocated | **+228** (`id-ledger.by_path` 1,264 → 1,492) |
| Category codes newly allocated | **+83** (`id-ledger.category_seq` 117 → 200) |
| Object identities changed | **0** (`by_object` 4,914 → 4,914) |
| Identities removed | **0** |

### 2.1 The finding that dominates this report

> **The working tree contains 228 permanently allocated corpus identities and 83 newly minted category codes that exist only in an uncommitted ledger.**

`by_path` grew 1,264 → 1,492 with **zero removals**. `category_seq` grew 117 → 200. Every one of the 228 registered paths **exists on disk**; none is a phantom registration.

This is the same failure *class* as the precedent recorded in `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` §1 — *140 identifiers minted as a side effect of a drift check* — at **1.6× the scale**, and it is the single strongest argument against the bulk-discard shortcut that the companion plan §3.6.5 forbids. Discarding this tree would destroy 228 permanent corpus identities.

---

## 3. Change Set Identification

The 338 mutations are **not drift.** They resolve into **four coherent, self-documenting change sets**, each with a declared purpose and an identifiable owner. This is the most important structural finding of Step 1: the baseline is dirty but it is not incoherent.

| Set | Name | Modified | Untracked | Purpose evidence |
|---|---|---|---|---|
| **CS-1** | **UEG-000001 — Universal Execution Governance** | **9** | **3** | `00-MASTER/UEG-000001/ueg-declaration.json` · `verify.sh` Stage 0 · MIP Part 52 |
| **CS-2** | **UVI-000001 — Verification intelligence / impact** | **6** | 0 | `engine/verification_intelligence/` + `verification_impact` + tests |
| **CS-3** | **Corpus registration run** | **22** | **228** | `id-ledger` +228 identities · portal regeneration |
| **CS-4** | **Knowledge provenance registration** | **1** | 0 | `registry_coverage/declarations.json` +1 line |
| **U** | **Unassigned — pre-existing untracked analysis corpus** | 0 | **69** | Root-level `.md` analysis artifacts |
| | **TOTAL** | **38** | **300** | |

`9 + 6 + 22 + 1 = 38` ✔ · `3 + 228 + 69 = 300` ✔

### 3.1 CS-1 — UEG-000001 Universal Execution Governance

**The most coherent change set in the tree, and the only one that is self-declaring.**

Purpose, read directly from the `verify.sh` diff: a **separation-of-powers correction**. The gate previously repaired its own environment; it now observes and refuses.

> `# THIS SCRIPT NO LONGER REPAIRS ITS OWN ENVIRONMENT, AND SAYING SO IS THE POINT.`
> `# It used to call ucos_ensure_venv here, which will \`rm -rf\` a virtual environment whose…`
> `# --- Stage 0: UEG-000001 environment integrity gate (OBSERVE ONLY) ---`
> `# IT VERIFIES THE ENVIRONMENT; IT DOES NOT REPAIR IT.`

The set carries its own declaration (`ueg-declaration.json`, `separation_of_powers`), its own test measuring the boundary **over the source of `verify.sh` itself** (`test_execution_environment.py`), its own exclusion rule with a nine-line written rationale, and its own plan-level admission (MIP **Part 52**, *"Admitted by `UEG-000001`… derived from execution-environment assessment `F-1`/`F-2`"*).

**This is the change set most eligible to proceed**, and it is also the one that most needs care, because it modifies the gate that measures everything else.

### 3.2 CS-2 — UVI-000001 verification intelligence and impact

Modifies `engine/verification_intelligence/{model,registry,selection}.py`, `engine/verification_impact/changes.py`, and two tests. `test_verification_impact.py` is **+155 / −0** — a substantial new test body.

**Direct collision with later closure work.** This set touches the exact surfaces BC-2 (`T-19.1` detection) and `T-13.3` (substrate coverage, **R-24 CRITICAL**) would modify, and it includes `platform/tests/test_mutation_classification.py` — **BC-1's own test**. Per §7, this set must be settled before BC-1 or BC-2 is attempted, or their evidence is attributable to neither.

### 3.3 CS-3 — Corpus registration run

The largest set by volume: **22 modified + 228 untracked = 250 of 338 mutations (74%)**.

It registered **228 previously unregistered artifacts** — overwhelmingly root-level determinations, H-06 decision records, PHASE reports and SCOPE-B reports, plus 25 `adr/`, 3 `engine/` and 1 `00-BOOK/DECISIONS/` path — allocating one corpus identity each and **83 new 6-character category codes** (`ASSESS`, `B01BIR`, `B02LIF`, `GATEPU`, `H06ATO`, …), then regenerated the portal and every dependent registry.

The 6-character codes confirm `DERIVED_CATEGORY_MAXLEN = 6` (constraint **P-13**) is live and being exercised at scale.

**Numerical coherence:** 228 identities allocated ↔ 228 new portal pages. The correspondence is exact and is the strongest evidence that this set is one atomic operation that has not been committed.

### 3.4 CS-4 — Knowledge provenance registration

A single line: `"knowledge/canonical-knowledge-history.json"` added to `engine/registry_coverage/declarations.json`. Registers the knowledge-history file for coverage. Smallest, most isolated, lowest-risk change in the tree.

---

## 4. Modified Tracked Files — Full Classification

Diff figures are `+insertions / −deletions` measured first-party. **Owner is *probable*, inferred from declared homes and producer registries — not assigned.** **Purpose is read from diff content where the diff states it, and marked `INFERRED` where it does not.**

### 4.1 CS-1 · UEG-000001 — 9 files

| # | Path | Diff | Origin | Probable owner | Purpose | Evidence | Class |
|---|---|---|---|---|---|---|---|
| 1 | `verify.sh` | **+46 / −6** | CS-1 | Verification / gate owner | Adds **Stage 0 UEG environment integrity gate (OBSERVE ONLY)**; removes gate self-healing (`ucos_ensure_venv`) | **Self-stating in diff** — 6 rationale comments quoted §3.1 | **R-07 `SOURCE`** |
| 2 | `.gitignore` | **+9 / −0** | CS-1 | Exclusion authority | Excludes `.ucos/` — UEG environment fingerprint cache and per-run evidence | **Self-stating** — 8-line written rationale: *"None of it reproduces on another machine… committing it would publish a claim that is false everywhere except where it was written"* | **R-02 `EXCLUSION`** |
| 3 | `scripts/ucos-env.sh` | **+84 / −3** | CS-1 | Environment owner | Environment resolution moved out of the gate | INFERRED from CS-1 coherence | **R-07 `SOURCE`** |
| 4 | `ENVIRONMENT-SETUP.md` | **+91 / −1** | CS-1 | Environment owner | Documents the new repair/verify boundary | INFERRED | **R-08 `AUTHORED_DOCUMENT`** |
| 5 | `bootstrap.sh` | **+13 / −0** | CS-1 | Build owner | Repair path relocated to bootstrap | INFERRED | **R-07 `SOURCE`** |
| 6 | `doctor.sh` | **+14 / −0** | CS-1 | Build owner | Diagnostic path for the observed-not-repaired environment | INFERRED | **R-07 `SOURCE`** |
| 7 | `Makefile` | **+16 / −1** | CS-1 | Build owner | Target wiring for the environment gate | INFERRED | **R-07 `SOURCE`** |
| 8 | `pyproject.toml` | **+9 / −1** | CS-1 | Build owner | Toolchain declaration for the environment contract | INFERRED | **R-07 `SOURCE`** (build manifest, named in R-07's predicate) |
| 9 | `UCOS-MIP-000003-MASTER-IMPLEMENTATION-PLAN-V3.md` | **+55 / −1** | CS-1 | MIP owner | Admits **Part 52 — Universal Execution Governance**; parts 50 → 52 | **Self-stating** — *"Admitted by `UEG-000001`… derived from execution-environment assessment `F-1`/`F-2`"* | **R-09 `GOVERNED_ANALYSIS`** — **unclassifiable by machine until BC-1 closes** |

### 4.2 CS-2 · UVI-000001 — 6 files

| # | Path | Diff | Origin | Probable owner | Purpose | Evidence | Class |
|---|---|---|---|---|---|---|---|
| 10 | `engine/tests/unit/test_verification_impact.py` | **+155 / −0** | CS-2 | UVI-000001 owner | New test body for impact analysis | INFERRED | **R-07 `SOURCE`** |
| 11 | `engine/verification_impact/changes.py` | **+51 / −13** | CS-2 | UVI-000001 owner | Change-detection logic for impact | INFERRED | **R-07 `SOURCE`** |
| 12 | `engine/verification_intelligence/registry.py` | **+73 / −0** | CS-2 | UVI-000001 owner | Substrate/stage registry extension | INFERRED — **intersects `C-43` substrate list (10.4% coverage)** | **R-07 `SOURCE`** |
| 13 | `engine/verification_intelligence/selection.py` | **+31 / −1** | CS-2 | UVI-000001 owner | Selection logic | INFERRED — **intersects `C-42` / `T-13.3` / R-24 CRITICAL** | **R-07 `SOURCE`** |
| 14 | `engine/verification_intelligence/model.py` | **+11 / −0** | CS-2 | UVI-000001 owner | Model extension | INFERRED — intersects `C-26` | **R-07 `SOURCE`** |
| 15 | `platform/tests/test_mutation_classification.py` | **+3 / −3** | CS-2 | Repository Intelligence | Unknown — **3 lines changed, 3 removed** | **NONE.** Grep confirms **no `R-09` / `GOVERNED_ANALYSIS` coverage added** | **R-07 `SOURCE`** |

**File 15 requires specific attention.** It is the test of the blocker BC-1 exists to close, it has been modified, and it does **not** cover the missing predicate. Whether the change is unrelated maintenance or an abandoned attempt cannot be determined from the diff and must be answered by its owner.

### 4.3 CS-3 · Corpus registration run — 22 files

| # | Path | Diff | Probable owner | Purpose | Class |
|---|---|---|---|---|---|
| 16 | `00-BOOK/DATA/id-ledger.json` | **+12,290 / −8,058** | 00-BOOK / registry | **+228 identities · +83 categories** | **R-03 `CORPUS_REGISTRATION`** |
| 17 | `00-BOOK/DATA/artifacts.json` | **+9,368 / −3** | 00-BOOK / registry | 228 artifact records added | **R-03 `CORPUS_REGISTRATION`** |
| 18 | `00-BOOK/DATA/change-ledger.json` | **+22,898 / −13,068** | 00-BOOK / registry | Change lineage for the registration run | **R-03** (declared generated input) |
| 19 | `00-BOOK/DATA/relationships.json` | **+21,366 / −17,670** | 00-BOOK / registry | Relationship graph regeneration | **R-04 `GENERATED_ARTIFACT`** — `00-BOOK/DATA/` is a declared `generated_input` |
| 20 | `00-BOOK/DATA/control-tower.json` | **+719 / −103** | 00-BOOK | Control-tower state | **R-04** |
| 21 | `00-BOOK/DATA/volumes.json` | **+9 / −9** | 00-BOOK | Volume state | **R-04** |
| 22 | `00-BOOK/REGISTRIES/KNOWLEDGE-GRAPH-REGISTRY.md` | **+12,794 / −12,332** | 00-BOOK | Graph projection | **R-04** (`EXCLUDE_DIR_PREFIXES` lists `00-BOOK/REGISTRIES/`) |
| 23 | `00-BOOK/REGISTRIES/VOLUME-REGISTRY.md` | **+236 / −8** | 00-BOOK | Volume projection | **R-04** |
| 24 | `00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md` | **+229 / −1** | 00-BOOK | **229 ≈ 228 + header** | **R-04** |
| 25 | `00-BOOK/REGISTRIES/UNIVERSAL-PAGE-REGISTRY.md` | **+229 / −1** | 00-BOOK | Page projection | **R-04** |
| 26 | `00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md` | **+46 / −46** | 00-BOOK | Lineage projection | **R-04** |
| 27 | `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md` | **+93 / −16** | 00-BOOK | Control-tower projection | **R-04** |
| 28 | `00-BOOK/PORTAL/index.md` | **+229 / −1** | 00-BOOK | Portal index — **229 entries** | **R-04 (contested — see §6.2)** |
| 29 | `00-BOOK/PORTAL/UCOS-BOOK-000000.md` | **+440 / −0** | 00-BOOK | Portal book page | **R-04 (contested)** |
| 30 | `00-BOOK/PORTAL/UCOS-IDX-000001.md` | **+8 / −0** | 00-BOOK | Portal index page | **R-04 (contested)** |
| 31 | `00-BOOK/PORTAL/UCOS-ENG-000003.md` | **+6 / −0** | 00-BOOK | Portal page | **R-04 (contested)** |
| 32 | `00-BOOK/PORTAL/UCOS-USIS-000017.md` | **+3 / −1** | 00-BOOK | Portal page | **R-04 (contested)** |
| 33 | `00-BOOK/PORTAL/UCOS-CEP-000001.md` | **+2 / −0** | 00-BOOK | Portal page | **R-04 (contested)** |
| 34 | `00-BOOK/PORTAL/UCOS-USIS-000001.md` | **+1 / −0** | 00-BOOK | Portal page | **R-04 (contested)** |
| 35 | `00-BOOK/PORTAL/UCOS-EVOUSIS015-000002.md` | **+1 / −1** | 00-BOOK | Portal page | **R-04 (contested)** |
| 36 | `00-BOOK/PORTAL/UCOS-EVOUSIS016-000002.md` | **+1 / −1** | 00-BOOK | Portal page | **R-04 (contested)** |
| 37 | `00-BOOK/PORTAL/UCOS-USIS-000018.md` | **+1 / −1** | 00-BOOK | Portal page | **R-04 (contested)** |

### 4.4 CS-4 · Knowledge provenance — 1 file

| # | Path | Diff | Probable owner | Purpose | Evidence | Class |
|---|---|---|---|---|---|---|
| 38 | `engine/registry_coverage/declarations.json` | **+1 / −0** | Registry coverage owner | Registers `knowledge/canonical-knowledge-history.json` for coverage | **Self-evident** — single added array element | **R-06 `GOVERNED_DECLARATION`** |

---

## 5. Untracked Files — Classification

300 untracked paths, classified into the five requested categories.

| Category | Count | Share |
|---|---|---|
| **Generated artifact** | **228** | 76.0% |
| **Canonical artifact** | **69** | 23.0% |
| **Implementation artifact** | **2** | 0.7% |
| **Governed declaration** *(sub-class of canonical; broken out for accuracy)* | **1** | 0.3% |
| **Temporary artifact** | **0** | 0% |
| **Unknown** | **0** | 0% |
| **TOTAL** | **300** | 100% |

### 5.1 Generated artifact — 228

`00-BOOK/PORTAL/*.md` — 228 new portal pages (e.g. `UCOS-ADR-000004.md` … ).

**Basis for the classification, and the contest within it (§6.2):** `00-BOOK/tools/config.py:895` lists `00-BOOK/PORTAL/` in `EXCLUDE_DIR_PREFIXES`, and `config.py:451` describes the group as *"DATA/, CONTROL-TOWER/, PORTAL/, generated evidence"*. Three tools reference portal generation (`config.py`, `ukb.py`, `ukbx.py`). PORTAL is therefore **declared generated output**.

**Against that:** PORTAL is **tracked** — 1,240 files are under version control — and **absent from `generated-artifact-registry.json`** (0 of 345 canonical paths carry the prefix; the register's paths are 334 `00-MASTER/` + 11 `intelligence/`).

### 5.2 Canonical artifact — 69

Root-level `.md` analysis artifacts: determinations, assessments, matrices, registers, plans, reports, certifications and packages. All 69 match the R-09 `GOVERNED_ANALYSIS` filename criterion.

| Sub-group | Count | Note |
|---|---|---|
| Pre-existing untracked analysis corpus | **66** | Includes 7 of the 8 baseline determinations this programme depends on — e.g. `…FINITE-TO-INFINITE-TRANSFORMATION-MASTER-DETERMINATION.md`, `…100-PERCENT-CLOSURE-MASTER-REGISTER.md`, `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` |
| Created this session | **3** | `…EXECUTION-READINESS-DETERMINATION.md` · `…BLOCKER-CLOSURE-IMPLEMENTATION-PLAN.md` · `…BLOCKER-CLOSURE-STATUS-REGISTER.md` |

**Finding of consequence:** the **closure master register and six of the seven baseline determinations on which the entire readiness programme rests are themselves untracked.** The programme's evidential foundation is not under version control. This is the `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` governance void made concrete — determination artifacts have no lifecycle, so nothing required them to be committed.

**Not classified as temporary.** These are cited by name as authority by committed and uncommitted artifacts alike. Treating them as temporary would license deletion of the programme's own evidence base.

### 5.3 Implementation artifact — 2

| Path | Content | Set |
|---|---|---|
| `engine/execution_environment/` | 8 modules — `contract.py` · `discovery.py` · `evidence.py` · `fingerprint.py` · `gate.py` · `model.py` · `__init__.py` · `__main__.py` | CS-1 |
| `engine/tests/unit/test_execution_environment.py` | Test that measures the repair/verify boundary **over the source of `verify.sh`** | CS-1 |

### 5.4 Governed declaration — 1

| Path | Content | Set |
|---|---|---|
| `00-MASTER/UEG-000001/ueg-declaration.json` | The UEG-000001 programme declaration, carrying `separation_of_powers` | CS-1 |

Broken out from *canonical artifact* because its declared class is **R-06 `GOVERNED_DECLARATION`**, not R-08/R-09, and because it is the authority record on which the whole of CS-1 rests.

### 5.5 Temporary artifact — 0 · Unknown — 0

**No untracked path is temporary and none is unknown.** Every one of the 300 resolves to a declared producer, a declared programme, or a named analysis class. Caches and per-run evidence that *would* be temporary (`.ucos/`, `.ucos-verification-evidence/`) are **already excluded** by `.gitignore` and therefore do not appear in the untracked set at all — which is CS-1 working as designed.

---

## 6. Findings Requiring Resolution

### 6.1 F-1 — 228 corpus identities and 83 category codes exist only in an uncommitted ledger

**Severity: HIGH. Class: R-03 `CORPUS_REGISTRATION` — the highest-authority class present in the tree.**

`by_path` 1,264 → 1,492 (+228, zero removals) · `category_seq` 117 → 200 (+83). All 228 registered paths exist. Same failure class as the 140-identifier precedent, at 1.6× scale.

**Consequences:**
- **Bulk discard would destroy 228 permanent corpus identities.** The prohibition in the companion plan §3.6.5 is confirmed by measurement, not asserted.
- **Committing the ledger without the 228 portal pages** leaves 228 registered artifacts whose projections do not exist.
- **Committing the portal pages without the ledger** leaves 228 pages whose identities are unallocated.
- CS-3 is therefore **atomic**, and there is **no cross-class transaction authority** (B-7: *"an authority spanning 7 programmes — none exists"*).

### 6.2 F-2 — PORTAL has three disagreeing authorities

**Severity: MEDIUM. Blocks clean R-04 classification of 238 mutations (10 modified + 228 untracked).**

| Authority | Says |
|---|---|
| `00-BOOK/tools/config.py:451,895` | PORTAL **is generated output**; excluded from registration eligibility |
| `git` | PORTAL **is tracked** — 1,240 files under version control |
| `00-BOOK/DATA/generated-artifact-registry.json` | PORTAL **is not a registered generated path** — 0 of 345 canonical paths |

This is precisely the drift the register's own `why_this_exists` warns of: *"The same fact — 'this path is generated output' — was expressed in three independent places… They drifted."* The register was built to end that drift and **does not cover PORTAL**.

**Until F-2 is resolved by the 00-BOOK owner, the R-04 classification of 238 mutations is contested**, and whether portal pages should be committed at all cannot be answered.

### 6.3 F-3 — One corpus identity allocated to an untracked, non-ASCII-named file

**Severity: MEDIUM.**

Of the 228 newly registered paths, **227 are tracked and exactly 1 is not**:

```
UCOS-Ω∞-FINAL-REPOSITORY-READINESS-DETERMINATION.md
```

Two distinct problems in one row:

1. **A permanent corpus identity was allocated to a path not under version control** — registration ran ahead of the tracked set, and criterion 3 of R-09 (*repository-controlled — tracked by version control*) would exclude it.
2. **The filename carries non-ASCII glyphs (`Ω`, `∞`).** This intersects the identifier alphabet constraints on record — `P-09` extension kind codes `[A-Z][A-Z0-9]{1,7}` and `T-6.4` — and its derived 6-character category code should be inspected for how those glyphs were reduced.

### 6.4 F-4 — BC-1's own test is modified and does not cover the missing predicate

**Severity: MEDIUM.**

`platform/tests/test_mutation_classification.py` is **+3 / −3** with **no `R-09` or `GOVERNED_ANALYSIS` reference**. Whether this is unrelated maintenance or an abandoned attempt at BC-1 is not determinable from the diff. **Its owner must state which**, before BC-1 is attempted on top of it.

### 6.5 F-5 — The programme's evidence base is untracked

**Severity: MEDIUM.**

The closure master register and six of the seven baseline determinations underpinning the readiness verdict are **untracked**. Every conclusion in the readiness determination, the closure plan and this report cites artifacts that could be deleted without a version-control trace.

**Root cause is already on record:** determination artifacts occupy a governance void with no lifecycle authority (`T-15.3`, secondary decision **S-6**). R-09 exists to give this class governance and has no predicate — so **F-5, F-4 and BC-1 are one defect seen from three directions.**

### 6.6 F-6 — `verify.sh` diff variance confirmed

**Severity: LOW — disclosure only.**

Inherited figure **+45 / −0**; measured **+46 / −6**. The measured value is recorded. Reconciliation is BC-6 step 3 and belongs to the gate owner. Because the deletions remove gate self-healing, the variance **may change stage semantics**, which would make the inherited *"4 of 15 stages fail"* figure stale.

---

## 7. Disposition

Dispositions are **analytical recommendations**. This report **approves nothing** and **commits nothing**.

### 7.1 Eligible for commit — 1 set · 1 file

| Item | Basis | Caveat |
|---|---|---|
| **CS-4** — `engine/registry_coverage/declarations.json` (+1/−0) | Single declared array element registering an existing knowledge file. Self-evident purpose, isolated, no identity allocated, no registry projection, no cross-class dependency | Owner confirmation still required. **R-06 `GOVERNED_DECLARATION`** is an owned class |

**Nothing else is eligible**, and the reason is uniform: no other set has a recorded owner, purpose and approval, which is the condition BC-6 A6-1 states.

### 7.2 Requiring review — 2 sets · 15 files + 3 untracked

| Item | Files | Review question |
|---|---|---|
| **CS-1** UEG-000001 | 9 modified + 3 untracked | Purpose is self-stated and coherent, and the set **modifies the gate that measures everything else** and **removes a self-healing path**. Review must confirm: (a) removing `ucos_ensure_venv` breaks no declared stage; (b) the `.gitignore` `.ucos/` rule does not hide something a gate needs to see; (c) Stage 0 is genuinely observe-only; (d) MIP Part 52 admission is accepted by the MIP owner |
| **CS-2** UVI-000001 | 6 modified | Purpose is **not stated** in any diff. Review must establish intent per file, and specifically resolve **F-4**. This set must be settled **before** BC-1 and BC-2 (**R-24 CRITICAL** applies to `selection.py`) |

**Review order is forced:** `.gitignore` (CS-1, file 2) is an **R-02 `EXCLUSION`** mutation and changes the gate's field of view. It must be settled before any measurement is trusted — which is why the companion plan puts G-9 first, and why that ordering is confirmed here rather than restated.

### 7.3 Requiring rollback — 0

**No mutation is recommended for rollback, and none may be rolled back at this step.**

| Candidate | Why rollback is refused |
|---|---|
| CS-3 corpus registration | Rollback would **destroy 228 permanent corpus identities and 83 category codes** (F-1) |
| CS-1 UEG-000001 | Coherent, declared, tested, self-documenting. Rollback would discard an authority record and a working boundary correction |
| CS-2 UVI-000001 | Intent unknown. **Rollback of unknown intent is as unjustified as commit of unknown intent** |
| CS-4 | Trivially correct |
| 300 untracked | Includes the programme's own evidence base (F-5) and 228 identity-bearing projections (F-1) |

**Bulk discard — `git checkout .`, `reset --hard`, `clean -fd`, cross-group `stash` — is refused on measured grounds:** it would destroy 228 identities, an authority declaration, a boundary-measuring test, and the programme's evidence base, and would itself be an unclassified, unowned, unevidenced mutation of exactly the class this programme exists to prevent.

### 7.4 Requiring authority — 1 set · 22 files + 228 untracked + 3 findings

| Item | Authority required | Why |
|---|---|---|
| **CS-3** corpus registration (250 mutations) | **00-BOOK / registry owner**, plus whatever authority governs permanent identity allocation | **R-03 `CORPUS_REGISTRATION`** — 228 permanent identities and 83 category codes. Not an engineering commit |
| **F-2** PORTAL three-way disagreement | **00-BOOK owner** + generated-artifact-registry owner | Three declared authorities disagree. Resolution determines whether 238 mutations are committed, regenerated or excluded |
| **F-3** identity on an untracked non-ASCII path | **Identity / registry owner** | A permanent identity was allocated outside the tracked set |
| **F-5** untracked evidence base | **Lifecycle authority — NOT LOCATED** (secondary decision **S-6**) | Determination artifacts have no lifecycle authority. Committing them is a lifecycle act with no competent decider |
| **CS-1** `.gitignore` | **Exclusion authority** | **R-02 `EXCLUSION`** — changes what every gate can see |
| **CS-1** MIP Part 52 | **MIP owner** | **R-09 `GOVERNED_ANALYSIS`** — and machine-unclassifiable until BC-1 closes |

### 7.5 Disposition roll-up

| Disposition | Sets | Modified files | Untracked paths |
|---|---|---|---|
| Eligible for commit | 1 (CS-4) | **1** | 0 |
| Requiring review | 2 (CS-1, CS-2) | **15** | **3** |
| Requiring authority | 1 (CS-3) + 5 findings | **22** | **228** |
| Requiring rollback | **0** | **0** | **0** |
| Unassigned pending lifecycle authority (F-5) | 1 (U) | 0 | **69** |
| **TOTAL** | | **38** ✔ | **300** ✔ |

---

## 8. What Step 1 Establishes and What It Does Not

### 8.1 Establishes

1. **The baseline is dirty but coherent.** 338 mutations resolve into four change sets and one pre-existing untracked corpus. None is unexplained drift; **zero paths classify as `unknown` or `temporary`**.
2. **74% of the tree is one atomic corpus-registration operation** carrying 228 permanent identities.
3. **Bulk discard is refuted by measurement, not by preference** (F-1).
4. **Review order is forced by evidence:** `.gitignore` first (field of view), then CS-2 (BC-1/BC-2 surfaces), then CS-1, then CS-3 under authority.
5. **Only 1 of 38 modified files is eligible for commit today**, and 0 are eligible for rollback.
6. **F-4, F-5 and BC-1 are one defect.** R-09 `GOVERNED_ANALYSIS` has no predicate; determination artifacts therefore have no governance; so the programme's evidence base went untracked and BC-1's own test drifted unnoticed.

### 8.2 Does not establish

| Not established | Why | Whose act |
|---|---|---|
| Which 4 of 15 `verify.sh` stages fail | The gate was **not executed** — `run` mode mints and emits, only 4 of 29 gates declare a mode, and `verify.sh` itself is modified | **BC-6 step 4**, gate owner |
| Purpose of CS-2's six files | No diff states intent | Owner attribution |
| Whether the 3 lines in `test_mutation_classification.py` relate to BC-1 | Not determinable from the diff | Repository Intelligence |
| Whether PORTAL should be committed | Three declared authorities disagree (F-2) | 00-BOOK owner |
| Whether the 69 untracked analyses should be committed | No lifecycle authority is located (F-5 / S-6) | **Not available in-repo** |
| Any **classification of record** | `classify()` returns ERROR for every subject (BC-1). Every class here is a manual reading | BC-1 closure |

### 8.3 The circularity, stated plainly

**BC-6 Step 1 was to classify every mutation before implementation. Classification is exactly the capability BC-1 exists to restore.** Every class assignment in this report is a hand reading of declared predicates that the machine cannot currently evaluate — and one of the 38 modified files (MIP, file 9) belongs to the very class whose predicate is missing.

This does not invalidate Step 1: the manual reading is sufficient to establish disposition, ordering and the refutation of bulk discard. But it means **Step 1 cannot produce a classification of record**, and the honest sequence is:

> attribute and settle the tree by owner (BC-6 steps 1–3, **manual**) → close BC-1 → **re-classify the settled tree by machine** → then measure the gate.

---

## 9. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ this file |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Tracked files changed by this report | ✅ **0** — still 38 modified, identical set |
| Files committed | ✅ **0** |
| Files restored / deleted | ✅ **0** |
| Registry changes | ✅ **0** — no registry read was followed by a write |
| Certification changes | ✅ **0** |
| Ownership assigned | ✅ **0** — all owners are *probable*, read from declared homes |
| Commits approved | ✅ **0** |
| `git status` delta | ✅ 338 → 339 lines; **the single delta is this new untracked report** |

---

*This report modified no file, committed nothing, restored nothing, deleted nothing, and updated no registry or certification. It assigned no ownership, approved no commit, and resolved no finding. Every class assignment is a manual reading of declared predicates and is not a classification of record, because the classifier returns ERROR for every subject at this baseline. Six findings (F-1…F-6) are recorded and all remain open. BC-6 remains **OPEN** at 0 of 8 acceptance criteria. The single repository mutation is the creation of this file.*

**END REPORT — BC-6 STEP 1 COMPLETE · STEPS 2–6 NOT PERFORMED · STOPPED AFTER REPORT CREATION.**
