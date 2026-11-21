# Output 2 — Programme Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** enumeration of `00-MASTER/*/` and `git ls-files` per directory at HEAD `9de85ad`; UCCEP programme roster reproduced from `00-MASTER/UCCEP-000000/uccep.json`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 2 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Programmes and their operational-memory directories. Constitutions → Output 3. Registries → Output 4. Ownership → Output 9. |
| EVIDENCE | `evidence/programme-dirs.txt` · `evidence/programme-engines.txt` · `evidence/verdicts.txt` |

---

## 1. Operational-memory programme directories (`00-MASTER/`)

**45 directories, 646 tracked files.** `00-MASTER/` is excluded from corpus registration by `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES` per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`, so nothing below holds a registered corpus identity.

| Directory | Tracked files | Method |
|---|---|---|
| `UCOS-USIS-WAVE2` | 102 | M-1 |
| `UCOS-USIS-WAVE1` | 81 | M-1 |
| `UAKOS-CLOSURE-006` | 33 | M-1 |
| `CHECKPOINTS` | 32 | M-1 |
| `UCCEP-000000` | 23 | M-1 |
| `UCOS-AB-001` · `UCOS-EG-001` | 21 each | M-1 |
| `UCOS-UMA-001` | 20 | M-1 |
| `UCOS-USIS-WAVE0` | 16 | M-1 |
| `UAKOS-CLOSURE-007` · `UAKOS-PHASE-001B` · `UCCEP-000005` | 15 each | M-1 |
| `UCOS-USIS-001` | 14 | M-1 |
| `UAKOS-PHASE-001A-R1` · `UAKOS-PHASE-003` · `UAKOS-PHASE-004` | 13 each | M-1 |
| `UAKOS-PHASE-002` | 11 | M-1 |
| `UCDA-000001` | 11 | M-1 |
| `UAKOS-CLOSURE-003` · `UAKOS-PHASE-003R` · `UCOS-CRAT-001` · `EIP-018D` · `UCCEP-000006` | 10 each | M-1 |
| `UAKOS-PHASE-003A-R2` · `UAKOS-PHASE-005` · `UCOS-CVER-001` · `UCOS-EKAP-001` · `UCOS-NUCLEUS-001` | 9 each | M-1 |
| `UAKOS-CLOSURE-002` · `UCOS-PROJ-SYNC-001` · `UCOS-USIS-WAVE3-FOUNDATION` | 8 each | M-1 |
| `UAKOS-PHASE-006` | 7 | M-1 |
| `UCOS-USIS-WAVE3-STRUCTURE` | 6 | M-1 |
| `RTR-001` · `UCOS-USIS-WAVE2-AUTH` | 5 each | M-1 |
| `RA-002` · `RA-003` | 3 each | M-1 |
| `STATE` | 2 | M-1 |
| `UAKOS-CLOSURE-004` · `UAKOS-CLOSURE-005` · `UAKOS-PHASE-007` · `UCOS-ACE-001` · `UCOS-CCD-001` | 1 each | M-1 |
| `UCOS-USIS-WAVE3-REGISTRY` | 10 | M-1 |
| `UCCEP-000007` *(this programme)* | 0 at measurement | M-1 |

## 2. The MCS component set

`MCS-000` §00 fixes a seven-file deterministic boot. All seven are present as tracked files at the repository root of `00-MASTER/`.

| Component | File | Question it answers (MCS-000 §03) |
|---|---|---|
| MCP-001 | `MCP-001-MASTER-CONTEXT.md` | Who are we and by what rules? |
| MCP-002 | `MCP-002-MASTER-STATE.md` | Where are we and what is next? |
| MCP-003 | `MCP-003-MASTER-EXECUTION.md` | What is authorized to run? |
| MCP-004 | `MCP-004-MASTER-DECISIONS.md` | Why is it this way? |
| MCP-005 | `MCP-005-MASTER-DASHBOARD.md` | How much is done? |
| MCP-006 | `MCP-006-MASTER-TRACEABILITY.md` | Can we prove it? |
| MCP-007 | `MCP-007-MASTER-RECOVERY.md` | How do we resume? |
| — | `MCS-000-MASTER-CONTEXT-SYSTEM-ARCHITECTURE.md` | The subsystem's own architecture |
| — | `UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md` | Capability implementation contract (15 stages) |
| — | `UCOS-RECON-001-…md` · `UCOS-RECON-C1-…md` | Reconciliation determinations |

## 3. Programme engines (17 tracked `.py` under `00-MASTER/`)

| Engine | Owning programme | Method |
|---|---|---|
| `UAKOS-CLOSURE-002/closure_engine.py` · `phase2_engine.py` · `phase3_engine.py` | Repository closure | M-2 |
| `UAKOS-PHASE-001A-R1/cert_engine.py` | Certification phase | M-2 |
| `UAKOS-PHASE-001B/emit_registers.py` · `provenance_engine.py` | Register emission / provenance | M-2 |
| `UAKOS-PHASE-002/phase2_recon.py` | Reconciliation | M-2 |
| `UAKOS-PHASE-003/phase3_gap.py` · `UAKOS-PHASE-003R/phase3r_engine.py` | Gap analysis | M-2 |
| `UAKOS-PHASE-004/phase4_plan.py` | Planning | M-2 |
| `UAKOS-PHASE-005/phase5_gov.py` | Governance | M-2 |
| `UAKOS-PHASE-006/phase6_certify.py` | Certification | M-2 |
| `UCCEP-000000/uccep_engine.py` | Aggregate constitutional gate | M-2 |
| `UCCEP-000005/derive.py` · `emit_views.py` | Dependency derivation / views | M-2 |
| `UCDA-000001/ucda_engine.py` | Implementation Evidence Gate (CEP-002 Art 28) | M-2 |
| `UCOS-USIS-WAVE0/freeze_c4_engine.py` | Wave-0 freeze | M-2 |

Generator classification and write-scope for these engines is Output 7's subject.

## 4. The UCCEP programme roster (16)

Reproduced verbatim from `00-MASTER/UCCEP-000000/uccep.json` → `programs[]`, which the engine derives from `uccep-bindings.json`. Verdicts are that engine's own, measured at the full tier.

| Id | Programme | Verdict | Rendered output |
|---|---|---|---|
| PROGRAM-000001 | Universal Constitutional Assimilation | PASS | `00-MASTER/UCCEP-000000/01-CANONICAL-ASSIMILATION-REGISTER.md` |
| PROGRAM-000002 | Repository Truth Reconciliation | PASS | `00-MASTER/UCCEP-000000/02-REPOSITORY-TRUTH-REGISTER.md` |
| PROGRAM-000003 | Universal Meta-Model Governance | PASS | `00-MASTER/UCCEP-000000/03-META-MODEL-GOVERNANCE-CERTIFICATION.md` |
| PROGRAM-000004 | Universal Registry Evolution | PASS | `00-MASTER/UCCEP-000000/04-UNIVERSAL-REGISTRY-CERTIFICATION.md` |
| PROGRAM-000005 | Universal Repository Governance | PASS | `00-MASTER/UCCEP-000000/05-REPOSITORY-GOVERNANCE-CERTIFICATION.md` |
| PROGRAM-000006 | Universal Enforcement Evolution | PASS | `00-MASTER/UCCEP-000000/06-EXECUTABLE-CONSTITUTIONAL-GOVERNANCE.md` |
| PROGRAM-000007 | Universal Traceability Evolution | **PASS-WITH-ADVISORY** | `00-MASTER/UCCEP-000000/07-UNIVERSAL-TRACEABILITY-GRAPH.md` |
| PROGRAM-000008 | Universal Dependency Evolution | PASS | `00-MASTER/UCCEP-000000/08-DEPENDENCY-INTELLIGENCE.md` |
| PROGRAM-000009 | Universal Knowledge Evolution | PASS | `00-MASTER/UCCEP-000000/09-KNOWLEDGE-EVOLUTION-ENGINE.md` |
| PROGRAM-000010 | Universal Implementation Evolution | PASS | `00-MASTER/UCCEP-000000/10-IMPLEMENTATION-EVOLUTION-ENGINE.md` |
| PROGRAM-000011 | Universal Validation Evolution | PASS | `00-MASTER/UCCEP-000000/11-VALIDATION-INTELLIGENCE.md` |
| PROGRAM-000012 | Universal Certification Evolution | **PASS-WITH-ADVISORY** | `00-MASTER/UCCEP-000000/12-CERTIFICATION-INTELLIGENCE.md` |
| PROGRAM-000013 | Universal Evolution Intelligence | PASS | `00-MASTER/UCCEP-000000/13-EVOLUTION-INTELLIGENCE.md` |
| PROGRAM-000014 | Universal Repository Intelligence | **PASS-WITH-ADVISORY** | `00-MASTER/UCCEP-000000/14-REPOSITORY-INTELLIGENCE.md` |
| PROGRAM-000015 | Universal Continuous Certification | **PASS-WITH-ADVISORY** | `00-MASTER/UCCEP-000000/15-CONTINUOUS-CONSTITUTIONAL-CERTIFICATION.md` |
| PROGRAM-000016 | Universal Decision Assimilation | PASS | `00-MASTER/UCCEP-000000/18-DECISION-ASSIMILATION-CERTIFICATION.md` |

**16/16 PASS**, four carrying an advisory. The advisory checks are named in `10-VALIDATION-INVENTORY.md` §4; the ceiling they feed is in `11-CERTIFICATION-INVENTORY.md` §4.

## 5. The UCCEP programme chain

| Programme | Directory | Role as its own outputs declare |
|---|---|---|
| `UCCEP-000000` | `00-MASTER/UCCEP-000000/` | Aggregate constitutional gate + binding declaration |
| `UCCEP-000005` | `00-MASTER/UCCEP-000005/` | Repository dependency remediation (closed) |
| `UCCEP-000006` | `00-MASTER/UCCEP-000006/` | Execution authorization & operator transition |
| `UCCEP-000007` | `00-MASTER/UCCEP-000007/` | Repository Controlled Implementation Programme — **this directory**, currently carrying only the discovery baseline |

`UCCEP-000001`…`000004` have no directory in the repository at this HEAD (M-1). Their absence is recorded, not explained, in `12-DISCOVERY-OBSERVATIONS.md` OBS-2.

---

*`UCCEP-000007` Output 2. AUTHORITY = NONE (DERIVED TRUTH). Measured, not designed. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
