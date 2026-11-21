# ADR-0024: UCDA decision mutations become hash-chained and append-only

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `adr/0019-residual-phase4-finding-disposition.md` (`WP-UCDA-028`), `P4-F-005` |
| Supersedes | none — discharges another of `WP-UCDA-028`'s six independent sub-obligations |

## Context

`P4-F-005` (owner `UCDA-000001`): `ucda_engine.py` is explicitly a pure reader (*"AUTHORITY = NONE (DERIVED TRUTH)... reads a single DATA declaration"*) — it never writes `ucda-decisions.json`. Every mutation to that file, including this session's own `DEC-ADR-0017`/`0018` stage/disposition edits, was raw external JSON overwriting with no transition validation and no record of the prior state. Only git commit history could recover a decision's earlier state, and only if it had actually been committed — which none of this session's edits had been at the time this gap was investigated.

Prior discovery (this session) found two candidate approaches and did not choose between them: (a) a hash-chained history ledger modeled on `engine/context/registry.py`'s `ContextRegistry.AuditEntry`, or (b) a git-commit-discipline policy. This decision chooses (a): a policy has no tamper evidence and depends on discipline being followed, which is exactly the kind of unenforced assumption this session has repeatedly found and corrected.

## Decision

We **implement** `record_decision_update(doc, decision_id, updates) -> dict` and `verify_decision_history(doc) -> list[str]` in `ucda_engine.py`, directly reusing `ContextRegistry`'s `AuditEntry` shape (`sequence`, chained `previous_hash`/`entry_hash`, computed via the engine's own existing `digest()` function — no new hashing scheme). `record_decision_update` **computes** a new document (before/after snapshot hashes, an appended chain entry, the decision's fields updated) — it does not write to disk. Persisting the result remains the caller's responsibility, exactly as every decision this session registered — the defect was the *absence of an audited computation*, not the location of the write.

A new self-check, `--check-decision-history`, is added to the existing `SELF_CHECKS` dispatch table (the same mechanism `--check-declaration`/`--check-no-enumeration`/`--check-determinism` already use) — no new CLI subsystem, one more entry in an existing one.

We explicitly **preserve** `ucda_engine.py`'s stated authority model: it still legislates nothing, still contains no hardcoded decision/stage/disposition literal (unaffected — the new functions operate generically on whatever `doc` is passed), and still never writes `ucda-decisions.json` itself.

We **refuse** to build a second decision-mutation authority, a second registry, or a policy substitute — this is the one, sole path for auditable decision mutation going forward, reusing `ContextRegistry`'s proven shape rather than inventing a new one.

## Consequences

Positive: a decision's mutation history is now hash-chained and tamper-evident (verified: corrupting one entry's hash breaks both its own verification and the next entry's link check). Every mutation going forward that uses this function — including this decision's own registration, below — is self-documenting.

Neutral: `ucda-decisions.json` gains an additive `decision_history` top-level key; `check_declaration()` was confirmed (by direct dry run against the real file) not to reject it — 0 findings on a document carrying the new key.

Negative: decisions registered before this fix (`DEC-ADR-0015` through `DEC-ADR-0023`) have no retroactive history — only their current state is known, exactly as before. This is disclosed, not hidden: backfilling a fabricated "before" state for those would misrepresent history that was never actually captured.

Reversible: the two new functions are additive library code; `ucda_engine.py`'s existing read-only behavior (report/gate/other self-checks) is completely unchanged if they are never called.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — `ucda_engine.py` remains `AUTHORITY = NONE`; no new authority created.
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `adr/0019`, `00-MASTER/UCDA-000001/ucda_engine.py`.
- [x] No secret material embedded (SEC-04).

## Validation evidence

- Dry run against the real, live `ucda-decisions.json`: `record_decision_update()` produces a document that passes `check_declaration()` with 0 findings.
- Multi-update chaining verified: two sequential updates to the same decision produce `sequence=[1,2]` with a correctly linked `previous_hash`/`entry_hash` chain; `verify_decision_history()` reports 0 findings.
- Tamper detection verified: corrupting one chain entry's `entry_hash` is caught by `verify_decision_history()`, which also correctly reports the *next* entry's link as broken (not just the tampered entry itself).
- `--check-decision-history` CLI self-check runs and reports `PASS` against the real file.
- This decision's own registration (below) is the first live, non-dry-run use of the mechanism.
