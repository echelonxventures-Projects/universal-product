# ADR-0017: Authorize REG-AUTO-001 to mint identities closing UCL-F-006

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ (explicit directive: "ABSOLUTE UNIVERSAL EXPANSION CLOSURE DIRECTIVE", Phase 2) |
| Technology Constitution refs | UCL-000001, UGA-001 (UCOS-UGA-001), REG-AUTO-001, CEP-002 Article 28 |
| Supersedes | none — this decision reverses the disposition of `UCL-F-006`, it does not supersede the finding record itself |

## Context

`UCL-F-006` was discovered during `PHASE-4`/`ADR-0014` work (pre-dating this session) and deliberately deferred: *"resolving it is a `CORPUS_REGISTRATION` mutation... minting permanent, append-only, never-renumberable identities... out of scope for a bound re-tightening and must not be bundled into it."* Tasks 2-5 of this session re-confirmed the finding independently — `VERIFICATION-INTELLIGENCE-CLOSURE-REPORT.md` and `FINAL-UNIVERSAL-INFINITE-EXPANSION-FOUNDATION-CERTIFICATION-REPORT.md` both traced three test failures (`UGA-INV-01`, `UGA-INV-10`, and the shard-collection completeness check) to this one root cause and, on direct question, the deciding authority chose to leave it referred rather than mint (recorded in this session's transcript). This decision **reverses that choice** under the explicit follow-up directive "ABSOLUTE UNIVERSAL EXPANSION CLOSURE DIRECTIVE, PHASE 2 — UCL-F-006 ABSOLUTE CLOSURE," which names the exact steps required before execution and instructs them performed.

**Why minting is required.** `00-BOOK/DATA/id-ledger.json` carries 1264 registered document paths (`by_path`) and 4888 registered non-document objects (`by_object`) at this checkpoint. Twenty-four version-controlled objects exist in neither map — confirmed by direct enumeration (`uga_engine.build(mint=False)["anonymous"]`, this session), not by document claim. `UGA-INV-01` (`EVERY_OBJECT_HAS_UNIVERSAL_ID`) and `UGA-INV-10` (`EVERY_MUTATION_HAS_AUDIT_EVENT`, which cannot hold for an object with no identity to audit against) both fail on exactly this set, and `engine.verification_intelligence.registry.load_substrates()` depends on the same derived surfaces these 24 objects are missing from, which is the second-order cause of the shard-collection completeness failure. No path other than minting closes any of the three.

**Affected objects — all 24, enumerated by direct execution, not estimated:**

| Object class (minted category) | Count | Paths |
|---|---|---|
| `EXECUTABLE_OBJECT` (`ENGINE`) | 2 | `engine/lineage/memory.py`, `platform/repository_intelligence/mutation_classification.py` |
| `TEST_OBJECT` (`TESTOBJ`) | 4 | `engine/tests/expansion/test_platform_composition_verification.py`, `engine/tests/expansion/test_universal_expansion_verification.py`, `engine/tests/expansion/test_universal_memory_verification.py`, `platform/tests/test_mutation_classification.py` |
| `DATA_OBJECT` (`DATAOBJ`) | 3 | `00-MASTER/UCOS-CEU-001/ceu-declaration.json`, `00-MASTER/UCXI-000001/ucxi-declaration.json`, `engine/lineage/memory-layers.json` |
| `EXCLUDED_DOCUMENT` (`EXDOC`) | 15 | `PHASE-4-CAPABILITY-GAP-MATRIX.md`, `PHASE-4-RESUMPTION-STATE-REPORT.md`, `PHASE-4-VALIDATION-AND-CERTIFICATION-EVIDENCE.md`, `REPOSITORY-IDENTITY-ALLOCATION-OWNER-DECISION-RECORD.md`, `adr/0003`…`adr/0013` (eleven files, `0003` through `0013` inclusive) |

Traced through `classify_object()`/`epoch1_identity()` (`00-MASTER/UCOS-UGA-001/uga_engine.py:187-309`) directly: none of the 24 carry `object_class == DOCUMENT_ARTIFACT` (the class UGA-001 refuses to mint for, deferring instead to `UMB-IMP-001`), so all 24 are within UGA-001's own minting authority — no second identity authority is invoked, and REG-AUTO-001/UGA-001 remains the sole owner (`CAA-INV-04`, 0 violations at last measurement).

**Owner.** `REG-AUTO-001`, operating through `00-MASTER/UCOS-UGA-001/uga_engine.py run`, using the corpus's own shared `category_seq` counter (`00-BOOK/DATA/id-ledger.json`) — the same construction `EXEC-REG-001` already established, not a new one.

**Irreversible impact — stated precisely, not overstated.** Two distinct senses of "irreversible" apply and must not be conflated:
1. *Within this working tree, before any commit*: **not irreversible**. `uga_engine.py run` only mutates `00-BOOK/DATA/id-ledger.json` (append new `by_object` entries) and regenerates derived surfaces under `00-MASTER/UCOS-UGA-001/`; nothing outside the working tree is touched, no network or clock is read, and `git restore`/`git diff` can inspect or revert every byte before any commit is made.
2. *As a design property of the identity authority itself*: genuinely permanent by construction — `epoch1_identity`'s own comment states *"an existing entry is returned untouched, so an identity is permanent and is never reissued to a different path"* — once minted (and, practically, once committed), an id in `by_object` is never reused for a different object even if this one is later retired. This is the property `UCL-F-006` named as the reason to defer, and it is real: the correct response is deliberateness before minting, which this decision provides, not indefinite deferral.

**Evidence.** `uga_engine.build(mint=False)` executed this session enumerates the 24 objects exactly as listed above (reproducible: re-running the same command against an unchanged tree returns byte-identical output — `epoch1_identity` reads no clock and the mint step is the only state-changing operation). `UCL-GAP-CLOSURE-REPORT.md` and `adr/0014-retighten-the-ucl-unadmitted-target-ratchet.md` are the located, prior findings this decision closes.

**Temporal context.** Anchored to `git HEAD = 03179308` under reference system `logical:git-commit-order@ucos-consolidation`. No wall-clock value is asserted as authoritative; `epoch1_identity`'s `first_seen` field is the engine's own local convenience timestamp, not a governed temporal claim, consistent with `engine/temporal/coordinate.py`'s refusal to read a clock.

**Location/reality context.** Not applicable — this decision concerns repository-object identity allocation, not a spatial, physical, or `ContextKind.REALITY` subject.

**Authorization.** This decision is authorized by the explicit, direct instruction "ABSOLUTE UNIVERSAL EXPANSION CLOSURE DIRECTIVE," Phase 2, issued after this session's prior turn had already disclosed the exact irreversibility characteristics above and the deciding authority had, on that full disclosure, chosen to proceed. No authorization is assumed beyond the 24 objects named in this decision; a future anonymous object requires its own decision under this same Article, not a standing blanket authorization.

## Decision

We **authorize** `REG-AUTO-001` to execute `00-MASTER/UCOS-UGA-001/uga_engine.py run` once, minting universal identities for exactly the 24 objects enumerated above, and to persist the resulting `00-BOOK/DATA/id-ledger.json` and regenerated `00-MASTER/UCOS-UGA-001/` derived surfaces.

We do **not** authorize minting for the separate 192-document `CORPUS_REGISTRATION` drift the same finding's evidence trail names (`UCL-F-006`'s wider context, `00-BOOK/tools/register.sh (ukb.py build --mint)`) — that is a different registration authority (`UMB-IMP-001`, corpus documents) over a different, larger, unenumerated population, and remains **out of scope** for this decision exactly as `ADR-0014` originally scoped it out. Bundling it in now would repeat the error this decision exists to correct for its own, narrower population: minting without enumerating exactly what is minted and why.

## Consequences

Positive: `UGA-INV-01`/`UGA-INV-10` close for this population; the shard-collection completeness test's second-order dependency on these derived surfaces closes; three previously-referred test failures resolve to a verified state rather than a disclosed residual.

Neutral: no existing identity is touched, reissued, or renumbered — `epoch1_identity` only appends.

Negative: the 24 identities minted here are permanent by the ledger's own design, so a future decision to reorganize or rename any of these 24 paths must account for a stable id that will not itself be renumbered.

Reversible (pre-commit only): until this working tree is committed, `git restore 00-BOOK/DATA/id-ledger.json 00-MASTER/UCOS-UGA-001/` fully undoes this decision's execution.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no second identity authority created; `UGA-INV-04`'s single-authority invariant is unaffected by construction.
- [x] Rollback / migration path recorded (CC-04) — see Consequences; pre-commit `git restore` is exact and complete.
- [x] Traceability links to affected artifacts recorded (CC-05) — `UCL-GAP-CLOSURE-REPORT.md`, `adr/0014-retighten-the-ucl-unadmitted-target-ratchet.md`, `VERIFICATION-INTELLIGENCE-CLOSURE-REPORT.md`, `FINAL-UNIVERSAL-INFINITE-EXPANSION-FOUNDATION-CERTIFICATION-REPORT.md`, `00-MASTER/UCOS-UGA-001/uga_engine.py`.
- [x] No secret material embedded (SEC-04).
