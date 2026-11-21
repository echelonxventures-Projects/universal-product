# B-01 — Machine-Readable Birth Scope Governance Determination

| Field | Value |
|---|---|
| ITEM | Scope B · B-01 |
| POLICY | `00-MASTER/UOBC-000001/birth-scope-policy.json` (`UOBC-BSP-001`) |
| EXTENDS | `UOBC-000001` — scope of application only |
| CONSTITUENT AUTHORITY | **NONE** |
| GOVERNANCE AUTHORITY | **NONE** |
| PREDECESSOR | `SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md` §1.2 — the rule this file makes executable |

---

## 1. What B-01 does, and what it refuses to do

`SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md` §1.2 determined which object kinds require a birth record and which must never hold one independently. **That determination lived only in prose, so nothing computed it.** A generated artifact could be given an independent constitutional identity; a birth record could name a subject that does not exist; the adoption gap could widen with no signal. B-01 converts the rule into data and measures it.

This is the same upgrade `UCPA-000001` performed in Scope A: a ratified rule that nothing computed.

**B-01 refuses to backfill.** `G11`'s disposition — *"an explicit `register.sh` migration transaction, not a verification-time backfill"* — is not reopened. A gate that demanded 6,044 birth records would be a verification-time backfill wearing a different name.

---

## 2. The measurement that shaped the policy

Measured before the policy was written, because a policy written first and measured second describes an intention rather than a repository:

| Kind | On disk | Born | Coverage |
|---|---|---|---|
| Engine capability packages | 43 | **6** | 14% |
| Test suites | 821 | **7** | <1% |
| Determinations | 253 | **17** | 7% |
| Programmes | — | **5** | — |

**No kind is at 100%.** A policy declaring blanket `MANDATORY` adoption would therefore have closed the gate on the entire repository on the day it was installed, and would have been disabled rather than fixed. The honest enforceable form is UISD's: **refuse the undisclosed gap, not every gap.**

---

## 3. What is enforced today

| Law | Enforced now | What it makes impossible |
|---|---|---|
| `BSP-L-01` | **yes** | A kind missing a required field; a rule naming an absent check; a check no rule claims |
| `BSP-L-02` | **yes** | An object that classifies to no kind, or to two. Measured: **0 unresolved of 6,079** |
| `BSP-L-03` | **yes — strict** | **A generated or derived object holding an independent birth record.** The mandate's second objective, enforced absolutely |
| `BSP-L-04` | **yes — strict** | A birth record naming a subject that does not exist, or naming something generated. Measured: **35 of 35 resolve** |
| `BSP-L-05` | **yes** | A kind requiring birth with an undisclosed adoption state, or a DEFERRED state naming no gap |
| `BSP-L-06` | **yes — ratchet** | Adoption falling. Floors: PACKAGE 6 · TEST_SUITE 7 · DOCUMENT 17 · PROGRAMME 5, all measured, none with slack |

**The positive obligation is disclosed, not demanded.** Every kind requiring birth carries `adoption: DEFERRED` and names `G11`. The instant a kind's adoption flips to mandatory, enforcement follows **with no engine change** — the state is data.

---

## 4. Two design decisions, and why

### 4.1 Ordered first-match classification, with a mandatory catch-all

Kinds are evaluated in declared order; the first match wins. This makes classification **single-valued by construction** rather than by a uniqueness check that could pass while two selectors silently overlapped, and **total by construction** through a final `catch_all` kind that `BSP-L-02` requires to exist and to be last.

`ADDRESSED_OBJECT` is that catch-all, and it is the infinite-scope guarantee: **an object kind nobody has imagined is classified on the day it appears, with no engine change.** Promotion is by declaring a kind above it — never by editing code.

### 4.2 Coverage floors are keyed by subject class, not object kind

An inconsistency in the first draft of this policy, found by validating the specification against the repository before implementing it: floors were keyed by `object_kind` (a classification of **files**) while coverage counts **birth records**. Comparing a record count against a file population produces a number that means nothing.

Corrected: floors are keyed by the `subject_class` a birth record resolves to under `subject_resolution` — `PACKAGE`, `TEST_SUITE`, `DOCUMENT`, `PROGRAMME`. The two axes are deliberately distinct: `object_kind` answers *"may this file be born"*; `subject_class` answers *"what did this birth record name"*.

Validation after correction: **35 of 35 births accounted for, all four floors hold exactly, zero slack.**

---

## 5. Preserved decisions

| Decision | Preserved how |
|---|---|
| UCKP-ART-05 is the only identity authority | Policy `authority: NONE — DERIVED TRUTH`; holds no counter, mints nothing |
| Birth ≠ file existence | Granularity is the constitutional object: package, suite, declaration, document — never the path |
| Birth applies to capabilities, test suites, declarations, determinations | Four kinds, `birth_required: true` |
| Birth does not apply to generated projections, derived registers, rendered documents, build outputs | Two kinds, `enforcement: MANDATORY_ABSENCE`, enforced strictly by `BSP-L-03` |
| No new registry / identity system / lifecycle engine | Policy is a file under the **existing** `UOBC-000001`; measurement lives in the **existing** `engine/object_birth/`; gated by the **existing** UOBC stage in `./verify.sh` |

**No new verification stage is created.** Birth scope is part of the birth contract; a second stage would be a second place to look for one subject.

---

## 6. UELA consumption

B-01 closes the prerequisite named in `SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md` §5: *"§1.2 must be machine-readable before UELA can automate Birth Determination."* After B-01, UELA can answer **"does this object require birth?"** by reading `birth-scope-policy.json` — no prose, no chat history, no human interpretation.

---

*End of B-01-BIRTH-SCOPE-GOVERNANCE-DETERMINATION.md*
