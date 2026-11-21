# H-06 R-4 GRANDFATHERING POLICY CN-2 COMPLETION VALIDATION DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-R4-GPCN2VD |
| **Authority** | READ-ONLY VALIDATION. Validates entry **E-3** and the completed record. Authorizes nothing. |
| **Validates** | `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` entry **E-3** · record completion |
| **Predecessors** | E-1 determination — 9 of 9 PASS · E-2 supplementary determination — 4 of 4 integrity PASS, CN-2 partial |
| **Subject sha256 (pre-E-3)** | `e2b1cce8394539c5b869dfc87d908ab5f4fa3665968de5b9c0987cff3cd9c248` · 409 lines |
| **Subject sha256 (post-E-3)** | `39b19a613b343848b9e7844c18a268821dc94371f2204c76a0dadf9cb77ab2e4` · 433 lines |
| **Baseline** | HEAD `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · **0 commits created** |
| **Produced** | 2026-08-16 |
| **Determination** | **PASS — 10 of 10 · CN-2 CLOSED · P-3 record COMPLETE at 13 of 13** |

---

## 1. Pre-Write Verification

Read-only, executed before any write.

### 1.1 Canonical Record

| # | Check | Expected | Observed | Result |
|---|---|---|---|--:|
| 1.1.1 | SHA256 | `e2b1cce8…c248` as certified by the E-2 determination | `e2b1cce8394539c5b869dfc87d908ab5f4fa3665968de5b9c0987cff3cd9c248` | **MATCH** |
| 1.1.2 | Line count | 409 | **409** | **MATCH** |
| 1.1.3 | E-1 CLOSED | 5 §5 marks, logged §8 | E-1 row present · lines 191, 204, 217, 233, 245 marked | **CONFIRMED CLOSED** |
| 1.1.4 | E-2 acknowledgement marks unchanged | 3 marks at §6 | lines 254, 256, 259 `[X]` | **UNCHANGED** |
| 1.1.5 | Existing decisions unchanged | APPROVED · APPROVED · OPTION 1 · APPROVED · APPROVED | identical | **UNCHANGED** |
| 1.1.6 | Signature unchanged | Bipin Kumar · `2026-08-16T20:10:00+05:30` · Bipin Kumar | identical | **UNCHANGED** |
| 1.1.7 | **Target fields blank before recording** | `________________` at both | line 222 `________________` · line 225 `________________` | **BLANK — no conflict condition** |

Check 1.1.7 is the transmission's stop condition. Both fields were blank, so recording proceeded.

### 1.2 Boundary

| # | Check | Expected | Observed | Result |
|---|---|---|---|--:|
| 1.2.1 | R-4 r2 unchanged | `3f0abe615d32de48…de15` · 0 marks | identical · **0 marks** | **UNCHANGED** |
| 1.2.2 | pre-r2 snapshot unchanged | `074582134dbdd248…3acb` · 0 marks | identical · **0 marks** | **UNCHANGED** |
| 1.2.3 | `gate_mode` | 0 | **0** | **PASS** |
| 1.2.4 | `replay_path` | 0 | **0** | **PASS** |
| 1.2.5 | `audit_emission` | 0 | **0** | **PASS** |
| 1.2.6 | Declaration changes | 0 | **0** | **PASS** |
| 1.2.7 | Engine writes | 0 | **0** | **PASS** |
| 1.2.8 | Registry writes | 0 | **0** | **PASS** |
| 1.2.9 | `mutation-governance-boundary.json` | `509d1a4d…2165` | identical | **UNCHANGED** |

**Pre-write gate: CLEARED.**

---

## 2. Requested Validations

### 2.1 Check 1 — Migration Deadline Recorded

| Property | Value |
|---|---|
| Field | §5.3 — *If OPTION 1 — migration deadline for the 9 in-scope declarations (ISO 8601)* |
| Location | line 222 |
| Transmitted | `2026-11-30T23:59:59+05:30` |
| Recorded | `2026-11-30T23:59:59+05:30` |
| Fidelity | **byte-identical** |
| Offset | **`+05:30` preserved exactly — not normalized to UTC, not converted** |
| ISO 8601 validity | valid — date, time, explicit offset |
| Inferred? | **NO** — literal value supplied by the owner |

**PASS.**

### 2.2 Check 2 — Migration Owner Recorded

| Property | Value |
|---|---|
| Field | §5.3 — *If OPTION 1 — migration owner* |
| Location | line 225 |
| Transmitted | `Bipin Kumar` |
| Recorded | `Bipin Kumar` |
| Fidelity | **byte-identical** · non-placeholder |
| Inferred? | **NO** |

**PASS.**

### 2.3 Check 3 — CN-2 Closed

| CN-2 component | Closed at | State |
|---|---|--:|
| §6 acknowledgement 1 — Phase 0.2 only | E-2 | **CLOSED** |
| §6 acknowledgement 2 — no authority conferred | E-2 | **CLOSED** |
| §6 acknowledgement 3 — gate purity does not close | E-2 | **CLOSED** |
| §5.3 migration deadline | **E-3** | **CLOSED** |
| §5.3 migration owner | **E-3** | **CLOSED** |

**CN-2: CLOSED — 5 of 5 components.** The E-2 conflict condition (non-values in two value positions)
is resolved by E-3 and is recorded as CLOSED at record §8.3.

### 2.4 Check 4 — Completion Criteria Satisfied

§7.1, all 13 items:

| # | Condition | State |
|---|---|--:|
| 1 | §5.1 exactly one mark | **SATISFIED** |
| 2 | §5.2 exactly one mark | **SATISFIED** |
| 3 | §5.3 exactly one mark | **SATISFIED** |
| 4 | §5.4 exactly one mark | **SATISFIED** |
| 5 | §5.5 exactly one mark | **SATISFIED** |
| 6 | Option 1 migration deadline and owner populated | **SATISFIED at E-3** |
| 7 | Alternative disposition if Decision 1 or 2 REJECTED | **n/a** — both APPROVED |
| 8 | §6 acknowledgement 1 | **SATISFIED** |
| 9 | §6 acknowledgement 2 | **SATISFIED** |
| 10 | §6 acknowledgement 3 | **SATISFIED** |
| 11 | `Selected By` | **SATISFIED** |
| 12 | `Date` | **SATISFIED** |
| 13 | `Signature` | **SATISFIED** |

**13 of 13 satisfied · 1 n/a · 0 outstanding. Record COMPLETE.**

Progression across entries: **9 of 13 (E-1) → 12 of 13 (E-2) → 13 of 13 (E-3).**

### 2.5 Check 5 — P-3 Record Internally Consistent

| # | Consistency check | Observed | Result |
|---|---|---|--:|
| 2.5.1 | Mark reconciliation | 13 checkboxes (§5 ten, §6 three) · **8 marked · 5 unmarked** · 8+5=13 | **RECONCILED** |
| 2.5.2 | No double marks | one `[X]` per §5 block, one per §6 line — adjacency scan | **PASS** |
| 2.5.3 | Remaining blank value fields | lines 196 and 209 only — the two *If REJECTED — alternative disposition* fields | **CORRECT** — both decisions APPROVED, so item 7 is n/a and these must stay blank |
| 2.5.4 | Conditional logic coherent | Decision 3 = OPTION 1 → deadline and owner populated; OPTION 2 unmarked → no Option 2 conditionals exist | **COHERENT** |
| 2.5.5 | Header Status vs §7.1 vs §10 | all three state 13 of 13 / COMPLETE / CN-2 CLOSED | **CONSISTENT** |
| 2.5.6 | §8 log vs observed marks | cumulative 3 entries · 8 marks · 2 of 2 conditional values | **CONSISTENT** |
| 2.5.7 | §1 evidence chain link 13 | RECORDED — 5 of 5, Option 1, Bipin Kumar, `2026-08-16T20:10:00+05:30` | **CONSISTENT** |
| 2.5.8 | §4.2 Phase 0.2 row | PASS — Option 1 recorded | **CONSISTENT** |
| 2.5.9 | Arithmetic preserved | `9 + 13 + 23 = 45` · `22 + 23 = 45` · §2.3 measurements intact | **UNALTERED** |
| 2.5.10 | Control C-2 parameterized | expiry `2026-11-30T23:59:59+05:30` · owner Bipin Kumar | **RESOLVED** — the unbounded-window gap reported in the E-2 determination is closed |

**PASS.**

### 2.6 Check 6 — All Prior Decisions Unchanged

| Decision | Line | Value | Result |
|---|--:|---|--:|
| 1 — Class B disposition | 191 | `[X] APPROVED` | **UNALTERED** |
| 2 — Class C/D disposition | 204 | `[X] APPROVED` | **UNALTERED** |
| 3 — Grandfathering policy | 217 | `[X] OPTION 1` | **UNALTERED** |
| 4 — Corrected denominator | 233 | `[X] APPROVED` | **UNALTERED** |
| 5 — Eligibility ≠ authorization | 245 | `[X] APPROVED` | **UNALTERED** |
| §6 acknowledgements 1–3 | 254 · 256 · 259 | `[X]` ×3 | **UNALTERED** |

E-3 added no mark and removed none; mark count is 8 before and after. E-3 wrote two value fields only.
§2 and §3 evidence text and the reproduced R-4 §6 recommendation are untouched. **PASS.**

### 2.7 Check 7 — Signature Integrity Preserved

| Field | E-1 value | Post-E-3 value | Result |
|---|---|---|--:|
| `Selected By` | Bipin Kumar | Bipin Kumar | **UNCHANGED** |
| `Date` | `2026-08-16T20:10:00+05:30` | `2026-08-16T20:10:00+05:30` | **UNCHANGED — offset intact** |
| `Signature` | Bipin Kumar | Bipin Kumar | **UNCHANGED** |
| Evidence Reference | R-4 r2 · `3f0abe61…` | identical | **UNCHANGED** |

**PASS.**

### 2.8 Check 8 — Canonical Decision Surface Only

| # | Check | Result |
|---|---|--:|
| 2.8.1 | Both E-3 values written to `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` §5.3 | **PASS** |
| 2.8.2 | R-4 r2 §7 field set | **0 marks · no value populated** | **PASS — CN-1 still open** |
| 2.8.3 | pre-r2 snapshot | **0 marks** | **PASS** |
| 2.8.4 | `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` · `…CORRECTION-EXECUTION-VALIDATION-DETERMINATION.md` | untouched, evidence only | **PASS** |
| 2.8.5 | Any decision or conditional field populated outside the canonical surface | **NONE** | **PASS** |

### 2.9 Check 9 — No Implementation Authority Inferred

| # | Assertion | State |
|---|---|--:|
| 2.9.1 | Declaration mutation authorized | **NO** — 0 `gate_mode` / `replay_path` / `audit_emission` |
| 2.9.2 | Class B declaration authorized | **NO** — 13 remain eligible-but-unauthorized; separate scope-extension decision required |
| 2.9.3 | Declaration creation authorized | **NO** — 23 absent surfaces may not be created (IADR §5, IAR §1.1) |
| 2.9.4 | Engine modification authorized | **NO** |
| 2.9.5 | Registry modification authorized | **NO** — excluded under H-06 entirely |
| 2.9.6 | Implementation execution authorized | **NO** |
| 2.9.7 | Migration deadline confers authority to write toward it | **NO** — recording an expiry parameterizes control C-2; it does not authorize any write |

**CIEP v2 Phase 0:**

| # | Condition | State |
|---|---|--:|
| 0.1 | IADR §8 signed | **PASS** |
| 0.2 | P-3 selected | **PASS — complete** |
| 0.3 | Baseline confirmed | **PASS** |
| 0.4 | Corrected success criteria accepted | **PENDING RE-MEASUREMENT — owner act** |
| 0.5 | `verify.sh` baseline captured | **FAIL** |
| 0.6 | Unrelated deltas isolated | **FAIL** — 189 working-tree entries; owning programmes must commit |

**Record completion satisfies Phase 0.2 only. Three conditions remain unsatisfied, so implementation
is not permitted.** Gate purity does not close — GP-1, GP-3, GP-11 terminate OPEN (residual). **PASS.**

### 2.10 Check 10 — Repository Boundary Unchanged

| Surface | Pre-E-3 | Post-E-3 | Result |
|---|---|---|--:|
| R-4 r2 | `3f0abe615d32de48…de15` | identical | **UNCHANGED** |
| pre-r2 snapshot | `074582134dbdd248…3acb` | identical | **UNCHANGED** |
| `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` | `4452b67898c219f8…52a3` | identical | **UNCHANGED** |
| `H-06-R4-CORRECTION-EXECUTION-VALIDATION-DETERMINATION.md` | `dd93856fd168e154…58e3`¹ | identical | **UNCHANGED** |
| `00-BOOK/DATA/mutation-governance-boundary.json` | `509d1a4d…2165` | identical | **UNCHANGED** |
| Declarations · engines · registries | — | **0 writes** | **PASS** |
| HEAD · branch | `1f869865` · `integration/recovery-001` | identical · **0 commits** | **UNCHANGED** |

¹ `dd93856fd168e1546e12f2b5df3ec21306c0afb7b60972d0f123c899872958f3`.

**Files written by E-3:**

| Path | Change |
|---|---|
| `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` | 2 value fields populated · state tables synchronized (header Status, §7.1, §8 log + E-3 row, §8.4 new, §10, closing paragraph) · 409 → 433 lines |
| `H-06-R4-GRANDFATHERING-POLICY-CN2-COMPLETION-VALIDATION-DETERMINATION.md` | this document |

Nothing else. Working-tree deltas outside these two files predate this session and belong to the
Phase 0.6 condition. **PASS.**

---

## 3. Determination Summary

| # | Requested validation | Result |
|---|---|--:|
| 1 | Migration deadline recorded | **PASS — `2026-11-30T23:59:59+05:30`** |
| 2 | Migration owner recorded | **PASS — Bipin Kumar** |
| 3 | CN-2 closed | **PASS — 5 of 5 components** |
| 4 | Completion criteria satisfied | **PASS — 13 of 13** |
| 5 | P-3 record internally consistent | **PASS — 10 of 10 consistency checks** |
| 6 | All prior decisions unchanged | **PASS** |
| 7 | Signature integrity preserved | **PASS** |
| 8 | Canonical decision surface only | **PASS** |
| 9 | No implementation authority inferred | **PASS** |
| 10 | Repository boundary unchanged | **PASS** |

**10 of 10 PASS.**

Record-internal §9 requirements V-1..V-10, re-run in full:

| # | Requirement | E-1 result | Now |
|---|---|--:|--:|
| V-1 | Exactly one mark per field | PASS | **PASS** |
| V-2 | Conditional fields | **UNSATISFIED** | **PASS** |
| V-3 | Acknowledgement completeness | **UNSATISFIED** | **PASS — 3 of 3** |
| V-4 | Identity / date / signature | PASS | **PASS** |
| V-5 | Transmission fidelity | PASS w/ disclosure | **PASS** |
| V-6 | Evidence integrity | PASS | **PASS** |
| V-7 | R-4 §7 unmarked | PASS | **PASS — CN-1 open** |
| V-8 | Chain integrity, links 1–12 | PASS | **PASS** |
| V-9 | Boundary preservation | PASS | **PASS** |
| V-10 | Boundary honesty | PASS | **PASS** |

**10 of 10 PASS.** All record-internal validation requirements are now satisfied; the two previously
unsatisfied requirements (V-2, V-3) are closed.

---

## 4. Residual Items

| ID | Item | State | Owner |
|---|---|--:|---|
| **CN-1** | R-4 r2 §7 retains an unmarked field set; annotation required to point at the canonical surface | **OPEN** | Correction authority |
| **CN-2** | Option 1 migration parameters and §6 acknowledgements | **CLOSED** | — |
| **C-1 (E-2 conflict)** | Non-values transmitted in two value positions | **CLOSED at E-3** | — |
| **Phase 0.4** | Corrected success criteria acceptance | **PENDING** | Mutation Governance Owner |
| **Phase 0.5** | `verify.sh` baseline capture | **FAIL** | Implementation authority |
| **Phase 0.6** | Unrelated working-tree deltas isolated | **FAIL** | Owning programmes |
| **GP-1 · GP-3 · GP-11** | Gate purity residual | **OPEN (residual)** | — |

CN-1 is unchanged by this entry and is not a completion criterion of the owner decision record; it is
a canonicality-hygiene item requiring correction authority, which this determination does not hold.

---

*This determination is read-only with respect to every surface except itself. It validates entry E-3,
confirms both migration parameters are recorded byte-identically with the `+05:30` offset preserved,
confirms CN-2 is closed and the P-3 owner decision record is complete at 13 of 13, confirms the five
decisions, three acknowledgements and signature block are unaltered, and confirms the repository
boundary is unchanged. It confers no authority. Record completion satisfies CIEP v2 Phase 0.2 only.*

---

P-3 owner decision record complete.
CN-2 closed.
Phase 0.2 complete.
Phase 0.4, 0.5, 0.6 remain separately gated.
No implementation executed.
No unauthorized repository mutation performed.
