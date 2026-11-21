# UCOS-URR-001 — DISPOSITION DETERMINATION

| | |
|---|---|
| **ARTIFACT ID** | UCOS-URR-001-DISPOSITION |
| **PROGRAM** | Ω-A07 Universal Foundation Completion |
| **AUTHORITY** | NONE (DERIVED TRUTH) |
| **STANDING** | DERIVED — records a measurement and an open question; decides nothing |
| **SUBJECT** | `00-MASTER/UCOS-URR-001/urr-declaration.json` |
| **SUBJECT STANDING** | **PROPOSED — NOT ADMITTED.** Holds no authority. Not Repository Truth. |

## 1. Why this record exists

Ω-A07 found an in-flight artifact: a 698-line discovery-grammar declaration for a *Universal
Requirement Repository* — modal lexicon, anchor grammar, authority zones, criteria records,
thirteen inference laws, acceptance signals, coverage rules, nineteen gap classes, priority and
risk rules, A–G comparison axes, twelve integrity conditions, twelve closure conditions and
eighteen deliverables. It is careful, substantial work.

It is also **unimplemented and unadmitted**. Measured:

| Declared integration surface | Present? |
|---|---|
| `00-MASTER/UCOS-URR-001/urr_engine.py` | **ABSENT** |
| `.github/workflows/urr-gate.yml` | **ABSENT** |
| `engine/tests/unit/test_urr_requirement_repository.py` | **ABSENT** |
| Makefile targets `urr`, `urr-gate`, `urr-self`, `urr-replay`, `urr-closure-gate` | **0 of 5 present** |
| The declaration itself | present, **untracked** |

So the artifact declares its own integration surface and none of it exists. Under
`REG-AUTO-001` P7 that is an engine no target names — the exact defect class
`UAKOS-CLOSURE-009` was raised to close. Ω-A07 will not leave it undisclosed, and Ω-A07 will
not implement it either. This record says why, and states the decision that is not mine to take.

## 2. Why it was NOT implemented

Ω-A07's mission is explicit: *"The objective is no longer to build additional independent
frameworks."* Implementing this declaration as written would build a nineteenth independent
programme with its own eighteen-deliverable register plane over a population that is **already
registered**:

| | `UAKOS-CLOSURE-009` (committed, tracked) | `UCOS-URR-001` (proposed) |
|---|---|---|
| Requirements registered | **541** | would register its own |
| Gap classes | **19** | 19 (differently defined) |
| Work packages | **12** | would derive its own |
| Baseline conditions | **12** | 12 closure conditions |
| Determination | `ASSIMILATION-INCOMPLETE` | would emit its own |
| Standing | tracked, gated, re-rendered | untracked, ungated |

Two register planes over one requirement population, each computing its own gap classes, its own
priorities and its own headline determination, is precisely what `UCOS-UFC-001` **UFC-16** names
a constitutional contradiction:

> One subject population SHALL yield one measurement. Two Foundation surfaces reporting
> different numbers for the same population under the same policy is a constitutional
> contradiction and SHALL be converged, never reconciled by note.

Ω-A07 has just spent its whole execution removing one such contradiction — two ownership
determinations over 541 subjects reporting 151/390/2 and 180/361/0. Creating a second one in the
requirement layer on the same pass would be incoherent. **The reusable capability was
implemented; the parallel programme was not.**

## 3. What was implemented instead

The declaration's *mechanism* — "measurement by declared policy, extensible by registration,
never by editing an engine" — is not rejected. It is the mechanism Ω-A07 built and certified, at
Foundation tier where every future programme inherits it rather than in one programme's plane:

| The declaration's mechanism | Where it now lives, reusable |
|---|---|
| Authority zones, ranks, canonical-home eligibility | `platform.universal_truth` — declared zone policy (`UCOS-URTF-001`) |
| Registration eligibility, form and residue rules | `platform.universal_truth.eligibility` — declared eligibility ledger |
| Evidence kinds and criteria records as pluggable sources | `platform.universal_ownership.evidence` — registered evidence providers (`UCOS-UOF-001`) |
| Coverage rules, gap classes, priority as measured policy | `platform.universal_measurement` — registered policies with declared blocking and precedence (`UCOS-UMPF-001`) |
| Integrity and closure conditions as executable gates | `platform.universal_foundation.freeze` — declared criteria, each bound to a measured evidence kind |
| Inference laws as declared, measured obligations | `platform.universal_foundation.conformance` — one executable probe per declared article |
| Recommendation instead of manual triage | `platform.universal_ownership.recommendation` — deterministic proposals, never ownership |

A future Universal Requirement Repository is therefore a **specialisation document plus
registered policies** against the frozen Foundation. It is no longer an engine anyone has to
write, which is the whole point of having converged the Foundation first.

## 4. The decision that is not mine

Three constitutionally valid alternatives remain, and choosing between them changes the standing
of a **committed, gated register**. That makes it a governance act, not an engineering one:

**Alternative A — ADMIT AS EXTENSION (recommended).** `UAKOS-CLOSURE-009` remains the canonical
requirement register. The declaration's broader discovery grammar — the modal lexicon, the open
anchor grammar, the inference laws, the conversation-origin and document-origin classes — is
admitted as declared *extensions* to that owner, expressed as registered Foundation policies.
Nothing is superseded, no second plane appears, and the discovery breadth is gained.
*Consequence:* `UAKOS-CLOSURE-009`'s register grows and must be re-certified.

**Alternative B — SUPERSEDE.** The URR grammar becomes the canonical requirement model and
`UAKOS-CLOSURE-009`'s register is explicitly superseded, with the supersession recorded under
`CMG-000001` XVI.6 and the prior owner preserved in lineage per `CEP-002` 14.4.
*Consequence:* a certified register is retired; every consumer of its 541 requirement identities
must be re-pointed. Higher cost, and it discards a measurement currently in force.

**Alternative C — REJECT.** The declaration is recorded as considered and not adopted, with
constitutional justification, and removed.
*Consequence:* the discovery breadth is lost. `UAKOS-CLOSURE-007` §3 already recorded an
IDENTIFIER COMPLETENESS: FAIL that this declaration's open anchor grammar was written to
remediate, so rejection leaves a known finding open.

**Recommendation: A.** It is the only alternative that both preserves a measurement in force and
gains the discovery breadth, and it is the only one that requires no second plane. It is
recommended, **not decided**: `CEP-002` 14.2 reserves this class of act to a governing authority,
and Ω-A07's own governance-minimisation rule forbids replacing a deterministic capability with a
manual decision *and equally* forbids taking a decision reserved to an authority.

## 5. Standing of the subject until that decision is taken

* The declaration **holds no authority** and is **not Repository Truth**.
* No engine reads it. No gate consumes it. No target invokes it.
* It is **not** a Foundation capability: it is absent from
  `platform/universal_foundation/catalog/foundation-capabilities.json`, so the Foundation
  Constitution does not govern it and the freeze determination does not depend on it.
* It is **not** a constitutional model: it is absent from
  `platform/universal_foundation/catalog/foundation-convergence.json`, so it contributes no
  duplicate implementation and no competing authority.
* It therefore **does not block the Foundation freeze**, and is reported as the one open
  governance decision rather than as a Foundation gap.

Recorded so that a future run finds a disclosed proposal with a stated standing, and does not
mistake an unadmitted declaration for authorized work.
