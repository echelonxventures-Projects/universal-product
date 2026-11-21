# Output 1 — Repository Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `git ls-files` and `git rev-list` at HEAD `9de85ad`; see `17-EVIDENCE-APPENDIX.md` E-01…E-04

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 1 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | The physical repository as committed. Semantics belong to Outputs 2–11. |
| BASELINE | HEAD `9de85ad` · anchor `1c6e750` · branch `programme/evo-usis-005` · tree CLEAN |
| EVIDENCE | `evidence/head.txt` · `evidence/zone-counts.txt` · `evidence/ext-counts.txt` · `evidence/code-loc.txt` |

---

## 1. Repository identity

| Fact | Measured | Method | Source |
|---|---|---|---|
| Origin | `github.com/echelonxventures-Projects/ABSOLUTE-FOUNDATION.git` | M-1 | `git remote -v` |
| Branch | `programme/evo-usis-005` | M-1 | `git rev-parse --abbrev-ref HEAD` |
| Upstream | **none configured** — ahead/behind not computable; nothing pushed | M-1 | `git rev-parse --abbrev-ref @{u}` → *no upstream* |
| HEAD | `9de85adb7e26211d07bd99b3bed356280c936a93` | M-1 | `git rev-parse HEAD` |
| HEAD subject | `OA-1 step 4: operational-memory reconciliation to the baseline anchor` | M-1 | `git log -1` |
| Rollback anchor | `1c6e750e53efdbcba5fc501d58fc99781b03a966` | M-1 | ancestor of HEAD, verified |
| Commits | **183** | M-1 | `git rev-list --count HEAD` |
| Tracked files | **4,499** | M-1 | `git ls-files \| wc -l` |
| Working tree | **CLEAN** (0 entries) | M-1 | `git status --porcelain` |

## 2. Tracked files by type

| Extension | Files | Method |
|---|---|---|
| `.md` | 2,496 | M-1 |
| `.py` | 1,412 | M-1 |
| `.json` | 548 | M-1 |
| `.docx` | 24 | M-1 |
| `.sh` | 8 | M-1 |
| `.yml` | 4 | M-1 |
| `.txt` | 4 | M-1 |
| `.toml` | 1 | M-1 |
| `.gitignore` | 1 | M-1 |
| *(no extension — `Makefile`)* | 1 | M-1 |
| **Total** | **4,499** | M-1 |

Counts use `core.quotePath=false`; without it, zone and extension tallies split on the non-ASCII `Ω∞` filenames and misreport (observed and recorded in `12-DISCOVERY-OBSERVATIONS.md` OBS-1).

## 3. Tracked files by top-level zone

| Zone | Files | Role as declared by the zone's own owner |
|---|---|---|
| `00-BOOK/` | 1,324 | Universal Knowledge Book — registries, portal, control tower, tools |
| `00-MASTER/` | 646 | Operational Memory (`MCS-000`); excluded from corpus registration |
| `platform/` | 555 | Realized platform code (EC-2) |
| `engine/` | 374 | Realized engine code (EC-1) |
| `service/` | 281 | Band-11 realized code |
| `data/` | 256 | Band-10 realized code |
| `infrastructure/` | 244 | Band-13 realized code |
| `application/` | 233 | Band-12 realized code |
| `02-MASTER/` | 80 | Master architecture and determination set |
| *(root)* | 80 | Root-level determinations, reports, `Makefile`, `verify.sh` |
| `00-CEP/` | 48 | Constitutional Engineering Program instruments |
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` | 36 | USIS programme zone |
| `intelligence/` | 27 | Repository Intelligence Engine outputs + code |
| `12-APPLICATION/` | 22 | Application family specification |
| `04-REFERENCE/` | 22 | Reference architecture corpus |
| `13-INFRASTRUCTURE/` | 20 | Infrastructure family specification |
| `09-PLATFORM/` | 20 | Platform family specification |
| `06-IMPLEMENTATION/` | 20 | Implementation architecture |
| `11-SERVICE/` | 19 | Service family specification |
| `10-DATA/` | 19 | Data family specification |
| `08-RUNTIME/` | 18 | Runtime family specification |
| `00-CMG/` | 18 | Meta-constitutional zone |
| `00-SOURCE/` | 13 | **FROZEN** source corpus |
| `IAC-001A…E/` | 41 | Implementation Authority Program lanes (7+8+9+9+9 across five directories) |
| `EVO-USIS-014/015/016` | 27 | USIS evolution lanes (9 each) |
| `07-ENGINEERING/` | 9 | Engineering programme |
| `05-GENERATION/` | 7 | Generation framework |
| `03-CATALOGS/` | 7 | Canonical catalogs |
| `01-WORKING/` | 7 | Consolidation working registers |
| `14-SECURITY/` | 5 | Security family specification |
| `.kiro/` | 4 | Session hooks (registration-excluded) |
| `.github/` | 4 | CI workflows (registration-excluded) |
| `adr/` | 3 | Architectural decision records |
| `scripts/` | 3 | Environment bootstrap |
| `99-FREEZE/` | 3 | **FROZEN** freeze notice and hashes |
| `00-SOURCE-MANIFEST/` | 2 | Source manifest |

## 4. Python source volume — totals only

| Measure | Value | Method |
|---|---|---|
| Tracked `.py` files in the measured trees | **1,395** | M-2 |
| Total LOC in those trees | **292,599** | M-2 |
| Of which test modules (`test_*.py`) | **564** | M-2 |

The per-tree breakdown is **owned by `06-IMPLEMENTATION-INVENTORY.md` §1** and is not restated here. The 17 remaining tracked `.py` files are the programme engines under `00-MASTER/`, enumerated in `02-PROGRAMME-INVENTORY.md` §3.

## 5. Frozen surfaces

| Surface | Files | Declared state | Source |
|---|---|---|---|
| `00-SOURCE/` | 13 | **FROZEN**, read-only absolutely | `99-FREEZE/FREEZE-NOTICE.md` |
| `99-FREEZE/` | 3 | **FROZEN** — freeze notice, `SOURCE-FILES.txt`, `SOURCE-HASHES.txt` | same |
| `00-SOURCE-MANIFEST/` | 2 | Source manifest over the frozen corpus | same |

---

*`UCCEP-000007` Output 1. AUTHORITY = NONE (DERIVED TRUTH). Measured, not designed. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
