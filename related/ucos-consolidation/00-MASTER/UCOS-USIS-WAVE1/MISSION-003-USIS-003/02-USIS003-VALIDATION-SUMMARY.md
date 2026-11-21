# 02 — USIS-003 VALIDATION SUMMARY (independent re-run)

All gates re-executed this session against the working tree carrying the
uncommitted USIS-003 registration. Scope: **1006** artifacts.

---

## 1 — Gate ledger

| # | Gate | Result | Key evidence |
|---|---|:--:|---|
| 1 | `register.sh` (10-phase transaction) | **TRANSACTION COMPLETE** | all phases sealed; exit 0 |
| 2 | `ukb validate` | **PASSED** | 1006 artifacts; append-only page ledger intact; referential integrity OK |
| 3 | `ukb enforce` | **PASSED** | eligible 1006 == registered 1006; 0 unregistered / 0 unclassified / 0 invalid |
| 4 | `ukbx validate` | **PASSED** | 15 signals; provenance present; secret-free |
| 5 | `ukbx twin --check` | **CERTIFIED 7/7** | C-05 referential · **C-07 acyclic** · C-08 navigation · C-09 control-tower · C-10 export · C-11 search |
| 6 | `ukbx certify` | **CERTIFIED 10/10** | 10 integrity domains — scope 1006, 15 signals, 1099 change events |
| 7 | `register.sh --guard` | **exit 3 (expected)** | uncommitted-registration drift only (see `03`) |

## 2 — Correctness cross-checks

| Check | Result | Evidence |
|---|:--:|---|
| Classification (USIS/USIS/VOL-024) | **PASS** | metadata + `config.py:275`; `unclassified == 0` |
| Single canonical home (`07-SCIENCES/`) | **PASS** | one path; Area 07 |
| Single canonical ownership (`USIS-U-SCI`) | **PASS** | every science row owned by `USIS-U-SCI` |
| Depends-On resolves (USIS-002 + USIS-004 registered/committed) | **PASS** | both edges resolve in graph |
| Meta-model conformance to committed USIS-004 | **PASS** | `Implements → UCOS-USIS-000004` (committed `e33c05b`) |
| No forward reference | **PASS** | all targets pre-registered |
| Acyclic, downward-only graph | **PASS** | twin C-07; edges to ancestors only |
| Cross-links reference-only (LAW USIS-02) | **PASS** | Part C/D |
| Append-only identity | **PASS** | id-ledger append; nothing reused/renumbered |
| No new volume | **PASS** | VOL-024 reused; `artifact_count` 4 → 5 |
| Frozen paths / `config.py` unchanged | **PASS** | `git diff` empty |
| 30-discipline enumeration | **PASS** | Part C rows 1..30 |

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
| 13 | Capability Closure (meta-model conformance) | **PASS** |
| 14 | No Forward Reference / Dependency Closure | **PASS** |
| 15 | Traceability Closure | **PASS** |
| 18 | Repository Consistency (byte-stable) | **PASS** |
| 19 | Constitutional Consistency | **PASS** |
| 20/21 | Open / uncapped | **PASS** |

## 4 — Environment note (non-blocking)

`ukb validate` runs structural checks only (`jsonschema not installed`), matching
the published baseline (R-4); CI enforces the schema layer. Not a regression.

## 5 — Determination

**All applicable validation and certification gates PASS.** The only non-PASS
signal (`--guard` exit 3) is the intentional uncommitted state, analyzed in `03`.
Validation supports **acceptance**.
