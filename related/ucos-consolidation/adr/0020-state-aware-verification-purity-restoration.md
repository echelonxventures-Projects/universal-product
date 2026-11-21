# ADR-0020: The verification-purity restoration fixture must be state-aware, not a blind checkout

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ (directive: "Continue with evidence-first recovery and stabilization", Phase 2) |
| Technology Constitution refs | `GOVERNED-EVOLUTION-STATE-DETERMINATION.md`, `platform/tests/test_verification_purity.py` |
| Supersedes | none |

## Context

`platform/tests/test_verification_purity.py` exists to guarantee the verification plane (`./verify.sh`'s observing stages) never mutates governed state — a real, previously-caught defect (documented in its own module docstring: a verification run once minted 140 permanent identities and emitted ~140 pages because a mutating transaction was invoked from a read-only path). Its `_restore_derived_views` fixture (`:195-209`) exists to revert *incidental derived-view regeneration* that an observing command may legitimately produce as a side effect of "regenerate then compare" tools, so that regeneration drift does not leak out of the module as working-tree noise.

**The defect, found this session by direct execution, not documentation:** the fixture's implementation is
```python
subprocess.run(["git", "checkout", "--", "00-BOOK/DATA/", "00-BOOK/REGISTRIES/", "00-BOOK/CONTROL-TOWER/"], ...)
```
run unconditionally in teardown, for every test in the module. This does not distinguish "drift this test caused" from "legitimate uncommitted state that already existed before this test ran." Running the full suite this session reverted `00-BOOK/DATA/id-ledger.json` and `00-BOOK/DATA/canonical-observation-audit.json` — both real, intentional, governed mutations from `DEC-ADR-0017`/`DEC-ADR-0018` (identity minting, itself separately authorized and executed) — back to their committed `HEAD` state, silently, with no test failure to signal it (the fixture's own purpose is to make drift invisible, so it succeeded at hiding exactly the state it should have distinguished from noise).

This is confirmed the sole cause: `git diff --stat 00-BOOK/DATA/id-ledger.json` returned empty (byte-identical to `HEAD`) immediately after a full-suite run, despite `uga_engine.py run` having been executed and independently verified earlier in the same session. No other file outside `00-BOOK/DATA/`, `00-BOOK/REGISTRIES/`, `00-BOOK/CONTROL-TOWER/` was affected, and nothing under `00-BOOK/REGISTRIES/`/`00-BOOK/CONTROL-TOWER/` was dirty at any point this session, so only `00-BOOK/DATA/` files were actually at risk in practice.

## Decision

We **authorize** replacing `_restore_derived_views`'s blind `git checkout --` with a state-aware restoration that:

1. **Snapshots exactly the dirty set** under the three guarded roots at fixture *setup* (before the test runs) — both the path set (`git status --porcelain`) and, for each already-dirty path, its exact byte content.
2. **After the test runs**, computes the dirty set again and classifies every path into exactly one of three cases:
   - **Newly dirty** (clean before, dirty after) — purely caused by this test. Restored to `HEAD` via a scoped `git checkout -- <path>` (tracked) or removed (new untracked file), exactly as the current fixture already does, but now scoped to only the paths actually responsible.
   - **Already dirty, unchanged by the test** — left untouched.
   - **Already dirty before, and further changed by the test** — restored to its **pre-test** byte content (a direct file write of the snapshotted bytes), never to `HEAD`, so legitimate prior uncommitted work is preserved exactly as it stood before this test ran.
3. Never issues an unscoped `git checkout` over an entire directory again.

This satisfies every requirement of this decision's authorizing directive: tests may still clean their own mutations (case 1 and case 3 both revert what the test itself did); tests never blindly checkout canonical governance/data paths (restoration is always scoped to specific paths, computed from an actual diff, never a directory-wide command); restoration is state-aware (the three-way classification is exactly what "state-aware" requires); and existing evidence survives full-suite execution (case 2 and the corrected case 3 both guarantee pre-existing dirty state is never discarded).

We do **not** authorize removing the fixture's underlying guarantee (that derived-view drift a test causes does not leak out of the module) — only correcting its blast radius.

## Consequences

Positive: `DEC-ADR-0017`/`DEC-ADR-0018`'s identity-minting evidence — and any other legitimate future uncommitted governance work under the three guarded roots — survives a full test-suite run. The purity guarantee this module exists for is preserved, now correctly scoped.

Neutral: the fixture becomes more complex (three-way classification vs. one blind command) in exchange for correctness; this is the same tradeoff `ucos_ruff_gate` already made when it moved from directory-wide `ruff <dir>` to an explicit tracked-file list for an analogous reason (documented in `scripts/ucos-env.sh:294-345`).

Negative: none identified. The new logic is strictly narrower than the old one (it reverts a subset of what the old command reverted — the difference is exactly the previously-mishandled already-dirty case), so no test that passed under the old (buggy) behavior can newly fail under the corrected one for files that were clean before the test — the two behaviors are identical for the clean-before case, which is the case every one of this module's own tests actually exercises (they regenerate derived views from a starting-clean state in CI; the bug only manifests when *other*, legitimate work is already dirty in the same paths, which this session's own Phase 2/3 work is the first documented instance of).

Reversible: the new fixture logic is pure Python plus scoped git/filesystem calls; reverting this decision means restoring the single `git checkout --` line.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — the purity guarantee `test_verification_purity.py` exists to enforce is preserved, not weakened.
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `platform/tests/test_verification_purity.py`, `GOVERNED-EVOLUTION-STATE-DETERMINATION.md`, `adr/0017-ucl-f-006-identity-minting-authorization.md`, `adr/0018-ucl-f-006-follow-on-identity-minting-authorization.md`.
- [x] No secret material embedded (SEC-04).
