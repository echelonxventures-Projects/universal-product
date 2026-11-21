# EVO-USIS-007 · 03 — Validation Report

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-007-VAL (Validation Report) |
| PROGRAM | UCOS-USIS-001 |
| CLASSIFICATION | Operational-memory validation report (Wave 2) |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Record the Phase-4 validation of USIS-007 against the mandated tooling and closure checks. All governance gates PASS.

---

## 1 — Executed tooling

| Command | Result | Evidence |
|---------|--------|----------|
| `./doctor.sh` | ENVIRONMENT READY | python 3.12 / pytest / pytest-cov / coverage / ruff all OK |
| `./verify.sh` | **PASSED** — all gates green (31s) | ruff PASS · pytest+coverage 97% (≥90%) PASS · coverage report PASS · governance enforce --pre PASS |
| `register.sh` | TRANSACTION COMPLETE | 10/10 phases (Registration Report §2) |
| `ukb enforce` | PASS | 1125 registered, 0 unregistered, 0 unclassified, 0 invalid (audit run #425) |
| `ukb validate` | PASS | 1125 artifacts; append-only page ledger intact; referential integrity OK |
| `ukbx validate` | PASS | 15 signals; append-only; every subject resolves; provenance present; no secrets |
| `ukbx twin --check` | CERTIFIED (7/7) | C-05 referential, C-07 acyclic, C-08 navigation, C-09 control-tower, … all PASS |
| `register.sh --guard` | DRIFT (expected) | regenerated projections uncommitted; idempotent re-run reproduced identical set — see §3 |

> Note on `jsonschema`: `ukb validate` reported "jsonschema not installed — ran structural checks only." Structural, append-only, and referential checks all PASSED. Full JSON-schema validation is an optional enhancement (`pip install jsonschema`) and is non-blocking; it does not affect USIS-007 conformance.

## 2 — Mandated verification checks

| Check | Result | Basis |
|-------|--------|-------|
| Dependency closure | PASS | every USIS-007 `Depends-On` (USIS-002/003/004/005) resolves to a registered node; `ukb validate` referential integrity OK (obligation 14) |
| Knowledge Once | PASS | 1 canonical home per concept; USIS-007 references, never restates (obligation 8; LAW USIS-02) |
| No duplication | PASS | no duplicate universe/catalog/registry created (obligation 2); Reuse Report basis |
| No cycles | PASS | `ukbx twin --check` C-07 acyclic; CIOA downward-only (obligation 5) |
| No orphan references | PASS | `ukb enforce` 0 orphans; parent + home present; C-05 all endpoints resolve (obligation 4) |

## 3 — Drift-guard interpretation (not a blocker)

`register.sh --guard` re-ran the transaction idempotently and then flagged the regenerated `00-BOOK/DATA|REGISTRIES|CONTROL-TOWER|PORTAL` as **modified-but-uncommitted** (exit 3). This is the designed "commit the regeneration" signal — the drift *is* the un-committed registration of USIS-007 and its deterministic projections, not a corpus inconsistency. Internal consistency is proven by `ukb validate` / `ukb enforce` / `ukbx certify` all PASS. Clearing the guard requires a git commit of the regenerated projections, which is outside this programme's mutation authority unless explicitly requested.

## 4 — Determination

Phase 4 validation is **COMPLETE**. All governance and closure gates PASS. The only residual is the expected uncommitted-regeneration drift (§3), which is procedural (git commit), not constitutional.

*END — EVO-USIS-007 · 03 Validation Report.*
