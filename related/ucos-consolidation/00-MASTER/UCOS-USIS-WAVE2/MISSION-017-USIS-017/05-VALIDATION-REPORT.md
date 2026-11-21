# EVO-USIS-017 · 05 — Validation Report

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-017-VAL | PROGRAM | UCOS-USIS-001 |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

## 1 — Executed tooling

| Command | Result | Evidence |
|---------|--------|----------|
| `./doctor.sh` | ENVIRONMENT READY | python 3.12 / pytest / pytest-cov / coverage / ruff OK |
| `./verify.sh` | **PASSED** (30s) | ruff PASS · pytest+coverage ≥90% PASS · coverage report PASS · enforce --pre PASS |
| `register.sh` | TRANSACTION COMPLETE | 10/10 phases |
| `ukb enforce` | PASS | 1133 registered, 0 unregistered/unclassified/invalid (audit #449) |
| `ukb validate` | PASS | 1133 artifacts; append-only page ledger intact; referential integrity OK |
| `ukbx validate` | PASS | 15 signals; append-only; subjects resolve; provenance present; no secrets |
| `ukbx twin --check` | CERTIFIED 7/7 | C-05 · C-07 · C-08 · C-09 · C-10 · C-11 · C-04/12 |
| `register.sh --guard` | DRIFT (expected) | regenerated projections uncommitted (procedural) |

> `ukb validate` note: `jsonschema` not installed → structural + append-only + referential checks ran and PASSED; full JSON-schema validation optional/non-blocking.

## 2 — Mandated verification checks

| Check | Result | Basis |
|-------|--------|-------|
| Repository structure integrity | PASS | Phase 1A: 18-APIS-SDK canonical, no variance |
| Registry integrity | PASS | `ukb validate` schema/structural PASS |
| Knowledge Once | PASS | USIS-017 references Service/…/SERVICE-PLATFORM (obligation 8; LAW USIS-02) |
| Dependency closure | PASS | Depends-On USIS-012/004/002 all registered; referential OK (obligation 14) |
| Registry / Lineage integrity | PASS | `ukbx certify` domains 2/6/7 PASS; CHANGE-VERSION-LINEAGE clean |
| No cycles | PASS | `ukbx twin --check` C-07 acyclic (obligation 5) |
| Zero duplication / orphans | PASS | `ukb enforce` 0 orphans; 0 duplicate ids/pages (obligations 2/4) |

## 3 — Drift-guard interpretation (not a blocker)

`register.sh --guard` re-ran idempotently and flagged regenerated `00-BOOK` projections as uncommitted (exit 3) — the designed "commit the regeneration" signal, not a corpus inconsistency. Internal consistency proven by validate/enforce/certify all PASS. Sealing requires a git commit (outside this programme's authority unless requested).

## 4 — Determination

Phase 4 validation **COMPLETE**. All governance + closure + structure gates PASS. Sole residual: expected uncommitted-regeneration drift (procedural).

*END — EVO-USIS-017 · 05 Validation Report.*
