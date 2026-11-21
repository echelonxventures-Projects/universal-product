# GOVERNED EVOLUTION STATE DETERMINATION

> **Mission:** UCOS Ω∞ — verification/evolution plane separation
> **Baseline:** `5eb1a704` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-17
> **Mode:** Determination. **No existing artifact is reclassified by this document.**
> **Authority:** NONE (DERIVED TRUTH). Defines a category and its rules. Legislates nothing and reclassifies nothing.
> **Prerequisite:** `MUTATION-OWNERSHIP-DISCOVERY-DETERMINATION.md`

---

## 1. Why a third category is required

The repository classified every object as either **authored** (a human wrote it) or **generated** (a producer can recompute it). `00-BOOK/DATA/id-ledger.json` is neither, and the consequence was concrete: because nothing described what it was, nothing governed who could write it, and a verification command minted 140 permanent Universal Identifiers as a side effect of a drift check.

Measured evidence that it is not a generated view:

| Test | Result |
|---|---|
| Carries a `generated_at` stamp? | **No** — the only one of seven corpus registers without one |
| Appears as a `canonical_path` in `generated-artifact-registry.json`? | **No** — appears only inside the `input_closure` of 10 *other* artifacts |
| Reproducible by re-running its producer? | **No** |

Measured evidence that it is not an authored input: no human writes `by_path`, `category_seq` or `page_cursor`. `allocate()` derives them from three unrecoverable sources — arrival order, a monotone cursor, and a wall clock.

UGA currently classifies it `TOOLING_OBJECT`, lifecycle `AUTHORED`. That is the misclassification this determination names; it does not correct it (§8).

---

## 2. Definition

> **GOVERNED EVOLUTION STATE** — an artifact recording the accumulated, append-only consequence of past evolution events, not reproducible from present repository content, and therefore mutable only by an explicit governed evolution transaction.

**Three properties, all required:**

| Property | Test |
|---|---|
| **Irreducible** | Deleting it and re-running every producer does not reproduce it |
| **Append-only** | Existing entries are never rewritten, renumbered or reissued |
| **Consequence-of-events** | Its content records that something happened, not what something *is* |

**Excluded by definition:** derived views, projections, generated indexes. If a producer can recompute it, it is a projection and belongs to `GENERATED_ARTIFACT`.

### 2.1 The discriminating test, stated operationally

```
Can the artifact be deleted and reproduced from (tree + producers)?
   YES → derived view / projection / generated index      → GENERATED_ARTIFACT
   NO  → does its content record accumulated events?
           YES → GOVERNED EVOLUTION STATE
           NO  → authored input
```

---

## 3. Scope

### 3.1 Authority

| Dimension | Determination |
|---|---|
| **Category authority** | NONE — this determination defines a category, it does not own instances |
| **Per-artifact authority** | the artifact's existing declared owner is unchanged |
| **Constitutional superior** | UCKP-LAW-0001; identity state additionally under UCKP-ART-05 |
| **Mutation authority** | declared per artifact in `00-BOOK/DATA/mutation-governance-boundary.json` |

This category creates **no new authority**. It names a property that determines *which* authority may mutate an artifact, and the answer is always an existing one.

### 3.2 Ownership

Ownership is unchanged by membership. `id-ledger.json` remains UMB-IMP-001's; `birth-ledger.json` remains UOBC-000001's. Membership constrains *how* an owner may mutate, never *who* owns.

---

## 4. Mutation model

**One rule:** a GOVERNED EVOLUTION STATE artifact is mutated only by an explicit evolution transaction that requests the mutation. Never by default, never as a side effect, never from the verification plane.

| Requirement | Rule |
|---|---|
| **Explicit request** | The mutation must be requested by a named flag or operation. Omission means observe. |
| **Declared class** | The mutation must correspond to a class in `mutation-governance-boundary.json` naming exactly one owning authority. |
| **Verification exclusion** | The class must name the verification plane in `does_not_govern`. |
| **Append-only** | Existing entries are never rewritten. Supersession adds; it does not replace. |
| **No reissue** | An identifier once allocated is never renumbered or reused. Removal retires it. |
| **Unreachable write in observation** | Observation must not reach the write at all. A guarded no-op rewrite is insufficient: the guarantee must be structural. |

### 4.1 Realised pattern

The pattern is `mint: bool`, already present in `uga_engine.py` (`epoch1_identity`, `mint_observation`, `build`) and applied in this cycle to `ukb.py::allocate` / `cmd_build`:

```
cmd_build()            observation  — allocates nothing, ledger write unreachable
cmd_build(--mint)      evolution    — allocates; reserved to the REG-AUTO-001 transaction
```

**Why verification may not regenerate, even read-only-in-intent.** Regeneration writes. A verification path that regenerated derived views to compare them against the committed ones would fail whenever committed views are stale relative to a fresh derivation — and the only way to make it pass would be to commit a regeneration produced from inside verification, which is the loop this separation removes. This is not hypothetical: at baseline `5eb1a704`, `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` is unmodified with respect to HEAD, yet a fresh derivation computes a different `content_hash` than the committed `artifacts.json` records, and a fresh derivation produces 1 356 change events against 1 353 committed. **The committed derived views are measurably stale at HEAD.** Detecting that divergence is legitimate and belongs to the evolution plane, reached through `ukb build` in observation mode; it is not a verification obligation.

---

## 5. Temporal model

Bound to CMG-000002. A GOVERNED EVOLUTION STATE artifact records *when* events happened, so its temporal behaviour is part of its content rather than metadata about its generation.

| Requirement | Rule |
|---|---|
| **Coordinate, not bare value** | A recorded time must carry the reference system that gives it meaning |
| **No mandated representation** | CMG-000002 §3.1 forbids mandating UTC, ISO 8601, Unix epoch, GPS, TAI, Gregorian, 24-hour clock, Earth time zones or leap seconds |
| **Frozen at record** | A temporal coordinate is never revised after the event it records |
| **Engine clock-free** | The engine reads no clock; the caller supplies the coordinate, so the record replays |

**Conformance measured, not assumed:**

| Artifact | Temporal behaviour | Conforms |
|---|---|---|
| `birth-ledger.json` | caller-supplied qualified coordinate (`logical:ucos-repository-history@1#484`); engine clock-free | **YES** |
| UGA `by_object` | `commit:<sha12>` — a commit-derived contextual coordinate | **YES** |
| `id-ledger.json` `by_path` | `first_seen` from `_now()` — **hard-coded ISO-8601 Earth UTC** | **NO** |
| `change-ledger.json` | every `at` from `_now()` — same | **NO** (also a derived view) |

The `id-ledger.json` non-conformance is a **recorded finding, not corrected here**: `first_seen` is frozen at mint and append-only, so changing its representation would rewrite existing entries — precisely what §4 forbids. Migrating it requires its own determination.

---

## 6. Lineage model

| Requirement | Rule |
|---|---|
| **Append-only history** | History grows; entries are never deleted or edited |
| **Supersession, not replacement** | A superseded entry is retained alongside its successor |
| **Retired, not removed** | An identifier for a vanished subject is retained-but-retired, never reclaimed |
| **Derivable descendants** | Child/successor links are derived by inverting the parent edge, never stored twice |

Two lineage planes exist and must not be conflated:

- **Accumulated** — `id-ledger.json` `history`, `birth-ledger.json` `supersessions`. GOVERNED EVOLUTION STATE.
- **Projected** — `change-ledger.json` `lineage`, which its own producer documents as "regenerated deterministically each transaction; **NOT** an append-only source of truth". A derived view.

---

## 7. Certification requirements

| Requirement | Rule |
|---|---|
| **Integrity provable** | Content digest or hash chain re-derivable from the artifact itself |
| **Certification is separate** | Registration is not certification. CEP-005 is the certification channel |
| **Certification never mutates state** | A certificate references state; it does not write it |
| **Replay** | The artifact must load such that loading re-verifies it |

`birth-ledger.json` satisfies replay through `BirthRecord.from_dict` refusing an incomplete record, and integrity through re-derivation of every identity from its own inputs (`UOBC-L-03`). `id-ledger.json` has no self-verifying digest — a recorded finding, not corrected here.

---

## 8. Candidate membership — assessed, NOT applied

**No object is reclassified by this determination.** The table records the assessment that a future reclassification cycle would act on.

| Candidate | Irreducible | Append-only | Records events | Assessment | Current class |
|---|---|---|---|---|---|
| `00-BOOK/DATA/id-ledger.json` | yes | yes | yes | **MEMBER** — the canonical case | `TOOLING_OBJECT` / `AUTHORED` |
| `00-MASTER/UOBC-000001/birth-ledger.json` | yes | yes | yes | **MEMBER** | `DATA_OBJECT` |
| `knowledge/canonical-knowledge.json` (UKDA) | yes | yes | yes (supersedes chains) | **MEMBER** — authored/accumulated hybrid | `DATA_OBJECT` |
| certification audit ledger (`engine/universal_certification/audit.py`) | yes | yes | yes | **MEMBER in form, not persisted** | in-memory |
| `00-BOOK/DATA/artifacts.json` | no | no | no | **EXCLUDED** — derived view | `TOOLING_OBJECT` |
| `00-BOOK/DATA/change-ledger.json` | no | no | projects events | **EXCLUDED** — derived view | `TOOLING_OBJECT` |
| `relationships.json`, `volumes.json`, `control-tower.json`, `certification.json` | no | no | no | **EXCLUDED** — derived views | `TOOLING_OBJECT` |
| `UAUE-EVOLUTION-HISTORY.json` | no (`projection_of`) | n/a | projects | **EXCLUDED** — projection | `DATA_OBJECT` |
| UGA 9 surfaces | no | n/a | no | **EXCLUDED** — projections | `DATA_OBJECT` |

**Why reclassification is deferred.** Changing `object_class` for `id-ledger.json` changes its `evidence_class` and `certification_status` assignment and re-renders all nine UGA surfaces, and UGA's classifier (`classify_object`) is a **total path-based function** with an unconditional terminal branch — admitting a new class means changing the classifier itself, which changes classification for every object it evaluates. That is a distinct architectural act requiring its own determination and its own commit.

---

## 9. Recorded future determinations

Each affects canonical architecture and requires its own lifecycle determination. None is performed in this cycle.

| # | Subject | Why deferred |
|---|---|---|
| **F-1** | Admit `GOVERNED_EVOLUTION_STATE` as a UGA `object_class` and reclassify the members of §8 | Changes a total classifier; re-renders 9 surfaces |
| **F-2** | Persist `engine/nucleus/lineage.py::LineageLedger` | Introduces a tracked append-only ledger — new canonical state |
| **F-3** | Persist `engine/uckp/evolution.py::EvolutionLedger` | Same; also interacts with UAUE's declared refusal to write a registry |
| **F-4** | Persist `engine/universal_certification/audit.py::CertificationAuditLedger` | Same |
| **F-5** | Migrate `id-ledger.json` `first_seen` to a CMG-000002 qualified coordinate | Would rewrite append-only entries; needs a representation-migration determination |
| **F-6** | Give `id-ledger.json` a self-verifying integrity digest | Changes the ledger's own shape |
| **F-7** | Reconcile the measured staleness of committed derived views at HEAD | A registration transaction, sequenced by `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` |

---

## 10. Determination summary

| Item | Determination |
|---|---|
| Third category required | **YES** — defined §2 |
| Category creates new authority | **NO** — constrains how existing owners mutate |
| Mutation model | Explicit request · declared class · verification excluded · append-only · unreachable write in observation |
| Temporal model | CMG-000002 coordinates; two members conform, `id-ledger.json` does not (recorded) |
| Lineage model | Append-only; supersede not replace; retire not reclaim; descendants derived |
| Certification | Integrity re-derivable; certification separate from registration; never mutates state |
| Objects reclassified | **NONE** |
| Classifier modified | **NONE** |
| Future determinations recorded | 7 (§9) |

---

**END GOVERNED EVOLUTION STATE DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Authority:** NONE — DERIVED TRUTH
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived) · CMG-000001 (law)
