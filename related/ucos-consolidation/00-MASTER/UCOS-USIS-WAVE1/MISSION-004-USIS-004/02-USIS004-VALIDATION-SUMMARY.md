# 02 — USIS-004 VALIDATION SUMMARY (independent re-run)

All gates re-executed this session against the working tree carrying the
uncommitted USIS-004 registration. Scope: **1005** artifacts.

---

## 1 — Gate ledger

| # | Gate | Result | Key evidence |
|---|---|:--:|---|
| 1 | `register.sh` (10-phase transaction) | **TRANSACTION COMPLETE** | all phases sealed; exit 0 |
| 2 | `ukb validate` | **PASSED** | 1005 artifacts; append-only page ledger intact; referential integrity OK |
| 3 | `ukb enforce` | **PASSED** | eligible 1005 == registered 1005; 0 unregistered / 0 unclassified / 0 invalid |
| 4 | `ukbx validate` | **PASSED** | 15 signals; provenance present; secret-free |
| 5 | `ukbx twin --check` | **CERTIFIED 7/7** | C-05 referential · **C-07 acyclic** · C-08 navigation · C-09 control-tower · C-10 export · C-11 search |
| 6 | `ukbx certify` | **CERTIFIED 10/10** | 10 integrity domains — scope 1005, 15 signals, 1098 change events |
| 7 | `register.sh --guard` | **exit 3 (expected)** | uncommitted-registration drift only (see `03`) |

## 2 — Correctness cross-checks

| Check | Result | Evidence |
|---|:--:|---|
| Classification (USIS/USIS/VOL-024) | **PASS** | metadata + `config.py:275`; `unclassified == 0` |
| Single canonical home (`05-META-MODEL/`) | **PASS** | one path; Area 05 (USIS-005 §2/§3) |
| Depends-On resolves (USIS-001 + USIS-002 registered) | **PASS** | both edges resolve in graph |
| No forward reference | **PASS** | all targets pre-registered |
| Acyclic, downward-only graph | **PASS** | twin C-07; 8 edges to ancestors |
| Append-only identity | **PASS** | id-ledger 9139 → 9142; nothing reused/renumbered |
| No new volume | **PASS** | VOL-024 reused; `artifact_count` 3 → 4 |
| Frozen paths / `config.py` unchanged | **PASS** | `git diff` empty on all frozen/governed paths |
| LAW USIS-08 realization (24-tier model) | **PASS** | Part C rows 1..24; conformance/agnosticism/reuse-first/recursion present |

## 3 — USIS-011 proof obligations (acceptance-relevant)

| Obl. | Name | Status |
|---|---|:--:|
| 2 | Zero Duplication | **PASS** |
| 3 | Zero Overlap | **PASS** |
| 4 | Zero Orphan Artifacts | **PASS** |
| 5 | Zero Circular Dependencies | **PASS** |
| 8 | Knowledge Once | **PASS** |
| 9 | Canonical Ownership | **PASS** |
| 10 | Registry Closure | **PASS** |
| 13 | Capability Closure (schema defined) | **PASS** |
| 14 | No Forward Reference / Dependency Closure | **PASS** |
| 15 | Traceability Closure | **PASS** |
| 18 | Repository Consistency (byte-stable) | **PASS** |
| 19 | Constitutional Consistency | **PASS** |
| 20/21 | Open / uncapped | **PASS** |

## 4 — Environment note (non-blocking)

`ukb validate` runs structural checks only (`jsonschema not installed`), matching
the published baseline (Risk R-4). Full schema validation is enforced by CI
(`ucos-registration-gate.yml`). Not a regression; not a blocker.

## 5 — Determination

**All applicable validation and certification gates PASS.** The only non-PASS
signal (`--guard` exit 3) is the intentional uncommitted state, analyzed in `03`.
Validation supports **acceptance**.
