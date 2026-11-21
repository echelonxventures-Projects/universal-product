# 00-MASTER/UEI-000001 — Universal Evolution Intelligence

| Field | Value |
|---|---|
| PROGRAMME | `UEI-000001` |
| DIRECTIVE | `Ω∞-001B` — Universal Evolution Intelligence (UEI Ω∞) |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| GOVERNING INSTRUMENT | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` |
| RESILIENCE OWNER (inherited) | `00-MASTER/UER-000001/uer-resilience.json` — Ω∞-001A |
| EXECUTION OWNER | `00-MASTER/MCP-003-MASTER-EXECUTION.md` |
| RECOVERY OWNER | `00-MASTER/MCP-007-MASTER-RECOVERY.md` |
| AGGREGATE GATE | `00-MASTER/UCCEP-000000/uccep-bindings.json` |
| THIS DIRECTORY | **Operational Memory** — permanently excluded from corpus registration per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |

---

## What Ω∞-001B requires

Fifteen evolution-intelligence capabilities, each bound to the repository home that
already realises it, each owning at least one step of the evolution lifecycle or one
standing loop, each verified by a mandatory validation dimension that discharges an exit
criterion, and each placed under a **located** governing instrument:

| Capability | Mandate |
|---|---|
| `UEI-CAP-01` Universal Observation | observe the platform, corpus and execution substrate |
| `UEI-CAP-02` Universal Learning | retain observation as searchable institutional knowledge |
| `UEI-CAP-03` Universal Optimization | improve without changing meaning or losing traceability |
| `UEI-CAP-04` Universal Recommendation | derive what to do next, evidence-cited and ranked |
| `UEI-CAP-05` Universal Impact Analysis | know the full consequence before the change |
| `UEI-CAP-06` Universal Simulation | run the evolution against a model before the platform |
| `UEI-CAP-07` Universal Improvement Discovery | discover improvements instead of guessing them |
| `UEI-CAP-08` Universal Evolution Planning | order the work by dependency and critical path |
| `UEI-CAP-09` Universal Evolution Execution | execute authorized, checkpointed, reversible, evidenced |
| `UEI-CAP-10` Continuous Improvement | improvement as a standing automated obligation |
| `UEI-CAP-11` Continuous Optimization | proven measures may never silently regress |
| `UEI-CAP-12` Universal Future Prediction | project from located evidence, or declare the absence |
| `UEI-CAP-13` Repository Evolution | evolve the repository with a full traceable record |
| `UEI-CAP-14` Knowledge Evolution | evolve knowledge without loss |
| `UEI-CAP-15` Architecture Evolution | evolve architecture under freeze and amendment |

**Everything governed** is not a slogan here: a capability with no governance obligation
whose instrument resolves against Repository Truth leaves the capability *ungoverned*,
which un-satisfies its validation, which un-meets its exit criterion, which closes the
gate. The clause is enforced by computation.

---

## Layout

| Path | Kind | Notes |
|---|---|---|
| `uei-evolution.json` | **authored DATA** | The only file to edit. Programme, outputs, capabilities, both pipelines, validations, exit criteria, governance, continuation. |
| `uei_engine.py` | **authored code** | Deterministic, stdlib-only. Contains no capability id, no capability name, no mandate, no validation dimension and no deliverable filename as a literal, so extension never requires a code change. |
| `README.md` | authored | This file. |
| `00-UEI-DASHBOARD.md` | **regenerated** | Start here. Coverage, governance, step binding, metrics, gate verdict. |
| `01-UNIVERSAL-EVOLUTION-INTELLIGENCE-CONSTITUTION.md` | **regenerated** | The full contract in one instrument. |
| `02-UNIVERSAL-OBSERVATION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-01` contract and binding. |
| `03-UNIVERSAL-LEARNING-SPECIFICATION.md` | **regenerated** | `UEI-CAP-02` contract and binding. |
| `04-UNIVERSAL-OPTIMIZATION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-03` contract and binding. |
| `05-UNIVERSAL-RECOMMENDATION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-04` contract and binding. |
| `06-UNIVERSAL-IMPACT-ANALYSIS-SPECIFICATION.md` | **regenerated** | `UEI-CAP-05` contract and binding. |
| `07-UNIVERSAL-SIMULATION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-06` contract and binding. |
| `08-UNIVERSAL-IMPROVEMENT-DISCOVERY-SPECIFICATION.md` | **regenerated** | `UEI-CAP-07` contract and binding. |
| `09-UNIVERSAL-EVOLUTION-PLANNING-SPECIFICATION.md` | **regenerated** | `UEI-CAP-08` contract and binding. |
| `10-UNIVERSAL-EVOLUTION-EXECUTION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-09` contract and binding. |
| `11-CONTINUOUS-IMPROVEMENT-SPECIFICATION.md` | **regenerated** | `UEI-CAP-10` contract and binding. |
| `12-CONTINUOUS-OPTIMIZATION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-11` contract and binding. |
| `13-UNIVERSAL-FUTURE-PREDICTION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-12` contract and binding. |
| `14-REPOSITORY-EVOLUTION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-13` contract and binding. |
| `15-KNOWLEDGE-EVOLUTION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-14` contract and binding. |
| `16-ARCHITECTURE-EVOLUTION-SPECIFICATION.md` | **regenerated** | `UEI-CAP-15` contract and binding. |
| `17-EVOLUTION-LIFECYCLE-DETERMINATION.md` | **regenerated** | The fifteen-step lifecycle and the eight standing loops, with binding. |
| `18-GOVERNANCE-BINDING-DETERMINATION.md` | **regenerated** | The proof of *everything governed*. |
| `19-VALIDATION-REPORT.md` | **regenerated** | Mandatory validation computed from Repository Truth. |
| `20-CERTIFICATION-REPORT.md` | **regenerated** | Certification verdict and enforcement route. |
| `21-EVOLUTION-READINESS-REPORT.md` | **regenerated** | Exit criteria and readiness determination. |
| `22-CONTINUATION-PACKAGE.md` | **regenerated** | The mandatory input to the next autonomous session. |
| `uei.json` | **regenerated** | Machine model + seal. |
| `evidence/evolution-evidence-index.json` | **regenerated** | Per-capability resolved/unresolved references and the governance binding state. |

---

## Operation

```
make uei          # regenerate the twenty-three deliverables + machine model + evidence index
make uei-gate     # fail-closed Evolution Intelligence Gate
make uei-self     # the six guards over the programme's own surface
```

Exit semantics of `--gate`:

| Exit | Meaning |
|---|---|
| `0` | gate **OPEN** — every capability covered and governed, every step bound, every validation and exit criterion satisfied |
| `1` | gate **CLOSED** — an uncovered, ungoverned or unsatisfied element is present |
| `2` | **fail-closed abort** — the declaration is unusable, so no verdict may be asserted |

Active enforcement routes, none of them new apparatus:

| Layer | Owner |
|---|---|
| Session start | `.kiro/hooks/uei-000001.json` |
| Continuous integration | `.github/workflows/uei-gate.yml` |
| Developer entry point | `make uei` · `make uei-gate` · `make uei-self` |
| Aggregate gate | `00-MASTER/UCCEP-000000/uccep-bindings.json` — recommended additive binding, authorization required |

---

## The six self-guards

| Guard | Proves |
|---|---|
| `--check-declaration` | Identifiers are unique; the key set of every section is fixed; every deliverable declares a renderer that exists and no renderer is dead; every capability is fully specified, carries a gap field, has a deliverable that specifies it, owns at least one step, and is verified by at least one validation; every validation discharges an exit criterion; every governance obligation names a declared capability and a locatable instrument; every programme reference resolves. |
| `--check-no-enumeration` | No declared identifier, capability name, mandate, validation dimension or deliverable filename appears as a literal in the engine source — so binding a new capability is DATA only. |
| `--check-write-scope` | Every write lands inside `00-MASTER/UEI-000001/`; the forbidden-write prefixes (including `engine/`, `platform/`, `intelligence/`, `00-BOOK/`, `99-FREEZE/`, `adr/`) exist and are never written. |
| `--check-determinism` | Rendering twice from one fixed repository state produces byte-identical output — no timestamp, no wall-clock, no ordering instability. |
| `--check-governance` | No declared capability is left ungoverned, and an obligation whose instrument cannot be located is reported as governing nothing rather than counted as governance. |
| `--check-reuse-before-create` | Every bound home and evidence reference resolves **outside** this programme's own directory — the zero-duplication invariant. A capability authored here rather than bound would trip this guard. |

---

## Extending the contract

Adding a sixteenth capability is an edit to `uei-evolution.json` and nothing else:

1. add the `capabilities` entry, with its `homes` and `evidence` pointing at repository
   paths that already exist and are git-tracked;
2. add an `outputs` entry with `"renderer": "capability"` and `"capability"` set to the
   new id;
3. add a `pipeline_evolution` or `pipeline_continuous` step it owns;
4. add a `validations` entry that verifies it and an `exit_criteria` entry that the
   validation discharges;
5. add a `governance` entry naming it and a located governing instrument.

Omit any of these and `--check-declaration` or `--check-governance` names the omission.
The engine is not touched.

---

*This directory is DERIVED TRUTH. It creates no authority, declares no constitutional
ratification, freezes no architecture, and supersedes no governing instrument. It binds
capability that already exists and duplicates none. Where it conflicts with a higher
frozen or governing instrument, the higher instrument governs.*
