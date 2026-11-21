# UCOS-UCAF-001 · Admission and Disposition

| Field | Value |
|---|---|
| CLASSIFICATION | SUBSTANTIVE |
| META REGISTRY | `00-CMG/CMG-REGISTRY.json` |
| ADMITTED TO THE META REGISTRY | no — by design |
| BASIS | 00-CMG/CMG-000001 ARTICLE LXXVI.2(b) forbids admitting a substantive concept into the meta-constitutional layer, so this programme claims no namespace token there (ARTICLE XLI.5) and is absent from the meta registry by design. |

Exactly one disposition is recorded for every concept reached. A disposition is
drawn from the totality rule of the located instrument, never invented here, and
CREATE is a validation failure: a concept whose owner is named cannot be created a
second time without manufacturing the parallel authority that instrument forbids.

## Concepts reached

| Concept | Statement | Disposition | Canonical owner | Owner resolves | Disposition located | Refusal recorded |
|---|---|---|---|---|---|---|
| `UCAF-AD-01` | execution authority — which authority may authorize an execution, and under what authorization | REUSE | `00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md` | YES | YES | YES |
| `UCAF-AD-02` | constitutional tier lattice — the ordered tiers of authority and their occupancy | REUSE | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` | YES | YES | YES |
| `UCAF-AD-03` | tier vesting — which occupant each authority tier of the Program vests in | REUSE | `00-CEP/CEP-000-CONSTITUTIONAL-ENGINEERING-CHARTER.md` | YES | YES | YES |
| `UCAF-AD-04` | gate execution tiers — the boot, standard and full tiers by which verification work is scheduled | REUSE | `00-MASTER/UCCEP-000000/uccep-bindings.json` | YES | YES | YES |
| `UCAF-AD-05` | authority realization — the binding between a located authority and the executable plane that exercises it | EXTEND | `00-MASTER/UCOS-UCAF-001/ucaf-authority.json` | YES | YES | YES |
| `UCAF-AD-06` | tier projection fidelity — agreement between the canonical lattice and the machine projection every gate reads | EXTEND | `00-MASTER/UCOS-UCAF-001/ucaf-authority.json` | YES | YES | YES |

## Alternatives rejected

- CREATE a Universal Execution Authority programme — refused: 00-CEP/CEP-003 vests execution authority and 00-CMG/CMG-REGISTRY.json already delegates execution-operation to it, so discovery yields an owner and 00-CMG/CMG-000001 LXXVII.2(a) requires REUSE.
- CREATE a Tier Governance programme — refused: 00-CMG/CMG-000001 ARTICLE XVI legislates exactly one precedence lattice and ARTICLE XVI.8 already governs tier admission; a second governor of tiers would breach CMG-INV-02.
- Admit either concept into the meta-constitutional registry — refused: both are substantive and 00-CMG/CMG-000001 LXXVI.2(b) forbids admitting a substantive concept there.
- Unify gate execution tiers with the constitutional precedence lattice — refused: they are distinct owned concepts sharing a word, and unifying them by reinterpretation is what 00-CMG/CMG-000001 LXXVI.6 forbids.
- Close the recorded vacancy by reading the charter's vesting of the tier as its occupant — refused: 00-CMG/CMG-000001 XVII.4 forbids promoting a lower instrument into a vacant tier and LXXXI.5 voids any reading that does, so corroboration is measured only for tiers the projection already reports located.
