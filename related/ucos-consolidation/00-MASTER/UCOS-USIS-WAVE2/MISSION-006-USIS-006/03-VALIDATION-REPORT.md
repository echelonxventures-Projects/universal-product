# EVO-USIS-006 · 03 — Validation Report

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-006-VAL (Validation Report) |
| PROGRAM | UCOS-USIS-001 |
| CLASSIFICATION | Operational-memory validation report (Wave 2) |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Record Phase-4 validation of USIS-006. All governance and closure gates PASS.

---

## 1 — Executed tooling

| Command | Result | Evidence |
|---------|--------|----------|
| `./doctor.sh` | ENVIRONMENT READY | python 3.12 / pytest / pytest-cov / coverage / ruff OK |
| `./verify.sh` | **PASSED** (30s) | ruff PASS · pytest+coverage ≥90% PASS · coverage report PASS · enforce --pre PASS |
| `register.sh` | TRANSACTION COMPLETE | 10/10 phases |
| `ukb enforce` | PASS | 1126 registered, 0 unregistered/unclassified/invalid (audit #428) |
| `ukb validate` | PASS | 1126 artifacts; append-only page ledger intact; referential integrity OK |
| `ukbx validate` | PASS | 15 signals; append-only; subjects resolve; provenance present; no secrets |
| `ukbx twin --check` | CERTIFIED 7/7 | C-05 referential · C-07 acyclic · C-08 navigation · C-09 control-tower · C-10 export · C-11 search (172 hits) · C-04/12 signals |
| `register.sh --guard` | DRIFT (expected) | regenerated projections uncommitted (procedural; §3) |

> `ukb validate` note: `jsonschema` not installed → structural + append-only + referential checks ran and PASSED; full JSON-schema validation optional/non-blocking.

## 2 — Mandated verification checks

| Check | Result | Basis |
|-------|--------|-------|
| Knowledge Once | PASS | 1 home per concept; USIS-006 references USIS-007/004/005 (obligation 8; LAW USIS-02) |
| Dependency closure | PASS | Depends-On USIS-007/004/005/002/003 all registered; referential integrity OK (obligation 14) |
| No cycles | PASS | `ukbx twin --check` C-07 acyclic; CIOA downward-only (obligation 5) |
| No orphan references | PASS | `ukb enforce` 0 orphans; parent + home present; C-05 endpoints resolve (obligation 4) |
| No duplicate knowledge | PASS | 0 duplicate registry/catalog; Domain Architecture referenced not duplicated (obligation 2) |
| No invalid registry entries | PASS | `ukb validate` schema/structural PASS; 0 invalid |
| No broken lineage | PASS | 18 relationship edges resolve; CHANGE-VERSION-LINEAGE registry regenerated clean |
| Coverage completeness | PASS | see Coverage Closure Certificate (05) — 13/13 dimensions 100% |

## 3 — Drift-guard interpretation (not a blocker)

`register.sh --guard` re-ran the transaction idempotently and flagged the regenerated `00-BOOK/DATA|REGISTRIES|CONTROL-TOWER|PORTAL` as uncommitted (exit 3) — the designed "commit the regeneration" signal, not a corpus inconsistency. Internal consistency proven by `ukb validate`/`enforce`/`ukbx certify` all PASS. Sealing requires a git commit (outside this programme's mutation authority unless requested).

## 4 — Determination

Phase 4 validation is **COMPLETE**. All governance + closure gates PASS. Sole residual: expected uncommitted-regeneration drift (procedural).

*END — EVO-USIS-006 · 03 Validation Report.*
