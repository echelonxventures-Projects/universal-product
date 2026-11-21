# H-06 IADR §8 SIGNATURE PACKAGE

| Field | Value |
|---|---|
| **ID** | H-06-IADR-SP |
| **Authority** | SIGNATURE PREPARATION ONLY. Not a signature. Not an authorization. No implementation authorized. |
| **Phase** | Foundation Closure — Gate Purity — Implementation Authorization Signature Preparation |
| **Signature target** | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATED.md` §8 — **UNSIGNED** |
| **Signature authority** | Mutation Governance Owner |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` · 0 commits since baseline |
| **Produced** | 2026-08-16 |
| **Status** | **PACKAGE PREPARED — SIGNATURE FIELDS BLANK — SIGNATURE PENDING** |

---

## 0. The Authorization Boundary

> **IADR §8 signature is the authorization boundary.**
> **No owner decision record substitutes for the signature.**
> **No implementation may begin until signature validation passes.**

This statement governs every section below. The owner decision record at
`H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md` records five APPROVED phase
dispositions and is complete — and it still authorizes nothing. The boundary is §8, and §8 is
unsigned.

---

## 1. Pre-Preparation Verification

Measured read-only before this package was written.

### 1.1 Owner Decision Record

| Check | Measured | Result |
|---|---|---|
| Record | `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md` · sha256 `6eb3f97d763b87730651e7a39a0f48db3369776d2b31e017217abf066ac3ee98` | — |
| Entry A-1 | **CLOSED** | **CONFIRMED** |
| `APPROVED` marks | **5** | **CONFIRMED** |
| `REJECTED` marks | **0** | **CONFIRMED** |
| Acknowledgements | **3 of 3 marked** | **CONFIRMED** |
| `Authorized By` · `Date` | **Bipin Kumar** · **2026-08-16T20:10:00+05:30** | **CONFIRMED** |
| §8.3 completion | **10 of 10 satisfied** | **CONFIRMED** |
| Validation determination | `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-VALIDATION-DETERMINATION.md` — **OWNER DECISION VALIDATION PASSES**, 8 of 8 checks | **PASS** |

### 1.2 IADR Status

| Check | Measured | Result |
|---|---|---|
| Original IADR unchanged | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md` · sha256 `90e856f6…` · mtime **2026-08-16 17:01:26** · 0 marked boxes | **UNCHANGED — immutable historical artifact** |
| Updated IADR alignment artifact available | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATED.md` · sha256 `9c96ebf7…` · 442 lines · U-1..U-8 applied · validated 5 of 5 | **AVAILABLE** |
| §8 remains unsigned | `[ ] AUTHORIZED` · `[ ] NOT AUTHORIZED` — **0 marked boxes** · `Authorized By` `________________` · `Date` `________________` | **UNSIGNED** |

### 1.3 R-4 Status

| Check | Measured | Result |
|---|---|---|
| R-4 correction pending | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` · mtime **2026-08-16 18:55:47** · unmodified | **CORRECTION STILL PENDING** |
| Defective text still present | C-5's "36 gate targets with no declaration surface" — **1 occurrence, uncorrected** | **CONFIRMED PENDING** |
| P-3 selection | **0 marked boxes** — not selected, and not selected by this package | **UNSELECTED** |

### 1.4 Repository Boundary

| Check | Measured |
|---|---|
| HEAD · branch | `1f869865` · `integration/recovery-001` · **0** commits since baseline |
| `gate_mode` · `replay_path` · `audit_emission` in JSON surfaces | **0** |
| `*-declaration.json` modified | **0 of 11** |
| `mutation-governance-boundary.json` | **UNCHANGED** — clean status · sha256 `509d1a4d…` · mtime 2026-08-12 17:19:25 |

---

## 2. Authorization Chain Summary

| # | Link | Source | State |
|---|---|---|---|
| 1 | Mutation governance owner decision — Option B | `H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md` §7 — Bipin Kumar, 2026-08-16 | **RECORDED** |
| 2 | Ratification validation | `H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md` §8 | **PASS — 5 of 5** |
| 3 | Implementation authorization request | `H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md` | **VALID** |
| 4 | IAR validation | `H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md` §9 | **PASS — 7 of 7** |
| 5 | Ownership disposition owner decision | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-RECORD.md` r4 §9 — 5 APPROVED, entry E-3 CLOSED | **RECORDED** |
| 6 | Ownership decision validation | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-VALIDATION-DETERMINATION.md` §9 | **PASS — 5 of 5** |
| 7 | IADR alignment update | `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATED.md` — U-1..U-8 | **APPLIED** |
| 8 | Alignment update validation | `H-06-IADR-ALIGNMENT-UPDATE-VALIDATION-DETERMINATION.md` §7 | **PASS — 5 of 5** |
| 9 | Implementation authorization owner decision | `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md` §5 — 5 APPROVED, entry A-1 CLOSED | **RECORDED** |
| 10 | Owner decision validation | `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-VALIDATION-DETERMINATION.md` §7 | **PASS — 8 of 8** |
| **11** | **IADR §8 signature** | **Updated IADR §8** | **UNSIGNED — THIS PACKAGE** |
| 12 | Signature validation | Not yet produced | **PENDING** |
| 13 | Controlled execution approval | CIEP v2, per phase | **NOT GRANTED** |

**Links 1–10 are complete. Link 11 is the boundary. Links 12–13 are downstream.**

---

## 3. Owner Decision References

### 3.1 The Two Recorded Owner Decisions

| Decision | Record | Values | Effect |
|---|---|---|---|
| **Ownership disposition** | ODODR r4 §9 · sha256 `277369a9…` | 5 APPROVED · 3 acknowledgements · Bipin Kumar · 2026-08-16T20:10:00+05:30 · entry E-3 CLOSED | Adopted the ownership model: 22 declarable · 23 governed gaps · 45 dispositioned · no new surface · GP-11a/GP-11b · F-5/F-6 |
| **Implementation authorization phases** | IAODR §5 · sha256 `6eb3f97d…` | 5 APPROVED · 3 acknowledgements · Bipin Kumar · 2026-08-16T20:10:00+05:30 · entry A-1 CLOSED | Recorded phase-level governance direction across preparation, declaration mutation, engine remediation, registry (conditional), and controlled execution |

### 3.2 Phase Dispositions Recorded

| # | Phase | Owner disposition |
|---|---|---|
| 1 | Implementation preparation | **APPROVED** |
| 2 | Declaration mutation after validation | **APPROVED** |
| 3 | Engine remediation | **APPROVED** |
| 4 | Registry modification where separately approved | **APPROVED** — conditional; see §5.2 |
| 5 | Controlled implementation execution | **APPROVED** |

### 3.3 Acknowledgements On Record

All three marked by the owner on IAODR:

| # | Acknowledgement |
|---|---|
| 1 | Approval does not authorize implementation automatically |
| 2 | Implementation requires separate execution authorization |
| 3 | Gate purity closure remains dependent on residual findings GP-1, GP-3, GP-11 |

**Acknowledgement 1 is the owner's own recorded statement of why this package exists.** The phase
approvals do not authorize; the signature does.

---

## 4. Exact Scope Being Authorized

Signing §8 authorizes **exactly and only** the following, per updated IADR §§4.0–4.8 and IAR §§1
and 4. Nothing may be added, removed, or reinterpreted at the point of signature.

### 4.1 Population and Reach

| Figure | Meaning |
|---|--:|
| Gate targets at HEAD | **45** |
| Declaration surfaces in scope | **11** `*-declaration.json` files (IAR §1.1) |
| Gate targets reachable by those 11 files | **9** — `uga-declaration.json` and `urr-declaration.json` own no `*-gate` target |
| Targets eligible under ownership Decision 1 | **22** (Class A 9 + Class B 13) — **eligibility is not authorization** |
| Authorized declarations | **4** |

```
9 authorized-reachable  +  13 eligible-but-unauthorized  +  23 governed gaps  =  45
```

### 4.2 Authorized Work Items

| # | Item | Bound |
|---|---|---|
| S-1 | Additive `gate_mode` on the programme block of the 11 in-scope `*-declaration.json` files | Values limited to `OBSERVE` · `PRODUCER` · `EXECUTION`; optional `audit_emission` sub-field for `OBSERVE_WITH_DECLARED_AUDIT_EMISSION`. No mode written before P-2 measurement. No mode on a surface whose engine lacks a `--check-declaration` guard (F-6) |
| S-2 | Per-programme `gate_mode` values written after P-2 | Per programme, after measurement only |
| S-3 | Replay contract for every `PRODUCER` programme | Named path regenerating in memory, comparing committed bytes without writing first, failing on any difference. **Hard co-obligation** — a PRODUCER declaration without a tested replay path is reclassification-as-conformance, refused by GATE-PURITY D-3.6 |
| S-4 | GP-2 write-order correction | **3 engines**, identities confirmed per P-4 first |
| S-5 | GP-4 dead flag resolution | **3 engines**, identities confirmed per P-5 first |
| S-6 | GP-5 / GP-9 audit classification correction | `verify.sh` stage 4 label "Read-only" → `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` |
| S-7 | GP-10 `emit()` tier guard | `aee_engine.py:1807`, suppress under `--tier observe` |
| S-8 | Post-implementation verification | Updated IADR §4.8 — structural · behavioural · verification run · GP-1..GP-11 re-assessment under GP-11a/GP-11b with A-1..A-7 |

### 4.3 What Executing This Scope Does Not Achieve

| Finding | Terminal state after full authorized execution |
|---|---|
| GP-2 · GP-4 · GP-10 | **CLOSED** |
| GP-1 · GP-3 · GP-11 | **OPEN (residual)** |
| Gate purity dimension | **NOT CLOSED** |
| Foundation Freeze | **NOT CLOSED** — gate purity is one dimension of six criteria F-1..F-6 |

This matches the owner's marked acknowledgement 3. **Signing §8 does not buy gate purity closure.**

---

## 5. Explicit Exclusions

Not authorized by an §8 signature, under any reading, regardless of any other instruction or
artifact. Updated IADR §5 carries all seventeen rows; the substantive classes are:

| # | Excluded |
|---|---|
| X-1 | Creation of any new registry, governance surface, authority layer, schema family, or constitutional document |
| X-2 | Modification of `mutation-governance-boundary.json` — authority chains or any content |
| X-3 | Modification of `generated-artifact-registry.json` beyond what GP-2/GP-4 fixes strictly require |
| X-4 | `gate_mode` on any **Class B** surface — eligible under Decision 1, **unauthorized** here |
| X-5 | `gate_mode` on any **Class C or Class D** target — governed gaps only |
| X-6 | `gate_mode` on any surface whose owning engine lacks a `--check-declaration` guard (F-6) |
| X-7 | GP-1 and GP-3 remediation — outside authorized scope |
| X-8 | Architecture changes not required by GP-2, GP-4, GP-5, GP-10, or declaration additions |
| X-9 | Any change to `00-BOOK/DATA/` not required by approved scope |
| X-10 | Any change to H-01..H-05 or R-B1..R-B5 scope |
| X-11 | Any engine not listed in GP-1..GP-11 findings |
| X-12 | CI workflow changes beyond those strictly required by GP-2 or GP-4 fixes |
| X-13 | Foundation Freeze declaration |
| X-14 | Modification of UICO or UICM artifacts |
| X-15 | Any action in IAR §5 Forbidden Actions — all nine rows |

### 5.1 `uar-gate` Asymmetry — Disclosed

`uar-gate` is a governed gap whose engine **does** carry a `--check-declaration` guard, but whose
`programme` value is a JSON **string**, so no field is insertable without a structural change that
IADR §5 forbids. Its **GP-2 code fix is authorized while its mode declaration is not.** Disclosed,
not resolved; acknowledged by the owner on ODODR r4.

### 5.2 Registry Modification — Owner Approved In Principle, Still Excluded

IAODR Decision 4 is recorded **APPROVED**. That mark records an in-principle position only. Registry
modification remains excluded by X-2 and X-3 and is recorded in updated IADR §5 as not authorized
under H-06 at all. **An §8 signature does not convert Decision 4 into permission.** Any registry
change would additionally require the separate independent approval the decision's own title
contemplates, plus an amendment to the exclusion set under its own authority.

---

## 6. Remaining Blockers

**Signing §8 clears exactly one of four blockers. Three survive the signature.**

| # | Blocker | State | Cleared by signature? | Authority to clear |
|---|---|---|---|---|
| 1 | **IADR §8 signature** — CIEP v2 Phase 0.1 | **PENDING — UNSIGNED** | **YES** | Mutation Governance Owner |
| 2 | **R-4 correction** — §7 acknowledgement and C-5 misdescribe 13 Class B targets as surface-less | **PENDING — NOT PERFORMED** | **NO** | Explicit correction authority |
| 3 | **P-3 selection** — CIEP v2 Phase 0.2; blocked by blocker 2 | **PENDING — UNSELECTED** | **NO** | Mutation Governance Owner, after blocker 2 |
| 4 | **Phase 0 conditions** — all six required | **PENDING — NOT SATISFIED** | **PARTIAL — 0.1 only** | Mixed |

### 6.1 Phase 0 Detail

| # | Condition | State | Owner of the act |
|---|---|---|---|
| 0.1 | IADR §8 AUTHORIZED — signed and dated | **FAIL** | Signature authority — **this package** |
| 0.2 | P-3 R-4 policy selected | **FAIL** — blocked by R-4 correction | Owner |
| 0.3 | Baseline confirmed | **PASS** — `1f869865` · `integration/recovery-001` | — |
| 0.4 | Corrected success criteria accepted (O-7) | **ELIGIBLE FOR RE-MEASUREMENT** — ODODR Decision 2 resolved O-7; acknowledgement 2 accepts GP-11 OPEN (residual). Re-measurement is an owner act, not performed here | Owner |
| 0.5 | `verify.sh` baseline captured (A-1 defect) | **FAIL — never captured** | Implementation authority (preparatory) |
| 0.6 | Unrelated deltas isolated | **FAIL** — `verify.sh` +45/−0 · `generated-artifact-registry.json` +864/−0 | Owning programmes (UAUE et al.) — H-06 cannot commit their work |

**No phase begins until all six pass.** A signature today leaves 0.2, 0.5 and 0.6 failing and 0.4
unmeasured.

### 6.2 Ordering Constraint

```
R-4 correction  →  P-3 selection  →  ┐
Phase 0.4 re-measurement          →  ├→  Phase 0 all six PASS  →  controlled execution approval
Phase 0.5 baseline capture        →  │
Phase 0.6 isolation               →  │
IADR §8 signature  ────────────────→ ┘
```

The signature is independent of blockers 2–4 and may be executed before or after them, but
**implementation begins only when every branch converges.**

---

## 7. Signature Fields

**BLANK BY CONSTRUCTION. No value supplied, inferred, defaulted, or recommended into any field by
this package. This package is not a signature and does not become one by being prepared.**

Signing is performed against **updated IADR §8** — this section mirrors the fields so the package is
self-contained; it does not replace §8, and a mark here does not mark §8.

**Implementation Authorization:**

```
[ ] AUTHORIZED
[ ] NOT AUTHORIZED
```

**Authorized By:**
________________

**Date:**
________________

**Signature:**
________________

### 7.1 Completion Requirement

The signature is complete only when **all four** hold:

| # | Condition | Current |
|---|---|--:|
| 1 | Exactly one of `AUTHORIZED` / `NOT AUTHORIZED` marked — never both | **0 marks** |
| 2 | `Authorized By` populated | **blank** |
| 3 | `Date` populated — ISO 8601 | **blank** |
| 4 | `Signature` populated | **blank** |

**0 of 4 satisfied.** A partially completed signature block records no authorization; mixed states
are not interpolated, and no recommendation may populate any field.

---

## 8. Signature Validation Requirements

To be performed after signature by a separate determination —
`H-06-IADR-SIGNATURE-VALIDATION-DETERMINATION.md`. The checks are fixed now so the standard cannot
be adjusted afterward.

| # | Check | Pass condition |
|---|---|---|
| V-1 | Exactly one authorization mark | 1 of 2 marked · 0 double-marked, verified by mark-agnostic scan |
| V-2 | Identity completeness | `Authorized By` non-blank, non-placeholder, matching the signature authority of record |
| V-3 | Date completeness | Valid ISO 8601, recorded verbatim including offset |
| V-4 | Signature presence | `Signature` populated |
| V-5 | Scope integrity | Authorized scope identical to §4 — no element added, removed, or reinterpreted at signature |
| V-6 | Exclusion integrity | All exclusions X-1..X-15 intact; none relaxed by the signature |
| V-7 | Chain integrity | Links 1–10 re-measured and still CONFIRMED/PASS |
| V-8 | Blocker honesty | Blockers 2, 3, 4 reported as still pending unless independently evidenced |
| V-9 | Boundary preservation | 0 declaration mutations · 0 `gate_mode`/`replay_path`/`audit_emission` · 0 engine writes · 0 registry writes · `mutation-governance-boundary.json` unchanged · HEAD and branch unchanged · 0 implementation commits |

**Mandatory finding.** The validation must state explicitly that a signature satisfies **Phase 0.1
only**, and must not report implementation as permitted while any of Phase 0.2, 0.4, 0.5 or 0.6
remains unsatisfied.

---

## 9. Package State Attestation

| Property | State |
|---|---|
| Signature fields | **4 — all blank** |
| Authorization marks | **0** |
| Chain links 1–10 | **COMPLETE** |
| Updated IADR §8 | **UNSIGNED — 0 marked boxes** |
| Original IADR | **UNCHANGED** — `90e856f6…`, mtime 17:01:26 |
| R-4 | **UNCHANGED** — mtime 18:55:47, correction pending |
| P-3 | **UNSELECTED** |
| Phase 0 | **1 PASS · 4 FAIL · 1 awaiting re-measurement** |
| Implementation authorized | **NO** |
| Gate purity closed | **NO** |
| Repository mutation performed | **NONE** — no declaration modified · no `gate_mode` / `replay_path` / `audit_emission` added · no engine modified · no registry modified · `mutation-governance-boundary.json` unchanged · no implementation commit |

*This document is a signature preparation package. It is not a signature, not an authorization, and
not permission to act. It carries no mark, states no recommendation for the signature decision, and
confers no authority. **IADR §8 signature is the authorization boundary. No owner decision record
substitutes for the signature. No implementation may begin until signature validation passes.** HEAD
remains `1f869865` on `integration/recovery-001`.*

---

H-06 IADR signature package prepared.
Authorization signature pending.
No implementation authorized.
No repository mutation performed.
