# 00-MASTER/UCCEP-000000 — Universal Continuous Constitutional Evolution Programme

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000000` |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| REGISTERED CHARTER | `02-MASTER/UCCEP-000000-UNIVERSAL-CONTINUOUS-CONSTITUTIONAL-EVOLUTION-PROGRAMME-CHARTER.md` (`UCOS-CON-000064`) |
| THIS DIRECTORY | **Operational Memory** — permanently excluded from corpus registration per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |

The **aggregate** constitutional gate. It creates no constitution, no registry, no evolution model, no meta-model, no validator and no authority. It executes the gates that already exist and are already owned, then records one verdict and one disposition per agreement.

## Layout

| Path | Kind | Notes |
|---|---|---|
| `uccep-bindings.json` | **authored DATA** | The only file to edit. Programmes, gates, checks, principles, invariants, findings, work packages. |
| `uccep_engine.py` | **authored code** | Deterministic, stdlib-only aggregator. Contains no declared identifier, so extension never requires a code change. |
| `README.md` | authored | This file. |
| `00-UCCEP-DASHBOARD.md` | **regenerated** | Start here. Programme + gate state, determination, certification ceiling. |
| `01`–`15-*.md`, `18-*.md` | **regenerated** | The mission outputs, one per declared programme. |
| `16-CONSTITUTIONAL-GATE-REGISTER.md` | **regenerated** | The declared gates → located executables; principles and invariants → owners. |
| `17-ASSIMILATION-FINDINGS-REGISTER.md` | **regenerated** | Every finding, its disposition, its owner, its work package. |
| `uccep.json` | **regenerated** | Machine model + seal. |
| `evidence/*.log` | **regenerated, NOT sealed** | Raw output of each located gate. Excluded from the determinism claim because located owners emit run counters and timestamps. |

Never hand-edit a regenerated file — it is overwritten on the next run.

## Operation

```bash
make uccep         # regenerate (boot + standard tiers)
make uccep-gate    # fail-closed aggregate gate (standard)
make uccep-boot    # fast read-only tier
make uccep-full    # include heavy tier: verify.sh, determinism double-build, registration drift
make uccep-self    # the four guards over UCCEP's own surface
```

Exit: `0` every executed blocking check passed · `1` a blocking check failed · `2` fail-closed abort (declaration unusable, so no verdict may be asserted).

## The four self-guards

| Guard | Proves |
|---|---|
| `--check-declaration` | Every reference resolves in the repository; identifiers are unique; every finding has exactly one valid disposition; **no gate is manual**. |
| `--check-no-enumeration` | The declaration's key set is fixed (no domain/technology field can be smuggled in) **and no declared identifier appears as a literal in the engine source** — so a new programme, gate or check is DATA only. |
| `--check-write-scope` | UCCEP authors nothing outside this directory. |
| `--check-determinism` | Rendering is byte-identical across runs. |

## Two design rules worth knowing

**Absence of evidence is never evidence.** A check above the selected tier is `NOT-EXECUTED`, never `PASS`. A gate with unexecuted checks is `PARTIAL`, never `PASS`. If a declared evidence path is missing from a located owner's report, the check `FAIL`s rather than vacuously passing.

**A gate must be reachable in both directions.** Standing findings set the *certification ceiling*; they do not themselves fail the gate. A gate whose PASS state is unreachable regardless of repository state carries no evidentiary value — that is a defect, not rigour, and it is recorded as a finding rather than imitated.

## Extending

Adding a programme, gate, check, invariant, principle, finding or work package is **one entry in `uccep-bindings.json`**. If you find yourself editing `uccep_engine.py` to admit a new capability, the no-enumeration guard has already failed and the change is wrong.

---

*Operational Memory. Regenerated, never authoritative. Repository Truth remains the sole constitutional authority.*
