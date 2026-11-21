# REPOSITORY_IDENTITY_ALLOCATION OWNER DECISION RECORD

| Field | Value |
|---|---|
| **ID** | REPOSITORY_IDENTITY_ALLOCATION |
| **Candidate class** | `REPOSITORY_IDENTITY_ALLOCATION` |
| **Candidate subjects** | `00-BOOK/DATA/id-ledger.json#by_object` · `00-BOOK/DATA/id-ledger.json#by_observation` |
| **Candidate authority** | `UCOS-UGA-001` |
| **Named implementation** | `00-MASTER/UCOS-UGA-001/uga_engine.py` |
| **Target register** | `00-BOOK/DATA/mutation-governance-boundary.json` |
| **Authority** | NONE — RECORD PREPARED, EMPTY OF DECISIONS. No class admitted. No option selected. No implementation authorized. |
| **Phase** | Phase-0 — Mutation Governance Boundary Admission |
| **Baseline** | HEAD `36ccd1c4` · branch `integration/recovery-001` · working tree CLEAN |
| **Register state at baseline** | 7 mutation classes · 8 authorities · 9 invariants |
| **Depends on** | `REPOSITORY_IDENTITY_ALLOCATION` Human Ratification Decision Package v2 (derived analysis) |
| **Decision authority** | Mutation Governance Owner |
| **Status** | AWAITING OWNER DECISION — NO FIELD RECORDED |

---

## 1. Decision Metadata

### 1.1 Why this record exists

Two mutation subjects inside `00-BOOK/DATA/id-ledger.json` are governed by no declared
mutation class at baseline `36ccd1c4`:

| Subject | Live entries | Standing in the register at baseline |
|---|---|---|
| `#by_object` | 4888 | Named twice, both times as an exclusion |
| `#by_observation` | 7 | Not named — 0 occurrences |

Both are written by exactly one engine. Neither resolves to a mutation class. Closing
this requires a declaration, and `OWN-REQ-001` (DECLARED-NOT-INFERRED,
`platform/universal_ownership/contracts.py:7-8`) admits only constitutive declared
evidence: no measurement, determination or analysis can supply it. The act therefore
belongs to a named human authority.

### 1.2 What this record is

A form. It captures the Mutation Governance Owner's selections after review of the v2
package. It contains no recommendation, no inferred choice and no default. Every
selectable field is blank. An unrecorded field is unrecorded — it does not resolve to
any value, and no reader may treat absence as a selection.

### 1.3 Evidence available at time of decision

| Locator | Establishes |
|---|---|
| `uga_engine.py:265-303` · `:476-489` | Sole writer of each subject |
| `aee_engine.py:1601-1620` · `rib_engine.py` | Readers that fail closed — "minting is UCOS-UGA-001's, and a second minter would be a second authority" |
| `constitutional-authority-alignment.json:205-213` | `UCOS-OBSERVATION-UNIVERSE-001` `may_never_own` "a second identity authority" |
| `constitutional-authority-alignment.json:836-839` · `:342` | `CAA-INV-04` EXACTLY_ONE_IDENTITY_AUTHORITY · `mint_markers: ["category_seq"]` |
| `mutation-governance-boundary.json` invariants 1-9 | The nine invariants the admission is measured against |
| `mutation-governance-boundary.json:160` · `:316` | The two measured claims that become false on admission |
| `engine/registry_coverage/declarations.json:55-68` | Pre-existing contradiction — `by_object` assigned `mutation_class: CORPUS_REGISTRATION` |
| `platform/repository_intelligence/mutation_classification.py` | Two-sided `validate_rule_coverage`; ordered-precedence evaluation; fail-closed terminal |
| `platform/tests/test_mutation_classification.py:107` | Assertion that changes if R-03 is narrowed |
| `verify.sh:395-396` · `uga_engine.py::cmd_gate` | Verification plane calls `gate`; `gate` calls `build(mint=False)` |
| `uga-declaration.json` `ids_preserved` · `uga_engine.py:261-263,305-307` | Append-only; an identity once minted is never reissued or retired |
| `generated-artifact-registry.json` | 0 of 345 canonical artifacts declare the target register as an input |

---

## 2. Decision Questions

Five questions are placed before the Mutation Governance Owner. They are independent:
a selection on one does not determine a selection on another.

| ID | Question |
|---|---|
| **D-1** | Is `REPOSITORY_IDENTITY_ALLOCATION` admitted into `mutation-governance-boundary.json` as a mutation class governing `#by_object` and `#by_observation` under authority `UCOS-UGA-001`? |
| **D-2** | Which disposition applies to invariants INV-7 and INV-8, whose statements quantify over tracked artifacts while the register's `$subject_domain` declares the domain to be mutation subjects? |
| **D-3** | Does the admitted class enumerate `category_seq` in its `examples` array? |
| **D-4** | Do the four coherence items (A4 R-03 narrowing · A5 stale-claim correction · A6 invariant restatement · A9 registry-coverage correction) land inside the atomic admission commit, or are they deferred? |
| **D-5** | Is the irreversibility of the governed act acknowledged as a condition of the decision? |

D-2 is answerable independently of D-1 only in the negative direction: a disposition may
be recorded without admitting the class, but the admission's semantic effect depends on
which disposition is in force. D-3 has effect only if D-1 is recorded as admission.

---

## 3. Available Options

Options are listed in declared order. Order carries no preference, no ranking and no
scoring.

### D-1 — Admission

| Option | Statement |
|---|---|
| **D-1-A** | Admit the class as specified: two subjects, authority `UCOS-UGA-001`, implementation `uga_engine.py` |
| **D-1-B** | Do not admit. The two subjects remain governed by no declared class |
| **D-1-C** | Defer, pending a condition the owner states in the rationale field |

### D-2 — Invariant disposition (applies jointly to INV-7 and INV-8)

Current statements, verbatim from the register:

- **INV-7** — "Every tracked artifact resolves to exactly one mutation class. Failure: unclassified artifact."
- **INV-8** — "No artifact resolves to more than one mutation class. Failure: authority ambiguity."

| Option | Statement |
|---|---|
| **D-2-A** | Retain both statements unchanged |
| **D-2-B** | Retain both statements and add an artifact-specific exception for `id-ledger.json` regions |
| **D-2-C** | Restate both over the mutation-subject domain, with one scoping sentence stating that a consumed shared resource is not an independently mutable subject |
| **D-2-D** | Hybrid — restate both over the mutation-subject domain and retain a path-level statement as a derived corollary |

### D-3 — `examples` array representation

| Option | Statement |
|---|---|
| **D-3-1** | `examples` contains the two region locators only. `category_seq` is not enumerated by the class |
| **D-3-2** | `examples` contains the two region locators and `category_seq` |

### D-4 — Coherence items

| Option | Statement |
|---|---|
| **D-4-A** | Coherence closure — A4, A5, A6, A9 land inside the atomic admission commit |
| **D-4-B** | Deferred reconciliation — A4, A5, A6, A9 are deferred to separately recorded work |
| **D-4-C** | Split — the owner names per item which land now and which are deferred, in the field provided |

### D-5 — Irreversibility acknowledgement

| Option | Statement |
|---|---|
| **D-5-A** | Acknowledged — the authority conferred governs an append-only act with no reverse, and class admission does not create rollback capability for that act |
| **D-5-B** | Not acknowledged |

---

## 4. Owner-Selected Fields

```
## OWNER DECISION — REPOSITORY_IDENTITY_ALLOCATION

D-1  Admission
     [ ] D-1-A  Admit as specified
     [ ] D-1-B  Do not admit
     [ ] D-1-C  Defer

D-2  Invariant disposition (INV-7 and INV-8, jointly)
     [ ] D-2-A  Retain both statements unchanged
     [ ] D-2-B  Retain both, add artifact-specific exception
     [ ] D-2-C  Restate both over the mutation-subject domain
     [ ] D-2-D  Hybrid — subject domain plus retained path-level corollary

D-3  Examples array representation
     [ ] D-3-1  Two region locators only; category_seq not enumerated
     [ ] D-3-2  Two region locators and category_seq

D-4  Coherence items (A4 · A5 · A6 · A9)
     [ ] D-4-A  Coherence closure — all four inside the atomic commit
     [ ] D-4-B  Deferred reconciliation — all four deferred
     [ ] D-4-C  Split, as named below:
                A4 R-03 narrowing            [ ] now   [ ] deferred
                A5 stale-claim correction    [ ] now   [ ] deferred
                A6 invariant restatement     [ ] now   [ ] deferred
                A9 registry-coverage fix     [ ] now   [ ] deferred

D-5  Irreversibility acknowledgement
     [ ] D-5-A  Acknowledged
     [ ] D-5-B  Not acknowledged

Owner Rationale (required — constitutional basis for the selections recorded above):
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

Conditions or Reservations (optional):
_______________________________________________________________________________
_______________________________________________________________________________
```

No box above is pre-marked. No option is a default. An unmarked question is
**NOT RECORDED**, and no downstream act may proceed on an unrecorded question.

---

## 5. Consequence Mapping

Consequences of each option, stated without preference.

### D-1

| Option | Consequence |
|---|---|
| **D-1-A** | The two subjects resolve to a declared class with a named authority. H-06 Option B invariants 4 and 5 become satisfiable for `UCOS-UGA-001` for the first time. The register's lines 160 and 316 become false statements until corrected (see D-4/A5). The pre-existing contradiction at `registry_coverage/declarations.json:66` becomes a conflict between two live claims rather than one claim and one silence |
| **D-1-B** | 4895 permanent identities remain governed by no declared class. `#by_observation` remains unnamed in the register. The `registry_coverage` contradiction remains unenforced and undisclosed in the boundary register. `EX-018`, when built, measures these subjects as UNRESOLVED / FAILS CLOSED. H-06 Option B invariants 4 and 5 remain unsatisfiable for `UCOS-UGA-001` |
| **D-1-C** | Baseline standing persists unchanged for the duration of the deferral. No consequence beyond D-1-B accrues, and none is discharged |

### D-2

| Option | Consequence |
|---|---|
| **D-2-A** | Both statements remain literally satisfied: path subjects and region subjects are disjoint by construction, so each subject resolves exactly once. Authority-by-presentation persists — a mutation presented as the file path resolves to `REG-AUTO-001`, which disclaims the regions. INV-8's declared failure mode, "authority ambiguity," remains unmeasured by INV-8 |
| **D-2-B** | Both statements remain satisfied via a named exception for one artifact. Future multi-region artifacts require further exceptions |
| **D-2-C** | Invariant domain matches rule domain and the register's declared `$subject_domain`. `category_seq` becomes askable as a subject, which the scoping sentence resolves by declaring a consumed resource not to be an independently mutable subject. The target-versus-actual gap the register already declares — root-level `*.md` and most `00-MASTER/**/*.json` expected UNRESOLVED — is unchanged |
| **D-2-D** | As D-2-C, plus a retained path-level statement that must be kept synchronised with the subject-level statements |

### D-3

| Option | Consequence |
|---|---|
| **D-3-1** | No subject is enumerated by two classes. INV-8 standing is unchanged from baseline. `CORPUS_REGISTRATION`'s existing enumeration of `category_seq` remains a descriptive asymmetry with no resolution effect, addressable separately (B1) |
| **D-3-2** | `category_seq` is enumerated by two classes. An INV-8 subject/class overlap is created inside the admission commit, and two authorities become reachable for one counter |

### D-4

| Option | Consequence |
|---|---|
| **D-4-A** | No commit exists in which the register carries a false measured claim, asserts `REG-AUTO-001` governs regions it disclaims, or disagrees with `registry_coverage/declarations.json` |
| **D-4-B** | Lines 160 and 316 stand as false statements from the admission commit onward. R-03 continues to claim the whole file. The `registry_coverage` contradiction persists in its baseline condition — unenforced, since `matrix.py` only reads and echoes the field, no test asserts its value, and `registry_coverage` is not invoked from `verify.sh` |
| **D-4-C** | As selected per item |

### D-5

| Option | Consequence |
|---|---|
| **D-5-A** | The record carries the owner's acknowledgement that an identity allocated under this class cannot be withdrawn, renumbered or reassigned |
| **D-5-B** | The record carries no such acknowledgement. Any subsequent act relying on one has no basis in this record |

### Consequences that do not vary by option

Measured at baseline and unchanged by any selection above:

- **Certification** — 0 of 345 canonical artifacts declare the target register in
  `input_closure`; the register is not a `canonical_path`; no schema in
  `00-BOOK/SCHEMAS/` validates it. No certification digest covers it. Phase 8 fixed
  point, Phase 9 pristine clone and AEE convergence are unaffected.
- **Admission reversibility** — the admission is a text change in tracked files, with no
  data migration, no identity minted and no ledger byte written. It is revertible.
- **Governed-act reversibility** — `class admission does not create rollback capability
  for the governed act`. `uga-declaration.json` `ids_preserved`: "Nothing is re-minted,
  renumbered, reissued or retired… an identity once minted never changes."
- **Atomicity** — `validate_rule_coverage` refuses both directions and runs before the
  rule loop, so register entry, rule, predicate and test must land together. A partial
  landing returns `ERROR` for every subject.
- **Not decided here** — H-06 ratification, `gate_mode` assignment, `EX-017`, `EX-018`,
  `#by_execution`, `by_observation` audit coverage, and OMA-01.

---

## 6. Signature and Record Section

```
Decision Authority:        Mutation Governance Owner

Decision Recorded By:      ___________________________________

Role / Governance Title:   ___________________________________

Date:                      ___________________________________

Baseline at Decision:      HEAD ______________  branch ______________________

Working Tree at Decision:  [ ] CLEAN    [ ] DIRTY  (if dirty, state scope below)
                           ___________________________________

Decision Reference:        ___________________________________

Superseded Record:         ___________________________________  (or NONE)
```

The record is unsigned. An unsigned record carries no decision, and no field in
Section 4 may be read as recorded until this section is completed by a named human
authority with governance responsibility for mutation boundary policy.

The authority may not delegate the selection to an assessment process, a determination
document, or a derived analysis. All prior work on this admission is evidence
preparation only.

---

## 7. Post-Decision Execution Boundary

```
DECISION
│   Records D-1 through D-5 and the owner rationale.
│   Authorizes no repository change.
│
▼
RATIFICATION VALIDATION
│   Confirms the recorded selections are internally consistent
│   (D-3 evaluated against the D-2 disposition in force).
│   Authorizes no repository change.
│
▼
IMPLEMENTATION AUTHORIZATION
│   Explicit, separate act. Names: allowed files, allowed owners,
│   expected changes, and the revert path for the admission text.
│   Does not begin until ratification validation is complete.
│
▼
EXECUTION — ATOMIC ADMISSION COMMIT
│   Forced set, per the two-sided coverage check:
│     mutation_classes[] entry · authorities[] entry ·
│     classification_rules.rules[] entry · predicate +
│     RULE_PREDICATES entry · test alignment
│   Conditional set, per D-4:
│     A4 R-03 narrowing · A5 lines 160/316 · A6 invariant
│     restatement · A9 registry-coverage correction
│
▼
VERIFICATION
    Classifier resolves both subjects to the admitted class under the
    named authority; the terminal remains fail-closed for undeclared
    subjects; verify.sh stages pass with no allocation performed.
```

### Outside this boundary

The following are not authorized by any field in this record, and no selection above
extends to them:

| Item | Standing |
|---|---|
| `H-06` Option A/B ratification | Exogenous owner act. Unrecorded at baseline |
| `gate_mode` for `uga-declaration.json` | Requires H-06 ratification |
| `EX-017` migration | After-admission consequence |
| `EX-018` conformance gate | After-admission consequence |
| `#by_execution` admission | Excluded — 0 live entries, separate authority label |
| `by_observation` audit coverage | 0 of 7 audited; outside UGA-INV-10's denominator |
| **OMA-01 execution** | Not authorized. Requires the admission, H-06 ratification and a declared mode. Post-admission standing is AUTHORIZED IN CLASS — NOT AUTHORIZED IN MODE |
| Any `uga_engine.py run` invocation | Not authorized. Allocates permanent, never-reissued identities |

No step may be skipped. Authorization from one step does not extend to the next.

---

## 8. Final Status

**AWAITING OWNER DECISION — NO FIELD RECORDED**

---

No class admitted.
No option selected.
No invariant amended.
No implementation authorized.
No mutation executed.

REPOSITORY_IDENTITY_ALLOCATION decision pending.
