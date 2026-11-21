# UCOS-GOV-005 — REPOSITORY GOVERNANCE RECONCILIATION DETERMINATION

Governance Series — Repository-Wide Determination
Class: **Governance Determination** (determination only; not code, not implementation, not a registry, not a new control)
Builds upon: **UCOS-GOV-001**, **UCOS-GOV-002**, **UCOS-GOV-003**, **UCOS-GOV-004**; **REG-AUTO-001**; **UMB-IMP-001**

---

## 1. DOCUMENT AUTHORITY

| Field | Value |
|-------|-------|
| Artifact Identifier | UCOS-GOV-005 |
| Artifact Title | Repository Governance Reconciliation Determination |
| Repository | ABSOLUTE-FOUNDATION |
| Branch | `governance-reconciliation` |
| HEAD | `6b966df` (`EXEC-REG-001: implement autonomous execution register runtime`) |
| Governing Inputs | `00-BOOK/tools/ukb.py`; `00-BOOK/tools/config.py`; `00-BOOK/tools/register.sh`; `00-BOOK/DATA/enforcement-audit.json`; `.gitignore`; `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-AUTOMATIC-ARTIFACT-REGISTRATION-STANDARD.md`; `00-BOOK/MASTER-BOOK/UMB-IMP-001-AUTOMATIC-REGISTRATION-AND-ENFORCEMENT-REALIZATION.md` |

**Scope discipline.** This artifact determines the root causes of repository registration drift and designs the permanent correction architecture. It creates exactly one file; it modifies, renames, and deletes nothing; it implements nothing. It authorizes no code change by itself — it specifies the exact change sequence a subsequent implementation program must execute. All conclusions cite repository evidence (file + line, or audit `seq`).

**Method note.** Per mission mandate, the audit is **not assumed correct**. Every engine (repository, eligibility, classification, registration, audit) was inspected against its source. The determination distinguishes true positives (genuinely unregistered governance artifacts) from false positives (environment artifacts that were never repository artifacts).

---

## 2. EXECUTIVE DETERMINATION OBJECTIVE

Determine, from repository evidence only, **why repository registration drift occurs**, **which engine(s) are defective**, and **what permanent, rule-based correction eliminates the drift for all future repository growth**. The target end-state is a self-consistent governance system in which, at every commit and at every repository size:

```
registered == eligible     unclassified == 0     invalid == 0     violations == 0     audit == PASS
```

and that identity holds **without** hardcoded file exceptions, manual whitelists, artifact-specific patches, suppression toggles, or manual registration.

---

## 3. SYSTEM UNDER DETERMINATION (ENGINE MAP)

| Engine | Implementation site | Function |
|--------|--------------------|----------|
| **Eligibility** | `00-BOOK/tools/ukb.py :: _iter_files()` (≈607–617) | Enumerates on-disk files that count as repository artifacts. |
| **Classification** | `ukb.py :: classify()` (476–509) + `config.py :: CLASSIFY_RULES` (75–217), `DEFAULT_CLASS` (219) | Maps each eligible path to (program, category, volume). |
| **Registration** | `ukb.py :: cmd_build()` (664+), `allocate()` (632–654); catalog `00-BOOK/DATA/artifacts.json` | Append-only allocation of a Universal ID per eligible+classified path. |
| **Audit / Enforcement** | `ukb.py :: cmd_enforce()` (1551–1642), `_enforcement_audit()` (1529–1548); log `00-BOOK/DATA/enforcement-audit.json` | Four gates: eligibility · validity · classification · registration. |
| **Transaction** | `00-BOOK/tools/register.sh` | Orders enforce --pre → build → sync/twin/portal/validate/certify → enforce (post). |
| **Ignore authority** | `.gitignore` (repo root) | Canonical declaration of non-repository (environment/generated) paths. |

Governing law (as authored): *"Artifact Creation = Artifact Registration"* (REG-AUTO-001 §7 Atomic Creation Law), enforced by two UMB-IMP-001 gates bracketing the transaction (`register.sh` Phase 0 and Phase 9).

---

## 4. AUDIT-LOG FORENSICS (enforcement-audit.json, 53 runs)

The log is a faithful, deterministic recorder of what the engines computed. Its arithmetic is trustworthy; its **inputs** are not. The trajectory isolates the exact regression point.

| Phase | `seq` window | eligible | registered | Behaviour |
|-------|-------------|----------|-----------|-----------|
| **A — steady state** | 1–37 | 290 → 299 | tracks eligible after each post cycle | Only book-corpus `.md`/`.docx` artifacts. Each cycle a single new `00-BOOK/MASTER-BOOK/UMB-*` doc is pre-flagged then registered (parity restored post). PASS is normal. A persistent *advisory* unclassified set (APPLICATION-*, INFRASTRUCTURE-*, root `.docx`) is present but tolerated. |
| **B — flag divergence** | 26, 33, 34 | 296–298 | = eligible | Same unclassified set, but result flips to **FAIL** with the unclassified items promoted to `violations`. No repository change caused this — only the `--strict` invocation flag differs (see §7.4). First determinism defect. |
| **C — eligibility explosion** | 38 → 53 | 300 → **358** | frozen at **299** | `adr/*.md` (seq 38–39), then `.ec1-venv/**` site-packages, `.pytest_cache/README.md`, `*.egg-info/*.txt`, `determinism-evidence/*.json`, `engine/**/EPIC-*-COMPLETION-REPORT.md`, `platform/**/EC2-*-COMPLETION-REPORT.md`, `engine/determinism/blueprints/*.json`, and `02-MASTER/APP-*`, `UCOS-GOV-*`, `UCOS-EXEC-*` all enter `eligible`. Every run is **FAIL**; registration never advances. |

**Decisive observation.** At `seq 53` (latest): `eligible = 358`, `registered = 299`, a 59-artifact gap. Of the 59 unregistered/violating paths, roughly **33 are environment/generated files** that must never have been eligible (`.ec1-venv/**` ×25, `.pytest_cache/README.md`, `*.egg-info/*.txt` ×5, `determinism-evidence/*.json` ×2), and the remainder are **genuine governance/implementation documents** (`02-MASTER/APP-001/002`, `UCOS-GOV-001..004`, `UCOS-EXEC-001..003`, `adr/0000..0001`, seven `engine/*/EPIC-*-COMPLETION-REPORT.md`, six `platform/*/EC2-*-COMPLETION-REPORT.md`, `blueprints/BP-DATA-0001.json`) that are legitimately unclassified because no rule covers their family.

**Why registration froze at 299.** `register.sh` Phase 0 runs `ukb.py enforce --pre`; in PRE mode any unregistered file that is unclassified **or** invalid is a hard violation → the script `fail`s (exit 4) **before** Phase 1 (`build`). Because the environment artifacts are both unregistered and unclassified, the pre-gate fails on every run, the transaction aborts, `build` never executes, and no new Universal ID is ever allocated. The registry is therefore *frozen* at its last-good count (299) while the filesystem — and thus `eligible` — grows without bound. This is the mechanism of "permanent drift."

---

## 5. PRIMARY FAULT DETERMINATION — WHICH ENGINE IS WRONG?

> The audit is not presumed correct. Each candidate is adjudicated on evidence.

| Candidate | Verdict | Evidence |
|-----------|---------|----------|
| **Repository is wrong** | **NO** | The repository correctly declares environment/generated paths as non-artifacts in `.gitignore` (`.ec1-venv/`, `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `coverage.xml`, `build/`, `dist/`, `__pycache__/`). The physical tree is well-formed; the offending files are correctly untracked. |
| **Eligibility engine is wrong** | **YES — PRIMARY** | `_iter_files()` (ukb.py 607–617) walks the raw filesystem (`os.walk(REPO)`) and filters only by `C.EXCLUDE_DIR_PREFIXES` (config.py 556–567) and `C.INCLUDE_EXTENSIONS` (`.md/.txt/.docx/.json`, config.py 570). The denylist enumerates 9 hand-picked directories and **omits every entry already present in `.gitignore`**. Eligibility therefore contradicts the repository's own canonical ignore authority. |
| **Classification engine is wrong** | **YES — SECONDARY (incomplete)** | `classify()` (ukb.py 476–509) matches ordered `CLASSIFY_RULES` then a metadata clean-code fallback then `DEFAULT_CLASS = ("OTHER","MISC",...)` (config.py 219). No rule covers `^02-MASTER/APP-`, `^02-MASTER/UCOS-GOV-`, `^02-MASTER/UCOS-EXEC-`, `^adr/`, `^engine/`, `^platform/`; those families fall to OTHER/MISC = unclassified. The taxonomy is not total. |
| **Registration engine is wrong** | **NO (correct but starved)** | `allocate()` (ukb.py 632–654) is idempotent and append-only, keyed by path; `cmd_build()` registers exactly the eligible+classified set. It behaves correctly — it simply never runs because the pre-gate aborts the transaction (§4). The registration gap is a **cascade**, not an independent defect. |
| **Audit engine is wrong** | **YES — TERTIARY (non-deterministic gate)** | `cmd_enforce()` (1551–1642): in POST mode `unclassified` is a violation only when `--strict` is passed. The same repository state yields PASS or FAIL depending on an invocation flag (audit `seq 26/33` FAIL vs `seq 28` PASS). The audit result is not a pure function of repository state. Additionally, walking a mutable filesystem makes the audit non-repeatable across environments. |
| **Governance model is wrong** | **YES — ROOT (incomplete taxonomy)** | The artifact-type model was defined for the book corpus and never enumerated APP/GOV/EXEC determinations, ADRs, completion reports, evidence, or engineering/platform document families as first-class types — nor did it formally declare environment/generated outputs as non-artifacts. Both the eligibility and classification defects are downstream of this incompleteness. |

**Combined determination.** The failure is a **combination**, with a clear causal spine:
**incomplete governance model → over-broad eligibility (primary trigger) → classification gaps (secondary) → registration starvation (cascade) → non-deterministic audit (amplifier).**

---

## PART 1 — ELIGIBILITY ROOT CAUSE ANALYSIS

**Expected behaviour.** Eligibility must enumerate exactly the **repository artifacts** — the version-controlled, human-authored corpus — and nothing else. Environment, build, cache, and generated-evidence files are not repository artifacts.

**Actual behaviour.** `_iter_files()` performs `os.walk(REPO)` over the entire working directory, subtracting only `C.EXCLUDE_DIR_PREFIXES` and keeping any file whose extension is in `C.INCLUDE_EXTENSIONS`. Because a Python virtual environment (`.ec1-venv/`), build metadata (`*.egg-info/`), test cache (`.pytest_cache/`), and generated evidence (`determinism-evidence/`) all contain `.txt`/`.json`/`.md` files and are **absent from the denylist**, they are enumerated as eligible artifacts.

**Constitutional behaviour.** REG-AUTO-001 governs *"artifacts,"* not *"every byte on disk."* The repository already publishes the authoritative artifact/non-artifact boundary in `.gitignore`. Constitutionally, eligibility must be derived from **version control** (the tracked set / ignore authority), which is the single source of truth for "what is part of the repository."

**Root cause (ELIG-RC-1).** *Eligibility is defined by a raw filesystem walk gated by a hand-maintained directory denylist that does not honor `.gitignore` and does not restrict to git-tracked files.* Every new environment/generated directory silently becomes eligible until someone manually appends it to `EXCLUDE_DIR_PREFIXES` — the definition of unbounded drift.

**Evidence.**
- `ukb.py` 607–617 (`os.walk` + `EXCLUDE_DIR_PREFIXES` + `INCLUDE_EXTENSIONS`).
- `config.py` 556–567 (denylist: `.git/`, `.github/`, `.kiro/`, `00-BOOK/tools|DATA|REGISTRIES|CONTROL-TOWER|VOLUMES|PORTAL/` — **no** `.ec1-venv/`, `.pytest_cache/`, `*.egg-info/`, `determinism-evidence/`).
- `.gitignore` already ignores all leaking families → the correct boundary exists but is not consulted.
- `enforcement-audit.json` `seq 40` (eligible jumps to 328 as `.ec1-venv/**` appears) through `seq 53` (358).

---

## PART 2 — CLASSIFICATION GAP ANALYSIS

**Symptom.** Valid governance/implementation documents appear as unclassified (OTHER/MISC).

| Family (examples) | Current category | Correct category | Missing rule/definition |
|-------------------|------------------|------------------|-------------------------|
| `02-MASTER/APP-001/002` | OTHER/MISC | Application-foundation (APP) | No `^02-MASTER/APP-` rule |
| `02-MASTER/UCOS-GOV-001..005` | OTHER/MISC | Governance determination (GOV) | No `UCOS-GOV-` rule |
| `02-MASTER/UCOS-EXEC-001..003` | OTHER/MISC | Execution determination (EXEC) | No `UCOS-EXEC-` rule |
| `adr/0000..0001*.md` | OTHER/MISC | Architecture Decision Record (ADR) | No `^adr/` rule |
| `engine/**/EPIC-*-COMPLETION-REPORT.md` | OTHER/MISC | Engineering completion report | No `^engine/` rule |
| `platform/**/EC2-*-COMPLETION-REPORT.md` | OTHER/MISC | Platform completion report | No `^platform/` rule |
| `engine/determinism/blueprints/*.json` | OTHER/MISC | Engineering source fixture | No `^engine/` rule (or exclude as data) |

**Structural cause (CLASS-RC-1).** `CLASSIFY_RULES` is a curated allowlist of path/name regexes; `DEFAULT_CLASS` is a dead-end bucket (OTHER/MISC) rather than a *deterministic* category. Any artifact family not explicitly enumerated is unclassified. The catalogue was extended reactively (see the appended `^09-PLATFORM/`, `^10-DATA/`, `^11-SERVICE/`, `^12-APPLICATION/`, `^13-INFRASTRUCTURE/` rules and the F-6 hygiene block, config.py 156–217), which proves the model requires a manual rule per new tree — a recurring-symptom pattern, not a cause fix.

**Root cause.** *The classification taxonomy is not total: there is no deterministic mapping for every tracked artifact, so new artifact families fall to a dead-end OTHER/MISC bucket instead of a real, path-derivable category.*

**Missing category definitions.** GOV (governance determination), EXEC (execution determination), ADR (architecture decision record), and an engineering/implementation-document category (completion reports + fixtures) are not first-class categories in the model.

---

## PART 3 — REGISTRATION GAP ANALYSIS

**Symptom.** `registered (299) < eligible (358)`.

**Findings.**
1. **Missing registrations are not the disease.** `registered` is frozen because `register.sh` Phase 0 (`enforce --pre`) fail-closes on the unclassified/invalid environment artifacts and aborts before `build` (register.sh Phase 0 → `fail ... 4`). The registration engine is never given the chance to allocate.
2. **No invalid registrations.** Across all 53 runs `invalid == []` at the registry level; `allocate()` remains append-only and duplicate-free (ukb.py 632–654; validated by `cmd_validate`, 1473–1526).
3. **Category-mapping defect (cascade from Part 2).** Even if the pre-gate were reached, `build` would attempt to register environment files (they are eligible) and would classify governance docs as OTHER/MISC — so parity could only be "achieved" by registering garbage. Correct parity is impossible until eligibility and classification are fixed.
4. **Registration authority is sound.** The atomic transaction, idempotency, append-only ledger, and drift guard are correctly designed (register.sh; REG-AUTO-001 §7). No lifecycle defect exists in the registrar itself.

**Root cause (REG-RC-1).** *The registration count is a pure downstream function of eligibility ∩ classification; it is starved because the pre-registration gate fail-closes on inputs that should never have been eligible. Fix the inputs and registration parity is automatic — no manual registration is required or permitted.*

---

## PART 4 — GOVERNANCE MODEL GAP ANALYSIS

Is each family a first-class artifact type in the current model?

| Artifact type | First-class today? | Determination |
|---------------|--------------------|---------------|
| **APP** artifacts | Partial | `^12-APPLICATION/ → APP` exists; `02-MASTER/APP-00x` has no rule. **Must be first-class** (single APP program spanning both locations). |
| **GOV** artifacts | **No** | `UCOS-GOV-00x` unclassified. **Must be first-class** — governance determinations are the highest-authority documents in the repo. |
| **EXEC** artifacts | **No** | `UCOS-EXEC-00x` unclassified. **Must be first-class** — execution determinations authorize implementation. |
| **Completion reports** | **No** | `engine/**` and `platform/**` `*-COMPLETION-REPORT.md` unclassified. **Must be first-class** — they are the certified evidence of epic completion. |
| **Evidence artifacts** | **No** | `determinism-evidence/*.json` currently *leaks into* eligibility. Determination: **NOT a first-class registerable artifact** — it is *generated* output, regenerated each run, and must be declared a **non-artifact** (excluded via the ignore authority), exactly like `coverage.xml`. |
| **ADR artifacts** | **No** | `adr/*.md` unclassified. **Must be first-class** — ADRs are governed decision records (ADR-0001 is already cited as a CI prerequisite by GOV-003). |

**Constitutional correction.** The governance model must (a) enumerate GOV, EXEC, ADR, completion-report, and engineering/platform-document families as first-class categories with stable identifier namespaces and thematic volumes, and (b) formally define *environment* and *generated* outputs as **non-artifacts** whose authoritative boundary is version control (`.gitignore`/tracked set). Until both are done, the taxonomy is incomplete and drift is structurally guaranteed.

---

## PART 5 — PERMANENT GOVERNANCE CORRECTION ARCHITECTURE

Design principles: reuse existing canon; rule-based only; no hardcoded file names; scales to unbounded future growth; preserves determinism, auditability, and append-only identity.

### 5.1 Eligibility = Version-Control Authority (structural, permanent)
Redefine eligibility as **the set of git-tracked files** (equivalently: files not matched by `.gitignore`), then apply the existing `INCLUDE_EXTENSIONS` and any *intentional* corpus-internal `EXCLUDE_DIR_PREFIXES` (e.g. generator machinery under `00-BOOK/tools|DATA|REGISTRIES|…`). One canonical rule replaces the hand-maintained denylist. Consequences, with zero per-file config, forever:
- `.ec1-venv/**`, `*.egg-info/**`, `.pytest_cache/**`, `.ruff_cache/**`, `coverage.xml`, `.coverage`, `build/`, `dist/`, `__pycache__/` → excluded (already gitignored).
- `determinism-evidence/**` and editor lock files `~$*.docx` → excluded (untracked).
- Any *future* environment/generated directory that is gitignored/untracked → automatically excluded.

This is the single highest-leverage correction: it collapses `eligible` from 358 back to the true artifact count and removes ~33 false positives at `seq 53` without naming any of them.

### 5.2 Classification Totality = Deterministic Path-Derived Catch-All (structural, permanent)
Replace the OTHER/MISC dead-end with a **deterministic derive-from-path final rule**: any tracked artifact not matched by a curated rule is classified by its top-level directory / identifier prefix into a real category+volume. Curated `CLASSIFY_RULES` remain first (append-only; existing Universal IDs are preserved because `allocate()` is keyed by path). Effect: `unclassified` is structurally driven to **0** for every present and future tree — no per-tree rule is ever again required to avoid a dead end.

Additionally append (append-only, first-match-preserving) the explicit family rules that give the curated families their intended, stable namespaces:
`^adr/ → ADR`; `UCOS-GOV- → GOV`; `UCOS-EXEC- → EXEC`; `^02-MASTER/APP- → APP`; `^engine/ …-COMPLETION-REPORT → ENG`; `^platform/ …-COMPLETION-REPORT → PLT`.

### 5.3 Governance-Model Completion (constitutional)
Enumerate GOV, EXEC, ADR, completion-report, and engineering/platform-document categories as first-class types (mapped to existing volumes; nothing renumbered), and record the constitutional definition: **repository artifact ≡ tracked, human-authored corpus file of an included type; environment/generated output ≡ non-artifact bounded by version control.**

### 5.4 Deterministic Audit (correctness)
- Make eligibility a pure function of the tracked set at a commit — removing environment/timing variance (whether the venv exists, whether tests/evidence ran).
- Retire the `--strict` divergence: adopt a **single fixed gate policy**. Because §5.2 guarantees `unclassified == 0`, the classification gate can be *always enforced* safely and deterministically. The audit result becomes a pure function of repository state alone.
- Retain the existing stable ordering (`sorted(...)`) and idempotent de-dup (`_enforcement_audit`, 1529–1548).

### 5.5 Registration by Construction (cascade closes automatically)
With §5.1 (clean eligible) and §5.2 (total classification), the unmodified idempotent `allocate()`/`cmd_build()` registers exactly `eligible ∩ classified`. Parity `registered == eligible` follows by construction on the next successful transaction. **No manual registration, no whitelist, no per-artifact patch.**

### 5.6 Invariance proof sketch (future-growth guarantee)
For any future commit C: `eligible(C) = tracked(C) ∩ includedTypes` (pure fn of C); `classified(C) = eligible(C)` (totality); `registered(C) = classified(C)` (idempotent build) ⇒ `registered == eligible ∧ unclassified == 0 ∧ violations == 0`. New epics, applications, and programs add tracked files that are auto-eligible, auto-classified, and auto-registered; new tools/venvs/evidence are gitignored and auto-excluded. The identity is preserved for all C. ∎

---

## PART 6 — IMPLEMENTATION PACKAGE

### 6.1 Root Cause Summary
| ID | Root cause | Engine | Severity |
|----|-----------|--------|----------|
| ELIG-RC-1 | Filesystem walk + hand-maintained denylist ignores `.gitignore`/tracked set | Eligibility | Primary trigger |
| CLASS-RC-1 | Non-total taxonomy; OTHER/MISC dead-end; per-tree manual rules | Classification | Secondary |
| REG-RC-1 | Registration starved by pre-gate fail-close on illegitimate inputs | Registration (cascade) | Consequence |
| AUD-RC-1 | `--strict`-dependent, filesystem-dependent gate → non-deterministic/non-repeatable | Audit | Amplifier |
| GOV-RC-1 | Incomplete artifact-type model; env/generated not declared non-artifacts | Governance model | Root |

### 6.2 Eligibility Corrections
Redefine eligibility as the git-tracked set honoring `.gitignore`; keep `INCLUDE_EXTENSIONS` and only *intentional* corpus-internal excludes. (Design §5.1.)

### 6.3 Classification Corrections
Introduce a deterministic derive-from-path catch-all replacing OTHER/MISC; append family rules for ADR/GOV/EXEC/APP/completion-reports. (Design §5.2.)

### 6.4 Registration Corrections
None to the registrar. Parity restored by construction once 6.2–6.3 land. (Design §5.5.)

### 6.5 Governance Model Corrections
Add first-class categories (GOV, EXEC, ADR, completion-report, ENG/PLT-doc); constitutionally define non-artifacts by version control. (Design §5.3.)

### 6.6 Required Code Changes (exact sites; append-only / structural)
1. `00-BOOK/tools/ukb.py :: _iter_files()` — replace `os.walk` enumeration with the git-tracked set (honor `.gitignore`); retain extension + intentional-exclude filters.
2. `00-BOOK/tools/ukb.py :: classify()` — add deterministic path-derived final classifier before `DEFAULT_CLASS`.
3. `00-BOOK/tools/config.py :: CLASSIFY_RULES` — append (append-only) `^adr/`, `UCOS-GOV-`, `UCOS-EXEC-`, `^02-MASTER/APP-`, `^engine/…COMPLETION-REPORT`, `^platform/…COMPLETION-REPORT` rules.
4. `00-BOOK/tools/ukb.py :: cmd_enforce()` — remove `--strict` divergence; enforce a single fixed classification policy (now safe because unclassified→0).
5. `00-BOOK/tools/config.py` — add first-class category/volume definitions for the new families (no renumbering; map to existing volumes).

### 6.7 Required Catalog Changes
None hand-edited. `00-BOOK/DATA/artifacts.json` and all synchronized registers regenerate deterministically via `register.sh` (build → sync → twin → portal → validate → certify). Regeneration is the *only* sanctioned way the catalog changes.

### 6.8 Required Policy Changes
- `.gitignore` (optional hardening): add `determinism-evidence/` so generated evidence is explicitly declared non-artifact (already excluded as untracked; this makes intent explicit).
- Enforcement policy: unclassified is a *gated* (not advisory) condition under the single fixed policy.

### 6.9 Required Migration Actions
1. Land code/config changes (6.6).
2. Run `00-BOOK/tools/register.sh` once: pre-gate now passes (clean eligible + total classification); `build` allocates Universal IDs for the newly-classified genuine artifacts (APP/GOV/EXEC/ADR/completion reports); post-gate asserts parity.
3. Commit the regenerated `DATA/REGISTRIES/CONTROL-TOWER/PORTAL` (drift guard `--guard` must be clean).
4. No history rewrite; no ID renumbering (allocate is path-keyed).

### 6.10 Validation Procedure
| Check | Command / evidence | Expected |
|-------|--------------------|----------|
| Eligibility clean | `ukb.py enforce --pre` | 0 env artifacts in `eligible`; no `.ec1-venv/**`, `*.egg-info/**`, `.pytest_cache/**`, `determinism-evidence/**` |
| Classification total | enforce report | `unclassified == 0` |
| Parity | `ukb.py enforce` (post) | `registered == eligible` |
| Validity/integrity | `ukb.py validate` | append-only ledger, no dup IDs/pages, referential integrity OK |
| Determinism | run enforce twice (with/without former `--strict`), and after a fresh `pip install`/test run | identical `result`, `eligible`, `violations` regardless of flags or environment |
| Drift gate | `register.sh --guard` | exit 0, registers in sync |
| Determinism harness (unrelated but adjacent) | `python -m engine.determinism.reproduce BP-DATA-0001` | `byte_identical=True` |

### 6.11 Regression Prevention Controls
- **Structural, not enumerative:** eligibility bound to version control means no future env directory can leak (no denylist to forget).
- **Total classification:** no future tree can produce OTHER/MISC.
- **Single fixed gate policy:** audit result cannot diverge on invocation flags.
- **Existing CI/commit gates retained:** `ec1-ci.yml`, determinism gate, and `register.sh --guard` pre-commit hook continue to fail closed on any real drift.
- **Append-only invariants preserved:** `allocate()` path-keyed identity, de-duped audit log.

### 6.12 Final Readiness Determination
- Eligibility determination: **CORRECTABLE — root cause isolated (ELIG-RC-1).**
- Classification determination: **CORRECTABLE — root cause isolated (CLASS-RC-1).**
- Registration determination: **CORRECT ENGINE — parity restored by construction (REG-RC-1 is a cascade).**
- Governance model: **COMPLETABLE via first-class type enumeration (GOV-RC-1).**
- Determinism: **ACHIEVABLE via pure inputs + single fixed gate policy (AUD-RC-1).**
- No hardcoded exceptions, no manual registration, no suppression required by the design.

**GOV-005 DETERMINATION:** the repository governance failure is **fully diagnosed and permanently correctable** by the rule-based architecture in Part 5, executed via the sequence in Part 6. Upon that execution the invariant **`registered == eligible ∧ unclassified == 0 ∧ invalid == 0 ∧ violations == 0 ∧ audit == PASS`** holds at HEAD and remains valid for all future repository growth.

**Status of this artifact:** determination only — no code, catalog, policy, or registry has been modified by GOV-005. Implementation is authorized to a subsequent execution program under the Part 6 sequence.

---

## 7. APPENDIX — EVIDENCE INDEX

| Ref | Evidence |
|-----|----------|
| E1 | `00-BOOK/tools/ukb.py` 607–617 — `_iter_files()` `os.walk` + denylist + extensions |
| E2 | `00-BOOK/tools/config.py` 556–567 — `EXCLUDE_DIR_PREFIXES` (omits gitignored dirs); 570 — `INCLUDE_EXTENSIONS` |
| E3 | `.gitignore` — already ignores `.ec1-venv/`, `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `coverage.xml`, `build/`, `dist/` |
| E4 | `00-BOOK/tools/ukb.py` 476–509 — `classify()`; `config.py` 75–217 `CLASSIFY_RULES`, 219 `DEFAULT_CLASS` |
| E5 | `00-BOOK/tools/ukb.py` 1551–1642 — `cmd_enforce()` PRE/POST + `--strict` divergence |
| E6 | `00-BOOK/tools/register.sh` Phase 0 (`enforce --pre` fail 4) → transaction abort before Phase 1 build |
| E7 | `00-BOOK/tools/ukb.py` 632–654 — `allocate()` idempotent, path-keyed, append-only |
| E8 | `00-BOOK/DATA/enforcement-audit.json` — seq 1–37 steady (290–299); seq 26/33/34 flag-driven FAIL; seq 38 adr; seq 40 eligible 328; seq 53 eligible 358 / registered 299 |
