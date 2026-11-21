# 00-MASTER/URRC-000001 — Repository Reality & Constitutional Completion

| Field | Value |
|---|---|
| PROGRAMME | `URRC-000001` |
| CHARTERED AS | Programme `Omega-Infinity-001` — *Repository Reality & Constitutional Completion* |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| GOVERNING INSTRUMENT | `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` |
| EVOLUTION OWNER | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` |
| ROSTER BINDING | `PROGRAM-000017` — **authorization required**, see `WP-URRC-001` |
| THIS DIRECTORY | **Operational Memory** — permanently excluded from corpus registration per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |

This programme establishes **Repository Truth** for the thirty-two deliverables its charter names. It creates no catalogue, no registry, no roadmap and no authority. Where a canonical owner already exists it is **bound by reference** and never restated; where none exists the fact is **derived** from machine-readable repository truth; where honest derivation is impossible the absence is **declared and counted**, never filled in.

## Why the identifier is not the charter designation

The charter designation uses the token `Omega-Infinity-001`. That token, written in its Unicode form, is a **ratified constitutional law identifier** — `LAW Ω∞-001..020`, ratified by `02-MASTER/UCOS-RAT-001-REPOSITORY-RATIFICATION-DETERMINATION.md` (RAT-08/09) and carried verbatim in `01-WORKING/LAW-REGISTER.md` (LAW-R04). It is also identifier family **#25** in `00-MASTER/UAKOS-CLOSURE-007/03-IDENTIFIER-FAMILY-CATALOG.md`, whose regex is machine-applied by `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py`.

A programme bearing that token would be parsed as a law citation and would corrupt law-citation counts across the repository. The programme is therefore homed at `URRC-000001`, allocated forward-only from the `00-MASTER/` directory series per `00-MASTER/UCCEP-000008/05-GDR-E-REGISTER-EVIDENCE-AND-LINEAGE-REALIZATION.md` (GD-18-C1…C4), and registered in exactly one register — `00-MASTER/UCCEP-000000/uccep-bindings.json` → `programs[]` — per `00-MASTER/IMR-0000/19-PUBLIC-INTERFACE-CATALOGUE.md` IFL-01. The `--check-law-namespace` guard proves no emitted artefact reintroduces the law token.

## The four binding modes

Every deliverable carries exactly one mode, and the mode is **DATA**, not a judgement made in code.

| Mode | Meaning |
|---|---|
| `REUSE-BY-REFERENCE` | A canonical owner exists and is current. The programme emits a pointer row only. No content is restated. |
| `REUSE-WITH-DERIVED-DELTA` | A canonical owner exists. The programme emits the pointer **plus** a delta the owner does not contain — staleness against HEAD, a coverage ratio, or a scope gap. |
| `DERIVE` | No canonical owner exists. The programme computes the fact from declared substrate. |
| `DECLARED-UNKNOWN` | No substrate exists. The programme emits verified absence with a counted probe and the evidence class that would be required. Never a body, never a row. |

`--check-reuse-before-create` mechanizes the zero-duplication invariant: if a deliverable's canonical owner resolves on disk, its mode **must** be a reuse mode. A `DERIVE` over a resolving owner is a finding, not a preference.

## Layout

| Path | Kind | Notes |
|---|---|---|
| `urrc-bindings.json` | **authored DATA** | The only file to edit. Substrate, binding modes, meta-model, references, matrices, gates, the thirty-two deliverables, outputs, verdict sources, findings, work packages, law citations. |
| `urrc_engine.py` | **authored code** | Deterministic, stdlib-only. Holds no deliverable name, no matrix identifier, no substrate path and no binding-mode name, so extension never requires a code change. |
| `README.md` | authored | This file. |
| `00-URRC-DASHBOARD.md` | **regenerated** | Start here. Binding distribution, matrix verdicts, gate table, blocked-by set. |
| `01-DELIVERABLE-BINDING-REGISTER.md` | **regenerated** | The thirty-two deliverables: mode, canonical owner, resolution, currency, generator class. |
| `02-REPOSITORY-REALITY-DETERMINATION.md` | **regenerated** | Repository reality bound to its owner, plus the substrate census delta. |
| `03-REUSE-MATRIX.md` | **regenerated** | Repository-wide reuse disposition over all thirty-two bindings. |
| `04-DUPLICATION-MATRIX.md` | **regenerated** | Structural duplication only: content identity, name identity, registration delta, multi-home concepts, deliverable overlap. |
| `05-CONFLICT-MATRIX.md` | **regenerated** | Declared conflicts, status-vocabulary conflict, live dependency on superseded truth, and the determination conflict set. |
| `06-GAP-MATRIX.md` | **regenerated** | Deliverable, executability, dimension, traceability and open-work gaps. |
| `07-COMPLETENESS-MATRIX.md` | **regenerated** | Per-dimension completeness, declared as a lower bound. |
| `08-READINESS-MATRIX.md` | **regenerated** | Readiness bound to its owners, plus the blocked-by set. |
| `09-AUTOMATION-MATRIX.md` | **regenerated** | Automation *presence* per gate and deliverable. Automatability is not claimed. |
| `10-CATALOGUE-AND-REGISTRY-BINDING.md` | **regenerated** | Catalogue, registry, ontology, taxonomy, API and interface owners. |
| `11-ENGINE-CATALOGUE.md` | **regenerated** | Engines discovered by declared glob, joined to their gate, Makefile and workflow bindings. |
| `12-GRAPH-AND-CAPABILITY-BINDING.md` | **regenerated** | Graph owners, edge-count reconciliation, capability edge census. |
| `13-DECISION-INTELLIGENCE-MATRIX.md` | **regenerated** | Decision lifecycle and disposition occupancy, and deliverable↔decision coverage. |
| `14-VALIDATION-CERTIFICATION-COMPLIANCE-BINDING.md` | **regenerated** | Validation, certification and constitutional-compliance owners plus the certification-scope reconciliation. |
| `15-EVOLUTION-AND-ROADMAP-BINDING.md` | **regenerated** | Evolution and master-roadmap owners; executable-owner delta. |
| `16-NON-DERIVABLE-REGISTER.md` | **regenerated** | Every fact this programme refuses to fabricate, with its counted probe and required evidence class. |
| `17-PROGRAMME-COMPLETION-DETERMINATION.md` | **regenerated** | This programme's own completion determination. No repository-wide completion is claimed. |
| `urrc.json` | **regenerated** | Machine model + seal. |
| `evidence/urrc-substrate-index.json` | **regenerated** | Per-substrate presence, record counts and content hashes. Not sealed. |

Never hand-edit a regenerated file — it is overwritten on the next run.

## Operation

```bash
make urrc        # regenerate the determinations
make urrc-gate   # fail-closed repository-reality gate
make urrc-self   # the eight guards over URRC's own surface
```

Exit: `0` every blocking gate passed · `1` a blocking gate failed · `2` fail-closed abort (declaration or required substrate unusable, so no verdict may be asserted).

The programme runs at session start via `.kiro/hooks/urrc-000001.json`. It creates no new gate apparatus, pipeline, scheduler or daemon; its aggregate-gate binding is a declared work package, not a self-executed change.

## The eight self-guards

| Guard | Proves |
|---|---|
| `--check-declaration` | Identifiers are unique across every section; the key set of every section is fixed; deliverable indices are exactly the charter's contiguous range with no gap or repeat; every binding mode is drawn from the declared set; every cross-reference is bound; every gate binds at least one computable matrix, so a manual gate is impossible; the rendered output count matches the declaration; every reference resolves in the repository. |
| `--check-no-enumeration` | No declared identifier, deliverable name, binding-mode name or substrate path appears as a literal in the engine source — so a new deliverable, matrix, substrate or mode is DATA only. |
| `--check-write-scope` | Every write lands inside this directory. The forbidden prefixes include the frozen corpus, the registration authority, the constitutional zones, the source bands, and every canonical-owner zone this programme reads — so the programme can read Repository Truth but never author it. |
| `--check-determinism` | Two renders of one model are byte-identical. No timestamp is emitted anywhere. |
| `--check-substrate` | Every required substrate file exists, parses, and every pointer declared against it resolves inside it. Fail-closed otherwise, so a moved or emptied substrate can never be silently replaced by a fabricated value. |
| `--check-no-fabrication` | Every derived record carries either resolved substrate evidence or an explicit declared-unknown marker. A record with neither is a finding. |
| `--check-reuse-before-create` | No deliverable whose canonical owner resolves is bound in a create mode. This is the zero-duplication invariant, mechanized. |
| `--check-law-namespace` | Neither the declaration nor any rendered byte reintroduces the ratified law token outside the declared citation whitelist. |

## What this programme will not do

It does not ratify, does not freeze, does not deploy, does not publish, does not file, and does not write outside its own directory. It does not elect a winner among conflicting located determinations — it reports the conflict set with each verdict's scope and leaves adjudication to the authority that owns it. Three bindings that must land outside this directory are recorded as work packages with `authorization_required` and are executed by an authorized change, never by the engine.

---

*AUTHORITY = NONE (DERIVED TRUTH). This directory creates no authority, allocates no identity, and supersedes no governing instrument. Where it conflicts with a higher frozen or governing instrument, the higher instrument governs.*
