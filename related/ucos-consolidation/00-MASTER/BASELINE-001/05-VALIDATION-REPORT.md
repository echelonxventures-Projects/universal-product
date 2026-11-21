# BASELINE-001 · Validation Report

Every dimension is measured. A dimension declared and not measured is reported
`measured = NO` and fails closed: absence of a measurement is never evidence of
compliance.

| Dimension | Obligation | Blocking | Measured | Satisfied | Failures |
|---|---|---|---|---|---|
| `BLN-VAL-01` REGISTER-RESOLUTION | the located baseline register resolves and yields at least one recorded baseline | YES | YES | YES | 0 |
| `BLN-VAL-02` SCHEME-CONFORMANT | every recorded baseline identifier conforms to the ordinal scheme its located owner declares, and the scheme anchor is present in that owner | YES | YES | YES | 0 |
| `BLN-VAL-03` ORDINAL-DENSE | ordinals begin at the located origin ordinal, increase by exactly one, and no identifier or ordinal is duplicated | YES | YES | YES | 0 |
| `BLN-VAL-04` RECORD-RESOLVED | every recorded baseline resolves to a located evidence block | YES | YES | YES | 0 |
| `BLN-VAL-05` SUCCESSION-EXPLICIT | every non-origin baseline records an explicit predecessor, and the origin records none | YES | YES | YES | 0 |
| `BLN-VAL-06` SUCCESSION-CONSISTENT | every explicit predecessor is a recorded baseline and equals the structurally preceding baseline | YES | YES | YES | 0 |
| `BLN-VAL-07` SUCCESSION-ACYCLIC | the succession chain is acyclic, has exactly one origin and exactly one head, and covers every recorded baseline | YES | YES | YES | 0 |
| `BLN-VAL-08` SINGLE-CURRENT | exactly one recorded baseline carries the located current token | YES | YES | YES | 0 |
| `BLN-VAL-09` CURRENT-IS-HEAD | the baseline carrying the current token is the head of the succession chain | YES | YES | YES | 0 |
| `BLN-VAL-10` CITATION-RESOLVED | every baseline-shaped reference in the declared surfaces resolves to a recorded baseline | YES | YES | YES | 0 |
| `BLN-VAL-11` POINTER-RESOLVED | every repository pointer in every baseline evidence block resolves to an existing path | YES | YES | YES | 0 |
| `BLN-VAL-12` CURRENCY-MEASURED | every declared currency claim is read on both sides and carries a decided outcome; an unreadable claim fails closed and a divergence is referred to the claim owner | YES | YES | YES | 0 |
| `BLN-VAL-13` INHERITANCE-BOUND | every declared inheritance rule binds to a located clause whose text is present | YES | YES | YES | 0 |
| `BLN-VAL-14` NON-INHERITANCE-BOUND | every declared non-inheritance rule binds to a located clause whose text is present | YES | YES | YES | 0 |
| `BLN-VAL-15` NO-ELEVATION | no recorded baseline carries the terminal finality token, and every declared elevation prohibition binds to a located clause | YES | YES | YES | 0 |
| `BLN-VAL-16` CEILING-DISCLOSED | the located ceiling clause is present, the recorded vacancy is disposed — open in the projection or discharged by a located closing act — and the register discloses the ceiling token | YES | YES | YES | 0 |
| `BLN-VAL-17` VERSION-SUCCEEDED | every constitutional artifact whose recorded version exceeds the base version resolves to a universal identity whose located ledger records an increment event reaching that version | YES | YES | YES | 0 |
| `BLN-VAL-18` LINEAGE-MEASURED | the constitutional lineage population is measured, every recorded predecessor resolves to a present artifact, and the declared inheritance relationship type is located | YES | YES | YES | 0 |
| `BLN-VAL-19` RELEASE-CORROBORATED | every evolution release the current baseline claims in its chain is recorded in the located evolution register | YES | YES | YES | 0 |
| `BLN-VAL-20` RECORD-IMMUTABLE | this measurement's write set is disjoint from the located record set, so no append-only baseline record can be modified by it | YES | YES | YES | 0 |
| `BLN-VAL-21` CRITERIA-CORROBORATED | every advancement criterion the located scheme owner declares is discovered and corroborated in the current baseline's evidence block | YES | YES | YES | 0 |
| `BLN-VAL-22` SCOPE-BOUND | every declared scope rule binds to a located clause whose text is present | YES | YES | YES | 0 |
| `BLN-VAL-23` STATE-VOCABULARY | every recorded baseline state names at least one token of the located lifecycle-status vocabulary | YES | YES | YES | 0 |
| `BLN-VAL-24` AUTHORITY-DISCLOSED | the located register discloses that it holds no authority, it declares itself append-only, and this measurement discloses the same | YES | YES | YES | 0 |
| `BLN-VAL-25` CONTINUATION-BOUND | the located continuation record resolves and its anchor is present, so the baseline is not read as a claim of completeness beyond its scope | YES | YES | YES | 0 |
| `BLN-VAL-26` CAPABILITY-DISCHARGED | every declared capability is discharged by a measure that ran | YES | YES | YES | 0 |

## Measured failures

None.
