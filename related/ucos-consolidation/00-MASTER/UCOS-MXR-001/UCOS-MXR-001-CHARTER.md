# UCOS-MXR-001 — CHARTER

**Master Execution Roadmap — Implementation Execution Program (post UAKOS-CLOSURE-008)**

> AUTHORITY = NONE (DERIVED TRUTH). This programme authorizes nothing, ratifies nothing and
> certifies nothing. It orders work the repository's own registers already own. Fail-closed
> (TRACK-001).

---

## 1 — Mandate

Discovery, knowledge extraction, verification, reconciliation and closure are COMPLETE.
This programme repeats none of them. It transforms the CURRENT REPOSITORY STATE into a
deterministic execution program: a backlog, a dependency graph, waves, a critical path,
parallel groups, validation and certification gates, and a readiness determination that an
autonomous implementation agent can execute without further architectural analysis.

## 2 — Boundary

| Boundary | Rule |
|---|---|
| Repository | `~/Desktop/UCOS-CONSOLIDATION` — the ONLY implementation authority |
| Programme home | `00-MASTER/UCOS-MXR-001/` — the ONLY path this ENGINE writes |
| Integration surface | `Makefile` (targets `roadmap`, `roadmap-replay`, `roadmap-gate`) and `.github/workflows/roadmap-gate.yml` are committed WITH this programme so it is runnable and gated. The engine writes neither; they are declared here rather than left as an undeclared out-of-home footprint |
| Knowledge-assimilation directory | NOT read by this engine at all. Its knowledge already entered the repository through UAKOS-CLOSURE-008; consulting it again would be re-discovery |
| Existing registers | never rewritten. Where a register and HEAD evidence disagree, the divergence is RECORDED for its owner (register 01), not corrected here |
| Naming | outputs live inside the programme home, so they never shadow the root-level `03-DEPENDENCY-GRAPH.md` / `04-IMPLEMENTATION-BACKLOG.md` / `04-IMPLEMENTATION-WAVES.md` of earlier programmes |

## 3 — Inputs (state of record, read-only, hashed)

| Input | What is taken from it |
|---|---|
| `00-MASTER/MCP-003-MASTER-EXECUTION.md` | MEP-01..MEP-10: capability, owner, dependencies, priority, readiness, state, acceptance and exit criteria |
| `00-MASTER/MCP-002-MASTER-STATE.md` | §02 blockers of record · §05 the single next authorized capability |
| `00-MASTER/UCDA-000001/ucda-decisions.json` | the 18 registered implementation work packages with owner, route and acceptance |
| `intelligence/UCOS-RIE-AEOS-READINESS.json` | the declared execution-spine gaps G-01..G-12 with severity |
| `intelligence/UCOS-RIE-EXECUTION-FRONTIER.json` | the declared frontier and critical path (compared, not trusted blindly) |
| `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | the declared bottom-up layered architecture (spine before adapters/CLI) |
| `00-MASTER/UAKOS-CLOSURE-002/closure.json` | 440 concepts: disposition, `in_code`, `certified`, family, canonical homes |
| `00-MASTER/UAKOS-CLOSURE-008/assimilation.json` | homed knowledge items with destination, owner, wave, priority, dependencies |
| HEAD file evidence | five declared band probes — the ONLY measurement this engine takes |

## 4 — Prohibitions

- No discovery, no corpus mining, no re-extraction, no re-verification, no re-reconciliation.
- No replacement documentation: nothing here restates an existing register's content as a
  new authority.
- No invented precedence. Every dependency edge comes from a register field, a declared
  severity/layer ordering, or the register's own deterministic item ordering (used to give
  direction to symmetric knowledge-dependency evidence).
- No calendar estimates. The repository carries no velocity evidence, so effort is expressed
  only in points on a fixed scale (S=1 · M=3 · L=8 · XL=20).
- No fabricated commitment: registered FUTURE/DEFERRED entries stay out of the active
  backlog and are reported as an excluded pool.

## 5 — Method

1. **Determine** implementation status, owner, dependencies, blockers, priority, complexity,
   risk, validation and certification requirements and completion criteria for every
   remaining item.
2. **Graph** the items: topological order, levels, workstreams, critical path (computed twice
   — in-repository and out-of-corpus, never conflated).
3. **Partition** into waves W0..W7 plus WF, gated so no wave depends on a later wave.
4. **Determine readiness** per item: READY · BLOCKED · DEFERRED · WAITING_FOR_RATIFICATION ·
   WAITING_FOR_IMPLEMENTATION · WAITING_FOR_VALIDATION · WAITING_FOR_CERTIFICATION. Per-source
   readiness describes an item in isolation, so it is then CLOSED over the dependency graph: a
   READY item whose prerequisite cannot be started is BLOCKED, which makes BLOCKED a measured
   state rather than an unreachable one.
5. **Emit** the ten roadmap artifacts plus `roadmap.json`, and fail closed on any blocking gate.

## 6 — Success criteria

| Criterion | Gate |
|---|---|
| No additional discovery performed | inputs are the eight registers above; the assimilation directory is never opened |
| No reconciliation repeated | divergences are recorded, never resolved (register 01) |
| No duplicate documentation | all outputs live in the programme home and cite their source register per item |
| Every remaining item identified | backlog built from every remaining-work source the repository carries |
| Every dependency resolved | gate: every dependency resolves to a backlog item; graph acyclic |
| Deterministic execution order exists | gate: topological order covers every item |
| Autonomous execution possible | every item carries a location, a NAMED owner (placeholder owners are rejected), a validation command, success criteria and a rollback strategy (five gates) |
| Readiness means what it says | gate: no READY item depends on a non-executable prerequisite |
| No derivation presented as an estimate | where readiness, authorization or effort is derived from an evidence priority label rather than assessed, register 01 §derivation and register 09 say so |

## 7 — Artifacts

| Artifact | Contents |
|---|---|
| `01-MASTER-EXECUTION-ROADMAP.md` | the roadmap, the single next action, register-vs-evidence record |
| `02-IMPLEMENTATION-BACKLOG.md` | every item with id, location, owner, deps, priority, effort, statuses |
| `03-DEPENDENCY-GRAPH.md` | prerequisites, successors, levels, workstreams, declared layers |
| `04-IMPLEMENTATION-WAVES.md` | per-wave objective, scope, inputs, outputs, gates, effort, DoD |
| `05-CRITICAL-PATH.md` | in-repository critical path + out-of-corpus chain + declared path |
| `06-PARALLEL-EXECUTION-GROUPS.md` | safe concurrency levels and independent workstreams |
| `07-VALIDATION-GATES.md` | per-class validation commands + repository-wide gates |
| `08-CERTIFICATION-GATES.md` | per-class certification gates + the provisional ceiling |
| `09-IMPLEMENTATION-DASHBOARD.md` | completion measured over the concept model + backlog rollup |
| `10-EXECUTION-READINESS-DETERMINATION.md` | the autonomous execution plan + GO determination |
| `roadmap.json` | the machine-readable program: every item, the graph, the gates |

## 8 — Reproduction

```bash
make roadmap        # regenerate the ten artifacts + roadmap.json
make roadmap-replay # re-render the ten artifacts from roadmap.json (recorded HEAD preserved)
make roadmap-gate   # fail-closed: non-zero exit unless the roadmap is executable
./verify.sh         # canonical repository gate (unaffected by this programme)
```

The engine emits no timestamps and reads only committed repository state, so repeated runs at
the same HEAD are byte-identical. Across a commit boundary the recorded `head_commit` and the
seal necessarily change — a committed artifact cannot carry the sha of the commit that carries
it — so the CI drift check REPLAYS (`--render`, recorded HEAD preserved).

**Disclosed limit.** This programme is derived from `closure.json`, which is derived from the
corpus that this programme itself joins on commit. Regenerating `closure.json` after the commit
therefore measures MORE concepts than the committed roadmap was compiled from, so
"recompiled == committed" is not a reachable fixed point in a single commit and is not asserted
anywhere. What IS checkable, and is recorded, is the sha256 of every input the committed roadmap
was compiled from (`roadmap.json` → `inputs`). Recorded here rather than resolved: closing it
would mean either withholding the programme from the corpus it belongs to or rewriting a
register this programme does not own.
