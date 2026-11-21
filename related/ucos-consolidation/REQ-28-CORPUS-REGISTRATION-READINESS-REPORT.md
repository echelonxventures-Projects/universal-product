# REQ-28 — 192-DOCUMENT CORPUS REGISTRATION READINESS REPORT

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-22
**Phase:** 7B — **preparation only. No identity minted. No `register.sh --mint` executed. No mutation performed.**
**Requirement:** REQ-28 — *the 192-document corpus-registration population is registered.* Status at entry: **OPEN GAP**.
**Authority that would act:** `REG-AUTO-001` → `00-BOOK/tools/register.sh` → `ukb.py build --mint` (`CORPUS_REGISTRATION`, per `00-BOOK/DATA/mutation-governance-boundary.json`).

---

## 1 — Readiness verdict

### **NOT READY TO MINT.** The population is exact and verified; the authority mapping is not.

| Precondition | State |
|---|---|
| Population enumerated exactly | ✅ **192**, individually listed in §4 |
| Population eligibility verified | ✅ all 192 are version-controlled; boundary is a pure function of the commit |
| Population disjoint from VCS-unbound candidates | ✅ intersection = **0** |
| Irreversible footprint quantified | ✅ §5 |
| Artifact → Owner → **Authority** → Identity → Lifecycle mapped | ❌ **172 of 192 have no resolvable authority** (§3.1) |
| Repository's authority resolver is sound | ❌ **defect found** — 117 tracked files repo-wide are misclassified (§3.2) |

Two blockers, one of them a live correctness defect in a module certified earlier this
session. Both are stated with reproduction below. **Registration must not proceed until
§3.2 is fixed**, because minting now would bind 192 permanent identities to a decision
whose authority column is either empty or wrong.

---

## 2 — Population determination

### 2.1 Measured, not assumed

```
$ python3 00-BOOK/tools/ukb.py enforce --pre
  eligible on-disk artifacts : 1425
  registered (in registers)  : 1233
  unregistered eligible      :  192
  unclassified (OTHER/MISC)  :    0 (GATED)
  invalid (unreadable/empty) :    0
  awaiting VCS binding       :   25 (REPORTED — not repository artifacts until `git add`)
ENFORCEMENT PASSED
```

Independently recomputed against `ukb._iter_files()` and
`00-BOOK/DATA/artifacts.json`: `1425 − 1233 = 192`. Exact match.

### 2.2 Eligibility boundary — and why the 25 are *not* part of this population

`ukb._repo_artifact_paths()` defines eligibility as **`git ls-files --cached
--exclude-standard`** (tracked ∪ staged), intersected with `INCLUDE_EXTENSIONS`, minus the
corpus-internal generator homes (`00-BOOK/tools|DATA|REGISTRIES|CONTROL-TOWER|VOLUMES|PORTAL`).
Untracked-but-unignored files are **deliberately not eligible** (B-01c): *"the append-only
identity ledger can no longer mint PERMANENT identities for files the repository does not
contain."*

Verified this pass:

- all 192 are present in `--cached` → **`True`**
- `set(_vcs_unbound_candidates()) ∩ set(192)` → **`[]`** (empty)

The 25 "awaiting VCS binding" are a **disjoint** advisory set. They include this session's
own untracked determination reports. They are outside REQ-28's population and must not be
folded into it.

> **Consequence for this report itself:** this file and its siblings are untracked at
> authoring time, so they land in the *25-set*, not the *192-set*. `git add`-ing them before
> minting would silently grow the population past 192 and invalidate the decision's stated
> count. **Author first, register second, and re-run `enforce --pre` immediately before
> minting to confirm the number is still 192.**

### 2.3 Population profile

| Dimension | Distribution |
|---|---|
| Extension | 189 `.md`, 3 `.json` |
| Location | 178 repository root, 11 `adr/`, 3 `engine/` |
| Version control | 192 tracked/staged, 0 untracked |
| `ukb` classification | 192 resolved to a real `(program, category, volume)` — **0 unclassified** |

The 3 non-markdown members are `engine/lineage/families.json`,
`engine/lineage/memory-layers.json`, `engine/registry_coverage/declarations.json` — declared
data consumed by `engine.lineage.memory` (REQ-32) and `engine.registry_coverage`, not prose.

---

## 3 — Blocking findings

### 3.1 Blocker 1 — 172 of 192 have no resolvable governing authority

The directive requires the decision to map **Artifact → Owner → Authority → Identity
requirement → Lifecycle**. The repository's own authority resolver for a path is
`platform/repository_intelligence/mutation_classification.classify()`, governed by
`00-BOOK/DATA/mutation-governance-boundary.json` (REQ-38/REQ-39, both certified this
session). Run over the population:

| Mutation class | Count | Governing authority |
|---|---|---|
| **UNRESOLVED** (fail-closed) | **172** | — none — |
| `AUTHORED_DOCUMENT` | 19 | the authority the artifact declares of itself |
| `REPOSITORY_STATE` | 1 | `UCOS-RIB-001` GATE-02 / GATE-12 — **and this one is wrong**, see §3.2 |

Cause, isolated per criterion across the 189 markdown members
(`authored_document_checks()`):

| Failing criterion | Count |
|---|---|
| `self-declared-authority` | **170** |
| `repository-controlled` | 1 |

`_r08_authored_document` requires **all five** membership criteria. 170 of these documents
declare neither an `Authority:` nor a `Deciders:` field in their opening 40 lines, so Class 7
correctly refuses them and `classify()` falls through to its terminal and **fails closed** —
which is the designed behaviour, not a bug.

**This is not a registration blocker in `ukb`'s sense** — `ukb enforce` gates on its own
`(program, category, volume)` classifier, which is total and reports 0 unclassified.
Registration would succeed. It is a blocker on **writing the decision truthfully**: a
`CEP-002 Article 28` decision that must name an authority per artifact cannot do so for 172
of them.

Two lawful resolutions, in order of preference:

1. **The decision assigns authority to the population as a whole.** REQ-28's obligation is
   *corpus registration*, whose authority is unambiguously `REG-AUTO-001`. The decision
   names `REG-AUTO-001` as the registering authority for all 192 and records that per-artifact
   *mutation* authority remains separately unresolved for 172 — a **disclosed, scoped
   residual**, not a silent omission. Cheapest, honest, does not touch 170 files.
2. **Add self-declared `Authority:` headers to the 170 documents.** Correct in principle,
   but it is a 170-file edit that changes each document's `content_sha256`, and it presumes
   an authority for each that no one has yet determined. Not recommended as a precondition
   for registration; recommended as separate follow-on work.

### 3.2 Blocker 2 — a live defect misclassifies 117 tracked files repo-wide

**`platform/repository_intelligence/mutation_classification.py:139-146`**

```python
out = subprocess.run(["git", "ls-files"], cwd=self.root, capture_output=True, text=True, ...)
return frozenset(line for line in out.stdout.splitlines() if line)
```

`git ls-files` **C-quotes and octal-escapes any path containing non-ASCII bytes** unless
`-z` or `-c core.quotePath=false` is used. This repository has **117 tracked files whose
names contain `Ω∞`** (the `02-MASTER/`, `03-CATALOGS/`, `04-REFERENCE/`, `05-GENERATION/`,
`06-IMPLEMENTATION/`, `07-ENGINEERING/` constitution and catalog families, plus
`00-BOOK/CONTROL-TOWER/` pages). Every one of them arrives in `Repository.tracked` as
`"00-BOOK/...UCOS-\316\251\342\210\236-..."` — a quoted, escaped string that never equals
the real path.

Measured:

```
tracked files with non-ASCII names            : 117
how many appear in repo.tracked as-is         :   0
```

Because `_r01_repository_state` (the **first** rule in precedence order) returns `True` for
any existing path **not** in `repo.tracked`, all 117 are claimed by `REPOSITORY_STATE`
before any later rule is consulted:

| | Current (defective) | With a `quotePath`-corrected tracked set |
|---|---|---|
| `REPOSITORY_STATE` | **117** | 0 |
| `AUTHORED_DOCUMENT` | 0 | 19 |
| `UNRESOLVED` (fail-closed) | 0 | 98 |

**Impact:**

- 117 constitutional and reference documents are currently governed, on paper, by
  `UCOS-RIB-001` GATE-02/GATE-12 (repository integrity / filesystem contamination) instead
  of by their own declared authority. That is a **wrong** authority, not a missing one —
  strictly worse than fail-closed.
- `_r02_exclusion` (line 243) and `_r06_governed_declaration` both consult `repo.tracked`
  and are affected identically.
- REQ-38's certification claim — *"`classify()` is data-driven, fail-closed to `UNRESOLVED`"*
  — currently reports **0 unresolved** for these files only because the defect routes them
  into a class before the fail-closed terminal is reached. The stated evidence is real; the
  number it produces is not what a correct run would produce.
- One member of REQ-28's own population is affected:
  `UCOS-Ω∞-FINAL-REPOSITORY-READINESS-DETERMINATION.md`, the single
  `repository-controlled` failure in §3.1.

**Not caught by tests.** `platform/tests/test_mutation_classification.py` — **44 passing**,
re-executed this pass — exercises `Repository` through `_overrides["tracked"]` with
ASCII-only fixtures, so the real `git ls-files` path is never driven against a non-ASCII
name.

**Fix:** `["git", "-c", "core.quotePath=false", "ls-files", "-z"]`, split on `\0`. One line,
plus a regression test with a non-ASCII filename fixture.

> **This is a genuine bug found during discovery, outside REQ-28's nominal scope.** It is
> reported here rather than fixed, because Phase 7B is preparation-only and because it
> materially changes what a REQ-28 decision may truthfully assert. It also means REQ-38 and
> REQ-39 should be reviewed before any final certification claim.

### 3.3 Evidence-accuracy correction

`UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` REQ-39 cites *"13 new tests (53
total in `test_mutation_classification.py`)"*. Direct count:
`grep -c "^def test_"` → **44**; `pytest` → **44 passed**. The matrix figure is overstated by
9 and should be corrected to 44.

---

## 4 — The population, enumerated individually

All 192, sorted. `Category` is `ukb.classify()`'s resolved category. `Mutation class`,
`Declared authority` and `Declared lifecycle` are read from
`platform.repository_intelligence.mutation_classification` **as it behaves today** —
including the §3.2 defect, so the table shows the real current state rather than a corrected
projection.

| # | Artifact | Category (ukb) | Mutation class | Declared authority | Declared lifecycle |
|---|---|---|---|---|---|
| 1 | `ASSESSMENT-BOUNDARY-DETERMINATION.md` | ASSESS | **UNRESOLVED** | — | — |
| 2 | `ASSESSMENT-CONFLICT-REGISTER.md` | ASSESS | **UNRESOLVED** | — | — |
| 3 | `B-01-BIRTH-SCOPE-GOVERNANCE-DETERMINATION.md` | B01BIR | **UNRESOLVED** | — | — |
| 4 | `B-01-IMPLEMENTATION-PLAN.md` | B01IMP | **UNRESOLVED** | — | — |
| 5 | `B-02-LIFECYCLE-LINKAGE-GAP-DETERMINATION.md` | B02LIF | **UNRESOLVED** | — | — |
| 6 | `B-02-OWNERSHIP-RESOLUTION-REPORT.md` | B02OWN | **UNRESOLVED** | — | — |
| 7 | `B-02-UID-DICTIONARY-PERSISTENCE-DISCOVERY.md` | B02UID | **UNRESOLVED** | — | — |
| 8 | `B-02-UID-DICTIONARY-PERSISTENCE-EVIDENCE-REPORT.md` | B02UID | **UNRESOLVED** | — | — |
| 9 | `CANONICAL-AUTHORITY-DETERMINATION.md` | CANONI | **UNRESOLVED** | — | — |
| 10 | `CAPABILITY-COVERAGE-CLOSURE-DETERMINATION.md` | CAPABI | **UNRESOLVED** | — | — |
| 11 | `CERTIFICATION-ARCHITECTURE-DETERMINATION-DRAFT.md` | CERTIF | **UNRESOLVED** | — | — |
| 12 | `CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md` | CERTIF | **UNRESOLVED** | — | — |
| 13 | `CERTIFICATION-OWNERSHIP-RECONCILIATION-FINDING.md` | CERTIF | **UNRESOLVED** | — | — |
| 14 | `CMG-000012-IDENTITY-AND-OWNERSHIP-DETERMINATION.md` | CMG000 | AUTHORED_DOCUMENT | NONE — DERIVED TRUTH. Binds; asserts nothing of its own. | — |
| 15 | `CONSTITUTIONAL-BOUNDARY-RESOLUTION-DETERMINATION.md` | CON | **UNRESOLVED** | — | — |
| 16 | `DEPENDENCY-CLOSURE-DETERMINATION.md` | DEPEND | **UNRESOLVED** | — | — |
| 17 | `F-1-LINEAGE-DIVERGENCE-CORRECTION-REPORT.md` | F1LINE | **UNRESOLVED** | — | — |
| 18 | `F-1-LINEAGE-DIVERGENCE-DISPOSITION-DETERMINATION.md` | F1LINE | **UNRESOLVED** | — | — |
| 19 | `FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md` | FINALF | **UNRESOLVED** | — | — |
| 20 | `FINAL-FREEZE-READINESS-DETERMINATION.md` | FINALF | **UNRESOLVED** | — | — |
| 21 | `GATE-PURITY-DETERMINATION.md` | GATEPU | **UNRESOLVED** | — | — |
| 22 | `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` | GOVERN | **UNRESOLVED** | — | — |
| 23 | `H-06-ATOMIC-EVOLUTION-TRANSACTION-AUTHORITY-DETERMINATION.md` | H06ATO | **UNRESOLVED** | — | — |
| 24 | `H-06-BASELINE-EVOLUTION-UAUE-INTEGRATION-AUTHORITY-DETERMINATION.md` | H06BAS | **UNRESOLVED** | — | — |
| 25 | `H-06-CONTROLLED-IMPLEMENTATION-EXECUTION-PLAN-v2.md` | H06CON | **UNRESOLVED** | — | — |
| 26 | `H-06-CONTROLLED-IMPLEMENTATION-EXECUTION-PLAN.md` | H06CON | **UNRESOLVED** | — | — |
| 27 | `H-06-DECISION-BOUNDARY-VALIDATION.md` | H06DEC | **UNRESOLVED** | — | — |
| 28 | `H-06-DECISION-IMPACT-SIMULATION-DETERMINATION.md` | H06DEC | **UNRESOLVED** | — | — |
| 29 | `H-06-DOCUMENT-CANONICALITY-CLEANUP-DETERMINATION.md` | H06DOC | **UNRESOLVED** | — | — |
| 30 | `H-06-FINAL-OWNER-DECISION-READINESS-DETERMINATION.md` | H06FIN | **UNRESOLVED** | — | — |
| 31 | `H-06-GATE-OWNERSHIP-MODEL-RESOLUTION-DETERMINATION.md` | H06GAT | **UNRESOLVED** | — | — |
| 32 | `H-06-GOVERNANCE-DECISION-RECORD-VALIDATION-DETERMINATION.md` | H06GOV | **UNRESOLVED** | — | — |
| 33 | `H-06-IADR-ALIGNMENT-UPDATE-VALIDATION-DETERMINATION.md` | H06IAD | **UNRESOLVED** | — | — |
| 34 | `H-06-IADR-SIGNATURE-PACKAGE.md` | H06IAD | **UNRESOLVED** | — | — |
| 35 | `H-06-IADR-SIGNATURE-VALIDATION-DETERMINATION.md` | H06IAD | **UNRESOLVED** | — | — |
| 36 | `H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md` | H06IAR | **UNRESOLVED** | — | — |
| 37 | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATE-REQUIREMENTS.md` | H06IMP | **UNRESOLVED** | — | — |
| 38 | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATED.md` | H06IMP | **UNRESOLVED** | — | — |
| 39 | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md` | H06IMP | **UNRESOLVED** | — | — |
| 40 | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-VALIDATION-DETERMINATION.md` | H06IMP | **UNRESOLVED** | — | — |
| 41 | `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md` | H06IMP | **UNRESOLVED** | — | — |
| 42 | `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-VALIDATION-DETERMINATION.md` | H06IMP | **UNRESOLVED** | — | — |
| 43 | `H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md` | H06IMP | **UNRESOLVED** | — | — |
| 44 | `H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md` | H06IMP | **UNRESOLVED** | — | — |
| 45 | `H-06-IMPLEMENTATION-AUTHORIZATION-SIGNATURE-VALIDATION-DETERMINATION.md` | H06IMP | **UNRESOLVED** | — | — |
| 46 | `H-06-IMPLEMENTATION-COMMIT-BOUNDARY-RECONCILIATION-DETERMINATION.md` | H06IMP | **UNRESOLVED** | — | — |
| 47 | `H-06-IMPLEMENTATION-EVOLUTION-POPULATION-BOUNDARY-OWNER-DECISION-RECORD.md` | H06IMP | **UNRESOLVED** | — | — |
| 48 | `H-06-IMPLEMENTATION-EXECUTION-APPROVAL-VALIDATION-DETERMINATION.md` | H06IMP | **UNRESOLVED** | — | — |
| 49 | `H-06-IMPLEMENTATION-TASK-BREAKDOWN-PACKAGE.md` | H06IMP | **UNRESOLVED** | — | — |
| 50 | `H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md` | H06MUT | **UNRESOLVED** | — | — |
| 51 | `H-06-OPTION-COMPARISON-MATRIX.md` | H06OPT | **UNRESOLVED** | — | — |
| 52 | `H-06-OWNER-DECISION-ENTRY-VALIDATION-DETERMINATION.md` | H06OWN | **UNRESOLVED** | — | — |
| 53 | `H-06-OWNER-DECISION-READINESS-DETERMINATION.md` | H06OWN | **UNRESOLVED** | — | — |
| 54 | `H-06-OWNER-DECISION-RECORDING-CHECKLIST.md` | H06OWN | **UNRESOLVED** | — | — |
| 55 | `H-06-OWNERSHIP-DISPOSITION-DECISION-PACKAGE.md` | H06OWN | **UNRESOLVED** | — | — |
| 56 | `H-06-OWNERSHIP-DISPOSITION-DECISION-RECORD-CANONICALITY-CORRECTION-DETERMINATION.md` | H06OWN | **UNRESOLVED** | — | — |
| 57 | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-ENTRY-VALIDATION-DETERMINATION.md` | H06OWN | **UNRESOLVED** | — | — |
| 58 | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-RECORD.md` | H06OWN | **UNRESOLVED** | — | — |
| 59 | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-VALIDATION-DETERMINATION.md` | H06OWN | **UNRESOLVED** | — | — |
| 60 | `H-06-PHASE-0-REVALIDATION-DETERMINATION.md` | H06PHA | **UNRESOLVED** | — | — |
| 61 | `H-06-POST-86-COMMIT-REPOSITORY-STATE-RECONCILIATION-DETERMINATION.md` | H06POS | **UNRESOLVED** | — | — |
| 62 | `H-06-PRE-IMPLEMENTATION-REPOSITORY-STATE-VALIDATION.md` | H06PRE | **UNRESOLVED** | — | — |
| 63 | `H-06-R1-GATE-FILENAME-COLLISION-DETERMINATION.md` | H06R1G | **UNRESOLVED** | — | — |
| 64 | `H-06-R2-EXECUTION-AUDIT-TRAIL-DESTINATION-DETERMINATION.md` | H06R2E | **UNRESOLVED** | — | — |
| 65 | `H-06-R3-GATE-MODE-FIELD-CANONICAL-DETERMINATION.md` | H06R3G | **UNRESOLVED** | — | — |
| 66 | `H-06-R4-CONTROLLED-CORRECTION-EXECUTION-PREPARATION.md` | H06R4C | **UNRESOLVED** | — | — |
| 67 | `H-06-R4-CORRECTION-EXECUTION-VALIDATION-DETERMINATION.md` | H06R4C | **UNRESOLVED** | — | — |
| 68 | `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` | H06R4C | **UNRESOLVED** | — | — |
| 69 | `H-06-R4-GRANDFATHERING-POLICY-CN2-COMPLETION-VALIDATION-DETERMINATION.md` | H06R4G | **UNRESOLVED** | — | — |
| 70 | `H-06-R4-GRANDFATHERING-POLICY-DECISION-CANONICALITY-RESOLUTION-DETERMINATION.md` | H06R4G | **UNRESOLVED** | — | — |
| 71 | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD-HISTORICAL-PRE-R2.md` | H06R4G | **UNRESOLVED** | — | — |
| 72 | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` | H06R4G | **UNRESOLVED** | — | — |
| 73 | `H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md` | H06R4G | **UNRESOLVED** | — | — |
| 74 | `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` | H06R4G | **UNRESOLVED** | — | — |
| 75 | `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-VALIDATION-DETERMINATION.md` | H06R4G | **UNRESOLVED** | — | — |
| 76 | `H-06-R4-GRANDFATHERING-POLICY-SUPPLEMENTARY-TRANSMISSION-VALIDATION-DETERMINATION.md` | H06R4G | **UNRESOLVED** | — | — |
| 77 | `H-06-RATIFICATION-VALIDATION-DETERMINATION.md` | H06RAT | **UNRESOLVED** | — | — |
| 78 | `H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md` | H06RAT | **UNRESOLVED** | — | — |
| 79 | `H-06-SUCCESS-CRITERIA-REBASE-DETERMINATION.md` | H06SUC | **UNRESOLVED** | — | — |
| 80 | `H-06-TASK-001-BASELINE-CAPTURE-REPORT.md` | H06TAS | **UNRESOLVED** | — | — |
| 81 | `H-06-TASK-002-DECLARATION-SCHEMA-PREPARATION-REPORT.md` | H06TAS | **UNRESOLVED** | — | — |
| 82 | `H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md` | H06TAS | **UNRESOLVED** | — | — |
| 83 | `H-06-TASK-004-DECLARATION-UPDATE-PREPARATION-PLAN.md` | H06TAS | **UNRESOLVED** | — | — |
| 84 | `H-06-TASK-005-REPLAY-CONTRACT-IMPLEMENTATION-PLAN.md` | H06TAS | **UNRESOLVED** | — | — |
| 85 | `H-06-TASK-006-GP2-WRITE-ORDER-FIX-PLAN.md` | H06TAS | **UNRESOLVED** | — | — |
| 86 | `H-06-TASK-007-GP4-DEAD-FLAG-REMOVAL-PLAN.md` | H06TAS | **UNRESOLVED** | — | — |
| 87 | `H-06-TASK-008-DECLARATION-FILE-LOCATION-SURVEY.md` | H06TAS | **UNRESOLVED** | — | — |
| 88 | `H-06-TASK-009-GP10-AEE-TIER-GUARD-FIX-PLAN.md` | H06TAS | **UNRESOLVED** | — | — |
| 89 | `H-06-TASK-010-GATE-PURITY-CERTIFICATION-PLAN.md` | H06TAS | **UNRESOLVED** | — | — |
| 90 | `H-06-UAIE-COMMIT-READINESS-AND-REPLAY-PROOF-DETERMINATION.md` | H06UAI | **UNRESOLVED** | — | — |
| 91 | `H-06-UAIE-UAUE-RIB-ATOMIC-EVOLUTION-BOUNDARY-DETERMINATION.md` | H06UAI | **UNRESOLVED** | — | — |
| 92 | `H-06-UAUE-COMMIT-READINESS-REVALIDATION-DETERMINATION.md` | H06UAU | **UNRESOLVED** | — | — |
| 93 | `H-06-UAUE-DENOMINATOR-DELTA-OWNER-DECISION-RECORD.md` | H06UAU | **UNRESOLVED** | — | — |
| 94 | `H-06-UAUE-DENOMINATOR-DELTA-OWNER-DECISION-VALIDATION-DETERMINATION.md` | H06UAU | **UNRESOLVED** | — | — |
| 95 | `H-06-UAUE-OWNERSHIP-COMMIT-READINESS-DETERMINATION.md` | H06UAU | **UNRESOLVED** | — | — |
| 96 | `H-06-UNIVERSAL-EVOLUTION-TRANSACTION-AUTHORITY-GAP-RESOLUTION-DETERMINATION.md` | H06UNI | **UNRESOLVED** | — | — |
| 97 | `H-06-UNIVERSAL-EVOLUTION-TRANSACTION-OBJECT-DETERMINATION.md` | H06UNI | **UNRESOLVED** | — | — |
| 98 | `IMPLEMENTATION-REALITY-ASSESSMENT.md` | IMP | **UNRESOLVED** | — | — |
| 99 | `MUTATION-OWNERSHIP-DISCOVERY-DETERMINATION.md` | MUTATI | **UNRESOLVED** | — | — |
| 100 | `P1-A-01-ROOT-ONTOLOGY-DISCOVERY-REPORT.md` | P1A01R | AUTHORED_DOCUMENT | Repository Truth. Every finding below cites a Repository Tru | — |
| 101 | `P1-A-02-ROOT-ONTOLOGY-IMPLEMENTATION-PLAN.md` | P1A02R | **UNRESOLVED** | — | — |
| 102 | `PHASE-0.7-DEPENDENCY-GRAPH-CONSOLIDATION-READINESS-DETERMINATION.md` | PHASE0 | **UNRESOLVED** | — | — |
| 103 | `PHASE-0.7-DEPENDENCY-GRAPH-GOVERNANCE-BINDING-DETERMINATION.md` | PHASE0 | **UNRESOLVED** | — | — |
| 104 | `PHASE-4-CAPABILITY-GAP-MATRIX.md` | PHASE4 | AUTHORED_DOCUMENT | NONE — DERIVED TRUTH. This report measures located owners; i | — |
| 105 | `PHASE-4-RESUMPTION-STATE-REPORT.md` | PHASE4 | AUTHORED_DOCUMENT | NONE — DERIVED TRUTH. This report measures; it decides nothi | — |
| 106 | `PHASE-4-VALIDATION-AND-CERTIFICATION-EVIDENCE.md` | PHASE4 | AUTHORED_DOCUMENT | NONE — DERIVED TRUTH. Every row is a command output, not an  | — |
| 107 | `PHASE-CAA-INV-08-ENFORCEMENT-COMPLETENESS-DETERMINATION.md` | PHASEC | **UNRESOLVED** | — | — |
| 108 | `PHASE-CERTIFICATION-GOVERNANCE-BINDING-DETERMINATION.md` | PHASEC | **UNRESOLVED** | — | — |
| 109 | `PHASE-CERTIFICATION-GOVERNANCE-RELATIONSHIP-DETERMINATION.md` | PHASEC | **UNRESOLVED** | — | — |
| 110 | `PHASE-CERTIFICATION-TAXONOMY-READINESS-DETERMINATION.md` | PHASEC | **UNRESOLVED** | — | — |
| 111 | `PHASE-GOVERNANCE-FREEZE-DETERMINATION.md` | PHASEG | **UNRESOLVED** | — | — |
| 112 | `PHASE-GOVERNANCE-RECONCILIATION-FREEZE-READINESS-DETERMINATION.md` | PHASEG | **UNRESOLVED** | — | — |
| 113 | `PHASE-IDENTITY-NAMESPACE-GOVERNANCE-BINDING-DETERMINATION.md` | PHASEI | **UNRESOLVED** | — | — |
| 114 | `PHASE-IDENTITY-NAMESPACE-OWNERSHIP-DETERMINATION.md` | PHASEI | **UNRESOLVED** | — | — |
| 115 | `PHASE-KNOWLEDGE-IDENTITY-RELATIONSHIP-DETERMINATION.md` | PHASEK | **UNRESOLVED** | — | — |
| 116 | `PHASE-KNOWLEDGE-REGISTRY-OWNERSHIP-RECONCILIATION-DETERMINATION.md` | PHASEK | **UNRESOLVED** | — | — |
| 117 | `PHASE-P0-CLOSURE-DETERMINATION.md` | PHASEP | **UNRESOLVED** | — | — |
| 118 | `PHASE-P0-CLOSURE-REMEDIATION-DETERMINATION.md` | PHASEP | **UNRESOLVED** | — | — |
| 119 | `PHASE-P0-FINAL-CLOSURE-DETERMINATION.md` | PHASEP | **UNRESOLVED** | — | — |
| 120 | `PHASE-POST-FREEZE-EVOLUTION-READINESS-DETERMINATION.md` | PHASEP | **UNRESOLVED** | — | — |
| 121 | `PHASE-UCF-000-COMPLETENESS-DISCOVERY-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 122 | `PHASE-UCF-001-COMPLETENESS-DISCOVERY-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 123 | `PHASE-UCF-002-COMPLETENESS-ARCHITECTURE-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 124 | `PHASE-UCF-003-COMPLETENESS-GOVERNANCE-BINDING-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 125 | `PHASE-UCF-004-COMPLETENESS-GOVERNANCE-BINDING-IMPLEMENTATION-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 126 | `PHASE-UCF-005-PROVIDER-INTEGRATION-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 127 | `PHASE-UCF-006-PROVIDER-FEDERATION-ASSIMILATION-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 128 | `PHASE-UCF-007-PROVIDER-CATEGORY-GOVERNANCE-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 129 | `PHASE-UCF-008-PROVIDER-CATEGORY-OWNERSHIP-MODEL-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 130 | `PHASE-UCF-009-PROVIDER-CATEGORY-INTEGRITY-INVARIANT-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 131 | `PHASE-UCF-010-PROVIDER-CATEGORY-INTEGRITY-IMPLEMENTATION-READINESS-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 132 | `PHASE-UCF-011-PROVIDER-CATEGORY-INTEGRITY-OBSERVATIONAL-IMPLEMENTATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 133 | `PHASE-UCF-012-PROVIDER-CATEGORY-OWNERSHIP-RESOLUTION-INTEGRATION-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 134 | `PHASE-UCF-013-PROVIDER-CATEGORY-OWNERSHIP-RESOLUTION-INTEGRATION-IMPLEMENTATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 135 | `PHASE-UCF-014-PROVIDER-CATEGORY-OWNERSHIP-RESOLUTION-POPULATION-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 136 | `PHASE-UCF-015-PROVIDER-CATEGORY-OWNERSHIP-RESOLUTION-POPULATION-IMPLEMENTATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 137 | `PHASE-UNIVERSAL-ASSURANCE-RELATIONSHIP-DETERMINATION.md` | PHASEU | **UNRESOLVED** | — | — |
| 138 | `PHASE-VERDICT-VOCABULARY-TAXONOMY-DETERMINATION.md` | PHASEV | **UNRESOLVED** | — | — |
| 139 | `POST-ASSESSMENT-STABILIZATION-EVIDENCE-RECORD.md` | POSTAS | **UNRESOLVED** | — | — |
| 140 | `POST-STABILIZATION-DETERMINATION-LIFECYCLE-DECISION.md` | POSTST | **UNRESOLVED** | — | — |
| 141 | `REPOSITORY-ASSIMILATION-INVENTORY.md` | REPOSI | **UNRESOLVED** | — | — |
| 142 | `REPOSITORY-IDENTITY-ALLOCATION-OWNER-DECISION-RECORD.md` | REPOSI | **UNRESOLVED** | — | — |
| 143 | `SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md` | SCOPEB | **UNRESOLVED** | — | — |
| 144 | `SCOPE-B-DISCOVERY-REPORT.md` | SCOPEB | AUTHORED_DOCUMENT | Repository Truth. Every number below was measured, not quote | — |
| 145 | `SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md` | SCOPEB | **UNRESOLVED** | — | — |
| 146 | `SCOPE-B-WORKSTREAM-3-LINEAGE-DISCOVERY-DETERMINATION.md` | SCOPEB | **UNRESOLVED** | — | — |
| 147 | `SCOPE-B-WORKSTREAM-3-UNIVERSAL-LINEAGE-PROJECTION-ARCHITECTURE-DETERMINATION.md` | SCOPEB | **UNRESOLVED** | — | — |
| 148 | `SCOPE-B-WORKSTREAM-3-UNIVERSAL-LINEAGE-PROJECTION-IMPLEMENTATION-REPORT.md` | SCOPEB | **UNRESOLVED** | — | — |
| 149 | `SCOPE-B-WORKSTREAM-5-REGISTRY-COVERAGE-MATRIX-DISCOVERY-DETERMINATION.md` | SCOPEB | **UNRESOLVED** | — | — |
| 150 | `SCOPE-B-WORKSTREAM-5-REGISTRY-COVERAGE-MATRIX-IMPLEMENTATION-REPORT.md` | SCOPEB | **UNRESOLVED** | — | — |
| 151 | `SEMANTIC-LIFECYCLE-RECONCILIATION-REGISTER.md` | SEMANT | **UNRESOLVED** | — | — |
| 152 | `UAUE-EPOCH-6-CERTIFICATION-DETERMINATION.md` | UAUEEP | **UNRESOLVED** | — | — |
| 153 | `UAUE-IMPLEMENTATION-STATUS-DETERMINATION.md` | UAUEIM | **UNRESOLVED** | — | — |
| 154 | `UCKP-CMG-AUTHORITY-ALIGNMENT-DETERMINATION.md` | UCKPCM | **UNRESOLVED** | — | — |
| 155 | `UCKP-CMG-CONSTITUTIONAL-RECONCILIATION-DETERMINATION.md` | CON | **UNRESOLVED** | — | — |
| 156 | `UCOS-CEA-000001-CONSTITUTIONAL-EVOLUTION-ASSIMILATION-DETERMINATION.md` | CON | **UNRESOLVED** | — | — |
| 157 | `UCOS-CEA-000002-REGENERATED-ROADMAPS-AND-EXECUTION-SEQUENCE.md` | UCOSCE | **UNRESOLVED** | — | — |
| 158 | `UCOS-MIP-000003-MASTER-IMPLEMENTATION-PLAN-V3.md` | UCOSMI | **UNRESOLVED** | — | — |
| 159 | `UCOS-POST-STABILIZATION-READINESS-DETERMINATION.md` | UCOSPO | **UNRESOLVED** | — | — |
| 160 | `UCOS-UVI-000001-EVIDENCE-KEY-EXECUTION-CONTRACT-IMPLEMENTATION-REPORT.md` | UCOSUV | **UNRESOLVED** | — | — |
| 161 | `UCOS-UVI-000001-STAGE-READ-SET-SEPARATION-IMPLEMENTATION-REPORT.md` | UCOSUV | **UNRESOLVED** | — | — |
| 162 | `UCOS-UVI-000001-VERIFICATION-INTELLIGENCE-EVOLUTION-ARCHITECTURE-DETERMINATION.md` | UCOSUV | AUTHORED_DOCUMENT | NONE — DERIVED. Every constraint cited here is already owned | — |
| 163 | `UCOS-Ω∞-FINAL-REPOSITORY-READINESS-DETERMINATION.md` | UCOSFI | REPOSITORY_STATE | — | — |
| 164 | `UCPA-001-CONSTITUTIONAL-PRIMITIVE-ALIGNMENT-DETERMINATION.md` | CON | **UNRESOLVED** | — | — |
| 165 | `UNIVERSAL-BASELINE-TEMPORAL-CERTIFICATION-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 166 | `UNIVERSAL-EVOLUTION-FOUNDATION-GAP-ANALYSIS.md` | UNIVER | **UNRESOLVED** | — | — |
| 167 | `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 168 | `UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 169 | `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 170 | `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 171 | `UNIVERSAL-INFINITE-SCOPE-AND-DIRECTION-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 172 | `UNIVERSAL-LIFECYCLE-INHERITANCE-RECONCILIATION-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 173 | `UNIVERSAL-LIFECYCLE-SEMANTIC-RESCAN-REGISTER.md` | UNIVER | **UNRESOLVED** | — | — |
| 174 | `UNIVERSAL-RELATIONSHIP-INTELLIGENCE-FOUNDATION-DETERMINATION.md` | UNIVER | **UNRESOLVED** | — | — |
| 175 | `UNIVERSAL-VERIFICATION-INTELLIGENCE-DETERMINATION.md` | UNIVER | AUTHORED_DOCUMENT | NONE — DERIVED TRUTH | — |
| 176 | `UOBC-BSP-001-EVIDENCE-REPORT.md` | UOBCBS | **UNRESOLVED** | — | — |
| 177 | `VERIFICATION-CLOSURE-REMEDIATION-DETERMINATION.md` | VERIFI | **UNRESOLVED** | — | — |
| 178 | `VERIFICATION-EVIDENCE-REPORT.md` | VERIFI | **UNRESOLVED** | — | — |
| 179 | `adr/0003-constitutional-binding-of-ceu-and-ucxi.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Accepted |
| 180 | `adr/0004-uisd-scope-extension-to-entity-applicability.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 181 | `adr/0005-measurement-as-a-context-and-entity.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 182 | `adr/0006-entity-classification-authority-moves-to-ceu.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 183 | `adr/0007-disclose-every-finite-enumeration.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 184 | `adr/0008-unified-unknown-admission-verification.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 185 | `adr/0009-technology-independence-is-already-canonical.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Accepted |
| 186 | `adr/0010-platform-composition-is-already-canonical.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Accepted |
| 187 | `adr/0011-self-learning-and-evolution-are-already-canonical.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Accepted |
| 188 | `adr/0012-remove-residual-planetary-default.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 189 | `adr/0013-universal-persistent-evolutionary-graph-memory.md` | ADR | AUTHORED_DOCUMENT | Constitutional Authority · UCOS Ω∞ | Proposed |
| 190 | `engine/lineage/families.json` | ENG | **UNRESOLVED** | — | — |
| 191 | `engine/lineage/memory-layers.json` | ENG | **UNRESOLVED** | — | — |
| 192 | `engine/registry_coverage/declarations.json` | ENG | **UNRESOLVED** | — | — |

---

## 5 — Irreversible action disclosure

`register.sh` Phase 1 runs `ukb.py build --mint`. `--mint` is the **only** place in the
repository permitted to allocate permanent Universal IDs and page ranges
(`register.sh` header: *"The flag is what makes minting a decision rather than a side
effect"*). Allocation is **append-only from an immutable ledger**
(`00-BOOK/DATA/id-ledger.json`).

### 5.1 Quantified footprint

| Ledger dimension | Before | After (projected) | Δ |
|---|---|---|---|
| `by_path` entries | 1,264 | 1,456 | **+192 permanent identities** |
| `page_cursor` | 9,826 | ≈10,691 | **≈+865 pages** (60 lines/page) |
| `history` entries | 1,264 | 1,456 | +192 |
| `artifacts.json` registrations | 1,233 | 1,425 | +192 |

Verified: **0 of the 192 already hold a `by_path` ledger entry**, so every one of the 192 is
a fresh allocation. No re-use, no idempotent no-op.

### 5.2 What cannot be undone

- **Universal IDs are permanent.** A minted ID is never reclaimed, never reissued, and
  remains in `by_path` even if the artifact is later deleted or renamed. (`by_path` already
  holds 1,264 entries against 1,233 live registrations — 31 identities outliving their
  paths.)
- **Page ranges are permanent.** `page_cursor` only advances. The ≈865 pages consumed are
  never returned to the pool.
- **The ledger is append-only by construction**, not by convention.

### 5.3 Rollback limitation — stated plainly

**There is no rollback.** `git revert` of the registration commit restores the *files*
`id-ledger.json` and `artifacts.json` to their prior bytes, but it does **not** un-mint:

- it re-opens `page_cursor` to re-allocate the same 865 pages to different artifacts,
  breaking the append-only invariant the ledger's own validation asserts;
- any downstream artifact, report, portal page or external reference that captured a minted
  ID between mint and revert becomes a dangling reference;
- `ukb.py validate` checks for duplicate IDs and pages — a revert-then-remint cycle is the
  mechanism most likely to produce them.

**A revert is a repository-state mutation that contradicts a constitutional invariant, not a
recovery path.** The only safe posture is: get the population exactly right before minting,
because after minting there is only forward.

### 5.4 Side effects beyond the ledger

`register.sh` runs 10 phases, of which Phase 1 alone mints. Phases 2–4 (`ukbx sync --due`,
`ukbx twin`, `ukbx portal`) **regenerate** `00-BOOK/DATA`, `REGISTRIES`, `CONTROL-TOWER` and
`PORTAL`. Those regenerations are deterministic and re-derivable, but they will produce a
large working-tree diff that must be committed **in the same commit** as the artifacts —
`--guard` (and the pre-commit hook, if installed) fails otherwise. Phase 9 re-runs
`ukb enforce` and must report **0 unregistered eligible**.

---

## 6 — CEP-002 Article 28 decision draft

> **DRAFT — NOT REGISTERED.** Reproduced for review. It must not be entered into
> `00-MASTER/UCDA-000001/01-CONSTITUTIONAL-DECISION-REGISTER.md` until the §3.2 defect is
> fixed and §8's preconditions are met.

**Proposed identifier:** `adr/0029-req-28-corpus-registration-population.md` → `DEC-ADR-0029`
(`0028` is reserved for the REQ-43 decline; see the REQ-43 determination report.)

### 6.1 Exact population

The **192** version-controlled repository artifacts individually enumerated in §4 of this
report, being exactly the set

```
{ p : p ∈ ukb._iter_files()  ∧  p ∉ artifacts.json["artifacts"][*].path }
```

evaluated at checkpoint `03179308`. Composition: 189 `.md` + 3 `.json`; 178 repository root,
11 `adr/`, 3 `engine/`.

**Explicitly excluded from this population**, named rather than silently omitted:

- the **25** VCS-unbound candidates reported by `ukb enforce --pre` (untracked, therefore not
  yet repository artifacts under B-01c) — including the determination reports authored in
  this Phase 7 pass;
- the **1,233** already-registered artifacts;
- everything under the corpus-internal generator homes.

### 6.2 Authority

| Role | Holder |
|---|---|
| Registering authority | **`REG-AUTO-001`** — Corpus Registration Transaction, `00-BOOK/tools/register.sh`, executing `ukb.py build --mint` |
| Declared mutation class | `CORPUS_REGISTRATION`, per `00-BOOK/DATA/mutation-governance-boundary.json` |
| Deciding authority | `CEP-002 Article 28` |
| Identity authority | `UGA-001` / `REG-AUTO-001` (append-only `id-ledger.json`) |

**Disclosed residual, per §3.1:** per-artifact *mutation* authority remains **UNRESOLVED**
for 172 of the 192 under the mutation-governance boundary, because those documents declare
no `Authority:` or `Deciders:` field. This decision governs their **registration** only. It
does **not** assign, imply, or substitute for their mutation authority, and it must not be
read as closing REQ-38 or REQ-39 over this population.

### 6.3 Irreversible action disclosure

As §5: +192 permanent Universal IDs, ≈+865 permanently allocated pages, append-only ledger,
**no rollback path**. The decision text must reproduce §5.3 verbatim rather than reference it.

### 6.4 Validation criteria

| # | Criterion | Command |
|---|---|---|
| V1 | Population is still exactly 192 immediately before minting | `ukb.py enforce --pre` |
| V2 | Post-registration: 0 unregistered eligible | `ukb.py enforce` (register.sh Phase 9) |
| V3 | Ledger structurally valid — no duplicate IDs, no duplicate pages, referential integrity | `ukb.py validate` (Phase 5) |
| V4 | Signal-ledger integrity intact | `ukbx.py validate` (Phase 6) |
| V5 | Digital-twin certification passes | `ukbx.py twin --check` (Phase 7) |
| V6 | 9 integrity domains pass | `ukbx.py certify` (Phase 8) |
| V7 | No registration drift — registers committed with the artifacts | `register.sh --guard` |
| V8 | `by_path` grew by exactly 192; no pre-existing entry mutated | ledger diff |
| V9 | Full regression suite unchanged | canonical corpus, `--cov-fail-under=90` |
| V10 | All 10 repository gates still PASS | CMG, UAUE×2, UOBC, UISD, UCPA, UVI, ukb enforce/validate, UGA |

### 6.5 Rollback limitation

Stated as §5.3. **No rollback exists.** The decision must record that a `git revert` is a
constitutional-invariant violation rather than a recovery, and that the only mitigation is
pre-mint verification (V1).

### 6.6 Evidence requirements

| # | Evidence |
|---|---|
| E1 | This report, with the §4 enumeration, at the checkpoint the decision cites |
| E2 | `ukb.py enforce --pre` output captured **immediately before** minting, showing 192 |
| E3 | Full `register.sh` transcript, all 10 phases, showing `TRANSACTION COMPLETE` |
| E4 | `ukb.py enforce` output after, showing `unregistered eligible : 0` |
| E5 | `id-ledger.json` diff, confirming +192 `by_path`, `page_cursor` advance only |
| E6 | Full regression run, post-registration |
| E7 | 10-gate re-execution, post-registration |
| E8 | Explicit record that §3.1's 172-artifact authority residual is disclosed and out of scope |

---

## 7 — Artifact → Owner → Authority → Identity → Lifecycle mapping

Per the directive's required chain, at the population level. Per-artifact rows are §4.

```
Artifact          192 version-controlled repository artifacts (§4)
   ↓
Owner             the authoring programme; self-declared for 19, UNDETERMINED for 172 (§3.1)
   ↓
Authority         registration : REG-AUTO-001            (unambiguous, whole population)
                  mutation     : UNRESOLVED for 172      (disclosed residual, §3.1)
                  identity     : UGA-001 / REG-AUTO-001  (append-only ledger)
   ↓
Identity req.     one permanent Universal ID + one page range per artifact,
                  allocated append-only, never reclaimed (§5)
   ↓
Lifecycle         self-declared for 19; the remaining 173 carry no declared lifecycle.
                  Registration does not confer one — corpus registration records that an
                  artifact EXISTS and is identified, not what stage it is in.
```

The chain is **complete for registration** and **incomplete for mutation governance**. That
distinction is the substance of §3.1 and must survive into the decision text.

---

## 8 — Required sequence before minting

| Step | Action | Gate |
|---|---|---|
| 1 | Fix `Repository.tracked` — `git -c core.quotePath=false ls-files -z` (§3.2) | 44 existing tests still pass |
| 2 | Add a regression test with a non-ASCII filename fixture | new test passes; defect cannot recur |
| 3 | Re-run classification repo-wide; record the corrected distribution | 117 no longer `REPOSITORY_STATE` |
| 4 | Re-assess REQ-38 / REQ-39 against corrected output | matrix updated with real numbers |
| 5 | Correct REQ-39's test count 53 → 44 (§3.3) | matrix diff |
| 6 | Register `DEC-ADR-0029` from §6, with §3.1's residual disclosed | decision in the UCDA register |
| 7 | Re-run `ukb.py enforce --pre`; **confirm still exactly 192** | V1 |
| 8 | Execute `register.sh` (all 10 phases) | V2–V7 |
| 9 | Capture E2–E7; commit artifacts + regenerated registers **together** | `--guard` passes |
| 10 | Re-run full regression + 10 gates | V9, V10 |

Steps 1–5 are **prerequisites**, not follow-ups. Step 7 is not a formality: any file
`git add`-ed between now and then changes the population and invalidates the decision's
stated count.

---

## 9 — Boundary statement

This report prepares REQ-28. It does **not** close it. No identity was minted, no ledger
written, no register regenerated, no `register.sh` phase executed. The population is exact
as of checkpoint `03179308` and will change if the working tree changes. The two blockers in
§3 are stated as found; neither was fixed in this pass, as directed.

**Stopped before mutation, as directed.**
