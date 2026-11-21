# ADR-0018: Authorize REG-AUTO-001 to mint identities for this session's own new objects

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UGA-001 (UCOS-UGA-001), REG-AUTO-001, CEP-002 Article 28 |
| Supersedes | none — a follow-on to `ADR-0017`, not a replacement |

## Context

`ADR-0017` authorized minting for exactly 24 named objects and explicitly declined to authorize a standing blanket mint: *"A future anonymous object requires its own decision under this same Article, not a standing blanket authorization."* After executing that mint (`WP-UCDA-026`), the gate passed with 0 anonymous objects — but `engine/tests/unit/test_verification_intelligence.py::test_the_shards_collect_exactly_the_tests_the_whole_suite_collects` still failed, now reporting only 13 missing tests (down from 87), all inside `engine/tests/knowledge/ukip/test_confidence.py`.

**Root cause, traced directly.** `00-MASTER/UCOS-UGA-001/uga_engine.py:175` discovers objects via `git ls-files -z --cached` — the git *index*, not the working tree. `engine/knowledge/ukip/confidence.py` and `engine/tests/knowledge/ukip/test_confidence.py` (both authored this session, Task 3, `DEC-ADR-0016`) were never `git add`ed, so they were invisible to UGA-001's discovery entirely — neither counted as anonymous nor minted by `ADR-0017`'s run, which is why the prior gate run showed 0 violations while these two files still had no identity. This was verified directly: `git add`ing the two files (staging only, no commit) makes them appear in `uga_engine.build(mint=False)["anonymous"]` — exactly these two, nothing else.

**Affected objects — 2, enumerated directly:**

| Path | Object class (minted category) |
|---|---|
| `engine/knowledge/ukip/confidence.py` | `EXECUTABLE_OBJECT` (`ENGINE`) |
| `engine/tests/knowledge/ukip/test_confidence.py` | `TEST_OBJECT` (`TESTOBJ`) |

**Owner.** `REG-AUTO-001`, same mechanism as `ADR-0017` (`uga_engine.py run`, shared `category_seq`).

**Irreversible impact.** Identical in kind to `ADR-0017`: not irreversible pre-commit (`git restore`/`git reset` fully undoes both the staging and the ledger mutation); permanent by the ledger's own append-only design once committed. No new risk category is introduced — this is the same action over a smaller, simpler, session-own population with no relationship to the deferred 192-document corpus-registration population.

**Evidence.** Direct execution, this session: pre-staging anonymous count included these 2 paths as soon as `git add` made them visible; `git status --short` confirms no other file changed state as a side effect of staging.

**Temporal context.** Anchored to `git HEAD = 03179308`, same reference system as `ADR-0017`.

**Location/reality context.** Not applicable, same reasoning as `ADR-0017`.

**Authorization.** Continuation of the same explicit "ABSOLUTE UNIVERSAL EXPANSION CLOSURE DIRECTIVE" that authorized `ADR-0017`; scoped narrowly to these 2 objects only, per that decision's own stated limit.

## Decision

We **authorize** `REG-AUTO-001` to execute `00-MASTER/UCOS-UGA-001/uga_engine.py run` once more, minting identities for exactly the 2 objects named above (already staged into the git index, not committed).

## Consequences

Positive: the shard-collection completeness test's remaining 13-test gap closes; the anonymous-object count returns to 0 including this session's own deliverables.

Neutral: no existing identity touched; the 24 objects `ADR-0017` minted are unaffected.

Reversible (pre-commit): `git reset engine/knowledge/ukip/confidence.py engine/tests/knowledge/ukip/test_confidence.py && git restore 00-BOOK/DATA/id-ledger.json 00-MASTER/UCOS-UGA-001/` fully undoes both the staging and this decision's execution.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05) — `adr/0017-ucl-f-006-identity-minting-authorization.md`, `engine/knowledge/ukip/confidence.py`, `engine/tests/knowledge/ukip/test_confidence.py`.
- [x] No secret material embedded (SEC-04).
