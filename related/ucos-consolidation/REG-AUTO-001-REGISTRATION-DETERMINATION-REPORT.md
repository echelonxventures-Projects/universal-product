# REG-AUTO-001 — REGISTRATION DETERMINATION REPORT

| Field | Value |
|-------|-------|
| ARTIFACT ID | `UCOS-RDR-000001` |
| ARTIFACT | Registration Determination — the identity population awaiting a governed mint |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** This report DETERMINES; it does not register. The registering authority is `REG-AUTO-001`, declared in `00-BOOK/DATA/mutation-governance-boundary.json`. |
| **STATUS** | **PREPARED · AWAITING GOVERNED DECISION. NO IDENTITY HAS BEEN MINTED.** |
| BASELINE | HEAD `03179308` · branch `integration/recovery-001` · snapshot `2026-08-22T05:04Z` |
| PREPARED BY | UEG-000001 closure cycle, under the Category B rule (irreversible ⇒ determination package only) |
| METHOD | Read-only. `uga_engine.py gate` and `stats` mutate nothing; no `run` was executed. |

> **Why this report exists rather than a completed registration.** Every object below needs
> a permanent universal identity. Minting one consumes a monotonic counter in
> `00-BOOK/DATA/id-ledger.json` and appends to an append-only history. There is no unmint.
> The closure directive that produced this report forbids autonomous minting, and
> `verify.sh`'s own Stage 7 comment records what happened the one time a verification path
> was permitted to mint: ~140 permanent identities and ~140 portal pages emitted as a side
> effect of a run believed to be read-only. This report is the reviewable form of that act.

---

## §1 — EXACT OBJECT POPULATION

Three disjoint populations. They are separated because their **owners differ**, and a single
mint would register all three under one act.

### P-1 · Pre-existing unregistered documents — **10 objects**

Staged in the index before this closure cycle began. This cycle did not create, modify, or
stage any of them.

| # | Path | Index state |
|---|---|---|
| 1 | `FINAL-UNIVERSAL-INFINITE-EXPANSION-FOUNDATION-CERTIFICATION-REPORT.md` | `A ` |
| 2 | `KNOWLEDGE-CONFIDENCE-COMPLETION-DETERMINATION-REPORT.md` | `A ` |
| 3 | `P4-F-007-TEMPORAL-EVENT-OWNERSHIP-DETERMINATION.md` | `A ` |
| 4 | `RELATIONSHIP-TEMPORAL-VALIDITY-DETERMINATION-REPORT.md` | `A ` |
| 5 | `REQ-28-CORPUS-REGISTRATION-READINESS-REPORT.md` | `A ` |
| 6 | `REQ-43-STORAGE-NEUTRALITY-DETERMINATION-REPORT.md` | `A ` |
| 7 | `UCL-GAP-CLOSURE-REPORT.md` | `A ` |
| 8 | `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md` | `A ` |
| 9 | `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` | `A ` |
| 10 | `UCOS-OMEGA-INFINITY-100-PERCENT-CLOSURE-ROADMAP.md` | `A ` |

These 10 paths produce **31 violations** because each is counted by both `UGA-INV-01`
(`EVERY_OBJECT_HAS_UNIVERSAL_ID`) and `UGA-INV-10` (`EVERY_MUTATION_HAS_AUDIT_EVENT`), with
several carrying more than one unsatisfied condition.

### P-2 · Unregistered test objects — **2 objects**

| # | Path | Index state | Tests | Owner |
|---|---|---|---|---|
| 1 | `engine/tests/ceu/test_context_binding.py` | `A ` (pre-session) | 13 | UCOS-CEU-001 programme |
| 2 | `engine/tests/unit/test_execution_environment.py` | `??` (this cycle) | 117 | UEG-000001 |

**Both are now RUN and NOT silently skipped** — see §7. Their registration is required for
identity and pricing, not for execution.

### P-3 · This cycle's artifacts, on commit — **12 objects**

Untracked today, so outside the governed boundary (`git ls-files --cached`). They enter it
the moment they are committed.

| # | Path | Expected class |
|---|---|---|
| 1 | `00-MASTER/UEG-000001/ueg-declaration.json` | `DATA_OBJECT` |
| 2 | `UCOS-EXECUTION-ENVIRONMENT-ASSESSMENT.md` | `DOCUMENT_ARTIFACT` |
| 3 | `UCOS-EXECUTION-GOVERNANCE-CERTIFICATION.md` | `DOCUMENT_ARTIFACT` |
| 4–11 | `engine/execution_environment/{__init__,__main__,contract,discovery,evidence,fingerprint,gate,model}.py` | `EXECUTABLE_OBJECT` |
| 12 | `engine/tests/unit/test_execution_environment.py` | `TEST_OBJECT` *(also P-2)* |

This report itself and `REG-AUTO-001-REGISTRATION-DETERMINATION-REPORT.md` will add one
further `DOCUMENT_ARTIFACT` each when committed.

**Total distinct objects awaiting identity: 23** (10 + 2 + 12, less the one counted twice).

---

## §2 — CURRENT IDENTITY STATE

Measured from `00-BOOK/DATA/id-ledger.json` and `uga_engine.py stats`, both read-only:

| Quantity | Value |
|---|---|
| ledger version | 1 |
| `by_path` entries | 1 264 |
| `by_object` entries | 4 914 |
| `history` entries | 1 264 |
| total governed objects | 6 176 |
| distinct owners | 276 |

Object-class census, and the mint counters that would move:

| Class | Population | Counter | Current value |
|---|---|---|---|
| `EXECUTABLE_OBJECT` | 1 266 | `ENGINE` | 1 265 |
| `TEST_OBJECT` | 832 | `TESTOBJ` | **831** |
| `DOCUMENT_ARTIFACT` | 1 233 | `EXDOC` | 2 621 |
| `DATA_OBJECT` | 129 | `DATAOBJ` | 130 |
| `EXCLUDED_DOCUMENT` | 2 649 | — | — |
| `CONFIGURATION_OBJECT` | 31 | `CONFIG` | 31 |
| `TOOLING_OBJECT` | 36 | `TOOLING` | 36 |

**None of the 23 objects in §1 holds an identity.** Verified directly against the ledger:

```
engine/tests/ceu/test_context_binding.py           in id-ledger: False
engine/tests/unit/test_execution_environment.py    in id-ledger: False
```

This places **every object in §1 in Category C** of the closure directive's own taxonomy —
*identity missing, no approved mint authority in this cycle* — and therefore this report
rather than an execution.

---

## §3 — PROPOSED ADDITIONS

| Population | Objects | Counters advanced |
|---|---|---|
| P-1 documents | 10 | `EXDOC` (or per-name category) 2 621 → ~2 631 |
| P-2 test objects | 2 | `TESTOBJ` 831 → 833 |
| P-3 engine modules | 8 | `ENGINE` 1 265 → 1 273 |
| P-3 declaration | 1 | `DATAOBJ` 130 → 131 |
| P-3 + reports | 3 | `EXDOC` +3 |

**Identity form.** Sequential within category — the existing registered sibling
`engine/tests/unit/test_verification_intelligence.py` carries `UCOS-TESTOBJ-000820`. The two
test objects in P-2 would therefore receive approximately `UCOS-TESTOBJ-000832` and
`UCOS-TESTOBJ-000833`.

**Ordering is significant and is not this report's to choose.** Identities are assigned in
traversal order, so *which* object receives *which* number depends on when the mint runs and
what is tracked at that moment. Committing P-3 before minting produces a different assignment
than minting first and committing after. The reviewing authority should decide the order
deliberately, because §6 makes it permanent.

---

## §4 — AUTHORITY CHAIN

```
UCKP-LAW-0001  (engine/uckp/law.py)                      supreme constitutional authority
      │  ART-10 execution never owns knowledge · ART-16
      ▼
00-BOOK/DATA/mutation-governance-boundary.json           declares the mutation classes
      │  CORPUS_REGISTRATION → governed by REG-AUTO-001
      │  explicitly NOT governed by verify.sh
      ▼
REG-AUTO-001                                             the registering authority
      │  realized by 00-BOOK/tools/register.sh  (transaction)
      │  and     00-MASTER/UCOS-UGA-001/uga_engine.py run  (mint + surfaces)
      ▼
00-BOOK/DATA/id-ledger.json                              the identity ledger (append-only)
```

**Authorities that are NOT in this chain, and must not be mixed into it:**

| Authority | Owns | Relationship to this act |
|---|---|---|
| `UEG-000001` | execution environment | Prepared this report. Mints nothing, and its gate writes only gitignored paths. |
| `UVI-000001` | verification integrity | Consumes the derived registry. §7 changed how it *reacts* to unregistered objects; it registers none. |
| `UCOS-UGA-001` | object governance measurement | Measures the gap. Its `run` subcommand is the mint, and it is invoked under `REG-AUTO-001`, never on its own account. |

---

## §5 — IRREVERSIBILITY DISCLOSURE

The mint is irreversible in **three independent ways**, and all three must hold in the
reviewer's mind simultaneously:

1. **Counter consumption.** `category_seq` is monotonic. Minting `UCOS-TESTOBJ-000832`
   advances `TESTOBJ` to 832 permanently. Reverting the file does not return the number;
   the next mint takes 833, and 832 becomes a permanent hole.
2. **Append-only history.** `id-ledger.json` carries a 1 264-entry `history`. The mint
   appends. Append-only means no entry is ever removed — that is the property the ledger
   exists to provide, so "undo" is not a supported operation and could not be added without
   destroying the guarantee.
3. **Derived-surface fan-out.** `uga_engine.py run` emits eleven surfaces
   (`00-EXISTENCE-INVENTORY`, `01-EXECUTABLE-OBJECT-REGISTRY`, `02-UNIVERSAL-OBJECT-REGISTRY`,
   `03-AUDIT-UNIVERSE`, `04-RELATIONSHIP-GRAPH`, `05-GOVERNANCE-INVARIANTS`,
   `06-SELF-OBSERVATION`, `07-CERTIFICATION`, `08-OBSERVATION-REGISTRY`, the dashboard, and
   `00-BOOK/DATA/canonical-observation-audit.json`). Nine of the eleven are tracked files.

**A fourth effect the reviewer should expect but which is not part of this population.**
`uga_engine.py run` operates over the **whole tree**, not over a selected subset. It has no
path filter. Running it registers *everything* currently unregistered — the 23 objects here
and anything else in that state at that moment. This is the mechanism behind the ~140-identity
incident recorded in `verify.sh`. **There is no supported way to mint P-2 alone.**

---

## §6 — EXPECTED `id-ledger.json` IMPACT

| Field | Before | After (projected) | Reversible |
|---|---|---|---|
| `by_path` | 1 264 | ~1 287 | **No** |
| `by_object` | 4 914 | ~4 937 | **No** |
| `history` | 1 264 | ~1 287 | **No — append-only** |
| `category_seq.TESTOBJ` | 831 | 833 | **No — monotonic** |
| `category_seq.ENGINE` | 1 265 | ~1 273 | **No — monotonic** |
| `category_seq.EXDOC` | 2 621 | ~2 634 | **No — monotonic** |
| `category_seq.DATAOBJ` | 130 | 131 | **No — monotonic** |

Counts are projections from the §1 population, not measurements of a mint that has not run.
The exact figures depend on what is tracked at execution time — see §3.

---

## §7 — UGA IMPACT

| Invariant | Now | After the mint | Note |
|---|---|---|---|
| `UGA-INV-01` `EVERY_OBJECT_HAS_UNIVERSAL_ID` | **FAIL** — 31 violations / 6 176 measured | expected **PASS** | The 10 documents of P-1 are the entire violation set |
| `UGA-INV-10` `EVERY_MUTATION_HAS_AUDIT_EVENT` | **FAIL** — 31 violations / 4 943 measured | expected **PASS** | Same population, audit-event leg |
| `UGA-INV-02..09` | PASS | PASS | Unaffected |
| `OBS-INV-01..13` | PASS | PASS | Unaffected |
| `CAA-INV-01..` | PASS | PASS | Unaffected |

Two suites assert the UGA gate is wholly green and therefore fail today for the same reason:
`platform/tests/test_observation_universe.py::test_the_governance_gate_enforces_every_invariant`
and
`platform/tests/test_constitutional_authority_alignment.py::test_the_uga_gate_enforces_every_alignment_invariant`.
Both are **downstream** of `UGA-INV-01`; neither has an independent defect.

**What the mint does NOT fix, because it is already fixed.** `UVI-L-08` previously reported
130 tests in no shard, and that was **closed without minting**. The two unregistered test
objects are now admitted to the Test Object Registry by derivation from the collection roots
and are unconditionally selected. Measured after the correction:

```
collectible test objects (registry ∪ disk): 582
unregistered, admitted fail-wide          : 2
serial collection : 12301 tests
shard union       : 12301 tests
in NO shard       : 0
duplicated        : 0
VERDICT: ZERO silent exclusions
```

Registration will give those two objects an identity, an owner and a measured price. It will
not change whether they run — they already do.

---

## §8 — ROLLBACK IMPOSSIBILITY ANALYSIS

| Rollback strategy | Restores the ledger? | Assessment |
|---|---|---|
| `git checkout` the ledger | No | Restores the *file*, not the *authority state*. The identities were issued; a repository elsewhere, a portal page, or an emitted surface may already cite `UCOS-TESTOBJ-000832`. A restored file that no longer records an identity someone holds is worse than the mint: it is a dangling reference the ledger cannot explain. **Also forbidden by the operating constraints of this cycle.** |
| `git revert` the mint commit | No | Same defect, plus an audit record asserting the mint was undone when the numbers remain consumed. |
| Re-run `uga_engine.py run` | No | Idempotent by path, so it re-derives the same surfaces. It cannot decrement a counter. |
| Manual `category_seq` edit | **Prohibited** | Directly forbidden ("do not modify id-ledger.json without approved decision"), and it would break `UOBC-L-03` identity immutability — every id is re-derived from its namespace and local name, so a tampered counter is detectable and refused. |
| Accept and move forward | — | **The only sound strategy.** |

**Conclusion: there is no rollback.** The correct control is not recovery but *review before
execution*, which is what this report is for. The reviewable decision is not "should these
objects have identities" — they must — but **"is the tree in the state we want permanently
recorded?"** Once minted, the boundary is fixed at whatever is tracked at that instant.

**Recommended sequencing**, offered as a determination and not an action:

1. Resolve the 100 staged entries — commit or unstage — so the boundary is intentional.
2. Commit this cycle's P-3 artifacts, so the UEG capability is registered with everything else.
3. Then execute the mint once, under `REG-AUTO-001`, over a deliberate tree.

Minting before step 1 registers a boundary nobody chose.

---

## §9 — DETERMINATION

**NO MINT PERFORMED. NO IDENTITY CREATED. NO REGISTRY MUTATED. `id-ledger.json` IS BYTE-UNCHANGED.**

The population is enumerated (§1), the current state is measured (§2), the impact is projected
(§3, §6, §7), the authority chain is explicit (§4), the irreversibility is disclosed (§5), and
rollback is analysed and found to be impossible (§8).

**This determination is complete and awaits a governed decision by `REG-AUTO-001`.**
