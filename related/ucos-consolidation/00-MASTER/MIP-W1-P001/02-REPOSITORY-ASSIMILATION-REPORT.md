# 02 — Repository Assimilation Report

**Anchor** `integration/recovery-001` @ `c6c20fb5b4981f78ce76e6ba2fb48ec561cb52e5` · working tree CLEAN at anchor (0 entries)

---

## 1 · Repository Truth

| Measure | Value | Source |
|---|---|---|
| Tracked files | 4,895 | `git ls-files` |
| Working tree at anchor | CLEAN — 0 modified, 0 untracked, 0 deleted, 0 conflicts | `git status --porcelain` |
| Detached HEAD / interrupted operations / broken symlinks | none | `rib.json.repository` |
| Registered artifacts | 1,204 | `00-BOOK/DATA/artifacts.json` |
| Unregistered eligible artifacts | 0 (GATED) | `ukb enforce` |
| Unclassified (OTHER/MISC) | 0 (GATED) | `ukb enforce` |
| Invalid (unreadable/empty) | 0 | `ukb enforce` |
| Artifact paths not resolving on disk | 0 / 1,204 | measured |

## 2 · File-type census

| Extension | Count |
|---|---|
| `.md` | 2,682 |
| `.py` | 1,598 |
| `.json` | 567 |
| `.docx` | 24 |
| `.yml` | 9 |
| `.sh` | 8 |
| `.txt` | 4 |
| `.toml` | 1 |
| other (`.gitignore`, `Makefile`) | 2 |

## 3 · Plane decomposition

| Plane | Files | Share |
|---|---|---|
| Governance / knowledge corpus | 2,642 | 54.0% |
| Implementation / code | 2,159 | 44.1% |
| Root instruments & build | 78 | 1.6% |
| Automation / CI (`.github`, `.kiro`) | 16 | 0.3% |
| **Total** | **4,895** | 100% |

The repository is **majority-governance by file count**. This is a structural characteristic, not a
defect — but it is the reason traceability (output 13) rather than code quality is the binding
completeness constraint.

## 4 · Instrument-class census (governance plane)

| Instrument class | Files |
|---|---|
| Certification / certificate | 433 |
| Architecture | 206 |
| Registry / register | 205 |
| Constitution | 134 |
| Determination | 134 |
| Completion report | 83 |
| Evidence artefact (`_evidence/`, `/evidence/`) | 490 |

## 5 · Top-level topology

### Governance & knowledge zones

| Zone | Tracked | Purpose |
|---|---|---|
| `00-BOOK/` | 1,320 | Universal Master Knowledge Book — registries, schemas, data stores, portal projections (1,211 files), tools |
| `00-MASTER/` | 843 | Master Context System + 57 programme directories (operational memory, AUTHORITY=NONE) |
| `00-CEP/` | 48 | Constitutional Engineering Programme — 11 constitutions + 4 stages of binding architecture |
| `02-MASTER/` | 80 | Domain constitutions, universal catalogs, governance determinations |
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` | 36 | USIS programme — 21 numbered zones, 12 registries |
| `00-CMG/` | 18 | Constitutional Meta-Governance — CMG-000001…000014 + registry + gate tooling |
| `09-PLATFORM/` `13-INFRASTRUCTURE/` | 20 each | Band foundation programmes (001…018) |
| `12-APPLICATION/` | 22 | Band foundation programme + evolution determinations |
| `10-DATA/` `11-SERVICE/` | 19 each | Band foundation programmes (001…018) |
| `08-RUNTIME/` | 18 | Runtime programme (001…014 + GOV-001/2/3 + REG-001) |
| `04-REFERENCE/` | 22 | Reference architectures + 14 source `.docx` originals |
| `06-IMPLEMENTATION/` | 20 | Platform implementation determinations |
| `03-CATALOGS/` `05-GENERATION/` `07-ENGINEERING/` | 7 · 7 · 9 | Canonical catalogs, generation frameworks, ENG master architectures |
| `14-SECURITY/` | 5 | **Truncated programme** — see output 16 |
| `00-SOURCE/` `00-SOURCE-MANIFEST/` `99-FREEZE/` | 5 · 2 · 3 | Frozen source originals + manifest + freeze notice |
| `01-WORKING/` | 7 | Working registers (ontology register lives here) |
| `EVO-USIS-014…016`, `IAC-001A…E` | 9 each (43) | Sealed evolution / assimilation cycles |
| `adr/` | 3 | ADR template + 2 records |
| root `*.md` | 78 | Sequenced determinations `01-…` through `11-…` + 2 master plans |

### Implementation zones

| Root | LOC | Source files | Test files | Test functions | Authority |
|---|---|---|---|---|---|
| `platform/` | 87,400 | 336 | 266 | 2,797 | EC-2 CLOSED/FROZEN |
| `engine/` | 52,668 | 236 | 174 | 1,567 | EC-1 CERTIFIED |
| `application/` | 23,741 | 67 | 45 | 1,082 | EC-3 Band 12 realization |
| `data/` | 23,577 | 73 | 49 | 887 | EC-3 Band 10 realization |
| `infrastructure/` | 22,599 | 67 | 45 | 821 | EC-3 Band 13 realization |
| `service/` | 20,464 | 79 | 53 | 1,038 | EC-3 Band 11 realization |
| `intelligence/` | 15,617 | 65 | 6 | 115 | ADDITIVE (AUTHORITY=NONE) |
| `realization/` | 1,314 | 6 | — | — | URI manifest surface |
| **Total** | **246,066** | — | 638 | **8,307** | — |

## 6 · Automation & CI surface

| Workflow | Gate |
|---|---|
| `uccep-gate.yml` | Aggregate constitutional gate (14 gates · 16 programmes · 18 checks) |
| `ucos-registration-gate.yml` | `ukb enforce --pre` + `register.sh --guard` |
| `determinism.yml` | `engine.determinism.reproduce` double-build |
| `ec1-ci.yml` | lint / test / build / frozen-guard |
| `rib-gate.yml` | Repository Integration Gate (12 gates) |
| `research-publication-gate.yml` | Research (13 obligations) + Publication (14 obligations) |
| `uei-gate.yml` `uer-gate.yml` `urrc-gate.yml` | Evolution intelligence · execution resilience · RRC |

Session-start hooks: 7 (`.kiro/hooks/`) — closure, UCCEP, UCDA, UEI, UER, URRC, auto-register.
`Makefile` exposes 49 named targets. Environment is pinned and reproducible: Python 3.12,
pytest 8.3.4, pytest-cov 6.0.0, coverage 7.15.2, ruff 0.8.4 — `doctor.sh` reports ENVIRONMENT READY.

## 7 · Assimilation verdict

| Criterion | Verdict | Evidence |
|---|---|---|
| Every tracked file discovered and classified | **PASS** | 4,895 enumerated; 0 unclassified |
| Every eligible artifact registered | **PASS** | 1,204/1,204; 0 unregistered |
| Every registered path resolves | **PASS** | 0 missing of 1,204 |
| Repository integrity intact | **PASS** | RIB GATE-01/02, no conflicts or broken links |
| Registry content-hash binding correct | **FAIL** | 10 stale hashes at HEAD — blocker **B-1** |
| Verification scope covers the repository | **FAIL** | 56.9% LOC · 52.5% tests — blocker **B-4** |

**Repository assimilation is COMPLETE. Repository *certification* is not — B-1 and B-4 are open.**
