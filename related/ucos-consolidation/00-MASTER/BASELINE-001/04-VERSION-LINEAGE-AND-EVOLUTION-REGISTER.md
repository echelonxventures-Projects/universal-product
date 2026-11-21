# BASELINE-001 · Version Progression, Lineage and Evolution

## Version progression

The constitutional programme requires that any change occur only through the amendment
model and increment the version. Nothing measured that the increment was RECORDED.
Three located registers are read against each other: the constitutional register that
records the version in force, the artifact register that maps a path to its universal
identity, and the change ledger that records the increment event.

| Artifact | Recorded version | Universal identity | Increment recorded |
|---|---|---|---|
| `CMG-000001` | 1.3 | `UCOS-CON-000050` | YES |
| `CEP-001` | 1.1 | `UCOS-CON-000033` | YES |
| `CEP-002` | 1.2 | `UCOS-CON-000034` | YES |
| `CEP-009` | 1.1 | `UCOS-CON-000041` | YES |

## Configuration in force at the current baseline

- `CEP-001 1.1`
- `CEP-002 1.2`
- `CEP-009 1.1`
- `CMG-000001 1.3`

## Constitutional lineage

The meta-constitution requires every lineage predecessor to resolve to a present
artifact, and the located validator checks exactly that. The invariant is satisfiable
vacuously when no artifact records a predecessor, and a vacuously satisfied invariant
is indistinguishable from an enforced one unless the population is measured. This
measurement reports the population. It does not populate the field.

| Property | Value |
|---|---|
| Owner | `00-CMG/CMG-REGISTRY.json` |
| Registered artifacts | 45 |
| Artifacts recording a predecessor | 0 |
| Inheritance relationship type located | YES |
| Invariant vacuously satisfied | **YES** |
| Edges | — |

## Evolution chain

Owner: `00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md`. The releases the current baseline claims in
its chain must be recorded in the located evolution register. Nothing about the
release scheme, the release states or the release ordering is asserted here, because
none of it belongs to this owner.

| Release claimed by the current baseline | Recorded in the located register |
|---|---|
| `UCOS-EVO-001-FFI` | YES |
| `UCOS-EVO-001-UCEF` | YES |
| `UCOS-EVO-001-W01` | YES |

## Advancement criteria

Discovered from `00-MASTER/RELEASE-001/RELEASE-LIFECYCLE.md`: **5**.
Each criterion is read from the located scheme owner and corroborated in the current
baseline's own evidence block. A criterion the owner adds is measured on the next run.

| Criterion | Corroborated in the current baseline |
|---|---|
| A significant capability milestone is reached | YES |
| All blocking gates pass | YES |
| verify.sh GREEN | YES |
| UCCEP CERTIFIED-PROVISIONAL (or higher) with blocking=none | YES |
| Evolution version history records the complete chain from prior baseline | YES |

## Continuation

A baseline is complete for the scope it certifies and is never a claim of completeness
beyond it.

| Continuation | Owner | Bound |
|---|---|---|
| `BLN-CON-01` | `00-MASTER/BASELINE-001/REMAINING-ROADMAP-CLASSIFICATION.md` | YES |
