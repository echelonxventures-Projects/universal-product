# H-06 R-4 GRANDFATHERING POLICY OWNER DECISION VALIDATION DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-R4-GPODVD |
| **Authority** | READ-ONLY VALIDATION. Validates the recorded owner decision. Authorizes nothing. |
| **Phase** | Foundation Closure — Gate Purity — P-3 Resolution |
| **Validates** | `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` entry **E-1** |
| **Subject sha256 (post-entry)** | `0f124df118987ca7a07c204663f7230c4220b82f0fa4d2ec08b2d958bb31f763` · 389 lines |
| **Subject sha256 (pre-entry)** | `707f56abbf9f0003ea089438881389fbe174fe2f22fd67972379b1e46df0c1ae` · 369 lines |
| **Baseline** | HEAD `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · **0 commits created by this entry** |
| **Produced** | 2026-08-16 |
| **Determination** | **PASS — 9 of 9 requested checks · with 2 disclosed findings (F-A, F-B) that do not invalidate the recorded selection** |

---

## 1. Pre-Validation Performed Before Recording

Read-only, executed before any write.

### 1.1 Canonical Decision Record

| # | Check | Observed | Result |
|---|---|---|--:|
| 1.1.1 | Filename is the canonical decision surface | `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` | **PASS** |
| 1.1.2 | SHA256 before entry | `707f56abbf9f0003ea089438881389fbe174fe2f22fd67972379b1e46df0c1ae` | **RECORDED** |
| 1.1.3 | Line count before entry | **369** | **RECORDED** |
| 1.1.4 | All five decision fields unmarked | mark-agnostic scan `^\s*\[[^ ]\]` → **0 matches** | **PASS** |
| 1.1.5 | No existing signature | `Selected By` · `Date` · `Signature` all `________________` | **PASS** |
| 1.1.6 | No pre-filled or inferred value present | 0 marks, 0 populated conditional fields | **PASS** |

### 1.2 Non-Canonical Surfaces — Pre-Entry

| # | Surface | SHA256 | Expected by record §V-6 | Result |
|---|---|---|---|--:|
| 1.2.1 | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` (R-4 **r2**) | `3f0abe615d32de48a4f66a0e536f98290ddc2d392a2a8a4d0af45b887966de15` | `3f0abe615d32de48…` | **MATCH** |
| 1.2.2 | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.pre-r2.md` | `074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb` | `074582134dbdd248…` | **MATCH** |
| 1.2.3 | `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` | `4452b67898c219f8334290fb3bb1512aec999915d7a71c2b2c7b2e86ff9152a3` | evidence only | **RECORDED** |
| 1.2.4 | `H-06-R4-CORRECTION-EXECUTION-VALIDATION-DETERMINATION.md` | `dd93856fd168e1546e12f2b5df3ec21306c0afb7b60972d0f123c899872958f3` | evidence only | **RECORDED** |
| 1.2.5 | R-4 r2 §7 decision fields (lines 268–308) | mark scan → **0 marks** | 0 | **PASS** |
| 1.2.6 | pre-r2 snapshot decision fields | mark scan → **0 marks** | 0 | **PASS** |

### 1.3 Repository Boundary — Pre-Entry

| # | Check | Observed | Result |
|---|---|---|--:|
| 1.3.1 | HEAD | `1f869865d5ff709c03cb4eb595524820d55d0be6` | **MATCH** |
| 1.3.2 | Branch | `integration/recovery-001` | **MATCH** |
| 1.3.3 | `gate_mode` writes | **0** | **PASS** |
| 1.3.4 | `replay_path` writes | **0** | **PASS** |
| 1.3.5 | `audit_emission` writes | **0** | **PASS** |
| 1.3.6 | Declaration mutations | **0** — no `*-declaration.json` in working-tree delta | **PASS** |
| 1.3.7 | Engine writes | **0** | **PASS** |
| 1.3.8 | Registry writes | **0** — `generated-artifact-registry.json` carries no entry from this act | **PASS** |
| 1.3.9 | `mutation-governance-boundary.json` | `509d1a4d3f9af6e0c85cdf8cb098f29a80736aef9b0ec8e7a9c876fd73002165` | **MATCH `509d1a4d…`** |

**Pre-validation gate: CLEARED.** Recording proceeded.

---

## 2. Requested Validation Checks

### 2.1 Check 1 — Five Decision Areas Recorded

| Field | Section | Recorded selection | Line |
|---|---|---|--:|
| Decision 1 — Class B existing canonical surfaces disposition | §5.1 | `[X] APPROVED` | 191 |
| Decision 2 — Class C/D true governance gaps disposition | §5.2 | `[X] APPROVED` | 204 |
| Decision 3 — R-4 grandfathering policy | §5.3 | `[X] OPTION 1` | 217 |
| Decision 4 — Corrected denominator acceptance | §5.4 | `[X] APPROVED` | 233 |
| Decision 5 — Eligibility ≠ authorization acknowledgement | §5.5 | `[X] APPROVED` | 245 |

**5 of 5 decision areas recorded. PASS.**

### 2.2 Check 2 — Correct Number Of Marks

| Measure | Expected | Observed | Result |
|---|--:|--:|--:|
| Total marks in canonical record | 5 | **5** | **PASS** |
| Marks per decision field | 1 | **1 each** | **PASS** |
| Checkboxes remaining unmarked | 8 | **8** — 5 unselected alternates + 3 §6 acknowledgements | **CONSISTENT** |
| Marks in R-4 r2 | 0 | **0** | **PASS** |
| Marks in pre-r2 snapshot | 0 | **0** | **PASS** |

Arithmetic: §5 presents 10 checkboxes (5 fields × 2 options) plus §6's 3 acknowledgement boxes = 13.
5 marked + 8 unmarked = 13. Reconciled.

### 2.3 Check 3 — No Double Marks

Adjacency scan of each §5 selection block confirms exactly one `[X]` and one `[ ]` per block. No
field carries two marks. No field carries zero marks. **PASS.**

### 2.4 Check 4 — Signature Fields Complete

| Field | Transmitted | Recorded | Fidelity |
|---|---|---|--:|
| `Selected By` | `Bipin Kumar` | `Bipin Kumar` | **byte-identical** |
| `Date` | `2026-08-16T20:10:00+05:30` | `2026-08-16T20:10:00+05:30` | **byte-identical — `+05:30` offset preserved, not normalized to UTC** |
| `Signature` | `Bipin Kumar` | `Bipin Kumar` | **byte-identical** |

Date is valid ISO 8601 with explicit offset. `Selected By` is non-placeholder. **PASS.**

### 2.5 Check 5 — Canonical Surface Only

| # | Check | Result |
|---|---|--:|
| 2.5.1 | All 5 marks located in `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` §5 | **PASS** |
| 2.5.2 | All 3 signature values located in that record §7 | **PASS** |
| 2.5.3 | No decision field selected in any other file | **PASS** |

### 2.6 Check 6 — Non-Canonical Surfaces Untouched

| Surface | Pre-entry sha256 | Post-entry sha256 | Result |
|---|---|---|--:|
| R-4 r2 | `3f0abe615d32de48…de15` | `3f0abe615d32de48…de15` | **UNCHANGED** |
| pre-r2 preservation snapshot | `074582134dbdd248…3acb` | `074582134dbdd248…3acb` | **UNCHANGED** |
| `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` | `4452b67898c219f8…52a3` | `4452b67898c219f8…52a3` | **UNCHANGED** |
| `H-06-R4-CORRECTION-EXECUTION-VALIDATION-DETERMINATION.md` | `dd93856fd168e154…58e3`¹ | identical | **UNCHANGED** |
| R-4 r2 §7 decision fields | 0 marks | **0 marks** | **UNCHANGED — CN-1 remains open** |
| `00-BOOK/DATA/mutation-governance-boundary.json` | `509d1a4d3f9af6e0…2165` | `509d1a4d3f9af6e0…2165` | **UNCHANGED** |

¹ Full value `dd93856fd168e1546e12f2b5df3ec21306c0afb7b60972d0f123c899872958f3`.

### 2.7 Check 7 — P-3 Selection Recorded

| Property | Value |
|---|---|
| P-3 | R-4 grandfathering policy selection |
| Selection | **OPTION 1 — Temporary Compliance Window** |
| Mandatory controls attached | **C-1..C-6, all six** |
| Authority | Mutation Governance Owner — Bipin Kumar |
| Timestamp | 2026-08-16T20:10:00+05:30 |
| Recorded at | §5.3 line 217 · logged §8 entry E-1 · attested §10 |
| Derived from recommendation? | **NO** — R-4 r2 §6's Option 1 recommendation is reproduced at §3.3 as evidence and populated no field; the mark reproduces the owner's transmitted token `OPTION 1` |

**PASS.**

### 2.8 Check 8 — No Implementation Authority Inferred

| # | Assertion | State |
|---|---|--:|
| 2.8.1 | Declaration mutation authorized by this entry | **NO** — no `gate_mode` / `replay_path` / `audit_emission` on any surface |
| 2.8.2 | Class B declaration authorized | **NO** — Decision 1 APPROVED records the 13 as **eligible-but-unauthorized**; a separate owner scope-extension decision is required |
| 2.8.3 | Declaration creation authorized | **NO** — none of the 23 absent surfaces may be created (IADR §5, IAR §1.1) |
| 2.8.4 | Engine modification authorized | **NO** |
| 2.8.5 | Registry modification authorized | **NO** — excluded under H-06 entirely |
| 2.8.6 | Implementation execution authorized | **NO** |

**CIEP v2 Phase 0 after this entry:**

| # | Condition | State |
|---|---|--:|
| 0.1 | IADR §8 signed | **PASS** |
| 0.2 | P-3 selected | **PASS — cleared by this entry** |
| 0.3 | Baseline confirmed | **PASS** |
| 0.4 | Corrected success criteria accepted | **PENDING RE-MEASUREMENT** |
| 0.5 | `verify.sh` baseline captured | **FAIL** |
| 0.6 | Unrelated deltas isolated | **FAIL** — 187 working-tree entries; owning programmes must commit |

**This entry cleared Phase 0.2 only. Three conditions remain unsatisfied, so implementation is not
permitted.** Gate purity does not close — GP-1, GP-3 and GP-11 terminate OPEN (residual). **PASS.**

### 2.9 Check 9 — No Repository Mutation Beyond The Owner Decision Record

| Path | Mutation | Attribution |
|---|---|---|
| `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` | **WRITTEN** — 5 marks, 3 signature values, state tables synchronized (§0, §1 link 13, §4.2 row 0.2, §5 entry-state, §7.1, §8, §8.2, §10, header) | **THIS ENTRY — authorized target** |
| `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-VALIDATION-DETERMINATION.md` | **CREATED** — this document | **THIS ENTRY — required output** |
| All declarations · engines · registries · `mutation-governance-boundary.json` · R-4 r2 · pre-r2 | **NONE** | — |
| HEAD | **UNCHANGED** at `1f869865` · branch `integration/recovery-001` · **0 commits created** | — |

**Not attributable to this entry, disclosed for completeness:**

| Path | Origin | mtime |
|---|---|---|
| `00-MASTER/UAKOS-CLOSURE-002/` — 15 artifacts | **Session-start hook** (UAKOS-CLOSURE-002: CLOSED, concepts=549, gaps=0), fired before this transmission was processed | 21:50:36 |
| `H-06-R4-GRANDFATHERING-POLICY-DECISION-CANONICALITY-RESOLUTION-DETERMINATION.md` | Prior canonicality resolution step, complete before this entry | 21:47:32 |

Owner decision record write: **21:53:54** — after both. Neither is a decision surface and neither
carries a mark. **PASS for the decision boundary; hook activity disclosed rather than absorbed.**

---

## 3. Determination Summary

| # | Requested check | Result |
|---|---|--:|
| 1 | Five decision areas recorded | **PASS** |
| 2 | Correct number of marks | **PASS — 5** |
| 3 | No double marks | **PASS** |
| 4 | Signature fields complete | **PASS** |
| 5 | Canonical surface only | **PASS** |
| 6 | Non-canonical surfaces untouched | **PASS** |
| 7 | P-3 selection recorded | **PASS — Option 1** |
| 8 | No implementation authority inferred | **PASS** |
| 9 | No repository mutation beyond the owner decision record | **PASS** |

**9 of 9 PASS.**

Record-internal validation requirements §9 V-1..V-10:

| # | Requirement | Result |
|---|---|--:|
| V-1 | Exactly one mark per field | **PASS** |
| V-2 | Conditional fields — Option 1 requires migration deadline and migration owner | **UNSATISFIED — see F-A** |
| V-3 | Three §6 acknowledgements marked | **UNSATISFIED — 0 of 3 — see F-B** |
| V-4 | Identity / date / signature | **PASS** |
| V-5 | Transmission fidelity | **PASS with disclosure — see §4** |
| V-6 | Evidence integrity | **PASS** |
| V-7 | R-4 §7 unmarked | **PASS — 0 marks; CN-1 open** |
| V-8 | Chain integrity, links 1–12 | **PASS** |
| V-9 | Boundary preservation | **PASS** |
| V-10 | Boundary honesty | **PASS — Phase 0.2 only; 0.4, 0.5, 0.6 outstanding** |

**8 of 10 PASS · 2 UNSATISFIED.**

---

## 4. Findings — Disclosed, Not Absorbed

### F-A — Option 1 conditional fields not transmitted

§5.3 requires, on Option 1, a migration deadline (ISO 8601) for the 9 in-scope declarations and a
named migration owner. **Neither was transmitted.** Under the recording rule *do not infer any value*,
both fields were left blank. The Option 1 **selection is validly recorded**; the record's completion
requirement item 6 is **outstanding**. A supplementary owner transmission supplying both values is
required before the record can be declared closed. Control C-2 (self-expiry of
`UNDECLARED-PENDING-MIGRATION`) cannot be operated without a deadline.

### F-B — §6 acknowledgements not transmitted

Three mandatory acknowledgements (Phase 0.2-only scope · no authority conferred · gate purity does
not close) were **not transmitted** and were left unmarked. Completion requirement items 8–10 are
**outstanding**. The substance of all three is nonetheless asserted by this determination at §2.8;
the owner's formal marks remain required.

### F-C — Token differences, recorded without silent normalization

| Field | Transmitted | Field vocabulary | Recorded |
|---|---|---|---|
| Decision 1 | `APPROVE` | `APPROVED` / `REJECTED` | `[X] APPROVED` |
| Decision 2 | `APPROVE` | `APPROVED` / `REJECTED` | `[X] APPROVED` |
| Decision 5 | `ACKNOWLEDGED` | `APPROVED` / `REJECTED` | `[X] APPROVED` |

Each field offers exactly one affirmative and one negative option. The transmitted tokens are
unambiguously affirmative, so the affirmative option was marked in each case. No third reading
exists. These differences are logged in the record at §8.2 and here, so the mapping is auditable
rather than hidden. Decisions 3 and 4 and all three signature values are byte-identical to
transmission.

**No conflict condition was triggered.** No pre-existing field value differed from a transmitted
value; every field was blank before entry.

### Pending items

| ID | Item | Owner |
|---|---|---|
| **CN-1** | R-4 r2 §7 retains an unmarked field set; annotation under correction authority required to point at the canonical surface | Correction authority |
| **CN-2** | F-A and F-B — Option 1 deadline, migration owner, three §6 acknowledgements | Mutation Governance Owner |

---

## 5. Record State After Entry E-1

| Property | State |
|---|---|
| Fields presented · marked · unmarked | 5 · **5** · **0** |
| Acknowledgements marked | **0 of 3 — outstanding** |
| `Selected By` · `Date` · `Signature` | Bipin Kumar · 2026-08-16T20:10:00+05:30 · Bipin Kumar |
| Entries processed | **1 — E-1** |
| §5 decision surface | **CLOSED** |
| Record completion (§7.1, 13 items) | **9 satisfied · 1 n/a · 4 outstanding** |
| P-3 | **SELECTED — OPTION 1** |
| CIEP v2 Phase 0.2 | **PASS** |
| CIEP v2 Phase 0.4 / 0.5 / 0.6 | **PENDING / FAIL / FAIL** |
| Implementation authorized | **NO** |
| Gate purity closed | **NO — GP-1, GP-3, GP-11 OPEN (residual)** |
| HEAD | `1f869865d5ff709c03cb4eb595524820d55d0be6` · `integration/recovery-001` · 0 commits created |

---

*This determination is read-only with respect to every surface except itself. It validates entry E-1
against the nine requested checks and against the subject record's own §9 requirements, reports two
unsatisfied record-internal requirements as findings F-A and F-B rather than suppressing them, and
confers no authority. P-3 selection satisfies CIEP v2 Phase 0.2 only. Implementation is not
permitted while Phase 0.4, 0.5 and 0.6 remain unsatisfied.*

---

P-3 owner decision recorded and validated.
R-4 grandfathering policy selected.
Implementation remains gated pending Phase 0 completion.
No implementation executed.
No unauthorized repository mutation performed.
