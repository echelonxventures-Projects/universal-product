# 00-MASTER/UCDA-000001 — Constitutional Decision Assimilation

| Field | Value |
|---|---|
| PROGRAMME | `UCDA-000001` |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| GOVERNING INSTRUMENT | `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md` **Article 28** (added by `CEP-002-AMD-002`) |
| AGGREGATE GATE BINDING | `00-MASTER/UCCEP-000000/uccep-bindings.json` → `G-14` · `CK-DECISION-EVIDENCE` · `PROGRAM-000016` · `PR-21` · `IV-17` |
| THIS DIRECTORY | **Operational Memory** — permanently excluded from corpus registration per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |

The executable expression of the **Implementation Evidence Gate**. It creates no constitution, no decision register, no registry and no authority. The law is CEP-002 Article 28; the decisions live in the located registers that already exist; this directory carries only the **disposition overlay** over them and the engine that verifies it.

## What Article 28 requires

1. **No constitutionally agreed decision may remain only in conversation history** (28.4–28.7). Repository Truth is the sole admissible evidence that a decision exists and carries the disposition claimed for it.
2. A **mandatory nine-stage lifecycle** (28.8–28.12): DISCUSSION → CONSTITUTIONAL AGREEMENT → DECISION REGISTRATION → REPOSITORY MAPPING → IMPLEMENTATION → VALIDATION → CERTIFICATION → REPOSITORY TRUTH UPDATE → CLOSURE.
3. A **closed five-member disposition set** (28.13), exactly one per decision: IMPLEMENTED · REPRESENTED BY AN EXISTING CANONICAL CAPABILITY · REGISTERED AS AN IMPLEMENTATION WORK PACKAGE · REJECTED WITH CONSTITUTIONAL JUSTIFICATION · SUPERSEDED.
4. The **Implementation Evidence Gate** (28.17–28.21): no subsequent implementation programme, architectural work, or successor stage is authorized while any previously ratified or recorded decision is undispositioned.

## Located decision registers (nothing originates here)

`02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-DECISION-REGISTER.md` · `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-ADJUDICATION-RECORD.md` · `adr/` · `knowledge/decisions.json` · `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` · `00-MASTER/MCP-004-MASTER-DECISIONS.md`

Every entry in the overlay names the register it was recorded in, and the engine requires that reference to resolve. A second decision register is prohibited by 28.3.

## Layout

| Path | Kind | Notes |
|---|---|---|
| `ucda-decisions.json` | **authored DATA** | The only file to edit. Outputs, lifecycle, dispositions, work packages, decisions. |
| `ucda_engine.py` | **authored code** | Deterministic, stdlib-only. Contains no stage name, no disposition name and no decision identifier, so extension never requires a code change. |
| `README.md` | authored | This file. |
| `00-UCDA-DASHBOARD.md` | **regenerated** | Start here. Lifecycle occupancy, disposition distribution, determination. |
| `01-CONSTITUTIONAL-DECISION-REGISTER.md` | **regenerated** | Every decision, its register, its stage, its disposition, its located evidence. |
| `02-DECISION-LIFECYCLE-DETERMINATION.md` | **regenerated** | The lifecycle, its legal transitions, and verified structural properties. |
| `03-DISPOSITION-REGISTER.md` | **regenerated** | The closed disposition set, each member's evidence obligation, and the distribution. |
| `04-IMPLEMENTATION-EVIDENCE-GATE-DETERMINATION.md` | **regenerated** | The gate outcome, computed from Repository Truth, with the consequence and the enforcement route. |
| `05-WORK-PACKAGE-REGISTER.md` | **regenerated** | Every work package: owner, constitutional route, acceptance condition. |
| `06-DECISION-TRACEABILITY-CLOSURE.md` | **regenerated** | decision → register → index → disposition → located evidence. |
| `07-ARCHITECTURAL-COVERAGE-MATRIX.md` | **regenerated** | The Final Architectural Coverage Matrix: decision → located owner → **measured** coverage of the five equivalence dimensions → action taken → evidence. |
| `ucda.json` | **regenerated** | Machine model + seal. |
| `evidence/decision-evidence-index.json` | **regenerated** | Per-decision resolved and unresolved evidence references, and measured coverage. |

Never hand-edit a regenerated file — it is overwritten on the next run.

## Operation

```bash
make ucda        # regenerate the determinations
make ucda-gate   # fail-closed Implementation Evidence Gate
make ucda-self   # the four guards over UCDA's own surface
```

Exit: `0` gate OPEN · `1` gate CLOSED (a decision is undispositioned) · `2` fail-closed abort (declaration unusable, so no verdict may be asserted).

The gate also runs inside `make uccep-gate`, inside `.github/workflows/uccep-gate.yml`, and at session start via `.kiro/hooks/ucda-000001.json`. No new gate apparatus, pipeline, scheduler or daemon was created (28.19).

## The four self-guards

| Guard | Proves |
|---|---|
| `--check-declaration` | Identifiers are unique; the key set of every section is fixed; the lifecycle has exactly one terminal stage, only forward transitions, and full reachability; every disposition is drawn from the closed set; every disposition's required fields are present, single-valued where required, and resolve to a declared decision or work package where required; no decision asserts an obligation its disposition does not admit; no disposition is asserted before its earliest lawful stage; every programme reference resolves in the repository. |
| `--check-no-enumeration` | No declared identifier, stage name or disposition name appears as a literal in the engine source — so a new decision, stage, disposition or work package is DATA only. |
| `--check-write-scope` | Every write lands inside this directory. The forbidden prefixes include the frozen corpus, the registration authority, the constitutional zones, `adr/` and `knowledge/` — this programme never writes a decision register. |
| `--check-determinism` | Two renders of one model are byte-identical. No timestamp is emitted anywhere. |

## Bidirectionality of the verdict

A gate whose verdict cannot be reached in both directions carries no evidentiary value (the defect recorded as `UCCEP-F-001` against another located gate). This gate was probed in both directions: with the declaration as committed it exits `0` with the gate OPEN; with a single decision whose register and evidence do not resolve, it reports that decision by name, marks it conversation-only, and exits `1`.

## Coverage completeness — similarity is not sufficient

Article 28.13(b) lets a decision be recorded as already discharged by an existing canonical owner. Nothing in the bare Article prevents that claim from resting on a resemblance, so a partially covered decision could be closed as complete. The rule that closes this is registered at `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` **§7 (CR-1)** and mechanised here:

> A decision may assert 28.13(b) only where the located owner demonstrably covers **all five** declared equivalence dimensions — **functional**, **architectural**, **governance**, **lifecycle**, **extensibility**. Where any dimension is unevidenced, the decision is *partially represented*, 28.13(b) is unavailable, and the lawful disposition is 28.13(c) with a work package against the named shortfall.

The dimensions, the scope (a decision class, not a list of decisions) and the disposition the rule binds are all DATA in `ucda-decisions.json`, so `--check-no-enumeration` still passes and a sixth dimension is an entry, not a code change. A dimension is covered only where the decision names at least one artifact for it **and every artifact it names resolves**; a dimension for which nothing is named is not covered. Coverage is therefore measured from Repository Truth, and a claim survives only as long as the artifact it rests on does.

This adds **no** sixth disposition, **no** second decision register, **no** new gate apparatus and **no** new authority. A breach is a declaration-integrity finding, so the run aborts fail-closed (exit `2`) and no verdict is emitted — the claim cannot be recorded at all.

**Probed in both directions.** With the declaration as committed, the four guards pass and the gate is OPEN at the measured aggregate coverage. Withdrawing one proven dimension from a decision that asserts 28.13(b), and separately pointing one dimension at an artifact that does not exist, each names the affected decision, reports its measured percentage and the unevidenced dimension, and aborts fail-closed.

**Boundary.** `platform/coverage` owns Universe→Code coverage — whether declared implementation is realized. It holds no notion of a decision, register or disposition, so it is not a duplicate of this concern and is not extended by it. The boundary is itself recorded as a dispositioned decision rather than left to inference.

---

*AUTHORITY = NONE (DERIVED TRUTH). This directory creates no authority, allocates no identity, and supersedes no governing instrument. Where it conflicts with a higher frozen or governing instrument, the higher instrument governs.*
