# Validation Report

> Every dimension is measured from Repository Truth. Seal `ac285c5a1d44a04dfecfc67e0f70a25126347201ba584e748b3b506970bc7326`.

| ID | Dimension | Result | Class | Measured | Failures |
|---|---|---|---|---|---|
| `UAEP-VAL-01` | Every declared home resolves in Repository Truth | **PASS** | blocking | yes | — |
| `UAEP-VAL-02` | Every declared catalogue id exists in the canonical capability catalogue | **PASS** | blocking | yes | — |
| `UAEP-VAL-03` | Every declared symbol resolves in one of its capability's homes | **PASS** | blocking | yes | — |
| `UAEP-VAL-04` | Reuse before create | **PASS** | blocking | yes | — |
| `UAEP-VAL-05` | Exactly one disposition per capability from the declared set | **PASS** | blocking | yes | — |
| `UAEP-VAL-06` | No capability is unbound | **PASS** | blocking | yes | — |
| `UAEP-VAL-07` | Every declared vocabulary is open | **PASS** | blocking | yes | — |
| `UAEP-VAL-08` | Every declared pipeline type is registered in the seed vocabulary | **PASS** | blocking | yes | — |
| `UAEP-VAL-09` | No two capabilities claim an identical home set | **PASS** | blocking | yes | — |
| `UAEP-VAL-10` | No capability declares replacement of a protected owner | **PASS** | blocking | yes | — |
| `UAEP-VAL-11` | Every recorded gap names the reason it is not closed | **PASS** | blocking | yes | — |

**Measured:** 11/11 — a declared dimension with no measurement fails closed, because absence of evidence is never evidence.

**Blocking failures:** 0
