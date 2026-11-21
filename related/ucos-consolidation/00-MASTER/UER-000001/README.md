# 00-MASTER/UER-000001 — Universal Execution Resilience

| Field | Value |
|---|---|
| PROGRAMME | `UER-000001` |
| DIRECTIVE | `Ω∞-001A` — Universal Execution Resilience (UER Ω∞) |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| GOVERNING INSTRUMENT | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` |
| RECOVERY OWNER | `00-MASTER/MCP-007-MASTER-RECOVERY.md` |
| EXECUTION OWNER | `00-MASTER/MCP-003-MASTER-EXECUTION.md` |
| AGGREGATE GATE | `00-MASTER/UCCEP-000000/uccep-bindings.json` |
| THIS DIRECTORY | **Operational Memory** — permanently excluded from corpus registration per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |

The executable expression of **execution resilience**. It creates no checkpoint engine, no recovery engine, no journal, no atomic-write framework, no replay validator and no health monitor. Every one of those already exists and is certified. This programme **binds** them into one constitutional contract that every future autonomous programme inherits, and it verifies — from Repository Truth — that each binding resolves.

## What Ω∞-001A requires

Ten constitutional capabilities, each mapped to the repository home that already realises it (Reuse First · Zero Duplication · Zero Regeneration):

1. **Universal Checkpoint Framework** → `engine/runtime/execution/checkpoint.py`, `platform/repository_operations/checkpoint.py`, `00-MASTER/CHECKPOINTS/`
2. **Universal Execution Journal** → `engine/runtime/execution/auditing.py`, `00-BOOK/tools/governance_telemetry.py`, `00-MASTER/MCP-003` / `MCP-006`
3. **Universal Recovery Engine** → `engine/runtime/execution/recovery.py`, `00-MASTER/MCP-007-MASTER-RECOVERY.md`
4. **Universal Atomic Write Framework** → `00-BOOK/tools/governance_telemetry.py` (`_atomic_write`), `engine/runtime/execution/persistence.py`
5. **Universal Resume Framework** → `engine/runtime/execution/continuation.py`, `platform/repository_operations/engine.py`
6. **Universal Work Package Ledger** → `00-MASTER/MCP-003-MASTER-EXECUTION.md`, `00-MASTER/UCDA-000001/05-WORK-PACKAGE-REGISTER.md`
7. **Universal Continuation Package** → `00-MASTER/MCP-002-MASTER-STATE.md`, `00-MASTER/CHECKPOINTS/`
8. **Universal Replay Protection** → `engine/runtime/execution/replay.py` + `replay_validation.py`, `.github/workflows/determinism.yml`, `00-BOOK/tools/register.sh`
9. **Universal Repository Safety** → `00-MASTER/MCP-007` §01, `00-MASTER/UCCEP-000000/uccep-bindings.json`, `verify.sh`
10. **Universal Execution Health Intelligence** → `engine/runtime/execution/health.py` + `diagnostics.py` + `metrics.py` + `monitoring.py`, `00-MASTER/MCP-005-MASTER-DASHBOARD.md`

Plus the required **execution pipeline**, the **interruption-recovery pipeline**, and the eight **mandatory validation** dimensions — all bound to those ten capabilities.

## Layout

| Path | Kind | Notes |
|---|---|---|
| `uer-resilience.json` | **authored DATA** | The only file to edit. Programme, outputs, capabilities, pipelines, validations, exit criteria, continuation. |
| `uer_engine.py` | **authored code** | Deterministic, stdlib-only. Contains no capability id, no mandate and no validation dimension, so extension never requires a code change. |
| `README.md` | authored | This file. |
| `00-UER-DASHBOARD.md` | **regenerated** | Start here. Coverage, pipeline binding, validation, health, gate verdict. |
| `01-UNIVERSAL-EXECUTION-RESILIENCE-CONSTITUTION.md` | **regenerated** | The full contract: capabilities + pipelines + validations bound to existing homes. |
| `02-UNIVERSAL-CHECKPOINT-POLICY.md` | **regenerated** | Checkpoint capability, contract and binding. |
| `03-UNIVERSAL-RECOVERY-POLICY.md` | **regenerated** | Recovery capability, contract and binding. |
| `04-UNIVERSAL-ATOMIC-WRITE-SPECIFICATION.md` | **regenerated** | Atomic-write flow and binding. |
| `05-UNIVERSAL-EXECUTION-JOURNAL-SPECIFICATION.md` | **regenerated** | Execution journal and binding. |
| `06-UNIVERSAL-WORK-PACKAGE-LEDGER-SPECIFICATION.md` | **regenerated** | Work-package ledger and binding. |
| `07-UNIVERSAL-CONTINUATION-PACKAGE-SPECIFICATION.md` | **regenerated** | Continuation package and binding. |
| `08-UNIVERSAL-REPLAY-PROTECTION-SPECIFICATION.md` | **regenerated** | Replay protection and binding. |
| `09-UNIVERSAL-EXECUTION-HEALTH-SPECIFICATION.md` | **regenerated** | Execution-health intelligence and binding. |
| `10-VALIDATION-REPORT.md` | **regenerated** | Mandatory validation computed from Repository Truth. |
| `11-CERTIFICATION-REPORT.md` | **regenerated** | Certification verdict and enforcement route. |
| `12-EXECUTION-READINESS-REPORT.md` | **regenerated** | Exit criteria and readiness determination. |
| `13-CONTINUATION-PACKAGE.md` | **regenerated** | The mandatory input to the next autonomous session. |
| `uer.json` | **regenerated** | Machine model + seal. |
| `evidence/resilience-evidence-index.json` | **regenerated** | Per-capability resolved and unresolved home/evidence references. |

Never hand-edit a regenerated file — it is overwritten on the next run.

## Operation

```bash
make uer         # regenerate the determinations
make uer-gate    # fail-closed Execution Resilience Gate
make uer-self    # the four guards over UER's own surface
```

Exit: `0` gate OPEN · `1` gate CLOSED (a capability/validation/exit criterion is unsatisfied) · `2` fail-closed abort (declaration unusable, so no verdict may be asserted).

The gate also runs at session start via `.kiro/hooks/uer-000001.json` and in `.github/workflows/uer-gate.yml`. No new gate apparatus, pipeline, scheduler or daemon was created.

## The four self-guards

| Guard | Proves |
|---|---|
| `--check-declaration` | Identifiers are unique; the key set of every section is fixed; there are exactly fourteen deliverables; every capability is fully specified and carries a gap field; every output binds a declared capability; every pipeline step is owned by a declared capability; every validation is verified by a declared capability; every exit criterion is satisfied by a declared validation; every programme reference resolves in the repository. |
| `--check-no-enumeration` | No declared capability id, mandate or validation dimension appears as a literal in the engine source — so binding a new capability or proven gap is DATA only. |
| `--check-write-scope` | Every write lands inside this directory. The forbidden prefixes include the frozen corpus, the engine, the platform, the registration authority, the constitutional zones and `adr/` — this programme never writes a constitutional artefact, engine module or platform module. Every declared prefix must itself exist in tracked Repository Truth, so the guard is provable from a clean checkout. |
| `--check-determinism` | Two renders of one model are byte-identical. No timestamp is emitted anywhere — the same determinism guarantee the programme certifies for the platform it binds. |

## Bidirectionality of the verdict

A gate whose verdict cannot be reached in both directions carries no evidentiary value. This gate reaches both: with the declaration as committed it exits `0` with the gate OPEN; with any capability whose home or evidence does not resolve (or an open gap), that capability is reported by name as NOT COVERED and the gate exits `1`.

## Safe autonomous boundaries (Ω∞-001A)

This programme **improves execution behaviour, traceability, governance and repository resilience** by binding existing capability. It **does not** redesign unrelated architecture, rewrite constitutional artefacts, delete canonical capabilities, perform destructive refactoring, declare an architecture freeze, declare constitutional ratification, or deploy production changes. AUTHORITY = NONE (DERIVED TRUTH).

---

*AUTHORITY = NONE (DERIVED TRUTH). This directory creates no authority, allocates no identity, and supersedes no governing instrument. Where it conflicts with a higher frozen or governing instrument, the higher instrument governs.*
