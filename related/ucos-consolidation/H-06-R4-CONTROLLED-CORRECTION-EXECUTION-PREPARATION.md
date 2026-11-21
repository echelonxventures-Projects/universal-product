# H-06 R-4 CONTROLLED CORRECTION EXECUTION PREPARATION

| Field | Value |
|---|---|
| **ID** | H-06-R4-CCEP |
| **Authority** | CORRECTION EXECUTION PREPARATION ONLY. No R-4 modification. No P-3 selection. No declaration, engine, or registry mutation. |
| **Phase** | Foundation Closure — Gate Purity — R-4 Correction Execution Preparation |
| **Subject** | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` · sha256 `074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb` · 284 lines · mtime 2026-08-16 18:55:47 |
| **Prior artifact** | `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` — RC-1..RC-8 defined; **one misattribution corrected here, see §0.3** |
| **Baseline** | HEAD `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · 0 commits |
| **Produced** | 2026-08-16 |
| **Determination** | **EXECUTION SEQUENCE PREPARED — NOT EXECUTED — R-4 UNMODIFIED — P-3 UNSELECTED** |

---

## 0. Required Verification

### 0.1 Chain and Boundary

| Check | Measured | Result |
|---|---|---|
| Ownership disposition decision APPROVED and validated | ODODR `277369a9…` · **5 APPROVED** · 3 acknowledgements · **OWNER DECISION VALIDATION PASSES** | **CONFIRMED** |
| Implementation authorization decision APPROVED and validated | IAODR `6eb3f97d…` · **5 APPROVED** · 3 acknowledgements · entry A-1 **CLOSED** · **OWNER DECISION VALIDATION PASSES** | **CONFIRMED** |
| IADR §8 remains signed | `[X] AUTHORIZED` · Bipin Kumar · 2026-08-16T20:10:00+05:30 · **SIGNATURE VALIDATION PASSES** | **SIGNED** |
| R-4 unmodified before preparation | sha256 `074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb` · mtime **2026-08-16 18:55:47** | **UNMODIFIED** |
| P-3 unselected | **0** marked checkboxes · `Selected By` and `Date` blank | **UNSELECTED** |
| HEAD | **`1f869865`** · branch `integration/recovery-001` · **0** commits | **CONFIRMED** |
| `mutation-governance-boundary.json` unchanged | **0** status entries · sha256 `509d1a4d3f9af6e0…` | **UNCHANGED** |
| `gate_mode` · `replay_path` · `audit_emission` | **0 · 0 · 0** | **ZERO** |
| Declaration changes | **0** of 11 modified | **NONE** |
| Engine changes | **0** files written | **NONE** |

### 0.2 Statements Extracted Read-Only

Every "current statement" quoted in §2 was extracted from R-4 read-only, by line number, at the hash
above. No line was modified in the course of extraction.

### 0.3 Correction To The Prior Plan — Option Misattribution

**`H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` §2.7 attributed the overstated cost to Option 1. That
is wrong, and the error changes which option the defect affects.**

R-4 §4.1 is the assessment of **Option 2 — Immediate Non-Compliance**; §4.2 is Option 1. The
"36 new declaration files" and "36 forbidden acts" statements at lines 130–131, 141, 212 and 268 all
belong to the **Option 2** analysis.

| | Prior plan §2.7 | Corrected |
|---|---|---|
| Option whose cost is overstated | Option 1 | **Option 2** |
| Overstatement | 36 vs 23 creation acts | **unchanged — 36 vs 23** |
| Which option the recommendation argues against | — | **Option 2**, on the strength of the overstated figure |

**Consequence, stated precisely.** R-4 §6 recommends Option 1 because Option 2's own precondition
"requires 36 acts that IAR §1.1 does not authorize and IADR §5 forbids". The true figure is 23. The
**conclusion survives** — 23 forbidden creation acts still exceed authorized scope, so Option 2
remains infeasible — but the **margin is misstated by 13**, and the owner is entitled to decide
against accurate magnitudes. The prior plan's identification of the defective lines, the 13/23
partition, and RC-1..RC-8 are all unaffected; only the option label in §2.7 was wrong.

### 0.4 Option 2 Fails For Two Distinct Reasons — Refined Analysis

Correcting 36 → 23 splits Option 2's infeasibility into two grounds that the present text conflates:

| Population | Count | Why Option 2 still fails |
|---|--:|---|
| Class C + D | **23** | No surface exists; a batch declaration requires **creating 23 files** — forbidden as creation of a new governance surface (IADR §5) and outside IAR §1.1 |
| Class B | **13** | A capable surface exists, so no creation is needed — but writing a mode there is **unauthorized** (updated IADR §5 excludes `gate_mode` on Class B) |

Two different constitutional defects, two different populations. The corrected R-4 must say this;
the present text says "36 acts of creation", which is wrong for 13 of them.

---

## 1. Correction Authority Boundary

### 1.1 What May Change

| # | Permitted change | Scope |
|---|---|---|
| A-1 | Characterisations that generalise a filename measurement into a surface-existence claim | C-5 (L182), L130–131, L141, L186, L212, L268 |
| A-2 | Derived counts of **creation acts**, 36 → 23 | L131, L141, L212, L268 |
| A-3 | Addition of the Class A/B/C/D vocabulary and the `9 + 13 + 11 + 12 = 45` / `22 + 23 = 45` reconciliations | §3 |
| A-4 | The §7 acknowledgement text, so it states the corrected three-way population | L241–243 |
| A-5 | Disposition fields that currently address "the 36" as one population, split into 13 and 23 | L154, L233 |
| A-6 | Recommendation basis magnitude in §6, with its conclusion preserved | L211–212 |
| A-7 | Cross-references to ODODR r4, GOMRD, and updated IADR §3.2 | Header, §3, §5 |
| A-8 | A revision marker recording the correction | Header |

### 1.2 What May Not Change

| # | Prohibited change | Basis |
|---|---|---|
| N-1 | The §3.2 measurement `9 with · 36 without same-named *-declaration.json` and its 36-name enumeration | It is **correct**, and it is the evidence that quantifies the defect |
| N-2 | The §3.3 heterogeneity finding — 14 guard-carrying engines reading differently-named artifacts | It is correct and is R-4's own internal counter-evidence to C-5 |
| N-3 | The 45-target denominator, or the §3.1 measurement establishing it | Corrected denominator, already ratified across the chain |
| N-4 | Any checkbox state — Options 1 and 2, the disposition sub-field, ACKNOWLEDGED | Correction is not selection |
| N-5 | `Selected By` · `Date` | Attribution is the owner's act |
| N-6 | §5.1 pending vocabulary — `UNDECLARED-PENDING-MIGRATION` as transitional and additive | Ratified vocabulary unaffected |
| N-7 | §8's constraint that Option 2 cannot authorize file creation | Constitutional, not arithmetic — only the count inside it changes |
| N-8 | The direction of the §6 recommendation | Correcting evidence must not reverse a recommendation; if corrected evidence would change it, that is the owner's judgement, not the corrector's |

### 1.3 Why This Is Evidence Repair, Not Policy Selection

| Property | Evidence repair (this correction) | Policy selection (P-3) |
|---|---|---|
| Object | Statements **about** the population | The choice **between** Option 1 and Option 2 |
| Authority | Correction authority | Mutation Governance Owner |
| Artifact touched | R-4 narrative and count statements | R-4 §7 checkboxes and attribution |
| Outcome | The record describes reality accurately | A constitutional policy is adopted |
| Effect on P-3 | Moves it **BLOCKED → ELIGIBLE** | **Closes** it |

**The test applied throughout:** a change is evidence repair only if it leaves every decision field
unmarked and every option equally selectable. Any change that makes one option easier or harder to
choose *than the corrected evidence warrants* is policy interference, not repair. RC-6 sits closest
to this line, which is why N-8 constrains it: the magnitude is corrected, the direction is not
touched, and the fact that a corrected margin might bear on the owner's choice is disclosed rather
than resolved.

---

## 2. RC-1 Through RC-8 Execution Mapping

### RC-1 — C-5 Correction (Primary)

| | |
|---|---|
| **Affected section** | §5 Required Controls, control C-5 — **line 182** |
| **Current statement** | `| C-5 | The **36 gate targets with no declaration surface** are recorded as an explicit scope gap, not as pending declarations | A pending status cannot be written into a file that does not exist; recording them as "pending" would fabricate coverage |` |
| **Corrected statement** | C-5 splits into two populations: the **23** Class C/D targets with **no capable owning surface** are recorded as an explicit scope gap; the **13** Class B targets **have** a capable owning surface and are recorded as eligible-but-unauthorized, not as surface-less. Rationale retained for the 23: a pending status cannot be written into a file that does not exist. |
| **Evidence source** | R-4 §3.2 enumeration (13 Class B names present, remainder 23) · R-4 §3.3 heterogeneity finding · GOMRD Class B definition · ODODR r4 Decision 1 |
| **Validation method** | `grep -c "36 gate targets with no declaration surface"` → **0**; confirm both populations named with counts 13 and 23 |

### RC-2 — Population Reconciliation

| | |
|---|---|
| **Affected sections** | §3 (addition) · L131 · L141 · L186 · L212 · L268 |
| **Current statements** | L131 `require creating 36 new declaration files — an act that:` · L141 `implication, 36 acts that the constitutional chain forbids.` · L186 `Without it, Option 1 would appear to cover 45 gates while 36 of them have nowhere to` · L212 `precondition requires 36 acts that IAR §1.1 does not authorize and IADR §5 forbids.` · L268 `36 absent declaration files. If Option 2 is selected, implementation remains blocked until` |
| **Corrected statements** | Each count of **creation acts / absent files** becomes **23**. L186 becomes: 23 have nowhere to record the pending state, and 13 have a surface but no authorization. §3 gains `9 + 13 + 11 + 12 = 45` and `22 + 23 = 45`. |
| **Evidence source** | Verified partition of R-4 §3.2's own enumeration: 13 + 23 = 36; 9 + 13 + 23 = 45 |
| **Validation method** | Re-derive both sums from the §3.2 enumeration; confirm no surviving statement asserts 36 creation acts or 36 absent files |

### RC-3 — Ownership Model Alignment

| | |
|---|---|
| **Affected sections** | §3 · §5 |
| **Current statement** | R-4 has no Class A/B/C/D vocabulary; §3.3 describes heterogeneity without naming the classes |
| **Corrected statement** | Adopt Class A (9) · Class B (13) · Class C (11) · Class D (12); cite ODODR r4 Decision 1 as the governing ownership model; state **Eligibility ≠ Authorization** explicitly |
| **Evidence source** | GOMRD §2–§6 · ODODR r4 §4 · updated IADR §4.0 |
| **Validation method** | Confirm all four class counts present and summing to 45; confirm the eligibility/authorization distinction is stated, not implied |

### RC-4 — P-3 Prerequisite Correction (Executed Last)

| | |
|---|---|
| **Affected section** | §7 Acknowledgement of corrected measurement — **lines 241–243** |
| **Current statement** | `**Acknowledgement of corrected measurement:** I have read §3 and accept that the authorized scope of 11 *-declaration.json files reaches at most 9 of the 45 baseline gate targets, and that 36 gate targets are outside authorized scope.` |
| **Corrected statement** | Retain "reaches at most 9 of the 45 baseline gate targets". Replace the undifferentiated 36 with the three-way population: **9 authorized-reachable · 13 eligible-but-unauthorized (capable surface exists) · 23 governed gaps (no capable surface)** — 36 outside authorized scope, of which 13 are surface-capable. |
| **Evidence source** | ODODR r4 Decision 1 · corrected §3 · updated IADR §3.2 |
| **Validation method** | Confirm the acknowledgement names all three populations with counts; confirm the `[ ] ACKNOWLEDGED` box remains **UNMARKED** |

### RC-5 — Disposition Split

| | |
|---|---|
| **Affected sections** | §4.2 — **line 154** · §7 — **line 233** |
| **Current statements** | L154 `scope) while the remaining 36 are tracked as explicitly pending with named owners and a` · L233 `**If Option 1 selected — disposition of the 36 out-of-scope gate targets:**` |
| **Corrected statements** | L154: 9 advance within scope; the **13** Class B targets are eligible-but-unauthorized pending a scope extension; the **23** governed gaps are tracked as explicitly pending with named owners and a deadline. L233: disposition sought separately for the 13 and for the 23, since a pending mode is recordable for the 13 and not for the 23. |
| **Evidence source** | ODODR r4 Decision 1 · C-3 (existing register mechanism) · C-5 as corrected |
| **Validation method** | Confirm both populations addressed distinctly in each location; confirm no new checkbox is marked by the split |

### RC-6 — Option 2 Cost Restatement *(Option 2, per §0.3)*

| | |
|---|---|
| **Affected sections** | §4.1 — **lines 129–141** · §5 L186 · §6 — **lines 211–212** |
| **Current statement** | L130 `a batch, of which **36 have no *-declaration.json to write into**. Satisfying it would` · L131 `require creating 36 new declaration files` · L212 `precondition requires 36 acts that IAR §1.1 does not authorize and IADR §5 forbids.` |
| **Corrected statement** | Option 2's batch precondition fails on **two distinct grounds**: **23** targets require file creation, which IAR §1.1 does not authorize and IADR §5 forbids; **13** targets need no creation but writing a mode there is unauthorized under updated IADR §5's Class B exclusion. Option 2 therefore remains infeasible within authorized scope, on a corrected margin of 23 forbidden creations rather than 36. |
| **Evidence source** | Corrected §3 · updated IADR §5 Class B exclusion · IAR §1.1 |
| **Validation method** | Confirm both grounds stated with counts 23 and 13; confirm the recommendation **direction is unchanged** (N-8); confirm the corrected margin is stated rather than the conclusion being re-argued |

### RC-7 — Preservation Audit

| | |
|---|---|
| **Affected sections** | §3.2 · §3.3 · §5.1 · §8 |
| **Current statement** | All four correct as written |
| **Corrected statement** | **No change.** §3.2's measurement and 36-name enumeration, §3.3's heterogeneity finding, §5.1's pending vocabulary, and §8's constitutional constraint are preserved byte-for-byte — except the single count inside §8 L268 (36 → 23 absent files), which is RC-2. |
| **Evidence source** | §1.2 rules N-1, N-2, N-6, N-7 |
| **Validation method** | Byte comparison of §3.2 enumeration block, §3.3 paragraph, and §5.1 code block before and after |

### RC-8 — Cross-Reference Update

| | |
|---|---|
| **Affected sections** | Header · §3 · §5 |
| **Current statement** | R-4 cites `H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md` only |
| **Corrected statement** | Add: GOMRD (class model source) · ODODR r4 (governing owner decision) · updated IADR §3.2 and §5 (record of supersession and Class B exclusion) · this correction's validation determination. Add a revision marker: **r2 — evidence correction**. |
| **Evidence source** | The artifacts named |
| **Validation method** | Confirm all four references resolve to existing files; confirm the revision marker states that no decision field was altered |

---

## 3. Preservation Verification

Confirmed preserved by the mapping in §2, each with the rule that protects it:

| # | Item to preserve | Protected by | Verification |
|---|---|---|---|
| PV-1 | **Original enumeration evidence** — §3.2's 36 names and the `9 with · 36 without` measurement | N-1 · RC-7 | Byte comparison of the enumeration block; the 36 names must remain intact and in order |
| PV-2 | **Class A/B/C/D model** — introduced, and consistent with GOMRD and ODODR r4 | RC-3 | 9 + 13 + 11 + 12 = 45; class definitions match GOMRD |
| PV-3 | **45 target denominator** — and §3.1's measurement establishing it against the 46 working-tree figure | N-3 | §3.1 unchanged; every corrected statement uses 45 |
| PV-4 | **9 + 13 + 23 reconciliation** — and its equivalence to 22 + 23 = 45 | RC-2 · RC-3 | Both sums re-derived from PV-1's enumeration, independently of any narrative text |
| PV-5 | **P-3 dependency language** — §8's statement that closing P-3 does not authorize implementation, and that the IADR §8 signature is independent and neither substitutes for the other | N-7 | §8 paragraph preserved except the 36 → 23 count; the independence statement byte-identical |

### 3.1 Additional Preservation

| # | Item | Protected by |
|---|---|---|
| PV-6 | §3.3 heterogeneity finding — R-4's internal counter-evidence to C-5 | N-2 |
| PV-7 | §5.1 pending vocabulary, transitional and additive; ratified terminal vocabulary unchanged | N-6 |
| PV-8 | All five decision fields unmarked; `Selected By` and `Date` blank | N-4 · N-5 |
| PV-9 | §6 recommendation **direction** — Option 1, unchanged | N-8 |
| PV-10 | Controls C-1, C-2, C-3, C-4, C-6 — untouched; only C-5 is corrected | RC-1 scope limit |

**Every corrected count must be re-derivable from PV-1.** If the enumeration is preserved, any future
reader can recompute 13 and 23 without trusting the corrected narrative.

---

## 4. Mutation Sequence

**Defined for future execution under explicit correction authority. Not executed.**

### 4.1 Step 0 — Backup and Hash Capture

| # | Action | Expected |
|---|---|---|
| 0.1 | Record pre-correction sha256 | **`074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb`** |
| 0.2 | Record size and mtime | 284 lines · 13,405 bytes · 2026-08-16 18:55:47 |
| 0.3 | Copy R-4 to `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.pre-r2.md` as an immutable pre-correction reference | Byte-identical copy; hash matches 0.1 |
| 0.4 | Capture the §3.2 enumeration block, §3.3 paragraph, §5.1 code block, and §8 independence paragraph for byte comparison | Four reference extracts |
| 0.5 | Confirm all five checkboxes unmarked and attribution blank | 0 marks · blank |
| 0.6 | Confirm chain and boundary state per §0.1 | All CONFIRMED |

**Note on 0.3.** R-4 is **untracked** at baseline, so `git` provides no recovery. A filesystem copy is
the only rollback source, which makes step 0.3 mandatory rather than advisory. The copy must not use
a `.save` suffix — H-06-DOCUMENT-CANONICALITY-CLEANUP-DETERMINATION.md raised that pattern as a
finding, since a `.save` twin creates a second readable version of a governance record.

### 4.2 Controlled Edit Order

| Step | Correction | Depends on | Rationale for position |
|--:|---|---|---|
| 1 | **RC-1** — C-5 correction | 0.1–0.6 | The primary defect; everything else is consistency with it |
| 2 | **RC-2** — population arithmetic | RC-1 | Counts follow the corrected characterisation |
| 3 | **RC-3** — ownership model alignment | RC-1 | Vocabulary that RC-6 and RC-4 will use |
| 4 | **RC-6** — Option 2 cost restatement | RC-2, RC-3 | Requires corrected counts and class vocabulary |
| 5 | **RC-5** — disposition split | RC-1, RC-3 | Requires both populations named |
| 6 | **RC-8** — cross-references and revision marker | RC-1..RC-6 | References the corrections made |
| 7 | **RC-4** — §7 acknowledgement | **all above** | **Last.** The text the owner acknowledges must be final, not intermediate |
| 8 | **RC-7** — preservation audit | all above | Verification pass, not an edit |

**No step marks a checkbox. No step populates attribution. Step 7 is the P-3 gate and is deliberately
terminal.**

### 4.3 Post-Edit Validation

| # | Check | Pass condition |
|---|---|---|
| PE-1 | Pre-hash matches 0.1 | Confirms the correct artifact was edited |
| PE-2 | Post-hash recorded and differs from pre-hash | Change occurred and is attributable |
| PE-3 | `grep -c "36 gate targets with no declaration surface"` | **0** |
| PE-4 | No surviving statement asserts 36 creation acts or 36 absent files | 0 occurrences |
| PE-5 | Arithmetic re-derived from the preserved §3.2 enumeration | 13 + 23 = 36 · 9 + 13 + 11 + 12 = 45 · 22 + 23 = 45 |
| PE-6 | PV-1, PV-6, PV-7 byte-identical to the 0.4 extracts | Exact match |
| PE-7 | Checkboxes and attribution | **0 marks** · `Selected By` and `Date` blank |
| PE-8 | §6 recommendation direction | Unchanged — Option 1 |
| PE-9 | Controls C-1, C-2, C-3, C-4, C-6 | Byte-identical |
| PE-10 | Repository boundary | `gate_mode`/`replay_path`/`audit_emission` 0 · 0 declarations · 0 engine · 0 registry · boundary file `509d1a4d…` · HEAD `1f869865` · 0 commits |
| PE-11 | P-3 status | **ELIGIBLE FOR OWNER DECISION** — and reported as not selected |
| PE-12 | Phase 0.2 | Reported **still FAIL** — correctness of the record does not satisfy it; only the owner's selection does |

A validation determination records PE-1..PE-12. **P-3 may not be presented for selection until it
passes.**

### 4.4 Rollback Conditions

Rollback restores the 0.3 copy in full. Partial rollback is prohibited — a half-corrected R-4 is
worse than an uncorrected one, because it would carry two readable versions of the population model.

| # | Trigger | Action |
|--:|---|---|
| R-1 | Any checkbox marked, or attribution populated, at any step | **Immediate full rollback** — the correction has crossed into selection |
| R-2 | PV-1 enumeration altered or lost | **Immediate full rollback** — the evidence that quantifies the defect is destroyed |
| R-3 | PE-5 arithmetic fails to re-derive | Full rollback; re-measure before retrying |
| R-4 | §6 recommendation direction changed | Full rollback — N-8 violated |
| R-5 | Any declaration, engine, registry, or boundary file modified | **Immediate full rollback** and boundary re-verification |
| R-6 | Post-edit hash unrecorded, or pre-hash mismatch at PE-1 | Full rollback — the change is not attributable |
| R-7 | Any new governance surface created, or declaration creation authorized | **Immediate full rollback** — Decision 4 violated |

**Post-rollback requirement.** Restoring the copy must reproduce sha256
`074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb` exactly. A rollback that does not
restore that hash is a failed rollback and must be reported as such.

---

## 5. Forbidden Actions

Confirmed not performed in the production of this preparation, measured after writing it.

| # | Forbidden action | Measured state |
|---|---|---|
| F-1 | **P-3 selection** | **NOT PERFORMED** — 0 of 5 checkboxes marked; `Selected By` and `Date` blank |
| F-2 | **Implementation start** | **NOT PERFORMED** — 0 phases begun; Phase 0.2, 0.4, 0.5, 0.6 outstanding; 0 commits |
| F-3 | **Declarations** | **NOT PERFORMED** — 0 of 11 `*-declaration.json` modified; no declaration created |
| F-4 | **`gate_mode`** | **NOT PERFORMED** — count **0** |
| F-5 | **Registry changes** | **NOT PERFORMED** — 0 writes under `00-BOOK/DATA/`; `mutation-governance-boundary.json` unchanged at `509d1a4d…` |
| F-6 | **Engine changes** | **NOT PERFORMED** — 0 files written under `engine/` |
| F-7 | **R-4 modification** | **NOT PERFORMED** — sha256 `074582134dbdd248…` · mtime **2026-08-16 18:55:47**, unchanged |
| F-8 | `replay_path` · `audit_emission` | **NOT PERFORMED** — **0 · 0** |
| F-9 | Policy selection or a position between Option 1 and Option 2 | **NOT TAKEN** — §1.2 N-8 forbids it and §0.4 discloses the corrected margin without resolving it |

### 5.1 Preparation Attestation

| Property | State |
|---|---|
| R-4 modified | **NO** |
| P-3 selected | **NO** |
| Correction executed | **NO** |
| Files written by this preparation | **1** — this document |
| New governance surface created | **NO** |
| Implementation authorized | **NO** |
| Repository mutation performed | **NONE** |

*This document is a correction execution preparation artifact. It defines the edit sequence and
performs none of it. It selects no policy, marks no checkbox, and confers no authority. R-4 remains at
sha256 `074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb`, mtime 2026-08-16 18:55:47,
with all five decision fields unmarked. HEAD remains `1f869865` on `integration/recovery-001`.*

---

H-06 R-4 controlled correction execution preparation complete.
R-4 correction not executed.
P-3 selection not performed.
Implementation remains gated.
No repository mutation performed.
