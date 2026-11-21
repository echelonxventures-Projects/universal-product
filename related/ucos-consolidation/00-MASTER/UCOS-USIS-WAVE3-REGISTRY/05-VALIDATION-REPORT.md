# EVO-USIS-W3-REGISTRY-001 · 05 — Validation Report

| Field | Value |
|-------|-------|
| PROGRAMME | EVO-USIS-W3-REGISTRY-001 (S-02) |
| PHASE | 5–9 — Validation (fail-closed order, USIS-014 Part I) |
| RESULT | PASS — all validation gates green; verdict VALID |

## Gate results (Repository Truth — command verdicts)

| # | Gate | Mechanism | Verdict |
|---|------|-----------|---------|
| V-2 | pre-registration eligibility / classification | `ukb enforce --pre` (bracketed in `register.sh`) | PASS — USIS-021 eligible, classified USIS/VOL-024 |
| V-3 | structural + append-only + referential | `ukb validate` | **PASSED** — 1181 artifacts, append-only page ledger intact, referential integrity OK |
| V-4 | twin signal / provenance / secret-free | `ukbx validate` | **PASSED** — 15 signals, every subject resolves, provenance present, no embedded secrets |
| V-5 | twin hard checks | `ukbx twin --check` | **CERTIFIED** — hard checks 7/7 |
| V-12 | post-registration parity | `ukb enforce` | **PASSED** — registered 1181/1181; unregistered 0; unclassified 0; invalid 0 |
| V-14 | determinism (double-run byte stability) | second `register.sh` + count check | PASS — no re-allocation; USIS-021 stable |

> `jsonschema` not installed → `ukb validate` ran structural checks only (advisory, per S-01 G-13 non-blocking disposition). All structural, append-only, and referential checks passed.

## Obligation-set evaluation (USIS-014 Part F — applicable to a Master Registry)

| Obligation class | Evaluation | Result |
|------------------|-----------|--------|
| Existence & registration | USIS-021 on disk + in all registers | ✓ |
| Single-owner / no-duplicate | exactly one whole-corpus Master Registry; one owner (USIS) | ✓ |
| No-Orphan (GOV-001-T3) | every Depends-On resolves; 0 dangling edges; catalog member rows = 0 ⇒ 0 orphan rows | ✓ |
| Acyclic dependency (C-07) | Depends-On downward to USIS-GOV-000; graph acyclic (`ukbx twin` C-07 PASS) | ✓ |
| Referential integrity | `ukb validate` referential OK; all 44 edges resolve | ✓ |
| Append-only (LAW USIS-09) | contiguous ID/page append; no renumber | ✓ |
| Non-duplication (LAW USIS-02) | no parallel allocator/certifier/registry (PART H self-check) | ✓ |

## Constitutional invariant self-check (USIS-021 PART I)

All 9 fail-closed invariants evaluate to **0** (parallel allocator 0, duplicate registry 0, member rows 0, orphan rows 0, closed surface 0, governance determination 0, frozen/config edits 0, circular dependency 0, Earth/tech/vendor assumption 0).

## Determination

**PHASE 5–9 PASS.** Verdict **VALID** — no partial validity. Structural, twin, parity, and determinism gates all green; every obligation discharged; no lower-tier defect short-circuited the evaluation.
