# UICM — Cross-Run Lineage Context

> **Artifact:** `UICM-CROSS-RUN-LINEAGE-CONTEXT`
> **Programme:** UCOS-UICM-000001 — Phase 3 preparation
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY ONLY. No implementation. No registry created. No file under
> `engine/uicm/` modified. `uicm.json` unmodified. No committed register modified.
> **Method:** every claim below was executed against the committed registers in memory.
> Nothing was written. Where a claim could not be verified, it is marked as such.

---

## 1. The problem, stated precisely

`ObservationRegistry` is append-only in every respect *within* a run and carries no history
*across* runs. The measurement is exact:

```
02-CLOSURE-OBSERVATION-REGISTRY.json
    observation_total  3162   = 1054 coordinates x 3
    coordinate_total   1054
    current_total      1054
    superseded_total   2108   all within-run procedural steps
    max_revision          3   DISCOVERED -> MEASURED -> OPEN|CLOSED
    chain_intact       true
```

`max_revision` is exactly 3 for all 1054 coordinates because `build_registry` constructs a
fresh `ObservationRegistry()` on every run and records the same three-step transition path
per coordinate. There is no loader: the only `load` methods in the package are
`ClosureDeclaration.load` and `CanonicalOwners.load`.

The consequence is the one thing the programme cannot accept. When a gap closes, the
register is regenerated with the coordinate reading `CLOSED` at revision 3, and **no record
survives that it was ever `OPEN`**. The 2108 `SUPERSEDED` records are not history; they are
the `DISCOVERED` and `MEASURED` markers of the current run.

## 2. What already holds, and must not be rebuilt

Cross-run continuity is a *loader*, not a capability. Every structural property it needs is
already implemented and, in one case, already measured:

| Property | Mechanism | Status |
|---|---|---|
| No mutating operation | three verbs: `record`, read accessors, `verify`. No update, delete, overwrite or setter | **held** — measured by UICM-INV-16 over the package's own source |
| Record immutability | `Observation` is `@dataclass(frozen=True, slots=True)` | held |
| Deterministic identity | `observation_id(capability, dimension, revision)` — no counter, no clock | held |
| Derived identity | capability half from the capability register, dimension half from the declaration | held |
| Explicit lineage | `supersedes` per coordinate + `previous_hash` across the register | held |
| Supersession derived, not stamped | last appended per coordinate is current; earlier ones report `SUPERSEDED` | held |
| `SUPERSEDED` terminal | `_TRANSITIONS[SUPERSEDED] = frozenset()` | held |
| Transition legality enforced on append | `predecessor.state.require_transition_to(state)` inside `record` | held |
| `OPEN -> CLOSED`, `CLOSED -> CERTIFIED` | declared transitions | held |
| Seal recomputation | `expected_hash()` recomputes `entry_hash` from `body()` | held |

**Nothing in the append path needs to change.** `record` already refuses an undeclared
transition and already derives identity from lineage depth. What is missing is that lineage
depth always starts at zero.

## 3. Rehydration is sound — verified, not assumed

A throwaway in-memory prototype reconstructed the registry from the committed document,
ignoring the two derived fields (`current`, `effective_state`) and verifying each record's
seal before admitting it:

```
rehydrated observations : 3162
chain verify()          : True
head_hash matches       : True
coordinates             : 1054
max_revision            : 3
re-render BYTE-IDENTICAL: True
effective_state_counts match: True
cells projected         : 1054
```

Byte-identical re-render is the decisive result: **the committed register is already a valid
continuity genesis.** Migration requires no data transformation, no backfill and no rewrite.

Cell projection was checked independently — all 1054 cells reproduce exactly against
`03-CLOSURE-MEASUREMENT-REPORT.json`, with `observation_head` and `observation_total`
matching.

### What does *not* rehydrate

`Capability` cannot be reconstructed from the committed registers, and this is correct rather
than a defect. `Capability.to_dict()` is lossy by design: it emits `artifact_count` and an
`identified_artifacts` **count**, and omits the `artifacts` tuple entirely. So capability
identity must continue to be re-derived by `discover_population()` from the live boundary,
exactly as `uicm.json` requires ("The population is a rule over the tracked boundary, never a
list").

The division is therefore: **observations rehydrate; population does not.** An early
prototype that rebuilt `Capability` from the measurement report produced a mismatched matrix
digest — that was the harness being lossy, not rehydration failing, and it is recorded here
because it is exactly the mistake an implementation could make.

## 4. Load-time invariants

`ObservationRegistry.verify()` covers four properties: seal recomputation, global chain
linkage, dense sequence, and per-coordinate `supersedes` correctness. Cross-run loading needs
seven more, because a file on disk can be malformed in ways an in-memory register cannot.
All eleven were tested against the committed register:

| ID | Invariant | Covered by `verify()` | Committed register |
|---|---|---|---|
| L1 | every `entry_hash` recomputes from `body()` | yes | PASS |
| L2 | `previous_hash` chains globally in sequence order | yes | PASS |
| L3 | `sequence` dense `1..N` | yes | PASS |
| L4 | per coordinate, `supersedes` == prior id; first is `""` | yes | PASS |
| L5 | `revision` == lineage position (1-based) | **no** | PASS |
| L6 | every lineage transition is declared | **no** | PASS |
| L7 | `observation_id` re-derives exactly from identity + revision | **no** | PASS |
| L8 | document `format` matches `OBSERVATION_REGISTRY_FORMAT` | **no** | PASS |
| L9 | every `dimension_id` is declared | **no** | PASS |
| L10 | derived fields (`current`, `effective_state`) recompute exactly | **no** | PASS |
| L11 | exactly one current reading per coordinate | **no** | PASS |

**All eleven PASS.** L7 matters most: identity is re-derived and compared rather than trusted
from the file, so a tampered `observation_id` is caught. L10 matters because it proves the two
derived fields can be discarded on load without information loss — they are a reader
convenience, not state.

## 5. Population is not stable, and the next change is imminent

This is the hazard that most affects the design. The population is a rule over
`git ls-files --cached`, so it moves when the index moves.

```
population size: 62
  engine.uicm            in population: False
  engine.uaue            in population: True
  engine.uckp            in population: True
```

**`engine.uicm` is untracked, so UICM measures itself out of its own population.** Committing
it takes the population to 63 capabilities and 1071 coordinates — 17 coordinates with no prior
observation. Under continuity those must be genesis-recorded rather than treated as an error.

The reverse case is worse. `ClosureMatrix.require_total()` asserts
`len(cells) == len(capabilities) x len(dimensions)`. If a capability leaves the boundary, the
register still holds its 17 coordinates, `cells()` returns 1054 against an expected 1037, and
the run **fails hard**. Today this cannot happen because the register is regenerated from the
live population every run. Under continuity it becomes reachable, and it is the single
correctness hazard continuity introduces.

## 6. Retirement resolves the shrink hazard using only declared vocabulary

The constraint is that no observation may be deleted or replaced, and `SUPERSEDED` is the only
terminal state. Both are satisfied by treating retirement as an ordinary append:

```
  transition legality to SUPERSEDED, from every live state:
    DISCOVERED -> SUPERSEDED : True      CLOSED    -> SUPERSEDED : True
    MEASURED   -> SUPERSEDED : True      CERTIFIED -> SUPERSEDED : True
    OPEN       -> SUPERSEDED : True      BLOCKED   -> SUPERSEDED : True
```

Tested by retiring all 17 coordinates of one capability:

```
  appended retirement observations : 17
  chain intact                     : True
  lineage now                      : DISCOVERED -> MEASURED -> OPEN -> SUPERSEDED
  history preserved (not deleted)  : True
  cells() unfiltered               : 1054
  cells() excluding SUPERSEDED     : 1037   (= 61 x 17)
  require_total() would now PASS   : True
  attempt to revive the coordinate : REFUSED — ClosureStateError:
                                     undeclared closure transition SUPERSEDED -> CLOSED
```

No new state, no new transition, no deletion, and the full prior lineage stays readable. The
refusal on revival is discussed as a bounded limitation in
`UICM-LINEAGE-GAP-DETERMINATION.md` §3.

## 7. Replay survives, and this was measured three ways

Continuity makes the committed register an *input*, which is the property most likely to break
replay. It does not.

**No-change run appends nothing.**

```
  coordinates whose measured state differs from current: 0
  observations appended: 0
  head unchanged: True
  BYTE-IDENTICAL: True
```

This is the fixed point `uicm.json` already declares ("A second render over an unchanged
repository rewrites no byte"), now holding across runs rather than within one.

**`measure_twice()` stays deterministic.** Both passes rehydrate the same on-disk bytes, so
they compute identical appends:

```
  pass1 head == pass2 head    : True
  pass1 digest == pass2 digest: True
```

This holds only because `render` runs *after* both passes. An implementation that wrote
between passes would make pass 2 read pass 1's output and the determinism check would compare
a register against its own successor.

**Render-then-re-measure converges in one step.**

```
  pass 2 coordinates differing: 0  -> appends 0
  head stable                 : True
  FIXED POINT REACHED         : True
```

## 8. Digest impact

`ClosureMatrix.to_document()` seals both `observation_head` and `observation_total`, so the
matrix digest is a function of history as well as content. Confirmed by simulating the Wave-1
closure (`engine.uckp` identity + governance, `OPEN -> CLOSED`):

| Quantity | Genesis | After Wave 1 |
|---|---|---|
| matrix digest | `8ce37cd19fe4…` (committed) | `a7831b0ba362…` |
| observation head | unchanged | moved |
| `OPEN` cells | 158 | 156 |
| `CLOSED` cells | 896 | 898 |
| register bytes | 2,089,806 | 2,091,145 (+1,339, +0.064%) |

Growth is ~669 bytes per appended observation. Extrapolated across all 158 closures:
+105,702 bytes, **+5.1%** on a 2.09 MB register. Bounded and acceptable.

The digest moving when a coordinate closes is correct semantics, not drift. The matrix digest
answers "what is the state of closure, and on what history", and both changed.

**The register must not be added to `source_digests`.** `observation_head` already seals it,
and a sixth source entry would change the matrix digest at genesis for no additional
guarantee. Verified: the five existing source digests are unchanged by anything in this phase.

## 9. Determination

**CROSS-RUN CONTINUITY IS A LOADER, NOT A CAPABILITY. MIGRATION IS A NO-OP.**

Rehydration is byte-exact, all eleven load-time invariants hold on the committed register,
replay survives under all three tests, digest impact is bounded and semantically correct, and
the append path needs no change. One correctness hazard exists (population shrink) and is
resolved by retirement using only declared vocabulary.

Proceed to `UICM-OBSERVATION-CONTINUITY-MODEL.md` for the design, then
`UICM-LINEAGE-GAP-DETERMINATION.md` for what remains unresolved.
