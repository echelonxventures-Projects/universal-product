# Output 6 — Implementation Inventory

> **STATUS DOMAIN:** IMPLEMENTATION · **STATUS BASIS:** tracked-file enumeration of the code trees at HEAD `9de85ad` (M-2) and the `./verify.sh` run executed against this baseline (M-3). Per STATUS-001 §2 non-projection law, nothing here implies architecture, certification, or operational completion.

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 6 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Realized code as committed. Declared capability catalogue → Output 5. Gates that judge this code → Output 10. |
| EVIDENCE | `evidence/code-loc.txt` · `evidence/test-counts.txt` · `evidence/rie-metrics.txt` |

---

## 1. Code trees as committed

| Tree | `.py` files | of which `test_*.py` | LOC | Declared band / layer |
|---|---|---|---|---|
| `platform/` | 524 | **242** | 97,473 | EC-2 platform runtimes |
| `engine/` | 362 | **134** | 56,912 | EC-1 engine layers |
| `application/` | 112 | **44** | 34,024 | Band 12 — Application |
| `data/` | 122 | **48** | 32,906 | Band 10 — Data |
| `infrastructure/` | 112 | **44** | 30,843 | Band 13 — Infrastructure |
| `service/` | 132 | **52** | 30,300 | Band 11 — Service |
| `00-BOOK/tools/` | 13 | — | 6,031 | REG-AUTO-001 generator machinery |
| `intelligence/` | 16 | — | 2,598 | Repository Intelligence Engine |
| `scripts/` | 1 | — | 779 | Environment bootstrap |
| `00-CMG/tools/` | 1 | — | 733 | Meta-constitutional validator |
| **Total** | **1,395** | **564** | **292,599** | |

## 2. Verification executed against this baseline

`./verify.sh` run at the OA-1 baseline, four stages, all PASS (M-3):

| Stage | Result | Wall clock |
|---|---|---|
| ruff lint + format-check (engine + platform) | **PASS** | 0s |
| pytest + coverage gate (`--cov-fail-under=90`) | **PASS** | 26s |
| coverage report | **PASS** | 1–2s |
| governance enforce `--pre` | **PASS** | 0–1s |

Measured coverage at the run: **TOTAL 97%** over **31,884 statements / 6,162 branches**, 978 statements and 76 branches missed.

The pre-commit hook independently reported `All checks passed!` and `886 files already formatted` (M-3).

## 3. Coverage as the intelligence engine last recorded it

From `UCOS-RIE-HEALTH.json` → `code` (M-3, snapshot of 2026-07-26T02:49:04Z, predating this HEAD):

| Metric | Value |
|---|---|
| `coverage_line_pct` | 96.93 |
| `coverage_branch_pct` | 95.10 |
| `total_loc` | 101,499 (roots `engine` + `platform` only) |
| `total_tests` | 3,852 test functions |
| `engine` | 203 source files · 159 test files · 1,309 test functions · 39,555 LOC |
| `platform` | 271 source files · 253 test files · 2,543 test functions · 61,944 LOC |
| `health_flags.coverage_full` | **false** |

The engine's roots cover `engine` + `platform` only; the four band trees (`data`, `service`, `application`, `infrastructure` — 128,073 LOC by §1) are not in its `roots`. Recorded in `12-DISCOVERY-OBSERVATIONS.md` OBS-6.

## 4. Freeze and certification state of the code surface as declared

Reproduced from `00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §2 (M-3). These are that programme's declarations, not this programme's findings.

| Surface | Declared state | Protected-area id |
|---|---|---|
| `engine/**` · `platform/**` | freeze-gated by the EC-1 freeze + coverage gate | **X-8** |
| `application/**` | **FROZEN** — Band-12 baseline `beff9ed3…` | **X-6** |
| `data/**` · `service/**` frozen surfaces | **FROZEN** by their band determinations | **X-6** |
| `infrastructure/**` U01…U11 | **CERTIFIED**, not yet frozen (U12 freeze DEFERRED) | **X-7** |

## 5. Realization frontier as operational memory records it

`00-MASTER/MCP-002-MASTER-STATE.md` §01 records the EC-3 realization frontier as **U01…U11 CERTIFIED & COMPLETE** for Band 13, with `EC3-B13-U12` (Band-13 Freeze) **DEFERRED** and Bands 10–12 CERTIFIED-COMPLETE (Bands 11 and 12 additionally FROZEN) (M-3). This programme reproduces that record and does not re-verify the band certifications, which belong to their own certification determinations.

## 6. Non-projection notice

Per STATUS-001 §2, none of the above implies status in another domain. Specifically: the ARCHITECTURE domain being APPROVED and this IMPLEMENTATION evidence existing does **not** make roadmap, certification, or operational completion true. `control-tower.json` independently records `build`, `unit_testing`, `security`, `production` and `operational` as **BLOCKED** and four dimensions as **NOT_STARTED** (Output 4 §6).

---

*`UCCEP-000007` Output 6. AUTHORITY = NONE (DERIVED TRUTH). Measured, not certified. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
