# Output 4 — Registry Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `00-BOOK/DATA/*.json` parsed directly at HEAD `9de85ad`; register roster reproduced from `GOV-INT-001` §6.2

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 4 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | The register set, its stores, and their measured contents. Gates over the registers → Output 10. Generated-vs-authored classification → Output 7. |
| EVIDENCE | `evidence/registry-files.txt` · `evidence/registry-metrics.txt` · `evidence/cert-ct-metrics.txt` |

---

## 1. Single-store rule (the measurement's own basis)

`STATUS-REG-001` §0 fixes exactly one machine source of truth and one human index. `GOV-INT-001` §6.1 fixes one append-only store (`00-BOOK/DATA/`), one identifier allocator (`id-ledger.json`), one graph (`relationships.json`), and states that human indices under `REGISTRIES/` are generated, never hand-authored. This inventory measures that store; it declares no register of its own.

## 2. Machine stores (`00-BOOK/DATA/`, 10 tracked files)

| File | Role | Measured content | Method |
|---|---|---|---|
| `artifacts.json` | Append-only artifact registry | **1,199** artifacts | M-2 |
| `relationships.json` | Knowledge graph / traceability | **12,841** edges | M-2 |
| `id-ledger.json` | Sole identity allocator | **1,219** `by_path` entries · `page_cursor` **9,587** | M-2 |
| `control-tower.json` | Portfolio roll-up + 15 lifecycle dimensions | see §6 | M-2 |
| `certification.json` | Digital-twin certification | verdict **CERTIFIED**, domains **10/10** | M-2 |
| `change-ledger.json` | Change / version / lineage ledger | `change_events` array empty at HEAD; certification scope records **1,358** change events | M-2 |
| `twin.json` | Digital twin subjects + dimensions | **15** signals | M-2 |
| `signals.json` | Append-only signal ledger | **15** signals | M-2 |
| `volumes.json` | Volume registry | **25** volumes | M-2 |
| `connector-cursors.json` | Connector ingest cursors | 7 connectors (§7) | M-2 |

## 3. Human indices (`00-BOOK/REGISTRIES/`, 6 tracked files)

`UNIVERSAL-ARTIFACT-REGISTRY.md` · `UNIVERSAL-PAGE-REGISTRY.md` · `KNOWLEDGE-GRAPH-REGISTRY.md` · `CERTIFICATION-REGISTRY.md` · `CHANGE-VERSION-LINEAGE-REGISTRY.md` · `VOLUME-REGISTRY.md`.

All six are generated (Output 7). The seventh human index named by `STATUS-REG-001` §0 — the Master Execution Status Registry — is hand-authored and lives in `00-BOOK/CONTROL-TOWER/`, outside this directory.

## 4. The eleven-register set as declared

`GOV-INT-001` §6.2 declares eleven registers in one store: seven owned by `REG-AUTO-001` and four by `UCI-001`.

| # | Register | Declared file | Present at HEAD | Method |
|---|---|---|---|---|
| 1 | Artifact Registry | `artifacts.json` | **yes** | M-2 |
| 2 | Execution Status Registry | roll-up in `control-tower.json` | **yes** | M-2 |
| 3 | Control Tower | `control-tower.json` | **yes** | M-2 |
| 4 | Digital Twin | `twin.json` + `signals.json` | **yes** | M-2 |
| 5 | Traceability / Knowledge Graph | `relationships.json` | **yes** | M-2 |
| 6 | Dependency Registry | `artifacts.json[*].dependencies` | **yes** (field present on every entry) | M-2 |
| 7 | Page / ID Ledger | `id-ledger.json` | **yes** | M-2 |
| 8 | Universal Change Registry | `changes.json` | **NO — absent** | M-2 |
| 9 | Universal Knowledge Registry | `knowledge.json` | **NO — absent** | M-2 |
| 10 | Regeneration Requirements Registry | `regeneration.json` | **NO — absent** | M-2 |
| 11 | Rollback Registry | `rollback.json` | **NO — absent** | M-2 |

Registers 1–7 exist; registers 8–11 do not exist at this HEAD. `GOV-INT-001` §11 records their state as "READY TO ADD". The measurement is recorded here; the gap is carried in `13-KNOWN-GAPS.md` DG-1.

## 5. Artifact population as measured

| Dimension | Measured | Method |
|---|---|---|
| Registered artifacts | 1,199 | M-2 |
| Distinct categories | 94 | M-2 |
| Volumes | 25 | M-2 |
| Pages allocated | 9,587 | M-2 |
| Artifacts with a non-empty `traceability` field | **1,199 of 1,199** | M-4 |
| Artifacts with ≥1 declared dependency | **190 of 1,199** | M-4 |

Status histogram: `ACTIVE` 1,098 · `COMPLETE` 43 · `FROZEN` 27 · `UNDER_REVIEW` 15 · `FINAL` 9 · `CERTIFIED` 7.

Largest programme populations: `SERVICE` 168 · `DATA` 153 · `APPLICATION` 143 · `INFRASTRUCTU` 132 · `CONSOLIDATION` 58 · `PLATFORM` 51 · `USIS` 36 · `CEP` 35 · `UMB` 31.

The programme token `INFRASTRUCTU` (132) and `INFRASTRUCTURE` (20) both occur, as do other truncated 12-character tokens (`IMPLEMENTATI`, `ARCHITECTURA`, `CERTIFICATIO`, …). Measured and recorded in `12-DISCOVERY-OBSERVATIONS.md` OBS-4; not repaired.

## 6. Lifecycle dimensions (`control-tower.json`, 15)

| Dimension | Status | Signal source | As-of |
|---|---|---|---|
| architecture | APPROVED | MANUAL | 2026-07-26 |
| implementation | IMPLEMENTED | GIT | 2026-07-16 |
| build | **BLOCKED** | GITHUB_ACTIONS | 2026-07-15 |
| unit_testing | **BLOCKED** | GITHUB_ACTIONS | 2026-07-15 |
| integration_testing | NOT_STARTED | MANUAL | 2026-07-26 |
| functional_testing | NOT_STARTED | MANUAL | 2026-07-26 |
| performance_testing | NOT_STARTED | MANUAL | 2026-07-26 |
| security | **BLOCKED** | TRIVY | 2026-07-15 |
| certification | CERTIFIED | MANUAL | 2026-07-26 |
| deployment | IN_PROGRESS | KUBERNETES | 2026-07-15 |
| production | **BLOCKED** | PROMETHEUS | 2026-07-15 |
| operational | **BLOCKED** | PROMETHEUS | 2026-07-15 |
| release | NOT_STARTED | MANUAL | 2026-07-26 |
| execution | NOT_STARTED | MANUAL | 2026-07-26 |
| portfolio | IN_PROGRESS | MANUAL | 2026-07-26 |

Portfolio roll-up as recorded: *"IN_PROGRESS — analysis/architecture/generation complete; runtime testing/deployment pending EC-1"*.

Every automated dimension carries an `as_of` of **2026-07-15**, which precedes HEAD. Recorded in `14-KNOWN-RISKS.md` DR-3.

## 7. Connector cursors (7)

`execution-register` · `git-repository` · `github-actions` · `kubernetes` · `prometheus` · `sonarqube` · `trivy`. At the last transaction all seven reported `[OK]`; only `git-repository` produced an event (1 event, 0 new, 1 duplicate) (M-3, `register.sh` Phase output).

---

*`UCCEP-000007` Output 4. AUTHORITY = NONE (DERIVED TRUTH). Measures the store; creates no register. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
