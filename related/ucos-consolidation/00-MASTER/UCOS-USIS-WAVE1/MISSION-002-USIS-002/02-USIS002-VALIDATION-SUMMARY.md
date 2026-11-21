# 02 — USIS-002 VALIDATION SUMMARY (independent re-run)

All gates re-executed this session against the working tree carrying the
uncommitted USIS-002 registration. Scope: **1004** artifacts.

---

## 1 — Gate ledger

| # | Gate | Result | Key evidence |
|---|---|:--:|---|
| 1 | `register.sh` (10-phase transaction) | **TRANSACTION COMPLETE** | all phases sealed; exit 0 |
| 2 | `ukb validate` | **PASSED** | 1004 artifacts; append-only page ledger intact; referential integrity OK; forward-only lifecycle intact |
| 3 | `ukb enforce` | **PASSED** | eligible 1004 == registered 1004; unregistered 0 / unclassified 0 / invalid 0 |
| 4 | `ukbx validate` | **PASSED** | 15 signals, append-only, every subject resolves, provenance present, no embedded secrets |
| 5 | `ukbx twin --check` | **CERTIFIED 7/7** | C-05 referential · **C-07 acyclic** · C-08 navigation · C-09 control-tower · C-10 export · C-11 search |
| 6 | `ukbx certify` | **CERTIFIED 10/10** | identity·registry·traceability·knowledge-graph·change·version·lineage·synchronization·twin·execution — scope 1004, 15 signals, 1097 change events |
| 7 | `register.sh --guard` | **exit 3 (expected)** | uncommitted-registration drift only (see `03`) |

## 2 — Correctness cross-checks

| Check | Result | Evidence |
|---|:--:|---|
| Classification (USIS/USIS/VOL-024) | **PASS** | metadata + `config.py:275` agree; `unclassified == 0` |
| Single canonical home (`06-UNIVERSES/`) | **PASS** | one path; `08-DOMAINS/` untouched |
| Depends-On resolves (USIS-001 registered) | **PASS** | `UCOS-USIS-000002` present; edge in graph |
| No forward reference | **PASS** | all edge targets pre-registered (USIS-001 Wave 1; USIS-GOV-000 Wave 0) |
| Acyclic, downward-only graph | **PASS** | twin C-07; 8 edges all upward to ancestors |
| Append-only identity | **PASS** | id-ledger cursor 9136 → 9139; nothing reused/renumbered |
| No new volume | **PASS** | VOL-024 reused; `artifact_count` 2 → 3 |
| Frozen paths / `config.py` unchanged | **PASS** | `git diff` empty on all frozen/governed paths |

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
| 14 | No Forward Reference | **PASS** |
| 15 | Traceability Closure | **PASS** |
| 18 | Repository Consistency (byte-stable) | **PASS** |
| 19 | Constitutional Consistency | **PASS** |
| 20/21 | Open / uncapped registry | **PASS** |

## 4 — Environment note (non-blocking)

`ukb validate` runs structural checks only (`jsonschema not installed`), matching
the published baseline (Risk R-4). Full schema validation is enforced by CI
(`ucos-registration-gate.yml`). Not a regression; not a blocker.

## 5 — Determination

**All applicable validation and certification gates PASS.** The only non-PASS
signal (`--guard` exit 3) is the intentional uncommitted state, analyzed in `03`.
Validation supports **acceptance**.
