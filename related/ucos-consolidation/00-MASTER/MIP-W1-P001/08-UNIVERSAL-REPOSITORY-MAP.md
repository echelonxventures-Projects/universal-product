# 08 — Universal Repository Map

**Anchor** `c6c20fb` · 4,895 tracked files · 236 discovered units (RIB) · 66 capabilities · 1,204 registered artifacts

Owner for every row is `UCOS-PROGRAM-CUSTODIAN` (single custodian across all 1,204 registered
artifacts); the *technical* owner column below names the authority that governs change.

---

## 1 · Governance & knowledge plane — 2,642 files (54.0%)

| Directory | Files | Purpose | Technical owner | Related architecture | Related capability |
|---|---|---|---|---|---|
| `00-BOOK/` | 1,320 | Universal Master Knowledge Book | UMB / REG-AUTO-001 | layer 8 | RC-61/62/63 |
| ├ `PORTAL/` | 1,211 | page projections (derived) | `ukb.py` | — | RC-53 `platform.universal_portal` |
| ├ `tools/` | 45 | `ukb.py`, `ukbx.py`, `register.sh` + 42 support | REG-AUTO-001 | — | RC-61/62/63 |
| ├ `MASTER-BOOK/` | 31 | master book volumes | UMB | — | — |
| ├ `ADVANCEMENT/` | 20 | advancement records | UMB | — | — |
| ├ `SCHEMAS/` | 19 | 19 JSON schemas (artifact, build, connector, control-tower, deployment, environment, export-job, finding, flow, journey, page, production-service, relationship, repository, signal, status, test, ui-artifact, volume) | UMB | — | — |
| ├ `CONTROL-TOWER/` | 12 | execution-status & roadmap registries | UMB | — | RC-38 |
| ├ `DATA/` | 10 | **the canonical data plane** — artifacts, relationships, id-ledger, change-ledger, certification, twin, control-tower, volumes, signals, connector-cursors | REG-AUTO-001 | layer 8 | RC-17 `engine.registry` |
| └ `REGISTRIES/` | 6 | Artifact · Page · Volume · Certification · Change-Version-Lineage · Knowledge-Graph registries | UMB | — | RC-15 `engine.graph` |
| `00-MASTER/` | 843 | Master Context System — 57 programme directories | MCS (AUTHORITY=NONE) | layer 9 | RC-64 |
| ├ `MCP-001…007` | 7 | Context · State · Execution · Decisions · Dashboard · Traceability · Recovery | MCS | — | — |
| ├ `UCCEP-000000/` | 23 | aggregate constitutional gate + 19 determinations | CEP-009 | — | — |
| ├ `UAKOS-CLOSURE-002/` | 78 | knowledge closure Phase-001/002/003 (3 engines, 68 outputs) | FROZEN spec | — | — |
| ├ `UCOS-RIB-001/` | 24 | Repository Integration Blueprint (EPIC-001) | UCIC-001 | — | — |
| ├ `UCDA-000001/` | 8 | decision assimilation overlay | CEP-002 Art 28 | — | — |
| ├ `UEI/UER/URRC/UCMI/UCDA/RTR/RA/IMR/…` | ~700 | 50 further programme directories, CHECKPOINTS, STATE | MCS | — | — |
| `00-CEP/` | 48 | Constitutional Engineering Programme: 11 constitutions + 37 stage bindings | CEP | layer 3–4 | — |
| `02-MASTER/` | 80 | 22 domain constitutions · universal catalogs (Capability, Component, Domain, Universe) · GOV-001…006 · CIOA · CCE | UCGF | layers 3–5 | SPEC-CIOA, SPEC-CCE |
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` | 36 | USIS: 21 numbered zones; `04-REGISTRIES/` holds 12 registries + master | USIS-GOV-000 | layer 4 | **none — no code root** |
| `00-CMG/` | 18 | Constitutional Meta-Governance CMG-000001…000014 + registry + `tools/cmg-gate.sh` | CMG (T1, **VACANT**) | layer 2 | — |
| `12-APPLICATION/` | 22 | Band 12 programme 001…018 + EVOL/INF determinations | APPLICATION-GOV-000 | layer 4 | RC-01/02 |
| `09-PLATFORM/` | 20 | Band programme 001…018 | PLATFORM-GOV-000 | layer 4 | RC-31…58 |
| `13-INFRASTRUCTURE/` | 20 | Band 13 programme 001…018 | INFRASTRUCTURE-GOV-000 | layer 4 | RC-22/23 |
| `06-IMPLEMENTATION/` | 20 | 20 platform/compiler/registry implementation determinations | EC-2/EC-3 | layers 6–7 | RC-31…58 |
| `10-DATA/` | 19 | Band 10 programme 001…018 | DATA-GOV-000 | layer 4 | RC-03/04 |
| `11-SERVICE/` | 19 | Band 11 programme 001…018 | SERVICE-GOV-000 | layer 4 | RC-59/60 |
| `08-RUNTIME/` | 18 | Runtime programme 001…014 + GOV-001/2/3 + REG-001 | RUNTIME-GOV-001 | layer 4 | RC-50 |
| `04-REFERENCE/` | 22 | 7 reference architectures + 3 assimilation matrices + **14 source `.docx`** | REF | — | — |
| `07-ENGINEERING/` | 9 | ENG master architectures: Identity, Object, Relationship & Reference, Type, Value + freeze/index | ENG-GOV-003 | layer 6 | RC-05…21 |
| `03-CATALOGS/` | 7 | canonical API / Application / Data / Event / Runtime / Service / Workflow catalogs | CAT | — | — |
| `05-GENERATION/` | 7 | universal generation frameworks (API/App/Data/Event/Service/Workflow + constitution) | GEN | — | RC-40 |
| `01-WORKING/` | 7 | working registers — **`ONTOLOGY-REGISTER.md` lives here** | — | — | — |
| `14-SECURITY/` | **5** | `SECURITY-001…004` + `GOV-000` — **truncated** | SECURITY-GOV-000 | layer 4 | RC-51 (partial) |
| `00-SOURCE/` | 5 | frozen source originals (`ARCHITECTURE/`, `CONSTITUTIONS/`, `VISION/`, `PHASES/`) | 99-FREEZE | layer 1–2 | — |
| `EVO-USIS-014/015/016` | 27 | sealed USIS evolution cycles (9 each) | USIS | — | — |
| `IAC-001A…E` | 43 | sealed assimilation cycles (7–9 each) | — | — | — |
| `99-FREEZE/` | 3 | `FREEZE-NOTICE.md`, `SOURCE-FILES.txt`, `SOURCE-HASHES.txt` | CEP-007 | — | — |
| `00-SOURCE-MANIFEST/` | 2 | manifest (identical content to `99-FREEZE` pair — declared freeze-boundary copy) | CEP-007 | — | — |
| `adr/` | 3 | template + ADR-0001 foundation stack + ADR-0002 AEOS phase 1 | CEP-002 Art 28 | — | — |
| root `*.md` | 78 | sequenced determinations `01-…`→`11-…`; `UCOS-OMEGA-INFINITY-MASTER-IMPLEMENTATION-PLAN-V2.md` (158 KB); `UCOS-ACFV-000001` (64 KB); runbooks | MCS | layer 2 | — |

## 2 · Implementation plane — 2,159 files (44.1%) · 246,066 LOC

| Root | Files | LOC | Src | Test files | Test fns | Modules / packages | Owner authority | Gate scope |
|---|---|---|---|---|---|---|---|---|
| `platform/` | 638 | 87,400 | 336 | 266 | 2,797 | 29 subpackages | EC-2 CLOSED/FROZEN | **19 of 29 in coverage** |
| `engine/` | 422 | 52,668 | 236 | 174 | 1,567 | 16 subpackages + `identity/` (empty) | EC-1 CERTIFIED | **15 of 16 in coverage** |
| `service/` | 281 | 20,464 | 79 | 53 | 1,038 | flat modules ×13 concerns × 6 aspects | EC-3 Band 11 | **0 — outside** |
| `data/` | 256 | 23,577 | 73 | 49 | 887 | flat modules ×12 concerns × 6 aspects | EC-3 Band 10 | **0 — outside** |
| `infrastructure/` | 244 | 22,599 | 67 | 45 | 821 | flat modules ×11 concerns × 6 aspects | EC-3 Band 13 | **0 — outside** |
| `application/` | 233 | 23,741 | 67 | 45 | 1,082 | flat modules ×11 concerns × 6 aspects | EC-3 Band 12 | **0 — outside** |
| `intelligence/` | 82 | 15,617 | 65 | 6 | 115 | 6 subpackages (`kernel`, `publication`, `realization`, `research`, `rie`, `tests`) + 11 RIE JSON outputs | ADDITIVE (AUTHORITY=NONE) | **0 — outside** |
| `realization/` | 9 | 1,314 | 6 | — | — | `api`, `architecture`, `deployment`, `docs`, `runtime`, `schema`, `tests` + URI manifest | URI | **0 — outside** |
| `knowledge/` | 3 | — | — | — | — | `canonical-knowledge.json`, `decisions.json`, `handbooks/` | CEP-002 Art 28 | n/a |
| `scripts/` | 3 | — | — | — | — | `cert004_expansion.py`, `install-hooks.sh`, `ucos-env.sh` | — | n/a |

### EC-3 band module pattern (uniform across all four bands)

Every band realizes each concern as **six sibling modules**:
`<concern>.py` · `<concern>_meta.py` · `<concern>_realize.py` · `<concern>_validation.py` ·
`<concern>_certification.py` · `<concern>_traceability.py`

| Band | Concerns |
|---|---|
| `data/` | attribute, band10, certification, datum, entity, governance, lifecycle, meta, model, quality, realize, schema, security, storage, … |
| `service/` | band11, capability, composition, contract, execution, interface, model, operation, orchestration, policy, security, service, … |
| `application/` | application, capability, composition, feature, governance, interaction, model, module, security, state, workflow |
| `infrastructure/` | band13, capability, compute, environment, governance, integration, network, resilience, security, storage, topology |

This is the single most systematic reuse pattern in the codebase — 6 aspects × ~47 concerns ×
4 bands. See output 15.

## 3 · Automation & CI plane — 16 files

| Path | Purpose |
|---|---|
| `.github/workflows/uccep-gate.yml` | aggregate constitutional gate |
| `.github/workflows/ucos-registration-gate.yml` | `ukb enforce --pre` + `register.sh --guard` |
| `.github/workflows/determinism.yml` | `engine.determinism.reproduce` double-build |
| `.github/workflows/ec1-ci.yml` | lint / test / build / frozen-guard |
| `.github/workflows/rib-gate.yml` | Repository Integration Gate |
| `.github/workflows/research-publication-gate.yml` | research (13) + publication (14) obligations |
| `.github/workflows/uei-gate.yml` · `uer-gate.yml` · `urrc-gate.yml` | evolution intelligence · execution resilience · RRC |
| `.kiro/hooks/*.json` (7) | session-start gates: closure, uccep, ucda, uei, uer, urrc, auto-register |

## 4 · Root build & entry surface — 78 files

| Path | Purpose |
|---|---|
| `Makefile` | 49 named targets — the canonical entry surface |
| `bootstrap.sh` · `doctor.sh` · `verify.sh` · `repo-ops.sh` | env setup · env validation · canonical gate · repository operations |
| `pyproject.toml` | **declares the verification and packaging scope — origin of blocker B-4** |
| `repo-operations.json` | repository operations declaration |
| `coverage.xml` (1.5 MB) · `.coverage` (2.9 MB) | coverage evidence |
| `ENVIRONMENT-SETUP.md` · `VERIFICATION-RUNBOOK.md` · `MCP-001-…md` | runbooks |
| 78 sequenced determination documents | `01-…` → `11-…` series |

## 5 · Untracked operational surface (present, gitignored)

| Path | Contents |
|---|---|
| `.runtime/` | `cert004`, `governance`, `integration`, `knowledge-graph`, `recovery`, `repository`, `repository-intelligence`, checkpoint json |
| `.ec1-venv/` | pinned canonical venv (Python 3.12) |
| `dist/`, `*.egg-info/`, `determinism-evidence/` | build + determinism outputs |
| `engine/identity/` | **only `__pycache__` — residual empty package** |
| `04-REFERENCE/~$*.docx` | Word lock files (correctly gitignored, not corpus artifacts) |

## 6 · Map verdict

| Criterion | Verdict |
|---|---|
| Every directory, package, module and file inventoried | **PASS** — 4,895 mapped, 0 unclassified |
| Every unit resolves to exactly one canonical owner | **PASS** — RIB `GAP-OWNER` = 0 over 236 units |
| Every unit reachable in ≥1 measured plane | **PASS** — RIB GATE-11, 0 orphans |
| Related architecture / documentation / capability resolvable per zone | **PASS** for all governance zones and EC-1/EC-2/EC-3 |
| Every code root inside the canonical verification scope | **FAIL** — 6 roots outside (**B-4**) |
| Every band zone architecturally complete | **FAIL** — `14-SECURITY` truncated |
| Every specification zone bound to code | **FAIL** — `15-USIS` (36 instruments, 12 registries) has no code root |
