# Output 14 — Known Risks

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** risk records reproduced from `00-MASTER/UCCEP-000006/08-RISK-ASSESSMENT.md` and `00-MASTER/UCCEP-000006/10-HANDOVER-TO-UCCEP-000007.md` §5–§6, and `00-MASTER/MCP-002-MASTER-STATE.md` §risk, read at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 14 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Risks **recorded by located owners**, reproduced with their measured state at this baseline. This programme assesses no new risk and treats none. |

---

## 1. Risks recorded by `UCCEP-000006` (10), with state re-measured at this baseline

Severity, blocking flag and treatment are that programme's own classifications. The rightmost column is this programme's measurement of the risk's condition at HEAD `9de85ad` — a measurement, not a re-assessment.

| Id | Risk as recorded | Severity | Blocking | Treatment recorded | Measured state at this baseline |
|---|---|---|---|---|---|
| R-01 | `UCCEP-F-003` record lag | LOW | No | C-2 / OA-2 | **still open** — binding records `GOVERNED / blocking: true` (→ DG-2) |
| R-02 | Uncommitted registration | **HIGH (raised)** | **YES** | C-1 / OA-1 | **discharged** — OA-1 committed at `1c6e750`; `CK-REG-DRIFT` PASS, `G-07` PASS, tree CLEAN |
| R-03 | Traceability ≈22.7% | HIGH | No (advisory) | OA-4 · K-08 | **still open** — `CK-HEALTH` advisory FAIL (→ DG-5) |
| R-04 | Tier T1 VACANT | STANDING | No | C-3 disclosure | **still open** — `VAC-01` located=false (→ Output 15) |
| R-05 | Constant phase-3 verdict | MEDIUM | No (advisory) | OA-5 · K-12 | **still open** — `CK-CLOSURE-P3` advisory FAIL (→ DG-7) |
| R-06 | ENG out-of-sequence append | LOW | No | K-10 · fail-closed gate | **gate present** — `config.py :: CHAINS.ENG` corrected to `ENG-GOV-001` Output 11 Option B; graph acyclic |
| R-07 | Mutation before a committed anchor | **HIGH** | Neutralised | C-1 suspensive · RB-1 · V-0 | **neutralised** — anchor `1c6e750` exists and is an ancestor of HEAD; V-0 satisfied |
| R-08 | Atomicity regression | MEDIUM | No | K-03 · V-3 · RB-3 | **not observed** — OA-1 committed source and projections in one unit of 247 files |
| R-09 | Cycle reintroduction | MEDIUM | No | K-02 · V-2 · fail-closed gate | **not observed** — `dependency_cycle = []`, 1,199/1,199 placed, 0 unorderable |
| R-10 | Provisional presented as ratified | MEDIUM | No | C-3 · K-09 · V-5 | **controlled** — every output of this programme carries the provisional disclosure |

**Measured at this baseline: 2 of 10 discharged or neutralised (R-02, R-07); 4 still open (R-01, R-03, R-04, R-05); 4 not observed or controlled.**

## 2. Risks recorded in operational memory

| Id | Risk as recorded | Recorded evidence | Measured state |
|---|---|---|---|
| R-CI-STALE | CI build/unit/security signals dated 2026-07-15 predate current HEAD and EC-2's local evidence | `MCP-002` §risk; Control Tower signal dates | **confirmed** — every automated `control-tower.json` dimension carries `as_of = 2026-07-15` (→ OBS-15) |

## 3. Risk-adjacent conditions measured by this programme

Recorded as conditions, not classified as risks — this programme has no authority to assign severity.

| Id | Condition | Evidence | Method |
|---|---|---|---|
| **DR-1** | The baseline exists only locally: branch `programme/evo-usis-005` has no upstream, so the anchor commit has not been pushed and does not exist off this machine | `git rev-parse --abbrev-ref @{u}` → *no upstream* | M-1 |
| **DR-2** | 60 evidence files backing prior programmes' seals — including the nine inputs to authorization seal `f497410c…` — are outside version control, so those seals cannot be reproduced from committed history alone | `.gitignore:72`; `UCCEP-000006` §9 | M-1 |
| **DR-3** | Nine `control-tower.json` dimensions derive from connectors whose last event predates HEAD by 11 days; five dimensions read BLOCKED and four NOT_STARTED | `evidence/cert-ct-metrics.txt` | M-2 |
| **DR-4** | Schema validation is silently optional in the validation path actually executed at this baseline | `ukb validate` output | M-3 |
| **DR-5** | The capability and health intelligence used by any downstream reader is 2 artifacts / 24 edges / 13 pages behind the registers | `evidence/rie-metrics.txt` vs `evidence/registry-metrics.txt` | M-3 + M-2 |
| **DR-6** | The declared machine mirror of `MCP-002` reports a different branch and HEAD than the canonical Markdown | direct read of `00-MASTER/STATE/mcs-state.json` | M-2 |

## 4. What this output deliberately omits

No treatment, no mitigation, no owner assignment beyond what a located owner already recorded, no severity of this programme's own, and no sequencing. Boundary constraint **K-12** requires advisory failures to be disclosed and never reported as passing; that obligation is discharged in Output 10 §4 and above.

---

*`UCCEP-000007` Output 14. AUTHORITY = NONE (DERIVED TRUTH). Reproduces located risk records and measures their condition; treats nothing. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
