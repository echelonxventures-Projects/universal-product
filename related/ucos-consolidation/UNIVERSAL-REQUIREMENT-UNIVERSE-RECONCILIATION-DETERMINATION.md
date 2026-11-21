# UNIVERSAL REQUIREMENT UNIVERSE RECONCILIATION DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UNIVERSAL-REQUIREMENT-UNIVERSE-RECONCILIATION-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` |
| AUTHORITY | **NONE — DERIVED TRUTH.** Admits no requirement, mints no requirement identifier, creates no register, converges no population, and creates no UREE identity. |
| DISPOSITION | **DETERMINATION ONLY.** No requirement surface modified. |
| SUBJECT | Reconciliation of the `REQ-NN` tracker, the `RR-*` records and the `UCOS-URR-001` proposal; and the design of a Universal Requirement Universe lifecycle |
| BASELINE | HEAD `03179308f5cb` · branch `integration/recovery-001` · working tree unchanged |
| MODE | Read-only measurement. No registry mutation. No identity minting. No certification claim. |
| GOVERNING INSTRUMENTS | `UCOS-UFC-001` **UFC-16** · `CEP-002` 14.2 · `00-MASTER/UCOS-URR-001/00-URR-DISPOSITION-DETERMINATION.md` · `CMG-000001` LXXVI.6 (admission is visible, reinterpretation is not) |
| REFUSES | Creating UREE identity. Minting requirement IDs. Declaring either population authoritative over the other. Demoting the `REQ-NN` obligations. |

> **Headline.** The two populations are **not duplicates — they are different object classes measuring different subjects**, and the evidence for that is structural rather than interpretive: different derivation (hand-authored vs generated), different scope (session vs repository), different identifier grammar, and incompatible status models (one axis vs seven). They **can and should coexist as distinct lifecycle objects**, joined by a declared relation rather than merged. But the directive's instruction that *"existing requirements become discovered historical population only"* is **safe for the 549 and unsafe for the 49** — the 49 are live normative obligations, two of which are open, and demoting them to history would discard the only surface that records what this repository still owes.

---

## 1. Evidence

| Question | Command / file | Result |
|---|---|---|
| Population A | `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md:138-160` | **49**; `CERTIFIED 43 · GOVERNED CLOSURE 0 · OPEN GAP 2 (REQ-28, REQ-43) · SUPPORTED 2 · NOT APPLICABLE 2` |
| Population A grammar | same | `REQ-01..REQ-50`, non-contiguous (`REQ-07` absent) |
| Population A scope | same, line 3-6 | *"every requirement discussed across this session's full arc"* — session-bounded |
| Population A closure claim | line 149 | *"No requirement present in any prior session document is absent from this index."* — backward-looking only |
| Population B | `00-MASTER/UAKOS-CLOSURE-009/requirements.json` | `requirement_total: 549`, records 549, `determination: ASSIMILATION-INCOMPLETE` |
| Population B grammar | same | `RR-<concept_id>` (e.g. `RR-AF-3`) — derived from a concept identifier, not allocated |
| Population B derivation | same, `inputs{}` | generated from `00-MASTER/UAKOS-CLOSURE-008/assimilation.json`, `00-BOOK/DATA/artifacts.json`, `BASELINE-001/baseline.json`, `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json`, `00-MASTER/UCOS-RIB-001/rib.json` |
| Population B status model | same | **seven independent axes** — `implementation_status`, `validation_status`, `verification_status`, `certification_status`, `runtime_status`, `maturity`, `coverage` |
| Population B assimilation | same | `fully: 140` · `partially: 409` · `not: 0` · `reused_concepts: 549` · `created_concepts: 0` |
| Concept population it derives from | `00-MASTER/UAKOS-CLOSURE-002/closure.json` | `concept_total: 549` · `determination: CLOSED` · `dispositions {IMPLEMENTED 335, DEFERRED 176, SPECIFIED 25, REJECTED 13}` |
| Proposal C | `00-MASTER/UCOS-URR-001/urr-declaration.json` | `"standing": "PROPOSED — NOT ADMITTED"`; declares 37 keys incl. `modal_lexicon`, `anchor_grammar`, `inference_laws` (13), `gap_classes` (19), `closure_conditions` (12) |
| Proposal C integration surface | `00-URR-DISPOSITION-DETERMINATION.md` | `urr_engine.py` ABSENT · `urr-gate.yml` ABSENT · unit test ABSENT · Makefile targets **0 of 5** · declaration untracked |
| Why C was refused | same | *"a second register plane over the 541 requirements already registered by `00-MASTER/UAKOS-CLOSURE-009` would be the competing measurement `UCOS-UFC-001` UFC-16 forbids"* |
| Count drift | C vs B | C says **541**; B says **549**. Unexplained. |
| Join key | inspection of both | **None.** No `REQ-` token in `requirements.json`; no `RR-` token in the index. |

**Decisive structural evidence that B is derived, not authored:** `requirements.json` reports `reused_concepts: 549, created_concepts: 0`. Every `RR-*` record corresponds to a pre-existing concept; none was originated as a requirement. Population B is a **projection of the concept universe wearing a requirement-shaped lifecycle**. Population A contains obligations that were *authored* as obligations. These are categorically different acts.

---

## 2. Current state and conflicts

### 2.1 Are they separate concepts or duplicates?

**Separate concepts.** Five independent discriminators, none interpretive:

| Discriminator | A (`REQ-NN`) | B (`RR-*`) |
|---|---|---|
| Subject | what the repository **must do** (obligation) | what the repository **contains** (concept, lifecycle-assessed) |
| Origin | authored as an obligation | derived from a concept (`created_concepts: 0`) |
| Identifier | allocated ordinal, non-contiguous | deterministic function of `concept_id` |
| Scope | one session's discussion arc | whole repository corpus |
| Status model | one status per requirement | seven orthogonal axes per record |

Two further asymmetries confirm it. A carries `NOT APPLICABLE` (2 items) — a verdict that presumes a *demand* which no surface can satisfy; B has no such state because a concept that exists cannot be inapplicable. And B carries `runtime_status: NO-RUNTIME-EVIDENCE` across the population — a measurement axis A does not possess.

**Conclusion:** the 49 and the 549 are not two counts of one population. They are one obligation register and one derived concept-lifecycle register. `UFC-16` is therefore **not currently breached** — but it is **not currently satisfied either**, because nothing in the repository *declares* the subjects distinct. The violation is the silence, not the numbers.

### 2.2 Which is authoritative?

Neither, over the other. Authority is subject-scoped:

- For *"what obligations does this repository still owe?"* → **A**. It is the only surface carrying `OPEN GAP` with owners and blocking reasons (`REQ-28`, `REQ-43`).
- For *"what is the lifecycle state of everything this repository contains?"* → **B**. It is machine-readable, generated, and the only surface with per-axis evidence.
- For neither question → **C**. `UCOS-URR-001` is unadmitted with a measured-absent surface, and remains so.

### 2.3 Can they coexist as different lifecycle objects?

**Yes — and this is the recommended model.** The precedent is already load-bearing in this repository: `engine/knowledge/model.py` makes `decision`, `principle`, `rule`, `constraint`, `policy` and `law` *distinct kinds of one governed object type*, and `engine/nucleus/law.py` keeps `StructuralRole` as a *checked projection* of the CEU classifications rather than a rival. Coexistence with a declared relation is the established shape; merging is not.

### 2.4 Conflicts recorded

| ID | Conflict | Grade |
|---|---|---|
| **RC-C-01** | Two populations with no declared subject distinction. `UFC-16` neither satisfied nor breached — undisclosed. | **CONFIRMED** |
| **RC-C-02** | Third count in circulation: 541 (C) vs 549 (B). Unexplained by anything located. | **CONFIRMED** |
| **RC-C-03** | Three views of A disagree on ≥7 identifiers (`REQ-02/06/14/34/35/39/50`); traceability matrix reports `GOVERNED CLOSURE 5` where the index reports `0`. | **CONFIRMED** |
| **RC-C-04** | A has no intake rule — no admission grammar, no reserved `REQ-51`, no mechanism by which a discovered obligation enters. | **CONFIRMED** |
| **RC-C-05** | B's own verdict is `ASSIMILATION-INCOMPLETE` with most baseline conditions FAIL (`BC-01` 314/549 present in code; `BC-06` 0 of 314 carry determinism evidence). | **CONFIRMED** |
| **RC-C-06** | Ownership in B is inferred for **406 of 549** (`RG-B01 CANONICAL-OWNERSHIP-INFERRED`). | **CONFIRMED** |
| **RC-C-07** | The directive's "existing requirements become discovered historical population only" would demote A's two live open obligations to history. | **CONFIRMED** |

---

## 3. Design — Universal Requirement Universe

The requested ten-stage lifecycle, mapped to located owners. **Six of ten exist in some form; three are absent; one is blocked.**

| # | Stage | State | Located owner / gap |
|---|---|---|---|
| 1 | Requirement Discovery | **PARTIAL** | `UAKOS-CLOSURE-002` scans 3,324 markdown + 24 docx uploads across 6,176 tracked files. Obligation-shaped discovery (modal lexicon, anchor grammar) is declared in C and **unbuilt**. |
| 2 | Requirement Candidate | **ABSENT** | No candidate state exists in any surface. B's records are admitted concepts, not candidates. |
| 3 | Normalized Requirement Object | **ABSENT** | No normalizer. This is the prerequisite for stages 4–5 and its absence makes them unsound. |
| 4 | Existing Requirement Relationship Resolution | **ABSENT for requirements** | Mechanism exists for knowledge: content-hash equality (`PR-02` Knowledge Once) and `ukda_content_hash_duplicates` (0). Never applied to requirements. |
| 5 | Canonical Requirement Admission | **PARTIAL** | B admits by generation (`REUSED`, `created_concepts: 0`). A has no admission path at all (RC-C-04). |
| 6 | Master Implementation Plan Binding | **ABSENT** | No requirement→plan edge exists in either direction. MIP v2 has no requirement input. |
| 7 | Execution | **EXISTS** | `EVOLUTION-001` wave lifecycle; work packages `W01..W10` in B. |
| 8 | Validation | **EXISTS** | B's `validation_status` / `verification_status` axes; `verify.sh`. |
| 9 | Certification | **EXISTS, constrained** | B's `certification_status`; `CF-C4` forbids self-certification; executable-evidence rule binds. |
| 10 | Evolution History | **PARTIAL** | Append-only hash-chain mechanism exists (`ucda_engine.py`, `canonical-knowledge-history.json`); not wired to requirements. |

### 3.1 The canonical relationship model required

One relation, one direction, no merge:

```
RR-<concept_id>            REQ-NN
(descriptive: what exists) (normative: what is owed)
        │                        │
        └──── satisfies ────────►│      many-to-many
                                 │
             evidences ─────────►│      (an RR record may evidence
                                        an obligation without satisfying it)
```

Properties this relation must hold:

- **Directional.** `RR → REQ`. A concept may satisfy an obligation; an obligation never satisfies a concept.
- **Non-total in both directions, and both partialities are meaningful.** An `RR` satisfying no `REQ` is ordinary (most of the 549). A `REQ` satisfied by no `RR` is a **gap** — and is precisely how `REQ-28` and `REQ-43` should surface mechanically instead of by hand.
- **Counts derived, never written.** Under `UFC-16`, each population's count is written by exactly one surface; the relation's cardinality is computed.
- **Neither side renumbered.** `REQ-NN` ordinals and `RR-<concept_id>` derivations are both stable; the relation is additive.

This relation is what makes the two populations *reconciled* rather than merely *coexisting*, and it is the smallest artifact that discharges `UFC-16` without merging.

### 3.2 On "existing requirements become discovered historical population only"

Split the instruction, because it is true of one population and harmful to the other:

- **For B (549): already true, and correctly so.** `created_concepts: 0` means B *is* a discovered population by construction. Nothing changes.
- **For A (49): must not apply.** A holds two live obligations. `REQ-28` is blocked on a `CEP-002` Article 28 decision enumerating 192 documents — governance, not code. `REQ-43` was assessed and **explicitly not recommended** for implementation. Reclassifying these as history would delete the only record of what remains owed, and would be exactly the *reinterpretation* `CMG-000001` LXXVI.6 forbids: *"Reinterpretation is invisible to validation; admission is visible."*

**Recommended reading of the directive's intent:** A ceases to be a *ceiling* — it stops being the complete enumeration of what may ever be required — without ceasing to be a *live obligation register*. That is achieved by giving A an intake path (RC-C-04), not by demoting it.

---

## 4. Decision options

| Option | Description | Assessment |
|---|---|---|
| **A — Declare distinct subjects, add the `satisfies` relation** *(recommended)* | Record that the two populations measure different subjects; add the relation; give the obligation register an intake path. | Discharges `UFC-16` without merging. No identifier minted. Reversible. Makes `REQ-28`/`REQ-43` mechanically visible. |
| **B — Merge into one population** | Collapse A into B or B into A. | **Rejected.** Destroys the obligation/concept distinction; requires renumbering one side; and the seven-axis vs one-axis status models are not reconcilable without information loss. |
| **C — Admit `UCOS-URR-001`** | Build the refused engine. | **Rejected.** Creates the third plane `UFC-16` forbids, and the directive forbids UREE identity. |
| **D — Declare A historical, B authoritative** | Follow the directive literally. | **Rejected as stated.** Loses the two live open obligations (RC-C-07). Acceptable only if the obligations are first migrated into a surface that carries obligation semantics — which does not exist. |
| **E — Defer entirely** | Wait for owner decision. | Leaves RC-C-01 undisclosed and the stale views (RC-C-03) citable. |

**Recommended direction: A**, with two sequencing constraints. Normalization (stage 3) must precede relationship resolution (stage 4), or duplicate and conflict detection are unsound. And the population-authority declaration is an **owner decision** — the `UCOS-URR-001` disposition reserves it under `CEP-002` 14.2, and the companion authority determination records that no ratifying authority is located inside the repository, so it routes to you.

---

## 5. Validation approach

| Obligation | Measurement |
|---|---|
| Subjects are declared distinct | A machine-readable statement names both populations, their subjects and their writing surface; a check fails if any third surface writes either count |
| One population, one measurement | Each count written once; all other appearances derived and compared, failing on divergence |
| The relation is sound | Every `satisfies` edge resolves to an existing `RR` and an existing `REQ`; dangling edges fail closed |
| Unsatisfied obligations surface mechanically | Count of `REQ` with no satisfying `RR` is computed; the expected value is the disclosed open-gap set, not a literal |
| Normalization is deterministic | Identical text yields identical normal form and hash across runs; no clock, no locale |
| Duplicate detection reuses existing mechanism | Hash equality over normal forms, as `ukda_content_hash_duplicates` already does for knowledge |
| Conflict detection is real | Each conflict names both subjects and a disposition; unresolved conflicts block and are never defaulted |
| Intake is exercisable | Admit a synthetic requirement into a **copy** of each register per run; prove the original populations unmoved (`ISD-L-11` two-way ratchet) |
| No cardinality assertion | No test asserts 49, 541 or 549 unless cardinality is itself the invariant (the rule from commit `3e424148`) |
| Ownership inference reduces | `RG-B01` (currently 406/549) measured against a declared target, remainder disclosed |

---

## 6. Risk assessment

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| RU2-R-01 | Following the directive literally demotes A and loses `REQ-28`/`REQ-43` | **HIGH** | Split the instruction (§3.2). A loses ceiling status, not obligation status. |
| RU2-R-02 | Merging destroys the obligation/concept distinction and forces renumbering | **HIGH** | Relation, not merge. |
| RU2-R-03 | Building any requirement engine re-enacts the refused `UCOS-URR-001` | **HIGH** | No engine. Extend `EVOLUTION-001`'s classification register when authorised. |
| RU2-R-04 | Normalization implemented heuristically or by model inference, making it non-deterministic and unreplayable | **HIGH** | Pure deterministic function or not built. Replay-compare across runs. |
| RU2-R-05 | The 541/549 drift is papered over | **MEDIUM** | Explain or correct before any relation is declared; a relation built on an unexplained count inherits the error. |
| RU2-R-06 | Stale views (RC-C-03) remain citable and future work quotes the favourable one | **MEDIUM** | Withdraw or regenerate the non-authoritative views; treat as blocking for any count claim. |
| RU2-R-07 | A candidate state is treated as an admitted requirement, manufacturing scope | **MEDIUM** | Candidates carry a distinct lifecycle state; admission only by owner act. |
| RU2-R-08 | Requirement completeness claimed while B reports `ASSIMILATION-INCOMPLETE` and `BC-01..BC-06` FAIL | **HIGH** | No completeness claim until those conditions are addressed or disclosed per requirement. |
| RU2-R-09 | The relation is declared before subjects are declared distinct, so it appears to be a merge | **MEDIUM** | Declaration first, relation second. |

---

## 7. Acceptance criteria

1. A machine-readable declaration names both populations, states their distinct subjects, and names the single surface that writes each count. **Currently absent — this is the `UFC-16` obligation.**
2. The 541 / 549 discrepancy is explained or corrected. **Currently unexplained.**
3. The `satisfies` / `evidences` relation exists, resolves on both endpoints, and its cardinality is derived rather than written.
4. Every `REQ` with no satisfying `RR` is computed, and the result reproduces the disclosed open-gap set without a hardcoded expectation.
5. The obligation register has a named, exercisable intake path; a discovered obligation can enter without a hand edit to a tally. **Currently: no intake rule exists.**
6. `REQ-28` and `REQ-43` retain obligation status and their existing dispositions. Neither is reclassified as historical.
7. Normalization is deterministic and replay-verified.
8. No requirement identifier is minted; no `RR-*` or `REQ-NN` is allocated by this work. **Verifiable: no surface written.**
9. No UREE identity, engine, gate or Makefile target is created. `urr_engine.py` remains absent.
10. `RG-B01` inferred-ownership count is reduced against a declared target with the remainder disclosed. **Currently 406 of 549.**
11. Working tree unchanged; no requirement surface written. **Verified at close.**

---

## 8. Refusals

- Creating UREE identity, engine, gate or target. Not performed.
- Minting any requirement identifier.
- Declaring either population authoritative over the other. Subject-scoped authority is recommended; the ratifying act is an owner decision.
- Explaining the 541/549 delta. Measured, not resolved; no located explanation exists and none is invented.
- Executing `requirement_engine.py`, `closure_engine.py --gate` or `make closure009-replay`. Refused: those paths write tracked registers.
- Correcting the stale traceability matrix or gap register. Located artifacts; correction is a governed act.
- Reading all 549 `RR-*` records. Aggregate fields, one sample record and the declared gap classes were read; per-record verification was not performed. Any claim about an individual `RR` record is therefore **not** supported by this determination.
- Asserting `UAKOS-CLOSURE-002`'s concept population is complete. Its own disclosure records `scan_mode: repo-only (declared)` with the external corpus unscanned — see the companion feedback-loop determination.

---

## 9. Determination

**NOT DUPLICATES — TWO OBJECT CLASSES, RECONCILABLE BY RELATION, NOT BY MERGE.**

The reconciliation the directive asks for does not require choosing a winner, and choosing one would destroy information. The 49 are authored obligations; the 549 are derived concept-lifecycle records that, by their own `created_concepts: 0`, originate nothing. They answer different questions and carry incompatible status models. They can coexist — and the repository already uses exactly this pattern elsewhere, keeping distinct kinds of one governed object type and keeping projections as checked views rather than rivals.

What `UFC-16` actually demands here is not convergence but **disclosure**: say that the subjects differ, name the single writer of each count, and join them with a directional relation. That relation then does useful work immediately — an obligation with no satisfying record becomes a computed gap rather than a hand-maintained note, which is the mechanical form of what `REQ-28` and `REQ-43` are today.

One correction to the directive: existing requirements should stop being a **ceiling**, not stop being **obligations**. Demoting the 49 to historical population would discard two live, owned, open items and would be reinterpretation rather than admission.

The remaining blocker is unchanged and is not a repository process: the population-authority declaration is an owner decision, and the companion authority determination records that no competent ratifying authority is located within the repository.

**VERDICT: `DETERMINATION-COMPLETE · POPULATIONS RECONCILED IN DESIGN · AWAITING OWNER DECISION · IMPLEMENTATION-NOT-AUTHORIZED`**

No register created, no requirement admitted, no identifier minted, no population converged. Working tree unchanged.
