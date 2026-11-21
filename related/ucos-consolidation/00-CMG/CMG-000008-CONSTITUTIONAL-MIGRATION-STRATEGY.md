# UCOS Ω∞ — CMG CONSTITUTIONAL MIGRATION STRATEGY

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000008 |
| ARTIFACT | UCOS Ω∞ CMG Constitutional Migration Strategy |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Migration Strategy |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) |
| GOVERNED-BY | CMG-000001 |
| DEPENDS-ON | CMG-000001 |
| CANONICAL FORM | This Markdown file |

> Derived strategy under CMG-000001 Article LXX. Migration **operation** is owned by the located evolution constitution (`CMG-DLG-09`) and is not restated. This document states what migration admission of CMG-000001 requires — and the answer is materially none.

---

## 1 — THE HEADLINE: NO MIGRATION IS REQUIRED

CMG-000001 LXX.6 states that migration is not a precondition of its admission, and that this is a deliberate design property rather than a convenience. The property holds because admission is **pure addition**:

| What admission does | What it does not require |
|---|---|
| Adds one zone, one normative artifact, thirteen analyses, one projection, one validator | No existing artifact to change |
| Records recognition of 42 existing artifacts | No existing artifact to re-declare, re-register, or re-classify |
| Records a lattice that contains every located precedence statement | No located precedence statement to be amended |
| Recognizes every legacy identifier namespace as legacy-owned | No identifier to be renumbered or reformatted |
| Establishes one new namespace (`CMG`) | No existing namespace to be altered |
| Adds one gate to the existing chain | No existing gate to be modified |

There is therefore **no data migration, no schema migration, no identifier migration, no content backfill, and no transition period** (CMG-000001 LXVIII.6).

---

## 2 — WHY ADMISSION IS BACKWARD COMPATIBLE

Backward compatibility is a property of the change, not an aspiration (CMG-000001 LXVIII.1). The change is backward compatible because it satisfies the test at LXVIII.3: the impact analysis identifies zero artifacts that admission could invalidate.

The structural reason: CMG-000001's only operations on other instruments are **recognize, record, rank, and refer** (LXXXI.3, LXXXVI.3). None of the four imposes an obligation on the recognized artifact. A recognized constitution's authority, positive scope, negative scope, conflict rule, identity, version, lifecycle state, and text are all exactly what they were before recognition.

Contrast with the change that *would* have required migration: adopting the twelve meta invariants as corpus-wide obligations. That would impose new obligations on artifacts owned elsewhere, invalidate any non-conforming artifact, and require a migration plan for each. CMG-000001 explicitly declines to do this and records the question as `CMG-OQ-07`.

---

## 3 — WHAT WOULD REQUIRE MIGRATION, AND WHAT ITS PLAN WOULD BE

Recorded in advance so that the boundary is visible before it is crossed.

### 3.1 Adopting the meta invariants corpus-wide (`CMG-OQ-07`)

**Classification:** MAJOR (CMG-000001 XXIX.2) — it adds obligations to existing subjects.

**Plan sketch, if ratified:**
1. Run the validator in advisory mode across every constitutional artifact, not only the recognized set, to enumerate non-conformances per invariant.
2. Classify each non-conformance: remediable by declaration (the artifact adds a missing negative-scope clause), remediable by allocation (a concern gains an owner), or requiring amendment of the artifact.
3. Sequence by dependency depth, shallowest first, so that a remediation never depends on an unremediated superior. The CEP spine (depth 11) is remediated last.
4. Apply per-artifact remediation through each artifact's own amendment path — never by editing another owner's artifact.
5. Declare completion only when the validator reports zero findings over the extended scope (CMG-000001 LXX.3).

**Reversibility:** each step is an independent amendment with its own lineage; reversal is supersession, not deletion.

### 3.2 Closing the Tier-1 vacancy (`CMG-OQ-02`)

**Classification:** MAJOR in effect, though additive in text — it changes the standing of every artifact in the corpus from PROVISIONAL to a conferred standing.

**Plan sketch, if ratified:**
1. Record the occupying artifact (or the ratified permanent vacancy) in the registry.
2. Re-run authority resolution for every determination previously marked provisional (CMG-000001 XVII.4(d)).
3. Re-validate; re-certify; the readiness ceiling of LXXX.4 is removed by amendment.
4. **No artifact text changes.** Standing is a recorded fact, not embedded content — which is precisely why this migration is cheap. Had standing been written into each artifact's body, this step would have required amending 43 artifacts.

### 3.3 Federating a second repository

**Classification:** MINOR — the mechanism already exists.

**Plan sketch:** qualify identifiers with namespace roots (`<ROOT>:<SUB>:<LEAF>`, CMG-000001 XXXIII.4), mark cross-repository artifacts FEDERATION-SCOPED (XII.3), and extend traceability across the boundary (XXXVII.7). No renumbering of either repository is required, because namespace qualification was declared before any federation existed. This is forward compatibility doing its job.

### 3.4 Retiring or superseding CMG-000001

**Classification:** MAJOR.

**Plan sketch:** the successor takes a new identity in the `CMG` namespace, links to CMG-000001 by lineage, covers every retained concern (`CMG-RET-01` … `CMG-RET-11`) or explicitly reassigns them, repoints every dependent, and preserves CMG-000001 in POST-EFFECT (CMG-000001 LXXII.2–LXXII.5). Partial supersession that orphans a retained concern is prohibited.

---

## 4 — MIGRATION SAFETY RULES INHERITED

These are not restated as new law; they are the located rules that any future CMG migration is bound by, recorded here so a migration author does not need to rediscover them:

| Rule | Source |
|---|---|
| Migration must be verifiable at completion; an unprovable migration is not complete | CMG-000001 LXX.3 |
| Migration preserves identity and lineage; silent identity change is prohibited | LXX.4 |
| Migration must be resumable; an interrupted migration must leave no artifact in an undeclared state | LXX.5 |
| A migration that would edit frozen text proceeds by supersession instead | LXX.7, XLII.3 |
| Derived stores are migrated by regeneration, never by restoring a stale copy | LXXIV.6 |
| Backward compatibility is provided by migration and transition, never by weakening the current version | LXVIII.5 |

---

## 5 — ROLLBACK OF THE PRESENT CHANGE

| Step | Action | Effect |
|---|---|---|
| 1 | Remove the two added `Makefile` lines | The `cmg-gate` target disappears; no existing target is affected |
| 2 | Delete `00-CMG/` | All CMG artifacts, the projection, and the validator are removed |
| 3 | Re-run the repository's own gates | Prior state restored exactly |

Rollback requires no migration and leaves no residue, because admission wrote nothing into any pre-existing artifact. The only lasting trace would be universal identifiers allocated to the CMG files by the registration ledger; those remain allocated and are never reissued (CMG-000001 XXX.4), which is correct behaviour, not residue.
