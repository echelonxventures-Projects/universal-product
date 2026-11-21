# 06 — AUTHORITY CLASSIFICATION MATRIX

> **Mission:** IAC-001A · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Consolidated per-field determination for every major artifact family. Fields per mission spec: Location · Name · Type · Canonical Owner · Authority Status · Source of Truth · Generated · Git Tracked · Gitignored · Implementation Authority · Evidence Only · Notes.

Legend — Authority Status: **CANON** (Canonical) · **DERIV** (Derived) · **GEN-R** (Generated, registered/tracked) · **GEN-N** (Generated, non-authoritative) · **REF** (Reference Evidence) · **HIST** (Historical) · **TEMP** (Temporary) · **EXT** (External).

| Location | Name / Family | Type | Canonical Owner | Authority | Source of Truth | Gen | Tracked | Ignored | Impl.Auth | Evid-only | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `00-CEP/` | CEP-000..010 | Constitutions | 00-CEP | **CANON** | self (authored) | No | Yes | No | **Yes** | No | Apex authority |
| `03-CATALOGS/` | 7 canonical catalogs | Catalogs | 03-CATALOGS | **CANON** | self | No | Yes | No | **Yes** | No | API/APP/DATA/EVENT/RUNTIME/SERVICE/WORKFLOW |
| `04-REFERENCE/*ARCHITECTURE*.md` | 7 REF constitutions | Reference constitutions | 04-REFERENCE | **CANON** | self | No | Yes | No | **Yes** | No | Registered REF family |
| `04-REFERENCE/*.docx`, `ARCHITECTURAL-SOURCES/` | Source docs | Reference | 04-REFERENCE | **REF** | authors/uploads | No | Yes | No | No | Yes | Vision/source evidence |
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` | USIS-001/002/003/004, GOV-000 | Universe/constitution | 15-… (canonical home) | **CANON** | self | No | Yes | No | **Yes** | No | PROVISIONAL tier, registered |
| `00-MASTER/UCOS-USIS-001/` | USIS program lane | Program authoring | UCOS-USIS-001 | **CANON** | self | No | Yes | No | **Yes** | No | Authoring lane |
| `00-BOOK/SCHEMAS/` | *.schema.json | Schemas | 00-BOOK | **CANON** | self | No | Yes | No | **Yes** | No | Authored contracts |
| `engine/**/*.py` | Engineering code (372) | Engines/code | engine | **CANON** | self | No | Yes | No | **Yes** | No | Incl. closure/phase/seed engines |
| `00-MASTER/UAKOS-CLOSURE-002/*_engine.py` + README/CHARTER/PLAN/CONTRACT | Closure engines + charter | Engines/docs | UAKOS-CLOSURE-002 | **CANON** | self | No | Yes | No | **Yes** | No | SoT of the gitignored closure outputs |
| `data/_evidence/**` | UCOS-DATA-* (123) | Certification evidence | data | **REF** (registered) | engines | Yes | Yes | No | No | Yes | Distinct registered family; not ignored |
| `infrastructure/_evidence/`, `intelligence/_evidence/` | Band evidence | Certification evidence | resp. dirs | **REF** | engines | Yes | Yes | No | No | Yes | Tracked evidence |
| `00-BOOK/DATA/*.json` | artifacts/certification/twin/control-tower/volumes/… | Projections | 00-BOOK | **GEN-R / DERIV** | REG-AUTO-001 + engines | Yes | Yes | No | No | Partly | Admitted (EAC-001 F3) |
| `00-BOOK/REGISTRIES/*.md` | CERTIFICATION/VOLUME/ARTIFACT/PAGE/GRAPH/LINEAGE | Registries | 00-BOOK | **GEN-R / DERIV** | REG-AUTO-001 | Yes | Yes | No | No | No | Regenerable projections |
| `00-MASTER/EIP-018D/*` | Wave-0 determinations | Determinations | EIP-018D | **DERIV** | derived over corpus | No | Yes | No | No | No | Self-declares `AUTHORITY = NONE` |
| `00-MASTER/RTR-001/*` | Reconciliation determinations | Determinations | RTR-001 | **DERIV** | derived over corpus | No | Yes | No | No | No | Resolves closure.json authority |
| `00-MASTER/STATE/mcs-state.json` | MCP state | Operational state | 00-MASTER/STATE | **DERIV** | MCP-001 engine | Yes | Yes | No | No | No | Content = readiness (out of scope) |
| root `01..11-*.md` | Prior-audit report series | Determinations/reports | root | **DERIV / HIST** | prior missions | No | Yes | No | No | No | Overlapping series; superseded ones = HIST |
| `00-MASTER/UAKOS-CLOSURE-002/{closure,phase2,phase3}.json` | Engine JSON state | Machine state | (engine) | **GEN-N** | closure/phase engines | Yes | No | **Yes** | **No** | No | `.gitignore:53`; RTR-001/05 |
| `00-MASTER/UAKOS-CLOSURE-002/NN-*.md` | Numbered reports/registers 20/22/31/37/38/40 | Reports/registers | (engine) | **GEN-N** | closure/phase engines | Yes | No | **Yes** | **No** | No | `.gitignore:52`; 39/43 not regenerated |
| `/knowledge/` | Knowledge store + handbooks | Generated store | (engine) | **GEN-N** | `engine/knowledge/seed.py` | Yes | No | **Yes** | **No** | No | Regenerable |
| `determinism-evidence/`, `00-MASTER/**/evidence/`, `provenance.json`, `…GAP-DEPENDENCY-GRAPH.json` | Execution evidence / engine state | Evidence/state | (engine) | **GEN-N** | phase engines | Yes | No | **Yes** | **No** | No | GPR-001 S1 scope |
| `.runtime/` | Governance telemetry | Runtime state | governance_telemetry.py | **EXT** | per-clone runtime | Yes | No | **Yes** | **No** | No | Never tracked (determinism remediation) |
| `.register.lock`, `__pycache__`, `*.pyc`, `.ec1-venv`, `build`, `dist`, `*.egg-info`, `.pytest_cache`, `.ruff_cache`, `.coverage`, `coverage.xml`, `~$*` | Transients | Build/test/office | — | **TEMP** | tools | Yes | No | **Yes** | **No** | No | Non-artifacts |
| `intelligence/die/` | Unverified orphan | Code (quarantined) | — | **TEMP/quarantine** | — | n/a | No | **Yes** | **No** | No | Excluded from RC-1 baseline |
| DR-RAT-11 finality act | Absolute finality ratification | Governance act | out-of-corpus | **EXT** | external authority | n/a | No | n/a | **No** | No | Absent by design (blocks only L8) |

## Authority resolution rule (applied uniformly)

`Impl.Authority = (Git-Tracked AND NOT Gitignored AND authored-source-of-truth)`.
Generated-but-tracked projections (GEN-R) are authoritative **as records/projections**, deriving from canonical code — they are not originating authority. Every family above resolves to exactly one class with no overlap.

---
*End of 06-AUTHORITY-CLASSIFICATION-MATRIX.md*
