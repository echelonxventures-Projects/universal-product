# UCOS-UFEP-001 · Freeze Eligibility Register

One row per freeze subject. A subject is an artifact holding a valid canonical record
in the located ratification registry — CEP-007 III.2 admits nothing else to the freeze
lifecycle. Eligibility is decided by the five CEP-007 Article V preconditions; where a
subject is not eligible, the unsatisfied precondition is named.

| Subject | Artifact | Ratification record | Ratification state | State | Eligible | Unsatisfied |
|---|---|---|---|---|---|---|
| `UFEP-SUB-01` | The constitutional order of the repository — document supremacy, root ontology, invariant set, law canon and authority chain, as fixed by the exogenous constituent act EC-1 | `URAT-REC-01` | PROVISIONAL | `ELIGIBLE` | **YES** | — |
| `UFEP-SUB-02` | The repository foundation — repository constitution, universal context assimilation law, knowledge-once principle, single canonical source of truth, canonical ownership model and repository governance | `URAT-REC-02` | PROVISIONAL | `ELIGIBLE` | **YES** | — |
| `UFEP-SUB-03` | INFRASTRUCTURE-013 Universal Infrastructure Security (U08, C15 SecurityFacet) | `URAT-REC-03` | PROVISIONAL | `ELIGIBLE` | **YES** | — |
| `UFEP-SUB-04` | INFRASTRUCTURE-014 Universal Infrastructure Governance (EC3-B13-U09, C16 GovernanceFacet) | `URAT-REC-04` | PROVISIONAL | `ELIGIBLE` | **YES** | — |
| `UFEP-SUB-05` | INFRASTRUCTURE-005 Universal Infrastructure Integration (UIMM, EC3-B13-U10) | `URAT-REC-05` | PROVISIONAL | `ELIGIBLE` | **YES** | — |

## Precondition detail (CEP-007 Article V)

| Subject | Precondition | Outcome | Measured from |
|---|---|---|---|
| `UFEP-SUB-01` | `UFEP-PRE-01` | SATISFIED | `00-MASTER/UCOS-CRAT-001/07-FOUNDATION-FREEZE-AUTHORIZATION.md` |
| `UFEP-SUB-01` | `UFEP-PRE-02` | SATISFIED | `00-MASTER/UCOS-CVER-001/07-GOVERNANCE-CERTIFICATION.md` |
| `UFEP-SUB-01` | `UFEP-PRE-03` | SATISFIED | `00-MASTER/UCOS-URAT-001/urat.json` |
| `UFEP-SUB-01` | `UFEP-PRE-04` | SATISFIED | `00-MASTER/UCOS-UTCE-001/utce.json` |
| `UFEP-SUB-01` | `UFEP-PRE-05` | SATISFIED | `determinism-evidence/determinism-evidence.json` |
| `UFEP-SUB-02` | `UFEP-PRE-01` | SATISFIED | `00-MASTER/UCOS-CRAT-001/07-FOUNDATION-FREEZE-AUTHORIZATION.md` |
| `UFEP-SUB-02` | `UFEP-PRE-02` | SATISFIED | `00-MASTER/UCOS-CVER-001/07-GOVERNANCE-CERTIFICATION.md` |
| `UFEP-SUB-02` | `UFEP-PRE-03` | SATISFIED | `00-MASTER/UCOS-URAT-001/urat.json` |
| `UFEP-SUB-02` | `UFEP-PRE-04` | SATISFIED | `00-MASTER/UCOS-UTCE-001/utce.json` |
| `UFEP-SUB-02` | `UFEP-PRE-05` | SATISFIED | `determinism-evidence/determinism-evidence.json` |
| `UFEP-SUB-03` | `UFEP-PRE-01` | SATISFIED | `00-CEP/STAGE-04-S4-05-SECURITY-VALIDATION-CERTIFICATION-FREEZE-READINESS.md` |
| `UFEP-SUB-03` | `UFEP-PRE-02` | SATISFIED | `00-CEP/STAGE-04-S4-05-SECURITY-VALIDATION-CERTIFICATION-FREEZE-READINESS.md` |
| `UFEP-SUB-03` | `UFEP-PRE-03` | SATISFIED | `00-MASTER/UCOS-URAT-001/urat.json` |
| `UFEP-SUB-03` | `UFEP-PRE-04` | SATISFIED | `00-MASTER/UCOS-UTCE-001/utce.json` |
| `UFEP-SUB-03` | `UFEP-PRE-05` | SATISFIED | `determinism-evidence/determinism-evidence.json` |
| `UFEP-SUB-04` | `UFEP-PRE-01` | SATISFIED | `00-CEP/STAGE-04-S4-09-INFRASTRUCTURE-014-GOVERNANCE-VALIDATION.md` |
| `UFEP-SUB-04` | `UFEP-PRE-02` | SATISFIED | `00-CEP/STAGE-04-S4-10-INFRASTRUCTURE-014-GOVERNANCE-CERTIFICATION.md` |
| `UFEP-SUB-04` | `UFEP-PRE-03` | SATISFIED | `00-MASTER/UCOS-URAT-001/urat.json` |
| `UFEP-SUB-04` | `UFEP-PRE-04` | SATISFIED | `00-MASTER/UCOS-UTCE-001/utce.json` |
| `UFEP-SUB-04` | `UFEP-PRE-05` | SATISFIED | `determinism-evidence/determinism-evidence.json` |
| `UFEP-SUB-05` | `UFEP-PRE-01` | SATISFIED | `00-CEP/STAGE-04-S4-12-INFRASTRUCTURE-005-UIMM-INTEGRATION-PROVISIONAL-RATIFICATION.md` |
| `UFEP-SUB-05` | `UFEP-PRE-02` | SATISFIED | `00-CEP/STAGE-04-S4-12-INFRASTRUCTURE-005-UIMM-INTEGRATION-PROVISIONAL-RATIFICATION.md` |
| `UFEP-SUB-05` | `UFEP-PRE-03` | SATISFIED | `00-MASTER/UCOS-URAT-001/urat.json` |
| `UFEP-SUB-05` | `UFEP-PRE-04` | SATISFIED | `00-MASTER/UCOS-UTCE-001/utce.json` |
| `UFEP-SUB-05` | `UFEP-PRE-05` | SATISFIED | `determinism-evidence/determinism-evidence.json` |

## What each precondition is, and who owns it

| Precondition | Requirement | Scope | Constitutional owner |
|---|---|---|---|
| `UFEP-PRE-01` | closed validation | subject | `00-CEP/CEP-004-CONSTITUTIONAL-VALIDATION-CONSTITUTION.md` |
| `UFEP-PRE-02` | active certification | subject | `00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md` |
| `UFEP-PRE-03` | accepted ratification | subject | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` |
| `UFEP-PRE-04` | rooted-and-closed traceability | repository | `00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md` |
| `UFEP-PRE-05` | proven determinism | repository | `00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md` |
