# H-06 R-3 GATE MODE FIELD CANONICAL DETERMINATION

## 1. Authority

NONE — DETERMINATION ONLY. No policy selected. No implementation authorized.
Baseline: HEAD `1f869865` · branch `integration/recovery-001`

---

## 2. Question

Does an existing canonical field already represent gate mutation mode in *-declaration.json
files? Would introducing `gate_mode` duplicate an existing ownership surface?

---

## 3. Existing Field Inventory

Survey of all 11 *-declaration.json files for mode/gate/execution-related fields:

| Field | Location | Owner | Meaning |
|---|---|---|---|
| `programme.forbidden_write_prefixes` | 8 of 11 declarations | Per-programme | Write-scope boundary — what the programme may NOT write. NOT a mode declaration. |
| `execution` (top-level) | UCL-000001 only | UCL | Run contract: `run_id_inputs`, `writes: []`, `side_effects: none`. Documents UCL's own execution contract, not a gate mode vocabulary field. |
| `cko_model` | UCL, one other | UCL | Canonical Knowledge Object model — structural, not mode-related |
| `relationship_model` | UCL | UCL | Relationship graph model — structural |
| `object_model` | One declaration | Programme-specific | Object model definition — structural |

No declaration contains a field named `gate_mode`, `execution_mode`, `mutation_mode`,
`gate_authority`, or any semantic equivalent representing the mode of the gate entry point.

The `execution` field in UCL is a run-contract descriptor for UCL's internal execution
semantics (determinism inputs, write list, side effects). It is not a vocabulary field
asserting "this gate is OBSERVE/PRODUCER/EXECUTION." Its `writes: []` value is a
programme-specific contract claim, not a canonical mode taxonomy entry.

---

## 4. Ownership Analysis

**No existing field owns the gate-mode semantic.**

`forbidden_write_prefixes` answers: *what paths may this programme not write?*
`execution.run_contract` (UCL only) answers: *what are UCL's determinism inputs and side effects?*
Neither answers: *when this programme's gate entry point is invoked, does it write, and is that write the declared purpose?*

**Duplication risk:** None. `gate_mode` would occupy a unique semantic position not
currently held by any field in any declaration. It would sit alongside
`forbidden_write_prefixes` as a complementary dimension: scope (what is forbidden) +
intent (what the gate path does by design).

**Knowledge Once compliance:** Adding `gate_mode` to the `programme` block of each
*-declaration.json is additive and non-duplicating. The field's values (OBSERVE,
PRODUCER, EXECUTION) reference existing authority surfaces:
- PRODUCER → `generated-artifact-registry.json`
- EXECUTION → `mutation-governance-boundary.json`
- OBSERVE → no external reference required

This creates pointers into existing surfaces, not new surfaces.

---

## 5. Canonical Field Determination

**gate_mode ACCEPTABLE AS DECISION MATERIAL**

No existing field owns this semantic. No duplication risk exists. The placeholder name
`gate_mode` in the H-06 decision record is acceptable as decision material and as the
candidate field name for ratification. The owner may confirm it or substitute an
alternative during ratification — the semantic position is unambiguously vacant.

---

## 6. Governance Impact

**Does not affect freeze.**

R-3 was non-blocking for the H-06 Option A/B decision. It is required before the
declaration schema can be extended. The field name is now confirmed unoccupied.

Updated R-3 status: **RESOLVED — `gate_mode` is acceptable; no conflict with existing fields.**

---

## 7. Remaining Unknowns

None arising from R-3.

| ID | Item | Status |
|---|---|---|
| R-1 | GP-6 collision verification | RESOLVED |
| R-2 | EXECUTION audit trail destination | RESOLVED |
| R-3 | `gate_mode` field name confirmation | RESOLVED |
| R-4 | Grandfathering policy for migration window | OPEN |

Sequence advances to R-4.

---

No implementation authorized.
No governance option selected.
R-3 evidence determination complete.
