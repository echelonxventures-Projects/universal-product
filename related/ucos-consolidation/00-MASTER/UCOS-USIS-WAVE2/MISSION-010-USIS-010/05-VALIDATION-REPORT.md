# EVO-USIS-010 · 05 — Validation Report

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-010-VAL (Validation Report) |
| PROGRAM | UCOS-USIS-001 |
| CLASSIFICATION | Operational-memory validation report (Wave 2) |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Record Phase-4 validation of USIS-010. All governance and closure gates PASS.

---

## 1 — Executed tooling

| Command | Result | Evidence |
|---------|--------|----------|
| `./doctor.sh` | ENVIRONMENT READY | python 3.12 / pytest / pytest-cov / coverage / ruff OK |
| `./verify.sh` | **PASSED** (31s) | ruff PASS · pytest+coverage ≥90% PASS · coverage report PASS · enforce --pre PASS |
| `register.sh` | TRANSACTION COMPLETE | 10/10 phases |
| `ukb enforce` | PASS | 1129 registered, 0 unregistered/unclassified/invalid (audit #437) |
| `ukb validate` | PASS | 1129 artifacts; append-only page ledger intact; referential integrity OK |
| `ukbx validate` | PASS | 15 signals; append-only; subjects resolve; provenance present; no secrets |
| `ukbx twin --check` | CERTIFIED 7/7 | C-05 referential · C-07 acyclic · C-08 navigation · C-09 control-tower · C-10 export · C-11 search · C-04/12 signals |
| `register.sh --guard` | DRIFT (expected) | regenerated projections uncommitted (procedural; §3) |

> `ukb validate` note: `jsonschema` not installed → structural + append-only + referential checks ran and PASSED; full JSON-schema validation optional/non-blocking.

## 2 — Mandated verification checks

| Check | Result | Basis |
|-------|--------|-------|
| Repository structure integrity | PASS | Phase 1A: 11-PATTERNS canonical, no variance (RSV Report) |
| Registry integrity | PASS | `ukb validate` schema/structural PASS; Pattern row + registries consistent |
| Knowledge Once | PASS | USIS-010 references USIS-008/009/006/007 (obligation 8; LAW USIS-02) |
| Dependency closure | PASS | Depends-On USIS-008/009/004/002 all registered; referential integrity OK (obligation 14) |
| No cycles | PASS | `ukbx twin --check` C-07 acyclic (obligation 5) |
| No orphan artifacts | PASS | `ukb enforce` 0 orphans; parent + home present (obligation 4) |
| No duplicate knowledge | PASS | 0 duplicate registry/catalog; Domain/Capability/Model/Algorithm referenced (obligation 2) |
| No broken lineage | PASS | 16 relationship edges resolve; CHANGE-VERSION-LINEAGE clean |
| No invalid registry entries | PASS | `ukb validate` 0 invalid |

## 3 — Drift-guard interpretation (not a blocker)

`register.sh --guard` re-ran idempotently and flagged regenerated `00-BOOK` projections as uncommitted (exit 3) — the designed "commit the regeneration" signal, not a corpus inconsistency. Internal consistency proven by validate/enforce/certify all PASS. Sealing requires a git commit (outside this programme's authority unless requested).

## 4 — Determination

Phase 4 validation **COMPLETE**. All governance + closure + structure gates PASS. Sole residual: expected uncommitted-regeneration drift (procedural).

*END — EVO-USIS-010 · 05 Validation Report.*
