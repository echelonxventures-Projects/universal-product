# UCOS-URAT-001 · State Machine, Preconditions and Registry Rules

## Ratification states (projected from the located clause)

| State | Located in clause | Admits to freeze lifecycle | Terminal |
|---|---|---|---|
| `NOT_ELIGIBLE` | YES | no | no |
| `ELIGIBLE` | YES | no | no |
| `DELIBERATING` | YES | no | no |
| `ACCEPTED` | YES | YES | no |
| `PROVISIONAL` | YES | YES | no |
| `DEFERRED` | YES | no | no |
| `REJECTED` | YES | no | no |
| `APPEALING` | YES | no | no |
| `FINALIZED` | YES | YES | YES |

## Legal transitions

A transition not listed here IS PROHIBITED. This engine performs none of them: it
records only what a located act determined.

| From | To | Performable in corpus |
|---|---|---|
| `NOT_ELIGIBLE` | `ELIGIBLE` | YES |
| `ELIGIBLE` | `DELIBERATING` | YES |
| `DELIBERATING` | `ACCEPTED` | YES |
| `DELIBERATING` | `PROVISIONAL` | YES |
| `DELIBERATING` | `DEFERRED` | YES |
| `DELIBERATING` | `REJECTED` | YES |
| `ACCEPTED` | `FINALIZED` | **NO — out-of-corpus finality authority** |
| `PROVISIONAL` | `FINALIZED` | **NO — out-of-corpus finality authority** |
| `PROVISIONAL` | `REJECTED` | YES |
| `DEFERRED` | `ELIGIBLE` | YES |
| `REJECTED` | `APPEALING` | YES |
| `APPEALING` | `DELIBERATING` | YES |
| `APPEALING` | `REJECTED` | YES |

## Preconditions (CEP-006 V.1)

| Precondition | Obligation | Owner | Owner resolves | Named in clause |
|---|---|---|---|---|
| `URAT-PRE-01` | closed validation | `00-CEP/CEP-004-CONSTITUTIONAL-VALIDATION-CONSTITUTION.md` | YES | YES |
| `URAT-PRE-02` | active certification | `00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md` | YES | YES |
| `URAT-PRE-03` | rooted-and-closed traceability | `00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md` | YES | YES |
| `URAT-PRE-04` | preservation of frozen work | `00-CEP/CEP-000-CONSTITUTIONAL-ENGINEERING-CHARTER.md` | YES | YES |

## Registry rules (CEP-006 Article XVI)

| Rule | Obligation | Located in | Bound |
|---|---|---|---|
| `URAT-RULE-01` | uniqueness — every accepted artifact holds exactly one canonical record, and no duplicate ratification authority is admitted | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `URAT-RULE-02` | append-only in lineage, content-addressed, and reconciled against repository truth at boot | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `URAT-RULE-03` | a ratification absent from the registry is deemed non-existent and reliance upon it is prohibited | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `URAT-RULE-04` | the registry is operational memory and holds no authority over constitutional content | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `URAT-RULE-05` | in-corpus ratification confers only PROVISIONAL acceptance pending out-of-corpus finality | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `URAT-RULE-06` | ratification authority is never self-conferred by execution authority | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
