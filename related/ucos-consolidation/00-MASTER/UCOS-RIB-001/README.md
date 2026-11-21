# 00-MASTER/UCOS-RIB-001 — Repository Integration Blueprint

| Field | Value |
|---|---|
| PROGRAMME | `UCOS-RIB-001` |
| CHARTERED AS | `EPIC-001` / `WP-001` (programme `Ω∞-001`) |
| MISSION / PROMPT | `UCOS-IMP-MSN-000001` · `UCOS-PRM-IMP-000001` |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| GOVERNING INSTRUMENT | `00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md` |
| CAPABILITY OWNER BOUND | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` |
| ROUTE | `make rib` · `make rib-gate` · `make rib-self` |
| THIS DIRECTORY | **Operational Memory** — permanently excluded from corpus registration per `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` |

This programme is the permanent implementation contract EPIC-001 charters. It **creates no
capability catalogue, no dependency graph, no registry, no execution queue, no priority
register and no certification authority** — every one of those already exists and is already
owned. What did not exist is the *integration layer*: one place where the whole unit universe
is discovered from Repository Truth, measured, and given exactly one disposition.

## What is bound, and what is derived

A matrix marked **BOUND** is discharged by the owner that already holds it. This programme
emits the pointer and **zero rows** — that is precisely what makes the binding a reuse
rather than a second truth, and `--check-no-fabrication` fails if a bound matrix ever carries
rows here. A matrix marked **DERIVED** is computed here only because no owner holds it in
machine-readable form.

| Owner bound | What it already holds |
|---|---|
| `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | the canonical capability catalogue (66 records) |
| `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | the programme-level dependency graph |
| `intelligence/UCOS-RIE-EXECUTION-FRONTIER.json` | the execution frontier and critical path |
| `00-BOOK/tools/ukb.py` · `00-BOOK/DATA/` | registration, the typed graph, twin certification |
| `00-MASTER/URRC-000001/` | the reuse, duplication, conflict, gap and readiness matrices |
| `00-MASTER/UAKOS-CLOSURE-002/` | concept closure, the wave register, the priority register |
| `00-MASTER/UEI-000001` · `UER-000001` | evolution and resilience capability bindings |

## Discovery is total, and nothing is enumerated

The unit universe is discovered by eight declared sources — version-controlled Python roots
and packages, operational programmes owning an engine, the canonical catalogues, the
constitutional and meta-constitutional instruments, the portfolio programme rollup, and the
capability catalogue itself. No unit name appears anywhere in the engine;
`--check-no-enumeration` proves it by token search over the source.

## Exactly one disposition, always one

Each unit carries exactly one outcome from a closed set of eight — `REUSE`, `EXTEND`,
`CONFIGURE`, `IMPLEMENT`, `MERGE`, `SUPERSEDE`, `DEPRECATE`, `REMOVE`. The outcome is produced
by an **ordered, first-match-wins rule set whose last rule carries no clauses**, so the
function is total by construction: no unit can carry two dispositions, and none can carry
zero. `--check-declaration` rejects a rule set whose final rule is not a catch-all, or that
places a catch-all early enough to make a later rule unreachable. `--check-totality` proves
the property over the actual universe.

An **advisory** duplicate class may never drive a disposition. A shared leaf name across
layers, or a staged programme owning one engine per phase, is recorded and counted but
accuses no unit: a name is not a responsibility, and a phase is not a duplicate.

## Where a fact could not be honestly derived

Three facts are registered as non-derivable rather than estimated, each with a counted probe,
the evidence class that would be required, and the owner of the act that would supply it:
monetary or user-facing **benefit**, the ratified programme **phase** of a unit, and
**supersession** between units. An absence is excused only if its probe actually ran and
measured the substrate it claims to have searched.

## Layout

| Path | Kind | Notes |
|---|---|---|
| `rib-blueprint.json` | **authored DATA** | The only file to edit. Substrate, discovery sources, enrichment, measures, planes, cycle classes, dispositions, ordered rules, the sixteen matrices, gap and duplicate classes, obligations, twelve gates, outputs, severities, compliance, references, refusals, probes, work packages. |
| `rib_engine.py` | **authored code** | Deterministic, stdlib-only. Holds no unit key, capability name, disposition name, matrix/gate/output identifier or substrate path, so extension never requires a code change. |
| `README.md` | authored | This file. |
| `00-RIB-DASHBOARD.md` … `14-…` | **generated** | The fourteen mandatory outputs plus the dashboard. Regenerated, never hand-edited. |
| `rib.json` | **generated** | The whole computed model, including every finding truncated out of the rendered tables. |
| `evidence/` | **generated** | The content-addressed evidence index. |

## Exit semantics

| Command | 0 | 1 | 2 |
|---|---|---|---|
| `rib_engine.py --gate` | every blocking gate passed | a blocking gate failed | fail-closed abort — declaration or required substrate unusable |
| any `--check-*` guard | guard passed | guard failed | — |

The gate is **fail-closed by design**. A blueprint that cannot certify says so and stops;
it does not lower a threshold to pass itself.
