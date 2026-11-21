# UCOS-UCAF-001 · Scope and Resolution

## Scope rules (bound to located clauses)

| Rule | Obligation | Located in | Bound |
|---|---|---|---|
| `UCAF-SCOPE-01` | authority must be explicit, traceable, auditable, governed, revocable and bounded; no action without authority; no authority beyond jurisdiction | `01-WORKING/AUTHORITY-REGISTER.md` | YES |
| `UCAF-SCOPE-02` | sovereignty cannot be assumed, fabricated or bypassed; delegation does not transfer sovereignty | `01-WORKING/AUTHORITY-REGISTER.md` | YES |
| `UCAF-SCOPE-03` | governance shall never self-elevate and shall never create a governance power not established by its instrument | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-04` | governance shall not assert, simulate or substitute for constitutional authority | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-05` | delegation flows only downward, is bounded, recorded and revocable, and never exceeds the delegator's own power | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-06` | ratification authority shall never be self-conferred by execution authority and acts only upon an authorization | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-07` | where finality requires an authority outside the corpus, that authority is superior for finality and in-corpus ratification confers only PROVISIONAL acceptance | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-08` | resolution reaching a vacant tier shall not skip the tier and shall not promote a lower instrument into it | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-09` | a steward shall not confer authority, decide constitutional content, or exceed delegated bounds | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-10` | freeze authority shall never be self-conferred by execution authority and preserves only | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-11` | execution authority acts only within a stage that is in the EXECUTING condition, performs exactly the single next authorized action, and writes only to the declared write area of the active stage | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-12` | execution authority shall not govern, ratify, decide constitutional content, or exercise a power reserved to a higher tier | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-13` | execution authority never self-authorizes an action and acts only upon an authorization granted under the authorization article | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-14` | an authorization shall never be self-conferred by execution authority and shall never bypass a gate, a governance control or a preservation rule | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-15` | every tier is subordinate to every tier above it except where an orthogonality is declared, and rank is never decided by recency, size or prominence | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-16` | the tier set is open: a new tier is admitted by declaring its position relative to existing tiers, and admission shall not renumber an existing tier | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `UCAF-SCOPE-17` | the lattice shall be consistent with, and shall not amend, the four-tier Program authority order already declared by the charter | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |

## Competence resolution

Each answer is READ from the located instrument named as owner. An absent clause is
reported UNRESOLVED and is never answered by default.

| Question | Asked | Located in | In corpus | Answers | Outcome |
|---|---|---|---|---|---|
| `UCAF-R-01` | Which authority is the root of the authority derivation chain? | `01-WORKING/AUTHORITY-REGISTER.md` | YES | `AUTH-13`, `AUTH-03`, `AUTH-06` | ANSWERED |
| `UCAF-R-02` | Which authority is competent to perform ratification? | `01-WORKING/AUTHORITY-REGISTER.md` | YES | `AUTH-14`, `GOV-03`, `AUTH-13`, `AUTH-03`, `AUTH-04`, `GOV-11` | ANSWERED |
| `UCAF-R-03` | By what procedure is a ratification valid and audited? | `01-WORKING/AUTHORITY-REGISTER.md` | YES | `GOV-11`, `AUTH-14`, `AUTH-13`, `GOV-04` | ANSWERED |
| `UCAF-R-04` | By what procedure may the constitutional order be amended? | `01-WORKING/AUTHORITY-REGISTER.md` | YES | `GOV-12` | ANSWERED |
| `UCAF-R-05` | Which authority is superior for constitutional finality? | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | NO (out-of-corpus superior) | — | ANSWERED |
| `UCAF-R-06` | Which authority may confer PROVISIONAL acceptance, and what is the ceiling of an in-corpus determination? | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-07` | Which ratification states admit an artifact to the freeze lifecycle? | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-08` | Which authority allocates canonical ownership of a concern? | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-09` | Which authority may revoke a delegation, and when does the revocation take effect? | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-10` | Which authority resolves a contested authority over the same artifact? | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-11` | Was the exogenous constituent act performed, and are its constituent capabilities discharged? | `02-MASTER/UCOS-RAT-001-REPOSITORY-RATIFICATION-DETERMINATION.md` | NO (out-of-corpus superior) | — | ANSWERED |
| `UCAF-R-12` | Is the located authority derivation chain rooted? | `01-WORKING/AUTHORITY-REGISTER.md` | YES | `AUTH-13`, `AUTH-14`, `GOV-11`, `GOV-12`, `AUTH-03` | ANSWERED |
| `UCAF-R-13` | Which authority may authorize an execution, and may execution authority confer its own authorization? | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-14` | Upon what does an execution unit enter AUTHORIZED, and what is the consequence of a denied authorization? | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-15` | In which tier does execution authority vest, and which instrument vests it? | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-16` | Which authority governs the ordering of authority tiers, and how many precedence lattices are there? | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES | — | ANSWERED |
| `UCAF-R-17` | By what procedure is a new authority tier admitted, and may admission renumber an existing tier? | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES | — | ANSWERED |
