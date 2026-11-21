# H-06 R-4 CORRECTION EXECUTION — VALIDATION DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-R4-CEVD |
| **Authority** | VALIDATION ONLY. No P-3 selection. No implementation execution. No declaration, engine, or registry mutation. |
| **Phase** | Foundation Closure — Gate Purity — R-4 Evidence Correction Executed |
| **Subject** | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` — corrected **r1 → r2** |
| **Executed under** | `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` · `H-06-R4-CONTROLLED-CORRECTION-EXECUTION-PREPARATION.md` (RC-1..RC-8) |
| **Baseline** | HEAD `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · 0 commits |
| **Produced** | 2026-08-16 |
| **Determination** | **CORRECTION EXECUTED AND VALIDATED — R-4 OWNER DECISION PENDING — P-3 PENDING — IMPLEMENTATION GATED** |

---

## 1. Hashes

| # | Artifact | sha256 | Size |
|---|---|---|---|
| **1** | **R-4 before correction (r1)** | **`074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb`** | 284 lines · 13,405 bytes |
| **2** | **R-4 after correction (r2)** | **`3f0abe615d32de48a4f66a0e536f98290ddc2d392a2a8a4d0af45b887966de15`** | 347 lines · 18,542 bytes |
| 3 | Preservation copy `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.pre-r2.md` | **`074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb`** — byte-identical to row 1 | 13,405 bytes |

**Pre-mutation hash was recorded and asserted before any edit.** The measured hash matched the
value carried forward from the preparation artifact, confirming the correct artifact was edited.
Rollback to row 1 remains possible from row 3, which reproduces the original hash exactly.

**Preservation copy naming.** `.pre-r2.md` — the `.save` suffix was **not** used, per
`H-06-DOCUMENT-CANONICALITY-CLEANUP-DETERMINATION.md`, which raised that pattern as a finding
because a `.save` twin creates a second readable version of a governance record.

---

## 2. Pre-Execution Verification

### 2.1 HEAD

| Check | Measured |
|---|---|
| Commit | `1f869865d5ff709c03cb4eb595524820d55d0be6` |
| Branch | `integration/recovery-001` |
| Clean / dirty | **DIRTY — 183 entries, all pre-existing**; none created by this correction, and none in a declaration, engine, or registry surface attributable to it |
| Commits since baseline | **0** |

### 2.2 Governance Chain

| Link | Result |
|---|---|
| ODODR validation | **OWNER DECISION VALIDATION PASSES** |
| IAODR validation | **OWNER DECISION VALIDATION PASSES** |
| IADR signature validation | **SIGNATURE VALIDATION PASSES** — §8 `[X] AUTHORIZED`, 1 mark |

### 2.3 R-4 Pre-State

| Check | Measured |
|---|---|
| sha256 | `074582134dbdd248…` |
| mtime | 2026-08-16 18:55:47 |
| Checkbox state | **5 fields, 0 marked** |
| Owner selection fields | `Selected By` and `Date` both `________________` |

### 2.4 Prohibited Mutations — Zero Before

`gate_mode` **0** · `replay_path` **0** · `audit_emission` **0** · declarations modified **0** ·
engine writes **0** · registry writes **0** · `mutation-governance-boundary.json` clean at
`509d1a4d…`.

---

## 3. RC-1 Through RC-8 Verification

Executed in the prepared order — RC-1, RC-2, RC-3, RC-6, RC-5, RC-8, **RC-4 last**, RC-7 audit.

| # | Correction | Applied at | Verification | Result |
|---|---|---|---|---|
| **RC-1** | C-5 two-population correction | §5 control C-5 | Defective phrase "36 gate targets with no declaration surface" → **0 occurrences**; "23 gate targets with no capable owning surface" present; 13 Class B recorded as eligible-but-unauthorized | **VERIFIED** |
| **RC-2** | Creation-act counts 36 → 23 | §4.1 · §5 · §6 · §8 | "36 new declaration files" **0** · "36 acts" **0** · "36 absent declaration files" **0** · "36 of them have nowhere" **0**; three `**23**` creation-count statements present | **VERIFIED** |
| **RC-3** | Class A/B/C/D model + reconciliations | new §3.4 | §3.4 present; `Class A 9 + Class B 13 + Class C 11 + Class D 12 = 45` present; `22 + 23 = 45` and `9 + 13 + 23 = 45` present; **Eligibility ≠ Authorization** stated explicitly; all 13 Class B surfaces named | **VERIFIED** |
| **RC-4** | §7 acknowledgement — **applied last** | §7 | Acknowledgement now states 9 authorized-reachable · 13 Class B eligible-but-unauthorized · 23 Class C/D governed gaps, and that eligibility is not authorization; `[ ] ACKNOWLEDGED` remains **UNMARKED** | **VERIFIED** |
| **RC-5** | Disposition split | §4.2 · §7 | §4.2 distinguishes the 13 from the 23; §7 provides separate disposition blocks **(a)** for the 13 and **(b)** for the 23 — see §3.1 disclosure | **VERIFIED** |
| **RC-6** | Option 2 cost restated on two grounds | §4.1 · §6 · §8 | Option 2 fails on two distinct grounds: 23 forbidden creations (IAR §1.1, IADR §5) **and** 13 unauthorized Class B writes (updated IADR §5 exclusion); conflict table gained the Class B exclusion row | **VERIFIED** |
| **RC-7** | Preservation audit | §3.2 · §3.3 · §5.1 · §8 · C-1..C-4 | Byte comparison against pre-mutation extracts — see §4 | **VERIFIED** |
| **RC-8** | Cross-references + revision marker | Header · §3.3 | Header `Depends on` gained GOMRD, ODODR r4 §4, updated IADR §3.2/§5; revision marker **r2 — evidence correction** present, recording that no decision field was altered; §3.3 "See" sentence extended to point at §3.4 | **VERIFIED** |

### 3.1 Disclosure — Decision Field Count Increased 5 → 7

RC-5's structural split necessarily added a disposition sub-field pair. The record now carries
**7** checkboxes rather than 5:

| Field | State |
|---|---|
| `OPTION 1 — Temporary Compliance Window` | **`[ ]` UNMARKED** |
| `OPTION 2 — Immediate Non-Compliance` | **`[ ]` UNMARKED** |
| **(a)** 13 Class B — eligible-but-unauthorized *(new)* | **`[ ]` UNMARKED** |
| **(a)** 13 Class B — Other (specify) *(new)* | **`[ ]` UNMARKED** |
| **(b)** 23 Class C/D — explicit scope gap | **`[ ]` UNMARKED** |
| **(b)** 23 Class C/D — Other (specify) | **`[ ]` UNMARKED** |
| `ACKNOWLEDGED` | **`[ ]` UNMARKED** |

**Consequence for P-3 completion:** the owner must now dispose of the two populations separately.
This is the intended effect of RC-5 — a single "disposition of the 36" field could not express a
disposition for a population where a pending mode is recordable and one where it is not.
**Total marked: 0.** Disclosed because it changes what a complete P-3 transmission looks like.

### 3.2 Disclosure — §3.4 Insertion Renumbered §3.4 → §3.5

Inserting the class model as §3.4 shifted the pre-existing "Consequence for the Policy Choice"
from §3.4 to **§3.5**. Its content is otherwise unchanged. No cross-reference elsewhere in R-4
pointed at the old §3.4 number.

---

## 4. Preservation Verification

| # | Item | Method | Result |
|---|---|---|---|
| **PV-1** | §3.2 measurement and 36-name enumeration | Byte comparison against pre-mutation extract | **PRESERVED — byte-identical** |
| **PV-5** | §8 P-3 dependency language — closing P-3 does not authorize implementation; §8 signature independent; neither substitutes for the other | Byte comparison | **PRESERVED — byte-identical** |
| **PV-6** | §3.3 heterogeneity finding | Byte comparison + phrase audit | **FINDING PRESERVED** — see §4.1 |
| **PV-7** | §5.1 pending vocabulary `UNDECLARED-PENDING-MIGRATION`, transitional and additive | Byte comparison | **PRESERVED — byte-identical** |
| **PV-10** | Controls C-1, C-2, C-3, C-4 | Byte comparison | **PRESERVED — byte-identical** |
| **PV-3** | 45-target denominator and §3.1 measurement | Inspection | **PRESERVED** — every corrected statement uses 45 |
| **PV-9** | §6 recommendation direction | Inspection | **UNCHANGED — Option 1** |

### 4.1 PV-6 — Exactly What Changed In §3.3

The byte comparison flagged §3.3, and the difference is **one appended cross-reference clause**,
applied under RC-8:

| | Text |
|---|---|
| Before | `…The declaration surface is heterogeneous. See H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md §3.` |
| After | `…The declaration surface is heterogeneous. See H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md §3, and §3.4 below for the class model this heterogeneity produces.` |

The substantive finding is intact, phrase by phrase: "The 14 engines carrying", "differently-named",
"`rib_engine.py` reads", "rib-blueprint.json", "uaie-architecture.json", "The declaration surface is
heterogeneous" — all present. **Rule N-2 protects the finding, and the finding did not change**;
RC-8 authorizes cross-reference updates. Reported precisely rather than asserted as byte-identical.

### 4.2 Arithmetic Re-Derived From Preserved Evidence

Recomputed from R-4's own §3.2 enumeration, independently of any corrected narrative:

| Derivation | Result |
|---|---|
| Enumeration count | **36** ✓ |
| Class B names present | **13 of 13** ✓ |
| Remainder | **23** ✓ |
| `13 + 23` | **36** ✓ |
| `9 + 13 + 23` | **45** ✓ |

**Every corrected count is re-derivable from preserved evidence.** No corrected figure rests on the
corrected narrative alone.

### 4.3 Option 1 / Option 2 Distinction Preserved

§4.1 remains the **Option 2 — Immediate Non-Compliance** assessment; §4.2 remains **Option 1 —
Temporary Compliance Window**. The corrections were applied to the correct option: the creation-act
counts sit in §4.1 (Option 2), and the incremental-tracking language sits in §4.2 (Option 1). This
was the misattribution corrected at execution-preparation §0.3 before any edit was made.

---

## 5. Required Confirmations

| # | Confirmation | Measured | Result |
|---|---|---|---|
| 1 | **Owner fields remain unmarked** | **0** marked checkboxes of 7; `Selected By` `________________`; `Date` `________________` | **CONFIRMED** |
| 2 | **P-3 remains unselected** | Neither Option 1 nor Option 2 marked; no disposition marked; ACKNOWLEDGED unmarked | **CONFIRMED** |
| 3 | **No implementation executed** | 0 phases begun; Phase 0.2, 0.4, 0.5, 0.6 outstanding; 0 commits since baseline; HEAD `1f869865` | **CONFIRMED** |
| 4 | **No declaration mutation** | 0 of 11 `*-declaration.json` modified; `gate_mode` **0** · `replay_path` **0** · `audit_emission` **0** | **CONFIRMED** |
| 5 | **No engine mutation** | 0 files written under `engine/` | **CONFIRMED** |
| 6 | **No registry mutation** | 0 files written under `00-BOOK/DATA/`; `generated-artifact-registry.json` mtime **2026-08-15 10:49:30** unchanged; `mutation-governance-boundary.json` clean at `509d1a4d3f9af6e0…` | **CONFIRMED** |

### 5.1 Additional Confirmations

| Confirmation | Result |
|---|---|
| Recommendation direction unaltered | **CONFIRMED** — Option 1, unchanged |
| No wording improved beyond authorized corrections | **CONFIRMED** — every edit maps to an RC; no stylistic change |
| No new governance surface created | **CONFIRMED** |
| Original IADR still immutable | **CONFIRMED** — `90e856f6…`, mtime 17:01:26 |
| No rollback trigger fired | **CONFIRMED** — R-1..R-7 all negative |

### 5.2 Files Written

| File | Nature |
|---|---|
| `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` | Corrected r1 → r2 |
| `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.pre-r2.md` | Mandatory preservation copy, original hash |
| `H-06-R4-CORRECTION-EXECUTION-VALIDATION-DETERMINATION.md` | This determination |

Transient byte-comparison extracts were created under `.r4-correction-refs/` for the RC-7 audit and
**removed after use**; `pre-r2.md` is the authoritative preservation reference and reproduces every
extract.

---

## 6. P-3 Status Transition

| | Before correction | After correction |
|---|---|---|
| P-3 status | **BLOCKED** — the acknowledgement sat in a record whose C-5 asserted 36 surface-less targets, false for 13 | **ELIGIBLE FOR OWNER DECISION** |
| P-3 selection | Not performed | **Not performed** |
| CIEP v2 Phase 0.2 | **FAIL** | **STILL FAIL** — correctness of the record does not satisfy it; only the owner's selection does |

**Eligibility to decide is not a decision.** The record may now be presented for selection, on
corrected evidence that supports either outcome. No option is marked, recommended into a field, or
pre-disposed by this correction.

### 6.1 What A Complete P-3 Transmission Now Requires

One of Option 1 / Option 2 · migration deadline if Option 1 · disposition **(a)** for the 13 Class B
targets · disposition **(b)** for the 23 Class C/D targets · `ACKNOWLEDGED` · `Selected By` · `Date`.

### 6.2 Remaining Gates After P-3

Phase 0.4 owner re-measurement · Phase 0.5 `verify.sh` baseline capture · Phase 0.6 delta isolation
(owning programmes must commit `verify.sh` and `generated-artifact-registry.json`) · controlled
execution approval per CIEP v2 phase. Gate purity still does not close — GP-1, GP-3, GP-11 terminate
OPEN (residual).

---

## 7. Determination

| # | Check | Result |
|---|---|---|
| 1 | Pre-execution verification — HEAD, chain, R-4 state, zero prohibited mutations | **PASS** |
| 2 | Preservation copy created before mutation, exact original hash, no `.save` suffix | **PASS** |
| 3 | RC-1..RC-8 applied exactly as prepared, RC-4 last | **PASS** |
| 4 | Evidence and measurement sections preserved | **PASS** |
| 5 | 13 Class B / 23 true gap partition preserved and re-derivable | **PASS** |
| 6 | Option 1 / Option 2 distinction preserved | **PASS** |
| 7 | Only identified defects corrected; recommendation direction unaltered | **PASS** |
| 8 | Owner decision fields unmarked; P-3 unselected | **PASS** |
| 9 | No implementation, declaration, engine, or registry mutation | **PASS** |

**CORRECTION EXECUTED AND VALIDATED.** R-4 moves r1 `074582134dbdd248…` → r2
`3f0abe615d32de48…`, with the pre-correction artifact preserved at the original hash.

---

R-4 correction complete.
R-4 owner decision remains pending.
P-3 selection remains pending.
Implementation remains gated.
