# ADR-0014: Re-tighten the UCL unadmitted-target ratchet to its measured value

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCL-000001 UCL-V-41, UCL-V-42, UCL-F-004, UCL-F-005, CEP-002 Art 28 |
| Supersedes | none |

## Context

`UCL-V-41` and `UCL-V-42` are the only two failing criteria in UCL-000001; all thirteen self-checks and the other forty criteria pass. They fail because a declared ratchet has not been re-tightened after 77 commits of lawful work:

| Measure | Bound | Measured |
|---|---|---|
| `relationships_without_target_identity` | 217 | 274 |
| `unadmitted_target_artifacts` | 84 | 85 |

The bounds are not wrong; they are accurate records of a past measurement. `00-MASTER/UCL-000001/ucl-declaration.json` states the governing rule in its own `detail`: *"The bound is a RATCHET held at exactly the measured value, so it is re-tightened whenever governed records are lawfully admitted."*

The delta was measured by identity, not by count, as that rule requires. Exactly **one** artifact was added and none removed: `engine/constitution/stages.py`, introduced by commit `8bad683f` (P0-LIFECYCLE-CLOSURE-001). It is **ineligible** for corpus registration — `00-BOOK/tools/ukb.py::eligibility_universe()` contains no `engine/**/*.py` at all — so it is the disclosed condition in its ordinary form, not a new condition. The decisive test the rule attaches also holds: of the 85 unadmitted targets, **zero** could carry a constitutional identity.

The drift is not caused by the work being certified. Measured at clean `HEAD` with all Phase 4 changes stashed, the counts are byte-identical at 274 and 85.

Full evidence lineage: `UCL-GAP-CLOSURE-REPORT.md`.

Temporal note: anchored to `git HEAD = 03179308` under reference system `logical:git-commit-order@ucos-consolidation`. The `Date` row is a repository-local convenience, not an authority.

## Decision

Set `UCL-V-41.expect` to **274** and `UCL-V-42.expect` to **85** in `00-MASTER/UCL-000001/ucl-declaration.json`, appending the delta-by-identity evidence to each `detail` in the form the two prior moves (`92→98`, `98→217`) used, then re-derive the generated registers through the declared producer `ucl_engine.py`.

**There is no discretion in these values.** `UCL-V-41/42` fail when measured exceeds the bound, and `check-bounds-tight` (`ucl_engine.py:2894-2900`) fails when the bound exceeds the measured value. The only state satisfying both guards is `bound == measured`, exactly. Any value above 274 or 85 would immediately fail `check-bounds-tight`, which is precisely the guard that prevents inflating a bound to conceal a future regression.

We **decline** to bundle the corpus-registration drift into this decision. 192 eligible-but-unregistered documents exist (UGA reports 24 in its own universe as `UGA-INV-01`/`UGA-INV-10`), and the declaration's rationale sentence asserting that quantity is zero is no longer true. Recording that plainly is part of this decision; resolving it is not. It is a `CORPUS_REGISTRATION` mutation governed by `REG-AUTO-001 → 00-BOOK/tools/register.sh`, minting permanent, append-only, never-renumberable identities. It is recorded as `UCL-F-006` and referred to its owner.

## Consequences

Positive: the UCL gate returns to OPEN on evidence rather than on assertion, and the ratchet is once again exactly as tight as the repository permits, so the next genuinely new unadmitted corner is detected at +1. Neutral: no owner is amended, no authority is created, no relationship is lost or conflated — the disclosed condition is unchanged in kind and the generated registers are re-derived by their declared producer. Negative: the bound is looser in absolute terms than before, which is inherent to a ratchet over a growing corpus; `check-bounds-tight` bounds that looseness to zero slack. Reversible: the declaration edit is two integers and its evidence text, revertable by commit.

A second finding, `UCL-F-007`, is recorded: the committed generated reading had drifted 77 commits from its declaration, so a derived artifact was committed out of step with its source. UCL re-derivation should be bound into the routine gate sequence so that cannot recur.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
