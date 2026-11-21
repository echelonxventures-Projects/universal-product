# BASELINE-001 · Inheritance and Non-Inheritance

What a successor inherits, and what it never inherits, are both constitutional. Each
rule below binds to the located clause that states it, and the clause text is verified
present in its owner. A rule whose anchor is absent is a binding failure, not a silent
pass. No rule is restated here: only located, and bound.

## Inheritance rules

| Rule | Obligation | Located in | Bound |
|---|---|---|---|
| `BLN-INH-01` | inheritance is the adoption by a subordinate artifact of the obligations and prohibitions of a superior, without restatement | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-02` | inheritance is by reference only; restating an inherited obligation is duplication and violates Knowledge Once | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-03` | an inheritor shall not weaken an inherited obligation, remove an inherited prohibition or broaden an inherited scope | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-04` | inheritance shall be explicit; implicit inheritance from a containing programme, phase or directory is prohibited | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-05` | an inherited obligation shall be re-evaluated when the superior is amended; inheritance is live, not a snapshot | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-06` | a superseded version shall be retained, never deleted, and shall be reachable from its successor by an explicit lineage link | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-07` | version lineage shall be acyclic and append-only | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-INH-08` | a baseline is a pure function of the artifact, its bound evidence references and its ratification record, computed deterministically | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |
| `BLN-INH-09` | supersession is the sole mechanism by which a frozen artifact is evolved | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |
| `BLN-INH-10` | every frozen artifact carries an explicit version and an explicit lineage to its predecessor where one exists | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |
| `BLN-INH-11` | every amendment establishes a lineage link from predecessor to successor, and lineage is append-only | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` | YES |
| `BLN-INH-12` | every version in a lineage remains individually reproducible and discoverable, enabling evolution without historical destruction | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` | YES |

## Non-inheritance rules

Standing, ratification, finality and authority are never inherited. This was the
wholly unmeasured half of the concept.

| Rule | Prohibition | Located in | Bound |
|---|---|---|---|
| `BLN-NIN-01` | prior ratification shall not carry over to an amended artifact; every amended artifact is required to be re-validated and re-ratified | `00-CEP/CEP-000-CONSTITUTIONAL-ENGINEERING-CHARTER.md` | YES |
| `BLN-NIN-02` | no successor inherits the terminal finality state; a successor to a provisional artifact is itself provisional until independently determined | `00-CEP/STAGE-02-S2-08-FINALITY-BINDING-ARCHITECTURE.md` | YES |
| `BLN-NIN-03` | an inheritor shall not inherit authority; authority is allocated, not inherited | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-NIN-04` | a successor shall undergo validation, certification and ratification before it is eligible for freeze; freeze shall not bypass these | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |
| `BLN-NIN-05` | a successor shall not reuse, overwrite or inherit the identity of its predecessor | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` | YES |
| `BLN-NIN-06` | eligibility shall be re-determined after any amendment or after any lapse of validation, certification or ratification | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |

## Scope

| Rule | Bound of a baseline | Located in | Bound |
|---|---|---|---|
| `BLN-SCP-01` | certification closes scope and never closes evolution; a certified construct remains eligible for append-only successors | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001-INFINITE-EVOLUTION-UNIVERSAL-IDENTITY-AND-UNBOUNDED-EXPANSION-CONSTITUTION.md` | YES |
| `BLN-SCP-02` | the last member of any ordered set shall not be read as the maximum possible member, so the head of the baseline chain is not a ceiling on it | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001-INFINITE-EVOLUTION-UNIVERSAL-IDENTITY-AND-UNBOUNDED-EXPANSION-CONSTITUTION.md` | YES |
| `BLN-SCP-03` | admission is append-only; no admitted member is renumbered, renamed, reclassified or withdrawn | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES |
| `BLN-SCP-04` | the constitutional foundation shall not require redesign for the introduction of any future construct | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` | YES |
| `BLN-SCP-05` | a baseline shall be recomputable and shall yield a byte-identical result on recomputation | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |

## Elevation prohibitions and the ratification ceiling

The one thing a baseline measurement must never do is raise the standing of what it
measures. No recorded baseline carries the terminal finality token, and this
measurement confers no state on any baseline.

| Prohibition | Rule | Located in | Bound |
|---|---|---|---|
| `BLN-ELV-01` | freeze preserves only and shall never modify, validate, certify or ratify any artifact | `00-CEP/CEP-007-CONSTITUTIONAL-FREEZE-CONSTITUTION.md` | YES |
| `BLN-ELV-02` | ratification authority shall never be self-conferred by execution authority and acts only upon an authorization | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` | YES |
| `BLN-ELV-03` | a derived-truth record asserts nothing and is always reconciled against repository reality | `00-CEP/CEP-000-CONSTITUTIONAL-ENGINEERING-CHARTER.md` | YES |

| Ceiling | Value |
|---|---|
| Owner | `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` |
| Clause bound | YES |
| Disclosure token | `CERTIFIED-PROVISIONAL` |
| Terminal token (prohibited in a record) | `FINALIZED` |
| Vacancies located | 0 |
| Vacancies discharged | 1 |
| Baselines elevated by this measurement | **none** |
