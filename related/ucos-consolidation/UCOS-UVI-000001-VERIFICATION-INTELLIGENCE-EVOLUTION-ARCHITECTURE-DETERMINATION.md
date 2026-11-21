# UCOS-UVI-000001 — Verification Intelligence Evolution Architecture Determination

**Artifact ID:** UCOS-UVI-000001-EVOLUTION-ARCH-DET
**Programme:** UVI-000001 — Universal Verification Intelligence
**Standing:** DETERMINATION — architecture only. Legislates nothing. Creates no authority, no registry, no gate.
**Authority:** NONE — DERIVED. Every constraint cited here is already owned by an existing instrument.
**Baseline:** branch `integration/recovery-001` at `bd3f71ff`
**Date:** 2026-08-19
**Predecessor:** Verification Intelligence Evolution Discovery (COMPLETE)
**Execution mode:** ARCHITECTURE DETERMINATION ONLY — no implementation, no repository mutation, no code changes.

**Determination:** **ARCHITECTURE READY** — see §12.

---

## 1. Current Architecture Reality

Discovery established, by measurement rather than reading, that every primitive this evolution requires already exists and is running under gate. This section records only the facts the determinations below depend on.

### 1.1 Measured baseline

| Quantity | Measured | Method |
|---|---|---|
| `./verify.sh --full` wall clock | **499 s** | two independent timed runs, identical totals |
| pytest + coverage stage | 452 s (90.6%) | run's own per-stage summary |
| prerequisite generation | 29 s (5.8%) | same |
| all governance/validation/lineage/certification gates | ~28 s serial, **7 s** overlapped | same |
| tests executed | 11 990 across 13 shards | same |
| declared stages | 15, across 5 phases, 3 planes | `uvi-declaration.json` |
| tracked tree mutation by a full run | **none** | `git status --porcelain` diff, before/after |

The two-hour figure carried in the evolution brief does not correspond to any measurement in this repository. The superseded baseline recorded in the declaration is 2 814 s in pytest alone.

### 1.2 Primitives in force

| Primitive | Home | State |
|---|---|---|
| Stage Registry | `uvi-declaration.json` → `stage_registry` | declared, law-reconciled (UVI-L-03) |
| Mode Constitution | `uvi-declaration.json` → `mode_constitution` | 4 modes, claims and non-claims explicit |
| Dependency graph | `UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` | 9 902 edges over 1 931 objects |
| Relationship graph | `UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | 34 709 edges, 6 kinds |
| Impact analysis | `engine/verification_impact/` | fail-closed diff base, reverse closure |
| Selection | `engine/verification_intelligence/selection.py` | 5 substrates, 5 ordered layers |
| Evidence cache | `engine/verification_intelligence/evidence.py` | content-addressed, live, atomic |
| DAG execution | `engine/verification_intelligence/execution.py` | waves, phase barriers, deterministic shards |
| Cost model | `UVI-000001/test-cost-model.json` | 568 objects priced, serial measurement |
| Deterministic planning | `plan.py` | no clock, no host, no absolute path |

### 1.3 The four measured defects this architecture must resolve

1. **Three reusable stages can never compute a cache key.** `governance-pre`, `registry-validate` and `meta-constitutional` refuse permanently — two declared prefixes (`00-SOURCE/`, `00-BOOK/SCHEMAS/`) match zero registered objects despite 32 tracked files, and one deliberately unhashable file (`content_hash_withheld: SELF_REFERENTIAL`) poisons three digests.
2. **The artifact lineage graph is unread.** 345 artifacts, 1 891 `input_closure` edges, 32 producers — present, derived, and bypassed.
3. **The cost model is measured serially and applied concurrently.** 2.12× inflation; predicted uniform 129.6 s/shard against an observed 228–375 s spread.
4. **66.2% of tracked files carry no import edge.** On the current HEAD diff, 515 of 571 escalations arise from this single cause.

### 1.4 New measurements taken for this determination

Four facts were measured specifically to decide §3, §5, §7 and §6. They are stated here because the determinations rest on them and would be different if they were different.

| Measurement | Result | Decides |
|---|---|---|
| Cycles in the real import graph | **31 distinct cyclic node sets** | §3, §5 |
| Closure honesty of the import edge set | 0 unregistered edge targets | §5 |
| Non-code files reachable by any existing declared substrate | **421 of 4 057 (10.4%)** | §7 |
| Non-code files under some stage's declared `reuse_inputs` | **1 452 of 4 057 (35.8%)** | §7, §9 |
| Stages declaring a read-set | **8 of 15** — and exactly the 8 that are `reusable` | §7, §9 |
| Evidence key composition | engine version + stage id + label + read-set hashes — **argv absent** | §6 |

---

## 2. Architectural Principles

These are not proposed. Each is already binding somewhere in the corpus; they are gathered here because the determinations below are derived from them.

**P1 — One fact, one owner, many projections.** Already the operative pattern in `UCOS-CL-015` (generated-artifact registry: "one fact, one owner, many views") and in `UAPF-000001` ("one edge set, two views"). A second *view* is architecture; a second *fact* is drift.

**P2 — No parallel authority.** `UCOS-UFC-001` FG-15 is an executable gate. Any evolution that creates a second answer to a question an instrument already owns is refused before it is evaluated on merit.

**P3 — Reuse before create.** Enforced as a self-guard across at least nine programme gates. A new registry is admissible only where no existing owner holds the fact.

**P4 — Derived truth is never authority.** Every substrate the selector reads declares `authority: NONE — DERIVED TRUTH`. Reading a derived surface to *schedule* work is legitimate; reading it to *decide compliance* is not.

**P5 — Fail wide, never narrow.** UVI-L-07. The asymmetry is the whole safety argument: an intelligence layer that cannot compute a plan must cause *more* verification, never less.

**P6 — Selection is derived, never authored.** UVI-L-06. No test path literal may enter the selector or the declaration.

**P7 — Measurement is not a gate.** The cost model declares `NOT_A_GATE`: a stale measurement makes a plan slower, never wrong. Any cost evolution inherits this.

**P8 — Scheduling changes when, never what.** UVI-L-08. Topology is free to evolve because it is proven to be obligation-neutral.

---

## 3. Canonical Dependency Model

### 3.1 Determination

**B — one canonical dependency intelligence layer with multiple projections — with a boundary that the discovery brief did not anticipate.**

The convergence point is **the edge population**, not the traversal algorithm. UCOS shall have one canonical dependency *fact set* and two mathematically distinct *projections* over it. It shall not have one canonical dependency *graph object*.

### 3.2 Why this is determined and not preferred

The naive reading of P1/P2 is that `platform.foundation.dependencies.DependencyGraph` — the repository's declared canonical dependency model — should absorb the verification impact graph, leaving one implementation. **Measurement refutes this.**

`DependencyGraph` is an *ordering* model. Its declared guarantees are deterministic topological order via Kahn's algorithm, **cycle rejection** (AR-01, downward-only), and **closure honesty** (a dependency on an unknown node is rejected, IP-04). It raises on a cyclic graph.

The real Python import graph in this repository contains **31 distinct cyclic node sets**, including `engine/uaue/gate.py → exits.py → registers.py → gate.py`. These are not defects to be removed; module-level import cycles broken by deferred import are ordinary and legitimate.

Therefore:

> **`DependencyGraph` cannot host the impact edge set. Feeding it the measured import graph would raise `DependencyError` on 31 subgraphs.**

The two are not duplicate authority over one domain. They are **two projections with incompatible axioms** over a shared edge population:

| | Ordering projection | Reachability projection |
|---|---|---|
| Realisation | `platform/foundation/dependencies.py` | `engine/verification_impact/graph.py` |
| Question | "in what order may these run?" | "what does this change reach?" |
| Cycles | **must reject** (AR-01) | **must tolerate** (31 measured) |
| Unknown nodes | **must reject** (IP-04) | must tolerate (open world) |
| Direction | forward, `depends_on` | reverse, `dependents_of` |
| Domain | declared execution units | measured repository objects |

`UAPF-000001` already stated this exact relationship in prose: *"an edge `a → b` is 'a depends on b' read forward and 'b impacts a' read backward. Modelling them once means the dependency graph and the impact graph can never disagree."* UAPF then built the forward view and left the backward view unbuilt for verification. The determination is that verification's backward view is the *second half of a pattern UAPF already declared*, not a competing model.

### 3.3 Risk analysis

**Duplication risk — LOW, and lower than the alternative.** The duplicated asset today is not the traversal (both are ~20 lines and provably different); it is the *edge population*. Verification reads UGA's edges; UAPF reads declared unit edges. These describe different populations and are not duplicates. Forcing one traversal would require weakening `DependencyGraph`'s cycle rejection — which would silently remove the AR-01 guarantee that eleven other consumers depend on. **The duplication risk of convergence exceeds the duplication risk of separation.**

**Authority risk — LOW if the boundary is declared, HIGH if it is left implicit.** Today nothing states that these two are separate-by-axiom. A future reader sees two dependency graphs and reasonably concludes drift. The residual authority risk is *undeclared separation*, not the separation itself.

**Reuse potential — CONCENTRATED IN THE EDGE POPULATION.** The reusable asset is UGA-001's 9 902 import edges plus 34 709 relationship edges. Both projections should read that population. Verification already does. UAPF does not — but UAPF's domain is declared pipeline units, not repository objects, so this is correct.

**Migration impact — ZERO code movement.** The determination requires no module to move, merge or be rewritten. It requires one declaration: that the edge population is canonical and the projections are axiom-distinguished.

### 3.4 What is forbidden by this determination

- A third dependency *edge population*.
- Any consumer that constructs its own edge set from source rather than reading the canonical population.
- Weakening `DependencyGraph`'s cycle or closure rejection to accommodate reachability.
- Any claim that either projection is "the" dependency model.

---

## 4. Impact Intelligence Model

### 4.1 The proposed flow is correct and incomplete

The flow given in the brief —

```
Change Event → Changed Entity → Dependency Traversal → Affected Reality Surface
             → Verification Requirement Set → Execution Plan
```

— is the right shape. Measurement shows one node is not realised: **`Verification Requirement Set` currently resolves only to test objects.** Stages are selected by mode admission and evidence lookup; they are never selected by impact.

This is the central architectural gap. It is why a one-line Markdown change still runs twelve governance gates, and why `registry-validate` is the MAIN critical path on every run regardless of what changed.

### 4.2 Determined canonical flow

```
  CHANGE EVENT                         git diff, fail-closed (exists)
        │
        ▼
  CHANGED PATH SET                     ─── unresolved ──► ESCALATE (UVI-L-07)
        │
        ▼
  IDENTIFIED OBJECT                    UGA-001 registry record
        │
        ├──[E1 imports⁻¹]──► affected objects        (exists)
        ├──[E2 owned_by  ]──► affected owners        (exists)
        ├──[E3 capability]──► affected capabilities  (exists)
        ├──[E4 relationship]► affected identities    (exists)
        ├──[E5 produced_by]─► producing object       (PRESENT, UNREAD — §5)
        └──[E6 read_by   ]──► consuming STAGE        (PRESENT AS reuse_inputs, MISCLASSIFIED — §9)
        │
        ▼
  AFFECTED REALITY SURFACE             objects ∪ owners ∪ capabilities ∪ identities ∪ stages
        │
        ▼
  VERIFICATION REQUIREMENT SET         { test objects }  ∪  { stages }        ◄── stages are new
        │
        ▼
  EXECUTION PLAN                       waves · shards · evidence decisions (exists)
```

### 4.3 Required nodes

| Node | Owner | Status |
|---|---|---|
| Change event | `verification_impact/changes.py` | exists, fail-closed |
| Object identity | UCOS-UGA-001 | exists, 4 880 records |
| Owner | UCOS-UGA-001 | exists, 100% populated |
| Capability | UCOS-RIE catalogue | exists, 131 bindings |
| Artifact | UCOS-CL-015 | exists, 345 entries, **unread by selection** |
| Test object | UVI-000001 test registry | exists, 575 objects |
| **Stage** | **UVI-000001 stage registry** | **exists as a schedule unit; not an impact target** |

No new node class is required. The Stage node already exists and is already law-reconciled; it is simply not wired as a target of traversal.

### 4.4 Required edges

| Edge | Relation | Source | State |
|---|---|---|---|
| E1 | object → object | UGA `dependencies`, inverted | live |
| E2 | object → owner | UGA `owner` | live |
| E3 | owner → capability | RIE catalogue | live |
| E4 | identity → identity | relationship graph (`depends_on`, `produces`) | live |
| E5 | artifact → producer → inputs | `generated-artifact-registry.json` `input_closure` | **present, unread** |
| E6 | path → stage | stage `reuse_inputs` | **present, used only as a cache key** |

**E5 and E6 are the whole of the missing intelligence.** Both already exist as declared, owned, derived data. Neither requires a new registry, a new authority, or a new schema.

### 4.5 Ownership

| Question | Owner | New owner required |
|---|---|---|
| what exists, what it imports, who owns it | UCOS-UGA-001 | no |
| what capability an owner serves | UCOS-RIE-001 | no |
| what a producer produces and reads | UCOS-CL-015 | no |
| which stages exist and what each reads | UVI-000001 | no |
| **which verification a change requires** | **UVI-000001** | no — this is already its declared question |
| whether the repository is compliant | the twelve gate owners | unchanged |

**No new authority is created by this architecture.** UVI-000001's declared question is already *"which verification does this change require, and in what order may it be executed."* Selecting stages rather than only tests is a completion of that question, not an extension of it.

### 4.6 Evidence boundaries

Three boundaries must stay distinct, and conflating any two is the failure mode:

1. **Selection output is DERIVED TRUTH, never evidence.** A plan is not a claim that anything passed. It carries a digest for comparability, not for assurance.
2. **Stage results are the only evidence.** The evidence store holds stage verdicts keyed by input digest. Nothing else may enter it.
3. **Certification is neither.** It is the verdict of a mode that ran the whole suite under the floor without consulting evidence at all (UVI-L-09).

---

## 5. Artifact Verification Integration

### 5.1 Determination

`00-BOOK/DATA/generated-artifact-registry.json` shall be admitted as a **sixth read-only substrate** of selection, traversed in the reverse direction only.

### 5.2 Why admission is safe

Four properties already hold and together discharge the "must not become an authority" constraint:

- It declares `authority: AUTHORED REPOSITORY TRUTH, HELD AS A PROJECTION`. It is not a peer of UGA-001.
- Its module docstring states it is **deliberately upstream** of every engine it describes, and that nothing consults an engine's output to decide what that engine produces. Reading it from selection therefore introduces **no cycle**.
- It is already validated and already gated (`UCL-000001`, `UGA-INV-06` bootstrap-path closure, `bootstrap_gaps: []`).
- Selection would **read** it. It would not write, mint, extend or reconcile it. Under P4 this is the legitimate use of a derived surface.

### 5.3 Traversal direction is the load-bearing decision

The registry is authored **artifact → input_closure**. Impact needs the inverse:

```
changed input  ──[input_closure⁻¹]──►  artifact
artifact       ──[producer]──────────►  producer object
producer       ──[E1 imports⁻¹]──────►  ordinary reverse closure
```

Read forward it answers "what does this artifact depend on" — useless for impact. Read backward it answers "a change to this input reaches these artifacts, whose producer is this object" — which is exactly the relation no import edge can express.

### 5.4 Measured coverage and its honest limit

| Quantity | Measured |
|---|---|
| artifacts declared | 345 (all non-code, all tracked) |
| `input_closure` edges | 1 891 |
| distinct closure targets | 125 |
| targets resolving to a registered object | 116 |
| targets that are directory prefixes | 5 |
| **targets that resolve to nothing** | **4** |
| non-code tracked files this substrate reaches | **345 of 4 057 (8.5%)** |

**This substrate closes 8.5% of the non-code problem, not the whole of it.** Integrating it is correct and worthwhile; presenting it as the answer to §9 would be false. The 4 unresolved targets must escalate under P5 — an input closure that names something the registry cannot resolve is precisely the condition that cannot be bounded.

### 5.5 Prohibitions carried by this determination

- No write of any kind to the artifact registry from the verification path.
- No re-derivation of artifact lineage from the filesystem. If the registry does not declare it, it is not known, and unknown escalates.
- No second producer table inside UVI-000001.
- Traversal terminates at the producer object and hands off to E1. Verification must not re-implement producer semantics.

---

## 6. Evidence Intelligence Evolution

### 6.1 Reuse boundary

The boundary is **(mode × stage × input-digest)** and it is already correct. The five conditions in force — mode declares reuse, stage declares reusable, recomputed digest equals recorded, recorded result is PASS, engine version matches — are complete for what they cover. No condition is removed, weakened or added by this determination.

### 6.2 Immutable evidence identity — one measured incompleteness

The declaration states the key is computed from the declared inputs *"plus the stage's own command."* The implementation composes:

```
EVIDENCE_VERSION ‖ stage_id ‖ stage_label ‖ extra* ‖ Σ sorted(prefix, path:content_hash)
```

**The argv is not in the key.** The `label` is a proxy for it, and UVI-L-03 does reconcile labels to `run_stage` literals — so a *label* change is caught. But `verify.sh` invokes each stage as `run_stage "<label>" <argv…>`, and **the argv after the label is unbound**. Changing `--gate --quiet` to `--gate`, or repointing a stage at a different module while keeping its label, would produce a **false cache hit**.

The seam for the fix already exists and is unused: `input_digest` accepts `extra: tuple[str, ...]`, and no production caller passes it.

**Determination:** evidence identity must be *total over everything that can change the result*. The argv is such a thing. This is a correctness closure, not a feature.

### 6.3 Invalidation model

Content-addressed invalidation is the correct model and requires no change: a changed input yields a different address, so a superseded entry is never consulted again. There is no invalidation *event* and there should not be one — an explicit invalidation step is a second answer to "is this entry current."

One structural defect must be resolved, and it is a **distinction failure, not a policy gap**:

`input_digest` returns `None` — refusing reuse — in three situations it cannot currently tell apart:

| Condition | Meaning | Correct response |
|---|---|---|
| prefix matches zero registered objects | **authoring error** — the declaration names a path the registry does not carry | **fail loudly** |
| object carries `content_hash: null` with `content_hash_withheld` | **known and deliberate** — a self-referential surface | participate as a declared constant |
| object carries `content_hash: null` with no marker | genuinely unmeasured | refuse (current behaviour, correct) |

Today all three collapse to a silent permanent refusal. That is why `governance-pre`, `registry-validate` and `meta-constitutional` pay full cost on every run forever, and why nobody noticed: **a cache that silently never hits is indistinguishable from a cache that is cold.**

The safety property is preserved either way — refusing is always safe. What is lost is the ability to detect that the declaration is wrong.

### 6.4 Retention policy

Absent today: no eviction, expiry, pruning or bound anywhere in the module. Current store 20 entries / 80 KB — not yet material, unbounded by construction.

**Determination:** retention is a property of the **store**, not of verification, and must be architecturally incapable of changing a verdict.

- Bound by **generation count per `stage_id`**, not by age. Age is a clock, and no clock may enter the verification path (UVI-L-10).
- Eviction removes only entries no current digest addresses. Evicting a live entry costs time, never correctness.
- A store that cannot be pruned must not fail a run — the same swallow-on-`OSError` discipline `record()` already applies.
- Retention is **never** a gate and never certified.

### 6.5 Evidence lifecycle

```
  COMPUTE address  ── refuse ──►  stage RUNS   (safe terminal state)
        │
        ▼
  LOOK UP  ── miss ──►  stage RUNS ──►  RECORD (PASS or FAIL)
        │
       hit
        │
        ▼
  PASS? ── no ──►  stage RUNS
        │
       yes
        ▼
  REUSE (developer modes only — never certification, UVI-L-09)
```

Both PASS and FAIL are recorded, and must remain so: storing only passes would make a failure indistinguishable from an absent measurement on the next run. Entries are superseded by address, never mutated in place — the atomic temp-file-and-rename discipline is load-bearing and stays.

### 6.6 Preserved without exception

**Certification evidence cannot be reused.** `decide()` refuses on `mode.evidence_reuse` before it looks at the store. `integration` and `full` declare `evidence_reuse: false`. UVI-L-09 computes that no certification-eligible mode can reach a reuse decision at all. **Nothing in this section touches that path.**

---

## 7. Dependency Graph Relationship

### 7.1 Determination

**Separate domains. Not duplicate authority. No convergence of implementation. No third model.**

| Question | Answer |
|---|---|
| Duplicate authority? | **No** — measured incompatible axioms (§3.2) |
| Separate domains? | **Yes** — ordering over declared units vs reachability over measured objects |
| Canonical primitive candidate? | **The edge population**, not the graph object |
| Projection relationship? | Both are projections of one edge set, read in opposite directions |
| Third model allowed? | **No** |

### 7.2 The relationship, stated so it can be held

```
                    CANONICAL EDGE POPULATION
        UGA-001 import edges (9 902) + relationship edges (34 709)
                             │
             ┌───────────────┴───────────────┐
             ▼                               ▼
    ORDERING PROJECTION              REACHABILITY PROJECTION
    platform/foundation              engine/verification_impact
    forward · acyclic · closed       reverse · cyclic-tolerant · open
    "in what order?"                 "what does this reach?"
             │                               │
             ▼                               ▼
    UAPF-000001 scheduler            UVI-000001 selection
    (declared pipeline units)        (measured repository objects)
```

### 7.3 What this forbids

- Merging the two traversals. Measurement shows it would fail on 31 subgraphs.
- Weakening `DependencyGraph` to accept cycles. Eleven consumers rely on AR-01.
- Verification constructing edges from source rather than reading the canonical population.
- A third edge population under any name.

### 7.4 The residual risk this determination retires

The real exposure today is not duplication — it is that **the separation is undeclared**. Two dependency graphs with no stated relationship read as drift to any future reviewer, and the correct response to apparent drift is consolidation, which here would be actively wrong. Recording the axiom-distinction is the mitigation.

---

## 8. Cost Intelligence Model

### 8.1 The defect, precisely

The cost table is derived from `pytest --durations=0` over the whole suite **in one process**. The planner then balances **twelve concurrent shards** using those serial prices. Measured consequence:

| Quantity | Planner prediction | Measured | Ratio |
|---|---|---|---|
| serial suite cost | 1 616.5 s | 3 430.7 s | **2.12×** |
| per-shard load, wave 1 | 129.6 s uniform | 228.2 – 374.7 s | **1.64× spread** |
| pytest critical path | 191.4 s | 439.6 s | **2.30×** |
| effective speedup | 8.45× | 3.68× | — |

Under concurrency each shard pays its own import, collection and fixture cost and contends for I/O. That cost is invisible to a serial measurement, so longest-processing-time balancing optimises against prices that do not describe the topology it is planning for.

### 8.2 Determination

**Cost is a measurement under a topology. The topology must be part of the measurement's identity.**

A price recorded without the worker count it was observed at is not a reusable measurement — it is one observation presented as a constant. The cost model must therefore carry the topology under which each price was taken, exactly as the split entries already carry the `content_hash` under which node ids were valid.

### 8.3 Constraints this evolution inherits

**P7 is absolute and is what makes cost evolution safe.** The declaration already states: *"A stale or absent entry makes a plan slower, never wrong: UVI-L-08 measures that the partition is exactly the selection whatever the prices say."*

Consequently:

- Cost may never gate. No run fails because a measurement moved.
- Cost may never narrow a selection. It orders and packs; it never deselects.
- An unpriced object stays deliberately **over**-priced (4.0 s default) so an unknown cannot be packed into a full shard. This asymmetry is P5 applied to scheduling and must survive.
- No clock enters a plan (UVI-L-10). Prices are inputs to a plan, never observations recorded in one.

### 8.4 Historical execution data

The repository already has the right pattern for this and should not invent a second one: the evidence store is a content-addressed record of stage outcomes. Durations are the same shape of fact — keyed by what was executed, over what input, under what topology.

**Determination:** historical duration data belongs in a store with the evidence store's *properties* (content-addressed, untracked, atomic, verdict-neutral, deletable without consequence), and must remain strictly separate from the evidence store's *contents*. A duration is not a verdict, and the two must never share an address space — an entry that carries both invites a cache hit on a verdict because a duration matched.

### 8.5 Prediction model

Non-authoritative, and the weakest model that closes the measured gap is sufficient. A single measured concurrency inflation factor per worker count would have converted a 129.6 s prediction into a ~275 s prediction and rebalanced the observed 228–375 s spread. Nothing here requires learning, statistics or a model that could itself be wrong in an interesting way.

---

## 9. Non-Code Dependency Model

### 9.1 The measured reality

| Population | Count | Share of non-code |
|---|---|---|
| tracked files | 6 150 | — |
| non-code tracked files | 4 057 | 100% |
| reachable by any existing declared substrate | 421 | **10.4%** |
| under some stage's declared `reuse_inputs` | 1 452 | **35.8%** |
| **with no declared relation of any kind** | **2 605** | **64.2%** |

### 9.2 Determination — three classes, three relations, no pretence

The governing requirement is *"without pretending all dependencies are code imports."* The determination is that non-code files divide into three classes by **what relation actually holds**, and each is answered by a different edge that already exists:

**Class A — GENERATED (345 files, 8.5%).**
Relation: `produced_by`. A generated artifact's blast radius is its producer's blast radius. Answered by E5 (§5). Fully computable today from data already declared.

**Class B — DECLARED-CONSUMED (1 452 files, 35.8%).**
Relation: `read_by`. A declaration, schema, registry or corpus document is *read by* specific stages. This relation **already exists** — it is the stage registry's `reuse_inputs` — and is currently used only to compute cache keys.

**Class C — UNCLAIMED (2 605 files, 64.2%).**
No producer, no declared consumer. Predominantly `00-MASTER/` programme corpora (1 244), plus service/data/infrastructure/application trees. These **must escalate**, and escalation is the *correct* answer for them under P5.

### 9.3 The load-bearing correction: read-set is not reuse-eligibility

Measurement showed an exact correlation: **8 of 15 stages declare `reuse_inputs`, and they are precisely the 8 declared `reusable`.** The 7 stages that declare no read-set are exactly the 7 non-reusable ones.

This is not coincidence — it is a conflation in the schema. One field carries two independent facts:

| Fact | Nature | Example |
|---|---|---|
| *what this stage reads* | a **dependency relation**, always knowable | UGA reads the whole tree |
| *whether this stage may be answered from cache* | a **policy**, deliberately restrictive | UGA may never be reused |

Because the two are fused, a stage that must always run declares no read-set — and therefore **contributes nothing to impact analysis**, even though its read-set is perfectly well known. `universal-object-governance` reads the whole version-controlled boundary; that is a declarable fact and a useful one. Declaring it does not make the stage reusable.

**Determination:** the read-set must be declarable independently of reuse eligibility. This is the minimum change that makes Class B computable, and it adds no registry, no authority and no schema of its own — it separates two facts already living in one field of a declaration that already exists and is already law-reconciled by UVI-L-03.

### 9.4 The relation must be named

Under P1 and the requirement not to pretend, every non-code edge must carry its kind. The relationship graph already declares the vocabulary — `owned_by`, `produced_by`, `depends_on`, `produces`, `validated_by`, `evidenced_by` — and it is pattern-bound rather than enum-bound (UISD ISD-L-02), so it admits `read_by` without constitutional amendment.

**An import edge and a read edge must never be merged into an undifferentiated "dependency".** They have different transitivity: imports compose transitively; "stage S reads path P" does not compose and must not be traversed as though it did.

### 9.5 The honest metric

Escalation rate is the wrong thing to drive down — under P5, escalation is correct behaviour whenever impact is genuinely unbounded. Driving down escalation directly would create pressure to narrow on unknowns, which is exactly what UVI-L-07 forbids.

**The metric is the Class C population (2 605).** Every file that acquires a true declared relation moves from C to A or B, and escalation falls as a *consequence* of knowing more — never as a policy of assuming more.

---

## 10. Certification Boundary Model

### 10.1 The four laws, restated as they constrain this architecture

| Law | Constraint | Effect on this architecture |
|---|---|---|
| **UVI-L-04** | every pre-UVI baseline stage stays declared and admitted by every certification-eligible mode | stage-level impact selection may **never** apply to certification modes |
| **UVI-L-05** | only whole-suite + floor modes may be certification-eligible | no selection improvement can make a narrower mode certifying |
| **UVI-L-07** | unknown impact widens | E5/E6 must escalate on any unresolved edge; the 4 unresolved closure targets escalate |
| **UVI-L-09** | certification never consults the cache | every §6 evolution is confined to developer modes |

### 10.2 Allowed evolution areas

| # | Area | Why permitted |
|---|---|---|
| A1 | admit artifact lineage as a read-only substrate | adds edges; P5 preserved; no authority created |
| A2 | declare stage read-sets independently of reuse eligibility | separates two facts in an existing declaration |
| A3 | select **stages** by impact — **developer modes only** | L-04/L-05 bind certification modes to the full contract; developer modes already declare what they do not claim |
| A4 | bind argv into the evidence key | strictly *narrows* what may be reused; can only reduce reuse |
| A5 | distinguish withheld from missing content hashes | recovers reuse the declaration already grants |
| A6 | fail loudly on a read-set prefix matching nothing | converts a silent defect into a visible one |
| A7 | evidence retention bounded by generation count | store property; verdict-neutral by construction |
| A8 | topology-aware cost measurement | P7 — cost never gates, never deselects |
| A9 | record the ordering/reachability axiom distinction | records an existing fact |

### 10.3 Forbidden — structurally, not by policy

| # | Forbidden | Law |
|---|---|---|
| F1 | any evidence reuse in a certification-eligible mode | UVI-L-09 |
| F2 | any subset selection in a certification-eligible mode | UVI-L-05 |
| F3 | removing, weakening or un-admitting any baseline stage | UVI-L-04 |
| F4 | narrowing on an unresolved or unknown edge | UVI-L-07 |
| F5 | naming a test path in the selector or the declaration | UVI-L-06 |
| F6 | sharding or concurrency changing any obligation | UVI-L-08 |
| F7 | a clock, host name or absolute path entering a plan | UVI-L-10 |
| F8 | a second identity authority or a `category_seq` counter | CAA-INV-04 |
| F9 | a third dependency edge population | §3, §7 |
| F10 | cost, retention or duration data gating anything | P7 |

### 10.4 The boundary in one sentence

> Every evolution determined here operates on **which stages and tests a developer-mode run executes**, and on **the totality and hygiene of the evidence key**. None of it touches what a certification run does, because a certification run runs everything, under the floor, without consulting evidence — and that is the property the four laws exist to make unreachable by any selector, including this one.

### 10.5 A consequence that must be stated plainly

Sub-minute verification is **structurally unreachable for `--full`**. Wave 0 alone — the two objects that must run alone and first — measures 64.8 s, and certification may neither reuse evidence nor run a subset. Any sub-minute objective applies to the developer modes only, and any proposal that claims otherwise is claiming to have crossed F1 or F2.

---

## 11. Implementation Sequence

Ordered by dependency. Each step is independently verifiable and independently revertible. **No step is authorised by this document** — the sequence is part of the determination, not a mandate to execute.

| # | Step | Depends on | Class | Verified by |
|---|---|---|---|---|
| 1 | Distinguish `withheld` from `missing` content hash; fail loudly on a read-set prefix matching zero objects | — | A5, A6 | 3 blocked stages produce a key; a bad prefix fails |
| 2 | Bind stage argv into the evidence key via the existing `extra` seam | 1 | A4 | changed argv, same label ⇒ miss |
| 3 | Declare stage read-sets independently of reuse eligibility | — | A2 | all 15 stages carry a read-set; reuse policy unchanged |
| 4 | Admit `generated-artifact-registry.json` as a read-only sixth substrate, reverse-traversed | — | A1 | 345 artifacts reach their producers; 4 unresolved targets escalate |
| 5 | Extend impact to select **stages**, developer modes only | 3, 4 | A3 | certification modes admit the full contract unchanged |
| 6 | Record topology with each cost measurement | — | A8 | predicted shard load tracks observed within tolerance |
| 7 | Bound evidence retention by generation count per stage | 1, 2 | A7 | store bounded; no verdict changes; pruning failure is non-fatal |
| 8 | Record the ordering/reachability axiom distinction | — | A9 | the 31 cycles are named as the reason |

**Sequencing rationale.** Steps 1–2 are correctness closures on the cache and must precede anything that increases reliance on it — widening reuse over a key that is not total would be the one change in this document capable of producing a false green. Step 3 unblocks step 5. Step 4 is independent and may proceed in parallel. Steps 6–8 are independent throughout.

**Every step is measurable against the existing laws.** No step requires a new law, and each is refused by an existing one if implemented incorrectly.

---

## 12. Readiness Determination

## **ARCHITECTURE READY**

### 12.1 Basis

| Criterion | Finding |
|---|---|
| Does the evolution require a new authority? | **No.** Every fact has an existing owner (§4.5). |
| Does it require a new registry? | **No.** E5 and E6 are existing declared data (§4.4). |
| Does it require a new dependency model? | **No.** It forbids one (§3, §7). |
| Does it require a schema amendment? | **No.** The relationship vocabulary is pattern-bound and admits `read_by` (§9.4). |
| Does it reduce any verification obligation? | **No.** All ten laws hold unchanged; four are load-bearing constraints on it (§10). |
| Does it touch the certification path? | **No.** Every change is confined to developer modes or to key hygiene (§10.4). |
| Are the defects it addresses measured? | **Yes.** All four are reproduced with figures (§1.3, §1.4). |
| Is the sequence independently verifiable? | **Yes.** Eight steps, each refused by an existing law if wrong (§11). |

### 12.2 Determination

The architecture is an **evolution of the existing system, expressible entirely as: one substrate admitted, one conflated declaration field separated, one traversal target extended, and three correctness closures on a cache that already exists.**

It creates nothing. It converges nothing that measurement shows cannot converge. It leaves all four certification laws not merely intact but load-bearing — each one is what makes a specific part of this architecture safe rather than merely faster.

The single conclusion that most constrains what follows, and that this determination records so that it cannot be relitigated silently:

> **`platform.foundation.dependencies.DependencyGraph` and `engine.verification_impact.ImpactGraph` cannot be merged.** The measured import graph contains 31 cyclic node sets; the ordering model rejects cycles by constitutional guarantee (AR-01). They are two projections of one edge population, distinguished by axiom rather than by accident, and any future consolidation effort that treats their coexistence as drift will be attempting something the data forbids.

### 12.3 Standing of this document

DETERMINATION. It legislates nothing, owns no gate, holds no counter, and mints no identity. Every constraint it cites is owned elsewhere and unchanged by it. It authorises no implementation.

---

**Execution mode honoured:** architecture determination only. No implementation, no repository mutation, no code changes, no new registries, no new authorities. Measurements in §1.4 were taken read-only and in-process; the tracked tree was not modified.

**STOP — DETERMINATION COMPLETE.**
