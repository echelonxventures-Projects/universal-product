# Output 10 — Validation Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `00-MASTER/UCCEP-000000/uccep.json` (full-tier run at the baseline) · `uccep-bindings.json` · `Makefile` · `verify.sh` · `.github/workflows/` · `.kiro/hooks/` read at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 10 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | The checks, the gates that compose them, and the entry points that execute them. Certification verdicts and the ceiling → Output 11. |
| EVIDENCE | `evidence/verdicts.txt` · `evidence/make-targets.txt` · `evidence/enforcement-gates.txt` |

---

## 1. Checks (18) — measured verdicts at the baseline

| Check | Verdict | Exit | Tier | Advisory | Owner |
|---|---|---|---|---|---|
| CK-CMG | **PASS** | 0 | boot | no | `00-CMG/CMG-000001` · `tools/cmg_validate.py` |
| CK-REG-ENFORCE | **PASS** | 0 | boot | no | `ukb.py` (REG-AUTO-001 / UMB-IMP-001) |
| CK-REG-VALIDATE | **PASS** | 0 | boot | no | `ukb.py` |
| CK-CLOSURE-P1 | **PASS** | 0 | standard | no | `UAKOS-CLOSURE-002/closure_engine.py` |
| CK-CLOSURE-P2 | **PASS** | 0 | standard | no | `UAKOS-CLOSURE-002/phase2_engine.py` |
| CK-CLOSURE-P3 | **FAIL** | 1 | standard | **yes** | `UAKOS-CLOSURE-002/phase3_engine.py` |
| CK-HEALTH | **FAIL** | 1 | boot | **yes** | `platform/measurement` (UCOS-UMA-001) |
| CK-GRAPH | **PASS** | 0 | boot | no | `engine/graph` |
| CK-DISCOVERY | **PASS** | 0 | boot | no | `engine/discovery` |
| CK-RIE-DETERMINISM | **PASS** | 0 | standard | no | `intelligence/rie` |
| CK-VERIFY | **PASS** | 0 | full | no | `verify.sh` |
| CK-DETERMINISM-BUILD | **PASS** | 0 | full | no | `engine/determinism` |
| CK-REG-DRIFT | **PASS** | 0 | full | no | `register.sh` (REG-AUTO-001 §16.3) |
| CK-DECISION-EVIDENCE | **PASS** | 0 | boot | no | `UCDA-000001/ucda_engine.py` (CEP-002 Art 28) |
| CK-SELF-DECLARATION | **PASS** | 0 | boot | no | `UCCEP-000000/uccep_engine.py` |
| CK-SELF-NO-ENUMERATION | **PASS** | 0 | boot | no | same |
| CK-SELF-WRITE-SCOPE | **PASS** | 0 | boot | no | same |
| CK-SELF-DETERMINISM | **PASS** | 0 | standard | no | same |

**18 executed · 16 PASS · 2 FAIL, both advisory · 0 blocking failures · 0 unavailable.**

`CK-REG-DRIFT` was **FAIL (exit 3)** before the OA-1 commit and **PASS** after it — the state change that condition C-1 existed to produce (M-3, both runs).

## 2. Gates (14) — measured verdicts and composition

| Gate | Name | Verdict | Composed of | Owner |
|---|---|---|---|---|
| G-01 | Context Assimilation Gate | PASS | CK-CLOSURE-P1 | `MCP-001-MASTER-CONTEXT.md` |
| G-02 | Knowledge Assimilation Gate | PASS | CK-CLOSURE-P1, P2 | `UAKOS-CLOSURE-002` |
| G-03 | Reuse Gate | PASS | CK-CLOSURE-P2, CK-DISCOVERY | `IAC-001D` §05 |
| G-04 | Constitution Gate | PASS | CK-CMG | `CEP-001` |
| G-05 | Architecture Admission Gate | PASS | CK-CMG, CK-SELF-NO-ENUMERATION | `CMG-000001` |
| G-06 | Repository Truth Gate | PASS | CK-REG-ENFORCE, CK-REG-VALIDATE, CK-SELF-WRITE-SCOPE | `ukb.py` |
| G-07 | Registry Gate | **PASS** | CK-REG-ENFORCE, CK-REG-DRIFT | `register.sh` (REG-AUTO-001) |
| G-08 | Dependency Gate | PASS | CK-GRAPH | `engine/graph` |
| G-09 | Governance Gate | PASS | CK-CMG, CK-SELF-DECLARATION | `CEP-002` |
| G-10 | Validation Gate | PASS | CK-VERIFY | `CEP-004` |
| G-11 | Certification Gate | **PASS-WITH-ADVISORY** | CK-HEALTH, CK-VERIFY | `CEP-005` |
| G-12 | Evidence Gate | PASS | CK-RIE-DETERMINISM, CK-SELF-DETERMINISM | `CEP-008` |
| G-13 | Implementation Authorization Gate | PASS | CK-DETERMINISM-BUILD, CK-VERIFY | `UCIC-001` |
| G-14 | Implementation Evidence Gate | PASS | CK-DECISION-EVIDENCE | `CEP-002` Art 28 |

**14/14 PASS**, one carrying an advisory. `G-07` was FAIL before OA-1.

## 3. Binding declaration structure

`00-MASTER/UCCEP-000000/uccep-bindings.json` sections and sizes (M-2): `principles` **21** · `invariants` **17** · `checks` **18** · `gates` **14** · `programs` **16** · `findings` **8** · `work_packages` **5**.

`uccep_engine.py` passes `--check-no-enumeration`, so none of these identifiers appears as a literal in the engine: adding a check, gate, programme, finding or work package is a data edit requiring no code change (M-3).

## 4. Advisory checks (2) — disclosed, never absorbed

| Check | Measured failure | Governing finding | Constraint |
|---|---|---|---|
| `CK-CLOSURE-P3` | exit 1 | `UCCEP-F-001` — the phase-3 engine returns a constant NOT-CLOSED verdict independent of measured state | **K-12**: advisory failures are disclosed, not reported as passing |
| `CK-HEALTH` | exit 1 | `UCCEP-F-002` — repository health RED: 1,198 of 1,198 registered artifacts have incomplete traceability (≈22.7% semantic completeness) | **K-08**: traceability must not regress |

## 5. Enforcement chain (`CMG-DLG-40`)

| Entry point | Executes | Measured at this baseline |
|---|---|---|
| `verify.sh` | ruff · pytest+coverage · coverage report · `ukb enforce --pre` | **exit 0**, 4/4 stages PASS, coverage 97% |
| `verify.sh --full` | the above plus `register.sh --guard` | not run in this mission |
| `make cmg-gate` | `00-CMG/tools/cmg-gate.sh` | **exit 0**, 0 findings, READY-PROVISIONAL |
| `make uccep-boot / uccep-gate / uccep-full` | `uccep_engine.py` at tier boot / standard / full | full tier **exit 0** |
| `make uccep-self` | 4 self-guards | 4/4 PASS |
| `make ucda / ucda-gate` | `ucda_engine.py` | gate **OPEN**, exit 0 |
| `make ucda-self` | 4 self-guards | 4/4 PASS |
| `make closure / closure-gate / closure-phase2* / closure-phase3*` | closure engines | not run in this mission |
| `register.sh --guard` | the 10-phase Atomic Registration Transaction `T` + drift check | **exit 0**, 10/10 integrity domains CERTIFIED, zero drift |
| `.git/hooks/pre-commit` | ruff lint + format check | PASS (`886 files already formatted`) |

## 6. The four enforcement gates of the corpus

`config.py :: ENFORCEMENT_GATES = ("eligibility", "validity", "classification", "registration")`.

Measured at the baseline (M-3, `ukb enforce --pre`): eligible on-disk artifacts **1,199** · registered **1,199** · unregistered **0** · unclassified (OTHER/MISC) **0** · reconciled sets declared **1 (CMG)** · reconciled-set drift **0** · invalid **0**.

`REG-AUTO-001` §21 strengthened the pre-existing `classification` gate rather than adding a gate: a file inside a declared reconciled zone must resolve to a classification the determination admits. Zones outside the declaration are vacuously conformant (M-2, `ukb.py::reconciliation_violation`).

## 7. Continuous integration (4 workflows)

`determinism.yml` · `ec1-ci.yml` · `uccep-gate.yml` · `ucos-registration-gate.yml`. All four are tracked; `.github/` is registration-excluded (Output 7).

## 8. Session hooks (4)

`.kiro/hooks/`: `auto-register-artifact.json` (PostFileCreate → `register.sh`), `uakos-closure-002.json`, `uccep-000000.json`, `ucda-000001.json`. `.kiro/` is registration-excluded.

## 9. Measured limitation of the validation surface

`ukb validate` reports: *"jsonschema not installed — ran structural checks only"*. Schema validation is therefore **not** exercised at this baseline; structural checks pass. Governed by `UCCEP-F-006` / `WP-UCCEP-004`. Recorded in `13-KNOWN-GAPS.md` DG-3.

---

*`UCCEP-000007` Output 10. AUTHORITY = NONE (DERIVED TRUTH). Reports executed verdicts; creates no gate. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
