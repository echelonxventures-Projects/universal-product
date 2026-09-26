# Validation Report

> Every dimension is measured from Repository Truth. Seal `7be7a32b3961286d21b0d3c7402671e2c98a4793360690b39b615248bf8c86f7`.

| ID | Dimension | Result | Class | Measured | Failures |
|---|---|---|---|---|---|
| `UAIE-VAL-01` | Every declared faculty home resolves in Repository Truth | **PASS** | blocking | yes | — |
| `UAIE-VAL-02` | Every declared symbol resolves in one of its faculty's homes | **PASS** | blocking | yes | — |
| `UAIE-VAL-03` | Every faculty is realised by at least one registered analysis | **PASS** | blocking | yes | — |
| `UAIE-VAL-04` | Reuse before create | **PASS** | blocking | yes | — |
| `UAIE-VAL-05` | Exactly one disposition per faculty from the declared set | **PASS** | blocking | yes | — |
| `UAIE-VAL-06` | No faculty is unbound | **PASS** | blocking | yes | — |
| `UAIE-VAL-07` | No two faculties claim an identical home set | **PASS** | blocking | yes | — |
| `UAIE-VAL-08` | Ownership is single and located | **PASS** | blocking | yes | — |
| `UAIE-VAL-09` | The faculty dependency relation is closed and acyclic | **PASS** | blocking | yes | — |
| `UAIE-VAL-10` | Every declared register of the plane resolves and is readable in its declared form | **PASS** | blocking | yes | — |
| `UAIE-VAL-11` | Register-plane consistency across registers | **PASS** | blocking | yes | — |
| `UAIE-VAL-12` | Every declared catalogue identifier exists in the canonical capability catalogue | **PASS** | blocking | yes | — |
| `UAIE-VAL-13` | Every ontology anchor exists in its declared ontology register | **PASS** | blocking | yes | — |
| `UAIE-VAL-14` | Every contributed analysis is registered in the located analysis registry and duplicates no existing analysis | **PASS** | blocking | yes | — |
| `UAIE-VAL-15` | Every recorded gap states why it is not closed | **PASS** | blocking | yes | — |
| `UAIE-VAL-16` | No parallel authority in the meta-constitutional plane | **PASS** | blocking | yes | — |
| `UAIE-VAL-17` | Comprehension coverage over the register plane | **PASS** | blocking | yes | — |
| `UAIE-VAL-18` | Every Constitutional Evolution Contract obligation binds to a located owner, a named gate and resolving evidence | **PASS** | blocking | yes | — |
| `UAIE-VAL-19` | The declared change classification, release state and baseline are members of the registers that own them | **PASS** | blocking | yes | — |

**Measured:** 19/19 — a declared dimension with no measurement fails closed, because absence of evidence is never evidence.

**Blocking failures:** 0

## Obligations

| ID | Obligation |
|---|---|
| `UAIE-VAL-01` | no faculty may be bound to a path that does not exist |
| `UAIE-VAL-02` | a binding may not name a class or function that does not exist, and resolution is by parsing, never by importing the measured module |
| `UAIE-VAL-03` | each faculty cites one or more analysis identifiers and each resolves in the located analysis registry with a home that exists |
| `UAIE-VAL-04` | no faculty may be bound to a home inside this programme's own directory, because that would be this programme realising the faculty rather than reusing it |
| `UAIE-VAL-05` | totality and closure over the disposition vocabulary; CREATE is not a member of it |
| `UAIE-VAL-06` | every faculty names at least one home and exactly one canonical owner that resolves |
| `UAIE-VAL-07` | an identical binding for two faculties would be duplicate authority over one home |
| `UAIE-VAL-08` | each faculty's canonical owner resolves on disk and is not claimed as canonical owner by any other faculty |
| `UAIE-VAL-09` | every declared dependency names a declared faculty, no faculty depends on itself, and the relation admits a total order |
| `UAIE-VAL-10` | a register declared as structured data must parse; a register that cannot be read cannot be reasoned over |
| `UAIE-VAL-11` | every path referenced by every probed register resolves on disk, so no register may point at an artifact another register has lost |
| `UAIE-VAL-12` | a faculty may not cite a capability record that is absent, and a faculty citing a record whose replacement is prohibited must resolve at least one of its homes |
| `UAIE-VAL-13` | ontology integration is a binding to an element that already exists, so an anchor that is absent from the register closes the gate |
| `UAIE-VAL-14` | an analysis this programme adds must appear in the analysis registry owned by this programme, and its name must not already be registered to another owner |
| `UAIE-VAL-15` | a declared gap must carry a non-empty justification, so an absence is disclosed rather than hidden |
| `UAIE-VAL-16` | the declared admission determination must match Repository Truth: a programme declared substantive and not admitted to the meta-constitutional registry must in fact be absent from that registry's artifacts and namespace tokens |
| `UAIE-VAL-17` | every declared register is claimed by at least one faculty and every faculty register reference resolves to a declared register, so no part of the plane is unreasoned-over and no faculty reasons over a register that is not declared |
| `UAIE-VAL-18` | each of the ten obligations names a non-empty owner, gate and discharge, declares a status from the declared set, and every owner path and evidence path it cites resolves on disk — the verdict of each obligation remains with its own located gate and is never restated here |
| `UAIE-VAL-19` | the change class label appears in the located evolution register, its release token and the declared release state appear in the located release register, and the declared baseline identifier appears in the located baseline register, so none of the three may drift from the vocabulary that owns it |
